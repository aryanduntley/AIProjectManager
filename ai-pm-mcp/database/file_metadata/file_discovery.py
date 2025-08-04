"""
File Discovery Module

Handles project file discovery, categorization, and filtering.
"""

import os
import fnmatch
from pathlib import Path
from typing import Dict, List
from ..db_manager import DatabaseManager
from ...utils.project_paths import get_management_folder_name


class FileDiscovery:
    """File discovery and categorization operations."""
    
    def __init__(self, db_manager: DatabaseManager, config_manager=None):
        """Initialize with database manager."""
        self.db = db_manager
        self.config_manager = config_manager
    
    def discover_project_files(
        self,
        project_path: str,
        file_patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> Dict[str, List[str]]:
        """
        Discover and categorize project files by scanning the filesystem.
        
        Args:
            project_path: Path to project root
            file_patterns: File patterns to include (e.g., ['*.py', '*.js'])
            exclude_patterns: File patterns to exclude (e.g., ['node_modules/*', '*.pyc'])
            
        Returns:
            Dictionary with categorized file lists
        """
        try:
            project_root = Path(project_path)
            if not project_root.exists():
                return self._empty_file_categorization()
            
            # Default file patterns if not provided
            if file_patterns is None:
                file_patterns = ['*']
            
            # Default exclude patterns
            management_folder = get_management_folder_name(self.config_manager)
            default_excludes = [
                '__pycache__/*', '*.pyc', '*.pyo', '.git/*', '.idea/*', '.vscode/*',
                'node_modules/*', '*.log', '.DS_Store', '*.swp', '*.swo',
                f'{management_folder}/UserSettings/*', f'{management_folder}/database/backups/*'
            ]
            
            if exclude_patterns is None:
                exclude_patterns = default_excludes
            else:
                exclude_patterns.extend(default_excludes)
            
            categorized_files = {
                "source_files": [],
                "config_files": [],
                "documentation": [],
                "tests": [],
                "build_files": [],
                "data_files": []
            }
            
            # Walk through the project directory
            for root, dirs, files in os.walk(project_root):
                # Convert to relative path
                rel_root = os.path.relpath(root, project_root)
                if rel_root == '.':
                    rel_root = ''
                
                for file in files:
                    if rel_root:
                        file_path = f"{rel_root}/{file}"
                    else:
                        file_path = file
                    
                    # Check if file should be excluded
                    if self._should_exclude_file(file_path, exclude_patterns):
                        continue
                    
                    # Check if file matches include patterns
                    if not self._matches_include_patterns(file, file_patterns):
                        continue
                    
                    # Categorize the file
                    category = self._categorize_file(file_path, file)
                    if category in categorized_files:
                        categorized_files[category].append(file_path)
            
            # Sort file lists for consistency
            for category in categorized_files:
                categorized_files[category].sort()
            
            return categorized_files
            
        except Exception as e:
            self.db.logger.error(f"Error discovering and categorizing files: {e}")
            return self._empty_file_categorization()
    
    def _empty_file_categorization(self) -> Dict[str, List[str]]:
        """Return empty file categorization structure"""
        return {
            "source_files": [],
            "config_files": [],
            "documentation": [],
            "tests": [],
            "build_files": [],
            "data_files": []
        }
    
    def _should_exclude_file(self, file_path: str, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded based on patterns"""
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_path.lower(), pattern.lower()):
                return True
        return False
    
    def _matches_include_patterns(self, filename: str, file_patterns: List[str]) -> bool:
        """Check if file matches include patterns"""
        if '*' in file_patterns:
            return True
        
        for pattern in file_patterns:
            if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(filename.lower(), pattern.lower()):
                return True
        return False
    
    def _categorize_file(self, file_path: str, filename: str) -> str:
        """Categorize a file based on its path and name"""
        file_lower = filename.lower()
        path_lower = file_path.lower()
        
        # Test files
        if (any(pattern in file_lower for pattern in ['test_', '_test.', '.test.', '.spec.', '_spec.']) or
            any(pattern in path_lower for pattern in ['/test/', '/tests/', '__tests__', '.test/', '.spec/'])):
            return "tests"
        
        # Documentation files
        if (any(file_lower.endswith(ext) for ext in ['.md', '.rst', '.txt', '.doc', '.docx', '.pdf']) or
            file_lower in ['readme', 'changelog', 'license', 'authors', 'contributors', 'history'] or
            any(pattern in path_lower for pattern in ['/doc/', '/docs/', '/documentation/'])):
            return "documentation"
        
        # Configuration files
        if (any(file_lower.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf']) or
            file_lower in ['dockerfile', 'makefile', 'rakefile', 'gulpfile.js', 'gruntfile.js'] or
            any(pattern in file_lower for pattern in ['config', 'settings', '.env', 'package.json', 'requirements.txt', 
                                                      'cargo.toml', 'composer.json', 'setup.py', 'pyproject.toml'])):
            return "config_files"
        
        # Build files
        if (any(file_lower.endswith(ext) for ext in ['.sh', '.bat', '.cmd', '.ps1']) or
            file_lower in ['dockerfile', 'makefile', 'rakefile', 'gulpfile.js', 'gruntfile.js', 'webpack.config.js'] or
            any(pattern in path_lower for pattern in ['/build/', '/dist/', '/target/', '/bin/', '/scripts/'])):
            return "build_files"
        
        # Data files
        if (any(file_lower.endswith(ext) for ext in ['.csv', '.tsv', '.json', '.xml', '.sql', '.db', '.sqlite']) or
            any(pattern in path_lower for pattern in ['/data/', '/fixtures/', '/seeds/'])):
            return "data_files"
        
        # Source files (default)
        return "source_files"