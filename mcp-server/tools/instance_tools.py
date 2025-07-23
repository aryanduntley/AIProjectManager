"""
Instance Management Tools for AI Project Manager MCP Server
Provides Git-like instance operations for organizational state management
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.mcp_api import ToolDefinition
from core.instance_manager import MCPInstanceManager
from database.db_manager import DatabaseManager
from database.git_queries import GitQueries

logger = logging.getLogger(__name__)


class InstanceTools:
    """Tools for MCP instance management with Git-like operations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager
        self.git_queries = GitQueries(db_manager) if db_manager else None
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all instance management tools."""
        return [
            ToolDefinition(
                name="instance_create",
                description="Create new MCP instance with isolated workspace (like git checkout -b)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "instance_name": {
                            "type": "string",
                            "description": "Descriptive name for the instance (will be normalized to instance_id)"
                        },
                        "created_by": {
                            "type": "string",
                            "description": "User or system creating the instance",
                            "default": "ai"
                        },
                        "purpose": {
                            "type": "string",
                            "description": "Description of the work to be done in this instance"
                        },
                        "primary_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Primary themes this instance will work on",
                            "default": []
                        },
                        "related_flows": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Flow files related to this instance work",
                            "default": []
                        },
                        "expected_duration": {
                            "type": "string",
                            "description": "Expected duration of work (e.g., '3-5 days', '1 week')",
                            "default": ""
                        }
                    },
                    "required": ["project_path", "instance_name", "purpose"]
                },
                handler=self.create_instance
            ),
            ToolDefinition(
                name="instance_list",
                description="List all active MCP instances",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "status_filter": {
                            "type": "string",
                            "enum": ["active", "completed", "archived", "all"],
                            "description": "Filter instances by status",
                            "default": "active"
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.list_instances
            ),
            ToolDefinition(
                name="instance_status",
                description="Get detailed status of a specific MCP instance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "instance_id": {
                            "type": "string",
                            "description": "Instance ID to check status for"
                        }
                    },
                    "required": ["project_path", "instance_id"]
                },
                handler=self.get_instance_status
            ),
            ToolDefinition(
                name="instance_archive",
                description="Archive a completed MCP instance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "instance_id": {
                            "type": "string",
                            "description": "Instance ID to archive"
                        }
                    },
                    "required": ["project_path", "instance_id"]
                },
                handler=self.archive_instance
            ),
            ToolDefinition(
                name="instance_merge_initiate",
                description="Initiate merge process from instance to main (like git merge)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "source_instance": {
                            "type": "string",
                            "description": "Source instance ID to merge from"
                        },
                        "target_instance": {
                            "type": "string",
                            "description": "Target instance to merge to",
                            "default": "main"
                        }
                    },
                    "required": ["project_path", "source_instance"]
                },
                handler=self.initiate_merge
            ),
            ToolDefinition(
                name="instance_detect_conflicts",
                description="Detect conflicts between instance and main without initiating merge",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "source_instance": {
                            "type": "string",
                            "description": "Source instance ID to check for conflicts"
                        },
                        "target_instance": {
                            "type": "string",
                            "description": "Target instance to compare against",
                            "default": "main"
                        }
                    },
                    "required": ["project_path", "source_instance"]
                },
                handler=self.detect_conflicts
            ),
            ToolDefinition(
                name="instance_statistics",
                description="Get comprehensive instance management statistics",
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
                handler=self.get_instance_statistics
            ),
            ToolDefinition(
                name="instance_cleanup",
                description="Clean up orphaned instances and database records",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "dry_run": {
                            "type": "boolean",
                            "description": "If true, only report what would be cleaned up without doing it",
                            "default": True
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.cleanup_instances
            )
        ]
    
    async def create_instance(self, arguments: Dict[str, Any]) -> str:
        """Create new MCP instance with isolated workspace."""
        try:
            project_path = Path(arguments["project_path"])
            instance_name = arguments["instance_name"]
            created_by = arguments.get("created_by", "ai")
            purpose = arguments["purpose"]
            primary_themes = arguments.get("primary_themes", [])
            related_flows = arguments.get("related_flows", [])
            expected_duration = arguments.get("expected_duration", "")
            
            if not self.db_manager:
                return "Database not available. Instance management requires database connection."
            
            # Initialize instance manager
            instance_manager = MCPInstanceManager(project_path, self.db_manager)
            
            # Create instance
            result = instance_manager.create_instance(
                instance_name=instance_name,
                created_by=created_by,
                purpose=purpose,
                themes=primary_themes,
                related_flows=related_flows,
                expected_duration=expected_duration
            )
            
            if result.success:
                return f"""Instance created successfully!

