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
from pathlib import Path
from typing import Dict, Any

# Add deps directory to Python path for project-specific dependencies
deps_path = Path(__file__).parent / "deps"
if deps_path.exists():
    sys.path.insert(0, str(deps_path))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .core.config_manager import ConfigManager
from .core.mcp_api import MCPToolRegistry


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
            
            # Perform automatic session boot sequence
            logger.debug("Starting automatic session boot sequence")
            await self.perform_session_boot()
            
            logger.info("AI Project Manager MCP Server initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}", exc_info=True)
            raise
    
    async def perform_session_boot(self):
        """Perform automatic session boot sequence to detect and notify user of project state."""
        try:
            project_path = Path.cwd()
            logger.info(f"Performing session boot for project at: {project_path}")
            
            # Check for projectManagement structure
            project_mgmt_dir = project_path / "projectManagement"
            
            if not project_mgmt_dir.exists():
                # No project structure found - notify user
                self.notify_user_no_project_structure(project_path)
            else:
                # Project structure exists - check completeness
                await self.check_and_notify_project_state(project_path, project_mgmt_dir)
                
        except Exception as e:
            logger.error(f"Error during session boot: {e}")
            # Continue anyway - don't block server startup
    
    def notify_user_no_project_structure(self, project_path: Path):
        """Notify user that no project management structure was found."""
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
⚠️  No project management structure found.

🎯 **Next Steps Available:**
1. Initialize new project: Use 'project_initialize' tool
2. Review project status: Use 'project_get_status' tool  
3. Check for existing code: Use 'check_user_code_changes' tool

ℹ️  The AI Project Manager is ready to help you set up project management for this directory.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info("User notified: No project management structure found")
    
    async def check_and_notify_project_state(self, project_path: Path, project_mgmt_dir: Path):
        """Check existing project state and notify user."""
        try:
            # Check component completeness
            components = {
                "blueprint": project_mgmt_dir / "ProjectBlueprint" / "blueprint.md",
                "metadata": project_mgmt_dir / "ProjectBlueprint" / "metadata.json", 
                "flow_index": project_mgmt_dir / "ProjectFlow" / "flow-index.json",
                "themes": project_mgmt_dir / "Themes" / "themes.json",
                "completion_path": project_mgmt_dir / "Tasks" / "completion-path.json",
                "database": project_mgmt_dir / "project.db"
            }
            
            existing = {}
            missing = {}
            
            for name, path in components.items():
                if path.exists() and path.stat().st_size > 0:
                    existing[name] = str(path)
                else:
                    missing[name] = str(path)
            
            # Count tasks
            active_tasks = list((project_mgmt_dir / "Tasks" / "active").glob("*.json")) if (project_mgmt_dir / "Tasks" / "active").exists() else []
            sidequests = list((project_mgmt_dir / "Tasks" / "sidequests").glob("*.json")) if (project_mgmt_dir / "Tasks" / "sidequests").exists() else []
            
            # Determine project state
            if len(missing) == 0:
                self.notify_user_complete_project(project_path, existing, len(active_tasks), len(sidequests))
            elif len(existing) > len(missing):
                self.notify_user_partial_project(project_path, existing, missing, len(active_tasks), len(sidequests))
            else:
                self.notify_user_incomplete_project(project_path, existing, missing)
                
        except Exception as e:
            logger.error(f"Error checking project state: {e}")
            self.notify_user_unknown_project_state(project_path)
    
    def notify_user_complete_project(self, project_path: Path, existing: dict, active_tasks: int, sidequests: int):
        """Notify user that project structure is complete."""
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
✅ Complete project management structure found.

📊 **Project Status:**
• Blueprint: ✅ Available
• Themes: ✅ Available  
• Flows: ✅ Available
• Database: ✅ Available
• Active Tasks: {active_tasks}
• Sidequests: {sidequests}

🎯 **Ready to Continue:**
• Use 'project_get_status' for detailed information
• Use 'session_start' to begin/resume work
• Use 'task_get_active' to see current tasks

ℹ️  Project is ready for continued development.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info("User notified: Complete project structure found")
    
    def notify_user_partial_project(self, project_path: Path, existing: dict, missing: dict, active_tasks: int, sidequests: int):
        """Notify user that project structure is partially complete."""
        existing_list = "• " + "\n• ".join([f"{name}: ✅" for name in existing.keys()])
        missing_list = "• " + "\n• ".join([f"{name}: ❌" for name in missing.keys()])
        
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
⚠️  Partial project management structure found.

📊 **Current Status:**
{existing_list}
{missing_list}
• Active Tasks: {active_tasks}
• Sidequests: {sidequests}

🎯 **Next Steps Available:**
1. Complete initialization: Use 'project_initialize' with force=true
2. Review current state: Use 'project_get_status' tool
3. Restore missing components: Initialize individual components
4. Continue with existing: Use 'session_start' tool

ℹ️  Project can be completed or continued with partial state.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info("User notified: Partial project structure found")
    
    def notify_user_incomplete_project(self, project_path: Path, existing: dict, missing: dict):
        """Notify user that project structure is mostly incomplete."""
        existing_list = "• " + "\n• ".join([f"{name}: ✅" for name in existing.keys()]) if existing else "• None"
        
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
⚠️  Incomplete project management structure found.

📊 **Found Components:**
{existing_list}

🎯 **Recommended Next Steps:**
1. **Initialize Project**: Use 'project_initialize' tool to set up complete structure
2. **Check Status**: Use 'project_get_status' for detailed analysis
3. **Review Existing**: Check what can be preserved before reinitializing

ℹ️  Project needs initialization to enable full AI project management.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info("User notified: Incomplete project structure found")
    
    def notify_user_unknown_project_state(self, project_path: Path):
        """Notify user that project state could not be determined."""
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
❓ Could not determine project management state.

🎯 **Available Actions:**
• Use 'project_get_status' to analyze current state
• Use 'project_initialize' to set up project management
• Check server logs for detailed error information

ℹ️  Manual project analysis recommended.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info("User notified: Unknown project state")
    
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