"""
File Action Executor

Handles file operation actions for directive execution.
"""

import logging
from typing import Dict, Any
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


class FileActionExecutor(BaseActionExecutor):
    """Executes file operation actions using existing file tools."""
    
    def get_supported_actions(self) -> list[str]:
        """Get list of file action types this executor supports."""
        return [
            "check_line_limits",
            "update_file_metadata",
            "discover_themes",
            "validate_themes", 
            "update_themes"
        ]
    
    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a file action."""
        if action_type == "check_line_limits":
            return await self._execute_check_line_limits(parameters)
        elif action_type == "update_file_metadata":
            return await self._execute_update_file_metadata(parameters)
        elif action_type == "discover_themes":
            return await self._execute_discover_themes(parameters)
        elif action_type == "validate_themes":
            return await self._execute_validate_themes(parameters)
        elif action_type == "update_themes":
            return await self._execute_update_themes(parameters)
        else:
            return self._create_error_result(f"Unknown file action type: {action_type}")
    
    async def _execute_check_line_limits(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute check line limits action."""
        if self.file_tools:
            try:
                file_path = parameters.get("file_path", "")
                result = await self.file_tools.check_line_limits(file_path)
                return self._create_success_result("Line limits checked", result=result)
            except Exception as e:
                logger.error(f"Error checking line limits: {e}")
                return self._create_error_result(str(e))
        else:
            # Fallback implementation
            return await self._fallback_check_line_limits(parameters)
    
    async def _fallback_check_line_limits(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback line limit checking when file_tools not available."""
        try:
            file_path = parameters.get("file_path", "")
            if not file_path:
                return self._create_error_result("No file path provided")
            
            # Basic line count check
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                
                # Default limit of 900 lines as per directives
                limit = parameters.get("limit", 900)
                exceeds_limit = line_count > limit
                
                result = {
                    "file_path": file_path,
                    "line_count": line_count,
                    "limit": limit,
                    "exceeds_limit": exceeds_limit
                }
                
                if exceeds_limit:
                    logger.warning(f"File {file_path} exceeds line limit: {line_count} > {limit}")
                
                return self._create_success_result(
                    "Line limits checked via fallback method",
                    result=result
                )
                
            except FileNotFoundError:
                return self._create_error_result(f"File not found: {file_path}")
            except Exception as e:
                return self._create_error_result(f"Error checking file: {e}")
                
        except Exception as e:
            logger.error(f"Fallback line limit check failed: {e}")
            return self._create_error_result(f"Fallback check failed: {str(e)}")
    
    async def _execute_update_file_metadata(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update file metadata action using existing FileMetadataQueries."""
        if not self.file_metadata_queries:
            return self._create_failed_result(
                "No file metadata queries available - database not properly initialized",
                "update_file_metadata",
                parameters
            )
        
        try:
            file_path = parameters.get("file_path")
            metadata_updates = parameters.get("metadata", {})
            themes = parameters.get("themes", [])
            operation_type = parameters.get("operation", "update")
            
            if not file_path:
                return self._create_error_result("File path is required")
            
            if not metadata_updates and not themes:
                return self._create_error_result("Either metadata updates or themes must be provided")
            
            # Update file metadata using existing method
            success = self.file_metadata_queries.create_or_update_file_metadata(file_path, metadata_updates)
            
            if not success:
                return self._create_error_result(f"Failed to update metadata for {file_path}")
            
            # Update theme associations if provided
            if themes:
                self.file_metadata_queries.update_file_theme_associations(file_path, themes)
            
            # Log the operation
            self.file_metadata_queries.modification_logging.log_file_modification(
                file_path=file_path,
                file_type="code",
                operation=operation_type,
                details={
                    "directive_driven": True,
                    "metadata_updates": list(metadata_updates.keys()) if metadata_updates else [],
                    "themes_updated": themes
                }
            )
            
            logger.info(f"File metadata updated for: {file_path}")
            
            return self._create_success_result(
                f"File metadata updated for {file_path}",
                file_path=file_path,
                metadata_keys=list(metadata_updates.keys()) if metadata_updates else [],
                themes_count=len(themes)
            )
            
        except Exception as e:
            logger.error(f"Error updating file metadata: {e}")
            return self._create_error_result(f"File metadata update failed: {str(e)}")
    
    async def _execute_discover_themes(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute discover themes action using existing ThemeTools."""
        if not self.theme_tools:
            return self._create_failed_result(
                "No theme tools available - cannot discover themes",
                "discover_themes",
                parameters
            )
        
        try:
            project_path = parameters.get("project_path")
            force_rediscovery = parameters.get("force_rediscovery", False)
            
            if not project_path:
                return self._create_error_result("Project path is required")
            
            # Use existing theme tools method
            result = await self.theme_tools.discover_themes({
                "project_path": project_path,
                "force_rediscovery": force_rediscovery
            })
            
            # Check if discovery was successful
            if "Error" in result:
                logger.error(f"Theme discovery failed: {result}")
                return self._create_error_result(f"Theme discovery failed: {result}")
            
            # Parse result to extract theme information
            theme_count = 0
            theme_names = []
            if "discovered" in result and "themes:" in result:
                # Extract theme count and names from result string
                try:
                    import re
                    count_match = re.search(r'discovered (\d+) themes', result)
                    if count_match:
                        theme_count = int(count_match.group(1))
                    
                    names_match = re.search(r'themes: ([^.]+)', result)
                    if names_match:
                        theme_names = [name.strip() for name in names_match.group(1).split(',')]
                except:
                    pass
            
            logger.info(f"Themes discovered for project: {project_path}")
            
            return self._create_success_result(
                "Themes discovered successfully",
                project_path=project_path,
                theme_count=theme_count,
                theme_names=theme_names,
                force_rediscovery=force_rediscovery,
                result=result
            )
            
        except Exception as e:
            logger.error(f"Error discovering themes: {e}")
            return self._create_error_result(f"Theme discovery failed: {str(e)}")
    
    async def _execute_validate_themes(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validate themes action using existing ThemeTools."""
        if not self.theme_tools:
            return self._create_failed_result(
                "No theme tools available - cannot validate themes",
                "validate_themes",
                parameters
            )
        
        try:
            project_path = parameters.get("project_path")
            specific_themes = parameters.get("themes", [])
            
            if not project_path:
                return self._create_error_result("Project path is required")
            
            # Use existing theme tools validation method
            result = await self.theme_tools.validate_themes({
                "project_path": project_path
            })
            
            # Check if validation was successful
            if "Error" in result:
                logger.error(f"Theme validation failed: {result}")
                return self._create_error_result(f"Theme validation failed: {result}")
            
            # Additional validation for specific themes if provided
            validation_details = {
                "total_themes_validated": 0,
                "valid_themes": [],
                "invalid_themes": [],
                "warnings": []
            }
            
            if specific_themes:
                # Validate each specified theme exists
                from pathlib import Path
                from ..utils.project_paths import get_themes_path
                
                themes_dir = get_themes_path(Path(project_path), self.config_manager)
                
                for theme in specific_themes:
                    theme_file = themes_dir / f"{theme}.json"
                    if theme_file.exists():
                        validation_details["valid_themes"].append(theme)
                    else:
                        validation_details["invalid_themes"].append(theme)
                        validation_details["warnings"].append(f"Theme file not found: {theme}.json")
                
                validation_details["total_themes_validated"] = len(specific_themes)
            
            logger.info(f"Themes validated for project: {project_path}")
            
            return self._create_success_result(
                "Themes validated successfully",
                project_path=project_path,
                validation_details=validation_details,
                result=result
            )
            
        except Exception as e:
            logger.error(f"Error validating themes: {e}")
            return self._create_error_result(f"Theme validation failed: {str(e)}")
    
    async def _execute_update_themes(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update themes action using file metadata and theme associations."""
        if not self.file_metadata_queries:
            return self._create_failed_result(
                "No file metadata queries available - cannot update themes",
                "update_themes",
                parameters
            )
        
        try:
            affected_file = parameters.get("affected_file")
            new_themes = parameters.get("themes", [])
            operation_type = parameters.get("operation", "file_change")
            
            if not affected_file:
                return self._create_error_result("Affected file path is required")
            
            # Update theme associations for the file using existing database method
            if new_themes:
                success = self.file_metadata_queries.update_file_theme_associations(affected_file, new_themes)
                if not success:
                    return self._create_error_result(f"Failed to update theme associations for {affected_file}")
            
            # Get current theme associations to verify update
            current_associations = self.file_metadata_queries.get_file_theme_associations(affected_file)
            
            # Log the theme update operation
            self.file_metadata_queries.modification_logging.log_file_modification(
                file_path=affected_file,
                file_type="theme_association",
                operation=operation_type,
                details={
                    "directive_driven": True,
                    "themes_updated": new_themes,
                    "operation_type": operation_type,
                    "current_associations": current_associations
                }
            )
            
            # Use theme tools for additional theme updates if available
            theme_result = None
            if self.theme_tools and hasattr(self.theme_tools, 'update_themes_for_file'):
                try:
                    theme_result = await self.theme_tools.update_themes_for_file(affected_file)
                except AttributeError:
                    # Method doesn't exist, continue with database-only update
                    pass
                except Exception as theme_error:
                    logger.warning(f"Theme tools update failed, using database-only approach: {theme_error}")
            
            logger.info(f"Themes updated for file: {affected_file}")
            
            return self._create_success_result(
                f"Themes updated for {affected_file}",
                affected_file=affected_file,
                themes_count=len(new_themes),
                updated_themes=new_themes,
                current_associations=current_associations,
                theme_tools_result=theme_result
            )
            
        except Exception as e:
            logger.error(f"Error updating themes: {e}")
            return self._create_error_result(f"Theme update failed: {str(e)}")