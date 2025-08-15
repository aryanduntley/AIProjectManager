"""
Database Action Executor

Handles database-related actions for directive execution.
"""

import logging
from typing import Dict, Any
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


class DatabaseActionExecutor(BaseActionExecutor):
    """Executes database-related actions using existing database infrastructure."""
    
    def get_supported_actions(self) -> list[str]:
        """Get list of database action types this executor supports."""
        return [
            "update_database_file_metadata",
            "initialize_database", 
            "update_database_session"
        ]
    
    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a database action."""
        if action_type == "update_database_file_metadata":
            return await self._execute_update_database_file_metadata(parameters)
        elif action_type == "initialize_database":
            return await self._execute_initialize_database(parameters)
        elif action_type == "update_database_session":
            return await self._execute_update_database_session(parameters)
        else:
            return self._create_error_result(f"Unknown database action type: {action_type}")
    
    async def _execute_update_database_file_metadata(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update database file metadata action using existing FileMetadataQueries."""
        if not self.file_metadata_queries:
            return self._create_failed_result(
                "No file metadata queries available - database not properly initialized",
                "update_database_file_metadata",
                parameters
            )
        
        try:
            file_path = parameters.get("file_path", "")
            changes = parameters.get("changes", {})
            
            # Use existing create_or_update_file_metadata method
            metadata_to_update = changes.get("metadata", {})
            if "content_hash" in changes:
                metadata_to_update["content_hash"] = changes["content_hash"]
            if "line_count" in changes:
                metadata_to_update["line_count"] = changes["line_count"]
            if "file_size" in changes:
                metadata_to_update["file_size"] = changes["file_size"]
            
            success = self.file_metadata_queries.create_or_update_file_metadata(file_path, metadata_to_update)
            
            if success:
                # Log the file modification using existing logging
                self.file_metadata_queries.modification_logging.log_file_modification(
                    file_path=file_path,
                    file_type=changes.get("file_type", "code"),
                    operation="update",
                    details={"directive_driven": True, "changes": changes}
                )
                
                # Update theme associations if provided using existing method
                if "themes" in changes:
                    self.file_metadata_queries.update_file_theme_associations(file_path, changes["themes"])
                
                return self._create_success_result(
                    f"File metadata updated for {file_path}",
                    changes_applied=changes
                )
            else:
                return self._create_error_result(f"Failed to update metadata for {file_path}")
                
        except Exception as e:
            logger.error(f"Error updating file metadata: {e}")
            return self._create_error_result(str(e))
    
    async def _execute_initialize_database(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute initialize database action using existing database manager."""
        if not self.db_manager:
            return self._create_failed_result(
                "No database manager available - cannot initialize database",
                "initialize_database",
                parameters
            )
        
        try:
            fresh_init = parameters.get("fresh_init", False)
            
            if fresh_init:
                logger.info("Performing fresh database initialization")
            
            # Ensure schema is current using existing database manager
            self.db_manager.ensure_schema_current()
            
            # Start a session using existing session queries
            if self.session_queries:
                session_id = self.session_queries.start_session("directive_initialization")
                return self._create_success_result(
                    "Database initialized successfully",
                    fresh_init=fresh_init,
                    session_id=session_id
                )
            else:
                return self._create_success_result(
                    "Database schema initialized (session queries not available)",
                    fresh_init=fresh_init
                )
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return self._create_error_result(f"Database initialization failed: {str(e)}")
    
    async def _execute_update_database_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update database session action using existing SessionQueries."""
        if not self.session_queries:
            return self._create_failed_result(
                "No session queries available - database not properly initialized",
                "update_database_session",
                parameters
            )
        
        try:
            session_data = parameters.get("final_state", parameters)
            project_path = parameters.get("project_path", session_data.get("project_path", ""))
            
            # Save session context snapshot using existing method
            session_context_id = self.session_queries.context.save_context_snapshot(
                project_path=project_path,
                context_data=session_data,
                context_type="directive_update"
            )
            
            # Record work activity if this is from a directive using existing method
            if session_data.get("prepare_for_resume") or parameters.get("thorough_update"):
                self.session_queries.work_activity.record_work_activity(
                    project_path=project_path,
                    activity_type="directive_session_update",
                    activity_data=session_data,
                    session_context_id=session_context_id
                )
            
            return self._create_success_result(
                "Session data updated successfully",
                session_context_id=session_context_id,
                data_updated=list(session_data.keys())
            )
            
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return self._create_error_result(f"Session update failed: {str(e)}")