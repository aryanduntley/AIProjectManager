#!/usr/bin/env python3
"""
Run Command Processor - Direct replacement for slash commands

Handles commands like "run-aipm-init", "run-aipm-help", etc.
Direct 1:1 replacement for broken slash commands.
"""

import logging
from typing import Dict, Any, List
from ..core.mcp_api import ToolDefinition

logger = logging.getLogger(__name__)

class RunCommandProcessor:
    """Process run- commands as direct slash command replacements."""
    
    def __init__(self, db_manager=None, config_manager=None):
        """Initialize the run command processor."""
        self.db_manager = db_manager
        self.config_manager = config_manager
        
        # Available commands - direct mapping to aipm commands
        self.available_commands = [
            "run-aipm-help", "run-aipm-status", "run-aipm-init", 
            "run-aipm-resume", "run-aipm-tasks", "run-aipm-newTask",
            "run-aipm-analyze", "run-aipm-themes", "run-aipm-flows",
            "run-aipm-branch", "run-aipm-merge", "run-aipm-deploy", 
            "run-aipm-pause", "run-aipm-backup", "run-aipm-maintenance",
            "run-aipm-db-stats", "run-aipm-config"
        ]
        
        logger.info("RunCommandProcessor initialized")
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get run command processor tools - one for each command."""
        tools = []
        
        for command in self.available_commands:
            tools.append(
                ToolDefinition(
                    name=command.replace("-", "_"),  # run_aipm_init, etc.
                    description=f"Execute {command} (replacement for /{command.replace('run-', '')})",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Project directory path",
                                "default": "."
                            },
                            "args": {
                                "type": "object", 
                                "description": "Additional command arguments",
                                "default": {}
                            }
                        }
                    },
                    handler=self._create_handler(command)
                )
            )
        
        return tools
    
    def _create_handler(self, command: str):
        """Create a handler function for a specific command."""
        async def handler(arguments: Dict[str, Any]) -> str:
            return await self._execute_command(command, arguments)
        return handler
    
    async def _execute_command(self, run_command: str, arguments: Dict[str, Any]) -> str:
        """Execute a run- command."""
        project_path = arguments.get("project_path", ".")
        args = arguments.get("args", {})
        
        # Convert run-aipm-init to aimp-init
        aipm_command = run_command.replace("run-", "")
        
        logger.info(f"Executing {run_command} -> {aipm_command}")
        
        try:
            # Use the existing command system
            from ..tools.command_tools import CommandTools
            
            if self.db_manager and self.config_manager:
                command_tools = CommandTools(self.db_manager, self.config_manager, None)
                
                execute_args = {
                    "command": aipm_command,
                    "project_path": project_path,
                    "args": args
                }
                
                result = await command_tools.execute_command(execute_args)
                
                return f"✅ **{run_command}** executed successfully!\n\n{result}"
            
            else:
                # Fallback for specific commands
                return await self._fallback_execution(aipm_command, arguments)
                
        except Exception as e:
            logger.error(f"Error executing {run_command}: {e}")
            return f"❌ Error executing **{run_command}**: {str(e)}"
    
    async def _fallback_execution(self, command: str, arguments: Dict[str, Any]) -> str:
        """Fallback execution when full system isn't available."""
        
        if command == "aipm-help":
            return """🚀 **AI Project Manager Commands**

**Available run- commands** (replacement for slash commands):

**Essential:**
- `run-aipm-help` - Show this help
- `run-aipm-status` - Get project status  
- `run-aipm-init` - Initialize project

**Work Management:**
- `run-aipm-resume` - Resume previous work
- `run-aipm-tasks` - Show active tasks
- `run-aipm-pause` - Pause and save state

**Project Analysis:**
- `run-aipm-analyze` - Analyze project structure
- `run-aipm-themes` - Show project themes
- `run-aipm-flows` - Show user flows

**Git Workflow:**
- `run-aipm-branch` - Create work branch
- `run-aipm-merge` - Merge completed work
- `run-aipm-deploy` - Deploy to main branch

**Maintenance:**
- `run-aipm-backup` - Create database backup
- `run-aipm-maintenance` - Run cleanup
- `run-aipm-config` - Show configuration

💡 **Usage:** Simply type the command (e.g., "run-aipm-init") and I'll execute it automatically."""

        elif command == "aipm-status":
            return """📊 **Project Status**

⚠️ Full status requires database initialization.
Try `run-aipm-init` first to set up the project."""

        else:
            return f"""⚡ **{command}** Command

⚠️ This command requires full system initialization.
Try `run-aipm-init` first to set up the project management system."""