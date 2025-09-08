"""
Decorator Functions Module for DirectiveProcessor.

EXTRACTED from OLD_directive_processor.py decorator functions.
Handles completion hook decorators for directive processing.

NOTE: These decorators use queue_event() which was part of the recursion fix.
They may need updating for the new pause/resume architecture.
"""

import logging

logger = logging.getLogger(__name__)


def on_conversation_to_action(directive_processor):
    """
    Decorator for conversation-to-action transition hooks.
    
    EXTRACTED from OLD_directive_processor.py - FIXED VERSION.
    Uses event queuing instead of immediate execution to prevent recursion.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Execute original function
            result = await func(*args, **kwargs)
            
            # QUEUE event instead of immediate execution (prevents recursion)
            if hasattr(directive_processor, 'queue_event'):
                context = {
                    "trigger": "conversation_to_action_transition",
                    "function_result": result,
                    "args": args,
                    "kwargs": kwargs
                }
                directive_processor.queue_event("sessionManagement", context)
            else:
                # Fallback for new architecture - may use consultation manager
                logger.info("on_conversation_to_action hook triggered - queue_event not available")
            
            return result
        return wrapper
    return decorator


def on_file_edit_complete(directive_processor):
    """
    Decorator for file edit completion hooks.
    
    EXTRACTED from OLD_directive_processor.py - FIXED VERSION.
    Uses event queuing instead of immediate execution to prevent recursion.
    """
    def decorator(func):
        async def wrapper(file_path: str, *args, **kwargs):
            # Execute original function
            result = await func(file_path, *args, **kwargs)
            
            # QUEUE event instead of immediate execution (prevents recursion)
            if hasattr(directive_processor, 'queue_event'):
                context = {
                    "trigger": "file_edit_completion",
                    "file_path": file_path,
                    "changes_made": result,
                    "function_args": args,
                    "function_kwargs": kwargs
                }
                directive_processor.queue_event("fileOperations", context)
            else:
                # Fallback for new architecture - may use consultation manager
                logger.info(f"on_file_edit_complete hook triggered for {file_path} - queue_event not available")
            
            return result
        return wrapper
    return decorator


def on_task_completion(directive_processor):
    """
    Decorator for task completion hooks.
    
    EXTRACTED from OLD_directive_processor.py - FIXED VERSION.
    Uses event queuing instead of immediate execution to prevent recursion.
    """
    def decorator(func):
        async def wrapper(task_id: str, *args, **kwargs):
            # Execute original function 
            result = await func(task_id, *args, **kwargs)
            
            # QUEUE event instead of immediate execution (prevents recursion)
            if hasattr(directive_processor, 'queue_event'):
                context = {
                    "trigger": "task_completion",
                    "task_id": task_id,
                    "completion_result": result,
                    "function_args": args,
                    "function_kwargs": kwargs
                }
                directive_processor.queue_event("taskManagement", context)
            else:
                # Fallback for new architecture - may use consultation manager
                logger.info(f"on_task_completion hook triggered for {task_id} - queue_event not available")
            
            return result
        return wrapper
    return decorator