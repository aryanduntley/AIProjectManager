"""
Database initialization and setup functionality for MCP API.
"""

import logging
from typing import Dict, Any
from pathlib import Path

# Import database components
from ...database.db_manager import DatabaseManager
from ...database.session_queries import SessionQueries
from ...database.task_status_queries import TaskStatusQueries
from ...database.theme_flow_queries import ThemeFlowQueries
from ...database.file_metadata_queries import FileMetadataQueries
from ...database.user_preference_queries import UserPreferenceQueries
from ...database.event_queries import EventQueries
from ...utils.project_paths import get_project_management_path, get_database_path
from ...core.scope_engine import ScopeEngine
from ...core.processor import TaskProcessor

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Handles database initialization and component setup."""
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
    
    # Delegate to main registry attributes
    @property
    def config_manager(self):
        return self.tool_registry.config_manager
        
    @property
    def db_manager(self):
        return self.tool_registry.db_manager
        
    @db_manager.setter
    def db_manager(self, value):
        self.tool_registry.db_manager = value
        
    @property
    def session_queries(self):
        return self.tool_registry.session_queries
        
    @session_queries.setter  
    def session_queries(self, value):
        self.tool_registry.session_queries = value
        
    @property
    def task_queries(self):
        return self.tool_registry.task_queries
        
    @task_queries.setter
    def task_queries(self, value):
        self.tool_registry.task_queries = value
        
    @property
    def theme_flow_queries(self):
        return self.tool_registry.theme_flow_queries
        
    @theme_flow_queries.setter
    def theme_flow_queries(self, value):
        self.tool_registry.theme_flow_queries = value
        
    @property
    def file_metadata_queries(self):
        return self.tool_registry.file_metadata_queries
        
    @file_metadata_queries.setter
    def file_metadata_queries(self, value):
        self.tool_registry.file_metadata_queries = value
        
    @property
    def user_preference_queries(self):
        return self.tool_registry.user_preference_queries
        
    @user_preference_queries.setter
    def user_preference_queries(self, value):
        self.tool_registry.user_preference_queries = value
        
    @property
    def event_queries(self):
        return self.tool_registry.event_queries
        
    @event_queries.setter
    def event_queries(self, value):
        self.tool_registry.event_queries = value
        
    @property
    def analytics_dashboard(self):
        return self.tool_registry.analytics_dashboard
        
    @analytics_dashboard.setter
    def analytics_dashboard(self, value):
        self.tool_registry.analytics_dashboard = value
        
    @property
    def scope_engine(self):
        return self.tool_registry.scope_engine
        
    @scope_engine.setter
    def scope_engine(self, value):
        self.tool_registry.scope_engine = value
        
    @property
    def task_processor(self):
        return self.tool_registry.task_processor
        
    @task_processor.setter
    def task_processor(self, value):
        self.tool_registry.task_processor = value
    
    async def _initialize_database(self, project_path: str):
        """Initialize database components for the project."""
        # DEBUG_DATABASE: Track database initialization process
        debug_file = Path(".") / "debug_database.log"
        def write_database_debug(msg):
            try:
                with open(debug_file, "a") as f:
                    f.write(f"{msg}\n")
            except Exception:
                pass
        
        write_database_debug(f"[DEBUG_DATABASE] === _initialize_database CALLED ===")
        write_database_debug(f"[DEBUG_DATABASE] project_path: {project_path}")
        
        try:
            project_path_obj = Path(project_path)
            db_path = get_database_path(project_path_obj, self.config_manager)
            project_mgmt_dir = get_project_management_path(project_path_obj, self.config_manager)
            schema_path = project_mgmt_dir / "database" / "schema.sql"
            
            write_database_debug(f"[DEBUG_DATABASE] db_path: {db_path}")
            write_database_debug(f"[DEBUG_DATABASE] About to create DatabaseManager")
            
            write_database_debug(f"[DEBUG_DATABASE] Checking schema_path: {schema_path}")
            # Copy schema from ai-pm-mcp if it doesn't exist
            if not schema_path.exists():
                write_database_debug(f"[DEBUG_DATABASE] Schema doesn't exist, checking foundational location")
                # Get schema from ai-pm-mcp foundational location
                foundational_schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
                write_database_debug(f"[DEBUG_DATABASE] Foundational schema path: {foundational_schema_path}")
                if foundational_schema_path.exists():
                    write_database_debug(f"[DEBUG_DATABASE] Foundational schema exists, copying")
                    import shutil
                    # Create destination directory if it doesn't exist
                    schema_path.parent.mkdir(parents=True, exist_ok=True)
                    write_database_debug(f"[DEBUG_DATABASE] Destination directory created: {schema_path.parent}")
                    shutil.copy2(foundational_schema_path, schema_path)
                    write_database_debug(f"[DEBUG_DATABASE] ✅ Schema copied successfully")
                    logger.info(f"Copied foundational database schema to {schema_path}")
                else:
                    write_database_debug(f"[DEBUG_DATABASE] ⚠️ Foundational schema not found")
            else:
                write_database_debug(f"[DEBUG_DATABASE] ✅ Schema already exists")
            
            write_database_debug(f"[DEBUG_DATABASE] Schema handling completed")
            # Initialize database manager
            try:
                write_database_debug(f"[DEBUG_DATABASE] Testing DatabaseManager import")
                # DatabaseManager already imported at module level
                write_database_debug(f"[DEBUG_DATABASE] ✅ DatabaseManager import successful")
                
                write_database_debug(f"[DEBUG_DATABASE] Creating DatabaseManager with: {str(project_path_obj)}")
                self.db_manager = DatabaseManager(str(project_path_obj), self.config_manager)
                write_database_debug(f"[DEBUG_DATABASE] ✅ DatabaseManager created successfully")
                
                write_database_debug(f"[DEBUG_DATABASE] Connecting to database")
                self.db_manager.connect()
                write_database_debug(f"[DEBUG_DATABASE] ✅ Database connected successfully")
                
                write_database_debug(f"[DEBUG_DATABASE] Setting up database queries")
                # Continue with query setup
                write_database_debug(f"[DEBUG_DATABASE] Database connection phase completed successfully")
            except ImportError as import_error:
                write_database_debug(f"[DEBUG_DATABASE] ❌ IMPORT ERROR: {import_error}")
                write_database_debug(f"[DEBUG_DATABASE] Import error suggests path isolation issue")
                raise
            except Exception as db_error:
                write_database_debug(f"[DEBUG_DATABASE] ❌ DATABASE ERROR: {db_error}")
                write_database_debug(f"[DEBUG_DATABASE] Error type: {type(db_error)}")
                raise
            
            # Initialize query classes
            write_database_debug(f"[DEBUG_DATABASE] Initializing query classes")
            self.session_queries = SessionQueries(self.db_manager)
            write_database_debug(f"[DEBUG_DATABASE] ✅ SessionQueries initialized")
            self.task_queries = TaskStatusQueries(self.db_manager)
            write_database_debug(f"[DEBUG_DATABASE] ✅ TaskStatusQueries initialized")
            self.theme_flow_queries = ThemeFlowQueries(self.db_manager)
            write_database_debug(f"[DEBUG_DATABASE] ✅ ThemeFlowQueries initialized")
            self.file_metadata_queries = FileMetadataQueries(self.db_manager)
            write_database_debug(f"[DEBUG_DATABASE] ✅ FileMetadataQueries initialized")
            self.user_preference_queries = UserPreferenceQueries(self.db_manager)
            write_database_debug(f"[DEBUG_DATABASE] ✅ UserPreferenceQueries initialized")
            self.event_queries = EventQueries(self.db_manager)
            write_database_debug(f"[DEBUG_DATABASE] ✅ EventQueries initialized")
            
            # Initialize analytics dashboard
            write_database_debug(f"[DEBUG_DATABASE] Importing AnalyticsDashboard")
            from ...core.analytics_dashboard import AnalyticsDashboard
            write_database_debug(f"[DEBUG_DATABASE] ✅ AnalyticsDashboard imported successfully")
            self.analytics_dashboard = AnalyticsDashboard(
                session_queries=self.session_queries,
                task_queries=self.task_queries,
                theme_flow_queries=self.theme_flow_queries,
                file_metadata_queries=self.file_metadata_queries,
                user_preference_queries=self.user_preference_queries
            )
            write_database_debug(f"[DEBUG_DATABASE] ✅ AnalyticsDashboard initialized successfully")
            
            logger.info(f"Database and advanced intelligence initialized at {db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def _initialize_core_components(self, project_path: str):
        """Initialize core processing components with database integration."""
        try:
            mcp_server_path = Path(__file__).parent.parent
            
            # Initialize enhanced scope engine with database components
            self.scope_engine = ScopeEngine(
                mcp_server_path=mcp_server_path,
                theme_flow_queries=self.theme_flow_queries,
                session_queries=self.session_queries,
                file_metadata_queries=self.file_metadata_queries
            )
            
            # Initialize task processor
            self.task_processor = TaskProcessor(
                scope_engine=self.scope_engine,
                task_queries=self.task_queries,
                session_queries=self.session_queries,
                theme_flow_queries=self.theme_flow_queries,
                file_metadata_queries=self.file_metadata_queries
            )
            
            logger.info("Core processing components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing core components: {e}")
            raise