import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, deque
from ..db_manager import DatabaseManager

class ImpactAnalysis:
    def __init__(self, db_manager: DatabaseManager, modification_logging=None, dependency_analysis=None, file_discovery=None):
        self.db = db_manager
        self.modification_logging = modification_logging
        self.dependency_analysis = dependency_analysis
        self.file_discovery = file_discovery
          
    def get_impact_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        Get impact analysis for file changes.
        
        Args:
            file_path: File path to analyze
            
        Returns:
            Impact analysis with affected files and components
        """
        # Get recent modifications for this file
        modifications = []
        if self.modification_logging:
            modifications = self.modification_logging.get_file_modifications(file_path=file_path, days=30)
        
        # Analyze dependencies
        dependencies = {"imports": [], "dependencies": []}
        if self.dependency_analysis:
            dependencies = self.dependency_analysis.analyze_file_dependencies(file_path)
        
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
        """Get themes that reference this file path by querying file metadata."""
        try:
            # Query file_metadata table to find themes associated with this file
            query = """
                SELECT theme_associations
                FROM file_metadata
                WHERE file_path = ?
            """
            
            results = self.db.execute_query(query, (file_path,))
            themes = []
            if results and len(results) > 0:
                theme_associations_str = results[0]["theme_associations"]
                if theme_associations_str:
                    import json
                    theme_associations = json.loads(theme_associations_str)
                    themes = theme_associations if isinstance(theme_associations, list) else []
            
            return themes
            
        except Exception as e:
            self.db.logger.error(f"Error getting themes for file {file_path}: {e}")
            return []
    
    def _get_themes_for_file_with_history(self, file_path: str) -> Dict[str, List[str]]:
        """
        Get both current and historical themes for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with 'current' and 'historical' theme lists
        """
        try:
            # Get current themes
            current_themes = self._get_themes_for_file(file_path)
            
            # Get historical themes from modifications log
            historical_themes = []
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
                theme_data = row["theme_data"]
                if theme_data:
                    try:
                        import json
                        theme_list = json.loads(theme_data) if isinstance(theme_data, str) else theme_data
                        if isinstance(theme_list, list):
                            historical_themes.extend(theme_list)
                    except (json.JSONDecodeError, TypeError):
                        continue
            
            return {
                "current": current_themes,
                "historical": list(set(historical_themes)),
                "all_unique": list(set(current_themes + historical_themes))
            }
            
        except Exception as e:
            self.db.logger.error(f"Error getting themes with history for file {file_path}: {e}")
            return {"current": [], "historical": [], "all_unique": []}
    
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
            project_files = {}
            if self.file_discovery:
                project_files = self.file_discovery.discover_project_files(project_path)
            else:
                return self._empty_relationship_mapping()
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
                        analysis = {}
                        if self.dependency_analysis:
                            analysis = self.dependency_analysis.analyze_file_dependencies(str(full_path))
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
        # Get files with high modification frequency using relevance-based ordering
        frequent_modifications = self.db.execute_query("""
            SELECT file_path, COUNT(*) as mod_count, 
                   MAX(timestamp) as last_modified,
                   COUNT(CASE WHEN session_id IS NOT NULL THEN 1 END) as session_modifications
            FROM file_modifications
            GROUP BY file_path
            ORDER BY 
                session_modifications DESC,
                mod_count DESC,
                last_modified DESC
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
    