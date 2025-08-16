"""
Theme context operations.

Handles theme context loading, management, and contextual information retrieval.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base_operations import BaseThemeOperations

logger = logging.getLogger(__name__)


class ThemeContextOperations(BaseThemeOperations):
    """Handles theme context loading and management."""
    
    async def get_theme_context(self, project_path: Path, primary_theme: str,
                               context_mode: str = "theme-focused") -> str:
        """Get context for themes based on context mode."""
        try:
            project_path = Path(project_path)
            themes_dir = self.get_themes_directory(project_path)
            
            # Load primary theme
            primary_theme_file = themes_dir / f"{primary_theme}.json"
            if not primary_theme_file.exists():
                return f"Primary theme '{primary_theme}' not found."
            
            primary_theme_data = json.loads(primary_theme_file.read_text())
            context = {
                "contextMode": context_mode,
                "primaryTheme": primary_theme,
                "themes": [primary_theme_data],
                "files": primary_theme_data.get("files", []),
                "paths": primary_theme_data.get("paths", [])
            }
            
            if context_mode == "theme-expanded":
                # Load linked themes
                linked_themes = primary_theme_data.get("linkedThemes", [])
                for linked_theme in linked_themes:
                    linked_theme_file = themes_dir / f"{linked_theme}.json"
                    if linked_theme_file.exists():
                        linked_theme_data = json.loads(linked_theme_file.read_text())
                        context["themes"].append(linked_theme_data)
                        context["files"].extend(linked_theme_data.get("files", []))
                        context["paths"].extend(linked_theme_data.get("paths", []))
                
                context["loadedThemes"] = [primary_theme] + linked_themes
            
            elif context_mode == "project-wide":
                # Load all themes
                themes_index = themes_dir / "themes.json"
                if themes_index.exists():
                    all_themes = json.loads(themes_index.read_text())
                    context["loadedThemes"] = list(all_themes.keys())
                    
                    for theme_name in all_themes.keys():
                        if theme_name != primary_theme:
                            theme_file = themes_dir / f"{theme_name}.json"
                            if theme_file.exists():
                                theme_data = json.loads(theme_file.read_text())
                                context["themes"].append(theme_data)
                                context["files"].extend(theme_data.get("files", []))
                                context["paths"].extend(theme_data.get("paths", []))
            
            else:  # theme-focused
                context["loadedThemes"] = [primary_theme]
            
            # Remove duplicates
            context["files"] = list(set(context["files"]))
            context["paths"] = list(set(context["paths"]))
            
            return f"Theme context loaded:\n\n{json.dumps(context, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error getting theme context: {e}")
            return f"Error getting theme context: {str(e)}"
    
    async def _extract_theme_context(self, theme_name: str, theme_data: Dict[str, Any],
                                   project_path: Path, include_files: bool, include_flows: bool,
                                   max_files: int) -> Dict[str, Any]:
        """Extract contextual information from a theme."""
        context = {
            "name": theme_name,
            "description": theme_data.get("metadata", {}).get("description", ""),
            "keywords": theme_data.get("keywords", []),
            "patterns": theme_data.get("patterns", []),
            "files": [],
            "flows": [],
            "priority": theme_data.get("context", {}).get("priority", 1.0),
            "scope": theme_data.get("context", {}).get("scope", "project"),
            "statistics": theme_data.get("statistics", {}),
            "file_samples": []
        }
        
        # Get file information if requested
        if include_files:
            files = theme_data.get("files", [])
            context["files"] = files[:max_files] if max_files else files
            
            # Get file samples for context
            context["file_samples"] = await self._get_file_samples(
                project_path, context["files"][:5]  # Sample first 5 files
            )
        
        # Get flow information if requested
        if include_flows:
            context["flows"] = theme_data.get("flows", [])
        
        return context
    
    async def _get_file_samples(self, project_path: Path, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Get sample content from theme files."""
        samples = []
        
        for file_path in file_paths:
            try:
                full_path = project_path / file_path
                if full_path.exists() and full_path.is_file():
                    # Read file content (limited for context)
                    file_size = full_path.stat().st_size
                    if file_size > 10240:  # Skip files larger than 10KB
                        continue
                    
                    try:
                        content = full_path.read_text(encoding='utf-8', errors='ignore')
                        # Get first few lines as sample
                        lines = content.split('\n')[:10]
                        sample_content = '\n'.join(lines)
                        
                        samples.append({
                            "file_path": file_path,
                            "file_type": full_path.suffix,
                            "size_bytes": file_size,
                            "sample_content": sample_content[:500],  # First 500 characters
                            "line_count": len(content.split('\n'))
                        })
                    except Exception:
                        # If can't read as text, just include metadata
                        samples.append({
                            "file_path": file_path,
                            "file_type": full_path.suffix,
                            "size_bytes": file_size,
                            "sample_content": "[Binary or unreadable content]",
                            "line_count": 0
                        })
            except Exception as e:
                logger.debug(f"Error sampling file {file_path}: {e}")
        
        return samples
    
    async def _find_theme_relationships(self, themes: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find relationships between themes."""
        relationships = []
        theme_names = list(themes.keys())
        
        for i, theme1_name in enumerate(theme_names):
            for theme2_name in theme_names[i+1:]:
                theme1 = themes[theme1_name]
                theme2 = themes[theme2_name]
                
                # Find keyword overlaps
                keywords1 = set(theme1["keywords"])
                keywords2 = set(theme2["keywords"])
                keyword_overlap = keywords1.intersection(keywords2)
                
                # Find file overlaps
                files1 = set(theme1["files"])
                files2 = set(theme2["files"])
                file_overlap = files1.intersection(files2)
                
                # Find flow overlaps
                flows1 = set(theme1["flows"])
                flows2 = set(theme2["flows"])
                flow_overlap = flows1.intersection(flows2)
                
                # Calculate relationship strength
                total_overlap = len(keyword_overlap) + len(file_overlap) + len(flow_overlap)
                
                if total_overlap > 0:
                    relationship_strength = self._calculate_relationship_strength(
                        keyword_overlap, file_overlap, flow_overlap,
                        len(keywords1) + len(keywords2),
                        len(files1) + len(files2),
                        len(flows1) + len(flows2)
                    )
                    
                    relationships.append({
                        "theme1": theme1_name,
                        "theme2": theme2_name,
                        "strength": relationship_strength,
                        "keyword_overlap": list(keyword_overlap),
                        "file_overlap": list(file_overlap),
                        "flow_overlap": list(flow_overlap),
                        "total_overlaps": total_overlap
                    })
        
        # Sort by relationship strength
        relationships.sort(key=lambda r: r["strength"], reverse=True)
        return relationships
    
    def _calculate_relationship_strength(self, keyword_overlap: set, file_overlap: set,
                                       flow_overlap: set, total_keywords: int,
                                       total_files: int, total_flows: int) -> float:
        """Calculate the strength of relationship between two themes."""
        # Weights for different types of overlaps
        keyword_weight = 0.4
        file_weight = 0.4
        flow_weight = 0.2
        
        # Calculate normalized overlap scores
        keyword_score = len(keyword_overlap) / max(total_keywords, 1) if total_keywords > 0 else 0
        file_score = len(file_overlap) / max(total_files, 1) if total_files > 0 else 0
        flow_score = len(flow_overlap) / max(total_flows, 1) if total_flows > 0 else 0
        
        # Weighted average
        strength = (
            keyword_score * keyword_weight +
            file_score * file_weight +
            flow_score * flow_weight
        )
        
        return round(strength * 100, 2)  # Convert to percentage
    
    def _format_context_report(self, context_data: Dict[str, Any], theme_names: List[str],
                             include_files: bool, include_flows: bool) -> str:
        """Format the context data into a readable report."""
        result = f"Theme Context Report\n"
        result += f"{'='*50}\n\n"
        
        # Summary
        stats = context_data["statistics"]
        result += f"Context Summary:\n"
        result += f"- Themes analyzed: {stats['total_themes']}\n"
        result += f"- Combined keywords: {stats['total_keywords']}\n"
        if include_files:
            result += f"- Combined files: {stats['total_files']}\n"
        if include_flows:
            result += f"- Combined flows: {stats['total_flows']}\n"
        result += f"- Theme relationships: {len(context_data['relationships'])}\n\n"
        
        # Individual theme details
        result += "Theme Details:\n"
        result += "-" * 30 + "\n"
        
        for theme_name in theme_names:
            if theme_name not in context_data["themes"]:
                result += f"⚠️ Theme '{theme_name}' not found\n\n"
                continue
            
            theme = context_data["themes"][theme_name]
            result += f"\n📁 {theme_name}\n"
            result += f"   Description: {theme['description']}\n"
            result += f"   Priority: {theme['priority']}\n"
            result += f"   Scope: {theme['scope']}\n"
            result += f"   Keywords ({len(theme['keywords'])}): {', '.join(theme['keywords'][:10])}"
            if len(theme['keywords']) > 10:
                result += f" (+{len(theme['keywords'])-10} more)"
            result += "\n"
            
            if include_files and theme['files']:
                result += f"   Files ({len(theme['files'])}): "
                result += f"{', '.join([Path(f).name for f in theme['files'][:5]])}"
                if len(theme['files']) > 5:
                    result += f" (+{len(theme['files'])-5} more)"
                result += "\n"
            
            if include_flows and theme['flows']:
                result += f"   Flows ({len(theme['flows'])}): {', '.join(theme['flows'][:5])}"
                if len(theme['flows']) > 5:
                    result += f" (+{len(theme['flows'])-5} more)"
                result += "\n"
        
        # Theme relationships
        if context_data["relationships"]:
            result += f"\nTheme Relationships:\n"
            result += "-" * 30 + "\n"
            
            for rel in context_data["relationships"][:5]:  # Top 5 relationships
                result += f"\n🔗 {rel['theme1']} ↔ {rel['theme2']}\n"
                result += f"   Relationship strength: {rel['strength']}%\n"
                
                if rel['keyword_overlap']:
                    result += f"   Shared keywords: {', '.join(rel['keyword_overlap'][:3])}"
                    if len(rel['keyword_overlap']) > 3:
                        result += f" (+{len(rel['keyword_overlap'])-3} more)"
                    result += "\n"
                
                if rel['file_overlap']:
                    result += f"   Shared files: {len(rel['file_overlap'])} files\n"
                
                if rel['flow_overlap']:
                    result += f"   Shared flows: {', '.join(rel['flow_overlap'][:2])}"
                    if len(rel['flow_overlap']) > 2:
                        result += f" (+{len(rel['flow_overlap'])-2} more)"
                    result += "\n"
        
        # Combined resources
        if include_files and context_data["combined_files"]:
            result += f"\nAll Related Files ({len(context_data['combined_files'])}):\n"
            result += "-" * 30 + "\n"
            for file_path in context_data["combined_files"][:15]:
                result += f"  - {file_path}\n"
            if len(context_data["combined_files"]) > 15:
                result += f"  ... and {len(context_data['combined_files'])-15} more files\n"
        
        if include_flows and context_data["combined_flows"]:
            result += f"\nAll Related Flows ({len(context_data['combined_flows'])}):\n"
            result += "-" * 30 + "\n"
            for flow in context_data["combined_flows"]:
                result += f"  - {flow}\n"
        
        return result