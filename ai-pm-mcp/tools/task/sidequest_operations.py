"""
Sidequest operations for the AI Project Manager.

Handles sidequest creation, status updates, and listing operations.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ...database.task_status_queries import TaskStatusQueries
from ...database.file_metadata_queries import FileMetadataQueries

logger = logging.getLogger(__name__)


class SidequestOperations:
    """Sidequest management operations."""
    
    def __init__(self, task_queries: Optional[TaskStatusQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None):
        self.task_queries = task_queries
        self.file_metadata_queries = file_metadata_queries

    async def create_sidequest(self, arguments: Dict[str, Any]) -> str:
        """Create a new sidequest from a parent task."""
        try:
            parent_task_id = arguments["parent_task_id"]
            title = arguments["title"]
            description = arguments["description"]
            reason = arguments["reason"]
            urgency = arguments.get("urgency", "medium")
            impact_on_parent = arguments.get("impact_on_parent", "minimal")
            estimated_effort = arguments.get("estimated_effort")
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Check sidequest limits
            limit_check = await self.task_queries.check_sidequest_limits(parent_task_id)
            if not limit_check["can_create"]:
                return f"Cannot create sidequest: {limit_check['reason']}. Current active sidequests: {limit_check['active_count']}, Limit: {limit_check['limit']}"
            
            # Generate sidequest ID
            sidequest_id = f"SQ-{parent_task_id.split('-', 1)[1]}-{datetime.now(timezone.utc).strftime('%H%M%S')}"
            
            # Create sidequest in database
            await self.task_queries.create_sidequest(
                sidequest_id=sidequest_id,
                parent_task_id=parent_task_id,
                title=title,
                description=description,
                reason=reason,
                urgency=urgency,
                impact_on_parent=impact_on_parent,
                estimated_effort=estimated_effort
            )
            
            # Log sidequest creation
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=f"Tasks/sidequests/{sidequest_id}.json",
                    file_type="sidequest",
                    operation="create",
                    details={
                        "sidequest_id": sidequest_id,
                        "parent_task_id": parent_task_id,
                        "title": title,
                        "reason": reason
                    }
                )
            
            return f"Sidequest '{title}' created successfully with ID: {sidequest_id}. Warning threshold: {limit_check['warning_threshold']}, Current count: {limit_check['active_count'] + 1}"
            
        except Exception as e:
            logger.error(f"Error creating sidequest: {e}")
            return f"Error creating sidequest: {str(e)}"

    async def update_sidequest_status(self, arguments: Dict[str, Any]) -> str:
        """Update sidequest status and progress."""
        try:
            sidequest_id = arguments["sidequest_id"]
            status = arguments["status"]
            progress_percentage = arguments.get("progress_percentage")
            completion_trigger = arguments.get("completion_trigger")
            notes = arguments.get("notes", [])
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Update sidequest in database
            await self.task_queries.update_sidequest_status(
                sidequest_id=sidequest_id,
                status=status,
                progress_percentage=progress_percentage,
                completion_trigger=completion_trigger,
                notes=notes
            )
            
            # Log sidequest update
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=f"sidequest:{sidequest_id}",
                    file_type="sidequest",
                    operation="update",
                    details={
                        "status": status,
                        "progress_percentage": progress_percentage,
                        "notes_count": len(notes)
                    }
                )
            
            return f"Sidequest {sidequest_id} updated to status: {status}" + (f" ({progress_percentage}% complete)" if progress_percentage is not None else "")
            
        except Exception as e:
            logger.error(f"Error updating sidequest status: {e}")
            return f"Error updating sidequest status: {str(e)}"

    async def list_active_sidequests(self, arguments: Dict[str, Any]) -> str:
        """List active sidequests for a task or project."""
        try:
            parent_task_id = arguments.get("parent_task_id")
            project_path = arguments.get("project_path")
            status_filter = arguments.get("status_filter", ["pending", "in-progress"])
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            if parent_task_id:
                # Get sidequests for specific task
                sidequests = await self.task_queries.get_sidequests_for_task(parent_task_id, status_filter)
                title_prefix = f"Active sidequests for task {parent_task_id}"
            elif project_path:
                # Get all sidequests for project
                sidequests = await self.task_queries.get_all_sidequests(status_filter)
                title_prefix = f"Active sidequests for project {project_path}"
            else:
                return "Either parent_task_id or project_path must be provided."
            
            if not sidequests:
                return f"No active sidequests found."
            
            sidequest_list = []
            for sidequest in sidequests:
                sidequest_summary = {
                    "sidequest_id": sidequest["sidequest_id"],
                    "parent_task_id": sidequest["parent_task_id"],
                    "title": sidequest["title"],
                    "status": sidequest["status"],
                    "urgency": sidequest["urgency"],
                    "impact_on_parent": sidequest["impact_on_parent"],
                    "progress_percentage": sidequest["progress_percentage"],
                    "created_at": sidequest["created_at"],
                    "last_updated": sidequest["last_updated"]
                }
                sidequest_list.append(sidequest_summary)
            
            return f"{title_prefix}:\n\n{json.dumps(sidequest_list, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error listing active sidequests: {e}")
            return f"Error listing active sidequests: {str(e)}"