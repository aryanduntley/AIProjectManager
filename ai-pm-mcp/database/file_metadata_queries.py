"""
File Metadata Database Queries - Modular Coordinator

This is the main coordinator class that delegates to specialized modules for:
- Directory operations
- File discovery and categorization  
- Dependency analysis
- Impact analysis
- Theme operations
- File modification logging
- Initialization tracking

Replaces README.json with intelligent file discovery and impact analysis.
"""

from typing import Dict, List, Any, Optional
from .db_manager import DatabaseManager

# Import the specialized modules
from .file_metadata.directory_ops import DirectoryOperations
from .file_metadata.file_discovery import FileDiscovery  
from .file_metadata.dependency_analysis import DependencyAnalysis
from .file_metadata.impact_analysis import ImpactAnalysis
from .file_metadata.theme_operations import ThemeOperations
from .file_metadata.modification_logging import ModificationLogging
from .file_metadata.initialization_tracking import InitializationTracking


class FileMetadataQueries:
    """
    Main coordinator for file metadata operations.
    
    Delegates to specialized modules while maintaining the same API.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager and create module instances."""
        self.db = db_manager
        
        # Initialize basic modules first
        self.directory_ops = DirectoryOperations(db_manager)
        self.file_discovery = FileDiscovery(db_manager)
        self.dependency_analysis = DependencyAnalysis(db_manager)
        self.modification_logging = ModificationLogging(db_manager)
        
        # Initialize modules that depend on other modules
        self.initialization_tracking = InitializationTracking(db_manager, self.dependency_analysis)
        self.impact_analysis = ImpactAnalysis(db_manager, self.modification_logging, self.dependency_analysis, self.file_discovery)
        self.theme_operations = ThemeOperations(db_manager, self.modification_logging)
    
    # ========================================================================
    # DIRECTORY OPERATIONS - Delegate to DirectoryOperations
    # ========================================================================
    
    def update_directory_metadata(self, directory_metadata: Dict[str, Any]) -> bool:
        """Update directory metadata for intelligent file discovery."""
        return self.directory_ops.update_directory_metadata(directory_metadata)
    
    def get_directory_metadata(self, directory_path: str) -> Optional[Dict[str, Any]]:
        """Get directory metadata for a specific path."""
        return self.directory_ops.get_directory_metadata(directory_path)
    
    # ========================================================================
    # FILE DISCOVERY - Delegate to FileDiscovery
    # ========================================================================
    
    def discover_project_files(
        self,
        project_path: str,
        file_patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> Dict[str, List[str]]:
        """Discover and categorize project files by scanning the filesystem."""
        return self.file_discovery.discover_project_files(project_path, file_patterns, exclude_patterns)
    
    # ========================================================================
    # DEPENDENCY ANALYSIS - Delegate to DependencyAnalysis  
    # ========================================================================
    
    def analyze_file_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Analyze file dependencies and relationships by parsing file content."""
        return self.dependency_analysis.analyze_file_dependencies(file_path)
    
    # ========================================================================
    # IMPACT ANALYSIS - Delegate to ImpactAnalysis
    # ========================================================================
    
    def get_impact_analysis(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive impact analysis for a file."""
        return self.impact_analysis.get_impact_analysis(file_path)
    
    def map_file_relationships(self, project_path: str) -> Dict[str, Any]:
        """Map file relationships across the entire project."""
        return self.impact_analysis.map_file_relationships(project_path)
    
    def get_critical_files(self, project_path: str) -> List[Dict[str, Any]]:
        """Get list of critical files based on dependency analysis."""
        return self.impact_analysis.get_critical_files(project_path)
    
    # ========================================================================
    # THEME OPERATIONS - Delegate to ThemeOperations
    # ========================================================================
    
    def update_file_theme_associations(self, file_path: str, themes: List[str]) -> bool:
        """Update theme associations for a file."""
        return self.theme_operations.update_file_theme_associations(file_path, themes)
    
    def get_files_by_theme(self, theme_name: str) -> List[Dict[str, Any]]:
        """Get all files associated with a specific theme."""
        return self.theme_operations.get_files_by_theme(theme_name)
    
    def get_theme_file_coverage(self, theme_name: str) -> Dict[str, Any]:
        """Get file coverage statistics for a theme."""
        return self.theme_operations.get_theme_file_coverage(theme_name)
    
    # ========================================================================
    # MODIFICATION LOGGING - Delegate to ModificationLogging
    # ========================================================================
    
    def log_file_modification(
        self,
        file_path: str,
        file_type: str,
        operation: str,
        session_id: str = None,
        details: Dict[str, Any] = None
    ) -> bool:
        """Log a file modification event for tracking and analysis."""
        return self.modification_logging.log_file_modification(
            file_path, file_type, operation, session_id, details
        )
    
    def get_file_modifications(
        self,
        file_path: str = None,
        file_type: str = None,
        operation: str = None,
        session_id: str = None,
        days: int = 30,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """Get file modification history with flexible filtering."""
        return self.modification_logging.get_file_modifications(
            file_path, file_type, operation, session_id, days, limit
        )
    
    def get_file_modification_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of file modifications."""
        return self.modification_logging.get_file_modification_summary(days)
    
    def get_file_hotspots(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get file modification hotspots for performance analysis.""" 
        return self.modification_logging.get_file_hotspots(days)
    
    def cleanup_old_modifications(self, keep_count: int = 500) -> int:
        """Clean up old file modification records, keeping only the most recent ones."""
        return self.modification_logging.cleanup_old_modifications(keep_count)
    
    # ========================================================================
    # INITIALIZATION TRACKING - Delegate to InitializationTracking
    # ========================================================================
    
    def create_or_update_file_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """Create or update file metadata in the database."""
        return self.initialization_tracking.create_or_update_file_metadata(file_path, metadata)
    
    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from the database."""
        return self.initialization_tracking.get_file_metadata(file_path)
    
    def mark_file_analyzed(self, file_path: str) -> bool:
        """Mark a file as analyzed during initialization."""
        return self.initialization_tracking.mark_file_analyzed(file_path)
    
    def get_initialization_progress(self, session_id: str = None) -> Dict[str, Any]:
        """Get current initialization progress with analytics."""
        return self.initialization_tracking.get_initialization_progress(session_id)
    
    def get_unanalyzed_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of files that haven't been analyzed yet."""
        return self.initialization_tracking.get_unanalyzed_files(limit)
    
    def analyze_and_store_file_metadata(self, file_path: str) -> bool:
        """Analyze a single file and store its metadata."""
        return self.initialization_tracking.analyze_and_store_file_metadata(file_path)
    
    def batch_analyze_files(self, file_paths: List[str], batch_size: int = 10) -> Dict[str, Any]:
        """Analyze multiple files in batches for performance."""
        return self.initialization_tracking.batch_analyze_files(file_paths, batch_size)