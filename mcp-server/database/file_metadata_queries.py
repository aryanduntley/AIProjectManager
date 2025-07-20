"""
File Metadata Database Queries
Replaces README.json with intelligent file discovery and impact analysis for AI Project Manager.

Follows the exact schema structure defined in mcp-server/database/schema.sql
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from .db_manager import DatabaseManager


class FileMetadataQueries:
    """
    File metadata and modification tracking with intelligent project understanding.
    
    Key Features:
    - Replace README.json with database-driven file metadata
    - Intelligent file discovery and impact analysis
    - Change impact tracking across sessions
    - File relationship mapping and dependency analysis
    - Theme-file association intelligence
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    # Directory Metadata Management
    
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
    
    # File Modification Tracking
    
    def log_file_modification(
        self,
        file_path: str,
        file_type: str,
        operation: str,
        session_id: str = None,
        details: Dict[str, Any] = None
    ) -> bool:
        """
        Log a file modification event for tracking and analysis.
        
        Args:
            file_path: Path to the modified file
            file_type: Type of file (theme, flow, task, blueprint, code, config, etc.)
            operation: Operation performed (create, update, delete)
            session_id: Session ID for context
            details: Additional details about the modification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO file_modifications 
                (file_path, file_type, operation, session_id, details)
                VALUES (?, ?, ?, ?, ?)
            """
            
            self.db.execute_update(query, (
                file_path, file_type, operation, session_id,
                json.dumps(details or {})
            ))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error logging file modification: {e}")
            return False
    
    def get_file_modifications(
        self,
        file_path: str = None,
        file_type: str = None,
        operation: str = None,
        session_id: str = None,
        days: int = 30,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get file modification history with flexible filtering.
        
        Args:
            file_path: Optional file path filter
            file_type: Optional file type filter
            operation: Optional operation filter
            session_id: Optional session ID filter
            days: Number of days to include
            limit: Optional result limit
            
        Returns:
            List of file modification records
        """
        base_query = """
            SELECT file_path, file_type, operation, session_id, details, timestamp
            FROM file_modifications
            WHERE timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        conditions = []
        params = []
        
        if file_path:
            conditions.append("file_path LIKE ?")
            params.append(f"%{file_path}%")
        
        if file_type:
            conditions.append("file_type = ?")
            params.append(file_type)
        
        if operation:
            conditions.append("operation = ?")
            params.append(operation)
        
        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " ORDER BY timestamp DESC"
        
        if limit:
            base_query += f" LIMIT {limit}"
        
        results = []
        for row in self.db.execute_query(base_query, tuple(params)):
            results.append({
                "file_path": row["file_path"],
                "file_type": row["file_type"],
                "operation": row["operation"],
                "session_id": row["session_id"],
                "details": json.loads(row["details"]) if row["details"] else {},
                "timestamp": row["timestamp"]
            })
        
        return results
    
    def get_file_modification_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of file modifications."""
        base_query = f"""
            FROM file_modifications 
            WHERE timestamp >= datetime('now', '-{days} days')
        """
        
        # Total modifications
        total_query = f"SELECT COUNT(*) as count {base_query}"
        total_modifications = self.db.execute_query(total_query)[0]["count"]
        
        # By operation
        operation_query = f"""
            SELECT operation, COUNT(*) as count {base_query}
            GROUP BY operation
            ORDER BY count DESC
        """
        operations = {row["operation"]: row["count"] 
                     for row in self.db.execute_query(operation_query)}
        
        # By file type
        type_query = f"""
            SELECT file_type, COUNT(*) as count {base_query}
            GROUP BY file_type
            ORDER BY count DESC
        """
        file_types = {row["file_type"]: row["count"] 
                     for row in self.db.execute_query(type_query)}
        
        # Most modified files
        files_query = f"""
            SELECT file_path, COUNT(*) as count {base_query}
            GROUP BY file_path
            ORDER BY count DESC
            LIMIT 10
        """
        most_modified = [
            {"file_path": row["file_path"], "modifications": row["count"]}
            for row in self.db.execute_query(files_query)
        ]
        
        return {
            "total_modifications": total_modifications,
            "by_operation": operations,
            "by_file_type": file_types,
            "most_modified_files": most_modified,
            "analysis_period_days": days
        }
    
    # File Discovery and Intelligence
    
    def discover_project_files(
        self,
        project_path: str,
        file_patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> Dict[str, List[str]]:
        """
        Discover and categorize project files.
        
        This method would typically scan the filesystem and categorize files,
        but for now it returns the structure that would be stored in the database.
        
        Args:
            project_path: Path to project root
            file_patterns: File patterns to include
            exclude_patterns: File patterns to exclude
            
        Returns:
            Dictionary with categorized file lists
        """
        # This would be implemented to scan the filesystem
        # For now, return structure that would be populated
        return {
            "source_files": [],
            "config_files": [],
            "documentation": [],
            "tests": [],
            "build_files": [],
            "data_files": []
        }
    
    def analyze_file_dependencies(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze file dependencies and relationships.
        
        This would parse import statements, references, and dependencies.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Dictionary with dependency information
        """
        # Placeholder for file analysis logic
        return {
            "imports": [],
            "exports": [],
            "dependencies": [],
            "dependents": [],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def get_impact_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        Get impact analysis for file changes.
        
        Args:
            file_path: File path to analyze
            
        Returns:
            Impact analysis with affected files and components
        """
        # Get recent modifications for this file
        modifications = self.get_file_modifications(file_path=file_path, days=30)
        
        # Analyze dependencies (placeholder - would be more sophisticated)
        dependencies = self.analyze_file_dependencies(file_path)
        
        # Get related theme files
        related_themes = self._get_themes_for_file(file_path)
        
        return {
            "file_path": file_path,
            "recent_modifications": len(modifications),
            "last_modified": modifications[0]["timestamp"] if modifications else None,
            "dependencies": dependencies,
            "affected_themes": related_themes,
            "impact_level": self._calculate_impact_level(file_path, modifications, dependencies),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _get_themes_for_file(self, file_path: str) -> List[str]:
        """Get themes that reference this file path."""
        # This would query theme files to find which themes include this file
        # For now, return empty list - would be implemented with theme integration
        return []
    
    def _calculate_impact_level(
        self,
        file_path: str,
        modifications: List[Dict[str, Any]],
        dependencies: Dict[str, Any]
    ) -> str:
        """Calculate impact level (low, medium, high) based on file characteristics."""
        score = 0
        
        # Factor in modification frequency
        if len(modifications) > 10:
            score += 3
        elif len(modifications) > 5:
            score += 2
        elif len(modifications) > 0:
            score += 1
        
        # Factor in dependencies
        if len(dependencies.get("dependents", [])) > 10:
            score += 3
        elif len(dependencies.get("dependents", [])) > 5:
            score += 2
        elif len(dependencies.get("dependents", [])) > 0:
            score += 1
        
        # Factor in file type
        if any(pattern in file_path for pattern in [".config", "package.json", "requirements.txt"]):
            score += 2
        elif any(pattern in file_path for pattern in [".test", ".spec", "test_"]):
            score -= 1
        
        if score >= 6:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"
    
    # File Relationship Mapping
    
    def map_file_relationships(self, project_path: str) -> Dict[str, Any]:
        """
        Build a comprehensive map of file relationships in the project.
        
        Args:
            project_path: Project root path
            
        Returns:
            Dictionary with file relationship mapping
        """
        # This would be a comprehensive analysis of all project files
        return {
            "dependency_graph": {},
            "circular_dependencies": [],
            "orphaned_files": [],
            "critical_files": [],
            "file_clusters": [],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def get_critical_files(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Identify critical files based on dependencies and modification patterns.
        
        Args:
            project_path: Project root path
            
        Returns:
            List of critical files with analysis
        """
        # Get files with high modification frequency
        frequent_modifications = self.db.execute_query("""
            SELECT file_path, COUNT(*) as mod_count
            FROM file_modifications
            WHERE timestamp >= datetime('now', '-30 days')
            GROUP BY file_path
            ORDER BY mod_count DESC
            LIMIT 20
        """)
        
        critical_files = []
        for row in frequent_modifications:
            file_path = row["file_path"]
            impact_analysis = self.get_impact_analysis(file_path)
            
            if impact_analysis["impact_level"] in ["high", "medium"]:
                critical_files.append({
                    "file_path": file_path,
                    "modification_count": row["mod_count"],
                    "impact_level": impact_analysis["impact_level"],
                    "affected_themes": impact_analysis["affected_themes"],
                    "analysis": impact_analysis
                })
        
        return critical_files
    
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
            # Log the theme association change
            details = {
                "themes": themes,
                "association_type": association_type,
                "previous_associations": []  # Would track previous state
            }
            
            return self.log_file_modification(
                file_path=file_path,
                file_type="theme_association",
                operation="update",
                details=details
            )
            
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
    
    # Performance and Analytics
    
    def get_file_hotspots(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get file modification hotspots for performance analysis.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of file hotspots with activity metrics
        """
        query = """
            SELECT 
                file_path,
                file_type,
                COUNT(*) as modification_count,
                COUNT(DISTINCT session_id) as session_count,
                MIN(timestamp) as first_modification,
                MAX(timestamp) as last_modification,
                COUNT(DISTINCT operation) as operation_types
            FROM file_modifications
            WHERE timestamp >= datetime('now', '-{} days')
            GROUP BY file_path, file_type
            HAVING modification_count > 1
            ORDER BY modification_count DESC, session_count DESC
            LIMIT 50
        """.format(days)
        
        results = []
        for row in self.db.execute_query(query):
            # Calculate modification frequency
            first_mod = datetime.fromisoformat(row["first_modification"])
            last_mod = datetime.fromisoformat(row["last_modification"])
            duration_days = (last_mod - first_mod).days + 1
            
            frequency = row["modification_count"] / duration_days if duration_days > 0 else 0
            
            results.append({
                "file_path": row["file_path"],
                "file_type": row["file_type"],
                "modification_count": row["modification_count"],
                "session_count": row["session_count"],
                "operation_types": row["operation_types"],
                "first_modification": row["first_modification"],
                "last_modification": row["last_modification"],
                "frequency_per_day": round(frequency, 2),
                "activity_score": row["modification_count"] * row["session_count"]
            })
        
        return results
    
    def cleanup_old_modifications(self, days: int = 90) -> int:
        """
        Clean up old file modification records.
        
        Args:
            days: Keep records newer than this many days
            
        Returns:
            Number of records deleted
        """
        try:
            query = """
                DELETE FROM file_modifications 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days)
            
            deleted_count = self.db.execute_update(query)
            self.db.logger.info(f"Cleaned up {deleted_count} old file modification records")
            return deleted_count
            
        except Exception as e:
            self.db.logger.error(f"Error cleaning up file modifications: {e}")
            return 0