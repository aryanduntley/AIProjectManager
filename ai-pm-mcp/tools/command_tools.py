#!/usr/bin/env python3
"""
Command Tools

MCP tools that implement the command system for better user experience.
These tools provide workflow-level approval and command discovery.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List

from ..core.mcp_api import ToolDefinition

logger = logging.getLogger(__name__)


class CommandTools:
    """MCP tools for command system and user workflow management."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.commands = {
            "status": {
                "description": "Get current project state and available options",
                "workflow": ["get_project_state_analysis"],
                "approval_level": "none"
            },
            "help": {
                "description": "Show all available commands with descriptions",
                "workflow": ["show_command_help"],
                "approval_level": "none"
            },
            "init": {
                "description": "Initialize AI project management (checks status first, suggests /resume if already set up)",
                "workflow": ["get_project_state_analysis", "check_existing_setup", "make_initialization_choice"],
                "approval_level": "workflow"
            },
            "resume": {
                "description": "Resume previous work and active tasks",
                "workflow": ["session_boot_with_git_detection", "task_list_active", "context_load_theme"],
                "approval_level": "workflow"
            },
            "tasks": {
                "description": "Show active tasks and progress",
                "workflow": ["task_list_active", "sidequest_list_active"],
                "approval_level": "none"
            },
            "newTask": {
                "description": "Create and start new task",
                "workflow": ["task_create", "context_load_theme", "flow_load_selective"],
                "approval_level": "workflow"
            },
            "analyze": {
                "description": "Full project analysis and theme discovery",
                "workflow": ["get_project_state_analysis", "theme_discover", "project_get_status"],
                "approval_level": "workflow"
            },
            "themes": {
                "description": "Show project themes and structure",
                "workflow": ["theme_list", "theme_get_context"],
                "approval_level": "none"
            },
            "flows": {
                "description": "Show user experience flows",
                "workflow": ["flow_index_create", "context_get_flows"],
                "approval_level": "none"
            },
            "branch": {
                "description": "Create AI work branch for parallel development",
                "workflow": ["create_instance_branch", "switch_to_branch"],
                "approval_level": "workflow"
            },
            "merge": {
                "description": "Merge AI work back to main branch",
                "workflow": ["get_branch_status", "merge_instance_branch"],
                "approval_level": "workflow"
            },
            "config": {
                "description": "Show current configuration settings",
                "workflow": ["get_config"],
                "approval_level": "none"
            },
            "deploy": {
                "description": "Deploy AI improvements to your main branch (merges ai-pm-org-main → user's main)",
                "workflow": ["get_branch_status", "git_merge_ai_main_to_user"],
                "approval_level": "workflow"
            }
        }
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all command tools."""
        return [
            ToolDefinition(
                name="help_commands",
                description="Show all available AI Project Manager commands and their descriptions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Specific command to get help for (optional)",
                            "enum": list(self.commands.keys())
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format",
                            "enum": ["detailed", "quick", "json"],
                            "default": "detailed"
                        }
                    }
                },
                handler=self.help_commands
            ),
            ToolDefinition(
                name="execute_command",
                description="Execute an AI Project Manager command with workflow-level approval",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command to execute",
                            "enum": list(self.commands.keys())
                        },
                        "args": {
                            "type": "object",
                            "description": "Arguments for the command",
                            "default": {}
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Project directory path",
                            "default": "."
                        }
                    },
                    "required": ["command"]
                },
                handler=self.execute_command
            ),
            ToolDefinition(
                name="command_status",
                description="Get project state and show available next steps (implements /status command)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Project directory path",
                            "default": "."
                        }
                    }
                },
                handler=self.command_status
            )
        ]
    
    async def help_commands(self, arguments: Dict[str, Any]) -> str:
        """Show available commands and their descriptions."""
        try:
            command = arguments.get("command")
            format_type = arguments.get("format", "detailed")
            
            if command:
                return self._format_single_command_help(command, format_type)
            else:
                return self._format_all_commands_help(format_type)
                
        except Exception as e:
            logger.error(f"Error in help_commands: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error showing help: {str(e)}"
            }, indent=2)
    
    def _format_single_command_help(self, command: str, format_type: str) -> str:
        """Format help for a single command."""
        if command not in self.commands:
            return json.dumps({
                "type": "error",
                "message": f"Unknown command: {command}"
            }, indent=2)
        
        cmd_info = self.commands[command]
        
        if format_type == "json":
            return json.dumps({
                "type": "command_help",
                "command": command,
                "description": cmd_info["description"],
                "workflow": cmd_info["workflow"],
                "approval_level": cmd_info["approval_level"]
            }, indent=2)
        
        return f"""# /{command} Command Help

