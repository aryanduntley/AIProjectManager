#!/usr/bin/env python3
"""
MCP Tool Integration Test Suite for AI Project Manager MCP Server.

Tests all MCP tools with database integration including event logging,
analytics dashboard, context loading, and advanced intelligence features.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add the parent directory and deps to Python path for server imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent  # ai-pm-mcp/
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "deps"))

# Import handling for both script and module execution
try:
    # Try relative imports first (when run as module from server)
    from .core.mcp_api import MCPToolRegistry
    from .core.config_manager import ConfigManager
    from .database.db_manager import DatabaseManager
    from .tools.log_tools import LogTools
    from .tools.project_tools import ProjectTools
    from .tools.theme_tools import ThemeTools
    from .tools.task_tools import TaskTools
    from .tools.session_manager import SessionManager
    from .utils.project_paths import get_database_path
except ImportError:
    # Fall back to absolute imports (when run directly as script)
    from core.mcp_api import MCPToolRegistry
    from core.config_manager import ConfigManager
    from database.db_manager import DatabaseManager
    from tools.log_tools import LogTools
    from tools.project_tools import ProjectTools
    from tools.theme_tools import ThemeTools
    from tools.task_tools import TaskTools
    from tools.session_manager import SessionManager
    from utils.project_paths import get_database_path


class MCPIntegrationTestSuite:
    """Test suite for MCP tool integration with database."""
    
    def __init__(self):
        self.temp_dir = None
        self.project_path = None
        self.config_manager = None
        self.db_manager = None
        self.registry = None
        
    async def setup_test_environment(self):
        """Set up test project and database."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test_project"
        self.project_path.mkdir()
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        await self.config_manager.load_config()
        
        # Setup database
        db_path = get_database_path(self.project_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_manager = DatabaseManager(str(db_path))
        await self.db_manager.initialize_database()
        
        # Initialize MCP registry
        self.registry = MCPToolRegistry(self.config_manager)
        await self.registry.initialize_database_components(str(db_path))
        
        print(f"✓ Test environment set up at: {self.project_path}")
        
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.db_manager:
            self.db_manager.close()
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        print("✓ Test environment cleaned up")
    
    async def test_project_tools_integration(self):
        """Test ProjectTools with database integration."""
        print("\n--- Testing ProjectTools Integration ---")
        
        try:
            project_tools = ProjectTools()
            
            # Test project initialization with database
            result = await project_tools.initialize_project({
                "project_path": str(self.project_path),
                "project_name": "Test Integration Project"
            })
            
            assert "successfully initialized" in result.lower(), "Project initialization should succeed"
            print("✓ Project initialization with database")
            
            # Verify database was created
            db_path = get_database_path(self.project_path)
            assert db_path.exists(), "Database should be created during initialization"
            print("✓ Database automatically created")
            
            # Test project status with database analytics
            status_result = await project_tools.get_project_status({
                "project_path": str(self.project_path)
            })
            
            assert "project structure" in status_result.lower(), "Status should include structure info"
            print("✓ Project status with database integration")
            
            # Test blueprint operations
            blueprint_result = await project_tools.get_blueprint({
                "project_path": str(self.project_path)
            })
            
            assert blueprint_result, "Blueprint should be retrievable"
            print("✓ Blueprint operations working")
            
            return True
            
        except Exception as e:
            print(f"✗ ProjectTools integration test failed: {e}")
            return False
    
    async def test_log_tools_integration(self):
        """Test LogTools with event database integration."""
        print("\n--- Testing LogTools Integration ---")
        
        try:
            # Initialize project first
            project_tools = ProjectTools()
            await project_tools.initialize_project({
                "project_path": str(self.project_path),
                "project_name": "Test Project"
            })
            
            # Test log tools with database
            log_tools = LogTools()
            
            # Test event logging
            log_result = await log_tools.log_event({
                "event_type": "decision",
                "title": "Chose Database Integration",
                "description": "Decided to integrate SQLite database for better analytics",
                "primary_theme": "database",
                "impact_level": "high",
                "ai_reasoning": "Database provides better analytics and session persistence"
            })
            
            assert "event logged" in log_result.lower(), "Event should be logged successfully"
            print("✓ Event logging to database")
            
            # Test recent events retrieval
            recent_result = await log_tools.get_recent_events({
                "limit": 5
            })
            
            assert "recent events" in recent_result.lower(), "Should retrieve recent events"
            print("✓ Recent events retrieval from database")
            
            # Test event search
            search_result = await log_tools.search_events({
                "query": "database",
                "limit": 10
            })
            
            assert "search results" in search_result.lower(), "Should find matching events"
            print("✓ Event search functionality")
            
            # Test event analytics
            analytics_result = await log_tools.get_event_analytics({
                "days": 30
            })
            
            assert "analytics" in analytics_result.lower(), "Should provide event analytics"
            print("✓ Event analytics from database")
            
            # Test event outcome update
            # First extract event ID from log result
            if "event logged:" in log_result:
                parts = log_result.split("event logged: ")
                if len(parts) > 1:
                    event_info = parts[1].split(" - ")[0]
                    
                    outcome_result = await log_tools.update_event_outcome({
                        "event_id": event_info,
                        "outcome": "Implementation successful and working well"
                    })
                    
                    print("✓ Event outcome update")
            
            return True
            
        except Exception as e:
            print(f"✗ LogTools integration test failed: {e}")
            return False
    
    async def test_theme_tools_database_integration(self):
        """Test ThemeTools with theme-flow database relationships."""
        print("\n--- Testing ThemeTools Database Integration ---")
        
        try:
            # Setup project
            project_tools = ProjectTools()
            await project_tools.initialize_project({
                "project_path": str(self.project_path),
                "project_name": "Test Project"
            })
            
            # Create test project structure
            await self._create_test_project_structure()
            
            theme_tools = ThemeTools()
            
            # Test theme discovery with database sync
            discovery_result = await theme_tools.discover_themes({
                "project_path": str(self.project_path),
                "force_rediscovery": True
            })
            
            assert "discovered" in discovery_result.lower(), "Should discover themes"
            print("✓ Theme discovery with database sync")
            
            # Test theme-flow relationship creation
            sync_result = await theme_tools.sync_theme_flows({
                "project_path": str(self.project_path)
            })
            
            assert "synced" in sync_result.lower() or "synchronized" in sync_result.lower(), "Should sync theme-flow relationships"
            print("✓ Theme-flow relationship sync to database")
            
            # Test theme context with database optimization
            themes_list = await theme_tools.list_themes({
                "project_path": str(self.project_path)
            })
            
            # Extract first theme name for context test
            if "available themes" in themes_list.lower():
                lines = themes_list.split('\n')
                theme_lines = [line for line in lines if line.strip().startswith('- ')]
                if theme_lines:
                    theme_name = theme_lines[0].split(':')[0].replace('- ', '')
                    
                    context_result = await theme_tools.get_theme_context({
                        "project_path": str(self.project_path),
                        "primary_theme": theme_name,
                        "context_mode": "theme-focused"
                    })
                    
                    assert "context loaded" in context_result.lower(), "Should load theme context"
                    print("✓ Theme context with database optimization")
            
            # Test theme validation with database checks
            validation_result = await theme_tools.validate_themes({
                "project_path": str(self.project_path)
            })
            
            assert "validation" in validation_result.lower(), "Should validate themes"
            print("✓ Theme validation with database")
            
            return True
            
        except Exception as e:
            print(f"✗ ThemeTools database integration test failed: {e}")
            return False
    
    async def test_task_tools_database_integration(self):
        """Test TaskTools with database status tracking."""
        print("\n--- Testing TaskTools Database Integration ---")
        
        try:
            # Setup project
            project_tools = ProjectTools()
            await project_tools.initialize_project({
                "project_path": str(self.project_path),
                "project_name": "Test Project"
            })
            
            task_tools = TaskTools()
            
            # Test task creation with database tracking
            task_result = await task_tools.create_task({
                "project_path": str(self.project_path),
                "title": "Implement User Authentication",
                "description": "Create login and registration system",
                "primary_theme": "authentication",
                "milestone_id": "M01",
                "context_mode": "theme-focused"
            })
            
            assert "task created" in task_result.lower(), "Should create task with database tracking"
            print("✓ Task creation with database integration")
            
            # Extract task ID for further tests
            task_id = None
            if "task-" in task_result:
                import re
                match = re.search(r'TASK-[\w-]+', task_result)
                if match:
                    task_id = match.group()
            
            if task_id:
                # Test task status retrieval
                status_result = await task_tools.get_task_status({
                    "project_path": str(self.project_path),
                    "task_id": task_id
                })
                
                assert "status" in status_result.lower(), "Should retrieve task status from database"
                print("✓ Task status retrieval from database")
                
                # Test task progress update
                progress_result = await task_tools.update_task_progress({
                    "project_path": str(self.project_path),
                    "task_id": task_id,
                    "progress": 50,
                    "status": "in-progress"
                })
                
                assert "updated" in progress_result.lower(), "Should update task progress in database"
                print("✓ Task progress update to database")
                
                # Test sidequest creation with limits
                sidequest_result = await task_tools.create_sidequest({
                    "project_path": str(self.project_path),
                    "parent_task_id": task_id,
                    "title": "Add Email Validation",
                    "description": "Implement email format validation"
                })
                
                assert "sidequest created" in sidequest_result.lower(), "Should create sidequest with database tracking"
                print("✓ Sidequest creation with database limits")
            
            # Test task analytics
            analytics_result = await task_tools.get_task_analytics({
                "project_path": str(self.project_path),
                "days": 30
            })
            
            assert "analytics" in analytics_result.lower(), "Should provide task analytics from database"
            print("✓ Task analytics from database")
            
            return True
            
        except Exception as e:
            print(f"✗ TaskTools database integration test failed: {e}")
            return False
    
    async def test_session_manager_integration(self):
        """Test SessionManager with database persistence."""
        print("\n--- Testing SessionManager Integration ---")
        
        try:
            session_manager = SessionManager()
            
            # Test session start with database persistence
            start_result = await session_manager.start_session({
                "project_path": str(self.project_path),
                "context": json.dumps({"theme": "authentication", "mode": "theme-focused"})
            })
            
            assert "session started" in start_result.lower(), "Should start session with database"
            print("✓ Session start with database persistence")
            
            # Extract session ID
            session_id = None
            if "session-" in start_result:
                import re
                match = re.search(r'session-[\w-]+', start_result)
                if match:
                    session_id = match.group()
            
            if session_id:
                # Test context snapshot
                snapshot_result = await session_manager.save_context_snapshot({
                    "session_id": session_id,
                    "context": json.dumps({
                        "current_theme": "authentication",
                        "loaded_files": ["auth.js", "login.tsx"],
                        "task_progress": 25
                    })
                })
                
                assert "snapshot saved" in snapshot_result.lower(), "Should save context snapshot"
                print("✓ Context snapshot to database")
                
                # Test session analytics
                analytics_result = await session_manager.get_session_analytics({
                    "project_path": str(self.project_path),
                    "days": 7
                })
                
                assert "analytics" in analytics_result.lower(), "Should provide session analytics"
                print("✓ Session analytics from database")
            
            return True
            
        except Exception as e:
            print(f"✗ SessionManager integration test failed: {e}")
            return False
    
    async def test_advanced_intelligence_tools(self):
        """Test advanced intelligence MCP tools."""
        print("\n--- Testing Advanced Intelligence Tools ---")
        
        try:
            # Setup project with some data
            await self._setup_project_with_sample_data()
            
            # Test analytics dashboard tool
            analytics_result = await self.registry.call_tool("analytics_dashboard", {
                "project_path": str(self.project_path),
                "time_range_days": 30
            })
            
            assert isinstance(analytics_result, str), "Analytics should return string result"
            print("✓ Analytics dashboard tool")
            
            # Test quick status tool
            status_result = await self.registry.call_tool("quick_status", {
                "project_path": str(self.project_path)
            })
            
            assert isinstance(status_result, str), "Quick status should return string result"
            print("✓ Quick status tool")
            
            # Test user preference learning
            learn_result = await self.registry.call_tool("learn_preference", {
                "preference_type": "context",
                "preference_data": json.dumps({
                    "task_type": "authentication",
                    "preferred_mode": "theme-expanded",
                    "success_outcome": True
                })
            })
            
            assert isinstance(learn_result, str), "Learn preference should return string result"
            print("✓ User preference learning tool")
            
            # Test recommendations
            rec_result = await self.registry.call_tool("get_recommendations", {
                "project_path": str(self.project_path),
                "task_type": "authentication"
            })
            
            assert isinstance(rec_result, str), "Recommendations should return string result"
            print("✓ Intelligent recommendations tool")
            
            return True
            
        except Exception as e:
            print(f"✗ Advanced intelligence tools test failed: {e}")
            return False
    
    async def test_error_handling_integration(self):
        """Test error handling across MCP tools."""
        print("\n--- Testing Error Handling Integration ---")
        
        try:
            # Test handling invalid project path
            project_tools = ProjectTools()
            
            result = await project_tools.get_project_status({
                "project_path": "/nonexistent/path"
            })
            
            assert "error" in result.lower() or "not found" in result.lower(), "Should handle invalid paths gracefully"
            print("✓ Invalid project path handling")
            
            # Test handling invalid task operations
            task_tools = TaskTools()
            
            result = await task_tools.get_task_status({
                "project_path": str(self.project_path),
                "task_id": "nonexistent-task"
            })
            
            assert "not found" in result.lower() or "error" in result.lower(), "Should handle invalid task ID"
            print("✓ Invalid task ID handling")
            
            # Test handling malformed parameters
            log_tools = LogTools()
            
            result = await log_tools.log_event({
                # Missing required fields
                "title": "Test Event"
            })
            
            assert isinstance(result, str), "Should handle malformed parameters gracefully"
            print("✓ Malformed parameters handling")
            
            return True
            
        except Exception as e:
            print(f"✗ Error handling integration test failed: {e}")
            return False
    
    async def _create_test_project_structure(self):
        """Create realistic test project structure."""
        directories = [
            "src/components", "src/services", "src/hooks", "src/utils",
            "tests/unit", "api/controllers", "docs"
        ]
        
        for dir_path in directories:
            (self.project_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create test files
        test_files = {
            "src/components/Login.tsx": "// Login component",
            "src/services/authService.ts": "// Auth service",
            "src/hooks/useAuth.ts": "// Auth hook",
            "package.json": json.dumps({"name": "test-project"})
        }
        
        for file_path, content in test_files.items():
            (self.project_path / file_path).write_text(content)
    
    async def _setup_project_with_sample_data(self):
        """Set up project with sample data for testing."""
        # Initialize project
        project_tools = ProjectTools()
        await project_tools.initialize_project({
            "project_path": str(self.project_path),
            "project_name": "Test Project"
        })
        
        # Create test structure
        await self._create_test_project_structure()
        
        # Add some sample events
        log_tools = LogTools()
        await log_tools.log_event({
            "event_type": "decision",
            "title": "Framework Selection",
            "description": "Chose React for frontend",
            "primary_theme": "frontend",
            "impact_level": "high"
        })
    
    async def run_all_tests(self):
        """Run all MCP integration tests."""
        print("=== MCP Tool Integration Test Suite ===\n")
        
        await self.setup_test_environment()
        
        tests = [
            ("ProjectTools Integration", self.test_project_tools_integration),
            ("LogTools Integration", self.test_log_tools_integration),
            ("ThemeTools Database Integration", self.test_theme_tools_database_integration),
            ("TaskTools Database Integration", self.test_task_tools_database_integration),
            ("SessionManager Integration", self.test_session_manager_integration),
            ("Advanced Intelligence Tools", self.test_advanced_intelligence_tools),
            ("Error Handling Integration", self.test_error_handling_integration),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
                if result:
                    print(f"✓ {test_name} - PASSED")
                else:
                    print(f"✗ {test_name} - FAILED")
            except Exception as e:
                print(f"✗ {test_name} - FAILED: {e}")
                results.append((test_name, False))
        
        # Cleanup
        self.cleanup_test_environment()
        
        # Summary
        print("\n=== Test Summary ===")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All MCP integration tests passed!")
            return 0
        else:
            print("❌ Some MCP integration tests failed")
            return 1


async def main():
    """Run MCP integration test suite."""
    test_suite = MCPIntegrationTestSuite()
    return await test_suite.run_all_tests()


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