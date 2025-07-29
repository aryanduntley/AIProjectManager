#!/usr/bin/env python3
"""
Debug script to check task management directive structure.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add ai-pm-mcp to Python path
sys.path.insert(0, str(Path(__file__).parent / "ai-pm-mcp"))

from core.scope_engine import CompressedContextManager

async def debug_task_directive():
    """Debug the task management directive structure."""
    
    # Initialize context manager
    mcp_server_path = Path(__file__).parent / "ai-pm-mcp"
    context_manager = CompressedContextManager(mcp_server_path)
    
    # Load core context
    await context_manager.load_core_context()
    
    # Get task management directive
    task_directive = context_manager.get_directive_summary("taskManagement")
    
    print("=== Task Management Directive Structure ===")
    print(json.dumps(task_directive, indent=2))
    
    # Check if it has implementationNote
    def search_for_implementation_note(obj, path=""):
        if isinstance(obj, dict):
            if 'implementationNote' in obj:
                print(f"\n✓ Found implementationNote at: {path}")
                print(f"Content: {obj['implementationNote'][:100]}...")
                return True
            for key, value in obj.items():
                if search_for_implementation_note(value, f"{path}.{key}" if path else key):
                    return True
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if search_for_implementation_note(item, f"{path}[{i}]"):
                    return True
        return False
    
    has_note = search_for_implementation_note(task_directive)
    
    if not has_note:
        print("\n❌ No implementationNote found")
        
        # Let's check what directive keys are available
        print("\n=== Available Directive Keys ===")
        core_context = context_manager._core_context.get('directive-compressed', {})
        for key in core_context.keys():
            print(f"- {key}")
    
    # Test the helper method
    print(f"\n=== Testing _has_implementation_note method ===")
    result = context_manager._has_implementation_note(task_directive)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(debug_task_directive())