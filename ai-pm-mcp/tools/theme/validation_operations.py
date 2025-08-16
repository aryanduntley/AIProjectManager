"""
Theme validation operations.

Handles theme validation, consistency checking, and integrity verification.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .base_operations import BaseThemeOperations

logger = logging.getLogger(__name__)


class ThemeValidationOperations(BaseThemeOperations):
    """Handles theme validation and consistency checking."""
    
    async def validate_themes(self, project_path: Path, specific_theme: str = None) -> str:
        """Validate theme consistency and detect issues."""
        try:
            project_path = Path(project_path)
            themes_dir = self.get_themes_directory(project_path)
            themes_index = themes_dir / "themes.json"
            
            if not themes_index.exists():
                return "No themes found to validate."
            
            validation_results = {
                "valid": True,
                "issues": [],
                "warnings": [],
                "theme_count": 0,
                "file_coverage": {}
            }
            
            themes_data = json.loads(themes_index.read_text())
            themes_to_check = [specific_theme] if specific_theme else list(themes_data.keys())
            
            for theme_name in themes_to_check:
                theme_file = themes_dir / f"{theme_name}.json"
                if not theme_file.exists():
                    validation_results["issues"].append(f"Theme file missing: {theme_name}.json")
                    validation_results["valid"] = False
                    continue
                
                try:
                    theme_data = json.loads(theme_file.read_text())
                    validation_results["theme_count"] += 1
                    
                    # Check required fields
                    required_fields = ["theme", "description", "paths", "files"]
                    for field in required_fields:
                        if field not in theme_data:
                            validation_results["issues"].append(f"Theme {theme_name}: Missing required field '{field}'")
                            validation_results["valid"] = False
                    
                    # Check file existence
                    missing_files = []
                    for file_path in theme_data.get("files", []):
                        full_path = project_path / file_path
                        if not full_path.exists():
                            missing_files.append(file_path)
                    
                    if missing_files:
                        validation_results["warnings"].append(f"Theme {theme_name}: Files not found: {missing_files}")
                    
                    # Check path existence
                    missing_paths = []
                    for path in theme_data.get("paths", []):
                        full_path = project_path / path
                        if not full_path.exists():
                            missing_paths.append(path)
                    
                    if missing_paths:
                        validation_results["warnings"].append(f"Theme {theme_name}: Paths not found: {missing_paths}")
                    
                    # Check linked themes
                    invalid_links = []
                    for linked_theme in theme_data.get("linkedThemes", []):
                        linked_file = themes_dir / f"{linked_theme}.json"
                        if not linked_file.exists():
                            invalid_links.append(linked_theme)
                    
                    if invalid_links:
                        validation_results["issues"].append(f"Theme {theme_name}: Invalid linked themes: {invalid_links}")
                        validation_results["valid"] = False
                    
                except json.JSONDecodeError:
                    validation_results["issues"].append(f"Theme {theme_name}: Invalid JSON format")
                    validation_results["valid"] = False
            
            status = "VALID" if validation_results["valid"] else "INVALID"
            return f"Theme validation result: {status}\n\n{json.dumps(validation_results, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error validating themes: {e}")
            return f"Error validating themes: {str(e)}"
    
    async def _validate_themes_index(self, themes_index: Dict[str, Any], 
                                   validation_results: Dict[str, Any]):
        """Validate the themes index structure."""
        # Check required fields
        if "metadata" not in themes_index:
            validation_results["errors"].append("Themes index missing metadata section")
        else:
            metadata = themes_index["metadata"]
            if "version" not in metadata:
                validation_results["warnings"].append("Themes index missing version")
            if "created" not in metadata:
                validation_results["warnings"].append("Themes index missing creation date")
        
        if "themes" not in themes_index:
            validation_results["errors"].append("Themes index missing themes section")
        
        # Check discovery information
        if "discovery" not in themes_index:
            validation_results["suggestions"].append("Consider adding discovery section to themes index")
        else:
            discovery = themes_index["discovery"]
            if not discovery.get("last_discovery"):
                validation_results["suggestions"].append("No recent theme discovery found - consider running discovery")
    
    async def _validate_theme_file(self, themes_dir: Path, theme_name: str, 
                                 theme_info: Dict[str, Any], project_path: Path,
                                 validation_results: Dict[str, Any], fix_issues: bool):
        """Validate an individual theme file."""
        theme_file_path = themes_dir / f"{theme_name}.json"
        
        # Check if file exists
        if not theme_file_path.exists():
            validation_results["errors"].append(f"Theme file missing: {theme_name}.json")
            return
        
        # Load and validate theme data
        try:
            theme_data = json.loads(theme_file_path.read_text())
        except json.JSONDecodeError as e:
            validation_results["errors"].append(f"Invalid JSON in theme {theme_name}: {str(e)}")
            return
        
        # Validate theme structure
        required_fields = ["metadata", "keywords", "patterns", "flows", "files", "context", "statistics"]
        for field in required_fields:
            if field not in theme_data:
                validation_results["warnings"].append(f"Theme {theme_name} missing field: {field}")
                
                # Fix if requested
                if fix_issues:
                    theme_data[field] = self._get_default_field_value(field)
                    validation_results["fixed_issues"].append(f"Added missing field '{field}' to theme {theme_name}")
        
        # Validate metadata
        if "metadata" in theme_data:
            metadata = theme_data["metadata"]
            if metadata.get("name") != theme_name:
                validation_results["warnings"].append(f"Theme {theme_name} metadata name mismatch")
                if fix_issues:
                    metadata["name"] = theme_name
                    validation_results["fixed_issues"].append(f"Fixed metadata name for theme {theme_name}")
        
        # Validate keywords
        keywords = theme_data.get("keywords", [])
        if not isinstance(keywords, list):
            validation_results["errors"].append(f"Theme {theme_name} keywords should be a list")
        elif len(keywords) == 0:
            validation_results["suggestions"].append(f"Theme {theme_name} has no keywords - consider adding some")
        
        # Validate patterns
        patterns = theme_data.get("patterns", [])
        if not isinstance(patterns, list):
            validation_results["errors"].append(f"Theme {theme_name} patterns should be a list")
        
        # Validate file references
        files = theme_data.get("files", [])
        if isinstance(files, list):
            missing_files = []
            for file_path in files[:10]:  # Check first 10 files for performance
                full_path = project_path / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
            
            if missing_files:
                validation_results["warnings"].append(
                    f"Theme {theme_name} references {len(missing_files)} missing files"
                )
                validation_results["files_checked"] += len(files)
        
        # Validate statistics
        statistics = theme_data.get("statistics", {})
        if isinstance(statistics, dict):
            file_count = statistics.get("file_count", 0)
            actual_file_count = len(files) if isinstance(files, list) else 0
            if file_count != actual_file_count:
                validation_results["warnings"].append(
                    f"Theme {theme_name} file count mismatch: {file_count} vs {actual_file_count}"
                )
                if fix_issues:
                    statistics["file_count"] = actual_file_count
                    validation_results["fixed_issues"].append(f"Fixed file count for theme {theme_name}")
        
        # Save fixes if any were made
        if fix_issues and validation_results["fixed_issues"]:
            theme_file_path.write_text(json.dumps(theme_data, indent=2))
    
    async def _check_orphaned_files(self, themes_dir: Path, themes: Dict[str, Any], 
                                  validation_results: Dict[str, Any]):
        """Check for orphaned theme files not referenced in the index."""
        # Get all theme files
        theme_files = set()
        for file_path in themes_dir.glob("*.json"):
            if file_path.name != "themes.json":  # Exclude the index file
                theme_files.add(file_path.stem)
        
        # Get indexed themes
        indexed_themes = set(themes.keys())
        
        # Find orphaned files
        orphaned_files = theme_files - indexed_themes
        if orphaned_files:
            validation_results["warnings"].append(
                f"Found {len(orphaned_files)} orphaned theme files: {', '.join(orphaned_files)}"
            )
    
    async def _check_duplicate_themes(self, themes: Dict[str, Any], 
                                    validation_results: Dict[str, Any]):
        """Check for duplicate themes based on keywords and patterns."""
        theme_fingerprints = {}
        
        for theme_name, theme_info in themes.items():
            # Create fingerprint based on description
            description = theme_info.get("description", "").lower().strip()
            if description in theme_fingerprints:
                validation_results["suggestions"].append(
                    f"Themes '{theme_name}' and '{theme_fingerprints[description]}' have similar descriptions"
                )
            else:
                theme_fingerprints[description] = theme_name
    
    async def _validate_file_references(self, project_path: Path, themes: Dict[str, Any],
                                      validation_results: Dict[str, Any]):
        """Validate that referenced files actually exist."""
        total_files_checked = 0
        missing_files = 0
        
        for theme_name in themes.keys():
            theme_data = self.load_theme(self.get_themes_directory(project_path), theme_name)
            if not theme_data:
                continue
            
            files = theme_data.get("files", [])
            if isinstance(files, list):
                for file_path in files:
                    total_files_checked += 1
                    full_path = project_path / file_path
                    if not full_path.exists():
                        missing_files += 1
        
        validation_results["files_checked"] = total_files_checked
        
        if missing_files > 0:
            validation_results["warnings"].append(
                f"Found {missing_files}/{total_files_checked} missing file references across all themes"
            )
    
    def _get_default_field_value(self, field: str) -> Any:
        """Get default value for a missing field."""
        defaults = {
            "metadata": {
                "name": "",
                "description": "",
                "created": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "category": "general"
            },
            "keywords": [],
            "patterns": [],
            "flows": [],
            "files": [],
            "context": {
                "priority": 1.0,
                "scope": "project",
                "relationships": []
            },
            "statistics": {
                "file_count": 0,
                "flow_count": 0,
                "usage_count": 0
            }
        }
        return defaults.get(field, {})
    
    def _generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a formatted validation report."""
        result = "Theme Validation Report\n"
        result += "=" * 50 + "\n\n"
        
        # Summary
        result += "Summary:\n"
        result += f"- Themes validated: {validation_results['themes_validated']}\n"
        result += f"- Files checked: {validation_results['files_checked']}\n"
        result += f"- Errors found: {len(validation_results['errors'])}\n"
        result += f"- Warnings: {len(validation_results['warnings'])}\n"
        result += f"- Suggestions: {len(validation_results['suggestions'])}\n"
        
        # Overall status
        if validation_results['errors']:
            result += f"\n🔴 Status: FAILED - {len(validation_results['errors'])} critical errors\n"
        elif validation_results['warnings']:
            result += f"\n🟡 Status: WARNINGS - {len(validation_results['warnings'])} issues found\n"
        else:
            result += f"\n🟢 Status: PASSED - No critical issues found\n"
        
        # Detailed issues
        if validation_results['errors']:
            result += f"\n❌ ERRORS ({len(validation_results['errors'])}):\n"
            for error in validation_results['errors']:
                result += f"  • {error}\n"
        
        if validation_results['warnings']:
            result += f"\n⚠️ WARNINGS ({len(validation_results['warnings'])}):\n"
            for warning in validation_results['warnings']:
                result += f"  • {warning}\n"
        
        if validation_results['suggestions']:
            result += f"\n💡 SUGGESTIONS ({len(validation_results['suggestions'])}):\n"
            for suggestion in validation_results['suggestions']:
                result += f"  • {suggestion}\n"
        
        return result