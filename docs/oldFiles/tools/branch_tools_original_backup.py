"""
Branch Tools for AI Project Manager - Simple Git branch-based MCP tools.

Provides MCP tools for managing AI project instances using pure Git branches.
Replaces the complex instance management tools with simple Git operations.
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel

from ..core.branch_manager import GitBranchManager, BranchInfo

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Any = None


class BranchTools:
    """MCP tools for Git branch-based instance management."""
    
    def __init__(self, project_root: str = None, server_instance=None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.branch_manager = GitBranchManager(self.project_root)
        self.server_instance = server_instance
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all branch management tools."""
        return [
            ToolDefinition(
                name="create_instance_branch",
                description="Create a new AI instance branch for parallel development work",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    }
                },
                handler=self._create_instance_branch
            ),
            
            ToolDefinition(
                name="list_instance_branches",
                description="List all active AI instance branches with sequential numbering",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    }
                },
                handler=self._list_instance_branches
            ),
            
            ToolDefinition(
                name="merge_instance_branch",
                description="Merge an AI instance branch into the main AI organizational state using pull requests when possible",
                input_schema={
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the branch to merge (e.g., 'ai-pm-org-branch-001')"
                        },
                        "force_direct_merge": {
                            "type": "boolean",
                            "description": "Force direct merge instead of creating pull request (default: false)",
                            "default": False
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    },
                    "required": ["branch_name"]
                },
                handler=self._merge_instance_branch
            ),
            
            ToolDefinition(
                name="delete_instance_branch",
                description="Delete a completed AI instance branch",
                input_schema={
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the branch to delete"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force delete even if not merged (default: false)",
                            "default": False
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    },
                    "required": ["branch_name"]
                },
                handler=self._delete_instance_branch
            ),
            
            ToolDefinition(
                name="switch_to_branch",
                description="Switch to an AI instance branch to work on it",
                input_schema={
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the branch to switch to"
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    },
                    "required": ["branch_name"]
                },
                handler=self._switch_to_branch
            ),
            
            
            ToolDefinition(
                name="get_branch_status",
                description="Get detailed status information about AI branches and current state",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    }
                },
                handler=self._get_branch_status
            ),
            
            ToolDefinition(
                name="check_user_code_changes",
                description="Check if the user has made code changes outside of AI management",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    }
                },
                handler=self._check_user_code_changes
            ),
            
            # ========================================================================
            # NEW GIT REMOTE OPERATIONS TOOLS
            # ========================================================================
            
            ToolDefinition(
                name="git_push_ai_main_remote",
                description="Push ai-pm-org-main branch to remote origin repository",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force push (use with caution, default: false)",
                            "default": False
                        }
                    }
                },
                handler=self._git_push_ai_main_remote
            ),
            
            ToolDefinition(
                name="git_fetch_ai_main_updates",
                description="Fetch latest updates for ai-pm-org-main from remote origin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    }
                },
                handler=self._git_fetch_ai_main_updates
            ),
            
            ToolDefinition(
                name="git_sync_ai_main_branch",
                description="Synchronize local ai-pm-org-main with remote version (fetch + merge/rebase)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        },
                        "strategy": {
                            "type": "string",
                            "description": "Sync strategy: 'merge' or 'rebase' (default: merge)",
                            "enum": ["merge", "rebase"],
                            "default": "merge"
                        }
                    }
                },
                handler=self._git_sync_ai_main_branch
            ),
            
            ToolDefinition(
                name="git_pull_ai_main_changes",
                description="Pull latest changes from remote ai-pm-org-main (fetch + merge in one step)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    }
                },
                handler=self._git_pull_ai_main_changes
            ),
            
            ToolDefinition(
                name="git_setup_ai_main_from_user",
                description="Create and setup ai-pm-org-main branch from user's main branch",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        },
                        "user_main_branch": {
                            "type": "string",
                            "description": "Name of user's main branch (default: main)",
                            "default": "main"
                        }
                    }
                },
                handler=self._git_setup_ai_main_from_user
            ),
            
            ToolDefinition(
                name="git_clone_remote_ai_main",
                description="Clone/checkout existing remote ai-pm-org-main branch (for team collaboration setup)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    }
                },
                handler=self._git_clone_remote_ai_main
            ),
            
            ToolDefinition(
                name="git_push_work_branch_remote",
                description="Push ai-pm-org-branch-{XXX} work branch to remote origin",
                input_schema={
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the work branch to push (e.g., 'ai-pm-org-branch-001')"
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    },
                    "required": ["branch_name"]
                },
                handler=self._git_push_work_branch_remote
            ),
            
            ToolDefinition(
                name="git_fetch_all_remotes",
                description="Fetch updates from all configured remote repositories",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    }
                },
                handler=self._git_fetch_all_remotes
            ),
            
            ToolDefinition(
                name="git_check_remote_status",
                description="Check remote repository connection status and branch information",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        }
                    }
                },
                handler=self._git_check_remote_status
            ),
            
            ToolDefinition(
                name="git_merge_ai_main_to_user",
                description="Deploy AI improvements by merging ai-pm-org-main into user's main branch (primary workflow)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        },
                        "user_main_branch": {
                            "type": "string",
                            "description": "Name of user's main branch (default: main)",
                            "default": "main"
                        },
                        "create_backup": {
                            "type": "boolean",
                            "description": "Create backup branch before merging (default: true)",
                            "default": True
                        }
                    }
                },
                handler=self._git_merge_ai_main_to_user
            ),
            
            ToolDefinition(
                name="git_reconcile_user_changes",
                description="Reconciliation tool: merge user's main branch changes into ai-pm-org-main (use sparingly)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (optional, uses current if not provided)"
                        },
                        "user_main_branch": {
                            "type": "string",
                            "description": "Name of user's main branch (default: main)",
                            "default": "main"
                        }
                    }
                },
                handler=self._git_reconcile_user_changes
            )
        ]
    
    def _get_branch_manager(self, project_path: str = None) -> GitBranchManager:
        """Get branch manager for the specified project path."""
        if project_path:
            return GitBranchManager(Path(project_path))
        return self.branch_manager
    
    async def _create_instance_branch(self, arguments: Dict[str, Any]) -> str:
        """Create a new AI instance branch."""
        try:
            project_path = arguments.get("project_path")
            
            branch_manager = self._get_branch_manager(project_path)
            
            branch_name, success = branch_manager.create_instance_branch()
            
            if success:
                # Add directive hook for branch creation
                if self.server_instance and hasattr(self.server_instance, 'on_branch_operation_complete'):
                    context = {
                        "trigger": "branch_creation",
                        "operation_type": "create_instance_branch",
                        "branch_name": branch_name,
                        "project_path": str(project_path) if project_path else str(self.project_root),
                        "success": True,
                        "operation_details": {
                            "created_branch": branch_name,
                            "source_branch": "ai-pm-org-main",
                            "branch_type": "instance_branch"
                        }
                    }
                    await self.server_instance.on_branch_operation_complete(context, "branchManagement")
                
                return f"✅ Created AI instance branch: {branch_name}\n" \
                       f"   Ready for development work!"
            else:
                return f"❌ Failed to create branch '{branch_name}'\n" \
                       f"   Check that the project has Git initialized and ai-pm-org-main exists."
                
        except Exception as e:
            logger.error(f"Error in create_instance_branch: {e}")
            return f"❌ Error creating instance branch: {str(e)}"
    
    async def _list_instance_branches(self, arguments: Dict[str, Any]) -> str:
        """List all AI instance branches."""
        try:
            project_path = arguments.get("project_path")
            branch_manager = self._get_branch_manager(project_path)
            
            branches = branch_manager.list_instance_branches()
            current_branch = branch_manager.get_current_branch()
            
            if not branches:
                return "📋 No active AI instance branches found.\n" \
                       f"   Current branch: {current_branch}\n" \
                       f"   Use 'create_instance_branch' to start working on a new feature."
            
            result = "📋 **Active AI Instance Branches:**\n\n"
            
            for branch in branches:
                status_icon = "👉" if branch.is_current else "  "
                result += f"{status_icon} **{branch.name}**\n"
                if branch.is_current:
                    result += f"     ✨ Currently active\n"
                result += "\n"
            
            result += f"**Current branch:** {current_branch}\n"
            result += f"**Total branches:** {len(branches)}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error in list_instance_branches: {e}")
            return f"❌ Error listing branches: {str(e)}"
    
    async def _merge_instance_branch(self, arguments: Dict[str, Any]) -> str:
        """Merge an AI instance branch using pull requests when possible."""
        try:
            branch_name = arguments["branch_name"]
            force_direct_merge = arguments.get("force_direct_merge", False)
            project_path = arguments.get("project_path")
            
            branch_manager = self._get_branch_manager(project_path)
            
            result_message, success = branch_manager.merge_instance_branch(branch_name, force_direct_merge)
            
            if success:
                # Add directive hook for successful branch merge
                if self.server_instance and hasattr(self.server_instance, 'on_branch_operation_complete'):
                    context = {
                        "trigger": "branch_merge",
                        "operation_type": "merge_instance_branch", 
                        "branch_name": branch_name,
                        "project_path": str(project_path) if project_path else str(self.project_root),
                        "success": True,
                        "operation_details": {
                            "merged_branch": branch_name,
                            "target_branch": "ai-pm-org-main",
                            "merge_method": "pull_request" if not force_direct_merge else "direct_merge",
                            "force_direct_merge": force_direct_merge,
                            "result_message": result_message
                        }
                    }
                    await self.server_instance.on_branch_operation_complete(context, "branchManagement")
                
                # The result_message now contains formatted information about PR or direct merge
                return result_message
            else:
                if "conflict" in result_message.lower():
                    return f"⚠️ **Merge Conflicts Detected**\n\n{result_message}\n\n" \
                           f"🔧 **Next Steps:**\n" \
                           f"   1. Resolve conflicts manually in your Git client\n" \
                           f"   2. Use 'git add' to stage resolved files\n" \
                           f"   3. Use 'git commit' to complete the merge\n" \
                           f"   4. Run this tool again to verify completion"
                else:
                    return f"❌ **Merge Failed**\n\n{result_message}"
                
        except Exception as e:
            logger.error(f"Error in merge_instance_branch: {e}")
            return f"❌ Error merging branch: {str(e)}"
    
    async def _delete_instance_branch(self, arguments: Dict[str, Any]) -> str:
        """Delete an AI instance branch."""
        try:
            branch_name = arguments["branch_name"]
            force = arguments.get("force", False)
            project_path = arguments.get("project_path")
            
            branch_manager = self._get_branch_manager(project_path)
            
            result_message, success = branch_manager.delete_instance_branch(branch_name, force)
            
            if success:
                # Add directive hook for successful branch deletion
                if self.server_instance and hasattr(self.server_instance, 'on_branch_operation_complete'):
                    context = {
                        "trigger": "branch_deletion",
                        "operation_type": "delete_instance_branch",
                        "branch_name": branch_name,
                        "project_path": str(project_path) if project_path else str(self.project_root),
                        "success": True,
                        "operation_details": {
                            "deleted_branch": branch_name,
                            "force_delete": force,
                            "result_message": result_message
                        }
                    }
                    await self.server_instance.on_branch_operation_complete(context, "branchManagement")
                
                return f"✅ **Branch Deleted Successfully**\n" \
                       f"   Deleted: {branch_name}\n" \
                       f"   {result_message}"
            else:
                if "unmerged" in result_message.lower() or "not fully merged" in result_message.lower():
                    return f"⚠️ **Cannot Delete Unmerged Branch**\n" \
                           f"   Branch: {branch_name}\n" \
                           f"   {result_message}\n\n" \
                           f"🔧 **Options:**\n" \
                           f"   1. Merge the branch first with 'merge_instance_branch'\n" \
                           f"   2. Force delete with force=true (⚠️ will lose work!)"
                else:
                    return f"❌ **Delete Failed**\n" \
                           f"   Branch: {branch_name}\n" \
                           f"   Error: {result_message}"
                
        except Exception as e:
            logger.error(f"Error in delete_instance_branch: {e}")
            return f"❌ Error deleting branch: {str(e)}"
    
    async def _switch_to_branch(self, arguments: Dict[str, Any]) -> str:
        """Switch to an AI instance branch."""
        try:
            branch_name = arguments["branch_name"]
            project_path = arguments.get("project_path")
            
            branch_manager = self._get_branch_manager(project_path)
            
            result_message, success = branch_manager.switch_to_branch(branch_name)
            
            if success:
                return f"✅ **Switched to Branch**\n" \
                       f"   Active: {branch_name}\n" \
                       f"   Ready to continue work on this feature!"
            else:
                return f"❌ **Switch Failed**\n" \
                       f"   Branch: {branch_name}\n" \
                       f"   Error: {result_message}"
                
        except Exception as e:
            logger.error(f"Error in switch_to_branch: {e}")
            return f"❌ Error switching to branch: {str(e)}"
    
    
    async def _get_branch_status(self, arguments: Dict[str, Any]) -> str:
        """Get detailed branch status."""
        try:
            project_path = arguments.get("project_path")
            branch_manager = self._get_branch_manager(project_path)
            
            current_branch = branch_manager.get_current_branch()
            branches = branch_manager.list_instance_branches()
            
            result = f"📊 **AI Project Manager Branch Status**\n\n"
            result += f"**Current Branch:** {current_branch}\n"
            result += f"**Active Instance Branches:** {len(branches)}\n\n"
            
            if current_branch.startswith('ai-pm-org-'):
                if current_branch == 'ai-pm-org-main':
                    result += "🏠 **Status:** Working on main AI organizational state\n"
                    result += "   This is the canonical branch for AI project management.\n\n"
                else:
                    result += f"🔧 **Status:** Working on instance branch\n"
                    result += f"   All changes will be isolated to this branch.\n\n"
            else:
                result += f"⚠️ **Status:** On user code branch ({current_branch})\n"
                result += f"   Switch to ai-pm-org-main or create an instance branch for AI work.\n\n"
            
            if branches:
                result += "**Instance Branches:**\n"
                for branch in branches:
                    status = "👉 ACTIVE" if branch.is_current else "  "
                    result += f"{status} {branch.name}\n"
            else:
                result += "**No active instance branches found.**\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error in get_branch_status: {e}")
            return f"❌ Error getting branch status: {str(e)}"
    
    async def _check_user_code_changes(self, arguments: Dict[str, Any]) -> str:
        """Check for user code changes."""
        try:
            project_path = arguments.get("project_path")
            branch_manager = self._get_branch_manager(project_path)
            
            changed_files = branch_manager.get_user_code_changes()
            
            if not changed_files:
                return f"✅ **No User Code Changes Detected**\n" \
                       f"   User's main branch is in sync with AI organizational state.\n" \
                       f"   No reconciliation needed."
            else:
                result = f"📝 **User Code Changes Detected**\n\n"
                result += f"**Changed Files:** {len(changed_files)}\n"
                for file in changed_files[:10]:  # Limit to first 10 files
                    result += f"   • {file}\n"
                
                if len(changed_files) > 10:
                    result += f"   ... and {len(changed_files) - 10} more files\n"
                
                result += f"\n💡 **Recommendation:**\n"
                result += f"   Consider updating AI organizational state to reflect these changes.\n"
                result += f"   The system can help reconcile themes and flows with the new code structure."
                
                return result
                
        except Exception as e:
            logger.error(f"Error in check_user_code_changes: {e}")
            return f"❌ Error checking user code changes: {str(e)}"
    
    # ============================================================================
    # NEW GIT REMOTE OPERATIONS HANDLERS
    # ============================================================================
    
    async def _git_push_ai_main_remote(self, arguments: Dict[str, Any]) -> str:
        """Push ai-pm-org-main branch to remote origin repository."""
        try:
            project_path = arguments.get("project_path")
            force = arguments.get("force", False)
            
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Check if we're on ai-pm-org-main or switch to it
            current_branch = branch_manager.get_current_branch()
            if current_branch != "ai-pm-org-main":
                result = subprocess.run([
                    'git', 'checkout', 'ai-pm-org-main'
                ], cwd=project_root, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return f"❌ **Failed to switch to ai-pm-org-main**\n" \
                           f"   Error: {result.stderr}\n" \
                           f"   Current branch: {current_branch}"
            
            # Check if remote origin exists
            remote_check = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], cwd=project_root, capture_output=True, text=True)
            
            if remote_check.returncode != 0:
                return f"❌ **No Remote Origin Configured**\n" \
                       f"   Configure a remote origin first with:\n" \
                       f"   `git remote add origin <repository-url>`"
            
            remote_url = remote_check.stdout.strip()
            
            # Push to remote
            push_cmd = ['git', 'push', '-u', 'origin', 'ai-pm-org-main']
            if force:
                push_cmd.insert(2, '--force')  # Insert after 'push'
            
            result = subprocess.run(push_cmd, cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                return f"✅ **ai-pm-org-main Pushed Successfully!**\n" \
                       f"   Remote: {remote_url}\n" \
                       f"   Branch: ai-pm-org-main\n" \
                       f"   {'Force pushed' if force else 'Pushed'} to origin\n\n" \
                       f"   Team members can now access your AI organizational state!"
            else:
                if "rejected" in result.stderr or "non-fast-forward" in result.stderr:
                    return f"⚠️ **Push Rejected - Remote Has New Changes**\n" \
                           f"   Remote: {remote_url}\n" \
                           f"   Error: {result.stderr}\n\n" \
                           f"🔧 **Solutions:**\n" \
                           f"   1. Fetch and sync first: Use 'git_fetch_ai_main_updates'\n" \
                           f"   2. Force push (⚠️ overwrites remote): force=true\n" \
                           f"   3. Resolve conflicts manually"
                else:
                    return f"❌ **Push Failed**\n" \
                           f"   Remote: {remote_url}\n" \
                           f"   Error: {result.stderr}"
                    
        except Exception as e:
            logger.error(f"Error in git_push_ai_main_remote: {e}")
            return f"❌ Error pushing ai-pm-org-main to remote: {str(e)}"
    
    async def _git_fetch_ai_main_updates(self, arguments: Dict[str, Any]) -> str:
        """Fetch latest updates for ai-pm-org-main from remote origin."""
        try:
            project_path = arguments.get("project_path")
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Check if remote origin exists
            remote_check = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], cwd=project_root, capture_output=True, text=True)
            
            if remote_check.returncode != 0:
                return f"❌ **No Remote Origin Configured**\n" \
                       f"   Configure a remote origin first with:\n" \
                       f"   `git remote add origin <repository-url>`"
            
            remote_url = remote_check.stdout.strip()
            
            # Fetch ai-pm-org-main from remote
            result = subprocess.run([
                'git', 'fetch', 'origin', 'ai-pm-org-main'
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check if there are new changes
                diff_result = subprocess.run([
                    'git', 'rev-list', '--count', 'ai-pm-org-main..origin/ai-pm-org-main'
                ], cwd=project_root, capture_output=True, text=True)
                
                new_commits = 0
                if diff_result.returncode == 0 and diff_result.stdout.strip().isdigit():
                    new_commits = int(diff_result.stdout.strip())
                
                if new_commits > 0:
                    return f"✅ **Fetched {new_commits} New Changes!**\n" \
                           f"   Remote: {remote_url}\n" \
                           f"   Branch: ai-pm-org-main\n" \
                           f"   New commits available from origin\n\n" \
                           f"🔧 **Next Steps:**\n" \
                           f"   • Use 'git_sync_ai_main_branch' to merge changes\n" \
                           f"   • Use 'git_pull_ai_main_changes' for fetch+merge in one step"
                else:
                    return f"✅ **Already Up to Date**\n" \
                           f"   Remote: {remote_url}\n" \
                           f"   Branch: ai-pm-org-main\n" \
                           f"   No new changes available from origin"
            else:
                return f"❌ **Fetch Failed**\n" \
                       f"   Remote: {remote_url}\n" \
                       f"   Error: {result.stderr}"
                    
        except Exception as e:
            logger.error(f"Error in git_fetch_ai_main_updates: {e}")
            return f"❌ Error fetching ai-pm-org-main updates: {str(e)}"
    
    async def _git_sync_ai_main_branch(self, arguments: Dict[str, Any]) -> str:
        """Synchronize local ai-pm-org-main with remote version (fetch + merge/rebase)."""
        try:
            project_path = arguments.get("project_path")
            strategy = arguments.get("strategy", "merge")
            
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Check if we're on ai-pm-org-main or switch to it
            current_branch = branch_manager.get_current_branch()
            if current_branch != "ai-pm-org-main":
                result = subprocess.run([
                    'git', 'checkout', 'ai-pm-org-main'
                ], cwd=project_root, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return f"❌ **Failed to switch to ai-pm-org-main**\n" \
                           f"   Error: {result.stderr}\n" \
                           f"   Current branch: {current_branch}"
            
            # First fetch the updates
            fetch_result = subprocess.run([
                'git', 'fetch', 'origin', 'ai-pm-org-main'
            ], cwd=project_root, capture_output=True, text=True)
            
            if fetch_result.returncode != 0:
                return f"❌ **Fetch Failed**\n" \
                       f"   Error: {fetch_result.stderr}"
            
            # Check if there are changes to sync
            diff_result = subprocess.run([
                'git', 'rev-list', '--count', 'ai-pm-org-main..origin/ai-pm-org-main'
            ], cwd=project_root, capture_output=True, text=True)
            
            if diff_result.returncode == 0 and diff_result.stdout.strip() == "0":
                return f"✅ **Already Synchronized**\n" \
                       f"   Branch: ai-pm-org-main\n" \
                       f"   No changes to sync from remote"
            
            # Perform merge or rebase
            if strategy == "rebase":
                sync_result = subprocess.run([
                    'git', 'rebase', 'origin/ai-pm-org-main'
                ], cwd=project_root, capture_output=True, text=True)
                operation = "rebased"
            else:
                sync_result = subprocess.run([
                    'git', 'merge', 'origin/ai-pm-org-main'
                ], cwd=project_root, capture_output=True, text=True)
                operation = "merged"
            
            if sync_result.returncode == 0:
                return f"✅ **Synchronization Complete!**\n" \
                       f"   Branch: ai-pm-org-main\n" \
                       f"   Strategy: {strategy}\n" \
                       f"   Successfully {operation} remote changes\n" \
                       f"   Local ai-pm-org-main is now up to date"
            else:
                if "CONFLICT" in sync_result.stdout or "conflict" in sync_result.stderr.lower():
                    return f"⚠️ **Sync Conflicts Detected**\n" \
                           f"   Strategy: {strategy}\n" \
                           f"   Conflicts need manual resolution\n\n" \
                           f"🔧 **Resolution Steps:**\n" \
                           f"   1. Resolve conflicts in affected files\n" \
                           f"   2. Use 'git add' to stage resolved files\n" \
                           f"   3. Use 'git {'rebase --continue' if strategy == 'rebase' else 'commit'}' to complete\n\n" \
                           f"**Conflict Details:**\n{sync_result.stdout}"
                else:
                    return f"❌ **Sync Failed**\n" \
                           f"   Strategy: {strategy}\n" \
                           f"   Error: {sync_result.stderr}"
                    
        except Exception as e:
            logger.error(f"Error in git_sync_ai_main_branch: {e}")
            return f"❌ Error syncing ai-pm-org-main branch: {str(e)}"
    
    async def _git_pull_ai_main_changes(self, arguments: Dict[str, Any]) -> str:
        """Pull latest changes from remote ai-pm-org-main (fetch + merge in one step)."""
        try:
            project_path = arguments.get("project_path")
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Check if we're on ai-pm-org-main or switch to it
            current_branch = branch_manager.get_current_branch()
            if current_branch != "ai-pm-org-main":
                result = subprocess.run([
                    'git', 'checkout', 'ai-pm-org-main'
                ], cwd=project_root, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return f"❌ **Failed to switch to ai-pm-org-main**\n" \
                           f"   Error: {result.stderr}\n" \
                           f"   Current branch: {current_branch}"
            
            # Pull changes from remote
            result = subprocess.run([
                'git', 'pull', 'origin', 'ai-pm-org-main'
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                if "Already up to date" in result.stdout:
                    return f"✅ **Already Up to Date**\n" \
                           f"   Branch: ai-pm-org-main\n" \
                           f"   No new changes from remote"
                else:
                    return f"✅ **Pull Complete!**\n" \
                           f"   Branch: ai-pm-org-main\n" \
                           f"   Successfully pulled and merged remote changes\n" \
                           f"   {result.stdout.strip()}"
            else:
                if "CONFLICT" in result.stdout or "conflict" in result.stderr.lower():
                    return f"⚠️ **Pull Conflicts Detected**\n" \
                           f"   Branch: ai-pm-org-main\n" \
                           f"   Conflicts need manual resolution\n\n" \
                           f"🔧 **Resolution Steps:**\n" \
                           f"   1. Resolve conflicts in affected files\n" \
                           f"   2. Use 'git add' to stage resolved files\n" \
                           f"   3. Use 'git commit' to complete the merge\n\n" \
                           f"**Conflict Details:**\n{result.stdout}"
                else:
                    return f"❌ **Pull Failed**\n" \
                           f"   Branch: ai-pm-org-main\n" \
                           f"   Error: {result.stderr}"
                    
        except Exception as e:
            logger.error(f"Error in git_pull_ai_main_changes: {e}")
            return f"❌ Error pulling ai-pm-org-main changes: {str(e)}"
    
    async def _git_setup_ai_main_from_user(self, arguments: Dict[str, Any]) -> str:
        """Create and setup ai-pm-org-main branch from user's main branch."""
        try:
            project_path = arguments.get("project_path")
            user_main_branch = arguments.get("user_main_branch", "main")
            
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Check if ai-pm-org-main already exists
            if branch_manager._branch_exists("ai-pm-org-main"):
                return f"⚠️ **ai-pm-org-main Already Exists**\n" \
                       f"   Branch: ai-pm-org-main\n" \
                       f"   Use other tools to sync or manage the existing branch\n\n" \
                       f"🔧 **Available Actions:**\n" \
                       f"   • Switch to it: 'switch_to_branch'\n" \
                       f"   • Sync with remote: 'git_sync_ai_main_branch'\n" \
                       f"   • Check status: 'get_branch_status'"
            
            # Check if user's main branch exists
            user_branch_check = subprocess.run([
                'git', 'branch', '--list', user_main_branch
            ], cwd=project_root, capture_output=True, text=True)
            
            if not user_branch_check.stdout.strip():
                return f"❌ **User Branch Not Found**\n" \
                       f"   Branch: {user_main_branch}\n" \
                       f"   Available branches:\n" \
                       f"   {self._list_available_branches(project_root)}"
            
            # Create ai-pm-org-main from user's main branch
            result = subprocess.run([
                'git', 'checkout', '-b', 'ai-pm-org-main', user_main_branch
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Initialize basic AI project management structure if needed
                success_message = f"✅ **ai-pm-org-main Created Successfully!**\n" \
                                f"   Created from: {user_main_branch}\n" \
                                f"   New branch: ai-pm-org-main\n" \
                                f"   Ready for AI project management\n\n" \
                                f"🎯 **Next Steps:**\n" \
                                f"   • Initialize project management: Use project initialization tools\n" \
                                f"   • Create work branches: Use 'create_instance_branch'\n" \
                                f"   • Push to remote: Use 'git_push_ai_main_remote'"
                
                return success_message
            else:
                return f"❌ **Failed to Create ai-pm-org-main**\n" \
                       f"   Error: {result.stderr}\n" \
                       f"   Source branch: {user_main_branch}"
                    
        except Exception as e:
            logger.error(f"Error in git_setup_ai_main_from_user: {e}")
            return f"❌ Error setting up ai-pm-org-main from user branch: {str(e)}"
    
    async def _git_clone_remote_ai_main(self, arguments: Dict[str, Any]) -> str:
        """Clone/checkout existing remote ai-pm-org-main branch (for team collaboration setup)."""
        try:
            project_path = arguments.get("project_path")
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Check if ai-pm-org-main already exists locally
            if branch_manager._branch_exists("ai-pm-org-main"):
                return f"⚠️ **ai-pm-org-main Already Exists Locally**\n" \
                       f"   Local branch: ai-pm-org-main\n" \
                       f"   Use 'git_sync_ai_main_branch' to sync with remote instead\n\n" \
                       f"🔧 **Alternative Actions:**\n" \
                       f"   • Sync with remote: 'git_sync_ai_main_branch'\n" \
                       f"   • Check remote status: 'git_check_remote_status'"
            
            # Check if remote origin exists
            remote_check = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], cwd=project_root, capture_output=True, text=True)
            
            if remote_check.returncode != 0:
                return f"❌ **No Remote Origin Configured**\n" \
                       f"   Configure a remote origin first with:\n" \
                       f"   `git remote add origin <repository-url>`"
            
            remote_url = remote_check.stdout.strip()
            
            # Fetch remote to make sure we have latest info
            fetch_result = subprocess.run([
                'git', 'fetch', 'origin'
            ], cwd=project_root, capture_output=True, text=True)
            
            if fetch_result.returncode != 0:
                return f"❌ **Failed to Fetch Remote**\n" \
                       f"   Remote: {remote_url}\n" \
                       f"   Error: {fetch_result.stderr}"
            
            # Check if remote ai-pm-org-main exists
            remote_branch_check = subprocess.run([
                'git', 'branch', '-r', '--list', 'origin/ai-pm-org-main'
            ], cwd=project_root, capture_output=True, text=True)
            
            if not remote_branch_check.stdout.strip():
                return f"❌ **Remote ai-pm-org-main Not Found**\n" \
                       f"   Remote: {remote_url}\n" \
                       f"   Branch: origin/ai-pm-org-main\n" \
                       f"   Team member may need to push ai-pm-org-main first\n\n" \
                       f"📋 **Available Remote Branches:**\n" \
                       f"   {self._list_remote_branches(project_root)}"
            
            # Create and checkout local ai-pm-org-main from remote
            result = subprocess.run([
                'git', 'checkout', '-b', 'ai-pm-org-main', 'origin/ai-pm-org-main'
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                return f"✅ **Remote ai-pm-org-main Cloned Successfully!**\n" \
                       f"   Remote: {remote_url}\n" \
                       f"   Branch: ai-pm-org-main\n" \
                       f"   Team collaboration setup complete\n\n" \
                       f"🎯 **You Now Have Access To:**\n" \
                       f"   • Team's AI organizational state\n" \
                       f"   • Shared themes, flows, and tasks\n" \
                       f"   • Collaborative project management"
            else:
                return f"❌ **Failed to Clone Remote ai-pm-org-main**\n" \
                       f"   Remote: {remote_url}\n" \
                       f"   Error: {result.stderr}"
                    
        except Exception as e:
            logger.error(f"Error in git_clone_remote_ai_main: {e}")
            return f"❌ Error cloning remote ai-pm-org-main: {str(e)}"
    
    async def _git_push_work_branch_remote(self, arguments: Dict[str, Any]) -> str:
        """Push ai-pm-org-branch-{XXX} work branch to remote origin."""
        try:
            branch_name = arguments["branch_name"]
            project_path = arguments.get("project_path")
            
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Validate branch name format
            if not branch_name.startswith("ai-pm-org-branch-"):
                return f"❌ **Invalid Branch Name**\n" \
                       f"   Provided: {branch_name}\n" \
                       f"   Expected: ai-pm-org-branch-XXX format\n" \
                       f"   Example: ai-pm-org-branch-001"
            
            # Check if branch exists locally
            if not branch_manager._branch_exists(branch_name):
                return f"❌ **Branch Not Found Locally**\n" \
                       f"   Branch: {branch_name}\n" \
                       f"   Available branches:\n" \
                       f"   {self._list_available_branches(project_root)}"
            
            # Check if remote origin exists
            remote_check = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], cwd=project_root, capture_output=True, text=True)
            
            if remote_check.returncode != 0:
                return f"❌ **No Remote Origin Configured**\n" \
                       f"   Configure a remote origin first with:\n" \
                       f"   `git remote add origin <repository-url>`"
            
            remote_url = remote_check.stdout.strip()
            
            # Switch to the work branch if not already on it
            current_branch = branch_manager.get_current_branch()
            if current_branch != branch_name:
                checkout_result = subprocess.run([
                    'git', 'checkout', branch_name
                ], cwd=project_root, capture_output=True, text=True)
                
                if checkout_result.returncode != 0:
                    return f"❌ **Failed to switch to {branch_name}**\n" \
                           f"   Error: {checkout_result.stderr}"
            
            # Push work branch to remote
            result = subprocess.run([
                'git', 'push', '-u', 'origin', branch_name
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                branch_number = branch_manager._extract_branch_number(branch_name)
                return f"✅ **Work Branch Pushed Successfully!**\n" \
                       f"   Remote: {remote_url}\n" \
                       f"   Branch: {branch_name} (#{branch_number:03d})\n" \
                       f"   Ready for team collaboration or PR creation\n\n" \
                       f"🎯 **Next Steps:**\n" \
                       f"   • Create PR: Use existing merge tools\n" \
                       f"   • Continue development: Work on this branch\n" \
                       f"   • Share with team: Branch is now accessible to team members"
            else:
                return f"❌ **Push Failed**\n" \
                       f"   Branch: {branch_name}\n" \
                       f"   Remote: {remote_url}\n" \
                       f"   Error: {result.stderr}"
                    
        except Exception as e:
            logger.error(f"Error in git_push_work_branch_remote: {e}")
            return f"❌ Error pushing work branch to remote: {str(e)}"
    
    async def _git_fetch_all_remotes(self, arguments: Dict[str, Any]) -> str:
        """Fetch updates from all configured remote repositories."""
        try:
            project_path = arguments.get("project_path")
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Get list of remotes
            remotes_result = subprocess.run([
                'git', 'remote'
            ], cwd=project_root, capture_output=True, text=True)
            
            if remotes_result.returncode != 0:
                return f"❌ **Failed to Get Remote List**\n" \
                       f"   Error: {remotes_result.stderr}"
            
            remotes = remotes_result.stdout.strip().split('\n')
            if not remotes or not remotes[0]:
                return f"⚠️ **No Remote Repositories Configured**\n" \
                       f"   Configure a remote with:\n" \
                       f"   `git remote add origin <repository-url>`"
            
            # Fetch from all remotes
            result = subprocess.run([
                'git', 'fetch', '--all'
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                remote_info = []
                for remote in remotes:
                    if remote.strip():
                        # Get remote URL
                        url_result = subprocess.run([
                            'git', 'remote', 'get-url', remote.strip()
                        ], cwd=project_root, capture_output=True, text=True)
                        
                        if url_result.returncode == 0:
                            remote_info.append(f"   • {remote.strip()}: {url_result.stdout.strip()}")
                
                return f"✅ **Fetched From All Remotes!**\n" \
                       f"   Remotes ({len(remotes)}):\n" \
                       f"{''.join(info + chr(10) for info in remote_info)}" \
                       f"   All remote branches and tags updated\n\n" \
                       f"🎯 **Next Steps:**\n" \
                       f"   • Check remote status: 'git_check_remote_status'\n" \
                       f"   • Sync AI branch: 'git_sync_ai_main_branch'\n" \
                       f"   • View changes: Use standard git tools"
            else:
                return f"❌ **Fetch Failed**\n" \
                       f"   Error: {result.stderr}\n" \
                       f"   Some remotes may be unreachable"
                    
        except Exception as e:
            logger.error(f"Error in git_fetch_all_remotes: {e}")
            return f"❌ Error fetching from all remotes: {str(e)}"
    
    async def _git_check_remote_status(self, arguments: Dict[str, Any]) -> str:
        """Check remote repository connection status and branch information."""
        try:
            project_path = arguments.get("project_path")
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Get list of remotes
            remotes_result = subprocess.run([
                'git', 'remote', '-v'
            ], cwd=project_root, capture_output=True, text=True)
            
            if remotes_result.returncode != 0:
                return f"❌ **Failed to Get Remote Information**\n" \
                       f"   Error: {remotes_result.stderr}"
            
            if not remotes_result.stdout.strip():
                return f"⚠️ **No Remote Repositories Configured**\n" \
                       f"   Local repository only\n" \
                       f"   Configure remote with: `git remote add origin <url>`"
            
            # Check connectivity to origin (most common remote)
            connectivity_info = []
            origin_check = subprocess.run([
                'git', 'ls-remote', '--heads', 'origin'
            ], cwd=project_root, capture_output=True, text=True, timeout=10)
            
            if origin_check.returncode == 0:
                connectivity_info.append("   ✅ origin: Connected")
                
                # Check for ai-pm-org-main on remote
                if "ai-pm-org-main" in origin_check.stdout:
                    connectivity_info.append("   ✅ origin/ai-pm-org-main: Available")
                else:
                    connectivity_info.append("   ❌ origin/ai-pm-org-main: Not found")
                    
                # Count remote AI branches
                ai_branches = [line for line in origin_check.stdout.split('\n') 
                             if 'ai-pm-org-branch-' in line]
                connectivity_info.append(f"   📊 Remote AI work branches: {len(ai_branches)}")
            else:
                connectivity_info.append("   ❌ origin: Connection failed")
            
            # Get current branch status vs remote
            current_branch = branch_manager.get_current_branch()
            tracking_info = []
            
            if current_branch.startswith("ai-pm-org"):
                # Check tracking status
                status_result = subprocess.run([
                    'git', 'status', '-b', '--porcelain'
                ], cwd=project_root, capture_output=True, text=True)
                
                if status_result.returncode == 0:
                    status_lines = status_result.stdout.split('\n')
                    if status_lines:
                        branch_line = status_lines[0]
                        if "ahead" in branch_line:
                            tracking_info.append(f"   📤 {current_branch}: Has unpushed commits")
                        elif "behind" in branch_line:
                            tracking_info.append(f"   📥 {current_branch}: Behind remote")
                        elif "up to date" in branch_line or "up-to-date" in branch_line:
                            tracking_info.append(f"   ✅ {current_branch}: Up to date")
                        else:
                            tracking_info.append(f"   📊 {current_branch}: Status unclear")
            
            result = f"📡 **Remote Repository Status**\n\n"
            result += f"**Configured Remotes:**\n{remotes_result.stdout}\n"
            result += f"**Connectivity:**\n" + '\n'.join(connectivity_info) + "\n"
            
            if tracking_info:
                result += f"\n**Current Branch Status:**\n" + '\n'.join(tracking_info) + "\n"
            
            result += f"\n**Current Branch:** {current_branch}"
            
            return result
                    
        except subprocess.TimeoutExpired:
            return f"⚠️ **Remote Check Timeout**\n" \
                   f"   Remote repository may be unreachable\n" \
                   f"   Check network connection"
        except Exception as e:
            logger.error(f"Error in git_check_remote_status: {e}")
            return f"❌ Error checking remote status: {str(e)}"
    
    async def _git_merge_ai_main_to_user(self, arguments: Dict[str, Any]) -> str:
        """Deploy AI improvements by merging ai-pm-org-main into user's main branch (primary workflow)."""
        try:
            project_path = arguments.get("project_path")
            user_main_branch = arguments.get("user_main_branch", "main")
            create_backup = arguments.get("create_backup", True)
            
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Check if both branches exist
            if not branch_manager._branch_exists("ai-pm-org-main"):
                return f"❌ **ai-pm-org-main Branch Not Found**\n" \
                       f"   No AI improvements to deploy\n" \
                       f"   Create it first with: 'git_setup_ai_main_from_user'"
            
            user_branch_check = subprocess.run([
                'git', 'branch', '--list', user_main_branch
            ], cwd=project_root, capture_output=True, text=True)
            
            if not user_branch_check.stdout.strip():
                return f"❌ **User Branch Not Found**\n" \
                       f"   Branch: {user_main_branch}\n" \
                       f"   Available branches:\n" \
                       f"   {self._list_available_branches(project_root)}"
            
            # Create backup branch if requested
            backup_branch = None
            if create_backup:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_branch = f"backup_{user_main_branch}_{timestamp}"
                
                # Switch to user's main to create backup
                checkout_result = subprocess.run([
                    'git', 'checkout', user_main_branch
                ], cwd=project_root, capture_output=True, text=True)
                
                if checkout_result.returncode != 0:
                    return f"❌ **Failed to switch to {user_main_branch}**\n" \
                           f"   Error: {checkout_result.stderr}"
                
                # Create backup branch
                backup_result = subprocess.run([
                    'git', 'branch', backup_branch
                ], cwd=project_root, capture_output=True, text=True)
                
                if backup_result.returncode != 0:
                    return f"❌ **Failed to create backup branch**\n" \
                           f"   Error: {backup_result.stderr}"
            
            # Check if there are changes to merge
            diff_result = subprocess.run([
                'git', 'rev-list', '--count', f'{user_main_branch}..ai-pm-org-main'
            ], cwd=project_root, capture_output=True, text=True)
            
            if diff_result.returncode == 0 and diff_result.stdout.strip() == "0":
                backup_msg = f"\n   Backup created: {backup_branch}" if create_backup else ""
                return f"✅ **No AI Improvements to Deploy**\n" \
                       f"   {user_main_branch} already contains all AI changes\n" \
                       f"   No deployment needed{backup_msg}"
            
            # Get list of changed files for preview
            changed_files_result = subprocess.run([
                'git', 'diff', '--name-only', f'{user_main_branch}..ai-pm-org-main'
            ], cwd=project_root, capture_output=True, text=True)
            
            changed_files = []
            if changed_files_result.returncode == 0:
                changed_files = changed_files_result.stdout.strip().split('\n')
                changed_files = [f for f in changed_files if f.strip()]
            
            # Ensure we're on user's main branch
            current_branch = branch_manager.get_current_branch()
            if current_branch != user_main_branch:
                checkout_result = subprocess.run([
                    'git', 'checkout', user_main_branch
                ], cwd=project_root, capture_output=True, text=True)
                
                if checkout_result.returncode != 0:
                    return f"❌ **Failed to switch to {user_main_branch}**\n" \
                           f"   Error: {checkout_result.stderr}"
            
            # Perform the merge (AI improvements → User's main)
            result = subprocess.run([
                'git', 'merge', 'ai-pm-org-main', '-m', 
                f'Deploy AI improvements from ai-pm-org-main to {user_main_branch}'
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Add directive hook for successful AI deployment
                if self.server_instance and hasattr(self.server_instance, 'on_branch_operation_complete'):
                    context = {
                        "trigger": "ai_deployment",
                        "operation_type": "git_merge_ai_main_to_user",
                        "user_main_branch": user_main_branch,
                        "project_path": str(project_path) if project_path else str(self.project_root),
                        "success": True,
                        "operation_details": {
                            "source_branch": "ai-pm-org-main",
                            "target_branch": user_main_branch,
                            "backup_created": create_backup,
                            "backup_branch": backup_branch if create_backup else None,
                            "files_updated": len(changed_files),
                            "changed_files": changed_files,
                            "deployment_type": "ai_to_user"
                        }
                    }
                    await self.server_instance.on_branch_operation_complete(context, "branchManagement")
                
                backup_msg = f"   📋 **Backup Created**: {backup_branch}\n" if create_backup else ""
                return f"✅ **AI Improvements Deployed Successfully!**\n" \
                       f"   From: ai-pm-org-main\n" \
                       f"   Into: {user_main_branch}\n" \
                       f"   Files updated: {len(changed_files)}\n" \
                       f"   Deployment complete\n\n" \
                       f"{backup_msg}" \
                       f"📝 **Updated Files:**\n" \
                       f"   {chr(10).join(f'   • {f}' for f in changed_files[:10])}" \
                       f"{'   ... and more' if len(changed_files) > 10 else ''}\n\n" \
                       f"🎉 **Your main branch now contains all AI improvements!**\n" \
                       f"🔧 **Next Steps:**\n" \
                       f"   • Test your updated code\n" \
                       f"   • Push to remote if ready: git push origin {user_main_branch}\n" \
                       f"   • Continue development or create new AI work branches"
            else:
                if "CONFLICT" in result.stdout or "conflict" in result.stderr.lower():
                    backup_msg = f"\n   ⚠️  Backup available: {backup_branch}" if create_backup else ""
                    return f"⚠️ **Deployment Conflicts Detected**\n" \
                           f"   From: ai-pm-org-main\n" \
                           f"   Into: {user_main_branch}\n" \
                           f"   Manual resolution required{backup_msg}\n\n" \
                           f"🔧 **Resolution Steps:**\n" \
                           f"   1. Resolve conflicts in affected files\n" \
                           f"   2. Use 'git add' to stage resolved files\n" \
                           f"   3. Use 'git commit' to complete the deployment\n" \
                           f"   4. Test thoroughly before pushing\n\n" \
                           f"**Conflict Details:**\n{result.stdout}"
                else:
                    return f"❌ **Deployment Failed**\n" \
                           f"   From: ai-pm-org-main\n" \
                           f"   Into: {user_main_branch}\n" \
                           f"   Error: {result.stderr}"
                    
        except Exception as e:
            logger.error(f"Error in git_merge_ai_main_to_user: {e}")
            return f"❌ Error deploying AI improvements: {str(e)}"
    
    async def _git_reconcile_user_changes(self, arguments: Dict[str, Any]) -> str:
        """Reconciliation tool: merge user's main branch changes into ai-pm-org-main (use sparingly)."""
        try:
            project_path = arguments.get("project_path")
            user_main_branch = arguments.get("user_main_branch", "main")
            
            branch_manager = self._get_branch_manager(project_path)
            project_root = branch_manager.project_root
            
            # Check if both branches exist
            if not branch_manager._branch_exists("ai-pm-org-main"):
                return f"❌ **ai-pm-org-main Branch Not Found**\n" \
                       f"   Create it first with: 'git_setup_ai_main_from_user'"
            
            user_branch_check = subprocess.run([
                'git', 'branch', '--list', user_main_branch
            ], cwd=project_root, capture_output=True, text=True)
            
            if not user_branch_check.stdout.strip():
                return f"❌ **User Branch Not Found**\n" \
                       f"   Branch: {user_main_branch}\n" \
                       f"   Available branches:\n" \
                       f"   {self._list_available_branches(project_root)}"
            
            # Switch to ai-pm-org-main
            current_branch = branch_manager.get_current_branch()
            if current_branch != "ai-pm-org-main":
                checkout_result = subprocess.run([
                    'git', 'checkout', 'ai-pm-org-main'
                ], cwd=project_root, capture_output=True, text=True)
                
                if checkout_result.returncode != 0:
                    return f"❌ **Failed to switch to ai-pm-org-main**\n" \
                           f"   Error: {checkout_result.stderr}"
            
            # Check if there are changes to merge
            diff_result = subprocess.run([
                'git', 'rev-list', '--count', f'ai-pm-org-main..{user_main_branch}'
            ], cwd=project_root, capture_output=True, text=True)
            
            if diff_result.returncode == 0 and diff_result.stdout.strip() == "0":
                return f"✅ **Already Up to Date**\n" \
                       f"   ai-pm-org-main contains all changes from {user_main_branch}\n" \
                       f"   No reconciliation needed"
            
            # Get list of changed files for preview
            changed_files_result = subprocess.run([
                'git', 'diff', '--name-only', f'ai-pm-org-main..{user_main_branch}'
            ], cwd=project_root, capture_output=True, text=True)
            
            changed_files = []
            if changed_files_result.returncode == 0:
                changed_files = changed_files_result.stdout.strip().split('\n')
                changed_files = [f for f in changed_files if f.strip()]
            
            # Perform the merge
            result = subprocess.run([
                'git', 'merge', user_main_branch, '-m', 
                f'Reconcile user changes from {user_main_branch} into AI organizational state'
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Add directive hook for successful user change reconciliation
                if self.server_instance and hasattr(self.server_instance, 'on_branch_operation_complete'):
                    context = {
                        "trigger": "user_reconciliation",
                        "operation_type": "git_reconcile_user_changes",
                        "user_main_branch": user_main_branch,
                        "project_path": str(project_path) if project_path else str(self.project_root),
                        "success": True,
                        "operation_details": {
                            "source_branch": user_main_branch,
                            "target_branch": "ai-pm-org-main",
                            "files_changed": len(changed_files),
                            "changed_files": changed_files,
                            "reconciliation_type": "user_to_ai",
                            "requires_theme_update": True,
                            "requires_flow_update": True
                        }
                    }
                    await self.server_instance.on_branch_operation_complete(context, "branchManagement")
                
                return f"✅ **User Changes Merged Successfully!**\n" \
                       f"   From: {user_main_branch}\n" \
                       f"   Into: ai-pm-org-main\n" \
                       f"   Files changed: {len(changed_files)}\n" \
                       f"   Reconciliation complete\n\n" \
                       f"📝 **Changed Files:**\n" \
                       f"   {chr(10).join(f'   • {f}' for f in changed_files[:10])}" \
                       f"{'   ... and more' if len(changed_files) > 10 else ''}\n\n" \
                       f"🎯 **Next Steps:**\n" \
                       f"   • Update themes/flows to reflect changes\n" \
                       f"   • Push to remote: 'git_push_ai_main_remote'\n" \
                       f"   • Continue AI project management"
            else:
                if "CONFLICT" in result.stdout or "conflict" in result.stderr.lower():
                    return f"⚠️ **Merge Conflicts Detected**\n" \
                           f"   From: {user_main_branch}\n" \
                           f"   Into: ai-pm-org-main\n" \
                           f"   Manual resolution required\n\n" \
                           f"🔧 **Resolution Steps:**\n" \
                           f"   1. Resolve conflicts in affected files\n" \
                           f"   2. Use 'git add' to stage resolved files\n" \
                           f"   3. Use 'git commit' to complete the merge\n\n" \
                           f"**Conflict Details:**\n{result.stdout}"
                else:
                    return f"❌ **Merge Failed**\n" \
                           f"   From: {user_main_branch}\n" \
                           f"   Into: ai-pm-org-main\n" \
                           f"   Error: {result.stderr}"
                    
        except Exception as e:
            logger.error(f"Error in git_merge_user_main_to_ai: {e}")
            return f"❌ Error reconciling user changes to AI branch: {str(e)}"
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _list_available_branches(self, project_root: Path) -> str:
        """Get a formatted list of available branches."""
        try:
            result = subprocess.run([
                'git', 'branch', '--list'
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                branches = [line.strip().replace('*', '').strip() 
                          for line in result.stdout.split('\n') if line.strip()]
                return '\n'.join(f'   • {branch}' for branch in branches[:10])
            else:
                return "   Unable to list branches"
                
        except Exception as e:
            logger.error(f"Error listing available branches: {e}")
            return "   Error listing branches"
    
    def _list_remote_branches(self, project_root: Path) -> str:
        """Get a formatted list of remote branches."""
        try:
            result = subprocess.run([
                'git', 'branch', '-r', '--list'
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                branches = [line.strip() for line in result.stdout.split('\n') 
                          if line.strip() and 'origin/HEAD' not in line]
                return '\n'.join(f'   • {branch}' for branch in branches[:10])
            else:
                return "   Unable to list remote branches"
                
        except Exception as e:
            logger.error(f"Error listing remote branches: {e}")
            return "   Error listing remote branches"