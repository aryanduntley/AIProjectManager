import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..db_manager import DatabaseManager

class InitializationTracking:
    def __init__(self, db_manager: DatabaseManager, dependency_analysis=None):
        self.db = db_manager
        self.dependency_analysis = dependency_analysis
        
	# File Metadata Initialization Tracking (Phase 2 Implementation)
    
    def create_or_update_file_metadata(
        self,
        file_path: str,
        file_purpose: str = None,
        file_description: str = None,
        important_exports: List[str] = None,
        dependencies: List[str] = None,
        dependents: List[str] = None,
        language: str = None,
        file_size: int = None,
        theme_associations: List[str] = None,
        flow_references: List[str] = None,
        analysis_metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Create or update file metadata in the database.
        
        Args:
            file_path: Path to the file
            file_purpose: Purpose of the file
            file_description: Description of the file
            important_exports: List of important exports from the file
            dependencies: List of file dependencies
            dependents: List of files that depend on this file
            language: Programming language of the file
            file_size: Size of the file in bytes
            theme_associations: List of theme names associated with the file
            flow_references: List of flow IDs that reference this file
            analysis_metadata: Additional metadata from analysis
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT OR REPLACE INTO file_metadata
                (file_path, file_purpose, file_description, important_exports, 
                 dependencies, dependents, language, file_size, theme_associations, 
                 flow_references, analysis_metadata, last_analyzed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute_update(query, (
                file_path,
                file_purpose,
                file_description,
                json.dumps(important_exports or []),
                json.dumps(dependencies or []),
                json.dumps(dependents or []),
                language,
                file_size,
                json.dumps(theme_associations or []),
                json.dumps(flow_references or []),
                json.dumps(analysis_metadata or {}),
                datetime.now().isoformat()
            ))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error creating/updating file metadata for {file_path}: {e}")
            return False
    
    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from the database.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File metadata dictionary or None if not found
        """
        try:
            query = """
                SELECT file_path, file_purpose, file_description, important_exports,
                       dependencies, dependents, language, file_size, last_analyzed,
                       theme_associations, flow_references, initialization_analyzed,
                       analysis_metadata, created_at, updated_at
                FROM file_metadata
                WHERE file_path = ?
            """
            
            results = self.db.execute_query(query, (file_path,))
            if results:
                row = results[0]
                return {
                    'file_path': row['file_path'],
                    'file_purpose': row['file_purpose'],
                    'file_description': row['file_description'],
                    'important_exports': json.loads(row['important_exports'] or '[]'),
                    'dependencies': json.loads(row['dependencies'] or '[]'),
                    'dependents': json.loads(row['dependents'] or '[]'),
                    'language': row['language'],
                    'file_size': row['file_size'],
                    'last_analyzed': row['last_analyzed'],
                    'theme_associations': json.loads(row['theme_associations'] or '[]'),
                    'flow_references': json.loads(row['flow_references'] or '[]'),
                    'initialization_analyzed': bool(row['initialization_analyzed']),
                    'analysis_metadata': json.loads(row['analysis_metadata'] or '{}'),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
            
        except Exception as e:
            self.db.logger.error(f"Error getting file metadata for {file_path}: {e}")
            return None
    
    def mark_file_analyzed(self, file_path: str) -> bool:
        """
        Mark a file as analyzed during initialization.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE file_metadata 
                SET initialization_analyzed = TRUE,
                    last_analyzed = ?
                WHERE file_path = ?
            """
            
            self.db.execute_update(query, (datetime.now().isoformat(), file_path))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error marking file as analyzed {file_path}: {e}")
            return False
    
    def get_initialization_progress(self, session_id: str = None) -> Dict[str, Any]:
        """
        Get initialization progress for file analysis.
        
        Args:
            session_id: Optional session ID to filter by
            
        Returns:
            Dictionary with initialization progress information
        """
        try:
            # Get session information if session_id provided
            session_info = {}
            if session_id:
                session_query = """
                    SELECT initialization_phase, files_processed, total_files_discovered,
                           initialization_started_at, initialization_completed_at
                    FROM sessions
                    WHERE session_id = ?
                """
                
                session_results = self.db.execute_query(session_query, (session_id,))
                if session_results:
                    session_row = session_results[0]
                    session_info = {
                        'initialization_phase': session_row['initialization_phase'],
                        'files_processed': session_row['files_processed'],
                        'total_files_discovered': session_row['total_files_discovered'],
                        'initialization_started_at': session_row['initialization_started_at'],
                        'initialization_completed_at': session_row['initialization_completed_at']
                    }
            
            # Get overall file metadata statistics
            total_files_query = "SELECT COUNT(*) as total FROM file_metadata"
            analyzed_files_query = "SELECT COUNT(*) as analyzed FROM file_metadata WHERE initialization_analyzed = TRUE"
            
            total_files = self.db.execute_query(total_files_query)[0]['total']
            analyzed_files = self.db.execute_query(analyzed_files_query)[0]['analyzed']
            
            completion_percentage = (analyzed_files / total_files * 100) if total_files > 0 else 0
            
            # Get unanalyzed files
            unanalyzed_query = """
                SELECT file_path, language, file_size, created_at
                FROM file_metadata
                WHERE initialization_analyzed = FALSE
                ORDER BY created_at ASC
                LIMIT 10
            """
            
            unanalyzed_results = self.db.execute_query(unanalyzed_query)
            unanalyzed_files = []
            for row in unanalyzed_results:
                unanalyzed_files.append({
                    'file_path': row['file_path'],
                    'language': row['language'],
                    'file_size': row['file_size'],
                    'created_at': row['created_at']
                })
            
            return {
                'session_info': session_info,
                'total_files': total_files,
                'analyzed_files': analyzed_files,
                'unanalyzed_files_count': total_files - analyzed_files,
                'completion_percentage': round(completion_percentage, 2),
                'unanalyzed_files_sample': unanalyzed_files,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.db.logger.error(f"Error getting initialization progress: {e}")
            return {
                'error': str(e),
                'total_files': 0,
                'analyzed_files': 0,
                'completion_percentage': 0.0,
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def get_unanalyzed_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of files that haven't been analyzed during initialization.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of unanalyzed file information
        """
        try:
            query = """
                SELECT file_path, language, file_size, created_at, file_purpose
                FROM file_metadata
                WHERE initialization_analyzed = FALSE
                ORDER BY created_at ASC
                LIMIT ?
            """
            
            results = self.db.execute_query(query, (limit,))
            unanalyzed_files = []
            
            for row in results:
                unanalyzed_files.append({
                    'file_path': row['file_path'],
                    'language': row['language'],
                    'file_size': row['file_size'],
                    'file_purpose': row['file_purpose'],
                    'created_at': row['created_at']
                })
            
            return unanalyzed_files
            
        except Exception as e:
            self.db.logger.error(f"Error getting unanalyzed files: {e}")
            return []
    
    def analyze_and_store_file_metadata(self, file_path: str) -> bool:
        """
        Analyze a file and store its metadata in the database.
        This combines file analysis with database storage.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from pathlib import Path
            
            file_obj = Path(file_path)
            if not file_obj.exists():
                return False
            
            # Get basic file information
            file_size = file_obj.stat().st_size
            language = self._detect_language_from_extension(file_obj.suffix)
            
            # Analyze dependencies
            dependency_analysis = {}
            if self.dependency_analysis:
                dependency_analysis = self.dependency_analysis.analyze_file_dependencies(file_path)
            
            # Determine file purpose based on path and content analysis
            file_purpose = self._determine_file_purpose(file_path, dependency_analysis)
            
            # Create basic file description
            file_description = self._generate_file_description(file_path, dependency_analysis, language)
            
            # Extract important exports
            important_exports = dependency_analysis.get('exports', [])
            dependencies = dependency_analysis.get('dependencies', [])
            
            # Store metadata in database
            success = self.create_or_update_file_metadata(
                file_path=file_path,
                file_purpose=file_purpose,
                file_description=file_description,
                important_exports=important_exports,
                dependencies=dependencies,
                language=language,
                file_size=file_size,
                analysis_metadata={
                    'analysis_result': dependency_analysis,
                    'analyzed_at': datetime.now().isoformat()
                }
            )
            
            # Mark as analyzed if storage was successful
            if success:
                self.mark_file_analyzed(file_path)
            
            return success
            
        except Exception as e:
            self.db.logger.error(f"Error analyzing and storing file metadata for {file_path}: {e}")
            return False
    
    def _detect_language_from_extension(self, extension: str) -> str:
        """Detect programming language from file extension."""
        extension = extension.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'bash',
            '.sql': 'sql',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.md': 'markdown',
            '.rst': 'restructuredtext'
        }
        
        return language_map.get(extension, 'unknown')
    
    def _determine_file_purpose(self, file_path: str, dependency_analysis: Dict[str, Any]) -> str:
        """Determine the purpose of a file based on its path and analysis."""
        from pathlib import Path
        
        path_lower = file_path.lower()
        filename = Path(file_path).name.lower()
        
        # Test files
        if ('test' in path_lower or 'spec' in path_lower or 
            filename.startswith('test_') or filename.endswith('_test.py') or
            filename.endswith('.test.js') or filename.endswith('.spec.js')):
            return 'test'
        
        # Configuration files
        if ('config' in path_lower or 'settings' in path_lower or
            filename in ['dockerfile', 'makefile', '.env', 'package.json', 'requirements.txt']):
            return 'configuration'
        
        # Documentation files
        if filename.endswith(('.md', '.rst', '.txt')) or filename == 'readme':
            return 'documentation'
        
        # Build/deployment files
        if ('build' in path_lower or 'deploy' in path_lower or 'script' in path_lower or
            filename.endswith(('.sh', '.bat', '.ps1'))):
            return 'build'
        
        # Main entry points
        if filename in ['main.py', 'index.js', 'app.py', 'server.py', '__main__.py']:
            return 'entry_point'
        
        # Utility files
        if 'util' in path_lower or 'helper' in path_lower or 'common' in path_lower:
            return 'utility'
        
        # API/Service files
        if 'api' in path_lower or 'service' in path_lower or 'handler' in path_lower:
            return 'api'
        
        # Model/Data files
        if 'model' in path_lower or 'schema' in path_lower or 'entity' in path_lower:
            return 'model'
        
        # Component files (for frontend)
        if 'component' in path_lower or filename.endswith(('.jsx', '.tsx', '.vue')):
            return 'component'
        
        # Default to source if not otherwise categorized
        return 'source'
    
    def _generate_file_description(self, file_path: str, dependency_analysis: Dict[str, Any], language: str) -> str:
        """Generate a basic description for the file."""
        from pathlib import Path
        
        filename = Path(file_path).name
        exports = dependency_analysis.get('exports', [])
        imports = dependency_analysis.get('imports', [])
        
        description_parts = [f"{language.title()} file: {filename}"]
        
        if exports:
            if len(exports) <= 3:
                description_parts.append(f"Exports: {', '.join(exports)}")
            else:
                description_parts.append(f"Exports {len(exports)} items including: {', '.join(exports[:3])}")
        
        if imports:
            if len(imports) <= 3:
                description_parts.append(f"Imports: {', '.join(imports)}")
            else:
                description_parts.append(f"Has {len(imports)} dependencies")
        
        return ". ".join(description_parts)
    
    def batch_analyze_files(self, file_paths: List[str], batch_size: int = 10) -> Dict[str, Any]:
        """
        Analyze multiple files in batches for initialization.
        
        Args:
            file_paths: List of file paths to analyze
            batch_size: Number of files to process in each batch
            
        Returns:
            Dictionary with batch analysis results
        """
        try:
            total_files = len(file_paths)
            processed_files = 0
            successful_analyses = 0
            failed_analyses = 0
            failed_files = []
            
            # Process files in batches
            for i in range(0, total_files, batch_size):
                batch_files = file_paths[i:i + batch_size]
                
                for file_path in batch_files:
                    try:
                        success = self.analyze_and_store_file_metadata(file_path)
                        if success:
                            successful_analyses += 1
                        else:
                            failed_analyses += 1
                            failed_files.append(file_path)
                        
                        processed_files += 1
                        
                    except Exception as e:
                        self.db.logger.error(f"Error analyzing file {file_path}: {e}")
                        failed_analyses += 1
                        failed_files.append(file_path)
                        processed_files += 1
                
                # Log progress
                progress = (processed_files / total_files) * 100
                self.db.logger.info(f"Batch analysis progress: {processed_files}/{total_files} files ({progress:.1f}%)")
            
            return {
                'total_files': total_files,
                'processed_files': processed_files,
                'successful_analyses': successful_analyses,
                'failed_analyses': failed_analyses,
                'failed_files': failed_files,
                'success_rate': (successful_analyses / total_files * 100) if total_files > 0 else 0,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.db.logger.error(f"Error in batch file analysis: {e}")
            return {
                'total_files': len(file_paths),
                'processed_files': 0,
                'successful_analyses': 0,
                'failed_analyses': len(file_paths),
                'error': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }