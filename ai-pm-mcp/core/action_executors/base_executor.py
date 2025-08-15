"""
Base Action Executor

Provides common functionality for all action executor modules.
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseActionExecutor(ABC):
    """Base class for action executors with common functionality."""
    
    def __init__(self, db_manager=None, mcp_tools: Optional[Dict[str, Any]] = None):
        """Initialize with database manager and MCP tools."""
        self.db_manager = db_manager
        self.mcp_tools = mcp_tools or {}
        self._initialize_database_queries()
        self._initialize_tool_references()
    
    def _initialize_database_queries(self):
        """Initialize database query instances."""
        if self.db_manager:
            from ...database.file_metadata_queries import FileMetadataQueries
            from ...database.session_queries import SessionQueries
            from ...database.task_status_queries import TaskStatusQueries
            from ...database.event_queries import EventQueries
            
            self.file_metadata_queries = FileMetadataQueries(self.db_manager)
            self.session_queries = SessionQueries(self.db_manager)
            self.task_status_queries = TaskStatusQueries(self.db_manager)
            self.event_queries = EventQueries(self.db_manager)
            
            logger.debug(f"{self.__class__.__name__} initialized with database access")
        else:
            self.file_metadata_queries = None
            self.session_queries = None
            self.task_status_queries = None
            self.event_queries = None
            logger.debug(f"{self.__class__.__name__} initialized without database access")
    
    def _initialize_tool_references(self):
        """Initialize references to MCP tool instances."""
        self.task_tools = self.mcp_tools.get("task_tools")
        self.project_tools = self.mcp_tools.get("project_tools") 
        self.log_tools = self.mcp_tools.get("log_tools")
        self.theme_tools = self.mcp_tools.get("theme_tools")
        self.database_tools = self.mcp_tools.get("database_tools")
        self.session_tools = self.mcp_tools.get("session_tools")
        self.file_tools = self.mcp_tools.get("file_tools")
        self.branch_tools = self.mcp_tools.get("branch_tools")
    
    @abstractmethod
    def get_supported_actions(self) -> list[str]:
        """Get list of action types this executor supports."""
        pass
    
    @abstractmethod
    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action of the supported types."""
        pass
    
    def _create_success_result(self, message: str, **kwargs) -> Dict[str, Any]:
        """Create standardized success result."""
        result = {
            "status": "success",
            "message": message
        }
        result.update(kwargs)
        return result
    
    def _create_error_result(self, error: str, action_type: str = None, **kwargs) -> Dict[str, Any]:
        """Create standardized error result."""
        result = {
            "status": "error", 
            "error": error
        }
        if action_type:
            result["action_type"] = action_type
        result.update(kwargs)
        return result
    
    def _create_failed_result(self, error: str, action_type: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized failure result (system not available)."""
        result = {
            "status": "failed",
            "error": error,
            "action_type": action_type
        }
        if parameters:
            result["parameters"] = parameters
        return result