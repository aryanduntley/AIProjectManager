"""
Flow status management operations.

Handles flow and step status updates with database persistence.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_operations import BaseFlowOperations

logger = logging.getLogger(__name__)


class FlowStatusManager(BaseFlowOperations):
    """Manages flow and step status updates."""
    
    async def update_flow_status(self, project_path: Path, flow_id: str, 
                                status: Optional[str] = None, 
                                completion_percentage: Optional[int] = None,
                                step_updates: List[Dict[str, Any]] = None,
                                session_id: Optional[str] = None) -> str:
        """Update flow and step status with database persistence."""
        try:
            if step_updates is None:
                step_updates = []
                
            # Find flow file
            flow_file_path = await self.find_flow_file(project_path, flow_id)
            if not flow_file_path:
                return f"Flow file for '{flow_id}' not found."
            
            # Load and update flow data
            flow_data = json.loads(flow_file_path.read_text())
            
            updated_fields = []
            
            # Update overall status
            if status:
                if "status" not in flow_data:
                    flow_data["status"] = {}
                flow_data["status"]["overall_status"] = status
                flow_data["status"]["last_updated"] = datetime.utcnow().isoformat()
                updated_fields.append(f"status: {status}")
            
            # Update completion percentage
            if completion_percentage is not None:
                if "status" not in flow_data:
                    flow_data["status"] = {}
                flow_data["status"]["completion_percentage"] = completion_percentage
                updated_fields.append(f"completion: {completion_percentage}%")
            
            # Update step statuses
            step_updates_applied = 0
            for step_update in step_updates:
                step_id = step_update["step_id"]
                step_status = step_update["status"]
                completed_at = step_update.get("completed_at")
                
                # Find and update step
                for flow_key, flow_content in flow_data.get("flows", {}).items():
                    for step in flow_content.get("steps", []):
                        if step.get("step_id") == step_id:
                            step["status"] = step_status
                            if completed_at:
                                step["completed_at"] = completed_at
                            step_updates_applied += 1
                            break
            
            if step_updates_applied > 0:
                updated_fields.append(f"{step_updates_applied} steps updated")
            
            # Write updated flow data
            flow_file_path.write_text(json.dumps(flow_data, indent=2))
            
            # Update database if available
            db_result = ""
            if self.theme_flow_queries:
                try:
                    await self.theme_flow_queries.update_flow_status(
                        flow_id=flow_id,
                        status=status,
                        completion_percentage=completion_percentage
                    )
                    
                    # Update step statuses in database
                    for step_update in step_updates:
                        await self.theme_flow_queries.update_flow_step_status(
                            flow_id=flow_id,
                            step_id=step_update["step_id"],
                            status=step_update["status"],
                            completed_at=step_update.get("completed_at")
                        )
                    
                    db_result = " and database"
                except Exception as e:
                    db_result = f" (database update failed: {str(e)})"
            
            # Track update in session if provided
            if session_id and self.session_queries:
                await self.session_queries.log_flow_status_update(
                    session_id=session_id,
                    flow_id=flow_id,
                    status_changes=updated_fields
                )
            
            return (
                f"Flow status updated successfully in file{db_result}:\n"
                f"- Flow: {flow_id}\n"
                f"- Updates: {', '.join(updated_fields)}\n"
                f"- Step updates applied: {step_updates_applied}"
            )
            
        except Exception as e:
            logger.error(f"Error updating flow status: {e}")
            return f"Error updating flow status: {str(e)}"