"""
Base flow operations and shared utilities for flow management.

Contains core functionality shared across all flow management operations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from ...utils.project_paths import get_flows_path, get_themes_path

logger = logging.getLogger(__name__)


class BaseFlowOperations:
    """Base class for flow operations with shared utilities."""
    
    def __init__(self, 
                 theme_flow_queries=None,
                 session_queries=None,
                 file_metadata_queries=None,
                 config_manager=None):
        self.theme_flow_queries = theme_flow_queries
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
        self.config_manager = config_manager
        self.server_instance = None
    
    async def find_flow_file(self, project_path: Path, flow_id: str) -> Optional[Path]:
        """Find the flow file containing the specified flow ID."""
        flow_dir = get_flows_path(project_path, self.config_manager)
        flow_index_path = flow_dir / "flow-index.json"
        
        if not flow_index_path.exists():
            return None
        
        try:
            flow_index = json.loads(flow_index_path.read_text())
            flow_files = flow_index.get("flowFiles", {})
            
            if flow_id in flow_files:
                flow_file = flow_files[flow_id]["file"]
                return flow_dir / flow_file
        except json.JSONDecodeError:
            pass
        
        return None
    
    async def flow_needs_update(self, existing_flow: Dict[str, Any], 
                               file_flow_data: Dict[str, Any]) -> bool:
        """Check if flow data in database needs updating."""
        # Compare metadata timestamps or version
        existing_updated = existing_flow.get("last_updated", "")
        file_updated = file_flow_data.get("metadata", {}).get("last_updated", "")
        
        if file_updated and existing_updated:
            return file_updated > existing_updated
        
        # If no timestamps, assume update needed
        return True
    
    async def track_selective_flow_loading(self, session_id: str, task_themes: List[str],
                                          loaded_flow_ids: List[str], task_description: str):
        """Track selective flow loading for analytics."""
        try:
            if self.session_queries:
                await self.session_queries.log_flow_loading_event(
                    session_id=session_id,
                    event_type="selective_loading",
                    task_themes=task_themes,
                    loaded_flows=loaded_flow_ids,
                    task_description=task_description,
                    loading_strategy="selective"
                )
        except Exception as e:
            logger.debug(f"Error tracking flow loading: {e}")
    
    async def generate_loading_recommendations(self, loaded_flows: Dict[str, Any],
                                              task_themes: List[str], 
                                              task_description: str) -> List[str]:
        """Generate recommendations based on loaded flows."""
        recommendations = []
        
        # Check for incomplete flows
        incomplete_flows = []
        for flow_id, flow_data in loaded_flows.items():
            status = flow_data.get("status", {})
            completion = status.get("completion_percentage", 0)
            if completion < 100:
                incomplete_flows.append((flow_id, completion))
        
        if incomplete_flows:
            recommendations.append(
                f"Consider completing {len(incomplete_flows)} incomplete flows for better context"
            )
        
        # Check for missing themes
        covered_themes = set()
        for flow_data in loaded_flows.values():
            themes = flow_data.get("themes", {})
            covered_themes.update(themes.get("primary", []))
            covered_themes.update(themes.get("secondary", []))
        
        missing_themes = set(task_themes) - covered_themes
        if missing_themes:
            recommendations.append(
                f"Consider flows covering these themes: {', '.join(missing_themes)}"
            )
        
        # Performance recommendations
        total_flows_count = sum(len(data.get("flows", {})) for data in loaded_flows.values())
        if total_flows_count > 20:
            recommendations.append(
                "High flow count detected - consider more selective loading for performance"
            )
        
        return recommendations