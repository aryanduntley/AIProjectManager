"""
Scope and context loading engine for the AI Project Manager MCP Server.

Handles intelligent context loading based on themes, README guidance, context modes,
compressed context management, and database-driven optimization for optimal AI session continuity.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import os

# Database integration
from ..database.theme_flow_queries import ThemeFlowQueries
from ..database.session_queries import SessionQueries
from ..database.file_metadata_queries import FileMetadataQueries

logger = logging.getLogger(__name__)


class ContextMode(Enum):
    """Available context loading modes."""
    THEME_FOCUSED = "theme-focused"
    THEME_EXPANDED = "theme-expanded"
    PROJECT_WIDE = "project-wide"


@dataclass
class ContextResult:
    """Result of context loading operation."""
    mode: ContextMode
    primary_theme: str
    loaded_themes: List[str]
    files: List[str]
    paths: List[str]
    readmes: Dict[str, str]
    shared_files: Dict[str, List[str]]
    recommendations: List[str]
    memory_estimate: int


class CompressedContextManager:
    """Manages compressed context files for optimal AI session continuity."""
    
    def __init__(self, mcp_server_path: Optional[Path] = None):
        """Initialize with MCP server path for core context loading."""
        if mcp_server_path is None:
            # Auto-detect MCP server path relative to this file
            mcp_server_path = Path(__file__).parent.parent
        
        self.mcp_server_path = mcp_server_path
        self.core_context_path = mcp_server_path / "core-context"
        
        # Core context (always loaded)
        self._core_context = {}
        self._loaded = False
    
    async def load_core_context(self) -> Dict[str, Any]:
        """Load compressed core context files."""
        if self._loaded:
            return self._core_context
        
        try:
            # Load all core context files
            core_files = [
                "system-essence.json",
                "workflow-triggers.json", 
                "directive-compressed.json",
                "validation-core.json"
            ]
            
            for filename in core_files:
                file_path = self.core_context_path / filename
                if file_path.exists():
                    context_data = json.loads(file_path.read_text())
                    self._core_context[filename.replace('.json', '')] = context_data
                else:
                    logger.warning(f"Core context file not found: {file_path}")
            
            self._loaded = True
            logger.info(f"Loaded {len(self._core_context)} core context files")
            
        except Exception as e:
            logger.error(f"Error loading core context: {e}")
            raise
        
        return self._core_context
    
    def get_workflow_for_scenario(self, scenario: str) -> Optional[Dict[str, Any]]:
        """Get workflow definition for a specific scenario."""
        if not self._loaded:
            return None
            
        workflow_triggers = self._core_context.get('workflow-triggers', {})
        scenarios = workflow_triggers.get('commonScenarios', {})
        
        return scenarios.get(scenario)
    
    def get_directive_summary(self, directive_key: str) -> Optional[Dict[str, Any]]:
        """Get compressed directive information."""
        if not self._loaded:
            return None
            
        directives = self._core_context.get('directive-compressed', {})
        return directives.get(directive_key)
    
    def get_validation_rules(self, validation_type: str) -> Optional[Dict[str, Any]]:
        """Get validation rules for specific validation type."""
        if not self._loaded:
            return None
            
        validation_core = self._core_context.get('validation-core', {})
        return validation_core.get(validation_type)
    
    def get_session_boot_sequence(self) -> List[str]:
        """Get the session boot sequence steps."""
        if not self._loaded:
            return []
            
        system_essence = self._core_context.get('system-essence', {})
        return system_essence.get('sessionBootSequence', [])
    
    def get_core_rules(self) -> List[str]:
        """Get critical rules for AI behavior."""
        if not self._loaded:
            return []
            
        system_essence = self._core_context.get('system-essence', {})
        return system_essence.get('criticalRules', [])
    
    def should_escalate_context(self, issue_description: str) -> Tuple[bool, str]:
        """Determine if context escalation is needed based on issue."""
        if not self._loaded:
            return False, "Core context not loaded"
        
        workflow_triggers = self._core_context.get('workflow-triggers', {})
        escalation_scenario = workflow_triggers.get('commonScenarios', {}).get('context_escalation_needed')
        
        if not escalation_scenario:
            return False, "No escalation rules found"
        
        # Check if issue contains escalation trigger keywords
        triggers = escalation_scenario.get('triggers', [])
        issue_lower = issue_description.lower()
        
        for trigger in triggers:
            if trigger.lower() in issue_lower:
                return True, f"Issue matches escalation trigger: {trigger}"
        
        return False, "No escalation triggers found in issue"
    
    def _directive_id_to_compressed_key(self, directive_id: str) -> str:
        """Convert numbered directive ID to compressed directive key."""
        # Handle already converted keys
        if not directive_id.startswith(('0', '1', '2')):
            return directive_id
            
        # Remove number prefix and convert to camelCase
        parts = directive_id.split('-', 1)
        if len(parts) == 2:
            name_parts = parts[1].split('-')
            # First part lowercase, rest title case
            camel_case = name_parts[0] + ''.join(word.capitalize() for word in name_parts[1:])
            return camel_case
        
        return directive_id
    
    def _has_implementation_note(self, obj: Any) -> bool:
        """Recursively search for implementationNote in a nested object."""
        if isinstance(obj, dict):
            if 'implementationNote' in obj:
                return True
            for value in obj.values():
                if self._has_implementation_note(value):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if self._has_implementation_note(item):
                    return True
        return False
    
    def get_directive_escalation_level(self, directive_id: str, operation_context: str = "") -> str:
        """Determine appropriate directive escalation level based on new escalation logic."""
        if not self._loaded:
            return "compressed"  # Default fallback
        
        # Get escalation rules from compressed directives
        directive_escalation = self._core_context.get('directive-compressed', {}).get('directiveEscalation', {})
        escalation_protocol = directive_escalation.get('escalationProtocol', {})
        
        # Check for forced JSON operations
        forced_json_ops = escalation_protocol.get('forcedJSONOperations', [])
        if directive_id in forced_json_ops:
            logger.info(f"Forcing JSON escalation for {directive_id} (complex system operation)")
            return "json"
        
        # Check for implementationNote in compressed directive (search recursively)
        compressed_key = self._directive_id_to_compressed_key(directive_id)
        compressed_directive = self.get_directive_summary(compressed_key)
        if compressed_directive and self._has_implementation_note(compressed_directive):
            logger.info(f"Auto-escalating {directive_id} to JSON (implementationNote present)")
            return "json"
        
        # Check escalation triggers
        when_to_escalate = directive_escalation.get('whenToEscalate', {})
        
        # Check for force JSON triggers
        force_json = when_to_escalate.get('forceJSON', [])
        auto_json = when_to_escalate.get('autoJSON', [])
        
        operation_lower = operation_context.lower()
        
        for trigger in force_json + auto_json:
            if trigger.lower() in operation_lower:
                logger.info(f"Auto-escalating {directive_id} to JSON (trigger: {trigger})")
                return "json"
        
        # Default to compressed for routine operations
        logger.debug(f"Using compressed directives for {directive_id} (routine operation)")
        return "compressed"
    
    def should_escalate_to_markdown(self, directive_id: str, json_context_insufficient: bool = False, 
                                   error_context: str = "") -> bool:
        """Determine if should escalate from JSON to Markdown directives."""
        if not self._loaded:
            return False
        
        # Always escalate if JSON context is insufficient
        if json_context_insufficient:
            logger.info(f"Escalating {directive_id} to MD (JSON context insufficient)")
            return True
        
        # Check escalation triggers
        directive_escalation = self._core_context.get('directive-compressed', {}).get('directiveEscalation', {})
        when_to_escalate = directive_escalation.get('whenToEscalate', {})
        auto_md = when_to_escalate.get('autoMD', [])
        
        error_lower = error_context.lower()
        
        for trigger in auto_md:
            if trigger.lower() in error_lower:
                logger.info(f"Auto-escalating {directive_id} to MD (trigger: {trigger})")
                return True
        
        return False
    
    async def load_directive_with_escalation(self, directive_id: str, operation_context: str = "", 
                                           force_level: Optional[str] = None) -> Dict[str, Any]:
        """Load directive with appropriate escalation level."""
        try:
            # Determine escalation level
            if force_level:
                escalation_level = force_level
                logger.info(f"Using forced escalation level {force_level} for {directive_id}")
            else:
                escalation_level = self.get_directive_escalation_level(directive_id, operation_context)
            
            directive_content = {}
            
            # Always start with compressed (for context preservation)
            compressed = self.get_directive_summary(directive_id)
            if compressed:
                directive_content['compressed'] = compressed
            
            # Load JSON if needed
            if escalation_level in ['json', 'markdown']:
                json_path = self.mcp_server_path / "reference" / "directives" / f"{directive_id}.json"
                if json_path.exists():
                    json_content = json.loads(json_path.read_text())
                    directive_content['json'] = json_content
                    logger.debug(f"Loaded JSON directive for {directive_id}")
                else:
                    logger.warning(f"JSON directive not found: {json_path}")
            
            # Load Markdown if needed
            if escalation_level == 'markdown':
                md_path = self.mcp_server_path / "reference" / "directivesmd" / f"{directive_id}.md"
                if md_path.exists():
                    md_content = md_path.read_text()
                    directive_content['markdown'] = md_content
                    logger.debug(f"Loaded MD directive for {directive_id}")
                else:
                    logger.warning(f"MD directive not found: {md_path}")
            
            directive_content['escalation_level'] = escalation_level
            directive_content['escalation_reason'] = f"Auto-escalated based on {operation_context}" if operation_context else "Default level"
            
            return directive_content
            
        except Exception as e:
            logger.error(f"Error loading directive {directive_id}: {e}")
            return {"error": str(e), "escalation_level": "compressed"}
    
    async def generate_situational_context(self, project_path: Path, situation: str) -> Dict[str, Any]:
        """Generate context specific to current project situation."""
        try:
            # Load project state
            project_state = await self._analyze_project_state(project_path)
            
            # Get workflow for situation
            workflow = self.get_workflow_for_scenario(situation)
            if not workflow:
                return {"error": f"No workflow found for situation: {situation}"}
            
            # Generate contextual response
            context = {
                "situation": situation,
                "workflow": workflow,
                "projectState": project_state,
                "requiredFiles": workflow.get('requiredFiles', []),
                "actions": workflow.get('actions', []),
                "contextMode": workflow.get('contextMode', 'theme-focused'),
                "priority": workflow.get('priority', 'medium')
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error generating situational context: {e}")
            return {"error": str(e)}
    
    async def _analyze_project_state(self, project_path: Path) -> Dict[str, Any]:
        """Analyze current project state for context generation."""
        state = {
            "hasProjectManagement": False,
            "hasActiveImplementationPlan": False,
            "hasActiveTasks": False,
            "themesCount": 0,
            "milestonesCount": 0
        }
        
        try:
            pm_path = project_path / "projectManagement"
            if pm_path.exists():
                state["hasProjectManagement"] = True
                
                # Check for active implementation plan
                impl_active = pm_path / "Implementations" / "active"
                if impl_active.exists():
                    active_plans = list(impl_active.glob("*.md"))
                    state["hasActiveImplementationPlan"] = len(active_plans) > 0
                
                # Check for active tasks
                tasks_active = pm_path / "Tasks" / "active"
                if tasks_active.exists():
                    active_tasks = list(tasks_active.glob("TASK-*.json"))
                    state["hasActiveTasks"] = len(active_tasks) > 0
                
                # Count themes
                themes_dir = pm_path / "Themes"
                if themes_dir.exists():
                    theme_files = list(themes_dir.glob("*.json"))
                    # Exclude themes.json index file
                    state["themesCount"] = len([f for f in theme_files if f.name != "themes.json"])
                
                # Count milestones
                completion_path = pm_path / "Tasks" / "completion-path.json"
                if completion_path.exists():
                    try:
                        cp_data = json.loads(completion_path.read_text())
                        state["milestonesCount"] = len(cp_data.get('milestones', []))
                    except:
                        pass
        
        except Exception as e:
            logger.debug(f"Error analyzing project state: {e}")
        
        return state


class ScopeEngine:
    """Engine for determining and loading project context based on themes with database optimization."""
    
    def __init__(self, mcp_server_path: Optional[Path] = None, 
                 theme_flow_queries: Optional[ThemeFlowQueries] = None,
                 session_queries: Optional[SessionQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None):
        self.max_memory_mb = 100  # Maximum context memory in MB
        self.readme_priority_files = [
            'README.md', 'readme.md', 'Readme.md',
            'README.txt', 'readme.txt'
        ]
        
        # Initialize compressed context manager
        self.context_manager = CompressedContextManager(mcp_server_path)
        self._core_context_loaded = False
        
        # Database components for optimized context loading
        self.theme_flow_queries = theme_flow_queries
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
    
    async def ensure_core_context_loaded(self):
        """Ensure compressed core context is loaded."""
        if not self._core_context_loaded:
            await self.context_manager.load_core_context()
            self._core_context_loaded = True
    
    async def get_session_boot_context(self, project_path: Path) -> Dict[str, Any]:
        """Get context specifically for session boot sequence."""
        await self.ensure_core_context_loaded()
        
        boot_sequence = self.context_manager.get_session_boot_sequence()
        core_rules = self.context_manager.get_core_rules()
        project_state = await self.context_manager._analyze_project_state(project_path)
        
        return {
            "bootSequence": boot_sequence,
            "coreRules": core_rules,
            "projectState": project_state,
            "contextMode": "session-boot"
        }
    
    async def get_situational_context(self, project_path: Path, situation: str) -> Dict[str, Any]:
        """Get context for a specific situation using compressed context."""
        await self.ensure_core_context_loaded()
        return await self.context_manager.generate_situational_context(project_path, situation)
    
    async def load_context(self, project_path: Path, primary_theme: str, 
                          context_mode: ContextMode = ContextMode.THEME_FOCUSED,
                          force_mode: bool = False) -> ContextResult:
        """Load context based on theme and context mode."""
        try:
            themes_dir = project_path / "projectManagement" / "Themes"
            
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
            context.memory_estimate = await self._estimate_memory_usage(context)
            
            # Generate recommendations
            context.recommendations = await self._generate_recommendations(context, actual_mode, context_mode)
            
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
                db_metadata = await self._load_database_metadata(project_path, paths)
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
    
    async def _load_database_metadata(self, project_path: Path, paths: List[str]) -> Dict[str, str]:
        """Load file metadata from database to replace README.json files."""
        metadata_content = {}
        
        try:
            # Get directory metadata for each path
            for path in paths:
                full_path = str(project_path / path)
                
                # Get directory metadata from database
                dir_metadata = self.file_metadata_queries.get_directory_metadata(full_path)
                
                if dir_metadata:
                    # Format metadata as README-like content
                    content_parts = []
                    
                    if dir_metadata.get('description'):
                        content_parts.append(f"# {path}\n\n{dir_metadata['description']}")
                    
                    if dir_metadata.get('purpose'):
                        content_parts.append(f"**Purpose**: {dir_metadata['purpose']}")
                    
                    # File relationships
                    file_relationships = self.file_metadata_queries.get_file_relationships(full_path)
                    if file_relationships:
                        content_parts.append("\n**File Relationships**:")
                        for rel in file_relationships[:5]:  # Limit to top 5
                            content_parts.append(f"- {rel.get('file_path', 'Unknown')}: {rel.get('relationship_type', 'related')}")
                    
                    # Key files in directory
                    key_files = dir_metadata.get('key_files', [])
                    if key_files:
                        content_parts.append("\n**Key Files**:")
                        for file in key_files[:5]:  # Limit to top 5
                            if isinstance(file, dict):
                                content_parts.append(f"- {file.get('name', 'Unknown')}: {file.get('purpose', 'No description')}")
                            else:
                                content_parts.append(f"- {file}")
                    
                    # Combine content
                    if content_parts:
                        full_content = "\n".join(content_parts)
                        metadata_content[path] = full_content[:2000]  # Limit to 2KB
                        
                        # Log that we're using database metadata
                        logger.debug(f"Using database metadata for {path} instead of README.json")
            
            # Also try to get project root metadata
            root_metadata = self.file_metadata_queries.get_directory_metadata(str(project_path))
            if root_metadata and '.' not in metadata_content:
                content_parts = []
                
                if root_metadata.get('description'):
                    content_parts.append(f"# Project Overview\n\n{root_metadata['description']}")
                
                if root_metadata.get('purpose'):
                    content_parts.append(f"**Purpose**: {root_metadata['purpose']}")
                
                # Project structure overview
                structure = root_metadata.get('structure_overview')
                if structure:
                    content_parts.append(f"\n**Structure**: {structure}")
                
                if content_parts:
                    metadata_content['.'] = "\n".join(content_parts)[:2000]
            
        except Exception as e:
            logger.warning(f"Error loading database metadata: {e}")
            # Return empty dict to fall back to file-based README loading
            return {}
        
        return metadata_content
    
    async def _estimate_memory_usage(self, context: ContextResult) -> int:
        """Estimate memory usage in MB for the loaded context."""
        # Rough estimates
        files_mb = len(context.files) * 0.1  # ~100KB per file average
        readmes_mb = sum(len(content) for content in context.readmes.values()) / (1024 * 1024)
        themes_mb = len(context.loaded_themes) * 0.01  # ~10KB per theme definition
        
        total_mb = files_mb + readmes_mb + themes_mb
        return int(total_mb)
    
    async def _generate_recommendations(self, context: ContextResult, 
                                       actual_mode: ContextMode, 
                                       requested_mode: ContextMode) -> List[str]:
        """Generate recommendations for context optimization."""
        recommendations = []
        
        # Memory usage recommendations
        if context.memory_estimate > self.max_memory_mb:
            recommendations.append(
                f"High memory usage ({context.memory_estimate}MB). "
                f"Consider using a more focused context mode."
            )
        
        # Mode recommendations
        if actual_mode != requested_mode:
            recommendations.append(
                f"Context mode escalated from {requested_mode.value} to {actual_mode.value} "
                f"based on theme complexity."
            )
        
        # Coverage recommendations
        if context.mode == ContextMode.THEME_FOCUSED and len(context.shared_files) > 3:
            recommendations.append(
                "Theme has many shared files. Consider theme-expanded mode for better context."
            )
        
        if context.mode == ContextMode.PROJECT_WIDE and len(context.loaded_themes) > 10:
            recommendations.append(
                "Loading many themes. Consider if theme-expanded mode would be sufficient."
            )
        
        # README recommendations
        missing_readmes = []
        for path in context.paths:
            if path not in context.readmes and path != '.':
                missing_readmes.append(path)
        
        if len(missing_readmes) > 3:
            recommendations.append(
                f"Consider adding README.md files to {len(missing_readmes)} directories "
                f"for better context guidance."
            )
        
        return recommendations
    
    async def assess_context_escalation(self, current_context: ContextResult, 
                                      issue_description: str) -> Tuple[bool, ContextMode, str]:
        """Assess if context escalation is needed based on an issue."""
        current_mode = current_context.mode
        
        # Keywords that suggest need for broader context
        escalation_keywords = [
            'import', 'dependency', 'reference', 'call', 'connection',
            'integration', 'shared', 'cross', 'global', 'config'
        ]
        
        # Check if issue mentions cross-theme concerns
        issue_lower = issue_description.lower()
        needs_escalation = any(keyword in issue_lower for keyword in escalation_keywords)
        
        if not needs_escalation:
            return False, current_mode, "No escalation needed"
        
        # Determine escalation path
        if current_mode == ContextMode.THEME_FOCUSED:
            new_mode = ContextMode.THEME_EXPANDED
            reason = "Issue mentions cross-theme dependencies or integrations"
        elif current_mode == ContextMode.THEME_EXPANDED:
            new_mode = ContextMode.PROJECT_WIDE
            reason = "Issue requires project-wide context"
        else:
            return False, current_mode, "Already at maximum context level"
        
        return True, new_mode, reason
    
    async def get_context_summary(self, context: ContextResult) -> str:
        """Get a human-readable summary of the loaded context."""
        summary_parts = [
            f"Context Mode: {context.mode.value}",
            f"Primary Theme: {context.primary_theme}",
            f"Loaded Themes: {', '.join(context.loaded_themes)}",
            f"Files: {len(context.files)} files",
            f"Paths: {len(context.paths)} directories",
            f"README files: {len(context.readmes)} found",
            f"Memory Usage: ~{context.memory_estimate}MB"
        ]
        
        if context.shared_files:
            summary_parts.append(f"Shared Files: {len(context.shared_files)} files shared across themes")
        
        if context.recommendations:
            summary_parts.append("Recommendations:")
            for rec in context.recommendations:
                summary_parts.append(f"  - {rec}")
        
        return "\n".join(summary_parts)
    
    async def filter_files_by_relevance(self, context: ContextResult, 
                                       task_description: str) -> List[str]:
        """Filter context files by relevance to a specific task."""
        if not task_description:
            return context.files
        
        # Extract keywords from task description
        task_keywords = set(word.lower().strip('.,!?:;') 
                           for word in task_description.split() 
                           if len(word) > 2)
        
        # Score files based on keyword matches
        file_scores = {}
        for file_path in context.files:
            score = 0
            file_parts = file_path.lower().replace('/', ' ').replace('_', ' ').replace('-', ' ')
            
            for keyword in task_keywords:
                if keyword in file_parts:
                    score += 1
            
            # Boost score for files in primary theme
            if any(theme_path in file_path for theme_path in context.paths[:3]):
                score += 0.5
            
            file_scores[file_path] = score
        
        # Return files sorted by relevance (minimum score of 0.5)
        relevant_files = [
            file_path for file_path, score in file_scores.items() 
            if score >= 0.5
        ]
        
        # If no relevant files found, return top N files from primary theme
        if not relevant_files and context.files:
            primary_theme_files = [
                f for f in context.files 
                if any(theme_path in f for theme_path in context.paths[:3])
            ]
            relevant_files = primary_theme_files[:10] if primary_theme_files else context.files[:10]
        
        return relevant_files
    
    async def validate_context_integrity(self, project_path: Path, context: ContextResult) -> Dict[str, Any]:
        """Validate context integrity using compressed validation rules."""
        await self.ensure_core_context_loaded()
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks_performed": []
        }
        
        try:
            # Get validation rules from compressed context
            integration_rules = self.context_manager.get_validation_rules('integrationValidation')
            integrity_rules = self.context_manager.get_validation_rules('dataIntegrity')
            
            if not integration_rules or not integrity_rules:
                validation_results["warnings"].append("Validation rules not available in compressed context")
                return validation_results
            
            # Validate theme integrity
            themes_dir = project_path / "projectManagement" / "Themes"
            for theme_name in context.loaded_themes:
                theme_file = themes_dir / f"{theme_name}.json"
                if not theme_file.exists():
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"Theme file missing: {theme_name}.json")
                
                validation_results["checks_performed"].append(f"Theme file existence: {theme_name}")
            
            # Validate file references
            file_check_count = 0
            for file_path in context.files[:10]:  # Check first 10 files for performance
                full_path = project_path / file_path
                if not full_path.exists():
                    validation_results["warnings"].append(f"Referenced file not found: {file_path}")
                file_check_count += 1
            
            validation_results["checks_performed"].append(f"File existence checks: {file_check_count} files")
            
            # Check README coverage
            missing_readmes = []
            for path in context.paths[:5]:  # Check first 5 paths
                if path not in context.readmes and path != '.':
                    missing_readmes.append(path)
            
            if missing_readmes:
                validation_results["warnings"].append(f"Missing README files in {len(missing_readmes)} directories")
            
            validation_results["checks_performed"].append("README coverage check")
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    async def get_compressed_directive(self, directive_key: str) -> Optional[Dict[str, Any]]:
        """Get compressed directive information."""
        await self.ensure_core_context_loaded()
        return self.context_manager.get_directive_summary(directive_key)
    
    # Database-Enhanced Context Loading Methods
    
    async def load_context_with_database_optimization(self, project_path: Path, primary_theme: str,
                                                    context_mode: ContextMode = ContextMode.THEME_FOCUSED,
                                                    task_id: Optional[str] = None,
                                                    session_id: Optional[str] = None) -> ContextResult:
        """Load context with database optimization for theme-flow relationships and session tracking."""
        try:
            # Load context using existing method first
            context = await self.load_context(project_path, primary_theme, context_mode)
            
            # Enhance with database information if available
            if self.theme_flow_queries:
                await self._enhance_context_with_flows(context, primary_theme)
            
            if self.session_queries and session_id:
                await self._track_context_usage(session_id, context, task_id)
            
            if self.file_metadata_queries:
                await self._enhance_context_with_file_intelligence(project_path, context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error loading context with database optimization: {e}")
            # Fallback to regular context loading
            return await self.load_context(project_path, primary_theme, context_mode)
    
    async def _enhance_context_with_flows(self, context: ContextResult, primary_theme: str):
        """Enhance context with flow information from database."""
        try:
            # Get flows associated with this theme
            theme_flows = await self.theme_flow_queries.get_flows_for_theme(primary_theme)
            
            if theme_flows:
                # Add flow information to recommendations
                flow_count = len(theme_flows)
                context.recommendations.append(
                    f"Theme has {flow_count} associated flows: {', '.join([f['flow_id'] for f in theme_flows])}"
                )
                
                # Load flow status for better context
                for flow_info in theme_flows:
                    flow_status = await self.theme_flow_queries.get_flow_status(flow_info['flow_id'])
                    if flow_status:
                        status_info = f"Flow {flow_info['flow_id']}: {flow_status['status']} ({flow_status['completion_percentage']}%)"
                        context.recommendations.append(status_info)
        
        except Exception as e:
            logger.debug(f"Error enhancing context with flows: {e}")
    
    async def _track_context_usage(self, session_id: str, context: ContextResult, task_id: Optional[str]):
        """Track context usage for analytics and learning."""
        try:
            # Update session context tracking
            context_data = {
                "loaded_themes": context.loaded_themes,
                "context_mode": context.mode.value,
                "memory_estimate": context.memory_estimate,
                "files_count": len(context.files),
                "paths_count": len(context.paths),
                "readmes_count": len(context.readmes)
            }
            
            await self.session_queries.update_session_context(session_id, context_data)
            
            if task_id:
                # Determine if context escalation is needed based on task complexity
                target_mode = self._determine_required_mode_for_task(task_id, context)
                
                # Log context escalation if mode was changed
                await self.session_queries.log_context_escalation(
                    session_id=session_id,
                    from_mode=context.mode.value,
                    to_mode=target_mode.value,
                    reason=f"Context loaded for task {task_id}" + (
                        f" (escalated to {target_mode.value})" if target_mode != context.mode else ""
                    ),
                    task_id=task_id
                )
                
                # Update context mode if escalation is needed
                if target_mode != context.mode:
                    context.mode = target_mode
        
        except Exception as e:
            logger.debug(f"Error tracking context usage: {e}")
    
    def _determine_required_mode_for_task(self, task_id: str, current_context: ContextResult) -> ContextMode:
        """Determine the required context mode based on task complexity and requirements."""
        try:
            # Start with current mode as baseline
            required_mode = current_context.mode
            
            # Get task details to assess complexity
            if hasattr(self, 'task_queries') and self.task_queries:
                try:
                    task_details = self.task_queries.get_task_details(task_id)
                    if task_details:
                        # Escalate based on task complexity indicators
                        priority = task_details.get('priority', 'medium').lower()
                        estimated_effort = task_details.get('estimated_effort')
                        themes = task_details.get('related_themes', [])
                        
                        # High priority tasks may need broader context
                        if priority == 'high' and required_mode == ContextMode.FOCUSED:
                            required_mode = ContextMode.BALANCED
                        
                        # Complex tasks with multiple themes need broader context
                        if len(themes) >= 3 and required_mode == ContextMode.FOCUSED:
                            required_mode = ContextMode.BALANCED
                        elif len(themes) >= 5 and required_mode == ContextMode.BALANCED:
                            required_mode = ContextMode.COMPREHENSIVE
                        
                        # Large estimated effort suggests comprehensive context needed
                        if estimated_effort and isinstance(estimated_effort, (int, float)):
                            if estimated_effort >= 8 and required_mode != ContextMode.COMPREHENSIVE:
                                required_mode = ContextMode.COMPREHENSIVE
                            elif estimated_effort >= 5 and required_mode == ContextMode.FOCUSED:
                                required_mode = ContextMode.BALANCED
                        
                        # Check for task type indicators
                        title = task_details.get('title', '').lower()
                        description = task_details.get('description', '').lower()
                        
                        complexity_keywords = [
                            'refactor', 'redesign', 'architecture', 'integration', 
                            'migration', 'optimization', 'security', 'performance'
                        ]
                        
                        comprehensive_keywords = [
                            'system', 'entire', 'complete', 'full', 'comprehensive',
                            'overhaul', 'rebuild', 'restructure'
                        ]
                        
                        # Check for complexity indicators in title/description
                        if any(keyword in title or keyword in description for keyword in comprehensive_keywords):
                            required_mode = ContextMode.COMPREHENSIVE
                        elif any(keyword in title or keyword in description for keyword in complexity_keywords):
                            if required_mode == ContextMode.FOCUSED:
                                required_mode = ContextMode.BALANCED
                        
                except Exception as task_error:
                    logger.debug(f"Could not analyze task details for mode determination: {task_error}")
            
            # Context size-based escalation
            current_files = len(current_context.relevant_files)
            current_themes = len(current_context.loaded_themes)
            
            # If context is already large, maintain or escalate mode
            if current_files >= 50 or current_themes >= 10:
                if required_mode == ContextMode.FOCUSED:
                    required_mode = ContextMode.COMPREHENSIVE
                elif required_mode == ContextMode.BALANCED:
                    required_mode = ContextMode.COMPREHENSIVE
            elif current_files >= 20 or current_themes >= 5:
                if required_mode == ContextMode.FOCUSED:
                    required_mode = ContextMode.BALANCED
            
            # Never downgrade mode during a session (sticky escalation)
            if required_mode.value < current_context.mode.value:
                required_mode = current_context.mode
            
            return required_mode
            
        except Exception as e:
            logger.error(f"Error determining required mode for task {task_id}: {e}")
            # Safe fallback - maintain current mode
            return current_context.mode
    
    async def _enhance_context_with_file_intelligence(self, project_path: Path, context: ContextResult):
        """Enhance context with file metadata and relationships."""
        try:
            # Get file modification history for relevant files
            recent_files = []
            for file_path in context.files[:10]:  # Check recent activity for first 10 files
                file_info = await self.file_metadata_queries.get_file_modification_history(file_path, limit=1)
                if file_info:
                    recent_files.append((file_path, file_info[0]))
            
            if recent_files:
                # Sort by most recently modified
                recent_files.sort(key=lambda x: x[1]['timestamp'], reverse=True)
                most_recent = recent_files[0]
                
                context.recommendations.append(
                    f"Most recently modified file: {most_recent[0]} "
                    f"({most_recent[1]['timestamp']})"
                )
        
        except Exception as e:
            logger.debug(f"Error enhancing context with file intelligence: {e}")
    
    async def get_optimized_flow_context(self, project_path: Path, flow_ids: List[str],
                                       session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get optimized context for specific flows using database relationships."""
        if not self.theme_flow_queries:
            return {"error": "Theme-flow queries not available"}
        
        try:
            context_data = {
                "flows": {},
                "related_themes": set(),
                "cross_flow_dependencies": [],
                "recommended_context_mode": ContextMode.THEME_FOCUSED.value
            }
            
            # Load flow information and related themes
            for flow_id in flow_ids:
                # Get flow details
                flow_info = await self.theme_flow_queries.get_flow_details(flow_id)
                if flow_info:
                    context_data["flows"][flow_id] = flow_info
                    
                    # Get themes associated with this flow
                    flow_themes = await self.theme_flow_queries.get_themes_for_flow(flow_id)
                    for theme_info in flow_themes:
                        context_data["related_themes"].add(theme_info['theme_name'])
                
                # Get cross-flow dependencies
                dependencies = await self.theme_flow_queries.get_cross_flow_dependencies(flow_id)
                context_data["cross_flow_dependencies"].extend(dependencies)
            
            # Convert set to list for JSON serialization
            context_data["related_themes"] = list(context_data["related_themes"])
            
            # Determine recommended context mode based on complexity
            theme_count = len(context_data["related_themes"])
            dependency_count = len(context_data["cross_flow_dependencies"])
            
            if theme_count > 3 or dependency_count > 5:
                context_data["recommended_context_mode"] = ContextMode.PROJECT_WIDE.value
            elif theme_count > 1 or dependency_count > 0:
                context_data["recommended_context_mode"] = ContextMode.THEME_EXPANDED.value
            
            # Track usage if session provided
            if session_id and self.session_queries:
                await self.session_queries.log_flow_context_usage(
                    session_id=session_id,
                    flow_ids=flow_ids,
                    themes_loaded=context_data["related_themes"],
                    context_mode=context_data["recommended_context_mode"]
                )
            
            return context_data
            
        except Exception as e:
            logger.error(f"Error getting optimized flow context: {e}")
            return {"error": str(e)}
    
    async def get_intelligent_context_recommendations(self, project_path: Path, 
                                                    current_context: ContextResult,
                                                    task_description: str,
                                                    session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get intelligent context recommendations based on task and historical data."""
        recommendations = {
            "current_assessment": {},
            "escalation_recommendations": [],
            "flow_suggestions": [],
            "theme_suggestions": [],
            "memory_optimization": []
        }
        
        try:
            # Assess current context
            recommendations["current_assessment"] = {
                "mode": current_context.mode.value,
                "themes_loaded": len(current_context.loaded_themes),
                "files_available": len(current_context.files),
                "memory_usage": current_context.memory_estimate,
                "coverage_score": await self._calculate_coverage_score(current_context)
            }
            
            # Use database analytics if available
            if self.session_queries and session_id:
                # Get similar tasks and their successful context patterns
                similar_patterns = await self.session_queries.get_successful_context_patterns(
                    task_keywords=task_description.lower().split()[:5]
                )
                
                if similar_patterns:
                    recommendations["escalation_recommendations"].append({
                        "reason": "Based on similar successful tasks",
                        "suggested_mode": similar_patterns.get('most_successful_mode'),
                        "confidence": similar_patterns.get('confidence_score', 0.5)
                    })
            
            # Flow-based recommendations if database available
            if self.theme_flow_queries:
                primary_theme = current_context.primary_theme
                relevant_flows = await self.theme_flow_queries.get_flows_for_theme(primary_theme)
                
                incomplete_flows = [
                    f for f in relevant_flows 
                    if f.get('completion_percentage', 0) < 100
                ]
                
                if incomplete_flows:
                    recommendations["flow_suggestions"] = [
                        {
                            "flow_id": f['flow_id'],
                            "status": f['status'],
                            "completion": f.get('completion_percentage', 0),
                            "suggestion": f"Consider flow {f['flow_id']} for task context"
                        }
                        for f in incomplete_flows
                    ]
            
            # Memory optimization suggestions
            if current_context.memory_estimate > self.max_memory_mb * 0.8:
                recommendations["memory_optimization"].append({
                    "issue": "High memory usage detected",
                    "current_usage": current_context.memory_estimate,
                    "suggestions": [
                        "Consider more focused context mode",
                        "Use file relevance filtering",
                        "Limit README file loading"
                    ]
                })
            
        except Exception as e:
            logger.error(f"Error generating intelligent context recommendations: {e}")
            recommendations["error"] = str(e)
        
        return recommendations
    
    async def _calculate_coverage_score(self, context: ContextResult) -> float:
        """Calculate a coverage score for the current context."""
        try:
            # Base score from theme coverage
            theme_score = min(len(context.loaded_themes) / 5.0, 1.0)
            
            # README coverage score
            readme_score = min(len(context.readmes) / len(context.paths) if context.paths else 0, 1.0)
            
            # File coverage score (balanced - not too many, not too few)
            ideal_file_count = 15
            file_score = 1.0 - abs(len(context.files) - ideal_file_count) / ideal_file_count
            file_score = max(0.0, min(file_score, 1.0))
            
            # Weighted average
            coverage_score = (theme_score * 0.3 + readme_score * 0.3 + file_score * 0.4)
            
            return round(coverage_score, 2)
            
        except Exception as e:
            logger.debug(f"Error calculating coverage score: {e}")
            return 0.5
    
    # Multi-Flow System Integration Methods
    
    async def load_selective_flows_for_context(self, project_path: Path, 
                                             task_themes: List[str],
                                             task_description: str = "",
                                             max_flows: int = 5,
                                             session_id: Optional[str] = None) -> Dict[str, Any]:
        """Load flows selectively based on task requirements using multi-flow system."""
        if not self.theme_flow_queries:
            return {"error": "Multi-flow system requires database integration"}
        
        try:
            # Use database optimization for flow selection
            selected_flows = await self._select_flows_with_database_intelligence(
                task_themes, task_description, max_flows, session_id
            )
            
            # Load actual flow data
            flow_dir = project_path / "projectManagement" / "ProjectFlow"
            loaded_flows = {}
            flow_context = {
                "selected_flows": [],
                "cross_flow_dependencies": [],
                "recommended_context_mode": "theme-focused",
                "performance_metrics": {
                    "selection_time_ms": 0,
                    "loading_time_ms": 0,
                    "memory_estimate_kb": 0
                }
            }
            
            start_time = datetime.utcnow()
            
            for flow_info in selected_flows:
                flow_id = flow_info["flow_id"]
                flow_file = flow_info.get("flow_file", f"{flow_info.get('domain', 'general')}-flow.json")
                flow_path = flow_dir / flow_file
                
                if flow_path.exists():
                    try:
                        flow_data = json.loads(flow_path.read_text())
                        loaded_flows[flow_id] = flow_data
                        
                        flow_summary = {
                            "flow_id": flow_id,
                            "name": flow_data.get("metadata", {}).get("name", "Unknown"),
                            "domain": flow_data.get("metadata", {}).get("domain", "general"),
                            "status": flow_data.get("status", {}).get("overall_status", "unknown"),
                            "completion_percentage": flow_data.get("status", {}).get("completion_percentage", 0),
                            "themes": flow_data.get("themes", {}),
                            "flows_count": len(flow_data.get("flows", {})),
                            "relevance_score": flow_info.get("relevance_score", 0)
                        }
                        flow_context["selected_flows"].append(flow_summary)
                        
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in flow file: {flow_file}")
            
            loading_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            flow_context["performance_metrics"]["loading_time_ms"] = loading_time
            
            # Analyze cross-flow dependencies
            if len(loaded_flows) > 1:
                dependencies = await self._analyze_cross_flow_dependencies_for_context(
                    list(loaded_flows.keys())
                )
                flow_context["cross_flow_dependencies"] = dependencies
            
            # Determine recommended context mode based on flow complexity
            total_flows_count = sum(len(data.get("flows", {})) for data in loaded_flows.values())
            total_themes = set()
            for flow_data in loaded_flows.values():
                themes = flow_data.get("themes", {})
                total_themes.update(themes.get("primary", []))
                total_themes.update(themes.get("secondary", []))
            
            if len(total_themes) > 3 or total_flows_count > 10:
                flow_context["recommended_context_mode"] = "project-wide"
            elif len(total_themes) > 1 or len(flow_context["cross_flow_dependencies"]) > 0:
                flow_context["recommended_context_mode"] = "theme-expanded"
            
            # Estimate memory usage
            flow_context["performance_metrics"]["memory_estimate_kb"] = len(loaded_flows) * 100  # ~100KB per flow
            
            # Track usage if session provided
            if session_id and self.session_queries:
                await self.session_queries.log_selective_flow_loading(
                    session_id=session_id,
                    task_themes=task_themes,
                    loaded_flows=list(loaded_flows.keys()),
                    performance_metrics=flow_context["performance_metrics"]
                )
            
            flow_context["loaded_flows_data"] = loaded_flows
            return flow_context
            
        except Exception as e:
            logger.error(f"Error in selective flow loading: {e}")
            return {"error": str(e)}
    
    async def get_context_with_selective_flows(self, project_path: Path, 
                                             primary_theme: str,
                                             task_description: str = "",
                                             context_mode: ContextMode = ContextMode.THEME_FOCUSED,
                                             max_flows: int = 5,
                                             session_id: Optional[str] = None) -> ContextResult:
        """Load context enhanced with selectively loaded flows."""
        try:
            # Load base context
            base_context = await self.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=primary_theme,
                context_mode=context_mode,
                session_id=session_id
            )
            
            # Get related themes from context
            task_themes = base_context.loaded_themes
            
            # Load selective flows
            flow_context = await self.load_selective_flows_for_context(
                project_path=project_path,
                task_themes=task_themes,
                task_description=task_description,
                max_flows=max_flows,
                session_id=session_id
            )
            
            if "error" not in flow_context:
                # Enhance context with flow information
                flow_recommendations = []
                
                # Add flow-specific recommendations
                selected_flows = flow_context.get("selected_flows", [])
                if selected_flows:
                    flow_recommendations.append(
                        f"Loaded {len(selected_flows)} relevant flows for task context"
                    )
                    
                    incomplete_flows = [f for f in selected_flows if f["completion_percentage"] < 100]
                    if incomplete_flows:
                        flow_recommendations.append(
                            f"{len(incomplete_flows)} flows incomplete - consider prioritizing completion"
                        )
                
                # Cross-flow dependency recommendations
                dependencies = flow_context.get("cross_flow_dependencies", [])
                if dependencies:
                    flow_recommendations.append(
                        f"Found {len(dependencies)} cross-flow dependencies - consider loading order"
                    )
                
                # Context mode recommendations based on flows
                recommended_mode = flow_context.get("recommended_context_mode")
                if recommended_mode and recommended_mode != context_mode.value:
                    flow_recommendations.append(
                        f"Multi-flow analysis suggests {recommended_mode} context mode"
                    )
                
                # Performance recommendations
                perf_metrics = flow_context.get("performance_metrics", {})
                memory_kb = perf_metrics.get("memory_estimate_kb", 0)
                if memory_kb > 1000:  # > 1MB
                    flow_recommendations.append(
                        f"Flow memory usage: {memory_kb}KB - consider selective loading"
                    )
                
                # Add flow recommendations to base context
                base_context.recommendations.extend(flow_recommendations)
                
                # Update memory estimate with flow data
                base_context.memory_estimate += int(memory_kb / 1024)  # Convert to MB
            
            return base_context
            
        except Exception as e:
            logger.error(f"Error loading context with selective flows: {e}")
            # Fallback to regular context loading
            return await self.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=primary_theme,
                context_mode=context_mode,
                session_id=session_id
            )
    
    async def _select_flows_with_database_intelligence(self, task_themes: List[str],
                                                     task_description: str,
                                                     max_flows: int,
                                                     session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Select flows using database intelligence and historical patterns."""
        selected_flows = []
        
        try:
            # Get flows for each theme
            theme_flows = []
            for theme in task_themes:
                flows = await self.theme_flow_queries.get_flows_for_theme(theme)
                theme_flows.extend(flows)
            
            # Remove duplicates and score by relevance
            flows_by_id = {}
            for flow in theme_flows:
                flow_id = flow["flow_id"]
                if flow_id not in flows_by_id:
                    flows_by_id[flow_id] = flow
                    flows_by_id[flow_id]["relevance_score"] = 0
                
                # Base relevance score from theme relationship
                relevance_order = flow.get("relevance_order", 1)
                flows_by_id[flow_id]["relevance_score"] += 1.0 / relevance_order
            
            # Enhanced scoring with task description
            if task_description:
                task_keywords = set(word.lower() for word in task_description.split() if len(word) > 2)
                
                for flow_id, flow_info in flows_by_id.items():
                    # Check flow file name
                    flow_file = flow_info.get("flow_file", "").lower()
                    file_keywords = set(flow_file.replace("-flow.json", "").replace("-", " ").split())
                    
                    keyword_matches = len(task_keywords.intersection(file_keywords))
                    flows_by_id[flow_id]["relevance_score"] += keyword_matches * 0.5
            
            # Historical success pattern scoring if session available
            if session_id and self.session_queries:
                try:
                    success_patterns = await self.session_queries.get_flow_success_patterns(
                        session_id=session_id,
                        task_themes=task_themes,
                        task_keywords=task_description.lower().split()[:5]
                    )
                    
                    if success_patterns:
                        for flow_id in flows_by_id:
                            if flow_id in success_patterns.get("successful_flows", []):
                                flows_by_id[flow_id]["relevance_score"] += 1.0
                                
                except Exception as e:
                    logger.debug(f"Could not get historical success patterns: {e}")
            
            # Flow status boost (prioritize in-progress flows)
            for flow_id in flows_by_id:
                try:
                    flow_status = await self.theme_flow_queries.get_flow_status(flow_id)
                    if flow_status:
                        status = flow_status.get("status", "")
                        if status == "in-progress":
                            flows_by_id[flow_id]["relevance_score"] += 0.8
                        elif status == "needs-review":
                            flows_by_id[flow_id]["relevance_score"] += 0.5
                        
                        # Completion percentage factor
                        completion = flow_status.get("completion_percentage", 0)
                        if 20 <= completion < 80:  # Partially complete flows are more relevant
                            flows_by_id[flow_id]["relevance_score"] += 0.3
                            
                except Exception as e:
                    logger.debug(f"Could not get flow status for {flow_id}: {e}")
            
            # Sort by relevance score and select top flows
            sorted_flows = sorted(flows_by_id.values(), key=lambda x: x["relevance_score"], reverse=True)
            selected_flows = sorted_flows[:max_flows]
            
        except Exception as e:
            logger.error(f"Error in database-intelligent flow selection: {e}")
        
        return selected_flows
    
    async def _analyze_cross_flow_dependencies_for_context(self, flow_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze cross-flow dependencies for context loading optimization."""
        dependencies = []
        
        try:
            if self.theme_flow_queries:
                for flow_id in flow_ids:
                    flow_dependencies = await self.theme_flow_queries.get_cross_flow_dependencies(flow_id)
                    
                    for dep in flow_dependencies:
                        if dep.get("to_flow") in flow_ids:  # Dependency within our loaded set
                            dependencies.append({
                                "from_flow": flow_id,
                                "to_flow": dep["to_flow"],
                                "dependency_type": dep.get("dependency_type", "requires"),
                                "description": dep.get("description", ""),
                                "impact": "context_loading"
                            })
        
        except Exception as e:
            logger.debug(f"Error analyzing cross-flow dependencies: {e}")
        
        return dependencies
    
    async def optimize_multi_flow_context_loading(self, project_path: Path,
                                                task_data: Dict[str, Any],
                                                session_id: Optional[str] = None) -> Dict[str, Any]:
        """Optimize context loading strategy for multi-flow scenarios."""
        optimization_result = {
            "strategy": "adaptive",
            "recommended_flows": [],
            "context_mode": "theme-focused",
            "loading_order": [],
            "performance_estimate": {},
            "recommendations": []
        }
        
        try:
            # Extract task information
            primary_theme = task_data.get("primaryTheme", "general")
            task_description = task_data.get("description", "")
            subtasks = task_data.get("subtasks", [])
            
            # Determine complexity level
            complexity_score = 0
            if len(subtasks) > 3:
                complexity_score += 2
            if len(task_description.split()) > 20:
                complexity_score += 1
            if any(keyword in task_description.lower() for keyword in 
                   ["integration", "system", "architecture", "database", "api"]):
                complexity_score += 2
            
            # Adjust strategy based on complexity
            if complexity_score >= 4:
                optimization_result["strategy"] = "comprehensive"
                optimization_result["context_mode"] = "project-wide"
                max_flows = 8
            elif complexity_score >= 2:
                optimization_result["strategy"] = "expanded"
                optimization_result["context_mode"] = "theme-expanded"
                max_flows = 5
            else:
                optimization_result["strategy"] = "focused"
                optimization_result["context_mode"] = "theme-focused"
                max_flows = 3
            
            # Get all relevant themes
            all_themes = {primary_theme}
            for subtask in subtasks:
                flow_refs = subtask.get("flowReferences", [])
                for flow_ref in flow_refs:
                    # Extract theme from flow reference if available
                    if self.theme_flow_queries:
                        flow_themes = await self.theme_flow_queries.get_themes_for_flow(
                            flow_ref.get("flowId", "")
                        )
                        for theme_info in flow_themes:
                            all_themes.add(theme_info["theme_name"])
            
            # Select flows with database intelligence
            selected_flows = await self._select_flows_with_database_intelligence(
                list(all_themes), task_description, max_flows, session_id
            )
            
            optimization_result["recommended_flows"] = selected_flows
            
            # Analyze dependencies and determine loading order
            if len(selected_flows) > 1:
                flow_ids = [f["flow_id"] for f in selected_flows]
                dependencies = await self._analyze_cross_flow_dependencies_for_context(flow_ids)
                
                if dependencies:
                    # Generate optimal loading order
                    loading_order = await self._generate_dependency_aware_loading_order(
                        flow_ids, dependencies
                    )
                    optimization_result["loading_order"] = loading_order
                    optimization_result["recommendations"].append(
                        f"Dependency-aware loading order recommended: {' → '.join(loading_order)}"
                    )
            
            # Performance estimation
            total_estimated_memory = len(selected_flows) * 100  # KB per flow
            estimated_loading_time = len(selected_flows) * 50  # ms per flow
            
            optimization_result["performance_estimate"] = {
                "memory_kb": total_estimated_memory,
                "loading_time_ms": estimated_loading_time,
                "context_switch_cost": "low" if len(selected_flows) <= 3 else "moderate"
            }
            
            # Generate optimization recommendations
            if total_estimated_memory > 800:  # > 800KB
                optimization_result["recommendations"].append(
                    "Consider reducing flow count for memory optimization"
                )
            
            if len(all_themes) > len(selected_flows):
                missing_theme_count = len(all_themes) - len(set(
                    theme for flow in selected_flows
                    for theme in flow.get("primary_themes", [])
                ))
                if missing_theme_count > 0:
                    optimization_result["recommendations"].append(
                        f"Consider additional flows to cover {missing_theme_count} themes"
                    )
            
            # Historical success pattern recommendations
            if session_id and self.session_queries:
                try:
                    similar_optimizations = await self.session_queries.get_similar_optimization_patterns(
                        session_id=session_id,
                        complexity_score=complexity_score,
                        theme_count=len(all_themes)
                    )
                    
                    if similar_optimizations:
                        optimization_result["recommendations"].append(
                            f"Based on similar tasks: {similar_optimizations.get('recommendation', 'N/A')}"
                        )
                        
                except Exception as e:
                    logger.debug(f"Could not get historical optimization patterns: {e}")
            
        except Exception as e:
            logger.error(f"Error optimizing multi-flow context loading: {e}")
            optimization_result["error"] = str(e)
        
        return optimization_result
    
    async def _generate_dependency_aware_loading_order(self, flow_ids: List[str],
                                                     dependencies: List[Dict[str, Any]]) -> List[str]:
        """Generate loading order that respects cross-flow dependencies."""
        # Simple topological sort for dependency resolution
        in_degree = {flow_id: 0 for flow_id in flow_ids}
        
        # Calculate in-degrees
        for dep in dependencies:
            if dep["to_flow"] in in_degree:
                in_degree[dep["to_flow"]] += 1
        
        # Topological sort
        queue = [flow_id for flow_id, degree in in_degree.items() if degree == 0]
        loading_order = []
        
        while queue:
            flow_id = queue.pop(0)
            loading_order.append(flow_id)
            
            # Update in-degrees
            for dep in dependencies:
                if dep["from_flow"] == flow_id and dep["to_flow"] in in_degree:
                    in_degree[dep["to_flow"]] -= 1
                    if in_degree[dep["to_flow"]] == 0:
                        queue.append(dep["to_flow"])
        
        return loading_order