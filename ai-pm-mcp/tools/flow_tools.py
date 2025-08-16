"""
Flow Tools - Refactored Modular Implementation

Multi-flow system management tools for the AI Project Manager MCP Server.
Handles selective flow loading, cross-flow dependencies, flow index management,
and integration with the database-driven theme-flow relationship system.

This is a refactored version that delegates to specialized flow handlers.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Core components
from ..core.mcp_api import ToolDefinition
from ..database.theme_flow_queries import ThemeFlowQueries
from ..database.session_queries import SessionQueries
from ..database.file_metadata_queries import FileMetadataQueries

# Flow handlers
from .flow.index_management import FlowIndexManager
from .flow.loading_optimization import FlowLoadingOptimizer
from .flow.dependency_analysis import FlowDependencyAnalyzer
from .flow.database_sync import FlowDatabaseSync
from .flow.status_management import FlowStatusManager

logger = logging.getLogger(__name__)


class FlowTools:
    """Tools for multi-flow system management with database integration."""
    
    def __init__(self, 
                 theme_flow_queries: Optional[ThemeFlowQueries] = None,
                 session_queries: Optional[SessionQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None,
                 config_manager=None):
        self.theme_flow_queries = theme_flow_queries
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
        self.config_manager = config_manager
        self.server_instance = None  # Will be set by MCPToolRegistry
        
        # Initialize flow handlers
        handler_kwargs = {
            'theme_flow_queries': theme_flow_queries,
            'session_queries': session_queries,
            'file_metadata_queries': file_metadata_queries,
            'config_manager': config_manager
        }
        
        self.index_manager = FlowIndexManager(**handler_kwargs)
        self.loading_optimizer = FlowLoadingOptimizer(**handler_kwargs)
        self.dependency_analyzer = FlowDependencyAnalyzer(**handler_kwargs)
        self.database_sync = FlowDatabaseSync(**handler_kwargs)
        self.status_manager = FlowStatusManager(**handler_kwargs)
        
        # Set server instance on all handlers when available
        for handler in [self.index_manager, self.loading_optimizer, self.dependency_analyzer, 
                       self.database_sync, self.status_manager]:
            handler.server_instance = self.server_instance
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get available flow management tools."""
        return [
            ToolDefinition(
                name="flow_index_create",
                description="Create or update flow index with multi-flow coordination",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "flows": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "flow_id": {"type": "string"},
                                    "flow_file": {"type": "string"},
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "primary_themes": {"type": "array", "items": {"type": "string"}},
                                    "secondary_themes": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["flow_id", "flow_file", "name"]
                            },
                            "description": "List of flows to include in the index"
                        },
                        "cross_flow_dependencies": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "from_flow": {"type": "string"},
                                    "to_flow": {"type": "string"},
                                    "dependency_type": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            },
                            "description": "Cross-flow dependencies"
                        }
                    },
                    "required": ["project_path", "flows"]
                },
                handler=self.create_flow_index
            ),
            ToolDefinition(
                name="flow_create",
                description="Create a new individual flow file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "flow_id": {"type": "string", "description": "Unique identifier for the flow"},
                        "flow_name": {"type": "string", "description": "Human-readable name for the flow"},
                        "domain": {"type": "string", "description": "Domain or theme category"},
                        "description": {"type": "string", "description": "Description of what this flow accomplishes"},
                        "primary_themes": {"type": "array", "items": {"type": "string"}, "description": "Primary themes"},
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_id": {"type": "string"},
                                    "trigger": {"type": "string"},
                                    "user_experience": {"type": "string"},
                                    "conditions": {"type": "array", "items": {"type": "string"}},
                                    "outcomes": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "description": "Flow steps"
                        }
                    },
                    "required": ["project_path", "flow_id", "flow_name", "domain"]
                },
                handler=self.create_flow
            ),
            ToolDefinition(
                name="flow_load_selective",
                description="Selectively load flows based on task requirements and themes",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "task_themes": {"type": "array", "items": {"type": "string"}, "description": "Required themes"},
                        "task_description": {"type": "string", "description": "Task description for context analysis"},
                        "max_flows": {"type": "integer", "default": 5, "description": "Maximum flows to load"},
                        "session_id": {"type": "string", "description": "Session ID for tracking"}
                    },
                    "required": ["project_path", "task_themes"]
                },
                handler=self.load_flows_selective
            ),
            ToolDefinition(
                name="flow_dependencies_analyze",
                description="Analyze cross-flow dependencies and recommend loading order",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "flow_ids": {"type": "array", "items": {"type": "string"}, "description": "Flow IDs to analyze"},
                        "include_indirect": {"type": "boolean", "default": True, "description": "Include indirect dependencies"}
                    },
                    "required": ["project_path", "flow_ids"]
                },
                handler=self.analyze_flow_dependencies
            ),
            ToolDefinition(
                name="flow_status_update",
                description="Update flow and step status with database persistence",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "flow_id": {"type": "string", "description": "Flow ID to update"},
                        "status": {"type": "string", "enum": ["pending", "in-progress", "complete", "needs-review", "blocked"]},
                        "completion_percentage": {"type": "integer", "minimum": 0, "maximum": 100},
                        "step_updates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_id": {"type": "string"},
                                    "status": {"type": "string"},
                                    "completed_at": {"type": "string"}
                                }
                            }
                        },
                        "session_id": {"type": "string", "description": "Session ID for tracking"}
                    },
                    "required": ["project_path", "flow_id"]
                },
                handler=self.update_flow_status
            ),
            ToolDefinition(
                name="flow_optimize_loading",
                description="Get optimized flow loading recommendations based on usage patterns",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "current_context": {"type": "object", "description": "Current context information"},
                        "task_complexity": {"type": "string", "enum": ["simple", "moderate", "complex"], "default": "moderate"},
                        "session_id": {"type": "string", "description": "Session ID for historical analysis"}
                    },
                    "required": ["project_path"]
                },
                handler=self.optimize_flow_loading
            ),
            ToolDefinition(
                name="flow_sync_database",
                description="Synchronize flow definitions with database for optimal performance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "force_update": {"type": "boolean", "default": False, "description": "Force update even if no changes detected"}
                    },
                    "required": ["project_path"]
                },
                handler=self.sync_flows_with_database
            )
        ]
    
    # Handler methods that delegate to the appropriate modules
    async def create_flow_index(self, arguments: Dict[str, Any]) -> str:
        """Delegate to FlowIndexManager."""
        return await self.index_manager.create_flow_index(
            Path(arguments["project_path"]),
            arguments["flows"],
            arguments.get("cross_flow_dependencies", [])
        )
    
    async def create_flow(self, arguments: Dict[str, Any]) -> str:
        """Delegate to FlowIndexManager."""
        return await self.index_manager.create_flow(
            Path(arguments["project_path"]),
            arguments["flow_id"],
            arguments["flow_name"],
            arguments["domain"],
            arguments.get("description", ""),
            arguments.get("primary_themes", []),
            arguments.get("steps", [])
        )
    
    async def load_flows_selective(self, arguments: Dict[str, Any]) -> str:
        """Delegate to FlowLoadingOptimizer."""
        return await self.loading_optimizer.load_flows_selective(
            Path(arguments["project_path"]),
            arguments["task_themes"],
            arguments.get("task_description", ""),
            arguments.get("max_flows", 5),
            arguments.get("session_id")
        )
    
    async def analyze_flow_dependencies(self, arguments: Dict[str, Any]) -> str:
        """Delegate to FlowDependencyAnalyzer."""
        return await self.dependency_analyzer.analyze_flow_dependencies(
            Path(arguments["project_path"]),
            arguments["flow_ids"],
            arguments.get("include_indirect", True)
        )
    
    async def update_flow_status(self, arguments: Dict[str, Any]) -> str:
        """Delegate to FlowStatusManager."""
        return await self.status_manager.update_flow_status(
            Path(arguments["project_path"]),
            arguments["flow_id"],
            arguments.get("status"),
            arguments.get("completion_percentage"),
            arguments.get("step_updates", []),
            arguments.get("session_id")
        )
    
    async def optimize_flow_loading(self, arguments: Dict[str, Any]) -> str:
        """Delegate to FlowLoadingOptimizer."""
        return await self.loading_optimizer.optimize_flow_loading(
            Path(arguments["project_path"]),
            arguments.get("current_context", {}),
            arguments.get("task_complexity", "moderate"),
            arguments.get("session_id")
        )
    
    async def sync_flows_with_database(self, arguments: Dict[str, Any]) -> str:
        """Delegate to FlowDatabaseSync."""
        return await self.database_sync.sync_flows_with_database(
            Path(arguments["project_path"]),
            arguments.get("force_update", False)
        )