"""
Database package for AI Project Manager
Provides SQLite database functionality for persistent storage.
"""

from .db_manager import DatabaseManager
from .theme_flow_queries import ThemeFlowQueries
from .session_queries import SessionQueries

__all__ = ['DatabaseManager', 'ThemeFlowQueries', 'SessionQueries']

# Version info
__version__ = '1.0.0'