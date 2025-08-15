"""
Task Action Executor

Handles task management actions for directive execution.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


class TaskActionExecutor(BaseActionExecutor):
    """Executes task management actions using existing task infrastructure."""
    
    def get_supported_actions(self) -> list[str]:
        """Get list of task action types this executor supports."""
        return [
            "create_task",
            "update_task_status", 
            "create_sidequest",
            "check_completed_subtasks"
        ]
    
    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task action."""
        if action_type == "create_task":
            return await self._execute_create_task(parameters)
        elif action_type == "update_task_status":
            return await self._execute_update_task_status(parameters)
        elif action_type == "create_sidequest":
            return await self._execute_create_sidequest(parameters)
        elif action_type == "check_completed_subtasks":
            return await self._execute_check_completed_subtasks(parameters)
        else:
            return self._create_error_result(f"Unknown task action type: {action_type}")
    
    async def _execute_create_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create task action using existing TaskStatusQueries."""
        if not self.task_status_queries:
            return self._create_failed_result(
                "No task status queries available - database not properly initialized",
                "create_task",
                parameters
            )
        
        try:
            # Extract task parameters with defaults
            task_id = parameters.get("task_id", f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            title = parameters.get("title", "")
            description = parameters.get("description", "")
            milestone_id = parameters.get("milestone_id")
            implementation_plan_id = parameters.get("implementation_plan_id")
            primary_theme = parameters.get("primary_theme")
            related_themes = parameters.get("related_themes", [])
            priority = parameters.get("priority", "medium")
            assigned_to = parameters.get("assigned_to", "ai-agent")
            acceptance_criteria = parameters.get("acceptance_criteria", [])
            testing_requirements = parameters.get("testing_requirements", {})
            
            if not title:
                return self._create_error_result("Task title is required")
            
            # Create task using existing database method
            created_task_id = await self.task_status_queries.create_task(
                task_id=task_id,
                title=title,
                description=description,
                milestone_id=milestone_id,
                implementation_plan_id=implementation_plan_id,
                primary_theme=primary_theme,
                related_themes=related_themes,
                priority=priority,
                assigned_to=assigned_to,
                acceptance_criteria=acceptance_criteria,
                testing_requirements=testing_requirements
            )
            
            logger.info(f"Task created successfully: {created_task_id}")
            
            return self._create_success_result(
                f"Task '{title}' created successfully",
                task_id=created_task_id,
                title=title,
                priority=priority,
                status="pending"
            )
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return self._create_error_result(f"Task creation failed: {str(e)}")
    
    async def _execute_update_task_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update task status action using existing TaskStatusQueries."""
        if not self.task_status_queries:
            return self._create_failed_result(
                "No task status queries available - database not properly initialized",
                "update_task_status",
                parameters
            )
        
        try:
            task_id = parameters.get("task_id")
            status = parameters.get("status")
            progress_percentage = parameters.get("progress_percentage")
            estimated_effort = parameters.get("estimated_effort")
            actual_effort = parameters.get("actual_effort")
            notes = parameters.get("notes", "")
            
            if not task_id:
                return self._create_error_result("Task ID is required")
            
            if not status:
                return self._create_error_result("Status is required")
            
            # Update task status using existing database method
            success = self.task_status_queries.update_task_status(
                task_id=task_id,
                status=status,
                progress_percentage=progress_percentage,
                estimated_effort=estimated_effort,
                actual_effort=actual_effort,
                notes=notes
            )
            
            if success:
                logger.info(f"Task {task_id} status updated to {status}")
                return self._create_success_result(
                    f"Task {task_id} status updated to {status}",
                    task_id=task_id,
                    status=status,
                    progress_percentage=progress_percentage
                )
            else:
                return self._create_error_result(f"Failed to update task {task_id} status")
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return self._create_error_result(f"Task status update failed: {str(e)}")
    
    async def _execute_create_sidequest(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create sidequest action using existing TaskStatusQueries."""
        if not self.task_status_queries:
            return self._create_failed_result(
                "No task status queries available - cannot create sidequest",
                "create_sidequest", 
                parameters
            )
        
        try:
            # Extract sidequest parameters
            parent_task_id = parameters.get("parent_task_id")
            title = parameters.get("title", "")
            description = parameters.get("description", "")
            priority = parameters.get("priority", "medium")
            estimated_effort = parameters.get("estimated_effort", "1h")
            
            if not parent_task_id:
                return self._create_error_result("Parent task ID is required for sidequest")
            
            if not title:
                return self._create_error_result("Sidequest title is required")
            
            # Check sidequest limits before creating
            limits_check = self.task_status_queries.check_sidequest_limits(parent_task_id)
            if not limits_check.get("can_create", False):
                return self._create_error_result(
                    f"Cannot create sidequest: {limits_check.get('reason', 'Limit reached')}"
                )
            
            # Prepare sidequest data
            sidequest_data = {
                "parent_task_id": parent_task_id,
                "title": title,
                "description": description,
                "priority": priority,
                "estimated_effort": estimated_effort
            }
            
            # Create sidequest using existing database method
            sidequest_id = await self.task_status_queries.create_sidequest(sidequest_data)
            
            logger.info(f"Sidequest created successfully: {sidequest_id} for task {parent_task_id}")
            
            return self._create_success_result(
                f"Sidequest '{title}' created successfully",
                sidequest_id=sidequest_id,
                parent_task_id=parent_task_id,
                title=title,
                priority=priority
            )
            
        except Exception as e:
            logger.error(f"Error creating sidequest: {e}")
            return self._create_error_result(f"Sidequest creation failed: {str(e)}")
    
    async def _execute_check_completed_subtasks(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute check completed subtasks action using existing TaskStatusQueries."""
        if not self.task_status_queries:
            return self._create_failed_result(
                "No task status queries available - cannot check completed subtasks",
                "check_completed_subtasks",
                parameters
            )
        
        try:
            parent_task_id = parameters.get("parent_task_id")
            mark_completions = parameters.get("mark_completions", False)
            
            if not parent_task_id:
                return self._create_error_result("Parent task ID is required")
            
            # Get all subtasks for the parent task
            subtasks = self.task_status_queries.get_subtasks(parent_task_id, "task")
            
            completed_subtasks = []
            pending_subtasks = []
            
            for subtask in subtasks:
                if subtask.get("status") == "completed":
                    completed_subtasks.append(subtask)
                else:
                    pending_subtasks.append(subtask)
            
            # If mark_completions is True, complete subtasks that should be completed
            marked_completions = []
            if mark_completions:
                for subtask in pending_subtasks:
                    # Check if subtask should be auto-completed based on criteria
                    if self._should_auto_complete_subtask(subtask):
                        subtask_id = subtask.get("subtask_id")
                        success = self.task_status_queries.update_subtask_status(
                            subtask_id=subtask_id,
                            status="completed",
                            progress_percentage=100,
                            notes="Auto-completed during work pause check"
                        )
                        if success:
                            marked_completions.append(subtask_id)
                            completed_subtasks.append(subtask)
                            pending_subtasks.remove(subtask)
            
            logger.info(f"Checked subtasks for task {parent_task_id}: {len(completed_subtasks)} completed, {len(pending_subtasks)} pending")
            
            return self._create_success_result(
                f"Subtask check completed for task {parent_task_id}",
                parent_task_id=parent_task_id,
                total_subtasks=len(subtasks),
                completed_count=len(completed_subtasks),
                pending_count=len(pending_subtasks),
                marked_completions=marked_completions,
                ready_for_resume=len(pending_subtasks) == 0
            )
            
        except Exception as e:
            logger.error(f"Error checking completed subtasks: {e}")
            return self._create_error_result(f"Subtask check failed: {str(e)}")
    
    def _should_auto_complete_subtask(self, subtask: Dict[str, Any]) -> bool:
        """Determine if a subtask should be auto-completed during work pause check."""
        # Auto-complete if progress is 100% but status isn't completed
        if subtask.get("progress_percentage", 0) >= 100:
            return True
        
        # Auto-complete if status indicates completion but not marked as such
        status = subtask.get("status", "").lower()
        if status in ["done", "finished", "ready", "verified"]:
            return True
        
        return False