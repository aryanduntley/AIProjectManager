"""
Project Action Executor

Handles project management actions for directive execution.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from .base_executor import BaseActionExecutor

logger = logging.getLogger(__name__)


class ProjectActionExecutor(BaseActionExecutor):
    """Executes project management actions using existing project tools."""
    
    def get_supported_actions(self) -> list[str]:
        """Get list of project action types this executor supports."""
        return [
            "update_blueprint",
            "create_project_blueprint", 
            "analyze_project_structure",
            "update_project_state",
            "create_implementation_plan"
        ]
    
    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a project action."""
        if action_type == "update_blueprint":
            return await self._execute_update_blueprint(parameters)
        elif action_type == "create_project_blueprint":
            return await self._execute_create_project_blueprint(parameters)
        elif action_type == "analyze_project_structure":
            return await self._execute_analyze_project_structure(parameters)
        elif action_type == "update_project_state":
            return await self._execute_update_project_state(parameters)
        elif action_type == "create_implementation_plan":
            return await self._execute_create_implementation_plan(parameters)
        else:
            return self._create_error_result(f"Unknown project action type: {action_type}")
    
    async def _execute_update_blueprint(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update blueprint action using existing ProjectTools."""
        if not self.project_tools:
            return self._create_failed_result(
                "No project tools available - cannot update blueprint",
                "update_blueprint",
                parameters
            )
        
        try:
            project_path = parameters.get("project_path")
            content = parameters.get("content")
            
            if not project_path:
                return self._create_error_result("Project path is required")
            
            if not content:
                return self._create_error_result("Blueprint content is required")
            
            # Use existing project tools method
            result = await self.project_tools.update_blueprint({
                "project_path": project_path,
                "content": content
            })
            
            # Check if update was successful
            if "Error" in result:
                logger.error(f"Blueprint update failed: {result}")
                return self._create_error_result(f"Blueprint update failed: {result}")
            
            logger.info(f"Blueprint updated successfully for project: {project_path}")
            
            return self._create_success_result(
                "Blueprint updated successfully",
                project_path=project_path,
                result=result
            )
            
        except Exception as e:
            logger.error(f"Error updating blueprint: {e}")
            return self._create_error_result(f"Blueprint update failed: {str(e)}")
    
    async def _execute_create_project_blueprint(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create project blueprint action using existing ProjectTools."""
        if not self.project_tools:
            return self._create_failed_result(
                "No project tools available - cannot create blueprint", 
                "create_project_blueprint",
                parameters
            )
        
        try:
            project_path = parameters.get("project_path")
            project_name = parameters.get("project_name")
            force = parameters.get("force", False)
            
            if not project_path:
                return self._create_error_result("Project path is required")
            
            if not project_name:
                return self._create_error_result("Project name is required")
            
            # Use existing project tools initialization method which creates blueprint
            result = await self.project_tools.initialize_project({
                "project_path": project_path,
                "project_name": project_name,
                "force": force
            })
            
            # Check if initialization was successful
            if "Error" in result:
                logger.error(f"Project blueprint creation failed: {result}")
                return self._create_error_result(f"Blueprint creation failed: {result}")
            
            logger.info(f"Project blueprint created successfully: {project_name} at {project_path}")
            
            return self._create_success_result(
                "Project blueprint created successfully",
                project_path=project_path,
                project_name=project_name,
                result=result
            )
            
        except Exception as e:
            logger.error(f"Error creating project blueprint: {e}")
            return self._create_error_result(f"Blueprint creation failed: {str(e)}")
    
    async def _execute_analyze_project_structure(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analyze project structure action using existing ProjectTools."""
        if not self.project_tools:
            return self._create_failed_result(
                "No project tools available - cannot analyze project structure",
                "analyze_project_structure", 
                parameters
            )
        
        try:
            project_path = parameters.get("project_path")
            
            if not project_path:
                return self._create_error_result("Project path is required")
            
            # Use existing project status method to analyze structure
            result = await self.project_tools.get_project_status({
                "project_path": project_path
            })
            
            # Check if analysis was successful
            if "Error" in result or "No project management structure found" in result:
                logger.error(f"Project structure analysis failed: {result}")
                return self._create_error_result(f"Structure analysis failed: {result}")
            
            # Enhanced analysis with additional project information
            from pathlib import Path
            project_dir = Path(project_path)
            
            analysis_data = {
                "project_path": project_path,
                "project_exists": project_dir.exists(),
                "is_directory": project_dir.is_dir() if project_dir.exists() else False,
                "management_structure": result,
                "file_count": len(list(project_dir.rglob("*"))) if project_dir.exists() and project_dir.is_dir() else 0,
                "directory_count": len([p for p in project_dir.rglob("*") if p.is_dir()]) if project_dir.exists() and project_dir.is_dir() else 0
            }
            
            logger.info(f"Project structure analyzed for: {project_path}")
            
            return self._create_success_result(
                "Project structure analyzed successfully",
                analysis=analysis_data
            )
            
        except Exception as e:
            logger.error(f"Error analyzing project structure: {e}")
            return self._create_error_result(f"Structure analysis failed: {str(e)}")
    
    async def _execute_update_project_state(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update project state action using existing database infrastructure."""
        if not self.session_queries:
            return self._create_failed_result(
                "No session queries available - cannot update project state",
                "update_project_state",
                parameters
            )
        
        try:
            project_path = parameters.get("project_path")
            state_data = parameters.get("state_data", {})
            context_type = parameters.get("context_type", "project_state_update")
            
            if not project_path:
                return self._create_error_result("Project path is required")
            
            if not state_data:
                return self._create_error_result("State data is required")
            
            # Save project state as context snapshot using existing session infrastructure
            session_context_id = self.session_queries.context.save_context_snapshot(
                project_path=project_path,
                context_data=state_data,
                context_type=context_type
            )
            
            # Record as work activity for tracking
            self.session_queries.work_activity.record_work_activity(
                project_path=project_path,
                activity_type="project_state_update",
                activity_data={
                    "state_keys": list(state_data.keys()),
                    "context_type": context_type,
                    "update_timestamp": datetime.now().isoformat()
                },
                session_context_id=session_context_id
            )
            
            logger.info(f"Project state updated for: {project_path}")
            
            return self._create_success_result(
                "Project state updated successfully",
                project_path=project_path,
                session_context_id=session_context_id,
                state_keys=list(state_data.keys())
            )
            
        except Exception as e:
            logger.error(f"Error updating project state: {e}")
            return self._create_error_result(f"Project state update failed: {str(e)}")
    
    async def _execute_create_implementation_plan(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create implementation plan action using existing ProjectTools."""
        if not self.project_tools:
            return self._create_failed_result(
                "No project tools available - cannot create implementation plan",
                "create_implementation_plan",
                parameters
            )
        
        try:
            project_path = parameters.get("project_path")
            milestone_id = parameters.get("milestone_id")
            title = parameters.get("title")
            version = parameters.get("version", "v1")
            is_high_priority = parameters.get("is_high_priority", False)
            
            if not project_path:
                return self._create_error_result("Project path is required")
            
            if not milestone_id:
                return self._create_error_result("Milestone ID is required")
            
            if not title:
                return self._create_error_result("Plan title is required")
            
            # Use existing project tools method
            result = await self.project_tools.create_implementation_plan({
                "project_path": project_path,
                "milestone_id": milestone_id,
                "title": title,
                "version": version,
                "is_high_priority": is_high_priority
            })
            
            # Check if creation was successful
            if "Error" in result:
                logger.error(f"Implementation plan creation failed: {result}")
                return self._create_error_result(f"Plan creation failed: {result}")
            
            logger.info(f"Implementation plan created: {title} for milestone {milestone_id}")
            
            return self._create_success_result(
                "Implementation plan created successfully",
                project_path=project_path,
                milestone_id=milestone_id,
                title=title,
                version=version,
                is_high_priority=is_high_priority,
                result=result
            )
            
        except Exception as e:
            logger.error(f"Error creating implementation plan: {e}")
            return self._create_error_result(f"Implementation plan creation failed: {str(e)}")