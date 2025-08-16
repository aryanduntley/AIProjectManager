#!/usr/bin/env python3
"""
Git Workflow Command Handlers

Handles Git branch creation, merging, and deployment commands.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any
from .base_command import BaseCommandHandler

logger = logging.getLogger(__name__)


class GitCommandHandler(BaseCommandHandler):
    """Handles Git workflow commands."""
    
    async def execute_branch(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-branch command with safety checks."""
        try:
            from ..branch_tools import BranchTools
            branch_tools = BranchTools(str(project_path))
            
            # First, get safety check information
            from ...core.branch_manager import GitBranchManager
            branch_manager = GitBranchManager(project_path)
            
            # Check workflow safety
            safety_check = branch_manager.check_workflow_safety()
            
            safety_report = f"""# /aipm-branch Command - Safety Check

## Current Repository Status:
- **Repository Type**: {safety_check['repository_type']}
- **Current Branch**: {safety_check['current_branch']}
- **Overall Safety**: {'✅ Safe' if safety_check['safe'] else '⚠️ Issues Detected'}

"""
            
            # Report warnings if any
            if safety_check['warnings']:
                safety_report += "## ⚠️ Warnings:\n"
                for warning in safety_check['warnings']:
                    safety_report += f"- **{warning['severity'].upper()}**: {warning['message']}\n"
                safety_report += "\n"
            
            # Report recommendations if any
            if safety_check['recommendations']:
                safety_report += "## 💡 Recommendations:\n"
                for rec in safety_check['recommendations']:
                    safety_report += f"- {rec['message']}\n"
                safety_report += "\n"
            
            # If there are high-severity warnings, stop here
            high_severity_warnings = [w for w in safety_check['warnings'] if w.get('severity') == 'high']
            if high_severity_warnings:
                safety_report += "## ❌ Branch Creation Blocked\n"
                safety_report += "High-severity issues must be resolved before creating a branch.\n"
                safety_report += "Please follow the recommendations above.\n"
                return safety_report
            
            # Proceed with branch creation
            result = await branch_tools.create_instance_branch({})
            
            # Add directive hook after branch creation workflow completion
            await self._trigger_workflow_directive({
                "trigger": "workflow_completion",
                "workflow_type": "git_branch_creation",
                "command": "/aipm-branch",
                "project_path": str(project_path),
                "repository_type": safety_check.get('repository_type', 'unknown'),
                "current_branch": safety_check.get('current_branch', 'unknown'),
                "safety_status": safety_check.get('safe', False)
            })
            
            return f"""{safety_report}## ✅ Branch Creation Result:
{result}

## 🎯 Next Steps:
- Your new branch is ready for development
- Use `/aipm-merge` when ready to create a pull request
- Use `/tasks` to see current work items
"""
            
        except Exception as e:
            logger.error(f"Error in _execute_branch: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-branch command: {str(e)}"
            }, indent=2)
    
    async def execute_merge(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-merge command with PR creation."""
        try:
            from ..branch_tools import BranchTools
            branch_tools = BranchTools(str(project_path))
            
            # Get current branch info
            from ...core.branch_manager import GitBranchManager
            branch_manager = GitBranchManager(project_path)
            current_branch = branch_manager._get_current_branch()
            repo_info = branch_manager._detect_repository_type()
            
            merge_report = f"""# /aipm-merge Command - Pull Request Creation

## Current Status:
- **Current Branch**: {current_branch}
- **Repository Type**: {repo_info.get('type', 'unknown')}
- **GitHub CLI Available**: {'✅ Yes' if repo_info.get('gh_cli_available') else '❌ No'}
- **GitHub Repository**: {'✅ Yes' if repo_info.get('is_github') else '❌ No'}

"""
            
            # Check if we're on a work branch
            if not current_branch.startswith('ai-pm-org-branch-'):
                merge_report += f"""## ❌ Cannot Merge
You're currently on branch '{current_branch}' which is not an AI work branch.

### Valid branches for merging:
- Branches starting with 'ai-pm-org-branch-' (e.g., ai-pm-org-branch-001)

### To create a work branch:
Use `/aipm-branch` command to create a new AI work branch first.
"""
                return merge_report
            
            # Check if force direct merge was requested
            force_direct = args.get('force_direct_merge', False)
            
            # Proceed with merge/PR creation
            arguments = {
                'branch_name': current_branch,
                'force_direct_merge': force_direct
            }
            
            result = await branch_tools.merge_instance_branch(arguments)
            
            merge_report += f"""## 🚀 Merge Operation Result:
{result}

## 📋 What Happened:
The system attempted to create a pull request if GitHub CLI is available and this is a GitHub repository.
If PR creation wasn't possible, a direct merge may have been performed.

## 🎯 Next Steps:
- If a PR was created: Review and merge it on GitHub
- If direct merge occurred: The changes are now in ai-pm-org-main  
- Use `/aipm-deploy` when ready to merge ai-pm-org-main into your main branch
- Use `/aipm-branch` to create a new work branch for future development
"""
            
        except Exception as e:
            logger.error(f"Error in execute_merge: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-merge command: {str(e)}"
            }, indent=2)
    
    async def execute_deploy(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-deploy command to merge AI improvements to user's main branch."""
        try:
            from ..branch_tools import BranchTools
            branch_tools = BranchTools(str(project_path))
            
            # Get current branch status
            from ...core.branch_manager import GitBranchManager
            branch_manager = GitBranchManager(project_path)
            current_branch = branch_manager.get_current_branch()
            
            deploy_report = f"""# /aipm-deploy Command - Deploy AI Improvements

## Current Status:
- **Current Branch**: {current_branch}
- **Operation**: Merging AI improvements from ai-pm-org-main → user's main branch
- **Purpose**: Deploy completed AI work to your production code

## 🚀 Deployment Process:
"""
            
            # Check if ai-pm-org-main exists
            if not branch_manager._branch_exists("ai-pm-org-main"):
                return f"""# /aipm-deploy Command - No AI Improvements Found

❌ **No AI Branch to Deploy**
- ai-pm-org-main branch not found
- Nothing to deploy to your main branch

🔧 **Next Steps:**
1. Use `/aipm-init` to set up AI project management
2. Use `/aipm-branch` to create AI work branches
3. Complete some AI improvements first
4. Then use `/aipm-deploy` to merge them to your main branch
"""
            
            # Get deployment arguments with safety defaults
            arguments = {
                'project_path': str(project_path),
                'user_main_branch': args.get('user_main_branch', 'main'),
                'create_backup': args.get('create_backup', True)  # Always create backup by default
            }
            
            result = await branch_tools._git_merge_ai_main_to_user(arguments)
            
            deploy_report += f"""## 🎯 Deployment Result:
{result}

## 📋 What Happened:
- ✅ AI improvements merged from ai-pm-org-main into your main branch
- 🔄 A backup was created before deployment (if backup option was enabled)
- 📦 Your main branch now contains the latest AI improvements

## 🎯 Next Steps:
- Test your application to ensure everything works correctly
- Review the changes that were deployed
- Consider pushing the updated main branch to your remote repository
- Use `/aipm-branch` to create new work branches for future development

## 💡 Pro Tip:
Use `/aipm-backup` to create additional backups of important states.
"""
            
        except Exception as e:
            logger.error(f"Error in execute_deploy: {e}")
            return json.dumps({
                "type": "error", 
                "message": f"Error executing /aipm-deploy command: {str(e)}"
            }, indent=2)