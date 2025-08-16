"""
Theme Tools - Refactored Modular Implementation

Theme management tools for the AI Project Manager MCP Server.
Handles theme discovery, creation, management, and context loading.

This is a refactored version that delegates to specialized theme handlers.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..core.mcp_api import ToolDefinition
from ..database.theme_flow_queries import ThemeFlowQueries
from ..database.file_metadata_queries import FileMetadataQueries

# Theme handlers
from .theme.discovery_operations import ThemeDiscoveryOperations
from .theme.management_operations import ThemeManagementOperations
from .theme.validation_operations import ThemeValidationOperations
from .theme.flow_integration import ThemeFlowIntegration
from .theme.context_operations import ThemeContextOperations

logger = logging.getLogger(__name__)


class ThemeTools:
    """Tools for theme management and discovery."""
    
    def __init__(self, theme_flow_queries: Optional[ThemeFlowQueries] = None, 
                 file_metadata_queries: Optional[FileMetadataQueries] = None, config_manager=None):
        self.theme_flow_queries = theme_flow_queries
        self.file_metadata_queries = file_metadata_queries
        self.config_manager = config_manager
        self.server_instance = None  # Will be set by MCPToolRegistry
        
        # Initialize theme handlers
        handler_kwargs = {
            'theme_flow_queries': theme_flow_queries,
            'file_metadata_queries': file_metadata_queries,
            'config_manager': config_manager
        }
        
        self.discovery_ops = ThemeDiscoveryOperations(**handler_kwargs)
        self.management_ops = ThemeManagementOperations(**handler_kwargs)
        self.validation_ops = ThemeValidationOperations(**handler_kwargs)
        self.flow_integration = ThemeFlowIntegration(**handler_kwargs)
        self.context_ops = ThemeContextOperations(**handler_kwargs)
        
        # Set server instance on all handlers when available
        for handler in [self.discovery_ops, self.management_ops, self.validation_ops,
                       self.flow_integration, self.context_ops]:
            handler.server_instance = self.server_instance
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all theme management tools."""
        return [
            ToolDefinition(
                name="theme_discover",
                description="Automatically discover themes in a project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "force_rediscovery": {"type": "boolean", "default": False, "description": "Force rediscovery even if themes exist"}
                    },
                    "required": ["project_path"]
                },
                handler=self.discover_themes
            ),
            ToolDefinition(
                name="theme_create",
                description="Create a new theme definition",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "theme_name": {"type": "string", "description": "Name of the theme"},
                        "description": {"type": "string", "description": "Description of the theme"},
                        "paths": {"type": "array", "items": {"type": "string"}, "description": "Directory paths for this theme"},
                        "files": {"type": "array", "items": {"type": "string"}, "description": "Specific files for this theme"},
                        "linked_themes": {"type": "array", "items": {"type": "string"}, "description": "Related themes", "default": []}
                    },
                    "required": ["project_path", "theme_name", "description"]
                },
                handler=self.create_theme
            ),
            ToolDefinition(
                name="theme_list",
                description="List all themes in a project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "include_details": {"type": "boolean", "description": "Include detailed theme information", "default": False}
                    },
                    "required": ["project_path"]
                },
                handler=self.list_themes
            ),
            ToolDefinition(
                name="theme_get",
                description="Get detailed information about a specific theme",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "theme_name": {"type": "string", "description": "Name of the theme"}
                    },
                    "required": ["project_path", "theme_name"]
                },
                handler=self.get_theme
            ),
            ToolDefinition(
                name="theme_update",
                description="Update an existing theme definition",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "theme_name": {"type": "string", "description": "Name of the theme"},
                        "updates": {
                            "type": "object",
                            "description": "Updates to apply to the theme",
                            "properties": {
                                "description": {"type": "string"},
                                "paths": {"type": "array", "items": {"type": "string"}},
                                "files": {"type": "array", "items": {"type": "string"}},
                                "linkedThemes": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "required": ["project_path", "theme_name", "updates"]
                },
                handler=self.update_theme
            ),
            ToolDefinition(
                name="theme_delete",
                description="Delete a theme definition",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "theme_name": {"type": "string", "description": "Name of the theme to delete"},
                        "confirm": {"type": "boolean", "description": "Confirmation flag", "default": False}
                    },
                    "required": ["project_path", "theme_name", "confirm"]
                },
                handler=self.delete_theme
            ),
            ToolDefinition(
                name="theme_get_context",
                description="Get context for themes based on context mode",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "primary_theme": {"type": "string", "description": "Primary theme for context loading"},
                        "context_mode": {
                            "type": "string",
                            "enum": ["theme-focused", "theme-expanded", "project-wide"],
                            "description": "Context loading mode",
                            "default": "theme-focused"
                        }
                    },
                    "required": ["project_path", "primary_theme"]
                },
                handler=self.get_theme_context
            ),
            ToolDefinition(
                name="theme_validate",
                description="Validate theme consistency and detect issues",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "theme_name": {"type": "string", "description": "Specific theme to validate (optional)"}
                    },
                    "required": ["project_path"]
                },
                handler=self.validate_themes
            ),
            ToolDefinition(
                name="theme_sync_flows",
                description="Synchronize theme-flow relationships with database",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "theme_name": {"type": "string", "description": "Specific theme to sync (optional)"}
                    },
                    "required": ["project_path"]
                },
                handler=self.sync_theme_flows
            ),
            ToolDefinition(
                name="theme_get_flows",
                description="Get flows associated with a theme",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to the project directory"},
                        "theme_name": {"type": "string", "description": "Theme name"}
                    },
                    "required": ["project_path", "theme_name"]
                },
                handler=self.get_theme_flows
            )
        ]
    
    # Handler methods that delegate to the appropriate modules
    async def discover_themes(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeDiscoveryOperations."""
        return await self.discovery_ops.discover_themes(
            Path(arguments["project_path"]),
            arguments.get("force_rediscovery", False)
        )
    
    async def create_theme(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeManagementOperations."""
        return await self.management_ops.create_theme(
            Path(arguments["project_path"]),
            arguments["theme_name"],
            arguments["description"],
            arguments.get("paths", []),
            arguments.get("files", []),
            arguments.get("linked_themes", [])
        )
    
    async def list_themes(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeManagementOperations."""
        return await self.management_ops.list_themes(
            Path(arguments["project_path"]),
            arguments.get("include_details", False)
        )
    
    async def get_theme(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeManagementOperations."""
        return await self.management_ops.get_theme(
            Path(arguments["project_path"]),
            arguments["theme_name"]
        )
    
    async def update_theme(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeManagementOperations."""
        return await self.management_ops.update_theme(
            Path(arguments["project_path"]),
            arguments["theme_name"],
            arguments["updates"]
        )
    
    async def delete_theme(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeManagementOperations."""
        return await self.management_ops.delete_theme(
            Path(arguments["project_path"]),
            arguments["theme_name"],
            arguments.get("confirm", False)
        )
    
    async def get_theme_context(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeContextOperations."""
        return await self.context_ops.get_theme_context(
            Path(arguments["project_path"]),
            arguments["primary_theme"],
            arguments.get("context_mode", "theme-focused")
        )
    
    async def validate_themes(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeValidationOperations."""
        return await self.validation_ops.validate_themes(
            Path(arguments["project_path"]),
            arguments.get("theme_name")
        )
    
    async def sync_theme_flows(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeFlowIntegration."""
        return await self.flow_integration.sync_theme_flows(
            Path(arguments["project_path"]),
            arguments.get("theme_name")
        )
    
    async def get_theme_flows(self, arguments: Dict[str, Any]) -> str:
        """Delegate to ThemeFlowIntegration."""
        return await self.flow_integration.get_theme_flows(
            Path(arguments["project_path"]),
            arguments["theme_name"]
        )