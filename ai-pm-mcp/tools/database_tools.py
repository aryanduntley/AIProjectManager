"""
Database management tools for the AI Project Manager MCP Server.

Handles database backups, maintenance, cleanup, and optimization operations.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.mcp_api import ToolDefinition
from ..database.db_manager import DatabaseManager
from ..database.session_queries import SessionQueries
from ..database.file_metadata_queries import FileMetadataQueries
from ..database.event_queries import EventQueries
from ..utils.project_paths import get_project_management_path

logger = logging.getLogger(__name__)


class DatabaseTools:
    """Tools for database management operations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None, config_manager=None):
        self.tools = []
        self.db_manager = db_manager
        self.config_manager = config_manager
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all database management tools."""
        return [
            ToolDefinition(
                name="database_backup",
                description="Create a backup of the project database",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "backup_name": {
                            "type": "string",
                            "description": "Optional custom backup name (timestamp will be added if not provided)",
                            "default": ""
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.backup_database
            ),
            ToolDefinition(
                name="database_maintenance",
                description="Perform database maintenance including cleanup, archiving, and optimization",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "keep_modifications": {
                            "type": "integer", 
                            "description": "Number of most recent file modification records to keep",
                            "default": 500
                        },
                        "keep_sessions": {
                            "type": "integer",
                            "description": "Number of most recent work sessions to keep active per project", 
                            "default": 20
                        },
                        "vacuum": {
                            "type": "boolean",
                            "description": "Run database vacuum to reclaim space",
                            "default": True
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.database_maintenance
            ),
            ToolDefinition(
                name="database_stats",
                description="Get detailed database statistics and health information",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.database_statistics
            )
        ]

    async def backup_database(self, arguments: Dict[str, Any]) -> str:
        """Create a backup of the project database.
        
        Backups are saved to: projectManagement/database/backups/
        """
        try:
            project_path = Path(arguments["project_path"])
            backup_name = arguments.get("backup_name", "")
            
            # Get project management directory and database path
            project_mgmt_dir = get_project_management_path(project_path, self.config_manager)
            db_path = project_mgmt_dir / "project.db"
            
            if not db_path.exists():
                return f"Database not found at {db_path}. Initialize project first."
            
            # Create backup directory if it doesn't exist
            backup_dir = project_mgmt_dir / "database" / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if backup_name:
                backup_filename = f"{backup_name}_{timestamp}.db"
            else:
                backup_filename = f"project_backup_{timestamp}.db"
            
            backup_path = backup_dir / backup_filename
            
            # Create backup using SQLite backup API
            db_manager = DatabaseManager(str(project_path))
            success = db_manager.backup_database(str(backup_path))
            
            if success:
                # Get backup size
                backup_size_mb = backup_path.stat().st_size / (1024 * 1024)
                
                logger.info(f"Database backup created: {backup_path}")
                return f"""✅ Database backup created successfully!

**Backup Details:**
• File: {backup_filename}
• Location: {backup_dir}
• Size: {backup_size_mb:.2f} MB

**Backup Path:** `{backup_dir}/{backup_filename}`

Use this backup to restore your project database if needed."""
            else:
                return f"❌ Failed to create database backup. Check logs for details."
            
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return f"Error creating database backup: {str(e)}"

    async def database_maintenance(self, arguments: Dict[str, Any]) -> str:
        """Perform database maintenance including cleanup, archiving, and optimization."""
        try:
            project_path = Path(arguments["project_path"])
            keep_modifications = arguments.get("keep_modifications", 500)
            keep_sessions = arguments.get("keep_sessions", 20)
            vacuum = arguments.get("vacuum", True)
            
            # Get database path
            project_mgmt_dir = get_project_management_path(project_path, self.config_manager)
            db_path = project_mgmt_dir / "project.db"
            
            if not db_path.exists():
                return f"Database not found at {db_path}. Initialize project first."
            
            # 🛡️ SAFETY: Automatic backup before maintenance
            backup_arguments = {
                'project_path': str(project_path),
                'backup_name': 'pre-maintenance'
            }
            backup_result = await self.backup_database(backup_arguments)
            
            # Check if backup failed
            if "❌" in backup_result:
                return f"""❌ **Maintenance Cancelled**

**Reason**: Pre-maintenance backup failed
**Error**: {backup_result}

**What to do**: 
1. Check database permissions
2. Ensure sufficient disk space
3. Try manual backup first: `/aipm-backup`

