#!/usr/bin/env python3
"""
AI Project Manager MCP Server

A Model Context Protocol server that provides AI-driven project management
capabilities including persistent context management, theme-based organization,
and seamless session continuity.
"""

import asyncio
import sys
import os
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Add deps directory to Python path for project-specific dependencies
deps_path = Path(__file__).parent / "deps"
if deps_path.exists():
    sys.path.insert(0, str(deps_path))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .core.config_manager import ConfigManager
from .core.mcp_api import MCPToolRegistry
from .core.state_analyzer import ProjectStateAnalyzer
from .core.user_communication import UserCommunicationService
from .core.directive_processor import DirectiveProcessor, create_directive_processor
from .core.action_executor import ActionExecutor, create_action_executor


# Configure enhanced debugging logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Log startup info for debugging
logger.info(f"Starting AI Project Manager MCP Server")
logger.info(f"Python path: {sys.path}")
logger.info(f"Server file location: {__file__}")
logger.info(f"Working directory: {Path.cwd()}")


class AIProjectManagerServer:
    """Main MCP server for AI project management."""
    
    def __init__(self):
        self.server = Server("ai-project-manager")
        self.config_manager = ConfigManager()
        self.state_analyzer = ProjectStateAnalyzer()
        self.user_comm = UserCommunicationService()
        self.initial_state = None
        
        # Initialize directive processing system
        self.action_executor = None
        self.directive_processor = None
        self.tool_registry = None  # Will be created after directive processor
        
    async def initialize(self):
        """Initialize the server and register tools."""
        try:
            logger.debug("Starting server initialization")
            
            # Load configuration
            logger.debug("Loading configuration")
            await self.config_manager.load_config()
            logger.debug("Configuration loaded successfully")
            
            # Initialize directive processing system
            logger.debug("Initializing directive processing system")
            await self._initialize_directive_system()
            logger.debug("Directive processing system initialized")
            
            # Create tool registry with directive processor
            logger.debug("Creating tool registry with directive processor")
            from .core.mcp_api import MCPToolRegistry
            self.tool_registry = MCPToolRegistry(self.config_manager, self.directive_processor)
            
            # Register all tools
            logger.debug("Registering tools")
            
            # DEBUG_DATABASE: Minimal debugging for database initialization tracking
            debug_file = Path.cwd() / "debug_database.log"
            def write_database_debug(msg):
                try:
                    with open(debug_file, "a") as f:
                        f.write(f"{msg}\n")
                except Exception:
                    pass
            
            write_database_debug(f"[DEBUG_DATABASE] === SERVER: Calling register_all_tools ===")
            write_database_debug(f"[DEBUG_DATABASE] PROJECT_PATH: None (not provided)")
            
            await self.tool_registry.register_all_tools(self.server)
            
            write_database_debug(f"[DEBUG_DATABASE] === SERVER: register_all_tools completed ===")
            write_database_debug(f"[DEBUG_DATABASE] DB Manager available: {hasattr(self.tool_registry, 'db_manager') and self.tool_registry.db_manager is not None}")
            
            logger.debug("Tools registered successfully")
            
            # Update ActionExecutor with database manager now that tool registry has initialized it
            if hasattr(self.tool_registry, 'db_manager') and self.tool_registry.db_manager:
                logger.debug("Updating ActionExecutor with database manager")
                self.action_executor.db_manager = self.tool_registry.db_manager
                self.action_executor._initialize_database_queries()
                logger.debug("ActionExecutor database integration completed")
            
            # FIX: Update ActionExecutor with real MCP tool instances
            if hasattr(self.tool_registry, 'tool_instances') and self.tool_registry.tool_instances:
                logger.debug(f"Updating ActionExecutor with {len(self.tool_registry.tool_instances)} MCP tool instances")
                self.action_executor.set_mcp_tools(self.tool_registry.tool_instances)
                logger.debug("ActionExecutor MCP tools integration completed")
            
            # Execute session start hook
            await self._on_session_start()
            
            # Store initial state analysis but don't auto-execute
            logger.debug("Analyzing initial project state")
            self.initial_state = await self.analyze_initial_state()
            logger.info("MCP Server ready - try '/status' command or use get_project_state_analysis tool to see available options")
            
            logger.info("AI Project Manager MCP Server initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}", exc_info=True)
            raise
    
    async def _initialize_directive_system(self):
        """Initialize the directive processing and action execution system."""
        try:
            # Create action executor with MCP tools reference
            mcp_tools = {
                "task_tools": None,  # Will be populated after tool registry initialization
                "project_tools": None,
                "log_tools": None,
                "theme_tools": None,
                "database_tools": None,
                "session_tools": None,
                "branch_tools": None
            }
            
            self.action_executor = create_action_executor(mcp_tools, db_manager=None)  # DB manager added after tool registry initialization
            
            # Create directive processor with action executor
            self.directive_processor = create_directive_processor(self.action_executor)
            
            logger.info("Directive processing system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize directive system: {e}")
            raise
    
    async def _on_session_start(self):
        """Hook point: Session starting."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for session start hook")
            return
        
        try:
            context = {
                "trigger": "session_start",
                "server_instance": "ai-project-manager",
                "project_path": str(Path.cwd()),
                "session_context": {
                    "server_initialized": True,
                    "tools_registered": True
                },
                "project_state": self.initial_state
            }
            
            logger.info("Executing session start directive")
            result = await self.directive_processor.execute_directive("sessionManagement", context)
            logger.info(f"Session start directive completed: {result.get('actions_taken', [])}")
            
        except Exception as e:
            logger.error(f"Error in session start hook: {e}")
    
    async def _on_work_pause(self):
        """Hook point: Work pause preparation (for /aipm-pause command)."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for work pause hook")
            return
        
        try:
            context = {
                "trigger": "work_pause",
                "server_instance": "ai-project-manager",
                "pause_context": {
                    "thorough_cleanup": True,
                    "prepare_for_resume": True,
                    "check_completions": True
                },
                "current_project_state": self.initial_state
            }
            
            logger.info("Executing work pause directive")
            result = await self.directive_processor.execute_directive("sessionManagement", context)
            logger.info(f"Work pause directive completed: {result.get('actions_taken', [])}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in work pause hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    # Hook point methods that can be called from MCP tools
    async def on_file_edit_complete(self, file_path: str, changes_made: Dict[str, Any]) -> Dict[str, Any]:
        """Hook point: File editing completed - real-time state preservation."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for file edit hook")
            return {"error": "No directive processor"}
        
        try:
            context = {
                "trigger": "file_edit_completion",
                "file_path": file_path,
                "changes_made": changes_made,
                "project_context": self.initial_state,
                "timestamp": "now"
            }
            
            logger.debug(f"Executing file edit completion directive for: {file_path}")
            result = await self.directive_processor.execute_directive("fileOperations", context)
            return result
            
        except Exception as e:
            logger.error(f"Error in file edit completion hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_task_completion(self, task_id: str, completion_result: Dict[str, Any]) -> Dict[str, Any]:
        """Hook point: Task/subtask completed - real-time state preservation."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for task completion hook")
            return {"error": "No directive processor"}
        
        try:
            context = {
                "trigger": "task_completion",
                "task_id": task_id,
                "completion_result": completion_result,
                "task_data": completion_result.get("task_data", {}),
                "project_state": self.initial_state,
                "timestamp": "now"
            }
            
            logger.info(f"Executing task completion directive for task: {task_id}")
            result = await self.directive_processor.execute_directive("taskManagement", context)
            return result
            
        except Exception as e:
            logger.error(f"Error in task completion hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_branch_operation_complete(self, context: Dict[str, Any], directive_key: str) -> Dict[str, Any]:
        """Hook point: Git branch operation completed - organizational state updates."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for branch operation hook")
            return {"error": "No directive processor"}
        
        try:
            # Enhance context with server state
            enhanced_context = {
                **context,
                "project_context": self.initial_state,
                "server_state": {"ready": True},
                "timestamp": "now"
            }
            
            operation_type = context.get("operation_type", "unknown")
            logger.info(f"Executing branch operation directive for: {operation_type}")
            result = await self.directive_processor.execute_directive(directive_key, enhanced_context)
            return result
            
        except Exception as e:
            logger.error(f"Error in branch operation hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_project_operation_complete(self, context: Dict[str, Any], directive_key: str) -> Dict[str, Any]:
        """Hook point: Project management operation completed - update project understanding."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for project operation hook")
            return {"error": "No directive processor"}
        
        try:
            # Enhance context with server state
            enhanced_context = {
                **context,
                "project_context": self.initial_state,
                "server_state": {"ready": True},
                "timestamp": "now"
            }
            
            operation_type = context.get("operation_type", "unknown")
            logger.info(f"Executing {directive_key} directive for {operation_type} completion")
            
            result = await self.directive_processor.execute_directive(directive_key, enhanced_context)
            return result
            
        except Exception as e:
            logger.error(f"Error in project operation hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_database_operation_complete(self, context: Dict[str, Any], directive_key: str) -> Dict[str, Any]:
        """Hook point: Database operation completed - update project data integrity tracking."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for database operation hook")
            return {"error": "No directive processor"}
        
        try:
            # Enhance context with server state
            enhanced_context = {
                **context,
                "project_context": self.initial_state,
                "server_state": {"ready": True},
                "timestamp": "now"
            }
            
            operation_type = context.get("operation_type", "unknown")
            logger.info(f"Executing {directive_key} directive for {operation_type} completion")
            
            result = await self.directive_processor.execute_directive(directive_key, enhanced_context)
            return result
            
        except Exception as e:
            logger.error(f"Error in database operation hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_initialization_operation_complete(self, context: Dict[str, Any], directive_key: str) -> Dict[str, Any]:
        """Hook point: Initialization operation completed - update project understanding and workflow state."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for initialization operation hook")
            return {"error": "No directive processor"}
        
        try:
            # Enhance context with server state
            enhanced_context = {
                **context,
                "project_context": self.initial_state,
                "server_state": {"ready": True},
                "timestamp": "now"
            }
            
            operation_type = context.get("operation_type", "unknown")
            choice = context.get("choice", "unknown")
            logger.info(f"Executing {directive_key} directive for {operation_type} - choice: {choice}")
            
            result = await self.directive_processor.execute_directive(directive_key, enhanced_context)
            return result
            
        except Exception as e:
            logger.error(f"Error in initialization operation hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_logging_operation_complete(self, context: Dict[str, Any], directive_key: str) -> Dict[str, Any]:
        """Hook point: Logging operation completed - update project understanding and decision history."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for logging operation hook")
            return {"error": "No directive processor"}
        
        try:
            # Enhance context with server state
            enhanced_context = {
                **context,
                "project_context": self.initial_state,
                "server_state": {"ready": True},
                "timestamp": "now"
            }
            
            operation_type = context.get("operation_type", "unknown")
            event_title = context.get("title", "unknown")
            logger.info(f"Executing {directive_key} directive for {operation_type} - event: {event_title}")
            
            result = await self.directive_processor.execute_directive(directive_key, enhanced_context)
            return result
            
        except Exception as e:
            logger.error(f"Error in logging operation hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_session_operation_complete(self, context: Dict[str, Any], directive_key: str) -> Dict[str, Any]:
        """Hook point: Session operation completed - update session context and workflow state."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for session operation hook")
            return {"error": "No directive processor"}
        
        try:
            # Enhance context with server state
            enhanced_context = {
                **context,
                "project_context": self.initial_state,
                "server_state": {"ready": True},
                "timestamp": "now"
            }
            
            operation_type = context.get("operation_type", "unknown")
            session_id = context.get("session_id", "unknown")
            logger.info(f"Executing {directive_key} directive for {operation_type} - session: {session_id}")
            
            result = await self.directive_processor.execute_directive(directive_key, enhanced_context)
            return result
            
        except Exception as e:
            logger.error(f"Error in session operation hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_advanced_operation_complete(self, context: Dict[str, Any], directive_key: str) -> Dict[str, Any]:
        """Hook point: Advanced system operation completed - update system performance and optimization state."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for advanced operation hook")
            return {"error": "No directive processor"}
        
        try:
            # Enhance context with server state
            enhanced_context = {
                **context,
                "project_context": self.initial_state,
                "server_state": {"ready": True},
                "timestamp": "now"
            }
            
            operation_type = context.get("operation_type", "unknown")
            optimization_level = context.get("optimization_level", "unknown")
            logger.info(f"Executing {directive_key} directive for {operation_type} - level: {optimization_level}")
            
            result = await self.directive_processor.execute_directive(directive_key, enhanced_context)
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced operation hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_conversation_to_action_transition(self, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook point: AI moving from conversation to action - state preservation opportunity."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for conversation transition hook")
            return {"error": "No directive processor"}
        
        try:
            context = {
                "trigger": "conversation_to_action_transition",
                "conversation_context": conversation_context,
                "session_state": {"project_state": self.initial_state},
                "project_context": self.initial_state,
                "timestamp": "now"
            }
            
            logger.debug("Executing conversation to action transition directive")
            result = await self.directive_processor.execute_directive("sessionManagement", context)
            return result
            
        except Exception as e:
            logger.error(f"Error in conversation transition hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_core_operation_complete(self, context: Dict[str, Any], directive_key: str) -> Dict[str, Any]:
        """Hook point: Core module operation completed - update system understanding."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for core operation hook")
            return {"error": "No directive processor"}
        
        try:
            # Enhance context with server state
            enhanced_context = {
                **context,
                "project_context": self.initial_state,
                "server_state": {"ready": True},
                "timestamp": "now"
            }
            
            operation_type = context.get("operation_type", "unknown")
            logger.info(f"Executing {directive_key} directive for core operation: {operation_type}")
            
            result = await self.directive_processor.execute_directive(directive_key, enhanced_context)
            return result
            
        except Exception as e:
            logger.error(f"Error in core operation hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def on_workflow_completion(self, workflow_context: Dict[str, Any], directive_key: str = "workflowManagement") -> Dict[str, Any]:
        """Hook point: High-level workflow completion - triggers comprehensive project understanding updates."""
        if not self.directive_processor:
            logger.warning("Directive processor not available for workflow completion hook")
            return {"error": "No directive processor"}
        
        try:
            # Enhanced context for workflow completion directive
            enhanced_context = {
                **workflow_context,  # Include all workflow-specific context
                "session_state": {"project_state": self.initial_state},
                "project_context": self.initial_state
            }
            
            logger.info(f"Executing workflow completion directive: {workflow_context.get('workflow_type', 'unknown')} via {workflow_context.get('command', 'direct')}")
            result = await self.directive_processor.execute_directive(directive_key, enhanced_context)
            return result
            
        except Exception as e:
            logger.error(f"Error in workflow completion hook: {e}")
            return {"error": str(e), "actions_taken": []}
    
    async def analyze_initial_state(self):
        """Analyze initial project state without auto-executing actions."""
        try:
            project_path = Path.cwd()
            logger.info(f"Analyzing initial state for project at: {project_path}")
            
            # Use state analyzer for comprehensive analysis
            state_analysis = await self.state_analyzer.analyze_project_state(project_path)
            
            logger.debug(f"Initial state determined: {state_analysis['state']}")
            return state_analysis
                
        except Exception as e:
            logger.error(f"Error during initial state analysis: {e}")
            return {
                "state": "unknown",
                "project_path": str(Path.cwd()),
                "details": {"error": str(e)},
                "git_analysis": {},
                "recommended_actions": ["project_get_status", "check_logs"]
            }
    
    # REMOVED: execute_git_history_recovery - now handled by initialization tools
    # Use make_initialization_choice MCP tool with appropriate choice
    
    # REMOVED: execute_project_initialization - now handled by initialization tools
    # Use make_initialization_choice MCP tool with 'initialize_project' choice
    
    # REMOVED: execute_existing_project_boot - now handled by initialization tools
    # Use make_initialization_choice MCP tool with appropriate choice based on state
    
    async def analyze_git_project_state(self, project_path: Path) -> Dict[str, Any]:
        """Analyze Git repository state for AI project management branches using proper branch manager logic."""
        analysis = {
            "is_git_repo": False,
            "has_ai_branches": False,
            "current_branch": None,
            "current_branch_type": "unknown",
            "ai_main_exists": False,
            "ai_instance_branches": [],
            "remote_ai_branches": [],
            "is_team_member": False,
            "has_remote": False
        }
        
        try:
            # Import and use the proper branch manager
            from .core.branch_manager import GitBranchManager
            branch_manager = GitBranchManager(project_path)
            
            # Check if this is a Git repository
            result = subprocess.run([
                'git', 'rev-parse', '--git-dir'
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                return analysis
                
            analysis["is_git_repo"] = True
            
            # Get current branch and identify its type
            current_branch = branch_manager.get_current_branch()
            analysis["current_branch"] = current_branch
            
            # Identify branch type
            if current_branch == "ai-pm-org-main":
                analysis["current_branch_type"] = "ai_main"
            elif current_branch.startswith("ai-pm-org-branch-"):
                analysis["current_branch_type"] = "ai_instance"
            elif current_branch in ["main", "master"]:
                analysis["current_branch_type"] = "user_main"
            else:
                analysis["current_branch_type"] = "user_other"
            
            # Check for AI main branch existence
            analysis["ai_main_exists"] = branch_manager._branch_exists("ai-pm-org-main")
            
            # Get all AI instance branches
            instance_branches = branch_manager.list_instance_branches()
            analysis["ai_instance_branches"] = [branch.name for branch in instance_branches]
            analysis["has_ai_branches"] = analysis["ai_main_exists"] or len(analysis["ai_instance_branches"]) > 0
            
            # Detect team member scenario
            analysis["is_team_member"] = branch_manager._detect_team_member_scenario()
            
            # Check for remote repository and remote AI branches
            result = subprocess.run([
                'git', 'remote'
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                analysis["has_remote"] = True
                
                # Check for remote AI branches
                result = subprocess.run([
                    'git', 'branch', '-r'
                ], cwd=project_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    remote_branches = [line.strip() for line in result.stdout.strip().split('\n')]
                    remote_ai_branches = [b for b in remote_branches if 'ai-pm-org-' in b]
                    analysis["remote_ai_branches"] = remote_ai_branches
                    
        except Exception as e:
            logger.error(f"Error analyzing Git state: {e}")
            
        return analysis
    
    async def get_initial_state_analysis(self) -> Dict[str, Any]:
        """Get the stored initial state analysis for MCP tools."""
        if self.initial_state is None:
            self.initial_state = await self.analyze_initial_state()
        return self.initial_state
    
    async def check_auto_task_setting(self, project_mgmt_dir: Path) -> bool:
        """Check if auto task creation is enabled in user settings."""
        try:
            config_file = project_mgmt_dir / ".ai-pm-config.json"
            if config_file.exists():
                import json
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return config.get("tasks", {}).get("resumeTasksOnStart", False)
        except Exception as e:
            logger.error(f"Error reading auto task setting: {e}")
        return False
    
    # REMOVED: notify_user_git_history_found - replaced with MCP tools
    # All user communication now goes through get_project_state_analysis MCP tool
    
    # REMOVED: notify_user_no_project_structure - replaced with MCP tools
    # All user communication now goes through get_project_state_analysis MCP tool
    
    # REMOVED: check_and_notify_project_state - replaced by state_analyzer
    # All project state analysis now handled by ProjectStateAnalyzer class
    
    # REMOVED: notify_user_complete_project - replaced with MCP tools
    # All user communication now goes through get_project_state_analysis MCP tool
    
    # REMOVED: notify_user_partial_project - replaced with MCP tools
    # All user communication now goes through get_project_state_analysis MCP tool
    
    # REMOVED: notify_user_incomplete_project - replaced with MCP tools
    # All user communication now goes through get_project_state_analysis MCP tool
    
    # REMOVED: notify_user_unknown_project_state - replaced with MCP tools
    # All user communication now goes through get_project_state_analysis MCP tool
    
    async def run(self):
        """Run the MCP server with stdio transport."""
        try:
            logger.debug("Initializing server")
            await self.initialize()
            
            logger.debug("Starting stdio server")
            # Run the server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP Server ready for connections")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
                
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise


async def main():
    """Main entry point for the MCP server."""
    server = AIProjectManagerServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)