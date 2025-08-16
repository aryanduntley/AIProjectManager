"""
Project blueprint management operations.

Handles blueprint retrieval, updates, and management.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_operations import BaseProjectOperations

logger = logging.getLogger(__name__)


class ProjectBlueprintManager(BaseProjectOperations):
    """Manages project blueprint operations."""
    
    async def get_blueprint(self, project_path: Path) -> str:
        """Get the current project blueprint."""
        try:
            project_path = Path(project_path)
            blueprint_data = self.load_blueprint(project_path)
            
            if not blueprint_data:
                return "No blueprint found. Initialize the project first."
            
            # Format the blueprint for display
            result = f"Project Blueprint: {blueprint_data.get('project_name', 'Unknown')}\n"
            result += f"Version: {blueprint_data.get('version', 'Unknown')}\n"
            result += f"Description: {blueprint_data.get('description', 'No description')}\n"
            result += f"Created: {blueprint_data.get('created', 'Unknown')}\n"
            result += f"Last Updated: {blueprint_data.get('last_updated', 'Unknown')}\n\n"
            
            # Show structure if available
            structure = blueprint_data.get('structure', {})
            if structure:
                result += "Project Structure:\n"
                directories = structure.get('directories', [])
                files = structure.get('files', [])
                
                if directories:
                    result += f"  Directories ({len(directories)}):\n"
                    for directory in directories[:10]:  # Limit to first 10
                        result += f"    - {directory}\n"
                    if len(directories) > 10:
                        result += f"    ... and {len(directories) - 10} more\n"
                
                if files:
                    result += f"  Files ({len(files)}):\n"
                    for file in files[:10]:  # Limit to first 10
                        result += f"    - {file}\n"
                    if len(files) > 10:
                        result += f"    ... and {len(files) - 10} more\n"
            
            # Show dependencies if available
            dependencies = blueprint_data.get('dependencies', {})
            if dependencies:
                result += f"\nDependencies ({len(dependencies)}):\n"
                for dep_name, dep_info in list(dependencies.items())[:5]:  # Limit to first 5
                    if isinstance(dep_info, dict):
                        version = dep_info.get('version', 'Unknown')
                        result += f"  - {dep_name}: {version}\n"
                    else:
                        result += f"  - {dep_name}: {dep_info}\n"
                if len(dependencies) > 5:
                    result += f"  ... and {len(dependencies) - 5} more\n"
            
            # Show metadata if available
            metadata = blueprint_data.get('metadata', {})
            if metadata:
                result += "\nMetadata:\n"
                for key, value in metadata.items():
                    result += f"  - {key}: {value}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting blueprint: {e}")
            return f"Error getting blueprint: {str(e)}"
    
    async def update_blueprint(self, project_path: Path, updates: Dict[str, Any]) -> str:
        """Update the project blueprint."""
        try:
            project_path = Path(project_path)
            blueprint_data = self.load_blueprint(project_path)
            
            if not blueprint_data:
                return "No blueprint found. Initialize the project first."
            
            # Track what was updated
            updated_fields = []
            
            # Update basic fields
            for field in ['project_name', 'version', 'description']:
                if field in updates:
                    old_value = blueprint_data.get(field, 'None')
                    blueprint_data[field] = updates[field]
                    updated_fields.append(f"{field}: '{old_value}' → '{updates[field]}'")
            
            # Update structure
            if 'structure' in updates:
                if 'structure' not in blueprint_data:
                    blueprint_data['structure'] = {}
                
                structure_updates = updates['structure']
                if 'directories' in structure_updates:
                    blueprint_data['structure']['directories'] = structure_updates['directories']
                    updated_fields.append(f"directories: {len(structure_updates['directories'])} items")
                
                if 'files' in structure_updates:
                    blueprint_data['structure']['files'] = structure_updates['files']
                    updated_fields.append(f"files: {len(structure_updates['files'])} items")
            
            # Update dependencies
            if 'dependencies' in updates:
                if 'dependencies' not in blueprint_data:
                    blueprint_data['dependencies'] = {}
                
                dependencies_updates = updates['dependencies']
                blueprint_data['dependencies'].update(dependencies_updates)
                updated_fields.append(f"dependencies: {len(dependencies_updates)} items updated")
            
            # Update configuration
            if 'configuration' in updates:
                if 'configuration' not in blueprint_data:
                    blueprint_data['configuration'] = {}
                
                config_updates = updates['configuration']
                blueprint_data['configuration'].update(config_updates)
                updated_fields.append(f"configuration: {len(config_updates)} items updated")
            
            # Update metadata
            if 'metadata' in updates:
                if 'metadata' not in blueprint_data:
                    blueprint_data['metadata'] = {}
                
                metadata_updates = updates['metadata']
                blueprint_data['metadata'].update(metadata_updates)
                updated_fields.append(f"metadata: {len(metadata_updates)} items updated")
            
            # Update timestamp
            blueprint_data['last_updated'] = datetime.utcnow().isoformat()
            
            # Save updated blueprint
            if self.save_blueprint(project_path, blueprint_data):
                # Add directive hook for server notification
                if self.server_instance and hasattr(self.server_instance, 'on_project_operation_complete'):
                    hook_context = {
                        "trigger": "blueprint_update_complete",
                        "operation_type": "blueprint_update",
                        "project_path": str(project_path),
                        "updated_fields": updated_fields,
                        "timestamp": datetime.now().isoformat()
                    }
                    try:
                        await self.server_instance.on_project_operation_complete(hook_context, "projectManagement")
                    except Exception as e:
                        logger.warning(f"Blueprint update hook failed: {e}")
                
                result = f"Blueprint updated successfully:\n"
                for field in updated_fields:
                    result += f"  - {field}\n"
                result += f"  - last_updated: {blueprint_data['last_updated']}\n"
                return result
            else:
                return "Error saving updated blueprint."
            
        except Exception as e:
            logger.error(f"Error updating blueprint: {e}")
            return f"Error updating blueprint: {str(e)}"