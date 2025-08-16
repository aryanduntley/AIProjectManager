"""
Branch Setup Operations - AI main branch setup and initialization.

Handles: setup_ai_main_from_user, clone_remote_ai_main
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel

from ...core.branch_manager import GitBranchManager

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Any = None


class SetupOperationsHandler:
    """Handler for AI main branch setup operations."""
    
    def __init__(self, branch_manager: GitBranchManager, server_instance=None):
        self.branch_manager = branch_manager
        self.server_instance = server_instance
        self.project_root = branch_manager.project_root
    
    def get_tools(self) -> List[ToolDefinition]:
        """Get setup operation tools."""
        return [
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
                handler=self.git_setup_ai_main_from_user
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
                handler=self.git_clone_remote_ai_main
            )
        ]
    
    def _get_branch_manager(self, project_path: str = None) -> GitBranchManager:
        """Get branch manager for the specified project path."""
        if project_path:
            return GitBranchManager(Path(project_path))
        return self.branch_manager

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

    async def git_setup_ai_main_from_user(self, arguments: Dict[str, Any]) -> str:
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

    async def git_clone_remote_ai_main(self, arguments: Dict[str, Any]) -> str:
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