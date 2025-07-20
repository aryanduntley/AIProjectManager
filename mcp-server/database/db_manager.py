"""
Database Manager for AI Project Manager
Handles SQLite database connections, initialization, and schema management.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
import logging

class DatabaseManager:
    """Manages the SQLite database for the AI Project Manager."""
    
    def __init__(self, project_path: str):
        """
        Initialize the database manager.
        
        Args:
            project_path: Path to the project root directory
        """
        self.project_path = Path(project_path)
        self.project_mgmt_path = self.project_path / "projectManagement"
        self.db_path = self.project_mgmt_path / "project.db"
        self.schema_path = Path(__file__).parent.parent.parent / "reference" / "templates" / "database" / "schema.sql"
        self.connection: Optional[sqlite3.Connection] = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> sqlite3.Connection:
        """
        Create or connect to the SQLite database.
        
        Returns:
            SQLite connection object
        """
        if self.connection is None:
            # Ensure the projectManagement directory exists
            self.project_mgmt_path.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            
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
        if self.connection:
            self.connection.close()
            self.connection = None
    
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
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()