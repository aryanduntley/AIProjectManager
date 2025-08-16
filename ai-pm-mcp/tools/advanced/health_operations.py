"""
System health operations for the AI Project Manager.

Handles comprehensive system health checks across all components.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ...core.performance_optimizer import LargeProjectOptimizer
from ...core.error_recovery import ErrorRecoveryManager
from ...core.audit_system import AuditTrail
from ...database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class HealthOperations:
    """System health check operations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager

    async def system_health_check(self, arguments: Dict[str, Any]) -> str:
        """Run comprehensive system health check."""
        try:
            project_path = Path(arguments["project_path"])
            include_performance = arguments.get("include_performance", True)
            include_recovery = arguments.get("include_recovery", True)
            include_audit = arguments.get("include_audit", True)
            
            if not self.db_manager:
                return "Database not available. System health check requires database connection."
            
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "components": {},
                "issues": [],
                "warnings": []
            }
            
            # Performance health check
            if include_performance:
                try:
                    optimizer = LargeProjectOptimizer(project_path, self.db_manager)
                    perf_recommendations = optimizer.get_optimization_recommendations()
                    
                    if perf_recommendations["success"]:
                        recommendations = perf_recommendations["recommendations"]
                        high_priority_issues = [r for r in recommendations if r["priority"] == "high"]
                        
                        health_report["components"]["performance"] = {
                            "status": "issues" if high_priority_issues else "healthy",
                            "recommendations": len(recommendations),
                            "high_priority_issues": len(high_priority_issues)
                        }
                        
                        if high_priority_issues:
                            health_report["issues"].extend([r["description"] for r in high_priority_issues])
                    else:
                        health_report["components"]["performance"] = {"status": "error", "error": perf_recommendations.get("error")}
                        health_report["issues"].append("Performance analysis failed")
                        
                except Exception as e:
                    health_report["components"]["performance"] = {"status": "error", "error": str(e)}
                    health_report["issues"].append(f"Performance check failed: {str(e)}")
            
            # Recovery system health check
            if include_recovery:
                try:
                    recovery_manager = ErrorRecoveryManager(project_path, self.db_manager)
                    recovery_status = recovery_manager.get_recovery_status()
                    
                    if recovery_status["success"]:
                        total_recovery_points = recovery_status["recovery_points"]["total"]
                        total_backups = recovery_status["backups"]["total"]
                        
                        health_report["components"]["recovery"] = {
                            "status": "healthy" if total_recovery_points > 0 else "warning",
                            "recovery_points": total_recovery_points,
                            "backups": total_backups
                        }
                        
                        if total_recovery_points == 0:
                            health_report["warnings"].append("No recovery points available")
                    else:
                        health_report["components"]["recovery"] = {"status": "error", "error": recovery_status.get("error")}
                        health_report["issues"].append("Recovery system check failed")
                        
                except Exception as e:
                    health_report["components"]["recovery"] = {"status": "error", "error": str(e)}
                    health_report["issues"].append(f"Recovery check failed: {str(e)}")
            
            # Audit system health check
            if include_audit:
                try:
                    audit_trail = AuditTrail(project_path, self.db_manager)
                    audit_status = audit_trail.get_audit_system_status()
                    
                    if audit_status["success"]:
                        status_info = audit_status["status"]
                        
                        health_report["components"]["audit"] = {
                            "status": "healthy" if status_info["compliance_status"] else "issues",
                            "compliance_violations": status_info["compliance_violations"],
                            "total_events": status_info["total_logged_events"]
                        }
                        
                        if status_info["compliance_violations"] > 0:
                            health_report["issues"].append(f"{status_info['compliance_violations']} compliance violations detected")
                    else:
                        health_report["components"]["audit"] = {"status": "error", "error": audit_status.get("error")}
                        health_report["issues"].append("Audit system check failed")
                        
                except Exception as e:
                    health_report["components"]["audit"] = {"status": "error", "error": str(e)}
                    health_report["issues"].append(f"Audit check failed: {str(e)}")
            
            # Determine overall status
            component_statuses = [comp.get("status", "error") for comp in health_report["components"].values()]
            if "error" in component_statuses:
                health_report["overall_status"] = "error"
            elif "issues" in component_statuses:
                health_report["overall_status"] = "issues"
            elif "warning" in component_statuses:
                health_report["overall_status"] = "warning"
            
            # Format response
            status_icons = {
                "healthy": "✅",
                "warning": "⚠️",
                "issues": "❌",
                "error": "🔴"
            }
            
            overall_icon = status_icons.get(health_report["overall_status"], "❓")
            
            response = f"""{overall_icon} System Health Check Report

Overall Status: {health_report['overall_status'].upper()}
Timestamp: {health_report['timestamp'][:19]}

Component Status:
"""
            
            for component, info in health_report["components"].items():
                comp_icon = status_icons.get(info.get("status", "error"), "❓")
                response += f"{comp_icon} {component.title()}: {info.get('status', 'error').upper()}\n"
            
            if health_report["issues"]:
                response += "\n🔴 Issues Detected:\n"
                for issue in health_report["issues"]:
                    response += f"• {issue}\n"
            
            if health_report["warnings"]:
                response += "\n⚠️ Warnings:\n"
                for warning in health_report["warnings"]:
                    response += f"• {warning}\n"
            
            if health_report["overall_status"] == "healthy":
                response += "\n🎉 All systems operating normally!"
            
            return response
            
        except Exception as e:
            logger.error(f"Error running system health check: {e}")
            return f"Error running system health check: {str(e)}"