"""
Advanced Integration Tools for AI Project Manager MCP Server
Phase 4 tools providing performance optimization, error recovery, and audit capabilities
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from core.mcp_api import ToolDefinition
from core.performance_optimizer import LargeProjectOptimizer
from core.error_recovery import ErrorRecoveryManager, RecoveryLevel, OperationType
from core.audit_system import AuditTrail, AuditLevel, AuditEventType
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class AdvancedTools:
    """Advanced integration tools for Phase 4 features."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all advanced integration tools."""
        return [
            # Performance Optimization Tools
            ToolDefinition(
                name="system_optimize_performance",
                description="Run comprehensive performance optimization for large projects",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "optimization_level": {
                            "type": "string",
                            "enum": ["basic", "comprehensive", "aggressive"],
                            "description": "Level of optimization to perform",
                            "default": "comprehensive"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.optimize_performance
            ),
            ToolDefinition(
                name="system_get_performance_recommendations",
                description="Get performance optimization recommendations for the project",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_performance_recommendations
            ),
            
            # Error Recovery Tools
            ToolDefinition(
                name="recovery_create_checkpoint",
                description="Create a recovery checkpoint before critical operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "operation_type": {
                            "type": "string",
                            "enum": ["instance_creation", "instance_merge", "conflict_resolution", "database_operation", "file_operation"],
                            "description": "Type of operation this checkpoint is for"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the operation"
                        },
                        "context_data": {
                            "type": "object",
                            "description": "Context data for the operation",
                            "default": {}
                        }
                    },
                    "required": ["project_path", "operation_type", "description"]
                },
                handler=self.create_recovery_checkpoint
            ),
            ToolDefinition(
                name="recovery_rollback",
                description="Rollback to a previous recovery checkpoint",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "recovery_point_id": {
                            "type": "string",
                            "description": "ID of the recovery point to rollback to"
                        },
                        "recovery_level": {
                            "type": "string",
                            "enum": ["minimal", "partial", "complete"],
                            "description": "Level of recovery to perform",
                            "default": "complete"
                        }
                    },
                    "required": ["project_path", "recovery_point_id"]
                },
                handler=self.rollback_to_checkpoint
            ),
            ToolDefinition(
                name="recovery_status",
                description="Get status of recovery system and available recovery points",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_recovery_status
            ),
            
            # Audit System Tools
            ToolDefinition(
                name="audit_generate_report",
                description="Generate comprehensive audit report for specified time period",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "start_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Start date for audit report (YYYY-MM-DD)"
                        },
                        "end_date": {
                            "type": "string",
                            "format": "date",
                            "description": "End date for audit report (YYYY-MM-DD)"
                        },
                        "report_type": {
                            "type": "string",
                            "enum": ["summary", "detailed", "compliance", "forensic"],
                            "description": "Type of audit report to generate",
                            "default": "summary"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.generate_audit_report
            ),
            ToolDefinition(
                name="audit_search_events",
                description="Search audit events with specific criteria",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "event_type": {
                            "type": "string",
                            "description": "Filter by event type"
                        },
                        "actor": {
                            "type": "string",
                            "description": "Filter by actor (user/system)"
                        },
                        "start_time": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Filter events after this time"
                        },
                        "end_time": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Filter events before this time"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of events to return",
                            "default": 50
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.search_audit_events
            ),
            ToolDefinition(
                name="audit_system_status",
                description="Get status and health of the audit system",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_audit_status
            ),
            
            # System Health and Diagnostics
            ToolDefinition(
                name="system_health_check",
                description="Run comprehensive system health check across all components",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "include_performance": {
                            "type": "boolean",
                            "description": "Include performance diagnostics",
                            "default": True
                        },
                        "include_recovery": {
                            "type": "boolean",
                            "description": "Include recovery system diagnostics",
                            "default": True
                        },
                        "include_audit": {
                            "type": "boolean",
                            "description": "Include audit system diagnostics",
                            "default": True
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.system_health_check
            )
        ]
    
    async def optimize_performance(self, arguments: Dict[str, Any]) -> str:
        """Run comprehensive performance optimization."""
        try:
            project_path = Path(arguments["project_path"])
            optimization_level = arguments.get("optimization_level", "comprehensive")
            
            if not self.db_manager:
                return "Database not available. Performance optimization requires database connection."
            
            # Initialize performance optimizer
            optimizer = LargeProjectOptimizer(project_path, self.db_manager)
            
            # Run optimization based on level
            if optimization_level == "basic":
                # Basic database optimization only
                result = optimizer.db_optimizer.optimize_database()
            elif optimization_level == "comprehensive":
                # Full large project optimization
                result = optimizer.optimize_for_large_project()
            elif optimization_level == "aggressive":
                # Comprehensive optimization plus additional tuning
                result = optimizer.optimize_for_large_project()
                if result["success"]:
                    # Additional aggressive optimizations
                    index_result = optimizer.db_optimizer.create_performance_indexes()
                    result["optimization_report"]["additional_indexes"] = index_result
            
            if result["success"]:
                report = result.get("optimization_report", {})
                
                response = f"""🚀 Performance Optimization Complete!

Optimization Level: {optimization_level.upper()}
Project Size: {report.get('project_size', 0):,} bytes
Large Project: {'Yes' if report.get('is_large_project', False) else 'No'}

Optimizations Applied:
"""
                
                for optimization in report.get("optimizations_applied", []):
                    response += f"• {optimization.replace('_', ' ').title()}\n"
                
                if "database_optimization" in report:
                    db_info = report["database_optimization"]
                    response += f"""
Database Optimization:
• Database Size: {db_info.get('database_size', 0):,} bytes
• Indexes: {db_info.get('indexes_count', 0)} active indexes
• Operations: VACUUM, ANALYZE, OPTIMIZE completed
"""
                
                if "performance_indexes" in report:
                    idx_info = report["performance_indexes"]
                    response += f"""
Performance Indexes:
• Created {idx_info.get('total_indexes', 0)} new performance indexes
"""
                
                if "performance_metrics" in report:
                    metrics = report["performance_metrics"]
                    response += f"""
Performance Metrics:
• Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.2%}
• Database Queries: {metrics.get('total_database_queries', 0)}
• File Operations: {metrics.get('total_file_operations', 0)}
"""
                
                return response
            else:
                return f"❌ Performance optimization failed: {result.get('error', 'Unknown error')}"
            
        except Exception as e:
            logger.error(f"Error optimizing performance: {e}")
            return f"Error optimizing performance: {str(e)}"
    
    async def get_performance_recommendations(self, arguments: Dict[str, Any]) -> str:
        """Get performance optimization recommendations."""
        try:
            project_path = Path(arguments["project_path"])
            
            if not self.db_manager:
                return "Database not available. Performance analysis requires database connection."
            
            optimizer = LargeProjectOptimizer(project_path, self.db_manager)
            recommendations_result = optimizer.get_optimization_recommendations()
            
            if recommendations_result["success"]:
                recommendations = recommendations_result["recommendations"]
                metrics = recommendations_result["project_metrics"]
                
                response = f"""📊 Performance Analysis Report

Project Metrics:
• Large Project: {'Yes' if metrics.get('is_large_project', False) else 'No'}
• Project Size: {metrics.get('project_size', 0):,} bytes
• Active Instances: {metrics.get('active_instances', 0)}
• Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.2%}
• Last Optimization: {metrics.get('last_optimization', 'Never')[:19]}

"""
                
                if recommendations:
                    response += "🎯 Recommendations:\n\n"
                    for i, rec in enumerate(recommendations, 1):
                        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "⚪")
                        response += f"{priority_icon} **{rec['type'].replace('_', ' ').title()}** ({rec['priority']} priority)\n"
                        response += f"   {rec['description']}\n"
                        response += f"   Action: {rec['action']}\n\n"
                else:
                    response += "✅ No performance recommendations - system is optimally configured!"
                
                return response
            else:
                return f"❌ Performance analysis failed: {recommendations_result.get('error', 'Unknown error')}"
            
        except Exception as e:
            logger.error(f"Error getting performance recommendations: {e}")
            return f"Error getting performance recommendations: {str(e)}"
    
    async def create_recovery_checkpoint(self, arguments: Dict[str, Any]) -> str:
        """Create a recovery checkpoint."""
        try:
            project_path = Path(arguments["project_path"])
            operation_type = OperationType(arguments["operation_type"])
            description = arguments["description"]
            context_data = arguments.get("context_data", {})
            
            if not self.db_manager:
                return "Database not available. Recovery system requires database connection."
            
            # Initialize error recovery manager
            recovery_manager = ErrorRecoveryManager(project_path, self.db_manager)
            
            # Create recovery point
            recovery_point_id = recovery_manager.create_recovery_point(
                operation_type, description, context_data
            )
            
            if recovery_point_id:
                return f"""✅ Recovery checkpoint created successfully!

Recovery Point ID: {recovery_point_id}
Operation Type: {operation_type.value}
Description: {description}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This checkpoint can be used to rollback the system if the operation fails.
Use `recovery_rollback` with the Recovery Point ID to restore if needed."""
            else:
                return "❌ Failed to create recovery checkpoint. Check system logs for details."
                
        except Exception as e:
            logger.error(f"Error creating recovery checkpoint: {e}")
            return f"Error creating recovery checkpoint: {str(e)}"
    
    async def rollback_to_checkpoint(self, arguments: Dict[str, Any]) -> str:
        """Rollback to a recovery checkpoint."""
        try:
            project_path = Path(arguments["project_path"])
            recovery_point_id = arguments["recovery_point_id"]
            recovery_level = RecoveryLevel(arguments.get("recovery_level", "complete"))
            
            if not self.db_manager:
                return "Database not available. Recovery system requires database connection."
            
            recovery_manager = ErrorRecoveryManager(project_path, self.db_manager)
            
            # Perform rollback
            rollback_result = recovery_manager.rollback_to_recovery_point(
                recovery_point_id, recovery_level
            )
            
            if rollback_result["success"]:
                response = f"""🔄 Rollback completed successfully!

Recovery Point ID: {recovery_point_id}
Recovery Level: {recovery_level.value}

Actions Performed:
"""
                for action in rollback_result["rollback_actions"]:
                    response += f"• {action}\n"
                
                response += """
⚠️  The system has been restored to the checkpoint state.
Any changes made after the checkpoint have been reverted."""
                
                return response
            else:
                return f"❌ Rollback failed: {rollback_result['error']}"
                
        except Exception as e:
            logger.error(f"Error rolling back to checkpoint: {e}")
            return f"Error rolling back to checkpoint: {str(e)}"
    
    async def get_recovery_status(self, arguments: Dict[str, Any]) -> str:
        """Get recovery system status."""
        try:
            project_path = Path(arguments["project_path"])
            
            if not self.db_manager:
                return "Database not available. Recovery system requires database connection."
            
            recovery_manager = ErrorRecoveryManager(project_path, self.db_manager)
            status_result = recovery_manager.get_recovery_status()
            
            if status_result["success"]:
                response = f"""🛡️ Recovery System Status

Recovery Points:
• Total: {status_result['recovery_points']['total']}
• Recent: {len(status_result['recovery_points']['recent'])}

Backups:
• Total: {status_result['backups']['total']}
• Recent: {len(status_result['backups']['recent'])}

System Status: {status_result['system_status'].upper()}

Recent Recovery Points:
"""
                
                for point in status_result['recovery_points']['recent']:
                    response += f"• {point['id'][:20]}... ({point['operation_type']}) - {point['timestamp'][:19]}\n"
                
                if status_result['recent_events']:
                    response += "\nRecent Recovery Events:\n"
                    for event in status_result['recent_events'][-3:]:
                        response += f"• {event['event_type']} - {event['timestamp'][:19]}\n"
                
                return response
            else:
                return f"❌ Could not get recovery status: {status_result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error getting recovery status: {e}")
            return f"Error getting recovery status: {str(e)}"
    
    async def generate_audit_report(self, arguments: Dict[str, Any]) -> str:
        """Generate comprehensive audit report."""
        try:
            project_path = Path(arguments["project_path"])
            report_type = arguments.get("report_type", "summary")
            
            # Parse date arguments
            start_date = None
            end_date = None
            
            if "start_date" in arguments:
                start_date = datetime.fromisoformat(arguments["start_date"])
            if "end_date" in arguments:
                end_date = datetime.fromisoformat(arguments["end_date"])
            
            if not self.db_manager:
                return "Database not available. Audit system requires database connection."
            
            # Initialize audit system
            audit_trail = AuditTrail(project_path, self.db_manager)
            
            # Generate report
            report = audit_trail.generate_audit_report(start_date, end_date)
            
            if "error" in report:
                return f"❌ Audit report generation failed: {report['error']}"
            
            # Format response based on report type
            response = f"""📋 Audit Report ({report_type.upper()})

Report ID: {report['report_id']}
Generated: {report['generated_at'][:19]}
Period: {report['period']['start'][:10]} to {report['period']['end'][:10]} ({report['period']['duration_days']} days)

Summary:
• Total Events: {report['summary']['total_events']:,}
• Unique Actors: {report['summary']['unique_actors']}
• Event Types: {report['summary']['event_types']}
• Integrity Issues: {report['summary']['integrity_issues']}

"""
            
            if report_type in ["detailed", "forensic"]:
                response += "Event Statistics:\n"
                for event_type, count in list(report['statistics']['events_by_type'].items())[:10]:
                    response += f"• {event_type.replace('_', ' ').title()}: {count}\n"
                
                response += "\nTop Actors:\n"
                for actor, count in list(report['statistics']['events_by_actor'].items())[:5]:
                    response += f"• {actor}: {count} events\n"
            
            # Compliance status
            compliance = report['compliance']
            compliance_icon = "✅" if compliance['compliant'] else "❌"
            response += f"\n{compliance_icon} Compliance Status: {'COMPLIANT' if compliance['compliant'] else 'VIOLATIONS DETECTED'}\n"
            
            if compliance['violations']:
                response += "Violations:\n"
                for violation in compliance['violations'][:3]:
                    response += f"• {violation}\n"
            
            if compliance['warnings']:
                response += "Warnings:\n"
                for warning in compliance['warnings'][:3]:
                    response += f"• {warning}\n"
            
            # Recommendations
            if report['recommendations']:
                response += "\n🎯 Recommendations:\n"
                for rec in report['recommendations'][:5]:
                    response += f"• {rec}\n"
            
            # Integrity status
            integrity_rate = report['integrity']['integrity_rate']
            integrity_icon = "✅" if integrity_rate > 0.95 else "⚠️"
            response += f"\n{integrity_icon} Data Integrity: {integrity_rate:.1%} ({report['integrity']['events_checked']} events checked)\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating audit report: {e}")
            return f"Error generating audit report: {str(e)}"
    
    async def search_audit_events(self, arguments: Dict[str, Any]) -> str:
        """Search audit events with specific criteria."""
        try:
            project_path = Path(arguments["project_path"])
            limit = arguments.get("limit", 50)
            
            # Build search filters
            filters = {}
            for key in ["event_type", "actor", "start_time", "end_time"]:
                if key in arguments:
                    filters[key] = arguments[key]
            
            if not self.db_manager:
                return "Database not available. Audit system requires database connection."
            
            audit_trail = AuditTrail(project_path, self.db_manager)
            events = audit_trail.search_audit_events(filters, limit)
            
            if not events:
                return "No audit events found matching the specified criteria."
            
            response = f"🔍 Audit Event Search Results ({len(events)} events)\n\n"
            
            for event in events[:20]:  # Show max 20 events
                if "error" in event:
                    response += f"❌ {event['error']}\n"
                    continue
                
                timestamp = event.get("timestamp", "")[:19]
                event_type = event.get("event_type", "unknown").replace("_", " ").title()
                actor = event.get("actor", "unknown")
                description = event.get("description", "")[:100]
                
                response += f"• **{event_type}** - {timestamp}\n"
                response += f"  Actor: {actor}\n"
                response += f"  Description: {description}{'...' if len(event.get('description', '')) > 100 else ''}\n\n"
            
            if len(events) > 20:
                response += f"... and {len(events) - 20} more events\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching audit events: {e}")
            return f"Error searching audit events: {str(e)}"
    
    async def get_audit_status(self, arguments: Dict[str, Any]) -> str:
        """Get audit system status."""
        try:
            project_path = Path(arguments["project_path"])
            
            if not self.db_manager:
                return "Database not available. Audit system requires database connection."
            
            audit_trail = AuditTrail(project_path, self.db_manager)
            status_result = audit_trail.get_audit_system_status()
            
            if status_result["success"]:
                status = status_result["status"]
                
                response = f"""📊 Audit System Status

Configuration:
• Audit Level: {status['audit_level'].upper()}
• System Health: {status['system_health'].upper()}

Event Statistics:
• Buffer Events: {status['buffer_events']}
• Total Logged Events: {status['total_logged_events']:,}

Log File Sizes:
"""
                
                for log_file, size in status['log_file_sizes'].items():
                    response += f"• {log_file}: {size:,} bytes\n"
                
                compliance_icon = "✅" if status['compliance_status'] else "❌"
                response += f"\n{compliance_icon} Compliance Status: {'COMPLIANT' if status['compliance_status'] else 'VIOLATIONS DETECTED'}\n"
                
                if status['compliance_violations'] > 0:
                    response += f"• Violations: {status['compliance_violations']}\n"
                
                return response
            else:
                return f"❌ Could not get audit status: {status_result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error getting audit status: {e}")
            return f"Error getting audit status: {str(e)}"
    
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