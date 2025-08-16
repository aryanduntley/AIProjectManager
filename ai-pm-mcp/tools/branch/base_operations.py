"""
Branch Base Operations - Core branch management functionality.

Handles: create, list, merge, delete, switch, status, check_user_code_changes
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel

from ...core.branch_manager import GitBranchManager, BranchInfo

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Any = None


class BaseOperationsHandler:
    """Handler for core branch operations."""
    
    def __init__(self, branch_manager: GitBranchManager, server_instance=None):
        self.branch_manager = branch_manager
        self.server_instance = server_instance
        self.project_root = branch_manager.project_root
    
    def get_tools(self) -> List[ToolDefinition]:
        """Get core branch operation tools."""
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
                handler=self.create_instance_branch
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
                handler=self.list_instance_branches
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
                handler=self.merge_instance_branch
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
                handler=self.delete_instance_branch
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
                handler=self.switch_to_branch
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
                handler=self.get_branch_status
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
                handler=self.check_user_code_changes
            )
        ]
    
    def _get_branch_manager(self, project_path: str = None) -> GitBranchManager:
        """Get branch manager for the specified project path."""
        if project_path:
            return GitBranchManager(Path(project_path))
        return self.branch_manager

    async def create_instance_branch(self, arguments: Dict[str, Any]) -> str:
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

    async def list_instance_branches(self, arguments: Dict[str, Any]) -> str:
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

    async def merge_instance_branch(self, arguments: Dict[str, Any]) -> str:
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

    async def delete_instance_branch(self, arguments: Dict[str, Any]) -> str:
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

    async def switch_to_branch(self, arguments: Dict[str, Any]) -> str:
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

    async def get_branch_status(self, arguments: Dict[str, Any]) -> str:
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

    async def check_user_code_changes(self, arguments: Dict[str, Any]) -> str:
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