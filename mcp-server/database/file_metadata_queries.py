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
        Discover and categorize project files by scanning the filesystem.
        
        Args:
            project_path: Path to project root
            file_patterns: File patterns to include (e.g., ['*.py', '*.js'])
            exclude_patterns: File patterns to exclude (e.g., ['node_modules/*', '*.pyc'])
            
        Returns:
            Dictionary with categorized file lists
        """
        import os
        import fnmatch
        from pathlib import Path
        
        try:
            project_root = Path(project_path)
            if not project_root.exists():
                return self._empty_file_categorization()
            
            # Default file patterns if not provided
            if file_patterns is None:
                file_patterns = ['*']
            
            # Default exclude patterns
            default_excludes = [
                '__pycache__/*', '*.pyc', '*.pyo', '.git/*', '.idea/*', '.vscode/*',
                'node_modules/*', '*.log', '.DS_Store', '*.swp', '*.swo',
                'projectManagement/UserSettings/*', 'projectManagement/database/backups/*'
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
        import fnmatch
        
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_path.lower(), pattern.lower()):
                return True
        return False
    
    def _matches_include_patterns(self, filename: str, file_patterns: List[str]) -> bool:
        """Check if file matches include patterns"""
        import fnmatch
        
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
    
    def analyze_file_dependencies(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze file dependencies and relationships by parsing file content.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Dictionary with dependency information
        """
        try:
            from pathlib import Path
            import re
            
            file_obj = Path(file_path)
            if not file_obj.exists():
                return self._empty_dependency_analysis()
            
            # Read file content
            try:
                with open(file_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, IOError):
                # Skip binary files or files we can't read
                return self._empty_dependency_analysis()
            
            # Analyze based on file extension
            file_extension = file_obj.suffix.lower()
            
            if file_extension == '.py':
                return self._analyze_python_dependencies(content, file_path)
            elif file_extension in ['.js', '.ts', '.jsx', '.tsx']:
                return self._analyze_javascript_dependencies(content, file_path)
            elif file_extension in ['.java']:
                return self._analyze_java_dependencies(content, file_path)
            elif file_extension in ['.go']:
                return self._analyze_go_dependencies(content, file_path)
            elif file_extension in ['.rs']:
                return self._analyze_rust_dependencies(content, file_path)
            else:
                return self._analyze_generic_dependencies(content, file_path)
                
        except Exception as e:
            self.db.logger.error(f"Error analyzing file dependencies for {file_path}: {e}")
            return self._empty_dependency_analysis()
    
    def _empty_dependency_analysis(self) -> Dict[str, Any]:
        """Return empty dependency analysis"""
        return {
            "imports": [],
            "exports": [],
            "dependencies": [],
            "dependents": [],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _analyze_python_dependencies(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Python file dependencies"""
        import re
        
        imports = []
        exports = []
        
        # Find import statements
        import_patterns = [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import',
            r'from\s+\.([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import',  # relative imports
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.extend(matches)
        
        # Find class and function definitions (exports)
        export_patterns = [
            r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^([A-Z_][A-Z0-9_]*)\s*=',  # Constants
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            exports.extend(matches)
        
        return {
            "imports": list(set(imports)),
            "exports": list(set(exports)),
            "dependencies": list(set(imports)),
            "dependents": [],  # Would need project-wide analysis
            "language": "python",
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _analyze_javascript_dependencies(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file dependencies"""
        import re
        
        imports = []
        exports = []
        
        # Find import statements
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.extend(matches)
        
        # Find export statements
        export_patterns = [
            r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'export\s*\{\s*([^}]+)\s*\}',
            r'module\.exports\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            exports.extend(matches)
        
        return {
            "imports": list(set(imports)),
            "exports": list(set(exports)),
            "dependencies": list(set(imports)),
            "dependents": [],
            "language": "javascript",
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _analyze_java_dependencies(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Java file dependencies"""
        import re
        
        imports = []
        exports = []
        
        # Find import statements
        import_matches = re.findall(r'import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)', content, re.MULTILINE)
        imports.extend(import_matches)
        
        # Find class definitions
        class_matches = re.findall(r'(?:public\s+)?class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE)
        exports.extend(class_matches)
        
        return {
            "imports": list(set(imports)),
            "exports": list(set(exports)),
            "dependencies": list(set(imports)),
            "dependents": [],
            "language": "java",
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _analyze_go_dependencies(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Go file dependencies"""
        import re
        
        imports = []
        exports = []
        
        # Find import statements
        import_patterns = [
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'import\s*\(\s*[\'"]([^\'"]+)[\'"]',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.extend(matches)
        
        # Find exported functions and types
        export_patterns = [
            r'func\s+([A-Z][a-zA-Z0-9_]*)',  # Exported functions start with capital
            r'type\s+([A-Z][a-zA-Z0-9_]*)',  # Exported types start with capital
            r'var\s+([A-Z][a-zA-Z0-9_]*)',   # Exported vars start with capital
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            exports.extend(matches)
        
        return {
            "imports": list(set(imports)),
            "exports": list(set(exports)),
            "dependencies": list(set(imports)),
            "dependents": [],
            "language": "go",
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _analyze_rust_dependencies(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Rust file dependencies"""
        import re
        
        imports = []
        exports = []
        
        # Find use statements
        use_matches = re.findall(r'use\s+([a-zA-Z_][a-zA-Z0-9_:]*)', content, re.MULTILINE)
        imports.extend(use_matches)
        
        # Find public items
        export_patterns = [
            r'pub\s+fn\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'pub\s+struct\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'pub\s+enum\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'pub\s+trait\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            exports.extend(matches)
        
        return {
            "imports": list(set(imports)),
            "exports": list(set(exports)),
            "dependencies": list(set(imports)),
            "dependents": [],
            "language": "rust",
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _analyze_generic_dependencies(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze generic file dependencies using basic heuristics"""
        import re
        
        # Look for common include/import patterns
        imports = []
        
        include_patterns = [
            r'#include\s+[<"]([^>"]+)[>"]',  # C/C++
            r'@import\s+[\'"]([^\'"]+)[\'"]',  # Objective-C
            r'#import\s+[<"]([^>"]+)[>"]',     # Objective-C
            r'require\s+[\'"]([^\'"]+)[\'"]',  # Various languages
        ]
        
        for pattern in include_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.extend(matches)
        
        return {
            "imports": list(set(imports)),
            "exports": [],
            "dependencies": list(set(imports)),
            "dependents": [],
            "language": "generic",
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
        """Get themes that reference this file path by querying theme-flow relationships."""
        try:
            # Query theme-flow relationships to find themes associated with this file
            query = """
                SELECT DISTINCT tf.theme_name
                FROM theme_flows tf
                WHERE tf.flow_file LIKE ? 
                   OR JSON_EXTRACT(tf.metadata, '$.files') LIKE ?
                   OR JSON_EXTRACT(tf.metadata, '$.related_files') LIKE ?
                ORDER BY tf.theme_name
            """
            
            # Create search patterns for the file path
            file_pattern = f"%{file_path}%"
            
            results = self.db.execute_query(query, (file_pattern, file_pattern, file_pattern))
            
            themes = []
            for row in results:
                themes.append(row["theme_name"])
            
            # Additionally, check file modifications for theme associations
            mod_query = """
                SELECT DISTINCT JSON_EXTRACT(details, '$.themes') as theme_data
                FROM file_modifications
                WHERE file_path = ? 
                  AND JSON_EXTRACT(details, '$.themes') IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 10
            """
            
            mod_results = self.db.execute_query(mod_query, (file_path,))
            for row in mod_results:
                theme_data = row.get("theme_data")
                if theme_data:
                    try:
                        import json
                        theme_list = json.loads(theme_data) if isinstance(theme_data, str) else theme_data
                        if isinstance(theme_list, list):
                            themes.extend(theme_list)
                    except (json.JSONDecodeError, TypeError):
                        continue
            
            # Remove duplicates and return
            return list(set(themes))
            
        except Exception as e:
            self.db.logger.error(f"Error getting themes for file {file_path}: {e}")
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
        try:
            from pathlib import Path
            import networkx as nx
            from collections import defaultdict, deque
            
            project_root = Path(project_path)
            if not project_root.exists():
                return self._empty_relationship_mapping()
            
            # Discover all project files
            project_files = self.discover_project_files(project_path)
            all_files = []
            for category, files in project_files.items():
                all_files.extend(files)
            
            # Build dependency graph
            dependency_graph = {}
            file_dependencies = {}
            reverse_dependencies = defaultdict(list)
            
            # Analyze each file's dependencies
            for file_path in all_files:
                try:
                    full_path = project_root / file_path
                    if full_path.exists():
                        analysis = self.analyze_file_dependencies(str(full_path))
                        file_dependencies[file_path] = analysis
                        
                        # Build dependency graph
                        dependencies = analysis.get("dependencies", [])
                        dependency_graph[file_path] = dependencies
                        
                        # Build reverse dependency mapping
                        for dep in dependencies:
                            reverse_dependencies[dep].append(file_path)
                            
                except Exception as e:
                    self.db.logger.warning(f"Could not analyze dependencies for {file_path}: {e}")
                    dependency_graph[file_path] = []
            
            # Detect circular dependencies
            circular_dependencies = self._detect_circular_dependencies(dependency_graph)
            
            # Find orphaned files (no dependencies and no dependents)
            orphaned_files = []
            for file_path in all_files:
                has_dependencies = len(dependency_graph.get(file_path, [])) > 0
                has_dependents = len(reverse_dependencies.get(file_path, [])) > 0
                
                if not has_dependencies and not has_dependents:
                    orphaned_files.append(file_path)
            
            # Identify critical files (many dependents)
            critical_files = []
            for file_path, dependents in reverse_dependencies.items():
                if len(dependents) >= 5:  # Files with 5+ dependents are critical
                    critical_files.append({
                        "file_path": file_path,
                        "dependent_count": len(dependents),
                        "dependents": dependents[:10],  # Limit to top 10
                        "criticality_score": self._calculate_criticality_score(file_path, dependents, dependency_graph)
                    })
            
            # Sort critical files by dependent count
            critical_files.sort(key=lambda x: x["dependent_count"], reverse=True)
            
            # Create file clusters based on dependency relationships
            file_clusters = self._create_file_clusters(dependency_graph, reverse_dependencies)
            
            # Calculate relationship statistics
            stats = self._calculate_relationship_statistics(
                dependency_graph, reverse_dependencies, all_files
            )
            
            return {
                "dependency_graph": dependency_graph,
                "reverse_dependencies": dict(reverse_dependencies),
                "circular_dependencies": circular_dependencies,
                "orphaned_files": orphaned_files,
                "critical_files": critical_files,
                "file_clusters": file_clusters,
                "statistics": stats,
                "total_files_analyzed": len(all_files),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.db.logger.error(f"Error mapping file relationships: {e}")
            return self._empty_relationship_mapping()
    
    def _empty_relationship_mapping(self) -> Dict[str, Any]:
        """Return empty relationship mapping structure"""
        return {
            "dependency_graph": {},
            "reverse_dependencies": {},
            "circular_dependencies": [],
            "orphaned_files": [],
            "critical_files": [],
            "file_clusters": [],
            "statistics": {
                "total_files": 0,
                "total_dependencies": 0,
                "average_dependencies_per_file": 0.0,
                "max_dependencies": 0,
                "max_dependents": 0
            },
            "total_files_analyzed": 0,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _detect_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies using depth-first search"""
        circular_deps = []
        visited = set()
        rec_stack = set()
        
        def dfs_visit(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle - extract the circular portion
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if len(cycle) > 2:  # Ignore self-references
                    circular_deps.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            # Visit all dependencies
            for dep in dependency_graph.get(node, []):
                if dep in dependency_graph:  # Only visit files we have data for
                    dfs_visit(dep, path + [node])
            
            rec_stack.remove(node)
        
        # Check each file for circular dependencies
        for file_path in dependency_graph:
            if file_path not in visited:
                dfs_visit(file_path, [])
        
        # Remove duplicate cycles (same cycle in different order)
        unique_cycles = []
        for cycle in circular_deps:
            # Normalize cycle by starting with the lexicographically smallest element
            if cycle:
                min_idx = cycle.index(min(cycle))
                normalized = cycle[min_idx:] + cycle[:min_idx]
                if normalized not in unique_cycles:
                    unique_cycles.append(normalized)
        
        return unique_cycles
    
    def _calculate_criticality_score(self, file_path: str, dependents: List[str], 
                                   dependency_graph: Dict[str, List[str]]) -> float:
        """Calculate a criticality score for a file based on its role in the dependency graph"""
        score = 0.0
        
        # Base score from number of direct dependents
        score += len(dependents) * 2
        
        # Bonus for being in critical paths (files that many others depend on transitively)
        transitive_dependents = set()
        for dependent in dependents:
            transitive_dependents.update(self._get_transitive_dependents(dependent, dependency_graph))
        score += len(transitive_dependents) * 0.5
        
        # Bonus for file type criticality
        if any(pattern in file_path.lower() for pattern in ['config', 'settings', 'main', 'index', 'init']):
            score += 5
        
        # Bonus for being in root or core directories
        if '/' not in file_path or any(pattern in file_path for pattern in ['/core/', '/lib/', '/utils/']):
            score += 3
        
        return round(score, 2)
    
    def _get_transitive_dependents(self, file_path: str, dependency_graph: Dict[str, List[str]]) -> Set[str]:
        """Get all files that transitively depend on the given file"""
        transitive = set()
        queue = deque([file_path])
        visited = set()
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            
            # Find all files that depend on current
            for file, deps in dependency_graph.items():
                if current in deps and file not in visited:
                    transitive.add(file)
                    queue.append(file)
        
        return transitive
    
    def _create_file_clusters(self, dependency_graph: Dict[str, List[str]], 
                            reverse_dependencies: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Create clusters of related files based on dependency relationships"""
        try:
            import networkx as nx
        except ImportError:
            # Fallback clustering without networkx
            return self._create_simple_file_clusters(dependency_graph, reverse_dependencies)
        
        # Create undirected graph for clustering
        G = nx.Graph()
        
        # Add edges for dependency relationships
        for file_path, deps in dependency_graph.items():
            for dep in deps:
                if dep in dependency_graph:  # Only include files we have data for
                    G.add_edge(file_path, dep)
        
        # Find connected components (clusters)
        clusters = []
        for i, component in enumerate(nx.connected_components(G)):
            if len(component) > 1:  # Ignore single-file "clusters"
                cluster_files = list(component)
                
                # Calculate cluster statistics
                internal_edges = 0
                external_dependencies = set()
                
                for file_path in cluster_files:
                    deps = dependency_graph.get(file_path, [])
                    for dep in deps:
                        if dep in cluster_files:
                            internal_edges += 1
                        else:
                            external_dependencies.add(dep)
                
                clusters.append({
                    "cluster_id": f"cluster_{i+1}",
                    "files": cluster_files,
                    "size": len(cluster_files),
                    "internal_dependencies": internal_edges,
                    "external_dependencies": len(external_dependencies),
                    "cohesion_score": internal_edges / len(cluster_files) if cluster_files else 0,
                    "common_patterns": self._find_common_patterns(cluster_files)
                })
        
        # Sort clusters by size (largest first)
        clusters.sort(key=lambda x: x["size"], reverse=True)
        
        return clusters
    
    def _create_simple_file_clusters(self, dependency_graph: Dict[str, List[str]], 
                                   reverse_dependencies: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Simple clustering fallback when networkx is not available"""
        clusters = []
        visited = set()
        
        for file_path in dependency_graph:
            if file_path in visited:
                continue
            
            # Find all files connected to this one
            cluster_files = set()
            queue = deque([file_path])
            
            while queue:
                current = queue.popleft()
                if current in visited:
                    continue
                
                visited.add(current)
                cluster_files.add(current)
                
                # Add dependencies and dependents
                deps = dependency_graph.get(current, [])
                dependents = reverse_dependencies.get(current, [])
                
                for related_file in deps + dependents:
                    if related_file not in visited and related_file in dependency_graph:
                        queue.append(related_file)
            
            if len(cluster_files) > 1:
                clusters.append({
                    "cluster_id": f"cluster_{len(clusters)+1}",
                    "files": list(cluster_files),
                    "size": len(cluster_files),
                    "common_patterns": self._find_common_patterns(list(cluster_files))
                })
        
        return clusters
    
    def _find_common_patterns(self, files: List[str]) -> List[str]:
        """Find common patterns in a cluster of files"""
        patterns = []
        
        # Common directory patterns
        directories = set()
        for file_path in files:
            if '/' in file_path:
                directories.add(file_path.split('/')[0])
        
        if len(directories) == 1:
            patterns.append(f"All files in '{list(directories)[0]}' directory")
        
        # Common file extensions
        extensions = set()
        for file_path in files:
            if '.' in file_path:
                extensions.add(file_path.split('.')[-1])
        
        if len(extensions) == 1:
            patterns.append(f"All files are .{list(extensions)[0]} files")
        
        # Common naming patterns
        if len(files) >= 3:
            # Look for common prefixes
            common_prefix = ""
            if files:
                first_file = files[0].split('/')[-1]  # Get filename only
                for char_idx in range(len(first_file)):
                    char = first_file[char_idx]
                    if all(f.split('/')[-1].startswith(first_file[:char_idx+1]) for f in files):
                        common_prefix = first_file[:char_idx+1]
                    else:
                        break
            
            if len(common_prefix) > 2:
                patterns.append(f"Common prefix: '{common_prefix}'")
        
        return patterns
    
    def _calculate_relationship_statistics(self, dependency_graph: Dict[str, List[str]], 
                                         reverse_dependencies: Dict[str, List[str]], 
                                         all_files: List[str]) -> Dict[str, Any]:
        """Calculate comprehensive statistics about file relationships"""
        total_dependencies = sum(len(deps) for deps in dependency_graph.values())
        total_files = len(all_files)
        
        # Calculate dependency distribution
        dependency_counts = [len(deps) for deps in dependency_graph.values()]
        dependent_counts = [len(deps) for deps in reverse_dependencies.values()]
        
        return {
            "total_files": total_files,
            "total_dependencies": total_dependencies,
            "average_dependencies_per_file": round(total_dependencies / total_files, 2) if total_files > 0 else 0.0,
            "max_dependencies": max(dependency_counts) if dependency_counts else 0,
            "max_dependents": max(dependent_counts) if dependent_counts else 0,
            "files_with_no_dependencies": len([c for c in dependency_counts if c == 0]),
            "files_with_no_dependents": len([c for c in dependent_counts if c == 0]),
            "highly_connected_files": len([c for c in dependency_counts if c >= 10]),
            "dependency_distribution": {
                "0_deps": len([c for c in dependency_counts if c == 0]),
                "1_5_deps": len([c for c in dependency_counts if 1 <= c <= 5]),
                "6_10_deps": len([c for c in dependency_counts if 6 <= c <= 10]),
                "11_plus_deps": len([c for c in dependency_counts if c >= 11])
            }
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