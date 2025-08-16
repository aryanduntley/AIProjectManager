"""
Flow index creation and management operations.

Handles flow index creation, updates, and maintenance for multi-flow coordination.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_operations import BaseFlowOperations
from ...utils.project_paths import get_flows_path

logger = logging.getLogger(__name__)


class FlowIndexManager(BaseFlowOperations):
    """Manages flow index creation and updates."""
    
    async def create_flow_index(self, project_path: Path, flows: List[Dict[str, Any]], 
                               cross_flow_dependencies: List[Dict[str, Any]] = None) -> str:
        """Create or update flow index with multi-flow coordination."""
        try:
            if cross_flow_dependencies is None:
                cross_flow_dependencies = []
                
            flow_dir = get_flows_path(project_path, self.config_manager)
            flow_dir.mkdir(parents=True, exist_ok=True)
            
            flow_index_path = flow_dir / "flow-index.json"
            
            # Create flow index structure
            flow_index = {
                "metadata": {
                    "version": "1.0.0",
                    "created": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat(),
                    "description": "Master flow index with multi-flow coordination"
                },
                "flowFiles": {},
                "crossFlowDependencies": cross_flow_dependencies,
                "globalFlowSettings": {
                    "maxConcurrentFlows": 10,
                    "defaultContextMode": "theme-expanded",
                    "enableSelectiveLoading": True,
                    "performanceOptimization": True
                },
                "flowCategories": {}
            }
            
            # Process flows and organize by category
            categories = {}
            for flow in flows:
                flow_id = flow["flow_id"]
                flow_file = flow["flow_file"]
                
                # Determine category from flow file name or explicit domain
                if "-flow.json" in flow_file:
                    category = flow_file.replace("-flow.json", "")
                else:
                    category = flow.get("domain", "general")
                
                if category not in categories:
                    categories[category] = []
                categories[category].append(flow_id)
                
                # Add to flow files mapping
                flow_index["flowFiles"][flow_id] = {
                    "file": flow_file,
                    "name": flow["name"],
                    "description": flow.get("description", ""),
                    "primary_themes": flow.get("primary_themes", []),
                    "secondary_themes": flow.get("secondary_themes", []),
                    "category": category,
                    "created": datetime.utcnow().isoformat(),
                    "status": "pending"
                }
            
            flow_index["flowCategories"] = categories
            
            # Write flow index
            flow_index_path.write_text(json.dumps(flow_index, indent=2))
            
            # Sync with database if available
            sync_result = ""
            if self.theme_flow_queries:
                try:
                    await self.theme_flow_queries.sync_flow_index(flow_index)
                    sync_result = " and synchronized with database"
                except Exception as e:
                    sync_result = f" (database sync failed: {str(e)})"
            
            return (
                f"Flow index created successfully{sync_result}:\n"
                f"- {len(flows)} flows registered\n"
                f"- {len(categories)} categories: {', '.join(categories.keys())}\n"
                f"- {len(cross_flow_dependencies)} cross-flow dependencies\n"
                f"- Selective loading: {'enabled' if flow_index['globalFlowSettings']['enableSelectiveLoading'] else 'disabled'}"
            )
            
        except Exception as e:
            logger.error(f"Error creating flow index: {e}")
            return f"Error creating flow index: {str(e)}"
    
    async def _update_flow_index_with_new_flow(self, project_path: Path, flow_id: str, 
                                             flow_file: str, flow_name: str, 
                                             description: str, primary_themes: List[str], 
                                             domain: str):
        """Update flow index with newly created flow."""
        flow_index_path = get_flows_path(project_path, self.config_manager) / "flow-index.json"
        
        if flow_index_path.exists():
            flow_index = json.loads(flow_index_path.read_text())
        else:
            # Create basic flow index if it doesn't exist
            flow_index = {
                "metadata": {
                    "version": "1.0.0",
                    "created": datetime.utcnow().isoformat(),
                    "description": "Master flow index"
                },
                "flowFiles": {},
                "crossFlowDependencies": [],
                "globalFlowSettings": {
                    "enableSelectiveLoading": True
                },
                "flowCategories": {}
            }
        
        # Add new flow to index
        flow_index["flowFiles"][flow_id] = {
            "file": flow_file,
            "name": flow_name,
            "description": description,
            "primary_themes": primary_themes,
            "secondary_themes": [],
            "category": domain,
            "created": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        # Update categories
        if domain not in flow_index["flowCategories"]:
            flow_index["flowCategories"][domain] = []
        flow_index["flowCategories"][domain].append(flow_id)
        
        # Update metadata
        flow_index["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        
        # Write updated index
        flow_index_path.write_text(json.dumps(flow_index, indent=2))
    
    async def create_flow(self, project_path: Path, flow_id: str, flow_name: str, 
                         domain: str, description: str = "", primary_themes: List[str] = None,
                         steps: List[Dict[str, Any]] = None) -> str:
        """Create a new individual flow file."""
        try:
            if primary_themes is None:
                primary_themes = []
            if steps is None:
                steps = []
                
            flow_dir = get_flows_path(project_path, self.config_manager)
            flow_dir.mkdir(parents=True, exist_ok=True)
            
            # Create flow file name
            flow_file_name = f"{domain}-flow.json"
            flow_file_path = flow_dir / flow_file_name
            
            # Create flow structure with enhanced status tracking
            flow_data = {
                "metadata": {
                    "flow_id": flow_id,
                    "name": flow_name,
                    "domain": domain,
                    "description": description,
                    "version": "1.0.0",
                    "created": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat()
                },
                "themes": {
                    "primary": primary_themes,
                    "secondary": []
                },
                "status": {
                    "overall_status": "pending",
                    "completion_percentage": 0,
                    "last_updated": datetime.utcnow().isoformat(),
                    "milestone_integration": {
                        "required_milestones": [],
                        "completion_validation": []
                    }
                },
                "flows": {}
            }
            
            # Add individual flows within the domain
            if steps:
                # Create a main flow with the provided steps
                main_flow_id = f"{flow_id}-main"
                flow_data["flows"][main_flow_id] = {
                    "id": main_flow_id,
                    "name": f"Main {flow_name} Flow",
                    "description": description,
                    "status": "pending",
                    "steps": []
                }
                
                # Process steps with enhanced status tracking
                for i, step in enumerate(steps):
                    step_data = {
                        "step_id": step.get("step_id", f"STEP-{i+1:03d}"),
                        "step_number": i + 1,
                        "trigger": step.get("trigger", ""),
                        "user_experience": step.get("user_experience", ""),
                        "conditions": step.get("conditions", []),
                        "outcomes": step.get("outcomes", []),
                        "status": "pending",
                        "dependencies": [],
                        "file_references": [],
                        "implementation_status": "pending"
                    }
                    flow_data["flows"][main_flow_id]["steps"].append(step_data)
            
            # Write flow file
            flow_file_path.write_text(json.dumps(flow_data, indent=2))
            
            # Trigger directive processing for flow file creation
            if self.server_instance and hasattr(self.server_instance, 'on_file_edit_complete'):
                try:
                    changes_made = {
                        "operation": "create_flow",
                        "flow_id": flow_id,
                        "flow_name": flow_name,
                        "description": description,
                        "primary_themes": primary_themes,
                        "file_created": str(flow_file_path)
                    }
                    await self.server_instance.on_file_edit_complete(str(flow_file_path), changes_made)
                except Exception as e:
                    logger.warning(f"Failed to trigger file edit completion directive for flow creation: {e}")
            
            # Update flow index if it exists
            await self._update_flow_index_with_new_flow(
                project_path, flow_id, flow_file_name, flow_name, description, primary_themes, domain
            )
            
            # Sync with database if available
            sync_result = ""
            if self.theme_flow_queries:
                try:
                    await self.theme_flow_queries.create_flow(flow_id, flow_data)
                    sync_result = " and registered in database"
                except Exception as e:
                    sync_result = f" (database sync failed: {str(e)})"
            
            return (
                f"Flow created successfully{sync_result}:\n"
                f"- Flow ID: {flow_id}\n"
                f"- File: {flow_file_name}\n"
                f"- Domain: {domain}\n"
                f"- Primary themes: {', '.join(primary_themes)}\n"
                f"- Steps: {len(steps)}\n"
                f"- Status: pending"
            )
            
        except Exception as e:
            logger.error(f"Error creating flow: {e}")
            return f"Error creating flow: {str(e)}"