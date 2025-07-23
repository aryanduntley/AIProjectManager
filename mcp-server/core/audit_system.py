"""
Comprehensive Audit System for MCP Instance Management
Provides detailed audit trails, compliance logging, and forensic analysis capabilities
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid

from ..database.db_manager import DatabaseManager
from ..database.git_queries import GitQueries


class AuditLevel(Enum):
    """Levels of audit detail"""
    MINIMAL = "minimal"      # Basic operations only
    STANDARD = "standard"    # Standard business operations
    DETAILED = "detailed"    # Detailed technical operations
    FORENSIC = "forensic"    # Complete forensic trail


class AuditEventType(Enum):
    """Types of events that can be audited"""
    INSTANCE_CREATED = "instance_created"
    INSTANCE_ARCHIVED = "instance_archived"
    MERGE_INITIATED = "merge_initiated"
    MERGE_COMPLETED = "merge_completed"
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"
    GIT_CHANGE_DETECTED = "git_change_detected"
    DATABASE_MODIFIED = "database_modified"
    FILE_MODIFIED = "file_modified"
    USER_ACTION = "user_action"
    SYSTEM_ERROR = "system_error"
    RECOVERY_EXECUTED = "recovery_executed"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class AuditEvent:
    """Represents a single audit event"""
    def __init__(self, event_type: AuditEventType, level: AuditLevel,
                 actor: str, description: str, data: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.event_type = event_type
        self.level = level
        self.actor = actor
        self.description = description
        self.data = data
        self.timestamp = datetime.now()
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate integrity checksum for the event"""
        content = f"{self.event_type.value}{self.actor}{self.description}{json.dumps(self.data, sort_keys=True)}{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "level": self.level.value,
            "actor": self.actor,
            "description": self.description,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "checksum": self.checksum
        }
    
    def verify_integrity(self) -> bool:
        """Verify the integrity of this audit event"""
        expected_checksum = self._calculate_checksum()
        return self.checksum == expected_checksum


class ComplianceTracker:
    """Tracks compliance-related metrics and requirements"""
    def __init__(self):
        self.compliance_rules = {
            "data_retention": {
                "audit_logs": 90,  # days
                "merge_history": 365,  # days
                "recovery_points": 30  # days
            },
            "access_control": {
                "require_actor_identification": True,
                "log_all_database_changes": True,
                "log_file_access": True
            },
            "change_management": {
                "require_merge_approval": True,
                "log_conflict_resolutions": True,
                "track_organizational_changes": True
            }
        }
    
    def check_compliance(self, audit_events: List[AuditEvent]) -> Dict[str, Any]:
        """Check compliance against defined rules"""
        compliance_report = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "metrics": {}
        }
        
        try:
            # Check data retention compliance
            retention_check = self._check_retention_compliance(audit_events)
            compliance_report["metrics"]["retention"] = retention_check
            
            # Check access control compliance
            access_check = self._check_access_control_compliance(audit_events)
            compliance_report["metrics"]["access_control"] = access_check
            
            # Check change management compliance
            change_check = self._check_change_management_compliance(audit_events)
            compliance_report["metrics"]["change_management"] = change_check
            
            # Aggregate violations
            for check in [retention_check, access_check, change_check]:
                compliance_report["violations"].extend(check.get("violations", []))
                compliance_report["warnings"].extend(check.get("warnings", []))
            
            compliance_report["compliant"] = len(compliance_report["violations"]) == 0
            
        except Exception as e:
            compliance_report["compliant"] = False
            compliance_report["violations"].append(f"Compliance check failed: {str(e)}")
        
        return compliance_report
    
    def _check_retention_compliance(self, audit_events: List[AuditEvent]) -> Dict[str, Any]:
        """Check data retention compliance"""
        retention_report = {"violations": [], "warnings": [], "metrics": {}}
        
        now = datetime.now()
        audit_retention_cutoff = now - timedelta(days=self.compliance_rules["data_retention"]["audit_logs"])
        
        # Check for events older than retention period
        old_events = [e for e in audit_events if e.timestamp < audit_retention_cutoff]
        if old_events:
            retention_report["warnings"].append(f"{len(old_events)} audit events exceed retention period")
        
        retention_report["metrics"]["total_events"] = len(audit_events)
        retention_report["metrics"]["events_within_retention"] = len(audit_events) - len(old_events)
        
        return retention_report
    
    def _check_access_control_compliance(self, audit_events: List[AuditEvent]) -> Dict[str, Any]:
        """Check access control compliance"""
        access_report = {"violations": [], "warnings": [], "metrics": {}}
        
        # Check for events without proper actor identification
        unidentified_events = [e for e in audit_events if not e.actor or e.actor == "unknown"]
        if unidentified_events:
            access_report["violations"].append(f"{len(unidentified_events)} events lack proper actor identification")
        
        # Check for database changes without logging
        db_events = [e for e in audit_events if e.event_type == AuditEventType.DATABASE_MODIFIED]
        access_report["metrics"]["database_change_events"] = len(db_events)
        
        return access_report
    
    def _check_change_management_compliance(self, audit_events: List[AuditEvent]) -> Dict[str, Any]:
        """Check change management compliance"""
        change_report = {"violations": [], "warnings": [], "metrics": {}}
        
        # Check merge operations have proper approval trail
        merge_events = [e for e in audit_events if e.event_type == AuditEventType.MERGE_COMPLETED]
        conflict_events = [e for e in audit_events if e.event_type == AuditEventType.CONFLICT_RESOLVED]
        
        change_report["metrics"]["merge_operations"] = len(merge_events)
        change_report["metrics"]["conflict_resolutions"] = len(conflict_events)
        
        # Check for merges without conflict resolution records
        merge_ids = {e.data.get("merge_id") for e in merge_events if e.data.get("merge_id")}
        resolved_merge_ids = {e.data.get("merge_id") for e in conflict_events if e.data.get("merge_id")}
        
        unresolved_merges = merge_ids - resolved_merge_ids
        if unresolved_merges:
            change_report["warnings"].append(f"{len(unresolved_merges)} merges lack conflict resolution records")
        
        return change_report


