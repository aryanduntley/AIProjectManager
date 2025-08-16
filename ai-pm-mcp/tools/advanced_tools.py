"""
Advanced Integration Tools for AI Project Manager MCP Server
Advanced tools providing performance optimization, error recovery, and audit capabilities
Adapted for Git branch-based management instead of instance-based management
"""

import logging
from typing import List, Dict, Any, Optional

from ..core.mcp_api import ToolDefinition
from ..database.db_manager import DatabaseManager

from .advanced.performance_operations import PerformanceOperations
from .advanced.recovery_operations import RecoveryOperations
from .advanced.audit_operations import AuditOperations
from .advanced.health_operations import HealthOperations

logger = logging.getLogger(__name__)


class AdvancedTools:
    """Advanced integration tools for enhanced system capabilities."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager
        
        # Initialize operation modules
        self.performance_ops = PerformanceOperations(db_manager)
        self.recovery_ops = RecoveryOperations(db_manager)
        self.audit_ops = AuditOperations(db_manager)
        self.health_ops = HealthOperations(db_manager)
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all advanced integration tools."""
        return [
            # Performance Optimization Tools
            ToolDefinition(
                name="system_optimize_performance",
                description="Run comprehensive performance optimization for large projects with Git branches",
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
                name="system_performance_recommendations",
                description="Get performance optimization recommendations for large projects",
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
                            "enum": ["database_migration", "schema_update", "data_import", "config_change", "deployment", "maintenance"],
                            "description": "Type of operation being performed"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the operation"
                        },
                        "context_data": {
                            "type": "object",
                            "description": "Additional context data for recovery",
                            "default": {}
                        }
                    },
                    "required": ["project_path", "operation_type", "description"]
                },
                handler=self.create_recovery_checkpoint
            ),
            ToolDefinition(
                name="recovery_rollback",
                description="Rollback to a specific recovery checkpoint",
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
                            "enum": ["metadata_only", "data_only", "complete"],
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
                description="Generate comprehensive audit report for compliance and analysis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory"
                        },
                        "report_type": {
                            "type": "string",
                            "enum": ["summary", "detailed", "forensic"],
                            "description": "Type of report to generate",
                            "default": "summary"
                        },
                        "start_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Start date for report period (ISO format)"
                        },
                        "end_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "End date for report period (ISO format)"
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
                            "description": "Filter by actor"
                        },
                        "start_time": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Start time for search (ISO format)"
                        },
                        "end_time": {
                            "type": "string",
                            "format": "date-time",
                            "description": "End time for search (ISO format)"
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
                name="audit_status",
                description="Get audit system status and configuration",
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
                            "description": "Include performance component check",
                            "default": True
                        },
                        "include_recovery": {
                            "type": "boolean",
                            "description": "Include recovery component check",
                            "default": True
                        },
                        "include_audit": {
                            "type": "boolean",
                            "description": "Include audit component check",
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
        return await self.performance_ops.optimize_performance(arguments)

    async def get_performance_recommendations(self, arguments: Dict[str, Any]) -> str:
        """Get performance optimization recommendations."""
        return await self.performance_ops.get_performance_recommendations(arguments)

    async def create_recovery_checkpoint(self, arguments: Dict[str, Any]) -> str:
        """Create a recovery checkpoint."""
        return await self.recovery_ops.create_recovery_checkpoint(arguments)

    async def rollback_to_checkpoint(self, arguments: Dict[str, Any]) -> str:
        """Rollback to a recovery checkpoint."""
        return await self.recovery_ops.rollback_to_checkpoint(arguments)

    async def get_recovery_status(self, arguments: Dict[str, Any]) -> str:
        """Get recovery system status."""
        return await self.recovery_ops.get_recovery_status(arguments)

    async def generate_audit_report(self, arguments: Dict[str, Any]) -> str:
        """Generate comprehensive audit report."""
        return await self.audit_ops.generate_audit_report(arguments)

    async def search_audit_events(self, arguments: Dict[str, Any]) -> str:
        """Search audit events with specific criteria."""
        return await self.audit_ops.search_audit_events(arguments)

    async def get_audit_status(self, arguments: Dict[str, Any]) -> str:
        """Get audit system status."""
        return await self.audit_ops.get_audit_status(arguments)

    async def system_health_check(self, arguments: Dict[str, Any]) -> str:
        """Run comprehensive system health check."""
        return await self.health_ops.system_health_check(arguments)