#!/usr/bin/env python3
"""
Analysis Command Handlers

Handles project analysis, themes, and flows commands.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any
from .base_command import BaseCommandHandler

logger = logging.getLogger(__name__)


class AnalysisCommandHandler(BaseCommandHandler):
    """Handles project analysis commands."""
    
    async def execute_analyze(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-analyze command."""
        try:
            # This would integrate with theme discovery and project analysis tools
            return json.dumps({
                "type": "info",
                "message": "Analyze command workflow: get_project_state_analysis → theme_discover → project_get_status",
                "next_steps": "Use theme_tools and project_tools to implement analysis functionality"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in _execute_analyze: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-analyze command: {str(e)}"
            }, indent=2)
    
    async def execute_themes(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-themes command."""
        try:
            from ..theme_tools import ThemeTools
            theme_tools = ThemeTools(self.db_manager)
            
            # Get themes list
            result = await theme_tools.list_themes({
                "project_path": str(project_path)
            })
            
            return f"""# /aipm-themes Command Result

## Project Themes:
{result}

## Next Steps:
- Use `/aipm-analyze` to discover new themes
- Use context loading tools to work with specific themes
"""
            
        except Exception as e:
            logger.error(f"Error in _execute_themes: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-themes command: {str(e)}"
            }, indent=2)
    
    async def execute_flows(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-flows command."""
        try:
            from ..flow_tools import FlowTools
            flow_tools = FlowTools(self.db_manager)
            
            # This would show flow index
            return json.dumps({
                "type": "info",
                "message": "Flows command workflow: flow_index_create → context_get_flows",
                "next_steps": "Use flow_tools to implement flow display"
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error in _execute_flows: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-flows command: {str(e)}"
            }, indent=2)
    
    async def execute_config(self, project_path: Path, args: Dict[str, Any]) -> str:
        """Execute /aipm-config command."""
        try:
            from ...core.config_manager import ConfigManager
            from ...utils.project_paths import get_current_git_branch, can_modify_config
            import json
            
            # Use ConfigManager directly instead of removed config_tools
            config_manager = ConfigManager()
            config_data = config_manager.get_effective_config()
            
            return f"""# Current AI Project Manager Configuration

{json.dumps(config_data, indent=2)}

## Configuration Information
- **Configuration File**: {config_manager.config_file}
- **Current Branch**: {get_current_git_branch()}
- **Configuration Editable**: {can_modify_config()}
- **Management Folder**: {config_data.get('project', {}).get('management_folder_name', 'projectManagement')}

## Key Settings
- **Max File Lines**: {config_data.get('project', {}).get('max_file_lines', 900)}
- **Auto Modularize**: {config_data.get('project', {}).get('auto_modularize', True)}
- **Theme Discovery**: {config_data.get('project', {}).get('theme_discovery', True)}
- **Git Enabled**: {config_data.get('git', {}).get('enabled', True)}
- **Branch Management**: {config_data.get('branch_management', {}).get('enabled', True)}
"""
            
        except Exception as e:
            logger.error(f"Error in _execute_config: {e}")
            return json.dumps({
                "type": "error",
                "message": f"Error executing /aipm-config command: {str(e)}"
            }, indent=2)