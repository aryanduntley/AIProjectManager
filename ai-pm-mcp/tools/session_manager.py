"""
Work period management tools for the AI Project Manager MCP Server.

Handles activity-based work tracking, context snapshots, and work analytics.
Replaces traditional session lifecycle with activity-based work periods.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.mcp_api import ToolDefinition
from ..database.session_queries import SessionQueries
from ..database.file_metadata_queries import FileMetadataQueries
from ..database.git_queries import GitQueries

from .session.core_operations import CoreOperations
from .session.analytics_operations import AnalyticsOperations
from .session.git_integration import GitIntegration
from .session.initialization_operations import InitializationOperations

logger = logging.getLogger(__name__)


class SessionManager:
    """Tools for activity-based work period management and context tracking."""
    
    def __init__(self, session_queries: Optional[SessionQueries] = None, 
                 file_metadata_queries: Optional[FileMetadataQueries] = None,
                 git_queries: Optional[GitQueries] = None,
                 db_manager = None, server_instance=None):
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
        self.git_queries = git_queries
        self.db_manager = db_manager
        self.server_instance = server_instance
        
        # Initialize operation modules
        self.core_ops = CoreOperations(session_queries, file_metadata_queries, server_instance)
        self.analytics_ops = AnalyticsOperations(session_queries, server_instance)
        self.git_ops = GitIntegration(session_queries, git_queries, db_manager, server_instance)
        self.init_ops = InitializationOperations(session_queries, file_metadata_queries, server_instance)
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all work period management tools."""
        return [
            ToolDefinition(
                name="session_start",
                description="Start a new work period with activity tracking",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "context_mode": {
                            "type": "string",
                            "enum": ["theme-focused", "task-driven", "exploratory", "maintenance"],
                            "description": "Context mode for work session",
                            "default": "theme-focused"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Optional: Resume existing session ID"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.start_work_period
            ),
            ToolDefinition(
                name="session_save_context",
                description="Save current session context snapshot",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to save context for"
                        },
                        "loaded_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of currently loaded theme names"
                        },
                        "loaded_flows": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of currently loaded flow names"
                        },
                        "files_accessed": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of files accessed in this session"
                        }
                    },
                    "required": ["session_id", "loaded_themes"]
                },
                handler=self.save_context_snapshot
            ),
            ToolDefinition(
                name="session_get_context",
                description="Get current session context and history",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to get context for"
                        }
                    },
                    "required": ["session_id"]
                },
                handler=self.get_session_context
            ),
            ToolDefinition(
                name="session_update_activity",
                description="Update session activity and active themes/tasks",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to update"
                        },
                        "active_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Currently active theme names"
                        },
                        "active_tasks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Currently active task IDs"
                        },
                        "active_sidequests": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Currently active sidequest IDs"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Session notes or updates"
                        }
                    },
                    "required": ["session_id"]
                },
                handler=self.update_session_activity
            ),
            ToolDefinition(
                name="session_list_recent",
                description="List recent work periods for a project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of sessions to return",
                            "default": 10
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.list_recent_sessions
            ),
            ToolDefinition(
                name="session_get_analytics",
                description="Get session analytics and work metrics",
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
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_session_analytics
            ),
            ToolDefinition(
                name="session_archive_stale",
                description="Archive stale work periods with no recent activity",
                input_schema={
                    "type": "object",
                    "properties": {
                        "hours_threshold": {
                            "type": "integer",
                            "description": "Hours of inactivity before archiving",
                            "default": 24
                        }
                    }
                },
                handler=self.archive_stale_periods
            ),
            ToolDefinition(
                name="session_boot_with_git",
                description="Enhanced session boot with Git change detection",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "context_mode": {
                            "type": "string",
                            "enum": ["theme-focused", "task-driven", "exploratory", "maintenance"],
                            "description": "Context mode for work session",
                            "default": "theme-focused"
                        },
                        "force_git_check": {
                            "type": "boolean",
                            "description": "Force Git change detection even for branch instances",
                            "default": False
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.boot_session_with_git_detection
            ),
            ToolDefinition(
                name="session_get_initialization_summary",
                description="Get detailed file metadata initialization progress",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_initialization_summary
            ),
            ToolDefinition(
                name="session_reset_initialization",
                description="Reset file metadata initialization to start fresh",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Confirm reset operation",
                            "default": False
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.reset_initialization
            )
        ]

    async def start_work_period(self, arguments: Dict[str, Any]) -> str:
        """Start a new work period with activity tracking."""
        return await self.core_ops.start_work_period(arguments)

    async def save_context_snapshot(self, arguments: Dict[str, Any]) -> str:
        """Save current session context snapshot."""
        return await self.core_ops.save_context_snapshot(arguments)

    async def get_session_context(self, arguments: Dict[str, Any]) -> str:
        """Get current session context and history."""
        return await self.core_ops.get_session_context(arguments)

    async def update_session_activity(self, arguments: Dict[str, Any]) -> str:
        """Update session activity and active tasks/themes."""
        return await self.core_ops.update_session_activity(arguments)

    async def list_recent_sessions(self, arguments: Dict[str, Any]) -> str:
        """List recent sessions for a project."""
        return await self.analytics_ops.list_recent_sessions(arguments)

    async def get_session_analytics(self, arguments: Dict[str, Any]) -> str:
        """Get session analytics and metrics."""
        return await self.analytics_ops.get_session_analytics(arguments)

    async def archive_stale_periods(self, arguments: Dict[str, Any]) -> str:
        """Archive stale work periods with no recent activity."""
        return await self.analytics_ops.archive_stale_periods(arguments)

    async def boot_session_with_git_detection(self, arguments: Dict[str, Any]) -> str:
        """Enhanced session boot with Git change detection and organizational reconciliation."""
        return await self.git_ops.boot_session_with_git_detection(arguments)

    async def get_initialization_summary(self, arguments: Dict[str, Any]) -> str:
        """Get detailed summary of file metadata initialization progress."""
        return await self.init_ops.get_initialization_summary(arguments)

    async def reset_initialization(self, arguments: Dict[str, Any]) -> str:
        """Reset file metadata initialization to start fresh."""
        return await self.init_ops.reset_initialization(arguments)

    async def _check_initialization_status(self, session_id: str) -> str:
        """Check file metadata initialization status and provide user feedback."""
        return await self.init_ops.check_initialization_status(session_id)

    def _identify_instance_type(self, project_path: Path) -> str:
        """Identify if this is a main instance or branch instance based on marker files."""
        return self.init_ops.identify_instance_type(project_path)

    def _generate_boot_report(self, instance_type: str, git_changes: Optional[Dict],
                            reconciliation_result: Optional[Dict], session_result: str) -> str:
        """Generate comprehensive boot report."""
        return self.init_ops.generate_boot_report(instance_type, git_changes, reconciliation_result, session_result)