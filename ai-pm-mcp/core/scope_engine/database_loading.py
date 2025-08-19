"""
Database Loading Module
Handles database optimization and metadata loading for context operations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from .compressed_context import ContextMode, ContextResult

logger = logging.getLogger(__name__)


class DatabaseLoading:
    """Database optimization and metadata loading operations."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties directly
        self.theme_flow_queries = parent_instance.theme_flow_queries
        self.session_queries = parent_instance.session_queries
        self.file_metadata_queries = parent_instance.file_metadata_queries
    
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
    
    # Database-Enhanced Context Loading Methods
    
    async def load_context_with_database_optimization(self, project_path: Path, primary_theme: str,
                                                    context_mode: ContextMode = ContextMode.THEME_FOCUSED,
                                                    task_id: Optional[str] = None,
                                                    session_id: Optional[str] = None) -> ContextResult:
        """Load context with database optimization for theme-flow relationships and session tracking."""
        try:
            # Load context using existing method first
            context = await self.parent.load_context(project_path, primary_theme, context_mode)
            
            # Enhance with database information if available
            if self.theme_flow_queries:
                await self.parent._enhance_context_with_flows(context, primary_theme)
            
            if self.session_queries and session_id:
                await self._track_context_usage(session_id, context, task_id)
            
            if self.file_metadata_queries:
                await self._enhance_context_with_file_intelligence(project_path, context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error loading context with database optimization: {e}")
            # Fallback to regular context loading
            return await self.parent.load_context(project_path, primary_theme, context_mode)
    
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
            current_files = len(current_context.files)
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
    