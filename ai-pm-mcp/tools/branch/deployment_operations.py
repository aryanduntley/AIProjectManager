"""
Branch Deployment Operations - AI-User integration workflows.

Handles: git_merge_ai_main_to_user, git_reconcile_user_changes
These are the most critical operations for deploying AI improvements to user branches
and reconciling user changes back into the AI organizational state.
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ...core.branch_manager import GitBranchManager

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Any = None


class DeploymentOperationsHandler:
    """Handler for critical AI-User deployment operations."""
    
    def __init__(self, branch_manager: GitBranchManager, server_instance=None):
        self.branch_manager = branch_manager
        self.server_instance = server_instance
        self.project_root = branch_manager.project_root
    
    def get_tools(self) -> List[ToolDefinition]:
        """Get deployment operation tools."""
        return [
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
                handler=self.git_merge_ai_main_to_user
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
                handler=self.git_reconcile_user_changes
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

    async def git_merge_ai_main_to_user(self, arguments: Dict[str, Any]) -> str:
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
                        "project_path": str(project_path) if project_path else str(project_root),
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

    async def git_reconcile_user_changes(self, arguments: Dict[str, Any]) -> str:
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
                        "project_path": str(project_path) if project_path else str(project_root),
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
            logger.error(f"Error in git_reconcile_user_changes: {e}")
            return f"❌ Error reconciling user changes to AI branch: {str(e)}"