"""
Logging Action Executor

Handles logging and event actions for directive execution.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


class LoggingActionExecutor(BaseActionExecutor):
    """Executes logging and event actions using existing logging infrastructure."""
    
    def get_supported_actions(self) -> list[str]:
        """Get list of logging action types this executor supports."""
        return [
            "log_noteworthy_event",
            "update_projectlogic",
            "log_directive_execution"
        ]
    
    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a logging action."""
        if action_type == "log_noteworthy_event":
            return await self._execute_log_noteworthy_event(parameters)
        elif action_type == "update_projectlogic":
            return await self._execute_update_projectlogic(parameters)
        elif action_type == "log_directive_execution":
            return await self._execute_log_directive_execution(parameters)
        else:
            return self._create_error_result(f"Unknown logging action type: {action_type}")
    
    async def _execute_log_noteworthy_event(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute log noteworthy event action using existing EventQueries with enhanced parameters."""
        try:
            # Extract enhanced parameters for better event logging
            event_type = parameters.get("event", parameters.get("event_type", "unknown_event"))
            title = parameters.get("title", f"Event: {event_type}")
            description = parameters.get("description", "")
            event_data = parameters.get("parameters", parameters)
            project_context = parameters.get("context", {})
            impact_level = parameters.get("impact_level", "normal")
            primary_theme = parameters.get("primary_theme")
            task_id = parameters.get("task_id")
            
            # Enhanced event data structure
            enhanced_event_data = {
                "title": title,
                "description": description,
                "original_parameters": event_data,
                "directive_driven": True,
                "primary_theme": primary_theme,
                "task_id": task_id
            }
            
            if self.event_queries:
                try:
                    # Use existing EventQueries with enhanced data
                    event_id = self.event_queries.log_event(
                        event_type=event_type,
                        event_data=enhanced_event_data,
                        project_context=project_context,
                        impact_level=impact_level
                    )
                    
                    logger.info(f"Noteworthy event logged: {event_type} (ID: {event_id})")
                    
                    return self._create_success_result(
                        f"Noteworthy event '{title}' logged successfully",
                        event_id=event_id,
                        event_type=event_type,
                        title=title,
                        impact_level=impact_level
                    )
                    
                except Exception as e:
                    logger.error(f"Database event logging failed: {e}")
                    # Fall back to enhanced fallback method
                    return await self._enhanced_fallback_log_event(parameters)
            else:
                # Use enhanced fallback method
                return await self._enhanced_fallback_log_event(parameters)
                
        except Exception as e:
            logger.error(f"Error processing noteworthy event: {e}")
            return self._create_error_result(f"Event logging failed: {str(e)}")
    
    async def _execute_update_projectlogic(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update project logic action by writing to projectlogic.jsonl file."""
        # Project logic is distinct from event logging - writes to actual projectlogic.jsonl file
        # Tracks major logical decisions and project reasoning evolution
        
        try:
            project_path = parameters.get("project_path")
            if not project_path:
                return self._create_error_result("Project path is required for project logic updates")
            
            # Extract project logic entry components (based on template format)
            entry_type = parameters.get("type", "logic-update")
            description = parameters.get("description", parameters.get("summary", ""))
            reasoning = parameters.get("reasoning", parameters.get("reason", ""))
            impact = parameters.get("impact", [])
            affected_themes = parameters.get("affectedThemes", parameters.get("affected_themes", []))
            files = parameters.get("files", [])
            decision = parameters.get("decision", "")
            related_task = parameters.get("relatedTask", parameters.get("related_task"))
            related_sidequest = parameters.get("relatedSidequest", parameters.get("related_sidequest"))
            
            if not description:
                return self._create_error_result("Description/summary is required for project logic entry")
            
            # Create properly formatted project logic entry
            logic_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": entry_type,
                "description": description,
                "reasoning": reasoning,
                "impact": impact,
                "affectedThemes": affected_themes,
                "files": files,
                "decision": decision
            }
            
            # Add optional fields if present
            if related_task:
                logic_entry["relatedTask"] = related_task
            if related_sidequest:
                logic_entry["relatedSidequest"] = related_sidequest
            
            # Additional fields for specific entry types
            if entry_type == "architecture-pivot":
                logic_entry["previousDirection"] = parameters.get("previousDirection", "")
                logic_entry["newDirection"] = parameters.get("newDirection", "")
                logic_entry["userDiscussion"] = parameters.get("userDiscussion", "")
            elif entry_type == "scope-refinement" or entry_type == "scope-escalation":
                logic_entry["newComponents"] = parameters.get("newComponents", [])
                logic_entry["dependencies"] = parameters.get("dependencies", [])
            
            # Write to projectlogic.jsonl file
            try:
                from pathlib import Path
                from ..utils.project_paths import get_project_management_path
                
                project_mgmt_dir = get_project_management_path(Path(project_path), self.config_manager)
                logic_file = project_mgmt_dir / "ProjectLogic" / "projectlogic.jsonl"
                
                if not project_mgmt_dir.exists():
                    return self._create_error_result(f"Project management directory not found: {project_mgmt_dir}")
                
                # Ensure ProjectLogic directory exists
                logic_file.parent.mkdir(exist_ok=True)
                
                # Append entry to projectlogic.jsonl
                with open(logic_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(logic_entry) + '\n')
                
                logger.info(f"Project logic updated: {entry_type} - {description}")
                
                return self._create_success_result(
                    f"Project logic updated: {entry_type}",
                    logic_entry=logic_entry,
                    file_path=str(logic_file),
                    project_path=project_path,
                    entry_type=entry_type
                )
                
            except Exception as e:
                logger.error(f"Failed to write to projectlogic.jsonl: {e}")
                return self._create_error_result(f"Failed to write project logic: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error processing project logic update: {e}")
            return self._create_error_result(f"Project logic update failed: {str(e)}")
    
    async def _execute_log_directive_execution(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute log directive execution action."""
        directive_key = parameters.get("directive_key", "unknown")
        trigger = parameters.get("trigger", "unknown")
        
        logger.info(f"Directive executed: {directive_key} with trigger {trigger}")
        
        return self._create_success_result(
            "Directive execution logged",
            directive_key=directive_key,
            trigger=trigger
        )
    
    # Enhanced fallback implementations for when database not available
    async def _enhanced_fallback_log_event(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced fallback logging with file writing capability when event queries not available."""
        try:
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "event_type": parameters.get("event", parameters.get("event_type", "unknown_event")),
                "title": parameters.get("title", "Untitled Event"),
                "description": parameters.get("description", ""),
                "impact_level": parameters.get("impact_level", "normal"),
                "parameters": parameters,
                "fallback_logged": True
            }
            
            # Try to write to project noteworthy file if project path available
            project_path = parameters.get("context", {}).get("project_path")
            if project_path:
                try:
                    from pathlib import Path
                    from ..utils.project_paths import get_project_management_path
                    
                    project_mgmt_dir = get_project_management_path(Path(project_path), None)
                    noteworthy_file = project_mgmt_dir / "ProjectLogic" / "noteworthy-fallback.jsonl"
                    
                    if project_mgmt_dir.exists():
                        # Ensure ProjectLogic directory exists
                        noteworthy_file.parent.mkdir(exist_ok=True)
                        
                        # Append to fallback noteworthy file
                        with open(noteworthy_file, 'a', encoding='utf-8') as f:
                            f.write(json.dumps(event_data) + '\n')
                        
                        logger.info(f"Noteworthy event written to: {noteworthy_file}")
                        
                        return self._create_success_result(
                            "Event logged via enhanced fallback (file write)",
                            event_data=event_data,
                            file_path=str(noteworthy_file),
                            project_path=project_path
                        )
                        
                except Exception as file_error:
                    logger.warning(f"File write failed: {file_error}")
                    # Continue to basic logging fallback
            
            # Basic logging fallback
            log_message = f"NOTEWORTHY EVENT: {json.dumps(event_data)}"
            logger.info(log_message)
            
            return self._create_success_result(
                "Event logged via basic fallback (logging only)",
                event_data=event_data
            )
            
        except Exception as e:
            logger.error(f"Enhanced fallback logging failed: {e}")
            return self._create_error_result(f"Fallback logging failed: {str(e)}")
    
    # Keep original fallback for backward compatibility
    async def _fallback_log_event(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Basic fallback logging - kept for compatibility."""
        return await self._enhanced_fallback_log_event(parameters)
    
    async def _fallback_update_projectlogic(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback project logic update - should not be needed since main method handles file operations."""
        # This fallback should rarely be called since the main method now handles file operations directly
        logger.warning("Using fallback project logic update - main method should handle this")
        
        try:
            # Create basic project logic entry format
            logic_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": parameters.get("type", "directive_action"),
                "description": parameters.get("description", "Fallback project logic entry"),
                "reasoning": parameters.get("reasoning", "Updated via fallback method"),
                "impact": parameters.get("impact", []),
                "affectedThemes": parameters.get("affectedThemes", []),
                "files": parameters.get("files", []),
                "decision": parameters.get("decision", "")
            }
            
            # Basic logging as last resort
            logger.info(f"PROJECT LOGIC FALLBACK: {json.dumps(logic_entry)}")
            
            return self._create_success_result(
                "Project logic updated via fallback logging only",
                logic_entry=logic_entry,
                warning="File write not available - logged to console only"
            )
            
        except Exception as e:
            logger.error(f"Fallback project logic update failed: {e}")
            return self._create_error_result(f"Fallback update failed: {str(e)}")