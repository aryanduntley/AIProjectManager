"""
Git Integration Module for AI Project Manager
Handles root-level Git repository management and project code change detection
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import hashlib

from ..database.db_manager import DatabaseManager


class GitIntegrationManager:
    """
    Manages Git integration for AI Project Manager including:
    - Root-level Git repository initialization and validation
    - Project code change detection
    - Theme impact analysis when code changes occur
    - Integration with MCP instance management
    """
    
    def __init__(self, project_root: Path, db_manager: DatabaseManager):
        self.project_root = Path(project_root)
        self.db_manager = db_manager
        self.git_dir = self.project_root / ".git"
        self.project_management_dir = self.project_root / "projectManagement"
        
    # ============================================================================
    # GIT REPOSITORY MANAGEMENT
    # ============================================================================
    
    def is_git_repository(self) -> bool:
        """Check if project root is a Git repository"""
        return self.git_dir.exists() and self.git_dir.is_dir()
    
    def initialize_git_repository(self) -> Dict[str, Any]:
        """
        Initialize Git repository at project root if it doesn't exist
        Returns initialization result with status and details
        """
        result = {
            "success": False,
            "action": "none",
            "message": "",
            "git_hash": None,
            "created_files": []
        }
        
        try:
            if self.is_git_repository():
                result["action"] = "existing"
                result["message"] = "Git repository already exists"
                result["git_hash"] = self.get_current_git_hash()
                result["success"] = True
            else:
                # Initialize new Git repository
                subprocess.run(
                    ["git", "init"], 
                    cwd=self.project_root, 
                    check=True, 
                    capture_output=True, 
                    text=True
                )
                
                # Create initial .gitignore for MCP instance management
                gitignore_content = self._generate_mcp_gitignore()
                gitignore_path = self.project_root / ".gitignore"
                
                if gitignore_path.exists():
                    # Append to existing .gitignore
                    with open(gitignore_path, "a") as f:
                        f.write("\n# MCP Instance Management\n")
                        f.write(gitignore_content)
                    result["created_files"].append(".gitignore (updated)")
                else:
                    # Create new .gitignore
                    with open(gitignore_path, "w") as f:
                        f.write(gitignore_content)
                    result["created_files"].append(".gitignore")
                
                # Add initial files to Git
                subprocess.run(
                    ["git", "add", "."], 
                    cwd=self.project_root, 
                    check=True, 
                    capture_output=True, 
                    text=True
                )
                
                # Create initial commit
                subprocess.run([
                    "git", "commit", "-m", 
                    "Initial commit: AI Project Manager with Git integration"
                ], cwd=self.project_root, check=True, capture_output=True, text=True)
                
                result["action"] = "initialized"
                result["message"] = "Git repository initialized successfully"
                result["git_hash"] = self.get_current_git_hash()
                result["success"] = True
                
        except subprocess.CalledProcessError as e:
            result["message"] = f"Git command failed: {e.stderr}"
        except Exception as e:
            result["message"] = f"Git initialization error: {str(e)}"
            
        return result
    
    def _generate_mcp_gitignore(self) -> str:
        """Generate .gitignore content for Git branch-based AI Project Manager"""
        return """
# AI Project Manager - Git Branch Based Management
# Track organizational state, not user-specific settings or temporary files

# Project Management - Track Organizational State, Not User Data
projectManagement/UserSettings/
projectManagement/database/backups/
projectManagement/.mcp-session-*

