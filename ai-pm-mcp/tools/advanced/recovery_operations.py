"""
Error recovery operations for the AI Project Manager.

Handles recovery checkpoint creation, rollback, and status monitoring.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ...core.error_recovery import ErrorRecoveryManager, RecoveryLevel, OperationType
from ...database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class RecoveryOperations:
    """Error recovery management operations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager

    async def create_recovery_checkpoint(self, arguments: Dict[str, Any]) -> str:
        """Create a recovery checkpoint."""
        try:
            project_path = Path(arguments["project_path"])
            operation_type = OperationType(arguments["operation_type"])
            description = arguments["description"]
            context_data = arguments.get("context_data", {})
            
            if not self.db_manager:
                return "Database not available. Recovery system requires database connection."
            
            # Initialize error recovery manager
            recovery_manager = ErrorRecoveryManager(project_path, self.db_manager)
            
            # Create recovery point
            recovery_point_id = recovery_manager.create_recovery_point(
                operation_type, description, context_data
            )
            
            if recovery_point_id:
                return f"""✅ Recovery checkpoint created successfully!

Recovery Point ID: {recovery_point_id}
Operation Type: {operation_type.value}
Description: {description}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This checkpoint can be used to rollback the system if the operation fails.
Use `recovery_rollback` with the Recovery Point ID to restore if needed."""
            else:
                return "❌ Failed to create recovery checkpoint. Check system logs for details."
                
        except Exception as e:
            logger.error(f"Error creating recovery checkpoint: {e}")
            return f"Error creating recovery checkpoint: {str(e)}"

    async def rollback_to_checkpoint(self, arguments: Dict[str, Any]) -> str:
        """Rollback to a recovery checkpoint."""
        try:
            project_path = Path(arguments["project_path"])
            recovery_point_id = arguments["recovery_point_id"]
            recovery_level = RecoveryLevel(arguments.get("recovery_level", "complete"))
            
            if not self.db_manager:
                return "Database not available. Recovery system requires database connection."
            
            recovery_manager = ErrorRecoveryManager(project_path, self.db_manager)
            
            # Perform rollback
            rollback_result = recovery_manager.rollback_to_recovery_point(
                recovery_point_id, recovery_level
            )
            
            if rollback_result["success"]:
                response = f"""🔄 Rollback completed successfully!

Recovery Point ID: {recovery_point_id}
Recovery Level: {recovery_level.value}

Actions Performed:
"""
                for action in rollback_result["rollback_actions"]:
                    response += f"• {action}\n"
                
                response += """
⚠️  The system has been restored to the checkpoint state.
Any changes made after the checkpoint have been reverted."""
                
                return response
            else:
                return f"❌ Rollback failed: {rollback_result['error']}"
                
        except Exception as e:
            logger.error(f"Error rolling back to checkpoint: {e}")
            return f"Error rolling back to checkpoint: {str(e)}"

    async def get_recovery_status(self, arguments: Dict[str, Any]) -> str:
        """Get recovery system status."""
        try:
            project_path = Path(arguments["project_path"])
            
            if not self.db_manager:
                return "Database not available. Recovery system requires database connection."
            
            recovery_manager = ErrorRecoveryManager(project_path, self.db_manager)
            status_result = recovery_manager.get_recovery_status()
            
            if status_result["success"]:
                response = f"""🛡️ Recovery System Status

Recovery Points:
• Total: {status_result['recovery_points']['total']}
• Recent: {len(status_result['recovery_points']['recent'])}

Backups:
• Total: {status_result['backups']['total']}
• Recent: {len(status_result['backups']['recent'])}

System Status: {status_result['system_status'].upper()}

Recent Recovery Points:
"""
                
                for point in status_result['recovery_points']['recent']:
                    response += f"• {point['id'][:20]}... ({point['operation_type']}) - {point['timestamp'][:19]}\n"
                
                if status_result['recent_events']:
                    response += "\nRecent Recovery Events:\n"
                    for event in status_result['recent_events'][-3:]:
                        response += f"• {event['event_type']} - {event['timestamp'][:19]}\n"
                
                return response
            else:
                return f"❌ Could not get recovery status: {status_result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error getting recovery status: {e}")
            return f"Error getting recovery status: {str(e)}"