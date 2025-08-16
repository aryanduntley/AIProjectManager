#!/usr/bin/env python3
"""
Database Management Command Handlers

Handles database backup, maintenance, and statistics commands.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from .base_command import BaseCommandHandler

logger = logging.getLogger(__name__)


class DatabaseCommandHandler(BaseCommandHandler):
    """Handles database management commands."""
    
    async def execute_backup(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-backup command."""
        try:
            from ...tools.database_tools import DatabaseTools
            database_tools = DatabaseTools(self.db_manager, self.config_manager)
            
            arguments = {
                'project_path': str(project_path),
                'backup_name': args.get('backup_name', '')
            }
            
            result = await database_tools.backup_database(arguments)
            
            # Add directive hook after database backup workflow completion
            await self._trigger_workflow_directive({
                "trigger": "workflow_completion",
                "workflow_type": "database_backup",
                "command": "/aipm-backup",
                "project_path": str(project_path),
                "backup_name": args.get('backup_name', '')
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in _execute_backup: {e}")
            return f"❌ Error creating database backup: {str(e)}"

    async def execute_maintenance(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-maintenance command."""
        try:
            from ...tools.database_tools import DatabaseTools
            database_tools = DatabaseTools(self.db_manager, self.config_manager)
            
            arguments = {
                'project_path': str(project_path),
                'keep_modifications': args.get('keep_modifications', 500),
                'keep_sessions': args.get('keep_sessions', 20),
                'vacuum': args.get('vacuum', True)
            }
            
            result = await database_tools.database_maintenance(arguments)
            
            # Add directive hook after database maintenance workflow completion
            await self._trigger_workflow_directive({
                "trigger": "workflow_completion", 
                "workflow_type": "database_maintenance",
                "command": "/aipm-maintenance",
                "project_path": str(project_path),
                "maintenance_options": {
                    "keep_modifications": args.get('keep_modifications', 500),
                    "keep_sessions": args.get('keep_sessions', 20),
                    "vacuum": args.get('vacuum', True)
                }
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in _execute_maintenance: {e}")
            return f"❌ Error running database maintenance: {str(e)}"

    async def execute_db_stats(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-db-stats command."""
        try:
            from ...tools.database_tools import DatabaseTools
            database_tools = DatabaseTools(self.db_manager, self.config_manager)
            
            arguments = {'project_path': str(project_path)}
            result = await database_tools.database_statistics(arguments)
            return result
            
        except Exception as e:
            logger.error(f"Error in execute_db_stats: {e}")
            return f"❌ Error getting database statistics: {str(e)}"