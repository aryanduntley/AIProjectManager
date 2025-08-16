#!/usr/bin/env python3
"""
Task Management Command Handlers

Handles task creation, management, and workflow commands.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any
from .base_command import BaseCommandHandler

logger = logging.getLogger(__name__)


class TaskCommandHandler(BaseCommandHandler):
    """Handles task management commands."""
    
    async def execute_resume(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-resume command."""
        try:
            # This would integrate with session manager and task tools
            return json.dumps({
                "type": "info",
                "message": "Resume command workflow: session_boot_with_git_detection → task_list_active → context_load_theme",
                "next_steps": "Use session_manager and task_tools to implement resume functionality"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in _execute_resume: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-resume command: {str(e)}"
            }, indent=2)
    
    async def execute_tasks(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-tasks command."""
        try:
            from ..task_tools import TaskTools
            task_tools = TaskTools(self.db_manager)
            
            # Get active tasks
            result = await task_tools.get_active_tasks({
                "project_path": str(project_path)
            })
            
            return f"""# /aipm-tasks Command Result

## Active Tasks:
{result}

## Next Steps:
- Use `/aipm-newTask <description>` to create new tasks
- Use `/aipm-resume` to continue working on tasks
"""
            
        except Exception as e:
            logger.error(f"Error in _execute_tasks: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-tasks command: {str(e)}"
            }, indent=2)
    
    async def execute_new_task(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-newTask command."""
        try:
            from ..task_tools import TaskTools
            task_tools = TaskTools(self.db_manager)
            
            # Create new task with description
            task_description = args.get('description', 'New task created via command')
            
            create_result = await task_tools.create_task({
                "project_path": str(project_path),
                "description": task_description
            })
            
            # Add directive hook after task creation workflow completion
            await self._trigger_workflow_directive({
                "trigger": "workflow_completion",
                "workflow_type": "task_creation",
                "command": "/aipm-newTask",
                "project_path": str(project_path),
                "task_description": task_description
            })
            
            return f"""# /aipm-newTask Command Result

## New Task Created:
{create_result}

## Next Steps:
- Use `/aipm-tasks` to view all active tasks
- Use `/aipm-resume` to begin working on tasks
"""
            
        except Exception as e:
            logger.error(f"Error in _execute_newTask: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-newTask command: {str(e)}"
            }, indent=2)