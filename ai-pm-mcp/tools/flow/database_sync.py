"""
Flow database synchronization operations.

Handles synchronization between flow files and database for optimal performance.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base_operations import BaseFlowOperations
from ...utils.project_paths import get_flows_path, get_themes_path

logger = logging.getLogger(__name__)


class FlowDatabaseSync(BaseFlowOperations):
    """Manages synchronization between flow files and database."""
    
    async def sync_flows_with_database(self, project_path: Path, force_update: bool = False) -> str:
        """Synchronize flow definitions with database for optimal performance."""
        try:
            if not self.theme_flow_queries:
                return "Database not available. Flow synchronization requires database connection."
            
            flow_dir = get_flows_path(project_path, self.config_manager)
            if not flow_dir.exists():
                return "No ProjectFlow directory found. Initialize flows first."
            
            # Load flow index
            flow_index_path = flow_dir / "flow-index.json"
            if not flow_index_path.exists():
                return "No flow index found. Create flow index first."
            
            flow_index = json.loads(flow_index_path.read_text())
            
            # Collect all flow data
            flows_data = {}
            flow_files = flow_index.get("flowFiles", {})
            
            sync_results = {
                "flows_processed": 0,
                "flows_updated": 0,
                "flows_created": 0,
                "errors": []
            }
            
            for flow_id, flow_info in flow_files.items():
                flow_file = flow_info["file"]
                flow_file_path = flow_dir / flow_file
                
                if flow_file_path.exists():
                    try:
                        flow_data = json.loads(flow_file_path.read_text())
                        flows_data[flow_id] = flow_data
                        sync_results["flows_processed"] += 1
                        
                        # Check if flow exists in database
                        existing_flow = await self.theme_flow_queries.get_flow_details(flow_id)
                        
                        if existing_flow:
                            # Update existing flow
                            if force_update or await self.flow_needs_update(existing_flow, flow_data):
                                await self.theme_flow_queries.update_flow(flow_id, flow_data)
                                sync_results["flows_updated"] += 1
                        else:
                            # Create new flow
                            await self.theme_flow_queries.create_flow(flow_id, flow_data)
                            sync_results["flows_created"] += 1
                        
                    except json.JSONDecodeError as e:
                        sync_results["errors"].append(f"Invalid JSON in {flow_file}: {str(e)}")
                    except Exception as e:
                        sync_results["errors"].append(f"Error processing {flow_file}: {str(e)}")
                else:
                    sync_results["errors"].append(f"Flow file not found: {flow_file}")
            
            # Sync flow index metadata
            try:
                await self.theme_flow_queries.sync_flow_index(flow_index)
            except Exception as e:
                sync_results["errors"].append(f"Error syncing flow index: {str(e)}")
            
            # Sync theme-flow relationships
            try:
                themes_dir = get_themes_path(project_path, self.config_manager)
                if themes_dir.exists():
                    theme_files = list(themes_dir.glob("*.json"))
                    theme_data = {}
                    
                    for theme_file in theme_files:
                        if theme_file.name != "themes.json":
                            try:
                                theme_name = theme_file.stem
                                theme_content = json.loads(theme_file.read_text())
                                if "flows" in theme_content:
                                    theme_data[theme_name] = theme_content
                            except json.JSONDecodeError:
                                continue
                    
                    if theme_data:
                        await self.theme_flow_queries.sync_theme_flows_from_files(
                            theme_data, flow_index
                        )
            except Exception as e:
                sync_results["errors"].append(f"Error syncing theme-flow relationships: {str(e)}")
            
            # Format results
            result = "Flow database synchronization completed:\n"
            result += f"- Flows processed: {sync_results['flows_processed']}\n"
            result += f"- Flows updated: {sync_results['flows_updated']}\n"
            result += f"- Flows created: {sync_results['flows_created']}\n"
            
            if sync_results["errors"]:
                result += f"- Errors: {len(sync_results['errors'])}\n"
                result += "\nErrors encountered:\n"
                for error in sync_results["errors"]:
                    result += f"  • {error}\n"
            else:
                result += "- No errors encountered\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error synchronizing flows with database: {e}")
            return f"Error synchronizing flows with database: {str(e)}"