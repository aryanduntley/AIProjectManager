#!/usr/bin/env python3
"""
Main entry point for running the AI Project Manager MCP server as a module.
Usage: python -m ai-pm-mcp
"""

import asyncio
import sys
import logging
from .server import main

# Configure logging for module execution
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)