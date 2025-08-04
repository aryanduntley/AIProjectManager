"""
Multi-flow system management tools for the AI Project Manager MCP Server.

Handles selective flow loading, cross-flow dependencies, flow index management,
and integration with the database-driven theme-flow relationship system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import asyncio

# Core components
from ..core.mcp_api import ToolDefinition
from ..database.theme_flow_queries import ThemeFlowQueries
from ..database.session_queries import SessionQueries
from ..database.file_metadata_queries import FileMetadataQueries
from ..utils.project_paths import get_flows_path, get_themes_path

logger = logging.getLogger(__name__)


class FlowTools:
    """Tools for multi-flow system management with database integration."""
    
    def __init__(self, 
                 theme_flow_queries: Optional[ThemeFlowQueries] = None,
                 session_queries: Optional[SessionQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None,
                 config_manager=None):
        self.theme_flow_queries = theme_flow_queries
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
        self.config_manager = config_manager
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get available flow management tools."""
        return [
            ToolDefinition(
                name="flow_index_create",
                description="Create or update flow index with multi-flow coordination",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "flows": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "flow_id": {"type": "string"},
                                    "flow_file": {"type": "string"},
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "primary_themes": {"type": "array", "items": {"type": "string"}},
                                    "secondary_themes": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["flow_id", "flow_file", "name"]
                            },
                            "description": "List of flows to include in the index"
                        },
                        "cross_flow_dependencies": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "from_flow": {"type": "string"},
                                    "to_flow": {"type": "string"},
                                    "dependency_type": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            },
                            "description": "Cross-flow dependencies"
                        }
                    },
                    "required": ["project_path", "flows"]
                },
                handler=self.create_flow_index
            ),
            ToolDefinition(
                name="flow_create",
                description="Create a new individual flow file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "flow_id": {
                            "type": "string",
                            "description": "Unique identifier for the flow"
                        },
                        "flow_name": {
                            "type": "string",
                            "description": "Human-readable name for the flow"
                        },
                        "domain": {
                            "type": "string",
                            "description": "Domain or theme category (e.g., authentication, payment)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of what this flow accomplishes"
                        },
                        "primary_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Primary themes associated with this flow"
                        },
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_id": {"type": "string"},
                                    "trigger": {"type": "string"},
                                    "user_experience": {"type": "string"},
                                    "conditions": {"type": "array", "items": {"type": "string"}},
                                    "outcomes": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "description": "Flow steps"
                        }
                    },
                    "required": ["project_path", "flow_id", "flow_name", "domain"]
                },
                handler=self.create_flow
            ),
            ToolDefinition(
                name="flow_load_selective",
                description="Selectively load flows based on task requirements and themes",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "task_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Themes required for the task"
                        },
                        "task_description": {
                            "type": "string",
                            "description": "Description of the task for context analysis"
                        },
                        "max_flows": {
                            "type": "integer",
                            "default": 5,
                            "description": "Maximum number of flows to load"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for tracking"
                        }
                    },
                    "required": ["project_path", "task_themes"]
                },
                handler=self.load_flows_selective
            ),
            ToolDefinition(
                name="flow_dependencies_analyze",
                description="Analyze cross-flow dependencies and recommend loading order",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "flow_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Flow IDs to analyze dependencies for"
                        },
                        "include_indirect": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include indirect dependencies in analysis"
                        }
                    },
                    "required": ["project_path", "flow_ids"]
                },
                handler=self.analyze_flow_dependencies
            ),
            ToolDefinition(
                name="flow_status_update",
                description="Update flow and step status with database persistence",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "flow_id": {
                            "type": "string",
                            "description": "Flow ID to update"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in-progress", "complete", "needs-review", "blocked"],
                            "description": "New flow status"
                        },
                        "completion_percentage": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Completion percentage"
                        },
                        "step_updates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_id": {"type": "string"},
                                    "status": {"type": "string"},
                                    "completed_at": {"type": "string"}
                                }
                            },
                            "description": "Step status updates"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for tracking"
                        }
                    },
                    "required": ["project_path", "flow_id"]
                },
                handler=self.update_flow_status
            ),
            ToolDefinition(
                name="flow_optimize_loading",
                description="Get optimized flow loading recommendations based on usage patterns",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "current_context": {
                            "type": "object",
                            "description": "Current context information"
                        },
                        "task_complexity": {
                            "type": "string",
                            "enum": ["simple", "moderate", "complex"],
                            "default": "moderate",
                            "description": "Task complexity level"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for historical analysis"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.optimize_flow_loading
            ),
            ToolDefinition(
                name="flow_sync_database",
                description="Synchronize flow definitions with database for optimal performance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "force_update": {
                            "type": "boolean",
                            "default": False,
                            "description": "Force update even if no changes detected"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.sync_flows_with_database
            )
        ]
    
    async def create_flow_index(self, arguments: Dict[str, Any]) -> str:
        """Create or update flow index with multi-flow coordination."""
        try:
            project_path = Path(arguments["project_path"])
            flows = arguments["flows"]
            cross_flow_dependencies = arguments.get("cross_flow_dependencies", [])
            
            flow_dir = get_flows_path(project_path, self.config_manager)
            flow_dir.mkdir(parents=True, exist_ok=True)
            
            flow_index_path = flow_dir / "flow-index.json"
            
            # Create flow index structure
            flow_index = {
                "metadata": {
                    "version": "1.0.0",
                    "created": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat(),
                    "description": "Master flow index with multi-flow coordination"
                },
                "flowFiles": {},
                "crossFlowDependencies": cross_flow_dependencies,
                "globalFlowSettings": {
                    "maxConcurrentFlows": 10,
                    "defaultContextMode": "theme-expanded",
                    "enableSelectiveLoading": True,
                    "performanceOptimization": True
                },
                "flowCategories": {}
            }
            
            # Process flows and organize by category
            categories = {}
            for flow in flows:
                flow_id = flow["flow_id"]
                flow_file = flow["flow_file"]
                
                # Determine category from flow file name or explicit domain
                if "-flow.json" in flow_file:
                    category = flow_file.replace("-flow.json", "")
                else:
                    category = flow.get("domain", "general")
                
                if category not in categories:
                    categories[category] = []
                categories[category].append(flow_id)
                
                # Add to flow files mapping
                flow_index["flowFiles"][flow_id] = {
                    "file": flow_file,
                    "name": flow["name"],
                    "description": flow.get("description", ""),
                    "primary_themes": flow.get("primary_themes", []),
                    "secondary_themes": flow.get("secondary_themes", []),
                    "category": category,
                    "created": datetime.utcnow().isoformat(),
                    "status": "pending"
                }
            
            flow_index["flowCategories"] = categories
            
            # Write flow index
            flow_index_path.write_text(json.dumps(flow_index, indent=2))
            
            # Sync with database if available
            sync_result = ""
            if self.theme_flow_queries:
                try:
                    await self.theme_flow_queries.sync_flow_index(flow_index)
                    sync_result = " and synchronized with database"
                except Exception as e:
                    sync_result = f" (database sync failed: {str(e)})"
            
            return (
                f"Flow index created successfully{sync_result}:\n"
                f"- {len(flows)} flows registered\n"
                f"- {len(categories)} categories: {', '.join(categories.keys())}\n"
                f"- {len(cross_flow_dependencies)} cross-flow dependencies\n"
                f"- Selective loading: {'enabled' if flow_index['globalFlowSettings']['enableSelectiveLoading'] else 'disabled'}"
            )
            
        except Exception as e:
            logger.error(f"Error creating flow index: {e}")
            return f"Error creating flow index: {str(e)}"
    
    async def create_flow(self, arguments: Dict[str, Any]) -> str:
        """Create a new individual flow file."""
        try:
            project_path = Path(arguments["project_path"])
            flow_id = arguments["flow_id"]
            flow_name = arguments["flow_name"]
            domain = arguments["domain"]
            description = arguments.get("description", "")
            primary_themes = arguments.get("primary_themes", [])
            steps = arguments.get("steps", [])
            
            flow_dir = get_flows_path(project_path, self.config_manager)
            flow_dir.mkdir(parents=True, exist_ok=True)
            
            # Create flow file name
            flow_file_name = f"{domain}-flow.json"
            flow_file_path = flow_dir / flow_file_name
            
            # Create flow structure with enhanced status tracking
            flow_data = {
                "metadata": {
                    "flow_id": flow_id,
                    "name": flow_name,
                    "domain": domain,
                    "description": description,
                    "version": "1.0.0",
                    "created": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat()
                },
                "themes": {
                    "primary": primary_themes,
                    "secondary": []
                },
                "status": {
                    "overall_status": "pending",
                    "completion_percentage": 0,
                    "last_updated": datetime.utcnow().isoformat(),
                    "milestone_integration": {
                        "required_milestones": [],
                        "completion_validation": []
                    }
                },
                "flows": {}
            }
            
            # Add individual flows within the domain
            if steps:
                # Create a main flow with the provided steps
                main_flow_id = f"{flow_id}-main"
                flow_data["flows"][main_flow_id] = {
                    "id": main_flow_id,
                    "name": f"Main {flow_name} Flow",
                    "description": description,
                    "status": "pending",
                    "steps": []
                }
                
                # Process steps with enhanced status tracking
                for i, step in enumerate(steps):
                    step_data = {
                        "step_id": step.get("step_id", f"STEP-{i+1:03d}"),
                        "step_number": i + 1,
                        "trigger": step.get("trigger", ""),
                        "user_experience": step.get("user_experience", ""),
                        "conditions": step.get("conditions", []),
                        "outcomes": step.get("outcomes", []),
                        "status": "pending",
                        "dependencies": [],
                        "file_references": [],
                        "implementation_status": "pending"
                    }
                    flow_data["flows"][main_flow_id]["steps"].append(step_data)
            
            # Write flow file
            flow_file_path.write_text(json.dumps(flow_data, indent=2))
            
            # Update flow index if it exists
            await self._update_flow_index_with_new_flow(
                project_path, flow_id, flow_file_name, flow_name, description, primary_themes, domain
            )
            
            # Sync with database if available
            sync_result = ""
            if self.theme_flow_queries:
                try:
                    await self.theme_flow_queries.create_flow(flow_id, flow_data)
                    sync_result = " and registered in database"
                except Exception as e:
                    sync_result = f" (database sync failed: {str(e)})"
            
            return (
                f"Flow created successfully{sync_result}:\n"
                f"- Flow ID: {flow_id}\n"
                f"- File: {flow_file_name}\n"
                f"- Domain: {domain}\n"
                f"- Primary themes: {', '.join(primary_themes)}\n"
                f"- Steps: {len(steps)}\n"
                f"- Status: pending"
            )
            
        except Exception as e:
            logger.error(f"Error creating flow: {e}")
            return f"Error creating flow: {str(e)}"
    
    async def load_flows_selective(self, arguments: Dict[str, Any]) -> str:
        """Selectively load flows based on task requirements and themes."""
        try:
            project_path = Path(arguments["project_path"])
            task_themes = arguments["task_themes"]
            task_description = arguments.get("task_description", "")
            max_flows = arguments.get("max_flows", 5)
            session_id = arguments.get("session_id")
            
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
                await self._track_selective_flow_loading(
                    session_id, task_themes, [f["flow_id"] for f in selected_flows], task_description
                )
            
            # Generate loading recommendations
            recommendations = await self._generate_loading_recommendations(
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
    
    async def analyze_flow_dependencies(self, arguments: Dict[str, Any]) -> str:
        """Analyze cross-flow dependencies and recommend loading order."""
        try:
            project_path = Path(arguments["project_path"])
            flow_ids = arguments["flow_ids"]
            include_indirect = arguments.get("include_indirect", True)
            
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
            loading_order = []
            
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
    
    async def update_flow_status(self, arguments: Dict[str, Any]) -> str:
        """Update flow and step status with database persistence."""
        try:
            project_path = Path(arguments["project_path"])
            flow_id = arguments["flow_id"]
            status = arguments.get("status")
            completion_percentage = arguments.get("completion_percentage")
            step_updates = arguments.get("step_updates", [])
            session_id = arguments.get("session_id")
            
            # Find flow file
            flow_file_path = await self._find_flow_file(project_path, flow_id)
            if not flow_file_path:
                return f"Flow file for '{flow_id}' not found."
            
            # Load and update flow data
            flow_data = json.loads(flow_file_path.read_text())
            
            updated_fields = []
            
            # Update overall status
            if status:
                if "status" not in flow_data:
                    flow_data["status"] = {}
                flow_data["status"]["overall_status"] = status
                flow_data["status"]["last_updated"] = datetime.utcnow().isoformat()
                updated_fields.append(f"status: {status}")
            
            # Update completion percentage
            if completion_percentage is not None:
                if "status" not in flow_data:
                    flow_data["status"] = {}
                flow_data["status"]["completion_percentage"] = completion_percentage
                updated_fields.append(f"completion: {completion_percentage}%")
            
            # Update step statuses
            step_updates_applied = 0
            for step_update in step_updates:
                step_id = step_update["step_id"]
                step_status = step_update["status"]
                completed_at = step_update.get("completed_at")
                
                # Find and update step
                for flow_key, flow_content in flow_data.get("flows", {}).items():
                    for step in flow_content.get("steps", []):
                        if step.get("step_id") == step_id:
                            step["status"] = step_status
                            if completed_at:
                                step["completed_at"] = completed_at
                            step_updates_applied += 1
                            break
            
            if step_updates_applied > 0:
                updated_fields.append(f"{step_updates_applied} steps updated")
            
            # Write updated flow data
            flow_file_path.write_text(json.dumps(flow_data, indent=2))
            
            # Update database if available
            db_result = ""
            if self.theme_flow_queries:
                try:
                    await self.theme_flow_queries.update_flow_status(
                        flow_id=flow_id,
                        status=status,
                        completion_percentage=completion_percentage
                    )
                    
                    # Update step statuses in database
                    for step_update in step_updates:
                        await self.theme_flow_queries.update_flow_step_status(
                            flow_id=flow_id,
                            step_id=step_update["step_id"],
                            status=step_update["status"],
                            completed_at=step_update.get("completed_at")
                        )
                    
                    db_result = " and database"
                except Exception as e:
                    db_result = f" (database update failed: {str(e)})"
            
            # Track update in session if provided
            if session_id and self.session_queries:
                await self.session_queries.log_flow_status_update(
                    session_id=session_id,
                    flow_id=flow_id,
                    status_changes=updated_fields
                )
            
            return (
                f"Flow status updated successfully in file{db_result}:\n"
                f"- Flow: {flow_id}\n"
                f"- Updates: {', '.join(updated_fields)}\n"
                f"- Step updates applied: {step_updates_applied}"
            )
            
        except Exception as e:
            logger.error(f"Error updating flow status: {e}")
            return f"Error updating flow status: {str(e)}"
    
    async def optimize_flow_loading(self, arguments: Dict[str, Any]) -> str:
        """Get optimized flow loading recommendations based on usage patterns."""
        try:
            project_path = Path(arguments["project_path"])
            current_context = arguments.get("current_context", {})
            task_complexity = arguments.get("task_complexity", "moderate")
            session_id = arguments.get("session_id")
            
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
    
    async def sync_flows_with_database(self, arguments: Dict[str, Any]) -> str:
        """Synchronize flow definitions with database for optimal performance."""
        try:
            project_path = Path(arguments["project_path"])
            force_update = arguments.get("force_update", False)
            
            if not self.theme_flow_queries:
                return "Database not available. Flow synchronization requires database connection."
            
            flow_dir = get_flows_path(project_path, self.config_manager)
            if not flow_dir.exists():
                return "No ProjectFlow directory found. Initialize flows first."
            
            # Load flow index
            flow_index_path = flow_dir / "flow-index.json"
            if not flow_index_path.exists():
                return "No flow index found. Create flow index first."
            
            flow_index = json.loads(flow_index_path.read_text())
            
            # Collect all flow data
            flows_data = {}
            flow_files = flow_index.get("flowFiles", {})
            
            sync_results = {
                "flows_processed": 0,
                "flows_updated": 0,
                "flows_created": 0,
                "errors": []
            }
            
            for flow_id, flow_info in flow_files.items():
                flow_file = flow_info["file"]
                flow_file_path = flow_dir / flow_file
                
                if flow_file_path.exists():
                    try:
                        flow_data = json.loads(flow_file_path.read_text())
                        flows_data[flow_id] = flow_data
                        sync_results["flows_processed"] += 1
                        
                        # Check if flow exists in database
                        existing_flow = await self.theme_flow_queries.get_flow_details(flow_id)
                        
                        if existing_flow:
                            # Update existing flow
                            if force_update or await self._flow_needs_update(existing_flow, flow_data):
                                await self.theme_flow_queries.update_flow(flow_id, flow_data)
                                sync_results["flows_updated"] += 1
                        else:
                            # Create new flow
                            await self.theme_flow_queries.create_flow(flow_id, flow_data)
                            sync_results["flows_created"] += 1
                        
                    except json.JSONDecodeError as e:
                        sync_results["errors"].append(f"Invalid JSON in {flow_file}: {str(e)}")
                    except Exception as e:
                        sync_results["errors"].append(f"Error processing {flow_file}: {str(e)}")
                else:
                    sync_results["errors"].append(f"Flow file not found: {flow_file}")
            
            # Sync flow index metadata
            try:
                await self.theme_flow_queries.sync_flow_index(flow_index)
            except Exception as e:
                sync_results["errors"].append(f"Error syncing flow index: {str(e)}")
            
            # Sync theme-flow relationships
            try:
                themes_dir = get_themes_path(project_path, self.config_manager)
                if themes_dir.exists():
                    theme_files = list(themes_dir.glob("*.json"))
                    theme_data = {}
                    
                    for theme_file in theme_files:
                        if theme_file.name != "themes.json":
                            try:
                                theme_name = theme_file.stem
                                theme_content = json.loads(theme_file.read_text())
                                if "flows" in theme_content:
                                    theme_data[theme_name] = theme_content
                            except json.JSONDecodeError:
                                continue
                    
                    if theme_data:
                        await self.theme_flow_queries.sync_theme_flows_from_files(
                            theme_data, flow_index
                        )
            except Exception as e:
                sync_results["errors"].append(f"Error syncing theme-flow relationships: {str(e)}")
            
            # Format results
            result = "Flow database synchronization completed:\n"
            result += f"- Flows processed: {sync_results['flows_processed']}\n"
            result += f"- Flows updated: {sync_results['flows_updated']}\n"
            result += f"- Flows created: {sync_results['flows_created']}\n"
            
            if sync_results["errors"]:
                result += f"- Errors: {len(sync_results['errors'])}\n"
                result += "\nErrors encountered:\n"
                for error in sync_results["errors"]:
                    result += f"  • {error}\n"
            else:
                result += "- No errors encountered\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error synchronizing flows with database: {e}")
            return f"Error synchronizing flows with database: {str(e)}"
    
    # Helper methods
    
    async def _update_flow_index_with_new_flow(self, project_path: Path, flow_id: str, 
                                             flow_file: str, flow_name: str, 
                                             description: str, primary_themes: List[str], 
                                             domain: str):
        """Update flow index with newly created flow."""
        flow_index_path = get_flows_path(project_path, self.config_manager) / "flow-index.json"
        
        if flow_index_path.exists():
            flow_index = json.loads(flow_index_path.read_text())
        else:
            # Create basic flow index if it doesn't exist
            flow_index = {
                "metadata": {
                    "version": "1.0.0",
                    "created": datetime.utcnow().isoformat(),
                    "description": "Master flow index"
                },
                "flowFiles": {},
                "crossFlowDependencies": [],
                "globalFlowSettings": {
                    "enableSelectiveLoading": True
                },
                "flowCategories": {}
            }
        
        # Add new flow to index
        flow_index["flowFiles"][flow_id] = {
            "file": flow_file,
            "name": flow_name,
            "description": description,
            "primary_themes": primary_themes,
            "secondary_themes": [],
            "category": domain,
            "created": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        # Update categories
        if domain not in flow_index["flowCategories"]:
            flow_index["flowCategories"][domain] = []
        flow_index["flowCategories"][domain].append(flow_id)
        
        # Update metadata
        flow_index["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        
        # Write updated index
        flow_index_path.write_text(json.dumps(flow_index, indent=2))
    
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
    
    async def _find_flow_file(self, project_path: Path, flow_id: str) -> Optional[Path]:
        """Find the flow file containing the specified flow ID."""
        flow_dir = get_flows_path(project_path, self.config_manager)
        flow_index_path = flow_dir / "flow-index.json"
        
        if not flow_index_path.exists():
            return None
        
        try:
            flow_index = json.loads(flow_index_path.read_text())
            flow_files = flow_index.get("flowFiles", {})
            
            if flow_id in flow_files:
                flow_file = flow_files[flow_id]["file"]
                return flow_dir / flow_file
        except json.JSONDecodeError:
            pass
        
        return None
    
    async def _flow_needs_update(self, existing_flow: Dict[str, Any], 
                               file_flow_data: Dict[str, Any]) -> bool:
        """Check if flow data in database needs updating."""
        # Compare metadata timestamps or version
        existing_updated = existing_flow.get("last_updated", "")
        file_updated = file_flow_data.get("metadata", {}).get("last_updated", "")
        
        if file_updated and existing_updated:
            return file_updated > existing_updated
        
        # If no timestamps, assume update needed
        return True
    
    async def _track_selective_flow_loading(self, session_id: str, task_themes: List[str],
                                          loaded_flow_ids: List[str], task_description: str):
        """Track selective flow loading for analytics."""
        try:
            if self.session_queries:
                await self.session_queries.log_flow_loading_event(
                    session_id=session_id,
                    event_type="selective_loading",
                    task_themes=task_themes,
                    loaded_flows=loaded_flow_ids,
                    task_description=task_description,
                    loading_strategy="selective"
                )
        except Exception as e:
            logger.debug(f"Error tracking flow loading: {e}")
    
    async def _generate_loading_recommendations(self, loaded_flows: Dict[str, Any],
                                              task_themes: List[str], 
                                              task_description: str) -> List[str]:
        """Generate recommendations based on loaded flows."""
        recommendations = []
        
        # Check for incomplete flows
        incomplete_flows = []
        for flow_id, flow_data in loaded_flows.items():
            status = flow_data.get("status", {})
            completion = status.get("completion_percentage", 0)
            if completion < 100:
                incomplete_flows.append((flow_id, completion))
        
        if incomplete_flows:
            recommendations.append(
                f"Consider completing {len(incomplete_flows)} incomplete flows for better context"
            )
        
        # Check for missing themes
        covered_themes = set()
        for flow_data in loaded_flows.values():
            themes = flow_data.get("themes", {})
            covered_themes.update(themes.get("primary", []))
            covered_themes.update(themes.get("secondary", []))
        
        missing_themes = set(task_themes) - covered_themes
        if missing_themes:
            recommendations.append(
                f"Consider flows covering these themes: {', '.join(missing_themes)}"
            )
        
        # Performance recommendations
        total_flows_count = sum(len(data.get("flows", {})) for data in loaded_flows.values())
        if total_flows_count > 20:
            recommendations.append(
                "High flow count detected - consider more selective loading for performance"
            )
        
        return recommendations