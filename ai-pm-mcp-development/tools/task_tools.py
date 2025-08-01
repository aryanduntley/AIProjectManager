"""
Task management tools for the AI Project Manager MCP Server.

Handles task creation, management, status tracking, and sidequest coordination.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from ..core.mcp_api import ToolDefinition
from ..database.task_status_queries import TaskStatusQueries
from ..database.session_queries import SessionQueries
from ..database.file_metadata_queries import FileMetadataQueries

logger = logging.getLogger(__name__)


class TaskTools:
    """Tools for task lifecycle management and coordination."""
    
    def __init__(self, task_queries: Optional[TaskStatusQueries] = None, 
                 session_queries: Optional[SessionQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None):
        self.task_queries = task_queries
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all task management tools."""
        return [
            ToolDefinition(
                name="task_create",
                description="Create a new task with milestone, theme, and flow integration",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "title": {
                            "type": "string",
                            "description": "Task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed task description"
                        },
                        "milestone_id": {
                            "type": "string",
                            "description": "Milestone ID from completion-path.json"
                        },
                        "primary_theme": {
                            "type": "string",
                            "description": "Primary theme for this task"
                        },
                        "related_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Related themes",
                            "default": []
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "Task priority",
                            "default": "medium"
                        },
                        "estimated_effort": {
                            "type": "string",
                            "description": "Estimated effort (e.g., '2 hours', '1 day')"
                        }
                    },
                    "required": ["project_path", "title", "description", "milestone_id", "primary_theme"]
                },
                handler=self.create_task
            ),
            ToolDefinition(
                name="task_update_status",
                description="Update task status and progress",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to update"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in-progress", "blocked", "completed", "cancelled"],
                            "description": "New task status"
                        },
                        "progress_percentage": {
                            "type": "integer",
                            "description": "Progress percentage (0-100)",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "actual_effort": {
                            "type": "string",
                            "description": "Actual effort spent"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Update notes"
                        }
                    },
                    "required": ["task_id", "status"]
                },
                handler=self.update_task_status
            ),
            ToolDefinition(
                name="task_get",
                description="Get task details and status",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to retrieve"
                        }
                    },
                    "required": ["task_id"]
                },
                handler=self.get_task
            ),
            ToolDefinition(
                name="task_list_active",
                description="List active tasks for a project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "status_filter": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["pending", "in-progress", "blocked", "completed", "cancelled"]
                            },
                            "description": "Filter by status",
                            "default": ["pending", "in-progress"]
                        },
                        "theme_filter": {
                            "type": "string",
                            "description": "Filter by theme (optional)"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.list_active_tasks
            ),
            ToolDefinition(
                name="sidequest_create",
                description="Create a new sidequest from a parent task",
                input_schema={
                    "type": "object",
                    "properties": {
                        "parent_task_id": {
                            "type": "string",
                            "description": "Parent task ID"
                        },
                        "title": {
                            "type": "string",
                            "description": "Sidequest title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed sidequest description"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for creating the sidequest"
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Sidequest urgency",
                            "default": "medium"
                        },
                        "impact_on_parent": {
                            "type": "string",
                            "enum": ["minimal", "moderate", "significant"],
                            "description": "Impact on parent task",
                            "default": "minimal"
                        },
                        "estimated_effort": {
                            "type": "string",
                            "description": "Estimated effort"
                        }
                    },
                    "required": ["parent_task_id", "title", "description", "reason"]
                },
                handler=self.create_sidequest
            ),
            ToolDefinition(
                name="sidequest_update_status",
                description="Update sidequest status and progress",
                input_schema={
                    "type": "object",
                    "properties": {
                        "sidequest_id": {
                            "type": "string",
                            "description": "Sidequest ID to update"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in-progress", "blocked", "completed", "cancelled"],
                            "description": "New sidequest status"
                        },
                        "progress_percentage": {
                            "type": "integer",
                            "description": "Progress percentage (0-100)",
                            "minimum": 0,
                            "maximum": 100
                        },
                        "completion_trigger": {
                            "type": "object",
                            "description": "Completion criteria (JSON)"
                        },
                        "notes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Progress notes"
                        }
                    },
                    "required": ["sidequest_id", "status"]
                },
                handler=self.update_sidequest_status
            ),
            ToolDefinition(
                name="sidequest_list_active",
                description="List active sidequests for a task or project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "parent_task_id": {
                            "type": "string",
                            "description": "Parent task ID (optional)"
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Project path to list all sidequests (optional)"
                        },
                        "status_filter": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["pending", "in-progress", "blocked", "completed", "cancelled"]
                            },
                            "description": "Filter by status",
                            "default": ["pending", "in-progress"]
                        }
                    }
                },
                handler=self.list_active_sidequests
            ),
            ToolDefinition(
                name="task_get_analytics",
                description="Get task completion analytics and metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze",
                            "default": 30
                        },
                        "theme_filter": {
                            "type": "string",
                            "description": "Filter by theme (optional)"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_task_analytics
            ),
            ToolDefinition(
                name="sidequest_check_limits",
                description="Check sidequest limits for a task",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID to check limits for"
                        }
                    },
                    "required": ["task_id"]
                },
                handler=self.check_sidequest_limits
            )
        ]
    
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
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Validate project structure exists
            project_path_obj = Path(project_path)
            if not (project_path_obj / "projectManagement").exists():
                return f"Project management structure not found. Initialize project first."
            
            # Generate task ID
            task_id = f"TASK-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            
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
    
    async def create_sidequest(self, arguments: Dict[str, Any]) -> str:
        """Create a new sidequest from a parent task."""
        try:
            parent_task_id = arguments["parent_task_id"]
            title = arguments["title"]
            description = arguments["description"]
            reason = arguments["reason"]
            urgency = arguments.get("urgency", "medium")
            impact_on_parent = arguments.get("impact_on_parent", "minimal")
            estimated_effort = arguments.get("estimated_effort")
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Check sidequest limits
            limit_check = await self.task_queries.check_sidequest_limits(parent_task_id)
            if not limit_check["can_create"]:
                return f"Cannot create sidequest: {limit_check['reason']}. Current active sidequests: {limit_check['active_count']}, Limit: {limit_check['limit']}"
            
            # Generate sidequest ID
            sidequest_id = f"SQ-{parent_task_id.split('-', 1)[1]}-{datetime.now(timezone.utc).strftime('%H%M%S')}"
            
            # Create sidequest in database
            await self.task_queries.create_sidequest(
                sidequest_id=sidequest_id,
                parent_task_id=parent_task_id,
                title=title,
                description=description,
                reason=reason,
                urgency=urgency,
                impact_on_parent=impact_on_parent,
                estimated_effort=estimated_effort
            )
            
            # Log sidequest creation
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=f"Tasks/sidequests/{sidequest_id}.json",
                    file_type="sidequest",
                    operation="create",
                    details={
                        "sidequest_id": sidequest_id,
                        "parent_task_id": parent_task_id,
                        "title": title,
                        "reason": reason
                    }
                )
            
            return f"Sidequest '{title}' created successfully with ID: {sidequest_id}. Warning threshold: {limit_check['warning_threshold']}, Current count: {limit_check['active_count'] + 1}"
            
        except Exception as e:
            logger.error(f"Error creating sidequest: {e}")
            return f"Error creating sidequest: {str(e)}"
    
    async def update_sidequest_status(self, arguments: Dict[str, Any]) -> str:
        """Update sidequest status and progress."""
        try:
            sidequest_id = arguments["sidequest_id"]
            status = arguments["status"]
            progress_percentage = arguments.get("progress_percentage")
            completion_trigger = arguments.get("completion_trigger")
            notes = arguments.get("notes", [])
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Update sidequest in database
            await self.task_queries.update_sidequest_status(
                sidequest_id=sidequest_id,
                status=status,
                progress_percentage=progress_percentage,
                completion_trigger=completion_trigger,
                notes=notes
            )
            
            # Log sidequest update
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=f"sidequest:{sidequest_id}",
                    file_type="sidequest",
                    operation="update",
                    details={
                        "status": status,
                        "progress_percentage": progress_percentage,
                        "notes_count": len(notes)
                    }
                )
            
            return f"Sidequest {sidequest_id} updated to status: {status}" + (f" ({progress_percentage}% complete)" if progress_percentage is not None else "")
            
        except Exception as e:
            logger.error(f"Error updating sidequest status: {e}")
            return f"Error updating sidequest status: {str(e)}"
    
    async def list_active_sidequests(self, arguments: Dict[str, Any]) -> str:
        """List active sidequests for a task or project."""
        try:
            parent_task_id = arguments.get("parent_task_id")
            project_path = arguments.get("project_path")
            status_filter = arguments.get("status_filter", ["pending", "in-progress"])
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            if parent_task_id:
                # Get sidequests for specific task
                sidequests = await self.task_queries.get_sidequests_for_task(parent_task_id, status_filter)
                title_prefix = f"Active sidequests for task {parent_task_id}"
            elif project_path:
                # Get all sidequests for project
                sidequests = await self.task_queries.get_all_sidequests(status_filter)
                title_prefix = f"Active sidequests for project {project_path}"
            else:
                return "Either parent_task_id or project_path must be provided."
            
            if not sidequests:
                return f"No active sidequests found."
            
            sidequest_list = []
            for sidequest in sidequests:
                sidequest_summary = {
                    "sidequest_id": sidequest["sidequest_id"],
                    "parent_task_id": sidequest["parent_task_id"],
                    "title": sidequest["title"],
                    "status": sidequest["status"],
                    "urgency": sidequest["urgency"],
                    "impact_on_parent": sidequest["impact_on_parent"],
                    "progress_percentage": sidequest["progress_percentage"],
                    "created_at": sidequest["created_at"],
                    "last_updated": sidequest["last_updated"]
                }
                sidequest_list.append(sidequest_summary)
            
            return f"{title_prefix}:\n\n{json.dumps(sidequest_list, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error listing active sidequests: {e}")
            return f"Error listing active sidequests: {str(e)}"
    
    async def get_task_analytics(self, arguments: Dict[str, Any]) -> str:
        """Get task completion analytics and metrics."""
        try:
            project_path = arguments["project_path"]
            days = arguments.get("days", 30)
            theme_filter = arguments.get("theme_filter")
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Get analytics from database
            analytics = await self.task_queries.get_task_analytics(days, theme_filter)
            
            return f"Task analytics for {project_path} (last {days} days):\n\n{json.dumps(analytics, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error getting task analytics: {e}")
            return f"Error getting task analytics: {str(e)}"
    
    async def check_sidequest_limits(self, arguments: Dict[str, Any]) -> str:
        """Check sidequest limits for a task."""
        try:
            task_id = arguments["task_id"]
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Check limits
            limit_check = await self.task_queries.check_sidequest_limits(task_id)
            
            status_message = f"Sidequest limits for task {task_id}:\n\n"
            status_message += f"Active sidequests: {limit_check['active_count']}\n"
            status_message += f"Maximum allowed: {limit_check['limit']}\n"
            status_message += f"Warning threshold: {limit_check['warning_threshold']}\n"
            status_message += f"Can create new: {limit_check['can_create']}\n"
            
            if not limit_check['can_create']:
                status_message += f"Reason: {limit_check['reason']}\n"
            elif limit_check['active_count'] >= limit_check['warning_threshold']:
                status_message += "Warning: Approaching sidequest limit\n"
            
            return status_message
            
        except Exception as e:
            logger.error(f"Error checking sidequest limits: {e}")
            return f"Error checking sidequest limits: {str(e)}"
    
    async def _create_task_file(self, project_path: Path, task_id: str, task_data: Dict[str, Any]):
        """Create task file for compatibility."""
        tasks_dir = project_path / "projectManagement" / "Tasks" / "active"
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        task_file = tasks_dir / f"{task_id}.json"
        task_file.write_text(json.dumps(task_data, indent=2))
    
    async def _update_task_file_status(self, task_id: str, status: str, progress_percentage: Optional[int], notes: Optional[str]):
        """Update task file status with proper project context and database integration."""
        try:
            if not self.task_queries:
                logger.warning(f"Cannot update task file status for {task_id}: Database queries not available")
                return
            
            # Get task details from database to find associated project path
            task_details = self.task_queries.get_task_details(task_id)
            if not task_details:
                logger.error(f"Task {task_id} not found in database")
                return
            
            # Update database status first (primary source of truth)
            success = self.task_queries.update_task_status(
                task_id=task_id,
                status=status,
                progress_percentage=progress_percentage,
                notes=notes
            )
            
            if not success:
                logger.error(f"Failed to update database status for task {task_id}")
                return
            
            # Try to update associated project files if file metadata is available
            if self.file_metadata_queries:
                # Log the task status change for file tracking
                self.file_metadata_queries.log_file_modification(
                    file_path=f"task:{task_id}",  # Virtual file path for task tracking
                    file_type="task",
                    operation="status_update",
                    details={
                        "task_id": task_id,
                        "new_status": status,
                        "progress_percentage": progress_percentage,
                        "notes": notes,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            
            # Update session context if available
            if self.session_queries:
                session_id = self.session_queries.get_current_session_id()
                if session_id:
                    # Log task status change in session
                    self.session_queries.log_session_event(
                        session_id=session_id,
                        event_type="task_status_update",
                        details={
                            "task_id": task_id,
                            "status": status,
                            "progress_percentage": progress_percentage
                        }
                    )
            
            # Attempt to sync with any physical task files in the project structure
            try:
                project_path = task_details.get('project_path')
                if project_path:
                    await self._sync_task_file_on_disk(project_path, task_id, status, progress_percentage, notes)
            except Exception as file_sync_error:
                logger.warning(f"Could not sync task file on disk for {task_id}: {file_sync_error}")
                # Don't fail the overall operation if file sync fails
                
            logger.info(f"Successfully updated task status: {task_id} -> {status}")
            
        except Exception as e:
            logger.error(f"Error updating task file status for {task_id}: {e}")
            raise
    
    async def _sync_task_file_on_disk(self, project_path: str, task_id: str, status: str, 
                                    progress_percentage: Optional[int], notes: Optional[str]):
        """Sync task status to physical files in project structure."""
        try:
            from pathlib import Path
            
            project_root = Path(project_path)
            tasks_dir = project_root / "projectManagement" / "Tasks"
            
            if not tasks_dir.exists():
                logger.debug(f"Tasks directory does not exist: {tasks_dir}")
                return
            
            # Look for task files that might contain this task
            task_files = list(tasks_dir.glob("*.json"))
            
            for task_file in task_files:
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    
                    # Check if this file contains our task
                    updated = False
                    
                    # Handle different task file structures
                    if isinstance(task_data, dict):
                        # Check if task_data has task arrays
                        for key in ['tasks', 'task_list', 'items']:
                            if key in task_data and isinstance(task_data[key], list):
                                for task in task_data[key]:
                                    if isinstance(task, dict) and task.get('id') == task_id:
                                        task['status'] = status
                                        if progress_percentage is not None:
                                            task['progress_percentage'] = progress_percentage
                                        if notes:
                                            task['notes'] = notes
                                        task['last_updated'] = datetime.now(timezone.utc).isoformat()
                                        updated = True
                                        break
                        
                        # Check if task_data itself is the task
                        if task_data.get('id') == task_id:
                            task_data['status'] = status
                            if progress_percentage is not None:
                                task_data['progress_percentage'] = progress_percentage
                            if notes:
                                task_data['notes'] = notes
                            task_data['last_updated'] = datetime.now(timezone.utc).isoformat()
                            updated = True
                    
                    elif isinstance(task_data, list):
                        # Task file is a direct list of tasks
                        for task in task_data:
                            if isinstance(task, dict) and task.get('id') == task_id:
                                task['status'] = status
                                if progress_percentage is not None:
                                    task['progress_percentage'] = progress_percentage
                                if notes:
                                    task['notes'] = notes
                                task['last_updated'] = datetime.now(timezone.utc).isoformat()
                                updated = True
                                break
                    
                    # Write back the updated file
                    if updated:
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, indent=2, ensure_ascii=False)
                        logger.debug(f"Updated task {task_id} in file {task_file}")
                        return  # Successfully updated, no need to check other files
                        
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Could not read/write task file {task_file}: {e}")
                    continue
            
            logger.debug(f"Task {task_id} not found in any task files in {tasks_dir}")
            
        except Exception as e:
            logger.error(f"Error syncing task file on disk: {e}")
            # Don't re-raise - this is a nice-to-have feature