"""
File operations for task management.

Handles task file creation, updates, and syncing with project structure.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ...database.task_status_queries import TaskStatusQueries
from ...database.session_queries import SessionQueries
from ...database.file_metadata_queries import FileMetadataQueries
from ...utils.project_paths import get_tasks_path

logger = logging.getLogger(__name__)


class FileOperations:
    """Task file management operations."""
    
    def __init__(self, task_queries: Optional[TaskStatusQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None,
                 config_manager=None,
                 session_queries: Optional[SessionQueries] = None):
        self.task_queries = task_queries
        self.file_metadata_queries = file_metadata_queries
        self.config_manager = config_manager
        self.session_queries = session_queries
        self.server_instance = None

    async def create_task_file(self, project_path: Path, task_id: str, task_data: Dict[str, Any]):
        """Create task file for compatibility."""
        tasks_dir = get_tasks_path(project_path, self.config_manager) / "active"
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        task_file = tasks_dir / f"{task_id}.json"
        task_file.write_text(json.dumps(task_data, indent=2))

    async def update_task_file_status(self, task_id: str, status: str, progress_percentage: Optional[int], notes: Optional[str]):
        """Update task file status with proper project context and database integration."""
        try:
            if not self.task_queries:
                logger.warning(f"Cannot update task file status for {task_id}: Database queries not available")
                return
            
            # Get task details from database to find associated project path
            task_details = self.task_queries.get_task_details(task_id)
            if not task_details:
                logger.error(f"Task {task_id} not found in database")
                return
            
            # Update database status first (primary source of truth)
            success = self.task_queries.update_task_status(
                task_id=task_id,
                status=status,
                progress_percentage=progress_percentage,
                notes=notes
            )
            
            if not success:
                logger.error(f"Failed to update database status for task {task_id}")
                return
            
            # Try to update associated project files if file metadata is available
            if self.file_metadata_queries:
                # Log the task status change for file tracking
                self.file_metadata_queries.log_file_modification(
                    file_path=f"task:{task_id}",  # Virtual file path for task tracking
                    file_type="task",
                    operation="status_update",
                    details={
                        "task_id": task_id,
                        "new_status": status,
                        "progress_percentage": progress_percentage,
                        "notes": notes,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                )
            
            # Update session context if available
            if self.session_queries:
                session_id = self.session_queries.get_current_session_id()
                if session_id:
                    # Log task status change in session
                    self.session_queries.log_session_event(
                        session_id=session_id,
                        event_type="task_status_update",
                        details={
                            "task_id": task_id,
                            "status": status,
                            "progress_percentage": progress_percentage
                        }
                    )
            
            # Attempt to sync with any physical task files in the project structure
            try:
                project_path = task_details.get('project_path')
                if project_path:
                    await self.sync_task_file_on_disk(project_path, task_id, status, progress_percentage, notes)
            except Exception as file_sync_error:
                logger.warning(f"Could not sync task file on disk for {task_id}: {file_sync_error}")
                # Don't fail the overall operation if file sync fails
                
            logger.info(f"Successfully updated task status: {task_id} -> {status}")
            
        except Exception as e:
            logger.error(f"Error updating task file status for {task_id}: {e}")
            raise

    async def sync_task_file_on_disk(self, project_path: str, task_id: str, status: str, 
                                   progress_percentage: Optional[int], notes: Optional[str]):
        """Sync task status to physical files in project structure."""
        try:
            project_root = Path(project_path)
            tasks_dir = get_tasks_path(project_root, self.config_manager)
            
            if not tasks_dir.exists():
                logger.debug(f"Tasks directory does not exist: {tasks_dir}")
                return
            
            # Look for task files that might contain this task
            task_files = list(tasks_dir.glob("*.json"))
            
            for task_file in task_files:
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    
                    # Check if this file contains our task
                    updated = False
                    
                    # Handle different task file structures
                    if isinstance(task_data, dict):
                        # Check if task_data has task arrays
                        for key in ['tasks', 'task_list', 'items']:
                            if key in task_data and isinstance(task_data[key], list):
                                for task in task_data[key]:
                                    if isinstance(task, dict) and task.get('id') == task_id:
                                        task['status'] = status
                                        if progress_percentage is not None:
                                            task['progress_percentage'] = progress_percentage
                                        if notes:
                                            task['notes'] = notes
                                        task['last_updated'] = datetime.now(timezone.utc).isoformat()
                                        updated = True
                                        break
                        
                        # Check if task_data itself is the task
                        if task_data.get('id') == task_id:
                            task_data['status'] = status
                            if progress_percentage is not None:
                                task_data['progress_percentage'] = progress_percentage
                            if notes:
                                task_data['notes'] = notes
                            task_data['last_updated'] = datetime.now(timezone.utc).isoformat()
                            updated = True
                    
                    elif isinstance(task_data, list):
                        # Task file is a direct list of tasks
                        for task in task_data:
                            if isinstance(task, dict) and task.get('id') == task_id:
                                task['status'] = status
                                if progress_percentage is not None:
                                    task['progress_percentage'] = progress_percentage
                                if notes:
                                    task['notes'] = notes
                                task['last_updated'] = datetime.now(timezone.utc).isoformat()
                                updated = True
                                break
                    
                    # Write back the updated file
                    if updated:
                        with open(task_file, 'w', encoding='utf-8') as f:
                            json.dump(task_data, f, indent=2, ensure_ascii=False)
                        logger.debug(f"Updated task {task_id} in file {task_file}")
                        return  # Successfully updated, no need to check other files
                        
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Could not read/write task file {task_file}: {e}")
                    continue
            
            logger.debug(f"Task {task_id} not found in any task files in {tasks_dir}")
            
        except Exception as e:
            logger.error(f"Error syncing task file on disk: {e}")
            # Don't re-raise - this is a nice-to-have feature