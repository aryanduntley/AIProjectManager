"""
Theme discovery operations.

Handles automatic theme detection and discovery from project files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import Counter
import re

from .base_operations import BaseThemeOperations

logger = logging.getLogger(__name__)


class ThemeDiscoveryOperations(BaseThemeOperations):
    """Handles theme discovery and automatic detection."""
    
    async def discover_themes(self, project_path: Path, force_rediscovery: bool = False) -> str:
        """Automatically discover themes in a project."""
        try:
            project_path = Path(project_path)
            themes_dir = self.get_themes_directory(project_path)
            
            # Check if themes already exist and force_rediscovery is False
            if not force_rediscovery and themes_dir.exists():
                themes_index = self.load_themes_index(themes_dir)
                if themes_index and themes_index.get("themes"):
                    existing_count = len(themes_index["themes"])
                    return f"Themes already exist ({existing_count} themes found). Use force_rediscovery=true to rediscover."
            
            # Ensure themes directory exists
            themes_dir.mkdir(parents=True, exist_ok=True)
            
            # Perform theme discovery
            discovery_result = await self._discover_themes_basic(project_path)
            
            # Save discovered themes
            await self.save_themes(themes_dir, discovery_result["themes"])
            
            # Update themes index with discovery metadata
            await self.update_themes_index(themes_dir, discovery_result)
            
            # Sync with database if available
            sync_result = ""
            if self.theme_flow_queries:
                try:
                    for theme_name, theme_data in discovery_result["themes"].items():
                        await self.theme_flow_queries.create_or_update_theme(
                            theme_name=theme_name,
                            theme_data=theme_data
                        )
                    sync_result = " and synced with database"
                except Exception as e:
                    sync_result = f" (database sync failed: {str(e)})"
            
            result = f"Theme discovery completed successfully{sync_result}:\n"
            result += f"- Themes discovered: {len(discovery_result['themes'])}\n"
            result += f"- Files analyzed: {discovery_result['files_analyzed']}\n"
            result += f"- Discovery method: {discovery_result['method']}\n"
            result += f"- Themes directory: {themes_dir}\n\n"
            
            # List discovered themes
            result += "Discovered themes:\n"
            for theme_name, theme_data in discovery_result["themes"].items():
                file_count = theme_data.get("statistics", {}).get("file_count", 0)
                keywords = theme_data.get("keywords", [])
                result += f"  • {theme_name}: {file_count} files"
                if keywords:
                    result += f", keywords: {', '.join(keywords[:5])}"
                    if len(keywords) > 5:
                        result += f" (+{len(keywords)-5} more)"
                result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error discovering themes: {e}")
            return f"Error discovering themes: {str(e)}"
    
    async def _discover_themes_basic(self, project_path: Path) -> Dict[str, Any]:
        """Perform basic theme discovery using file patterns and content analysis."""
        themes = {}
        files_analyzed = 0
        
        # Define file patterns to analyze
        patterns = [
            "*.py", "*.js", "*.ts", "*.jsx", "*.tsx",
            "*.java", "*.cpp", "*.c", "*.h", "*.cs",
            "*.md", "*.txt", "*.json", "*.yaml", "*.yml",
            "*.html", "*.css", "*.scss", "*.less"
        ]
        
        # Collect all files to analyze
        files_to_analyze = []
        for pattern in patterns:
            files_to_analyze.extend(project_path.rglob(pattern))
        
        # Exclude common directories
        excluded_dirs = {
            '.git', '.svn', 'node_modules', '__pycache__', '.pytest_cache',
            'venv', 'env', '.venv', 'build', 'dist', 'target'
        }
        
        # Filter out files in excluded directories
        filtered_files = []
        for file_path in files_to_analyze:
            if not any(excluded_dir in file_path.parts for excluded_dir in excluded_dirs):
                filtered_files.append(file_path)
        
        # Analyze files for theme detection
        keyword_counter = Counter()
        file_themes = {}
        
        for file_path in filtered_files[:500]:  # Limit to first 500 files for performance
            try:
                if file_path.is_file() and file_path.stat().st_size < 1024 * 1024:  # Skip files > 1MB
                    files_analyzed += 1
                    file_keywords = self._extract_keywords_from_file(file_path)
                    
                    if file_keywords:
                        keyword_counter.update(file_keywords)
                        file_themes[str(file_path.relative_to(project_path))] = file_keywords
                        
            except Exception as e:
                logger.debug(f"Error analyzing file {file_path}: {e}")
                continue
        
        # Group keywords into themes
        theme_groups = self._group_keywords_into_themes(keyword_counter)
        
        # Create theme objects
        for theme_name, theme_keywords in theme_groups.items():
            # Find files associated with this theme
            theme_files = []
            for file_path, file_keywords in file_themes.items():
                if any(keyword in file_keywords for keyword in theme_keywords):
                    theme_files.append(file_path)
            
            # Create theme data structure
            theme_data = self.create_default_theme(
                theme_name=theme_name,
                description=f"Automatically discovered theme related to {theme_name.lower().replace('_', ' ')}"
            )
            
            theme_data.update({
                "keywords": list(theme_keywords),
                "files": theme_files,
                "patterns": self._generate_file_patterns(theme_files),
                "statistics": {
                    "file_count": len(theme_files),
                    "flow_count": 0,
                    "usage_count": sum(keyword_counter[kw] for kw in theme_keywords)
                }
            })
            
            themes[theme_name] = theme_data
        
        return {
            "themes": themes,
            "files_analyzed": files_analyzed,
            "method": "basic_keyword_analysis",
            "statistics": {
                "total_keywords": len(keyword_counter),
                "most_common_keywords": keyword_counter.most_common(10),
                "theme_groups_created": len(theme_groups)
            }
        }
    
    def _extract_keywords_from_file(self, file_path: Path) -> List[str]:
        """Extract potential theme keywords from a file."""
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Extract keywords based on file type
            keywords = set()
            
            # Common programming keywords and patterns
            if file_path.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs']:
                # Extract class names
                class_matches = re.findall(r'class\s+(\w+)', content, re.IGNORECASE)
                keywords.update(self._normalize_keywords(class_matches))
                
                # Extract function names
                function_matches = re.findall(r'(?:def|function|public|private|protected)\s+(\w+)', content, re.IGNORECASE)
                keywords.update(self._normalize_keywords(function_matches))
                
                # Extract import/include statements
                import_matches = re.findall(r'(?:import|from|include|require)\s+["\']?(\w+)', content, re.IGNORECASE)
                keywords.update(self._normalize_keywords(import_matches))
            
            # Documentation files
            elif file_path.suffix in ['.md', '.txt']:
                # Extract headers
                header_matches = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
                keywords.update(self._normalize_keywords(header_matches))
                
                # Extract emphasized words
                emphasis_matches = re.findall(r'\*\*(.+?)\*\*|__(.+?)__|`(.+?)`', content)
                for match_group in emphasis_matches:
                    for match in match_group:
                        if match:
                            keywords.update(self._normalize_keywords([match]))
            
            # Configuration files
            elif file_path.suffix in ['.json', '.yaml', '.yml']:
                # Extract top-level keys
                if file_path.suffix == '.json':
                    try:
                        data = json.loads(content)
                        if isinstance(data, dict):
                            keywords.update(self._normalize_keywords(data.keys()))
                    except json.JSONDecodeError:
                        pass
                else:
                    # Simple YAML key extraction
                    yaml_keys = re.findall(r'^(\w+):', content, re.MULTILINE)
                    keywords.update(self._normalize_keywords(yaml_keys))
            
            # Filter and return meaningful keywords
            filtered_keywords = []
            for keyword in keywords:
                if len(keyword) >= 3 and keyword.lower() not in {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'was', 'one', 'our', 'out', 'get', 'use', 'man', 'new', 'now', 'way', 'its', 'two', 'how', 'may', 'say', 'she', 'has', 'her', 'him', 'his', 'who', 'oil', 'sit', 'set', 'run', 'eat', 'far', 'sea', 'eye'}:
                    filtered_keywords.append(keyword)
            
            return filtered_keywords[:20]  # Limit to top 20 keywords per file
            
        except Exception as e:
            logger.debug(f"Error extracting keywords from {file_path}: {e}")
            return []
    
    def _normalize_keywords(self, keywords: List[str]) -> List[str]:
        """Normalize keywords by cleaning and standardizing them."""
        normalized = []
        for keyword in keywords:
            if isinstance(keyword, str):
                # Remove special characters, convert to lowercase
                clean_keyword = re.sub(r'[^a-zA-Z0-9_]', '', keyword.strip())
                if clean_keyword and len(clean_keyword) >= 3:
                    # Convert camelCase to snake_case for consistency
                    snake_case = re.sub(r'([A-Z])', r'_\1', clean_keyword).lower().lstrip('_')
                    normalized.append(snake_case)
        return normalized
    
    def _group_keywords_into_themes(self, keyword_counter: Counter) -> Dict[str, List[str]]:
        """Group keywords into logical themes."""
        themes = {}
        
        # Get most common keywords
        common_keywords = [kw for kw, count in keyword_counter.most_common(100) if count >= 2]
        
        # Define theme categories with their associated keywords
        theme_patterns = {
            'authentication': ['auth', 'login', 'user', 'password', 'token', 'session', 'oauth', 'jwt', 'signin', 'signup'],
            'database': ['db', 'database', 'sql', 'query', 'table', 'model', 'schema', 'migration', 'entity', 'orm'],
            'api': ['api', 'rest', 'endpoint', 'request', 'response', 'http', 'route', 'controller', 'service'],
            'frontend': ['ui', 'component', 'render', 'view', 'template', 'css', 'html', 'dom', 'react', 'vue'],
            'testing': ['test', 'spec', 'mock', 'assert', 'expect', 'junit', 'pytest', 'describe', 'it'],
            'configuration': ['config', 'settings', 'env', 'environment', 'properties', 'yaml', 'json'],
            'security': ['security', 'crypto', 'hash', 'encrypt', 'decrypt', 'secure', 'ssl', 'tls'],
            'data_processing': ['data', 'process', 'transform', 'parse', 'validate', 'serialize', 'deserialize'],
            'logging': ['log', 'logger', 'debug', 'info', 'warn', 'error', 'trace'],
            'utilities': ['util', 'helper', 'common', 'shared', 'tool', 'library']
        }
        
        # Assign keywords to themes
        assigned_keywords = set()
        
        for theme_name, theme_keywords in theme_patterns.items():
            matching_keywords = []
            
            for keyword in common_keywords:
                if keyword in assigned_keywords:
                    continue
                    
                # Check if keyword matches theme pattern
                if any(pattern in keyword.lower() for pattern in theme_keywords):
                    matching_keywords.append(keyword)
                    assigned_keywords.add(keyword)
            
            if matching_keywords:
                themes[theme_name] = matching_keywords
        
        # Create a "general" theme for unassigned high-frequency keywords
        unassigned_keywords = [kw for kw in common_keywords[:20] if kw not in assigned_keywords]
        if unassigned_keywords:
            themes['general'] = unassigned_keywords
        
        return themes
    
    def _generate_file_patterns(self, file_paths: List[str]) -> List[str]:
        """Generate file patterns from a list of file paths."""
        patterns = set()
        
        for file_path in file_paths[:10]:  # Limit to first 10 files
            path = Path(file_path)
            
            # Add extension pattern
            if path.suffix:
                patterns.add(f"*{path.suffix}")
            
            # Add directory patterns
            if len(path.parts) > 1:
                patterns.add(f"{path.parts[0]}/*")
            
            # Add specific file patterns for common names
            if path.name.lower() in ['config.py', 'settings.py', 'models.py', 'views.py', 'utils.py']:
                patterns.add(path.name)
        
        return list(patterns)[:5]  # Limit to 5 patterns

    def _get_files_in_directory(self, directory: Path, project_path: Path, max_depth: int = 3) -> List[str]:
        """Get files in a directory with depth limit."""
        files = []
        try:
            for item in directory.rglob('*'):
                if item.is_file() and self._is_source_file(item):
                    rel_path = item.relative_to(project_path)
                    # Check depth
                    if len(rel_path.parts) <= max_depth:
                        files.append(str(rel_path))
        except Exception as e:
            logger.warning(f"Error scanning directory {directory}: {e}")
        return files[:50]  # Limit to 50 files per theme

    def _is_source_file(self, file_path: Path) -> bool:
        """Check if file is a source code file."""
        source_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.rb', '.php', '.go', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.less', '.vue', '.svelte'
        }
        return file_path.suffix.lower() in source_extensions