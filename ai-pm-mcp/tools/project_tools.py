"""
Project Tools - Refactored Modular Implementation

Project management tools for the AI Project Manager MCP Server.
Handles project initialization, blueprint management, and project structure operations.

This is a refactored version that delegates to specialized project handlers.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.mcp_api import ToolDefinition
from ..database.db_manager import DatabaseManager
from ..database.session_queries import SessionQueries
from ..database.task_status_queries import TaskStatusQueries
from ..database.theme_flow_queries import ThemeFlowQueries
from ..database.file_metadata_queries import FileMetadataQueries

# Project handlers
from .project.initialization_operations import ProjectInitializationOperations
from .project.blueprint_management import ProjectBlueprintManager
from .project.database_operations import ProjectDatabaseOperations
from .project.status_monitoring import ProjectStatusMonitor
from .project.implementation_planning import ImplementationPlanner

logger = logging.getLogger(__name__)


class ProjectTools:
    """Tools for project management operations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None, config_manager=None, directive_processor=None, server_instance=None):
        self.tools = []
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.directive_processor = directive_processor
        self.server_instance = server_instance
        self.session_queries = SessionQueries(db_manager) if db_manager else None
        self.task_queries = TaskStatusQueries(db_manager) if db_manager else None
        self.theme_flow_queries = ThemeFlowQueries(db_manager) if db_manager else None
        self.file_metadata_queries = FileMetadataQueries(db_manager) if db_manager else None
        
        # Initialize project handlers
        handler_kwargs = {
            'db_manager': db_manager,
            'config_manager': config_manager,
            'directive_processor': directive_processor,
            'server_instance': server_instance,
            'session_queries': self.session_queries,
            'task_queries': self.task_queries,
            'theme_flow_queries': self.theme_flow_queries,
            'file_metadata_queries': self.file_metadata_queries
        }
        
        self.initialization_ops = ProjectInitializationOperations(**handler_kwargs)
        self.blueprint_manager = ProjectBlueprintManager(**handler_kwargs)
        self.database_ops = ProjectDatabaseOperations(**handler_kwargs)
        self.status_monitor = ProjectStatusMonitor(**handler_kwargs)
        self.implementation_planner = ImplementationPlanner(**handler_kwargs)
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all project management tools."""
        return [
            ToolDefinition(
                name="project_initialize",
                description="Initialize project management structure in a directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "project_name": {"type": "string", "description": "Name of the project"},
                        "force": {"type": "boolean", "description": "Force initialization even if structure exists", "default": False},
                        "description": {"type": "string", "description": "Project description (optional)"},
                        "initialize_database": {"type": "boolean", "description": "Initialize project database", "default": True}
                    },
                    "required": ["project_path", "project_name"]
                },
                handler=self.initialize_project
            ),
            ToolDefinition(
                name="project_get_blueprint",
                description="Get the current project blueprint",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"}
                    },
                    "required": ["project_path"]
                },
                handler=self.get_blueprint
            ),
            ToolDefinition(
                name="project_update_blueprint",
                description="Update the project blueprint",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "updates": {"type": "object", "description": "Blueprint updates"}
                    },
                    "required": ["project_path", "updates"]
                },
                handler=self.update_blueprint
            ),
            ToolDefinition(
                name="project_get_status",
                description="Get overall project status and structure information",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"}
                    },
                    "required": ["project_path"]
                },
                handler=self.get_project_status
            ),
            ToolDefinition(
                name="project_init_database",
                description="Initialize database for an existing project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"}
                    },
                    "required": ["project_path"]
                },
                handler=self.initialize_database
            ),
            ToolDefinition(
                name="resume_initialization",
                description="Resume file metadata initialization for a project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "project_name": {"type": "string", "description": "Project name (optional, will be read from blueprint)"}
                    },
                    "required": ["project_path"]
                },
                handler=self.resume_file_metadata_initialization
            ),
            ToolDefinition(
                name="get_initialization_progress",
                description="Get initialization progress for a project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"}
                    },
                    "required": ["project_path"]
                },
                handler=self.get_initialization_progress
            ),
            ToolDefinition(
                name="create_implementation_plan",
                description="Create a new implementation plan",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "milestone_id": {"type": "string", "description": "Milestone ID (e.g., M-01, M-02)"},
                        "title": {"type": "string", "description": "Implementation plan title"},
                        "version": {"type": "string", "description": "Plan version (e.g., v1, v2)", "default": "v1"},
                        "is_high_priority": {"type": "boolean", "description": "Whether this is a high-priority implementation plan", "default": False}
                    },
                    "required": ["project_path", "milestone_id", "title"]
                },
                handler=self.create_implementation_plan
            )
        ]
    
    # Handler methods that delegate to the appropriate modules
    async def initialize_project(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ProjectInitializationOperations."""
        return await self.initialization_ops.initialize_project(
            Path(arguments["project_path"]),
            arguments["project_name"],
            arguments.get("force", False),
            arguments.get("description"),
            arguments.get("initialize_database", True)
        )
    
    async def get_blueprint(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ProjectBlueprintManager."""
        return await self.blueprint_manager.get_blueprint(
            Path(arguments["project_path"])
        )
    
    async def update_blueprint(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ProjectBlueprintManager."""
        return await self.blueprint_manager.update_blueprint(
            Path(arguments["project_path"]),
            arguments["updates"]
        )
    
    async def get_project_status(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ProjectStatusMonitor."""
        return await self.status_monitor.get_project_status(
            Path(arguments["project_path"])
        )
    
    async def initialize_database(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ProjectDatabaseOperations."""
        return await self.database_ops.initialize_database(
            Path(arguments["project_path"])
        )
    
    async def resume_file_metadata_initialization(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ProjectDatabaseOperations."""
        return await self.database_ops.resume_file_metadata_initialization(
            Path(arguments["project_path"]),
            arguments.get("project_name")
        )
    
    async def get_initialization_progress(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ProjectDatabaseOperations."""
        return await self.database_ops.get_initialization_progress(
            Path(arguments["project_path"])
        )
    
    async def create_implementation_plan(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ImplementationPlanner."""
        return await self.implementation_planner.create_implementation_plan(
            Path(arguments["project_path"]),
            arguments["milestone_id"],
            arguments["title"],
            arguments.get("version", "v1"),
            arguments.get("is_high_priority", False)
        )