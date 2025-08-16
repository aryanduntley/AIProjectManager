"""
Branch Remote Operations - Git remote interaction functionality.

Handles: push, pull, fetch, sync, check_remote_status operations
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


class RemoteOperationsHandler:
    """Handler for Git remote operations."""
    
    def __init__(self, branch_manager: GitBranchManager, server_instance=None):
        self.branch_manager = branch_manager
        self.server_instance = server_instance
        self.project_root = branch_manager.project_root
    
    def get_tools(self) -> List[ToolDefinition]:
        """Get remote operation tools."""
        return [
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
                handler=self.git_push_ai_main_remote
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
                handler=self.git_fetch_ai_main_updates
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
                handler=self.git_sync_ai_main_branch
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
                handler=self.git_pull_ai_main_changes
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
                handler=self.git_push_work_branch_remote
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
                handler=self.git_fetch_all_remotes
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
                handler=self.git_check_remote_status
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

    async def git_push_ai_main_remote(self, arguments: Dict[str, Any]) -> str:
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

    async def git_fetch_ai_main_updates(self, arguments: Dict[str, Any]) -> str:
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

    async def git_sync_ai_main_branch(self, arguments: Dict[str, Any]) -> str:
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

    async def git_pull_ai_main_changes(self, arguments: Dict[str, Any]) -> str:
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

    async def git_push_work_branch_remote(self, arguments: Dict[str, Any]) -> str:
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

    async def git_fetch_all_remotes(self, arguments: Dict[str, Any]) -> str:
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

    async def git_check_remote_status(self, arguments: Dict[str, Any]) -> str:
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