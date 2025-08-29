#!/usr/bin/env python3
"""
Main entry point for running the AI Project Manager MCP server as a module.
Usage: python -m ai-pm-mcp
"""

import sys
from pathlib import Path

# COMPLETE PYTHON PATH ISOLATION FOR MCP SERVER
# This ensures the MCP server runs independently without global dependency interference

def isolate_python_environment():
    """
    Completely isolate the MCP server from global Python paths that may contain
    conflicting libraries, test files, or dependencies. Keep only essential system paths.
    """
    # Store original sys.path for debugging
    original_path = sys.path.copy()
    
    # Get our dependencies path
    mcp_root = Path(__file__).parent
    deps_path = mcp_root / "deps"
    
    # Essential system paths that must be preserved
    essential_system_paths = [
        # Python standard library locations
        path for path in original_path 
        if any(pattern in path for pattern in [
            '/usr/lib/python3',      # System Python stdlib
            '/usr/local/lib/python', # Local Python installations  
            'python3.zip',           # Zipped stdlib
            'lib-dynload',           # Dynamic loading
            'site-packages'          # But only system site-packages, not user
        ]) and '/home/' not in path  # Exclude user-local paths
    ]
    
    # Build clean, isolated sys.path
    clean_path = [
        '',  # Current directory (empty string)
        str(mcp_root),  # MCP server root directory
    ]
    
    # Add bundled dependencies first (highest priority)
    if deps_path.exists():
        clean_path.append(str(deps_path))
    
    # Add essential system paths
    clean_path.extend(essential_system_paths)
    
    # Replace sys.path with clean, isolated version
    sys.path.clear()
    sys.path.extend(clean_path)
    
    print(f"[MCP ISOLATION] Removed {len(original_path)} paths, kept {len(clean_path)} essential paths", file=sys.stderr)
    print(f"[MCP ISOLATION] Bundled deps: {deps_path}", file=sys.stderr)
    
    # Debug: Show what we kept
    for i, path in enumerate(clean_path[:5]):  # Show first 5 paths
        print(f"[MCP ISOLATION] Path {i}: {path}", file=sys.stderr)

# Apply isolation before any other imports
isolate_python_environment()

import asyncio
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