"""
Enhanced Database Manager for AI Project Manager
Handles SQLite database connections, initialization, schema management, and transaction handling.
Supports session persistence, theme-flow relationships, task tracking, and analytics.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple, Union
from contextlib import contextmanager
import logging
import threading

# Import ConfigManager for folder name configuration
try:
    from ..core.config_manager import ConfigManager
except ImportError:
    # Fallback if import fails
    ConfigManager = None

class DatabaseManager:
    """
    Enhanced database manager for AI Project Manager.
    
    Provides comprehensive database operations including:
    - Connection management with pooling
    - Transaction handling with rollback support
    - Schema initialization and migration
    - Performance optimization with indexes
    - Analytics and metrics collection
    """
    
    def __init__(self, project_path: str, config_manager: Optional['ConfigManager'] = None):
        """
        Initialize the database manager.
        
        Args:
            project_path: Path to the project root directory
            config_manager: Optional ConfigManager instance for folder name configuration
        """
        self.project_path = Path(project_path)
        self.config_manager = config_manager
        
        # Get management folder name from config or use default
        management_folder_name = "projectManagement"
        if self.config_manager and ConfigManager:
            try:
                management_folder_name = self.config_manager.get_management_folder_name()
            except Exception:
                # Fall back to default if config is not loaded
                pass
        
        self.project_mgmt_path = self.project_path / management_folder_name
        self.db_path = self.project_mgmt_path / "project.db"
        self.schema_path = Path(__file__).parent / "schema.sql"
        self.connection: Optional[sqlite3.Connection] = None
        self.logger = logging.getLogger(__name__)
        self._lock = threading.RLock()  # For thread safety
        self._in_transaction = False  # Track transaction state
        
        # Configuration
        self.enable_foreign_keys = True
        self.journal_mode = "WAL"  # Write-Ahead Logging for better concurrency
        self.synchronous = "NORMAL"  # Balance between safety and performance
        
    def connect(self) -> sqlite3.Connection:
        """
        Create or connect to the SQLite database with enhanced configuration.
        
        Returns:
            SQLite connection object
        """
        with self._lock:
            if self.connection is None:
                # Ensure the project management directory exists
                self.project_mgmt_path.mkdir(parents=True, exist_ok=True)
                
                # Connect to database with timeout and check_same_thread=False for threading
                self.connection = sqlite3.connect(
                    str(self.db_path), 
                    timeout=30.0,
                    check_same_thread=False
                )
                
                # Configure connection
                self.connection.row_factory = sqlite3.Row  # Enable dict-like access
                self.connection.execute(f"PRAGMA journal_mode = {self.journal_mode}")
                self.connection.execute(f"PRAGMA synchronous = {self.synchronous}")
                
                if self.enable_foreign_keys:
                    self.connection.execute("PRAGMA foreign_keys = ON")
                
                # Initialize schema if needed
                self._initialize_schema()
                
            return self.connection
    
    def _initialize_schema(self):
        """Initialize the database schema from the schema.sql file."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        
        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        cursor = self.connection.cursor()
        cursor.executescript(schema_sql)
        self.connection.commit()
        
        self.logger.info(f"Database schema initialized: {self.db_path}")
    
    def close(self):
        """Close the database connection."""
        with self._lock:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.logger.info("Database connection closed")
    
    async def initialize_database(self):
        """
        Explicit database initialization for when you want control over the lifecycle.
        
        This provides explicit initialization for AI sessions, tests, and tools that need
        predictable database setup timing and clear error handling at startup.
        
        Returns:
            self for method chaining
        """
        self.connect()  # Reuse existing lazy initialization logic
        self.logger.info("Database explicitly initialized")
        return self
    
    def execute(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as dictionaries (for test compatibility).
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of query results as dictionaries
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        # Convert sqlite3.Row objects to dictionaries
        return [dict(row) for row in rows]
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of query results
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(query, params)
        
        # Only commit if we're not inside a transaction
        if not self._in_transaction:
            connection.commit()
        
        return cursor.rowcount
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """
        Execute an INSERT query and return the inserted row ID.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            ID of the inserted row
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(query, params)
        
        # Only commit if we're not inside a transaction
        if not self._in_transaction:
            connection.commit()
            
        return cursor.lastrowid
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Optional path for backup file
            
        Returns:
            Path to the backup file
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = str(self.project_mgmt_path / f"project_backup_{timestamp}.db")
        
        connection = self.connect()
        with sqlite3.connect(backup_path) as backup_conn:
            connection.backup(backup_conn)
        
        self.logger.info(f"Database backup created: {backup_path}")
        return backup_path
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics and information.
        
        Returns:
            Dictionary with database statistics
        """
        connection = self.connect()
        
        stats = {
            "database_path": str(self.db_path),
            "database_size_mb": round(os.path.getsize(self.db_path) / (1024 * 1024), 2),
            "tables": {}
        }
        
        # Get table information
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table_row in tables:
            table_name = table_row['name']
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            stats["tables"][table_name] = count
        
        return stats
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions with automatic rollback on failure.
        
        Usage:
            with db_manager.transaction():
                db_manager.execute_update("INSERT INTO ...", params)
                db_manager.execute_update("UPDATE ...", params)
        """
        connection = self.connect()
        old_transaction_state = self._in_transaction
        self._in_transaction = True
        try:
            yield connection
            connection.commit()
            self.logger.debug("Transaction committed successfully")
        except Exception as e:
            connection.rollback()
            self.logger.error(f"Transaction failed, rolled back: {e}")
            raise
        finally:
            self._in_transaction = old_transaction_state
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute a query multiple times with different parameters.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Total number of affected rows
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.executemany(query, params_list)
        connection.commit()
        return cursor.rowcount
    
    def get_last_insert_id(self) -> Optional[int]:
        """
        Get the ID of the last inserted row.
        
        Returns:
            Last insert row ID or None
        """
        if self.connection:
            return self.connection.lastrowid
        return None
    
    def optimize_database(self):
        """
        Optimize the database by running VACUUM and ANALYZE commands.
        This helps maintain performance for large datasets.
        """
        connection = self.connect()
        cursor = connection.cursor()
        
        # Analyze tables to update query planner statistics
        cursor.execute("ANALYZE")
        
        # Vacuum to reclaim space and defragment
        cursor.execute("VACUUM")
        
        connection.commit()
        self.logger.info("Database optimization completed")
    
    def check_integrity(self) -> bool:
        """
        Check database integrity.
        
        Returns:
            True if database integrity is ok, False otherwise
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        
        integrity_ok = result and result[0] == "ok"
        if integrity_ok:
            self.logger.info("Database integrity check passed")
        else:
            self.logger.error(f"Database integrity check failed: {result}")
        
        return integrity_ok
    
    def get_schema_version(self) -> Optional[str]:
        """
        Get the current schema version from user_version pragma.
        
        Returns:
            Schema version string or None
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute("PRAGMA user_version")
        result = cursor.fetchone()
        return str(result[0]) if result else None
    
    def set_schema_version(self, version: str):
        """
        Set the schema version.
        
        Args:
            version: Version string to set
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA user_version = {version}")
        connection.commit()
        self.logger.info(f"Schema version set to: {version}")
    
    def execute_script(self, script: str):
        """
        Execute a SQL script with multiple statements.
        
        Args:
            script: SQL script to execute
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.executescript(script)
        connection.commit()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()