"""
Audit system operations for the AI Project Manager.

Handles audit report generation, event searching, and status monitoring.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ...core.audit_system import AuditTrail, AuditLevel, AuditEventType
from ...database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class AuditOperations:
    """Audit system management operations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager

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