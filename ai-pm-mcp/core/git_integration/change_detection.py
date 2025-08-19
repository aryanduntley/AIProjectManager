"""
Change Detection Module
Handles project code change detection and Git state analysis.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import utilities from parent module paths
from ...utils.project_paths import get_management_folder_name


class ChangeDetection:
    """Project code change detection and analysis."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties
        self.project_root = parent_instance.project_root
        self.db_manager = parent_instance.db_manager
        self.config_manager = parent_instance.config_manager
        self.server_instance = parent_instance.server_instance
        self.git_dir = parent_instance.git_dir
    
    # ============================================================================
    # PROJECT CODE CHANGE DETECTION
    # ============================================================================
    
    def detect_project_code_changes(self) -> Dict[str, Any]:
        """
        Detect changes in project code since last known Git state
        Returns comprehensive change analysis for organizational reconciliation
        """
        # Get current Git state
        current_hash = self.get_current_git_hash()
        if not current_hash:
            return {
                "success": False,
                "error": "Could not determine current Git hash",
                "changes_detected": False
            }
        
        # Get last known state from database
        last_known_state = self._get_last_known_git_state()
        
        if not last_known_state or last_known_state["current_git_hash"] != current_hash:
            # Changes detected - analyze them
            changes = self._analyze_git_changes(
                last_known_state["current_git_hash"] if last_known_state else None,
                current_hash
            )
            
            # Update database with new state
            self._update_git_project_state(current_hash, changes)
            
            return {
                "success": True,
                "changes_detected": True,
                "last_known_hash": last_known_state["current_git_hash"] if last_known_state else None,
                "current_hash": current_hash,
                "change_summary": changes["summary"],
                "affected_files": changes["files"],
                "affected_themes": changes["themes"],
                "reconciliation_needed": len(changes["themes"]) > 0
            }
        
        return {
            "success": True,
            "changes_detected": False,
            "current_hash": current_hash,
            "message": "No changes detected since last session"
        }
    
    def _get_last_known_git_state(self) -> Optional[Dict[str, Any]]:
        """Get last known Git state from database"""
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                SELECT current_git_hash, last_sync_timestamp, change_summary, affected_themes
                FROM git_project_state 
                WHERE project_root_path = ?
                ORDER BY created_at DESC 
                LIMIT 1
            """, (str(self.project_root),))
            
            row = cursor.fetchone()
            if row:
                return {
                    "current_git_hash": row[0],
                    "last_sync_timestamp": row[1],
                    "change_summary": row[2],
                    "affected_themes": json.loads(row[3]) if row[3] else []
                }
            return None
            
        except Exception as e:
            print(f"Error getting last known Git state: {e}")
            return None
    
    def _analyze_git_changes(self, last_hash: Optional[str], current_hash: str) -> Dict[str, Any]:
        """
        Analyze Git changes between two commits
        Returns detailed change analysis including affected themes
        """
        try:
            if not last_hash:
                # First time setup - treat all existing files as baseline
                return {
                    "summary": "Initial Git state recorded",
                    "files": [],
                    "themes": [],
                    "change_types": {"baseline": True}
                }
            
            # Get changed files between commits
            diff_result = subprocess.run([
                "git", "diff", "--name-status", f"{last_hash}..{current_hash}"
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            changed_files = []
            change_types = {"added": 0, "modified": 0, "deleted": 0}
            
            for line in diff_result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 2:
                    status = parts[0]
                    file_path = parts[1]
                    
                    # Skip project management files (organizational state)
                    management_folder = get_management_folder_name(self.config_manager)
                    if file_path.startswith(f'{management_folder}/'):
                        continue
                    
                    change_type = self._get_change_type_from_status(status)
                    changed_files.append({
                        "path": file_path,
                        "status": status,
                        "type": change_type
                    })
                    
                    if change_type in change_types:
                        change_types[change_type] += 1
            
            # Analyze theme impact
            affected_themes = self.parent._analyze_theme_impact(changed_files)
            
            # Generate summary
            summary = self._generate_change_summary(change_types, len(changed_files), affected_themes)
            
            return {
                "summary": summary,
                "files": changed_files,
                "themes": affected_themes,
                "change_types": change_types
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "summary": f"Error analyzing Git changes: {e.stderr}",
                "files": [],
                "themes": [],
                "change_types": {"error": True}
            }
    
    def _get_change_type_from_status(self, status: str) -> str:
        """Convert Git status code to change type"""
        if status.startswith('A'):
            return "added"
        elif status.startswith('M'):
            return "modified"
        elif status.startswith('D'):
            return "deleted"
        elif status.startswith('R'):
            return "renamed"
        else:
            return "modified"
    
    def _generate_change_summary(self, change_types: Dict[str, int], total_files: int, affected_themes: List[str]) -> str:
        """Generate human-readable change summary"""
        if change_types.get("baseline"):
            return "Initial Git state recorded - no previous changes to analyze"
        
        if total_files == 0:
            return "No project code changes detected"
        
        parts = []
        if change_types.get("added", 0) > 0:
            parts.append(f"{change_types['added']} files added")
        if change_types.get("modified", 0) > 0:
            parts.append(f"{change_types['modified']} files modified")
        if change_types.get("deleted", 0) > 0:
            parts.append(f"{change_types['deleted']} files deleted")
        
        summary = f"Project code changes detected: {', '.join(parts)}"
        
        if affected_themes:
            summary += f" - Affected themes: {', '.join(affected_themes)}"
        
        return summary
    
    def _update_git_project_state(self, current_hash: str, changes: Dict[str, Any]) -> None:
        """Update database with current Git project state"""
        try:
            cursor = self.db_manager.connection.cursor()
            
            # Get last known hash for comparison
            last_known_hash = None
            last_state = self._get_last_known_git_state()
            if last_state:
                last_known_hash = last_state["current_git_hash"]
            
            # Insert new Git project state record
            cursor.execute("""
                INSERT INTO git_project_state (
                    project_root_path, current_git_hash, last_known_hash,
                    change_summary, affected_themes, reconciliation_status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(self.project_root),
                current_hash,
                last_known_hash,
                changes["summary"],
                json.dumps(changes["themes"]),
                "pending" if changes["themes"] else "completed"
            ))
            
            # Record individual file changes for impact tracking
            git_state_id = cursor.lastrowid
            for file_change in changes["files"]:
                # Analyze per-file theme impact
                file_themes = self.parent._analyze_single_file_theme_impact(file_change["path"])
                
                cursor.execute("""
                    INSERT INTO git_change_impacts (
                        git_state_id, file_path, change_type, affected_themes
                    ) VALUES (?, ?, ?, ?)
                """, (
                    git_state_id,
                    file_change["path"],
                    file_change["type"],
                    json.dumps(file_themes)
                ))
            
            self.db_manager.connection.commit()
            
        except Exception as e:
            print(f"Error updating Git project state: {e}")
            self.db_manager.connection.rollback()