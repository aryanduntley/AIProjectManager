"""
Theme management tools for the AI Project Manager MCP Server.

Handles theme discovery, creation, management, and context loading.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.mcp_api import ToolDefinition
from database.theme_flow_queries import ThemeFlowQueries
from database.file_metadata_queries import FileMetadataQueries

logger = logging.getLogger(__name__)


class ThemeTools:
    """Tools for theme management and discovery."""
    
    def __init__(self, theme_flow_queries: Optional[ThemeFlowQueries] = None, file_metadata_queries: Optional[FileMetadataQueries] = None):
        self.theme_flow_queries = theme_flow_queries
        self.file_metadata_queries = file_metadata_queries
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all theme management tools."""
        return [
            ToolDefinition(
                name="theme_discover",
                description="Automatically discover themes in a project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "force_rediscovery": {
                            "type": "boolean",
                            "description": "Force rediscovery even if themes exist",
                            "default": False
                        }
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
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "theme_name": {
                            "type": "string",
                            "description": "Name of the theme"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the theme"
                        },
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Directory paths for this theme"
                        },
                        "files": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "Specific files for this theme"
                        },
                        "linked_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Related themes",
                            "default": []
                        }
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
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "include_details": {
                            "type": "boolean",
                            "description": "Include detailed theme information",
                            "default": False
                        }
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
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "theme_name": {
                            "type": "string",
                            "description": "Name of the theme"
                        }
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
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "theme_name": {
                            "type": "string",
                            "description": "Name of the theme"
                        },
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
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "theme_name": {
                            "type": "string",
                            "description": "Name of the theme to delete"
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Confirmation flag",
                            "default": False
                        }
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
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "theme_name": {
                            "type": "string",
                            "description": "Specific theme to validate (optional)"
                        }
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
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "theme_name": {
                            "type": "string",
                            "description": "Specific theme to sync (optional)"
                        }
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
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "theme_name": {
                            "type": "string",
                            "description": "Theme name"
                        }
                    },
                    "required": ["project_path", "theme_name"]
                },
                handler=self.get_theme_flows
            )
        ]
    
    async def discover_themes(self, arguments: Dict[str, Any]) -> str:
        """Discover themes automatically from project structure."""
        try:
            project_path = Path(arguments["project_path"])
            force_rediscovery = arguments.get("force_rediscovery", False)
            
            if not project_path.exists():
                return f"Project directory does not exist: {project_path}"
            
            # Check if themes already exist
            themes_dir = project_path / "projectManagement" / "Themes"
            themes_file = themes_dir / "themes.json"
            
            if themes_file.exists() and not force_rediscovery:
                return f"Themes already exist. Use force_rediscovery=true to rediscover."
            
            # Perform basic theme discovery (placeholder logic)
            logger.info(f"Discovering themes in {project_path}")
            
            # Basic theme discovery based on directory structure
            discovered_themes = await self._discover_themes_basic(project_path)
            
            if not discovered_themes:
                return "No themes discovered in the project."
            
            # Save discovered themes
            await self._save_themes(themes_dir, discovered_themes)
            
            # Update master themes index
            await self._update_themes_index(themes_dir, {"themes": discovered_themes})
            
            # Log theme discovery if database available
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=str(themes_dir),
                    file_type="theme",
                    operation="create",
                    details={"themes_discovered": list(discovered_themes.keys()), "count": len(discovered_themes)}
                )
            
            theme_count = len(discovered_themes)
            theme_names = list(discovered_themes.keys())
            
            return f"Successfully discovered {theme_count} themes: {', '.join(theme_names)}. Themes saved to {themes_dir}"
            
        except Exception as e:
            logger.error(f"Error discovering themes: {e}")
            return f"Error discovering themes: {str(e)}"
    
    async def create_theme(self, arguments: Dict[str, Any]) -> str:
        """Create a new theme definition."""
        try:
            project_path = Path(arguments["project_path"])
            theme_name = arguments["theme_name"]
            description = arguments["description"]
            paths = arguments.get("paths", [])
            files = arguments.get("files", [])
            linked_themes = arguments.get("linked_themes", [])
            
            themes_dir = project_path / "projectManagement" / "Themes"
            if not themes_dir.exists():
                return f"Project management structure not found. Initialize project first."
            
            # Create theme definition
            theme_definition = {
                "theme": theme_name,
                "category": "user-defined",
                "description": description,
                "confidence": 1.0,
                "paths": paths,
                "files": files,
                "linkedThemes": linked_themes,
                "sharedFiles": {},
                "frameworks": [],
                "keywords": [theme_name.lower()],
                "createdDate": datetime.now().isoformat(),
                "createdBy": "user"
            }
            
            # Save theme file
            theme_file = themes_dir / f"{theme_name}.json"
            theme_file.write_text(json.dumps(theme_definition, indent=2))
            
            # Update themes index
            await self._add_to_themes_index(themes_dir, theme_name, description)
            
            # Log theme creation if database available
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=str(theme_file),
                    file_type="theme",
                    operation="create",
                    details={"theme_name": theme_name, "description": description}
                )
            
            return f"Theme '{theme_name}' created successfully at {theme_file}"
            
        except Exception as e:
            logger.error(f"Error creating theme: {e}")
            return f"Error creating theme: {str(e)}"
    
    async def list_themes(self, arguments: Dict[str, Any]) -> str:
        """List all themes in the project."""
        try:
            project_path = Path(arguments["project_path"])
            include_details = arguments.get("include_details", False)
            
            themes_dir = project_path / "projectManagement" / "Themes"
            themes_index = themes_dir / "themes.json"
            
            if not themes_index.exists():
                return "No themes found. Run theme discovery first."
            
            themes_data = json.loads(themes_index.read_text())
            
            if not themes_data:
                return "No themes defined in the project."
            
            if include_details:
                # Load detailed information for each theme
                detailed_themes = {}
                for theme_name in themes_data.keys():
                    theme_file = themes_dir / f"{theme_name}.json"
                    if theme_file.exists():
                        detailed_themes[theme_name] = json.loads(theme_file.read_text())
                
                return f"Detailed themes:\n\n{json.dumps(detailed_themes, indent=2)}"
            else:
                # Return simple list
                theme_list = []
                for theme_name, description in themes_data.items():
                    theme_list.append(f"- {theme_name}: {description}")
                
                return f"Available themes ({len(theme_list)}):\n" + "\n".join(theme_list)
            
        except Exception as e:
            logger.error(f"Error listing themes: {e}")
            return f"Error listing themes: {str(e)}"
    
    async def get_theme(self, arguments: Dict[str, Any]) -> str:
        """Get detailed information about a specific theme."""
        try:
            project_path = Path(arguments["project_path"])
            theme_name = arguments["theme_name"]
            
            themes_dir = project_path / "projectManagement" / "Themes"
            theme_file = themes_dir / f"{theme_name}.json"
            
            if not theme_file.exists():
                return f"Theme '{theme_name}' not found."
            
            theme_data = json.loads(theme_file.read_text())
            return f"Theme '{theme_name}':\n\n{json.dumps(theme_data, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error getting theme: {e}")
            return f"Error getting theme: {str(e)}"
    
    async def update_theme(self, arguments: Dict[str, Any]) -> str:
        """Update an existing theme definition."""
        try:
            project_path = Path(arguments["project_path"])
            theme_name = arguments["theme_name"]
            updates = arguments["updates"]
            
            themes_dir = project_path / "projectManagement" / "Themes"
            theme_file = themes_dir / f"{theme_name}.json"
            
            if not theme_file.exists():
                return f"Theme '{theme_name}' not found."
            
            # Load existing theme
            theme_data = json.loads(theme_file.read_text())
            
            # Apply updates
            for key, value in updates.items():
                if key in theme_data:
                    theme_data[key] = value
            
            # Update last modified
            theme_data["lastModified"] = datetime.now().isoformat()
            
            # Save updated theme
            theme_file.write_text(json.dumps(theme_data, indent=2))
            
            # Log theme update if database available
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=str(theme_file),
                    file_type="theme",
                    operation="update",
                    details={"theme_name": theme_name, "updates": list(updates.keys())}
                )
            
            return f"Theme '{theme_name}' updated successfully."
            
        except Exception as e:
            logger.error(f"Error updating theme: {e}")
            return f"Error updating theme: {str(e)}"
    
    async def delete_theme(self, arguments: Dict[str, Any]) -> str:
        """Delete a theme definition."""
        try:
            project_path = Path(arguments["project_path"])
            theme_name = arguments["theme_name"]
            confirm = arguments.get("confirm", False)
            
            if not confirm:
                return f"Deletion not confirmed. Set confirm=true to delete theme '{theme_name}'."
            
            themes_dir = project_path / "projectManagement" / "Themes"
            theme_file = themes_dir / f"{theme_name}.json"
            
            if not theme_file.exists():
                return f"Theme '{theme_name}' not found."
            
            # Remove theme file
            theme_file.unlink()
            
            # Update themes index
            await self._remove_from_themes_index(themes_dir, theme_name)
            
            # Log theme deletion if database available
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=str(theme_file),
                    file_type="theme",
                    operation="delete",
                    details={"theme_name": theme_name}
                )
            
            return f"Theme '{theme_name}' deleted successfully."
            
        except Exception as e:
            logger.error(f"Error deleting theme: {e}")
            return f"Error deleting theme: {str(e)}"
    
    async def get_theme_context(self, arguments: Dict[str, Any]) -> str:
        """Get context for themes based on context mode."""
        try:
            project_path = Path(arguments["project_path"])
            primary_theme = arguments["primary_theme"]
            context_mode = arguments.get("context_mode", "theme-focused")
            
            themes_dir = project_path / "projectManagement" / "Themes"
            
            # Load primary theme
            primary_theme_file = themes_dir / f"{primary_theme}.json"
            if not primary_theme_file.exists():
                return f"Primary theme '{primary_theme}' not found."
            
            primary_theme_data = json.loads(primary_theme_file.read_text())
            context = {
                "contextMode": context_mode,
                "primaryTheme": primary_theme,
                "themes": [primary_theme_data],
                "files": primary_theme_data.get("files", []),
                "paths": primary_theme_data.get("paths", [])
            }
            
            if context_mode == "theme-expanded":
                # Load linked themes
                linked_themes = primary_theme_data.get("linkedThemes", [])
                for linked_theme in linked_themes:
                    linked_theme_file = themes_dir / f"{linked_theme}.json"
                    if linked_theme_file.exists():
                        linked_theme_data = json.loads(linked_theme_file.read_text())
                        context["themes"].append(linked_theme_data)
                        context["files"].extend(linked_theme_data.get("files", []))
                        context["paths"].extend(linked_theme_data.get("paths", []))
                
                context["loadedThemes"] = [primary_theme] + linked_themes
            
            elif context_mode == "project-wide":
                # Load all themes
                themes_index = themes_dir / "themes.json"
                if themes_index.exists():
                    all_themes = json.loads(themes_index.read_text())
                    context["loadedThemes"] = list(all_themes.keys())
                    
                    for theme_name in all_themes.keys():
                        if theme_name != primary_theme:
                            theme_file = themes_dir / f"{theme_name}.json"
                            if theme_file.exists():
                                theme_data = json.loads(theme_file.read_text())
                                context["themes"].append(theme_data)
                                context["files"].extend(theme_data.get("files", []))
                                context["paths"].extend(theme_data.get("paths", []))
            
            else:  # theme-focused
                context["loadedThemes"] = [primary_theme]
            
            # Remove duplicates
            context["files"] = list(set(context["files"]))
            context["paths"] = list(set(context["paths"]))
            
            return f"Theme context loaded:\n\n{json.dumps(context, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error getting theme context: {e}")
            return f"Error getting theme context: {str(e)}"
    
    async def validate_themes(self, arguments: Dict[str, Any]) -> str:
        """Validate theme consistency and detect issues."""
        try:
            project_path = Path(arguments["project_path"])
            specific_theme = arguments.get("theme_name")
            
            themes_dir = project_path / "projectManagement" / "Themes"
            themes_index = themes_dir / "themes.json"
            
            if not themes_index.exists():
                return "No themes found to validate."
            
            validation_results = {
                "valid": True,
                "issues": [],
                "warnings": [],
                "theme_count": 0,
                "file_coverage": {}
            }
            
            themes_data = json.loads(themes_index.read_text())
            themes_to_check = [specific_theme] if specific_theme else list(themes_data.keys())
            
            for theme_name in themes_to_check:
                theme_file = themes_dir / f"{theme_name}.json"
                if not theme_file.exists():
                    validation_results["issues"].append(f"Theme file missing: {theme_name}.json")
                    validation_results["valid"] = False
                    continue
                
                try:
                    theme_data = json.loads(theme_file.read_text())
                    validation_results["theme_count"] += 1
                    
                    # Check required fields
                    required_fields = ["theme", "description", "paths", "files"]
                    for field in required_fields:
                        if field not in theme_data:
                            validation_results["issues"].append(f"Theme {theme_name}: Missing required field '{field}'")
                            validation_results["valid"] = False
                    
                    # Check file existence
                    missing_files = []
                    for file_path in theme_data.get("files", []):
                        full_path = project_path / file_path
                        if not full_path.exists():
                            missing_files.append(file_path)
                    
                    if missing_files:
                        validation_results["warnings"].append(f"Theme {theme_name}: Files not found: {missing_files}")
                    
                    # Check path existence
                    missing_paths = []
                    for path in theme_data.get("paths", []):
                        full_path = project_path / path
                        if not full_path.exists():
                            missing_paths.append(path)
                    
                    if missing_paths:
                        validation_results["warnings"].append(f"Theme {theme_name}: Paths not found: {missing_paths}")
                    
                    # Check linked themes
                    invalid_links = []
                    for linked_theme in theme_data.get("linkedThemes", []):
                        linked_file = themes_dir / f"{linked_theme}.json"
                        if not linked_file.exists():
                            invalid_links.append(linked_theme)
                    
                    if invalid_links:
                        validation_results["issues"].append(f"Theme {theme_name}: Invalid linked themes: {invalid_links}")
                        validation_results["valid"] = False
                    
                except json.JSONDecodeError:
                    validation_results["issues"].append(f"Theme {theme_name}: Invalid JSON format")
                    validation_results["valid"] = False
            
            status = "VALID" if validation_results["valid"] else "INVALID"
            return f"Theme validation result: {status}\n\n{json.dumps(validation_results, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error validating themes: {e}")
            return f"Error validating themes: {str(e)}"
    
    async def _save_themes(self, themes_dir: Path, themes: Dict[str, Any]):
        """Save discovered themes to individual files."""
        themes_dir.mkdir(parents=True, exist_ok=True)
        
        for theme_name, theme_data in themes.items():
            theme_file = themes_dir / f"{theme_name}.json"
            theme_file.write_text(json.dumps(theme_data, indent=2))
    
    async def _update_themes_index(self, themes_dir: Path, discovery_result: Dict[str, Any]):
        """Update the master themes index."""
        themes_index = themes_dir / "themes.json"
        
        # Create themes index
        index_data = {}
        for theme_name, theme_data in discovery_result['themes'].items():
            index_data[theme_name] = theme_data.get('description', f'{theme_name} theme')
        
        themes_index.write_text(json.dumps(index_data, indent=2))
    
    async def _add_to_themes_index(self, themes_dir: Path, theme_name: str, description: str):
        """Add a theme to the themes index."""
        themes_index = themes_dir / "themes.json"
        
        if themes_index.exists():
            index_data = json.loads(themes_index.read_text())
        else:
            index_data = {}
        
        index_data[theme_name] = description
        themes_index.write_text(json.dumps(index_data, indent=2))
    
    async def _remove_from_themes_index(self, themes_dir: Path, theme_name: str):
        """Remove a theme from the themes index."""
        themes_index = themes_dir / "themes.json"
        
        if themes_index.exists():
            index_data = json.loads(themes_index.read_text())
            if theme_name in index_data:
                del index_data[theme_name]
                themes_index.write_text(json.dumps(index_data, indent=2))
    
    async def _discover_themes_basic(self, project_path: Path) -> Dict[str, Any]:
        """Basic theme discovery based on directory structure."""
        themes = {}
        
        # Common source directories to check
        source_dirs = [
            "src", "lib", "app", "components", "services", 
            "utils", "hooks", "pages", "views", "controllers"
        ]
        
        for src_dir_name in source_dirs:
            src_dir = project_path / src_dir_name
            if src_dir.exists() and src_dir.is_dir():
                # Look for subdirectories as potential themes
                for subdir in src_dir.iterdir():
                    if subdir.is_dir() and not subdir.name.startswith('.'):
                        theme_name = subdir.name.lower()
                        if theme_name not in themes:
                            themes[theme_name] = {
                                "theme": theme_name,
                                "category": "discovered",
                                "description": f"Auto-discovered theme from {src_dir_name}/{subdir.name}",
                                "confidence": 0.7,
                                "paths": [str(subdir.relative_to(project_path))],
                                "files": self._get_files_in_directory(subdir, project_path),
                                "linkedThemes": [],
                                "sharedFiles": {},
                                "frameworks": [],
                                "keywords": [theme_name],
                                "createdDate": datetime.now().isoformat(),
                                "createdBy": "auto-discovery"
                            }
        
        # If no themes discovered from subdirectories, create a default theme
        if not themes:
            themes["main"] = {
                "theme": "main",
                "category": "default",
                "description": "Main application theme",
                "confidence": 0.8,
                "paths": ["src", "app", "lib"],
                "files": self._get_files_in_directory(project_path, project_path, max_depth=2),
                "linkedThemes": [],
                "sharedFiles": {},
                "frameworks": [],
                "keywords": ["main", "app"],
                "createdDate": datetime.now().isoformat(),
                "createdBy": "auto-discovery"
            }
        
        return themes
    
    def _get_files_in_directory(self, directory: Path, project_path: Path, max_depth: int = 3) -> List[str]:
        """Get files in a directory with depth limit."""
        files = []
        try:
            for item in directory.rglob('*'):
                if item.is_file() and self._is_source_file(item):
                    rel_path = item.relative_to(project_path)
                    # Check depth
                    if len(rel_path.parts) <= max_depth:
                        files.append(str(rel_path))
        except Exception as e:
            logger.warning(f"Error scanning directory {directory}: {e}")
        return files[:50]  # Limit to 50 files per theme
    
    def _is_source_file(self, file_path: Path) -> bool:
        """Check if file is a source code file."""
        source_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.rb', '.php', '.go', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.less', '.vue', '.svelte'
        }
        return file_path.suffix.lower() in source_extensions
    
    async def sync_theme_flows(self, arguments: Dict[str, Any]) -> str:
        """Synchronize theme-flow relationships with database."""
        try:
            project_path = Path(arguments["project_path"])
            specific_theme = arguments.get("theme_name")
            
            if not self.theme_flow_queries:
                return "Database not available. Theme-flow synchronization requires database connection."
            
            themes_dir = project_path / "projectManagement" / "Themes"
            flow_dir = project_path / "projectManagement" / "ProjectFlow"
            
            if not themes_dir.exists():
                return "No themes directory found. Initialize project first."
            
            # Load flow index
            flow_index_path = flow_dir / "flow-index.json"
            if not flow_index_path.exists():
                return "No flow index found. Initialize flows first."
            
            flow_index_data = json.loads(flow_index_path.read_text())
            
            # Load theme files
            theme_files_data = {}
            themes_to_sync = [specific_theme] if specific_theme else []
            
            if not themes_to_sync:
                # Load all themes
                for theme_file in themes_dir.glob("*.json"):
                    if theme_file.name != "themes.json":
                        theme_name = theme_file.stem
                        try:
                            theme_data = json.loads(theme_file.read_text())
                            if "flows" in theme_data:
                                theme_files_data[theme_name] = theme_data
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in theme file: {theme_file}")
            else:
                # Load specific theme
                theme_file = themes_dir / f"{specific_theme}.json"
                if theme_file.exists():
                    theme_data = json.loads(theme_file.read_text())
                    if "flows" in theme_data:
                        theme_files_data[specific_theme] = theme_data
            
            if not theme_files_data:
                return "No themes with flow data found to synchronize."
            
            # Synchronize with database
            sync_results = await self.theme_flow_queries.sync_theme_flows_from_files(
                theme_files_data, flow_index_data
            )
            
            return f"Theme-flow synchronization completed:\n{json.dumps(sync_results, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error synchronizing theme flows: {e}")
            return f"Error synchronizing theme flows: {str(e)}"
    
    async def get_theme_flows(self, arguments: Dict[str, Any]) -> str:
        """Get flows associated with a theme."""
        try:
            project_path = Path(arguments["project_path"])
            theme_name = arguments["theme_name"]
            
            if not self.theme_flow_queries:
                return "Database not available. Theme-flow queries require database connection."
            
            # Get flows from database
            flows = await self.theme_flow_queries.get_flows_for_theme(theme_name)
            
            if not flows:
                return f"No flows found for theme '{theme_name}'."
            
            # Get flow status if available
            flows_with_status = []
            for flow in flows:
                flow_status = await self.theme_flow_queries.get_flow_status(flow["flow_id"])
                flow_info = {
                    "flow_id": flow["flow_id"],
                    "flow_file": flow["flow_file"],
                    "relevance_order": flow["relevance_order"],
                    "status": flow_status["status"] if flow_status else "unknown",
                    "completion_percentage": flow_status["completion_percentage"] if flow_status else 0
                }
                flows_with_status.append(flow_info)
            
            return f"Flows for theme '{theme_name}':\n{json.dumps(flows_with_status, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error getting theme flows: {e}")
            return f"Error getting theme flows: {str(e)}"