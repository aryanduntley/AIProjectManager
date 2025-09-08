"""
Central AI-powered directive processing with explicit escalation.

This module implements the critical gap fix identified in the MCP implementation -
providing explicit integration points between MCP execution and directive guidance.

ARCHITECTURAL FIX: Event queue system implemented to prevent recursive execution loops.
"""

import json
import asyncio
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# MCP framework imports (will be added when available)
try:
    from mcp import types
    from mcp.server import Server
except ImportError:
    # Fallback for development
    types = None
    Server = None

logger = logging.getLogger(__name__)


class DirectiveProcessor:
    """
    Central AI-powered directive processing with explicit escalation.
    
    This class serves as the bridge between MCP execution and directive guidance,
    implementing the critical integration points missing from the original MCP design.
    """
    
    def __init__(self, action_executor=None):
        """Initialize the directive processor with compressed directives and event queue."""
        self.compressed_directives = None
        self.action_executor = action_executor
        
        # Event queue system (replaces recursion-prone direct calls)
        self._event_queue = asyncio.Queue()
        self._processing_events = False
        self._event_processor_task = None
        
        # Legacy recursion tracking (kept as ultimate failsafe during transition)
        self._execution_stack = []  # Will be removed after full event queue adoption
        
        self._load_compressed_directives()
    
    def _load_compressed_directives(self):
        """Load directive-compressed.json once at startup."""
        try:
            compressed_path = Path(__file__).parent.parent / "core-context" / "directive-compressed.json"
            if compressed_path.exists():
                with open(compressed_path, 'r', encoding='utf-8') as f:
                    self.compressed_directives = json.load(f)
                logger.info(f"Loaded {len(self.compressed_directives)} compressed directives")
            else:
                logger.error(f"Compressed directives not found at: {compressed_path}")
                self.compressed_directives = {}
        except Exception as e:
            logger.error(f"Failed to load compressed directives: {e}")
            self.compressed_directives = {}
    
    def queue_event(self, event_type: str, context: Dict[str, Any], priority: int = 0):
        """Queue an event for processing instead of immediate execution."""
        event = {
            "event_type": event_type,
            "context": context.copy(),  # Prevent context mutation
            "priority": priority,
            "timestamp": time.time(),
            "event_id": f"{event_type}:{uuid.uuid4().hex[:8]}"
        }
        
        self._event_queue.put_nowait(event)
        logger.debug(f"[EVENT_QUEUE] Queued: {event['event_id']}")
        
        # Start event processor if not running
        if not self._processing_events:
            self._event_processor_task = asyncio.create_task(self._process_event_queue())
    
    async def _process_event_queue(self):
        """Process queued events sequentially to prevent recursion."""
        self._processing_events = True
        logger.info("[EVENT_PROCESSOR] Starting event queue processing")
        
        try:
            while not self._event_queue.empty():
                event = await self._event_queue.get()
                
                try:
                    logger.info(f"[EVENT_PROCESSOR] Processing: {event['event_id']}")
                    await self._execute_directive_internal(
                        event["event_type"], 
                        event["context"]
                    )
                    logger.debug(f"[EVENT_PROCESSOR] Completed: {event['event_id']}")
                    
                except Exception as e:
                    logger.error(f"[EVENT_PROCESSOR] Failed {event['event_id']}: {e}")
                    # Continue processing other events
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.001)
                
        finally:
            self._processing_events = False
            logger.info("[EVENT_PROCESSOR] Event queue processing complete")
    
    async def _execute_directive_internal(self, directive_key: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Internal directive execution - does NOT queue events (prevents recursion)."""
        logger.info(f"[DIRECTIVE_EXEC] Executing: {directive_key}")
        
        # Flag to prevent decorators from queuing events during execution
        context["_suppress_events"] = True
        
        try:
            # 1. Validate directive key exists
            if not self.compressed_directives or directive_key not in self.compressed_directives:
                logger.error(f"[DIRECTIVE_EXEC] Unknown directive key: {directive_key}")
                return {
                    "directive_key": directive_key,
                    "error": f"Unknown directive key: {directive_key}",
                    "actions_taken": [],
                    "escalated": False
                }
            
            # 2. Get compressed directive content
            directive_content = self.compressed_directives[directive_key]
            
            # 3. Check for forced escalation operations
            forced_escalation_keys = [
                "01-system-initialization", "15-git-integration", "03-session-management", 
                "14-branch-management", "database-integration", "09-logging-documentation", 
                "04-theme-management", "08-project-management"
            ]
            
            needs_escalation = (
                directive_key in forced_escalation_keys or
                "implementationNote" in str(directive_content)
            )
            
            if needs_escalation:
                return await self.escalate_directive(directive_key, context, "Forced escalation operation")
            
            # 4. Analyze directive + context to determine actions
            actions = await self._ai_determine_actions(directive_content, context, directive_key)
            
            # 5. Handle escalation if AI requests it
            if actions.get("needs_escalation"):
                escalated_actions = await self.escalate_directive(
                    directive_key, 
                    context, 
                    actions.get("escalation_reason", "AI requested more detailed guidance")
                )
                return escalated_actions
            
            # 6. Execute determined actions via action executor
            execution_results = []
            if self.action_executor:
                execution_results = await self.action_executor.execute_actions(actions.get("actions", []))
            
            return {
                "directive_key": directive_key,
                "actions_taken": actions.get("actions", []),
                "execution_results": execution_results,
                "escalated": False,
                "analysis": actions.get("analysis", "")
            }
            
        except Exception as e:
            logger.error(f"[DIRECTIVE_EXEC] Error in {directive_key}: {e}")
            return {
                "directive_key": directive_key,
                "error": str(e),
                "actions_taken": [],
                "escalated": False
            }
        finally:
            # Remove suppression flag
            context.pop("_suppress_events", None)
    
    async def execute_directive(self, directive_key: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute specific directive with AI decision-making and optional escalation.
        
        This is the core method that MCP code should call at integration points.
        Uses the new event queue architecture to prevent recursion.
        
        Args:
            directive_key: Key identifying which directive to execute
            context: Execution context containing trigger info, project state, etc.
            
        Returns:
            Dict containing actions taken, results, and escalation status
        """
        # Check if we're in event suppression mode (prevents recursive queueing)
        if context.get("_suppress_events", False):
            logger.debug(f"[EXECUTE_DIRECTIVE] Events suppressed, using internal execution: {directive_key}")
            return await self._execute_directive_internal(directive_key, context)
        
        # For external calls, use the new event-queue based execution
        logger.info(f"[EXECUTE_DIRECTIVE] === EXECUTING DIRECTIVE: {directive_key} ===")
        logger.info(f"[EXECUTE_DIRECTIVE] Context keys: {list(context.keys())}")
        logger.info(f"[EXECUTE_DIRECTIVE] Trigger: {context.get('trigger', 'NOT_SET')}")
        
        # Write debug to file for reliable access
        from pathlib import Path
        debug_file = Path(context.get('project_path', '.')) / "debug_directive.log"
        
        def write_directive_debug(msg):
            try:
                with open(debug_file, "a") as f:
                    f.write(f"{msg}\n")
            except Exception:
                pass  # Don't fail if we can't write debug
        
        write_directive_debug(f"=== NEW DIRECTIVE PROCESSOR (NO RECURSION) ===")
        write_directive_debug(f"[EXECUTE_DIRECTIVE] === EXECUTING DIRECTIVE: {directive_key} ===")
        write_directive_debug(f"[EXECUTE_DIRECTIVE] Context keys: {list(context.keys())}")
        write_directive_debug(f"[EXECUTE_DIRECTIVE] Trigger: {context.get('trigger', 'NOT_SET')}")
        
        try:
            # Execute directly using internal method (no recursion possible)
            return await self._execute_directive_internal(directive_key, context)
            
        except Exception as e:
            logger.error(f"Error executing directive {directive_key}: {e}")
            return {
                "directive_key": directive_key,
                "error": str(e),
                "actions_taken": [],
                "escalated": False
            }
    
    async def escalate_directive(self, directive_key: str, context: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """
        Escalate to JSON or MD directive files when compressed insufficient.
        
        Implements the 3-tier escalation system:
        1. compressed -> 2. JSON -> 3. MD
        """
        logger.info(f"[DEBUG_DIRECTIVE] === ESCALATING DIRECTIVE: {directive_key} ===")
        logger.info(f"[DEBUG_DIRECTIVE] Escalation reason: {reason}")
        
        # Check if directive has implementationNote with specific file path
        directive_content = self.compressed_directives.get(directive_key, {})
        implementation_note = directive_content.get("implementationNote", "")
        
        # Extract file path from implementationNote if available
        actual_directive_name = directive_key  # default fallback
        if implementation_note and "reference/directives/" in implementation_note:
            # Extract filename from implementationNote
            # Format: "...Load reference/directives/02-project-initialization.json for..."
            import re
            match = re.search(r'reference/directives/([^.]+)\.json', implementation_note)
            if match:
                actual_directive_name = match.group(1)
                logger.info(f"[DEBUG_DIRECTIVE] Extracted directive name from implementationNote: {actual_directive_name}")
        
        # Try JSON first (Tier 2)
        json_path = Path(__file__).parent.parent / "reference" / "directives" / f"{actual_directive_name}.json"
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_content = json.load(f)
                
                logger.info(f"Escalated to JSON directive: {directive_key}")
                
                # AI analyzes detailed JSON directive + context
                actions = await self._ai_determine_actions(json_content, context, directive_key, tier=2)
                
                # Further escalation to MD if needed
                if actions.get("needs_escalation"):
                    return await self.escalate_to_markdown(
                        directive_key, 
                        context, 
                        actions.get("escalation_reason", "Still need more comprehensive guidance")
                    )
                
                # Execute actions
                execution_results = []
                if self.action_executor:
                    execution_results = await self.action_executor.execute_actions(actions.get("actions", []))
                
                return {
                    "directive_key": directive_key,
                    "actions_taken": actions.get("actions", []),
                    "execution_results": execution_results,
                    "escalated": True,
                    "escalation_level": "JSON",
                    "escalation_reason": reason,
                    "analysis": actions.get("analysis", "")
                }
                
            except Exception as e:
                logger.error(f"Error processing JSON directive {directive_key}: {e}")
        
        # If JSON doesn't exist or fails, try MD directly
        return await self.escalate_to_markdown(directive_key, context, reason)
    
    async def escalate_to_markdown(self, directive_key: str, context: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Final escalation to Markdown directive files."""
        logger.info(f"[DEBUG_DIRECTIVE] Final escalation to MD for directive {directive_key}")
        
        # Check if directive has implementationNote with specific file path (same logic as JSON escalation)
        directive_content = self.compressed_directives.get(directive_key, {})
        implementation_note = directive_content.get("implementationNote", "")
        
        # Extract file path from implementationNote if available
        actual_directive_name = directive_key  # default fallback
        if implementation_note and "reference/directives/" in implementation_note:
            import re
            match = re.search(r'reference/directives/([^.]+)\.json', implementation_note)
            if match:
                actual_directive_name = match.group(1)
                logger.info(f"[DEBUG_DIRECTIVE] Using directive name for MD: {actual_directive_name}")
        
        md_path = Path(__file__).parent.parent / "reference" / "directivesmd" / f"{actual_directive_name}.md"
        if md_path.exists():
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                logger.info(f"Escalated to MD directive: {directive_key}")
                
                # AI analyzes comprehensive Markdown directive + context  
                actions = await self._ai_determine_actions(md_content, context, directive_key, tier=3)
                
                # Execute actions
                execution_results = []
                if self.action_executor:
                    execution_results = await self.action_executor.execute_actions(actions.get("actions", []))
                
                return {
                    "directive_key": directive_key,
                    "actions_taken": actions.get("actions", []),
                    "execution_results": execution_results,
                    "escalated": True,
                    "escalation_level": "MARKDOWN",
                    "escalation_reason": reason,
                    "analysis": actions.get("analysis", "")
                }
                
            except Exception as e:
                logger.error(f"Error processing MD directive {directive_key}: {e}")
        
        # If no escalation files found
        logger.error(f"No escalation files found for directive: {directive_key}")
        return {
            "directive_key": directive_key,
            "error": f"No escalation files found for directive: {directive_key}",
            "actions_taken": [],
            "escalated": True,
            "escalation_level": "FAILED"
        }
    
    async def _ai_determine_actions(
        self, 
        directive_content: Any, 
        context: Dict[str, Any], 
        directive_key: str,
        tier: int = 1
    ) -> Dict[str, Any]:
        """
        AI analyzes directive content + context to determine appropriate actions.
        
        This is where the actual AI decision-making happens based on directive guidance.
        For now, implementing basic rule-based action determination that can be 
        enhanced with actual AI analysis later.
        """
        # DEBUG_DIRECTIVE: AI determination entry
        logger.info(f"[DEBUG_DIRECTIVE] === AI DETERMINE ACTIONS START ===")
        logger.info(f"[DEBUG_DIRECTIVE] Directive: {directive_key}, Tier: {tier}")
        logger.info(f"[DEBUG_DIRECTIVE] Directive content type: {type(directive_content)}")
        logger.info(f"[DEBUG_DIRECTIVE] Context keys: {list(context.keys())}")
        
        # Basic action determination based on common patterns
        actions = []
        analysis = ""
        needs_escalation = False
        escalation_reason = ""
        
        try:
            # Extract trigger information
            trigger = context.get("trigger", "unknown")
            logger.info(f"[DEBUG_DIRECTIVE] Trigger extracted: {trigger}")
            
            # Session management actions
            if directive_key == "sessionManagement" or "session" in directive_key:
                if trigger == "session_start":
                    actions.extend([
                        {
                            "type": "initialize_session",
                            "parameters": {"context": context}
                        },
                        {
                            "type": "restore_session_context", 
                            "parameters": {"session_data": context.get("session_context", {})}
                        }
                    ])
                    analysis = "Session start detected - initializing session and restoring context"
                
                elif trigger == "work_pause":
                    # Comprehensive work pause - thorough cleanup for /aipm-pause
                    actions.extend([
                        {
                            "type": "check_completed_subtasks",
                            "parameters": {"mark_completions": True}
                        },
                        {
                            "type": "update_project_state",
                            "parameters": {"thorough_update": True}
                        },
                        {
                            "type": "save_session_summary",
                            "parameters": {"summary": context.get("pause_context", {})}
                        },
                        {
                            "type": "update_database_session",
                            "parameters": {"prepare_for_resume": True, "current_state": context.get("current_project_state", {})}
                        }
                    ])
                    analysis = "Work pause detected - performing thorough cleanup and state preservation for resume"
                
                elif trigger == "conversation_to_action_transition":
                    # Real-time state preservation during natural workflow
                    actions.extend([
                        {
                            "type": "update_project_state",
                            "parameters": {"incremental_update": True}
                        },
                        {
                            "type": "log_noteworthy_event",
                            "parameters": {
                                "event": "conversation_to_action",
                                "context": context.get("conversation_context", {}),
                                "timestamp": "now"
                            }
                        }
                    ])
                    analysis = "Conversation to action transition - preserving state during workflow"
            
            # File operations actions
            elif directive_key == "fileOperations" or "file" in directive_key:
                if trigger == "file_edit_completion":
                    file_path = context.get("file_path", "")
                    actions.extend([
                        {
                            "type": "update_database_file_metadata",
                            "parameters": {
                                "file_path": file_path,
                                "changes": context.get("changes_made", {})
                            }
                        },
                        {
                            "type": "check_line_limits",
                            "parameters": {"file_path": file_path}
                        },
                        {
                            "type": "update_themes",
                            "parameters": {"affected_file": file_path}
                        }
                    ])
                    analysis = f"File edit completion for {file_path} - updating metadata and checking constraints"
            
            # Task management actions
            elif directive_key == "taskManagement" or "task" in directive_key:
                if trigger == "task_completion":
                    task_id = context.get("task_id", "")
                    actions.extend([
                        {
                            "type": "update_task_status",
                            "parameters": {
                                "task_id": task_id,
                                "status": "completed",
                                "completion_result": context.get("completion_result", {})
                            }
                        },
                        {
                            "type": "update_project_state",
                            "parameters": {"task_completion": True}
                        },
                        {
                            "type": "log_noteworthy_event",
                            "parameters": {
                                "event": "task_completed",
                                "task_id": task_id,
                                "timestamp": "now"
                            }
                        }
                    ])
                    analysis = f"Task completion for {task_id} - updating status and logging event"
            
            # Project initialization actions
            elif directive_key == "projectInitialization":
                logger.info(f"[DEBUG_DIRECTIVE] MATCHED: projectInitialization directive")
                
                # Extract initialization parameters properly
                init_request = context.get("initialization_request", {})
                force_reinit = init_request.get("force_reinitialize", False) or context.get("force", False)
                
                logger.info(f"[DEBUG_DIRECTIVE] Init request: {init_request}")
                logger.info(f"[DEBUG_DIRECTIVE] Force reinit: {force_reinit}")
                logger.info(f"[DEBUG_DIRECTIVE] Project path from context: {context.get('project_path', 'NOT_SET')}")
                
                actions.extend([
                    {
                        "type": "analyze_project_structure",
                        "parameters": {
                            "project_path": context.get("project_path", ""),
                            "force": force_reinit
                        }
                    },
                    {
                        "type": "create_project_blueprint",
                        "parameters": {
                            "project_path": context.get("project_path", ""),
                            "project_analysis": "pending",
                            "project_name": init_request.get("project_name", ""),
                            "description": init_request.get("description", "")
                        }
                    },
                    {
                        "type": "initialize_database",
                        "parameters": {
                            "fresh_init": force_reinit,
                            "initialize_database": init_request.get("initialize_database", True)
                        }
                    }
                ])
                analysis = "Project initialization requested - analyzing structure and creating blueprint"
                # This usually needs escalation for user consultation
                needs_escalation = True
                escalation_reason = "Need detailed project consultation workflow"
                
                logger.info(f"[DEBUG_DIRECTIVE] Project init actions created: {len(actions)}")
                logger.info(f"[DEBUG_DIRECTIVE] Project init needs escalation: {needs_escalation}")
                logger.info(f"[DEBUG_DIRECTIVE] Project init escalation reason: {escalation_reason}")
            
            # Theme management actions  
            elif directive_key == "themeManagement":
                actions.extend([
                    {
                        "type": "discover_themes",
                        "parameters": {"project_structure": context.get("project_context", {})}
                    },
                    {
                        "type": "validate_themes", 
                        "parameters": {"existing_themes": context.get("current_themes", [])}
                    }
                ])
                analysis = "Theme management requested - discovering and validating themes"
            
            # For complex directives, escalate to get detailed guidance
            elif tier == 1 and any(key in directive_key for key in ["system", "git", "branch", "database"]):
                needs_escalation = True
                escalation_reason = "Complex system operation requires detailed guidance"
                analysis = f"Complex directive {directive_key} requires escalation for proper implementation"
            
            else:
                # Default minimal actions
                actions.append({
                    "type": "log_directive_execution",
                    "parameters": {
                        "directive_key": directive_key,
                        "trigger": trigger,
                        "timestamp": "now"
                    }
                })
                analysis = f"Basic logging for directive {directive_key} with trigger {trigger}"
        
        except Exception as e:
            logger.error(f"[DEBUG_DIRECTIVE] ERROR in AI action determination: {e}")
            analysis = f"Error analyzing directive: {e}"
            needs_escalation = True
            escalation_reason = f"Error during analysis: {e}"
        
        # DEBUG_DIRECTIVE: Final action determination results
        final_result = {
            "actions": actions,
            "analysis": analysis,
            "needs_escalation": needs_escalation,
            "escalation_reason": escalation_reason,
            "directive_key": directive_key,
            "tier": tier
        }
        
        logger.info(f"[DEBUG_DIRECTIVE] === AI DETERMINE ACTIONS END ===")
        logger.info(f"[DEBUG_DIRECTIVE] Final actions count: {len(actions)}")
        logger.info(f"[DEBUG_DIRECTIVE] Final analysis: {analysis}")
        logger.info(f"[DEBUG_DIRECTIVE] Final needs_escalation: {needs_escalation}")
        logger.info(f"[DEBUG_DIRECTIVE] Final escalation_reason: {escalation_reason}")
        
        return final_result
    
    async def shutdown(self):
        """Graceful shutdown with event queue cleanup."""
        logger.info("[SHUTDOWN] Stopping DirectiveProcessor")
        
        # Wait for event queue to empty
        if self._processing_events and self._event_processor_task:
            try:
                await asyncio.wait_for(self._event_processor_task, timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning("[SHUTDOWN] Event processor timeout - forcing stop")
                self._event_processor_task.cancel()
        
        # Clear any remaining events
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                logger.warning(f"[SHUTDOWN] Discarding event: {event.get('event_id', 'unknown')}")
            except asyncio.QueueEmpty:
                break
        
        logger.info("[SHUTDOWN] DirectiveProcessor stopped")

    def get_available_directives(self) -> List[str]:
        """Get list of available directive keys."""
        return list(self.compressed_directives.keys()) if self.compressed_directives else []
    
    def is_directive_available(self, directive_key: str) -> bool:
        """Check if a directive key is available."""
        return directive_key in self.compressed_directives if self.compressed_directives else False


# Integration hook point decorators for easy MCP integration
def on_conversation_to_action(directive_processor: DirectiveProcessor):
    """Decorator for conversation-to-action transition hooks - FIXED VERSION."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Execute original function
            result = await func(*args, **kwargs)
            
            # QUEUE event instead of immediate execution (prevents recursion)
            context = {
                "trigger": "conversation_to_action_transition",
                "function_result": result,
                "args": args,
                "kwargs": kwargs
            }
            directive_processor.queue_event("sessionManagement", context)
            
            return result
        return wrapper
    return decorator


def on_file_edit_complete(directive_processor: DirectiveProcessor):
    """Decorator for file edit completion hooks - FIXED VERSION."""
    def decorator(func):
        async def wrapper(file_path: str, *args, **kwargs):
            # Execute original function
            result = await func(file_path, *args, **kwargs)
            
            # QUEUE event instead of immediate execution (prevents recursion)
            context = {
                "trigger": "file_edit_completion",
                "file_path": file_path,
                "changes_made": result,
                "function_args": args,
                "function_kwargs": kwargs
            }
            directive_processor.queue_event("fileOperations", context)
            
            return result
        return wrapper
    return decorator


def on_task_completion(directive_processor: DirectiveProcessor):
    """Decorator for task completion hooks - FIXED VERSION."""
    def decorator(func):
        async def wrapper(task_id: str, *args, **kwargs):
            # Execute original function 
            result = await func(task_id, *args, **kwargs)
            
            # QUEUE event instead of immediate execution (prevents recursion)
            context = {
                "trigger": "task_completion",
                "task_id": task_id,
                "completion_result": result,
                "function_args": args,
                "function_kwargs": kwargs
            }
            directive_processor.queue_event("taskManagement", context)
            
            return result
        return wrapper
    return decorator


# Utility function to create properly configured directive processor
def create_directive_processor(action_executor=None) -> DirectiveProcessor:
    """Create a properly configured DirectiveProcessor instance."""
    processor = DirectiveProcessor(action_executor=action_executor)
    
    if not processor.compressed_directives:
        logger.warning("DirectiveProcessor created but no directives loaded")
    else:
        logger.info(f"DirectiveProcessor created with {len(processor.compressed_directives)} directives")
    
    return processor


if __name__ == "__main__":
    # Test basic functionality
    async def test_directive_processor():
        processor = create_directive_processor()
        
        # Test available directives
        directives = processor.get_available_directives()
        print(f"Available directives: {directives}")
        
        # Test basic execution
        if directives:
            test_context = {
                "trigger": "test",
                "project_context": {"status": "testing"}
            }
            
            result = await processor.execute_directive(directives[0], test_context)
            print(f"Test result: {result}")
    
    # Run test
    asyncio.run(test_directive_processor())