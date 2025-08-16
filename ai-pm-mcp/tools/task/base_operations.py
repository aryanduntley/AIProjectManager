"""
Core task operations for the AI Project Manager.

Handles basic task creation, updating, retrieval, and listing operations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ...database.task_status_queries import TaskStatusQueries
from ...database.file_metadata_queries import FileMetadataQueries
from ...utils.project_paths import get_project_management_path, get_tasks_path

logger = logging.getLogger(__name__)


class BaseOperations:
    """Core task operations."""
    
    def __init__(self, task_queries: Optional[TaskStatusQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None,
                 config_manager=None):
        self.task_queries = task_queries
        self.file_metadata_queries = file_metadata_queries
        self.config_manager = config_manager
        self.server_instance = None
        self._file_ops = None

    async def create_task(self, arguments: Dict[str, Any]) -> str:
        """Create a new task with database integration."""
        try:
            project_path = arguments["project_path"]
            title = arguments["title"]
            description = arguments["description"]
            milestone_id = arguments["milestone_id"]
            primary_theme = arguments["primary_theme"]
            related_themes = arguments.get("related_themes", [])
            priority = arguments.get("priority", "medium")
            estimated_effort = arguments.get("estimated_effort")
            is_high_priority_task = arguments.get("is_high_priority_task", False)
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Validate project structure exists
            project_path_obj = Path(project_path)
            if not get_project_management_path(project_path_obj, self.config_manager).exists():
                return f"Project management structure not found. Initialize project first."
            
            # Generate task ID with HIGH prefix for high-priority tasks
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
            if is_high_priority_task:
                task_id = f"HIGH-TASK-{timestamp}"
                # Automatically set priority to high for high-priority tasks
                priority = "high"
            else:
                task_id = f"TASK-{timestamp}"
            
            # Create task in database
            await self.task_queries.create_task(
                task_id=task_id,
                title=title,
                description=description,
                milestone_id=milestone_id,
                primary_theme=primary_theme,
                related_themes=related_themes,
                priority=priority,
                estimated_effort=estimated_effort
            )
            
            # Create task file for compatibility
            await self._create_task_file(project_path_obj, task_id, {
                "taskId": task_id,
                "title": title,
                "description": description,
                "status": "pending",
                "priority": priority,
                "milestoneId": milestone_id,
                "primaryTheme": primary_theme,
                "relatedThemes": related_themes,
                "estimatedEffort": estimated_effort,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "subtasks": []
            })
            
            # Log task creation
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=f"Tasks/active/{task_id}.json",
                    file_type="task",
                    operation="create",
                    details={
                        "task_id": task_id,
                        "title": title,
                        "milestone_id": milestone_id,
                        "primary_theme": primary_theme
                    }
                )
            
            return f"Task '{title}' created successfully with ID: {task_id}"
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return f"Error creating task: {str(e)}"

    async def update_task_status(self, arguments: Dict[str, Any]) -> str:
        """Update task status and progress."""
        try:
            task_id = arguments["task_id"]
            status = arguments["status"]
            progress_percentage = arguments.get("progress_percentage")
            actual_effort = arguments.get("actual_effort")
            notes = arguments.get("notes")
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Update task in database
            await self.task_queries.update_task_status(
                task_id=task_id,
                status=status,
                progress_percentage=progress_percentage,
                actual_effort=actual_effort
            )
            
            # Update task file
            await self._update_task_file_status(task_id, status, progress_percentage, notes)
            
            # Log task update
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=f"task:{task_id}",
                    file_type="task",
                    operation="update",
                    details={
                        "status": status,
                        "progress_percentage": progress_percentage,
                        "notes": notes
                    }
                )
            
            # Trigger directive processing for task status updates, especially completions
            if self.server_instance and hasattr(self.server_instance, 'on_task_completion'):
                try:
                    # Check if this is a completion
                    is_completion = status.lower() in ['completed', 'done', 'finished']
                    
                    completion_result = {
                        "task_id": task_id,
                        "status": status,
                        "progress_percentage": progress_percentage,
                        "actual_effort": actual_effort,
                        "notes": notes,
                        "is_completion": is_completion,
                        "task_data": {
                            "operation": "task_status_update",
                            "previous_status": "unknown",  # Could be enhanced to track this
                            "new_status": status
                        }
                    }
                    
                    # Always trigger for status updates, directive processor will decide appropriate actions
                    await self.server_instance.on_task_completion(task_id, completion_result)
                    
                except Exception as e:
                    logger.warning(f"Failed to trigger task completion directive: {e}")
            
            return f"Task {task_id} updated to status: {status}" + (f" ({progress_percentage}% complete)" if progress_percentage is not None else "")
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return f"Error updating task status: {str(e)}"

    async def get_task(self, arguments: Dict[str, Any]) -> str:
        """Get task details and status."""
        try:
            task_id = arguments["task_id"]
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Get task from database
            task = await self.task_queries.get_task(task_id)
            if not task:
                return f"Task {task_id} not found."
            
            # Get subtasks
            subtasks = await self.task_queries.get_subtasks(task_id)
            
            # Get sidequests
            sidequests = await self.task_queries.get_sidequests_for_task(task_id)
            
            task_details = {
                "task": dict(task),
                "subtasks": [dict(subtask) for subtask in subtasks],
                "sidequests": [dict(sidequest) for sidequest in sidequests]
            }
            
            return f"Task details for {task_id}:\n\n{json.dumps(task_details, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return f"Error getting task: {str(e)}"

    async def list_active_tasks(self, arguments: Dict[str, Any]) -> str:
        """List active tasks for a project."""
        try:
            project_path = arguments["project_path"]
            status_filter = arguments.get("status_filter", ["pending", "in-progress"])
            theme_filter = arguments.get("theme_filter")
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Get active tasks from database
            tasks = await self.task_queries.get_tasks_by_status(status_filter, theme_filter)
            
            if not tasks:
                return f"No active tasks found for project {project_path}"
            
            task_list = []
            for task in tasks:
                task_summary = {
                    "task_id": task["task_id"],
                    "title": task["title"],
                    "status": task["status"],
                    "priority": task["priority"],
                    "milestone_id": task["milestone_id"],
                    "primary_theme": task["primary_theme"],
                    "progress_percentage": task["progress_percentage"],
                    "created_at": task["created_at"],
                    "last_updated": task["last_updated"]
                }
                task_list.append(task_summary)
            
            return f"Active tasks for {project_path}:\n\n{json.dumps(task_list, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error listing active tasks: {e}")
            return f"Error listing active tasks: {str(e)}"

    def _get_file_ops(self):
        """Lazy initialize file operations to avoid circular imports."""
        if self._file_ops is None:
            from .file_operations import FileOperations
            self._file_ops = FileOperations(self.task_queries, self.file_metadata_queries, self.config_manager, None)
            self._file_ops.server_instance = self.server_instance
        return self._file_ops

    async def _create_task_file(self, project_path: Path, task_id: str, task_data: Dict[str, Any]):
        """Create task file for compatibility."""
        file_ops = self._get_file_ops()
        return await file_ops.create_task_file(project_path, task_id, task_data)

    async def _update_task_file_status(self, task_id: str, status: str, progress_percentage: Optional[int], notes: Optional[str]):
        """Update task file status with proper project context and database integration."""
        file_ops = self._get_file_ops()
        return await file_ops.update_task_file_status(task_id, status, progress_percentage, notes)