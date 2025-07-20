"""
Task Status Management Database Queries
Handles real-time task/subtask status tracking, sidequest coordination, and progress management.

Follows the exact schema structure defined in mcp-server/database/schema.sql
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from .db_manager import DatabaseManager


class TaskStatusQueries:
    """
    Comprehensive task and sidequest status management with database operations.
    
    Key Features:
    - Real-time task/subtask status tracking
    - Multiple sidequest support with limit enforcement
    - Context preservation for task switching
    - Progress analytics and velocity tracking
    - Parent-child relationship management
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db = db_manager
    
    # Task Status Management
    
    def create_task(
        self,
        task_id: str,
        title: str,
        description: str = "",
        milestone_id: str = None,
        implementation_plan_id: str = None,
        primary_theme: str = None,
        related_themes: List[str] = None,
        priority: str = "medium",
        assigned_to: str = "ai-agent",
        acceptance_criteria: List[str] = None,
        testing_requirements: Dict[str, Any] = None
    ) -> bool:
        """
        Create a new task with comprehensive metadata.
        
        Args:
            task_id: Unique task identifier
            title: Task title
            description: Task description
            milestone_id: Associated milestone
            implementation_plan_id: Associated implementation plan
            primary_theme: Primary theme name
            related_themes: List of related theme names
            priority: Task priority (high, medium, low)
            assigned_to: Who is assigned to the task
            acceptance_criteria: List of acceptance criteria
            testing_requirements: Testing requirements dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO task_status (
                    task_id, title, description, status, priority, milestone_id,
                    implementation_plan_id, primary_theme, related_themes, assigned_to,
                    review_required, acceptance_criteria, testing_requirements
                ) VALUES (?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Set review_required based on complexity
            review_required = bool(acceptance_criteria or testing_requirements)
            
            params = (
                task_id, title, description, priority, milestone_id,
                implementation_plan_id, primary_theme, json.dumps(related_themes or []),
                assigned_to, review_required, json.dumps(acceptance_criteria or []),
                json.dumps(testing_requirements or {})
            )
            
            self.db.execute_update(query, params)
            
            # Initialize sidequest limits for this task
            self._initialize_sidequest_limits(task_id)
            
            return True
        except Exception as e:
            self.db.logger.error(f"Error creating task {task_id}: {e}")
            return False
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress_percentage: int = None,
        estimated_effort: str = None,
        actual_effort: str = None,
        notes: str = None
    ) -> bool:
        """
        Update task status and progress.
        
        Args:
            task_id: Task identifier
            status: New status (pending, in-progress, blocked, completed, cancelled)
            progress_percentage: Progress percentage (0-100)
            estimated_effort: Estimated effort description
            actual_effort: Actual effort description
            notes: Additional notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            update_fields = ["status = ?"]
            params = [status]
            
            if progress_percentage is not None:
                update_fields.append("progress_percentage = ?")
                params.append(progress_percentage)
            
            if estimated_effort is not None:
                update_fields.append("estimated_effort = ?")
                params.append(estimated_effort)
            
            if actual_effort is not None:
                update_fields.append("actual_effort = ?")
                params.append(actual_effort)
            
            # Set completion timestamp if task is completed
            if status == "completed":
                update_fields.append("completed_at = CURRENT_TIMESTAMP")
            
            params.append(task_id)
            
            query = f"""
                UPDATE task_status 
                SET {', '.join(update_fields)}
                WHERE task_id = ?
            """
            
            affected_rows = self.db.execute_update(query, tuple(params))
            
            # Log task completion if status is completed
            if status == "completed" and affected_rows > 0:
                self._log_task_completion(task_id)
            
            return affected_rows > 0
        except Exception as e:
            self.db.logger.error(f"Error updating task status {task_id}: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task details by ID."""
        query = "SELECT * FROM task_status WHERE task_id = ?"
        result = self.db.execute_query(query, (task_id,))
        
        if result:
            return self._task_row_to_dict(result[0])
        return None
    
    def _task_row_to_dict(self, row) -> Dict[str, Any]:
        """Convert task database row to dictionary."""
        return {
            "task_id": row["task_id"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "priority": row["priority"],
            "milestone_id": row["milestone_id"],
            "implementation_plan_id": row["implementation_plan_id"],
            "primary_theme": row["primary_theme"],
            "related_themes": json.loads(row["related_themes"]) if row["related_themes"] else [],
            "progress_percentage": row["progress_percentage"],
            "estimated_effort": row["estimated_effort"],
            "actual_effort": row["actual_effort"],
            "created_at": row["created_at"],
            "last_updated": row["last_updated"],
            "completed_at": row["completed_at"],
            "assigned_to": row["assigned_to"],
            "review_required": bool(row["review_required"]),
            "acceptance_criteria": json.loads(row["acceptance_criteria"]) if row["acceptance_criteria"] else [],
            "testing_requirements": json.loads(row["testing_requirements"]) if row["testing_requirements"] else {}
        }
    
    def get_tasks_by_status(self, status: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get tasks by status."""
        query = "SELECT * FROM task_status WHERE status = ? ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        results = []
        for row in self.db.execute_query(query, (status,)):
            results.append(self._task_row_to_dict(row))
        return results
    
    def get_tasks_by_theme(self, theme_name: str) -> List[Dict[str, Any]]:
        """Get tasks by primary theme."""
        query = """
            SELECT * FROM task_status 
            WHERE primary_theme = ? 
            ORDER BY priority DESC, created_at ASC
        """
        
        results = []
        for row in self.db.execute_query(query, (theme_name,)):
            results.append(self._task_row_to_dict(row))
        return results
    
    def get_tasks_by_milestone(self, milestone_id: str) -> List[Dict[str, Any]]:
        """Get tasks by milestone."""
        query = """
            SELECT * FROM task_status 
            WHERE milestone_id = ? 
            ORDER BY priority DESC, created_at ASC
        """
        
        results = []
        for row in self.db.execute_query(query, (milestone_id,)):
            results.append(self._task_row_to_dict(row))
        return results
    
    # Sidequest Management with Multiple Support
    
    def create_sidequest(
        self,
        sidequest_id: str,
        parent_task_id: str,
        title: str,
        description: str = "",
        scope_description: str = "",
        reason: str = "",
        urgency: str = "medium",
        impact_on_parent: str = "minimal",
        primary_theme: str = None,
        related_themes: List[str] = None,
        completion_trigger: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new sidequest with automatic limit checking.
        
        Args:
            sidequest_id: Unique sidequest identifier
            parent_task_id: Parent task ID
            title: Sidequest title
            description: Sidequest description
            scope_description: Scope description for the sidequest
            reason: Reason for creating the sidequest
            urgency: Urgency level (high, medium, low)
            impact_on_parent: Impact on parent task (minimal, moderate, significant)
            primary_theme: Primary theme name
            related_themes: List of related themes
            completion_trigger: Completion criteria
            
        Returns:
            Dictionary with creation result and limit status
        """
        try:
            # Check sidequest limits first
            limit_status = self.check_sidequest_limits(parent_task_id)
            
            if limit_status["limit_status"] == "at_limit":
                return {
                    "success": False,
                    "reason": "sidequest_limit_exceeded",
                    "limit_status": limit_status,
                    "message": f"Maximum of {limit_status['max_allowed_sidequests']} sidequests reached for task {parent_task_id}"
                }
            
            # Create the sidequest (trigger will automatically update limits)
            query = """
                INSERT INTO sidequest_status (
                    sidequest_id, parent_task_id, title, description, status,
                    scope_description, reason, urgency, impact_on_parent,
                    primary_theme, related_themes, completion_trigger
                ) VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                sidequest_id, parent_task_id, title, description, scope_description,
                reason, urgency, impact_on_parent, primary_theme,
                json.dumps(related_themes or []), json.dumps(completion_trigger or {})
            )
            
            self.db.execute_update(query, params)
            
            # Warn if approaching limit
            if limit_status["limit_status"] == "approaching_limit":
                warning = f"Approaching sidequest limit ({limit_status['active_sidequests_count'] + 1}/{limit_status['max_allowed_sidequests']})"
            else:
                warning = None
            
            return {
                "success": True,
                "sidequest_id": sidequest_id,
                "limit_status": limit_status,
                "warning": warning
            }
            
        except Exception as e:
            self.db.logger.error(f"Error creating sidequest {sidequest_id}: {e}")
            return {
                "success": False,
                "reason": "database_error",
                "error": str(e)
            }
    
    def check_sidequest_limits(self, parent_task_id: str) -> Dict[str, Any]:
        """Check current sidequest limits and return status."""
        query = """
            SELECT active_sidequests_count, max_allowed_sidequests, 
                   warning_threshold, limit_status, remaining_capacity
            FROM sidequest_limit_status 
            WHERE task_id = ?
        """
        
        result = self.db.execute_query(query, (parent_task_id,))
        if result:
            row = result[0]
            return {
                "task_id": parent_task_id,
                "active_sidequests_count": row["active_sidequests_count"],
                "max_allowed_sidequests": row["max_allowed_sidequests"],
                "warning_threshold": row["warning_threshold"],
                "limit_status": row["limit_status"],
                "remaining_capacity": row["remaining_capacity"]
            }
        else:
            # Initialize limits if they don't exist
            self._initialize_sidequest_limits(parent_task_id)
            return {
                "task_id": parent_task_id,
                "active_sidequests_count": 0,
                "max_allowed_sidequests": 3,
                "warning_threshold": 2,
                "limit_status": "normal",
                "remaining_capacity": 3
            }
    
    def _initialize_sidequest_limits(self, task_id: str):
        """Initialize sidequest limits for a task."""
        query = """
            INSERT OR IGNORE INTO task_sidequest_limits (task_id)
            VALUES (?)
        """
        self.db.execute_update(query, (task_id,))
    
    def update_sidequest_status(
        self,
        sidequest_id: str,
        status: str,
        progress_percentage: int = None,
        notes: List[str] = None
    ) -> bool:
        """
        Update sidequest status and progress.
        
        Args:
            sidequest_id: Sidequest identifier
            status: New status (pending, in-progress, completed, cancelled)
            progress_percentage: Progress percentage (0-100)
            notes: Additional notes array
            
        Returns:
            True if successful, False otherwise
        """
        try:
            update_fields = ["status = ?"]
            params = [status]
            
            if progress_percentage is not None:
                update_fields.append("progress_percentage = ?")
                params.append(progress_percentage)
            
            if notes is not None:
                update_fields.append("notes = ?")
                params.append(json.dumps(notes))
            
            # Set completion timestamp if sidequest is completed
            if status == "completed":
                update_fields.append("completed_at = CURRENT_TIMESTAMP")
            
            params.append(sidequest_id)
            
            query = f"""
                UPDATE sidequest_status 
                SET {', '.join(update_fields)}
                WHERE sidequest_id = ?
            """
            
            # The trigger will automatically update sidequest limits
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
            
        except Exception as e:
            self.db.logger.error(f"Error updating sidequest status {sidequest_id}: {e}")
            return False
    
    def get_sidequest(self, sidequest_id: str) -> Optional[Dict[str, Any]]:
        """Get sidequest details by ID."""
        query = "SELECT * FROM sidequest_status WHERE sidequest_id = ?"
        result = self.db.execute_query(query, (sidequest_id,))
        
        if result:
            return self._sidequest_row_to_dict(result[0])
        return None
    
    def _sidequest_row_to_dict(self, row) -> Dict[str, Any]:
        """Convert sidequest database row to dictionary."""
        return {
            "sidequest_id": row["sidequest_id"],
            "parent_task_id": row["parent_task_id"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "priority": row["priority"],
            "scope_description": row["scope_description"],
            "reason": row["reason"],
            "urgency": row["urgency"],
            "impact_on_parent": row["impact_on_parent"],
            "primary_theme": row["primary_theme"],
            "related_themes": json.loads(row["related_themes"]) if row["related_themes"] else [],
            "progress_percentage": row["progress_percentage"],
            "estimated_effort": row["estimated_effort"],
            "actual_effort": row["actual_effort"],
            "created_at": row["created_at"],
            "last_updated": row["last_updated"],
            "completed_at": row["completed_at"],
            "completion_trigger": json.loads(row["completion_trigger"]) if row["completion_trigger"] else {},
            "notes": json.loads(row["notes"]) if row["notes"] else []
        }
    
    def get_active_sidequests(self, parent_task_id: str) -> List[Dict[str, Any]]:
        """Get all active sidequests for a parent task."""
        query = """
            SELECT sidequest_id, title, status, impact_level,
                   ssr.subtask_id, st.title as subtask_title
            FROM sidequest_status ss
            LEFT JOIN subtask_sidequest_relationships ssr ON ss.sidequest_id = ssr.sidequest_id
            LEFT JOIN subtask_status st ON ssr.subtask_id = st.subtask_id
            WHERE ss.parent_task_id = ? AND ss.status IN ('pending', 'in-progress')
            ORDER BY ss.created_at
        """
        
        results = []
        for row in self.db.execute_query(query, (parent_task_id,)):
            results.append({
                "sidequest_id": row["sidequest_id"],
                "title": row["title"],
                "status": row["status"],
                "impact_level": row["impact_level"],
                "subtask_id": row["subtask_id"],
                "subtask_title": row["subtask_title"]
            })
        return results
    
    # Subtask Management
    
    def create_subtask(
        self,
        subtask_id: str,
        parent_id: str,
        parent_type: str,  # 'task' or 'sidequest'
        title: str,
        description: str = "",
        context_mode: str = "theme-focused",
        flow_references: List[Dict[str, Any]] = None,
        files: List[str] = None,
        dependencies: List[str] = None,
        priority: str = "medium"
    ) -> bool:
        """
        Create a new subtask for a task or sidequest.
        
        Args:
            subtask_id: Unique subtask identifier
            parent_id: Parent task or sidequest ID
            parent_type: Type of parent ('task' or 'sidequest')
            title: Subtask title
            description: Subtask description
            context_mode: Context mode for this subtask
            flow_references: List of flow references (flowId, flowFile, steps)
            files: List of file paths
            dependencies: List of dependency subtask IDs
            priority: Subtask priority
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO subtask_status (
                    subtask_id, parent_id, parent_type, title, description,
                    status, priority, context_mode, flow_references,
                    files, dependencies
                ) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?)
            """
            
            params = (
                subtask_id, parent_id, parent_type, title, description,
                priority, context_mode, json.dumps(flow_references or []),
                json.dumps(files or []), json.dumps(dependencies or [])
            )
            
            self.db.execute_update(query, params)
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error creating subtask {subtask_id}: {e}")
            return False
    
    def update_subtask_status(
        self,
        subtask_id: str,
        status: str,
        progress_percentage: int = None,
        blockers: List[str] = None,
        notes: str = None
    ) -> bool:
        """Update subtask status and progress."""
        try:
            update_fields = ["status = ?"]
            params = [status]
            
            if progress_percentage is not None:
                update_fields.append("progress_percentage = ?")
                params.append(progress_percentage)
            
            if blockers is not None:
                update_fields.append("blockers = ?")
                params.append(json.dumps(blockers))
            
            if notes is not None:
                update_fields.append("notes = ?")
                params.append(notes)
            
            # Set completion timestamp if subtask is completed
            if status == "completed":
                update_fields.append("completed_at = CURRENT_TIMESTAMP")
            
            params.append(subtask_id)
            
            query = f"""
                UPDATE subtask_status 
                SET {', '.join(update_fields)}
                WHERE subtask_id = ?
            """
            
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
            
        except Exception as e:
            self.db.logger.error(f"Error updating subtask status {subtask_id}: {e}")
            return False
    
    def get_subtasks(self, parent_id: str, parent_type: str) -> List[Dict[str, Any]]:
        """Get subtasks for a parent task or sidequest."""
        query = """
            SELECT * FROM subtask_status 
            WHERE parent_id = ? AND parent_type = ?
            ORDER BY created_at ASC
        """
        
        results = []
        for row in self.db.execute_query(query, (parent_id, parent_type)):
            results.append(self._subtask_row_to_dict(row))
        return results
    
    def _subtask_row_to_dict(self, row) -> Dict[str, Any]:
        """Convert subtask database row to dictionary."""
        return {
            "subtask_id": row["subtask_id"],
            "parent_id": row["parent_id"],
            "parent_type": row["parent_type"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "priority": row["priority"],
            "context_mode": row["context_mode"],
            "flow_references": json.loads(row["flow_references"]) if row["flow_references"] else [],
            "files": json.loads(row["files"]) if row["files"] else [],
            "dependencies": json.loads(row["dependencies"]) if row["dependencies"] else [],
            "blockers": json.loads(row["blockers"]) if row["blockers"] else [],
            "progress_percentage": row["progress_percentage"],
            "estimated_effort": row["estimated_effort"],
            "actual_effort": row["actual_effort"],
            "created_at": row["created_at"],
            "last_updated": row["last_updated"],
            "completed_at": row["completed_at"],
            "notes": row["notes"]
        }
    
    # Subtask-Sidequest Relationship Management
    
    def create_subtask_sidequest_relationship(
        self,
        subtask_id: str,
        sidequest_id: str,
        relationship_type: str = "spawned_from",
        impact_level: str = "minimal",
        notes: str = None
    ) -> bool:
        """
        Create a relationship between a subtask and sidequest.
        
        Args:
            subtask_id: Subtask ID
            sidequest_id: Sidequest ID
            relationship_type: Type of relationship (spawned_from, blocks, supports)
            impact_level: Impact level (minimal, moderate, significant)
            notes: Additional notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT OR IGNORE INTO subtask_sidequest_relationships (
                    subtask_id, sidequest_id, relationship_type, impact_level, notes
                ) VALUES (?, ?, ?, ?, ?)
            """
            
            affected_rows = self.db.execute_update(query, (
                subtask_id, sidequest_id, relationship_type, impact_level, notes
            ))
            
            return affected_rows > 0
            
        except Exception as e:
            self.db.logger.error(f"Error creating subtask-sidequest relationship: {e}")
            return False
    
    # Analytics and Metrics
    
    def _log_task_completion(self, task_id: str):
        """Log task completion metrics for analytics."""
        try:
            # Get task details
            task = self.get_task(task_id)
            if not task:
                return
            
            # Extract estimated and actual hours if available
            estimated_hours = None
            actual_hours = None
            
            if task.get("estimated_effort"):
                # Parse estimated effort (e.g., "4 hours", "2 days")
                estimated_hours = self._parse_effort_to_hours(task["estimated_effort"])
            
            if task.get("actual_effort"):
                # Parse actual effort
                actual_hours = self._parse_effort_to_hours(task["actual_effort"])
            
            # Calculate complexity score based on task attributes
            complexity_score = self._calculate_complexity_score(task)
            
            # Insert into task_metrics (session_id will be added by integration layer)
            query = """
                INSERT INTO task_metrics (
                    task_id, milestone_id, theme_name, estimated_effort_hours,
                    actual_effort_hours, complexity_score, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            
            self.db.execute_update(query, (
                task_id, task.get("milestone_id"), task.get("primary_theme"),
                estimated_hours, actual_hours, complexity_score
            ))
            
        except Exception as e:
            self.db.logger.error(f"Error logging task completion metrics: {e}")
    
    def _parse_effort_to_hours(self, effort_str: str) -> Optional[float]:
        """Parse effort string to hours."""
        if not effort_str:
            return None
        
        effort_lower = effort_str.lower()
        try:
            if "hour" in effort_lower:
                return float(effort_lower.split()[0])
            elif "day" in effort_lower:
                return float(effort_lower.split()[0]) * 8  # 8 hours per day
            elif "week" in effort_lower:
                return float(effort_lower.split()[0]) * 40  # 40 hours per week
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _calculate_complexity_score(self, task: Dict[str, Any]) -> int:
        """Calculate complexity score (1-10) based on task attributes."""
        score = 1
        
        # Add complexity based on acceptance criteria count
        if task.get("acceptance_criteria"):
            score += min(len(task["acceptance_criteria"]), 3)
        
        # Add complexity based on related themes
        if task.get("related_themes"):
            score += min(len(task["related_themes"]), 2)
        
        # Add complexity based on testing requirements
        if task.get("testing_requirements") and task["testing_requirements"]:
            score += 2
        
        # Add complexity based on priority
        if task.get("priority") == "high":
            score += 1
        
        return min(score, 10)
    
    def get_task_analytics(self, theme_name: str = None, days: int = 30) -> Dict[str, Any]:
        """Get task completion analytics."""
        base_query = """
            FROM task_metrics tm
            JOIN task_status ts ON tm.task_id = ts.task_id
            WHERE tm.completed_at >= datetime('now', '-{} days')
        """.format(days)
        
        params = []
        if theme_name:
            base_query += " AND tm.theme_name = ?"
            params.append(theme_name)
        
        # Task completion count
        count_query = f"SELECT COUNT(*) as count {base_query}"
        total_completed = self.db.execute_query(count_query, tuple(params))[0]["count"]
        
        # Average completion time
        avg_hours_query = f"""
            SELECT AVG(tm.actual_effort_hours) as avg_hours {base_query}
            AND tm.actual_effort_hours IS NOT NULL
        """
        avg_hours = self.db.execute_query(avg_hours_query, tuple(params))[0]["avg_hours"]
        
        # Average complexity
        avg_complexity_query = f"""
            SELECT AVG(tm.complexity_score) as avg_complexity {base_query}
        """
        avg_complexity = self.db.execute_query(avg_complexity_query, tuple(params))[0]["avg_complexity"]
        
        # Tasks by status
        status_query = """
            SELECT status, COUNT(*) as count 
            FROM task_status 
            WHERE created_at >= datetime('now', '-{} days')
        """.format(days)
        
        status_params = []
        if theme_name:
            status_query += " AND primary_theme = ?"
            status_params.append(theme_name)
        
        status_query += " GROUP BY status"
        
        status_counts = {row["status"]: row["count"] 
                        for row in self.db.execute_query(status_query, tuple(status_params))}
        
        return {
            "total_completed_tasks": total_completed,
            "avg_completion_hours": round(avg_hours or 0, 2),
            "avg_complexity_score": round(avg_complexity or 0, 1),
            "tasks_by_status": status_counts,
            "analysis_period_days": days,
            "theme_filter": theme_name
        }