⚠️ **Safety First**: Maintenance includes permanent deletion of old file modification records. A backup is required before proceeding."""
            
            # Initialize database manager and queries
            db_manager = DatabaseManager(str(project_path))
            event_queries = EventQueries(db_manager)
            file_metadata_queries = FileMetadataQueries(db_manager)
            session_queries = SessionQueries(db_manager)
            
            maintenance_results = [
                f"🛡️ **Safety backup created**: `pre-maintenance_[timestamp].db`"
            ]
            
            # 1. Archive old events
            archived_events = event_queries.archive_events()
            maintenance_results.append(f"📁 Archived {archived_events} old events")
            
            # 2. Clean up old file modifications (keep most recent)
            cleaned_modifications = file_metadata_queries.cleanup_old_modifications(keep_modifications)
            maintenance_results.append(f"🗑️ Cleaned up {cleaned_modifications} old file modification records (kept {keep_modifications} most recent)")
            
            # 3. Archive old work sessions (keep most recent per project) 
            archived_sessions = session_queries.archive_stale_work_periods(keep_sessions)
            maintenance_results.append(f"📦 Archived {archived_sessions} old work sessions (kept {keep_sessions} most recent per project)")
            
            # 4. Database optimization
            if vacuum:
                db_size_before = db_path.stat().st_size / (1024 * 1024)
                db_manager.optimize_database()
                db_size_after = db_path.stat().st_size / (1024 * 1024)
                space_saved = db_size_before - db_size_after
                maintenance_results.append(f"⚡ Database optimized (saved {space_saved:.2f} MB)")
            
            # 5. Get database statistics
            stats = self._get_database_statistics(db_manager)
            
            logger.info(f"Database maintenance completed for {project_path}")
            
            result = f"✅ **Database maintenance completed!**\n\n" + "\n".join(maintenance_results)
            result += f"\n\n📊 **Database Statistics:**\n"
            for table, count in stats.items():
                result += f"• {table}: {count} records\n"
            
            result += f"""\n\n🗑️ **Cleanup Summary:**
• **File modification records**: Kept {keep_modifications} most recent, permanently deleted older ones
• **Work sessions**: Kept {keep_sessions} most recent per project, archived older ones
• **Events**: Archived old events (preserved but marked inactive)
• **Database size**: Optimized with VACUUM

🛡️ **Safety Backup Location:**
`{project_mgmt_dir}/database/backups/pre-maintenance_[timestamp].db`

💡 **Next Steps:**
• Test your project to ensure everything works correctly
• If satisfied with maintenance, you can delete the pre-maintenance backup
• If issues arise, restore from the pre-maintenance backup"""
            
            return result
            
        except Exception as e:
            logger.error(f"Error during database maintenance: {e}")
            return f"Error during database maintenance: {str(e)}"

    async def database_statistics(self, arguments: Dict[str, Any]) -> str:
        """Get detailed database statistics and health information."""
        try:
            project_path = Path(arguments["project_path"])
            
            # Get database path
            project_mgmt_dir = get_project_management_path(project_path, self.config_manager)
            db_path = project_mgmt_dir / "project.db"
            
            if not db_path.exists():
                return f"Database not found at {db_path}. Initialize project first."
            
            # Initialize database manager
            db_manager = DatabaseManager(str(project_path))
            
            # Get basic statistics
            stats = self._get_database_statistics(db_manager)
            db_size_mb = db_path.stat().st_size / (1024 * 1024)
            
            # Get archived vs active counts
            archived_stats = self._get_archived_statistics(db_manager)
            
            # Format result
            result = f"""📊 **Database Statistics**

**File Information:**
• Database Size: {db_size_mb:.2f} MB
• Location: {db_path}

**Table Record Counts:**
"""
            
            for table, count in stats.items():
                archived_count = archived_stats.get(table, 0)
                active_count = count - archived_count
                result += f"• {table}: {count} total ({active_count} active, {archived_count} archived)\n"
            
            result += f"""
**Storage Recommendations:**
• Records can be safely archived after 90+ days
• Run maintenance if database exceeds 100MB
• Create backups before major operations
"""
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
            return f"Error getting database statistics: {str(e)}"

    def _get_database_statistics(self, db_manager: DatabaseManager) -> Dict[str, int]:
        """Get statistics about database table sizes."""
        tables = [
            'sessions', 'work_activities', 'file_modifications', 'noteworthy_events',
            'task_status', 'sidequest_status', 'user_preferences', 'flow_status'
        ]
        
        stats = {}
        for table in tables:
            try:
                result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = result[0]['count'] if result else 0
            except Exception:
                stats[table] = 0
        
        return stats

    def _get_archived_statistics(self, db_manager: DatabaseManager) -> Dict[str, int]:
        """Get statistics about archived records."""
        tables_with_archive = [
            'sessions', 'noteworthy_events'
        ]
        
        archived_stats = {}
        for table in tables_with_archive:
            try:
                result = db_manager.execute_query(
                    f"SELECT COUNT(*) as count FROM {table} WHERE archived_at IS NOT NULL"
                )
                archived_stats[table] = result[0]['count'] if result else 0
            except Exception:
                archived_stats[table] = 0
        
        return archived_stats