"""
Work Activity Tracking
Handles activity-based work tracking, context restoration, and work period analytics.
"""

import json
from datetime import datetime
from typing import Dict, Optional, Any
from ..db_manager import DatabaseManager


class WorkActivityTracker:
    """Manages activity-based work tracking and analytics."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def record_work_activity(
        self, 
        project_path: str,
        activity_type: str, 
        tool_name: str = None,
        activity_data: Dict[str, Any] = None,
        duration_ms: int = None,
        session_context_id: str = None
    ) -> bool:
        """
        Record a work activity (replaces session lifecycle tracking).
        
        Args:
            project_path: Project path for this activity
            activity_type: Type of activity (tool_call, theme_load, task_update, etc.)
            tool_name: Name of MCP tool that was called
            activity_data: JSON data with activity details
            duration_ms: How long the activity took in milliseconds
            session_context_id: Link to session for context restoration
            
        Returns:
            bool: True if successful
        """
        try:
            query = """
            INSERT INTO work_activities 
            (project_path, activity_type, tool_name, activity_data, duration_ms, session_context_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            activity_json = json.dumps(activity_data) if activity_data else None
            
            params = (
                project_path,
                activity_type, 
                tool_name,
                activity_json,
                duration_ms,
                session_context_id
            )
            
            self.db.execute_update(query, params)
            
            # Update last_tool_activity in sessions table if session_context_id provided
            if session_context_id:
                self.db.execute_update(
                    "UPDATE sessions SET last_tool_activity = ? WHERE session_id = ?",
                    (datetime.now().isoformat(), session_context_id,)
                )
            
            return True
            
        except Exception as e:
            print(f"Error recording work activity: {e}")
            return False
    
    def get_recent_work_context(self, project_path: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get recent work context based on session relevance and activity timeline.
        
        Args:
            project_path: Project path to get context for
            limit: Maximum number of activities to analyze
            
        Returns:
            Dict[str, Any]: Recent work context data
        """
        try:
            # Use relevance-based ordering prioritizing session context over time windows
            query = """
            SELECT wa.*, s.context_mode, s.active_themes, s.active_tasks, s.active_sidequests
            FROM work_activities wa
            LEFT JOIN sessions s ON wa.session_context_id = s.session_id
            WHERE wa.project_path = ?
            ORDER BY 
                CASE WHEN wa.session_context_id IS NOT NULL THEN 0 ELSE 1 END,
                wa.timestamp DESC
            LIMIT ?
            """
            
            result = self.db.execute_query(query, (project_path, limit))
            
            if not result:
                return {
                    "recent_activities": [],
                    "last_activity_time": None,
                    "session_context": None
                }
            
            activities = []
            latest_session_context = None
            
            for row in result:
                activity = {
                    "id": row[0],
                    "activity_type": row[2],
                    "tool_name": row[3],
                    "activity_data": json.loads(row[4]) if row[4] else {},
                    "timestamp": row[5],
                    "duration_ms": row[6]
                }
                activities.append(activity)
                
                # Capture session context from most recent activity
                if not latest_session_context and len(row) > 7:
                    latest_session_context = {
                        "context_mode": row[7],
                        "active_themes": json.loads(row[8]) if row[8] else [],
                        "active_tasks": json.loads(row[9]) if row[9] else [],
                        "active_sidequests": json.loads(row[10]) if row[10] else []
                    }
            
            return {
                "recent_activities": activities,
                "last_activity_time": activities[0]["timestamp"] if activities else None,
                "session_context": latest_session_context
            }
            
        except Exception as e:
            print(f"Error getting recent work context: {e}")
            return {
                "recent_activities": [],
                "last_activity_time": None,
                "session_context": None
            }
    
    def archive_stale_work_periods(self, keep_sessions: int = 20) -> int:
        """
        Archive old work periods, keeping only the most recent sessions per project.
        
        Args:
            keep_sessions: Number of most recent sessions to keep active per project
            
        Returns:
            int: Number of work periods archived
        """
        try:
            # Archive all but the most recent keep_sessions sessions per project
            query = """
            UPDATE sessions 
            SET archived_at = ?, archive_reason = 'maintenance_cleanup'
            WHERE session_id NOT IN (
                SELECT session_id 
                FROM sessions 
                WHERE project_path = sessions.project_path 
                AND archived_at IS NULL
                ORDER BY last_tool_activity DESC 
                LIMIT ?
            )
            AND archived_at IS NULL
            """
            
            current_time = datetime.now().isoformat()
            cursor = self.db.execute_update(query, (current_time, keep_sessions))
            
            return cursor.rowcount if hasattr(cursor, 'rowcount') else 0
            
        except Exception as e:
            print(f"Error archiving stale work periods: {e}")
            return 0
    
    def get_work_period_analytics(self, project_path: str, days: int = 30) -> Dict[str, Any]:
        """
        Get work activity analytics (replaces session analytics).
        
        Args:
            project_path: Project path to analyze
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Work period analytics
        """
        try:
            # Get activity summary
            activity_query = """
            SELECT 
                activity_type,
                COUNT(*) as count,
                AVG(duration_ms) as avg_duration,
                SUM(duration_ms) as total_duration
            FROM work_activities
            WHERE project_path = ? 
            AND timestamp >= datetime('now', '-{} days')
            GROUP BY activity_type
            ORDER BY count DESC
            """.format(days)
            
            activity_result = self.db.execute_query(activity_query, (project_path,))
            
            activity_summary = {}
            total_activities = 0
            total_time_ms = 0
            
            for row in activity_result:
                activity_type = row[0]
                count = row[1]
                avg_duration = row[2] or 0
                total_duration = row[3] or 0
                
                activity_summary[activity_type] = {
                    "count": count,
                    "avg_duration_ms": avg_duration,
                    "total_duration_ms": total_duration
                }
                
                total_activities += count
                total_time_ms += total_duration
            
            # Get work periods (sessions) summary
            session_query = """
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN archived_at IS NULL THEN 1 END) as active_sessions,
                AVG(CASE 
                    WHEN archived_at IS NOT NULL 
                    THEN (julianday(archived_at) - julianday(work_period_started)) * 24 * 60 * 60 * 1000
                    ELSE (julianday('now') - julianday(work_period_started)) * 24 * 60 * 60 * 1000
                END) as avg_session_duration_ms
            FROM sessions
            WHERE project_path = ?
            AND start_time >= datetime('now', '-{} days')
            """.format(days)
            
            session_result = self.db.execute_query(session_query, (project_path,))
            
            session_stats = {
                "total_sessions": 0,
                "active_sessions": 0,
                "avg_session_duration_ms": 0
            }
            
            if session_result:
                row = session_result[0]
                session_stats = {
                    "total_sessions": row[0] or 0,
                    "active_sessions": row[1] or 0,
                    "avg_session_duration_ms": row[2] or 0
                }
            
            return {
                "project_path": project_path,
                "analysis_period_days": days,
                "activity_summary": activity_summary,
                "total_activities": total_activities,
                "total_active_time_ms": total_time_ms,
                "session_stats": session_stats,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting work period analytics: {e}")
            return {
                "project_path": project_path,
                "analysis_period_days": days,
                "activity_summary": {},
                "total_activities": 0,
                "total_active_time_ms": 0,
                "session_stats": {
                    "total_sessions": 0,
                    "active_sessions": 0,
                    "avg_session_duration_ms": 0
                },
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }