"""
MCP API and tool registry for the AI Project Manager server.

Handles tool registration, request routing, and response formatting.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import asyncio
import sys

# Add deps directory to Python path for project-specific dependencies
deps_path = Path(__file__).parent.parent / "deps"
if deps_path.exists():
    sys.path.insert(0, str(deps_path))

from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolRequest
from pydantic import BaseModel

from .config_manager import ConfigManager
from .scope_engine import ScopeEngine
from .processor import TaskProcessor
from .mcpApi.tool_registration import ToolRegistration
from .mcpApi.database_initializer import DatabaseInitializer
from .mcpApi.enhanced_tool_handlers import EnhancedToolHandlers
from .mcpApi.basic_tool_handlers import BasicToolHandlers
from ..database.db_manager import DatabaseManager
from ..database.session_queries import SessionQueries
from ..database.task_status_queries import TaskStatusQueries
from ..database.theme_flow_queries import ThemeFlowQueries
from ..database.file_metadata_queries import FileMetadataQueries
from ..database.user_preference_queries import UserPreferenceQueries
from ..database.event_queries import EventQueries
from ..utils.project_paths import get_project_management_path, get_database_path

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None


class MCPToolRegistry:
    """Registry for MCP tools with automatic discovery and registration."""
    
    def __init__(self, config_manager: ConfigManager, directive_processor=None):
        self.config_manager = config_manager
        self.directive_processor = directive_processor
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        
        # Server instance for hook point integration
        self.server_instance = None
        
        # Database components
        self.db_manager: Optional[DatabaseManager] = None
        self.session_queries: Optional[SessionQueries] = None
        self.task_queries: Optional[TaskStatusQueries] = None
        self.theme_flow_queries: Optional[ThemeFlowQueries] = None
        self.file_metadata_queries: Optional[FileMetadataQueries] = None
        self.user_preference_queries: Optional[UserPreferenceQueries] = None
        self.event_queries: Optional[EventQueries] = None
        
        # Core processing components
        self.scope_engine: Optional[ScopeEngine] = None
        self.task_processor: Optional[TaskProcessor] = None
        
        # Advanced intelligence components
        self.analytics_dashboard = None
        
        # Tool instances for ActionExecutor integration (FIX for ActionExecutor access)
        self.tool_instances: Dict[str, Any] = {}
        
        # Modularized components
        self.tool_registration = ToolRegistration(self)
        self.database_initializer = DatabaseInitializer(self)
        self.enhanced_tool_handlers = EnhancedToolHandlers(self)
        self.basic_tool_handlers = BasicToolHandlers(self)
        
        # Make ToolDefinition available for modular components
        self.ToolDefinition = ToolDefinition
        
    async def register_all_tools(self, server: Server, project_path: Optional[str] = None):
        """Register all available tools with the MCP server."""
        # DEBUG_DATABASE: Minimal debugging for database initialization tracking
        debug_file = Path(".") / "debug_database.log"
        def write_database_debug(msg):
            try:
                with open(debug_file, "a") as f:
                    f.write(f"{msg}\n")
            except Exception:
                pass
        
        write_database_debug(f"[DEBUG_DATABASE] === MCP_API: register_all_tools called ===")
        write_database_debug(f"[DEBUG_DATABASE] project_path: {project_path}")
        
        try:
            # Store server instance for hook point integration
            self.server_instance = server
            
            # Initialize database if project path provided
            if project_path:
                write_database_debug(f"[DEBUG_DATABASE] ✅ PROJECT PATH PROVIDED - Testing _initialize_database")
                await self.database_initializer._initialize_database(project_path)
                
                write_database_debug(f"[DEBUG_DATABASE] ✅ _initialize_database completed successfully")
                write_database_debug(f"[DEBUG_DATABASE] DB Manager now available: {hasattr(self, 'db_manager') and self.db_manager is not None}")
                # Initialize core processing components
                # await self.database_initializer._initialize_core_components(project_path)
            else:
                write_database_debug(f"[DEBUG_DATABASE] ❌ NO PROJECT PATH - Skipping database initialization")
            
            # Import tool modules
            write_database_debug(f"[DEBUG_DATABASE] About to discover tools")
            await self.tool_registration._discover_tools()
            write_database_debug(f"[DEBUG_DATABASE] ✅ Tools discovered successfully")
            
            # Register list_tools handler
            @server.list_tools()
            async def list_tools() -> List[Tool]:
                tools = []
                for tool_name, tool_def in self.tools.items():
                    tool = Tool(
                        name=tool_name,
                        description=tool_def.description,
                        inputSchema=tool_def.input_schema
                    )
                    tools.append(tool)
                    logger.debug(f"Added tool to list: {tool_name}")
                return tools
            
            # Set up tool call handler
            @server.call_tool()
            async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
                return await self._handle_tool_call(name, arguments)
            
            logger.info(f"Registered {len(self.tools)} tools successfully")
            
        except Exception as e:
            logger.error(f"Error registering tools: {e}")
            raise
    
    async def _handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle incoming tool calls."""
        try:
            if name not in self.tool_handlers:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
            
            handler = self.tool_handlers[name]
            result = await handler(arguments)
            
            if isinstance(result, str):
                return [TextContent(type="text", text=result)]
            elif isinstance(result, list) and all(isinstance(item, TextContent) for item in result):
                return result
            else:
                return [TextContent(type="text", text=str(result))]
                
        except Exception as e:
            logger.error(f"Error handling tool call {name}: {e}")
            return [TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )]
        