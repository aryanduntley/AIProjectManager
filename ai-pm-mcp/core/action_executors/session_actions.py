"""
Session Action Executor

Handles session management actions for directive execution.
"""

import logging
from typing import Dict, Any
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


class SessionActionExecutor(BaseActionExecutor):
    """Executes session management actions using existing session infrastructure."""
    
    def get_supported_actions(self) -> list[str]:
        """Get list of session action types this executor supports."""
        return [
            "initialize_session",
            "restore_session_context",
            "save_session_summary"
        ]
    
    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a session action."""
        if action_type == "initialize_session":
            return await self._execute_initialize_session(parameters)
        elif action_type == "restore_session_context":
            return await self._execute_restore_session_context(parameters)
        elif action_type == "save_session_summary":
            return await self._execute_save_session_summary(parameters)
        else:
            return self._create_error_result(f"Unknown session action type: {action_type}")
    
    async def _execute_initialize_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute initialize session action using existing SessionQueries."""
        if not self.session_queries:
            return self._create_failed_result(
                "No session queries available - cannot initialize session",
                "initialize_session",
                parameters
            )
        
        try:
            context = parameters.get("context", {})
            project_path = context.get("project_path", "")
            
            # Start session using existing method
            session_id = self.session_queries.start_session("directive_session_start")
            
            # Save initial context snapshot
            session_context_id = None
            if context:
                session_context_id = self.session_queries.context.save_context_snapshot(
                    project_path=project_path,
                    context_data=context,
                    context_type="session_initialization"
                )
            
            return self._create_success_result(
                "Session initialized successfully",
                session_id=session_id,
                session_context_id=session_context_id
            )
            
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return self._create_error_result(f"Session initialization failed: {str(e)}")
    
    async def _execute_restore_session_context(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute restore session context action using existing SessionQueries."""
        if not self.session_queries:
            return self._create_failed_result(
                "No session queries available - cannot restore session context",
                "restore_session_context", 
                parameters
            )
        
        try:
            session_data = parameters.get("session_data", {})
            project_path = parameters.get("project_path", "")
            
            # Get recent boot context using existing method
            boot_context = self.session_queries.boot_context.get_boot_context(project_path)
            
            return self._create_success_result(
                "Session context restored successfully",
                boot_context=boot_context,
                provided_session_data=session_data
            )
            
        except Exception as e:
            logger.error(f"Error restoring session context: {e}")
            return self._create_error_result(f"Session context restoration failed: {str(e)}")
    
    async def _execute_save_session_summary(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute save session summary action using existing SessionQueries."""
        if not self.session_queries:
            return self._create_failed_result(
                "No session queries available - cannot save session summary",
                "save_session_summary",
                parameters
            )
        
        try:
            summary = parameters.get("summary", {})
            project_path = parameters.get("project_path", "")
            
            # Save as context snapshot using existing method
            session_context_id = self.session_queries.context.save_context_snapshot(
                project_path=project_path,
                context_data=summary,
                context_type="session_summary"
            )
            
            # Record work activity for the summary
            self.session_queries.work_activity.record_work_activity(
                project_path=project_path,
                activity_type="session_summary_saved",
                activity_data=summary,
                session_context_id=session_context_id
            )
            
            return self._create_success_result(
                "Session summary saved successfully",
                session_context_id=session_context_id,
                summary_keys=list(summary.keys())
            )
            
        except Exception as e:
            logger.error(f"Error saving session summary: {e}")
            return self._create_error_result(f"Session summary save failed: {str(e)}")