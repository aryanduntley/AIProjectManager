#!/usr/bin/env python3
"""
AI Project Manager MCP Server

A Model Context Protocol server that provides AI-driven project management
capabilities including persistent context management, theme-based organization,
and seamless session continuity.
"""

import asyncio
import sys
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
        self.tool_registry = MCPToolRegistry(self.config_manager)
        self.state_analyzer = ProjectStateAnalyzer()
        self.user_comm = UserCommunicationService()
        self.initial_state = None
        
    async def initialize(self):
        """Initialize the server and register tools."""
        try:
            logger.debug("Starting server initialization")
            
            # Load configuration
            logger.debug("Loading configuration")
            await self.config_manager.load_config()
            logger.debug("Configuration loaded successfully")
            
            # Register all tools
            logger.debug("Registering tools")
            await self.tool_registry.register_all_tools(self.server)
            logger.debug("Tools registered successfully")
            
            # Store initial state analysis but don't auto-execute
            logger.debug("Analyzing initial project state")
            self.initial_state = await self.analyze_initial_state()
            logger.info("MCP Server ready - use get_project_state_analysis to see initialization options")
            
            logger.info("AI Project Manager MCP Server initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}", exc_info=True)
            raise
    
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
            config_file = project_mgmt_dir / "UserSettings" / "config.json"
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