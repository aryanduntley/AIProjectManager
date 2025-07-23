"""
Database queries for Git integration and instance management
Handles all database operations related to Git state tracking and MCP instance coordination
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class GitQueries:
    """Database query interface for Git integration functionality"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.connection = db_manager.connection
    
    # ============================================================================
    # GIT PROJECT STATE MANAGEMENT
    # ============================================================================
    
    def get_current_git_state(self, project_root: str) -> Optional[Dict[str, Any]]:
        """Get the most recent Git state for a project"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, current_git_hash, last_known_hash, last_sync_timestamp,
                       change_summary, affected_themes, reconciliation_status,
                       reconciliation_notes, created_at, updated_at
                FROM git_project_state 
                WHERE project_root_path = ?
                ORDER BY created_at DESC 
                LIMIT 1
            """, (project_root,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "current_git_hash": row[1],
                    "last_known_hash": row[2],
                    "last_sync_timestamp": row[3],
                    "change_summary": row[4],
                    "affected_themes": json.loads(row[5]) if row[5] else [],
                    "reconciliation_status": row[6],
                    "reconciliation_notes": row[7],
                    "created_at": row[8],
                    "updated_at": row[9]
                }
            return None
            
        except Exception as e:
            print(f"Error getting current Git state: {e}")
            return None
    
    def record_git_state(self, project_root: str, current_hash: str, 
                        last_known_hash: Optional[str] = None,
                        change_summary: str = "", 
                        affected_themes: List[str] = None) -> Optional[int]:
        """Record new Git project state"""
        if affected_themes is None:
            affected_themes = []
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO git_project_state (
                    project_root_path, current_git_hash, last_known_hash,
                    change_summary, affected_themes, reconciliation_status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project_root, current_hash, last_known_hash, 
                change_summary, json.dumps(affected_themes),
                "pending" if affected_themes else "completed"
            ))
            
            git_state_id = cursor.lastrowid
            self.connection.commit()
            return git_state_id
            
        except Exception as e:
            print(f"Error recording Git state: {e}")
            self.connection.rollback()
            return None
    
    def update_reconciliation_status(self, git_state_id: int, status: str, 
                                   notes: str = "") -> bool:
        """Update reconciliation status for a Git state record"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE git_project_state 
                SET reconciliation_status = ?, reconciliation_notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, notes, git_state_id))
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating reconciliation status: {e}")
            self.connection.rollback()
            return False
    
    def get_git_history(self, project_root: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Git state history for a project"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT current_git_hash, change_summary, affected_themes,
                       reconciliation_status, created_at
                FROM git_project_state 
                WHERE project_root_path = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (project_root, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "git_hash": row[0],
                    "change_summary": row[1],
                    "affected_themes": json.loads(row[2]) if row[2] else [],
                    "reconciliation_status": row[3],
                    "created_at": row[4]
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting Git history: {e}")
            return []
    
    # ============================================================================
    # GIT CHANGE IMPACT TRACKING
    # ============================================================================
    
    def record_file_change_impact(self, git_state_id: int, file_path: str, 
                                 change_type: str, affected_themes: List[str] = None,
                                 impact_severity: str = "low") -> bool:
        """Record impact of a specific file change"""
        if affected_themes is None:
            affected_themes = []
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO git_change_impacts (
                    git_state_id, file_path, change_type, affected_themes, impact_severity
                ) VALUES (?, ?, ?, ?, ?)
            """, (git_state_id, file_path, change_type, json.dumps(affected_themes), impact_severity))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Error recording file change impact: {e}")
            self.connection.rollback()
            return False
    
    def get_change_impacts_for_git_state(self, git_state_id: int) -> List[Dict[str, Any]]:
        """Get all change impacts for a specific Git state"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT file_path, change_type, affected_themes, impact_severity,
                       reconciliation_action, reconciliation_status, notes
                FROM git_change_impacts 
                WHERE git_state_id = ?
                ORDER BY impact_severity DESC, file_path ASC
            """, (git_state_id,))
            
            impacts = []
            for row in cursor.fetchall():
                impacts.append({
                    "file_path": row[0],
                    "change_type": row[1],
                    "affected_themes": json.loads(row[2]) if row[2] else [],
                    "impact_severity": row[3],
                    "reconciliation_action": row[4],
                    "reconciliation_status": row[5],
                    "notes": row[6]
                })
            
            return impacts
            
        except Exception as e:
            print(f"Error getting change impacts: {e}")
            return []
    
    def update_change_impact_reconciliation(self, git_state_id: int, file_path: str,
                                          action: str, status: str, notes: str = "") -> bool:
        """Update reconciliation status for a specific file change impact"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE git_change_impacts 
                SET reconciliation_action = ?, reconciliation_status = ?, notes = ?
                WHERE git_state_id = ? AND file_path = ?
            """, (action, status, notes, git_state_id, file_path))
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating change impact reconciliation: {e}")
            self.connection.rollback()
            return False
    
    # ============================================================================
    # MCP INSTANCE MANAGEMENT
    # ============================================================================
    
    def create_mcp_instance(self, instance_id: str, instance_name: str, 
                           created_from: str = "main", created_by: str = "",
                           purpose: str = "", primary_themes: List[str] = None,
                           related_flows: List[str] = None, 
                           expected_duration: str = "") -> bool:
        """Create new MCP instance record"""
        if primary_themes is None:
            primary_themes = []
        if related_flows is None:
            related_flows = []
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO mcp_instances (
                    instance_id, instance_name, created_from, created_by, purpose,
                    primary_themes, related_flows, expected_duration, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """, (
                instance_id, instance_name, created_from, created_by, purpose,
                json.dumps(primary_themes), json.dumps(related_flows), expected_duration
            ))
            
            self.connection.commit()
            return True
            
        except sqlite3.IntegrityError:
            print(f"Instance ID '{instance_id}' already exists")
            return False
        except Exception as e:
            print(f"Error creating MCP instance: {e}")
            self.connection.rollback()
            return False
    
    def get_mcp_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get MCP instance details"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT instance_id, instance_name, created_from, created_by, purpose,
                       primary_themes, related_flows, expected_duration, status,
                       workspace_path, database_path, git_base_hash,
                       created_at, last_activity, completed_at, archived_at
                FROM mcp_instances 
                WHERE instance_id = ?
            """, (instance_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "instance_id": row[0],
                    "instance_name": row[1],
                    "created_from": row[2],
                    "created_by": row[3],
                    "purpose": row[4],
                    "primary_themes": json.loads(row[5]) if row[5] else [],
                    "related_flows": json.loads(row[6]) if row[6] else [],
                    "expected_duration": row[7],
                    "status": row[8],
                    "workspace_path": row[9],
                    "database_path": row[10],
                    "git_base_hash": row[11],
                    "created_at": row[12],
                    "last_activity": row[13],
                    "completed_at": row[14],
                    "archived_at": row[15]
                }
            return None
            
        except Exception as e:
            print(f"Error getting MCP instance: {e}")
            return None
    
    def list_active_instances(self) -> List[Dict[str, Any]]:
        """List all active MCP instances"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT instance_id, instance_name, created_by, purpose, primary_themes,
                       created_at, last_activity
                FROM mcp_instances 
                WHERE status = 'active'
                ORDER BY last_activity DESC
            """)
            
            instances = []
            for row in cursor.fetchall():
                instances.append({
                    "instance_id": row[0],
                    "instance_name": row[1],
                    "created_by": row[2],
                    "purpose": row[3],
                    "primary_themes": json.loads(row[4]) if row[4] else [],
                    "created_at": row[5],
                    "last_activity": row[6]
                })
            
            return instances
            
        except Exception as e:
            print(f"Error listing active instances: {e}")
            return []
    
    def update_instance_status(self, instance_id: str, status: str, 
                              workspace_path: str = "", database_path: str = "",
                              git_base_hash: str = "") -> bool:
        """Update MCP instance status and paths"""
        try:
            cursor = self.connection.cursor()
            
            # Build dynamic update query based on provided parameters
            update_fields = ["status = ?"]
            params = [status]
            
            if workspace_path:
                update_fields.append("workspace_path = ?")
                params.append(workspace_path)
            
            if database_path:
                update_fields.append("database_path = ?")
                params.append(database_path)
                
            if git_base_hash:
                update_fields.append("git_base_hash = ?")
                params.append(git_base_hash)
            
            if status in ['completed', 'archived']:
                update_fields.append(f"{status}_at = CURRENT_TIMESTAMP")
            
            params.append(instance_id)
            
            cursor.execute(f"""
                UPDATE mcp_instances 
                SET {', '.join(update_fields)}
                WHERE instance_id = ?
            """, params)
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating instance status: {e}")
            self.connection.rollback()
            return False
    
    def archive_instance(self, instance_id: str) -> bool:
        """Archive an MCP instance"""
        return self.update_instance_status(instance_id, "archived")
    
    # ============================================================================
    # INSTANCE MERGE MANAGEMENT
    # ============================================================================
    
    def create_instance_merge(self, merge_id: str, source_instance: str,
                             target_instance: str = "main", merged_by: str = "") -> Optional[int]:
        """Create new instance merge record"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO instance_merges (
                    merge_id, source_instance, target_instance, merge_status, merged_by
                ) VALUES (?, ?, ?, 'pending', ?)
            """, (merge_id, source_instance, target_instance, merged_by))
            
            merge_record_id = cursor.lastrowid
            self.connection.commit()
            return merge_record_id
            
        except Exception as e:
            print(f"Error creating instance merge: {e}")
            self.connection.rollback()
            return None
    
    def update_merge_status(self, merge_id: str, status: str, 
                           conflicts_detected: int = 0, conflicts_resolved: int = 0,
                           conflict_types: List[str] = None, resolution_strategy: Dict = None,
                           merge_summary: str = "", merge_notes: str = "") -> bool:
        """Update instance merge status and details"""
        if conflict_types is None:
            conflict_types = []
        if resolution_strategy is None:
            resolution_strategy = {}
            
        try:
            cursor = self.connection.cursor()
            
            update_fields = [
                "merge_status = ?", "conflicts_detected = ?", "conflicts_resolved = ?",
                "conflict_types = ?", "resolution_strategy = ?", "merge_summary = ?", "merge_notes = ?"
            ]
            params = [
                status, conflicts_detected, conflicts_resolved,
                json.dumps(conflict_types), json.dumps(resolution_strategy),
                merge_summary, merge_notes
            ]
            
            if status == 'completed':
                update_fields.append("completed_at = CURRENT_TIMESTAMP")
            elif status == 'failed':
                update_fields.append("failed_at = CURRENT_TIMESTAMP")
            
            params.append(merge_id)
            
            cursor.execute(f"""
                UPDATE instance_merges 
                SET {', '.join(update_fields)}
                WHERE merge_id = ?
            """, params)
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating merge status: {e}")
            self.connection.rollback()
            return False
    
    def get_merge_record(self, merge_id: str) -> Optional[Dict[str, Any]]:
        """Get instance merge record details"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT merge_id, source_instance, target_instance, merge_status,
                       conflicts_detected, conflicts_resolved, conflict_types,
                       resolution_strategy, merge_summary, database_conflicts,
                       organizational_conflicts, merged_by, merge_notes,
                       started_at, completed_at, failed_at
                FROM instance_merges 
                WHERE merge_id = ?
            """, (merge_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "merge_id": row[0],
                    "source_instance": row[1],
                    "target_instance": row[2],
                    "merge_status": row[3],
                    "conflicts_detected": row[4],
                    "conflicts_resolved": row[5],
                    "conflict_types": json.loads(row[6]) if row[6] else [],
                    "resolution_strategy": json.loads(row[7]) if row[7] else {},
                    "merge_summary": row[8],
                    "database_conflicts": json.loads(row[9]) if row[9] else [],
                    "organizational_conflicts": json.loads(row[10]) if row[10] else [],
                    "merged_by": row[11],
                    "merge_notes": row[12],
                    "started_at": row[13],
                    "completed_at": row[14],
                    "failed_at": row[15]
                }
            return None
            
        except Exception as e:
            print(f"Error getting merge record: {e}")
            return None
    
    def get_merge_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get merge history across all instances"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT merge_id, source_instance, target_instance, merge_status,
                       conflicts_detected, conflicts_resolved, merge_summary,
                       merged_by, started_at, completed_at
                FROM instance_merges 
                ORDER BY started_at DESC 
                LIMIT ?
            """, (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "merge_id": row[0],
                    "source_instance": row[1],
                    "target_instance": row[2],
                    "merge_status": row[3],
                    "conflicts_detected": row[4],
                    "conflicts_resolved": row[5],
                    "merge_summary": row[6],
                    "merged_by": row[7],
                    "started_at": row[8],
                    "completed_at": row[9]
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting merge history: {e}")
            return []
    
    # ============================================================================
    # INSTANCE WORKSPACE FILE TRACKING
    # ============================================================================
    
    def record_instance_file_operation(self, instance_id: str, file_path: str,
                                     file_type: str, operation: str,
                                     original_content_hash: str = "",
                                     modified_content_hash: str = "") -> bool:
        """Record file operation in instance workspace"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO instance_workspace_files (
                    instance_id, file_path, file_type, operation,
                    original_content_hash, modified_content_hash
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (instance_id, file_path, file_type, operation, 
                  original_content_hash, modified_content_hash))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Error recording instance file operation: {e}")
            self.connection.rollback()
            return False
    
    def get_instance_file_changes(self, instance_id: str) -> List[Dict[str, Any]]:
        """Get all file changes for an instance"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT file_path, file_type, operation, modification_timestamp,
                       merge_status, conflict_resolution
                FROM instance_workspace_files 
                WHERE instance_id = ?
                ORDER BY modification_timestamp DESC
            """, (instance_id,))
            
            changes = []
            for row in cursor.fetchall():
                changes.append({
                    "file_path": row[0],
                    "file_type": row[1],
                    "operation": row[2],
                    "modification_timestamp": row[3],
                    "merge_status": row[4],
                    "conflict_resolution": row[5]
                })
            
            return changes
            
        except Exception as e:
            print(f"Error getting instance file changes: {e}")
            return []
    
    def update_file_merge_status(self, instance_id: str, file_path: str,
                               merge_status: str, conflict_resolution: str = "") -> bool:
        """Update merge status for instance file"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE instance_workspace_files 
                SET merge_status = ?, conflict_resolution = ?
                WHERE instance_id = ? AND file_path = ?
            """, (merge_status, conflict_resolution, instance_id, file_path))
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating file merge status: {e}")
            self.connection.rollback()
            return False
    
    # ============================================================================
    # ANALYTICS AND REPORTING
    # ============================================================================
    
    def get_git_integration_stats(self, project_root: str) -> Dict[str, Any]:
        """Get Git integration statistics for a project"""
        try:
            cursor = self.connection.cursor()
            
            # Git state statistics
            cursor.execute("""
                SELECT COUNT(*), 
                       SUM(CASE WHEN reconciliation_status = 'completed' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN reconciliation_status = 'pending' THEN 1 ELSE 0 END) as pending
                FROM git_project_state 
                WHERE project_root_path = ?
            """, (project_root,))
            git_stats = cursor.fetchone()
            
            # Instance statistics
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN status = 'archived' THEN 1 ELSE 0 END) as archived
                FROM mcp_instances
            """)
            instance_stats = cursor.fetchone()
            
            # Merge statistics
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN merge_status = 'completed' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN merge_status = 'pending' THEN 1 ELSE 0 END) as pending,
                       SUM(CASE WHEN merge_status = 'failed' THEN 1 ELSE 0 END) as failed,
                       SUM(conflicts_detected) as total_conflicts,
                       SUM(conflicts_resolved) as resolved_conflicts
                FROM instance_merges
            """)
            merge_stats = cursor.fetchone()
            
            return {
                "git_states": {
                    "total": git_stats[0] if git_stats else 0,
                    "reconciled": git_stats[1] if git_stats else 0,
                    "pending_reconciliation": git_stats[2] if git_stats else 0
                },
                "instances": {
                    "total": instance_stats[0] if instance_stats else 0,
                    "active": instance_stats[1] if instance_stats else 0,
                    "completed": instance_stats[2] if instance_stats else 0,
                    "archived": instance_stats[3] if instance_stats else 0
                },
                "merges": {
                    "total": merge_stats[0] if merge_stats else 0,
                    "completed": merge_stats[1] if merge_stats else 0,
                    "pending": merge_stats[2] if merge_stats else 0,
                    "failed": merge_stats[3] if merge_stats else 0,
                    "total_conflicts": merge_stats[4] if merge_stats else 0,
                    "resolved_conflicts": merge_stats[5] if merge_stats else 0
                }
            }
            
        except Exception as e:
            print(f"Error getting Git integration stats: {e}")
            return {
                "git_states": {"total": 0, "reconciled": 0, "pending_reconciliation": 0},
                "instances": {"total": 0, "active": 0, "completed": 0, "archived": 0},
                "merges": {"total": 0, "completed": 0, "pending": 0, "failed": 0, 
                          "total_conflicts": 0, "resolved_conflicts": 0}
            }