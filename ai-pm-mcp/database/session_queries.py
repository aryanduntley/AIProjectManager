"""
Enhanced Session Management Database Queries - Modular Version
Handles session persistence, context snapshots, and boot sequence optimization for AI Project Manager.

This modular version delegates to specialized managers for better organization and maintainability.
"""

from typing import List, Dict, Optional, Any
from .db_manager import DatabaseManager
from .session import (
    SessionLifecycleManager,
    SessionContextManager, 
    WorkActivityTracker,
    InitializationTracker,
    SessionAnalytics,
    FileTaskTracker,
    BootContextManager
)


class SessionQueries:
    """
    Enhanced session management with modular architecture.
    
    This class serves as the main interface to all session-related database operations,
    delegating to specialized managers for different aspects of session management.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize with database manager and create specialized managers.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        
        # Initialize specialized managers
        self.lifecycle = SessionLifecycleManager(db_manager)
        self.context = SessionContextManager(db_manager)
        self.work_activity = WorkActivityTracker(db_manager)
        self.initialization = InitializationTracker(db_manager)
        self.analytics = SessionAnalytics(db_manager)
        self.file_task = FileTaskTracker(db_manager)
        self.boot_context = BootContextManager(db_manager)
    
    # ================================================================
    # Session Lifecycle Methods
    # ================================================================
    
    def start_session(self, project_path: str, context_mode: str = "theme-focused", 
                     active_themes: List[str] = None, active_tasks: List[str] = None,
                     active_sidequests: List[str] = None, metadata: Dict[str, Any] = None,
                     context: Dict[str, Any] = None) -> str:
        """Start a new AI session with context preservation."""
        return self.lifecycle.start_session(
            project_path, context_mode, active_themes, active_tasks, 
            active_sidequests, metadata, context
        )
    
    def update_session_activity(self, session_id: str, context: str = None, 
                                active_themes: List[str] = None, 
                                active_tasks: List[str] = None,
                                active_sidequests: List[str] = None) -> bool:
        """Update session with current activity information."""
        return self.lifecycle.update_session_activity(
            session_id, context, active_themes, active_tasks, active_sidequests
        )
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        return self.lifecycle.get_session(session_id)
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session data for restoration."""
        return self.lifecycle.get_session_data(session_id)
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sessions ordered by last activity."""
        return self.lifecycle.get_recent_sessions(limit)
    
    def get_latest_session(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Get the most recent session for a specific project."""
        return self.lifecycle.get_latest_session(project_path)
    
    # ================================================================
    # Session Context Methods
    # ================================================================
    
    def save_session_context(self, session_id: str, loaded_themes: List[str],
                            loaded_flows: List[str], files_accessed: List[str],
                            context_escalations: int = 0):
        """Save session context for quick restoration."""
        return self.context.save_session_context(
            session_id, loaded_themes, loaded_flows, files_accessed, context_escalations
        )
    
    def update_session_context(self, session_id: str, context_data: Dict[str, Any]):
        """Update session context with tracking data."""
        return self.context.update_session_context(session_id, context_data)
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session context for restoration."""
        return self.context.get_session_context(session_id)
    
    def save_context_snapshot(self, session_id: str, task_id: Optional[str] = None,
                             sidequest_id: Optional[str] = None, 
                             context_data: Dict[str, Any] = None,
                             queue_position: int = 0) -> int:
        """Save a context snapshot for seamless task switching."""
        return self.context.save_context_snapshot(
            session_id, task_id, sidequest_id, context_data, queue_position
        )
    
    def get_context_snapshot(self, task_id: Optional[str] = None, 
                           sidequest_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve context snapshot for task resumption."""
        return self.context.get_context_snapshot(task_id, sidequest_id)
    
    def clear_context_snapshot(self, task_id: Optional[str] = None, 
                              sidequest_id: Optional[str] = None):
        """Clear context snapshot after successful resumption."""
        return self.context.clear_context_snapshot(task_id, sidequest_id)
    
    def update_active_themes(self, session_id: str, active_themes: List[str]):
        """Update active themes for a session."""
        return self.context.update_active_themes(session_id, active_themes)
    
    def update_active_tasks(self, session_id: str, active_tasks: List[str]):
        """Update active tasks for a session."""
        return self.context.update_active_tasks(session_id, active_tasks)
    
    def update_active_sidequests(self, session_id: str, active_sidequests: List[str]):
        """Update active sidequests for a session."""
        return self.context.update_active_sidequests(session_id, active_sidequests)
    
    # ================================================================
    # Work Activity Tracking Methods  
    # ================================================================
    
    def record_work_activity(self, project_path: str, activity_type: str, 
                           tool_name: str = None, activity_data: Dict[str, Any] = None,
                           duration_ms: int = None, session_context_id: str = None) -> bool:
        """Record a work activity (replaces session lifecycle tracking)."""
        return self.work_activity.record_work_activity(
            project_path, activity_type, tool_name, activity_data, 
            duration_ms, session_context_id
        )
    
    def get_recent_work_context(self, project_path: str, hours: int = 4) -> Dict[str, Any]:
        """Get recent work context based on activity timeline."""
        return self.work_activity.get_recent_work_context(project_path, hours)
    
    def archive_stale_work_periods(self, keep_sessions: int = 20) -> int:
        """Archive work periods, keeping only the most recent sessions per project."""
        return self.work_activity.archive_stale_work_periods(keep_sessions)
    
    def get_work_period_analytics(self, project_path: str, days: int = 30) -> Dict[str, Any]:
        """Get work activity analytics (replaces session analytics)."""
        return self.work_activity.get_work_period_analytics(project_path, days)
    
    # ================================================================
    # Initialization Tracking Methods
    # ================================================================
    
    def start_initialization(self, session_id: str, total_files_discovered: int) -> bool:
        """Start file metadata initialization tracking."""
        return self.initialization.start_initialization(session_id, total_files_discovered)
    
    def update_initialization_phase(self, session_id: str, phase: str) -> bool:
        """Update initialization phase."""
        return self.initialization.update_initialization_phase(session_id, phase)
    
    def complete_initialization(self, session_id: str) -> bool:
        """Mark initialization as complete."""
        return self.initialization.complete_initialization(session_id)
    
    def get_initialization_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get initialization status and progress."""
        return self.initialization.get_initialization_status(session_id)
    
    def get_sessions_needing_initialization(self) -> List[Dict[str, Any]]:
        """Get sessions with incomplete initialization that can be resumed."""
        return self.initialization.get_sessions_needing_initialization()
    
    def increment_files_processed(self, session_id: str) -> bool:
        """Increment the files processed counter."""
        return self.initialization.increment_files_processed(session_id)
    
    def reset_initialization(self, session_id: str) -> bool:
        """Reset initialization progress (requires confirmation in calling code)."""
        return self.initialization.reset_initialization(session_id)
    
    def get_initialization_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get initialization analytics across all sessions."""
        return self.initialization.get_initialization_analytics(days)
    
    # ================================================================
    # Analytics Methods
    # ================================================================
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get overall session statistics."""
        return self.analytics.get_session_statistics()
    
    def log_context_escalation(self, session_id: str, from_mode: str, to_mode: str, 
                              reason: str, theme_name: str = None, task_id: str = None):
        """Log context escalation event for analytics."""
        return self.analytics.log_context_escalation(
            session_id, from_mode, to_mode, reason, theme_name, task_id
        )
    
    def get_session_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive session analytics."""
        return self.analytics.get_session_analytics(days)
    
    def get_session_analytics_enhanced(self, project_path: str, days: int = 30) -> Dict[str, Any]:
        """Get enhanced session analytics for a specific project."""
        return self.analytics.get_session_analytics_enhanced(project_path, days)
    
    # ================================================================
    # File and Task Tracking Methods
    # ================================================================
    
    def log_file_modification(self, session_id: str, file_path: str, file_type: str, 
                             modification_type: str, details: Dict[str, Any] = None) -> bool:
        """Log file modification for tracking and analytics."""
        return self.file_task.log_file_modification(
            session_id, file_path, file_type, modification_type, details
        )
    
    def get_file_modifications(self, session_id: str = None, file_type: str = None, 
                              days: int = 7) -> List[Dict[str, Any]]:
        """Get file modifications with optional filters."""
        return self.file_task.get_file_modifications(session_id, file_type, days)
    
    def record_task_completion(self, session_id: str, task_id: str, milestone_id: str = None,
                              theme_name: str = None, completion_data: Dict[str, Any] = None,
                              files_modified: List[str] = None) -> bool:
        """Record task completion with metrics."""
        return self.file_task.record_task_completion(
            session_id, task_id, milestone_id, theme_name, completion_data, files_modified
        )
    
    def get_task_metrics(self, theme_name: str = None, milestone_id: str = None,
                        days: int = 30) -> Dict[str, Any]:
        """Get task completion metrics and analytics."""
        return self.file_task.get_task_metrics(theme_name, milestone_id, days)
    
    # ================================================================
    # Boot Context Methods
    # ================================================================
    
    def get_boot_context(self, project_path: str) -> Dict[str, Any]:
        """Get comprehensive boot context for session restoration."""
        return self.boot_context.get_boot_context(project_path)