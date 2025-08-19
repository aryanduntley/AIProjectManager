"""
Context Loading Module
Handles core context loading, theme loading, and basic context operations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
import os
from .compressed_context import ContextMode, ContextResult

# Import utilities from parent module paths
from ...utils.project_paths import get_themes_path

logger = logging.getLogger(__name__)


class ContextLoading:
    """Core context loading and theme management operations."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties directly
        self.compressed_context_manager = parent_instance.compressed_context_manager
        self.theme_flow_queries = parent_instance.theme_flow_queries
        self.session_queries = parent_instance.session_queries
        self.file_metadata_queries = parent_instance.file_metadata_queries
        
        # Initialize flags and settings
        self._core_context_loaded = False
        self.max_memory_mb = 100  # Maximum context memory in MB
        self.readme_priority_files = [
            'README.md', 'readme.md', 'Readme.md',
            'README.txt', 'readme.txt'
        ]
    
    async def ensure_core_context_loaded(self):
        """Ensure compressed core context is loaded."""
        if not self._core_context_loaded:
            await self.compressed_context_manager.load_core_context()
            self._core_context_loaded = True
    
    async def get_session_boot_context(self, project_path: Path) -> Dict[str, Any]:
        """Get context specifically for session boot sequence."""
        await self.ensure_core_context_loaded()
        
        boot_sequence = self.compressed_context_manager.get_session_boot_sequence()
        core_rules = self.compressed_context_manager.get_core_rules()
        project_state = await self.compressed_context_manager._analyze_project_state(project_path)
        
        return {
            "bootSequence": boot_sequence,
            "coreRules": core_rules,
            "projectState": project_state,
            "contextMode": "session-boot"
        }
    
    async def get_situational_context(self, project_path: Path, situation: str) -> Dict[str, Any]:
        """Get context for a specific situation using compressed context."""
        await self.ensure_core_context_loaded()
        return await self.compressed_context_manager.generate_situational_context(project_path, situation)
    
    async def load_context(self, project_path: Path, primary_theme: str, 
                          context_mode: ContextMode = ContextMode.THEME_FOCUSED,
                          force_mode: bool = False) -> ContextResult:
        """Load context based on theme and context mode."""
        try:
            themes_dir = get_themes_path(project_path, self.parent.config_manager)
            
            # Load primary theme
            primary_theme_data = await self._load_theme(themes_dir, primary_theme)
            if not primary_theme_data:
                raise ValueError(f"Primary theme '{primary_theme}' not found")
            
            # Determine actual context mode (may escalate if needed)
            actual_mode = await self._determine_context_mode(
                themes_dir, primary_theme_data, context_mode, force_mode
            )
            
            # Load context based on determined mode
            context = await self._load_context_by_mode(
                project_path, themes_dir, primary_theme, primary_theme_data, actual_mode
            )
            
            # Load README files for context
            context.readmes = await self._load_readmes(project_path, context.paths)
            
            # Estimate memory usage
            context.memory_estimate = await self.parent._estimate_memory_usage(context)
            
            # Generate recommendations
            context.recommendations = await self.parent._generate_recommendations(context, {}, project_path)
            
            return context
            
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            raise
    
    async def _load_theme(self, themes_dir: Path, theme_name: str) -> Optional[Dict[str, Any]]:
        """Load a theme definition."""
        theme_file = themes_dir / f"{theme_name}.json"
        if not theme_file.exists():
            return None
        
        try:
            return json.loads(theme_file.read_text())
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in theme file: {theme_file}")
            return None
    
    async def _determine_context_mode(self, themes_dir: Path, primary_theme_data: Dict[str, Any],
                                    requested_mode: ContextMode, force_mode: bool) -> ContextMode:
        """Determine the actual context mode to use."""
        if force_mode:
            return requested_mode
        
        # Analyze theme complexity to suggest mode
        file_count = len(primary_theme_data.get('files', []))
        linked_themes = primary_theme_data.get('linkedThemes', [])
        shared_files = primary_theme_data.get('sharedFiles', {})
        
        # If theme has many linked themes or shared files, suggest expansion
        if requested_mode == ContextMode.THEME_FOCUSED:
            if len(linked_themes) > 2 or len(shared_files) > 5:
                logger.info(f"Theme has {len(linked_themes)} linked themes and {len(shared_files)} shared files. "
                           f"Consider using theme-expanded mode.")
                return ContextMode.THEME_EXPANDED
        
        # If expanded mode but few connections, theme-focused might suffice
        if requested_mode == ContextMode.THEME_EXPANDED:
            if len(linked_themes) == 0 and len(shared_files) <= 2:
                logger.info("Theme has few connections. theme-focused mode may be sufficient.")
        
        return requested_mode
    
    async def _load_context_by_mode(self, project_path: Path, themes_dir: Path, 
                                   primary_theme: str, primary_theme_data: Dict[str, Any],
                                   mode: ContextMode) -> ContextResult:
        """Load context based on the specified mode."""
        context = ContextResult(
            mode=mode,
            primary_theme=primary_theme,
            loaded_themes=[primary_theme],
            files=list(primary_theme_data.get('files', [])),
            paths=list(primary_theme_data.get('paths', [])),
            readmes={},
            shared_files={},
            recommendations=[],
            memory_estimate=0
        )
        
        if mode == ContextMode.THEME_FOCUSED:
            # Only load primary theme
            context.shared_files = primary_theme_data.get('sharedFiles', {})
            
        elif mode == ContextMode.THEME_EXPANDED:
            # Load primary theme + linked themes
            linked_themes = primary_theme_data.get('linkedThemes', [])
            
            for linked_theme in linked_themes:
                linked_data = await self._load_theme(themes_dir, linked_theme)
                if linked_data:
                    context.loaded_themes.append(linked_theme)
                    context.files.extend(linked_data.get('files', []))
                    context.paths.extend(linked_data.get('paths', []))
                    
                    # Merge shared files
                    for file_path, sharing_info in linked_data.get('sharedFiles', {}).items():
                        if file_path not in context.shared_files:
                            context.shared_files[file_path] = []
                        context.shared_files[file_path].extend(sharing_info.get('sharedWith', []))
            
        elif mode == ContextMode.PROJECT_WIDE:
            # Load all themes
            themes_index = themes_dir / "themes.json"
            if themes_index.exists():
                all_themes = json.loads(themes_index.read_text())
                
                for theme_name in all_themes.keys():
                    if theme_name != primary_theme:
                        theme_data = await self._load_theme(themes_dir, theme_name)
                        if theme_data:
                            context.loaded_themes.append(theme_name)
                            context.files.extend(theme_data.get('files', []))
                            context.paths.extend(theme_data.get('paths', []))
                            
                            # Merge shared files
                            for file_path, sharing_info in theme_data.get('sharedFiles', {}).items():
                                if file_path not in context.shared_files:
                                    context.shared_files[file_path] = []
                                context.shared_files[file_path].extend(sharing_info.get('sharedWith', []))
        
        # Remove duplicates
        context.files = list(set(context.files))
        context.paths = list(set(context.paths))
        
        # Add global files and paths that are always accessible
        global_paths = await self._get_global_paths(project_path)
        context.paths.extend(global_paths)
        context.paths = list(set(context.paths))
        
        return context
    
    async def _get_global_paths(self, project_path: Path) -> List[str]:
        """Get globally accessible paths regardless of theme."""
        global_patterns = [
            # Project root level
            "package.json", "requirements.txt", "Cargo.toml", "composer.json",
            ".env", ".env.local", "config.json", "settings.json",
            "Dockerfile", "docker-compose.yml", "Makefile",
            "README.md", "LICENSE", "CHANGELOG.md",
            ".gitignore", ".gitattributes",
            
            # Source root patterns
            "src", "lib", "app",
            "src/index.*", "src/main.*", "src/app.*", "src/App.*",
            "src/config", "src/constants", "src/types", "src/utils"
        ]
        
        global_paths = []
        
        for pattern in global_patterns:
            # Check if it's a direct file
            file_path = project_path / pattern
            if file_path.exists():
                if file_path.is_file():
                    global_paths.append(pattern)
                elif file_path.is_dir():
                    global_paths.append(pattern)
        
        return global_paths
    
    async def _load_readmes(self, project_path: Path, paths: List[str]) -> Dict[str, str]:
        """Load README files and database metadata for quick context."""
        readmes = {}
        
        # First, try to load from database metadata if available
        if self.file_metadata_queries:
            try:
                db_metadata = await self.parent._load_database_metadata(project_path, paths)
                readmes.update(db_metadata)
            except Exception as e:
                logger.debug(f"Error loading database metadata: {e}")
        
        # Add project root README (fallback or supplement)
        for readme_name in self.readme_priority_files:
            root_readme = project_path / readme_name
            if root_readme.exists():
                try:
                    content = root_readme.read_text(encoding='utf-8')
                    # If not already in database metadata, add it
                    root_key = str(Path('.'))
                    if root_key not in readmes:
                        readmes[root_key] = content[:2000]  # Limit to 2KB
                    break
                except Exception as e:
                    logger.debug(f"Error reading {root_readme}: {e}")
        
        # Load READMEs from theme paths (fallback for paths not in database)
        for path in paths:
            if path in readmes:  # Skip if already loaded from database
                continue
                
            path_obj = project_path / path
            if path_obj.is_dir():
                for readme_name in self.readme_priority_files:
                    readme_file = path_obj / readme_name
                    if readme_file.exists():
                        try:
                            content = readme_file.read_text(encoding='utf-8')
                            readmes[path] = content[:2000]  # Limit to 2KB
                            break
                        except Exception as e:
                            logger.debug(f"Error reading {readme_file}: {e}")
        
        return readmes
    