Instance Details:
• Instance ID: {result.instance_id}
• Workspace: {result.workspace_path}
• Purpose: {purpose}
• Primary Themes: {', '.join(primary_themes) if primary_themes else 'None'}
• Expected Duration: {expected_duration or 'Not specified'}

The instance workspace is now isolated and ready for independent development.
Use 'instance_merge_initiate' when ready to merge changes back to main."""
            else:
                return f"Instance creation failed: {result.message}"
            
        except Exception as e:
            logger.error(f"Error creating instance: {e}")
            return f"Error creating instance: {str(e)}"
    
    async def list_instances(self, arguments: Dict[str, Any]) -> str:
        """List MCP instances with filtering."""
        try:
            project_path = Path(arguments["project_path"])
            status_filter = arguments.get("status_filter", "active")
            
            if not self.db_manager:
                return "Database not available. Instance management requires database connection."
            
            instance_manager = MCPInstanceManager(project_path, self.db_manager)
            
            if status_filter == "active" or status_filter == "all":
                active_instances = instance_manager.get_active_instances()
            else:
                active_instances = []
            
            if not active_instances:
                return f"No {status_filter} instances found."
            
            # Format instance list
            lines = [f"=== {status_filter.upper()} MCP INSTANCES ===", ""]
            
            for instance in active_instances:
                lines.extend([
                    f"📋 {instance.instance_id}",
                    f"   Purpose: {instance.purpose}",
                    f"   Created by: {instance.created_by}",
                    f"   Status: {instance.status}",
                    f"   Themes: {', '.join(instance.primary_themes) if instance.primary_themes else 'None'}",
                    f"   Created: {instance.created_at[:19] if instance.created_at else 'Unknown'}",
                    f"   Last Activity: {instance.last_activity[:19] if instance.last_activity else 'Unknown'}",
                    ""
                ])
            
            lines.append(f"Total: {len(active_instances)} instances")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error listing instances: {e}")
            return f"Error listing instances: {str(e)}"
    
    async def get_instance_status(self, arguments: Dict[str, Any]) -> str:
        """Get detailed status of a specific instance."""
        try:
            project_path = Path(arguments["project_path"])
            instance_id = arguments["instance_id"]
            
            if not self.db_manager:
                return "Database not available. Instance management requires database connection."
            
            instance_manager = MCPInstanceManager(project_path, self.db_manager)
            status = instance_manager.get_instance_status(instance_id)
            
            if not status.exists:
                error_msg = status.details.get("error", "Instance not found")
                return f"Instance '{instance_id}' not found. {error_msg}"
            
            instance_data = status.details["instance_data"]
            
            status_report = f"""=== INSTANCE STATUS: {instance_id} ===

Basic Information:
• Name: {instance_data.get('instance_name', 'Unknown')}
• Status: {status.status}
• Created From: {instance_data.get('created_from', 'Unknown')}
• Created By: {instance_data.get('created_by', 'Unknown')}
• Purpose: {instance_data.get('purpose', 'No purpose specified')}

Themes and Flows:
• Primary Themes: {', '.join(instance_data.get('primary_themes', [])) if instance_data.get('primary_themes') else 'None'}
• Related Flows: {', '.join(instance_data.get('related_flows', [])) if instance_data.get('related_flows') else 'None'}

Workspace Information:
• Workspace Path: {status.details.get('workspace_path', 'Unknown')}
• Workspace Exists: {'Yes' if status.details.get('workspace_exists') else 'No'}
• Database Path: {status.details.get('database_path', 'Unknown')}
• Database Exists: {'Yes' if status.details.get('database_exists') else 'No'}

Timeline:
• Created: {instance_data.get('created_at', 'Unknown')[:19] if instance_data.get('created_at') else 'Unknown'}
• Last Activity: {instance_data.get('last_activity', 'Unknown')[:19] if instance_data.get('last_activity') else 'Unknown'}
• Expected Duration: {instance_data.get('expected_duration', 'Not specified')}

