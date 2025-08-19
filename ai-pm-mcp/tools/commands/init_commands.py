#!/usr/bin/env python3
"""
Initialization Command Handlers

Handles project initialization, status, and help commands.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from .base_command import BaseCommandHandler

logger = logging.getLogger(__name__)


class InitCommandHandler(BaseCommandHandler):
    """Handles initialization-related commands."""
    
    async def execute_status(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-status command."""
        try:
            # Use existing initialization tools for state analysis
            from ..initialization_tools import InitializationTools
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
Use `/aipm-help` to see all available commands, or try:
- `/aipm-init` - Initialize project management
- `/aipm-analyze` - Analyze project structure  
- `/aipm-tasks` - Show active tasks
"""
                
        except Exception as e:
            logger.error(f"Error in command_status: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error getting project status: {str(e)}",
                "suggested_commands": ["aipm-help", "aipm-init"]
            }, indent=2)
    
    async def execute_init(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-init command with status check and appropriate redirection."""
        try:
            from ..initialization_tools import InitializationTools
            init_tools = InitializationTools(self.db_manager)
            
            # Get state analysis first
            state_result = await init_tools.get_project_state_analysis({
                "project_path": str(project_path)
            })
            
            # Check if project is already fully initialized
            try:
                state_data = json.loads(state_result)
                state = state_data.get("state", "unknown")
                
                # If project is already complete, suggest /aipm-resume instead
                if state == "complete":
                    return f"""# ℹ️ Project Already Initialized

## Current Status:
{state_result}

## 🔄 Did you mean `/aipm-resume`?

This project appears to already have AI Project Manager fully set up and running. 

**If you want to:**
- **Continue previous work** → Use `/aipm-resume` 
- **See current tasks** → Use `/aipm-tasks`
- **Check project status** → Use `/aipm-status`
- **Create work branch** → Use `/aipm-branch`

**If you really want to re-initialize:**
- Move or backup the existing `projectManagement/` directory first
- Then run `/aipm-init` again

## 💡 Recommended Next Step:
Try `/aipm-resume` to continue your previous work, or `/aipm-status` to see available options.
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
                
                # Add directive hook after initialization workflow completion
                await self._trigger_workflow_directive({
                    "trigger": "workflow_completion",
                    "workflow_type": "project_initialization",
                    "command": "/aipm-init",
                    "project_path": str(project_path),
                    "initialization_choice": choice,
                    "state_before": state
                })
                
                return f"""# /aipm-init Command Executed

## Project Analysis:
{state_result}

## Action Taken:
Choice: {choice}

## Result:
{choice_result}

## 🎯 Next Steps:
- Use `/aipm-resume` to start working with tasks
- Use `/aipm-branch` to create a work branch  
- Use `/aipm-tasks` to see active items
"""
            except Exception as parse_error:
                logger.warning(f"Failed to parse state analysis: {parse_error}")
                return f"""# /aipm-init Command - Analysis Complete

{state_result}

**Next Steps**: Use `make_initialization_choice` tool to select your preferred option.
"""
                
        except Exception as e:
            logger.error(f"Error in _execute_init: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-init command: {str(e)}"
            }, indent=2)
    
    async def execute_help(self, arguments: Dict[str, Any]) -> str:
        """Show available commands and their descriptions."""
        try:
            command = arguments.get("command")
            format_type = arguments.get("format", "detailed")
            
            if command and command in self._get_all_commands():
                # Show detailed help for specific command
                cmd_info = self._get_all_commands()[command]
                return f"""# /aipm-help - {command}

## Description:
{cmd_info['description']}

## Workflow:
{' → '.join(cmd_info['workflow'])}

## Approval Level:
{cmd_info['approval_level']}

## Usage:
`/{command}`

## Available Commands:
Use `/aipm-help` to see all commands.
"""
            
            if format_type == "simple":
                # Simple format - just list commands
                commands = list(self._get_all_commands().keys())
                return f"""# Available Commands

{chr(10).join([f"- /{cmd}" for cmd in sorted(commands)])}

Use `/aipm-help <command>` for detailed information about a specific command.
"""
            
            # Detailed format - show all commands with descriptions
            help_text = """# AI Project Manager - Available Commands

## Essential Commands
- **`/aipm-status`** - Get current project state and suggested next steps
- **`/aipm-help`** - Show this help information
- **`/aipm-init`** - Initialize AI project management (auto-detects best approach)

