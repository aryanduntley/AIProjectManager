"""
Organizational Reconciliation Module
Handles reconciliation of organizational state with code changes.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Import utilities from parent module paths
from ...utils.project_paths import get_themes_path, get_flows_path, get_tasks_path


class OrganizationalReconciliation:
    """Organizational state reconciliation with code changes."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties
        self.project_root = parent_instance.project_root
        self.db_manager = parent_instance.db_manager
        self.config_manager = parent_instance.config_manager
        self.server_instance = parent_instance.server_instance
        self.git_dir = parent_instance.git_dir
    
    # ============================================================================
    # ORGANIZATIONAL STATE RECONCILIATION
    # ============================================================================
    
    async def reconcile_organizational_state_with_code(self, change_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconcile organizational state (themes, flows, tasks) with detected code changes
        This is called when project code changes are detected during session boot
        """
        if not change_analysis.get("reconciliation_needed", False):
            return {
                "success": True,
                "action": "none",
                "message": "No organizational reconciliation needed"
            }
        
        reconciliation_result = {
            "success": True,
            "action": "reconciled",
            "message": "",
            "affected_themes": change_analysis.get("affected_themes", []),
            "theme_updates": [],
            "flow_updates": [],
            "task_updates": [],
            "requires_user_review": False
        }
        
        try:
            affected_themes = change_analysis.get("affected_themes", [])
            changed_files = change_analysis.get("files", [])
            
            # 1. Update theme files with new file references
            theme_updates = self._update_themes_with_file_changes(affected_themes, changed_files)
            reconciliation_result["theme_updates"] = theme_updates
            
            # 2. Check and update flows based on changed files
            flow_updates = self._update_flows_with_file_changes(affected_themes, changed_files)
            reconciliation_result["flow_updates"] = flow_updates
            
            # 3. Update task status if implementation files changed
            task_updates = self._update_tasks_with_file_changes(changed_files)
            reconciliation_result["task_updates"] = task_updates
            
            # 4. Determine if user review is required
            requires_review = (
                len(theme_updates) > 0 or
                len(flow_updates) > 0 or
                any(change["type"] == "deleted" for change in changed_files) or
                len(affected_themes) > 3  # Many themes affected
            )
            
            reconciliation_result["requires_user_review"] = requires_review
            
            # Generate summary message
            changes_summary = []
            if theme_updates:
                changes_summary.append(f"{len(theme_updates)} theme files updated")
            if flow_updates:
                changes_summary.append(f"{len(flow_updates)} flow references updated")
            if task_updates:
                changes_summary.append(f"{len(task_updates)} task statuses updated")
            
            if changes_summary:
                reconciliation_result["message"] = f"Organizational state reconciled: {', '.join(changes_summary)}"
            else:
                reconciliation_result["message"] = f"Code changes analyzed - {len(affected_themes)} themes identified but no updates needed"
            
            if requires_review:
                reconciliation_result["message"] += " - User review recommended"
            
            # Hook point: Organizational state reconciliation completed
            if self.server_instance and hasattr(self.server_instance, 'on_core_operation_complete'):
                await self.parent._trigger_git_hook("organizational_reconciliation_complete", {
                    "operation_type": "reconcile_organizational_state_with_code",
                    "affected_themes": reconciliation_result["affected_themes"],
                    "theme_updates": reconciliation_result["theme_updates"],
                    "flow_updates": reconciliation_result["flow_updates"],
                    "requires_user_review": reconciliation_result["requires_user_review"],
                    "success": reconciliation_result["success"]
                })
            
            return reconciliation_result
            
        except Exception as e:
            return {
                "success": False,
                "action": "error",
                "message": f"Error during organizational reconciliation: {str(e)}",
                "affected_themes": change_analysis.get("affected_themes", []),
                "requires_user_review": True
            }
    
    def _update_themes_with_file_changes(self, affected_themes: List[str], changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update theme files to reflect file changes"""
        theme_updates = []
        themes_dir = get_themes_path(self.project_root, self.config_manager)
        
        if not themes_dir.exists():
            return theme_updates
        
        try:
            for theme_name in affected_themes:
                theme_file = themes_dir / f"{theme_name}.json"
                if not theme_file.exists():
                    continue
                
                # Load existing theme data
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)
                
                if not isinstance(theme_data, dict) or "files" not in theme_data:
                    continue
                
                current_files = set(theme_data.get("files", []))
                updated_files = current_files.copy()
                changes_made = False
                
                # Process file changes for this theme
                for file_change in changed_files:
                    file_path = file_change["path"]
                    change_type = file_change["type"]
                    
                    # Check if this file belongs to this theme
                    file_themes = self._get_themes_for_file(file_path, {theme_name: theme_data})
                    if theme_name not in file_themes:
                        # Check if file should be added based on inference
                        inferred_themes = (
                            self._infer_themes_from_directory(file_path) +
                            self._infer_themes_from_patterns(file_path)
                        )
                        if theme_name not in inferred_themes:
                            continue
                    
                    if change_type == "added" and file_path not in current_files:
                        updated_files.add(file_path)
                        changes_made = True
                    elif change_type == "deleted" and file_path in current_files:
                        updated_files.discard(file_path)
                        changes_made = True
                
                # Save updated theme file if changes were made
                if changes_made:
                    theme_data["files"] = sorted(list(updated_files))
                    theme_data["lastModified"] = datetime.now().isoformat()
                    
                    with open(theme_file, 'w') as f:
                        json.dump(theme_data, f, indent=2)
                    
                    theme_updates.append({
                        "theme": theme_name,
                        "files_added": len(updated_files) - len(current_files),
                        "files_removed": len(current_files) - len(updated_files),
                        "action": "updated"
                    })
            
            return theme_updates
            
        except Exception as e:
            print(f"Error updating themes with file changes: {e}")
            return []
    
    def _update_flows_with_file_changes(self, affected_themes: List[str], changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update flow references based on file changes"""
        flow_updates = []
        flows_dir = get_flows_path(self.project_root, self.config_manager)
        
        if not flows_dir.exists():
            return flow_updates
        
        try:
            # Check flow-index.json for flows related to affected themes
            flow_index_path = flows_dir / "flow-index.json"
            if not flow_index_path.exists():
                return flow_updates
            
            with open(flow_index_path, 'r') as f:
                flow_index = json.load(f)
            
            flow_files = flow_index.get("flowFiles", [])
            
            for flow_info in flow_files:
                if not isinstance(flow_info, dict):
                    continue
                
                flow_file = flow_info.get("file", "")
                flow_themes = flow_info.get("primaryThemes", []) + flow_info.get("secondaryThemes", [])
                
                # Check if this flow is affected by theme changes
                if any(theme in affected_themes for theme in flow_themes):
                    flow_path = flows_dir / flow_file
                    if flow_path.exists():
                        # Mark flow for potential review
                        flow_updates.append({
                            "flow_file": flow_file,
                            "affected_themes": [t for t in flow_themes if t in affected_themes],
                            "action": "review_recommended"
                        })
            
            return flow_updates
            
        except Exception as e:
            print(f"Error updating flows with file changes: {e}")
            return []
    
    def _update_tasks_with_file_changes(self, changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update task status based on implementation file changes"""
        task_updates = []
        tasks_dir = get_tasks_path(self.project_root, self.config_manager)
        
        if not tasks_dir.exists():
            return task_updates
        
        try:
            # Check active tasks for file references
            active_tasks_dir = tasks_dir / "active"
            if active_tasks_dir.exists():
                for task_file in active_tasks_dir.glob("TASK-*.json"):
                    try:
                        with open(task_file, 'r') as f:
                            task_data = json.load(f)
                        
                        if not isinstance(task_data, dict):
                            continue
                        
                        # Check if any changed files are referenced in task subtasks
                        subtasks = task_data.get("subtasks", [])
                        task_affected = False
                        
                        for subtask in subtasks:
                            if not isinstance(subtask, dict):
                                continue
                            
                            subtask_files = subtask.get("files", [])
                            for file_change in changed_files:
                                if file_change["path"] in subtask_files:
                                    task_affected = True
                                    break
                            
                            if task_affected:
                                break
                        
                        if task_affected:
                            # Mark task as potentially needing review
                            task_updates.append({
                                "task_file": task_file.name,
                                "task_id": task_data.get("taskId", "unknown"),
                                "action": "implementation_files_changed"
                            })
                    
                    except (json.JSONDecodeError, IOError):
                        continue
            
            return task_updates
            
        except Exception as e:
            print(f"Error updating tasks with file changes: {e}")
            return []
    
    