Git Integration:
• Base Git Hash: {instance_data.get('git_base_hash', 'Unknown')[:8] if instance_data.get('git_base_hash') else 'Unknown'}...
"""
            
            return status_report
            
        except Exception as e:
            logger.error(f"Error getting instance status: {e}")
            return f"Error getting instance status: {str(e)}"
    
    async def archive_instance(self, arguments: Dict[str, Any]) -> str:
        """Archive a completed instance."""
        try:
            project_path = Path(arguments["project_path"])
            instance_id = arguments["instance_id"]
            
            if not self.db_manager:
                return "Database not available. Instance management requires database connection."
            
            instance_manager = MCPInstanceManager(project_path, self.db_manager)
            result = instance_manager.archive_instance(instance_id)
            
            if result["success"]:
                return f"""Instance '{instance_id}' archived successfully!

Archive Details:
• Archive Location: {result.get('archive_path', 'Unknown')}
• Status: Archived and moved to completed instances
• Workspace: Preserved in archive for future reference

The instance is now archived and no longer active. The workspace and metadata have been preserved for historical reference."""
            else:
                return f"Failed to archive instance '{instance_id}': {result['message']}"
            
        except Exception as e:
            logger.error(f"Error archiving instance: {e}")
            return f"Error archiving instance: {str(e)}"
    
    async def initiate_merge(self, arguments: Dict[str, Any]) -> str:
        """Initiate merge process from source instance to target."""
        try:
            project_path = Path(arguments["project_path"])
            source_instance = arguments["source_instance"]
            target_instance = arguments.get("target_instance", "main")
            
            if not self.db_manager:
                return "Database not available. Instance management requires database connection."
            
            instance_manager = MCPInstanceManager(project_path, self.db_manager)
            result = instance_manager.initiate_merge(source_instance, target_instance)
            
            if result["success"]:
                conflict_analysis = result["conflict_analysis"]
                
                merge_report = f"""=== MERGE INITIATED ===

Merge Details:
• Merge ID: {result['merge_id']}
• Source: {source_instance}
• Target: {target_instance}
• Status: {'Conflicts detected - resolution required' if result['requires_resolution'] else 'Ready to proceed'}

Conflict Analysis:
• Conflicts Detected: {result['conflicts_detected']}
• Summary: {conflict_analysis['summary']}
"""
                
                if result["requires_resolution"]:
                    merge_report += f"""
Conflict Types: {', '.join(conflict_analysis['conflict_types'])}

Detailed Conflicts:"""
                    
                    for conflict in conflict_analysis["conflicts"]:
                        merge_report += f"""
• {conflict['type'].upper()}: {conflict.get('file', 'N/A')}
  {conflict['description']}"""
                    
                    merge_report += """

Next Steps:
1. Review conflicts above
2. Use conflict resolution tools to resolve each conflict
3. Complete merge once all conflicts are resolved

⚠️  This merge requires manual conflict resolution by the main instance."""
                
                else:
                    merge_report += """

✅ No conflicts detected! Merge can proceed automatically.
Use merge completion tools to finalize the merge."""
                
                return merge_report
            else:
                return f"Failed to initiate merge: {result['message']}"
            
        except Exception as e:
            logger.error(f"Error initiating merge: {e}")
            return f"Error initiating merge: {str(e)}"
    
    async def detect_conflicts(self, arguments: Dict[str, Any]) -> str:
        """Detect conflicts without initiating merge."""
        try:
            project_path = Path(arguments["project_path"])
            source_instance = arguments["source_instance"]
            target_instance = arguments.get("target_instance", "main")
            
            if not self.db_manager:
                return "Database not available. Instance management requires database connection."
            
            instance_manager = MCPInstanceManager(project_path, self.db_manager)
            conflict_analysis = instance_manager.detect_conflicts(source_instance, target_instance)
            
            if conflict_analysis.get("error"):
                return f"Error detecting conflicts: {conflict_analysis['summary']}"
            
            conflicts_detected = conflict_analysis["conflicts_detected"]
            
            report = f"""=== CONFLICT DETECTION REPORT ===

Source Instance: {source_instance}
Target Instance: {target_instance}
Conflicts Detected: {conflicts_detected}
Summary: {conflict_analysis['summary']}
"""
            
            if conflicts_detected > 0:
                report += f"""