## Work Management  
- **`/aipm-resume`** - Resume previous work and active tasks
- **`/aipm-tasks`** - Show active tasks and progress
- **`/aipm-newTask <description>`** - Create and start working on new task
- **`/aipm-pause`** - Find suitable stopping point and prepare for clean resumption

## Project Understanding
- **`/aipm-analyze`** - Full project analysis and theme discovery
- **`/aipm-themes`** - Show project themes and file organization
- **`/aipm-flows`** - Show user experience flows and journeys

## Git Workflow
- **`/aipm-branch`** - Create AI work branch for parallel development
- **`/aipm-merge`** - Merge completed work back to ai-pm-org-main  
- **`/aipm-deploy`** - Deploy AI improvements to your main branch

## Database Management
- **`/aipm-backup`** - Create manual database backup with timestamp
- **`/aipm-maintenance`** - Run database cleanup and optimization
- **`/aipm-db-stats`** - Show database health and storage statistics

## Configuration
- **`/aipm-config`** - Show current configuration settings

Use `/aipm-help <command>` for detailed information about any specific command.
"""
            return help_text
            
        except Exception as e:
            logger.error(f"Error in help_commands: {e}")
            return f"Error retrieving help information: {str(e)}"
    
    def _get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all available commands with their metadata."""
        return {
            "aipm-status": {
                "description": "Get current project state and available options",
                "workflow": ["get_project_state_analysis"],
                "approval_level": "none"
            },
            "aipm-help": {
                "description": "Show all available commands with descriptions",
                "workflow": ["show_command_help"],
                "approval_level": "none"
            },
            "aipm-init": {
                "description": "Initialize AI project management (checks status first, suggests /aipm-resume if already set up)",
                "workflow": ["get_project_state_analysis", "check_existing_setup", "make_initialization_choice"],
                "approval_level": "workflow"
            },
            "aipm-resume": {
                "description": "Resume previous work and active tasks",
                "workflow": ["session_boot_with_git_detection", "task_list_active", "context_load_theme"],
                "approval_level": "workflow"
            },
            "aipm-tasks": {
                "description": "Show active tasks and progress",
                "workflow": ["task_list_active", "sidequest_list_active"],
                "approval_level": "none"
            },
            "aipm-newTask": {
                "description": "Create and start new task",
                "workflow": ["task_create", "context_load_theme", "flow_load_selective"],
                "approval_level": "workflow"
            },
            "aipm-analyze": {
                "description": "Full project analysis and theme discovery",
                "workflow": ["get_project_state_analysis", "theme_discover", "project_get_status"],
                "approval_level": "workflow"
            },
            "aipm-themes": {
                "description": "Show project themes and structure",
                "workflow": ["theme_list", "theme_get_context"],
                "approval_level": "none"
            },
            "aipm-flows": {
                "description": "Show user experience flows",
                "workflow": ["flow_index_create", "context_get_flows"],
                "approval_level": "none"
            },
            "aipm-branch": {
                "description": "Create AI work branch for parallel development",
                "workflow": ["create_instance_branch", "switch_to_branch"],
                "approval_level": "workflow"
            },
            "aipm-merge": {
                "description": "Merge AI work back to main branch",
                "workflow": ["get_branch_status", "merge_instance_branch"],
                "approval_level": "workflow"
            },
            "aipm-config": {
                "description": "Show current configuration settings",
                "workflow": ["get_config"],
                "approval_level": "none"
            },
            "aipm-deploy": {
                "description": "Deploy AI improvements to your main branch (merges ai-pm-org-main → user's main)",
                "workflow": ["get_branch_status", "git_merge_ai_main_to_user"],
                "approval_level": "workflow"
            },
            "aipm-backup": {
                "description": "Create manual database backup with timestamp",
                "workflow": ["database_backup"],
                "approval_level": "none"
            },
            "aipm-maintenance": {
                "description": "Run database cleanup with automatic pre-maintenance backup (keeps 500 recent file modifications, 20 recent sessions per project)",
                "workflow": ["database_backup", "database_maintenance"],
                "approval_level": "workflow"
            },
            "aipm-db-stats": {
                "description": "Show database health, storage usage, and performance statistics",
                "workflow": ["database_stats"],
                "approval_level": "none"
            },
            "aipm-pause": {
                "description": "Find suitable stopping point and prepare project for clean resumption",
                "workflow": ["work_pause_preparation", "thorough_cleanup", "context_preservation"],
                "approval_level": "none"
            }
        }