"""
Theme management operations.

Handles CRUD operations for themes (create, list, get, update, delete).
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_operations import BaseThemeOperations

logger = logging.getLogger(__name__)


class ThemeManagementOperations(BaseThemeOperations):
    """Handles theme CRUD operations and management."""
    
    async def create_theme(self, project_path: Path, theme_name: str, description: str,
                          paths: List[str] = None, files: List[str] = None,
                          linked_themes: List[str] = None) -> str:
        """Create a new theme definition."""
        try:
            if paths is None:
                paths = []
            if files is None:
                files = []
            if linked_themes is None:
                linked_themes = []
                
            project_path = Path(project_path)
            themes_dir = self.get_themes_directory(project_path)
            
            if not themes_dir.exists():
                return f"Project management structure not found. Initialize project first."
            
            # Create theme definition using original structure
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
            await self.add_to_themes_index(themes_dir, theme_name, description)
            
            # Log theme creation if database available
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=str(theme_file),
                    file_type="theme",
                    operation="create",
                    details={"theme_name": theme_name, "description": description}
                )
            
            # Trigger directive processing for file creation
            if self.server_instance and hasattr(self.server_instance, 'on_file_edit_complete'):
                try:
                    changes_made = {
                        "operation": "create_theme",
                        "theme_name": theme_name,
                        "description": description,
                        "file_created": str(theme_file)
                    }
                    await self.server_instance.on_file_edit_complete(str(theme_file), changes_made)
                except Exception as e:
                    logger.warning(f"Failed to trigger file edit completion directive: {e}")
            
            return f"Theme '{theme_name}' created successfully at {theme_file}"
            
        except Exception as e:
            logger.error(f"Error creating theme: {e}")
            return f"Error creating theme: {str(e)}"
    
    async def list_themes(self, project_path: Path, include_details: bool = False) -> str:
        """List all themes in the project."""
        try:
            project_path = Path(project_path)
            themes_dir = self.get_themes_directory(project_path)
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
    
    async def get_theme(self, project_path: Path, theme_name: str) -> str:
        """Get detailed information about a specific theme."""
        try:
            project_path = Path(project_path)
            themes_dir = self.get_themes_directory(project_path)
            
            theme_file = themes_dir / f"{theme_name}.json"
            
            if not theme_file.exists():
                return f"Theme '{theme_name}' not found."
            
            theme_data = json.loads(theme_file.read_text())
            return f"Theme '{theme_name}':\n\n{json.dumps(theme_data, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error getting theme: {e}")
            return f"Error getting theme: {str(e)}"
    
    async def update_theme(self, project_path: Path, theme_name: str, updates: Dict[str, Any]) -> str:
        """Update an existing theme definition."""
        try:
            project_path = Path(project_path)
            themes_dir = self.get_themes_directory(project_path)
            
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
    
    async def delete_theme(self, project_path: Path, theme_name: str, confirm: bool = False) -> str:
        """Delete a theme definition."""
        try:
            project_path = Path(project_path)
            themes_dir = self.get_themes_directory(project_path)
            
            if not confirm:
                return f"Deletion not confirmed. Set confirm=true to delete theme '{theme_name}'."
            
            theme_file = themes_dir / f"{theme_name}.json"
            
            if not theme_file.exists():
                return f"Theme '{theme_name}' not found."
            
            # Remove theme file
            theme_file.unlink()
            
            # Update themes index
            await self.remove_from_themes_index(themes_dir, theme_name)
            
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