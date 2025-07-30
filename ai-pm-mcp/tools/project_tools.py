"""
Project management tools for the AI Project Manager MCP Server.

Handles project initialization, blueprint management, and project structure operations.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import shutil

from ..core.mcp_api import ToolDefinition
from ..database.db_manager import DatabaseManager
from ..database.session_queries import SessionQueries
from ..database.task_status_queries import TaskStatusQueries
from ..database.theme_flow_queries import ThemeFlowQueries
from ..database.file_metadata_queries import FileMetadataQueries

logger = logging.getLogger(__name__)


class ProjectTools:
    """Tools for project management operations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.tools = []
        self.db_manager = db_manager
        self.session_queries = SessionQueries(db_manager) if db_manager else None
        self.task_queries = TaskStatusQueries(db_manager) if db_manager else None
        self.theme_flow_queries = ThemeFlowQueries(db_manager) if db_manager else None
        self.file_metadata_queries = FileMetadataQueries(db_manager) if db_manager else None
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all project management tools."""
        return [
            ToolDefinition(
                name="project_initialize",
                description="Initialize project management structure in a directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "project_name": {
                            "type": "string", 
                            "description": "Name of the project"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force initialization even if structure exists",
                            "default": False
                        }
                    },
                    "required": ["project_path", "project_name"]
                },
                handler=self.initialize_project
            ),
            ToolDefinition(
                name="project_get_blueprint",
                description="Get the current project blueprint",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_blueprint
            ),
            ToolDefinition(
                name="project_update_blueprint",
                description="Update the project blueprint",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "content": {
                            "type": "string",
                            "description": "New blueprint content in markdown"
                        }
                    },
                    "required": ["project_path", "content"]
                },
                handler=self.update_blueprint
            ),
            ToolDefinition(
                name="project_get_status",
                description="Get overall project status and structure information",
                input_schema={
                    "type": "object", 
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_project_status
            ),
            ToolDefinition(
                name="project_init_database",
                description="Initialize database for an existing project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.initialize_database
            ),
            ToolDefinition(
                name="resume_initialization",
                description="Resume incomplete file metadata initialization",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.resume_file_metadata_initialization
            ),
            ToolDefinition(
                name="get_initialization_progress",
                description="Get current file metadata initialization progress",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_initialization_progress
            )
        ]
    
    async def initialize_project(self, arguments: Dict[str, Any]) -> str:
        """Initialize project management structure."""
        try:
            project_path = Path(arguments["project_path"])
            project_name = arguments["project_name"]
            force = arguments.get("force", False)
            
            # Validate project path
            if not project_path.exists():
                return f"Project directory does not exist: {project_path}"
            
            # Check if project structure already exists
            project_mgmt_dir = project_path / "projectManagement"
            if project_mgmt_dir.exists() and not force:
                return f"Project management structure already exists at {project_mgmt_dir}. Use force=true to override."
            
            # Create the structure
            await self._create_project_structure(project_path, project_name)
            
            return f"Project management structure initialized successfully at {project_mgmt_dir}"
            
        except Exception as e:
            logger.error(f"Error initializing project: {e}")
            return f"Error initializing project: {str(e)}"
    
    async def _create_project_structure(self, project_path: Path, project_name: str):
        """Create the complete project management structure."""
        project_mgmt_dir = project_path / "projectManagement"
        
        # Create directory structure
        directories = [
            "ProjectBlueprint",
            "ProjectFlow",
            "ProjectLogic", 
            "Themes",
            "Tasks/active",
            "Tasks/sidequests",
            "Tasks/archive/tasks",
            "Tasks/archive/sidequests",
            "Logs/archived",
            "Placeholders",
            "UserSettings",
            "database"
        ]
        
        for dir_path in directories:
            (project_mgmt_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create metadata
        metadata = {
            "projectName": project_name,
            "createdDate": datetime.now().isoformat(),
            "mcpVersion": "1.0.0",
            "lastModified": datetime.now().isoformat()
        }
        
        # Create initial files
        files = {
            "ProjectBlueprint/blueprint.md": self._create_initial_blueprint(project_name),
            "ProjectBlueprint/metadata.json": json.dumps(metadata, indent=2),
            "ProjectFlow/flow-index.json": self._create_initial_flow_index(),
            "ProjectLogic/projectlogic.jsonl": "",
            "Themes/themes.json": json.dumps({}, indent=2),
            "Tasks/completion-path.json": json.dumps({
                "completionObjective": f"Complete {project_name} project development",
                "metadata": {
                    "createdDate": datetime.now().isoformat(),
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
            "UserSettings/config.json": json.dumps({
                "project": {
                    "max_file_lines": 900,
                    "auto_modularize": True,
                    "theme_discovery": True,
                    "backup_enabled": True
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
        await self._initialize_database(project_path)
    
    def _create_initial_blueprint(self, project_name: str) -> str:
        """Create initial project blueprint content."""
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

---

**Note**: This blueprint must be reviewed and approved by the user before development begins. See the scope files in `/projectManagement/Themes/` for more detailed information when needed.
"""
    
    def _create_initial_flow_index(self) -> str:
        """Create initial flow index JSON content."""
        flow_index = {
            "metadata": {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "description": "Master flow index with flow file references and cross-flow dependencies",
                "totalFlows": 0,
                "flowFiles": []
            },
            "flowFiles": [],
            "crossFlowDependencies": [],
            "globalFlowSettings": {
                "validationRules": [],
                "statusTracking": {
                    "flowLevel": ["pending", "in-progress", "complete", "needs-review"],
                    "stepLevel": ["pending", "in-progress", "complete", "needs-analyze", "blocked"]
                }
            },
            "flowFileMetadata": []
        }
        return json.dumps(flow_index, indent=2)
    
    async def get_blueprint(self, arguments: Dict[str, Any]) -> str:
        """Get the current project blueprint."""
        try:
            project_path = Path(arguments["project_path"])
            blueprint_path = project_path / "projectManagement" / "ProjectBlueprint" / "blueprint.md"
            
            if not blueprint_path.exists():
                return f"No blueprint found at {blueprint_path}. Initialize project first."
            
            content = blueprint_path.read_text(encoding='utf-8')
            return f"Project Blueprint:\n\n{content}"
            
        except Exception as e:
            logger.error(f"Error reading blueprint: {e}")
            return f"Error reading blueprint: {str(e)}"
    
    async def update_blueprint(self, arguments: Dict[str, Any]) -> str:
        """Update the project blueprint."""
        try:
            project_path = Path(arguments["project_path"])
            content = arguments["content"]
            
            blueprint_path = project_path / "projectManagement" / "ProjectBlueprint" / "blueprint.md"
            metadata_path = project_path / "projectManagement" / "ProjectBlueprint" / "metadata.json"
            
            if not blueprint_path.parent.exists():
                return f"Project management structure not found. Initialize project first."
            
            # Update blueprint content
            blueprint_path.write_text(content, encoding='utf-8')
            
            # Update metadata
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text())
                metadata["lastModified"] = datetime.now().isoformat()
                metadata_path.write_text(json.dumps(metadata, indent=2))
            
            return f"Blueprint updated successfully at {blueprint_path}"
            
        except Exception as e:
            logger.error(f"Error updating blueprint: {e}")
            return f"Error updating blueprint: {str(e)}"
    
    async def get_project_status(self, arguments: Dict[str, Any]) -> str:
        """Get overall project status and structure information."""
        try:
            project_path = Path(arguments["project_path"])
            project_mgmt_dir = project_path / "projectManagement"
            
            if not project_mgmt_dir.exists():
                return f"No project management structure found at {project_path}. Initialize project first."
            
            # Gather status information
            status = {
                "projectPath": str(project_path),
                "managementStructure": str(project_mgmt_dir),
                "initialized": True,
                "components": {}
            }
            
            # Check component status
            components = {
                "blueprint": project_mgmt_dir / "ProjectBlueprint" / "blueprint.md",
                "flow": project_mgmt_dir / "ProjectFlow" / "flow-index.json", 
                "logic": project_mgmt_dir / "ProjectLogic" / "projectlogic.jsonl",
                "themes": project_mgmt_dir / "Themes" / "themes.json",
                "completionPath": project_mgmt_dir / "Tasks" / "completion-path.json",
                "config": project_mgmt_dir / "UserSettings" / "config.json",
                "database": project_mgmt_dir / "project.db",
                "schema": project_mgmt_dir / "database" / "schema.sql"
            }
            
            for name, path in components.items():
                status["components"][name] = {
                    "exists": path.exists(),
                    "path": str(path),
                    "size": path.stat().st_size if path.exists() else 0
                }
            
            # Count tasks
            active_tasks = list((project_mgmt_dir / "Tasks" / "active").glob("*.json"))
            sidequests = list((project_mgmt_dir / "Tasks" / "sidequests").glob("*.json"))
            
            status["tasks"] = {
                "active": len(active_tasks),
                "sidequests": len(sidequests)
            }
            
            # Check database status
            db_path = project_mgmt_dir / "project.db"
            status["database"] = {
                "exists": db_path.exists(),
                "size": db_path.stat().st_size if db_path.exists() else 0
            }
            
            # Check themes
            themes_file = project_mgmt_dir / "Themes" / "themes.json"
            if themes_file.exists():
                try:
                    themes_data = json.loads(themes_file.read_text())
                    status["themes"] = {
                        "count": len(themes_data),
                        "themes": list(themes_data.keys())
                    }
                except:
                    status["themes"] = {"count": 0, "themes": []}
            
            return f"Project Status:\n\n{json.dumps(status, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            return f"Error getting project status: {str(e)}"
    
    async def _initialize_database(self, project_path: Path):
        """Initialize database for the project with file metadata discovery."""
        try:
            db_path = project_path / "projectManagement" / "project.db"
            schema_path = project_path / "projectManagement" / "database" / "schema.sql"
            
            # Copy foundational schema if it doesn't exist
            if not schema_path.exists():
                # Get schema from foundational ai-pm-mcp location
                foundational_schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
                if foundational_schema_path.exists():
                    shutil.copy2(foundational_schema_path, schema_path)
                    logger.info(f"Copied foundational database schema to {schema_path}")
                else:
                    logger.warning(f"Foundational database schema not found at {foundational_schema_path}")
                    return
            
            # Initialize database manager
            db_manager = DatabaseManager(str(project_path))
            db_manager.connect()
            
            # Initialize query classes
            session_queries = SessionQueries(db_manager)
            task_queries = TaskStatusQueries(db_manager)
            theme_flow_queries = ThemeFlowQueries(db_manager)
            file_metadata_queries = FileMetadataQueries(db_manager)
            
            # Create initial session for project setup
            session_id = session_queries.start_session(str(project_path))
            logger.info(f"Database initialized at {db_path} with session {session_id}")
            
            # Start file metadata initialization process
            await self._initialize_file_metadata(
                project_path, session_id, session_queries, file_metadata_queries
            )
            
            # Log initial project creation
            file_metadata_queries.log_file_modification(
                file_path="projectManagement/",
                file_type="project",
                operation="create",
                session_id=session_id,
                details={"action": "project_initialization", "structure_created": True}
            )
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def _initialize_file_metadata(
        self, 
        project_path: Path, 
        session_id: str, 
        session_queries, 
        file_metadata_queries
    ):
        """Initialize file metadata using database-driven approach (replaces README.json)."""
        try:
            logger.info("Starting database-driven file metadata initialization")
            
            # Step 1: Discover all project files
            discovered_files = file_metadata_queries.discover_project_files(
                str(project_path),
                exclude_patterns=[
                    'projectManagement/UserSettings/*',
                    'projectManagement/database/backups/*',
                    '__pycache__/*', '*.pyc', '.git/*', 'node_modules/*'
                ]
            )
            
            # Flatten discovered files for processing
            all_files = []
            for category, files in discovered_files.items():
                all_files.extend(files)
            
            if not all_files:
                logger.warning("No files discovered during initialization")
                return
            
            # Step 2: Start initialization tracking in session
            success = session_queries.start_initialization(session_id, len(all_files))
            if not success:
                logger.error("Failed to start initialization tracking")
                return
            
            logger.info(f"Discovered {len(all_files)} files for analysis")
            
            # Step 3: Analyze files in batches for better performance
            batch_size = 50  # Process files in batches of 50
            processed_count = 0
            
            for i in range(0, len(all_files), batch_size):
                batch = all_files[i:i + batch_size]
                
                # Analyze this batch of files
                batch_results = await file_metadata_queries.batch_analyze_files(
                    batch, str(project_path)
                )
                
                processed_count += len(batch)
                logger.info(f"Processed {processed_count}/{len(all_files)} files")
                
                # Update session progress
                session_queries.increment_files_processed(session_id, len(batch))
            
            # Step 4: Mark initialization as complete
            session_queries.complete_initialization(session_id)
            
            logger.info(f"File metadata initialization completed: {processed_count} files analyzed")
            
        except Exception as e:
            logger.error(f"Error during file metadata initialization: {e}")
            # Mark initialization as failed but don't raise - allow project init to continue
            session_queries.update_initialization_phase(session_id, 'failed')
    
    async def initialize_database(self, arguments: Dict[str, Any]) -> str:
        """Initialize database for an existing project."""
        try:
            project_path = Path(arguments["project_path"])
            
            if not project_path.exists():
                return f"Project directory does not exist: {project_path}"
            
            project_mgmt_dir = project_path / "projectManagement"
            if not project_mgmt_dir.exists():
                return f"Project management structure not found. Initialize project first."
            
            await self._initialize_database(project_path)
            return f"Database initialized successfully for project at {project_path}"
            
        except Exception as e:
            logger.error(f"Error in initialize_database: {e}")
            return f"Error initializing database: {str(e)}"
    
    async def resume_file_metadata_initialization(self, arguments: Dict[str, Any]) -> str:
        """Resume incomplete file metadata initialization."""
        try:
            project_path = Path(arguments["project_path"])
            
            if not project_path.exists():
                return f"Project directory does not exist: {project_path}"
            
            # Initialize database connection
            db_manager = DatabaseManager(str(project_path))
            db_manager.connect()
            
            # Initialize query classes
            session_queries = SessionQueries(db_manager)
            file_metadata_queries = FileMetadataQueries(db_manager)
            
            # Check for sessions needing initialization
            incomplete_sessions = session_queries.get_sessions_needing_initialization()
            if not incomplete_sessions:
                return "No incomplete initialization sessions found."
            
            # Get the most recent incomplete session
            session_data = incomplete_sessions[0]
            session_id = session_data['session_id']
            
            logger.info(f"Resuming initialization for session {session_id}")
            
            # Get unanalyzed files
            unanalyzed_files = file_metadata_queries.get_unanalyzed_files()
            
            if not unanalyzed_files:
                # Mark as complete if no unanalyzed files remain
                session_queries.complete_initialization(session_id)
                return f"File metadata initialization was already complete for session {session_id}"
            
            # Resume file analysis
            batch_size = 50
            processed_count = 0
            
            for i in range(0, len(unanalyzed_files), batch_size):
                batch = unanalyzed_files[i:i + batch_size]
                
                # Analyze this batch of files
                batch_results = await file_metadata_queries.batch_analyze_files(
                    batch, str(project_path)
                )
                
                processed_count += len(batch)
                logger.info(f"Resumed analysis: {processed_count}/{len(unanalyzed_files)} files")
                
                # Update session progress
                session_queries.increment_files_processed(session_id, len(batch))
            
            # Mark initialization as complete
            session_queries.complete_initialization(session_id)
            
            return f"File metadata initialization resumed and completed: {processed_count} files analyzed"
            
        except Exception as e:
            logger.error(f"Error resuming file metadata initialization: {e}")
            return f"Error resuming initialization: {str(e)}"
    
    async def get_initialization_progress(self, arguments: Dict[str, Any]) -> str:
        """Get current file metadata initialization progress."""
        try:
            project_path = Path(arguments["project_path"])
            
            if not project_path.exists():
                return f"Project directory does not exist: {project_path}"
            
            # Initialize database connection
            db_manager = DatabaseManager(str(project_path))
            db_manager.connect()
            
            # Initialize query classes
            session_queries = SessionQueries(db_manager)
            file_metadata_queries = FileMetadataQueries(db_manager)
            
            # Get initialization status
            status = session_queries.get_initialization_status()
            
            if not status:
                return "No initialization sessions found."
            
            # Get progress details
            progress = file_metadata_queries.get_initialization_progress()
            
            summary = f"""File Metadata Initialization Status:

Session ID: {status['session_id']}
Phase: {status['initialization_phase']}
Progress: {status['files_processed']}/{status['total_files_discovered']} files ({progress['completion_percentage']:.1f}%)
Started: {status.get('initialization_started_at', 'Unknown')}
Completed: {status.get('initialization_completed_at', 'In progress')}

Remaining files: {progress['remaining_files']}
Analysis rate: {progress.get('analysis_rate', 'Unknown')} files/min
"""
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting initialization progress: {e}")
            return f"Error getting progress: {str(e)}"