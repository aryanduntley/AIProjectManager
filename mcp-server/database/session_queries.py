"""
Session Tracking Queries for AI Project Manager
Handles all database operations related to session tracking and management.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from .db_manager import DatabaseManager

class SessionQueries:
    """Handles session tracking database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
    
    def start_session(self, context: str = "", active_themes: List[str] = None, 
                     active_tasks: List[str] = None, project_path: str = "") -> str:
        """
        Start a new session and return session ID.
        
        Args:
            context: Description of current session context
            active_themes: List of active theme names
            active_tasks: List of active task IDs
            project_path: Path to the project
            
        Returns:
            Generated session ID
        """
        session_id = f"SESSION-{datetime.now().strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}"
        
        try:
            self.db.execute_insert(
                """
                INSERT INTO sessions (session_id, context, active_themes, active_tasks, project_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    context,
                    json.dumps(active_themes or []),
                    json.dumps(active_tasks or []),
                    project_path
                )
            )
            
            self.db.logger.info(f"Started session: {session_id}")
            return session_id
            
        except Exception as e:
            self.db.logger.error(f"Error starting session: {e}")
            raise
    
    def update_session_activity(self, session_id: str, context: str = None, 
                              active_themes: List[str] = None, 
                              active_tasks: List[str] = None, notes: str = None) -> bool:
        """
        Update session activity and context.
        
        Args:
            session_id: The session identifier
            context: Updated context description
            active_themes: Updated list of active themes
            active_tasks: Updated list of active tasks
            notes: Additional notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            update_fields = []
            params = []
            
            if context is not None:
                update_fields.append("context = ?")
                params.append(context)
            
            if active_themes is not None:
                update_fields.append("active_themes = ?")
                params.append(json.dumps(active_themes))
            
            if active_tasks is not None:
                update_fields.append("active_tasks = ?")
                params.append(json.dumps(active_tasks))
            
            if notes is not None:
                update_fields.append("notes = ?")
                params.append(notes)
            
            if update_fields:
                # The trigger will automatically update last_activity
                params.append(session_id)
                query = f"UPDATE sessions SET {', '.join(update_fields)} WHERE session_id = ?"
                
                affected_rows = self.db.execute_update(query, tuple(params))
                return affected_rows > 0
            
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information by ID.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Session information dictionary or None
        """
        query = """
        SELECT session_id, start_time, last_activity, context, 
               active_themes, active_tasks, project_path, notes
        FROM sessions
        WHERE session_id = ?
        """
        results = self.db.execute_query(query, (session_id,))
        
        if results:
            row = results[0]
            return {
                'session_id': row['session_id'],
                'start_time': row['start_time'],
                'last_activity': row['last_activity'],
                'context': row['context'],
                'active_themes': json.loads(row['active_themes'] or '[]'),
                'active_tasks': json.loads(row['active_tasks'] or '[]'),
                'project_path': row['project_path'],
                'notes': row['notes']
            }
        
        return None
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session information dictionaries
        """
        query = """
        SELECT session_id, start_time, last_activity, context, 
               active_themes, active_tasks, project_path, notes
        FROM sessions
        ORDER BY start_time DESC
        LIMIT ?
        """
        results = self.db.execute_query(query, (limit,))
        
        return [
            {
                'session_id': row['session_id'],
                'start_time': row['start_time'],
                'last_activity': row['last_activity'],
                'context': row['context'],
                'active_themes': json.loads(row['active_themes'] or '[]'),
                'active_tasks': json.loads(row['active_tasks'] or '[]'),
                'project_path': row['project_path'],
                'notes': row['notes']
            }
            for row in results
        ]
    
    def get_session_activity_summary(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get session activity summary for recent days.
        
        Args:
            days: Number of days to include in summary
            
        Returns:
            List of session activity summaries
        """
        query = """
        SELECT session_id, start_time, last_activity, duration_hours, 
               context, active_themes, active_tasks
        FROM session_activity_summary
        WHERE start_time >= datetime('now', '-{} days')
        ORDER BY start_time DESC
        """.format(days)
        
        results = self.db.execute_query(query)
        
        return [
            {
                'session_id': row['session_id'],
                'start_time': row['start_time'],
                'last_activity': row['last_activity'],
                'duration_hours': row['duration_hours'],
                'context': row['context'],
                'active_themes': json.loads(row['active_themes'] or '[]'),
                'active_tasks': json.loads(row['active_tasks'] or '[]')
            }
            for row in results
        ]
    
    def log_file_modification(self, session_id: str, file_path: str, file_type: str, 
                            operation: str, details: Dict[str, Any] = None) -> bool:
        """
        Log a file modification event.
        
        Args:
            session_id: The session identifier
            file_path: Path to the modified file
            file_type: Type of file (theme, flow, task, etc.)
            operation: Operation performed (create, update, delete)
            details: Additional details as dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.execute_insert(
                """
                INSERT INTO file_modifications 
                (session_id, file_path, file_type, operation, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    file_path,
                    file_type,
                    operation,
                    json.dumps(details or {})
                )
            )
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error logging file modification: {e}")
            return False
    
    def get_file_modifications(self, session_id: str = None, file_type: str = None, 
                             days: int = 7) -> List[Dict[str, Any]]:
        """
        Get file modification history.
        
        Args:
            session_id: Optional session ID to filter by
            file_type: Optional file type to filter by
            days: Number of days to include
            
        Returns:
            List of file modification records
        """
        query = """
        SELECT session_id, file_path, file_type, operation, details, timestamp
        FROM file_modifications
        WHERE timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        params = []
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        
        if file_type:
            query += " AND file_type = ?"
            params.append(file_type)
        
        query += " ORDER BY timestamp DESC"
        
        results = self.db.execute_query(query, tuple(params))
        
        return [
            {
                'session_id': row['session_id'],
                'file_path': row['file_path'],
                'file_type': row['file_type'],
                'operation': row['operation'],
                'details': json.loads(row['details'] or '{}'),
                'timestamp': row['timestamp']
            }
            for row in results
        ]
    
    def record_task_completion(self, session_id: str, task_id: str, milestone_id: str = None,
                             theme_name: str = None, estimated_hours: float = None,
                             actual_hours: float = None, complexity_score: int = None,
                             notes: str = None) -> bool:
        """
        Record task completion metrics.
        
        Args:
            session_id: The session identifier
            task_id: The task identifier
            milestone_id: The milestone identifier
            theme_name: The theme name
            estimated_hours: Estimated effort in hours
            actual_hours: Actual effort in hours
            complexity_score: Complexity score (1-10)
            notes: Additional notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.execute_insert(
                """
                INSERT INTO task_metrics 
                (session_id, task_id, milestone_id, theme_name, estimated_effort_hours,
                 actual_effort_hours, complexity_score, notes, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    task_id,
                    milestone_id,
                    theme_name,
                    estimated_hours,
                    actual_hours,
                    complexity_score,
                    notes,
                    datetime.now().isoformat()
                )
            )
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error recording task completion: {e}")
            return False
    
    def get_task_metrics(self, theme_name: str = None, milestone_id: str = None,
                        days: int = 30) -> List[Dict[str, Any]]:
        """
        Get task completion metrics.
        
        Args:
            theme_name: Optional theme name to filter by
            milestone_id: Optional milestone ID to filter by
            days: Number of days to include
            
        Returns:
            List of task metrics
        """
        query = """
        SELECT task_id, milestone_id, theme_name, estimated_effort_hours,
               actual_effort_hours, complexity_score, notes, completed_at, session_id
        FROM task_metrics
        WHERE completed_at >= datetime('now', '-{} days')
        """.format(days)
        
        params = []
        
        if theme_name:
            query += " AND theme_name = ?"
            params.append(theme_name)
        
        if milestone_id:
            query += " AND milestone_id = ?"
            params.append(milestone_id)
        
        query += " ORDER BY completed_at DESC"
        
        results = self.db.execute_query(query, tuple(params))
        
        return [
            {
                'task_id': row['task_id'],
                'milestone_id': row['milestone_id'],
                'theme_name': row['theme_name'],
                'estimated_effort_hours': row['estimated_effort_hours'],
                'actual_effort_hours': row['actual_effort_hours'],
                'complexity_score': row['complexity_score'],
                'notes': row['notes'],
                'completed_at': row['completed_at'],
                'session_id': row['session_id']
            }
            for row in results
        ]
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get session statistics and analytics.
        
        Returns:
            Dictionary with session statistics
        """
        stats = {}
        
        # Total sessions
        total_sessions = self.db.execute_query("SELECT COUNT(*) as count FROM sessions")[0]['count']
        stats['total_sessions'] = total_sessions
        
        # Average session duration
        avg_duration = self.db.execute_query("""
            SELECT AVG(duration_hours) as avg_duration
            FROM session_activity_summary
        """)[0]['avg_duration']
        stats['average_session_duration_hours'] = round(avg_duration or 0, 2)
        
        # Most active themes
        active_themes = self.db.execute_query("""
            SELECT theme_name, COUNT(*) as usage_count
            FROM task_metrics
            WHERE completed_at >= datetime('now', '-30 days')
            GROUP BY theme_name
            ORDER BY usage_count DESC
            LIMIT 5
        """)
        stats['most_active_themes'] = [
            {'theme': row['theme_name'], 'usage_count': row['usage_count']}
            for row in active_themes
        ]
        
        # Recent activity
        recent_activity = self.db.execute_query("""
            SELECT COUNT(*) as count
            FROM sessions
            WHERE start_time >= datetime('now', '-7 days')
        """)[0]['count']
        stats['sessions_last_7_days'] = recent_activity
        
        return stats