"""
File and Task Tracking
Handles file modification logging and task completion metrics.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..db_manager import DatabaseManager


class FileTaskTracker:
    """Manages file modifications and task completion tracking."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def log_file_modification(self, session_id: str, file_path: str, file_type: str, 
                             modification_type: str, details: Dict[str, Any] = None) -> bool:
        """
        Log file modification for tracking and analytics.
        
        Args:
            session_id: Session ID
            file_path: Path to the modified file
            file_type: Type of file (py, js, md, etc.)
            modification_type: Type of modification (create, update, delete, rename)
            details: Additional details about the modification
            
        Returns:
            bool: True if successful
        """
        try:
            query = """
            INSERT INTO file_modifications (
                session_id, file_path, file_type, modification_type, 
                details, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            details_json = json.dumps(details or {})
            
            params = (
                session_id, file_path, file_type, modification_type,
                details_json, datetime.now().isoformat()
            )
            
            self.db.execute_update(query, params)
            return True
            
        except Exception as e:
            print(f"Error logging file modification: {e}")
            return False
    
    def get_file_modifications(self, session_id: str = None, file_type: str = None, 
                              days: int = 7) -> List[Dict[str, Any]]:
        """
        Get file modifications with optional filters.
        
        Args:
            session_id: Filter by session ID (optional)
            file_type: Filter by file type (optional)
            days: Number of days to look back
            
        Returns:
            List[Dict[str, Any]]: File modification records
        """
        try:
            # Build query with optional filters
            query = """
            SELECT * FROM file_modifications 
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
            
            result = self.db.execute_query(query, params)
            
            modifications = []
            for row in result:
                try:
                    details = json.loads(row[4]) if row[4] else {}
                except json.JSONDecodeError:
                    details = {}
                
                modifications.append({
                    "id": row[0],
                    "session_id": row[1],
                    "file_path": row[2],
                    "file_type": row[3],
                    "modification_type": row[4],
                    "details": details,
                    "timestamp": row[5]
                })
            
            return modifications
            
        except Exception as e:
            print(f"Error getting file modifications: {e}")
            return []
    
    def record_task_completion(self, session_id: str, task_id: str, milestone_id: str = None,
                              theme_name: str = None, completion_data: Dict[str, Any] = None,
                              files_modified: List[str] = None) -> bool:
        """
        Record task completion with metrics.
        
        Args:
            session_id: Session ID
            task_id: Completed task ID
            milestone_id: Associated milestone ID (optional)
            theme_name: Primary theme for the task (optional)
            completion_data: Additional completion data
            files_modified: List of files modified during task (optional)
            
        Returns:
            bool: True if successful
        """
        try:
            query = """
            INSERT INTO task_metrics (
                session_id, task_id, milestone_id, theme_name,
                completion_data, files_modified, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            completion_json = json.dumps(completion_data or {})
            files_json = json.dumps(files_modified or [])
            
            params = (
                session_id, task_id, milestone_id, theme_name,
                completion_json, files_json, datetime.now().isoformat()
            )
            
            self.db.execute_update(query, params)
            return True
            
        except Exception as e:
            print(f"Error recording task completion: {e}")
            return False
    
    def get_task_metrics(self, theme_name: str = None, milestone_id: str = None,
                        days: int = 30) -> Dict[str, Any]:
        """
        Get task completion metrics and analytics.
        
        Args:
            theme_name: Filter by theme (optional)
            milestone_id: Filter by milestone (optional)
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Task metrics and analytics
        """
        try:
            # Build query with optional filters
            base_query = """
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(DISTINCT theme_name) as unique_themes,
                COUNT(DISTINCT milestone_id) as unique_milestones,
                AVG(json_array_length(files_modified)) as avg_files_per_task
            FROM task_metrics
            WHERE completed_at >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            
            if theme_name:
                base_query += " AND theme_name = ?"
                params.append(theme_name)
                
            if milestone_id:
                base_query += " AND milestone_id = ?"
                params.append(milestone_id)
            
            result = self.db.execute_query(base_query, params)
            
            # Theme distribution query
            theme_query = """
            SELECT theme_name, COUNT(*) as task_count
            FROM task_metrics
            WHERE completed_at >= datetime('now', '-{} days')
            """.format(days)
            
            if milestone_id:
                theme_query += " AND milestone_id = ?"
                theme_params = [milestone_id]
            else:
                theme_params = []
                
            theme_query += " GROUP BY theme_name ORDER BY task_count DESC LIMIT 10"
            theme_result = self.db.execute_query(theme_query, theme_params)
            
            # Build metrics response
            metrics = {
                "analysis_period_days": days,
                "filters": {
                    "theme_name": theme_name,
                    "milestone_id": milestone_id
                },
                "summary": {},
                "theme_distribution": {},
                "generated_at": datetime.now().isoformat()
            }
            
            # Process summary
            if result:
                row = result[0]
                metrics["summary"] = {
                    "total_tasks": row[0] or 0,
                    "unique_themes": row[1] or 0,
                    "unique_milestones": row[2] or 0,
                    "avg_files_per_task": round(row[3] or 0, 2)
                }
            
            # Process theme distribution
            if theme_result:
                theme_distribution = {}
                total_tasks = sum(row[1] for row in theme_result)
                
                for row in theme_result:
                    theme = row[0] or "unknown"
                    count = row[1]
                    percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
                    
                    theme_distribution[theme] = {
                        "task_count": count,
                        "percentage": round(percentage, 2)
                    }
                
                metrics["theme_distribution"] = theme_distribution
            
            return metrics
            
        except Exception as e:
            print(f"Error getting task metrics: {e}")
            return {
                "analysis_period_days": days,
                "filters": {
                    "theme_name": theme_name,
                    "milestone_id": milestone_id
                },
                "summary": {
                    "total_tasks": 0,
                    "unique_themes": 0,
                    "unique_milestones": 0,
                    "avg_files_per_task": 0
                },
                "theme_distribution": {},
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }