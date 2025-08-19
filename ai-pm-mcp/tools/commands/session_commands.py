#!/usr/bin/env python3
"""
Session Command Handlers

Handles session management commands like pause and resume.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from .base_command import BaseCommandHandler

logger = logging.getLogger(__name__)


class SessionCommandHandler(BaseCommandHandler):
    """Handles session-related commands."""
    
    async def execute_pause(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-pause command - find suitable stopping point and prepare for clean resume."""
        try:
            # Trigger the work pause hook on the server
            if self.server_instance and hasattr(self.server_instance, '_on_work_pause'):
                logger.info("Executing work pause directive")
                result = await self.server_instance._on_work_pause()
                
                if result and "error" not in result:
                    actions_taken = result.get('actions_taken', [])
                    
                    # Format the response based on what actions were taken
                    pause_response = {
                        "type": "success",
                        "message": "Work pause completed successfully",
                        "summary": "AI Project Manager has found a suitable stopping point and prepared the project for clean resumption",
                        "actions_performed": actions_taken,
                        "cleanup_details": {
                            "subtasks_checked": "All completed subtasks have been marked and archived",
                            "project_data_updated": "All project management data has been synchronized",
                            "context_preserved": "Session context has been saved for seamless resumption",
                            "database_synchronized": "All organizational files and database records updated"
                        },
                        "resume_preparation": {
                            "status": "Ready for /aipm-resume",
                            "next_session_readiness": "Full project context will be automatically restored",
                            "recommendations": [
                                "Use /aipm-resume to continue work in next session",
                                "Use /aipm-status to check project state when resuming",
                                "Active tasks and progress are preserved"
                            ]
                        }
                    }
                    
                    return json.dumps(pause_response, indent=2)
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
                    return json.dumps({
                        "type": "error",
                        "message": f"Work pause failed: {error_msg}",
                        "suggestion": "Try /aipm-status to check current project state"
                    }, indent=2)
            else:
                return json.dumps({
                    "type": "error", 
                    "message": "Work pause functionality not available - server instance not properly initialized",
                    "suggestion": "Try restarting the MCP server"
                }, indent=2)
                
        except Exception as e:
            logger.error(f"Error in execute_pause: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-pause: {str(e)}",
                "suggestion": "Check server logs for details"
            }, indent=2)
            
    async def _trigger_pause_directive(self, pause_context: Dict[str, Any]):
        """Trigger workflow completion directive for pause operation."""
        workflow_context = {
            "workflow_type": "session_pause",
            "command": "/aipm-pause", 
            "operation_details": pause_context,
            "result": "pause_completed"
        }
        await self._trigger_workflow_directive(workflow_context, "sessionManagement")