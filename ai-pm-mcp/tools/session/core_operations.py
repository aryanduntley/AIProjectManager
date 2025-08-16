"""
Core session operations for the AI Project Manager.

Handles session creation, context management, and activity updates.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ...database.session_queries import SessionQueries
from ...database.file_metadata_queries import FileMetadataQueries

logger = logging.getLogger(__name__)


class CoreOperations:
    """Core session management operations."""
    
    def __init__(self, session_queries: Optional[SessionQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None,
                 server_instance=None):
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
        self.server_instance = server_instance

    async def start_work_period(self, arguments: Dict[str, Any]) -> str:
        """Start a new work period with activity tracking."""
        try:
            project_path = arguments["project_path"]
            context_mode = arguments.get("context_mode", "theme-focused")
            existing_session_id = arguments.get("session_id")
            
            if not self.session_queries:
                return "Database not available. Session management requires database connection."
            
            # Check if resuming existing session
            if existing_session_id:
                session = await self.session_queries.get_session(existing_session_id)
                if not session:
                    return f"Session {existing_session_id} not found."
                
                # Update session activity
                await self.session_queries.update_last_activity(existing_session_id)
                return f"Resumed session {existing_session_id}. Context mode: {session['context_mode']}, Active themes: {session['active_themes']}"
            
            # Create new session
            session_id = self.session_queries.start_session(
                project_path=project_path,
                context_mode=context_mode
            )
            
            # Check for incomplete file metadata initialization
            from .initialization_operations import InitializationOperations
            init_ops = InitializationOperations(self.session_queries, self.file_metadata_queries)
            initialization_status = await init_ops.check_initialization_status(session_id)
            
            # Check for team member scenario BEFORE creating ai-pm-org-main
            try:
                from ...core.branch_manager import GitBranchManager
                branch_manager = GitBranchManager(project_path)
                
                # Check if team member scenario FIRST (before creating ai-pm-org-main)
                current_branch, created_new = branch_manager.initialize_for_team_member()
                
                # If NOT a team member, ensure AI main branch exists
                if not created_new:
                    branch_manager.ensure_ai_main_branch_exists()
                    current_branch = branch_manager.get_current_branch()
                
                branch_info = ""
                if created_new:
                    branch_info = f" Team member detected - created work branch: {current_branch}"
                else:
                    branch_info = f" Working on branch: {current_branch}"
                    
            except Exception as e:
                logger.warning(f"Error during team member detection: {e}")
                branch_info = " (Branch detection failed - working on current branch)"
            
            # Log session creation
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=f"session:{session_id}",
                    file_type="session",
                    operation="create",
                    session_id=session_id,
                    details={"project_path": project_path, "context_mode": context_mode, "branch_info": branch_info}
                )
            
            # Add directive hook for server notification
            if self.server_instance and hasattr(self.server_instance, 'on_session_operation_complete'):
                hook_context = {
                    "trigger": "session_start_complete",
                    "operation_type": "session_start",
                    "session_id": session_id,
                    "project_path": project_path,
                    "context_mode": context_mode,
                    "branch_info": branch_info,
                    "timestamp": datetime.now().isoformat()
                }
                try:
                    await self.server_instance.on_session_operation_complete(hook_context, "sessionManagement")
                except Exception as e:
                    logger.warning(f"Session start hook failed: {e}")
            
            return f"Started new session {session_id} for project {project_path}. Context mode: {context_mode}{branch_info}{initialization_status}"
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return f"Error starting session: {str(e)}"

    async def save_context_snapshot(self, arguments: Dict[str, Any]) -> str:
        """Save current session context snapshot."""
        try:
            session_id = arguments["session_id"]
            loaded_themes = arguments["loaded_themes"]
            loaded_flows = arguments.get("loaded_flows", [])
            files_accessed = arguments.get("files_accessed", [])
            
            if not self.session_queries:
                return "Database not available. Session management requires database connection."
            
            # Save context snapshot
            await self.session_queries.save_context_snapshot(
                session_id=session_id,
                loaded_themes=loaded_themes,
                loaded_flows=loaded_flows,
                files_accessed=files_accessed
            )
            
            return f"Context snapshot saved for session {session_id}. Themes: {len(loaded_themes)}, Flows: {len(loaded_flows)}, Files: {len(files_accessed)}"
            
        except Exception as e:
            logger.error(f"Error saving context snapshot: {e}")
            return f"Error saving context snapshot: {str(e)}"

    async def get_session_context(self, arguments: Dict[str, Any]) -> str:
        """Get current session context and history."""
        try:
            session_id = arguments["session_id"]
            
            if not self.session_queries:
                return "Database not available. Session management requires database connection."
            
            # Get session details
            session = await self.session_queries.get_session(session_id)
            if not session:
                return f"Session {session_id} not found."
            
            # Get context snapshots
            context_snapshots = await self.session_queries.get_context_snapshots(session_id)
            
            # Get session summary
            session_summary = await self.session_queries.get_session_summary(session_id)
            
            context_info = {
                "session": session,
                "context_snapshots": context_snapshots,
                "session_summary": session_summary
            }
            
            return f"Session context for {session_id}:\n\n{json.dumps(context_info, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error getting session context: {e}")
            return f"Error getting session context: {str(e)}"

    async def update_session_activity(self, arguments: Dict[str, Any]) -> str:
        """Update session activity and active tasks/themes."""
        try:
            session_id = arguments["session_id"]
            active_themes = arguments.get("active_themes", [])
            active_tasks = arguments.get("active_tasks", [])
            active_sidequests = arguments.get("active_sidequests", [])
            notes = arguments.get("notes")
            
            if not self.session_queries:
                return "Database not available. Session management requires database connection."
            
            # Update session
            await self.session_queries.update_session_activity(
                session_id=session_id,
                active_themes=active_themes,
                active_tasks=active_tasks,
                active_sidequests=active_sidequests,
                notes=notes
            )
            
            return f"Session {session_id} updated. Active themes: {len(active_themes)}, Tasks: {len(active_tasks)}, Sidequests: {len(active_sidequests)}"
            
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
            return f"Error updating session activity: {str(e)}"