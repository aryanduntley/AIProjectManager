"""
Enhanced tool handlers and advanced intelligence features for MCP API.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from mcp.types import TextContent

# We'll access ToolDefinition through the tool_registry instead to avoid circular imports
# from ..mcp_api import ToolDefinition

logger = logging.getLogger(__name__)


class EnhancedToolHandlers:
    """Handles enhanced tool registration and execution."""
    
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
    
    # Delegate to main registry attributes
    @property
    def tools(self):
        return self.tool_registry.tools
    
    @property  
    def tool_handlers(self):
        return self.tool_registry.tool_handlers
        
    @property
    def analytics_dashboard(self):
        return self.tool_registry.analytics_dashboard
        
    @property
    def user_preference_queries(self):
        return self.tool_registry.user_preference_queries
        
    @property
    def scope_engine(self):
        return self.tool_registry.scope_engine
        
    @property
    def task_processor(self):
        return self.tool_registry.task_processor
    
    async def _register_enhanced_core_tools(self):
        """Register enhanced core processing tools."""
        try:
            # Access ToolDefinition through the main registry to avoid import issues
            # The main mcp_api.py has proper dependency isolation
            ToolDefinition = self.tool_registry.ToolDefinition
            
            # Enhanced context loading tool
            self.tools["context_load_enhanced"] = ToolDefinition(
                name="context_load_enhanced",
                description="Load project context with database optimization and intelligent recommendations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "primary_theme": {
                            "type": "string",
                            "description": "Primary theme for context loading"
                        },
                        "context_mode": {
                            "type": "string",
                            "enum": ["theme-focused", "theme-expanded", "project-wide"],
                            "default": "theme-focused",
                            "description": "Context loading mode"
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Optional task ID for context tracking"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for analytics tracking"
                        }
                    },
                    "required": ["project_path", "primary_theme"]
                }
            )
            self.tool_handlers["context_load_enhanced"] = self._handle_enhanced_context_loading
            
            # Task processing tool
            self.tools["task_process"] = ToolDefinition(
                name="task_process",
                description="Process a task with intelligent context resolution and execution coordination",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "task_data": {
                            "type": "object",
                            "description": "Task data including taskId, description, theme, subtasks"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for processing"
                        }
                    },
                    "required": ["project_path", "task_data", "session_id"]
                }
            )
            self.tool_handlers["task_process"] = self._handle_task_processing
            
            # Flow context optimization tool
            self.tools["flow_context_optimize"] = ToolDefinition(
                name="flow_context_optimize",
                description="Get optimized context for specific flows using database relationships",
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
                            "description": "List of flow IDs to optimize context for"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Optional session ID for tracking"
                        }
                    },
                    "required": ["project_path", "flow_ids"]
                }
            )
            self.tool_handlers["flow_context_optimize"] = self._handle_flow_context_optimization
            
            # Intelligent recommendations tool
            self.tools["context_recommendations"] = ToolDefinition(
                name="context_recommendations",
                description="Get intelligent context recommendations based on task and historical data",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "current_theme": {
                            "type": "string",
                            "description": "Current primary theme"
                        },
                        "current_mode": {
                            "type": "string",
                            "enum": ["theme-focused", "theme-expanded", "project-wide"],
                            "description": "Current context mode"
                        },
                        "task_description": {
                            "type": "string",
                            "description": "Description of the current task"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for historical analysis"
                        }
                    },
                    "required": ["project_path", "current_theme", "current_mode", "task_description"]
                }
            )
            self.tool_handlers["context_recommendations"] = self._handle_context_recommendations
            
            # Processing analytics tool
            self.tools["processing_analytics"] = ToolDefinition(
                name="processing_analytics",
                description="Get processing analytics for performance optimization and insights",
                input_schema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID for analytics"
                        },
                        "time_range_hours": {
                            "type": "integer",
                            "default": 24,
                            "description": "Time range in hours for analytics"
                        }
                    },
                    "required": ["session_id"]
                }
            )
            self.tool_handlers["processing_analytics"] = self._handle_processing_analytics
            
            # Advanced Intelligence Tools (Phase 5)
            if self.analytics_dashboard:
                # Comprehensive analytics dashboard
                self.tools["analytics_dashboard"] = ToolDefinition(
                    name="analytics_dashboard", 
                    description="Get comprehensive project analytics dashboard with predictive insights",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path to the project directory"
                            },
                            "time_range_days": {
                                "type": "integer",
                                "default": 30,
                                "description": "Time range in days for analytics"
                            }
                        },
                        "required": ["project_path"]
                    }
                )
                self.tool_handlers["analytics_dashboard"] = self._handle_analytics_dashboard
                
                # Quick status summary
                self.tools["quick_status"] = ToolDefinition(
                    name="quick_status",
                    description="Get quick project status summary for session boot or health checks",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string", 
                                "description": "Path to the project directory"
                            }
                        },
                        "required": ["project_path"]
                    }
                )
                self.tool_handlers["quick_status"] = self._handle_quick_status
            
            # User preference learning tools
            if self.user_preference_queries:
                # Learn from user decisions
                self.tools["learn_preference"] = ToolDefinition(
                    name="learn_preference",
                    description="Learn user preferences from decisions and behavior",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "preference_type": {
                                "type": "string",
                                "enum": ["context", "theme", "workflow"],
                                "description": "Type of preference to learn"
                            },
                            "preference_data": {
                                "type": "object",
                                "description": "Data about the preference decision"
                            }
                        },
                        "required": ["preference_type", "preference_data"]
                    }
                )
                self.tool_handlers["learn_preference"] = self._handle_learn_preference
                
                # Get recommendations
                self.tools["get_recommendations"] = ToolDefinition(
                    name="get_recommendations",
                    description="Get intelligent recommendations based on learned user preferences",
                    input_schema={
                        "type": "object", 
                        "properties": {
                            "recommendation_type": {
                                "type": "string",
                                "enum": ["context", "theme", "workflow"],
                                "description": "Type of recommendations to get"
                            },
                            "context_data": {
                                "type": "object",
                                "description": "Current context for recommendations"
                            }
                        },
                        "required": ["recommendation_type", "context_data"]
                    }
                )
                self.tool_handlers["get_recommendations"] = self._handle_get_recommendations
            
            logger.info("Enhanced core processing tools and advanced intelligence registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering enhanced core tools: {e}")
    
    # Enhanced core tool handlers
    
    async def _handle_enhanced_context_loading(self, arguments: Dict[str, Any]) -> str:
        """Handle enhanced context loading with database optimization."""
        try:
            project_path = Path(arguments["project_path"])
            primary_theme = arguments["primary_theme"]
            context_mode = arguments.get("context_mode", "theme-focused")
            task_id = arguments.get("task_id")
            session_id = arguments.get("session_id")
            
            from core.scope_engine import ContextMode
            mode = ContextMode(context_mode)
            
            context = await self.scope_engine.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=primary_theme,
                context_mode=mode,
                task_id=task_id,
                session_id=session_id
            )
            
            summary = await self.scope_engine.get_context_summary(context)
            
            return f"Enhanced context loaded successfully:\n\n{summary}"
            
        except Exception as e:
            logger.error(f"Error in enhanced context loading: {e}")
            return f"Error loading enhanced context: {str(e)}"
    
    async def _handle_task_processing(self, arguments: Dict[str, Any]) -> str:
        """Handle intelligent task processing."""
        try:
            project_path = Path(arguments["project_path"])
            task_data = arguments["task_data"]
            session_id = arguments["session_id"]
            
            result = await self.task_processor.process_task(
                project_path=project_path,
                task_data=task_data,
                session_id=session_id
            )
            
            summary = (
                f"Task Processing Result: {result.result.value}\n"
                f"Task ID: {result.task_id}\n"
                f"Execution Time: {result.execution_time_ms}ms\n"
                f"Context Mode: {result.context_used.mode.value if result.context_used else 'None'}\n"
                f"Recommendations: {len(result.recommendations)}\n"
                f"Next Actions: {len(result.next_actions)}\n"
            )
            
            if result.recommendations:
                summary += "\nRecommendations:\n" + "\n".join(f"- {rec}" for rec in result.recommendations)
            
            if result.next_actions:
                summary += "\nNext Actions:\n" + "\n".join(f"- {action}" for action in result.next_actions)
            
            if result.errors:
                summary += "\nErrors:\n" + "\n".join(f"- {error}" for error in result.errors)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in task processing: {e}")
            return f"Error processing task: {str(e)}"
    
    async def _handle_flow_context_optimization(self, arguments: Dict[str, Any]) -> str:
        """Handle flow context optimization."""
        try:
            project_path = Path(arguments["project_path"])
            flow_ids = arguments["flow_ids"]
            session_id = arguments.get("session_id")
            
            context_data = await self.scope_engine.get_optimized_flow_context(
                project_path=project_path,
                flow_ids=flow_ids,
                session_id=session_id
            )
            
            if "error" in context_data:
                return f"Error optimizing flow context: {context_data['error']}"
            
            summary = (
                f"Flow Context Optimization Results:\n"
                f"Flows analyzed: {len(flow_ids)}\n"
                f"Related themes: {len(context_data.get('related_themes', []))}\n"
                f"Cross-flow dependencies: {len(context_data.get('cross_flow_dependencies', []))}\n"
                f"Recommended context mode: {context_data.get('recommended_context_mode')}\n"
            )
            
            if context_data.get("related_themes"):
                summary += f"\nRelated themes: {', '.join(context_data['related_themes'])}"
            
            if context_data.get("cross_flow_dependencies"):
                summary += f"\nCross-flow dependencies: {len(context_data['cross_flow_dependencies'])} found"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in flow context optimization: {e}")
            return f"Error optimizing flow context: {str(e)}"
    
    async def _handle_context_recommendations(self, arguments: Dict[str, Any]) -> str:
        """Handle intelligent context recommendations."""
        try:
            project_path = Path(arguments["project_path"])
            current_theme = arguments["current_theme"]
            current_mode = arguments["current_mode"]
            task_description = arguments["task_description"]
            session_id = arguments.get("session_id")
            
            # Load current context first
            from core.scope_engine import ContextMode
            mode = ContextMode(current_mode)
            
            current_context = await self.scope_engine.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=current_theme,
                context_mode=mode,
                session_id=session_id
            )
            
            recommendations = await self.scope_engine.get_intelligent_context_recommendations(
                project_path=project_path,
                current_context=current_context,
                task_description=task_description,
                session_id=session_id
            )
            
            if "error" in recommendations:
                return f"Error generating recommendations: {recommendations['error']}"
            
            summary = "Intelligent Context Recommendations:\n\n"
            
            # Current assessment
            assessment = recommendations.get("current_assessment", {})
            if assessment:
                summary += f"Current Assessment:\n"
                summary += f"- Mode: {assessment.get('mode')}\n"
                summary += f"- Themes loaded: {assessment.get('themes_loaded')}\n"
                summary += f"- Files available: {assessment.get('files_available')}\n"
                summary += f"- Memory usage: {assessment.get('memory_usage')}MB\n"
                summary += f"- Coverage score: {assessment.get('coverage_score')}\n\n"
            
            # Escalation recommendations
            escalation_recs = recommendations.get("escalation_recommendations", [])
            if escalation_recs:
                summary += "Escalation Recommendations:\n"
                for rec in escalation_recs:
                    summary += f"- {rec.get('reason', 'No reason')}: {rec.get('suggested_mode', 'No suggestion')}\n"
                summary += "\n"
            
            # Flow suggestions
            flow_suggestions = recommendations.get("flow_suggestions", [])
            if flow_suggestions:
                summary += "Flow Suggestions:\n"
                for suggestion in flow_suggestions:
                    summary += f"- {suggestion.get('flow_id')}: {suggestion.get('suggestion')}\n"
                summary += "\n"
            
            # Memory optimization
            memory_opts = recommendations.get("memory_optimization", [])
            if memory_opts:
                summary += "Memory Optimization:\n"
                for opt in memory_opts:
                    summary += f"- {opt.get('issue')}: {opt.get('current_usage')}MB\n"
                    for sugg in opt.get('suggestions', []):
                        summary += f"  * {sugg}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in context recommendations: {e}")
            return f"Error generating context recommendations: {str(e)}"
    
    async def _handle_processing_analytics(self, arguments: Dict[str, Any]) -> str:
        """Handle processing analytics."""
        try:
            session_id = arguments["session_id"]
            time_range_hours = arguments.get("time_range_hours", 24)
            
            analytics = await self.task_processor.get_processing_analytics(
                session_id=session_id,
                time_range_hours=time_range_hours
            )
            
            if "error" in analytics:
                return f"Error generating analytics: {analytics['error']}"
            
            summary = f"Processing Analytics (Last {time_range_hours} hours):\n\n"
            
            # Session summary
            session_summary = analytics.get("session_summary", {})
            if session_summary:
                summary += "Session Summary:\n"
                summary += f"- Total sessions: {session_summary.get('total_sessions', 0)}\n"
                summary += f"- Active time: {session_summary.get('total_active_time_hours', 0):.1f}h\n"
                summary += f"- Average session: {session_summary.get('average_session_duration_minutes', 0):.1f}min\n\n"
            
            # Context usage
            context_usage = analytics.get("context_usage", {})
            if context_usage:
                summary += "Context Usage:\n"
                summary += f"- Average memory: {context_usage.get('average_memory_mb', 0):.1f}MB\n"
                summary += f"- Most used mode: {context_usage.get('most_used_mode', 'N/A')}\n"
                summary += f"- Escalations: {context_usage.get('escalation_count', 0)}\n\n"
            
            # Task performance
            task_performance = analytics.get("task_performance", {})
            if task_performance:
                summary += "Task Performance:\n"
                summary += f"- Tasks completed: {task_performance.get('completed_tasks', 0)}\n"
                summary += f"- Average processing time: {task_performance.get('average_processing_time_ms', 0)}ms\n"
                summary += f"- Success rate: {task_performance.get('success_rate', 0):.1%}\n\n"
            
            # Recommendations
            recommendations = analytics.get("recommendations", [])
            if recommendations:
                summary += "Recommendations:\n"
                for rec in recommendations:
                    summary += f"- {rec}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in processing analytics: {e}")
            return f"Error generating processing analytics: {str(e)}"
    
    # Advanced Intelligence Tool Handlers (Phase 5)
    
    async def _handle_analytics_dashboard(self, arguments: Dict[str, Any]) -> str:
        """Handle comprehensive analytics dashboard request."""
        try:
            project_path = arguments["project_path"]
            time_range_days = arguments.get("time_range_days", 30)
            
            if not self.analytics_dashboard:
                return "Analytics dashboard not available - database not initialized"
            
            dashboard_data = await self.analytics_dashboard.get_comprehensive_dashboard(
                project_path=project_path,
                time_range_days=time_range_days
            )
            
            if "error" in dashboard_data:
                return f"Error generating dashboard: {dashboard_data['error']}"
            
            # Format dashboard summary
            summary = f"📊 **Comprehensive Analytics Dashboard**\n\n"
            summary += f"**Analysis Period**: {time_range_days} days\n"
            summary += f"**Generated**: {dashboard_data.get('timestamp', 'Unknown')}\n\n"
            
            # Project Health
            health = dashboard_data.get("project_health", {})
            health_score = health.get("overall_health_score", 0.0)
            health_emoji = "🟢" if health_score > 0.7 else "🟡" if health_score > 0.4 else "🔴"
            summary += f"**Project Health**: {health_emoji} {health_score:.1%}\n"
            
            # Key Metrics
            session_data = dashboard_data.get("session_analytics", {})
            task_data = dashboard_data.get("task_performance", {})
            
            summary += f"**Session Productivity**: {session_data.get('productivity_score', 0.0):.1%}\n"
            summary += f"**Task Completion Rate**: {task_data.get('completion_rate', 0.0):.1%}\n"
            summary += f"**Active Tasks**: {task_data.get('active_tasks', 0)}\n\n"
            
            # Predictions
            predictions = dashboard_data.get("predictive_insights", {})
            if predictions:
                summary += "**🔮 Predictive Insights**:\n"
                escalation_prob = predictions.get("context_escalation_predictions", {}).get("next_session_escalation_probability", 0)
                summary += f"- Context escalation probability: {escalation_prob:.1%}\n"
                
                sidequest_prob = predictions.get("sidequest_predictions", {}).get("next_task_sidequest_probability", 0)
                summary += f"- Sidequest likelihood: {sidequest_prob:.1%}\n\n"
            
            # Top Recommendations
            recommendations = dashboard_data.get("recommendations", [])
            if recommendations:
                summary += "**💡 Top Recommendations**:\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    summary += f"{i}. {rec}\n"
                summary += "\n"
            
            # Alerts
            alerts = dashboard_data.get("alerts", [])
            if alerts:
                summary += "**⚠️ Alerts**:\n"
                for alert in alerts:
                    level_emoji = "🚨" if alert.get("level") == "critical" else "⚠️" if alert.get("level") == "high" else "ℹ️"
                    summary += f"{level_emoji} {alert.get('message', 'No message')}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in analytics dashboard: {e}")
            return f"Error generating analytics dashboard: {str(e)}"
    
    async def _handle_quick_status(self, arguments: Dict[str, Any]) -> str:
        """Handle quick status summary request."""
        try:
            project_path = arguments["project_path"]
            
            if not self.analytics_dashboard:
                return "Quick status not available - database not initialized"
            
            status_data = await self.analytics_dashboard.get_quick_status_summary(project_path)
            
            if "error" in status_data:
                return f"Error getting status: {status_data['error']}"
            
            # Format quick status
            health_score = status_data.get("health_score", 0.0)
            health_emoji = "🟢" if health_score > 0.7 else "🟡" if health_score > 0.4 else "🔴"
            
            summary = f"**Quick Project Status** {health_emoji}\n\n"
            summary += f"**Health Score**: {health_score:.1%}\n"
            summary += f"**Active Tasks**: {status_data.get('active_tasks', 0)}\n"
            summary += f"**Session Status**: {status_data.get('session_status', 'unknown')}\n"
            
            quick_stats = status_data.get("quick_stats", {})
            summary += f"**Tasks Completed (week)**: {quick_stats.get('tasks_completed_week', 0)}\n"
            summary += f"**Avg Session Duration**: {quick_stats.get('avg_session_duration', 0):.1f}h\n\n"
            
            summary += f"**💡 Recommendation**: {status_data.get('top_recommendation', 'Continue current workflow')}\n"
            
            urgent_alerts = status_data.get("urgent_alerts", 0)
            if urgent_alerts > 0:
                summary += f"**⚠️ Urgent Alerts**: {urgent_alerts}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in quick status: {e}")
            return f"Error getting quick status: {str(e)}"
    
    async def _handle_learn_preference(self, arguments: Dict[str, Any]) -> str:
        """Handle learning user preferences."""
        try:
            preference_type = arguments["preference_type"]
            preference_data = arguments["preference_data"]
            
            if not self.user_preference_queries:
                return "User preference learning not available - database not initialized"
            
            if preference_type == "context":
                result = self.user_preference_queries.learn_context_preference(preference_data)
            elif preference_type == "theme":
                result = self.user_preference_queries.learn_theme_preference(preference_data)
            elif preference_type == "workflow":
                result = self.user_preference_queries.learn_workflow_preference(preference_data)
            else:
                # Track general feedback
                result = self.user_preference_queries.track_decision_feedback(preference_data)
            
            return f"✅ Preference Learning: {result}"
            
        except Exception as e:
            logger.error(f"Error learning preference: {e}")
            return f"Error learning preference: {str(e)}"
    
    async def _handle_get_recommendations(self, arguments: Dict[str, Any]) -> str:
        """Handle getting intelligent recommendations."""
        try:
            recommendation_type = arguments["recommendation_type"]
            context_data = arguments["context_data"]
            
            if not self.user_preference_queries:
                return "Recommendations not available - database not initialized"
            
            if recommendation_type == "context":
                recommendations = self.user_preference_queries.get_context_recommendations(context_data)
                
                if recommendations.get("should_suggest", False):
                    return (f"🎯 **Context Recommendation**: {recommendations.get('recommended_mode')}\n"
                           f"**Confidence**: {recommendations.get('confidence', 0):.1%}\n"
                           f"**Reason**: {recommendations.get('reason', 'No reason provided')}")
                else:
                    return f"ℹ️ Context analysis complete - {recommendations.get('reason', 'No specific recommendations')}"
            
            elif recommendation_type == "theme":
                recommendations = self.user_preference_queries.get_theme_recommendations(context_data)
                
                summary = "🎨 **Theme Recommendations**:\n"
                if recommendations.get("suggested_themes"):
                    summary += f"**Suggested**: {', '.join(recommendations['suggested_themes'])}\n"
                if recommendations.get("avoid_themes"):
                    summary += f"**Avoid**: {', '.join(recommendations['avoid_themes'])}\n"
                summary += f"**Confidence**: {recommendations.get('confidence', 0):.1%}\n"
                
                return summary
            
            elif recommendation_type == "workflow":
                recommendations = self.user_preference_queries.get_workflow_recommendations(context_data)
                
                summary = "⚡ **Workflow Recommendations**:\n"
                summary += f"**Batch Size**: {recommendations.get('recommended_batch_size', 3)} tasks\n"
                summary += f"**Escalation Threshold**: {recommendations.get('escalation_threshold', 0.7):.1%}\n"
                summary += f"**Sidequest Tolerance**: {recommendations.get('sidequest_tolerance', 2)}\n"
                summary += f"**Confidence**: {recommendations.get('confidence', 0):.1%}\n"
                
                return summary
            
            return f"Unknown recommendation type: {recommendation_type}"
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return f"Error getting recommendations: {str(e)}"