#!/usr/bin/env python3
"""
Initialization Tools

MCP tools for user interaction during initialization process.
Provides proper user communication through MCP protocol instead of stderr.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

from ..core.mcp_api import ToolDefinition
from ..core.state_analyzer import ProjectStateAnalyzer
from ..core.user_communication import UserCommunicationService

logger = logging.getLogger(__name__)


class InitializationTools:
    """MCP tools for initialization user interaction."""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.state_analyzer = ProjectStateAnalyzer()
        self.user_comm = UserCommunicationService()
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all initialization tools."""
        return [
            ToolDefinition(
                name="get_project_state_analysis",
                description="Analyze current project state and present initialization options to user",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory (defaults to current directory)",
                            "default": "."
                        },
                        "force_full_analysis": {
                            "type": "boolean",
                            "description": "Force comprehensive analysis instead of using cached state",
                            "default": False
                        }
                    }
                },
                handler=self.get_project_state_analysis
            ),
            ToolDefinition(
                name="make_initialization_choice",
                description="Process user's initialization choice and execute appropriate action",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Path to the project directory",
                            "default": "."
                        },
                        "choice": {
                            "type": "string",
                            "description": "User's choice from the state analysis options",
                            "enum": [
                                "initialize_project",
                                "session_boot_with_git_detection", 
                                "join_team",
                                "create_branch",
                                "fresh_start",
                                "get_project_status",
                                "complete_initialization",
                                "continue_existing"
                            ]
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context for the choice",
                            "properties": {
                                "force": {"type": "boolean", "default": False},
                                "context_mode": {"type": "string", "default": "theme-focused"},
                                "force_git_check": {"type": "boolean", "default": True}
                            }
                        }
                    },
                    "required": ["choice"]
                },
                handler=self.make_initialization_choice
            )
        ]
    
    async def get_project_state_analysis(self, arguments: Dict[str, Any]) -> str:
        """
        Analyze current project state and present options to user.
        
        This tool provides the initial state analysis that was previously
        sent to stderr and made inaccessible to users.
        """
        try:
            project_path = Path(arguments.get("project_path", "."))
            force_full_analysis = arguments.get("force_full_analysis", False)
            
            logger.info(f"Analyzing project state for user: {project_path} (full_analysis: {force_full_analysis})")
            
            # Perform optimized state analysis (fast path for existing projects)
            state_analysis = await self.state_analyzer.analyze_project_state(project_path, force_full_analysis)
            
            # Format for user presentation
            user_response = self.user_comm.format_state_analysis(
                state_analysis["state"],
                state_analysis
            )
            
            logger.debug(f"State analysis complete: {state_analysis['state']}")
            
            return self.user_comm.format_as_json_response(user_response)
            
        except Exception as e:
            logger.error(f"Error in get_project_state_analysis: {e}")
            error_response = self.user_comm.format_status_update(
                f"Error analyzing project state: {str(e)}", 
                level="error"
            )
            return self.user_comm.format_as_json_response(error_response)
    
    async def make_initialization_choice(self, arguments: Dict[str, Any]) -> str:
        """
        Process user's initialization choice and execute appropriate action.
        
        This tool handles user choices that were previously auto-executed
        without user consent.
        """
        try:
            project_path = Path(arguments.get("project_path", "."))
            choice = arguments.get("choice")
            context = arguments.get("context", {})
            
            logger.info(f"Processing user choice: {choice} for {project_path}")
            
            if not choice:
                error_response = self.user_comm.format_status_update(
                    "No choice provided. Please specify your preferred action.",
                    level="error"
                )
                return self.user_comm.format_as_json_response(error_response)
            
            # Execute appropriate action based on choice
            if choice == "initialize_project":
                result = await self._execute_project_initialization(project_path, context)
            elif choice == "session_boot_with_git_detection":
                result = await self._execute_session_boot(project_path, context)
            elif choice == "join_team":
                result = await self._execute_join_team(project_path, context)
            elif choice == "create_branch":
                result = await self._execute_create_branch(project_path, context)
            elif choice == "fresh_start":
                result = await self._execute_fresh_start(project_path, context)
            elif choice == "get_project_status":
                result = await self._execute_status_check(project_path, context)
            elif choice == "complete_initialization":
                result = await self._execute_complete_initialization(project_path, context)
            elif choice == "continue_existing":
                result = await self._execute_continue_existing(project_path, context)
            else:
                result = {
                    "type": "error",
                    "message": f"Unknown choice: {choice}. Please use get_project_state_analysis to see available options."
                }
            
            return self.user_comm.format_as_json_response(result)
            
        except Exception as e:
            logger.error(f"Error in make_initialization_choice: {e}")
            error_response = self.user_comm.format_status_update(
                f"Error processing initialization choice: {str(e)}", 
                level="error"
            )
            return self.user_comm.format_as_json_response(error_response)
    
    async def _execute_project_initialization(self, project_path: Path, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute project initialization."""
        try:
            from .project_tools import ProjectTools
            project_tools = ProjectTools(self.db_manager)
            
            # Auto-determine project name
            project_name = project_path.name
            readme_path = project_path / "README.md"
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8')[:1000]
                    for line in content.split('\n'):
                        if line.startswith('# '):
                            project_name = line[2:].strip()
                            break
                except:
                    pass
            
            # Execute project initialization
            arguments = {
                "project_path": str(project_path),
                "project_name": project_name,
                "force": context.get("force", False)
            }
            result = await project_tools.initialize_project(arguments)
            
            return {
                "type": "success",
                "action": "project_initialization",
                "message": f"Project '{project_name}' initialized successfully.",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing project initialization: {e}")
            return {
                "type": "error",
                "action": "project_initialization",
                "message": f"Failed to initialize project: {str(e)}"
            }
    
    async def _execute_session_boot(self, project_path: Path, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute session boot with Git detection."""
        try:
            from .session_manager import SessionManager
            session_manager = SessionManager(self.db_manager)
            
            arguments = {
                "project_path": str(project_path),
                "context_mode": context.get("context_mode", "theme-focused"),
                "force_git_check": context.get("force_git_check", True)
            }
            result = await session_manager.boot_session_with_git_detection(arguments)
            
            return {
                "type": "success",
                "action": "session_boot",
                "message": "Session boot completed successfully.",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing session boot: {e}")
            return {
                "type": "error",
                "action": "session_boot",
                "message": f"Failed to boot session: {str(e)}"
            }
    
    async def _execute_join_team(self, project_path: Path, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute join team action (switch to ai-pm-org-main)."""
        try:
            from .branch_tools import BranchTools
            branch_tools = BranchTools(self.db_manager)
            
            arguments = {
                "branch_name": "ai-pm-org-main",
                "create_if_missing": False
            }
            result = await branch_tools.switch_to_branch(arguments)
            
            return {
                "type": "success",
                "action": "join_team",
                "message": "Switched to team's AI branch successfully.",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing join team: {e}")
            return {
                "type": "error",
                "action": "join_team",
                "message": f"Failed to join team: {str(e)}"
            }
    
    async def _execute_create_branch(self, project_path: Path, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create branch action."""
        try:
            from .branch_tools import BranchTools
            branch_tools = BranchTools(self.db_manager)
            
            arguments = {
                "base_branch": "ai-pm-org-main"
            }
            result = await branch_tools.create_instance_branch(arguments)
            
            return {
                "type": "success",
                "action": "create_branch",
                "message": "Created new AI work branch successfully.",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing create branch: {e}")
            return {
                "type": "error",
                "action": "create_branch",
                "message": f"Failed to create branch: {str(e)}"
            }
    
    async def _execute_fresh_start(self, project_path: Path, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fresh start (new project initialization)."""
        context["force"] = True  # Force initialization to override existing
        return await self._execute_project_initialization(project_path, context)
    
    async def _execute_status_check(self, project_path: Path, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute status check."""
        try:
            from .project_tools import ProjectTools
            project_tools = ProjectTools(self.db_manager)
            
            arguments = {"project_path": str(project_path)}
            result = await project_tools.get_project_status(arguments)
            
            return {
                "type": "success",
                "action": "status_check",
                "message": "Project status retrieved successfully.",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error executing status check: {e}")
            return {
                "type": "error",
                "action": "status_check",
                "message": f"Failed to get project status: {str(e)}"
            }
    
    async def _execute_complete_initialization(self, project_path: Path, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete initialization for partial projects."""
        context["force"] = True  # Force to complete missing components
        return await self._execute_project_initialization(project_path, context)
    
    async def _execute_continue_existing(self, project_path: Path, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute continue with existing partial structure."""
        return await self._execute_session_boot(project_path, context)