import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..db_manager import DatabaseManager

class DependencyAnalysis:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
          
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