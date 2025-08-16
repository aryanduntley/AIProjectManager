"""
Test Execution Tools for AI Project Manager MCP Server

Provides MCP tools for running tests within the server's import context,
solving the import issues that prevent external test execution.
"""

import json
import asyncio
import traceback
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..core.mcp_api import ToolDefinition
from ..core.config_manager import ConfigManager


class TestTools:
    """Tools for executing tests within the MCP server context."""
    
    def __init__(self, config_manager=None):
        """Initialize test tools."""
        self.config_manager = config_manager

    async def get_tools(self) -> List[ToolDefinition]:
        """Return list of available test tools."""
        return [
            ToolDefinition(
                name="run_database_tests",
                description="Run database infrastructure tests within the MCP server context",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self.run_database_tests
            ),
            ToolDefinition(
                name="run_basic_tests", 
                description="Run basic functionality tests within the MCP server context",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self.run_basic_tests
            ),
            ToolDefinition(
                name="run_all_tests",
                description="Run all available test suites within the MCP server context", 
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self.run_all_tests
            ),
            ToolDefinition(
                name="get_test_status",
                description="Get status of the internal testing system and available test suites",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                handler=self.get_test_status
            )
        ]

    async def run_database_tests(self, arguments: Dict[str, Any] = None) -> str:
        """
        Run database infrastructure tests within the MCP server context.
        
        This leverages the server's working import environment to execute
        database tests that fail when run externally due to import issues.
        
        Returns:
            str: JSON-formatted test results including pass/fail status and details
        """
        try:
            # Import test components - these work because we're in server context
            from tests.test_database_infrastructure import DatabaseTestSuite
            
            print("🔍 Running Database Infrastructure Tests...")
            print("=" * 50)
            
            # Create test suite and run tests
            test_suite = DatabaseTestSuite()
            
            # Run the comprehensive test suite
            exit_code = await test_suite.run_all_tests()
            
            result = {
                "test_suite": "database_infrastructure", 
                "status": "success" if exit_code == 0 else "failed",
                "exit_code": exit_code,
                "timestamp": datetime.now().isoformat(),
                "message": "Database infrastructure tests completed",
                "import_context": "mcp_server",
                "execution_method": "internal"
            }
            
            return json.dumps(result, indent=2)
            
        except ImportError as e:
            error_result = {
                "test_suite": "database_infrastructure",
                "status": "import_error", 
                "error": str(e),
                "error_type": "ImportError",
                "timestamp": datetime.now().isoformat(),
                "message": "Failed to import test components",
                "suggestion": "Check if test_database_infrastructure.py exists and is properly structured"
            }
            return json.dumps(error_result, indent=2)
            
        except Exception as e:
            error_result = {
                "test_suite": "database_infrastructure",
                "status": "execution_error",
                "error": str(e), 
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat(),
                "message": "Test execution failed"
            }
            return json.dumps(error_result, indent=2)

    async def run_basic_tests(self, arguments: Dict[str, Any] = None) -> str:
        """
        Run basic functionality tests within the MCP server context.
        
        Tests core components like ConfigManager, ProjectTools, and basic MCP functionality.
        
        Returns:
            str: JSON-formatted test results
        """
        try:
            from tests.test_basic import main as run_basic_test_main
            
            print("🔍 Running Basic Functionality Tests...")
            print("=" * 50)
            
            # Run basic tests
            exit_code = await run_basic_test_main()
            
            result = {
                "test_suite": "basic_functionality",
                "status": "success" if exit_code == 0 else "failed", 
                "exit_code": exit_code,
                "timestamp": datetime.now().isoformat(),
                "message": "Basic functionality tests completed",
                "import_context": "mcp_server",
                "execution_method": "internal"
            }
            
            return json.dumps(result, indent=2)
            
        except ImportError as e:
            error_result = {
                "test_suite": "basic_functionality",
                "status": "import_error",
                "error": str(e),
                "error_type": "ImportError", 
                "timestamp": datetime.now().isoformat(),
                "message": "Failed to import basic test components"
            }
            return json.dumps(error_result, indent=2)
            
        except Exception as e:
            error_result = {
                "test_suite": "basic_functionality", 
                "status": "execution_error",
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat(),
                "message": "Basic test execution failed"
            }
            return json.dumps(error_result, indent=2)

    async def run_all_tests(self, arguments: Dict[str, Any] = None) -> str:
        """
        Run all available test suites within the MCP server context.
        
        Executes all test categories and provides comprehensive results summary.
        Individual test results are captured and aggregated for full visibility.
        
        Returns:
            str: JSON-formatted results for all test suites
        """
        print("🚀 Running All Test Suites...")
        print("=" * 60)
        
        test_results = {}
        overall_status = "success"
        
        # Define all test suites to run
        test_suites = [
            ("basic", self.run_basic_tests),
            ("database", self.run_database_tests)
        ]
        
        for test_name, test_func in test_suites:
            try:
                print(f"\n📋 Executing {test_name} tests...")
                result_json = await test_func()
                result_data = json.loads(result_json)
                test_results[test_name] = result_data
                
                # Track overall status
                if result_data.get("status") != "success":
                    overall_status = "mixed"
                    
            except Exception as e:
                test_results[test_name] = {
                    "status": "execution_error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat()
                }
                overall_status = "mixed"
        
        # Compile summary
        total_tests = len(test_suites)
        successful_tests = sum(1 for result in test_results.values() 
                              if result.get("status") == "success")
        
        summary = {
            "test_execution": "all_suites",
            "overall_status": overall_status,
            "summary": {
                "total_suites": total_tests,
                "successful_suites": successful_tests,
                "failed_suites": total_tests - successful_tests,
                "success_rate": f"{(successful_tests/total_tests)*100:.1f}%"
            },
            "individual_results": test_results,
            "timestamp": datetime.now().isoformat(),
            "execution_context": "mcp_server_internal",
            "message": f"Executed {total_tests} test suites with {successful_tests} successful"
        }
        
        return json.dumps(summary, indent=2)

    async def get_test_status(self, arguments: Dict[str, Any] = None) -> str:
        """
        Get the status of the internal testing system and available test suites.
        
        Returns information about available tests, import context, and system readiness.
        
        Returns:
            str: JSON-formatted status information
        """
        try:
            # Check what test files are available
            test_files = [
                "tests/test_basic.py",
                "tests/test_database_infrastructure.py",
                "tests/test_theme_system.py",
                "tests/test_mcp_integration.py",
                "tests/test_comprehensive.py"
            ]
            
            available_tests = []
            for test_file in test_files:
                if Path(test_file).exists():
                    available_tests.append({
                        "file": test_file,
                        "status": "available",
                        "size_bytes": Path(test_file).stat().st_size
                    })
                else:
                    available_tests.append({
                        "file": test_file, 
                        "status": "missing"
                    })
            
            # Check import context
            import sys
            python_path_info = {
                "working_directory": str(Path.cwd()),
                "python_path_count": len(sys.path),
                "has_deps_path": any("deps" in p for p in sys.path),
                "has_ai_pm_mcp_path": any("ai-pm-mcp" in p for p in sys.path)
            }
            
            status_info = {
                "testing_system": "mcp_server_internal",
                "status": "ready",
                "available_test_tools": [
                    "run_basic_tests",
                    "run_database_tests",
                    "run_all_tests"
                ],
                "test_files": available_tests,
                "import_context": python_path_info,
                "advantages": [
                    "No import issues - tests run in server context",
                    "Full environment access - database, tools, configs",
                    "Production-identical testing environment", 
                    "Integrated with MCP protocol"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            return json.dumps(status_info, indent=2)
            
        except Exception as e:
            error_result = {
                "testing_system": "mcp_server_internal",
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(error_result, indent=2)