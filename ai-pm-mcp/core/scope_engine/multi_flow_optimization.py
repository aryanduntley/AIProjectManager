"""
Multi-Flow Optimization Module
Handles multi-flow optimization, utilities, and advanced context operations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from .compressed_context import ContextResult, ContextMode

# Import utilities from parent module paths
from ...utils.project_paths import get_themes_path

logger = logging.getLogger(__name__)


class MultiFlowOptimization:
    """Multi-flow optimization and utility operations."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties directly
        self.compressed_context_manager = parent_instance.compressed_context_manager
        self.theme_flow_queries = parent_instance.theme_flow_queries
        self.session_queries = parent_instance.session_queries
        self.file_metadata_queries = parent_instance.file_metadata_queries
    
    async def _analyze_cross_flow_dependencies_for_context(self, flow_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze cross-flow dependencies for context loading optimization."""
        dependencies = []
        
        try:
            if self.theme_flow_queries:
                for flow_id in flow_ids:
                    flow_dependencies = await self.theme_flow_queries.get_cross_flow_dependencies(flow_id)
                    
                    for dep in flow_dependencies:
                        if dep.get("to_flow") in flow_ids:  # Dependency within our loaded set
                            dependencies.append({
                                "from_flow": flow_id,
                                "to_flow": dep["to_flow"],
                                "dependency_type": dep.get("dependency_type", "requires"),
                                "description": dep.get("description", ""),
                                "impact": "context_loading"
                            })
        
        except Exception as e:
            logger.debug(f"Error analyzing cross-flow dependencies: {e}")
        
        return dependencies
    
    async def optimize_multi_flow_context_loading(self, project_path: Path,
                                                task_data: Dict[str, Any],
                                                session_id: Optional[str] = None) -> Dict[str, Any]:
        """Optimize context loading strategy for multi-flow scenarios."""
        optimization_result = {
            "strategy": "adaptive",
            "recommended_flows": [],
            "context_mode": "theme-focused",
            "loading_order": [],
            "performance_estimate": {},
            "recommendations": []
        }
        
        try:
            # Extract task information
            primary_theme = task_data.get("primaryTheme", "general")
            task_description = task_data.get("description", "")
            subtasks = task_data.get("subtasks", [])
            
            # Determine complexity level
            complexity_score = 0
            if len(subtasks) > 3:
                complexity_score += 2
            if len(task_description.split()) > 20:
                complexity_score += 1
            if any(keyword in task_description.lower() for keyword in 
                   ["integration", "system", "architecture", "database", "api"]):
                complexity_score += 2
            
            # Adjust strategy based on complexity
            if complexity_score >= 4:
                optimization_result["strategy"] = "comprehensive"
                optimization_result["context_mode"] = "project-wide"
                max_flows = 8
            elif complexity_score >= 2:
                optimization_result["strategy"] = "expanded"
                optimization_result["context_mode"] = "theme-expanded"
                max_flows = 5
            else:
                optimization_result["strategy"] = "focused"
                optimization_result["context_mode"] = "theme-focused"
                max_flows = 3
            
            # Get all relevant themes
            all_themes = {primary_theme}
            for subtask in subtasks:
                flow_refs = subtask.get("flowReferences", [])
                for flow_ref in flow_refs:
                    # Extract theme from flow reference if available
                    if self.theme_flow_queries:
                        flow_themes = await self.theme_flow_queries.get_themes_for_flow(
                            flow_ref.get("flowId", "")
                        )
                        for theme_info in flow_themes:
                            all_themes.add(theme_info["theme_name"])
            
            # Select flows with database intelligence
            selected_flows = await self._select_flows_with_database_intelligence(
                list(all_themes), task_description, max_flows, session_id
            )
            
            optimization_result["recommended_flows"] = selected_flows
            
            # Analyze dependencies and determine loading order
            if len(selected_flows) > 1:
                flow_ids = [f["flow_id"] for f in selected_flows]
                dependencies = await self._analyze_cross_flow_dependencies_for_context(flow_ids)
                
                if dependencies:
                    # Generate optimal loading order
                    loading_order = await self._generate_dependency_aware_loading_order(
                        flow_ids, dependencies
                    )
                    optimization_result["loading_order"] = loading_order
                    optimization_result["recommendations"].append(
                        f"Dependency-aware loading order recommended: {' → '.join(loading_order)}"
                    )
            
            # Performance estimation
            total_estimated_memory = len(selected_flows) * 100  # KB per flow
            estimated_loading_time = len(selected_flows) * 50  # ms per flow
            
            optimization_result["performance_estimate"] = {
                "memory_kb": total_estimated_memory,
                "loading_time_ms": estimated_loading_time,
                "context_switch_cost": "low" if len(selected_flows) <= 3 else "moderate"
            }
            
            # Generate optimization recommendations
            if total_estimated_memory > 800:  # > 800KB
                optimization_result["recommendations"].append(
                    "Consider reducing flow count for memory optimization"
                )
            
            if len(all_themes) > len(selected_flows):
                missing_theme_count = len(all_themes) - len(set(
                    theme for flow in selected_flows
                    for theme in flow.get("primary_themes", [])
                ))
                if missing_theme_count > 0:
                    optimization_result["recommendations"].append(
                        f"Consider additional flows to cover {missing_theme_count} themes"
                    )
            
            # Historical success pattern recommendations
            if session_id and self.session_queries:
                try:
                    similar_optimizations = await self.session_queries.get_similar_optimization_patterns(
                        session_id=session_id,
                        complexity_score=complexity_score,
                        theme_count=len(all_themes)
                    )
                    
                    if similar_optimizations:
                        optimization_result["recommendations"].append(
                            f"Based on similar tasks: {similar_optimizations.get('recommendation', 'N/A')}"
                        )
                        
                except Exception as e:
                    logger.debug(f"Could not get historical optimization patterns: {e}")
            
        except Exception as e:
            logger.error(f"Error optimizing multi-flow context loading: {e}")
            optimization_result["error"] = str(e)
        
        return optimization_result
    
    async def _generate_dependency_aware_loading_order(self, flow_ids: List[str],
                                                     dependencies: List[Dict[str, Any]]) -> List[str]:
        """Generate loading order that respects cross-flow dependencies."""
        # Simple topological sort for dependency resolution
        in_degree = {flow_id: 0 for flow_id in flow_ids}
        
        # Calculate in-degrees
        for dep in dependencies:
            if dep["to_flow"] in in_degree:
                in_degree[dep["to_flow"]] += 1
        
        # Topological sort
        queue = [flow_id for flow_id, degree in in_degree.items() if degree == 0]
        loading_order = []
        
        while queue:
            flow_id = queue.pop(0)
            loading_order.append(flow_id)
            
            # Update in-degrees
            for dep in dependencies:
                if dep["from_flow"] == flow_id and dep["to_flow"] in in_degree:
                    in_degree[dep["to_flow"]] -= 1
                    if in_degree[dep["to_flow"]] == 0:
                        queue.append(dep["to_flow"])
        
        return loading_order
    
    async def _estimate_memory_usage(self, context: ContextResult) -> int:
        """Estimate memory usage in MB for the loaded context."""
        # Rough estimates
        files_mb = len(context.files) * 0.1  # ~100KB per file average
        readmes_mb = sum(len(content) for content in context.readmes.values()) / (1024 * 1024)
        themes_mb = len(context.loaded_themes) * 0.01  # ~10KB per theme definition
        
        total_mb = files_mb + readmes_mb + themes_mb
        return int(total_mb)
    
    async def _generate_recommendations(self, context: ContextResult, 
                                       actual_mode: ContextMode, 
                                       requested_mode: ContextMode) -> List[str]:
        """Generate recommendations for context optimization."""
        recommendations = []
        
        # Memory usage recommendations
        if context.memory_estimate > self.max_memory_mb:
            recommendations.append(
                f"High memory usage ({context.memory_estimate}MB). "
                f"Consider using a more focused context mode."
            )
        
        # Mode recommendations
        if actual_mode != requested_mode:
            recommendations.append(
                f"Context mode escalated from {requested_mode.value} to {actual_mode.value} "
                f"based on theme complexity."
            )
        
        # Coverage recommendations
        if context.mode == ContextMode.THEME_FOCUSED and len(context.shared_files) > 3:
            recommendations.append(
                "Theme has many shared files. Consider theme-expanded mode for better context."
            )
        
        if context.mode == ContextMode.PROJECT_WIDE and len(context.loaded_themes) > 10:
            recommendations.append(
                "Loading many themes. Consider if theme-expanded mode would be sufficient."
            )
        
        # README recommendations
        missing_readmes = []
        for path in context.paths:
            if path not in context.readmes and path != '.':
                missing_readmes.append(path)
        
        if len(missing_readmes) > 3:
            recommendations.append(
                f"Consider adding README.md files to {len(missing_readmes)} directories "
                f"for better context guidance."
            )
        
        return recommendations
    
    async def assess_context_escalation(self, current_context: ContextResult, 
                                      issue_description: str) -> Tuple[bool, ContextMode, str]:
        """Assess if context escalation is needed based on an issue."""
        current_mode = current_context.mode
        
        # Keywords that suggest need for broader context
        escalation_keywords = [
            'import', 'dependency', 'reference', 'call', 'connection',
            'integration', 'shared', 'cross', 'global', 'config'
        ]
        
        # Check if issue mentions cross-theme concerns
        issue_lower = issue_description.lower()
        needs_escalation = any(keyword in issue_lower for keyword in escalation_keywords)
        
        if not needs_escalation:
            return False, current_mode, "No escalation needed"
        
        # Determine escalation path
        if current_mode == ContextMode.THEME_FOCUSED:
            new_mode = ContextMode.THEME_EXPANDED
            reason = "Issue mentions cross-theme dependencies or integrations"
        elif current_mode == ContextMode.THEME_EXPANDED:
            new_mode = ContextMode.PROJECT_WIDE
            reason = "Issue requires project-wide context"
        else:
            return False, current_mode, "Already at maximum context level"
        
        return True, new_mode, reason
    
    async def get_context_summary(self, context: ContextResult) -> str:
        """Get a human-readable summary of the loaded context."""
        summary_parts = [
            f"Context Mode: {context.mode.value}",
            f"Primary Theme: {context.primary_theme}",
            f"Loaded Themes: {', '.join(context.loaded_themes)}",
            f"Files: {len(context.files)} files",
            f"Paths: {len(context.paths)} directories",
            f"README files: {len(context.readmes)} found",
            f"Memory Usage: ~{context.memory_estimate}MB"
        ]
        
        if context.shared_files:
            summary_parts.append(f"Shared Files: {len(context.shared_files)} files shared across themes")
        
        if context.recommendations:
            summary_parts.append("Recommendations:")
            for rec in context.recommendations:
                summary_parts.append(f"  - {rec}")
        
        return "\n".join(summary_parts)
    
    async def filter_files_by_relevance(self, context: ContextResult, 
                                       task_description: str) -> List[str]:
        """Filter context files by relevance to a specific task."""
        if not task_description:
            return context.files
        
        # Extract keywords from task description
        task_keywords = set(word.lower().strip('.,!?:;') 
                           for word in task_description.split() 
                           if len(word) > 2)
        
        # Score files based on keyword matches
        file_scores = {}
        for file_path in context.files:
            score = 0
            file_parts = file_path.lower().replace('/', ' ').replace('_', ' ').replace('-', ' ')
            
            for keyword in task_keywords:
                if keyword in file_parts:
                    score += 1
            
            # Boost score for files in primary theme
            if any(theme_path in file_path for theme_path in context.paths[:3]):
                score += 0.5
            
            file_scores[file_path] = score
        
        # Return files sorted by relevance (minimum score of 0.5)
        relevant_files = [
            file_path for file_path, score in file_scores.items() 
            if score >= 0.5
        ]
        
        # If no relevant files found, return top N files from primary theme
        if not relevant_files and context.files:
            primary_theme_files = [
                f for f in context.files 
                if any(theme_path in f for theme_path in context.paths[:3])
            ]
            relevant_files = primary_theme_files[:10] if primary_theme_files else context.files[:10]
        
        return relevant_files
    
    async def validate_context_integrity(self, project_path: Path, context: ContextResult) -> Dict[str, Any]:
        """Validate context integrity using compressed validation rules."""
        await self.ensure_core_context_loaded()
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks_performed": []
        }
        
        try:
            # Get validation rules from compressed context
            integration_rules = self.context_manager.get_validation_rules('integrationValidation')
            integrity_rules = self.context_manager.get_validation_rules('dataIntegrity')
            
            if not integration_rules or not integrity_rules:
                validation_results["warnings"].append("Validation rules not available in compressed context")
                return validation_results
            
            # Validate theme integrity
            themes_dir = get_themes_path(project_path, self.config_manager)
            for theme_name in context.loaded_themes:
                theme_file = themes_dir / f"{theme_name}.json"
                if not theme_file.exists():
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"Theme file missing: {theme_name}.json")
                
                validation_results["checks_performed"].append(f"Theme file existence: {theme_name}")
            
            # Validate file references
            file_check_count = 0
            for file_path in context.files[:10]:  # Check first 10 files for performance
                full_path = project_path / file_path
                if not full_path.exists():
                    validation_results["warnings"].append(f"Referenced file not found: {file_path}")
                file_check_count += 1
            
            validation_results["checks_performed"].append(f"File existence checks: {file_check_count} files")
            
            # Check README coverage
            missing_readmes = []
            for path in context.paths[:5]:  # Check first 5 paths
                if path not in context.readmes and path != '.':
                    missing_readmes.append(path)
            
            if missing_readmes:
                validation_results["warnings"].append(f"Missing README files in {len(missing_readmes)} directories")
            
            validation_results["checks_performed"].append("README coverage check")
            
        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    async def get_compressed_directive(self, directive_key: str) -> Optional[Dict[str, Any]]:
        """Get compressed directive information."""
        await self.ensure_core_context_loaded()
        return self.context_manager.get_directive_summary(directive_key)
    
    
    
    async def _calculate_coverage_score(self, context: ContextResult) -> float:
        """Calculate a coverage score for the current context."""
        try:
            # Base score from theme coverage
            theme_score = min(len(context.loaded_themes) / 5.0, 1.0)
            
            # README coverage score
            readme_score = min(len(context.readmes) / len(context.paths) if context.paths else 0, 1.0)
            
            # File coverage score (balanced - not too many, not too few)
            ideal_file_count = 15
            file_score = 1.0 - abs(len(context.files) - ideal_file_count) / ideal_file_count
            file_score = max(0.0, min(file_score, 1.0))
            
            # Weighted average
            coverage_score = (theme_score * 0.3 + readme_score * 0.3 + file_score * 0.4)
            
            return round(coverage_score, 2)
            
        except Exception as e:
            logger.debug(f"Error calculating coverage score: {e}")
            return 0.5
    
    