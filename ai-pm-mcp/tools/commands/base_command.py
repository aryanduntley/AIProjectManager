#!/usr/bin/env python3
"""
Base Command Handler

Provides common functionality for all command categories.
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BaseCommandHandler:
    """Base class for command handlers with common directive integration."""
    
    def __init__(self, db_manager=None, config_manager=None, server_instance=None):
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.server_instance = server_instance
    
    async def _trigger_workflow_directive(self, workflow_context: Dict[str, Any], directive_key: str = "workflowManagement"):
        """Common method to trigger workflow completion directives."""
        if self.server_instance and hasattr(self.server_instance, 'on_workflow_completion'):
            workflow_context["timestamp"] = datetime.now().isoformat()
            try:
                await self.server_instance.on_workflow_completion(workflow_context, directive_key)
            except Exception as hook_error:
                logger.warning(f"Directive hook failed: {hook_error}")
    
    def _get_command_suggestions(self, state: str) -> list:
        """Get command suggestions based on project state."""
        if state == "no_structure":
            return ["aipm-init", "aipm-analyze"]
        elif state == "partial":
            return ["aipm-init", "aipm-status", "aipm-analyze"]
        elif state == "complete":
            return ["aipm-resume", "aipm-tasks", "aipm-status"]
        elif state == "git_history_found":
            return ["aipm-init", "aipm-resume", "aipm-branch"]
        else:
            return ["aipm-help", "aipm-status", "aipm-analyze"]