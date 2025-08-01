"""
Directory Operations Module

Handles directory metadata management for intelligent file discovery.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from ..db_manager import DatabaseManager


class DirectoryOperations:
    """Directory metadata management operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def update_directory_metadata(self, directory_metadata: Dict[str, Any]) -> bool:
        """
        Update directory metadata for intelligent file discovery.
        
        Args:
            directory_metadata: Dictionary with directory_path, purpose, description
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT OR REPLACE INTO directory_metadata
                (directory_path, purpose, description, last_updated)
                VALUES (?, ?, ?, ?)
            """
            
            self.db.execute_update(query, (
                directory_metadata.get('directory_path'),
                directory_metadata.get('purpose'),
                directory_metadata.get('description'),
                datetime.now().isoformat()
            ))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error updating directory metadata: {e}")
            return False
    
    def get_directory_metadata(self, directory_path: str) -> Optional[Dict[str, Any]]:
        """
        Get directory metadata for a specific path.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Directory metadata dictionary or None
        """
        try:
            query = """
                SELECT directory_path, purpose, description, last_updated
                FROM directory_metadata
                WHERE directory_path = ?
            """
            
            results = self.db.execute_query(query, (directory_path,))
            if results:
                row = results[0]
                return {
                    'directory_path': row['directory_path'],
                    'purpose': row['purpose'], 
                    'description': row['description'],
                    'last_updated': row['last_updated']
                }
            return None
            
        except Exception as e:
            self.db.logger.error(f"Error getting directory metadata: {e}")
            return None