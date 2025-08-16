"""
Theme-flow integration operations.

Handles synchronization and integration between themes and flows.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base_operations import BaseThemeOperations

logger = logging.getLogger(__name__)


class ThemeFlowIntegration(BaseThemeOperations):
    """Handles theme-flow synchronization and integration."""
    
    async def sync_theme_flows(self, project_path: Path, specific_theme: Optional[str] = None) -> str:
        """Synchronize theme-flow relationships with database."""
        try:
            project_path = Path(project_path)
            
            if not self.theme_flow_queries:
                return "Database not available. Theme-flow synchronization requires database connection."
            
            themes_dir = self.get_themes_directory(project_path)
            flow_dir = self.get_flows_directory(project_path)
            
            if not themes_dir.exists():
                return "No themes directory found. Initialize project first."
            
            # Load flow index
            flow_index_path = flow_dir / "flow-index.json"
            if not flow_index_path.exists():
                return "No flow index found. Initialize flows first."
            
            flow_index_data = json.loads(flow_index_path.read_text())
            
            # Load theme files
            theme_files_data = {}
            themes_to_sync = [specific_theme] if specific_theme else []
            
            if not themes_to_sync:
                # Load all themes
                for theme_file in themes_dir.glob("*.json"):
                    if theme_file.name != "themes.json":
                        theme_name = theme_file.stem
                        try:
                            theme_data = json.loads(theme_file.read_text())
                            if "flows" in theme_data:
                                theme_files_data[theme_name] = theme_data
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in theme file: {theme_file}")
            else:
                # Load specific theme
                theme_file = themes_dir / f"{specific_theme}.json"
                if theme_file.exists():
                    theme_data = json.loads(theme_file.read_text())
                    if "flows" in theme_data:
                        theme_files_data[specific_theme] = theme_data
            
            if not theme_files_data:
                return "No themes with flow data found to synchronize."
            
            # Synchronize with database
            sync_results = await self.theme_flow_queries.sync_theme_flows_from_files(
                theme_files_data, flow_index_data
            )
            
            return f"Theme-flow synchronization completed:\n{json.dumps(sync_results, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error syncing theme flows: {e}")
            return f"Error syncing theme flows: {str(e)}"
    
    async def get_theme_flows(self, project_path: Path, theme_name: str) -> str:
        """Get flows associated with a theme."""
        try:
            project_path = Path(project_path)
            themes_dir = self.get_themes_directory(project_path)
            flows_dir = self.get_flows_directory(project_path)
            
            # Load theme data
            theme_data = self.load_theme(themes_dir, theme_name)
            if not theme_data:
                return f"Theme '{theme_name}' not found"
            
            # Get associated flows
            associated_flows = theme_data.get("flows", [])
            
            result = f"Flows associated with theme '{theme_name}':\n"
            result += "=" * 50 + "\n\n"
            
            if not associated_flows:
                result += "No flows associated with this theme.\n"
                result += "Run theme_sync_flows to discover flow associations.\n"
                return result
            
            # Load flow details
            flow_index_path = flows_dir / "flow-index.json"
            flow_details = {}
            
            if flow_index_path.exists():
                flow_index = json.loads(flow_index_path.read_text())
                flow_files = flow_index.get("flowFiles", {})
                
                for flow_id in associated_flows:
                    if flow_id in flow_files:
                        flow_info = flow_files[flow_id]
                        flow_file_path = flows_dir / flow_info.get("file", f"{flow_id}.json")
                        
                        if flow_file_path.exists():
                            try:
                                flow_data = json.loads(flow_file_path.read_text())
                                flow_details[flow_id] = {
                                    "name": flow_info.get("name", flow_id),
                                    "description": flow_info.get("description", ""),
                                    "file": flow_info.get("file", ""),
                                    "status": flow_data.get("status", {}).get("overall_status", "unknown"),
                                    "completion": flow_data.get("status", {}).get("completion_percentage", 0)
                                }
                            except json.JSONDecodeError:
                                flow_details[flow_id] = {
                                    "name": flow_id,
                                    "description": "Error loading flow data",
                                    "file": flow_info.get("file", ""),
                                    "status": "error",
                                    "completion": 0
                                }
            
            # Display flow information
            result += f"Found {len(associated_flows)} associated flows:\n\n"
            
            for flow_id in associated_flows:
                if flow_id in flow_details:
                    flow_info = flow_details[flow_id]
                    result += f"📋 {flow_info['name']} ({flow_id})\n"
                    result += f"   Description: {flow_info['description']}\n"
                    result += f"   Status: {flow_info['status']}\n"
                    result += f"   Completion: {flow_info['completion']}%\n"
                    result += f"   File: {flow_info['file']}\n\n"
                else:
                    result += f"📋 {flow_id}\n"
                    result += f"   Status: Flow file not found\n\n"
            
            # Summary statistics
            if flow_details:
                completed_flows = sum(1 for f in flow_details.values() if f['status'] == 'complete')
                in_progress_flows = sum(1 for f in flow_details.values() if f['status'] == 'in-progress')
                avg_completion = sum(f['completion'] for f in flow_details.values()) / len(flow_details)
                
                result += f"Summary:\n"
                result += f"- Total flows: {len(associated_flows)}\n"
                result += f"- Completed: {completed_flows}\n"
                result += f"- In progress: {in_progress_flows}\n"
                result += f"- Average completion: {avg_completion:.1f}%\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting theme flows: {e}")
            return f"Error getting theme flows: {str(e)}"
    
    async def _sync_theme_with_flows(self, theme_name: str, theme_data: Dict[str, Any],
                                   flow_index: Dict[str, Any], flows_dir: Path,
                                   sync_results: Dict[str, Any]):
        """Sync a specific theme with available flows."""
        theme_keywords = set(theme_data.get("keywords", []))
        theme_patterns = theme_data.get("patterns", [])
        current_flows = set(theme_data.get("flows", []))
        
        # Find matching flows
        matching_flows = set()
        flow_files = flow_index.get("flowFiles", {})
        
        for flow_id, flow_info in flow_files.items():
            # Check if flow matches theme
            if await self._flow_matches_theme(flow_id, flow_info, flows_dir, theme_keywords, theme_patterns):
                matching_flows.add(flow_id)
                sync_results["flows_processed"] += 1
        
        # Update theme with new flow associations
        new_associations = matching_flows - current_flows
        removed_associations = current_flows - matching_flows
        
        if new_associations or removed_associations:
            theme_data["flows"] = list(matching_flows)
            theme_data["statistics"]["flow_count"] = len(matching_flows)
            theme_data["metadata"]["last_updated"] = "datetime.utcnow().isoformat()"
            
            # Save updated theme
            themes_dir = flows_dir.parent / "Themes"  # Assuming standard structure
            self.save_theme(themes_dir, theme_name, theme_data)
            
            sync_results["associations_created"] += len(new_associations)
            sync_results["associations_removed"] += len(removed_associations)
    
    async def _flow_matches_theme(self, flow_id: str, flow_info: Dict[str, Any],
                                flows_dir: Path, theme_keywords: set, theme_patterns: List[str]) -> bool:
        """Check if a flow matches a theme based on keywords and patterns."""
        # Check flow name and description
        flow_name = flow_info.get("name", "").lower()
        flow_description = flow_info.get("description", "").lower()
        
        # Check for keyword matches
        for keyword in theme_keywords:
            if keyword.lower() in flow_name or keyword.lower() in flow_description:
                return True
        
        # Check primary themes
        primary_themes = flow_info.get("primary_themes", [])
        for theme in primary_themes:
            if theme.lower() in [k.lower() for k in theme_keywords]:
                return True
        
        # Load full flow data for more detailed matching
        try:
            flow_file = flow_info.get("file", f"{flow_id}.json")
            flow_file_path = flows_dir / flow_file
            
            if flow_file_path.exists():
                flow_data = json.loads(flow_file_path.read_text())
                
                # Check flow content for keyword matches
                flow_content = json.dumps(flow_data).lower()
                for keyword in theme_keywords:
                    if keyword.lower() in flow_content:
                        return True
        
        except Exception as e:
            logger.debug(f"Error checking flow content for {flow_id}: {e}")
        
        return False