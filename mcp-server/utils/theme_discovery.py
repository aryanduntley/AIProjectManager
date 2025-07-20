"""
Theme discovery engine for the AI Project Manager MCP Server.

Automatically discovers and categorizes themes from project structure analysis.
"""

import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict, Counter

from utils.file_utils import FileAnalyzer

logger = logging.getLogger(__name__)


class ThemeDiscovery:
    """Discovers themes from project structure and code analysis."""
    
    def __init__(self):
        self.file_analyzer = FileAnalyzer()
        
        # Predefined theme categories and their indicators
        self.theme_categories = {
            'functional_domains': {
                'authentication': {
                    'keywords': ['auth', 'login', 'register', 'user', 'session', 'token', 'jwt', 'oauth', 'password', 'signin', 'signup'],
                    'directories': ['auth', 'authentication', 'user', 'account', 'login'],
                    'files': ['auth', 'login', 'user', 'session', 'token'],
                    'frameworks': ['passport', 'auth0', 'firebase-auth']
                },
                'payment': {
                    'keywords': ['payment', 'billing', 'checkout', 'stripe', 'paypal', 'invoice', 'transaction', 'credit', 'card', 'charge'],
                    'directories': ['payment', 'billing', 'checkout', 'transaction'],
                    'files': ['payment', 'billing', 'stripe', 'checkout', 'transaction'],
                    'frameworks': ['stripe', 'paypal-sdk', 'square']
                },
                'user-management': {
                    'keywords': ['user', 'profile', 'account', 'settings', 'preference', 'notification', 'avatar'],
                    'directories': ['user', 'profile', 'account', 'settings'],
                    'files': ['user', 'profile', 'account', 'settings'],
                    'frameworks': []
                },
                'messaging': {
                    'keywords': ['message', 'chat', 'notification', 'email', 'sms', 'push', 'websocket', 'socket'],
                    'directories': ['message', 'chat', 'notification', 'mail'],
                    'files': ['message', 'chat', 'notification', 'email', 'websocket'],
                    'frameworks': ['socket.io', 'pusher', 'sendgrid', 'nodemailer']
                },
                'search': {
                    'keywords': ['search', 'filter', 'query', 'index', 'elasticsearch', 'solr', 'algolia'],
                    'directories': ['search', 'filter', 'query'],
                    'files': ['search', 'filter', 'query', 'index'],
                    'frameworks': ['elasticsearch', 'algolia', 'solr']
                }
            },
            'technical_layers': {
                'database': {
                    'keywords': ['db', 'database', 'model', 'schema', 'migration', 'entity', 'repository', 'dao', 'orm'],
                    'directories': ['db', 'database', 'model', 'schema', 'migration', 'entity'],
                    'files': ['model', 'schema', 'migration', 'entity', 'repository'],
                    'frameworks': ['sqlalchemy', 'mongoose', 'sequelize', 'prisma', 'typeorm']
                },
                'api': {
                    'keywords': ['api', 'endpoint', 'route', 'controller', 'service', 'handler', 'middleware', 'rest', 'graphql'],
                    'directories': ['api', 'route', 'controller', 'service', 'handler', 'endpoint'],
                    'files': ['api', 'route', 'controller', 'service', 'handler'],
                    'frameworks': ['express', 'fastapi', 'spring', 'django-rest', 'graphql']
                },
                'security': {
                    'keywords': ['security', 'auth', 'permission', 'role', 'guard', 'middleware', 'cors', 'csrf', 'validation'],
                    'directories': ['security', 'guard', 'permission', 'middleware'],
                    'files': ['security', 'guard', 'permission', 'middleware', 'validation'],
                    'frameworks': ['helmet', 'cors', 'rate-limiting']
                },
                'testing': {
                    'keywords': ['test', 'spec', 'mock', 'fixture', 'unit', 'integration', 'e2e'],
                    'directories': ['test', 'tests', '__tests__', 'spec', 'e2e'],
                    'files': ['test', 'spec', 'mock', 'fixture'],
                    'frameworks': ['jest', 'mocha', 'pytest', 'jasmine', 'cypress']
                },
                'caching': {
                    'keywords': ['cache', 'redis', 'memcached', 'session', 'store'],
                    'directories': ['cache', 'store'],
                    'files': ['cache', 'redis', 'store'],
                    'frameworks': ['redis', 'memcached', 'node-cache']
                }
            },
            'user_interface': {
                'components': {
                    'keywords': ['component', 'widget', 'element', 'ui', 'button', 'form', 'input', 'modal'],
                    'directories': ['component', 'widget', 'ui', 'element'],
                    'files': ['component', 'widget', 'button', 'form', 'modal'],
                    'frameworks': ['react', 'vue', 'angular', 'svelte']
                },
                'pages': {
                    'keywords': ['page', 'view', 'screen', 'route', 'template'],
                    'directories': ['page', 'pages', 'view', 'views', 'screen', 'template'],
                    'files': ['page', 'view', 'screen', 'template'],
                    'frameworks': ['next', 'nuxt', 'gatsby']
                },
                'layout': {
                    'keywords': ['layout', 'header', 'footer', 'sidebar', 'navigation', 'menu'],
                    'directories': ['layout', 'layouts', 'navigation'],
                    'files': ['layout', 'header', 'footer', 'sidebar', 'navigation'],
                    'frameworks': []
                },
                'styling': {
                    'keywords': ['style', 'css', 'scss', 'theme', 'design', 'ui'],
                    'directories': ['style', 'styles', 'css', 'scss', 'theme'],
                    'files': ['style', 'css', 'scss', 'theme'],
                    'frameworks': ['styled-components', 'emotion', 'tailwind', 'bootstrap']
                }
            },
            'external_integrations': {
                'social-media': {
                    'keywords': ['social', 'facebook', 'twitter', 'instagram', 'linkedin', 'share'],
                    'directories': ['social', 'share'],
                    'files': ['social', 'share', 'facebook', 'twitter'],
                    'frameworks': ['facebook-sdk', 'twitter-api']
                },
                'analytics': {
                    'keywords': ['analytics', 'tracking', 'metrics', 'google', 'gtag', 'mixpanel'],
                    'directories': ['analytics', 'tracking'],
                    'files': ['analytics', 'tracking', 'metrics'],
                    'frameworks': ['google-analytics', 'mixpanel', 'segment']
                },
                'maps': {
                    'keywords': ['map', 'location', 'gps', 'geocoding', 'maps'],
                    'directories': ['map', 'location'],
                    'files': ['map', 'location', 'gps'],
                    'frameworks': ['google-maps', 'mapbox', 'leaflet']
                }
            },
            'data_management': {
                'validation': {
                    'keywords': ['validation', 'validator', 'schema', 'joi', 'yup', 'zod'],
                    'directories': ['validation', 'validator'],
                    'files': ['validation', 'validator', 'schema'],
                    'frameworks': ['joi', 'yup', 'zod', 'ajv']
                },
                'transformation': {
                    'keywords': ['transform', 'serialize', 'deserialize', 'mapper', 'converter'],
                    'directories': ['transform', 'mapper'],
                    'files': ['transform', 'mapper', 'converter', 'serializer'],
                    'frameworks': []
                }
            },
            'operational': {
                'logging': {
                    'keywords': ['log', 'logger', 'logging', 'winston', 'debug'],
                    'directories': ['log', 'logs', 'logging'],
                    'files': ['log', 'logger', 'logging'],
                    'frameworks': ['winston', 'bunyan', 'pino']
                },
                'monitoring': {
                    'keywords': ['monitor', 'health', 'metrics', 'prometheus', 'sentry'],
                    'directories': ['monitor', 'health', 'metrics'],
                    'files': ['monitor', 'health', 'metrics'],
                    'frameworks': ['prometheus', 'sentry', 'newrelic']
                },
                'deployment': {
                    'keywords': ['deploy', 'docker', 'kubernetes', 'ci', 'cd', 'build'],
                    'directories': ['deploy', 'deployment', '.github', 'ci'],
                    'files': ['dockerfile', 'docker-compose', 'ci', 'deploy'],
                    'frameworks': ['docker', 'kubernetes']
                }
            }
        }
    
    def discover_themes(self, project_path: Path) -> Dict[str, Any]:
        """Discover themes from project structure analysis."""
        try:
            # Analyze project structure
            logger.info(f"Analyzing project structure at {project_path}")
            structure = self.file_analyzer.analyze_project_structure(project_path)
            
            # Discover themes
            discovered_themes = self._identify_themes(structure)
            
            # Build theme relationships
            theme_relationships = self._build_theme_relationships(discovered_themes, structure)
            
            # Create theme definitions
            themes = self._create_theme_definitions(discovered_themes, theme_relationships, structure, project_path)
            
            return {
                'themes': themes,
                'metadata': {
                    'discovery_method': 'automatic',
                    'total_files': len(structure.get('files', [])),
                    'total_directories': len(structure.get('directories', {})),
                    'languages': structure.get('languages', []),
                    'frameworks': structure.get('frameworks', [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error discovering themes: {e}")
            return {'themes': {}, 'metadata': {}}
    
    def _identify_themes(self, structure: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Identify themes based on structure analysis."""
        discovered_themes = {}
        
        # Score each theme category
        for category_name, category_themes in self.theme_categories.items():
            for theme_name, theme_config in category_themes.items():
                score = self._calculate_theme_score(theme_config, structure)
                
                if score > 0.05:  # Very sensitive detection threshold
                    discovered_themes[theme_name] = {
                        'category': category_name,
                        'score': score,
                        'config': theme_config,
                        'evidence': self._collect_theme_evidence(theme_config, structure)
                    }
        
        # Discover custom themes from directory structure
        custom_themes = self._discover_custom_themes(structure)
        discovered_themes.update(custom_themes)
        
        return discovered_themes
    
    def _calculate_theme_score(self, theme_config: Dict[str, Any], structure: Dict[str, Any]) -> float:
        """Calculate relevance score for a theme."""
        score = 0.0
        total_weight = 0.0
        
        # Directory matching (high weight)
        directory_weight = 0.4
        directory_matches = 0
        for directory in structure.get('directories', {}):
            for theme_dir in theme_config.get('directories', []):
                if theme_dir.lower() in directory.lower():
                    directory_matches += 1
        
        if theme_config.get('directories'):
            score += (directory_matches / len(theme_config['directories'])) * directory_weight
        total_weight += directory_weight
        
        # Keyword matching (medium weight)
        keyword_weight = 0.3
        keyword_matches = 0
        keywords = structure.get('keywords', {})
        for keyword in theme_config.get('keywords', []):
            if keyword.lower() in keywords:
                keyword_matches += keywords[keyword.lower()]
        
        if theme_config.get('keywords'):
            normalized_keyword_score = min(keyword_matches / (len(theme_config['keywords']) * 2), 1.0)
            score += normalized_keyword_score * keyword_weight
        total_weight += keyword_weight
        
        # Framework matching (high weight)
        framework_weight = 0.3
        framework_matches = 0
        frameworks = set(fw.lower() for fw in structure.get('frameworks', []))
        for framework in theme_config.get('frameworks', []):
            if framework.lower() in frameworks:
                framework_matches += 1
        
        if theme_config.get('frameworks'):
            score += (framework_matches / len(theme_config['frameworks'])) * framework_weight
        total_weight += framework_weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _collect_theme_evidence(self, theme_config: Dict[str, Any], structure: Dict[str, Any]) -> Dict[str, List[str]]:
        """Collect evidence for theme detection."""
        evidence = {
            'directories': [],
            'files': [],
            'keywords': [],
            'frameworks': []
        }
        
        # Collect directory evidence
        for directory in structure.get('directories', {}):
            for theme_dir in theme_config.get('directories', []):
                if theme_dir.lower() in directory.lower():
                    evidence['directories'].append(directory)
        
        # Collect file evidence
        for file_info in structure.get('files', []):
            file_name = file_info.get('name', '').lower()
            for theme_file in theme_config.get('files', []):
                if theme_file.lower() in file_name:
                    evidence['files'].append(file_info.get('path', ''))
        
        # Collect keyword evidence
        keywords = structure.get('keywords', {})
        for keyword in theme_config.get('keywords', []):
            if keyword.lower() in keywords:
                evidence['keywords'].append(keyword)
        
        # Collect framework evidence
        frameworks = structure.get('frameworks', [])
        for framework in theme_config.get('frameworks', []):
            if framework.lower() in [fw.lower() for fw in frameworks]:
                evidence['frameworks'].append(framework)
        
        return evidence
    
    def _discover_custom_themes(self, structure: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Discover custom themes from project-specific patterns."""
        custom_themes = {}
        
        # Analyze directory structure for custom themes
        directories = structure.get('directories', {})
        
        # Look for domain-specific directories
        domain_keywords = Counter()
        for directory in directories:
            parts = directory.split('/')
            for part in parts:
                if len(part) > 3 and part.lower() not in [
                    'src', 'lib', 'app', 'test', 'tests', 'spec', 'build', 'dist'
                ]:
                    domain_keywords[part.lower()] += 1
        
        # Create themes for frequent domain keywords
        for keyword, count in domain_keywords.most_common(10):
            if count >= 2:  # Must appear in multiple places
                custom_themes[f"custom-{keyword}"] = {
                    'category': 'custom',
                    'score': min(count / 5.0, 1.0),
                    'config': {
                        'keywords': [keyword],
                        'directories': [keyword],
                        'files': [keyword],
                        'frameworks': []
                    },
                    'evidence': {
                        'directories': [d for d in directories if keyword in d.lower()],
                        'files': [],
                        'keywords': [keyword],
                        'frameworks': []
                    }
                }
        
        return custom_themes
    
    def _build_theme_relationships(self, themes: Dict[str, Any], structure: Dict[str, Any]) -> Dict[str, List[str]]:
        """Build relationships between themes based on shared files and imports."""
        relationships = defaultdict(list)
        
        # Analyze import relationships
        imports = structure.get('imports', {})
        theme_files = {}
        
        # Map files to themes
        for theme_name, theme_data in themes.items():
            theme_files[theme_name] = []
            for file_path in theme_data['evidence']['files']:
                theme_files[theme_name].append(file_path)
        
        # Find relationships through imports
        for file_path, file_imports in imports.items():
            file_themes = []
            for theme_name, files in theme_files.items():
                if any(theme_file in file_path for theme_file in files):
                    file_themes.append(theme_name)
            
            # If file belongs to multiple themes, they're related
            for i, theme1 in enumerate(file_themes):
                for theme2 in file_themes[i+1:]:
                    if theme2 not in relationships[theme1]:
                        relationships[theme1].append(theme2)
                    if theme1 not in relationships[theme2]:
                        relationships[theme2].append(theme1)
        
        return dict(relationships)
    
    def _create_theme_definitions(self, themes: Dict[str, Any], relationships: Dict[str, List[str]], 
                                structure: Dict[str, Any], project_path: Path) -> Dict[str, Dict[str, Any]]:
        """Create final theme definitions."""
        theme_definitions = {}
        
        for theme_name, theme_data in themes.items():
            # Collect all files for this theme
            theme_files = []
            theme_paths = []
            
            # Add files based on evidence
            for file_info in structure.get('files', []):
                file_path = file_info.get('path', '')
                file_name = file_info.get('name', '').lower()
                file_dir = file_info.get('directory', '').lower()
                
                # Check if file belongs to this theme
                belongs_to_theme = False
                
                # Check directory evidence
                for evidence_dir in theme_data['evidence']['directories']:
                    if evidence_dir.lower() in file_dir:
                        belongs_to_theme = True
                        break
                
                # Check file name evidence
                if not belongs_to_theme:
                    for keyword in theme_data['config']['keywords']:
                        if keyword.lower() in file_name:
                            belongs_to_theme = True
                            break
                
                if belongs_to_theme:
                    theme_files.append(file_path)
                    # Extract unique paths
                    path_parts = file_path.split('/')
                    if len(path_parts) > 1:
                        dir_path = '/'.join(path_parts[:-1])
                        if dir_path not in theme_paths:
                            theme_paths.append(dir_path)
            
            # Create theme definition
            theme_definitions[theme_name] = {
                'theme': theme_name,
                'category': theme_data['category'],
                'description': self._generate_theme_description(theme_name, theme_data),
                'confidence': theme_data['score'],
                'paths': theme_paths,
                'files': theme_files,
                'linkedThemes': relationships.get(theme_name, []),
                'sharedFiles': self._identify_shared_files(theme_name, themes, structure),
                'frameworks': theme_data['evidence']['frameworks'],
                'keywords': theme_data['evidence']['keywords']
            }
        
        return theme_definitions
    
    def _generate_theme_description(self, theme_name: str, theme_data: Dict[str, Any]) -> str:
        """Generate a description for the theme."""
        category = theme_data['category']
        evidence = theme_data['evidence']
        
        if category == 'custom':
            return f"Custom theme identified from project structure: {theme_name}"
        
        # Generate description based on evidence
        desc_parts = []
        
        if evidence['frameworks']:
            desc_parts.append(f"Uses {', '.join(evidence['frameworks'])}")
        
        if evidence['directories']:
            desc_parts.append(f"Located in {', '.join(evidence['directories'][:3])}")
        
        if evidence['keywords']:
            key_keywords = [k for k in evidence['keywords'] if k in theme_data['config']['keywords']]
            if key_keywords:
                desc_parts.append(f"Handles {', '.join(key_keywords[:3])}")
        
        base_descriptions = {
            'authentication': 'Manages user authentication and authorization',
            'payment': 'Handles payment processing and billing',
            'user-management': 'Manages user profiles and account settings',
            'database': 'Database models and data access layer',
            'api': 'API endpoints and service layer',
            'components': 'UI components and reusable elements',
            'pages': 'Application pages and views',
            'testing': 'Test files and testing utilities'
        }
        
        base_desc = base_descriptions.get(theme_name, f"{theme_name.replace('-', ' ').title()} functionality")
        
        if desc_parts:
            return f"{base_desc}. {'. '.join(desc_parts)}."
        else:
            return base_desc
    
    def _identify_shared_files(self, theme_name: str, themes: Dict[str, Any], structure: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Identify files shared between themes."""
        shared_files = {}
        current_theme_files = set(themes[theme_name]['evidence']['files'])
        
        for other_theme_name, other_theme_data in themes.items():
            if other_theme_name == theme_name:
                continue
            
            other_theme_files = set(other_theme_data['evidence']['files'])
            shared = current_theme_files.intersection(other_theme_files)
            
            for shared_file in shared:
                if shared_file not in shared_files:
                    shared_files[shared_file] = {
                        'sharedWith': [other_theme_name],
                        'description': f'Shared between {theme_name} and {other_theme_name}'
                    }
                else:
                    shared_files[shared_file]['sharedWith'].append(other_theme_name)
                    shared_files[shared_file]['description'] = f'Shared between multiple themes'
        
        return shared_files