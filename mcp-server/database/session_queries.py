"""
Enhanced Session Management Database Queries
Handles session persistence, context snapshots, and boot sequence optimization for AI Project Manager.

Follows the exact schema structure defined in mcp-server/database/schema.sql
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from .db_manager import DatabaseManager

class SessionQueries:
    """
    Enhanced session management with comprehensive database operations.
    
    Key Features:
    - Session persistence across disconnections
    - Context snapshots for seamless resumption
    - Boot sequence optimization with quick context restoration
    - Session analytics and performance tracking
    - Multiple sidequest coordination with context preservation
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
    
    def start_session(self, project_path: str, context_mode: str = "theme-focused", 
                     active_themes: List[str] = None, active_tasks: List[str] = None,
                     active_sidequests: List[str] = None, metadata: Dict[str, Any] = None,
                     context: Dict[str, Any] = None) -> str:
        """
        Start a new AI session with context preservation.
        
        Args:
            project_path: Path to the project
            context_mode: Context mode (theme-focused, theme-expanded, project-wide)
            active_themes: List of active theme names
            active_tasks: List of active task IDs
            active_sidequests: List of active sidequest IDs
            metadata: Additional session metadata
            
        Returns:
            Generated session ID
        """
        # Generate unique session ID with microseconds and UUID to prevent collisions
        import uuid
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        session_id = f"session_{timestamp}_{uuid.uuid4().hex[:8]}"
        
        # Merge context into metadata if provided
        if context:
            metadata = metadata or {}
            metadata.update({"context": context})
        
        try:
            self.db.execute_insert(
                """
                INSERT INTO sessions (
                    session_id, project_path, context_mode, active_themes, 
                    active_tasks, active_sidequests, metadata, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
                """,
                (
                    session_id,
                    project_path,
                    context_mode,
                    json.dumps(active_themes or []),
                    json.dumps(active_tasks or []),
                    json.dumps(active_sidequests or []),
                    json.dumps(metadata or {})
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
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Alias for get_session for test compatibility.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Session information dictionary or None
        """
        return self.get_session(session_id)
    
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
    
    # Enhanced Session Management Methods (following database implementation plan)
    
    def get_latest_session(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent session for a project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Session data dictionary or None
        """
        query = """
            SELECT * FROM sessions 
            WHERE project_path = ? 
            ORDER BY start_time DESC 
            LIMIT 1
        """
        
        result = self.db.execute_query(query, (project_path,))
        if result:
            row = result[0]
            return self._session_row_to_dict(row)
        return None
    
    def _session_row_to_dict(self, row) -> Dict[str, Any]:
        """Convert session database row to dictionary."""
        return {
            "session_id": row["session_id"],
            "start_time": row["start_time"],
            "last_activity": row["last_activity"],
            "context_mode": row["context_mode"],
            "active_themes": json.loads(row["active_themes"]) if row["active_themes"] else [],
            "active_tasks": json.loads(row["active_tasks"]) if row["active_tasks"] else [],
            "active_sidequests": json.loads(row["active_sidequests"]) if row["active_sidequests"] else [],
            "project_path": row["project_path"],
            "status": row["status"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            "notes": row["notes"]
        }
    
    def end_session(self, session_id: str, notes: Optional[str] = None):
        """
        End a session and mark it as completed.
        
        Args:
            session_id: Session ID to end
            notes: Optional session completion notes
        """
        query = """
            UPDATE sessions 
            SET status = 'completed', notes = ?
            WHERE session_id = ?
        """
        self.db.execute_update(query, (notes, session_id))
    
    # Session Context Management
    
    def save_session_context(
        self,
        session_id: str,
        loaded_themes: List[str],
        loaded_flows: List[str],
        files_accessed: List[str],
        context_escalations: int = 0
    ):
        """
        Save session context for quick restoration.
        
        Args:
            session_id: Session ID
            loaded_themes: List of loaded theme names
            loaded_flows: List of loaded flow file names
            files_accessed: List of accessed file paths
            context_escalations: Number of context escalations
        """
        query = """
            INSERT OR REPLACE INTO session_context (
                session_id, loaded_themes, loaded_flows, 
                context_escalations, files_accessed
            ) VALUES (?, ?, ?, ?, ?)
        """
        
        params = (
            session_id,
            ",".join(loaded_themes) if loaded_themes else "",
            ",".join(loaded_flows) if loaded_flows else "",
            context_escalations,
            json.dumps(files_accessed)
        )
        
        self.db.execute_update(query, params)
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session context for restoration.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session context dictionary or None
        """
        query = """
            SELECT * FROM session_context 
            WHERE session_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        result = self.db.execute_query(query, (session_id,))
        if result:
            row = result[0]
            return {
                "session_id": row["session_id"],
                "loaded_themes": row["loaded_themes"].split(",") if row["loaded_themes"] else [],
                "loaded_flows": row["loaded_flows"].split(",") if row["loaded_flows"] else [],
                "context_escalations": row["context_escalations"],
                "files_accessed": json.loads(row["files_accessed"]),
                "created_at": row["created_at"]
            }
        return None
    
    # Context Snapshots for Task Switching (using task_queue table)
    
    def save_context_snapshot(
        self,
        session_id: str,
        task_id: Optional[str] = None,
        sidequest_id: Optional[str] = None,
        context_data: Dict[str, Any] = None,
        queue_position: int = 0
    ) -> int:
        """
        Save a context snapshot for seamless task switching.
        
        Args:
            session_id: Current session ID
            task_id: Task being paused/switched from (optional)
            sidequest_id: Sidequest being managed (optional)
            context_data: Complete context state
            queue_position: Position in task queue
            
        Returns:
            Queue entry ID
        """
        query = """
            INSERT INTO task_queue (
                task_id, sidequest_id, queue_position, status, 
                context_snapshot, session_id, paused_at
            ) VALUES (?, ?, ?, 'paused', ?, ?, CURRENT_TIMESTAMP)
        """
        
        return self.db.execute_insert(query, (
            task_id, sidequest_id, queue_position, 
            json.dumps(context_data or {}), session_id
        ))
    
    def get_context_snapshot(self, task_id: Optional[str] = None, sidequest_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get context snapshot for task/sidequest resumption.
        
        Args:
            task_id: Task ID to resume (optional)
            sidequest_id: Sidequest ID to resume (optional)
            
        Returns:
            Context snapshot data or None
        """
        if task_id:
            query = """
                SELECT context_snapshot FROM task_queue 
                WHERE task_id = ? AND status = 'paused'
                ORDER BY paused_at DESC 
                LIMIT 1
            """
            params = (task_id,)
        elif sidequest_id:
            query = """
                SELECT context_snapshot FROM task_queue 
                WHERE sidequest_id = ? AND status = 'paused'
                ORDER BY paused_at DESC 
                LIMIT 1
            """
            params = (sidequest_id,)
        else:
            return None
        
        result = self.db.execute_query(query, params)
        if result:
            return json.loads(result[0]["context_snapshot"])
        return None
    
    def clear_context_snapshot(self, task_id: Optional[str] = None, sidequest_id: Optional[str] = None):
        """Clear context snapshot when task/sidequest is resumed."""
        if task_id:
            query = "DELETE FROM task_queue WHERE task_id = ? AND status = 'paused'"
            self.db.execute_update(query, (task_id,))
        elif sidequest_id:
            query = "DELETE FROM task_queue WHERE sidequest_id = ? AND status = 'paused'"
            self.db.execute_update(query, (sidequest_id,))
    
    # Boot Sequence Optimization
    
    def get_boot_context(self, project_path: str) -> Dict[str, Any]:
        """
        Get optimized context for session boot sequence.
        
        Args:
            project_path: Project path
            
        Returns:
            Boot context with session restoration data
        """
        latest_session = self.get_latest_session(project_path)
        boot_context = {
            "has_previous_session": latest_session is not None,
            "recommended_context_mode": "theme-focused",
            "suggested_themes": [],
            "active_tasks": [],
            "active_sidequests": [],
            "session_continuity": False
        }
        
        if latest_session:
            # Check if session was recently active (within last 24 hours)
            last_activity = datetime.fromisoformat(latest_session["last_activity"])
            hours_since_activity = (datetime.now() - last_activity).total_seconds() / 3600
            
            if hours_since_activity < 24 and latest_session["status"] == "active":
                boot_context.update({
                    "session_continuity": True,
                    "previous_session_id": latest_session["session_id"],
                    "recommended_context_mode": latest_session["context_mode"],
                    "suggested_themes": latest_session["active_themes"],
                    "active_tasks": latest_session["active_tasks"],
                    "active_sidequests": latest_session["active_sidequests"],
                    "hours_since_last_activity": round(hours_since_activity, 1)
                })
            else:
                # Analyze recent sessions for patterns
                analytics = self.get_session_analytics_enhanced(project_path, days=7)
                if analytics.get("most_used_themes"):
                    boot_context["suggested_themes"] = [theme for theme, _ in analytics["most_used_themes"][:3]]
                if analytics.get("context_mode_usage"):
                    most_used_mode = max(analytics["context_mode_usage"], key=analytics["context_mode_usage"].get)
                    boot_context["recommended_context_mode"] = most_used_mode
        
        return boot_context
    
    def get_session_analytics_enhanced(self, project_path: str, days: int = 30) -> Dict[str, Any]:
        """
        Get enhanced session analytics for a project.
        
        Args:
            project_path: Project path
            days: Number of days to analyze
            
        Returns:
            Analytics dictionary
        """
        base_query = """
            FROM sessions 
            WHERE project_path = ? 
            AND start_time >= datetime('now', '-{} days')
        """.format(days)
        
        # Total sessions
        total_query = f"SELECT COUNT(*) as count {base_query}"
        total_sessions = self.db.execute_query(total_query, (project_path,))[0]["count"]
        
        # Average session duration using the view
        duration_query = f"""
            SELECT AVG(duration_hours) as avg_duration_hours 
            FROM session_activity_summary 
            WHERE start_time >= datetime('now', '-{days} days')
        """
        try:
            result = self.db.execute_query(duration_query)
            avg_duration = result[0]["avg_duration_hours"] if result else 0
        except:
            avg_duration = 0
        
        # Context mode usage
        mode_query = f"""
            SELECT context_mode, COUNT(*) as count {base_query}
            GROUP BY context_mode
        """
        mode_usage = {row["context_mode"]: row["count"] 
                     for row in self.db.execute_query(mode_query, (project_path,))}
        
        # Most used themes
        themes_query = f"""
            SELECT active_themes {base_query}
            AND active_themes != '[]'
        """
        all_themes = []
        for row in self.db.execute_query(themes_query, (project_path,)):
            themes = json.loads(row["active_themes"] or "[]")
            all_themes.extend(themes)
        
        # Count theme usage
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "avg_duration_hours": round(avg_duration or 0, 2),
            "context_mode_usage": mode_usage,
            "most_used_themes": sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "analysis_period_days": days
        }
    
    def update_active_themes(self, session_id: str, active_themes: List[str]):
        """Update active themes for a session."""
        query = "UPDATE sessions SET active_themes = ? WHERE session_id = ?"
        self.db.execute_update(query, (json.dumps(active_themes), session_id))
    
    def update_active_tasks(self, session_id: str, active_tasks: List[str]):
        """Update active tasks for a session."""
        query = "UPDATE sessions SET active_tasks = ? WHERE session_id = ?"
        self.db.execute_update(query, (json.dumps(active_tasks), session_id))
    
    def update_active_sidequests(self, session_id: str, active_sidequests: List[str]):
        """Update active sidequests for a session."""
        query = "UPDATE sessions SET active_sidequests = ? WHERE session_id = ?"
        self.db.execute_update(query, (json.dumps(active_sidequests), session_id))