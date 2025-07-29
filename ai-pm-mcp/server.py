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

from core.config_manager import ConfigManager
from core.mcp_api import MCPToolRegistry


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


class AIProjectManagerServer:
    """Main MCP server for AI project management."""
    
    def __init__(self):
        self.server = Server("ai-project-manager")
        self.config_manager = ConfigManager()
        self.tool_registry = MCPToolRegistry(self.config_manager)
        
    async def initialize(self):
        """Initialize the server and register tools."""
        try:
            # Load configuration
            await self.config_manager.load_config()
            
            # Register all tools
            await self.tool_registry.register_all_tools(self.server)
            
            logger.info("AI Project Manager MCP Server initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise
    
    async def run(self):
        """Run the MCP server with stdio transport."""
        try:
            await self.initialize()
            
            # Run the server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
                
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}")
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