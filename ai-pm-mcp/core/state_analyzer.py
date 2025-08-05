#!/usr/bin/env python3
"""
Project State Analyzer

Analyzes project state and categorizes according to directives:
- none: No project management folder
- partial: Incomplete structure  
- complete: Full structure with all components
- unknown: Issues detected during analysis
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from ..utils.project_paths import get_project_management_path

logger = logging.getLogger(__name__)


class ProjectStateAnalyzer:
    """Analyzes project state and categorizes for user presentation."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
    
    async def analyze_project_state(self, project_path: Path, force_full_analysis: bool = False) -> Dict[str, Any]:
        """
        Optimized project state analysis with fast path for existing projects.
        
        Fast Path: For existing projects with cached state (~100ms)
        Full Path: For new/missing projects requiring comprehensive analysis (~2-5s)
        
        Returns:
        {
            "state": "none|partial|complete|unknown",
            "project_path": str,
            "details": {...},
            "git_analysis": {...},
            "recommended_actions": [...],
            "analysis_type": "fast|comprehensive"
        }
        """
        try:
            logger.debug(f"Analyzing project state for: {project_path}")
            
            # Check basic directory structure
            project_mgmt_dir = get_project_management_path(project_path, self.config_manager)
            
            # Fast Path: Existing projects with cached state
            if not force_full_analysis and project_mgmt_dir.exists():
                fast_result = await self._fast_state_analysis(project_path, project_mgmt_dir)
                if fast_result:
                    logger.debug("Used fast path analysis")
                    return fast_result
                else:
                    logger.debug("Fast path failed, falling back to comprehensive analysis")
            
            # Comprehensive Path: New projects or when fast path fails
            logger.debug("Performing comprehensive project analysis")
            return await self._comprehensive_state_analysis(project_path, project_mgmt_dir)
            
        except Exception as e:
            logger.error(f"Error analyzing project state: {e}")
            return {
                "state": "unknown",
                "project_path": str(project_path),
                "details": {"error": str(e)},
                "git_analysis": {},
                "recommended_actions": ["project_get_status", "check_logs"],
                "analysis_type": "error"
            }
    
    async def _fast_state_analysis(self, project_path: Path, project_mgmt_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Fast analysis for existing projects using cached state.
        Returns None if fast analysis isn't possible.
        """
        try:
            # Check for cached state in metadata
            metadata_file = project_mgmt_dir / "ProjectBlueprint" / "metadata.json"
            if not metadata_file.exists():
                return None
            
            # Read cached project state
            import json
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            cached_state = metadata.get("cached_state")
            if not cached_state:
                return None
            
            # Quick Git hash check for external changes
            git_changed = await self._quick_git_change_check(project_path, cached_state.get("last_git_hash"))
            
            # If Git unchanged and cache is recent, use cached state
            cache_age_hours = self._get_cache_age_hours(cached_state.get("last_updated"))
            if not git_changed and cache_age_hours < 24:  # Cache valid for 24 hours
                logger.debug(f"Using cached state (age: {cache_age_hours:.1f}h)")
                
                # Quick verification that key components still exist
                if await self._quick_component_verification(project_mgmt_dir):
                    return {
                        "state": cached_state.get("state", "complete"),
                        "project_path": str(project_path),
                        "details": cached_state.get("details", {}),
                        "git_analysis": cached_state.get("git_analysis", {}),
                        "recommended_actions": self._generate_quick_recommendations(cached_state.get("state")),
                        "analysis_type": "fast",
                        "cache_age_hours": cache_age_hours,
                        "git_changes_detected": git_changed
                    }
            
            return None  # Fast path failed, need comprehensive analysis
            
        except Exception as e:
            logger.debug(f"Fast analysis failed: {e}")
            return None
    
    async def _comprehensive_state_analysis(self, project_path: Path, project_mgmt_dir: Path) -> Dict[str, Any]:
        """
        Comprehensive analysis for new projects or when fast path fails.
        """
        # Analyze Git repository state
        git_analysis = await self._analyze_git_state(project_path)
        
        # Determine primary state category
        if not project_mgmt_dir.exists():
            if git_analysis.get("has_ai_branches"):
                state = "git_history_found"
                details = self._analyze_git_history_scenario(project_path, git_analysis)
            else:
                state = "no_structure"
                details = self._analyze_no_structure_scenario(project_path)
        else:
            # Analyze existing structure completeness
            structure_analysis = await self._analyze_project_structure(project_mgmt_dir)
            if structure_analysis["completeness_ratio"] >= 0.9:
                state = "complete"
                details = await self._analyze_complete_project(project_path, project_mgmt_dir, git_analysis)
            elif structure_analysis["completeness_ratio"] >= 0.5:
                state = "partial"
                details = self._analyze_partial_project(project_path, project_mgmt_dir, structure_analysis, git_analysis)
            else:
                state = "incomplete"
                details = self._analyze_incomplete_project(project_path, project_mgmt_dir, structure_analysis, git_analysis)
        
        # Cache the result for future fast analysis
        await self._cache_analysis_result(project_mgmt_dir, state, details, git_analysis)
        
        return {
            "state": state,
            "project_path": str(project_path),
            "details": details,
            "git_analysis": git_analysis,
            "recommended_actions": self._generate_recommendations(state, details),
            "analysis_type": "comprehensive"
        }
    
    async def _analyze_git_state(self, project_path: Path) -> Dict[str, Any]:
        """Analyze Git repository state for AI project management branches."""
        analysis = {
            "is_git_repo": False,
            "has_ai_branches": False,
            "current_branch": None,
            "current_branch_type": "unknown",
            "ai_main_exists": False,
            "ai_instance_branches": [],
            "remote_ai_branches": [],
            "is_team_member": False,
            "has_remote": False
        }
        
        try:
            # Import and use the proper branch manager
            from .branch_manager import GitBranchManager
            branch_manager = GitBranchManager(project_path)
            
            # Check if this is a Git repository
            result = subprocess.run([
                'git', 'rev-parse', '--git-dir'
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                return analysis
                
            analysis["is_git_repo"] = True
            
            # Get current branch and identify its type
            current_branch = branch_manager.get_current_branch()
            analysis["current_branch"] = current_branch
            
            # Identify branch type
            if current_branch == "ai-pm-org-main":
                analysis["current_branch_type"] = "ai_main"
            elif current_branch and current_branch.startswith("ai-pm-org-branch-"):
                analysis["current_branch_type"] = "ai_instance"
            elif current_branch in ["main", "master"]:
                analysis["current_branch_type"] = "user_main"
            else:
                analysis["current_branch_type"] = "user_other"
            
            # Check for AI main branch existence
            analysis["ai_main_exists"] = branch_manager._branch_exists("ai-pm-org-main")
            
            # Get all AI instance branches
            instance_branches = branch_manager.list_instance_branches()
            analysis["ai_instance_branches"] = [branch.name for branch in instance_branches]
            analysis["has_ai_branches"] = analysis["ai_main_exists"] or len(analysis["ai_instance_branches"]) > 0
            
            # Detect team member scenario
            analysis["is_team_member"] = branch_manager._detect_team_member_scenario()
            
            # Check for remote repository and remote AI branches
            result = subprocess.run([
                'git', 'remote'
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                analysis["has_remote"] = True
                
                # Check for remote AI branches
                result = subprocess.run([
                    'git', 'branch', '-r'
                ], cwd=project_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    remote_branches = [line.strip() for line in result.stdout.strip().split('\n')]
                    remote_ai_branches = [b for b in remote_branches if 'ai-pm-org-' in b]
                    analysis["remote_ai_branches"] = remote_ai_branches
                    
        except Exception as e:
            logger.error(f"Error analyzing Git state: {e}")
            
        return analysis
    
    async def _analyze_project_structure(self, project_mgmt_dir: Path) -> Dict[str, Any]:
        """Analyze completeness of project management structure."""
        components = {
            "blueprint": project_mgmt_dir / "ProjectBlueprint" / "blueprint.md",
            "metadata": project_mgmt_dir / "ProjectBlueprint" / "metadata.json", 
            "flow_index": project_mgmt_dir / "ProjectFlow" / "flow-index.json",
            "themes": project_mgmt_dir / "Themes" / "themes.json",
            "completion_path": project_mgmt_dir / "Tasks" / "completion-path.json",
            "database": project_mgmt_dir / "project.db"
        }
        
        existing = {}
        missing = {}
        
        for name, path in components.items():
            if path.exists() and path.stat().st_size > 0:
                existing[name] = str(path)
            else:
                missing[name] = str(path)
        
        completeness_ratio = len(existing) / len(components)
        
        # Count tasks
        active_tasks = []
        sidequests = []
        
        active_dir = project_mgmt_dir / "Tasks" / "active"
        if active_dir.exists():
            active_tasks = list(active_dir.glob("*.json"))
        
        sidequest_dir = project_mgmt_dir / "Tasks" / "sidequests"
        if sidequest_dir.exists():
            sidequests = list(sidequest_dir.glob("*.json"))
        
        return {
            "existing": existing,
            "missing": missing,
            "completeness_ratio": completeness_ratio,
            "active_tasks": len(active_tasks),
            "sidequests": len(sidequests),
            "task_files": [str(f) for f in active_tasks],
            "sidequest_files": [str(f) for f in sidequests]
        }
    
    def _analyze_git_history_scenario(self, project_path: Path, git_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Git history found scenario."""
        return {
            "project_path": str(project_path),
            "git_analysis": git_analysis,
            "scenario": "git_history_without_structure",
            "primary_issue": "Git branches contain AI project management history but no current directory structure"
        }
    
    def _analyze_no_structure_scenario(self, project_path: Path) -> Dict[str, Any]:
        """Analyze no project structure scenario."""
        # Check for software project indicators
        project_indicators = [
            'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 
            'composer.json', 'pom.xml', 'src/', 'app/', 'lib/', 'README.md'
        ]
        
        found_indicators = [indicator for indicator in project_indicators 
                          if (project_path / indicator).exists()]
        
        return {
            "project_path": str(project_path),
            "scenario": "no_project_management",
            "software_project_indicators": found_indicators,
            "appears_to_be_software_project": len(found_indicators) > 0
        }
    
    async def _analyze_complete_project(self, project_path: Path, project_mgmt_dir: Path, git_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complete project scenario."""
        structure_analysis = await self._analyze_project_structure(project_mgmt_dir)
        
        # Check auto-task setting
        auto_task_enabled = await self._check_auto_task_setting(project_mgmt_dir)
        
        return {
            "project_path": str(project_path),
            "scenario": "complete_project",
            "git_analysis": git_analysis,
            "auto_task_enabled": auto_task_enabled,
            **structure_analysis
        }
    
    def _analyze_partial_project(self, project_path: Path, project_mgmt_dir: Path, structure_analysis: Dict[str, Any], git_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze partial project scenario."""
        return {
            "project_path": str(project_path),
            "scenario": "partial_project",
            "git_analysis": git_analysis,
            **structure_analysis
        }
    
    def _analyze_incomplete_project(self, project_path: Path, project_mgmt_dir: Path, structure_analysis: Dict[str, Any], git_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze incomplete project scenario."""
        return {
            "project_path": str(project_path),
            "scenario": "incomplete_project", 
            "git_analysis": git_analysis,
            **structure_analysis
        }
    
    async def _check_auto_task_setting(self, project_mgmt_dir: Path) -> bool:
        """Check if auto task creation is enabled in user settings."""
        try:
            config_file = project_mgmt_dir / ".ai-pm-config.json"
            if config_file.exists():
                import json
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return config.get("tasks", {}).get("resumeTasksOnStart", False)
        except Exception as e:
            logger.error(f"Error reading auto task setting: {e}")
        return False
    
    def _generate_recommendations(self, state: str, details: Dict[str, Any]) -> list:
        """Generate appropriate user options based on state."""
        if state == "git_history_found":
            return ["join_team", "create_branch", "fresh_start", "analyze_history"]
        elif state == "no_structure":
            return ["initialize_project", "get_project_status", "check_existing_code"]
        elif state == "complete":
            auto_enabled = details.get("auto_task_enabled", False)
            if auto_enabled:
                return ["session_boot_with_git_detection"]  # Auto-continue
            else:
                return ["session_boot_with_git_detection", "project_get_status", "session_start", "task_list_active"]
        elif state == "partial":
            return ["complete_initialization", "review_state", "restore_components", "continue_existing", "git_integration"]
        elif state == "incomplete":
            return ["initialize_project", "check_status", "review_existing", "git_integration"]
        else:  # unknown
            return ["project_get_status", "project_initialize", "check_logs"]
    
    def categorize_state(self, components: Dict[str, Any]) -> str:
        """Categorize project state based on component analysis."""
        # This is a helper method for external callers
        completeness_ratio = components.get("completeness_ratio", 0)
        
        if completeness_ratio >= 0.9:
            return "complete"
        elif completeness_ratio >= 0.5:
            return "partial"
        elif completeness_ratio > 0:
            return "incomplete"
        else:
            return "none"
    
    # Fast Path Helper Methods
    
    async def _quick_git_change_check(self, project_path: Path, cached_git_hash: Optional[str]) -> bool:
        """Quick check if Git repository has changed since last analysis."""
        if not cached_git_hash:
            return True  # No cached hash, assume changed
        
        try:
            result = subprocess.run([
                'git', 'rev-parse', 'HEAD'
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                return True  # Git error, assume changed
            
            current_hash = result.stdout.strip()
            return current_hash != cached_git_hash
            
        except Exception as e:
            logger.debug(f"Git change check failed: {e}")
            return True  # Error, assume changed
    
    def _get_cache_age_hours(self, last_updated: Optional[str]) -> float:
        """Get cache age in hours."""
        if not last_updated:
            return float('inf')  # No timestamp, very old
        
        try:
            from datetime import datetime, timezone
            cached_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            age_seconds = (current_time - cached_time).total_seconds()
            return age_seconds / 3600  # Convert to hours
        except Exception:
            return float('inf')  # Parse error, assume very old
    
    async def _quick_component_verification(self, project_mgmt_dir: Path) -> bool:
        """Quick verification that key components still exist."""
        key_components = [
            project_mgmt_dir / "ProjectBlueprint" / "blueprint.md",
            project_mgmt_dir / "ProjectFlow" / "flow-index.json",
            project_mgmt_dir / "Themes" / "themes.json"
        ]
        
        for component in key_components:
            if not component.exists():
                logger.debug(f"Quick verification failed: {component} missing")
                return False
        
        return True
    
    def _generate_quick_recommendations(self, state: str) -> list:
        """Generate quick recommendations for cached states."""
        if state == "complete":
            return ["session_boot_with_git_detection", "task_list_active", "project_get_status"]
        elif state == "partial":
            return ["review_state", "complete_initialization", "continue_existing"]
        elif state == "git_history_found":
            return ["join_team", "create_branch", "fresh_start"]
        else:
            return ["project_get_status", "project_initialize"]
    
    async def _cache_analysis_result(self, project_mgmt_dir: Path, state: str, details: Dict[str, Any], git_analysis: Dict[str, Any]):
        """Cache analysis result in metadata for future fast analysis."""
        try:
            metadata_file = project_mgmt_dir / "ProjectBlueprint" / "metadata.json"
            if not metadata_file.exists():
                return  # Can't cache without metadata file
            
            # Read existing metadata
            import json
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Get current Git hash for future change detection
            current_git_hash = None
            try:
                result = subprocess.run([
                    'git', 'rev-parse', 'HEAD'
                ], cwd=project_mgmt_dir.parent, capture_output=True, text=True)
                if result.returncode == 0:
                    current_git_hash = result.stdout.strip()
            except Exception:
                pass
            
            # Cache the analysis result
            from datetime import datetime, timezone
            metadata["cached_state"] = {
                "state": state,
                "details": details,
                "git_analysis": git_analysis,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "last_git_hash": current_git_hash
            }
            
            # Write back to metadata file
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug("Analysis result cached in metadata")
            
        except Exception as e:
            logger.debug(f"Failed to cache analysis result: {e}")
            # Non-critical error, continue without caching