"""
Initialization Tracking
Handles file metadata initialization progress tracking and resumption.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from ..db_manager import DatabaseManager


class InitializationTracker:
    """Manages file metadata initialization tracking."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def start_initialization(self, session_id: str, total_files_discovered: int) -> bool:
        """
        Start file metadata initialization tracking.
        
        Args:
            session_id: Session ID
            total_files_discovered: Total number of files discovered for processing
            
        Returns:
            bool: True if successful
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
            
            params = (
                total_files_discovered,
                datetime.now().isoformat(),
                session_id
            )
            
            self.db.execute_update(query, params)
            return True
            
        except Exception as e:
            print(f"Error starting initialization: {e}")
            return False
    
    def update_initialization_phase(self, session_id: str, phase: str) -> bool:
        """
        Update initialization phase.
        
        Args:
            session_id: Session ID
            phase: New phase (discovering_files, analyzing_files, building_flows, complete)
            
        Returns:
            bool: True if successful
        """
        try:
            query = "UPDATE sessions SET initialization_phase = ? WHERE session_id = ?"
            self.db.execute_update(query, (phase, session_id))
            return True
            
        except Exception as e:
            print(f"Error updating initialization phase: {e}")
            return False
    
    def complete_initialization(self, session_id: str) -> bool:
        """
        Mark initialization as complete.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successful
        """
        try:
            query = """
            UPDATE sessions 
            SET initialization_phase = 'complete',
                initialization_completed_at = ?
            WHERE session_id = ?
            """
            
            params = (datetime.now().isoformat(), session_id)
            self.db.execute_update(query, params)
            return True
            
        except Exception as e:
            print(f"Error completing initialization: {e}")
            return False
    
    def get_initialization_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get initialization status and progress.
        
        Args:
            session_id: Session ID
            
        Returns:
            Optional[Dict[str, Any]]: Initialization status data
        """
        try:
            query = """
            SELECT initialization_phase, files_processed, total_files_discovered,
                   initialization_started_at, initialization_completed_at
            FROM sessions 
            WHERE session_id = ?
            """
            
            result = self.db.execute_query(query, (session_id,))
            if result:
                row = result[0]
                
                # Calculate progress percentage
                files_processed = row[1] or 0
                total_files = row[2] or 0
                progress_percentage = (files_processed / total_files * 100) if total_files > 0 else 0
                
                # Calculate duration if started
                duration_seconds = None
                if row[3]:  # initialization_started_at
                    start_time = datetime.fromisoformat(row[3])
                    end_time = datetime.fromisoformat(row[4]) if row[4] else datetime.now()
                    duration_seconds = (end_time - start_time).total_seconds()
                
                return {
                    "session_id": session_id,
                    "phase": row[0],
                    "files_processed": files_processed,
                    "total_files_discovered": total_files,
                    "progress_percentage": round(progress_percentage, 2),
                    "is_complete": row[0] == 'complete',
                    "started_at": row[3],
                    "completed_at": row[4],
                    "duration_seconds": duration_seconds,
                    "status": self._get_phase_description(row[0])
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting initialization status: {e}")
            return None
    
    def get_sessions_needing_initialization(self) -> List[Dict[str, Any]]:
        """
        Get sessions with incomplete initialization that can be resumed.
        
        Returns:
            List[Dict[str, Any]]: Sessions needing initialization
        """
        try:
            query = """
            SELECT session_id, project_path, initialization_phase, 
                   files_processed, total_files_discovered, initialization_started_at
            FROM sessions 
            WHERE archived_at IS NULL
            AND initialization_phase != 'complete' 
            AND initialization_phase != 'not_started'
            ORDER BY initialization_started_at DESC
            """
            
            result = self.db.execute_query(query)
            
            sessions = []
            for row in result:
                progress_percentage = 0
                if row[4] and row[4] > 0:  # total_files_discovered
                    progress_percentage = (row[3] or 0) / row[4] * 100
                
                sessions.append({
                    "session_id": row[0],
                    "project_path": row[1],
                    "phase": row[2],
                    "files_processed": row[3] or 0,
                    "total_files_discovered": row[4] or 0,
                    "progress_percentage": round(progress_percentage, 2),
                    "started_at": row[5],
                    "status": self._get_phase_description(row[2])
                })
            
            return sessions
            
        except Exception as e:
            print(f"Error getting sessions needing initialization: {e}")
            return []
    
    def increment_files_processed(self, session_id: str) -> bool:
        """
        Increment the files processed counter.
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successful
        """
        try:
            query = """
            UPDATE sessions 
            SET files_processed = files_processed + 1
            WHERE session_id = ?
            """
            
            self.db.execute_update(query, (session_id,))
            return True
            
        except Exception as e:
            print(f"Error incrementing files processed: {e}")
            return False
    
    def reset_initialization(self, session_id: str) -> bool:
        """
        Reset initialization progress (requires confirmation in calling code).
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if successful
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
            print(f"Error resetting initialization: {e}")
            return False
    
    def get_initialization_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get initialization analytics across all sessions.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Initialization analytics
        """
        try:
            query = """
            SELECT 
                initialization_phase,
                COUNT(*) as count,
                AVG(files_processed) as avg_files_processed,
                AVG(total_files_discovered) as avg_total_files,
                AVG(CASE 
                    WHEN initialization_completed_at IS NOT NULL AND initialization_started_at IS NOT NULL
                    THEN (julianday(initialization_completed_at) - julianday(initialization_started_at)) * 24 * 60 * 60
                    ELSE NULL
                END) as avg_duration_seconds
            FROM sessions
            WHERE initialization_started_at >= datetime('now', '-{} days')
            GROUP BY initialization_phase
            ORDER BY count DESC
            """.format(days)
            
            result = self.db.execute_query(query)
            
            analytics = {
                "analysis_period_days": days,
                "phase_summary": {},
                "totals": {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "avg_completion_time_seconds": 0,
                    "avg_files_per_session": 0
                },
                "generated_at": datetime.now().isoformat()
            }
            
            total_sessions = 0
            completed_count = 0
            total_completion_time = 0
            total_files = 0
            
            for row in result:
                phase = row[0]
                count = row[1]
                avg_files_processed = row[2] or 0
                avg_total_files = row[3] or 0
                avg_duration = row[4] or 0
                
                analytics["phase_summary"][phase] = {
                    "count": count,
                    "avg_files_processed": round(avg_files_processed, 2),
                    "avg_total_files": round(avg_total_files, 2),
                    "avg_duration_seconds": round(avg_duration, 2),
                    "description": self._get_phase_description(phase)
                }
                
                total_sessions += count
                total_files += avg_total_files * count
                
                if phase == 'complete':
                    completed_count = count
                    total_completion_time = avg_duration * count
            
            analytics["totals"]["total_sessions"] = total_sessions
            analytics["totals"]["completed_sessions"] = completed_count
            analytics["totals"]["completion_rate"] = (completed_count / total_sessions * 100) if total_sessions > 0 else 0
            analytics["totals"]["avg_completion_time_seconds"] = total_completion_time / completed_count if completed_count > 0 else 0
            analytics["totals"]["avg_files_per_session"] = total_files / total_sessions if total_sessions > 0 else 0
            
            return analytics
            
        except Exception as e:
            print(f"Error getting initialization analytics: {e}")
            return {
                "analysis_period_days": days,
                "phase_summary": {},
                "totals": {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "avg_completion_time_seconds": 0,
                    "avg_files_per_session": 0
                },
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _get_phase_description(self, phase: str) -> str:
        """Get human-readable description for initialization phase."""
        descriptions = {
            'not_started': 'Initialization not started',
            'discovering_files': 'Discovering project files',
            'analyzing_files': 'Analyzing file metadata',
            'building_flows': 'Building project flows',
            'complete': 'Initialization complete'
        }
        return descriptions.get(phase, f'Unknown phase: {phase}')