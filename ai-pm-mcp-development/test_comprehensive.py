#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Project Manager MCP Server.

Orchestrates all test suites including basic functionality, database infrastructure,
MCP integration, theme system, and performance benchmarks.
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Add the current directory and deps to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "deps"))

# Import test suites
from test_basic import main as run_basic_tests
from test_theme_system import main as run_theme_tests
from test_database_infrastructure import main as run_database_tests
from test_mcp_integration import main as run_mcp_tests


class ComprehensiveTestRunner:
    """Runs all test suites and provides comprehensive reporting."""
    
    def __init__(self):
        self.test_suites = [
            ("Basic Functionality", run_basic_tests, "Core MCP server functionality without database"),
            ("Database Infrastructure", run_database_tests, "Database components, queries, and performance"),
            ("MCP Integration", run_mcp_tests, "MCP tools with database integration"),
            ("Theme System", run_theme_tests, "Theme discovery, management, and context loading"),
        ]
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def print_header(self):
        """Print test suite header."""
        print("=" * 80)
        print("🧪 AI PROJECT MANAGER MCP SERVER - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test suites: {len(self.test_suites)}")
        print("=" * 80)
    
    async def run_test_suite(self, suite_name: str, test_func, description: str):
        """Run an individual test suite."""
        print(f"\n{'█' * 60}")
        print(f"🔧 RUNNING: {suite_name}")
        print(f"📄 {description}")
        print(f"{'█' * 60}")
        
        start_time = time.time()
        
        try:
            # Run the test suite
            result = await test_func()
            duration = time.time() - start_time
            
            success = (result == 0)
            
            self.results.append({
                'name': suite_name,
                'success': success,
                'duration': duration,
                'exit_code': result
            })
            
            status_icon = "✅" if success else "❌"
            print(f"\n{status_icon} {suite_name} completed in {duration:.2f}s")
            
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            
            self.results.append({
                'name': suite_name,
                'success': False,
                'duration': duration,
                'error': str(e)
            })
            
            print(f"\n❌ {suite_name} failed with exception: {e}")
            print(f"   Duration: {duration:.2f}s")
            
            return False
    
    async def run_all_tests(self):
        """Run all test suites."""
        self.start_time = time.time()
        self.print_header()
        
        overall_success = True
        
        for suite_name, test_func, description in self.test_suites:
            success = await self.run_test_suite(suite_name, test_func, description)
            if not success:
                overall_success = False
            
            # Brief pause between test suites
            await asyncio.sleep(1)
        
        self.end_time = time.time()
        self.print_summary()
        
        return 0 if overall_success else 1
    
    def print_summary(self):
        """Print comprehensive test summary."""
        total_duration = self.end_time - self.start_time
        passed_suites = sum(1 for result in self.results if result['success'])
        total_suites = len(self.results)
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        # Individual suite results
        for result in self.results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = result['duration']
            
            print(f"{status} {result['name']:<30} ({duration:>6.2f}s)")
            
            if not result['success'] and 'error' in result:
                print(f"    └── Error: {result['error']}")
        
        print("-" * 80)
        
        # Overall statistics
        success_rate = (passed_suites / total_suites * 100) if total_suites > 0 else 0
        
        print(f"📈 STATISTICS:")
        print(f"   Passed Suites:    {passed_suites}/{total_suites}")
        print(f"   Success Rate:     {success_rate:.1f}%")
        print(f"   Total Duration:   {total_duration:.2f}s")
        print(f"   Average per Suite: {total_duration/total_suites:.2f}s")
        
        # Performance insights
        if self.results:
            fastest = min(self.results, key=lambda x: x['duration'])
            slowest = max(self.results, key=lambda x: x['duration'])
            
            print(f"\n⚡ PERFORMANCE:")
            print(f"   Fastest Suite:    {fastest['name']} ({fastest['duration']:.2f}s)")
            print(f"   Slowest Suite:    {slowest['name']} ({slowest['duration']:.2f}s)")
        
        print("=" * 80)
        
        # Final verdict
        if passed_suites == total_suites:
            print("🎉 ALL TEST SUITES PASSED! System is ready for production.")
        else:
            failed_count = total_suites - passed_suites
            print(f"⚠️  {failed_count} TEST SUITE(S) FAILED. Review errors before production.")
        
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def generate_test_report(self):
        """Generate detailed test report file."""
        try:
            report_path = current_dir / "test_report.md"
            
            with open(report_path, 'w') as f:
                f.write("# AI Project Manager MCP Server - Test Report\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## Summary\n\n")
                passed_suites = sum(1 for result in self.results if result['success'])
                total_suites = len(self.results)
                success_rate = (passed_suites / total_suites * 100) if total_suites > 0 else 0
                total_duration = self.end_time - self.start_time
                
                f.write(f"- **Test Suites**: {total_suites}\n")
                f.write(f"- **Passed**: {passed_suites}\n")
                f.write(f"- **Failed**: {total_suites - passed_suites}\n")
                f.write(f"- **Success Rate**: {success_rate:.1f}%\n")
                f.write(f"- **Total Duration**: {total_duration:.2f}s\n\n")
                
                f.write("## Test Suite Results\n\n")
                
                for result in self.results:
                    status = "✅ PASSED" if result['success'] else "❌ FAILED"
                    f.write(f"### {result['name']}\n\n")
                    f.write(f"- **Status**: {status}\n")
                    f.write(f"- **Duration**: {result['duration']:.2f}s\n")
                    
                    if not result['success'] and 'error' in result:
                        f.write(f"- **Error**: {result['error']}\n")
                    
                    f.write("\n")
                
                f.write("## Recommendations\n\n")
                
                if passed_suites == total_suites:
                    f.write("🎉 All tests passed! The system is ready for production use.\n\n")
                    f.write("### Next Steps:\n")
                    f.write("- Deploy to production environment\n")
                    f.write("- Set up monitoring and logging\n")
                    f.write("- Schedule regular test runs\n")
                else:
                    f.write("⚠️ Some tests failed. Review and fix issues before production.\n\n")
                    f.write("### Required Actions:\n")
                    for result in self.results:
                        if not result['success']:
                            f.write(f"- Fix issues in {result['name']} test suite\n")
                    f.write("- Re-run tests after fixes\n")
                    f.write("- Consider additional debugging\n")
            
            print(f"\n📄 Detailed test report saved to: {report_path}")
            
        except Exception as e:
            print(f"⚠️  Could not generate test report: {e}")


