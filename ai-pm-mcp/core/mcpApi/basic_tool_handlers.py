"""
Basic tool handlers and fallback functionality for MCP API.
"""

import logging
from typing import Dict, Any
from pathlib import Path
from mcp.types import TextContent

# Import project-specific utilities
from ...utils.project_paths import get_project_management_path

logger = logging.getLogger(__name__)

# We'll access ToolDefinition through the tool_registry instead to avoid circular imports
# from ...core.mcp_api import ToolDefinition


class BasicToolHandlers:
    """Handles basic tool registration and execution."""
    
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
    def config_manager(self):
        return self.tool_registry.config_manager
    
    def _resolve_project_root(self) -> Path:
        """Intelligently resolve the project root directory."""
        try:
            # Strategy 1: Use stored project path if available
            if hasattr(self, 'project_path') and self.project_path:
                return Path(self.project_path)
            
            # Strategy 2: Look for Git repository root
            current_dir = Path.cwd()
            git_dir = current_dir
            while git_dir != git_dir.parent:
                if (git_dir / '.git').exists():
                    return git_dir
                git_dir = git_dir.parent
            
            # Strategy 3: Look for project management directory
            project_mgmt_dir = current_dir
            while project_mgmt_dir != project_mgmt_dir.parent:
                mgmt_path = get_project_management_path(project_mgmt_dir, self.config_manager)
                if mgmt_path.exists():
                    return project_mgmt_dir
                project_mgmt_dir = project_mgmt_dir.parent
            
            # Strategy 4: Look for common project markers
            project_markers = [
                'package.json', 'requirements.txt', 'Cargo.toml', 'pom.xml', 
                'setup.py', 'pyproject.toml', 'composer.json', 'go.mod'
            ]
            
            marker_dir = current_dir
            while marker_dir != marker_dir.parent:
                for marker in project_markers:
                    if (marker_dir / marker).exists():
                        logger.info(f"Resolved project root using marker '{marker}': {marker_dir}")
                        return marker_dir
                marker_dir = marker_dir.parent
            
            # Strategy 5: Fall back to current working directory
            logger.warning("Could not resolve project root intelligently. Using current working directory.")
            return current_dir
            
        except Exception as e:
            logger.error(f"Error resolving project root: {e}")
            return Path.cwd()
    
    async def _register_basic_tools(self):
        """Register basic tools for initial functionality."""
        # Access ToolDefinition through the main registry to avoid import issues
        # The main mcp_api.py has proper dependency isolation
        ToolDefinition = self.tool_registry.ToolDefinition
        
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

    async def _create_project_structure(self, project_path: Path):
        """Create the basic project management structure."""
        project_mgmt_dir = get_project_management_path(project_path, self.config_manager)
        
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
            ".ai-pm-config.json",
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
            ".ai-pm-config.json": '{"project": {"max_file_lines": 900, "auto_modularize": true, "management_folder_name": "projectManagement"}}'
        }
        
        for file_path, content in files.items():
            full_path = project_mgmt_dir / file_path
            if not full_path.exists():
                full_path.write_text(content)
        
        # Initialize database
        await self.tool_registry.database_initializer._initialize_database(str(project_path))

    async def _handle_project_init(self, arguments: Dict[str, Any]) -> str:
        """Handle project initialization."""
        try:
            project_path = Path(arguments["project_path"])
            force = arguments.get("force", False)
            
            # Check if project structure already exists
            project_mgmt_dir = get_project_management_path(project_path, self.config_manager)
            if project_mgmt_dir.exists() and not force:
                return f"Project management structure already exists at {project_mgmt_dir}. Use force=true to override."
            
            # Create basic structure
            await self._create_project_structure(project_path)
            
            return f"Project management structure initialized at {project_mgmt_dir}"
            
        except Exception as e:
            logger.error(f"Error in project_init: {e}")
            return f"Error initializing project: {str(e)}"
    
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
                # Resolve project root intelligently
                project_root = self._resolve_project_root()
                file_path = project_root / file_path
            
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
    
    async def _handle_init_database(self, arguments: Dict[str, Any]) -> str:
        """Handle database initialization."""
        try:
            project_path = arguments["project_path"]
            await self.tool_registry.database_initializer._initialize_database(project_path)
            return f"Database initialized successfully for project at {project_path}"
        except Exception as e:
            logger.error(f"Error in init_database: {e}")
            return f"Error initializing database: {str(e)}"