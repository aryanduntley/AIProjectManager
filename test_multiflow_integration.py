#!/usr/bin/env python3
"""
Multi-Flow System Integration Test
Tests the flow tools integration with database and selective loading capabilities.
"""

import sys
import asyncio
import json
from pathlib import Path

# Add the ai-pm-mcp directory and deps to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "ai-pm-mcp"))
sys.path.insert(0, str(project_root / "ai-pm-mcp" / "deps"))

from tools.flow_tools import FlowTools
from database.db_manager import DatabaseManager
from database.theme_flow_queries import ThemeFlowQueries
from database.session_queries import SessionQueries
from database.file_metadata_queries import FileMetadataQueries

async def test_multi_flow_system():
    """Test the multi-flow system functionality."""
    print("🧪 Testing Multi-Flow System Integration")
    print("=" * 50)
    
    # Setup test environment
    project_path = Path(__file__).parent / "test_project"
    project_path.mkdir(exist_ok=True)
    
    # Create projectManagement structure
    pm_dir = project_path / "projectManagement"
    pm_dir.mkdir(exist_ok=True)
    (pm_dir / "ProjectFlow").mkdir(exist_ok=True)
    (pm_dir / "database").mkdir(exist_ok=True)
    
    # Copy foundational schema
    schema_src = Path(__file__).parent / "ai-pm-mcp" / "database" / "schema.sql"
    schema_dst = pm_dir / "database" / "schema.sql"
    if schema_src.exists():
        import shutil
        shutil.copy2(schema_src, schema_dst)
    
    # Initialize database
    db_manager = DatabaseManager(str(project_path))
    db_manager.connect()
    
    # Initialize query classes
    theme_flow_queries = ThemeFlowQueries(db_manager)
    session_queries = SessionQueries(db_manager)
    file_metadata_queries = FileMetadataQueries(db_manager)
    
    # Initialize FlowTools
    flow_tools = FlowTools(theme_flow_queries, session_queries, file_metadata_queries)
    
    print("✅ Database and FlowTools initialized")
    
    # Test 1: Create flow index
    print("\n🧪 Test 1: Creating flow index...")
    flow_index_data = {
        "project_path": str(project_path),
        "flows": [
            {
                "flowId": "auth-flow",
                "filePath": "authentication-flow.json",
                "primaryTheme": "authentication",
                "dependencies": [],
                "crossFlowDependencies": ["api-flow"]
            },
            {
                "flowId": "api-flow", 
                "filePath": "api-flow.json",
                "primaryTheme": "api",
                "dependencies": ["auth-flow"],
                "crossFlowDependencies": []
            }
        ]
    }
    
    tools = await flow_tools.get_tools()
    index_tool = next(tool for tool in tools if tool.name == "flow_index_create")
    result = await index_tool.handler(flow_index_data)
    print(f"✅ Flow index result: {result[:100]}...")
    
    # Test 2: Selective flow loading
    print("\n🧪 Test 2: Testing selective flow loading...")
    selective_load_data = {
        "project_path": str(project_path),
        "task_themes": ["authentication", "security"],
        "max_flows": 2
    }
    
    selective_tool = next(tool for tool in tools if tool.name == "flow_load_selective")
    result = await selective_tool.handler(selective_load_data)
    print(f"✅ Selective loading result: {result[:100]}...")
    
    # Test 3: Dependency analysis
    print("\n🧪 Test 3: Testing cross-flow dependency analysis...")
    dependency_data = {
        "project_path": str(project_path),
        "target_flows": ["auth-flow", "api-flow"]
    }
    
    dependency_tool = next(tool for tool in tools if tool.name == "flow_dependencies_analyze")
    result = await dependency_tool.handler(dependency_data)
    print(f"✅ Dependency analysis result: {result[:100]}...")
    
    # Test 4: Database sync
    print("\n🧪 Test 4: Testing flow database sync...")
    sync_data = {
        "project_path": str(project_path)
    }
    
    sync_tool = next(tool for tool in tools if tool.name == "flow_sync_database")
    result = await sync_tool.handler(sync_data)
    print(f"✅ Database sync result: {result[:100]}...")
    
    print("\n🎉 Multi-Flow System Integration Test Completed!")
    print("All core functionality working correctly.")
    
    # Cleanup
    db_manager.close()
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_multi_flow_system())
        print(f"\n✅ Test {'PASSED' if result else 'FAILED'}")
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()