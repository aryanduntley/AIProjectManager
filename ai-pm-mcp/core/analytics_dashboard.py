"""
Comprehensive Analytics Dashboard for AI Project Manager.

Provides unified analytics across sessions, tasks, themes, user preferences,
and overall project intelligence with predictive insights and recommendations.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

# Database components
from database.session_queries import SessionQueries
from database.task_status_queries import TaskStatusQueries
from database.theme_flow_queries import ThemeFlowQueries
from database.file_metadata_queries import FileMetadataQueries
from database.user_preference_queries import UserPreferenceQueries

logger = logging.getLogger(__name__)


@dataclass
class ProjectHealthMetrics:
    """Project health assessment metrics."""
    overall_health_score: float  # 0.0 to 1.0
    task_completion_rate: float
    session_productivity_score: float
    theme_organization_score: float
    user_adaptation_score: float
    technical_debt_indicators: List[str]
    optimization_opportunities: List[str]
    risk_factors: List[str]


@dataclass
class PredictiveInsights:
    """AI-driven predictive insights."""
    context_escalation_probability: float
    sidequest_likelihood: float
    completion_time_estimate: Dict[str, int]  # in minutes
    recommended_actions: List[str]
    warning_indicators: List[str]


class AnalyticsDashboard:
    """Comprehensive analytics dashboard for project intelligence."""
    
    def __init__(self, 
                 session_queries: SessionQueries,
                 task_queries: TaskStatusQueries, 
                 theme_flow_queries: ThemeFlowQueries,
                 file_metadata_queries: FileMetadataQueries,
                 user_preference_queries: UserPreferenceQueries):
        """Initialize dashboard with all database query components."""
        self.session_queries = session_queries
        self.task_queries = task_queries
        self.theme_flow_queries = theme_flow_queries
        self.file_metadata_queries = file_metadata_queries
        self.user_preference_queries = user_preference_queries
    
    async def get_comprehensive_dashboard(self, 
                                        project_path: str,
                                        time_range_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard for project intelligence."""
        try:
            dashboard = {
                "timestamp": datetime.utcnow().isoformat(),
                "project_path": project_path,
                "analysis_period_days": time_range_days,
                "project_health": {},
                "session_analytics": {},
                "task_performance": {},
                "theme_insights": {},
                "user_adaptation": {},
                "predictive_insights": {},
                "recommendations": [],
                "alerts": []
            }
            
            # Gather all analytics components
            dashboard["project_health"] = await self._get_project_health_metrics(time_range_days)
            dashboard["session_analytics"] = await self._get_session_analytics_comprehensive(time_range_days)
            dashboard["task_performance"] = await self._get_task_performance_analytics(time_range_days)
            dashboard["theme_insights"] = await self._get_theme_organization_insights(time_range_days)
            dashboard["user_adaptation"] = await self._get_user_adaptation_analytics(time_range_days)
            dashboard["predictive_insights"] = await self._generate_predictive_insights(time_range_days)
            
            # Generate unified recommendations
            dashboard["recommendations"] = await self._generate_unified_recommendations(dashboard)
            dashboard["alerts"] = await self._identify_alert_conditions(dashboard)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating comprehensive dashboard: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "project_path": project_path
            }
    
    async def _get_project_health_metrics(self, days: int) -> Dict[str, Any]:
        """Calculate overall project health metrics."""
        try:
            health_metrics = {
                "overall_health_score": 0.0,
                "component_scores": {},
                "health_trends": {},
                "critical_issues": [],
                "improvement_areas": []
            }
            
            # Task completion health
            task_metrics = self.task_queries.get_task_analytics(days=days)
            task_completion_rate = task_metrics.get("completion_rate", 0.0)
            health_metrics["component_scores"]["task_completion"] = task_completion_rate
            
            # Session productivity health
            session_metrics = self.session_queries.get_session_analytics_enhanced("", days=days)
            avg_productivity = session_metrics.get("productivity_score", 0.5)
            health_metrics["component_scores"]["session_productivity"] = avg_productivity
            
            # Theme organization health
            theme_metrics = self.theme_flow_queries.get_flow_completion_analytics()
            theme_org_score = min(theme_metrics.get("average_completion", 0.0) / 100.0, 1.0)
            health_metrics["component_scores"]["theme_organization"] = theme_org_score
            
            # User adaptation health
            adaptation_summary = self.user_preference_queries.get_user_adaptation_summary(days)
            total_prefs = adaptation_summary.get("total_preferences", 0)
            high_conf_prefs = adaptation_summary.get("high_confidence_preferences", 0)
            adaptation_score = min(high_conf_prefs / max(total_prefs, 1), 1.0) if total_prefs > 0 else 0.5
            health_metrics["component_scores"]["user_adaptation"] = adaptation_score
            
            # Calculate overall health score (weighted average)
            weights = {
                "task_completion": 0.35,
                "session_productivity": 0.25,
                "theme_organization": 0.20,
                "user_adaptation": 0.20
            }
            
            overall_score = sum(
                health_metrics["component_scores"][component] * weight
                for component, weight in weights.items()
            )
            health_metrics["overall_health_score"] = overall_score
            
            # Identify critical issues
            if task_completion_rate < 0.3:
                health_metrics["critical_issues"].append("Very low task completion rate")
            if avg_productivity < 0.4:
                health_metrics["critical_issues"].append("Low session productivity")
            if theme_org_score < 0.2:
                health_metrics["critical_issues"].append("Poor theme organization")
            
            # Identify improvement areas
            if health_metrics["component_scores"]["user_adaptation"] < 0.6:
                health_metrics["improvement_areas"].append("AI learning and user adaptation")
            if health_metrics["component_scores"]["session_productivity"] < 0.7:
                health_metrics["improvement_areas"].append("Session workflow optimization")
                
            return health_metrics
            
        except Exception as e:
            logger.error(f"Error calculating project health metrics: {e}")
            return {"error": str(e)}
    
    async def _get_session_analytics_comprehensive(self, days: int) -> Dict[str, Any]:
        """Get comprehensive session analytics."""
        try:
            session_analytics = self.session_queries.get_session_analytics_enhanced("", days=days)
            
            # Add context escalation analysis
            context_patterns = {
                "escalation_frequency": session_analytics.get("avg_escalations_per_session", 0),
                "escalation_success_rate": session_analytics.get("successful_escalations", 0) / max(session_analytics.get("total_escalations", 1), 1),
                "most_common_escalation": session_analytics.get("most_common_escalation_reason", "Unknown"),
                "escalation_trends": []
            }
            session_analytics["context_patterns"] = context_patterns
            
            # Add session efficiency metrics
            efficiency_metrics = {
                "avg_session_duration": session_analytics.get("average_session_duration", 0),
                "productive_sessions_ratio": session_analytics.get("productive_sessions", 0) / max(session_analytics.get("total_sessions", 1), 1),
                "context_switching_frequency": session_analytics.get("context_switches_per_session", 0),
                "boot_time_optimization": session_analytics.get("average_boot_time", 0)
            }
            session_analytics["efficiency_metrics"] = efficiency_metrics
            
            return session_analytics
            
        except Exception as e:
            logger.error(f"Error getting session analytics: {e}")
            return {"error": str(e)}
    
    async def _get_task_performance_analytics(self, days: int) -> Dict[str, Any]:
        """Get comprehensive task performance analytics."""
        try:
            task_analytics = self.task_queries.get_task_analytics(days=days)
            
            # Add sidequest analysis
            sidequest_metrics = {
                "sidequest_creation_rate": task_analytics.get("sidequests_per_task", 0),
                "sidequest_completion_rate": task_analytics.get("sidequest_completion_rate", 0),
                "avg_sidequests_per_task": task_analytics.get("avg_sidequests_per_task", 0),
                "most_sidequest_prone_themes": task_analytics.get("high_sidequest_themes", [])
            }
            task_analytics["sidequest_metrics"] = sidequest_metrics
            
            # Add performance trends
            performance_trends = {
                "velocity_trend": task_analytics.get("velocity_trend", "stable"),
                "complexity_trend": task_analytics.get("avg_complexity_trend", "stable"),
                "effort_estimation_accuracy": task_analytics.get("estimation_accuracy", 0.5),
                "blocker_resolution_time": task_analytics.get("avg_blocker_resolution_time", 0)
            }
            task_analytics["performance_trends"] = performance_trends
            
            return task_analytics
            
        except Exception as e:
            logger.error(f"Error getting task performance analytics: {e}")
            return {"error": str(e)}
    
    async def _get_theme_organization_insights(self, days: int) -> Dict[str, Any]:
        """Get theme organization and relationship insights."""
        try:
            theme_insights = self.theme_flow_queries.get_flow_completion_analytics()
            
            # Add relationship analysis
            relationship_analysis = {
                "most_connected_themes": theme_insights.get("highly_connected_themes", []),
                "isolated_themes": theme_insights.get("isolated_themes", []),
                "cross_theme_dependency_score": theme_insights.get("cross_theme_score", 0.5),
                "theme_utilization_balance": theme_insights.get("utilization_balance", 0.5)
            }
            theme_insights["relationship_analysis"] = relationship_analysis
            
            # Add evolution tracking
            evolution_metrics = {
                "theme_creation_rate": theme_insights.get("new_themes_per_month", 0),
                "theme_modification_frequency": theme_insights.get("theme_updates_per_month", 0),
                "theme_stability_score": theme_insights.get("stability_score", 0.5),
                "organization_maturity": theme_insights.get("organization_maturity", "developing")
            }
            theme_insights["evolution_metrics"] = evolution_metrics
            
            return theme_insights
            
        except Exception as e:
            logger.error(f"Error getting theme insights: {e}")
            return {"error": str(e)}
    
    async def _get_user_adaptation_analytics(self, days: int) -> Dict[str, Any]:
        """Get comprehensive user adaptation analytics."""
        try:
            adaptation_data = self.user_preference_queries.get_user_adaptation_summary(days)
            
            # Add learning velocity analysis
            learning_velocity = {
                "preferences_learned_per_week": adaptation_data.get("total_preferences", 0) / max(days / 7, 1),
                "learning_acceleration": adaptation_data.get("learning_trend", "stable"),
                "confidence_improvement_rate": adaptation_data.get("confidence_growth_rate", 0),
                "adaptation_effectiveness": adaptation_data.get("adaptation_effectiveness", 0.5)
            }
            adaptation_data["learning_velocity"] = learning_velocity
            
            # Add behavioral insights
            behavioral_insights = {
                "most_consistent_preferences": adaptation_data.get("stable_preferences", []),
                "changing_preferences": adaptation_data.get("evolving_preferences", []),
                "workflow_optimization_score": adaptation_data.get("workflow_optimization", 0.5),
                "ai_user_alignment_score": adaptation_data.get("alignment_score", 0.5)
            }
            adaptation_data["behavioral_insights"] = behavioral_insights
            
            return adaptation_data
            
        except Exception as e:
            logger.error(f"Error getting user adaptation analytics: {e}")
            return {"error": str(e)}
    
    async def _generate_predictive_insights(self, days: int) -> Dict[str, Any]:
        """Generate AI-driven predictive insights."""
        try:
            predictive_insights = {
                "context_escalation_predictions": {},
                "sidequest_predictions": {},
                "completion_predictions": {},
                "resource_predictions": {},
                "risk_predictions": []
            }
            
            # Context escalation predictions based on historical patterns
            session_data = self.session_queries.get_session_analytics_enhanced("", days=days)
            escalation_rate = session_data.get("avg_escalations_per_session", 0)
            
            predictive_insights["context_escalation_predictions"] = {
                "next_session_escalation_probability": min(escalation_rate / 2, 1.0),
                "high_escalation_task_types": ["debugging", "integration"],
                "escalation_time_prediction": int(escalation_rate * 15)  # minutes
            }
            
            # Sidequest predictions
            task_data = self.task_queries.get_task_analytics(days=days)
            sidequest_rate = task_data.get("sidequests_per_task", 0)
            
            predictive_insights["sidequest_predictions"] = {
                "next_task_sidequest_probability": min(sidequest_rate, 1.0),
                "sidequest_prone_themes": task_data.get("high_sidequest_themes", []),
                "expected_sidequests_per_task": round(sidequest_rate, 1)
            }
            
            # Completion time predictions
            avg_task_time = task_data.get("average_completion_time_hours", 2.0)
            session_productivity = session_data.get("productivity_score", 0.5)
            
            predictive_insights["completion_predictions"] = {
                "current_task_estimated_minutes": int(avg_task_time * 60 / max(session_productivity, 0.1)),
                "session_productivity_forecast": session_productivity,
                "optimal_work_periods": ["morning", "afternoon"] if session_productivity > 0.6 else ["afternoon"]
            }
            
            # Resource predictions
            theme_data = self.theme_flow_queries.get_flow_completion_analytics()
            
            predictive_insights["resource_predictions"] = {
                "context_memory_forecast": theme_data.get("estimated_memory_usage", 50),
                "theme_expansion_likelihood": 0.3 if theme_data.get("cross_theme_score", 0) > 0.5 else 0.1,
                "database_growth_rate": "moderate"
            }
            
            # Risk predictions
            risk_factors = []
            if escalation_rate > 1.0:
                risk_factors.append("High context escalation frequency indicates potential scope creep")
            if sidequest_rate > 2.0:
                risk_factors.append("High sidequest rate may indicate insufficient initial planning")
            if session_productivity < 0.4:
                risk_factors.append("Low productivity trend suggests workflow optimization needed")
                
            predictive_insights["risk_predictions"] = risk_factors
            
            return predictive_insights
            
        except Exception as e:
            logger.error(f"Error generating predictive insights: {e}")
            return {"error": str(e)}
    
    async def _generate_unified_recommendations(self, dashboard_data: Dict[str, Any]) -> List[str]:
        """Generate unified recommendations based on all analytics data."""
        try:
            recommendations = []
            
            # Health-based recommendations
            health = dashboard_data.get("project_health", {})
            overall_health = health.get("overall_health_score", 0.5)
            
            if overall_health < 0.6:
                recommendations.append("Consider workflow optimization - overall project health below optimal")
            
            # Task performance recommendations
            task_perf = dashboard_data.get("task_performance", {})
            completion_rate = task_perf.get("completion_rate", 0.5)
            
            if completion_rate < 0.7:
                recommendations.append("Focus on task completion - break down large tasks into smaller subtasks")
            
            # Session efficiency recommendations
            session_data = dashboard_data.get("session_analytics", {})
            efficiency = session_data.get("efficiency_metrics", {})
            
            if efficiency.get("context_switching_frequency", 0) > 3:
                recommendations.append("Reduce context switching - plan task sequences to minimize theme changes")
            
            # User adaptation recommendations
            adaptation = dashboard_data.get("user_adaptation", {})
            high_conf_prefs = adaptation.get("high_confidence_preferences", 0)
            
            if high_conf_prefs < 5:
                recommendations.append("Continue using the system regularly to improve AI adaptation to your workflow")
            
            # Predictive recommendations
            predictions = dashboard_data.get("predictive_insights", {})
            escalation_prob = predictions.get("context_escalation_predictions", {}).get("next_session_escalation_probability", 0)
            
            if escalation_prob > 0.7:
                recommendations.append("Consider starting with theme-expanded context mode for upcoming tasks")
            
            # Theme organization recommendations
            theme_insights = dashboard_data.get("theme_insights", {})
            if theme_insights.get("relationship_analysis", {}).get("isolated_themes"):
                recommendations.append("Review isolated themes for potential consolidation or better integration")
            
            return recommendations[:8]  # Limit to top 8 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [f"Error generating recommendations: {str(e)}"]
    
    async def _identify_alert_conditions(self, dashboard_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify conditions that require immediate attention."""
        try:
            alerts = []
            
            # Critical health alerts
            health = dashboard_data.get("project_health", {})
            if health.get("overall_health_score", 1.0) < 0.3:
                alerts.append({
                    "level": "critical",
                    "category": "project_health",
                    "message": "Project health critically low - immediate attention required",
                    "action_required": True
                })
            
            # Performance alerts
            task_perf = dashboard_data.get("task_performance", {})
            if task_perf.get("completion_rate", 1.0) < 0.2:
                alerts.append({
                    "level": "high",
                    "category": "task_performance", 
                    "message": "Task completion rate very low - review task complexity and planning",
                    "action_required": True
                })
            
            # Resource alerts
            predictions = dashboard_data.get("predictive_insights", {})
            memory_forecast = predictions.get("resource_predictions", {}).get("context_memory_forecast", 0)
            if memory_forecast > 200:
                alerts.append({
                    "level": "medium",
                    "category": "resource_usage",
                    "message": "High memory usage predicted - consider context optimization",
                    "action_required": False
                })
            
            # Risk alerts
            risk_predictions = predictions.get("risk_predictions", [])
            if len(risk_predictions) > 2:
                alerts.append({
                    "level": "medium",
                    "category": "risk_management",
                    "message": f"Multiple risk factors identified: {len(risk_predictions)} issues",
                    "action_required": False
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error identifying alerts: {e}")
            return [{
                "level": "error",
                "category": "system",
                "message": f"Error in alert system: {str(e)}",
                "action_required": False
            }]
    
    async def get_quick_status_summary(self, project_path: str) -> Dict[str, Any]:
        """Get a quick status summary for session boot or quick checks."""
        try:
            summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "project_path": project_path,
                "health_score": 0.0,
                "active_tasks": 0,
                "session_status": "unknown",
                "urgent_alerts": 0,
                "top_recommendation": "",
                "quick_stats": {}
            }
            
            # Quick health check (last 7 days)
            health_metrics = await self._get_project_health_metrics(7)
            summary["health_score"] = health_metrics.get("overall_health_score", 0.0)
            
            # Active task count
            task_data = self.task_queries.get_task_analytics(days=7)
            summary["active_tasks"] = task_data.get("active_tasks", 0)
            
            # Recent session status
            session_data = self.session_queries.get_session_analytics_enhanced("", days=1)
            summary["session_status"] = "productive" if session_data.get("productivity_score", 0) > 0.6 else "needs_optimization"
            
            # Quick stats
            summary["quick_stats"] = {
                "tasks_completed_week": task_data.get("completed_tasks", 0),
                "avg_session_duration": session_data.get("average_session_duration", 0),
                "preference_confidence": self.user_preference_queries.get_user_adaptation_summary(7).get("high_confidence_preferences", 0)
            }
            
            # Top recommendation
            if summary["health_score"] < 0.6:
                summary["top_recommendation"] = "Focus on completing existing tasks to improve project health"
            elif summary["active_tasks"] > 5:
                summary["top_recommendation"] = "Consider prioritizing tasks to avoid context switching"
            else:
                summary["top_recommendation"] = "Project status good - continue current workflow"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating quick status summary: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "project_path": project_path
            }