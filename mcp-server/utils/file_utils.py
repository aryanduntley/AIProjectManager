"""
File utility functions for the AI Project Manager MCP Server.

Provides file system operations, analysis, and theme discovery utilities.
"""

import os
import re
import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class FileAnalyzer:
    """Analyzes files for theme discovery and dependency tracking."""
    
    def __init__(self):
        self.programming_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.vue', '.svelte', '.html', '.css', '.scss', '.sass', '.less'
        }
        
        self.config_extensions = {
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.env', '.properties'
        }
        
        self.doc_extensions = {
            '.md', '.txt', '.rst', '.adoc'
        }
    
    def analyze_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project structure for theme discovery."""
        try:
            structure = {
                'directories': {},
                'files': [],
                'imports': {},
                'keywords': defaultdict(int),
                'patterns': {},
                'frameworks': set(),
                'languages': set()
            }
            
            # Walk through project directory
            for root, dirs, files in os.walk(project_path):
                root_path = Path(root)
                relative_root = root_path.relative_to(project_path)
                
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                    'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build',
                    'target', '.git', '.svn', 'deps', 'dependencies'
                }]
                
                # Analyze directory structure
                if relative_root != Path('.'):
                    structure['directories'][str(relative_root)] = {
                        'files': [],
                        'subdirs': dirs.copy(),
                        'purpose': self._analyze_directory_purpose(root_path, files)
                    }
                
                # Analyze files
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    file_path = root_path / file
                    relative_file = file_path.relative_to(project_path)
                    
                    file_info = self._analyze_file(file_path)
                    file_info['path'] = str(relative_file)
                    file_info['directory'] = str(relative_root)
                    
                    structure['files'].append(file_info)
                    
                    # Add to directory files
                    if str(relative_root) in structure['directories']:
                        structure['directories'][str(relative_root)]['files'].append(file)
                    
                    # Collect imports and keywords
                    if file_info.get('imports'):
                        structure['imports'][str(relative_file)] = file_info['imports']
                    
                    for keyword in file_info.get('keywords', []):
                        structure['keywords'][keyword] += 1
                    
                    # Detect frameworks and languages
                    structure['frameworks'].update(file_info.get('frameworks', []))
                    if file_info.get('language'):
                        structure['languages'].add(file_info['language'])
            
            # Convert sets to lists for JSON serialization
            structure['frameworks'] = list(structure['frameworks'])
            structure['languages'] = list(structure['languages'])
            structure['keywords'] = dict(structure['keywords'])
            
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing project structure: {e}")
            return {}
    
    def _analyze_directory_purpose(self, dir_path: Path, files: List[str]) -> Dict[str, Any]:
        """Analyze directory purpose based on name and contents."""
        dir_name = dir_path.name.lower()
        purpose = {
            'category': 'unknown',
            'confidence': 0.0,
            'indicators': []
        }
        
        # Directory name patterns
        patterns = {
            'components': ['component', 'comp', 'widget'],
            'pages': ['page', 'view', 'screen', 'route'],
            'services': ['service', 'api', 'client', 'adapter'],
            'utils': ['util', 'helper', 'tool', 'common', 'shared'],
            'config': ['config', 'setting', 'env', 'constant'],
            'test': ['test', 'spec', '__test__'],
            'assets': ['asset', 'static', 'public', 'resource'],
            'styles': ['style', 'css', 'scss', 'theme'],
            'data': ['data', 'model', 'schema', 'entity'],
            'auth': ['auth', 'login', 'user', 'account'],
            'database': ['db', 'database', 'migration', 'model'],
            'middleware': ['middleware', 'guard', 'interceptor'],
            'hooks': ['hook', 'custom'],
            'store': ['store', 'state', 'redux', 'context'],
            'layout': ['layout', 'template', 'wrapper']
        }
        
        # Check directory name against patterns
        for category, keywords in patterns.items():
            for keyword in keywords:
                if keyword in dir_name:
                    purpose['category'] = category
                    purpose['confidence'] = 0.8
                    purpose['indicators'].append(f"directory_name:{keyword}")
                    break
            if purpose['confidence'] > 0:
                break
        
        # Analyze file contents for additional context
        file_extensions = [Path(f).suffix.lower() for f in files]
        
        # Test directory indicators
        test_extensions = ['.test.js', '.spec.js', '.test.ts', '.spec.ts']
        if any(any(ext in f for ext in test_extensions) or 
               'test' in f.lower() or 'spec' in f.lower() for f in files):
            if purpose['category'] == 'unknown':
                purpose['category'] = 'test'
                purpose['confidence'] = 0.9
            purpose['indicators'].append('test_files')
        
        # Component indicators
        if '.tsx' in file_extensions or '.jsx' in file_extensions:
            if purpose['category'] == 'unknown':
                purpose['category'] = 'components'
                purpose['confidence'] = 0.7
            purpose['indicators'].append('react_files')
        
        # Style indicators
        style_extensions = ['.css', '.scss', '.sass', '.less']
        if any(ext in style_extensions for ext in file_extensions):
            if purpose['category'] == 'unknown':
                purpose['category'] = 'styles'
                purpose['confidence'] = 0.8
            purpose['indicators'].append('style_files')
        
        return purpose
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze individual file for theme information."""
        file_info = {
            'name': file_path.name,
            'extension': file_path.suffix.lower(),
            'size': 0,
            'language': None,
            'imports': [],
            'exports': [],
            'keywords': [],
            'frameworks': [],
            'functions': [],
            'classes': [],
            'type': 'unknown'
        }
        
        try:
            # Get file size
            file_info['size'] = file_path.stat().st_size
            
            # Determine file type and language
            extension = file_path.suffix.lower()
            file_info['type'] = self._get_file_type(extension)
            file_info['language'] = self._get_language(extension)
            
            # Skip binary files and very large files
            if file_info['size'] > 1024 * 1024:  # 1MB limit
                return file_info
            
            if extension in self.programming_extensions:
                # Analyze source code files
                content = self._read_file_safely(file_path)
                if content:
                    file_info.update(self._analyze_source_code(content, extension))
            
            elif extension in self.config_extensions:
                # Analyze configuration files
                content = self._read_file_safely(file_path)
                if content:
                    file_info.update(self._analyze_config_file(content, extension))
            
            return file_info
            
        except Exception as e:
            logger.debug(f"Error analyzing file {file_path}: {e}")
            return file_info
    
    def _read_file_safely(self, file_path: Path) -> Optional[str]:
        """Safely read file content with encoding detection."""
        try:
            # Try UTF-8 first
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Try with error handling
                return file_path.read_text(encoding='utf-8', errors='ignore')
            except:
                return None
        except Exception:
            return None
    
    def _get_file_type(self, extension: str) -> str:
        """Determine file type from extension."""
        if extension in self.programming_extensions:
            return 'source'
        elif extension in self.config_extensions:
            return 'config'
        elif extension in self.doc_extensions:
            return 'documentation'
        elif extension in ['.sql']:
            return 'database'
        elif extension in ['.dockerfile', '.dockerignore']:
            return 'deployment'
        elif extension in ['.gitignore', '.gitattributes']:
            return 'vcs'
        else:
            return 'unknown'
    
    def _get_language(self, extension: str) -> Optional[str]:
        """Determine programming language from extension."""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.vue': 'vue',
            '.svelte': 'svelte',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less'
        }
        return language_map.get(extension)
    
    def _analyze_source_code(self, content: str, extension: str) -> Dict[str, Any]:
        """Analyze source code content."""
        info = {
            'imports': [],
            'exports': [],
            'keywords': [],
            'frameworks': [],
            'functions': [],
            'classes': []
        }
        
        try:
            if extension == '.py':
                info.update(self._analyze_python_code(content))
            elif extension in ['.js', '.ts', '.jsx', '.tsx']:
                info.update(self._analyze_javascript_code(content))
            else:
                # Generic analysis
                info.update(self._analyze_generic_code(content))
                
        except Exception as e:
            logger.debug(f"Error analyzing source code: {e}")
        
        return info
    
    def _analyze_python_code(self, content: str) -> Dict[str, Any]:
        """Analyze Python source code."""
        info = {
            'imports': [],
            'exports': [],
            'keywords': [],
            'frameworks': [],
            'functions': [],
            'classes': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        info['imports'].append(alias.name)
                        info['keywords'].extend(alias.name.split('.'))
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        info['imports'].append(node.module)
                        info['keywords'].extend(node.module.split('.'))
                        
                        # Detect frameworks
                        if any(fw in node.module.lower() for fw in [
                            'django', 'flask', 'fastapi', 'pyramid', 'tornado',
                            'sqlalchemy', 'pandas', 'numpy', 'tensorflow', 'pytorch'
                        ]):
                            info['frameworks'].append(node.module.split('.')[0])
                
                elif isinstance(node, ast.FunctionDef):
                    info['functions'].append(node.name)
                    info['keywords'].append(node.name.lower())
                
                elif isinstance(node, ast.ClassDef):
                    info['classes'].append(node.name)
                    info['keywords'].append(node.name.lower())
                    
        except SyntaxError:
            # Fallback to regex-based analysis
            info.update(self._analyze_generic_code(content))
        
        return info
    
    def _analyze_javascript_code(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript source code."""
        info = {
            'imports': [],
            'exports': [],
            'keywords': [],
            'frameworks': [],
            'functions': [],
            'classes': []
        }
        
        # Import patterns
        import_patterns = [
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\([\'"]([^\'"]+)[\'"]\)',
            r'import\([\'"]([^\'"]+)[\'"]\)'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            info['imports'].extend(matches)
            for match in matches:
                info['keywords'].extend(match.split('/'))
        
        # Export patterns
        export_patterns = [
            r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)',
            r'export\s*{\s*([^}]+)\s*}',
            r'module\.exports\s*=\s*(\w+)'
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content)
            if isinstance(matches, list) and matches:
                if ',' in str(matches[0]):
                    # Handle multiple exports
                    exports = [exp.strip() for exp in str(matches[0]).split(',')]
                    info['exports'].extend(exports)
                else:
                    info['exports'].extend(matches)
        
        # Function patterns
        function_patterns = [
            r'function\s+(\w+)',
            r'const\s+(\w+)\s*=\s*\(',
            r'(\w+)\s*:\s*function',
            r'(\w+)\s*=>\s*{'
        ]
        
        for pattern in function_patterns:
            matches = re.findall(pattern, content)
            info['functions'].extend(matches)
            info['keywords'].extend([m.lower() for m in matches])
        
        # Class patterns
        class_matches = re.findall(r'class\s+(\w+)', content)
        info['classes'].extend(class_matches)
        info['keywords'].extend([c.lower() for c in class_matches])
        
        # Framework detection
        framework_indicators = {
            'react': ['useState', 'useEffect', 'Component', 'jsx', 'tsx'],
            'vue': ['Vue', 'createApp', 'defineComponent', '.vue'],
            'angular': ['@Component', '@Injectable', 'NgModule'],
            'express': ['express()', 'app.get', 'app.post'],
            'nestjs': ['@Controller', '@Injectable', '@Module'],
            'next': ['next/', 'getServerSideProps', 'getStaticProps']
        }
        
        for framework, indicators in framework_indicators.items():
            if any(indicator in content for indicator in indicators):
                info['frameworks'].append(framework)
        
        return info
    
    def _analyze_generic_code(self, content: str) -> Dict[str, Any]:
        """Generic code analysis using regex patterns."""
        info = {
            'imports': [],
            'exports': [],
            'keywords': [],
            'frameworks': [],
            'functions': [],
            'classes': []
        }
        
        # Extract common programming keywords
        common_keywords = [
            'class', 'function', 'method', 'interface', 'component',
            'service', 'controller', 'model', 'view', 'router',
            'middleware', 'guard', 'filter', 'decorator', 'annotation'
        ]
        
        content_lower = content.lower()
        for keyword in common_keywords:
            if keyword in content_lower:
                info['keywords'].append(keyword)
        
        # Extract identifiers that might be relevant
        identifier_pattern = r'\b[A-Z][a-zA-Z0-9]*\b'
        identifiers = re.findall(identifier_pattern, content)
        info['keywords'].extend([id.lower() for id in identifiers[:20]])  # Limit to avoid noise
        
        return info
    
    def _analyze_config_file(self, content: str, extension: str) -> Dict[str, Any]:
        """Analyze configuration files."""
        info = {
            'keywords': [],
            'frameworks': []
        }
        
        try:
            if extension == '.json':
                data = json.loads(content)
                info['keywords'].extend(self._extract_json_keywords(data))
                
                # Detect frameworks from package.json
                if 'dependencies' in data or 'devDependencies' in data:
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    for dep in deps.keys():
                        if any(fw in dep for fw in [
                            'react', 'vue', 'angular', 'express', 'next',
                            'django', 'flask', 'spring', 'laravel'
                        ]):
                            info['frameworks'].append(dep.split('-')[0])
                            
        except Exception as e:
            logger.debug(f"Error parsing config file: {e}")
        
        return info
    
    def _extract_json_keywords(self, data: Any, depth: int = 0) -> List[str]:
        """Extract keywords from JSON data recursively."""
        if depth > 3:  # Limit recursion depth
            return []
        
        keywords = []
        
        if isinstance(data, dict):
            keywords.extend(data.keys())
            for value in data.values():
                keywords.extend(self._extract_json_keywords(value, depth + 1))
        elif isinstance(data, list):
            for item in data[:10]:  # Limit list processing
                keywords.extend(self._extract_json_keywords(item, depth + 1))
        elif isinstance(data, str):
            # Extract meaningful words from strings
            words = re.findall(r'\b[a-zA-Z]{3,}\b', data)
            keywords.extend(words[:5])  # Limit to avoid noise
        
        return keywords