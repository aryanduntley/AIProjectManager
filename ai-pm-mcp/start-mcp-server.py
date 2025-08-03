#!/usr/bin/env python3
"""
AI Project Manager MCP Server Launcher

Simple launcher script that sets up the environment and starts the MCP server.
This script handles all the path setup needed for the bundled dependencies.
"""

import os
import sys
import asyncio
from pathlib import Path

def setup_environment():
    """Set up the Python environment for the MCP server."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Add the script directory to Python path so imports work
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Add the deps directory to Python path for bundled dependencies
    deps_path = script_dir / "deps"
    if deps_path.exists() and str(deps_path) not in sys.path:
        sys.path.insert(0, str(deps_path))
    
    # Set working directory to the script directory
    os.chdir(script_dir)

def main():
    """Main entry point."""
    try:
        # Set up the environment
        setup_environment()
        
        # Import and run the server
        from server import main as server_main
        
        # Use logging for server startup messages (not user communication)
        import logging
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        logger = logging.getLogger(__name__)
        
        logger.info("🚀 Starting AI Project Manager MCP Server...")
        logger.info(f"📁 Server directory: {Path(__file__).parent.absolute()}")
        logger.info(f"🔧 Dependencies: {'bundled' if (Path(__file__).parent / 'deps').exists() else 'system'}")
        logger.info("⚡ Ready to connect with Claude or other MCP clients\n")
        
        # Run the server
        asyncio.run(server_main())
        
    except KeyboardInterrupt:
        logger.info("\n✨ AI Project Manager MCP Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        logger.error("\n🔍 Troubleshooting:")
        logger.error("1. Make sure you're running this from the ai-pm-mcp directory")
        logger.error("2. Check that all files are present (server.py, deps/, core/, etc.)")
        logger.error("3. Verify Python 3.8+ is installed")
        sys.exit(1)

if __name__ == "__main__":
    main()