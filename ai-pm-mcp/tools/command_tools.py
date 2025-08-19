#!/usr/bin/env python3
"""
Command Tools - Refactored Modular Implementation

MCP tools that implement the command system for better user experience.
These tools provide workflow-level approval and command discovery.

This is a refactored version that delegates to specialized command handlers.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List

from ..core.mcp_api import ToolDefinition
from .commands.init_commands import InitCommandHandler
from .commands.task_commands import TaskCommandHandler
from .commands.git_commands import GitCommandHandler
from .commands.database_commands import DatabaseCommandHandler  
from .commands.analysis_commands import AnalysisCommandHandler
from .commands.session_commands import SessionCommandHandler

logger = logging.getLogger(__name__)


class CommandTools:
    """MCP tools for command system and user workflow management."""
    
    def __init__(self, db_manager=None, config_manager=None, server_instance=None):
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.server_instance = server_instance
        
        # Initialize command handlers
        self.init_handler = InitCommandHandler(db_manager, config_manager, server_instance)
        self.task_handler = TaskCommandHandler(db_manager, config_manager, server_instance)
        self.git_handler = GitCommandHandler(db_manager, config_manager, server_instance)
        self.database_handler = DatabaseCommandHandler(db_manager, config_manager, server_instance)
        self.analysis_handler = AnalysisCommandHandler(db_manager, config_manager, server_instance)
        self.session_handler = SessionCommandHandler(db_manager, config_manager, server_instance)
        
        self.commands = self.init_handler._get_all_commands()
        
        # Pass commands to all handlers
        for handler in [self.init_handler, self.task_handler, self.git_handler, 
                       self.database_handler, self.analysis_handler, self.session_handler]:
            handler.commands = self.commands
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all available MCP tools for command execution."""
        return [
            ToolDefinition(
                name="execute_command",
                description="Execute AI Project Manager commands with workflow-level approval",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command to execute (without leading slash)",
                            "enum": list(self.commands.keys())
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
                name="help_commands",
                description="Get help information about available commands",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Specific command to get help for (optional)"
                        },
                        "format": {
                            "type": "string",
                            "description": "Help format: 'detailed' or 'simple'", 
                            "default": "detailed"
                        }
                    }
                },
                handler=self.init_handler.execute_help
            ),
            ToolDefinition(
                name="command_status",
                description="Get project state and show available next steps (implements /aipm-status command)",
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
            if command in ["aipm-status", "aipm-help", "aipm-init"]:
                if command == "aipm-status":
                    return await self.init_handler.execute_status(project_path, args)
                elif command == "aipm-help":
                    return await self.init_handler.execute_help(arguments)
                elif command == "aipm-init":
                    return await self.init_handler.execute_init(project_path, args)
                    
            elif command in ["aipm-resume", "aipm-tasks", "aipm-newTask"]:
                if command == "aipm-resume":
                    return await self.task_handler.execute_resume(project_path, args)
                elif command == "aipm-tasks":
                    return await self.task_handler.execute_tasks(project_path, args)
                elif command == "aipm-newTask":
                    return await self.task_handler.execute_new_task(project_path, args)
                    
            elif command in ["aipm-branch", "aipm-merge", "aipm-deploy"]:
                if command == "aipm-branch":
                    return await self.git_handler.execute_branch(project_path, args)
                elif command == "aipm-merge":
                    return await self.git_handler.execute_merge(project_path, args)
                elif command == "aipm-deploy":
                    return await self.git_handler.execute_deploy(project_path, args)
                    
            elif command in ["aipm-backup", "aipm-maintenance", "aipm-db-stats"]:
                if command == "aipm-backup":
                    return await self.database_handler.execute_backup(project_path, args)
                elif command == "aipm-maintenance":
                    return await self.database_handler.execute_maintenance(project_path, args)
                elif command == "aipm-db-stats":
                    return await self.database_handler.execute_db_stats(project_path, args)
                    
            elif command in ["aipm-analyze", "aipm-themes", "aipm-flows", "aipm-config"]:
                if command == "aipm-analyze":
                    return await self.analysis_handler.execute_analyze(project_path, args)
                elif command == "aipm-themes":
                    return await self.analysis_handler.execute_themes(project_path, args)
                elif command == "aipm-flows":
                    return await self.analysis_handler.execute_flows(project_path, args)
                elif command == "aipm-config":
                    return await self.analysis_handler.execute_config(project_path, args)
            
            elif command == "aipm-pause":
                return await self.session_handler.execute_pause(project_path, args)
            
            else:
                cmd_info = self.commands[command]
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
        """Get project state and show available next steps (implements /aipm-status command)."""
        project_path = Path(arguments.get("project_path", "."))
        return await self.init_handler.execute_status(project_path, {})