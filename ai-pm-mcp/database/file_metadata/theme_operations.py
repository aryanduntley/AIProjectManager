import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..db_manager import DatabaseManager

class ThemeOperations:
    def __init__(self, db_manager: DatabaseManager, modification_logging=None):
        self.db = db_manager
        self.modification_logging = modification_logging

	# Theme-File Integration (works with existing theme system)
    
    def update_file_theme_associations(
        self,
        file_path: str,
        themes: List[str],
        association_type: str = "belongs_to"
    ) -> bool:
        """
        Update theme associations for a file.
        
        This would be used to maintain theme-file relationships
        based on the existing theme system.
        
        Args:
            file_path: File path
            themes: List of theme names
            association_type: Type of association (belongs_to, references, imports)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            
            # Get previous associations for logging
            previous_query = """
                SELECT theme_associations 
                FROM file_metadata 
                WHERE file_path = ?
            """
            previous_results = self.db.execute_query(previous_query, (file_path,))
            previous_associations = []
            if previous_results and len(previous_results) > 0:
                theme_associations_str = previous_results[0]["theme_associations"]
                if theme_associations_str:
                    previous_associations = json.loads(theme_associations_str)
            
            # Update the file_metadata table with new theme associations
            update_query = """
                INSERT OR REPLACE INTO file_metadata 
                (file_path, theme_associations, updated_at)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(file_path) DO UPDATE SET
                    theme_associations = excluded.theme_associations,
                    updated_at = excluded.updated_at
            """
            
            self.db.execute_update(update_query, (
                file_path,
                json.dumps(themes)
            ))
            
            # Log the theme association change
            details = {
                "themes": themes,
                "association_type": association_type,
                "previous_associations": previous_associations
            }
            
            if self.modification_logging:
                self.modification_logging.log_file_modification(
                    file_path=file_path,
                    file_type="theme_association",
                    operation="update",
                    details=details
                )
            
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error updating file theme associations: {e}")
            return False
    
    def get_files_by_theme(self, theme_name: str) -> List[Dict[str, Any]]:
        """
        Get files associated with a theme.
        
        This integrates with the theme system to provide file listings.
        
        Args:
            theme_name: Theme name
            
        Returns:
            List of files with their associations
        """
        # Get recent file modifications for theme-related files
        theme_modifications = self.db.execute_query("""
            SELECT file_path, file_type, operation, timestamp, details
            FROM file_modifications
            WHERE JSON_EXTRACT(details, '$.themes') LIKE '%"' || ? || '"%'
            OR file_type = 'theme'
            ORDER BY timestamp DESC
        """, (theme_name,))
        
        results = []
        for row in theme_modifications:
            details = json.loads(row["details"]) if row["details"] else {}
            
            results.append({
                "file_path": row["file_path"],
                "file_type": row["file_type"],
                "operation": row["operation"],
                "timestamp": row["timestamp"],
                "themes": details.get("themes", []),
                "association_type": details.get("association_type", "unknown")
            })
        
        return results
    
    def get_theme_file_coverage(self, theme_name: str) -> Dict[str, Any]:
        """
        Get file coverage analysis for a theme.
        
        Args:
            theme_name: Theme name
            
        Returns:
            Coverage analysis dictionary
        """
        theme_files = self.get_files_by_theme(theme_name)
        
        # Analyze file types
        file_types = {}
        for file_info in theme_files:
            file_type = file_info["file_type"]
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        # Recent activity
        recent_modifications = len([
            f for f in theme_files 
            if f["timestamp"] >= (datetime.now() - datetime.timedelta(days=7)).isoformat()
        ])
        
        return {
            "theme_name": theme_name,
            "total_files": len(theme_files),
            "file_types": file_types,
            "recent_modifications": recent_modifications,
            "coverage_analysis": {
                "has_documentation": any("doc" in f["file_type"] for f in theme_files),
                "has_tests": any("test" in f["file_type"] for f in theme_files),
                "has_config": any("config" in f["file_type"] for f in theme_files)
            },
            "analysis_timestamp": datetime.now().isoformat()
        }
    