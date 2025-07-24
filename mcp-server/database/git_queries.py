"""
Database queries for Git integration and branch management
Handles all database operations related to Git state tracking and branch coordination
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
            
            # Branch statistics (using new Git branch-based system)
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                       SUM(CASE WHEN status = 'merged' THEN 1 ELSE 0 END) as merged,
                       SUM(CASE WHEN status = 'deleted' THEN 1 ELSE 0 END) as deleted
                FROM git_branches
            """)
            branch_stats = cursor.fetchone()
            
            return {
                "git_states": {
                    "total": git_stats[0] if git_stats else 0,
                    "reconciled": git_stats[1] if git_stats else 0,
                    "pending_reconciliation": git_stats[2] if git_stats else 0
                },
                "branches": {
                    "total": branch_stats[0] if branch_stats else 0,
                    "active": branch_stats[1] if branch_stats else 0,
                    "merged": branch_stats[2] if branch_stats else 0,
                    "deleted": branch_stats[3] if branch_stats else 0
                }
            }
            
        except Exception as e:
            print(f"Error getting Git integration stats: {e}")
            return {
                "git_states": {"total": 0, "reconciled": 0, "pending_reconciliation": 0},
                "branches": {"total": 0, "active": 0, "merged": 0, "deleted": 0}
            }