**Description**: {cmd_info["description"]}

**Approval Level**: {cmd_info["approval_level"]}
- `none`: No approval needed, executes immediately
- `workflow`: One-time approval for entire workflow

**Workflow Steps**:
{chr(10).join(f"  {i+1}. {step}" for i, step in enumerate(cmd_info["workflow"]))}

**Usage**: `/{command}` or use execute_command tool with command="{command}"
"""
    
    def _format_all_commands_help(self, format_type: str) -> str:
        """Format help for all commands."""
        if format_type == "json":
            return json.dumps({
                "type": "commands_help",
                "commands": self.commands
            }, indent=2)
        
        if format_type == "quick":
            help_text = "# AI Project Manager Commands\n\n"
            for cmd, info in self.commands.items():
                help_text += f"**/{cmd}** - {info['description']}\n"
            return help_text
        
        # Detailed format
        help_text = """# 🎯 AI Project Manager Commands

## Getting Started
**`/status`** - Get current project state and available options
**`/help`** - Show all available commands with descriptions  
**`/init`** - Initialize AI project management for this project

## Task Management  
**`/resume`** - Resume previous work and active tasks
**`/tasks`** - Show active tasks and progress
**`/newTask <description>`** - Create and start new task

## Project Analysis
**`/analyze`** - Full project analysis and theme discovery
**`/themes`** - Show project themes and structure
**`/flows`** - Show user experience flows

