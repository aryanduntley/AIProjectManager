"""
Tool registration and discovery functionality for MCP API.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class ToolRegistration:
    """Handles tool discovery, registration, and module management."""
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
    
    # Delegate to main registry attributes
    @property
    def tools(self):
        return self.tool_registry.tools
    
    @property  
    def tool_handlers(self):
        return self.tool_registry.tool_handlers
        
    @property
    def tool_instances(self):
        return self.tool_registry.tool_instances
        
    @property
    def db_manager(self):
        return self.tool_registry.db_manager
        
    @property
    def config_manager(self):
        return self.tool_registry.config_manager
        
    @property
    def directive_processor(self):
        return self.tool_registry.directive_processor
        
    @property
    def server_instance(self):
        return self.tool_registry.server_instance
        
    @property
    def task_queries(self):
        return self.tool_registry.task_queries
        
    @property
    def session_queries(self):
        return self.tool_registry.session_queries
        
    @property
    def file_metadata_queries(self):
        return self.tool_registry.file_metadata_queries
        
    @property
    def theme_flow_queries(self):
        return self.tool_registry.theme_flow_queries
        
    @property
    def event_queries(self):
        return self.tool_registry.event_queries
        
    @property
    def scope_engine(self):
        return self.tool_registry.scope_engine
        
    @property
    def task_processor(self):
        return self.tool_registry.task_processor
    
    async def _discover_tools(self):
        """Discover and import all tool modules."""
        try:
            # Import project tools with database integration and directive processor
            from ...tools.project_tools import ProjectTools
            project_tools = ProjectTools(self.db_manager, self.config_manager, self.directive_processor)
            self.tool_instances['project_tools'] = project_tools  # Store for ActionExecutor
            await self._register_tool_module(project_tools)
            
            # Import database tools
            from ...tools.database_tools import DatabaseTools
            database_tools = DatabaseTools(self.db_manager, self.config_manager)
            self.tool_instances['database_tools'] = database_tools  # Store for ActionExecutor
            await self._register_tool_module(database_tools)
            
            # Import task tools with database integration
            from ...tools.task_tools import TaskTools
            task_tools = TaskTools(self.task_queries, self.session_queries, self.file_metadata_queries)
            # Add server instance for hook point integration
            task_tools.server_instance = self.server_instance
            self.tool_instances['task_tools'] = task_tools  # Store for ActionExecutor
            await self._register_tool_module(task_tools)
            
            # Import session manager with database integration
            from ...tools.session_manager import SessionManager
            session_manager = SessionManager(self.session_queries, self.file_metadata_queries)
            await self._register_tool_module(session_manager)
            
            # File operations handled through internal services, not user-facing tools
            
            # Import theme tools with database integration
            from ...tools.theme_tools import ThemeTools
            theme_tools = ThemeTools(self.theme_flow_queries, self.file_metadata_queries, self.config_manager)
            # Add server instance for hook point integration
            theme_tools.server_instance = self.server_instance
            await self._register_tool_module(theme_tools)
            
            # Import flow tools with database integration
            from ...tools.flow_tools import FlowTools
            flow_tools = FlowTools(self.theme_flow_queries, self.session_queries, self.file_metadata_queries)
            # Add server instance for hook point integration
            flow_tools.server_instance = self.server_instance
            await self._register_tool_module(flow_tools)
            
            # Import enhanced core processing tools if components available
            if self.scope_engine and self.task_processor:
                await self._register_enhanced_core_tools()
            
            # Import log tools with event queries integration
            from ...tools.log_tools import LogTools
            log_tools = LogTools(self.event_queries)
            await self._register_tool_module(log_tools)
            
            # Config operations handled through internal services, not user-facing tools
            
            # Import branch tools for simplified Git branch management
            from ...tools.branch_tools import BranchTools
            branch_tools = BranchTools()
            branch_tools.server_instance = self.server_instance
            await self._register_tool_module(branch_tools)
            
            # Import initialization tools for proper user interaction during server boot
            from ...tools.initialization_tools import InitializationTools
            initialization_tools = InitializationTools(self.db_manager)
            await self._register_tool_module(initialization_tools)
            
            # Import command tools for better user experience and command discovery
            from ...tools.command_tools import CommandTools
            command_tools = CommandTools(self.db_manager, self.config_manager, self.server_instance)
            await self._register_tool_module(command_tools)
            
            # Import test tools for internal test execution within server context
            from ...tools.test_tools import TestTools
            test_tools = TestTools(self.config_manager)
            await self._register_tool_module(test_tools)
            
            
            # Import run command processor for direct slash command replacement
            from ...tools.run_command_processor import RunCommandProcessor
            run_processor = RunCommandProcessor(self.db_manager, self.config_manager, self.directive_processor)
            await self._register_tool_module(run_processor)
            
        except ImportError as e:
            logger.error(f"Critical tool modules not available: {e}")
            # Log missing modules and attempt fallback registration
            missing_modules = str(e).split("'")[1] if "'" in str(e) else "unknown"
            logger.info(f"Missing module: {missing_modules}. Attempting fallback tool registration.")
            
            # Try to register available tools individually
            await self._register_available_tools_individually()
    
    async def _register_tool_module(self, tool_module):
        """Register tools from a tool module."""
        if hasattr(tool_module, 'get_tools'):
            tools = await tool_module.get_tools()
            for tool_def in tools:
                self.tools[tool_def.name] = tool_def
                self.tool_handlers[tool_def.name] = tool_def.handler
    
    async def _register_available_tools_individually(self):
        """Register tools individually, handling import errors gracefully."""
        tool_modules = [
            ("project_tools", "ProjectTools"),
            ("theme_tools", "ThemeTools"), 
            ("task_tools", "TaskTools"),
            ("branch_tools", "BranchTools")
        ]
        
        registered_count = 0
        
        for module_name, class_name in tool_modules:
            try:
                # Dynamic import of tool module
                module = __import__(f"tools.{module_name}", fromlist=[class_name])
                tool_class = getattr(module, class_name)
                
                # Initialize tool with available dependencies
                tool_instance = self._initialize_tool_with_dependencies(tool_class)
                
                # Register the tool
                await self._register_tool_module(tool_instance)
                registered_count += 1
                logger.info(f"Successfully registered {class_name} from {module_name}")
                
            except ImportError as e:
                logger.warning(f"Could not import {module_name}.{class_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error initializing {class_name}: {e}")
                continue
        
        if registered_count == 0:
            logger.warning("No tool modules could be loaded. Falling back to basic tools.")
            await self.tool_registry.basic_tool_handlers._register_basic_tools()
        else:
            logger.info(f"Successfully registered {registered_count} tool modules")
    
    def _initialize_tool_with_dependencies(self, tool_class):
        """Initialize a tool class with available database dependencies."""
        try:
            # Try to initialize with full dependencies
            if hasattr(tool_class, '__init__'):
                import inspect
                sig = inspect.signature(tool_class.__init__)
                params = list(sig.parameters.keys())[1:]  # Skip 'self'
                
                kwargs = {}
                for param in params:
                    if param == 'task_queries' and hasattr(self, 'task_queries'):
                        kwargs[param] = self.task_queries
                    elif param == 'session_queries' and hasattr(self, 'session_queries'):
                        kwargs[param] = self.session_queries
                    elif param == 'file_metadata_queries' and hasattr(self, 'file_metadata_queries'):
                        kwargs[param] = self.file_metadata_queries
                    elif param == 'theme_flow_queries' and hasattr(self, 'theme_flow_queries'):
                        kwargs[param] = self.theme_flow_queries
                    elif param == 'git_queries' and hasattr(self, 'git_queries'):
                        kwargs[param] = self.git_queries
                
                return tool_class(**kwargs)
            else:
                return tool_class()
                
        except Exception as e:
            logger.warning(f"Could not initialize {tool_class.__name__} with dependencies: {e}")
            # Fallback to parameterless initialization
            try:
                return tool_class()
            except Exception as fallback_error:
                logger.error(f"Could not initialize {tool_class.__name__} at all: {fallback_error}")
                raise