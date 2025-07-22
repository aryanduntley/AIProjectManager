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

from core.config_manager import ConfigManager
from core.scope_engine import ScopeEngine
from core.processor import TaskProcessor
from database.db_manager import DatabaseManager
from database.session_queries import SessionQueries
from database.task_status_queries import TaskStatusQueries
from database.theme_flow_queries import ThemeFlowQueries
from database.file_metadata_queries import FileMetadataQueries
from database.user_preference_queries import UserPreferenceQueries
from database.event_queries import EventQueries

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
        
    async def register_all_tools(self, server: Server, project_path: Optional[str] = None):
        """Register all available tools with the MCP server."""
        try:
            # Initialize database if project path provided
            if project_path:
                await self._initialize_database(project_path)
                
                # Initialize core processing components
                await self._initialize_core_components(project_path)
            
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
            # Import project tools with database integration
            from tools.project_tools import ProjectTools
            project_tools = ProjectTools(self.db_manager)
            await self._register_tool_module(project_tools)
            
            # Import task tools with database integration
            from tools.task_tools import TaskTools
            task_tools = TaskTools(self.task_queries, self.session_queries, self.file_metadata_queries)
            await self._register_tool_module(task_tools)
            
            # Import session manager with database integration
            from tools.session_manager import SessionManager
            session_manager = SessionManager(self.session_queries, self.file_metadata_queries)
            await self._register_tool_module(session_manager)
            
            # Import file tools
            from tools.file_tools import FileTools
            await self._register_tool_module(FileTools())
            
            # Import theme tools with database integration
            from tools.theme_tools import ThemeTools
            theme_tools = ThemeTools(self.theme_flow_queries, self.file_metadata_queries)
            await self._register_tool_module(theme_tools)
            
            # Import flow tools with database integration
            from tools.flow_tools import FlowTools
            flow_tools = FlowTools(self.theme_flow_queries, self.session_queries, self.file_metadata_queries)
            await self._register_tool_module(flow_tools)
            
            # Import enhanced core processing tools if components available
            if self.scope_engine and self.task_processor:
                await self._register_enhanced_core_tools()
            
            # Import log tools with event queries integration
            from tools.log_tools import LogTools
            log_tools = LogTools(self.event_queries)
            await self._register_tool_module(log_tools)
            
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
        
        # Add database initialization tool
        self.tools["init_database"] = ToolDefinition(
            name="init_database",
            description="Initialize database for project management",
            input_schema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to the project directory"
                    }
                },
                "required": ["project_path"]
            }
        )
        self.tool_handlers["init_database"] = self._handle_init_database
        
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
            "Implementations/active",
            "Implementations/completed",
            "Logs/archived",
            "Placeholders",
            "UserSettings",
            "database"
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
            "Logs/noteworthy.json": "[]",
            "Placeholders/todos.jsonl": "",
            "UserSettings/config.json": '{"project": {"max_file_lines": 900, "auto_modularize": true}}'
        }
        
        for file_path, content in files.items():
            full_path = project_mgmt_dir / file_path
            if not full_path.exists():
                full_path.write_text(content)
        
        # Initialize database
        await self._initialize_database(str(project_path))
    
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
    
    async def _initialize_database(self, project_path: str):
        """Initialize database components for the project."""
        try:
            project_path_obj = Path(project_path)
            db_path = project_path_obj / "projectManagement" / "project.db"
            schema_path = project_path_obj / "projectManagement" / "database" / "schema.sql"
            
            # Copy schema from mcp-server if it doesn't exist
            if not schema_path.exists():
                # Get schema from mcp-server foundational location
                foundational_schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
                if foundational_schema_path.exists():
                    import shutil
                    shutil.copy2(foundational_schema_path, schema_path)
                    logger.info(f"Copied foundational database schema to {schema_path}")
            
            # Initialize database manager
            self.db_manager = DatabaseManager(str(project_path_obj))
            self.db_manager.connect()
            
            # Initialize query classes
            self.session_queries = SessionQueries(self.db_manager)
            self.task_queries = TaskStatusQueries(self.db_manager)
            self.theme_flow_queries = ThemeFlowQueries(self.db_manager)
            self.file_metadata_queries = FileMetadataQueries(self.db_manager)
            self.user_preference_queries = UserPreferenceQueries(self.db_manager)
            self.event_queries = EventQueries(self.db_manager)
            
            # Initialize analytics dashboard
            from core.analytics_dashboard import AnalyticsDashboard
            self.analytics_dashboard = AnalyticsDashboard(
                session_queries=self.session_queries,
                task_queries=self.task_queries,
                theme_flow_queries=self.theme_flow_queries,
                file_metadata_queries=self.file_metadata_queries,
                user_preference_queries=self.user_preference_queries
            )
            
            logger.info(f"Database and advanced intelligence initialized at {db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def _initialize_core_components(self, project_path: str):
        """Initialize core processing components with database integration."""
        try:
            mcp_server_path = Path(__file__).parent.parent
            
            # Initialize enhanced scope engine with database components
            self.scope_engine = ScopeEngine(
                mcp_server_path=mcp_server_path,
                theme_flow_queries=self.theme_flow_queries,
                session_queries=self.session_queries,
                file_metadata_queries=self.file_metadata_queries
            )
            
            # Initialize task processor
            self.task_processor = TaskProcessor(
                scope_engine=self.scope_engine,
                task_queries=self.task_queries,
                session_queries=self.session_queries,
                theme_flow_queries=self.theme_flow_queries,
                file_metadata_queries=self.file_metadata_queries
            )
            
            logger.info("Core processing components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing core components: {e}")
            raise
    
    async def _handle_init_database(self, arguments: Dict[str, Any]) -> str:
        """Handle database initialization."""
        try:
            project_path = arguments["project_path"]
            await self._initialize_database(project_path)
            return f"Database initialized successfully for project at {project_path}"
        except Exception as e:
            logger.error(f"Error in init_database: {e}")
            return f"Error initializing database: {str(e)}"
    
    async def _register_enhanced_core_tools(self):
        """Register enhanced core processing tools."""
        try:
            # Enhanced context loading tool
            self.tools["context_load_enhanced"] = ToolDefinition(
                name="context_load_enhanced",
                description="Load project context with database optimization and intelligent recommendations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "primary_theme": {
                            "type": "string",
                            "description": "Primary theme for context loading"
                        },
                        "context_mode": {
                            "type": "string",
                            "enum": ["theme-focused", "theme-expanded", "project-wide"],
                            "default": "theme-focused",
                            "description": "Context loading mode"
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Optional task ID for context tracking"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for analytics tracking"
                        }
                    },
                    "required": ["project_path", "primary_theme"]
                }
            )
            self.tool_handlers["context_load_enhanced"] = self._handle_enhanced_context_loading
            
            # Task processing tool
            self.tools["task_process"] = ToolDefinition(
                name="task_process",
                description="Process a task with intelligent context resolution and execution coordination",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "task_data": {
                            "type": "object",
                            "description": "Task data including taskId, description, theme, subtasks"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for processing"
                        }
                    },
                    "required": ["project_path", "task_data", "session_id"]
                }
            )
            self.tool_handlers["task_process"] = self._handle_task_processing
            
            # Flow context optimization tool
            self.tools["flow_context_optimize"] = ToolDefinition(
                name="flow_context_optimize",
                description="Get optimized context for specific flows using database relationships",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "flow_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of flow IDs to optimize context for"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Optional session ID for tracking"
                        }
                    },
                    "required": ["project_path", "flow_ids"]
                }
            )
            self.tool_handlers["flow_context_optimize"] = self._handle_flow_context_optimization
            
            # Intelligent recommendations tool
            self.tools["context_recommendations"] = ToolDefinition(
                name="context_recommendations",
                description="Get intelligent context recommendations based on task and historical data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "current_theme": {
                            "type": "string",
                            "description": "Current primary theme"
                        },
                        "current_mode": {
                            "type": "string",
                            "enum": ["theme-focused", "theme-expanded", "project-wide"],
                            "description": "Current context mode"
                        },
                        "task_description": {
                            "type": "string",
                            "description": "Description of the current task"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for historical analysis"
                        }
                    },
                    "required": ["project_path", "current_theme", "current_mode", "task_description"]
                }
            )
            self.tool_handlers["context_recommendations"] = self._handle_context_recommendations
            
            # Processing analytics tool
            self.tools["processing_analytics"] = ToolDefinition(
                name="processing_analytics",
                description="Get processing analytics for performance optimization and insights",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for analytics"
                        },
                        "time_range_hours": {
                            "type": "integer",
                            "default": 24,
                            "description": "Time range in hours for analytics"
                        }
                    },
                    "required": ["session_id"]
                }
            )
            self.tool_handlers["processing_analytics"] = self._handle_processing_analytics
            
            # Advanced Intelligence Tools (Phase 5)
            if self.analytics_dashboard:
                # Comprehensive analytics dashboard
                self.tools["analytics_dashboard"] = ToolDefinition(
                    name="analytics_dashboard", 
                    description="Get comprehensive project analytics dashboard with predictive insights",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path to the project directory"
                            },
                            "time_range_days": {
                                "type": "integer",
                                "default": 30,
                                "description": "Time range in days for analytics"
                            }
                        },
                        "required": ["project_path"]
                    }
                )
                self.tool_handlers["analytics_dashboard"] = self._handle_analytics_dashboard
                
                # Quick status summary
                self.tools["quick_status"] = ToolDefinition(
                    name="quick_status",
                    description="Get quick project status summary for session boot or health checks",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string", 
                                "description": "Path to the project directory"
                            }
                        },
                        "required": ["project_path"]
                    }
                )
                self.tool_handlers["quick_status"] = self._handle_quick_status
            
            # User preference learning tools
            if self.user_preference_queries:
                # Learn from user decisions
                self.tools["learn_preference"] = ToolDefinition(
                    name="learn_preference",
                    description="Learn user preferences from decisions and behavior",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "preference_type": {
                                "type": "string",
                                "enum": ["context", "theme", "workflow"],
                                "description": "Type of preference to learn"
                            },
                            "preference_data": {
                                "type": "object",
                                "description": "Data about the preference decision"
                            }
                        },
                        "required": ["preference_type", "preference_data"]
                    }
                )
                self.tool_handlers["learn_preference"] = self._handle_learn_preference
                
                # Get recommendations
                self.tools["get_recommendations"] = ToolDefinition(
                    name="get_recommendations",
                    description="Get intelligent recommendations based on learned user preferences",
                    input_schema={
                        "type": "object", 
                        "properties": {
                            "recommendation_type": {
                                "type": "string",
                                "enum": ["context", "theme", "workflow"],
                                "description": "Type of recommendations to get"
                            },
                            "context_data": {
                                "type": "object",
                                "description": "Current context for recommendations"
                            }
                        },
                        "required": ["recommendation_type", "context_data"]
                    }
                )
                self.tool_handlers["get_recommendations"] = self._handle_get_recommendations
            
            logger.info("Enhanced core processing tools and advanced intelligence registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering enhanced core tools: {e}")
    
    # Enhanced core tool handlers
    
    async def _handle_enhanced_context_loading(self, arguments: Dict[str, Any]) -> str:
        """Handle enhanced context loading with database optimization."""
        try:
            project_path = Path(arguments["project_path"])
            primary_theme = arguments["primary_theme"]
            context_mode = arguments.get("context_mode", "theme-focused")
            task_id = arguments.get("task_id")
            session_id = arguments.get("session_id")
            
            from core.scope_engine import ContextMode
            mode = ContextMode(context_mode)
            
            context = await self.scope_engine.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=primary_theme,
                context_mode=mode,
                task_id=task_id,
                session_id=session_id
            )
            
            summary = await self.scope_engine.get_context_summary(context)
            
            return f"Enhanced context loaded successfully:\n\n{summary}"
            
        except Exception as e:
            logger.error(f"Error in enhanced context loading: {e}")
            return f"Error loading enhanced context: {str(e)}"
    
    async def _handle_task_processing(self, arguments: Dict[str, Any]) -> str:
        """Handle intelligent task processing."""
        try:
            project_path = Path(arguments["project_path"])
            task_data = arguments["task_data"]
            session_id = arguments["session_id"]
            
            result = await self.task_processor.process_task(
                project_path=project_path,
                task_data=task_data,
                session_id=session_id
            )
            
            summary = (
                f"Task Processing Result: {result.result.value}\n"
                f"Task ID: {result.task_id}\n"
                f"Execution Time: {result.execution_time_ms}ms\n"
                f"Context Mode: {result.context_used.mode.value if result.context_used else 'None'}\n"
                f"Recommendations: {len(result.recommendations)}\n"
                f"Next Actions: {len(result.next_actions)}\n"
            )
            
            if result.recommendations:
                summary += "\nRecommendations:\n" + "\n".join(f"- {rec}" for rec in result.recommendations)
            
            if result.next_actions:
                summary += "\nNext Actions:\n" + "\n".join(f"- {action}" for action in result.next_actions)
            
            if result.errors:
                summary += "\nErrors:\n" + "\n".join(f"- {error}" for error in result.errors)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in task processing: {e}")
            return f"Error processing task: {str(e)}"
    
    async def _handle_flow_context_optimization(self, arguments: Dict[str, Any]) -> str:
        """Handle flow context optimization."""
        try:
            project_path = Path(arguments["project_path"])
            flow_ids = arguments["flow_ids"]
            session_id = arguments.get("session_id")
            
            context_data = await self.scope_engine.get_optimized_flow_context(
                project_path=project_path,
                flow_ids=flow_ids,
                session_id=session_id
            )
            
            if "error" in context_data:
                return f"Error optimizing flow context: {context_data['error']}"
            
            summary = (
                f"Flow Context Optimization Results:\n"
                f"Flows analyzed: {len(flow_ids)}\n"
                f"Related themes: {len(context_data.get('related_themes', []))}\n"
                f"Cross-flow dependencies: {len(context_data.get('cross_flow_dependencies', []))}\n"
                f"Recommended context mode: {context_data.get('recommended_context_mode')}\n"
            )
            
            if context_data.get("related_themes"):
                summary += f"\nRelated themes: {', '.join(context_data['related_themes'])}"
            
            if context_data.get("cross_flow_dependencies"):
                summary += f"\nCross-flow dependencies: {len(context_data['cross_flow_dependencies'])} found"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in flow context optimization: {e}")
            return f"Error optimizing flow context: {str(e)}"
    
    async def _handle_context_recommendations(self, arguments: Dict[str, Any]) -> str:
        """Handle intelligent context recommendations."""
        try:
            project_path = Path(arguments["project_path"])
            current_theme = arguments["current_theme"]
            current_mode = arguments["current_mode"]
            task_description = arguments["task_description"]
            session_id = arguments.get("session_id")
            
            # Load current context first
            from core.scope_engine import ContextMode
            mode = ContextMode(current_mode)
            
            current_context = await self.scope_engine.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=current_theme,
                context_mode=mode,
                session_id=session_id
            )
            
            recommendations = await self.scope_engine.get_intelligent_context_recommendations(
                project_path=project_path,
                current_context=current_context,
                task_description=task_description,
                session_id=session_id
            )
            
            if "error" in recommendations:
                return f"Error generating recommendations: {recommendations['error']}"
            
            summary = "Intelligent Context Recommendations:\n\n"
            
            # Current assessment
            assessment = recommendations.get("current_assessment", {})
            if assessment:
                summary += f"Current Assessment:\n"
                summary += f"- Mode: {assessment.get('mode')}\n"
                summary += f"- Themes loaded: {assessment.get('themes_loaded')}\n"
                summary += f"- Files available: {assessment.get('files_available')}\n"
                summary += f"- Memory usage: {assessment.get('memory_usage')}MB\n"
                summary += f"- Coverage score: {assessment.get('coverage_score')}\n\n"
            
            # Escalation recommendations
            escalation_recs = recommendations.get("escalation_recommendations", [])
            if escalation_recs:
                summary += "Escalation Recommendations:\n"
                for rec in escalation_recs:
                    summary += f"- {rec.get('reason', 'No reason')}: {rec.get('suggested_mode', 'No suggestion')}\n"
                summary += "\n"
            
            # Flow suggestions
            flow_suggestions = recommendations.get("flow_suggestions", [])
            if flow_suggestions:
                summary += "Flow Suggestions:\n"
                for suggestion in flow_suggestions:
                    summary += f"- {suggestion.get('flow_id')}: {suggestion.get('suggestion')}\n"
                summary += "\n"
            
            # Memory optimization
            memory_opts = recommendations.get("memory_optimization", [])
            if memory_opts:
                summary += "Memory Optimization:\n"
                for opt in memory_opts:
                    summary += f"- {opt.get('issue')}: {opt.get('current_usage')}MB\n"
                    for sugg in opt.get('suggestions', []):
                        summary += f"  * {sugg}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in context recommendations: {e}")
            return f"Error generating context recommendations: {str(e)}"
    
    async def _handle_processing_analytics(self, arguments: Dict[str, Any]) -> str:
        """Handle processing analytics."""
        try:
            session_id = arguments["session_id"]
            time_range_hours = arguments.get("time_range_hours", 24)
            
            analytics = await self.task_processor.get_processing_analytics(
                session_id=session_id,
                time_range_hours=time_range_hours
            )
            
            if "error" in analytics:
                return f"Error generating analytics: {analytics['error']}"
            
            summary = f"Processing Analytics (Last {time_range_hours} hours):\n\n"
            
            # Session summary
            session_summary = analytics.get("session_summary", {})
            if session_summary:
                summary += "Session Summary:\n"
                summary += f"- Total sessions: {session_summary.get('total_sessions', 0)}\n"
                summary += f"- Active time: {session_summary.get('total_active_time_hours', 0):.1f}h\n"
                summary += f"- Average session: {session_summary.get('average_session_duration_minutes', 0):.1f}min\n\n"
            
            # Context usage
            context_usage = analytics.get("context_usage", {})
            if context_usage:
                summary += "Context Usage:\n"
                summary += f"- Average memory: {context_usage.get('average_memory_mb', 0):.1f}MB\n"
                summary += f"- Most used mode: {context_usage.get('most_used_mode', 'N/A')}\n"
                summary += f"- Escalations: {context_usage.get('escalation_count', 0)}\n\n"
            
            # Task performance
            task_performance = analytics.get("task_performance", {})
            if task_performance:
                summary += "Task Performance:\n"
                summary += f"- Tasks completed: {task_performance.get('completed_tasks', 0)}\n"
                summary += f"- Average processing time: {task_performance.get('average_processing_time_ms', 0)}ms\n"
                summary += f"- Success rate: {task_performance.get('success_rate', 0):.1%}\n\n"
            
            # Recommendations
            recommendations = analytics.get("recommendations", [])
            if recommendations:
                summary += "Recommendations:\n"
                for rec in recommendations:
                    summary += f"- {rec}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in processing analytics: {e}")
            return f"Error generating processing analytics: {str(e)}"
    
    # Advanced Intelligence Tool Handlers (Phase 5)
    
    async def _handle_analytics_dashboard(self, arguments: Dict[str, Any]) -> str:
        """Handle comprehensive analytics dashboard request."""
        try:
            project_path = arguments["project_path"]
            time_range_days = arguments.get("time_range_days", 30)
            
            if not self.analytics_dashboard:
                return "Analytics dashboard not available - database not initialized"
            
            dashboard_data = await self.analytics_dashboard.get_comprehensive_dashboard(
                project_path=project_path,
                time_range_days=time_range_days
            )
            
            if "error" in dashboard_data:
                return f"Error generating dashboard: {dashboard_data['error']}"
            
            # Format dashboard summary
            summary = f"📊 **Comprehensive Analytics Dashboard**\n\n"
            summary += f"**Analysis Period**: {time_range_days} days\n"
            summary += f"**Generated**: {dashboard_data.get('timestamp', 'Unknown')}\n\n"
            
            # Project Health
            health = dashboard_data.get("project_health", {})
            health_score = health.get("overall_health_score", 0.0)
            health_emoji = "🟢" if health_score > 0.7 else "🟡" if health_score > 0.4 else "🔴"
            summary += f"**Project Health**: {health_emoji} {health_score:.1%}\n"
            
            # Key Metrics
            session_data = dashboard_data.get("session_analytics", {})
            task_data = dashboard_data.get("task_performance", {})
            
            summary += f"**Session Productivity**: {session_data.get('productivity_score', 0.0):.1%}\n"
            summary += f"**Task Completion Rate**: {task_data.get('completion_rate', 0.0):.1%}\n"
            summary += f"**Active Tasks**: {task_data.get('active_tasks', 0)}\n\n"
            
            # Predictions
            predictions = dashboard_data.get("predictive_insights", {})
            if predictions:
                summary += "**🔮 Predictive Insights**:\n"
                escalation_prob = predictions.get("context_escalation_predictions", {}).get("next_session_escalation_probability", 0)
                summary += f"- Context escalation probability: {escalation_prob:.1%}\n"
                
                sidequest_prob = predictions.get("sidequest_predictions", {}).get("next_task_sidequest_probability", 0)
                summary += f"- Sidequest likelihood: {sidequest_prob:.1%}\n\n"
            
            # Top Recommendations
            recommendations = dashboard_data.get("recommendations", [])
            if recommendations:
                summary += "**💡 Top Recommendations**:\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    summary += f"{i}. {rec}\n"
                summary += "\n"
            
            # Alerts
            alerts = dashboard_data.get("alerts", [])
            if alerts:
                summary += "**⚠️ Alerts**:\n"
                for alert in alerts:
                    level_emoji = "🚨" if alert.get("level") == "critical" else "⚠️" if alert.get("level") == "high" else "ℹ️"
                    summary += f"{level_emoji} {alert.get('message', 'No message')}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in analytics dashboard: {e}")
            return f"Error generating analytics dashboard: {str(e)}"
    
    async def _handle_quick_status(self, arguments: Dict[str, Any]) -> str:
        """Handle quick status summary request."""
        try:
            project_path = arguments["project_path"]
            
            if not self.analytics_dashboard:
                return "Quick status not available - database not initialized"
            
            status_data = await self.analytics_dashboard.get_quick_status_summary(project_path)
            
            if "error" in status_data:
                return f"Error getting status: {status_data['error']}"
            
            # Format quick status
            health_score = status_data.get("health_score", 0.0)
            health_emoji = "🟢" if health_score > 0.7 else "🟡" if health_score > 0.4 else "🔴"
            
            summary = f"**Quick Project Status** {health_emoji}\n\n"
            summary += f"**Health Score**: {health_score:.1%}\n"
            summary += f"**Active Tasks**: {status_data.get('active_tasks', 0)}\n"
            summary += f"**Session Status**: {status_data.get('session_status', 'unknown')}\n"
            
            quick_stats = status_data.get("quick_stats", {})
            summary += f"**Tasks Completed (week)**: {quick_stats.get('tasks_completed_week', 0)}\n"
            summary += f"**Avg Session Duration**: {quick_stats.get('avg_session_duration', 0):.1f}h\n\n"
            
            summary += f"**💡 Recommendation**: {status_data.get('top_recommendation', 'Continue current workflow')}\n"
            
            urgent_alerts = status_data.get("urgent_alerts", 0)
            if urgent_alerts > 0:
                summary += f"**⚠️ Urgent Alerts**: {urgent_alerts}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in quick status: {e}")
            return f"Error getting quick status: {str(e)}"
    
    async def _handle_learn_preference(self, arguments: Dict[str, Any]) -> str:
        """Handle learning user preferences."""
        try:
            preference_type = arguments["preference_type"]
            preference_data = arguments["preference_data"]
            
            if not self.user_preference_queries:
                return "User preference learning not available - database not initialized"
            
            if preference_type == "context":
                result = self.user_preference_queries.learn_context_preference(preference_data)
            elif preference_type == "theme":
                result = self.user_preference_queries.learn_theme_preference(preference_data)
            elif preference_type == "workflow":
                result = self.user_preference_queries.learn_workflow_preference(preference_data)
            else:
                # Track general feedback
                result = self.user_preference_queries.track_decision_feedback(preference_data)
            
            return f"✅ Preference Learning: {result}"
            
        except Exception as e:
            logger.error(f"Error learning preference: {e}")
            return f"Error learning preference: {str(e)}"
    
    async def _handle_get_recommendations(self, arguments: Dict[str, Any]) -> str:
        """Handle getting intelligent recommendations."""
        try:
            recommendation_type = arguments["recommendation_type"]
            context_data = arguments["context_data"]
            
            if not self.user_preference_queries:
                return "Recommendations not available - database not initialized"
            
            if recommendation_type == "context":
                recommendations = self.user_preference_queries.get_context_recommendations(context_data)
                
                if recommendations.get("should_suggest", False):
                    return (f"🎯 **Context Recommendation**: {recommendations.get('recommended_mode')}\n"
                           f"**Confidence**: {recommendations.get('confidence', 0):.1%}\n"
                           f"**Reason**: {recommendations.get('reason', 'No reason provided')}")
                else:
                    return f"ℹ️ Context analysis complete - {recommendations.get('reason', 'No specific recommendations')}"
            
            elif recommendation_type == "theme":
                recommendations = self.user_preference_queries.get_theme_recommendations(context_data)
                
                summary = "🎨 **Theme Recommendations**:\n"
                if recommendations.get("suggested_themes"):
                    summary += f"**Suggested**: {', '.join(recommendations['suggested_themes'])}\n"
                if recommendations.get("avoid_themes"):
                    summary += f"**Avoid**: {', '.join(recommendations['avoid_themes'])}\n"
                summary += f"**Confidence**: {recommendations.get('confidence', 0):.1%}\n"
                
                return summary
            
            elif recommendation_type == "workflow":
                recommendations = self.user_preference_queries.get_workflow_recommendations(context_data)
                
                summary = "⚡ **Workflow Recommendations**:\n"
                summary += f"**Batch Size**: {recommendations.get('recommended_batch_size', 3)} tasks\n"
                summary += f"**Escalation Threshold**: {recommendations.get('escalation_threshold', 0.7):.1%}\n"
                summary += f"**Sidequest Tolerance**: {recommendations.get('sidequest_tolerance', 2)}\n"
                summary += f"**Confidence**: {recommendations.get('confidence', 0):.1%}\n"
                
                return summary
            
            return f"Unknown recommendation type: {recommendation_type}"
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return f"Error getting recommendations: {str(e)}"