"""
Repository Management Module
Handles Git repository initialization, validation, and basic operations.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Import utilities from parent module paths
from ...utils.paths import load_template
from ...utils.project_paths import get_management_folder_name


class RepositoryManagement:
    """Git repository management operations."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties
        self.project_root = parent_instance.project_root
        self.db_manager = parent_instance.db_manager
        self.config_manager = parent_instance.config_manager
        self.server_instance = parent_instance.server_instance
        self.git_dir = parent_instance.git_dir
    
    # ============================================================================
    # GIT REPOSITORY MANAGEMENT
    # ============================================================================
    
    def is_git_repository(self) -> bool:
        """Check if project root is a Git repository"""
        return self.git_dir.exists() and self.git_dir.is_dir()
    
    async def initialize_git_repository(self) -> Dict[str, Any]:
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
                
                # Hook point: Git repository initialization completed
                if self.server_instance and hasattr(self.server_instance, 'on_core_operation_complete'):
                    await self._trigger_git_hook("git_repository_initialization_complete", {
                        "operation_type": "initialize_git_repository",
                        "git_action": result["action"],
                        "git_hash": result["git_hash"],
                        "created_files": result["created_files"],
                        "success": result["success"]
                    })
                
        except subprocess.CalledProcessError as e:
            result["message"] = f"Git command failed: {e.stderr}"
        except Exception as e:
            result["message"] = f"Git initialization error: {str(e)}"
            
        return result
    
    async def _trigger_git_hook(self, trigger: str, operation_data: Dict[str, Any]):
        """Helper method to trigger directive hooks for Git operations."""
        try:
            context = {
                "trigger": trigger,
                **operation_data,
                "project_root": str(self.project_root),
                "timestamp": datetime.now().isoformat()
            }
            await self.server_instance.on_core_operation_complete(context, "gitIntegration")
        except Exception as e:
            # Don't fail the Git operation if hook fails
            print(f"Git hook error: {e}")
    
    def _generate_mcp_gitignore(self) -> str:
        """Generate .gitignore content for Git branch-based AI Project Manager from template"""
        try:
            # Load gitignore content from template using the path utility
            template_content = load_template("project-gitignore-additions.txt")
            # Replace projectManagement with configured folder name
            management_folder = get_management_folder_name(self.config_manager)
            return template_content.replace("projectManagement", management_folder)
        except Exception as e:
            # Fallback to minimal hardcoded content if template can't be read
            # This ensures the system still works even if template is missing
            management_folder = get_management_folder_name(self.config_manager)
            return f"""
# AI Project Manager - Git Branch Based Management
# Track organizational state, not user-specific settings or temporary files

# MCP Server Infrastructure (tooling, not user code)
ai-pm-mcp/

# Project Management - Track Organizational State, Not User Data
# Note: {management_folder}/.ai-pm-config.json is tracked (branch-protected configuration)
{management_folder}/database/backups/
{management_folder}/.mcp-session-*
.tmp-ai-pm-config.json

# AI Project Manager temporary files
*.tmp
.ai-pm-temp/
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
            
            management_folder = get_management_folder_name(self.config_manager)
            if f"{management_folder}/database/backups/" not in gitignore_content:
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
    