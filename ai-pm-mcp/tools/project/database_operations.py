"""
Project database operations.

Handles database initialization, file metadata, and database-related operations.
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_operations import BaseProjectOperations
from ...database.session_queries import SessionQueries
from ...database.task_status_queries import TaskStatusQueries
from ...database.theme_flow_queries import ThemeFlowQueries
from ...database.file_metadata_queries import FileMetadataQueries
from ...database.event_queries import EventQueries

logger = logging.getLogger(__name__)


class ProjectDatabaseOperations(BaseProjectOperations):
    """Handles database initialization and metadata operations."""
    
    def __init__(self, db_manager=None, config_manager=None, directive_processor=None, **kwargs):
        super().__init__(db_manager, config_manager, directive_processor)
        self.session_queries = SessionQueries(db_manager) if db_manager else None
        self.task_queries = TaskStatusQueries(db_manager) if db_manager else None
        self.theme_flow_queries = ThemeFlowQueries(db_manager) if db_manager else None
        self.file_metadata_queries = FileMetadataQueries(db_manager) if db_manager else None
        self.event_queries = EventQueries(db_manager) if db_manager else None
    
    async def initialize_database(self, project_path: Path) -> str:
        """Initialize database for an existing project."""
        try:
            if not self.db_manager:
                return "Database manager not available."
            
            result = await self._initialize_database(project_path)
            return result
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return f"Error initializing database: {str(e)}"
    
    async def resume_file_metadata_initialization(self, project_path: Path, 
                                                project_name: Optional[str] = None) -> str:
        """Resume file metadata initialization for a project."""
        try:
            project_path = Path(project_path)
            
            if not project_name:
                # Try to get project name from blueprint
                blueprint_data = self.load_blueprint(project_path)
                project_name = blueprint_data.get('project_name', 'Unknown Project') if blueprint_data else 'Unknown Project'
            
            if not self.db_manager:
                return "Database manager not available."
            
            if not self.file_metadata_queries:
                return "File metadata queries not available."
            
            # Check if database exists
            db_path = self.get_database_file_path(project_path)
            if not db_path.exists():
                return f"Database not found at {db_path}. Initialize database first."
            
            # Start file metadata initialization
            result = await self._initialize_file_metadata(project_path, project_name)
            return result
            
        except Exception as e:
            logger.error(f"Error resuming file metadata initialization: {e}")
            return f"Error resuming file metadata initialization: {str(e)}"
    
    async def get_initialization_progress(self, project_path: Path) -> str:
        """Get initialization progress for a project."""
        try:
            project_path = Path(project_path)
            
            if not self.file_metadata_queries:
                return "File metadata queries not available."
            
            # Check database existence
            db_path = self.get_database_file_path(project_path)
            if not db_path.exists():
                return f"Database not found at {db_path}. Project may not be initialized."
            
            # Get file metadata initialization progress
            try:
                progress = await self.file_metadata_queries.get_initialization_progress(str(project_path))
                
                result = f"Initialization Progress for {project_path}:\n\n"
                
                if progress:
                    result += f"Total files scanned: {progress.get('total_files', 0)}\n"
                    result += f"Files processed: {progress.get('processed_files', 0)}\n"
                    result += f"Files with metadata: {progress.get('files_with_metadata', 0)}\n"
                    result += f"Processing errors: {progress.get('error_count', 0)}\n"
                    
                    if progress.get('total_files', 0) > 0:
                        completion_rate = (progress.get('processed_files', 0) / progress['total_files']) * 100
                        result += f"Completion rate: {completion_rate:.1f}%\n"
                    
                    last_update = progress.get('last_updated')
                    if last_update:
                        result += f"Last updated: {last_update}\n"
                    
                    status = progress.get('status', 'unknown')
                    result += f"Status: {status}\n"
                    
                    if status == 'in_progress':
                        result += "\nFile metadata initialization is currently running."
                    elif status == 'completed':
                        result += "\nFile metadata initialization completed successfully."
                    elif status == 'error':
                        result += "\nFile metadata initialization encountered errors."
                    
                else:
                    result += "No initialization progress data found."
                    result += "\nFile metadata initialization may not have been started."
                    result += "\nUse resume_initialization to start the process."
                
                return result
                
            except Exception as e:
                return f"Error getting progress data: {str(e)}"
            
        except Exception as e:
            logger.error(f"Error getting initialization progress: {e}")
            return f"Error getting initialization progress: {str(e)}"
    
    async def _initialize_database(self, project_path: Path):
        """Initialize project database."""
        try:
            db_path = self.get_database_file_path(project_path)
            
            # Ensure database directory exists
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize database if it doesn't exist
            if not db_path.exists() or db_path.stat().st_size == 0:
                await self.db_manager.initialize_database(str(db_path))
                logger.info(f"Database initialized at {db_path}")
                return f"Database initialized successfully at {db_path}"
            else:
                # Ensure database is properly set up
                await self.db_manager.initialize_database(str(db_path))
                return f"Database already exists and verified at {db_path}"
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            return f"Database initialization failed: {str(e)}"
    
    async def _initialize_file_metadata(self, project_path: Path, project_name: str):
        """Initialize file metadata for the project."""
        try:
            if not self.file_metadata_queries:
                return "File metadata queries not available"
            
            # Start file metadata initialization in background
            asyncio.create_task(
                self._run_file_metadata_initialization(project_path, project_name)
            )
            
            return f"File metadata initialization started for {project_name}"
            
        except Exception as e:
            logger.error(f"File metadata initialization error: {e}")
            return f"File metadata initialization failed: {str(e)}"
    
    async def _run_file_metadata_initialization(self, project_path: Path, project_name: str):
        """Run file metadata initialization in background."""
        try:
            # Record start of initialization
            await self.file_metadata_queries.start_initialization(
                project_path=str(project_path),
                project_name=project_name
            )
            
            # Get all files in project (excluding the management directory)
            all_files = []
            project_mgmt_dir = self.get_project_management_dir(project_path)
            
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    # Skip files in project management directory
                    try:
                        file_path.relative_to(project_mgmt_dir)
                        continue  # Skip files in management directory
                    except ValueError:
                        pass  # File is not in management directory, include it
                    
                    # Skip hidden files and common non-source files
                    if not file_path.name.startswith('.') and file_path.suffix not in ['.pyc', '.pyo', '.pyd']:
                        all_files.append(file_path)
            
            # Process files in batches
            batch_size = 100
            for i in range(0, len(all_files), batch_size):
                batch = all_files[i:i+batch_size]
                
                for file_path in batch:
                    try:
                        # Get basic file metadata
                        stat = file_path.stat()
                        relative_path = str(file_path.relative_to(project_path))
                        
                        metadata = {
                            'file_path': relative_path,
                            'full_path': str(file_path),
                            'size_bytes': stat.st_size,
                            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'file_type': file_path.suffix.lower() if file_path.suffix else 'no_extension',
                            'is_source_code': file_path.suffix.lower() in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb']
                        }
                        
                        # Store file metadata
                        await self.file_metadata_queries.store_file_metadata(
                            project_path=str(project_path),
                            file_path=relative_path,
                            metadata=metadata
                        )
                        
                    except Exception as e:
                        logger.warning(f"Error processing file {file_path}: {e}")
                        await self.file_metadata_queries.log_processing_error(
                            project_path=str(project_path),
                            file_path=str(file_path),
                            error=str(e)
                        )
                
                # Update progress
                await self.file_metadata_queries.update_initialization_progress(
                    project_path=str(project_path),
                    processed_count=min(i + batch_size, len(all_files)),
                    total_count=len(all_files)
                )
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            # Mark initialization as complete
            await self.file_metadata_queries.complete_initialization(
                project_path=str(project_path)
            )
            
            logger.info(f"File metadata initialization completed for {project_path}")
            
        except Exception as e:
            logger.error(f"File metadata initialization background task error: {e}")
            if self.file_metadata_queries:
                await self.file_metadata_queries.mark_initialization_error(
                    project_path=str(project_path),
                    error=str(e)
                )