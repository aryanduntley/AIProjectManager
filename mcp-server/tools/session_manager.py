"""
Session management tools for the AI Project Manager MCP Server.

Handles session persistence, context snapshots, and session analytics.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.mcp_api import ToolDefinition
from core.git_integration import GitIntegrationManager
from database.session_queries import SessionQueries
from database.file_metadata_queries import FileMetadataQueries
from database.git_queries import GitQueries

logger = logging.getLogger(__name__)


class SessionManager:
    """Tools for session management and persistence."""
    
    def __init__(self, session_queries: Optional[SessionQueries] = None, 
                 file_metadata_queries: Optional[FileMetadataQueries] = None,
                 git_queries: Optional[GitQueries] = None,
                 db_manager = None):
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
        self.git_queries = git_queries
        self.db_manager = db_manager
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all session management tools."""
        return [
            ToolDefinition(
                name="session_start",
                description="Start a new session or resume an existing session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "context_mode": {
                            "type": "string",
                            "enum": ["theme-focused", "theme-expanded", "project-wide"],
                            "description": "Context loading mode for the session",
                            "default": "theme-focused"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Existing session ID to resume (optional)"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.start_session
            ),
            ToolDefinition(
                name="session_save_context",
                description="Save current session context snapshot",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to save context for"
                        },
                        "loaded_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Currently loaded themes"
                        },
                        "loaded_flows": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Currently loaded flow files"
                        },
                        "files_accessed": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Files accessed in this session"
                        }
                    },
                    "required": ["session_id", "loaded_themes"]
                },
                handler=self.save_context_snapshot
            ),
            ToolDefinition(
                name="session_get_context",
                description="Get current session context and history",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to get context for"
                        }
                    },
                    "required": ["session_id"]
                },
                handler=self.get_session_context
            ),
            ToolDefinition(
                name="session_update_activity",
                description="Update session activity and active tasks/themes",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to update"
                        },
                        "active_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Currently active themes"
                        },
                        "active_tasks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Currently active task IDs"
                        },
                        "active_sidequests": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Currently active sidequest IDs"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Session notes or updates"
                        }
                    },
                    "required": ["session_id"]
                },
                handler=self.update_session_activity
            ),
            ToolDefinition(
                name="session_list_recent",
                description="List recent sessions for a project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of sessions to return",
                            "default": 10
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.list_recent_sessions
            ),
            ToolDefinition(
                name="session_get_analytics",
                description="Get session analytics and metrics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze",
                            "default": 30
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_session_analytics
            ),
            ToolDefinition(
                name="session_end",
                description="End a session and update final status",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to end"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["completed", "paused", "terminated"],
                            "description": "Final session status",
                            "default": "completed"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Session completion summary"
                        }
                    },
                    "required": ["session_id"]
                },
                handler=self.end_session
            ),
            ToolDefinition(
                name="session_boot_with_git_detection",
                description="Enhanced session boot with Git change detection and organizational reconciliation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "context_mode": {
                            "type": "string",
                            "enum": ["theme-focused", "theme-expanded", "project-wide"],
                            "description": "Context loading mode for the session",
                            "default": "theme-focused"
                        },
                        "force_git_check": {
                            "type": "boolean",
                            "description": "Force Git change detection even if session exists",
                            "default": False
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.boot_session_with_git_detection
            )
        ]
    
    async def start_session(self, arguments: Dict[str, Any]) -> str:
        """Start a new session or resume an existing session."""
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
            
            # Log session creation
            if self.file_metadata_queries:
                self.file_metadata_queries.log_file_modification(
                    file_path=f"session:{session_id}",
                    file_type="session",
                    operation="create",
                    session_id=session_id,
                    details={"project_path": project_path, "context_mode": context_mode}
                )
            
            return f"Started new session {session_id} for project {project_path}. Context mode: {context_mode}"
            
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
    
    async def list_recent_sessions(self, arguments: Dict[str, Any]) -> str:
        """List recent sessions for a project."""
        try:
            project_path = arguments["project_path"]
            limit = arguments.get("limit", 10)
            
            if not self.session_queries:
                return "Database not available. Session management requires database connection."
            
            # Get recent sessions
            sessions = await self.session_queries.get_recent_sessions(project_path, limit)
            
            if not sessions:
                return f"No sessions found for project {project_path}"
            
            session_list = []
            for session in sessions:
                session_info = {
                    "session_id": session["session_id"],
                    "start_time": session["start_time"],
                    "last_activity": session["last_activity"],
                    "status": session["status"],
                    "context_mode": session["context_mode"],
                    "active_themes": json.loads(session.get("active_themes", "[]")),
                    "active_tasks": json.loads(session.get("active_tasks", "[]"))
                }
                session_list.append(session_info)
            
            return f"Recent sessions for {project_path}:\n\n{json.dumps(session_list, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error listing recent sessions: {e}")
            return f"Error listing recent sessions: {str(e)}"
    
    async def get_session_analytics(self, arguments: Dict[str, Any]) -> str:
        """Get session analytics and metrics."""
        try:
            project_path = arguments["project_path"]
            days = arguments.get("days", 30)
            
            if not self.session_queries:
                return "Database not available. Session management requires database connection."
            
            # Get analytics
            analytics = await self.session_queries.get_session_analytics(project_path, days)
            
            return f"Session analytics for {project_path} (last {days} days):\n\n{json.dumps(analytics, indent=2, default=str)}"
            
        except Exception as e:
            logger.error(f"Error getting session analytics: {e}")
            return f"Error getting session analytics: {str(e)}"
    
    async def end_session(self, arguments: Dict[str, Any]) -> str:
        """End a session and update final status."""
        try:
            session_id = arguments["session_id"]
            status = arguments.get("status", "completed")
            summary = arguments.get("summary")
            
            if not self.session_queries:
                return "Database not available. Session management requires database connection."
            
            # End session
            await self.session_queries.end_session(session_id, status)
            
            # Log session ending
            if self.file_metadata_queries and summary:
                self.file_metadata_queries.log_file_modification(
                    file_path=f"session:{session_id}",
                    file_type="session",
                    operation="update",
                    session_id=session_id,
                    details={"status": status, "summary": summary}
                )
            
            return f"Session {session_id} ended with status: {status}"
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return f"Error ending session: {str(e)}"
    
    async def boot_session_with_git_detection(self, arguments: Dict[str, Any]) -> str:
        """
        Enhanced session boot with Git change detection and organizational reconciliation.
        This implements the enhanced boot sequence from the unified Git implementation plan.
        """
        try:
            project_path = Path(arguments["project_path"])
            context_mode = arguments.get("context_mode", "theme-focused")
            force_git_check = arguments.get("force_git_check", False)
            
            if not self.db_manager or not self.git_queries:
                return "Git integration not available. Database and Git queries required."
            
            # Initialize Git integration manager
            git_manager = GitIntegrationManager(project_path, self.db_manager)
            
            # Phase 1: Instance Identification
            instance_type = self._identify_instance_type(project_path)
            
            # Phase 2: Git Change Detection (Main instance only)
            git_changes = None
            if instance_type == "main" or force_git_check:
                git_changes = git_manager.detect_project_code_changes()
                
                if git_changes.get("success") and git_changes.get("changes_detected"):
                    logger.info(f"Git changes detected: {git_changes['change_summary']}")
                else:
                    logger.info("No Git changes detected since last session")
            
            # Phase 3: Organizational Reconciliation (if changes detected)
            reconciliation_result = None
            if git_changes and git_changes.get("reconciliation_needed"):
                reconciliation_result = git_manager.reconcile_organizational_state_with_code(git_changes)
                logger.info(f"Organizational reconciliation: {reconciliation_result.get('message', 'Completed')}")
            
            # Phase 4: Standard Session Boot
            session_result = await self.start_session({
                "project_path": str(project_path),
                "context_mode": context_mode
            })
            
            # Phase 5: Enhanced Boot Report
            boot_report = self._generate_boot_report(
                instance_type, git_changes, reconciliation_result, session_result
            )
            
            return boot_report
            
        except Exception as e:
            logger.error(f"Error in Git-aware session boot: {e}")
            return f"Error in Git-aware session boot: {str(e)}"
    
    def _identify_instance_type(self, project_path: Path) -> str:
        """
        Identify if this is a main instance or branch instance based on marker files.
        Returns 'main', 'branch', or 'unknown'
        """
        project_mgmt_dir = project_path / "projectManagement"
        
        # Check for main instance marker
        if (project_mgmt_dir / ".mcp-instance-main").exists():
            return "main"
        
        # Check for branch instance marker
        if (project_mgmt_dir / ".mcp-branch-info.json").exists():
            return "branch"
        
        # Default to main if no markers found (legacy behavior)
        return "main"
    
    def _generate_boot_report(self, instance_type: str, git_changes: Optional[Dict], 
                             reconciliation_result: Optional[Dict], session_result: str) -> str:
        """Generate comprehensive boot report with Git integration status"""
        
        report_lines = [
            "=== AI Project Manager Session Boot Report ===",
            f"Instance Type: {instance_type.upper()}",
            ""
        ]
        
        # Git Integration Status
        if git_changes:
            if git_changes.get("success"):
                if git_changes.get("changes_detected"):
                    report_lines.extend([
                        "🔄 Git Changes Detected:",
                        f"  • {git_changes.get('change_summary', 'Changes found')}",
                        f"  • Current Hash: {git_changes.get('current_hash', 'Unknown')[:8]}...",
                        f"  • Last Known: {git_changes.get('last_known_hash', 'None')[:8] if git_changes.get('last_known_hash') else 'None'}...",
                        f"  • Affected Files: {len(git_changes.get('affected_files', []))}",
                        ""
                    ])
                    
                    if git_changes.get("affected_themes"):
                        report_lines.extend([
                            "📋 Affected Themes:",
                            *[f"  • {theme}" for theme in git_changes.get("affected_themes", [])],
                            ""
                        ])
                else:
                    report_lines.extend([
                        "✅ No Git changes detected since last session",
                        ""
                    ])
            else:
                report_lines.extend([
                    f"❌ Git change detection failed: {git_changes.get('error', 'Unknown error')}",
                    ""
                ])
        elif instance_type == "branch":
            report_lines.extend([
                "🔀 Branch Instance: Git change detection skipped",
                ""
            ])
        
        # Organizational Reconciliation Status
        if reconciliation_result:
            if reconciliation_result.get("success"):
                report_lines.extend([
                    "🔧 Organizational Reconciliation:",
                    f"  • Action: {reconciliation_result.get('action', 'None')}",
                    f"  • Status: {reconciliation_result.get('message', 'Completed')}",
                    ""
                ])
                
                if reconciliation_result.get("requires_user_review"):
                    report_lines.extend([
                        "⚠️  User Review Required:",
                        "  • Significant code changes detected",
                        "  • Please review organizational state alignment",
                        ""
                    ])
        
        # Session Status
        report_lines.extend([
            "📊 Session Status:",
            f"  {session_result}",
            "",
            "=== Boot Complete ==="
        ])
        
        return "\n".join(report_lines)