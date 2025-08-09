"""
Boot Context Management
Handles session boot context retrieval and optimization.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from ..db_manager import DatabaseManager
from ..event_queries import EventQueries


class BootContextManager:
    """Manages boot sequence context retrieval and optimization."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def get_boot_context(self, project_path: str) -> Dict[str, Any]:
        """
        Get comprehensive boot context for session restoration.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dict[str, Any]: Boot context data
        """
        try:
            # Get most recent session for this project
            latest_session = self._get_latest_project_session(project_path)
            
            # Get session context if available
            session_context = None
            if latest_session:
                session_context = self._get_session_context_data(latest_session["session_id"])
            
            # Get recent work activities
            recent_activities = self._get_recent_activities(project_path, hours=24)
            
            # Get initialization status
            initialization_status = None
            if latest_session:
                initialization_status = self._get_initialization_status(latest_session["session_id"])
            
            # Check for high-priority items
            high_priority_status = self._check_high_priority_items()
            
            # Build comprehensive boot context
            boot_context = {
                "project_path": project_path,
                "latest_session": latest_session,
                "session_context": session_context,
                "recent_activities": recent_activities,
                "initialization_status": initialization_status,
                "high_priority_status": high_priority_status,
                "boot_recommendations": self._generate_boot_recommendations(
                    latest_session, session_context, initialization_status, high_priority_status
                ),
                "generated_at": datetime.now().isoformat()
            }
            
            return boot_context
            
        except Exception as e:
            print(f"Error getting boot context: {e}")
            return {
                "project_path": project_path,
                "latest_session": None,
                "session_context": None,
                "recent_activities": [],
                "initialization_status": None,
                "boot_recommendations": {
                    "action": "start_fresh",
                    "reason": f"Error retrieving boot context: {str(e)}"
                },
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _get_latest_project_session(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Get the most recent session for the project."""
        try:
            query = """
            SELECT session_id, start_time, last_tool_activity, context_mode,
                   active_themes, active_tasks, active_sidequests, archived_at,
                   initialization_phase, files_processed, total_files_discovered
            FROM sessions 
            WHERE project_path = ?
            ORDER BY last_tool_activity DESC 
            LIMIT 1
            """
            
            result = self.db.execute_query(query, (project_path,))
            
            if result:
                row = result[0]
                
                # Parse JSON fields
                try:
                    active_themes = json.loads(row[4]) if row[4] else []
                except json.JSONDecodeError:
                    active_themes = []
                    
                try:
                    active_tasks = json.loads(row[5]) if row[5] else []
                except json.JSONDecodeError:
                    active_tasks = []
                    
                try:
                    active_sidequests = json.loads(row[6]) if row[6] else []
                except json.JSONDecodeError:
                    active_sidequests = []
                
                return {
                    "session_id": row[0],
                    "start_time": row[1],
                    "last_activity": row[2],
                    "context_mode": row[3],
                    "active_themes": active_themes,
                    "active_tasks": active_tasks,
                    "active_sidequests": active_sidequests,
                    "is_archived": row[7] is not None,
                    "initialization_phase": row[8],
                    "files_processed": row[9] or 0,
                    "total_files_discovered": row[10] or 0
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting latest session: {e}")
            return None
    
    def _get_session_context_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session context data."""
        try:
            query = """
            SELECT loaded_themes, loaded_flows, context_escalations, 
                   files_accessed, created_at
            FROM session_context 
            WHERE session_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
            """
            
            result = self.db.execute_query(query, (session_id,))
            
            if result:
                row = result[0]
                
                try:
                    files_accessed = json.loads(row[3]) if row[3] else []
                except json.JSONDecodeError:
                    files_accessed = []
                
                return {
                    "loaded_themes": row[0].split(",") if row[0] else [],
                    "loaded_flows": row[1].split(",") if row[1] else [],
                    "context_escalations": row[2] or 0,
                    "files_accessed": files_accessed,
                    "created_at": row[4]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting session context: {e}")
            return None
    
    def _get_recent_activities(self, project_path: str, hours: int = 24) -> list:
        """Get recent work activities."""
        try:
            query = """
            SELECT activity_type, tool_name, timestamp, duration_ms
            FROM work_activities
            WHERE project_path = ? 
            AND timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp DESC
            LIMIT 20
            """.format(hours)
            
            result = self.db.execute_query(query, (project_path,))
            
            activities = []
            for row in result:
                activities.append({
                    "activity_type": row[0],
                    "tool_name": row[1],
                    "timestamp": row[2],
                    "duration_ms": row[3]
                })
            
            return activities
            
        except Exception as e:
            print(f"Error getting recent activities: {e}")
            return []
    
    def _get_initialization_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get initialization status."""
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
                
                files_processed = row[1] or 0
                total_files = row[2] or 0
                progress = (files_processed / total_files * 100) if total_files > 0 else 0
                
                return {
                    "phase": row[0],
                    "files_processed": files_processed,
                    "total_files": total_files,
                    "progress_percentage": round(progress, 2),
                    "is_complete": row[0] == 'complete',
                    "started_at": row[3],
                    "completed_at": row[4]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting initialization status: {e}")
            return None
    
    def _generate_boot_recommendations(self, latest_session: Optional[Dict], 
                                     session_context: Optional[Dict], 
                                     initialization_status: Optional[Dict],
                                     high_priority_status: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate boot recommendations based on available context."""
        try:
            # Check for high-priority items first - they take precedence
            if high_priority_status and high_priority_status.get("has_high_priority", False):
                return {
                    "action": "address_high_priority",
                    "reason": f"High priority work detected: {high_priority_status.get('summary', 'Unknown issues')}",
                    "priority": "critical",
                    "high_priority_details": high_priority_status,
                    "suggestions": [
                        "Review high-priority tasks and implementation plans",
                        "Address scope-exceeding issues",
                        "Consider escalating to dedicated high-priority workflow"
                    ]
                }
            
            # No previous session
            if not latest_session:
                return {
                    "action": "initialize_fresh",
                    "reason": "No previous session found for this project",
                    "priority": "high"
                }
            
            # Session is archived
            if latest_session.get("is_archived"):
                return {
                    "action": "start_new_session",
                    "reason": "Previous session was archived",
                    "priority": "medium",
                    "context_available": session_context is not None
                }
            
            # Incomplete initialization
            if initialization_status and not initialization_status.get("is_complete"):
                return {
                    "action": "resume_initialization",
                    "reason": f"Initialization incomplete ({initialization_status.get('progress_percentage', 0):.1f}%)",
                    "priority": "high",
                    "phase": initialization_status.get("phase"),
                    "progress": initialization_status.get("progress_percentage", 0)
                }
            
            # Active session with context
            if session_context and latest_session.get("active_tasks"):
                return {
                    "action": "resume_session",
                    "reason": "Active session with available context and tasks",
                    "priority": "high",
                    "active_tasks": len(latest_session.get("active_tasks", [])),
                    "loaded_themes": len(session_context.get("loaded_themes", []))
                }
            
            # Active session without much context
            if latest_session.get("active_tasks") or latest_session.get("active_themes"):
                return {
                    "action": "resume_partial",
                    "reason": "Active session found but limited context available",
                    "priority": "medium",
                    "suggestions": ["Review active themes", "Check task status", "Load recent context"]
                }
            
            # Default recommendation
            return {
                "action": "continue_development",
                "reason": "Previous session found, ready to continue",
                "priority": "medium",
                "context_mode": latest_session.get("context_mode", "theme-focused")
            }
            
        except Exception as e:
            return {
                "action": "start_fresh",
                "reason": f"Error generating recommendations: {str(e)}",
                "priority": "low"
            }
    
    def _check_high_priority_items(self) -> Optional[Dict[str, Any]]:
        """Check for high-priority events in the database."""
        try:
            event_queries = EventQueries(self.db)
            
            # Check if high priority exists (last 7 days for boot check)
            has_high_priority = event_queries.check_high_priority_exists(days_lookback=7)
            
            if not has_high_priority:
                return {
                    "has_high_priority": False,
                    "summary": "No high-priority items detected",
                    "events": [],
                    "escalation_required": []
                }
            
            # Get high priority events (limited for boot context)
            high_priority_events = event_queries.get_high_priority_events(limit=3, days_lookback=7)
            
            # Get escalation required events
            escalation_events = event_queries.get_escalation_required_events(limit=2, days_lookback=3)
            
            # Generate summary
            event_count = len(high_priority_events)
            escalation_count = len(escalation_events)
            
            summary_parts = []
            if event_count > 0:
                summary_parts.append(f"{event_count} high-priority event{'s' if event_count != 1 else ''}")
            if escalation_count > 0:
                summary_parts.append(f"{escalation_count} item{'s' if escalation_count != 1 else ''} requiring escalation")
            
            summary = "Found: " + ", ".join(summary_parts) if summary_parts else "High-priority status detected"
            
            return {
                "has_high_priority": True,
                "summary": summary,
                "events": [
                    {
                        "title": event.get("title", "Unknown"),
                        "type": event.get("event_type", "unknown"),
                        "impact": event.get("impact_level", "unknown"),
                        "created": event.get("created_at", "unknown")
                    }
                    for event in high_priority_events
                ],
                "escalation_required": [
                    {
                        "title": event.get("title", "Unknown"),
                        "type": event.get("event_type", "unknown"),
                        "created": event.get("created_at", "unknown")
                    }
                    for event in escalation_events
                ]
            }
            
        except Exception as e:
            print(f"Error checking high priority items: {e}")
            return {
                "has_high_priority": False,
                "summary": f"Error checking high-priority status: {str(e)}",
                "events": [],
                "escalation_required": []
            }