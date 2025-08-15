"""
Modular Action Executor for DirectiveProcessor.

Executes AI-determined actions via existing MCP tools using specialized action executors
for different categories of actions. This modular approach keeps the codebase manageable
and allows for focused implementation of each action category.
"""

import logging
from typing import Dict, Any, List, Optional

from .action_executors import (
    DatabaseActionExecutor,
    SessionActionExecutor, 
    TaskActionExecutor,
    ProjectActionExecutor,
    FileActionExecutor,
    LoggingActionExecutor
)

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Modular action executor that delegates to specialized executors by category.
    
    This class coordinates between the DirectiveProcessor's AI-determined actions 
    and specialized action executors for different categories (database, session,
    task, project, file, logging).
    """
    
    def __init__(self, mcp_tools: Optional[Dict[str, Any]] = None, db_manager=None):
        """
        Initialize ActionExecutor with specialized action executors.
        
        Args:
            mcp_tools: Dictionary of MCP tool categories and instances
            db_manager: DatabaseManager instance for database operations
        """
        self.mcp_tools = mcp_tools or {}
        self.db_manager = db_manager
        
        # Initialize specialized action executors
        self.database_executor = DatabaseActionExecutor(db_manager, mcp_tools)
        self.session_executor = SessionActionExecutor(db_manager, mcp_tools)
        self.task_executor = TaskActionExecutor(db_manager, mcp_tools)
        self.project_executor = ProjectActionExecutor(db_manager, mcp_tools)
        self.file_executor = FileActionExecutor(db_manager, mcp_tools)
        self.logging_executor = LoggingActionExecutor(db_manager, mcp_tools)
        
        # Create action type mapping
        self.action_mapping = self._build_action_mapping()
        
        logger.info(f"Modular ActionExecutor initialized with {len(self.action_mapping)} supported actions")
    
    def _build_action_mapping(self) -> Dict[str, Any]:
        """Build mapping of action types to their respective executors."""
        mapping = {}
        
        # Database actions
        for action_type in self.database_executor.get_supported_actions():
            mapping[action_type] = self.database_executor
        
        # Session actions  
        for action_type in self.session_executor.get_supported_actions():
            mapping[action_type] = self.session_executor
            
        # Task actions
        for action_type in self.task_executor.get_supported_actions():
            mapping[action_type] = self.task_executor
            
        # Project actions
        for action_type in self.project_executor.get_supported_actions():
            mapping[action_type] = self.project_executor
            
        # File actions
        for action_type in self.file_executor.get_supported_actions():
            mapping[action_type] = self.file_executor
            
        # Logging actions
        for action_type in self.logging_executor.get_supported_actions():
            mapping[action_type] = self.logging_executor
        
        return mapping
    
    async def execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute a list of actions using specialized action executors.
        
        Args:
            actions: List of action dictionaries with type and parameters
            
        Returns:
            List of execution results for each action
        """
        if not actions:
            logger.debug("No actions to execute")
            return []
        
        logger.info(f"Executing {len(actions)} actions via modular executors")
        results = []
        
        for i, action in enumerate(actions):
            try:
                action_type = action.get("type", "unknown")
                parameters = action.get("parameters", {})
                
                logger.debug(f"Executing action {i+1}/{len(actions)}: {action_type}")
                
                # Find the appropriate executor for this action type
                executor = self.action_mapping.get(action_type)
                if executor:
                    result = await executor.execute_action(action_type, parameters)
                else:
                    result = {
                        "status": "error",
                        "error": f"Unknown action type: {action_type}",
                        "action_type": action_type
                    }
                
                results.append({
                    "action": action,
                    "result": result,
                    "success": result.get("status") in ["success"],
                    "index": i
                })
                
            except Exception as e:
                logger.error(f"Error executing action {i+1}: {action.get('type', 'unknown')}: {e}")
                results.append({
                    "action": action,
                    "error": str(e),
                    "success": False,
                    "index": i
                })
        
        successful_actions = sum(1 for r in results if r.get("success", False))
        logger.info(f"Action execution completed: {successful_actions}/{len(actions)} successful")
        
        return results
    
    def _initialize_database_queries(self):
        """Update database managers in all specialized executors."""
        if self.db_manager:
            self.database_executor.db_manager = self.db_manager
            self.database_executor._initialize_database_queries()
            
            self.session_executor.db_manager = self.db_manager
            self.session_executor._initialize_database_queries()
            
            self.task_executor.db_manager = self.db_manager
            self.task_executor._initialize_database_queries()
            
            self.project_executor.db_manager = self.db_manager
            self.project_executor._initialize_database_queries()
            
            self.file_executor.db_manager = self.db_manager
            self.file_executor._initialize_database_queries()
            
            self.logging_executor.db_manager = self.db_manager
            self.logging_executor._initialize_database_queries()
            
            logger.info("Updated all specialized executors with database manager")
    
    def set_mcp_tools(self, mcp_tools: Dict[str, Any]):
        """Update MCP tools references in all specialized executors."""
        self.mcp_tools = mcp_tools
        
        # Update all specialized executors
        self.database_executor.mcp_tools = mcp_tools
        self.database_executor._initialize_tool_references()
        
        self.session_executor.mcp_tools = mcp_tools
        self.session_executor._initialize_tool_references()
        
        self.task_executor.mcp_tools = mcp_tools
        self.task_executor._initialize_tool_references()
        
        self.project_executor.mcp_tools = mcp_tools
        self.project_executor._initialize_tool_references()
        
        self.file_executor.mcp_tools = mcp_tools
        self.file_executor._initialize_tool_references()
        
        self.logging_executor.mcp_tools = mcp_tools
        self.logging_executor._initialize_tool_references()
        
        logger.info(f"Updated all specialized executors with MCP tools: {list(mcp_tools.keys())}")
    
    def get_available_actions(self) -> List[str]:
        """Get list of all available action types across all executors."""
        return sorted(self.action_mapping.keys())
    
    def get_tool_status(self) -> Dict[str, bool]:
        """Get status of available tool categories (for compatibility)."""
        return {
            "database_executor": self.database_executor.db_manager is not None,
            "session_executor": self.session_executor.session_queries is not None,
            "task_executor": self.task_executor.task_status_queries is not None,
            "project_executor": self.project_executor.project_tools is not None,
            "file_executor": self.file_executor.file_tools is not None,
            "logging_executor": self.logging_executor.event_queries is not None
        }


# Utility function to create properly configured action executor
def create_action_executor(mcp_tools: Optional[Dict[str, Any]] = None, db_manager=None) -> ActionExecutor:
    """Create a properly configured ActionExecutor instance."""
    executor = ActionExecutor(mcp_tools, db_manager)
    
    # Check database integration status
    db_status = "with database" if db_manager else "without database"
    action_count = len(executor.get_available_actions())
    
    logger.info(f"Modular ActionExecutor created with {action_count} available actions {db_status}")
    
    return executor


if __name__ == "__main__":
    # Test basic functionality
    import asyncio
    
    async def test_action_executor():
        executor = create_action_executor()
        
        # Test available actions
        actions = executor.get_available_actions()
        print(f"Available actions: {actions}")
        
        # Test tool status
        status = executor.get_tool_status()
        print(f"Executor status: {status}")
        
        # Test basic action execution
        test_actions = [
            {
                "type": "log_directive_execution",
                "parameters": {
                    "directive_key": "test",
                    "trigger": "test_execution",
                    "timestamp": "now"
                }
            }
        ]
        
        results = await executor.execute_actions(test_actions)
        print(f"Test execution results: {results}")
    
    # Run test
    asyncio.run(test_action_executor())