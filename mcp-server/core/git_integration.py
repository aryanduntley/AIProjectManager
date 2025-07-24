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
        """Generate .gitignore content for MCP instance management"""
        return """
# MCP Instance Management - Track Structure, Not Content
.mcp-instances/active/*/projectManagement/UserSettings/
.mcp-instances/active/*/projectManagement/database/backups/
.mcp-instances/*/logs/
.mcp-instances/*/temp/

# Project Management - Track Organizational State
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
                cursor.execute("""
                    INSERT INTO git_change_impacts (
                        git_state_id, file_path, change_type, affected_themes
                    ) VALUES (?, ?, ?, ?)
                """, (
                    git_state_id,
                    file_change["path"],
                    file_change["type"],
                    json.dumps([])  # TODO: Per-file theme impact analysis
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
        
        # TODO: Implement comprehensive organizational reconciliation
        # This would involve:
        # 1. Analyzing affected themes and updating theme files
        # 2. Checking if flows need updates based on changed files
        # 3. Updating task status if implementation files changed
        # 4. Notifying user of significant changes requiring review
        
        # For now, return basic reconciliation status
        return {
            "success": True,
            "action": "analyzed",
            "message": f"Code changes analyzed - {len(change_analysis.get('affected_themes', []))} themes potentially affected",
            "affected_themes": change_analysis.get("affected_themes", []),
            "requires_user_review": len(change_analysis.get("affected_themes", [])) > 0
        }
    
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
        
        # Check .gitignore for MCP patterns
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            if ".mcp-instances/" not in gitignore_content:
                validation_result["recommendations"].append("Update .gitignore with MCP instance management patterns")
        else:
            validation_result["recommendations"].append("Create .gitignore with MCP-specific patterns")
        
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
        Ensure the ai-pm-org-main branch exists.
        Creates it from user's main branch if it doesn't exist.
        """
        result = {
            "success": False,
            "action": "none",
            "message": "",
            "branch_created": False
        }
        
        try:
            ai_main_branch = "ai-pm-org-main"
            user_main_branch = "main"
            
            # Check if ai-pm-org-main exists
            if not self._branch_exists(ai_main_branch):
                # Create ai-pm-org-main from main
                subprocess.run([
                    'git', 'checkout', '-b', ai_main_branch, user_main_branch
                ], cwd=self.project_root, check=True, capture_output=True)
                
                result["success"] = True
                result["action"] = "created"
                result["message"] = f"Created {ai_main_branch} branch from {user_main_branch}"
                result["branch_created"] = True
                
                # Initialize AI project management structure on this branch
                self._initialize_ai_structure_on_branch()
                
            else:
                result["success"] = True
                result["action"] = "exists"
                result["message"] = f"{ai_main_branch} already exists"
                
            return result
            
        except Exception as e:
            result["message"] = f"Error ensuring AI main branch: {str(e)}"
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
        """Check if a branch exists."""
        try:
            result = subprocess.run([
                'git', 'branch', '--list', branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
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