## Advanced Features
**`/branch`** - Create AI work branch for parallel development
**`/merge`** - Merge AI work back to main branch
**`/deploy`** - Deploy AI improvements to your main branch (ai-pm-org-main → user's main)
**`/config`** - Show current configuration settings

## How Commands Work
Commands provide **workflow-level approval** - when you use a command like `/init`, you're approving the entire initialization workflow. The AI can then:
- ✅ Chain multiple MCP tools automatically
- ✅ Make decisions based on project data  
- ✅ Execute complex multi-step processes
- ✅ Operate autonomously within the approved workflow scope

## Usage Examples
```
User: "/status"
AI: [Shows project state and next steps]

User: "/init"  
AI: [Analyzes project → presents options → executes choice → sets up management]

User: "/resume"
AI: [Loads context → finds active tasks → continues work]
```

Use `help_commands` with a specific command name for detailed help on individual commands.
"""
        return help_text
    
    async def execute_command(self, arguments: Dict[str, Any]) -> str:
        """Execute a command with workflow-level approval."""
        try:
            command = arguments.get("command")
            args = arguments.get("args", {})
            project_path = Path(arguments.get("project_path", "."))
            
            if command not in self.commands:
                return json.dumps({
                    "type": "error",
                    "message": f"Unknown command: {command}. Use help_commands to see available commands."
                }, indent=2)
            
            cmd_info = self.commands[command]
            
            logger.info(f"Executing command: /{command}")
            
            # Execute the command workflow
            if command == "status":
                return await self._execute_status(project_path, args)
            elif command == "help":
                return await self.help_commands({"format": "detailed"})
            elif command == "init":
                return await self._execute_init(project_path, args)
            elif command == "resume":
                return await self._execute_resume(project_path, args)
            elif command == "tasks":
                return await self._execute_tasks(project_path, args)
            elif command == "analyze":
                return await self._execute_analyze(project_path, args)
            elif command == "themes":
                return await self._execute_themes(project_path, args)
            elif command == "flows":
                return await self._execute_flows(project_path, args)
            elif command == "branch":
                return await self._execute_branch(project_path, args)
            elif command == "merge":
                return await self._execute_merge(project_path, args)
            elif command == "config":
                return await self._execute_config(project_path, args)
            elif command == "deploy":
                return await self._execute_deploy(project_path, args)
            else:
                return json.dumps({
                    "type": "info",
                    "message": f"Command /{command} workflow: {cmd_info['workflow']}. Use individual MCP tools to execute."
                }, indent=2)
                
        except Exception as e:
            logger.error(f"Error in execute_command: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing command: {str(e)}"
            }, indent=2)
    
    async def command_status(self, arguments: Dict[str, Any]) -> str:
        """Get project state and show available next steps."""
        try:
            project_path = Path(arguments.get("project_path", "."))
            
            # Use existing initialization tools for state analysis
            from .initialization_tools import InitializationTools
            init_tools = InitializationTools(self.db_manager)
            
            # Get project state analysis
            state_result = await init_tools.get_project_state_analysis({
                "project_path": str(project_path),
                "force_full_analysis": False
            })
            
            # Parse the result and add command suggestions
            try:
                state_data = json.loads(state_result)
                if isinstance(state_data, dict) and "state" in state_data:
                    # Add command suggestions based on state
                    state_data["suggested_commands"] = self._get_command_suggestions(state_data["state"])
                    state_data["available_commands"] = list(self.commands.keys())
                    
                return json.dumps(state_data, indent=2)
            except:
                # If parsing fails, return original result with command info
                return f"""{state_result}

## Available Commands
Use `/help` to see all available commands, or try:
- `/init` - Initialize project management
- `/analyze` - Analyze project structure  
- `/tasks` - Show active tasks
"""
                
        except Exception as e:
            logger.error(f"Error in command_status: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error getting project status: {str(e)}",
                "suggested_commands": ["help", "init"]
            }, indent=2)
    
    def _get_command_suggestions(self, state: str) -> List[str]:
        """Get suggested commands based on project state."""
        if state == "no_structure":
            return ["init", "analyze"]
        elif state == "partial":
            return ["init", "status", "analyze"]
        elif state == "complete":
            return ["resume", "tasks", "status"]
        elif state == "git_history_found":
            return ["init", "resume", "branch"]
        else:
            return ["help", "status", "analyze"]
    
    async def _execute_status(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /status command."""
        return await self.command_status({"project_path": str(project_path)})
    
    async def _execute_init(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /init command with status check and appropriate redirection."""
        try:
            from .initialization_tools import InitializationTools
            init_tools = InitializationTools(self.db_manager)
            
            # Get state analysis first
            state_result = await init_tools.get_project_state_analysis({
                "project_path": str(project_path)
            })
            
            # Check if project is already fully initialized
            try:
                state_data = json.loads(state_result)
                state = state_data.get("state", "unknown")
                
                # If project is already complete, suggest /resume instead
                if state == "complete":
                    return f"""# ℹ️ Project Already Initialized

## Current Status:
{state_result}

## 🔄 Did you mean `/resume`?

This project appears to already have AI Project Manager fully set up and running. 

**If you want to:**
- **Continue previous work** → Use `/resume` 
- **See current tasks** → Use `/tasks`
- **Check project status** → Use `/status`
- **Create work branch** → Use `/branch`

**If you really want to re-initialize:**
- Move or backup the existing `projectManagement/` directory first
- Then run `/init` again

## 💡 Recommended Next Step:
Try `/resume` to continue your previous work, or `/status` to see available options.
"""
                
                # Auto-select appropriate initialization choice for non-complete states
                if state == "no_structure":
                    choice = "initialize_project"
                elif state == "partial":
                    choice = "complete_initialization"
                elif state == "git_history_found":
                    choice = "join_team"  # or could be "create_branch"
                else:
                    choice = "initialize_project"
                
                # Execute the choice
                choice_result = await init_tools.make_initialization_choice({
                    "project_path": str(project_path),
                    "choice": choice,
                    "context": args
                })
                
                return f"""# /init Command Executed

## Project Analysis:
{state_result}

## Action Taken:
Choice: {choice}

## Result:
{choice_result}

## 🎯 Next Steps:
- Use `/resume` to start working with tasks
- Use `/branch` to create a work branch  
- Use `/tasks` to see active items
"""
            except Exception as parse_error:
                logger.warning(f"Failed to parse state analysis: {parse_error}")
                return f"""# /init Command - Analysis Complete

{state_result}

**Next Steps**: Use `make_initialization_choice` tool to select your preferred option.
"""
                
        except Exception as e:
            logger.error(f"Error in _execute_init: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /init command: {str(e)}"
            }, indent=2)
    
    async def _execute_resume(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /resume command."""
        try:
            # This would integrate with session manager and task tools
            return json.dumps({
                "type": "info",
                "message": "Resume command workflow: session_boot_with_git_detection → task_list_active → context_load_theme",
                "next_steps": "Use session_manager and task_tools to implement full resume workflow"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in _execute_resume: {e}")
            return json.dumps({
                "type": "error", 
                "message": f"Error executing /resume command: {str(e)}"
            }, indent=2)
    
    async def _execute_tasks(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /tasks command."""
        try:
            from .task_tools import TaskTools
            task_tools = TaskTools(self.db_manager)
            
            # Get active tasks
            active_result = await task_tools.list_active_tasks({"project_path": str(project_path)})
            
            return f"""# /tasks Command Result

## Active Tasks:
{active_result}

Use `/resume` to continue work on these tasks.
"""
            
        except Exception as e:
            logger.error(f"Error in _execute_tasks: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /tasks command: {str(e)}"
            }, indent=2)
    
    async def _execute_analyze(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /analyze command."""
        try:
            # This would integrate with theme discovery and project analysis tools
            return json.dumps({
                "type": "info",
                "message": "Analyze command workflow: get_project_state_analysis → theme_discover → project_get_status",
                "next_steps": "Use project_tools and theme_tools to implement full analysis workflow"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in _execute_analyze: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /analyze command: {str(e)}"
            }, indent=2)
    
    async def _execute_themes(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /themes command."""
        try:
            from .theme_tools import ThemeTools
            theme_tools = ThemeTools(self.db_manager)
            
            # List themes
            themes_result = await theme_tools.list_themes({"project_path": str(project_path)})
            
            return f"""# /themes Command Result

{themes_result}
"""
            
        except Exception as e:
            logger.error(f"Error in _execute_themes: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /themes command: {str(e)}"
            }, indent=2)
    
    async def _execute_flows(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /flows command."""
        try:
            from .flow_tools import FlowTools
            flow_tools = FlowTools(self.db_manager)
            
            # This would show flow index
            return json.dumps({
                "type": "info",
                "message": "Flows command workflow: flow_index_create → context_get_flows",
                "next_steps": "Use flow_tools to implement flow display"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in _execute_flows: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /flows command: {str(e)}"
            }, indent=2)
    
    async def _execute_config(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /config command."""
        try:
            from .config_tools import ConfigTools
            config_tools = ConfigTools(self.db_manager)
            
            # Get configuration
            config_result = await config_tools.get_config({})
            
            return f"""# /config Command Result

{config_result}
"""
            
        except Exception as e:
            logger.error(f"Error in _execute_config: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /config command: {str(e)}"
            }, indent=2)
    
    async def _execute_branch(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /branch command with safety checks."""
        try:
            from .branch_tools import BranchTools
            branch_tools = BranchTools(str(project_path))
            
            # First, get safety check information
            from ..core.branch_manager import GitBranchManager
            branch_manager = GitBranchManager(project_path)
            
            # Check workflow safety
            safety_check = branch_manager.check_workflow_safety()
            
            safety_report = f"""# /branch Command - Safety Check

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
            
            return f"""{safety_report}## ✅ Branch Creation Result:
{result}

## 🎯 Next Steps:
- Your new branch is ready for development
- Use `/merge` when ready to create a pull request
- Use `/tasks` to see current work items
"""
            
        except Exception as e:
            logger.error(f"Error in _execute_branch: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /branch command: {str(e)}"
            }, indent=2)
    
    async def _execute_merge(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /merge command with PR creation."""
        try:
            from .branch_tools import BranchTools
            branch_tools = BranchTools(str(project_path))
            
            # Get current branch info
            from ..core.branch_manager import GitBranchManager
            branch_manager = GitBranchManager(project_path)
            current_branch = branch_manager._get_current_branch()
            repo_info = branch_manager._detect_repository_type()
            
            merge_report = f"""# /merge Command - Pull Request Creation

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
Use `/branch` command to create a new AI work branch first.
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
"""
            
            if repo_info.get('gh_cli_available') and repo_info.get('is_github') and not force_direct:
                merge_report += """- ✅ Pull request created using GitHub CLI
- 🔄 Branch pushed to remote repository  
- 👥 Ready for team review and collaboration
- 🔗 PR URL provided above for tracking

## 🎯 Next Steps:
- Share the PR URL with your team for review
- Monitor the PR for feedback and approvals
- The PR will be merged by authorized team members
"""
            else:
                merge_report += """- ⚠️ Direct merge performed (GitHub CLI not available)
- 🔧 Consider setting up GitHub CLI for better collaboration
- 📝 Changes merged directly into ai-pm-org-main

## 🎯 Next Steps:
- Changes are now in the main AI branch
- Consider pushing changes to remote if working with a team
- Use `/branch` to create a new work branch for additional work
"""
            
            return merge_report
            
        except Exception as e:
            logger.error(f"Error in _execute_merge: {e}")
            return json.dumps({
                "type": "error", 
                "message": f"Error executing /merge command: {str(e)}"
            }, indent=2)
    
    async def _execute_deploy(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /deploy command to merge AI improvements to user's main branch."""
        try:
            from .branch_tools import BranchTools
            branch_tools = BranchTools(str(project_path))
            
            # Get current branch status
            from ..core.branch_manager import GitBranchManager
            branch_manager = GitBranchManager(project_path)
            current_branch = branch_manager.get_current_branch()
            
            deploy_report = f"""# /deploy Command - Deploy AI Improvements

## Current Status:
- **Current Branch**: {current_branch}
- **Operation**: Merging AI improvements from ai-pm-org-main → user's main branch
- **Purpose**: Deploy completed AI work to your production code

## 🚀 Deployment Process:
"""
            
            # Check if ai-pm-org-main exists
            if not branch_manager._branch_exists("ai-pm-org-main"):
                return f"""# /deploy Command - No AI Improvements Found

❌ **No AI Branch to Deploy**
- ai-pm-org-main branch not found
- Nothing to deploy to your main branch

🔧 **Next Steps:**
1. Use `/init` to set up AI project management
2. Use `/branch` to create AI work branches
3. Complete some AI improvements first
4. Then use `/deploy` to merge them to your main branch
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
- 🔒 Backup branch automatically created for safety
- 📝 Your main branch now contains all AI improvements
- 🎉 Deployment complete - your code has been enhanced by AI!

## 🔧 Next Steps:
1. **Test thoroughly** - Verify all changes work as expected
2. **Push to remote** - `git push origin main` (when ready)
3. **Continue development** - Create new AI work branches with `/branch`
4. **Iterate** - Use `/resume` to continue AI-assisted development

## 🛡️ Safety Features:
- Backup branch created before deployment
- Conflict detection and resolution guidance
- Rollback capability if needed
- Your original code is always preserved
"""
            
            return deploy_report
            
        except Exception as e:
            logger.error(f"Error in _execute_deploy: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /deploy command: {str(e)}"
            }, indent=2)