"""
Project initialization operations.

Handles project structure creation and initial setup.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_operations import BaseProjectOperations
from ...utils.project_paths import get_management_folder_name

logger = logging.getLogger(__name__)


class ProjectInitializationOperations(BaseProjectOperations):
    """Handles project initialization and structure creation."""
    
    async def initialize_project(self, project_path: Path, project_name: str, force: bool = False, description: str = None, initialize_database: bool = True) -> str:
        """Initialize project management structure with directive-driven consultation."""
        try:
            project_path = Path(project_path).resolve()
            
            # Validate project path
            if not project_path.exists():
                return f"Project directory does not exist: {project_path}"
            
            # Check if project structure already exists
            project_mgmt_dir = self.get_project_management_dir(project_path)
            if project_mgmt_dir.exists() and not force:
                return f"Project management structure already exists at {project_mgmt_dir}. Use force=true to override."
            
            # CRITICAL: Use directive processor for proper AI-driven initialization
            # Debug logging to file for visibility
            debug_file = project_path / "debug_init.log"
            with open(debug_file, "w") as f:
                f.write("=== DEBUG INITIALIZATION LOG ===\n")
                f.write(f"Timestamp: {datetime.utcnow().isoformat()}\n\n")
            
            def write_debug(msg):
                with open(debug_file, "a") as f:
                    f.write(f"{msg}\n")
            
            if self.directive_processor:
                write_debug("[DEBUG_INIT] === PROJECT INITIALIZATION WITH DIRECTIVE PROCESSOR ===")
                write_debug(f"[DEBUG_INIT] Project path: {project_path}")
                write_debug(f"[DEBUG_INIT] Project name: {project_name}")
                write_debug(f"[DEBUG_INIT] DirectiveProcessor available: {self.directive_processor is not None}")
                logger.info("[DEBUG_INIT] === PROJECT INITIALIZATION WITH DIRECTIVE PROCESSOR ===")
                logger.info(f"[DEBUG_INIT] Project path: {project_path}")
                logger.info(f"[DEBUG_INIT] Project name: {project_name}")
                logger.info(f"[DEBUG_INIT] DirectiveProcessor available: {self.directive_processor is not None}")
                
                context = {
                    "trigger": "project_initialization", 
                    "project_path": str(project_path),
                    "project_name": project_name,
                    "force": force,
                    "management_dir": str(project_mgmt_dir),
                    "initialization_request": {
                        "project_path": str(project_path),
                        "project_name": project_name,
                        "description": description or f"AI-managed project: {project_name}",
                        "initialize_database": initialize_database,
                        "force_reinitialize": force
                    }
                }
                
                write_debug(f"[DEBUG_INIT] Context prepared: {list(context.keys())}")
                write_debug(f"[DEBUG_INIT] About to call directive_processor.execute_directive('projectInitialization')")
                logger.info(f"[DEBUG_INIT] Context prepared: {list(context.keys())}")
                logger.info(f"[DEBUG_INIT] About to call directive_processor.execute_directive('projectInitialization')")
                
                # Execute projectInitialization directive - this will escalate for proper consultation
                result = await self.directive_processor.execute_directive("projectInitialization", context)
                
                write_debug(f"[DEBUG_INIT] DirectiveProcessor result received")
                write_debug(f"[DEBUG_INIT] Result keys: {list(result.keys()) if result else 'None'}")
                write_debug(f"[DEBUG_INIT] Actions taken: {result.get('actions_taken', []) if result else 'None'}")
                write_debug(f"[DEBUG_INIT] Has actions: {bool(result.get('actions_taken')) if result else False}")
                write_debug(f"[DEBUG_INIT] Full result: {result}")
                logger.info(f"[DEBUG_INIT] DirectiveProcessor result received")
                logger.info(f"[DEBUG_INIT] Result keys: {list(result.keys()) if result else 'None'}")
                logger.info(f"[DEBUG_INIT] Actions taken: {result.get('actions_taken', []) if result else 'None'}")
                logger.info(f"[DEBUG_INIT] Has actions: {bool(result.get('actions_taken')) if result else False}")
                
                # The directive execution should handle the actual consultation and blueprint creation
                if result.get("actions_taken"):
                    # Add directive hook for server notification
                    if self.server_instance and hasattr(self.server_instance, 'on_project_operation_complete'):
                        hook_context = {
                            "trigger": "project_initialization_complete",
                            "operation_type": "project_initialization",
                            "project_path": str(project_path),
                            "project_name": project_name,
                            "actions_taken": result.get('actions_taken', []),
                            "timestamp": datetime.now().isoformat()
                        }
                        try:
                            await self.server_instance.on_project_operation_complete(hook_context, "projectManagement")
                        except Exception as e:
                            logger.warning(f"Project operation hook failed: {e}")
                    
                    return f"Project initialization directive executed successfully. Actions taken: {len(result.get('actions_taken', []))}"
                else:
                    write_debug(f"[DEBUG_INIT] *** DIRECTIVE PROCESSOR FAILED - NO ACTIONS DETERMINED ***")
                    write_debug(f"[DEBUG_INIT] DirectiveProcessor result: {result}")
                    write_debug(f"[DEBUG_INIT] FALLING BACK TO BASIC STRUCTURE CREATION")
                    logger.warning(f"[DEBUG_INIT] *** DIRECTIVE PROCESSOR FAILED - NO ACTIONS DETERMINED ***")
                    logger.warning(f"[DEBUG_INIT] DirectiveProcessor result: {result}")
                    logger.warning(f"[DEBUG_INIT] FALLING BACK TO BASIC STRUCTURE CREATION")
                    # Fall through to basic structure creation
                    
            else:
                write_debug("[DEBUG_INIT] *** NO DIRECTIVE PROCESSOR AVAILABLE - FALLING BACK ***")
                # Fallback to old behavior if no directive processor (should not happen in fixed system)
                logger.warning("[DEBUG_INIT] *** NO DIRECTIVE PROCESSOR AVAILABLE - FALLING BACK ***")
            
            write_debug(f"[DEBUG_INIT] === CREATING BASIC PROJECT STRUCTURE ===")
            write_debug(f"[DEBUG_INIT] About to call _create_project_structure")
            logger.info(f"[DEBUG_INIT] === CREATING BASIC PROJECT STRUCTURE ===")
            logger.info(f"[DEBUG_INIT] About to call _create_project_structure")
            
            # Create project structure
            await self._create_project_structure(project_path, project_name)
            
            logger.info(f"[DEBUG_INIT] Project structure created successfully")
            
            # Create and save blueprint
            blueprint_data = self.create_default_blueprint(project_name)
            blueprint_data["description"] = description or f"AI-managed project: {project_name}"
            
            self.save_blueprint(project_path, blueprint_data)
            
            result = f"Project '{project_name}' initialized successfully at {project_path}\n"
            result += f"- Management directory: {project_mgmt_dir}\n"
            result += f"- Blueprint created: {self.get_blueprint_file_path(project_path)}\n"
            
            # Initialize database if requested
            if initialize_database and self.db_manager:
                try:
                    from .database_operations import ProjectDatabaseOperations
                    db_ops = ProjectDatabaseOperations(self.db_manager, self.config_manager, self.directive_processor)
                    db_result = await db_ops._initialize_database(project_path)
                    result += f"- Database initialized: {self.get_database_file_path(project_path)}\n"
                    
                    # Start file metadata initialization if successful
                    if "successfully" in db_result.lower():
                        metadata_result = await db_ops._initialize_file_metadata(project_path, project_name)
                        if "started" in metadata_result.lower():
                            result += "- File metadata initialization started in background\n"
                        else:
                            result += f"- File metadata initialization: {metadata_result}\n"
                except Exception as e:
                    result += f"- Database initialization failed: {str(e)}\n"
                    logger.error(f"Database initialization error: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error initializing project: {e}")
            return f"Error initializing project: {str(e)}"
    
    async def _create_project_structure(self, project_path: Path, project_name: str):
        """Create the complete project management structure."""
        project_mgmt_dir = self.get_project_management_dir(project_path)
        
        # Create directory structure (matching original exactly)
        directories = [
            "ProjectBlueprint",
            "ProjectFlow",
            "ProjectLogic", 
            "Themes",
            "Tasks/active",
            "Tasks/sidequests",
            "Tasks/archive/tasks",
            "Tasks/archive/sidequests",
            "Implementations/active",
            "Implementations/archive",
            "Logs/archived",
            "Placeholders",
            "database"
        ]
        
        for dir_path in directories:
            (project_mgmt_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create metadata
        metadata = {
            "projectName": project_name,
            "createdDate": datetime.utcnow().isoformat(),
            "mcpVersion": "1.0.0",
            "lastModified": datetime.utcnow().isoformat()
        }
        
        # Create initial files (matching original exactly)
        files = {
            "ProjectBlueprint/blueprint.md": self.create_initial_blueprint(project_name),
            "ProjectBlueprint/metadata.json": json.dumps(metadata, indent=2),
            "ProjectFlow/flow-index.json": self.create_initial_flow_index(),
            "ProjectLogic/projectlogic.jsonl": "",
            "Themes/themes.json": json.dumps({}, indent=2),
            "Tasks/completion-path.json": json.dumps({
                "completionObjective": f"Complete {project_name} project development",
                "metadata": {
                    "createdDate": datetime.utcnow().isoformat(),
                    "version": "1.0.0"
                },
                "milestones": [],
                "riskFactors": [],
                "progressMetrics": {
                    "currentProgress": 0,
                    "estimatedCompletion": ""
                }
            }, indent=2),
            "Logs/noteworthy.json": json.dumps([], indent=2),
            "Placeholders/todos.jsonl": "",
            ".ai-pm-config.json": json.dumps({
                "project": {
                    "max_file_lines": 900,
                    "auto_modularize": True,
                    "theme_discovery": True,
                    "backup_enabled": True,
                    "management_folder_name": get_management_folder_name(self.config_manager)
                },
                "archiving": {
                    "projectlogicSizeLimit": "2MB",
                    "noteworthySizeLimit": "1MB",
                    "deleteArchivesOlderThan": "90 days"
                }
            }, indent=2)
        }
        
        for file_path, content in files.items():
            full_path = project_mgmt_dir / file_path
            if not full_path.exists() or full_path.stat().st_size == 0:
                full_path.write_text(content, encoding='utf-8')
        
        # Initialize database
        await self._initialize_database_fallback(project_path)
    
    async def _initialize_database_fallback(self, project_path: Path):
        """Initialize database as fallback when directive processor not available."""
        try:
            if self.db_manager:
                from .database_operations import ProjectDatabaseOperations
                db_ops = ProjectDatabaseOperations(self.db_manager, self.config_manager, self.directive_processor)
                await db_ops._initialize_database(project_path)
                logger.info(f"Database initialized for project at {project_path}")
            else:
                logger.warning("Database manager not available - skipping database initialization")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            # Don't fail the entire initialization if database fails