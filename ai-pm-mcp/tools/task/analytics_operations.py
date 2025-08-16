"""
Analytics and limits operations for the AI Project Manager.

Handles task analytics and sidequest limit checking.
"""

import json
import logging
from typing import Dict, Any, Optional

from ...database.task_status_queries import TaskStatusQueries

logger = logging.getLogger(__name__)


class AnalyticsOperations:
    """Task analytics and limits operations."""
    
    def __init__(self, task_queries: Optional[TaskStatusQueries] = None):
        self.task_queries = task_queries

    async def get_task_analytics(self, arguments: Dict[str, Any]) -> str:
        """Get task completion analytics and metrics."""
        try:
            project_path = arguments["project_path"]
            days = arguments.get("days", 30)
            theme_filter = arguments.get("theme_filter")
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Get analytics from database
            analytics = await self.task_queries.get_task_analytics(days, theme_filter)
            
            return f"Task analytics for {project_path} (last {days} days):\n\n{json.dumps(analytics, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error getting task analytics: {e}")
            return f"Error getting task analytics: {str(e)}"

    async def check_sidequest_limits(self, arguments: Dict[str, Any]) -> str:
        """Check sidequest limits for a task."""
        try:
            task_id = arguments["task_id"]
            
            if not self.task_queries:
                return "Database not available. Task management requires database connection."
            
            # Check limits
            limit_check = await self.task_queries.check_sidequest_limits(task_id)
            
            status_message = f"Sidequest limits for task {task_id}:\n\n"
            status_message += f"Active sidequests: {limit_check['active_count']}\n"
            status_message += f"Maximum allowed: {limit_check['limit']}\n"
            status_message += f"Warning threshold: {limit_check['warning_threshold']}\n"
            status_message += f"Can create new: {limit_check['can_create']}\n"
            
            if not limit_check['can_create']:
                status_message += f"Reason: {limit_check['reason']}\n"
            elif limit_check['active_count'] >= limit_check['warning_threshold']:
                status_message += "Warning: Approaching sidequest limit\n"
            
            return status_message
            
        except Exception as e:
            logger.error(f"Error checking sidequest limits: {e}")
            return f"Error checking sidequest limits: {str(e)}"