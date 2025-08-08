"""
Session Analytics
Handles session analytics, context escalation logging, and performance tracking.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from ..db_manager import DatabaseManager


class SessionAnalytics:
    """Manages session analytics and performance tracking."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get overall session statistics.
        
        Returns:
            Dict[str, Any]: Session statistics
        """
        try:
            query = """
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN archived_at IS NULL THEN 1 END) as active_sessions,
                AVG(CASE 
                    WHEN archived_at IS NOT NULL 
                    THEN (julianday(archived_at) - julianday(start_time)) * 24 * 60
                    ELSE (julianday('now') - julianday(start_time)) * 24 * 60
                END) as avg_duration_minutes,
                COUNT(DISTINCT project_path) as unique_projects
            FROM sessions
            """
            
            result = self.db.execute_query(query)
            
            if result:
                row = result[0]
                return {
                    "total_sessions": row[0] or 0,
                    "active_sessions": row[1] or 0,
                    "archived_sessions": (row[0] or 0) - (row[1] or 0),
                    "avg_session_duration_minutes": round(row[2] or 0, 2),
                    "unique_projects": row[3] or 0,
                    "generated_at": datetime.now().isoformat()
                }
            
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "archived_sessions": 0,
                "avg_session_duration_minutes": 0,
                "unique_projects": 0,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting session statistics: {e}")
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "archived_sessions": 0,
                "avg_session_duration_minutes": 0,
                "unique_projects": 0,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def log_context_escalation(self, session_id: str, from_mode: str, to_mode: str, 
                              reason: str, theme_name: str = None, task_id: str = None):
        """
        Log context escalation event for analytics.
        
        Args:
            session_id: Session ID
            from_mode: Original context mode
            to_mode: New context mode
            reason: Reason for escalation
            theme_name: Theme being worked on (optional)
            task_id: Task being worked on (optional)
        """
        try:
            event_data = {
                "from_mode": from_mode,
                "to_mode": to_mode,
                "reason": reason,
                "theme_name": theme_name,
                "task_id": task_id
            }
            
            query = """
            INSERT INTO noteworthy_events (
                event_type, primary_theme, task_id, work_period_id, 
                impact_level, decision_data, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                "context_escalation",
                theme_name or "unknown",
                task_id,
                session_id,
                "medium",
                json.dumps(event_data),
                datetime.now().isoformat()
            )
            
            self.db.execute_update(query, params)
            
        except Exception as e:
            print(f"Error logging context escalation: {e}")
    
    def get_session_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive session analytics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Session analytics data
        """
        try:
            # Session overview
            session_query = """
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN archived_at IS NULL THEN 1 END) as active_sessions,
                AVG(CASE 
                    WHEN archived_at IS NOT NULL 
                    THEN (julianday(archived_at) - julianday(start_time)) * 24 * 60
                    ELSE (julianday('now') - julianday(start_time)) * 24 * 60
                END) as avg_duration_minutes,
                COUNT(DISTINCT project_path) as unique_projects
            FROM sessions
            WHERE start_time >= datetime('now', '-{} days')
            """.format(days)
            
            session_result = self.db.execute_query(session_query)
            
            # Context mode distribution
            context_query = """
            SELECT context_mode, COUNT(*) as count
            FROM sessions
            WHERE start_time >= datetime('now', '-{} days')
            GROUP BY context_mode
            ORDER BY count DESC
            """.format(days)
            
            context_result = self.db.execute_query(context_query)
            
            # Context escalations
            escalation_query = """
            SELECT COUNT(*) as escalation_count,
                   AVG(json_extract(decision_data, '$.from_mode')) as from_mode,
                   AVG(json_extract(decision_data, '$.to_mode')) as to_mode
            FROM noteworthy_events
            WHERE event_type = 'context_escalation'
            AND created_at >= datetime('now', '-{} days')
            """.format(days)
            
            escalation_result = self.db.execute_query(escalation_query)
            
            # Build analytics response
            analytics = {
                "analysis_period_days": days,
                "session_overview": {},
                "context_modes": {},
                "escalations": {},
                "generated_at": datetime.now().isoformat()
            }
            
            # Process session overview
            if session_result:
                row = session_result[0]
                analytics["session_overview"] = {
                    "total_sessions": row[0] or 0,
                    "active_sessions": row[1] or 0,
                    "archived_sessions": (row[0] or 0) - (row[1] or 0),
                    "avg_duration_minutes": round(row[2] or 0, 2),
                    "unique_projects": row[3] or 0
                }
            
            # Process context mode distribution
            if context_result:
                mode_distribution = {}
                total_sessions = sum(row[1] for row in context_result)
                
                for row in context_result:
                    mode = row[0] or "unknown"
                    count = row[1]
                    percentage = (count / total_sessions * 100) if total_sessions > 0 else 0
                    
                    mode_distribution[mode] = {
                        "count": count,
                        "percentage": round(percentage, 2)
                    }
                
                analytics["context_modes"] = mode_distribution
            
            # Process escalations
            if escalation_result:
                row = escalation_result[0]
                analytics["escalations"] = {
                    "total_escalations": row[0] or 0,
                    "escalation_rate": (row[0] / analytics["session_overview"].get("total_sessions", 1) * 100) if analytics["session_overview"].get("total_sessions", 0) > 0 else 0
                }
            
            return analytics
            
        except Exception as e:
            print(f"Error getting session analytics: {e}")
            return {
                "analysis_period_days": days,
                "session_overview": {},
                "context_modes": {},
                "escalations": {},
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def get_session_analytics_enhanced(self, project_path: str, days: int = 30) -> Dict[str, Any]:
        """
        Get enhanced session analytics for a specific project.
        
        Args:
            project_path: Project path to analyze
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Enhanced analytics data
        """
        try:
            # Project-specific session analytics
            session_query = """
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN archived_at IS NULL THEN 1 END) as active_sessions,
                AVG(CASE 
                    WHEN archived_at IS NOT NULL 
                    THEN (julianday(archived_at) - julianday(start_time)) * 24 * 60
                    ELSE (julianday('now') - julianday(start_time)) * 24 * 60
                END) as avg_duration_minutes
            FROM sessions
            WHERE project_path = ? AND start_time >= datetime('now', '-{} days')
            """.format(days)
            
            session_result = self.db.execute_query(session_query, (project_path,))
            
            # Theme usage analytics
            theme_query = """
            SELECT 
                json_each.value as theme_name,
                COUNT(*) as usage_count
            FROM sessions, json_each(active_themes)
            WHERE project_path = ? AND start_time >= datetime('now', '-{} days')
            GROUP BY json_each.value
            ORDER BY usage_count DESC
            LIMIT 10
            """.format(days)
            
            theme_result = self.db.execute_query(theme_query, (project_path,))
            
            # Build enhanced analytics
            analytics = {
                "project_path": project_path,
                "analysis_period_days": days,
                "session_summary": {},
                "theme_usage": {},
                "performance_metrics": {},
                "generated_at": datetime.now().isoformat()
            }
            
            # Process session summary
            if session_result:
                row = session_result[0]
                analytics["session_summary"] = {
                    "total_sessions": row[0] or 0,
                    "active_sessions": row[1] or 0,
                    "avg_duration_minutes": round(row[2] or 0, 2)
                }
            
            # Process theme usage
            if theme_result:
                theme_usage = {}
                total_usage = sum(row[1] for row in theme_result)
                
                for row in theme_result:
                    theme_name = row[0]
                    count = row[1]
                    percentage = (count / total_usage * 100) if total_usage > 0 else 0
                    
                    theme_usage[theme_name] = {
                        "usage_count": count,
                        "usage_percentage": round(percentage, 2)
                    }
                
                analytics["theme_usage"] = theme_usage
            
            # Add performance metrics
            analytics["performance_metrics"] = {
                "avg_session_efficiency": self._calculate_session_efficiency(project_path, days),
                "context_stability": self._calculate_context_stability(project_path, days)
            }
            
            return analytics
            
        except Exception as e:
            print(f"Error getting enhanced session analytics: {e}")
            return {
                "project_path": project_path,
                "analysis_period_days": days,
                "session_summary": {},
                "theme_usage": {},
                "performance_metrics": {},
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _calculate_session_efficiency(self, project_path: str, days: int) -> float:
        """Calculate session efficiency metric."""
        # Placeholder for efficiency calculation
        # Could be based on tasks completed vs time spent
        return 75.5  # Placeholder value
    
    def _calculate_context_stability(self, project_path: str, days: int) -> float:
        """Calculate context stability metric."""
        # Placeholder for context stability calculation
        # Could be based on frequency of context escalations
        return 82.3  # Placeholder value