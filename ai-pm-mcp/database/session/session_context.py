"""
Session Context Management
Handles session context snapshots, theme/task/sidequest updates, and context preservation.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from ..db_manager import DatabaseManager


class SessionContextManager:
    """Manages session context and snapshots."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
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
            files_accessed: List of files that were accessed
            context_escalations: Number of context escalations
        """
        query = """
        INSERT OR REPLACE INTO session_context (
            session_id, loaded_themes, loaded_flows, 
            context_escalations, files_accessed, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = (
            session_id,
            ",".join(loaded_themes),
            ",".join(loaded_flows),
            context_escalations,
            json.dumps(files_accessed)
        )
        
        self.db.execute_update(query, params)
    
    def update_session_context(self, session_id: str, context_data: Dict[str, Any]):
        """
        Update session context with tracking data.
        
        Args:
            session_id: Session ID
            context_data: Dictionary containing context tracking information
        """
        # Convert context_data to the format expected by save_session_context
        loaded_themes = context_data.get("loaded_themes", [])
        # Extract flow names from loaded flows data if available
        loaded_flows = []
        if "loaded_flows_data" in context_data:
            loaded_flows = list(context_data["loaded_flows_data"].keys())
        
        # Save the context using the existing method
        self.save_session_context(
            session_id=session_id,
            loaded_themes=loaded_themes,
            loaded_flows=loaded_flows,
            files_accessed=[],  # Files accessed not tracked in this context
            context_escalations=0
        )
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session context for restoration.
        
        Args:
            session_id: Session ID
            
        Returns:
            Optional[Dict[str, Any]]: Session context data
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
            try:
                files_accessed = json.loads(row[4]) if row[4] else []
            except json.JSONDecodeError:
                files_accessed = []
            
            return {
                "session_id": row[0],
                "loaded_themes": row[1].split(",") if row[1] else [],
                "loaded_flows": row[2].split(",") if row[2] else [],
                "context_escalations": row[3] if row[3] else 0,
                "files_accessed": files_accessed,
                "created_at": row[5]
            }
        return None
    
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
            context_data: Current context data (themes, flows, files)
            queue_position: Position in task queue for multi-task scenarios
            
        Returns:
            int: Snapshot ID for reference
        """
        query = """
        INSERT INTO task_queue (
            session_id, task_id, sidequest_id, context_snapshot, 
            queue_position, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        context_json = json.dumps(context_data or {})
        
        params = (
            session_id, task_id, sidequest_id, context_json,
            queue_position, datetime.now().isoformat()
        )
        
        cursor = self.db.execute_update(query, params)
        return cursor.lastrowid if hasattr(cursor, 'lastrowid') else 0
    
    def get_context_snapshot(self, task_id: Optional[str] = None, sidequest_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve context snapshot for task resumption.
        
        Args:
            task_id: Task ID to restore context for
            sidequest_id: Sidequest ID to restore context for
            
        Returns:
            Optional[Dict[str, Any]]: Context snapshot data
        """
        if task_id:
            query = "SELECT * FROM task_queue WHERE task_id = ? ORDER BY created_at DESC LIMIT 1"
            params = (task_id,)
        elif sidequest_id:
            query = "SELECT * FROM task_queue WHERE sidequest_id = ? ORDER BY created_at DESC LIMIT 1"
            params = (sidequest_id,)
        else:
            return None
            
        result = self.db.execute_query(query, params)
        if result:
            row = result[0]
            try:
                context_data = json.loads(row[3]) if row[3] else {}
            except json.JSONDecodeError:
                context_data = {}
                
            return {
                "id": row[0],
                "session_id": row[1], 
                "task_id": row[2],
                "sidequest_id": row[3],
                "context_snapshot": context_data,
                "queue_position": row[5],
                "created_at": row[6]
            }
        return None
    
    def clear_context_snapshot(self, task_id: Optional[str] = None, sidequest_id: Optional[str] = None):
        """Clear context snapshot after successful resumption."""
        if task_id:
            self.db.execute_update("DELETE FROM task_queue WHERE task_id = ?", (task_id,))
        elif sidequest_id:
            self.db.execute_update("DELETE FROM task_queue WHERE sidequest_id = ?", (sidequest_id,))
    
    def update_active_themes(self, session_id: str, active_themes: List[str]):
        """Update active themes for a session."""
        self.db.execute_update("UPDATE sessions SET active_themes = ? WHERE session_id = ?", 
                             (json.dumps(active_themes), session_id))
    
    def update_active_tasks(self, session_id: str, active_tasks: List[str]):
        """Update active tasks for a session."""
        self.db.execute_update("UPDATE sessions SET active_tasks = ? WHERE session_id = ?",
                             (json.dumps(active_tasks), session_id))
    
    def update_active_sidequests(self, session_id: str, active_sidequests: List[str]):
        """Update active sidequests for a session."""
        self.db.execute_update("UPDATE sessions SET active_sidequests = ? WHERE session_id = ?",
                             (json.dumps(active_sidequests), session_id))