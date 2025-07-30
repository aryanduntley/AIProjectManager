"""
Enhanced Session Management Database Queries
Handles session persistence, context snapshots, and boot sequence optimization for AI Project Manager.

Follows the exact schema structure defined in ai-pm-mcp/database/schema.sql
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
    
    def log_context_escalation(self, session_id: str, from_mode: str, to_mode: str, 
                              reason: str, task_id: str = None):
        """
        Log a context escalation event.
        
        Args:
            session_id: Session ID
            from_mode: Previous context mode
            to_mode: New context mode
            reason: Reason for escalation
            task_id: Related task ID if any
        """
        try:
            # Update session context mode
            self.db.execute_update(
                "UPDATE sessions SET context_mode = ? WHERE session_id = ?",
                (to_mode, session_id)
            )
            
            # Log the escalation event
            event_data = {
                'event_type': 'context_escalation',
                'title': f'Context escalated from {from_mode} to {to_mode}',
                'description': reason,
                'session_id': session_id,
                'task_id': task_id,
                'context_data': json.dumps({
                    'from_mode': from_mode,
                    'to_mode': to_mode,
                    'reason': reason
                })
            }
            
            # Simple event logging without complex event management
            self.db.logger.info(f"Context escalation: {from_mode} → {to_mode} (Reason: {reason})")
            
        except Exception as e:
            self.db.logger.error(f"Error logging context escalation: {e}")
    
    def get_session_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get session analytics for the specified number of days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Analytics dictionary
        """
        try:
            # Total sessions in period
            total_query = """
                SELECT COUNT(*) as count FROM sessions 
                WHERE start_time >= datetime('now', '-{} days')
            """.format(days)
            total_sessions = self.db.execute_query(total_query)[0]['count']
            
            # Average session duration
            duration_query = """
                SELECT AVG(ROUND((julianday(last_activity) - julianday(start_time)) * 24, 2)) as avg_duration 
                FROM sessions 
                WHERE start_time >= datetime('now', '-{} days')
            """.format(days)
            result = self.db.execute_query(duration_query)
            avg_duration = result[0]['avg_duration'] if result else 0
            
            # Context mode distribution
            mode_query = """
                SELECT context_mode, COUNT(*) as count FROM sessions 
                WHERE start_time >= datetime('now', '-{} days')
                GROUP BY context_mode
            """.format(days)
            mode_results = self.db.execute_query(mode_query)
            mode_distribution = {row['context_mode']: row['count'] for row in mode_results}
            
            return {
                'total_sessions': total_sessions,
                'avg_duration_hours': round(avg_duration or 0, 2),
                'context_mode_distribution': mode_distribution,
                'analysis_period_days': days
            }
            
        except Exception as e:
            self.db.logger.error(f"Error getting session analytics: {e}")
            return {
                'total_sessions': 0,
                'avg_duration_hours': 0,
                'context_mode_distribution': {},
                'analysis_period_days': days
            }
    
    # Initialization Tracking Methods (Phase 2 Implementation)
    
    def start_initialization(self, session_id: str, total_files_discovered: int) -> bool:
        """
        Start initialization phase for a session.
        
        Args:
            session_id: Session ID to update
            total_files_discovered: Total number of files discovered for initialization
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE sessions 
                SET initialization_phase = 'discovering_files',
                    total_files_discovered = ?,
                    files_processed = 0,
                    initialization_started_at = ?
                WHERE session_id = ?
            """
            
            self.db.execute_update(query, (total_files_discovered, datetime.now().isoformat(), session_id))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error starting initialization for session {session_id}: {e}")
            return False
    
    def update_initialization_phase(self, session_id: str, phase: str) -> bool:
        """
        Update the initialization phase for a session.
        
        Args:
            session_id: Session ID to update
            phase: New initialization phase (discovering_files, analyzing_themes, building_flows, complete)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE sessions 
                SET initialization_phase = ?
                WHERE session_id = ?
            """
            
            self.db.execute_update(query, (phase, session_id))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error updating initialization phase for session {session_id}: {e}")
            return False
    
    def complete_initialization(self, session_id: str) -> bool:
        """
        Mark initialization as complete for a session.
        
        Args:
            session_id: Session ID to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE sessions 
                SET initialization_phase = 'complete',
                    initialization_completed_at = ?
                WHERE session_id = ?
            """
            
            self.db.execute_update(query, (datetime.now().isoformat(), session_id))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error completing initialization for session {session_id}: {e}")
            return False
    
    def get_initialization_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get initialization status for a session.
        
        Args:
            session_id: Session ID to check
            
        Returns:
            Dictionary with initialization status or None if session not found
        """
        try:
            query = """
                SELECT initialization_phase, files_processed, total_files_discovered,
                       initialization_started_at, initialization_completed_at
                FROM sessions
                WHERE session_id = ?
            """
            
            results = self.db.execute_query(query, (session_id,))
            if results:
                row = results[0]
                
                # Calculate completion percentage
                total_files = row['total_files_discovered'] or 0
                processed_files = row['files_processed'] or 0
                completion_percentage = (processed_files / total_files * 100) if total_files > 0 else 0
                
                # Calculate elapsed time if initialization started
                elapsed_time = None
                if row['initialization_started_at']:
                    start_time = datetime.fromisoformat(row['initialization_started_at'])
                    if row['initialization_completed_at']:
                        end_time = datetime.fromisoformat(row['initialization_completed_at'])
                        elapsed_time = (end_time - start_time).total_seconds()
                    else:
                        elapsed_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    'session_id': session_id,
                    'initialization_phase': row['initialization_phase'],
                    'files_processed': processed_files,
                    'total_files_discovered': total_files,
                    'completion_percentage': round(completion_percentage, 2),
                    'initialization_started_at': row['initialization_started_at'],
                    'initialization_completed_at': row['initialization_completed_at'],
                    'elapsed_time_seconds': elapsed_time,
                    'is_complete': row['initialization_phase'] == 'complete'
                }
            return None
            
        except Exception as e:
            self.db.logger.error(f"Error getting initialization status for session {session_id}: {e}")
            return None
    
    def get_sessions_needing_initialization(self) -> List[Dict[str, Any]]:
        """
        Get sessions that need initialization or have incomplete initialization.
        
        Returns:
            List of sessions that need initialization work
        """
        try:
            query = """
                SELECT session_id, project_path, initialization_phase, 
                       files_processed, total_files_discovered, start_time
                FROM sessions
                WHERE initialization_phase IN ('not_started', 'discovering_files', 'analyzing_themes', 'building_flows')
                  AND status = 'active'
                ORDER BY start_time DESC
            """
            
            results = self.db.execute_query(query)
            sessions = []
            
            for row in results:
                # Calculate completion percentage
                total_files = row['total_files_discovered'] or 0
                processed_files = row['files_processed'] or 0
                completion_percentage = (processed_files / total_files * 100) if total_files > 0 else 0
                
                sessions.append({
                    'session_id': row['session_id'],
                    'project_path': row['project_path'],
                    'initialization_phase': row['initialization_phase'],
                    'files_processed': processed_files,
                    'total_files_discovered': total_files,
                    'completion_percentage': round(completion_percentage, 2),
                    'start_time': row['start_time']
                })
            
            return sessions
            
        except Exception as e:
            self.db.logger.error(f"Error getting sessions needing initialization: {e}")
            return []
    
    def increment_files_processed(self, session_id: str) -> bool:
        """
        Increment the files_processed counter for a session.
        This is typically called via database trigger, but can be called manually.
        
        Args:
            session_id: Session ID to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE sessions 
                SET files_processed = files_processed + 1,
                    last_activity = ?
                WHERE session_id = ?
            """
            
            self.db.execute_update(query, (datetime.now().isoformat(), session_id))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error incrementing files processed for session {session_id}: {e}")
            return False
    
    def reset_initialization(self, session_id: str) -> bool:
        """
        Reset initialization status for a session to start over.
        
        Args:
            session_id: Session ID to reset
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE sessions 
                SET initialization_phase = 'not_started',
                    files_processed = 0,
                    total_files_discovered = 0,
                    initialization_started_at = NULL,
                    initialization_completed_at = NULL
                WHERE session_id = ?
            """
            
            self.db.execute_update(query, (session_id,))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error resetting initialization for session {session_id}: {e}")
            return False
    
    def get_initialization_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get analytics about initialization performance across sessions.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with initialization analytics
        """
        try:
            # Sessions by initialization phase
            phase_query = """
                SELECT initialization_phase, COUNT(*) as count
                FROM sessions
                WHERE start_time >= datetime('now', '-{} days')
                GROUP BY initialization_phase
            """.format(days)
            
            phase_results = self.db.execute_query(phase_query)
            phase_distribution = {row['initialization_phase']: row['count'] for row in phase_results}
            
            # Average initialization time for completed sessions
            completion_time_query = """
                SELECT AVG(
                    (julianday(initialization_completed_at) - julianday(initialization_started_at)) * 24 * 60
                ) as avg_minutes
                FROM sessions
                WHERE initialization_phase = 'complete'
                  AND initialization_started_at IS NOT NULL
                  AND initialization_completed_at IS NOT NULL
                  AND start_time >= datetime('now', '-{} days')
            """.format(days)
            
            time_result = self.db.execute_query(completion_time_query)
            avg_completion_time = time_result[0]['avg_minutes'] if time_result else 0
            
            # Average files processed per completed initialization
            files_query = """
                SELECT AVG(CAST(total_files_discovered AS FLOAT)) as avg_files,
                       AVG(CAST(files_processed AS FLOAT)) as avg_processed
                FROM sessions
                WHERE initialization_phase = 'complete'
                  AND start_time >= datetime('now', '-{} days')
            """.format(days)
            
            files_result = self.db.execute_query(files_query)
            avg_files = files_result[0]['avg_files'] if files_result else 0
            avg_processed = files_result[0]['avg_processed'] if files_result else 0
            
            # Success rate (completed vs started)
            started_count = self.db.execute_query("""
                SELECT COUNT(*) as count FROM sessions
                WHERE initialization_started_at IS NOT NULL 
                  AND start_time >= datetime('now', '-{} days')
            """.format(days))[0]['count']
            
            completed_count = phase_distribution.get('complete', 0)
            success_rate = (completed_count / started_count * 100) if started_count > 0 else 0
            
            return {
                'phase_distribution': phase_distribution,
                'avg_completion_time_minutes': round(avg_completion_time or 0, 2),
                'avg_files_discovered': round(avg_files or 0, 0),
                'avg_files_processed': round(avg_processed or 0, 0),
                'success_rate_percentage': round(success_rate, 2),
                'total_initializations_started': started_count,
                'total_initializations_completed': completed_count,
                'analysis_period_days': days
            }
            
        except Exception as e:
            self.db.logger.error(f"Error getting initialization analytics: {e}")
            return {
                'phase_distribution': {},
                'avg_completion_time_minutes': 0,
                'avg_files_discovered': 0,
                'avg_files_processed': 0,
                'success_rate_percentage': 0,
                'total_initializations_started': 0,
                'total_initializations_completed': 0,
                'analysis_period_days': days
            }