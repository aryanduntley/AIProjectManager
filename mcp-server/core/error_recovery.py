"""
Error Recovery and Rollback System for MCP Instance Management
Provides comprehensive error recovery, rollback capabilities, and failure handling
"""

import os
import shutil
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import traceback

from ..database.db_manager import DatabaseManager
from ..database.git_queries import GitQueries


class RecoveryLevel(Enum):
    """Levels of recovery operations"""
    MINIMAL = "minimal"      # Basic cleanup only
    PARTIAL = "partial"      # Restore critical state
    COMPLETE = "complete"    # Full rollback to previous state


class OperationType(Enum):
    """Types of operations that can be rolled back"""
    INSTANCE_CREATION = "instance_creation"
    INSTANCE_MERGE = "instance_merge"
    CONFLICT_RESOLUTION = "conflict_resolution"
    DATABASE_OPERATION = "database_operation"
    FILE_OPERATION = "file_operation"


class RecoveryPoint:
    """Represents a point in time that can be rolled back to"""
    def __init__(self, operation_type: OperationType, timestamp: datetime,
                 description: str, data: Dict[str, Any]):
        self.id = f"{operation_type.value}_{int(timestamp.timestamp())}"
        self.operation_type = operation_type
        self.timestamp = timestamp
        self.description = description
        self.data = data
        self.rollback_data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "operation_type": self.operation_type.value,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "data": self.data,
            "rollback_data": self.rollback_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecoveryPoint':
        point = cls(
            operation_type=OperationType(data["operation_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            description=data["description"],
            data=data["data"]
        )
        point.id = data["id"]
        point.rollback_data = data.get("rollback_data", {})
        return point


class BackupManager:
    """Manages backups for rollback operations"""
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / ".mcp-instances" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, backup_id: str, paths: List[Path]) -> Dict[str, Any]:
        """Create backup of specified paths"""
        try:
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir(exist_ok=True)
            
            backed_up_files = []
            for path in paths:
                if path.exists():
                    if path.is_file():
                        # Backup file
                        relative_path = path.relative_to(self.project_root)
                        backup_file_path = backup_path / relative_path
                        backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(path, backup_file_path)
                        backed_up_files.append(str(relative_path))
                    elif path.is_dir():
                        # Backup directory
                        relative_path = path.relative_to(self.project_root)
                        backup_dir_path = backup_path / relative_path
                        shutil.copytree(path, backup_dir_path, dirs_exist_ok=True)
                        backed_up_files.append(str(relative_path))
            
            # Create backup metadata
            metadata = {
                "backup_id": backup_id,
                "created_at": datetime.now().isoformat(),
                "files": backed_up_files,
                "total_files": len(backed_up_files)
            }
            
            metadata_file = backup_path / ".backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "files_backed_up": len(backed_up_files)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Backup creation failed: {str(e)}"
            }
    
    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore from backup"""
        try:
            backup_path = self.backup_dir / backup_id
            if not backup_path.exists():
                return {
                    "success": False,
                    "error": f"Backup '{backup_id}' not found"
                }
            
            # Read backup metadata
            metadata_file = backup_path / ".backup_metadata.json"
            if not metadata_file.exists():
                return {
                    "success": False,
                    "error": f"Backup metadata not found for '{backup_id}'"
                }
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            restored_files = []
            for relative_path in metadata["files"]:
                backup_item_path = backup_path / relative_path
                target_path = self.project_root / relative_path
                
                if backup_item_path.exists():
                    if backup_item_path.is_file():
                        # Restore file
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(backup_item_path, target_path)
                        restored_files.append(relative_path)
                    elif backup_item_path.is_dir():
                        # Restore directory
                        if target_path.exists():
                            shutil.rmtree(target_path)
                        shutil.copytree(backup_item_path, target_path)
                        restored_files.append(relative_path)
            
            return {
                "success": True,
                "files_restored": len(restored_files),
                "backup_metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Backup restoration failed: {str(e)}"
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        try:
            if not self.backup_dir.exists():
                return backups
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    metadata_file = backup_dir / ".backup_metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            backups.append(metadata)
                        except Exception:
                            # Skip corrupted backup metadata
                            continue
        except Exception:
            pass
        
        return sorted(backups, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def cleanup_old_backups(self, keep_days: int = 30) -> Dict[str, Any]:
        """Clean up old backups"""
        try:
            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 3600)
            cleaned_backups = []
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir():
                    metadata_file = backup_dir / ".backup_metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            backup_time = datetime.fromisoformat(metadata["created_at"]).timestamp()
                            if backup_time < cutoff_date:
                                shutil.rmtree(backup_dir)
                                cleaned_backups.append(metadata["backup_id"])
                        except Exception:
                            continue
            
            return {
                "success": True,
                "cleaned_backups": len(cleaned_backups),
                "backup_ids": cleaned_backups
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Backup cleanup failed: {str(e)}"
            }


class ErrorRecoveryManager:
    """Main error recovery and rollback system"""
    def __init__(self, project_root: Path, db_manager: DatabaseManager):
        self.project_root = Path(project_root)
        self.db_manager = db_manager
        self.git_queries = GitQueries(db_manager)
        
        # Recovery components
        self.backup_manager = BackupManager(project_root)
        self.recovery_points = []
        self.recovery_log_file = self.project_root / ".mcp-instances" / ".recovery_log.jsonl"
        
        # Ensure recovery log directory exists
        self.recovery_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def create_recovery_point(self, operation_type: OperationType, 
                            description: str, context_data: Dict[str, Any]) -> str:
        """Create a recovery point before a critical operation"""
        try:
            recovery_point = RecoveryPoint(
                operation_type=operation_type,
                timestamp=datetime.now(),
                description=description,
                data=context_data
            )
            
            # Create backup of critical files
            backup_paths = self._get_backup_paths_for_operation(operation_type, context_data)
            backup_result = self.backup_manager.create_backup(recovery_point.id, backup_paths)
            
            if backup_result["success"]:
                recovery_point.rollback_data = {
                    "backup_id": recovery_point.id,
                    "backup_paths": [str(p) for p in backup_paths],
                    "backup_result": backup_result
                }
            
            # Store recovery point
            self.recovery_points.append(recovery_point)
            
            # Log recovery point creation
            self._log_recovery_event("recovery_point_created", {
                "recovery_point_id": recovery_point.id,
                "operation_type": operation_type.value,
                "description": description,
                "backup_success": backup_result["success"]
            })
            
            return recovery_point.id
            
        except Exception as e:
            self._log_recovery_event("recovery_point_creation_failed", {
                "operation_type": operation_type.value,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return ""
    
    def _get_backup_paths_for_operation(self, operation_type: OperationType, 
                                      context_data: Dict[str, Any]) -> List[Path]:
        """Determine what paths need backup for different operation types"""
        backup_paths = []
        
        if operation_type == OperationType.INSTANCE_CREATION:
            # Backup main instance and instances directory
            backup_paths.extend([
                self.project_root / "projectManagement",
                self.project_root / ".mcp-instances"
            ])
        
        elif operation_type == OperationType.INSTANCE_MERGE:
            # Backup main instance, source instance, and merge records
            backup_paths.append(self.project_root / "projectManagement")
            
            source_instance = context_data.get("source_instance")
            if source_instance:
                source_path = self.project_root / ".mcp-instances" / "active" / source_instance
                if source_path.exists():
                    backup_paths.append(source_path)
        
        elif operation_type == OperationType.CONFLICT_RESOLUTION:
            # Backup main instance and conflict workspace
            backup_paths.extend([
                self.project_root / "projectManagement",
                self.project_root / ".mcp-instances" / "conflicts"
            ])
        
        elif operation_type == OperationType.DATABASE_OPERATION:
            # Backup database
            db_path = self.project_root / "projectManagement" / "project.db"
            if db_path.exists():
                backup_paths.append(db_path)
        
        elif operation_type == OperationType.FILE_OPERATION:
            # Backup specific files mentioned in context
            file_paths = context_data.get("file_paths", [])
            for file_path in file_paths:
                path = Path(file_path)
                if path.exists():
                    backup_paths.append(path)
        
        return backup_paths
    
    def rollback_to_recovery_point(self, recovery_point_id: str, 
                                 level: RecoveryLevel = RecoveryLevel.COMPLETE) -> Dict[str, Any]:
        """Rollback to a specific recovery point"""
        try:
            # Find recovery point
            recovery_point = None
            for point in self.recovery_points:
                if point.id == recovery_point_id:
                    recovery_point = point
                    break
            
            if not recovery_point:
                return {
                    "success": False,
                    "error": f"Recovery point '{recovery_point_id}' not found"
                }
            
            rollback_actions = []
            
            # Restore from backup
            if level in [RecoveryLevel.PARTIAL, RecoveryLevel.COMPLETE]:
                backup_id = recovery_point.rollback_data.get("backup_id")
                if backup_id:
                    restore_result = self.backup_manager.restore_backup(backup_id)
                    if restore_result["success"]:
                        rollback_actions.append(f"Restored {restore_result['files_restored']} files from backup")
                    else:
                        rollback_actions.append(f"Backup restoration failed: {restore_result['error']}")
            
            # Database rollback
            if level == RecoveryLevel.COMPLETE:
                db_rollback_result = self._rollback_database_changes(recovery_point)
                if db_rollback_result["success"]:
                    rollback_actions.append("Database changes rolled back")
                else:
                    rollback_actions.append(f"Database rollback failed: {db_rollback_result['error']}")
            
            # Operation-specific rollback
            operation_rollback_result = self._rollback_operation_specific(recovery_point, level)
            rollback_actions.extend(operation_rollback_result.get("actions", []))
            
            # Log rollback
            self._log_recovery_event("rollback_completed", {
                "recovery_point_id": recovery_point_id,
                "level": level.value,
                "actions": rollback_actions
            })
            
            return {
                "success": True,
                "rollback_actions": rollback_actions,
                "recovery_point": recovery_point.to_dict()
            }
            
        except Exception as e:
            self._log_recovery_event("rollback_failed", {
                "recovery_point_id": recovery_point_id,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {
                "success": False,
                "error": f"Rollback failed: {str(e)}"
            }
    
    def _rollback_database_changes(self, recovery_point: RecoveryPoint) -> Dict[str, Any]:
        """Rollback database changes"""
        try:
            # This is a simplified database rollback
            # In a real implementation, this would use database transactions or more sophisticated rollback
            
            if recovery_point.operation_type == OperationType.INSTANCE_CREATION:
                # Remove instance from database
                instance_id = recovery_point.data.get("instance_id")
                if instance_id:
                    cursor = self.db_manager.connection.cursor()
                    cursor.execute("DELETE FROM mcp_instances WHERE instance_id = ?", (instance_id,))
                    self.db_manager.connection.commit()
            
            elif recovery_point.operation_type == OperationType.INSTANCE_MERGE:
                # Rollback merge record
                merge_id = recovery_point.data.get("merge_id")
                if merge_id:
                    cursor = self.db_manager.connection.cursor()
                    cursor.execute("DELETE FROM instance_merges WHERE merge_id = ?", (merge_id,))
                    self.db_manager.connection.commit()
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _rollback_operation_specific(self, recovery_point: RecoveryPoint, 
                                   level: RecoveryLevel) -> Dict[str, Any]:
        """Handle operation-specific rollback logic"""
        actions = []
        
        try:
            if recovery_point.operation_type == OperationType.INSTANCE_CREATION:
                # Clean up instance workspace
                instance_id = recovery_point.data.get("instance_id")
                if instance_id:
                    workspace_path = self.project_root / ".mcp-instances" / "active" / instance_id
                    if workspace_path.exists():
                        shutil.rmtree(workspace_path)
                        actions.append(f"Removed instance workspace: {instance_id}")
            
            elif recovery_point.operation_type == OperationType.INSTANCE_MERGE:
                # Clean up merge artifacts
                merge_id = recovery_point.data.get("merge_id")
                if merge_id:
                    conflict_workspace = self.project_root / ".mcp-instances" / "conflicts" / merge_id
                    if conflict_workspace.exists():
                        shutil.rmtree(conflict_workspace)
                        actions.append(f"Removed merge conflict workspace: {merge_id}")
            
            return {"success": True, "actions": actions}
            
        except Exception as e:
            return {"success": False, "error": str(e), "actions": actions}
    
    def handle_operation_failure(self, operation_type: OperationType, 
                                error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failure of an operation with automatic recovery"""
        try:
            # Log the failure
            failure_id = f"failure_{int(datetime.now().timestamp())}"
            self._log_recovery_event("operation_failed", {
                "failure_id": failure_id,
                "operation_type": operation_type.value,
                "error": str(error),
                "context": context,
                "traceback": traceback.format_exc()
            })
            
            # Check if there's a recent recovery point for this operation
            recent_recovery_point = None
            for point in reversed(self.recovery_points):
                if (point.operation_type == operation_type and 
                    (datetime.now() - point.timestamp).total_seconds() < 3600):  # Within 1 hour
                    recent_recovery_point = point
                    break
            
            recovery_actions = []
            
            if recent_recovery_point:
                # Attempt automatic rollback
                rollback_result = self.rollback_to_recovery_point(
                    recent_recovery_point.id, 
                    RecoveryLevel.PARTIAL
                )
                
                if rollback_result["success"]:
                    recovery_actions.extend(rollback_result["rollback_actions"])
                    recovery_actions.append("Automatic rollback completed")
                else:
                    recovery_actions.append(f"Automatic rollback failed: {rollback_result['error']}")
            
            # Additional cleanup based on operation type
            cleanup_result = self._cleanup_failed_operation(operation_type, context)
            recovery_actions.extend(cleanup_result.get("actions", []))
            
            return {
                "success": True,
                "failure_id": failure_id,
                "recovery_actions": recovery_actions,
                "automatic_rollback": recent_recovery_point is not None
            }
            
        except Exception as recovery_error:
            self._log_recovery_event("recovery_handling_failed", {
                "original_error": str(error),
                "recovery_error": str(recovery_error),
                "traceback": traceback.format_exc()
            })
            return {
                "success": False,
                "error": f"Recovery handling failed: {str(recovery_error)}"
            }
    
    def _cleanup_failed_operation(self, operation_type: OperationType, 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Cleanup artifacts from failed operations"""
        actions = []
        
        try:
            if operation_type == OperationType.INSTANCE_CREATION:
                # Clean up partial instance creation
                instance_id = context.get("instance_id")
                if instance_id:
                    # Remove partial workspace
                    workspace_path = self.project_root / ".mcp-instances" / "active" / instance_id
                    if workspace_path.exists():
                        shutil.rmtree(workspace_path)
                        actions.append(f"Cleaned up partial workspace: {instance_id}")
                    
                    # Remove database record if created
                    try:
                        cursor = self.db_manager.connection.cursor()
                        cursor.execute("DELETE FROM mcp_instances WHERE instance_id = ?", (instance_id,))
                        if cursor.rowcount > 0:
                            self.db_manager.connection.commit()
                            actions.append(f"Removed database record: {instance_id}")
                    except Exception:
                        pass
            
            elif operation_type == OperationType.INSTANCE_MERGE:
                # Clean up partial merge
                merge_id = context.get("merge_id")
                if merge_id:
                    # Remove merge record
                    try:
                        cursor = self.db_manager.connection.cursor()
                        cursor.execute("DELETE FROM instance_merges WHERE merge_id = ?", (merge_id,))
                        if cursor.rowcount > 0:
                            self.db_manager.connection.commit()
                            actions.append(f"Removed partial merge record: {merge_id}")
                    except Exception:
                        pass
            
            return {"success": True, "actions": actions}
            
        except Exception as e:
            return {"success": False, "error": str(e), "actions": actions}
    
    def get_recovery_status(self) -> Dict[str, Any]:
        """Get comprehensive recovery system status"""
        try:
            # Get recovery points
            recovery_points_data = [point.to_dict() for point in self.recovery_points]
            
            # Get backup status
            available_backups = self.backup_manager.list_backups()
            
            # Get recent recovery events
            recent_events = self._get_recent_recovery_events(limit=20)
            
            return {
                "success": True,
                "recovery_points": {
                    "total": len(recovery_points_data),
                    "recent": recovery_points_data[-5:] if recovery_points_data else []
                },
                "backups": {
                    "total": len(available_backups),
                    "recent": available_backups[:5]
                },
                "recent_events": recent_events,
                "system_status": "healthy"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Could not get recovery status: {str(e)}"
            }
    
    def _log_recovery_event(self, event_type: str, data: Dict[str, Any]):
        """Log recovery system events"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data
            }
            
            with open(self.recovery_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            print(f"Warning: Could not log recovery event: {e}")
    
    def _get_recent_recovery_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent recovery events from log"""
        events = []
        try:
            if self.recovery_log_file.exists():
                with open(self.recovery_log_file, 'r') as f:
                    lines = f.readlines()
                
                # Get last 'limit' lines
                for line in lines[-limit:]:
                    try:
                        event = json.loads(line.strip())
                        events.append(event)
                    except Exception:
                        continue
        except Exception:
            pass
        
        return events
    
    def cleanup_old_recovery_data(self, keep_days: int = 7) -> Dict[str, Any]:
        """Clean up old recovery points and backups"""
        try:
            cleanup_results = []
            
            # Clean up old recovery points
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            old_points = [p for p in self.recovery_points if p.timestamp < cutoff_date]
            
            for point in old_points:
                self.recovery_points.remove(point)
            
            cleanup_results.append(f"Removed {len(old_points)} old recovery points")
            
            # Clean up old backups
            backup_cleanup = self.backup_manager.cleanup_old_backups(keep_days)
            if backup_cleanup["success"]:
                cleanup_results.append(f"Cleaned up {backup_cleanup['cleaned_backups']} old backups")
            
            return {
                "success": True,
                "cleanup_actions": cleanup_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Cleanup failed: {str(e)}"
            }