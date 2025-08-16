"""
Flow dependency analysis operations.

Handles cross-flow dependency analysis and loading order optimization.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

from .base_operations import BaseFlowOperations
from ...utils.project_paths import get_flows_path

logger = logging.getLogger(__name__)


class FlowDependencyAnalyzer(BaseFlowOperations):
    """Analyzes cross-flow dependencies and determines optimal loading order."""
    
    async def analyze_flow_dependencies(self, project_path: Path, flow_ids: List[str],
                                       include_indirect: bool = True) -> str:
        """Analyze cross-flow dependencies and recommend loading order."""
        try:
            flow_dir = get_flows_path(project_path, self.config_manager)
            flow_index_path = flow_dir / "flow-index.json"
            
            if not flow_index_path.exists():
                return "No flow index found. Create flow index first."
            
            flow_index = json.loads(flow_index_path.read_text())
            cross_flow_deps = flow_index.get("crossFlowDependencies", [])
            
            # Build dependency graph
            dependency_graph = {}
            reverse_deps = {}
            
            for dep in cross_flow_deps:
                from_flow = dep["from_flow"]
                to_flow = dep["to_flow"]
                dep_type = dep.get("dependency_type", "requires")
                
                if from_flow not in dependency_graph:
                    dependency_graph[from_flow] = []
                dependency_graph[from_flow].append({
                    "flow": to_flow,
                    "type": dep_type,
                    "description": dep.get("description", "")
                })
                
                if to_flow not in reverse_deps:
                    reverse_deps[to_flow] = []
                reverse_deps[to_flow].append({
                    "flow": from_flow,
                    "type": dep_type,
                    "description": dep.get("description", "")
                })
            
            # Analyze dependencies for requested flows
            analysis_results = {}
            
            for flow_id in flow_ids:
                direct_deps = dependency_graph.get(flow_id, [])
                depends_on = reverse_deps.get(flow_id, [])
                
                analysis = {
                    "flow_id": flow_id,
                    "direct_dependencies": direct_deps,
                    "depended_on_by": depends_on,
                    "dependency_score": len(direct_deps) + len(depends_on),
                    "loading_priority": "normal"
                }
                
                # Calculate indirect dependencies if requested
                if include_indirect:
                    indirect_deps = await self._calculate_indirect_dependencies(
                        flow_id, dependency_graph, set()
                    )
                    analysis["indirect_dependencies"] = indirect_deps
                    analysis["total_dependency_score"] = analysis["dependency_score"] + len(indirect_deps)
                
                # Determine loading priority
                total_score = analysis.get("total_dependency_score", analysis["dependency_score"])
                if total_score == 0:
                    analysis["loading_priority"] = "independent"
                elif total_score <= 2:
                    analysis["loading_priority"] = "low_dependency"
                elif total_score <= 5:
                    analysis["loading_priority"] = "moderate_dependency"
                else:
                    analysis["loading_priority"] = "high_dependency"
                
                analysis_results[flow_id] = analysis
            
            # Generate optimal loading order
            loading_order = await self._generate_optimal_loading_order(analysis_results, dependency_graph)
            
            # Get database insights if available
            db_insights = ""
            if self.theme_flow_queries:
                try:
                    db_deps = await self.theme_flow_queries.get_cross_flow_dependencies_for_flows(flow_ids)
                    if db_deps:
                        db_insights = f"\nDatabase insights: {len(db_deps)} additional dependencies found in usage patterns."
                except Exception as e:
                    db_insights = f"\nDatabase insights unavailable: {str(e)}"
            
            # Format results
            result = f"Flow dependency analysis for {len(flow_ids)} flows:\n\n"
            
            for flow_id in flow_ids:
                analysis = analysis_results[flow_id]
                result += f"Flow: {flow_id}\n"
                result += f"  Priority: {analysis['loading_priority']}\n"
                result += f"  Direct dependencies: {len(analysis['direct_dependencies'])}\n"
                result += f"  Depended on by: {len(analysis['depended_on_by'])}\n"
                
                if include_indirect:
                    result += f"  Indirect dependencies: {len(analysis.get('indirect_dependencies', []))}\n"
                    result += f"  Total dependency score: {analysis.get('total_dependency_score', 0)}\n"
                
                if analysis['direct_dependencies']:
                    result += "  Direct deps: " + ", ".join([d['flow'] for d in analysis['direct_dependencies']]) + "\n"
                
                result += "\n"
            
            result += f"Recommended loading order: {' → '.join(loading_order)}\n"
            result += db_insights
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing flow dependencies: {e}")
            return f"Error analyzing flow dependencies: {str(e)}"
    
    async def _calculate_indirect_dependencies(self, flow_id: str, 
                                             dependency_graph: Dict[str, List[Dict[str, Any]]],
                                             visited: Set[str]) -> List[str]:
        """Calculate indirect dependencies recursively."""
        if flow_id in visited:
            return []
        
        visited.add(flow_id)
        indirect_deps = []
        
        direct_deps = dependency_graph.get(flow_id, [])
        for dep in direct_deps:
            dep_flow = dep["flow"]
            indirect_deps.append(dep_flow)
            
            # Recurse for indirect dependencies
            further_deps = await self._calculate_indirect_dependencies(
                dep_flow, dependency_graph, visited.copy()
            )
            indirect_deps.extend(further_deps)
        
        return list(set(indirect_deps))
    
    async def _generate_optimal_loading_order(self, analysis_results: Dict[str, Any],
                                            dependency_graph: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Generate optimal loading order based on dependency analysis."""
        # Topological sort for dependency-aware loading order
        in_degree = {}
        flow_ids = list(analysis_results.keys())
        
        # Initialize in-degree count
        for flow_id in flow_ids:
            in_degree[flow_id] = 0
        
        # Calculate in-degrees
        for flow_id in flow_ids:
            for dep in dependency_graph.get(flow_id, []):
                if dep["flow"] in flow_ids:
                    in_degree[dep["flow"]] += 1
        
        # Topological sort
        queue = [flow_id for flow_id in flow_ids if in_degree[flow_id] == 0]
        loading_order = []
        
        while queue:
            # Sort queue by dependency score for consistent ordering
            queue.sort(key=lambda x: analysis_results[x].get("total_dependency_score", 0))
            flow_id = queue.pop(0)
            loading_order.append(flow_id)
            
            # Update in-degrees for dependent flows
            for dep in dependency_graph.get(flow_id, []):
                if dep["flow"] in flow_ids:
                    in_degree[dep["flow"]] -= 1
                    if in_degree[dep["flow"]] == 0:
                        queue.append(dep["flow"])
        
        return loading_order