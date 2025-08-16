"""
Task management tools for the AI Project Manager MCP Server.

Handles task creation, management, status tracking, and sidequest coordination.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.mcp_api import ToolDefinition
from ..database.task_status_queries import TaskStatusQueries
from ..database.session_queries import SessionQueries
from ..database.file_metadata_queries import FileMetadataQueries

from .task.base_operations import BaseOperations
from .task.sidequest_operations import SidequestOperations
from .task.analytics_operations import AnalyticsOperations
from .task.file_operations import FileOperations

logger = logging.getLogger(__name__)


class TaskTools:
    """Tools for task lifecycle management and coordination."""
    
    def __init__(self, task_queries: Optional[TaskStatusQueries] = None, 
                 session_queries: Optional[SessionQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None,
                 config_manager=None):
        self.task_queries = task_queries
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
        self.config_manager = config_manager
        self.server_instance = None  # Will be set by MCPToolRegistry
        
        # Initialize operation modules
        self.base_ops = BaseOperations(task_queries, file_metadata_queries, config_manager)
        self.sidequest_ops = SidequestOperations(task_queries, file_metadata_queries)
        self.analytics_ops = AnalyticsOperations(task_queries)
        self.file_ops = FileOperations(task_queries, file_metadata_queries, config_manager, session_queries)
    
    def _sync_server_instance(self):
        """Sync server instance to all operation modules."""
        self.base_ops.server_instance = self.server_instance
        self.file_ops.server_instance = self.server_instance
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all task management tools."""
        # Sync server instance to operations
        self._sync_server_instance()
        
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
                        "is_high_priority_task": {
                            "type": "boolean",
                            "description": "Whether this is a high-priority task requiring special handling",
                            "default": False
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
        self._sync_server_instance()
        return await self.base_ops.create_task(arguments)
    
    async def update_task_status(self, arguments: Dict[str, Any]) -> str:
        """Update task status and progress."""
        self._sync_server_instance()
        return await self.base_ops.update_task_status(arguments)
    
    async def get_task(self, arguments: Dict[str, Any]) -> str:
        """Get task details and status."""
        return await self.base_ops.get_task(arguments)
    
    async def list_active_tasks(self, arguments: Dict[str, Any]) -> str:
        """List active tasks for a project."""
        return await self.base_ops.list_active_tasks(arguments)
    
    async def create_sidequest(self, arguments: Dict[str, Any]) -> str:
        """Create a new sidequest from a parent task."""
        return await self.sidequest_ops.create_sidequest(arguments)
    
    async def update_sidequest_status(self, arguments: Dict[str, Any]) -> str:
        """Update sidequest status and progress."""
        return await self.sidequest_ops.update_sidequest_status(arguments)
    
    async def list_active_sidequests(self, arguments: Dict[str, Any]) -> str:
        """List active sidequests for a task or project."""
        return await self.sidequest_ops.list_active_sidequests(arguments)
    
    async def get_task_analytics(self, arguments: Dict[str, Any]) -> str:
        """Get task completion analytics and metrics."""
        return await self.analytics_ops.get_task_analytics(arguments)
    
    async def check_sidequest_limits(self, arguments: Dict[str, Any]) -> str:
        """Check sidequest limits for a task."""
        return await self.analytics_ops.check_sidequest_limits(arguments)
    
    async def _create_task_file(self, project_path: Path, task_id: str, task_data: Dict[str, Any]):
        """Create task file for compatibility."""
        return await self.file_ops.create_task_file(project_path, task_id, task_data)
    
    async def _update_task_file_status(self, task_id: str, status: str, progress_percentage: Optional[int], notes: Optional[str]):
        """Update task file status with proper project context and database integration."""
        self._sync_server_instance()
        return await self.file_ops.update_task_file_status(task_id, status, progress_percentage, notes)
    
    async def _sync_task_file_on_disk(self, project_path: str, task_id: str, status: str, 
                                    progress_percentage: Optional[int], notes: Optional[str]):
        """Sync task status to physical files in project structure."""
        return await self.file_ops.sync_task_file_on_disk(project_path, task_id, status, progress_percentage, notes)