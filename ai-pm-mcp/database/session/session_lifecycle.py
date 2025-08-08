"""
Session Lifecycle Management
Handles core session creation, updates, and retrieval operations.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from ..db_manager import DatabaseManager


class SessionLifecycleManager:
    """Manages core session lifecycle operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
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
            context: Session context data
            
        Returns:
            str: Session ID
        """
        session_id = str(uuid.uuid4())
        
        # Convert lists to JSON strings for storage
        active_themes_json = json.dumps(active_themes or [])
        active_tasks_json = json.dumps(active_tasks or [])
        active_sidequests_json = json.dumps(active_sidequests or [])
        metadata_json = json.dumps(metadata or {})
        context_json = json.dumps(context or {})
        
        query = """
        INSERT INTO sessions (
            session_id, start_time, work_period_started, last_tool_activity,
            context_mode, active_themes, active_tasks, active_sidequests, 
            project_path, metadata, context, activity_summary, context_snapshot
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        current_time = datetime.now().isoformat()
        params = (
            session_id, current_time, current_time, current_time,
            context_mode, active_themes_json, active_tasks_json, 
            active_sidequests_json, project_path, metadata_json, 
            context_json, '{}', '{}'
        )
        
        self.db.execute_update(query, params)
        return session_id
    
    def update_session_activity(self, session_id: str, context: str = None, 
                                active_themes: List[str] = None, 
                                active_tasks: List[str] = None,
                                active_sidequests: List[str] = None) -> bool:
        """
        Update session with current activity information.
        
        Args:
            session_id: Session ID to update
            context: Updated context information
            active_themes: Updated list of active themes
            active_tasks: Updated list of active tasks  
            active_sidequests: Updated list of active sidequests
            
        Returns:
            bool: True if successful
        """
        try:
            updates = ["last_tool_activity = ?"]
            params = [datetime.now().isoformat()]
            
            if context is not None:
                updates.append("context = ?")
                params.append(context)
                
            if active_themes is not None:
                updates.append("active_themes = ?") 
                params.append(json.dumps(active_themes))
                
            if active_tasks is not None:
                updates.append("active_tasks = ?")
                params.append(json.dumps(active_tasks))
                
            if active_sidequests is not None:
                updates.append("active_sidequests = ?")
                params.append(json.dumps(active_sidequests))
            
            params.append(session_id)
            
            query = f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = ?"
            self.db.execute_update(query, params)
            return True
            
        except Exception as e:
            print(f"Error updating session activity: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Optional[Dict[str, Any]]: Session data or None
        """
        query = """
        SELECT * FROM sessions WHERE session_id = ?
        """
        
        result = self.db.execute_query(query, (session_id,))
        if result:
            return self._session_row_to_dict(result[0])
        return None
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive session data for restoration.
        
        Args:
            session_id: Session ID
            
        Returns:
            Optional[Dict[str, Any]]: Complete session data
        """
        return self.get_session(session_id)
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent sessions ordered by last activity.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List[Dict[str, Any]]: List of recent sessions
        """
        query = """
        SELECT * FROM sessions 
        WHERE archived_at IS NULL
        ORDER BY last_tool_activity DESC 
        LIMIT ?
        """
        
        result = self.db.execute_query(query, (limit,))
        return [self._session_row_to_dict(row) for row in result]
    
    def get_latest_session(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent session for a specific project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Optional[Dict[str, Any]]: Latest session data or None
        """
        query = """
        SELECT * FROM sessions 
        WHERE project_path = ? AND archived_at IS NULL
        ORDER BY last_tool_activity DESC 
        LIMIT 1
        """
        
        result = self.db.execute_query(query, (project_path,))
        if result:
            return self._session_row_to_dict(result[0])
        return None
    
    def _session_row_to_dict(self, row) -> Dict[str, Any]:
        """
        Convert database row to session dictionary.
        
        Args:
            row: Database row
            
        Returns:
            Dict[str, Any]: Session dictionary
        """
        if not row:
            return {}
            
        session_data = {
            "session_id": row.get("session_id", row[0] if row else None),
            "start_time": row.get("start_time", row[1] if len(row) > 1 else None),
            "last_activity": row.get("last_tool_activity", row[2] if len(row) > 2 else None),
            "work_period_started": row.get("work_period_started", row[3] if len(row) > 3 else None),
            "last_tool_activity": row.get("last_tool_activity", row[4] if len(row) > 4 else None),
            "context_mode": row.get("context_mode", row[5] if len(row) > 5 else "theme-focused"),
            "project_path": row.get("project_path", row[6] if len(row) > 6 else None),
            "metadata": row.get("metadata", row[7] if len(row) > 7 else "{}"),
            "notes": row.get("notes", row[8] if len(row) > 8 else None),
            "activity_summary": row.get("activity_summary", row[9] if len(row) > 9 else "{}"),
            "context_snapshot": row.get("context_snapshot", row[10] if len(row) > 10 else "{}"),
            "archived_at": row.get("archived_at", row[11] if len(row) > 11 else None),
            "archive_reason": row.get("archive_reason", row[12] if len(row) > 12 else None),
            "initialization_phase": row.get("initialization_phase", row[13] if len(row) > 13 else "not_started"),
            "files_processed": row.get("files_processed", row[14] if len(row) > 14 else 0),
            "total_files_discovered": row.get("total_files_discovered", row[15] if len(row) > 15 else 0),
            "initialization_started_at": row.get("initialization_started_at", row[16] if len(row) > 16 else None),
            "initialization_completed_at": row.get("initialization_completed_at", row[17] if len(row) > 17 else None)
        }
        
        # Parse JSON fields safely
        try:
            session_data["active_themes"] = json.loads(row.get("active_themes", "[]"))
        except (json.JSONDecodeError, TypeError):
            session_data["active_themes"] = []
            
        try:
            session_data["active_tasks"] = json.loads(row.get("active_tasks", "[]"))
        except (json.JSONDecodeError, TypeError):
            session_data["active_tasks"] = []
            
        try:
            session_data["active_sidequests"] = json.loads(row.get("active_sidequests", "[]"))
        except (json.JSONDecodeError, TypeError):
            session_data["active_sidequests"] = []
            
        return session_data