# Temporary and cache files
*.pyc
__pycache__/
.DS_Store
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# Node modules and build artifacts
node_modules/
dist/
build/
*.log
.env.local
.env.development.local
.env.test.local
.env.production.local
"""
    
    def get_current_git_hash(self) -> Optional[str]:
        """Get current Git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get detailed Git repository status"""
        try:
            # Get status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get branch info
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "current_hash": self.get_current_git_hash(),
                "current_branch": branch_result.stdout.strip(),
                "status_lines": status_result.stdout.strip().split('\n') if status_result.stdout.strip() else [],
                "is_clean": not bool(status_result.stdout.strip()),
                "has_uncommitted_changes": bool(status_result.stdout.strip())
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "error": f"Git status failed: {e.stderr}",
                "current_hash": None,
                "current_branch": None,
                "status_lines": [],
                "is_clean": False,
                "has_uncommitted_changes": True
            }
    
    # ============================================================================
    # PROJECT CODE CHANGE DETECTION
    # ============================================================================
    
    def detect_project_code_changes(self) -> Dict[str, Any]:
        """
        Detect changes in project code since last known Git state
        Returns comprehensive change analysis for organizational reconciliation
        """
        # Get current Git state
        current_hash = self.get_current_git_hash()
        if not current_hash:
            return {
                "success": False,
                "error": "Could not determine current Git hash",
                "changes_detected": False
            }
        
        # Get last known state from database
        last_known_state = self._get_last_known_git_state()
        
        if not last_known_state or last_known_state["current_git_hash"] != current_hash:
            # Changes detected - analyze them
            changes = self._analyze_git_changes(
                last_known_state["current_git_hash"] if last_known_state else None,
                current_hash
            )
            
            # Update database with new state
            self._update_git_project_state(current_hash, changes)
            
            return {
                "success": True,
                "changes_detected": True,
                "last_known_hash": last_known_state["current_git_hash"] if last_known_state else None,
                "current_hash": current_hash,
                "change_summary": changes["summary"],
                "affected_files": changes["files"],
                "affected_themes": changes["themes"],
                "reconciliation_needed": len(changes["themes"]) > 0
            }
        
        return {
            "success": True,
            "changes_detected": False,
            "current_hash": current_hash,
            "message": "No changes detected since last session"
        }
    
    def _get_last_known_git_state(self) -> Optional[Dict[str, Any]]:
        """Get last known Git state from database"""
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT current_git_hash, last_sync_timestamp, change_summary, affected_themes
                FROM git_project_state 
                WHERE project_root_path = ?
                ORDER BY created_at DESC 
                LIMIT 1
            """, (str(self.project_root),))
            
            row = cursor.fetchone()
            if row:
                return {
                    "current_git_hash": row[0],
                    "last_sync_timestamp": row[1],
                    "change_summary": row[2],
                    "affected_themes": json.loads(row[3]) if row[3] else []
                }
            return None
            
        except Exception as e:
            print(f"Error getting last known Git state: {e}")
            return None
    
    def _analyze_git_changes(self, last_hash: Optional[str], current_hash: str) -> Dict[str, Any]:
        """
        Analyze Git changes between two commits
        Returns detailed change analysis including affected themes
        """
        try:
            if not last_hash:
                # First time setup - treat all existing files as baseline
                return {
                    "summary": "Initial Git state recorded",
                    "files": [],
                    "themes": [],
                    "change_types": {"baseline": True}
                }
            
            # Get changed files between commits
            diff_result = subprocess.run([
                "git", "diff", "--name-status", f"{last_hash}..{current_hash}"
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            changed_files = []
            change_types = {"added": 0, "modified": 0, "deleted": 0}
            
            for line in diff_result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 2:
                    status = parts[0]
                    file_path = parts[1]
                    
                    # Skip projectManagement files (organizational state)
                    if file_path.startswith('projectManagement/'):
                        continue
                    
                    change_type = self._get_change_type_from_status(status)
                    changed_files.append({
                        "path": file_path,
                        "status": status,
                        "type": change_type
                    })
                    
                    if change_type in change_types:
                        change_types[change_type] += 1
            
            # Analyze theme impact
            affected_themes = self._analyze_theme_impact(changed_files)
            
            # Generate summary
            summary = self._generate_change_summary(change_types, len(changed_files), affected_themes)
            
            return {
                "summary": summary,
                "files": changed_files,
                "themes": affected_themes,
                "change_types": change_types
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "summary": f"Error analyzing Git changes: {e.stderr}",
                "files": [],
                "themes": [],
                "change_types": {"error": True}
            }
    
    def _get_change_type_from_status(self, status: str) -> str:
        """Convert Git status code to change type"""
        if status.startswith('A'):
            return "added"
        elif status.startswith('M'):
            return "modified"
        elif status.startswith('D'):
            return "deleted"
        elif status.startswith('R'):
            return "renamed"
        else:
            return "modified"
    
    def _analyze_theme_impact(self, changed_files: List[Dict[str, Any]]) -> List[str]:
        """
        Analyze which themes are affected by the changed files
        This integrates with the theme management system to determine impact
        """
        try:
            affected_themes = set()
            theme_files = {}
            
            # Load existing themes to analyze file relationships
            themes_dir = self.project_root / "projectManagement" / "Themes"
            if themes_dir.exists():
                themes_json_path = themes_dir / "themes.json"
                if themes_json_path.exists():
                    try:
                        with open(themes_json_path, 'r') as f:
                            theme_files = json.load(f)
                    except (json.JSONDecodeError, FileNotFoundError):
                        theme_files = {}
            
            # Analyze each changed file for theme impact
            for file_change in changed_files:
                file_path = file_change["path"]
                change_type = file_change["type"]
                
                # Direct theme impact analysis
                file_themes = self._get_themes_for_file(file_path, theme_files)
                affected_themes.update(file_themes)
                
                # Directory-based theme inference
                dir_themes = self._infer_themes_from_directory(file_path)
                affected_themes.update(dir_themes)
                
                # File extension and naming pattern analysis
                pattern_themes = self._infer_themes_from_patterns(file_path)
                affected_themes.update(pattern_themes)
                
                # Special handling for deleted files
                if change_type == "deleted":
                    deletion_themes = self._analyze_deletion_impact(file_path, theme_files)
                    affected_themes.update(deletion_themes)
            
            return list(affected_themes)
            
        except Exception as e:
            print(f"Error analyzing theme impact: {e}")
            return []
    
    def _get_themes_for_file(self, file_path: str, theme_files: Dict[str, Any]) -> List[str]:
        """Get themes that explicitly reference this file"""
        themes = []
        for theme_name, theme_data in theme_files.items():
            if isinstance(theme_data, dict) and "files" in theme_data:
                theme_file_list = theme_data.get("files", [])
                if file_path in theme_file_list or any(file_path.endswith(f) for f in theme_file_list):
                    themes.append(theme_name)
        return themes
    
    def _infer_themes_from_directory(self, file_path: str) -> List[str]:
        """Infer themes based on directory structure"""
        themes = []
        path_parts = Path(file_path).parts
        
        # Common directory name to theme mappings
        directory_mappings = {
            "auth": ["authentication", "security"],
            "authentication": ["authentication", "security"],
            "login": ["authentication"],
            "user": ["user-management", "authentication"],
            "users": ["user-management"],
            "profile": ["user-management"],
            "payment": ["payment", "billing"],
            "billing": ["payment", "billing"],
            "checkout": ["payment", "checkout"],
            "cart": ["shopping-cart", "commerce"],
            "api": ["api", "backend"],
            "database": ["database", "data"],
            "db": ["database", "data"],
            "ui": ["ui", "frontend"],
            "components": ["ui", "frontend"],
            "frontend": ["frontend"],
            "backend": ["backend"],
            "admin": ["admin", "management"],
            "dashboard": ["dashboard", "admin"],
            "config": ["configuration"],
            "settings": ["configuration", "settings"],
            "test": ["testing"],
            "tests": ["testing"],
            "security": ["security"],
            "middleware": ["api", "security"]
        }
        
        for part in path_parts:
            part_lower = part.lower()
            if part_lower in directory_mappings:
                themes.extend(directory_mappings[part_lower])
        
        return themes
    
    def _infer_themes_from_patterns(self, file_path: str) -> List[str]:
        """Infer themes based on file naming patterns and extensions"""
        themes = []
        filename = Path(file_path).name.lower()
        
        # File pattern to theme mappings
        pattern_mappings = {
            "auth": ["authentication"],
            "login": ["authentication"],
            "signup": ["authentication"],
            "register": ["authentication"],
            "password": ["authentication", "security"],
            "session": ["authentication", "session-management"],
            "user": ["user-management"],
            "profile": ["user-management"],
            "payment": ["payment"],
            "billing": ["billing"],
            "invoice": ["billing"],
            "cart": ["shopping-cart"],
            "checkout": ["checkout"],
            "order": ["order-management"],
            "product": ["product-management"],
            "inventory": ["inventory"],
            "admin": ["admin"], 
            "dashboard": ["dashboard"],
            "api": ["api"],
            "middleware": ["api", "middleware"],
            "config": ["configuration"],
            "setting": ["configuration"],
            "database": ["database"],
            "migration": ["database"],
            "schema": ["database"],
            "test": ["testing"],
            "spec": ["testing"],
            "security": ["security"],
            "validation": ["validation"],
            "error": ["error-handling"],
            "log": ["logging"],
            "email": ["email", "notifications"],
            "notification": ["notifications"]
        }
        
        for pattern, pattern_themes in pattern_mappings.items():
            if pattern in filename:
                themes.extend(pattern_themes)
        
        return themes
    
    def _analyze_deletion_impact(self, file_path: str, theme_files: Dict[str, Any]) -> List[str]:
        """Analyze impact of file deletion on themes"""
        themes = []
        for theme_name, theme_data in theme_files.items():
            if isinstance(theme_data, dict) and "files" in theme_data:
                theme_file_list = theme_data.get("files", [])
                if file_path in theme_file_list:
                    themes.append(theme_name)
                    # Mark theme as needing review due to file deletion
        return themes
    
    def _generate_change_summary(self, change_types: Dict[str, int], total_files: int, affected_themes: List[str]) -> str:
        """Generate human-readable change summary"""
        if change_types.get("baseline"):
            return "Initial Git state recorded - no previous changes to analyze"
        
        if total_files == 0:
            return "No project code changes detected"
        
        parts = []
        if change_types.get("added", 0) > 0:
            parts.append(f"{change_types['added']} files added")
        if change_types.get("modified", 0) > 0:
            parts.append(f"{change_types['modified']} files modified")
        if change_types.get("deleted", 0) > 0:
            parts.append(f"{change_types['deleted']} files deleted")
        
        summary = f"Project code changes detected: {', '.join(parts)}"
        
        if affected_themes:
            summary += f" - Affected themes: {', '.join(affected_themes)}"
        
        return summary
    
    def _update_git_project_state(self, current_hash: str, changes: Dict[str, Any]) -> None:
        """Update database with current Git project state"""
        try:
            cursor = self.db_manager.connection.cursor()
            
            # Get last known hash for comparison
            last_known_hash = None
            last_state = self._get_last_known_git_state()
            if last_state:
                last_known_hash = last_state["current_git_hash"]
            
            # Insert new Git project state record
            cursor.execute("""
                INSERT INTO git_project_state (
                    project_root_path, current_git_hash, last_known_hash,
                    change_summary, affected_themes, reconciliation_status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(self.project_root),
                current_hash,
                last_known_hash,
                changes["summary"],
                json.dumps(changes["themes"]),
                "pending" if changes["themes"] else "completed"
            ))
            
            # Record individual file changes for impact tracking
            git_state_id = cursor.lastrowid
            for file_change in changes["files"]:
                # Analyze per-file theme impact
                file_themes = self._analyze_single_file_theme_impact(file_change["path"])
                
                cursor.execute("""
                    INSERT INTO git_change_impacts (
                        git_state_id, file_path, change_type, affected_themes
                    ) VALUES (?, ?, ?, ?)
                """, (
                    git_state_id,
                    file_change["path"],
                    file_change["type"],
                    json.dumps(file_themes)
                ))
            
            self.db_manager.connection.commit()
            
        except Exception as e:
            print(f"Error updating Git project state: {e}")
            self.db_manager.connection.rollback()
    
    # ============================================================================
    # ORGANIZATIONAL STATE RECONCILIATION
    # ============================================================================
    
    def reconcile_organizational_state_with_code(self, change_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconcile organizational state (themes, flows, tasks) with detected code changes
        This is called when project code changes are detected during session boot
        """
        if not change_analysis.get("reconciliation_needed", False):
            return {
                "success": True,
                "action": "none",
                "message": "No organizational reconciliation needed"
            }
        
        reconciliation_result = {
            "success": True,
            "action": "reconciled",
            "message": "",
            "affected_themes": change_analysis.get("affected_themes", []),
            "theme_updates": [],
            "flow_updates": [],
            "task_updates": [],
            "requires_user_review": False
        }
        
        try:
            affected_themes = change_analysis.get("affected_themes", [])
            changed_files = change_analysis.get("files", [])
            
            # 1. Update theme files with new file references
            theme_updates = self._update_themes_with_file_changes(affected_themes, changed_files)
            reconciliation_result["theme_updates"] = theme_updates
            
            # 2. Check and update flows based on changed files
            flow_updates = self._update_flows_with_file_changes(affected_themes, changed_files)
            reconciliation_result["flow_updates"] = flow_updates
            
            # 3. Update task status if implementation files changed
            task_updates = self._update_tasks_with_file_changes(changed_files)
            reconciliation_result["task_updates"] = task_updates
            
            # 4. Determine if user review is required
            requires_review = (
                len(theme_updates) > 0 or
                len(flow_updates) > 0 or
                any(change["type"] == "deleted" for change in changed_files) or
                len(affected_themes) > 3  # Many themes affected
            )
            
            reconciliation_result["requires_user_review"] = requires_review
            
            # Generate summary message
            changes_summary = []
            if theme_updates:
                changes_summary.append(f"{len(theme_updates)} theme files updated")
            if flow_updates:
                changes_summary.append(f"{len(flow_updates)} flow references updated")
            if task_updates:
                changes_summary.append(f"{len(task_updates)} task statuses updated")
            
            if changes_summary:
                reconciliation_result["message"] = f"Organizational state reconciled: {', '.join(changes_summary)}"
            else:
                reconciliation_result["message"] = f"Code changes analyzed - {len(affected_themes)} themes identified but no updates needed"
            
            if requires_review:
                reconciliation_result["message"] += " - User review recommended"
            
            return reconciliation_result
            
        except Exception as e:
            return {
                "success": False,
                "action": "error",
                "message": f"Error during organizational reconciliation: {str(e)}",
                "affected_themes": change_analysis.get("affected_themes", []),
                "requires_user_review": True
            }
    
    def _update_themes_with_file_changes(self, affected_themes: List[str], changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update theme files to reflect file changes"""
        theme_updates = []
        themes_dir = self.project_root / "projectManagement" / "Themes"
        
        if not themes_dir.exists():
            return theme_updates
        
        try:
            for theme_name in affected_themes:
                theme_file = themes_dir / f"{theme_name}.json"
                if not theme_file.exists():
                    continue
                
                # Load existing theme data
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)
                
                if not isinstance(theme_data, dict) or "files" not in theme_data:
                    continue
                
                current_files = set(theme_data.get("files", []))
                updated_files = current_files.copy()
                changes_made = False
                
                # Process file changes for this theme
                for file_change in changed_files:
                    file_path = file_change["path"]
                    change_type = file_change["type"]
                    
                    # Check if this file belongs to this theme
                    file_themes = self._get_themes_for_file(file_path, {theme_name: theme_data})
                    if theme_name not in file_themes:
                        # Check if file should be added based on inference
                        inferred_themes = (
                            self._infer_themes_from_directory(file_path) +
                            self._infer_themes_from_patterns(file_path)
                        )
                        if theme_name not in inferred_themes:
                            continue
                    
                    if change_type == "added" and file_path not in current_files:
                        updated_files.add(file_path)
                        changes_made = True
                    elif change_type == "deleted" and file_path in current_files:
                        updated_files.discard(file_path)
                        changes_made = True
                
                # Save updated theme file if changes were made
                if changes_made:
                    theme_data["files"] = sorted(list(updated_files))
                    theme_data["lastModified"] = datetime.now().isoformat()
                    
                    with open(theme_file, 'w') as f:
                        json.dump(theme_data, f, indent=2)
                    
                    theme_updates.append({
                        "theme": theme_name,
                        "files_added": len(updated_files) - len(current_files),
                        "files_removed": len(current_files) - len(updated_files),
                        "action": "updated"
                    })
            
            return theme_updates
            
        except Exception as e:
            print(f"Error updating themes with file changes: {e}")
            return []
    
    def _update_flows_with_file_changes(self, affected_themes: List[str], changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update flow references based on file changes"""
        flow_updates = []
        flows_dir = self.project_root / "projectManagement" / "ProjectFlow"
        
        if not flows_dir.exists():
            return flow_updates
        
        try:
            # Check flow-index.json for flows related to affected themes
            flow_index_path = flows_dir / "flow-index.json"
            if not flow_index_path.exists():
                return flow_updates
            
            with open(flow_index_path, 'r') as f:
                flow_index = json.load(f)
            
            flow_files = flow_index.get("flowFiles", [])
            
            for flow_info in flow_files:
                if not isinstance(flow_info, dict):
                    continue
                
                flow_file = flow_info.get("file", "")
                flow_themes = flow_info.get("primaryThemes", []) + flow_info.get("secondaryThemes", [])
                
                # Check if this flow is affected by theme changes
                if any(theme in affected_themes for theme in flow_themes):
                    flow_path = flows_dir / flow_file
                    if flow_path.exists():
                        # Mark flow for potential review
                        flow_updates.append({
                            "flow_file": flow_file,
                            "affected_themes": [t for t in flow_themes if t in affected_themes],
                            "action": "review_recommended"
                        })
            
            return flow_updates
            
        except Exception as e:
            print(f"Error updating flows with file changes: {e}")
            return []
    
    def _update_tasks_with_file_changes(self, changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update task status based on implementation file changes"""
        task_updates = []
        tasks_dir = self.project_root / "projectManagement" / "Tasks"
        
        if not tasks_dir.exists():
            return task_updates
        
        try:
            # Check active tasks for file references
            active_tasks_dir = tasks_dir / "active"
            if active_tasks_dir.exists():
                for task_file in active_tasks_dir.glob("TASK-*.json"):
                    try:
                        with open(task_file, 'r') as f:
                            task_data = json.load(f)
                        
                        if not isinstance(task_data, dict):
                            continue
                        
                        # Check if any changed files are referenced in task subtasks
                        subtasks = task_data.get("subtasks", [])
                        task_affected = False
                        
                        for subtask in subtasks:
                            if not isinstance(subtask, dict):
                                continue
                            
                            subtask_files = subtask.get("files", [])
                            for file_change in changed_files:
                                if file_change["path"] in subtask_files:
                                    task_affected = True
                                    break
                            
                            if task_affected:
                                break
                        
                        if task_affected:
                            # Mark task as potentially needing review
                            task_updates.append({
                                "task_file": task_file.name,
                                "task_id": task_data.get("taskId", "unknown"),
                                "action": "implementation_files_changed"
                            })
                    
                    except (json.JSONDecodeError, IOError):
                        continue
            
            return task_updates
            
        except Exception as e:
            print(f"Error updating tasks with file changes: {e}")
            return []
    
    def _analyze_single_file_theme_impact(self, file_path: str) -> List[str]:
        """Analyze theme impact for a single file"""
        try:
            themes = set()
            
            # Load existing theme data
            theme_files = {}
            themes_dir = self.project_root / "projectManagement" / "Themes"
            if themes_dir.exists():
                themes_json_path = themes_dir / "themes.json"
                if themes_json_path.exists():
                    try:
                        with open(themes_json_path, 'r') as f:
                            theme_files = json.load(f)
                    except (json.JSONDecodeError, FileNotFoundError):
                        theme_files = {}
            
            # Direct theme mapping
            direct_themes = self._get_themes_for_file(file_path, theme_files)
            themes.update(direct_themes)
            
            # Directory-based inference
            dir_themes = self._infer_themes_from_directory(file_path)
            themes.update(dir_themes)
            
            # Pattern-based inference
            pattern_themes = self._infer_themes_from_patterns(file_path)
            themes.update(pattern_themes)
            
            return list(themes)
            
        except Exception as e:
            print(f"Error analyzing single file theme impact for {file_path}: {e}")
            return []
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def validate_git_configuration(self) -> Dict[str, Any]:
        """Validate Git repository configuration for MCP compatibility"""
        validation_result = {
            "valid": True,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Check if Git is available
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            validation_result["valid"] = False
            validation_result["issues"].append("Git is not installed or not available in PATH")
            return validation_result
        
        # Check if repository exists
        if not self.is_git_repository():
            validation_result["issues"].append("No Git repository found at project root")
            validation_result["recommendations"].append("Run git init or initialize through MCP")
        
        # Check .gitignore for AI Project Manager patterns
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            if "projectManagement/UserSettings/" not in gitignore_content:
                validation_result["recommendations"].append("Update .gitignore with AI Project Manager patterns")
        else:
            validation_result["recommendations"].append("Create .gitignore with AI Project Manager patterns")
        
        return validation_result
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive Git repository information"""
        if not self.is_git_repository():
            return {"exists": False}
        
        try:
            # Get basic info
            current_hash = self.get_current_git_hash()
            status_info = self.get_git_status()
            
            # Get commit count
            commit_count_result = subprocess.run([
                "git", "rev-list", "--count", "HEAD"
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            # Get remote info
            remote_result = subprocess.run([
                "git", "remote", "-v"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return {
                "exists": True,
                "current_hash": current_hash,
                "current_branch": status_info.get("current_branch"),
                "is_clean": status_info.get("is_clean", False),
                "commit_count": int(commit_count_result.stdout.strip()) if commit_count_result.stdout.strip() else 0,
                "remotes": remote_result.stdout.strip().split('\n') if remote_result.stdout.strip() else [],
                "project_root": str(self.project_root)
            }
            
        except Exception as e:
            return {
                "exists": True,
                "error": f"Could not get repository info: {str(e)}"
            }
    
    # ============================================================================
    # AI BRANCH MANAGEMENT INTEGRATION
    # ============================================================================
    
    def ensure_ai_main_branch_exists(self) -> Dict[str, Any]:
        """
        Ensure the ai-pm-org-main branch exists with proper remote/local handling.
        Priority: Remote clone > Local restoration > Fresh creation
        """
        result = {
            "success": False,
            "action": "none",
            "message": "",
            "branch_created": False,
            "source": None
        }
        
        try:
            ai_main_branch = "ai-pm-org-main"
            user_main_branch = "main"
            
            # Check if ai-pm-org-main exists locally
            if self._branch_exists_local(ai_main_branch):
                result["success"] = True
                result["action"] = "exists"
                result["message"] = f"{ai_main_branch} already exists locally"
                result["source"] = "local"
                return result
            
            # Branch doesn't exist locally - check remote and previous state
            has_remote = self._has_remote_repository()
            remote_branch_exists = has_remote and self._branch_exists_remote(ai_main_branch)
            has_previous_state = self._has_previous_ai_state()
            
            if remote_branch_exists:
                # Priority 1: Clone from remote (team collaboration)
                result = self._clone_ai_branch_from_remote(ai_main_branch)
                
            elif has_previous_state and not remote_branch_exists:
                # Priority 2: Restore from previous local state
                result = self._restore_ai_organizational_state(ai_main_branch, user_main_branch)
                
            else:
                # Priority 3: Create fresh branch (first-time setup)
                result = self._create_fresh_ai_branch(ai_main_branch, user_main_branch)
            
            return result
            
        except Exception as e:
            result["message"] = f"Error ensuring AI main branch: {str(e)}"
            return result
    
    def _clone_ai_branch_from_remote(self, ai_main_branch: str) -> Dict[str, Any]:
        """Clone AI main branch from remote repository."""
        result = {
            "success": False,
            "action": "cloned_from_remote",
            "message": "",
            "branch_created": True,
            "source": "remote"
        }
        
        try:
            # Clone branch from remote
            subprocess.run([
                'git', 'checkout', '-b', ai_main_branch, f'origin/{ai_main_branch}'
            ], cwd=self.project_root, check=True, capture_output=True, text=True)
            
            result["success"] = True
            result["message"] = f"Cloned {ai_main_branch} from remote repository (team collaboration)"
            
            # Sync local database with remote organizational state
            self._sync_with_remote_ai_state()
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Failed to clone {ai_main_branch} from remote: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error cloning from remote: {str(e)}"
            return result
    
    def _restore_ai_organizational_state(self, ai_main_branch: str, user_main_branch: str) -> Dict[str, Any]:
        """Restore AI branch from previous local organizational state."""
        result = {
            "success": False,
            "action": "restored_from_local",
            "message": "",
            "branch_created": True,
            "source": "restoration"
        }
        
        try:
            # Create branch from user main but preserve organizational state
            subprocess.run([
                'git', 'checkout', '-b', ai_main_branch, user_main_branch
            ], cwd=self.project_root, check=True, capture_output=True, text=True)
            
            result["success"] = True
            result["message"] = f"Restored {ai_main_branch} with previous organizational state"
            
            # The organizational files should already exist from previous state
            # Just ensure database consistency
            self._validate_organizational_consistency()
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Failed to restore {ai_main_branch}: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error restoring organizational state: {str(e)}"
            return result
    
    def _create_fresh_ai_branch(self, ai_main_branch: str, user_main_branch: str) -> Dict[str, Any]:
        """Create fresh AI main branch for first-time setup."""
        result = {
            "success": False,
            "action": "created_fresh",
            "message": "",
            "branch_created": True,
            "source": "fresh"
        }
        
        try:
            # Create fresh branch from user main
            subprocess.run([
                'git', 'checkout', '-b', ai_main_branch, user_main_branch
            ], cwd=self.project_root, check=True, capture_output=True, text=True)
            
            result["success"] = True
            result["message"] = f"Created fresh {ai_main_branch} from {user_main_branch} (first-time setup)"
            
            # Initialize AI project management structure
            self._initialize_ai_structure_on_branch()
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Failed to create fresh {ai_main_branch}: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error creating fresh branch: {str(e)}"
            return result
    
    def switch_to_ai_branch(self, branch_name: str = "ai-pm-org-main") -> Dict[str, Any]:
        """Switch to AI main branch or specified AI branch for operations."""
        result = {
            "success": False,
            "previous_branch": None,
            "current_branch": None,
            "message": ""
        }
        
        try:
            # Get current branch before switching
            current_branch_result = subprocess.run([
                'git', 'rev-parse', '--abbrev-ref', 'HEAD'
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            result["previous_branch"] = current_branch_result.stdout.strip()
            
            # Switch to specified branch
            subprocess.run([
                'git', 'checkout', branch_name
            ], cwd=self.project_root, check=True, capture_output=True)
            
            result["success"] = True
            result["current_branch"] = branch_name
            result["message"] = f"Switched to branch: {branch_name}"
            
            return result
            
        except Exception as e:
            result["message"] = f"Error switching to branch {branch_name}: {str(e)}"
            return result
    
    def get_user_code_changes(self, ai_main_branch: str = "ai-pm-org-main", user_main_branch: str = "main") -> Dict[str, Any]:
        """
        Compare user's main branch with ai-pm-org-main to see user changes.
        Returns analysis of what the user has changed outside of AI management.
        """
        result = {
            "success": False,
            "changed_files": [],
            "change_summary": "",
            "themes_affected": [],
            "message": ""
        }
        
        try:
            # Ensure both branches exist
            if not self._branch_exists(ai_main_branch):
                result["message"] = f"AI main branch {ai_main_branch} does not exist"
                return result
                
            if not self._branch_exists(user_main_branch):
                result["message"] = f"User main branch {user_main_branch} does not exist"
                return result
            
            # Get diff between branches
            diff_result = subprocess.run([
                'git', 'diff', '--name-status',
                f'{ai_main_branch}..{user_main_branch}'
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            if not diff_result.stdout.strip():
                result["success"] = True
                result["message"] = "No changes detected between AI and user branches"
                return result
            
            # Parse changed files
            changed_files = []
            for line in diff_result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        status = parts[0]
                        file_path = parts[1]
                        changed_files.append({
                            "file": file_path,
                            "status": self._get_change_type_from_status(status),
                            "raw_status": status
                        })
            
            result["changed_files"] = changed_files
            
            # Analyze theme impact
            affected_themes = self._analyze_theme_impact(changed_files)
            result["themes_affected"] = affected_themes
            
            # Generate summary
            total_files = len(changed_files)
            change_types = {}
            for file in changed_files:
                change_type = file["status"]
                change_types[change_type] = change_types.get(change_type, 0) + 1
            
            result["change_summary"] = self._generate_change_summary(change_types, total_files, affected_themes)
            result["success"] = True
            result["message"] = f"Found {total_files} changed files affecting {len(affected_themes)} themes"
            
            return result
            
        except Exception as e:
            result["message"] = f"Error comparing user code changes: {str(e)}"
            return result
    
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists locally."""
        return self._branch_exists_local(branch_name)
    
    def _branch_exists_local(self, branch_name: str) -> bool:
        """Check if a branch exists locally."""
        try:
            result = subprocess.run([
                'git', 'branch', '--list', branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
        except Exception:
            return False
    
    def _branch_exists_remote(self, branch_name: str, remote_name: str = "origin") -> bool:
        """Check if a branch exists on the remote repository."""
        try:
            # First, try to fetch latest remote refs
            subprocess.run([
                'git', 'fetch', remote_name, '--quiet'
            ], cwd=self.project_root, capture_output=True, text=True, timeout=10)
            
            # Check if remote branch exists
            result = subprocess.run([
                'git', 'branch', '-r', '--list', f'{remote_name}/{branch_name}'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            # Network issues or no remote - return False
            return False
        except Exception:
            return False
    
    def _has_remote_repository(self, remote_name: str = "origin") -> bool:
        """Check if a remote repository is configured."""
        try:
            result = subprocess.run([
                'git', 'remote', 'get-url', remote_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
        except Exception:
            return False
    
    def _has_previous_ai_state(self) -> bool:
        """Check if there's evidence of previous AI Project Manager state."""
        try:
            # Check for projectManagement directory with content
            proj_mgmt_dir = self.project_root / "projectManagement"
            if proj_mgmt_dir.exists():
                # Check for key organizational files
                key_files = [
                    "ProjectBlueprint/blueprint.md",
                    "Themes/themes.json",
                    "Tasks/completion-path.json",
                    "project.db"
                ]
                
                if any((proj_mgmt_dir / key_file).exists() for key_file in key_files):
                    return True
            
            # Check database for previous sessions or branches
            try:
                cursor = self.db_manager.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM sessions WHERE project_root_path = ?", 
                             (str(self.project_root),))
                session_count = cursor.fetchone()[0]
                
                if session_count > 0:
                    return True
                    
                cursor.execute("SELECT COUNT(*) FROM git_project_state WHERE project_root_path = ?", 
                             (str(self.project_root),))
                git_state_count = cursor.fetchone()[0]
                
                if git_state_count > 0:
                    return True
                    
            except Exception:
                # Database might not exist yet
                pass
            
            # Check Git history for AI commits
            try:
                result = subprocess.run([
                    'git', 'log', '--oneline', '--grep=AI Project Manager', '--all'
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if result.stdout.strip():
                    return True
                    
            except Exception:
                pass
            
            return False
            
        except Exception:
            return False
    
    def _initialize_ai_structure_on_branch(self) -> None:
        """Initialize the AI project management structure on current branch."""
        try:
            # Create projectManagement directory structure if it doesn't exist
            proj_mgmt_dir = self.project_root / "projectManagement"
            proj_mgmt_dir.mkdir(exist_ok=True)
            
            # Basic AI metadata file
            ai_meta = {
                "branch_type": "ai-pm-org-main",
                "created_at": datetime.now().isoformat(),
                "description": "Canonical AI Project Manager organizational state"
            }
            
            with open(proj_mgmt_dir / ".ai-pm-meta.json", 'w') as f:
                json.dump(ai_meta, f, indent=2)
            
            # Commit the initial structure if there are changes
            status_result = subprocess.run([
                'git', 'status', '--porcelain'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if status_result.stdout.strip():
                subprocess.run(['git', 'add', 'projectManagement/'], cwd=self.project_root)
                subprocess.run([
                    'git', 'commit', '-m', 'Initialize AI Project Manager structure'
                ], cwd=self.project_root, capture_output=True)
                
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Warning: Could not initialize AI structure: {e}")
    
    def sync_ai_branch_metadata(self, branch_name: str) -> None:
        """Sync branch metadata with the simplified database."""
        try:
            # Extract branch number from name
            branch_number = None
            if branch_name.startswith('ai-pm-org-branch-'):
                try:
                    number_str = branch_name[17:]  # Remove 'ai-pm-org-branch-' prefix
                    branch_number = int(number_str)
                except ValueError:
                    pass
            
            # Insert or update branch metadata in database
            query = """
                INSERT OR REPLACE INTO git_branches 
                (branch_name, branch_number, created_at, status)
                VALUES (?, ?, CURRENT_TIMESTAMP, 'active')
            """
            
            self.db_manager.execute_query(query, (branch_name, branch_number))
            
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Warning: Could not sync branch metadata: {e}")
    
    def _sync_with_remote_ai_state(self) -> None:
        """Sync local database with remote organizational state after cloning."""
        try:
            # Update database to reflect that we're now working with remote state
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                INSERT INTO git_project_state (
                    project_root_path, current_git_hash, change_summary,
                    reconciliation_status
                ) VALUES (?, ?, ?, ?)
            """, (
                str(self.project_root),
                self.get_current_git_hash(),
                "Synced with remote AI organizational state",
                "completed"
            ))
            self.db_manager.connection.commit()
            
        except Exception as e:
            print(f"Warning: Could not sync remote AI state: {e}")
    
    def _validate_organizational_consistency(self) -> None:
        """Validate organizational file consistency after restoration."""
        try:
            # Basic validation that key organizational files exist
            proj_mgmt_dir = self.project_root / "projectManagement"
            if not proj_mgmt_dir.exists():
                proj_mgmt_dir.mkdir(exist_ok=True)
            
            # Ensure database exists and is accessible
            db_path = proj_mgmt_dir / "project.db"
            if db_path.exists():
                # Test database connectivity
                self.db_manager.connection.execute("SELECT 1").fetchone()
            
        except Exception as e:
            print(f"Warning: Organizational consistency validation failed: {e}")
    
    def create_work_branch(self, branch_number: int) -> Dict[str, Any]:
        """
        Create a new work branch from ai-pm-org-main (not user's main).
        This ensures work branches always clone the organizational state.
        """
        result = {
            "success": False,
            "action": "none",
            "message": "",
            "branch_name": None,
            "branch_created": False
        }
        
        try:
            ai_main_branch = "ai-pm-org-main"
            work_branch = f"ai-pm-org-branch-{branch_number}"
            
            # Ensure ai-pm-org-main exists first
            main_result = self.ensure_ai_main_branch_exists()
            if not main_result["success"]:
                result["message"] = f"Cannot create work branch: {main_result['message']}"
                return result
            
            # Check if work branch already exists
            if self._branch_exists_local(work_branch):
                result["success"] = True
                result["action"] = "exists"
                result["message"] = f"Work branch {work_branch} already exists"
                result["branch_name"] = work_branch
                return result
            
            # Switch to ai-pm-org-main first to ensure we're on the right base
            switch_result = self.switch_to_ai_branch(ai_main_branch)
            if not switch_result["success"]:
                result["message"] = f"Could not switch to {ai_main_branch}: {switch_result['message']}"
                return result
            
            # Create work branch from ai-pm-org-main (cloning organizational state)
            subprocess.run([
                'git', 'checkout', '-b', work_branch, ai_main_branch
            ], cwd=self.project_root, check=True, capture_output=True, text=True)
            
            # Create minimal branch metadata
            branch_metadata = {
                "branchId": work_branch,
                "branchNumber": branch_number,
                "createdFrom": ai_main_branch,
                "createdAt": datetime.now().isoformat(),
                "primaryThemes": [],
                "status": "active",
                "description": f"Work branch {branch_number} cloned from {ai_main_branch}"
            }
            
            metadata_path = self.project_root / ".ai-pm-meta.json"
            with open(metadata_path, 'w') as f:
                json.dump(branch_metadata, f, indent=2)
            
            # Commit the metadata
            subprocess.run(['git', 'add', '.ai-pm-meta.json'], cwd=self.project_root, check=True)
            subprocess.run([
                'git', 'commit', '-m', f'Initialize work branch {work_branch} metadata'
            ], cwd=self.project_root, check=True, capture_output=True)
            
            # Update database tracking
            self.sync_ai_branch_metadata(work_branch)
            
            result["success"] = True
            result["action"] = "created"
            result["message"] = f"Created work branch {work_branch} from {ai_main_branch}"
            result["branch_name"] = work_branch
            result["branch_created"] = True
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Git command failed creating work branch: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error creating work branch: {str(e)}"
            return result
    
    def get_next_branch_number(self) -> int:
        """Get the next available branch number for work branches."""
        try:
            # Get all existing AI work branches
            result = subprocess.run([
                'git', 'branch', '-a', '--list', 'ai-pm-org-branch-*'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            branch_numbers = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                # Extract branch name from output (remove * and whitespace)
                branch_name = line.strip().lstrip('* ').replace('remotes/origin/', '')
                
                # Extract number from branch name
                if branch_name.startswith('ai-pm-org-branch-'):
                    try:
                        number_str = branch_name[17:]  # Remove 'ai-pm-org-branch-' prefix
                        branch_numbers.append(int(number_str))
                    except ValueError:
                        continue
            
            # Return next available number
            if not branch_numbers:
                return 1
            else:
                return max(branch_numbers) + 1
                
        except Exception as e:
            print(f"Warning: Could not determine next branch number: {e}")
            return 1
    
    def create_next_work_branch(self) -> Dict[str, Any]:
        """Create a new work branch with the next available number."""
        next_number = self.get_next_branch_number()
        return self.create_work_branch(next_number)
    
    def list_ai_branches(self) -> Dict[str, Any]:
        """List all AI-related branches (local and remote)."""
        result = {
            "success": False,
            "branches": {
                "main": None,
                "work_branches": []
            },
            "message": ""
        }
        
        try:
            # Get all branches
            branch_result = subprocess.run([
                'git', 'branch', '-a'
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            ai_main_exists = False
            work_branches = []
            
            for line in branch_result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                # Clean branch name
                branch_name = line.strip().lstrip('* ').replace('remotes/origin/', '')
                is_current = line.strip().startswith('*')
                is_remote = 'remotes/origin/' in line
                
                if branch_name == 'ai-pm-org-main':
                    ai_main_exists = True
                    result["branches"]["main"] = {
                        "name": branch_name,
                        "current": is_current,
                        "remote": is_remote,
                        "local": not is_remote or self._branch_exists_local(branch_name)
                    }
                elif branch_name.startswith('ai-pm-org-branch-'):
                    # Extract branch number
                    try:
                        number_str = branch_name[17:]
                        branch_number = int(number_str)
                        work_branches.append({
                            "name": branch_name,
                            "number": branch_number,
                            "current": is_current,
                            "remote": is_remote,
                            "local": not is_remote or self._branch_exists_local(branch_name)
                        })
                    except ValueError:
                        continue
            
            # Sort work branches by number
            work_branches.sort(key=lambda x: x["number"])
            result["branches"]["work_branches"] = work_branches
            
            result["success"] = True
            result["message"] = f"Found {len(work_branches)} work branches"
            
            if not ai_main_exists:
                result["message"] += " (ai-pm-org-main not found)"
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Git command failed: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error listing AI branches: {str(e)}"
            return result