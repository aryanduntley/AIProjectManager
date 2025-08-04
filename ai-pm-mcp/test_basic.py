#!/usr/bin/env python3
"""
Basic test script for the AI Project Manager MCP Server.

Tests basic functionality without requiring a full MCP client.
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add the current directory and deps to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "deps"))

from .core.config_manager import ConfigManager
from .core.mcp_api import MCPToolRegistry
from .tools.project_tools import ProjectTools
from .utils.project_paths import get_project_management_path


async def test_config_manager():
    """Test configuration manager."""
    print("Testing ConfigManager...")
    
    config_manager = ConfigManager()
    config = await config_manager.load_config()
    
    print(f"✓ Config loaded: debug={config.debug}, max_file_lines={config.project.max_file_lines}")
    return True


async def test_project_tools():
    """Test project tools."""
    print("Testing ProjectTools...")
    
    project_tools = ProjectTools()
    tools = await project_tools.get_tools()
    
    print(f"✓ Found {len(tools)} project tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test project initialization
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        result = await project_tools.initialize_project({
            "project_path": str(temp_path),
            "project_name": "Test Project"
        })
        
        print(f"✓ Project initialization result: {result}")
        
        # Check if structure was created
        project_mgmt_dir = get_project_management_path(temp_path)
        if project_mgmt_dir.exists():
            print("✓ Project management structure created")
            
            # Test getting blueprint
            blueprint_result = await project_tools.get_blueprint({
                "project_path": str(temp_path)
            })
            print("✓ Blueprint retrieved successfully")
            
            # Test project status
            status_result = await project_tools.get_project_status({
                "project_path": str(temp_path)
            })
            print("✓ Project status retrieved successfully")
            
        else:
            print("✗ Project management structure not created")
            return False
    
    return True


async def test_tool_registry():
    """Test MCP tool registry."""
    print("Testing MCPToolRegistry...")
    
    config_manager = ConfigManager()
    await config_manager.load_config()
    
    registry = MCPToolRegistry(config_manager)
    
    # Test basic tool discovery
    await registry._discover_tools()
    
    print(f"✓ Discovered {len(registry.tools)} tools:")
    for tool_name in registry.tools.keys():
        print(f"  - {tool_name}")
    
    # Test basic tools
    if "project_init" in registry.tools:
        print("✓ Basic project_init tool found")
    
    if "get_config" in registry.tools:
        print("✓ Basic get_config tool found")
        
        # Test config tool
        result = await registry._handle_get_config({})
        print("✓ Config tool executed successfully")
    
    return True


async def main():
    """Run all tests."""
    print("=== AI Project Manager MCP Server Basic Tests ===\n")
    
    tests = [
        ("Configuration Manager", test_config_manager),
        ("Project Tools", test_project_tools),
        ("Tool Registry", test_tool_registry)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"✓ {test_name} passed\n")
        except Exception as e:
            print(f"✗ {test_name} failed: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)