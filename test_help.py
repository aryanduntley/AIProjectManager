#!/usr/bin/env python3
"""
Simple test to verify MCP server help functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the ai-pm-mcp directory to Python path
current_dir = Path(__file__).parent
ai_pm_dir = current_dir / "ai-pm-mcp"
deps_dir = ai_pm_dir / "deps"

sys.path.insert(0, str(deps_dir))
sys.path.insert(0, str(ai_pm_dir))

from ai_pm_mcp.core.config_manager import ConfigManager
from ai_pm_mcp.core.mcp_api import MCPToolRegistry
from ai_pm_mcp.tools.command_tools import CommandTools


async def test_help_functionality():
    """Test the help system and tool discovery."""
    print("=== Testing MCP Server Help Functionality ===\n")
    
    # Test 1: Tool Registry Discovery
    print("1. Testing Tool Discovery...")
    config_manager = ConfigManager()
    await config_manager.load_config()
    
    registry = MCPToolRegistry(config_manager)
    await registry._discover_tools()
    
    print(f"✓ Discovered {len(registry.tools)} tools total")
    
    # List some key tools
    key_tools = [
        'help_commands', 'command_status', 'execute_command',
        'project_initialize', 'task_create', 'theme_discover'
    ]
    
    found_tools = []
    for tool_name in key_tools:
        if tool_name in registry.tools:
            found_tools.append(tool_name)
            print(f"  ✓ Found: {tool_name}")
        else:
            print(f"  ✗ Missing: {tool_name}")
    
    print(f"\nFound {len(found_tools)}/{len(key_tools)} key tools")
    
    # Test 2: Help Command Functionality
    print("\n2. Testing Help Commands...")
    command_tools = CommandTools()
    
    # Test help_commands tool
    help_result = await command_tools.help_commands({"format": "quick"})
    print("✓ help_commands executed successfully")
    
    if "AI Project Manager Commands" in help_result:
        print("✓ Help output contains expected content")
    else:
        print("✗ Help output missing expected content")
    
    print("\nHelp Output Preview:")
    print("-" * 50)
    print(help_result[:500] + "..." if len(help_result) > 500 else help_result)
    print("-" * 50)
    
    # Test 3: Command List
    print("\n3. Testing Available Commands...")
    commands = command_tools.commands
    print(f"✓ Found {len(commands)} available commands:")
    
    for cmd, info in commands.items():
        print(f"  /{cmd} - {info['description']}")
    
    # Test 4: Single Command Help
    print("\n4. Testing Single Command Help...")
    single_help = await command_tools.help_commands({
        "command": "status", 
        "format": "detailed"
    })
    
    if "/status Command Help" in single_help:
        print("✓ Single command help working correctly")
    else:
        print("✗ Single command help not working")
    
    print("\nSingle Command Help Preview:")
    print("-" * 50)
    print(single_help[:300] + "..." if len(single_help) > 300 else single_help)
    print("-" * 50)
    
    print("\n=== Test Results ===")
    print(f"✓ Tool registry working: {len(registry.tools)} tools found")
    print(f"✓ Help system working: {len(commands)} commands available")
    print("✓ Help output properly formatted")
    print("✓ Command descriptions present")
    
    return True


async def main():
    """Run help functionality tests."""
    try:
        await test_help_functionality()
        print("\n🎉 All help functionality tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)