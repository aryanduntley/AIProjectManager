#!/usr/bin/env python3
"""
Simple direct test to verify MCP server tool counts and help functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).parent
ai_pm_dir = current_dir / "ai-pm-mcp"

# Add to Python path
sys.path.insert(0, str(ai_pm_dir / "deps"))
sys.path.insert(0, str(ai_pm_dir))
sys.path.insert(0, str(current_dir))

# Set working directory
os.chdir(str(current_dir))

try:
    # Import directly without package structure
    sys.path.append(str(ai_pm_dir))
    from core.config_manager import ConfigManager
    from core.mcp_api import MCPToolRegistry
    from tools.command_tools import CommandTools
    
    async def main():
        print("=== MCP Server Tool Count and Help Test ===\n")
        
        # Test tool registry
        config_manager = ConfigManager()
        await config_manager.load_config()
        
        registry = MCPToolRegistry(config_manager)
        
        # Load all tools
        print("Loading tools from registry...")
        await registry._discover_tools()
        
        print(f"✓ Total tools registered: {len(registry.tools)}")
        
        # List all tools by category
        tool_names = list(registry.tools.keys())
        tool_names.sort()
        
        print("\nAll registered tools:")
        for i, tool_name in enumerate(tool_names, 1):
            print(f"  {i:2d}. {tool_name}")
        
        # Test help functionality
        print(f"\n{'='*50}")
        print("Testing Help System...")
        
        command_tools = CommandTools()
        
        # Test quick help
        help_output = await command_tools.help_commands({"format": "quick"})
        print("\n✓ Help system working!")
        
        print("\nQuick Help Output:")
        print("-" * 30)
        print(help_output)
        
        print(f"\n{'='*50}")
        print("SUMMARY:")
        print(f"✓ Tools discovered: {len(registry.tools)}")
        print(f"✓ Help system operational")
        print(f"✓ Commands available: {len(command_tools.commands)}")
        
        return 0
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Available sys.path:")
    for path in sys.path:
        print(f"  - {path}")
    return 1
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)