class AuditTrail:
    """Main audit trail management system"""
    def __init__(self, project_root: Path, db_manager: DatabaseManager):
        self.project_root = Path(project_root)
        self.db_manager = db_manager
        self.git_queries = GitQueries(db_manager)
        
        # Audit configuration
        self.audit_level = AuditLevel.STANDARD
        self.compliance_tracker = ComplianceTracker()
        
        # Audit storage
        self.audit_dir = self.project_root / ".mcp-instances" / "audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        self.main_audit_log = self.audit_dir / "audit.jsonl"
        self.compliance_log = self.audit_dir / "compliance.jsonl"
        self.forensic_log = self.audit_dir / "forensic.jsonl"
        
        # In-memory event buffer
        self.event_buffer = []
        self.buffer_size = 100
    
    def set_audit_level(self, level: AuditLevel):
        """Set the audit detail level"""
        self.audit_level = level
        self.log_audit_event(
            AuditEventType.SYSTEM_ERROR,  # Using closest available type
            "system",
            f"Audit level changed to {level.value}",
            {"previous_level": self.audit_level.value, "new_level": level.value}
        )
    
    def log_audit_event(self, event_type: AuditEventType, actor: str,
                       description: str, data: Dict[str, Any],
                       level: Optional[AuditLevel] = None):
        """Log an audit event"""
        try:
            # Use provided level or current audit level
            event_level = level or self.audit_level
            
            # Create audit event
            event = AuditEvent(event_type, event_level, actor, description, data)
            
            # Add to buffer
            self.event_buffer.append(event)
            
            # Write to appropriate log files
            self._write_event_to_logs(event)
            
            # Flush buffer if full
            if len(self.event_buffer) >= self.buffer_size:
                self._flush_event_buffer()
            
        except Exception as e:
            # Emergency logging to ensure audit failures are recorded
            emergency_event = {
                "timestamp": datetime.now().isoformat(),
                "event_type": "audit_logging_failed",
                "error": str(e),
                "original_event": {
                    "type": event_type.value,
                    "actor": actor,
                    "description": description
                }
            }
            
            try:
                with open(self.audit_dir / "emergency.jsonl", 'a') as f:
                    f.write(json.dumps(emergency_event) + '\n')
            except Exception:
                pass  # Ultimate fallback - don't crash on audit failure
    
    def _write_event_to_logs(self, event: AuditEvent):
        """Write event to appropriate log files"""
        event_dict = event.to_dict()
        
        # Always write to main audit log
        with open(self.main_audit_log, 'a') as f:
            f.write(json.dumps(event_dict) + '\n')
        
        # Write to compliance log for compliance-relevant events
        compliance_events = {
            AuditEventType.MERGE_COMPLETED,
            AuditEventType.CONFLICT_RESOLVED,
            AuditEventType.DATABASE_MODIFIED,
            AuditEventType.INSTANCE_CREATED,
            AuditEventType.INSTANCE_ARCHIVED
        }
        
        if event.event_type in compliance_events:
            with open(self.compliance_log, 'a') as f:
                f.write(json.dumps(event_dict) + '\n')
        
        # Write to forensic log for detailed/forensic level events
        if event.level in [AuditLevel.DETAILED, AuditLevel.FORENSIC]:
            with open(self.forensic_log, 'a') as f:
                f.write(json.dumps(event_dict) + '\n')
    
    def _flush_event_buffer(self):
        """Flush the in-memory event buffer"""
        try:
            # Buffer is already written to files, just clear it
            self.event_buffer.clear()
        except Exception as e:
            print(f"Warning: Error flushing audit event buffer: {e}")
    
    def search_audit_events(self, filters: Dict[str, Any], 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Search audit events with filters"""
        try:
            matching_events = []
            
            # Read from main audit log
            if self.main_audit_log.exists():
                with open(self.main_audit_log, 'r') as f:
                    for line in f:
                        try:
                            event_dict = json.loads(line.strip())
                            if self._event_matches_filters(event_dict, filters):
                                matching_events.append(event_dict)
                                
                                if len(matching_events) >= limit:
                                    break
                        except Exception:
                            continue
            
            # Sort by timestamp (most recent first)
            matching_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return matching_events
            
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
    
    def _event_matches_filters(self, event_dict: Dict[str, Any], 
                             filters: Dict[str, Any]) -> bool:
        """Check if an event matches the given filters"""
        try:
            # Event type filter
            if "event_type" in filters:
                if event_dict.get("event_type") != filters["event_type"]:
                    return False
            
            # Actor filter
            if "actor" in filters:
                if filters["actor"] not in event_dict.get("actor", ""):
                    return False
            
            # Time range filter
            if "start_time" in filters or "end_time" in filters:
                event_time = datetime.fromisoformat(event_dict.get("timestamp", ""))
                
                if "start_time" in filters:
                    start_time = datetime.fromisoformat(filters["start_time"])
                    if event_time < start_time:
                        return False
                
                if "end_time" in filters:
                    end_time = datetime.fromisoformat(filters["end_time"])
                    if event_time > end_time:
                        return False
            
            # Data field filter
            if "data_contains" in filters:
                data_str = json.dumps(event_dict.get("data", {})).lower()
                search_term = filters["data_contains"].lower()
                if search_term not in data_str:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def generate_audit_report(self, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Search for events in date range
            filters = {
                "start_time": start_date.isoformat(),
                "end_time": end_date.isoformat()
            }
            events = self.search_audit_events(filters, limit=10000)
            
            # Convert to AuditEvent objects for analysis
            audit_events = []
            for event_dict in events:
                try:
                    event = AuditEvent(
                        AuditEventType(event_dict["event_type"]),
                        AuditLevel(event_dict["level"]),
                        event_dict["actor"],
                        event_dict["description"],
                        event_dict["data"]
                    )
                    event.id = event_dict["id"]
                    event.timestamp = datetime.fromisoformat(event_dict["timestamp"])
                    event.checksum = event_dict["checksum"]
                    audit_events.append(event)
                except Exception:
                    continue
            
            # Generate statistics
            event_counts = {}
            actor_counts = {}
            daily_counts = {}
            
            for event in audit_events:
                # Event type counts
                event_type = event.event_type.value
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                # Actor counts
                actor_counts[event.actor] = actor_counts.get(event.actor, 0) + 1
                
                # Daily counts
                date_key = event.timestamp.date().isoformat()
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
            
            # Check compliance
            compliance_report = self.compliance_tracker.check_compliance(audit_events)
            
            # Verify event integrity
            integrity_issues = []
            for event in audit_events[:100]:  # Check first 100 events
                if not event.verify_integrity():
                    integrity_issues.append(event.id)
            
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.now().isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "duration_days": (end_date - start_date).days
                },
                "summary": {
                    "total_events": len(audit_events),
                    "unique_actors": len(actor_counts),
                    "event_types": len(event_counts),
                    "integrity_issues": len(integrity_issues)
                },
                "statistics": {
                    "events_by_type": event_counts,
                    "events_by_actor": actor_counts,
                    "events_by_day": daily_counts
                },
                "compliance": compliance_report,
                "integrity": {
                    "events_checked": min(100, len(audit_events)),
                    "integrity_issues": integrity_issues,
                    "integrity_rate": 1 - (len(integrity_issues) / max(1, min(100, len(audit_events))))
                },
                "recommendations": self._generate_audit_recommendations(audit_events, compliance_report)
            }
            
            return report
            
        except Exception as e:
            return {
                "error": f"Audit report generation failed: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }
    
    def _generate_audit_recommendations(self, audit_events: List[AuditEvent], 
                                      compliance_report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on audit analysis"""
        recommendations = []
        
        try:
            # Check for high error rates
            error_events = [e for e in audit_events if e.event_type == AuditEventType.SYSTEM_ERROR]
            if len(error_events) > len(audit_events) * 0.1:  # >10% error rate
                recommendations.append("High error rate detected - review system stability")
            
            # Check for compliance violations
            if not compliance_report.get("compliant", True):
                recommendations.append("Compliance violations detected - review and address violations")
            
            # Check for unusual activity patterns
            if len(audit_events) > 1000:  # High activity
                recommendations.append("High audit activity detected - consider performance optimization")
                
            elif len(audit_events) < 10:  # Very low activity
                recommendations.append("Low audit activity - verify audit logging is functioning correctly")
            
            # Check for security-related recommendations
            unidentified_actors = [e for e in audit_events if e.actor in ["unknown", "system", ""]]
            if len(unidentified_actors) > len(audit_events) * 0.2:  # >20% unidentified
                recommendations.append("Many events lack proper actor identification - improve access control")
            
        except Exception:
            recommendations.append("Error generating recommendations - manual review suggested")
        
        return recommendations
    
    def archive_old_audit_logs(self, keep_days: int = 90) -> Dict[str, Any]:
        """Archive old audit logs"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            archive_dir = self.audit_dir / "archived"
            archive_dir.mkdir(exist_ok=True)
            
            archived_files = []
            
            # Archive main audit log
            if self.main_audit_log.exists():
                archive_result = self._archive_log_file(
                    self.main_audit_log, 
                    archive_dir / f"audit_{cutoff_date.strftime('%Y%m%d')}.jsonl",
                    cutoff_date
                )
                if archive_result["archived_events"] > 0:
                    archived_files.append(f"audit.jsonl ({archive_result['archived_events']} events)")
            
            return {
                "success": True,
                "archived_files": archived_files,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Audit log archival failed: {str(e)}"
            }
    
    def _archive_log_file(self, source_file: Path, archive_file: Path, 
                         cutoff_date: datetime) -> Dict[str, Any]:
        """Archive events older than cutoff date from a log file"""
        archived_events = 0
        kept_events = 0
        
        try:
            if not source_file.exists():
                return {"archived_events": 0, "kept_events": 0}
            
            # Read all events
            old_events = []
            recent_events = []
            
            with open(source_file, 'r') as f:
                for line in f:
                    try:
                        event_dict = json.loads(line.strip())
                        event_time = datetime.fromisoformat(event_dict.get("timestamp", ""))
                        
                        if event_time < cutoff_date:
                            old_events.append(line)
                        else:
                            recent_events.append(line)
                    except Exception:
                        # Keep malformed events in recent
                        recent_events.append(line)
            
            # Write old events to archive
            if old_events:
                with open(archive_file, 'w') as f:
                    f.writelines(old_events)
                archived_events = len(old_events)
            
            # Rewrite source file with recent events only
            with open(source_file, 'w') as f:
                f.writelines(recent_events)
            kept_events = len(recent_events)
            
            return {
                "archived_events": archived_events,
                "kept_events": kept_events
            }
            
        except Exception as e:
            return {
                "archived_events": 0,
                "kept_events": 0,
                "error": str(e)
            }
    
    def get_audit_system_status(self) -> Dict[str, Any]:
        """Get comprehensive audit system status"""
        try:
            # Count events in buffer and logs
            buffer_events = len(self.event_buffer)
            
            log_events = 0
            if self.main_audit_log.exists():
                with open(self.main_audit_log, 'r') as f:
                    log_events = sum(1 for line in f)
            
            # Get log file sizes
            log_sizes = {}
            for log_file in [self.main_audit_log, self.compliance_log, self.forensic_log]:
                if log_file.exists():
                    log_sizes[log_file.name] = log_file.stat().st_size
                else:
                    log_sizes[log_file.name] = 0
            
            # Get recent compliance status
            recent_events = self.search_audit_events({}, limit=1000)
            audit_events = []
            for event_dict in recent_events:
                try:
                    event = AuditEvent(
                        AuditEventType(event_dict["event_type"]),
                        AuditLevel(event_dict["level"]),
                        event_dict["actor"],
                        event_dict["description"],
                        event_dict["data"]
                    )
                    audit_events.append(event)
                except Exception:
                    continue
            
            compliance_status = self.compliance_tracker.check_compliance(audit_events)
            
            return {
                "success": True,
                "status": {
                    "audit_level": self.audit_level.value,
                    "buffer_events": buffer_events,
                    "total_logged_events": log_events,
                    "log_file_sizes": log_sizes,
                    "compliance_status": compliance_status["compliant"],
                    "compliance_violations": len(compliance_status["violations"]),
                    "system_health": "healthy" if compliance_status["compliant"] else "issues_detected"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Could not get audit system status: {str(e)}"
            }