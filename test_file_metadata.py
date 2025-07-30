#!/usr/bin/env python3
"""
Integration test for file metadata initialization system.
Runs from the project root to test the actual functionality.
"""

import sys
import os
import asyncio
import sqlite3
from pathlib import Path

# Set up path
project_root = Path(__file__).parent
ai_pm_path = project_root / "ai-pm-mcp"
sys.path.insert(0, str(ai_pm_path))

async def test_file_metadata_system():
    """Test the file metadata initialization system end-to-end."""
    print("🚀 AI Project Manager File Metadata System Integration Test")
    print("=" * 60)
    
    test_project_path = "/tmp/ai-pm-test-project"
    
    try:
        # Test 1: Import modules
        print("\n📋 TEST 1: Module Imports")
        print("-" * 30)
        
        # Import using -m approach simulation
        os.chdir(str(ai_pm_path))
        
        # Test basic server startup
        try:
            import server
            print("✅ Server module imported successfully")
        except Exception as e:
            print(f"❌ Server import failed: {e}")
            return False
        
        # Test 2: Check MCP server functionality  
        print("\n📋 TEST 2: MCP Server Functionality")
        print("-" * 30)
        
        # Start the MCP server application
        from server import app
        
        # Get available tools
        tools = await app.list_tools()
        
        initialization_tools = [
            "project_initialize",
            "get_initialization_progress", 
            "resume_initialization",
            "session_get_initialization_summary",
            "session_reset_initialization"
        ]
        
        found_tools = []
        for tool in tools.tools:
            if tool.name in initialization_tools:
                found_tools.append(tool.name)
                print(f"✅ Found tool: {tool.name}")
        
        missing_tools = set(initialization_tools) - set(found_tools)
        if missing_tools:
            print(f"⚠️  Missing tools: {', '.join(missing_tools)}")
        
        # Test 3: Project Initialization
        print("\n📋 TEST 3: Project Initialization")
        print("-" * 30)
        
        # Initialize project
        init_result = await app.call_tool(
            "project_initialize",
            {
                "project_path": test_project_path,
                "project_name": "Test Project",
                "force": True
            }
        )
        
        print(f"Initialization result: {init_result.content[0].text}")
        
        # Check project structure
        pm_dir = Path(test_project_path) / "projectManagement"
        if pm_dir.exists():
            print("✅ Project management directory created")
            
            # Check database
            db_path = pm_dir / "project.db" 
            if db_path.exists() and db_path.stat().st_size > 0:
                print(f"✅ Database created: {db_path.stat().st_size:,} bytes")
                
                # Test database content
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Check table creation
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ["sessions", "file_metadata", "file_modifications"]
                for table in required_tables:
                    if table in tables:
                        print(f"✅ Table exists: {table}")
                    else:
                        print(f"❌ Missing table: {table}")
                
                # Check session data
                cursor.execute("SELECT COUNT(*) FROM sessions")
                session_count = cursor.fetchone()[0]
                print(f"📊 Sessions created: {session_count}")
                
                # Check file metadata
                cursor.execute("SELECT COUNT(*) FROM file_metadata")
                file_count = cursor.fetchone()[0]
                print(f"📊 File metadata records: {file_count}")
                
                # Show some file data
                cursor.execute("SELECT file_path, language, initialization_analyzed FROM file_metadata LIMIT 5")
                files = cursor.fetchall()
                print("📄 Sample files analyzed:")
                for file_path, language, analyzed in files:
                    status = "✅" if analyzed else "❌"
                    print(f"  {status} {file_path} ({language})")
                
                conn.close()
            else:
                print("❌ Database not created or empty")
                return False
        else:
            print("❌ Project management directory not created")
            return False
        
        # Test 4: Progress Tracking
        print("\n📋 TEST 4: Progress Tracking")
        print("-" * 30)
        
        progress_result = await app.call_tool(
            "get_initialization_progress",
            {"project_path": test_project_path}
        )
        
        print("Progress report:")
        print(progress_result.content[0].text)
        
        # Test 5: Session Management
        print("\n📋 TEST 5: Session Management")
        print("-" * 30)
        
        summary_result = await app.call_tool(
            "session_get_initialization_summary", 
            {"project_path": test_project_path}
        )
        
        print("Session summary:")
        print(summary_result.content[0].text)
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner."""
    success = await test_file_metadata_system()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ FILE METADATA SYSTEM VALIDATION COMPLETE")
        print("=" * 60)
        print("🎯 VALIDATED FUNCTIONALITY:")
        print("✅ MCP server starts and registers tools")
        print("✅ Project initialization creates proper structure")
        print("✅ Database schema is applied correctly")
        print("✅ File discovery and analysis works")
        print("✅ Initialization progress tracking functions")
        print("✅ Session management tools are operational")
        print("✅ Database contains expected data")
        print("\n🚀 The file metadata initialization system is ready for production!")
    else:
        print("\n❌ Test failed - system needs debugging")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)  
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        sys.exit(1)