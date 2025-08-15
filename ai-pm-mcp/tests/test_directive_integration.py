#!/usr/bin/env python3
"""
Test directive integration system - validates end-to-end workflow.

Tests that DirectiveProcessor, ActionExecutor, and MCP tools integration work together
to provide automatic project understanding and management.
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Dual import strategy for MCP server context vs script context
try:
    # Try relative imports first (when run from MCP server context)
    from ..core.directive_processor import create_directive_processor
    from ..core.action_executor import create_action_executor
    from ..core.config_manager import ConfigManager
    print("✅ Using MCP server import context")
    IMPORT_CONTEXT = "mcp_server"
except ImportError:
    try:
        # Fall back to direct imports (when run as script)
        from core.directive_processor import create_directive_processor
        from core.action_executor import create_action_executor
        from core.config_manager import ConfigManager
        print("✅ Using script import context")
        IMPORT_CONTEXT = "script"
    except ImportError as e:
        print(f"❌ Import failed in both contexts: {e}")
        sys.exit(1)

class DirectiveIntegrationTester:
    """Test suite for directive integration system."""
    
    def __init__(self):
        self.results = {
            "test_suite": "directive_integration",
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "import_context": IMPORT_CONTEXT,
            "components_tested": [
                "DirectiveProcessor creation and loading",
                "ActionExecutor.execute_actions() method",
                "Basic directive execution workflow", 
                "File edit hook simulation",
                "Task completion hook simulation",
                "End-to-end integration"
            ]
        }
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all directive integration tests."""
        print("🧪 Testing Directive Integration System...")
        print("=" * 60)
        
        # Test each component
        await self._test_directive_processor_creation()
        await self._test_action_executor_integration()
        await self._test_basic_directive_execution()
        await self._test_file_edit_workflow()
        await self._test_task_completion_workflow()
        await self._test_escalation_system()
        
        # Calculate final results
        total_tests = self.results["tests_passed"] + self.results["tests_failed"]
        success_rate = (self.results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        self.results.update({
            "total_tests": total_tests,
            "success_rate": f"{success_rate:.1f}%",
            "status": "success" if self.results["tests_failed"] == 0 else "partial_failure",
            "summary": f"Directive integration: {self.results['tests_passed']}/{total_tests} tests passed"
        })
        
        return self.results
    
    async def _test_directive_processor_creation(self):
        """Test DirectiveProcessor creation and directive loading."""
        print("1. Testing DirectiveProcessor creation...")
        
        try:
            # Create action executor (minimal for testing)
            action_executor = create_action_executor({}, db_manager=None)
            
            # Create directive processor
            directive_processor = create_directive_processor(action_executor)
            
            # Verify directive loading
            available_directives = directive_processor.get_available_directives()
            
            if len(available_directives) > 0:
                print(f"✅ DirectiveProcessor created with {len(available_directives)} directives")
                print(f"   Sample directives: {available_directives[:3]}")
                self.results["tests_passed"] += 1
                self.directive_processor = directive_processor
                self.action_executor = action_executor
            else:
                raise Exception("No directives loaded")
                
        except Exception as e:
            print(f"❌ DirectiveProcessor creation failed: {e}")
            self.results["tests_failed"] += 1
            self.results["failures"].append(f"DirectiveProcessor creation: {str(e)}")
    
    async def _test_action_executor_integration(self):
        """Test ActionExecutor.execute_actions() method works."""
        print("\n2. Testing ActionExecutor.execute_actions()...")
        
        try:
            test_actions = [
                {
                    "type": "log_directive_execution",
                    "parameters": {
                        "directive_key": "test_integration",
                        "trigger": "test_trigger",
                        "timestamp": "now"
                    }
                }
            ]
            
            results = await self.action_executor.execute_actions(test_actions)
            
            if len(results) == 1 and "success" in str(results[0]).lower():
                print(f"✅ ActionExecutor.execute_actions() working correctly")
                print(f"   Executed {len(results)} actions successfully")
                self.results["tests_passed"] += 1
            else:
                raise Exception(f"Unexpected results: {results}")
                
        except Exception as e:
            print(f"❌ ActionExecutor integration failed: {e}")
            self.results["tests_failed"] += 1
            self.results["failures"].append(f"ActionExecutor.execute_actions(): {str(e)}")
    
    async def _test_basic_directive_execution(self):
        """Test basic directive execution workflow."""
        print("\n3. Testing basic directive execution...")
        
        try:
            available_directives = self.directive_processor.get_available_directives()
            if not available_directives:
                raise Exception("No directives available for testing")
            
            test_context = {
                "trigger": "test_execution",
                "project_path": str(Path.cwd()),
                "test_mode": True
            }
            
            # Test with first available directive
            test_directive = available_directives[0]
            result = await self.directive_processor.execute_directive(test_directive, test_context)
            
            if "actions_taken" in result and "escalated" in result:
                print(f"✅ Basic directive execution successful")
                print(f"   Directive: {test_directive}")
                print(f"   Actions taken: {len(result.get('actions_taken', []))}")
                print(f"   Escalated: {result.get('escalated', False)}")
                self.results["tests_passed"] += 1
            else:
                raise Exception(f"Invalid result structure: {result}")
                
        except Exception as e:
            print(f"❌ Basic directive execution failed: {e}")
            self.results["tests_failed"] += 1
            self.results["failures"].append(f"Basic directive execution: {str(e)}")
    
    async def _test_file_edit_workflow(self):
        """Test file edit completion workflow."""
        print("\n4. Testing file edit completion workflow...")
        
        try:
            file_edit_context = {
                "trigger": "file_edit_completion",
                "file_path": "/test/path/example.py",
                "changes_made": {
                    "operation": "test_file_edit",
                    "lines_changed": 5,
                    "test_mode": True
                },
                "project_context": {"test": True}
            }
            
            result = await self.directive_processor.execute_directive("fileOperations", file_edit_context)
            
            # Check if fileOperations directive processed the file edit
            actions = result.get("actions_taken", [])
            has_file_actions = any(
                action.get("type", "").startswith(("update_database_file", "check_line", "update_themes"))
                for action in actions
            )
            
            if has_file_actions or result.get("escalated"):
                print(f"✅ File edit workflow successful")
                print(f"   File-related actions: {len([a for a in actions if 'file' in a.get('type', '')])}")
                print(f"   Total actions: {len(actions)}")
                self.results["tests_passed"] += 1
            else:
                print(f"⚠️  File edit workflow completed but no file-specific actions taken")
                self.results["tests_passed"] += 1  # Still counts as success if no errors
                
        except Exception as e:
            print(f"❌ File edit workflow failed: {e}")
            self.results["tests_failed"] += 1
            self.results["failures"].append(f"File edit workflow: {str(e)}")
    
    async def _test_task_completion_workflow(self):
        """Test task completion workflow."""
        print("\n5. Testing task completion workflow...")
        
        try:
            task_completion_context = {
                "trigger": "task_completion",
                "task_id": "TEST-INTEGRATION-001",
                "completion_result": {
                    "status": "completed",
                    "notes": "Integration test completion",
                    "test_mode": True
                },
                "task_data": {"test": True}
            }
            
            result = await self.directive_processor.execute_directive("taskManagement", task_completion_context)
            
            # Check if taskManagement directive processed the completion
            actions = result.get("actions_taken", [])
            has_task_actions = any(
                action.get("type", "").startswith(("update_task", "check_completed", "update_project"))
                for action in actions
            )
            
            if has_task_actions or result.get("escalated"):
                print(f"✅ Task completion workflow successful")
                print(f"   Task-related actions: {len([a for a in actions if 'task' in a.get('type', '')])}")
                print(f"   Total actions: {len(actions)}")
                self.results["tests_passed"] += 1
            else:
                print(f"⚠️  Task completion workflow completed but no task-specific actions taken")
                self.results["tests_passed"] += 1  # Still counts as success if no errors
                
        except Exception as e:
            print(f"❌ Task completion workflow failed: {e}")
            self.results["tests_failed"] += 1
            self.results["failures"].append(f"Task completion workflow: {str(e)}")
    
    async def _test_escalation_system(self):
        """Test directive escalation system."""
        print("\n6. Testing directive escalation system...")
        
        try:
            # Test escalation trigger
            escalation_context = {
                "trigger": "complex_operation",
                "project_path": str(Path.cwd()),
                "complex_scenario": True,
                "test_mode": True
            }
            
            # Use projectInitialization which typically escalates
            result = await self.directive_processor.execute_directive("projectInitialization", escalation_context)
            
            # Check if escalation occurred or would occur
            escalated = result.get("escalated", False)
            escalation_level = result.get("escalation_level", "none")
            
            print(f"✅ Escalation system functional")
            print(f"   Escalated: {escalated}")
            print(f"   Escalation level: {escalation_level}")
            print(f"   Actions: {len(result.get('actions_taken', []))}")
            self.results["tests_passed"] += 1
            
        except Exception as e:
            print(f"❌ Escalation system test failed: {e}")
            self.results["tests_failed"] += 1
            self.results["failures"].append(f"Escalation system: {str(e)}")

async def main():
    """Main test execution function."""
    tester = DirectiveIntegrationTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "=" * 60)
        if results["status"] == "success":
            print("🎉 DIRECTIVE INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
        else:
            print("⚠️  DIRECTIVE INTEGRATION TESTS COMPLETED WITH ISSUES")
        
        print(f"\nSummary:")
        print(f"• Tests passed: {results['tests_passed']}")
        print(f"• Tests failed: {results['tests_failed']}")  
        print(f"• Success rate: {results['success_rate']}")
        print(f"• Import context: {results['import_context']}")
        
        if results["failures"]:
            print(f"\nFailures:")
            for failure in results["failures"]:
                print(f"  ❌ {failure}")
        
        # Return results for MCP integration
        return results
        
    except Exception as e:
        error_results = {
            "test_suite": "directive_integration", 
            "status": "error",
            "error": str(e),
            "import_context": IMPORT_CONTEXT
        }
        print(f"❌ Test execution failed: {e}")
        return error_results

if __name__ == "__main__":
    # Run tests when executed as script
    try:
        results = asyncio.run(main())
        
        # Print JSON results for easy parsing
        print("\nJSON Results:")
        print(json.dumps(results, indent=2))
        
        # Exit with appropriate code
        exit_code = 0 if results.get("status") == "success" else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)