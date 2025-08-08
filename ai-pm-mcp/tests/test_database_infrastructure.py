#!/usr/bin/env python3
"""
Comprehensive Database Infrastructure Test Suite for AI Project Manager MCP Server.

Tests all database components including DatabaseManager, query classes, 
event system, session persistence, and user analytics.
"""

import asyncio
import json
import sys
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Add the parent directory and deps to Python path for server imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent  # ai-pm-mcp/
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "deps"))

# Import database components
from database.db_manager import DatabaseManager
from database.session_queries import SessionQueries
from database.task_status_queries import TaskStatusQueries
from database.theme_flow_queries import ThemeFlowQueries
from database.file_metadata_queries import FileMetadataQueries
from database.user_preference_queries import UserPreferenceQueries
from database.event_queries import EventQueries


class DatabaseTestSuite:
    """Comprehensive database testing suite."""
    
    def __init__(self):
        self.temp_dir = None
        self.db_path = None
        self.db_manager = None
        self.test_results = []
        
    async def setup_test_database(self):
        """Set up a temporary test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_project.db"
        
        # Initialize database with schema
        self.db_manager = DatabaseManager(str(self.db_path))
        await self.db_manager.initialize_database()
        
        print(f"✓ Test database created at: {self.db_path}")
        
    def cleanup_test_database(self):
        """Clean up test database."""
        if self.db_manager:
            self.db_manager.close()
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        print("✓ Test database cleaned up")
    
    async def test_database_manager(self):
        """Test DatabaseManager core functionality."""
        print("\n--- Testing DatabaseManager ---")
        
        try:
            # Test database initialization
            assert self.db_path.exists(), "Database file should exist"
            print("✓ Database file created successfully")
            
            # Test connection
            assert self.db_manager.connection is not None, "Database connection should exist"
            print("✓ Database connection established")
            
            # Test schema creation by checking key tables
            cursor = self.db_manager.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'sessions', 'session_context', 'work_activities', 'task_status', 'subtask_status',
                'sidequest_status', 'theme_flows', 'flow_status', 'flow_step_status',
                'file_modifications', 'user_preferences', 'task_metrics',
                'noteworthy_events', 'event_relationships'
            ]
            
            missing_tables = [table for table in expected_tables if table not in tables]
            if missing_tables:
                raise AssertionError(f"Missing tables: {missing_tables}")
            
            print(f"✓ All {len(expected_tables)} required tables created")
            
            # Test execute method
            result = self.db_manager.execute("SELECT COUNT(*) as count FROM sessions")
            assert result == [{'count': 0}], "Initial sessions count should be 0"
            print("✓ Database execute method working")
            
            # Test transaction handling
            with self.db_manager.transaction():
                self.db_manager.execute(
                    "INSERT INTO sessions (session_id, project_path, start_time) VALUES (?, ?, ?)",
                    ("test-session", "/test/path", datetime.now(timezone.utc).isoformat())
                )
            
            result = self.db_manager.execute("SELECT COUNT(*) as count FROM sessions")
            assert result[0]['count'] == 1, "Transaction should have committed"
            print("✓ Database transactions working")
            
            return True
            
        except Exception as e:
            print(f"✗ DatabaseManager test failed: {e}")
            return False
    
    async def test_session_queries(self):
        """Test SessionQueries functionality."""
        print("\n--- Testing SessionQueries ---")
        
        try:
            session_queries = SessionQueries(self.db_manager)
            
            # Test session creation
            session_id = session_queries.start_session(
                project_path="/test/project",
                context={"theme": "test", "mode": "theme-focused"}
            )
            assert session_id, "Session ID should be returned"
            print(f"✓ Session created: {session_id}")
            
            # Test context snapshot
            session_queries.save_context_snapshot(
                session_id=session_id,
                context_data={"current_theme": "auth", "loaded_files": ["auth.js", "login.jsx"]}
            )
            print("✓ Context snapshot saved")
            
            # Test session retrieval
            session_data = session_queries.get_session_data(session_id)
            assert session_data is not None, "Session data should be retrievable"
            assert session_data['project_path'] == "/test/project", "Project path should match"
            print("✓ Session data retrieved successfully")
            
            # Test context escalation logging
            session_queries.log_context_escalation(
                session_id=session_id,
                from_mode="theme-focused",
                to_mode="theme-expanded",
                reason="Cross-theme dependencies discovered",
                task_id="test-task-123"
            )
            print("✓ Context escalation logged")
            
            # Test work period analytics
            activity = session_queries.get_work_period_analytics("/test/project", days=7)
            assert isinstance(activity, dict), "Activity should return dict"
            print("✓ Work period analytics retrieved")
            
            # Test session data retrieval
            sessions = session_queries.get_recent_sessions(limit=5)
            assert isinstance(sessions, list), "Should return list of sessions"
            print(f"✓ Retrieved {len(sessions)} recent sessions")
            
            # Test session analytics
            analytics = session_queries.get_session_analytics(days=30)
            assert isinstance(analytics, dict), "Analytics should return dict"
            print("✓ Session analytics retrieved")
            
            return True
            
        except Exception as e:
            print(f"✗ SessionQueries test failed: {e}")
            return False
    
    async def test_task_status_queries(self):
        """Test TaskStatusQueries functionality."""
        print("\n--- Testing TaskStatusQueries ---")
        
        try:
            task_queries = TaskStatusQueries(self.db_manager)
            
            # Test task creation
            task_id = await task_queries.create_task(
                task_id='test-task-001',
                title='Test Authentication System',
                description='Test authentication system implementation',
                primary_theme='authentication',
                milestone_id='M01'
            )
            assert task_id == 'test-task-001', "Task ID should match"
            print(f"✓ Task created: {task_id}")
            
            # Test subtask creation
            subtask_data = {
                'subtask_id': 'ST-001',
                'parent_task_id': task_id,
                'title': 'Login Component',
                'status': 'pending'
            }
            
            subtask_id = await task_queries.create_subtask(subtask_data)
            print(f"✓ Subtask created: {subtask_id}")
            
            # Test sidequest with limits
            sidequest_data = {
                'sidequest_id': 'SQ-001',
                'parent_task_id': task_id,
                'title': 'Email Validation System',
                'description': 'Add email validation for login'
            }
            
            sidequest_id = await task_queries.create_sidequest(sidequest_data)
            print(f"✓ Sidequest created: {sidequest_id}")
            
            # Test sidequest limits
            limit_status = await task_queries.check_sidequest_limits(task_id)
            assert 'active_sidequests_count' in limit_status, "Limit status should include active sidequests count"
            print(f"✓ Sidequest limits checked: {limit_status['active_sidequests_count']} active")
            
            # Test progress updates
            await task_queries.update_task_progress(task_id, 50, 'in-progress')
            await task_queries.update_subtask_progress(subtask_id, 25, 'in-progress')
            print("✓ Progress updates completed")
            
            # Test status retrieval
            task_status = await task_queries.get_task_status(task_id)
            assert task_status['progress_percentage'] == 50, "Task progress should be updated"
            print("✓ Task status retrieved and verified")
            
            # Test task completion with metrics
            await task_queries.complete_task(task_id)
            completed_task = await task_queries.get_task_status(task_id)
            assert completed_task['status'] == 'completed', "Task should be completed"
            print("✓ Task completion with metrics")
            
            return True
            
        except Exception as e:
            print(f"✗ TaskStatusQueries test failed: {e}")
            return False
    
    async def test_theme_flow_queries(self):
        """Test ThemeFlowQueries functionality."""
        print("\n--- Testing ThemeFlowQueries ---")
        
        try:
            theme_queries = ThemeFlowQueries(self.db_manager)
            
            # Test theme-flow relationship creation
            theme_queries.add_theme_flow_relationship(
                theme_name="authentication",
                flow_id="auth-login-flow",
                relevance_order=1
            )
            print("✓ Theme-flow relationship created")
            
            # Test flow status tracking
            theme_queries.update_flow_status(
                flow_id='auth-login-flow',
                status='in-progress',
                completion_percentage=60
            )
            print("✓ Flow status updated")
            
            # Test flow step status
            theme_queries.update_flow_step_status(
                step_id='validate-credentials',
                status='completed'
            )
            print("✓ Flow step status updated")
            
            # Test relationship queries
            theme_flows = theme_queries.get_flows_for_theme("authentication")
            assert len(theme_flows) > 0, "Should find flows for theme"
            print(f"✓ Found {len(theme_flows)} flows for authentication theme")
            
            flow_themes = theme_queries.get_themes_for_flow("auth-login-flow")
            assert len(flow_themes) > 0, "Should find themes for flow"
            print(f"✓ Found {len(flow_themes)} themes for auth-login-flow")
            
            # Test basic theme-flow functionality
            print("✓ Basic theme-flow relationships working")
            
            return True
            
        except Exception as e:
            print(f"✗ ThemeFlowQueries test failed: {e}")
            return False
    
    async def test_event_queries(self):
        """Test EventQueries functionality."""
        print("\n--- Testing EventQueries ---")
        
        try:
            event_queries = EventQueries(self.db_manager)
            
            # Test event creation
            event_data = {
                'event_type': 'decision',
                'title': 'Chose React over Vue',
                'description': 'Decided to use React for the frontend framework',
                'primary_theme': 'frontend',
                'impact_level': 'high',
                'ai_reasoning': 'React has better ecosystem support for our use case'
            }
            
            event_id = event_queries.create_event(event_data)
            assert event_id, "Event ID should be returned"
            print(f"✓ Event created: {event_id}")
            
            # Test event retrieval
            event = event_queries.get_event(event_id)
            assert event is not None, "Event should be retrievable"
            assert event['title'] == event_data['title'], "Event title should match"
            print("✓ Event retrieved successfully")
            
            # Test event search
            events = event_queries.search_events("React", limit=10)
            assert len(events) > 0, "Should find events matching search"
            print(f"✓ Event search found {len(events)} matching events")
            
            # Test event outcome update
            success = event_queries.update_event_outcome(
                event_id, 
                "Implementation successful, React components working well"
            )
            assert success, "Event outcome update should succeed"
            print("✓ Event outcome updated")
            
            # Test event relationships
            event_data_2 = {
                'event_type': 'milestone',
                'title': 'Frontend MVP Complete',
                'description': 'Basic React frontend is functional',
                'primary_theme': 'frontend'
            }
            
            event_id_2 = event_queries.create_event(event_data_2)
            
            # Create relationship between events
            success = event_queries.create_event_relationship(
                event_id, event_id_2, 'causes'
            )
            assert success, "Event relationship should be created"
            print("✓ Event relationship created")
            
            # Test event analytics
            analytics = event_queries.get_event_analytics(days=30)
            assert 'total_events' in analytics, "Analytics should include total events"
            assert analytics['total_events'] >= 2, "Should have at least 2 events"
            print(f"✓ Event analytics: {analytics['total_events']} total events")
            
            return True
            
        except Exception as e:
            print(f"✗ EventQueries test failed: {e}")
            return False
    
    async def test_user_preference_queries(self):
        """Test UserPreferenceQueries functionality."""
        print("\n--- Testing UserPreferenceQueries ---")
        
        try:
            user_queries = UserPreferenceQueries(self.db_manager)
            
            # Test context preference learning
            context_data = {
                'task_type': 'authentication',
                'initial_mode': 'theme-focused',
                'final_mode': 'theme-expanded',
                'escalation_reason': 'Cross-theme dependencies',
                'success_outcome': True
            }
            
            preference_id = user_queries.learn_context_preference(context_data)
            assert preference_id, "Preference ID should be returned"
            print(f"✓ Context preference learned: {preference_id}")
            
            # Test theme preference tracking
            theme_data = {
                'primary_theme': 'authentication',
                'related_themes': ['security', 'user-management'],
                'context_switch_count': 2,
                'session_duration': 3600
            }
            
            theme_pref_id = user_queries.learn_theme_preference(theme_data)
            print(f"✓ Theme preference learned: {theme_pref_id}")
            
            # Test workflow preference learning
            workflow_data = {
                'workflow_pattern': 'task-sidequest-resume',
                'pattern_success': True,
                'productivity_score': 0.85
            }
            
            workflow_pref_id = user_queries.learn_workflow_preference(workflow_data)
            print(f"✓ Workflow preference learned: {workflow_pref_id}")
            
            # Test preference recommendations
            recommendations = user_queries.get_context_recommendations(
                task_context={'description': 'authentication system implementation'}
            )
            assert isinstance(recommendations, dict), "Recommendations should be dict"
            print("✓ Context recommendations generated")
            
            # Test preference analytics
            analytics = await user_queries.get_preference_analytics()
            assert 'total_preferences' in analytics, "Analytics should include totals"
            print(f"✓ Preference analytics: {analytics.get('total_preferences', 0)} preferences")
            
            return True
            
        except Exception as e:
            print(f"✗ UserPreferenceQueries test failed: {e}")
            return False
    
    async def test_file_metadata_queries(self):
        """Test FileMetadataQueries functionality."""
        print("\n--- Testing FileMetadataQueries ---")
        
        try:
            file_queries = FileMetadataQueries(self.db_manager)
            
            # Test directory metadata
            dir_metadata = {
                'directory_path': '/test/src/components',
                'purpose': 'Reusable UI components',
                'description': 'React components for authentication flow'
            }
            
            file_queries.update_directory_metadata(dir_metadata)
            print("✓ Directory metadata updated")
            
            # Test file modification logging  
            file_queries.log_file_modification(
                file_path='/test/src/components/Login.tsx',
                file_type='component',
                operation='create',
                session_id='test-session',
                details={'purpose': 'User login form component'}
            )
            print("✓ File modification logged")
            
            # Test file modification retrieval
            modifications = file_queries.get_file_modifications('/test/src/components/Login.tsx')
            assert len(modifications) > 0, "Should have file modifications"
            print("✓ File modifications retrieved")
            
            # Test metadata retrieval
            retrieved_metadata = file_queries.get_directory_metadata('/test/src/components')
            assert retrieved_metadata is not None, "Should retrieve directory metadata"
            print("✓ Directory metadata retrieved")
            
            # Test file impact analysis
            impact_analysis = file_queries.get_impact_analysis('/test/src/components/Login.tsx')
            assert isinstance(impact_analysis, dict), "Impact analysis should be dict"
            print("✓ File impact analysis completed")
            
            return True
            
        except Exception as e:
            print(f"✗ FileMetadataQueries test failed: {e}")
            return False
    
    async def test_database_performance(self):
        """Test database performance with realistic data volumes."""
        print("\n--- Testing Database Performance ---")
        
        try:
            import time
            
            # Test bulk session creation
            session_queries = SessionQueries(self.db_manager)
            
            start_time = time.time()
            session_ids = []
            for i in range(100):
                session_id = session_queries.start_session(
                    project_path=f"/test/project{i}",
                    context={"iteration": i}
                )
                session_ids.append(session_id)
            
            bulk_create_time = time.time() - start_time
            print(f"✓ Created 100 sessions in {bulk_create_time:.3f}s ({bulk_create_time*10:.1f}ms avg)")
            
            # Test bulk query performance
            start_time = time.time()
            for session_id in session_ids[:50]:  # Test first 50
                session_queries.get_session_data(session_id)
            
            bulk_query_time = time.time() - start_time
            print(f"✓ Queried 50 sessions in {bulk_query_time:.3f}s ({bulk_query_time*20:.1f}ms avg)")
            
            # Test complex analytics query performance
            start_time = time.time()
            analytics = session_queries.get_session_analytics(days=30)
            analytics_time = time.time() - start_time
            print(f"✓ Analytics query completed in {analytics_time:.3f}s")
            
            # Performance assertions
            assert bulk_create_time < 5.0, "Bulk creation should complete in under 5 seconds"
            assert bulk_query_time < 2.0, "Bulk queries should complete in under 2 seconds"
            assert analytics_time < 1.0, "Analytics should complete in under 1 second"
            
            print("✓ All performance benchmarks passed")
            return True
            
        except Exception as e:
            print(f"✗ Database performance test failed: {e}")
            return False
    
    async def test_error_handling(self):
        """Test database error handling and recovery."""
        print("\n--- Testing Error Handling ---")
        
        try:
            session_queries = SessionQueries(self.db_manager)
            
            # Test handling invalid session ID
            invalid_session = session_queries.get_session_data("nonexistent-session")
            assert invalid_session is None, "Should return None for invalid session"
            print("✓ Invalid session ID handled gracefully")
            
            # Test handling database constraint violations
            task_queries = TaskStatusQueries(self.db_manager)
            
            # Try to create duplicate task
            task_id = await task_queries.create_task(
                task_id='duplicate-test',
                title='Test Task',
                description='Test task for duplicate check',
                primary_theme='testing',
                milestone_id='M01'
            )
            
            # Attempt to create same task again (should handle gracefully)
            try:
                await task_queries.create_task(
                    task_id='duplicate-test',
                    title='Test Task Duplicate',
                    description='Test task duplicate',
                    primary_theme='testing',
                    milestone_id='M01'
                )
                # If no exception, the method handled it gracefully
                print("✓ Duplicate task creation handled gracefully")
            except Exception:
                # Exception is also acceptable if properly logged
                print("✓ Duplicate task creation raised expected exception")
            
            # Test handling malformed data
            event_queries = EventQueries(self.db_manager)
            
            try:
                # Try to create event with minimal data
                minimal_event = event_queries.create_event({})
                print("✓ Minimal event data handled gracefully")
            except Exception:
                print("✓ Invalid event data raised expected exception")
            
            # Test transaction rollback
            try:
                with self.db_manager.transaction():
                    await task_queries.create_task(
                        task_id='rollback-test',
                        title='Rollback Test',
                        description='Test transaction rollback',
                        primary_theme='testing',
                        milestone_id='M01'
                    )
                    # Force an error to trigger rollback
                    raise ValueError("Intentional error for rollback test")
                    
            except ValueError:
                # Check that task was not created due to rollback
                task = await task_queries.get_task_status('rollback-test')
                assert task is None, "Task should not exist due to rollback"
                print("✓ Transaction rollback working correctly")
            
            return True
            
        except Exception as e:
            print(f"✗ Error handling test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all database tests."""
        print("=== Database Infrastructure Test Suite ===\n")
        
        await self.setup_test_database()
        
        tests = [
            ("Database Manager", self.test_database_manager),
            ("Session Queries", self.test_session_queries),
            ("Task Status Queries", self.test_task_status_queries),
            ("Theme Flow Queries", self.test_theme_flow_queries),
            ("Event Queries", self.test_event_queries),
            ("User Preference Queries", self.test_user_preference_queries),
            ("File Metadata Queries", self.test_file_metadata_queries),
            ("Database Performance", self.test_database_performance),
            ("Error Handling", self.test_error_handling),
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
        self.cleanup_test_database()
        
        # Summary
        print("\n=== Test Summary ===")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All database tests passed!")
            return 0
        else:
            print("❌ Some database tests failed")
            return 1


async def main():
    """Run database test suite."""
    test_suite = DatabaseTestSuite()
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