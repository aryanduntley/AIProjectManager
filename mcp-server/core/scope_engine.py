"""
Scope and context loading engine for the AI Project Manager MCP Server.

Handles intelligent context loading based on themes, README guidance, context modes,
and compressed context management for optimal AI session continuity.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import os

logger = logging.getLogger(__name__)


class ContextMode(Enum):
    """Available context loading modes."""
    THEME_FOCUSED = "theme-focused"
    THEME_EXPANDED = "theme-expanded"
    PROJECT_WIDE = "project-wide"


@dataclass
class ContextResult:
    """Result of context loading operation."""
    mode: ContextMode
    primary_theme: str
    loaded_themes: List[str]
    files: List[str]
    paths: List[str]
    readmes: Dict[str, str]
    shared_files: Dict[str, List[str]]
    recommendations: List[str]
    memory_estimate: int


class CompressedContextManager:
    """Manages compressed context files for optimal AI session continuity."""
    
    def __init__(self, mcp_server_path: Optional[Path] = None):
        """Initialize with MCP server path for core context loading."""
        if mcp_server_path is None:
            # Auto-detect MCP server path relative to this file
            mcp_server_path = Path(__file__).parent.parent
        
        self.mcp_server_path = mcp_server_path
        self.core_context_path = mcp_server_path / "core-context"
        
        # Core context (always loaded)
        self._core_context = {}
        self._loaded = False
    
    async def load_core_context(self) -> Dict[str, Any]:
        """Load compressed core context files."""
        if self._loaded:
            return self._core_context
        
        try:
            # Load all core context files
            core_files = [
                "system-essence.json",
                "workflow-triggers.json", 
                "directive-compressed.json",
                "validation-core.json"
            ]
            
            for filename in core_files:
                file_path = self.core_context_path / filename
                if file_path.exists():
                    context_data = json.loads(file_path.read_text())
                    self._core_context[filename.replace('.json', '')] = context_data
                else:
                    logger.warning(f"Core context file not found: {file_path}")
            
            self._loaded = True
            logger.info(f"Loaded {len(self._core_context)} core context files")
            
        except Exception as e:
            logger.error(f"Error loading core context: {e}")
            raise
        
        return self._core_context
    
    def get_workflow_for_scenario(self, scenario: str) -> Optional[Dict[str, Any]]:
        """Get workflow definition for a specific scenario."""
        if not self._loaded:
            return None
            
        workflow_triggers = self._core_context.get('workflow-triggers', {})
        scenarios = workflow_triggers.get('commonScenarios', {})
        
        return scenarios.get(scenario)
    
    def get_directive_summary(self, directive_key: str) -> Optional[Dict[str, Any]]:
        """Get compressed directive information."""
        if not self._loaded:
            return None
            
        directives = self._core_context.get('directive-compressed', {})
        return directives.get(directive_key)
    
    def get_validation_rules(self, validation_type: str) -> Optional[Dict[str, Any]]:
        """Get validation rules for specific validation type."""
        if not self._loaded:
            return None
            
        validation_core = self._core_context.get('validation-core', {})
        return validation_core.get(validation_type)
    
    def get_session_boot_sequence(self) -> List[str]:
        """Get the session boot sequence steps."""
        if not self._loaded:
            return []
            
        system_essence = self._core_context.get('system-essence', {})
        return system_essence.get('sessionBootSequence', [])
    
    def get_core_rules(self) -> List[str]:
        """Get critical rules for AI behavior."""
        if not self._loaded:
            return []
            
        system_essence = self._core_context.get('system-essence', {})
        return system_essence.get('criticalRules', [])
    
    def should_escalate_context(self, issue_description: str) -> Tuple[bool, str]:
        """Determine if context escalation is needed based on issue."""
        if not self._loaded:
            return False, "Core context not loaded"
        
        workflow_triggers = self._core_context.get('workflow-triggers', {})
        escalation_scenario = workflow_triggers.get('commonScenarios', {}).get('context_escalation_needed')
        
        if not escalation_scenario:
            return False, "No escalation rules found"
        
        # Check if issue contains escalation trigger keywords
        triggers = escalation_scenario.get('triggers', [])
        issue_lower = issue_description.lower()
        
        for trigger in triggers:
            if trigger.lower() in issue_lower:
                return True, f"Issue matches escalation trigger: {trigger}"
        
        return False, "No escalation triggers found in issue"
    
    async def generate_situational_context(self, project_path: Path, situation: str) -> Dict[str, Any]:
        """Generate context specific to current project situation."""
        try:
            # Load project state
            project_state = await self._analyze_project_state(project_path)
            
            # Get workflow for situation
            workflow = self.get_workflow_for_scenario(situation)
            if not workflow:
                return {"error": f"No workflow found for situation: {situation}"}
            
            # Generate contextual response
            context = {
                "situation": situation,
                "workflow": workflow,
                "projectState": project_state,
                "requiredFiles": workflow.get('requiredFiles', []),
                "actions": workflow.get('actions', []),
                "contextMode": workflow.get('contextMode', 'theme-focused'),
                "priority": workflow.get('priority', 'medium')
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error generating situational context: {e}")
            return {"error": str(e)}
    
    async def _analyze_project_state(self, project_path: Path) -> Dict[str, Any]:
        """Analyze current project state for context generation."""
        state = {
            "hasProjectManagement": False,
            "hasActiveImplementationPlan": False,
            "hasActiveTasks": False,
            "themesCount": 0,
            "milestonesCount": 0
        }
        
        try:
            pm_path = project_path / "projectManagement"
            if pm_path.exists():
                state["hasProjectManagement"] = True
                
                # Check for active implementation plan
                impl_active = pm_path / "Implementations" / "active"
                if impl_active.exists():
                    active_plans = list(impl_active.glob("*.md"))
                    state["hasActiveImplementationPlan"] = len(active_plans) > 0
                
                # Check for active tasks
                tasks_active = pm_path / "Tasks" / "active"
                if tasks_active.exists():
                    active_tasks = list(tasks_active.glob("TASK-*.json"))
                    state["hasActiveTasks"] = len(active_tasks) > 0
                
                # Count themes
                themes_dir = pm_path / "Themes"
                if themes_dir.exists():
                    theme_files = list(themes_dir.glob("*.json"))
                    # Exclude themes.json index file
                    state["themesCount"] = len([f for f in theme_files if f.name != "themes.json"])
                
                # Count milestones
                completion_path = pm_path / "Tasks" / "completion-path.json"
                if completion_path.exists():
                    try:
                        cp_data = json.loads(completion_path.read_text())
                        state["milestonesCount"] = len(cp_data.get('milestones', []))
                    except:
                        pass
        
        except Exception as e:
            logger.debug(f"Error analyzing project state: {e}")
        
        return state


class ScopeEngine:
    """Engine for determining and loading project context based on themes."""
    
    def __init__(self, mcp_server_path: Optional[Path] = None):
        self.max_memory_mb = 100  # Maximum context memory in MB
        self.readme_priority_files = [
            'README.md', 'readme.md', 'Readme.md',
            'README.txt', 'readme.txt'
        ]
        
        # Initialize compressed context manager
        self.context_manager = CompressedContextManager(mcp_server_path)
        self._core_context_loaded = False
    
    async def ensure_core_context_loaded(self):
        """Ensure compressed core context is loaded."""
        if not self._core_context_loaded:
            await self.context_manager.load_core_context()
            self._core_context_loaded = True
    
    async def get_session_boot_context(self, project_path: Path) -> Dict[str, Any]:
        """Get context specifically for session boot sequence."""
        await self.ensure_core_context_loaded()
        
        boot_sequence = self.context_manager.get_session_boot_sequence()
        core_rules = self.context_manager.get_core_rules()
        project_state = await self.context_manager._analyze_project_state(project_path)
        
        return {
            "bootSequence": boot_sequence,
            "coreRules": core_rules,
            "projectState": project_state,
            "contextMode": "session-boot"
        }
    
    async def get_situational_context(self, project_path: Path, situation: str) -> Dict[str, Any]:
        """Get context for a specific situation using compressed context."""
        await self.ensure_core_context_loaded()
        return await self.context_manager.generate_situational_context(project_path, situation)
    
    async def load_context(self, project_path: Path, primary_theme: str, 
                          context_mode: ContextMode = ContextMode.THEME_FOCUSED,
                          force_mode: bool = False) -> ContextResult:
        """Load context based on theme and context mode."""
        try:
            themes_dir = project_path / "projectManagement" / "Themes"
            
            # Load primary theme
            primary_theme_data = await self._load_theme(themes_dir, primary_theme)
            if not primary_theme_data:
                raise ValueError(f"Primary theme '{primary_theme}' not found")
            
            # Determine actual context mode (may escalate if needed)
            actual_mode = await self._determine_context_mode(
                themes_dir, primary_theme_data, context_mode, force_mode
            )
            
            # Load context based on determined mode
            context = await self._load_context_by_mode(
                project_path, themes_dir, primary_theme, primary_theme_data, actual_mode
            )
            
            # Load README files for context
            context.readmes = await self._load_readmes(project_path, context.paths)
            
            # Estimate memory usage
            context.memory_estimate = await self._estimate_memory_usage(context)
            
            # Generate recommendations
            context.recommendations = await self._generate_recommendations(context, actual_mode, context_mode)
            
            return context
            
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            raise
    
    async def _load_theme(self, themes_dir: Path, theme_name: str) -> Optional[Dict[str, Any]]:
        """Load a theme definition."""
        theme_file = themes_dir / f"{theme_name}.json"
        if not theme_file.exists():
            return None
        
        try:
            return json.loads(theme_file.read_text())
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in theme file: {theme_file}")
            return None
    
    async def _determine_context_mode(self, themes_dir: Path, primary_theme_data: Dict[str, Any],
                                    requested_mode: ContextMode, force_mode: bool) -> ContextMode:
        """Determine the actual context mode to use."""
        if force_mode:
            return requested_mode
        
        # Analyze theme complexity to suggest mode
        file_count = len(primary_theme_data.get('files', []))
        linked_themes = primary_theme_data.get('linkedThemes', [])
        shared_files = primary_theme_data.get('sharedFiles', {})
        
        # If theme has many linked themes or shared files, suggest expansion
        if requested_mode == ContextMode.THEME_FOCUSED:
            if len(linked_themes) > 2 or len(shared_files) > 5:
                logger.info(f"Theme has {len(linked_themes)} linked themes and {len(shared_files)} shared files. "
                           f"Consider using theme-expanded mode.")
                return ContextMode.THEME_EXPANDED
        
        # If expanded mode but few connections, theme-focused might suffice
        if requested_mode == ContextMode.THEME_EXPANDED:
            if len(linked_themes) == 0 and len(shared_files) <= 2:
                logger.info("Theme has few connections. theme-focused mode may be sufficient.")
        
        return requested_mode
    
    async def _load_context_by_mode(self, project_path: Path, themes_dir: Path, 
                                   primary_theme: str, primary_theme_data: Dict[str, Any],
                                   mode: ContextMode) -> ContextResult:
        """Load context based on the specified mode."""
        context = ContextResult(
            mode=mode,
            primary_theme=primary_theme,
            loaded_themes=[primary_theme],
            files=list(primary_theme_data.get('files', [])),
            paths=list(primary_theme_data.get('paths', [])),
            readmes={},
            shared_files={},
            recommendations=[],
            memory_estimate=0
        )
        
        if mode == ContextMode.THEME_FOCUSED:
            # Only load primary theme
            context.shared_files = primary_theme_data.get('sharedFiles', {})
            
        elif mode == ContextMode.THEME_EXPANDED:
            # Load primary theme + linked themes
            linked_themes = primary_theme_data.get('linkedThemes', [])
            
            for linked_theme in linked_themes:
                linked_data = await self._load_theme(themes_dir, linked_theme)
                if linked_data:
                    context.loaded_themes.append(linked_theme)
                    context.files.extend(linked_data.get('files', []))
                    context.paths.extend(linked_data.get('paths', []))
                    
                    # Merge shared files
                    for file_path, sharing_info in linked_data.get('sharedFiles', {}).items():
                        if file_path not in context.shared_files:
                            context.shared_files[file_path] = []
                        context.shared_files[file_path].extend(sharing_info.get('sharedWith', []))
            
        elif mode == ContextMode.PROJECT_WIDE:
            # Load all themes
            themes_index = themes_dir / "themes.json"
            if themes_index.exists():
                all_themes = json.loads(themes_index.read_text())
                
                for theme_name in all_themes.keys():
                    if theme_name != primary_theme:
                        theme_data = await self._load_theme(themes_dir, theme_name)
                        if theme_data:
                            context.loaded_themes.append(theme_name)
                            context.files.extend(theme_data.get('files', []))
                            context.paths.extend(theme_data.get('paths', []))
                            
                            # Merge shared files
                            for file_path, sharing_info in theme_data.get('sharedFiles', {}).items():
                                if file_path not in context.shared_files:
                                    context.shared_files[file_path] = []
                                context.shared_files[file_path].extend(sharing_info.get('sharedWith', []))
        
        # Remove duplicates
        context.files = list(set(context.files))
        context.paths = list(set(context.paths))
        
        # Add global files and paths that are always accessible
        global_paths = await self._get_global_paths(project_path)
        context.paths.extend(global_paths)
        context.paths = list(set(context.paths))
        
        return context
    
    async def _get_global_paths(self, project_path: Path) -> List[str]:
        """Get globally accessible paths regardless of theme."""
        global_patterns = [
            # Project root level
            "package.json", "requirements.txt", "Cargo.toml", "composer.json",
            ".env", ".env.local", "config.json", "settings.json",
            "Dockerfile", "docker-compose.yml", "Makefile",
            "README.md", "LICENSE", "CHANGELOG.md",
            ".gitignore", ".gitattributes",
            
            # Source root patterns
            "src", "lib", "app",
            "src/index.*", "src/main.*", "src/app.*", "src/App.*",
            "src/config", "src/constants", "src/types", "src/utils"
        ]
        
        global_paths = []
        
        for pattern in global_patterns:
            # Check if it's a direct file
            file_path = project_path / pattern
            if file_path.exists():
                if file_path.is_file():
                    global_paths.append(pattern)
                elif file_path.is_dir():
                    global_paths.append(pattern)
        
        return global_paths
    
    async def _load_readmes(self, project_path: Path, paths: List[str]) -> Dict[str, str]:
        """Load README files from relevant paths for quick context."""
        readmes = {}
        
        # Add project root README
        for readme_name in self.readme_priority_files:
            root_readme = project_path / readme_name
            if root_readme.exists():
                try:
                    content = root_readme.read_text(encoding='utf-8')
                    readmes[str(Path('.'))] = content[:2000]  # Limit to 2KB
                    break
                except Exception as e:
                    logger.debug(f"Error reading {root_readme}: {e}")
        
        # Load READMEs from theme paths
        for path in paths:
            path_obj = project_path / path
            if path_obj.is_dir():
                for readme_name in self.readme_priority_files:
                    readme_file = path_obj / readme_name
                    if readme_file.exists():
                        try:
                            content = readme_file.read_text(encoding='utf-8')
                            readmes[path] = content[:2000]  # Limit to 2KB
                            break
                        except Exception as e:
                            logger.debug(f"Error reading {readme_file}: {e}")
        
        return readmes
    
    async def _estimate_memory_usage(self, context: ContextResult) -> int:
        """Estimate memory usage in MB for the loaded context."""
        # Rough estimates
        files_mb = len(context.files) * 0.1  # ~100KB per file average
        readmes_mb = sum(len(content) for content in context.readmes.values()) / (1024 * 1024)
        themes_mb = len(context.loaded_themes) * 0.01  # ~10KB per theme definition
        
        total_mb = files_mb + readmes_mb + themes_mb
        return int(total_mb)
    
    async def _generate_recommendations(self, context: ContextResult, 
                                       actual_mode: ContextMode, 
                                       requested_mode: ContextMode) -> List[str]:
        """Generate recommendations for context optimization."""
        recommendations = []
        
        # Memory usage recommendations
        if context.memory_estimate > self.max_memory_mb:
            recommendations.append(
                f"High memory usage ({context.memory_estimate}MB). "
                f"Consider using a more focused context mode."
            )
        
        # Mode recommendations
        if actual_mode != requested_mode:
            recommendations.append(
                f"Context mode escalated from {requested_mode.value} to {actual_mode.value} "
                f"based on theme complexity."
            )
        
        # Coverage recommendations
        if context.mode == ContextMode.THEME_FOCUSED and len(context.shared_files) > 3:
            recommendations.append(
                "Theme has many shared files. Consider theme-expanded mode for better context."
            )
        
        if context.mode == ContextMode.PROJECT_WIDE and len(context.loaded_themes) > 10:
            recommendations.append(
                "Loading many themes. Consider if theme-expanded mode would be sufficient."
            )
        
        # README recommendations
        missing_readmes = []
        for path in context.paths:
            if path not in context.readmes and path != '.':
                missing_readmes.append(path)
        
        if len(missing_readmes) > 3:
            recommendations.append(
                f"Consider adding README.md files to {len(missing_readmes)} directories "
                f"for better context guidance."
            )
        
        return recommendations
    
    async def assess_context_escalation(self, current_context: ContextResult, 
                                      issue_description: str) -> Tuple[bool, ContextMode, str]:
        """Assess if context escalation is needed based on an issue."""
        current_mode = current_context.mode
        
        # Keywords that suggest need for broader context
        escalation_keywords = [
            'import', 'dependency', 'reference', 'call', 'connection',
            'integration', 'shared', 'cross', 'global', 'config'
        ]
        
        # Check if issue mentions cross-theme concerns
        issue_lower = issue_description.lower()
        needs_escalation = any(keyword in issue_lower for keyword in escalation_keywords)
        
        if not needs_escalation:
            return False, current_mode, "No escalation needed"
        
        # Determine escalation path
        if current_mode == ContextMode.THEME_FOCUSED:
            new_mode = ContextMode.THEME_EXPANDED
            reason = "Issue mentions cross-theme dependencies or integrations"
        elif current_mode == ContextMode.THEME_EXPANDED:
            new_mode = ContextMode.PROJECT_WIDE
            reason = "Issue requires project-wide context"
        else:
            return False, current_mode, "Already at maximum context level"
        
        return True, new_mode, reason
    
    async def get_context_summary(self, context: ContextResult) -> str:
        """Get a human-readable summary of the loaded context."""
        summary_parts = [
            f"Context Mode: {context.mode.value}",
            f"Primary Theme: {context.primary_theme}",
            f"Loaded Themes: {', '.join(context.loaded_themes)}",
            f"Files: {len(context.files)} files",
            f"Paths: {len(context.paths)} directories",
            f"README files: {len(context.readmes)} found",
            f"Memory Usage: ~{context.memory_estimate}MB"
        ]
        
        if context.shared_files:
            summary_parts.append(f"Shared Files: {len(context.shared_files)} files shared across themes")
        
        if context.recommendations:
            summary_parts.append("Recommendations:")
            for rec in context.recommendations:
                summary_parts.append(f"  - {rec}")
        
        return "\n".join(summary_parts)
    
    async def filter_files_by_relevance(self, context: ContextResult, 
                                       task_description: str) -> List[str]:
        """Filter context files by relevance to a specific task."""
        if not task_description:
            return context.files
        
        # Extract keywords from task description
        task_keywords = set(word.lower().strip('.,!?:;') 
                           for word in task_description.split() 
                           if len(word) > 2)
        
        # Score files based on keyword matches
        file_scores = {}
        for file_path in context.files:
            score = 0
            file_parts = file_path.lower().replace('/', ' ').replace('_', ' ').replace('-', ' ')
            
            for keyword in task_keywords:
                if keyword in file_parts:
                    score += 1
            
            # Boost score for files in primary theme
            if any(theme_path in file_path for theme_path in context.paths[:3]):
                score += 0.5
            
            file_scores[file_path] = score
        
        # Return files sorted by relevance (minimum score of 0.5)
        relevant_files = [
            file_path for file_path, score in file_scores.items() 
            if score >= 0.5
        ]
        
        # If no relevant files found, return top N files from primary theme
        if not relevant_files and context.files:
            primary_theme_files = [
                f for f in context.files 
                if any(theme_path in f for theme_path in context.paths[:3])
            ]
            relevant_files = primary_theme_files[:10] if primary_theme_files else context.files[:10]
        
        return relevant_files
    
    async def validate_context_integrity(self, project_path: Path, context: ContextResult) -> Dict[str, Any]:
        """Validate context integrity using compressed validation rules."""
        await self.ensure_core_context_loaded()
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks_performed": []
        }
        
        try:
            # Get validation rules from compressed context
            integration_rules = self.context_manager.get_validation_rules('integrationValidation')
            integrity_rules = self.context_manager.get_validation_rules('dataIntegrity')
            
            if not integration_rules or not integrity_rules:
                validation_results["warnings"].append("Validation rules not available in compressed context")
                return validation_results
            
            # Validate theme integrity
            themes_dir = project_path / "projectManagement" / "Themes"
            for theme_name in context.loaded_themes:
                theme_file = themes_dir / f"{theme_name}.json"
                if not theme_file.exists():
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"Theme file missing: {theme_name}.json")
                
                validation_results["checks_performed"].append(f"Theme file existence: {theme_name}")
            
            # Validate file references
            file_check_count = 0
            for file_path in context.files[:10]:  # Check first 10 files for performance
                full_path = project_path / file_path
                if not full_path.exists():
                    validation_results["warnings"].append(f"Referenced file not found: {file_path}")
                file_check_count += 1
            
            validation_results["checks_performed"].append(f"File existence checks: {file_check_count} files")
            
            # Check README coverage
            missing_readmes = []
            for path in context.paths[:5]:  # Check first 5 paths
                if path not in context.readmes and path != '.':
                    missing_readmes.append(path)
            
            if missing_readmes:
                validation_results["warnings"].append(f"Missing README files in {len(missing_readmes)} directories")
            
            validation_results["checks_performed"].append("README coverage check")
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    async def get_compressed_directive(self, directive_key: str) -> Optional[Dict[str, Any]]:
        """Get compressed directive information."""
        await self.ensure_core_context_loaded()
        return self.context_manager.get_directive_summary(directive_key)