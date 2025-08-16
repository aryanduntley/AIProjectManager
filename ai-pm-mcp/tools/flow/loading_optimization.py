"""
Flow loading and optimization operations.

Handles selective flow loading, optimization recommendations, and performance analysis.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_operations import BaseFlowOperations
from ...utils.project_paths import get_flows_path

logger = logging.getLogger(__name__)


class FlowLoadingOptimizer(BaseFlowOperations):
    """Handles selective flow loading and optimization."""
    
    async def load_flows_selective(self, project_path: Path, task_themes: List[str],
                                  task_description: str = "", max_flows: int = 5,
                                  session_id: Optional[str] = None) -> str:
        """Selectively load flows based on task requirements and themes."""
        try:
            flow_dir = get_flows_path(project_path, self.config_manager)
            flow_index_path = flow_dir / "flow-index.json"
            
            if not flow_index_path.exists():
                return "No flow index found. Create flow index first using flow_index_create."
            
            flow_index = json.loads(flow_index_path.read_text())
            
            # Use database optimization if available
            if self.theme_flow_queries:
                selected_flows = await self._select_flows_with_database_optimization(
                    task_themes, task_description, max_flows
                )
            else:
                selected_flows = await self._select_flows_file_based(
                    flow_dir, flow_index, task_themes, task_description, max_flows
                )
            
            # Load selected flow files
            loaded_flows = {}
            flow_summaries = []
            
            for flow_info in selected_flows:
                flow_id = flow_info["flow_id"]
                flow_file = flow_info["flow_file"]
                flow_path = flow_dir / flow_file
                
                if flow_path.exists():
                    try:
                        flow_data = json.loads(flow_path.read_text())
                        loaded_flows[flow_id] = flow_data
                        
                        # Create summary
                        status = flow_data.get("status", {})
                        summary = {
                            "flow_id": flow_id,
                            "name": flow_data.get("metadata", {}).get("name", "Unknown"),
                            "domain": flow_data.get("metadata", {}).get("domain", "general"),
                            "status": status.get("overall_status", "unknown"),
                            "completion": status.get("completion_percentage", 0),
                            "themes": flow_data.get("themes", {}).get("primary", []),
                            "relevance_score": flow_info.get("relevance_score", 0),
                            "flows_count": len(flow_data.get("flows", {}))
                        }
                        flow_summaries.append(summary)
                        
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in flow file: {flow_file}")
            
            # Track usage if session provided
            if session_id and self.session_queries:
                await self.track_selective_flow_loading(
                    session_id, task_themes, [f["flow_id"] for f in selected_flows], task_description
                )
            
            # Generate loading recommendations
            recommendations = await self.generate_loading_recommendations(
                loaded_flows, task_themes, task_description
            )
            
            result = (
                f"Selective flow loading completed:\n"
                f"- Task themes: {', '.join(task_themes)}\n"
                f"- Flows loaded: {len(loaded_flows)}/{len(flow_index.get('flowFiles', {}))}\n"
                f"- Total flows available: {sum(len(data.get('flows', {})) for data in loaded_flows.values())}\n\n"
            )
            
            result += "Loaded flows:\n"
            for summary in flow_summaries:
                result += (
                    f"  • {summary['name']} ({summary['flow_id']})\n"
                    f"    Domain: {summary['domain']}, Status: {summary['status']}, "
                    f"Completion: {summary['completion']}%\n"
                    f"    Themes: {', '.join(summary['themes'])}, "
                    f"Relevance: {summary['relevance_score']:.2f}\n"
                    f"    Flows: {summary['flows_count']}\n"
                )
            
            if recommendations:
                result += f"\nRecommendations:\n"
                for rec in recommendations:
                    result += f"  • {rec}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error in selective flow loading: {e}")
            return f"Error loading flows selectively: {str(e)}"
    
    async def optimize_flow_loading(self, project_path: Path, current_context: Dict[str, Any] = None,
                                   task_complexity: str = "moderate", session_id: Optional[str] = None) -> str:
        """Get optimized flow loading recommendations based on usage patterns."""
        try:
            if current_context is None:
                current_context = {}
                
            recommendations = {
                "loading_strategy": "selective",
                "max_recommended_flows": 5,
                "context_mode": "theme-expanded",
                "performance_optimizations": [],
                "flow_priorities": [],
                "memory_considerations": []
            }
            
            # Adjust recommendations based on task complexity
            if task_complexity == "simple":
                recommendations["max_recommended_flows"] = 3
                recommendations["context_mode"] = "theme-focused"
                recommendations["loading_strategy"] = "minimal"
            elif task_complexity == "complex":
                recommendations["max_recommended_flows"] = 8
                recommendations["context_mode"] = "project-wide"
                recommendations["loading_strategy"] = "comprehensive"
            
            # Get database-driven recommendations if available
            if self.theme_flow_queries and session_id:
                try:
                    # Get successful flow loading patterns from history
                    successful_patterns = await self.theme_flow_queries.get_successful_flow_patterns(
                        session_id=session_id,
                        task_complexity=task_complexity
                    )
                    
                    if successful_patterns:
                        recommendations["historical_insights"] = successful_patterns
                        recommendations["performance_optimizations"].append(
                            f"Based on {successful_patterns.get('pattern_count', 0)} similar successful sessions"
                        )
                except Exception as e:
                    logger.debug(f"Could not get historical patterns: {e}")
            
            # Analyze current flow index for optimization opportunities
            flow_dir = get_flows_path(project_path, self.config_manager)
            flow_index_path = flow_dir / "flow-index.json"
            
            if flow_index_path.exists():
                flow_index = json.loads(flow_index_path.read_text())
                flow_files = flow_index.get("flowFiles", {})
                
                # Categorize flows by completion status and complexity
                high_priority_flows = []
                moderate_priority_flows = []
                low_priority_flows = []
                
                for flow_id, flow_info in flow_files.items():
                    priority_score = 0
                    
                    # Factor in primary themes
                    current_themes = current_context.get("themes", [])
                    if any(theme in flow_info.get("primary_themes", []) for theme in current_themes):
                        priority_score += 3
                    
                    # Factor in status
                    if flow_info.get("status") == "in-progress":
                        priority_score += 2
                    elif flow_info.get("status") == "needs-review":
                        priority_score += 1
                    
                    # Categorize
                    if priority_score >= 4:
                        high_priority_flows.append(flow_id)
                    elif priority_score >= 2:
                        moderate_priority_flows.append(flow_id)
                    else:
                        low_priority_flows.append(flow_id)
                
                recommendations["flow_priorities"] = {
                    "high": high_priority_flows,
                    "moderate": moderate_priority_flows,
                    "low": low_priority_flows
                }
                
                # Performance optimizations based on flow count
                total_flows = len(flow_files)
                if total_flows > 10:
                    recommendations["performance_optimizations"].extend([
                        "Use selective loading to avoid memory overhead",
                        "Consider flow dependency analysis for optimal order",
                        "Enable database caching for faster access"
                    ])
                
                # Memory considerations
                estimated_memory = total_flows * 0.1  # Rough estimate: 100KB per flow
                if estimated_memory > 2:  # 2MB
                    recommendations["memory_considerations"].append(
                        f"Estimated memory usage: {estimated_memory:.1f}MB for all flows"
                    )
                    recommendations["memory_considerations"].append(
                        "Consider limiting concurrent flow loading"
                    )
            
            # Format recommendations
            result = f"Flow loading optimization recommendations (Complexity: {task_complexity}):\n\n"
            result += f"Strategy: {recommendations['loading_strategy']}\n"
            result += f"Max flows: {recommendations['max_recommended_flows']}\n"
            result += f"Context mode: {recommendations['context_mode']}\n\n"
            
            if recommendations["flow_priorities"]:
                result += "Flow Priorities:\n"
                for priority, flows in recommendations["flow_priorities"].items():
                    if flows:
                        result += f"  {priority.upper()}: {', '.join(flows)}\n"
                result += "\n"
            
            if recommendations["performance_optimizations"]:
                result += "Performance Optimizations:\n"
                for opt in recommendations["performance_optimizations"]:
                    result += f"  • {opt}\n"
                result += "\n"
            
            if recommendations["memory_considerations"]:
                result += "Memory Considerations:\n"
                for consideration in recommendations["memory_considerations"]:
                    result += f"  • {consideration}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing flow loading: {e}")
            return f"Error optimizing flow loading: {str(e)}"
    
    async def _select_flows_with_database_optimization(self, task_themes: List[str], 
                                                     task_description: str, 
                                                     max_flows: int) -> List[Dict[str, Any]]:
        """Select flows using database optimization."""
        selected_flows = []
        
        try:
            # Get flows for themes from database
            all_theme_flows = []
            for theme in task_themes:
                theme_flows = await self.theme_flow_queries.get_flows_for_theme(theme)
                all_theme_flows.extend(theme_flows)
            
            # Remove duplicates and score by relevance
            flows_by_id = {}
            for flow in all_theme_flows:
                flow_id = flow["flow_id"]
                if flow_id not in flows_by_id:
                    flows_by_id[flow_id] = flow
                    flows_by_id[flow_id]["relevance_score"] = 0
                
                # Increase relevance score
                flows_by_id[flow_id]["relevance_score"] += 1.0 / (flow.get("relevance_order", 1))
            
            # Add task description relevance scoring
            if task_description:
                task_keywords = set(task_description.lower().split())
                for flow_id, flow_info in flows_by_id.items():
                    flow_name = flow_info.get("flow_file", "").lower()
                    keyword_matches = sum(1 for keyword in task_keywords if keyword in flow_name)
                    flows_by_id[flow_id]["relevance_score"] += keyword_matches * 0.5
            
            # Sort by relevance and select top flows
            sorted_flows = sorted(flows_by_id.values(), 
                                key=lambda x: x["relevance_score"], reverse=True)
            selected_flows = sorted_flows[:max_flows]
            
        except Exception as e:
            logger.error(f"Error in database flow selection: {e}")
        
        return selected_flows
    
    async def _select_flows_file_based(self, flow_dir: Path, flow_index: Dict[str, Any],
                                     task_themes: List[str], task_description: str, 
                                     max_flows: int) -> List[Dict[str, Any]]:
        """Select flows using file-based analysis."""
        selected_flows = []
        flow_files = flow_index.get("flowFiles", {})
        
        # Score flows based on theme relevance
        flow_scores = {}
        for flow_id, flow_info in flow_files.items():
            score = 0
            
            # Theme relevance
            primary_themes = flow_info.get("primary_themes", [])
            secondary_themes = flow_info.get("secondary_themes", [])
            
            for theme in task_themes:
                if theme in primary_themes:
                    score += 2
                elif theme in secondary_themes:
                    score += 1
            
            # Task description keyword matching
            if task_description:
                task_keywords = set(task_description.lower().split())
                flow_name = flow_info.get("name", "").lower()
                flow_desc = flow_info.get("description", "").lower()
                
                name_matches = sum(1 for keyword in task_keywords if keyword in flow_name)
                desc_matches = sum(1 for keyword in task_keywords if keyword in flow_desc)
                
                score += name_matches * 0.5 + desc_matches * 0.3
            
            if score > 0:
                flow_scores[flow_id] = score
        
        # Select top scored flows
        sorted_flows = sorted(flow_scores.items(), key=lambda x: x[1], reverse=True)
        
        for flow_id, score in sorted_flows[:max_flows]:
            flow_info = flow_files[flow_id].copy()
            flow_info["flow_id"] = flow_id
            flow_info["relevance_score"] = score
            selected_flows.append(flow_info)
        
        return selected_flows