"""
Conflict Resolution Tools for AI Project Manager MCP Server
Handles Git-like merge conflict resolution with main instance authority
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.mcp_api import ToolDefinition
from core.conflict_resolution import ConflictResolutionInterface, ThemeConflict, FlowConflict, TaskConflict, DatabaseConflict
from core.instance_manager import MCPInstanceManager
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ConflictResolutionTools:
    """Tools for merge conflict resolution with main instance authority."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all conflict resolution tools."""
        return [
            ToolDefinition(
                name="merge_show_conflicts",
                description="Show detailed conflicts for a merge that requires resolution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "merge_id": {
                            "type": "string",
                            "description": "Merge ID to show conflicts for"
                        }
                    },
                    "required": ["project_path", "merge_id"]
                },
                handler=self.show_merge_conflicts
            ),
            ToolDefinition(
                name="merge_resolve_conflict",
                description="Resolve a specific conflict in a merge",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "merge_id": {
                            "type": "string",
                            "description": "Merge ID containing the conflict"
                        },
                        "conflict_id": {
                            "type": "string",
                            "description": "Specific conflict ID to resolve"
                        },
                        "resolution_strategy": {
                            "type": "string",
                            "enum": ["accept_main", "accept_instance", "manual_merge", "split_approach"],
                            "description": "How to resolve the conflict"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the resolution decision",
                            "default": ""
                        },
                        "merged_content": {
                            "type": "string",
                            "description": "Manually merged content (required for manual_merge strategy)",
                            "default": ""
                        }
                    },
                    "required": ["project_path", "merge_id", "conflict_id", "resolution_strategy"]
                },
                handler=self.resolve_conflict
            ),
            ToolDefinition(
                name="merge_apply_resolutions",
                description="Apply all conflict resolutions and complete merge",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "merge_id": {
                            "type": "string",
                            "description": "Merge ID to apply resolutions for"
                        },
                        "resolutions": {
                            "type": "object",
                            "description": "Map of conflict_id to resolution data",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "strategy": {
                                        "type": "string",
                                        "enum": ["accept_main", "accept_instance", "manual_merge", "split_approach"]
                                    },
                                    "notes": {"type": "string"},
                                    "merged_content": {"type": "string"}
                                },
                                "required": ["strategy"]
                            }
                        }
                    },
                    "required": ["project_path", "merge_id", "resolutions"]
                },
                handler=self.apply_resolutions
            ),
            ToolDefinition(
                name="merge_complete",
                description="Complete merge process and archive source instance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "merge_id": {
                            "type": "string",
                            "description": "Merge ID to complete"
                        }
                    },
                    "required": ["project_path", "merge_id"]
                },
                handler=self.complete_merge
            ),
            ToolDefinition(
                name="merge_status",
                description="Get detailed status of a merge operation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "merge_id": {
                            "type": "string",
                            "description": "Merge ID to check status for"
                        }
                    },
                    "required": ["project_path", "merge_id"]
                },
                handler=self.get_merge_status
            ),
            ToolDefinition(
                name="merge_history",
                description="Get history of recent merge operations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of merges to return",
                            "default": 10
                        }
                    },
                    "required": ["project_path"]
                },
                handler=self.get_merge_history
            )
        ]
    
    async def show_merge_conflicts(self, arguments: Dict[str, Any]) -> str:
        """Show detailed conflicts for a merge."""
        try:
            project_path = Path(arguments["project_path"])
            merge_id = arguments["merge_id"]
            
            if not self.db_manager:
                return "Database not available. Conflict resolution requires database connection."
            
            # Get merge record and conflicts
            from database.git_queries import GitQueries
            git_queries = GitQueries(self.db_manager)
            merge_record = git_queries.get_merge_record(merge_id)
            
            if not merge_record:
                return f"Merge '{merge_id}' not found."
            
            # Get conflicts from instance manager
            instance_manager = MCPInstanceManager(project_path, self.db_manager)
            conflict_analysis = instance_manager.detect_conflicts(
                merge_record["source_instance"], 
                merge_record["target_instance"]
            )
            
            if conflict_analysis.get("error"):
                return f"Error analyzing conflicts: {conflict_analysis['summary']}"
            
            conflicts = conflict_analysis["conflicts"]
            
            report_lines = [
                f"=== MERGE CONFLICT DETAILS ===",
                f"Merge ID: {merge_id}",
                f"Source: {merge_record['source_instance']}",
                f"Target: {merge_record['target_instance']}",
                f"Status: {merge_record['merge_status']}",
                f"Total Conflicts: {len(conflicts)}",
                ""
            ]
            
            if not conflicts:
                report_lines.append("✅ No conflicts detected! Merge can proceed automatically.")
                return "\n".join(report_lines)
            
            # Group conflicts by type
            conflicts_by_type = {}
            for conflict in conflicts:
                conflict_type = conflict["type"]
                if conflict_type not in conflicts_by_type:
                    conflicts_by_type[conflict_type] = []
                conflicts_by_type[conflict_type].append(conflict)
            
            # Present each conflict type
            for conflict_type, type_conflicts in conflicts_by_type.items():
                report_lines.extend([
                    f"## {conflict_type.upper()} CONFLICTS ({len(type_conflicts)})",
                    ""
                ])
                
                for i, conflict in enumerate(type_conflicts, 1):
                    conflict_id = f"{merge_id}-{conflict_type}-{conflict.get('file', i)}"
                    report_lines.extend([
                        f"### Conflict {i}: {conflict.get('file', 'N/A')}",
                        f"**Conflict ID**: `{conflict_id}`",
                        f"**Description**: {conflict['description']}",
                        f"**Type**: {conflict.get('conflict_type', 'Unknown')}",
                        ""
                    ])
                    
                    # Show resolution options
                    report_lines.extend([
                        "**Resolution Options**:",
                        "1. `accept_main` - Keep main instance version",
                        "2. `accept_instance` - Use instance version",
                        "3. `manual_merge` - Manually combine both versions",
                    ])
                    
                    if conflict_type == "theme":
                        report_lines.append("4. `split_approach` - Create separate themes")
                    
                    report_lines.extend(["", "---", ""])
            
            report_lines.extend([
                "## NEXT STEPS",
                "",
                "1. Use `merge_resolve_conflict` to resolve each conflict individually, OR",
                "2. Use `merge_apply_resolutions` to resolve multiple conflicts at once",
                "3. Use `merge_complete` to finalize the merge",
                "",
                "⚠️  All conflicts must be resolved before the merge can be completed."
            ])
            
            return "\n".join(report_lines)
            
        except Exception as e:
            logger.error(f"Error showing merge conflicts: {e}")
            return f"Error showing merge conflicts: {str(e)}"
    
    async def resolve_conflict(self, arguments: Dict[str, Any]) -> str:
        """Resolve a specific conflict."""
        try:
            project_path = Path(arguments["project_path"])
            merge_id = arguments["merge_id"]
            conflict_id = arguments["conflict_id"]
            strategy = arguments["resolution_strategy"]
            notes = arguments.get("notes", "")
            merged_content = arguments.get("merged_content", "")
            
            if not self.db_manager:
                return "Database not available. Conflict resolution requires database connection."
            
            # Initialize conflict resolution interface
            conflict_resolver = ConflictResolutionInterface(project_path, self.db_manager)
            
            # Prepare resolution data
            resolution_data = {
                "strategy": strategy,
                "notes": notes
            }
            
            if strategy == "manual_merge" and merged_content:
                resolution_data["merged_content"] = merged_content
            
            # Apply single resolution
            result = conflict_resolver._apply_single_resolution(merge_id, conflict_id, resolution_data)
            
            if result["success"]:
                return f"""✅ Conflict resolved successfully!

Conflict ID: {conflict_id}
Strategy: {strategy}
Result: {result['message']}
Notes: {notes or 'None'}

The conflict has been resolved. Use `merge_status` to check remaining conflicts, or `merge_complete` if all conflicts are resolved."""
            else:
                return f"❌ Failed to resolve conflict '{conflict_id}': {result['error']}"
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return f"Error resolving conflict: {str(e)}"
    
    async def apply_resolutions(self, arguments: Dict[str, Any]) -> str:
        """Apply multiple conflict resolutions at once."""
        try:
            project_path = Path(arguments["project_path"])
            merge_id = arguments["merge_id"]
            resolutions = arguments["resolutions"]
            
            if not self.db_manager:
                return "Database not available. Conflict resolution requires database connection."
            
            if not resolutions:
                return "No resolutions provided. Please specify conflict resolutions."
            
            # Initialize conflict resolution interface
            conflict_resolver = ConflictResolutionInterface(project_path, self.db_manager)
            
            # Apply all resolutions
            merge_result = conflict_resolver.apply_conflict_resolutions(merge_id, resolutions)
            
            if merge_result.success:
                return f"""✅ All conflict resolutions applied successfully!

{conflict_resolver.show_merge_summary(merge_result)}

The merge is now ready for completion. Use `merge_complete` to finalize the merge and archive the source instance."""
            else:
                return f"""❌ Some conflict resolutions failed:

{conflict_resolver.show_merge_summary(merge_result)}

Please review the failed resolutions and try again."""
            
        except Exception as e:
            logger.error(f"Error applying resolutions: {e}")
            return f"Error applying resolutions: {str(e)}"
    
    async def complete_merge(self, arguments: Dict[str, Any]) -> str:
        """Complete merge process and archive source instance."""
        try:
            project_path = Path(arguments["project_path"])
            merge_id = arguments["merge_id"]
            
            if not self.db_manager:
                return "Database not available. Conflict resolution requires database connection."
            
            # Initialize conflict resolution interface
            conflict_resolver = ConflictResolutionInterface(project_path, self.db_manager)
            
            # Complete merge
            result = conflict_resolver.complete_merge(merge_id)
            
            if result["success"]:
                return f"""🎉 Merge completed successfully!

{result['merge_summary']}

The source instance has been archived and all changes have been integrated into the main instance. The Git-like merge process is now complete."""
            else:
                return f"❌ Failed to complete merge: {result['message']}"
            
        except Exception as e:
            logger.error(f"Error completing merge: {e}")
            return f"Error completing merge: {str(e)}"
    
    async def get_merge_status(self, arguments: Dict[str, Any]) -> str:
        """Get detailed status of a merge operation."""
        try:
            project_path = Path(arguments["project_path"])
            merge_id = arguments["merge_id"]
            
            if not self.db_manager:
                return "Database not available. Conflict resolution requires database connection."
            
            from database.git_queries import GitQueries
            git_queries = GitQueries(self.db_manager)
            merge_record = git_queries.get_merge_record(merge_id)
            
            if not merge_record:
                return f"Merge '{merge_id}' not found."
            
            status_report = f"""=== MERGE STATUS ===

Merge ID: {merge_id}
Source Instance: {merge_record['source_instance']}
Target Instance: {merge_record['target_instance']}
Status: {merge_record['merge_status']}

Conflict Summary:
• Conflicts Detected: {merge_record['conflicts_detected']}
• Conflicts Resolved: {merge_record['conflicts_resolved']}
• Remaining Conflicts: {merge_record['conflicts_detected'] - merge_record['conflicts_resolved']}

Conflict Types: {', '.join(merge_record['conflict_types']) if merge_record['conflict_types'] else 'None'}

Timeline:
• Started: {merge_record['started_at'][:19] if merge_record['started_at'] else 'Unknown'}
• Completed: {merge_record['completed_at'][:19] if merge_record['completed_at'] else 'Not completed'}

Resolution Summary:
{merge_record['merge_summary'] or 'No summary available'}

Merge Notes:
{merge_record['merge_notes'] or 'No notes'}
"""
            
            # Add next steps based on status
            if merge_record['merge_status'] == 'pending':
                status_report += "\n**Next Steps**: Use `merge_show_conflicts` to see detailed conflicts"
            elif merge_record['merge_status'] == 'in-progress':
                remaining = merge_record['conflicts_detected'] - merge_record['conflicts_resolved']
                if remaining > 0:
                    status_report += f"\n**Next Steps**: Resolve {remaining} remaining conflicts"
                else:
                    status_report += "\n**Next Steps**: Use `merge_complete` to finalize the merge"
            elif merge_record['merge_status'] == 'completed':
                status_report += "\n**Status**: ✅ Merge completed successfully"
            elif merge_record['merge_status'] == 'failed':
                status_report += "\n**Status**: ❌ Merge failed - review conflicts and try again"
            
            return status_report
            
        except Exception as e:
            logger.error(f"Error getting merge status: {e}")
            return f"Error getting merge status: {str(e)}"
    
    async def get_merge_history(self, arguments: Dict[str, Any]) -> str:
        """Get history of recent merge operations."""
        try:
            project_path = Path(arguments["project_path"])
            limit = arguments.get("limit", 10)
            
            if not self.db_manager:
                return "Database not available. Conflict resolution requires database connection."
            
            from database.git_queries import GitQueries
            git_queries = GitQueries(self.db_manager)
            merge_history = git_queries.get_merge_history(limit)
            
            if not merge_history:
                return "No merge history found."
            
            history_lines = [
                f"=== MERGE HISTORY (Last {len(merge_history)}) ===",
                ""
            ]
            
            for merge in merge_history:
                status_icon = {
                    'completed': '✅',
                    'failed': '❌',
                    'pending': '⏳',
                    'in-progress': '🔄'
                }.get(merge['merge_status'], '❓')
                
                history_lines.extend([
                    f"{status_icon} **{merge['merge_id']}**",
                    f"   {merge['source_instance']} → {merge['target_instance']}",
                    f"   Status: {merge['merge_status']} | Conflicts: {merge['conflicts_resolved']}/{merge['conflicts_detected']}",
                    f"   Started: {merge['started_at'][:19] if merge['started_at'] else 'Unknown'}",
                    f"   Summary: {merge['merge_summary'][:100]}{'...' if len(merge['merge_summary'] or '') > 100 else ''}",
                    ""
                ])
            
            history_lines.append(f"Total merges shown: {len(merge_history)}")
            
            return "\n".join(history_lines)
            
        except Exception as e:
            logger.error(f"Error getting merge history: {e}")
            return f"Error getting merge history: {str(e)}"