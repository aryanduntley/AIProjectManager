#!/usr/bin/env python3
"""
Test script for the new directive escalation system.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add ai-pm-mcp to Python path
sys.path.insert(0, str(Path(__file__).parent / "ai-pm-mcp"))

from core.scope_engine import CompressedContextManager

async def test_directive_escalation():
    """Test the new directive escalation logic."""
    print("=== Testing Directive Escalation System ===\n")
    
    # Initialize context manager
    mcp_server_path = Path(__file__).parent / "ai-pm-mcp"
    context_manager = CompressedContextManager(mcp_server_path)
    
    # Load core context
    await context_manager.load_core_context()
    print("✓ Core context loaded\n")
    
    # Test scenarios
    test_cases = [
        # Forced JSON operations
        {
            "directive_id": "03-session-management",
            "operation_context": "session start",
            "expected_level": "json",
            "description": "Session management should force JSON"
        },
        {
            "directive_id": "15-git-integration", 
            "operation_context": "git repository detection",
            "expected_level": "json",
            "description": "Git integration should force JSON"
        },
        {
            "directive_id": "14-instance-management",
            "operation_context": "instance creation",
            "expected_level": "json", 
            "description": "Instance management should force JSON"
        },
        
        # Auto-escalate with implementationNote
        {
            "directive_id": "06-task-management",
            "operation_context": "routine task execution",
            "expected_level": "json",
            "description": "Task management has implementationNote, should auto-escalate to JSON"
        },
        
        # Should stay compressed for routine operations
        {
            "directive_id": "11-quality-assurance",
            "operation_context": "basic validation",
            "expected_level": "compressed",
            "description": "Basic validation should stay compressed"
        },
        
        # Auto-escalate based on context triggers
        {
            "directive_id": "05-context-loading",
            "operation_context": "database operations needed",
            "expected_level": "json",
            "description": "Database operations should trigger JSON escalation"
        }
    ]
    
    # Run tests
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}/{total}: {test_case['description']}")
        
        # Get escalation level
        actual_level = context_manager.get_directive_escalation_level(
            test_case['directive_id'], 
            test_case['operation_context']
        )
        
        # Check result
        if actual_level == test_case['expected_level']:
            print(f"  ✓ PASS - Escalated to {actual_level}")
            passed += 1
        else:
            print(f"  ✗ FAIL - Expected {test_case['expected_level']}, got {actual_level}")
        
        print()
    
    # Test full directive loading
    print("=== Testing Full Directive Loading ===\n")
    
    # Test loading a forced JSON directive
    session_directive = await context_manager.load_directive_with_escalation(
        "03-session-management", "session boot sequence"
    )
    
    if session_directive.get('escalation_level') == 'json':
        print("✓ Session management directive loaded with JSON escalation")
        print(f"  - Has compressed: {'compressed' in session_directive}")
        print(f"  - Has JSON: {'json' in session_directive}")
        print(f"  - Escalation reason: {session_directive.get('escalation_reason', 'None')}")
        passed += 1
    else:
        print(f"✗ Expected JSON escalation, got {session_directive.get('escalation_level', 'unknown')}")
    
    total += 1
    print()
    
    # Test markdown escalation
    print("=== Testing Markdown Escalation ===\n")
    
    should_escalate = context_manager.should_escalate_to_markdown(
        "06-task-management", 
        json_context_insufficient=True
    )
    
    if should_escalate:
        print("✓ Correctly identified need for markdown escalation")
        passed += 1
        
        # Test loading with markdown
        task_directive = await context_manager.load_directive_with_escalation(
            "06-task-management", "complex sidequest creation", force_level="markdown"
        )
        
        if task_directive.get('escalation_level') == 'markdown':
            print("✓ Task management directive loaded with markdown escalation")
            print(f"  - Has compressed: {'compressed' in task_directive}")
            print(f"  - Has JSON: {'json' in task_directive}")
            print(f"  - Has markdown: {'markdown' in task_directive}")
            passed += 1
        else:
            print(f"✗ Expected markdown escalation, got {task_directive.get('escalation_level', 'unknown')}")
        
        total += 1
    else:
        print("✗ Failed to identify need for markdown escalation")
    
    total += 1
    print()
    
    # Summary
    print("=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Directive escalation system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_directive_escalation())
    sys.exit(0 if success else 1)