Conflict Types: {', '.join(conflict_analysis['conflict_types'])}

Detailed Conflict Analysis:"""
                
                for conflict in conflict_analysis["conflicts"]:
                    report += f"""
• {conflict['type'].upper()}: {conflict.get('file', 'N/A')}
  {conflict['description']}
  Conflict Type: {conflict.get('conflict_type', 'Unknown')}"""
            else:
                report += """

✅ No conflicts detected! These instances can be merged safely."""
            
            return report
            
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return f"Error detecting conflicts: {str(e)}"
    
    async def get_instance_statistics(self, arguments: Dict[str, Any]) -> str:
        """Get comprehensive instance management statistics."""
        try:
            project_path = Path(arguments["project_path"])
            
            if not self.db_manager:
                return "Database not available. Instance management requires database connection."
            
            instance_manager = MCPInstanceManager(project_path, self.db_manager)
            stats = instance_manager.get_instance_statistics()
            
            if stats.get("error"):
                return f"Error getting statistics: {stats['error']}"
            
            stats_report = f"""=== INSTANCE MANAGEMENT STATISTICS ===

Instance Summary:
• Total Instances: {stats['instances']['total']}
• Active Instances: {stats['instances']['active']}
• Completed Instances: {stats['instances']['completed']}
• Archived Instances: {stats['instances']['archived']}

Filesystem Status:
• Active Workspaces: {stats['filesystem']['active_workspaces']}
• Archived Workspaces: {stats['filesystem']['archived_workspaces']}
• Instances Directory: {'Exists' if stats['filesystem']['instances_directory_exists'] else 'Missing'}

Git Integration:
• Git States Tracked: {stats['git_states']['total']}
• States Reconciled: {stats['git_states']['reconciled']}
• Pending Reconciliation: {stats['git_states']['pending_reconciliation']}

Merge History:
• Total Merges: {stats['merges']['total']}
• Completed Merges: {stats['merges']['completed']}
• Pending Merges: {stats['merges']['pending']}
• Failed Merges: {stats['merges']['failed']}
• Total Conflicts Handled: {stats['merges']['total_conflicts']}
• Conflicts Resolved: {stats['merges']['resolved_conflicts']}
"""
            
            return stats_report
            
        except Exception as e:
            logger.error(f"Error getting instance statistics: {e}")
            return f"Error getting instance statistics: {str(e)}"
    
    async def cleanup_instances(self, arguments: Dict[str, Any]) -> str:
        """Clean up orphaned instances and database records."""
        try:
            project_path = Path(arguments["project_path"])
            dry_run = arguments.get("dry_run", True)
            
            if not self.db_manager:
                return "Database not available. Instance management requires database connection."
            
            instance_manager = MCPInstanceManager(project_path, self.db_manager)
            cleanup_report = instance_manager.cleanup_orphaned_instances()
            
            if not cleanup_report["success"]:
                return f"Cleanup failed: {'; '.join(cleanup_report['errors'])}"
            
            report = f"""=== INSTANCE CLEANUP REPORT ===

Mode: {'DRY RUN (no changes made)' if dry_run else 'ACTIVE CLEANUP'}

Orphaned Workspaces Found: {len(cleanup_report['orphaned_workspaces'])}"""
            
            if cleanup_report['orphaned_workspaces']:
                report += "\n• " + "\n• ".join(cleanup_report['orphaned_workspaces'])
            
            report += f"""

Orphaned Database Records Found: {len(cleanup_report['orphaned_database_records'])}"""
            
            if cleanup_report['orphaned_database_records']:
                for record in cleanup_report['orphaned_database_records']:
                    report += f"\n• {record['instance_id']} (workspace: {record['workspace_path']})"
            
            report += f"""

Items Cleaned Up: {cleanup_report['cleaned_up']}

Errors: {len(cleanup_report['errors'])}"""
            
            if cleanup_report['errors']:
                report += "\n• " + "\n• ".join(cleanup_report['errors'])
            
            if dry_run and (cleanup_report['orphaned_workspaces'] or cleanup_report['orphaned_database_records']):
                report += """

To perform actual cleanup, run this command with dry_run=false."""
            
            return report
            
        except Exception as e:
            logger.error(f"Error cleaning up instances: {e}")
            return f"Error cleaning up instances: {str(e)}"