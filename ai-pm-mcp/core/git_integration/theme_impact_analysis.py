"""
Theme Impact Analysis Module
Handles analysis of which themes are affected by file changes.
"""

import json
from pathlib import Path
from typing import Dict, List, Any

# Import utilities from parent module paths
from ...utils.project_paths import get_themes_path


class ThemeImpactAnalysis:
    """Theme impact analysis for file changes."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties
        self.project_root = parent_instance.project_root
        self.db_manager = parent_instance.db_manager
        self.config_manager = parent_instance.config_manager
        self.server_instance = parent_instance.server_instance
        self.git_dir = parent_instance.git_dir
    
    def _analyze_theme_impact(self, changed_files: List[Dict[str, Any]]) -> List[str]:
        """
        Analyze which themes are affected by the changed files
        This integrates with the theme management system to determine impact
        """
        try:
            affected_themes = set()
            theme_files = {}
            
            # Load existing themes to analyze file relationships
            themes_dir = get_themes_path(self.project_root, self.config_manager)
            if themes_dir.exists():
                themes_json_path = themes_dir / "themes.json"
                if themes_json_path.exists():
                    try:
                        with open(themes_json_path, 'r') as f:
                            theme_files = json.load(f)
                    except (json.JSONDecodeError, FileNotFoundError):
                        theme_files = {}
            
            # Analyze each changed file for theme impact
            for file_change in changed_files:
                file_path = file_change["path"]
                change_type = file_change["type"]
                
                # Direct theme impact analysis
                file_themes = self._get_themes_for_file(file_path, theme_files)
                affected_themes.update(file_themes)
                
                # Directory-based theme inference
                dir_themes = self._infer_themes_from_directory(file_path)
                affected_themes.update(dir_themes)
                
                # File extension and naming pattern analysis
                pattern_themes = self._infer_themes_from_patterns(file_path)
                affected_themes.update(pattern_themes)
                
                # Special handling for deleted files
                if change_type == "deleted":
                    deletion_themes = self._analyze_deletion_impact(file_path, theme_files)
                    affected_themes.update(deletion_themes)
            
            return list(affected_themes)
            
        except Exception as e:
            print(f"Error analyzing theme impact: {e}")
            return []
    
    def _get_themes_for_file(self, file_path: str, theme_files: Dict[str, Any]) -> List[str]:
        """Get themes that explicitly reference this file"""
        themes = []
        for theme_name, theme_data in theme_files.items():
            if isinstance(theme_data, dict) and "files" in theme_data:
                theme_file_list = theme_data.get("files", [])
                if file_path in theme_file_list or any(file_path.endswith(f) for f in theme_file_list):
                    themes.append(theme_name)
        return themes
    
    def _infer_themes_from_directory(self, file_path: str) -> List[str]:
        """Infer themes based on directory structure"""
        themes = []
        path_parts = Path(file_path).parts
        
        # Common directory name to theme mappings
        directory_mappings = {
            "auth": ["authentication", "security"],
            "authentication": ["authentication", "security"],
            "login": ["authentication"],
            "user": ["user-management", "authentication"],
            "users": ["user-management"],
            "profile": ["user-management"],
            "payment": ["payment", "billing"],
            "billing": ["payment", "billing"],
            "checkout": ["payment", "checkout"],
            "cart": ["shopping-cart", "commerce"],
            "api": ["api", "backend"],
            "database": ["database", "data"],
            "db": ["database", "data"],
            "ui": ["ui", "frontend"],
            "components": ["ui", "frontend"],
            "frontend": ["frontend"],
            "backend": ["backend"],
            "admin": ["admin", "management"],
            "dashboard": ["dashboard", "admin"],
            "config": ["configuration"],
            "settings": ["configuration", "settings"],
            "test": ["testing"],
            "tests": ["testing"],
            "security": ["security"],
            "middleware": ["api", "security"]
        }
        
        for part in path_parts:
            part_lower = part.lower()
            if part_lower in directory_mappings:
                themes.extend(directory_mappings[part_lower])
        
        return themes
    
    def _infer_themes_from_patterns(self, file_path: str) -> List[str]:
        """Infer themes based on file naming patterns and extensions"""
        themes = []
        filename = Path(file_path).name.lower()
        
        # File pattern to theme mappings
        pattern_mappings = {
            "auth": ["authentication"],
            "login": ["authentication"],
            "signup": ["authentication"],
            "register": ["authentication"],
            "password": ["authentication", "security"],
            "session": ["authentication", "session-management"],
            "user": ["user-management"],
            "profile": ["user-management"],
            "payment": ["payment"],
            "billing": ["billing"],
            "invoice": ["billing"],
            "cart": ["shopping-cart"],
            "checkout": ["checkout"],
            "order": ["order-management"],
            "product": ["product-management"],
            "inventory": ["inventory"],
            "admin": ["admin"], 
            "dashboard": ["dashboard"],
            "api": ["api"],
            "middleware": ["api", "middleware"],
            "config": ["configuration"],
            "setting": ["configuration"],
            "database": ["database"],
            "migration": ["database"],
            "schema": ["database"],
            "test": ["testing"],
            "spec": ["testing"],
            "security": ["security"],
            "validation": ["validation"],
            "error": ["error-handling"],
            "log": ["logging"],
            "email": ["email", "notifications"],
            "notification": ["notifications"]
        }
        
        for pattern, pattern_themes in pattern_mappings.items():
            if pattern in filename:
                themes.extend(pattern_themes)
        
        return themes
    
    def _analyze_deletion_impact(self, file_path: str, theme_files: Dict[str, Any]) -> List[str]:
        """Analyze impact of file deletion on themes"""
        themes = []
        for theme_name, theme_data in theme_files.items():
            if isinstance(theme_data, dict) and "files" in theme_data:
                theme_file_list = theme_data.get("files", [])
                if file_path in theme_file_list:
                    themes.append(theme_name)
                    # Mark theme as needing review due to file deletion
        return themes
    
    def _analyze_single_file_theme_impact(self, file_path: str) -> List[str]:
        """Analyze theme impact for a single file"""
        try:
            themes = set()
            
            # Load existing theme data
            theme_files = {}
            themes_dir = get_themes_path(self.project_root, self.config_manager)
            if themes_dir.exists():
                themes_json_path = themes_dir / "themes.json"
                if themes_json_path.exists():
                    try:
                        with open(themes_json_path, 'r') as f:
                            theme_files = json.load(f)
                    except (json.JSONDecodeError, FileNotFoundError):
                        theme_files = {}
            
            # Direct theme mapping
            direct_themes = self._get_themes_for_file(file_path, theme_files)
            themes.update(direct_themes)
            
            # Directory-based inference
            dir_themes = self._infer_themes_from_directory(file_path)
            themes.update(dir_themes)
            
            # Pattern-based inference
            pattern_themes = self._infer_themes_from_patterns(file_path)
            themes.update(pattern_themes)
            
            return list(themes)
            
        except Exception as e:
            print(f"Error analyzing single file theme impact for {file_path}: {e}")
            return []
    
