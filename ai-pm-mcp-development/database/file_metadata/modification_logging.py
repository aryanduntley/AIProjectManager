"""
File Modification Logging Module

Handles file modification tracking and history analysis.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from ..db_manager import DatabaseManager


class ModificationLogging:
    """File modification logging and history operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def log_file_modification(
        self,
        file_path: str,
        file_type: str,
        operation: str,
        session_id: str = None,
        details: Dict[str, Any] = None
    ) -> bool:
        """
        Log a file modification event for tracking and analysis.
        
        Args:
            file_path: Path to the modified file
            file_type: Type of file (theme, flow, task, blueprint, code, config, etc.)
            operation: Operation performed (create, update, delete)
            session_id: Session ID for context
            details: Additional details about the modification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO file_modifications 
                (file_path, file_type, operation, session_id, details)
                VALUES (?, ?, ?, ?, ?)
            """
            
            self.db.execute_update(query, (
                file_path, file_type, operation, session_id,
                json.dumps(details or {})
            ))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error logging file modification: {e}")
            return False
    
    def get_file_modifications(
        self,
        file_path: str = None,
        file_type: str = None,
        operation: str = None,
        session_id: str = None,
        days: int = 30,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get file modification history with flexible filtering.
        
        Args:
            file_path: Optional file path filter
            file_type: Optional file type filter
            operation: Optional operation filter
            session_id: Optional session ID filter
            days: Number of days to include
            limit: Optional result limit
            
        Returns:
            List of file modification records
        """
        base_query = """
            SELECT file_path, file_type, operation, session_id, details, timestamp
            FROM file_modifications
            WHERE timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        conditions = []
        params = []
        
        if file_path:
            conditions.append("file_path LIKE ?")
            params.append(f"%{file_path}%")
        
        if file_type:
            conditions.append("file_type = ?")
            params.append(file_type)
        
        if operation:
            conditions.append("operation = ?")
            params.append(operation)
        
        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " ORDER BY timestamp DESC"
        
        if limit:
            base_query += f" LIMIT {limit}"
        
        results = []
        for row in self.db.execute_query(base_query, tuple(params)):
            results.append({
                "file_path": row["file_path"],
                "file_type": row["file_type"],
                "operation": row["operation"],
                "session_id": row["session_id"],
                "details": json.loads(row["details"]) if row["details"] else {},
                "timestamp": row["timestamp"]
            })
        
        return results
    
    def get_file_modification_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of file modifications."""
        base_query = f"""
            FROM file_modifications 
            WHERE timestamp >= datetime('now', '-{days} days')
        """
        
        # Total modifications
        total_query = f"SELECT COUNT(*) as count {base_query}"
        total_modifications = self.db.execute_query(total_query)[0]["count"]
        
        # By operation
        operation_query = f"""
            SELECT operation, COUNT(*) as count {base_query}
            GROUP BY operation
            ORDER BY count DESC
        """
        operations = {row["operation"]: row["count"] 
                     for row in self.db.execute_query(operation_query)}
        
        # By file type
        type_query = f"""
            SELECT file_type, COUNT(*) as count {base_query}
            GROUP BY file_type
            ORDER BY count DESC
        """
        file_types = {row["file_type"]: row["count"] 
                     for row in self.db.execute_query(type_query)}
        
        # Most modified files
        files_query = f"""
            SELECT file_path, COUNT(*) as count {base_query}
            GROUP BY file_path
            ORDER BY count DESC
            LIMIT 10
        """
        most_modified = [
            {"file_path": row["file_path"], "modifications": row["count"]}
            for row in self.db.execute_query(files_query)
        ]
        
        return {
            "period_days": days,
            "total_modifications": total_modifications,
            "operations": operations,
            "file_types": file_types,
            "most_modified_files": most_modified
        }

    # Performance and Analytics
    
    def get_file_hotspots(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get file modification hotspots for performance analysis.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of file hotspots with activity metrics
        """
        query = """
            SELECT 
                file_path,
                file_type,
                COUNT(*) as modification_count,
                COUNT(DISTINCT session_id) as session_count,
                MIN(timestamp) as first_modification,
                MAX(timestamp) as last_modification,
                COUNT(DISTINCT operation) as operation_types
            FROM file_modifications
            WHERE timestamp >= datetime('now', '-{} days')
            GROUP BY file_path, file_type
            HAVING modification_count > 1
            ORDER BY modification_count DESC, session_count DESC
            LIMIT 50
        """.format(days)
        
        results = []
        for row in self.db.execute_query(query):
            # Calculate modification frequency
            first_mod = datetime.fromisoformat(row["first_modification"])
            last_mod = datetime.fromisoformat(row["last_modification"])
            duration_days = (last_mod - first_mod).days + 1
            
            frequency = row["modification_count"] / duration_days if duration_days > 0 else 0
            
            results.append({
                "file_path": row["file_path"],
                "file_type": row["file_type"],
                "modification_count": row["modification_count"],
                "session_count": row["session_count"],
                "operation_types": row["operation_types"],
                "first_modification": row["first_modification"],
                "last_modification": row["last_modification"],
                "frequency_per_day": round(frequency, 2),
                "activity_score": row["modification_count"] * row["session_count"]
            })
        
        return results
    
    def cleanup_old_modifications(self, days: int = 90) -> int:
        """
        Clean up old file modification records.
        
        Args:
            days: Keep records newer than this many days
            
        Returns:
            Number of records deleted
        """
        try:
            query = """
                DELETE FROM file_modifications 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days)
            
            deleted_count = self.db.execute_update(query)
            self.db.logger.info(f"Cleaned up {deleted_count} old file modification records")
            return deleted_count
            
        except Exception as e:
            self.db.logger.error(f"Error cleaning up file modifications: {e}")
            return 0