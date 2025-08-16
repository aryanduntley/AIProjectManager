"""
Base theme operations and shared utilities for theme management.

Contains core functionality shared across all theme management operations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ...utils.project_paths import get_themes_path, get_flows_path

logger = logging.getLogger(__name__)


class BaseThemeOperations:
    """Base class for theme operations with shared utilities."""
    
    def __init__(self, theme_flow_queries=None, file_metadata_queries=None, config_manager=None):
        self.theme_flow_queries = theme_flow_queries
        self.file_metadata_queries = file_metadata_queries
        self.config_manager = config_manager
        self.server_instance = None
    
    def get_themes_directory(self, project_path: Path) -> Path:
        """Get the themes directory path."""
        return get_themes_path(project_path, self.config_manager)
    
    def get_flows_directory(self, project_path: Path) -> Path:
        """Get the flows directory path."""
        return get_flows_path(project_path, self.config_manager)
    
    def load_themes_index(self, themes_dir: Path) -> Optional[Dict[str, Any]]:
        """Load themes index if it exists."""
        themes_index_path = themes_dir / "themes.json"
        if themes_index_path.exists():
            try:
                return json.loads(themes_index_path.read_text())
            except json.JSONDecodeError as e:
                logger.error(f"Error reading themes index: {e}")
                return None
        return None
    
    def save_themes_index(self, themes_dir: Path, themes_index: Dict[str, Any]) -> bool:
        """Save themes index to file."""
        themes_index_path = themes_dir / "themes.json"
        try:
            themes_dir.mkdir(parents=True, exist_ok=True)
            themes_index_path.write_text(json.dumps(themes_index, indent=2))
            return True
        except Exception as e:
            logger.error(f"Error saving themes index: {e}")
            return False
    
    def load_theme(self, themes_dir: Path, theme_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific theme file."""
        theme_file_path = themes_dir / f"{theme_name}.json"
        if theme_file_path.exists():
            try:
                return json.loads(theme_file_path.read_text())
            except json.JSONDecodeError as e:
                logger.error(f"Error reading theme {theme_name}: {e}")
                return None
        return None
    
    def save_theme(self, themes_dir: Path, theme_name: str, theme_data: Dict[str, Any]) -> bool:
        """Save a theme to file."""
        theme_file_path = themes_dir / f"{theme_name}.json"
        try:
            themes_dir.mkdir(parents=True, exist_ok=True)
            theme_file_path.write_text(json.dumps(theme_data, indent=2))
            return True
        except Exception as e:
            logger.error(f"Error saving theme {theme_name}: {e}")
            return False
    
    def create_default_themes_index(self) -> Dict[str, Any]:
        """Create a default themes index structure."""
        return {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "description": "Theme management index for the AI Project Manager"
            },
            "themes": {},
            "discovery": {
                "last_discovery": None,
                "auto_discovery_enabled": True,
                "discovery_patterns": [
                    "*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.cs",
                    "*.md", "*.txt", "*.json", "*.yaml", "*.yml"
                ]
            }
        }
    
    def create_default_theme(self, theme_name: str, description: str = "") -> Dict[str, Any]:
        """Create a default theme structure."""
        return {
            "metadata": {
                "name": theme_name,
                "description": description,
                "created": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "category": "general"
            },
            "keywords": [],
            "patterns": [],
            "flows": [],
            "files": [],
            "context": {
                "priority": 1.0,
                "scope": "project",
                "relationships": []
            },
            "statistics": {
                "file_count": 0,
                "flow_count": 0,
                "usage_count": 0
            }
        }
    
    async def save_themes(self, themes_dir: Path, themes: Dict[str, Any]):
        """Save themes data to directory structure."""
        # Save main themes index
        themes_index = self.load_themes_index(themes_dir) or self.create_default_themes_index()
        
        for theme_name, theme_data in themes.items():
            # Save individual theme file
            if self.save_theme(themes_dir, theme_name, theme_data):
                # Update themes index
                themes_index["themes"][theme_name] = {
                    "name": theme_name,
                    "description": theme_data.get("metadata", {}).get("description", ""),
                    "file": f"{theme_name}.json",
                    "last_updated": datetime.utcnow().isoformat(),
                    "file_count": theme_data.get("statistics", {}).get("file_count", 0),
                    "flow_count": theme_data.get("statistics", {}).get("flow_count", 0)
                }
        
        themes_index["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        self.save_themes_index(themes_dir, themes_index)
    
    async def update_themes_index(self, themes_dir: Path, discovery_result: Dict[str, Any]):
        """Update themes index with discovery results."""
        themes_index = self.load_themes_index(themes_dir) or self.create_default_themes_index()
        
        themes_index["discovery"]["last_discovery"] = datetime.utcnow().isoformat()
        themes_index["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        
        # Update statistics
        if "statistics" not in themes_index:
            themes_index["statistics"] = {}
        
        themes_index["statistics"].update({
            "total_themes": len(discovery_result.get("themes", {})),
            "files_analyzed": discovery_result.get("files_analyzed", 0),
            "discovery_method": discovery_result.get("method", "basic")
        })
        
        self.save_themes_index(themes_dir, themes_index)
    
    async def add_to_themes_index(self, themes_dir: Path, theme_name: str, description: str):
        """Add a new theme to the themes index."""
        themes_index = self.load_themes_index(themes_dir) or self.create_default_themes_index()
        
        themes_index["themes"][theme_name] = {
            "name": theme_name,
            "description": description,
            "file": f"{theme_name}.json",
            "created": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "file_count": 0,
            "flow_count": 0
        }
        
        themes_index["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        self.save_themes_index(themes_dir, themes_index)
    
    async def remove_from_themes_index(self, themes_dir: Path, theme_name: str):
        """Remove a theme from the themes index."""
        themes_index = self.load_themes_index(themes_dir)
        if not themes_index:
            return
        
        if theme_name in themes_index.get("themes", {}):
            del themes_index["themes"][theme_name]
            themes_index["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            self.save_themes_index(themes_dir, themes_index)
        
        # Also remove the theme file
        theme_file_path = themes_dir / f"{theme_name}.json"
        if theme_file_path.exists():
            try:
                theme_file_path.unlink()
            except Exception as e:
                logger.error(f"Error removing theme file {theme_name}.json: {e}")