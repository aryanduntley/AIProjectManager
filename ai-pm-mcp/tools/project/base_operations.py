"""
Base project operations and shared utilities for project management.

Contains core functionality shared across all project management operations.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ...utils.project_paths import (
    get_project_management_path, get_blueprint_path, get_database_path, get_management_folder_name
)

logger = logging.getLogger(__name__)


class BaseProjectOperations:
    """Base class for project operations with shared utilities."""
    
    def __init__(self, db_manager=None, config_manager=None, directive_processor=None):
        self.tools = []
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.directive_processor = directive_processor
    
    def get_project_management_dir(self, project_path: Path) -> Path:
        """Get the project management directory path."""
        return get_project_management_path(project_path, self.config_manager)
    
    def get_blueprint_file_path(self, project_path: Path) -> Path:
        """Get the blueprint file path."""
        return get_blueprint_path(project_path, self.config_manager)
    
    def get_database_file_path(self, project_path: Path) -> Path:
        """Get the database file path."""
        return get_database_path(project_path, self.config_manager)
    
    def load_blueprint(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Load project blueprint if it exists."""
        blueprint_path = self.get_blueprint_file_path(project_path)
        if blueprint_path.exists():
            try:
                return json.loads(blueprint_path.read_text())
            except json.JSONDecodeError as e:
                logger.error(f"Error reading blueprint: {e}")
                return None
        return None
    
    def save_blueprint(self, project_path: Path, blueprint_data: Dict[str, Any]) -> bool:
        """Save blueprint data to file."""
        blueprint_path = self.get_blueprint_file_path(project_path)
        try:
            blueprint_path.parent.mkdir(parents=True, exist_ok=True)
            blueprint_path.write_text(json.dumps(blueprint_data, indent=2))
            return True
        except Exception as e:
            logger.error(f"Error saving blueprint: {e}")
            return False
    
    def create_default_blueprint(self, project_name: str) -> Dict[str, Any]:
        """Create a default project blueprint."""
        return {
            "project_name": project_name,
            "version": "1.0.0",
            "created": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "description": f"Project blueprint for {project_name}",
            "structure": {
                "directories": [],
                "files": []
            },
            "dependencies": {},
            "configuration": {},
            "metadata": {
                "framework": "ai-project-manager",
                "initialized": True
            }
        }
    
    def create_initial_blueprint(self, project_name: str) -> str:
        """Create initial project blueprint markdown content."""
        return f"""# {project_name} Project Blueprint

## Project Overview

This is the high-level blueprint for the {project_name} project. This document should be updated to reflect the complete project scope, objectives, and requirements.

## Project Scope

*To be defined with user input*

## Key Features

*To be defined with user input*

## Success Criteria

*To be defined with user input*

## Constraints and Limitations

*To be defined with user input*

## Timeline and Milestones

*To be defined with user input*

## Resources Required

*To be defined with user input*

---

*This blueprint is a living document and should be updated as the project evolves.*
"""
    
    def create_initial_flow_index(self) -> str:
        """Create initial flow index JSON content."""
        flow_index = {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.utcnow().isoformat(),
                "description": "Master flow index with flow file references and cross-flow dependencies",
                "totalFlows": 0,
                "flowFiles": []
            },
            "flowFiles": [],
            "crossFlowDependencies": [],
            "globalFlowSettings": {
                "maxConcurrentFlows": 10,
                "defaultContextMode": "file-focused",
                "enableSelectiveLoading": True
            }
        }
        return json.dumps(flow_index, indent=2)