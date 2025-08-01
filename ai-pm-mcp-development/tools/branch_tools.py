"""
Branch Tools for AI Project Manager - Simple Git branch-based MCP tools.

Provides MCP tools for managing AI project instances using pure Git branches.
Replaces the complex instance management tools with simple Git operations.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
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
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.branch_manager = GitBranchManager(self.project_root)
    
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
                description="Merge an AI instance branch into the main AI organizational state",
                input_schema={
                    "type": "object",
                    "properties": {
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the branch to merge (e.g., 'ai-pm-org-branch-001')"
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
        """Merge an AI instance branch."""
        try:
            branch_name = arguments["branch_name"]
            project_path = arguments.get("project_path")
            
            branch_manager = self._get_branch_manager(project_path)
            
            result_message, success = branch_manager.merge_instance_branch(branch_name)
            
            if success:
                return f"✅ **Merge Successful!**\n" \
                       f"   Merged: {branch_name}\n" \
                       f"   {result_message}\n\n" \
                       f"💡 Consider deleting the branch with 'delete_instance_branch' if work is complete."
            else:
                if "conflict" in result_message.lower():
                    return f"⚠️ **Merge Conflicts Detected**\n" \
                           f"   Branch: {branch_name}\n" \
                           f"   {result_message}\n\n" \
                           f"🔧 **Next Steps:**\n" \
                           f"   1. Resolve conflicts manually in your Git client\n" \
                           f"   2. Use 'git add' to stage resolved files\n" \
                           f"   3. Use 'git commit' to complete the merge\n" \
                           f"   4. Run this tool again to verify completion"
                else:
                    return f"❌ **Merge Failed**\n" \
                           f"   Branch: {branch_name}\n" \
                           f"   Error: {result_message}"
                
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