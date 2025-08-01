"""
Database package for AI Project Manager
Provides SQLite database functionality for persistent storage and advanced intelligence.
"""

from .db_manager import DatabaseManager
from .session_queries import SessionQueries
from .task_status_queries import TaskStatusQueries
from .theme_flow_queries import ThemeFlowQueries
from .file_metadata_queries import FileMetadataQueries
from .user_preference_queries import UserPreferenceQueries
from .event_queries import EventQueries

__all__ = [
    'DatabaseManager', 
    'SessionQueries',
    'TaskStatusQueries',
    'ThemeFlowQueries', 
    'FileMetadataQueries',
    'UserPreferenceQueries',
    'EventQueries'
]

# Version info
__version__ = '2.0.0'  # Updated for Phase 5 Advanced Intelligence