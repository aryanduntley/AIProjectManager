"""
MCP API and tool registry for the AI Project Manager server.

Handles tool registration, request routing, and response formatting.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolRequest
from pydantic import BaseModel

from core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None


class MCPToolRegistry:
    """Registry for MCP tools with automatic discovery and registration."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        
    async def register_all_tools(self, server: Server):
        """Register all available tools with the MCP server."""
        try:
            # Import tool modules
            await self._discover_tools()
            
            # Register tools with the server
            for tool_name, tool_def in self.tools.items():
                tool = Tool(
                    name=tool_name,
                    description=tool_def.description,
                    inputSchema=tool_def.input_schema
                )
                server.list_tools().append(tool)
                logger.debug(f"Registered tool: {tool_name}")
            
            # Set up tool call handler
            @server.call_tool()
            async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
                return await self._handle_tool_call(name, arguments)
            
            logger.info(f"Registered {len(self.tools)} tools successfully")
            
        except Exception as e:
            logger.error(f"Error registering tools: {e}")
            raise
    
    async def _discover_tools(self):
        """Discover and import all tool modules."""
        try:
            # Import project tools
            from tools.project_tools import ProjectTools
            await self._register_tool_module(ProjectTools())
            
            # Import task tools
            from tools.task_tools import TaskTools
            await self._register_tool_module(TaskTools())
            
            # Import file tools
            from tools.file_tools import FileTools
            await self._register_tool_module(FileTools())
            
            # Import theme tools
            from tools.theme_tools import ThemeTools
            await self._register_tool_module(ThemeTools())
            
            # Import log tools
            from tools.log_tools import LogTools
            await self._register_tool_module(LogTools())
            
            # Import config tools
            from tools.config_tools import ConfigTools
            await self._register_tool_module(ConfigTools())
            
        except ImportError as e:
            logger.warning(f"Some tool modules not available yet: {e}")
            # For now, register basic tools manually
            await self._register_basic_tools()
    
    async def _register_tool_module(self, tool_module):
        """Register tools from a tool module."""
        if hasattr(tool_module, 'get_tools'):
            tools = await tool_module.get_tools()
            for tool_def in tools:
                self.tools[tool_def.name] = tool_def
                self.tool_handlers[tool_def.name] = tool_def.handler
    
    async def _register_basic_tools(self):
        """Register basic tools for initial functionality."""
        # Basic project initialization tool
        self.tools["project_init"] = ToolDefinition(
            name="project_init",
            description="Initialize project management structure",
            input_schema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force initialization even if structure exists",
                        "default": False
                    }
                },
                "required": ["project_path"]
            }
        )
        self.tool_handlers["project_init"] = self._handle_project_init
        
        # Basic configuration tool
        self.tools["get_config"] = ToolDefinition(
            name="get_config",
            description="Get current configuration settings",
            input_schema={
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "description": "Configuration section to retrieve (optional)"
                    }
                }
            }
        )
        self.tool_handlers["get_config"] = self._handle_get_config
        
        # Basic file operations
        self.tools["read_file"] = ToolDefinition(
            name="read_file",
            description="Read a file with project awareness",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "project_relative": {
                        "type": "boolean",
                        "description": "Whether path is relative to project root",
                        "default": True
                    }
                },
                "required": ["file_path"]
            }
        )
        self.tool_handlers["read_file"] = self._handle_read_file
        
        logger.info("Registered basic tools")
    
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
    
    async def _handle_project_init(self, arguments: Dict[str, Any]) -> str:
        """Handle project initialization."""
        try:
            project_path = Path(arguments["project_path"])
            force = arguments.get("force", False)
            
            # Check if project structure already exists
            project_mgmt_dir = project_path / "projectManagement"
            if project_mgmt_dir.exists() and not force:
                return f"Project management structure already exists at {project_mgmt_dir}. Use force=true to override."
            
            # Create basic structure
            await self._create_project_structure(project_path)
            
            return f"Project management structure initialized at {project_mgmt_dir}"
            
        except Exception as e:
            logger.error(f"Error in project_init: {e}")
            return f"Error initializing project: {str(e)}"
    
    async def _create_project_structure(self, project_path: Path):
        """Create the basic project management structure."""
        project_mgmt_dir = project_path / "projectManagement"
        
        # Create directory structure
        directories = [
            "ProjectBlueprint",
            "ProjectFlow", 
            "ProjectLogic",
            "Themes",
            "Tasks/active",
            "Tasks/sidequests", 
            "Tasks/archive/tasks",
            "Tasks/archive/sidequests",
            "Logs/current",
            "Logs/archived",
            "Logs/compressed",
            "Placeholders",
            "UserSettings"
        ]
        
        for dir_path in directories:
            (project_mgmt_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create basic files
        files = {
            "ProjectBlueprint/blueprint.md": "# Project Blueprint\n\nTo be defined...\n",
            "ProjectFlow/flow-index.json": '{"flowFiles": [], "metadata": {"version": "1.0.0", "description": "Master flow index"}}',
            "ProjectLogic/projectlogic.jsonl": "",
            "Themes/themes.json": "{}",
            "Tasks/completion-path.json": '{"completionObjective": "To be defined", "steps": []}',
            "Logs/current/ai-decisions.jsonl": "",
            "Logs/current/user-feedback.jsonl": "",
            "Placeholders/todos.jsonl": "",
            "UserSettings/config.json": '{"project": {"max_file_lines": 900, "auto_modularize": true}}'
        }
        
        for file_path, content in files.items():
            full_path = project_mgmt_dir / file_path
            if not full_path.exists():
                full_path.write_text(content)
    
    async def _handle_get_config(self, arguments: Dict[str, Any]) -> str:
        """Handle configuration retrieval."""
        try:
            config = self.config_manager.get_config()
            section = arguments.get("section")
            
            if section:
                if hasattr(config, section):
                    section_config = getattr(config, section)
                    return section_config.model_dump_json(indent=2)
                else:
                    return f"Configuration section '{section}' not found"
            else:
                return config.model_dump_json(indent=2)
                
        except Exception as e:
            logger.error(f"Error in get_config: {e}")
            return f"Error retrieving configuration: {str(e)}"
    
    async def _handle_read_file(self, arguments: Dict[str, Any]) -> str:
        """Handle file reading."""
        try:
            file_path = Path(arguments["file_path"])
            project_relative = arguments.get("project_relative", True)
            
            if project_relative:
                # Assume current working directory is project root for now
                file_path = Path.cwd() / file_path
            
            if not file_path.exists():
                return f"File not found: {file_path}"
            
            if file_path.is_dir():
                return f"Path is a directory: {file_path}"
            
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            return f"Content of {file_path}:\n\n{content}"
            
        except Exception as e:
            logger.error(f"Error in read_file: {e}")
            return f"Error reading file: {str(e)}"