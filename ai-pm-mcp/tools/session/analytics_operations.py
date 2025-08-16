"""
Session analytics operations for the AI Project Manager.

Handles session listing, analytics, and maintenance operations.
"""

import json
import logging
from typing import Dict, Any, Optional

from ...database.session_queries import SessionQueries

logger = logging.getLogger(__name__)


class AnalyticsOperations:
    """Session analytics and management operations."""
    
    def __init__(self, session_queries: Optional[SessionQueries] = None):
        self.session_queries = session_queries

    async def list_recent_sessions(self, arguments: Dict[str, Any]) -> str:
        """List recent sessions for a project."""
        try:
            project_path = arguments["project_path"]
            limit = arguments.get("limit", 10)
            
            if not self.session_queries:
                return "Database not available. Session management requires database connection."
            
            # Get recent sessions
            sessions = await self.session_queries.get_recent_sessions(project_path, limit)
            
            if not sessions:
                return f"No sessions found for project {project_path}"
            
            session_list = []
            for session in sessions:
                session_info = {
                    "session_id": session["session_id"],
                    "start_time": session["start_time"],
                    "last_activity": session["last_activity"],
                    "context_mode": session["context_mode"],
                    "active_themes": json.loads(session.get("active_themes", "[]")),
                    "active_tasks": json.loads(session.get("active_tasks", "[]"))
                }
                session_list.append(session_info)
            
            return f"Recent sessions for {project_path}:\n\n{json.dumps(session_list, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error listing recent sessions: {e}")
            return f"Error listing recent sessions: {str(e)}"

    async def get_session_analytics(self, arguments: Dict[str, Any]) -> str:
        """Get session analytics and metrics."""
        try:
            project_path = arguments["project_path"]
            days = arguments.get("days", 30)
            
            if not self.session_queries:
                return "Database not available. Session management requires database connection."
            
            # Get analytics
            analytics = await self.session_queries.get_session_analytics(project_path, days)
            
            return f"Session analytics for {project_path} (last {days} days):\n\n{json.dumps(analytics, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error getting session analytics: {e}")
            return f"Error getting session analytics: {str(e)}"

    async def archive_stale_periods(self, arguments: Dict[str, Any]) -> str:
        """Archive stale work periods with no recent activity."""
        try:
            hours_threshold = arguments.get("hours_threshold", 24)
            
            if not self.session_queries:
                return "Database not available. Work period management requires database connection."
            
            # Archive stale periods using the new method
            archived_count = self.session_queries.archive_stale_work_periods(hours_threshold)
            
            return f"Archived {archived_count} stale work periods (inactive for {hours_threshold}+ hours)"
            
        except Exception as e:
            logger.error(f"Error archiving stale periods: {e}")
            return f"Error archiving stale periods: {str(e)}"