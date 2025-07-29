#!/usr/bin/env python3
"""
Main entry point for running the AI Project Manager MCP server as a module.
Usage: python -m ai-pm-mcp
"""

import asyncio
import sys
from server import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)