class TestEnvironmentChecker:
    """Checks test environment prerequisites."""
    
    @staticmethod
    def check_python_version():
        """Check Python version compatibility."""
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
    
    @staticmethod
    def check_dependencies():
        """Check required dependencies."""
        try:
            import sqlite3
            print("✅ SQLite support available")
            
            # Check if we can import our modules
            from database.db_manager import DatabaseManager
            from core.mcp_api import MCPToolRegistry
            print("✅ MCP modules importable")
            
            return True
            
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            return False
    
    @staticmethod
    def check_permissions():
        """Check file system permissions."""
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = Path(temp_dir) / "test.db"
                test_file.write_text("test")
                test_file.unlink()
            
            print("✅ File system permissions OK")
            return True
            
        except Exception as e:
            print(f"❌ File system permission error: {e}")
            return False
    
    def run_checks(self):
        """Run all environment checks."""
        print("\n🔍 ENVIRONMENT CHECKS")
        print("-" * 40)
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Dependencies", self.check_dependencies),
            ("Permissions", self.check_permissions),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                if not check_func():
                    all_passed = False
            except Exception as e:
                print(f"❌ {check_name}: {e}")
                all_passed = False
        
        print("-" * 40)
        
        if all_passed:
            print("✅ All environment checks passed")
        else:
            print("❌ Some environment checks failed")
        
        return all_passed


async def main():
    """Run comprehensive test suite."""
    
    # Check environment first
    env_checker = TestEnvironmentChecker()
    if not env_checker.run_checks():
        print("\n❌ Environment checks failed. Please fix issues before running tests.")
        return 1
    
    # Run tests
    test_runner = ComprehensiveTestRunner()
    exit_code = await test_runner.run_all_tests()
    
    # Generate report
    test_runner.generate_test_report()
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error in test runner: {e}")
        sys.exit(1)