"""
Flow Intelligence Module
Handles flow-based context enhancement and intelligent flow selection.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from .compressed_context import ContextResult, ContextMode

# Import utilities from parent module paths
from ...utils.project_paths import get_flows_path

logger = logging.getLogger(__name__)


class FlowIntelligence:
    """Flow intelligence and context enhancement operations."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties directly
        self.theme_flow_queries = parent_instance.theme_flow_queries
        self.session_queries = parent_instance.session_queries
        self.file_metadata_queries = parent_instance.file_metadata_queries
    
    async def _enhance_context_with_flows(self, context: ContextResult, primary_theme: str):
        """Enhance context with flow information from database."""
        try:
            # Get flows associated with this theme
            theme_flows = await self.theme_flow_queries.get_flows_for_theme(primary_theme)
            
            if theme_flows:
                # Add flow information to recommendations
                flow_count = len(theme_flows)
                context.recommendations.append(
                    f"Theme has {flow_count} associated flows: {', '.join([f['flow_id'] for f in theme_flows])}"
                )
                
                # Load flow status for better context
                for flow_info in theme_flows:
                    flow_status = await self.theme_flow_queries.get_flow_status(flow_info['flow_id'])
                    if flow_status:
                        status_info = f"Flow {flow_info['flow_id']}: {flow_status['status']} ({flow_status['completion_percentage']}%)"
                        context.recommendations.append(status_info)
        
        except Exception as e:
            logger.debug(f"Error enhancing context with flows: {e}")
    
    
    async def get_optimized_flow_context(self, project_path: Path, flow_ids: List[str],
                                       session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get optimized context for specific flows using database relationships."""
        if not self.theme_flow_queries:
            return {"error": "Theme-flow queries not available"}
        
        try:
            context_data = {
                "flows": {},
                "related_themes": set(),
                "cross_flow_dependencies": [],
                "recommended_context_mode": ContextMode.THEME_FOCUSED.value
            }
            
            # Load flow information and related themes
            for flow_id in flow_ids:
                # Get flow details
                flow_info = await self.theme_flow_queries.get_flow_details(flow_id)
                if flow_info:
                    context_data["flows"][flow_id] = flow_info
                    
                    # Get themes associated with this flow
                    flow_themes = await self.theme_flow_queries.get_themes_for_flow(flow_id)
                    for theme_info in flow_themes:
                        context_data["related_themes"].add(theme_info['theme_name'])
                
                # Get cross-flow dependencies
                dependencies = await self.theme_flow_queries.get_cross_flow_dependencies(flow_id)
                context_data["cross_flow_dependencies"].extend(dependencies)
            
            # Convert set to list for JSON serialization
            context_data["related_themes"] = list(context_data["related_themes"])
            
            # Determine recommended context mode based on complexity
            theme_count = len(context_data["related_themes"])
            dependency_count = len(context_data["cross_flow_dependencies"])
            
            if theme_count > 3 or dependency_count > 5:
                context_data["recommended_context_mode"] = ContextMode.PROJECT_WIDE.value
            elif theme_count > 1 or dependency_count > 0:
                context_data["recommended_context_mode"] = ContextMode.THEME_EXPANDED.value
            
            # Track usage if session provided
            if session_id and self.session_queries:
                await self.session_queries.log_flow_context_usage(
                    session_id=session_id,
                    flow_ids=flow_ids,
                    themes_loaded=context_data["related_themes"],
                    context_mode=context_data["recommended_context_mode"]
                )
            
            return context_data
            
        except Exception as e:
            logger.error(f"Error getting optimized flow context: {e}")
            return {"error": str(e)}
    
    async def get_intelligent_context_recommendations(self, project_path: Path, 
                                                    current_context: ContextResult,
                                                    task_description: str,
                                                    session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get intelligent context recommendations based on task and historical data."""
        recommendations = {
            "current_assessment": {},
            "escalation_recommendations": [],
            "flow_suggestions": [],
            "theme_suggestions": [],
            "memory_optimization": []
        }
        
        try:
            # Assess current context
            recommendations["current_assessment"] = {
                "mode": current_context.mode.value,
                "themes_loaded": len(current_context.loaded_themes),
                "files_available": len(current_context.files),
                "memory_usage": current_context.memory_estimate,
                "coverage_score": await self._calculate_coverage_score(current_context)
            }
            
            # Use database analytics if available
            if self.session_queries and session_id:
                # Get similar tasks and their successful context patterns
                similar_patterns = await self.session_queries.get_successful_context_patterns(
                    task_keywords=task_description.lower().split()[:5]
                )
                
                if similar_patterns:
                    recommendations["escalation_recommendations"].append({
                        "reason": "Based on similar successful tasks",
                        "suggested_mode": similar_patterns.get('most_successful_mode'),
                        "confidence": similar_patterns.get('confidence_score', 0.5)
                    })
            
            # Flow-based recommendations if database available
            if self.theme_flow_queries:
                primary_theme = current_context.primary_theme
                relevant_flows = await self.theme_flow_queries.get_flows_for_theme(primary_theme)
                
                incomplete_flows = [
                    f for f in relevant_flows 
                    if f.get('completion_percentage', 0) < 100
                ]
                
                if incomplete_flows:
                    recommendations["flow_suggestions"] = [
                        {
                            "flow_id": f['flow_id'],
                            "status": f['status'],
                            "completion": f.get('completion_percentage', 0),
                            "suggestion": f"Consider flow {f['flow_id']} for task context"
                        }
                        for f in incomplete_flows
                    ]
            
            # Memory optimization suggestions
            if current_context.memory_estimate > self.max_memory_mb * 0.8:
                recommendations["memory_optimization"].append({
                    "issue": "High memory usage detected",
                    "current_usage": current_context.memory_estimate,
                    "suggestions": [
                        "Consider more focused context mode",
                        "Use file relevance filtering",
                        "Limit README file loading"
                    ]
                })
            
        except Exception as e:
            logger.error(f"Error generating intelligent context recommendations: {e}")
            recommendations["error"] = str(e)
        
        return recommendations
    
    # Multi-Flow System Integration Methods
    
    async def load_selective_flows_for_context(self, project_path: Path, 
                                             task_themes: List[str],
                                             task_description: str = "",
                                             max_flows: int = 5,
                                             session_id: Optional[str] = None) -> Dict[str, Any]:
        """Load flows selectively based on task requirements using multi-flow system."""
        if not self.theme_flow_queries:
            return {"error": "Multi-flow system requires database integration"}
        
        try:
            # Use database optimization for flow selection
            selected_flows = await self._select_flows_with_database_intelligence(
                task_themes, task_description, max_flows, session_id
            )
            
            # Load actual flow data
            flow_dir = get_flows_path(project_path, self.config_manager)
            loaded_flows = {}
            flow_context = {
                "selected_flows": [],
                "cross_flow_dependencies": [],
                "recommended_context_mode": "theme-focused",
                "performance_metrics": {
                    "selection_time_ms": 0,
                    "loading_time_ms": 0,
                    "memory_estimate_kb": 0
                }
            }
            
            start_time = datetime.utcnow()
            
            for flow_info in selected_flows:
                flow_id = flow_info["flow_id"]
                flow_file = flow_info.get("flow_file", f"{flow_info.get('domain', 'general')}-flow.json")
                flow_path = flow_dir / flow_file
                
                if flow_path.exists():
                    try:
                        flow_data = json.loads(flow_path.read_text())
                        loaded_flows[flow_id] = flow_data
                        
                        flow_summary = {
                            "flow_id": flow_id,
                            "name": flow_data.get("metadata", {}).get("name", "Unknown"),
                            "domain": flow_data.get("metadata", {}).get("domain", "general"),
                            "status": flow_data.get("status", {}).get("overall_status", "unknown"),
                            "completion_percentage": flow_data.get("status", {}).get("completion_percentage", 0),
                            "themes": flow_data.get("themes", {}),
                            "flows_count": len(flow_data.get("flows", {})),
                            "relevance_score": flow_info.get("relevance_score", 0)
                        }
                        flow_context["selected_flows"].append(flow_summary)
                        
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in flow file: {flow_file}")
            
            loading_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            flow_context["performance_metrics"]["loading_time_ms"] = loading_time
            
            # Analyze cross-flow dependencies
            if len(loaded_flows) > 1:
                dependencies = await self._analyze_cross_flow_dependencies_for_context(
                    list(loaded_flows.keys())
                )
                flow_context["cross_flow_dependencies"] = dependencies
            
            # Determine recommended context mode based on flow complexity
            total_flows_count = sum(len(data.get("flows", {})) for data in loaded_flows.values())
            total_themes = set()
            for flow_data in loaded_flows.values():
                themes = flow_data.get("themes", {})
                total_themes.update(themes.get("primary", []))
                total_themes.update(themes.get("secondary", []))
            
            if len(total_themes) > 3 or total_flows_count > 10:
                flow_context["recommended_context_mode"] = "project-wide"
            elif len(total_themes) > 1 or len(flow_context["cross_flow_dependencies"]) > 0:
                flow_context["recommended_context_mode"] = "theme-expanded"
            
            # Estimate memory usage
            flow_context["performance_metrics"]["memory_estimate_kb"] = len(loaded_flows) * 100  # ~100KB per flow
            
            # Track usage if session provided
            if session_id and self.session_queries:
                await self.session_queries.log_selective_flow_loading(
                    session_id=session_id,
                    task_themes=task_themes,
                    loaded_flows=list(loaded_flows.keys()),
                    performance_metrics=flow_context["performance_metrics"]
                )
            
            flow_context["loaded_flows_data"] = loaded_flows
            return flow_context
            
        except Exception as e:
            logger.error(f"Error in selective flow loading: {e}")
            return {"error": str(e)}
    
    async def get_context_with_selective_flows(self, project_path: Path, 
                                             primary_theme: str,
                                             task_description: str = "",
                                             context_mode: ContextMode = ContextMode.THEME_FOCUSED,
                                             max_flows: int = 5,
                                             session_id: Optional[str] = None) -> ContextResult:
        """Load context enhanced with selectively loaded flows."""
        try:
            # Load base context
            base_context = await self.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=primary_theme,
                context_mode=context_mode,
                session_id=session_id
            )
            
            # Get related themes from context
            task_themes = base_context.loaded_themes
            
            # Load selective flows
            flow_context = await self.load_selective_flows_for_context(
                project_path=project_path,
                task_themes=task_themes,
                task_description=task_description,
                max_flows=max_flows,
                session_id=session_id
            )
            
            if "error" not in flow_context:
                # Enhance context with flow information
                flow_recommendations = []
                
                # Add flow-specific recommendations
                selected_flows = flow_context.get("selected_flows", [])
                if selected_flows:
                    flow_recommendations.append(
                        f"Loaded {len(selected_flows)} relevant flows for task context"
                    )
                    
                    incomplete_flows = [f for f in selected_flows if f["completion_percentage"] < 100]
                    if incomplete_flows:
                        flow_recommendations.append(
                            f"{len(incomplete_flows)} flows incomplete - consider prioritizing completion"
                        )
                
                # Cross-flow dependency recommendations
                dependencies = flow_context.get("cross_flow_dependencies", [])
                if dependencies:
                    flow_recommendations.append(
                        f"Found {len(dependencies)} cross-flow dependencies - consider loading order"
                    )
                
                # Context mode recommendations based on flows
                recommended_mode = flow_context.get("recommended_context_mode")
                if recommended_mode and recommended_mode != context_mode.value:
                    flow_recommendations.append(
                        f"Multi-flow analysis suggests {recommended_mode} context mode"
                    )
                
                # Performance recommendations
                perf_metrics = flow_context.get("performance_metrics", {})
                memory_kb = perf_metrics.get("memory_estimate_kb", 0)
                if memory_kb > 1000:  # > 1MB
                    flow_recommendations.append(
                        f"Flow memory usage: {memory_kb}KB - consider selective loading"
                    )
                
                # Add flow recommendations to base context
                base_context.recommendations.extend(flow_recommendations)
                
                # Update memory estimate with flow data
                base_context.memory_estimate += int(memory_kb / 1024)  # Convert to MB
            
            return base_context
            
        except Exception as e:
            logger.error(f"Error loading context with selective flows: {e}")
            # Fallback to regular context loading
            return await self.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=primary_theme,
                context_mode=context_mode,
                session_id=session_id
            )
    
    async def _select_flows_with_database_intelligence(self, task_themes: List[str],
                                                     task_description: str,
                                                     max_flows: int,
                                                     session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Select flows using database intelligence and historical patterns."""
        selected_flows = []
        
        try:
            # Get flows for each theme
            theme_flows = []
            for theme in task_themes:
                flows = await self.theme_flow_queries.get_flows_for_theme(theme)
                theme_flows.extend(flows)
            
            # Remove duplicates and score by relevance
            flows_by_id = {}
            for flow in theme_flows:
                flow_id = flow["flow_id"]
                if flow_id not in flows_by_id:
                    flows_by_id[flow_id] = flow
                    flows_by_id[flow_id]["relevance_score"] = 0
                
                # Base relevance score from theme relationship
                relevance_order = flow.get("relevance_order", 1)
                flows_by_id[flow_id]["relevance_score"] += 1.0 / relevance_order
            
            # Enhanced scoring with task description
            if task_description:
                task_keywords = set(word.lower() for word in task_description.split() if len(word) > 2)
                
                for flow_id, flow_info in flows_by_id.items():
                    # Check flow file name
                    flow_file = flow_info.get("flow_file", "").lower()
                    file_keywords = set(flow_file.replace("-flow.json", "").replace("-", " ").split())
                    
                    keyword_matches = len(task_keywords.intersection(file_keywords))
                    flows_by_id[flow_id]["relevance_score"] += keyword_matches * 0.5
            
            # Historical success pattern scoring if session available
            if session_id and self.session_queries:
                try:
                    success_patterns = await self.session_queries.get_flow_success_patterns(
                        session_id=session_id,
                        task_themes=task_themes,
                        task_keywords=task_description.lower().split()[:5]
                    )
                    
                    if success_patterns:
                        for flow_id in flows_by_id:
                            if flow_id in success_patterns.get("successful_flows", []):
                                flows_by_id[flow_id]["relevance_score"] += 1.0
                                
                except Exception as e:
                    logger.debug(f"Could not get historical success patterns: {e}")
            
            # Flow status boost (prioritize in-progress flows)
            for flow_id in flows_by_id:
                try:
                    flow_status = await self.theme_flow_queries.get_flow_status(flow_id)
                    if flow_status:
                        status = flow_status.get("status", "")
                        if status == "in-progress":
                            flows_by_id[flow_id]["relevance_score"] += 0.8
                        elif status == "needs-review":
                            flows_by_id[flow_id]["relevance_score"] += 0.5
                        
                        # Completion percentage factor
                        completion = flow_status.get("completion_percentage", 0)
                        if 20 <= completion < 80:  # Partially complete flows are more relevant
                            flows_by_id[flow_id]["relevance_score"] += 0.3
                            
                except Exception as e:
                    logger.debug(f"Could not get flow status for {flow_id}: {e}")
            
            # Sort by relevance score and select top flows
            sorted_flows = sorted(flows_by_id.values(), key=lambda x: x["relevance_score"], reverse=True)
            selected_flows = sorted_flows[:max_flows]
            
        except Exception as e:
            logger.error(f"Error in database-intelligent flow selection: {e}")
        
        return selected_flows
    