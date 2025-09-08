"""
Central AI-powered directive processing with modular architecture.

This module implements the primary DirectiveProcessor class while delegating 
specialized functionality to focused modules in directive_modules/.

MAINTAINS COMPATIBILITY: All existing imports and API calls continue to work unchanged.
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
    Primary DirectiveProcessor class with modular architecture.
    
    Maintains exact same public API as before while delegating specialized
    functionality to focused modules. Existing integrations with action_executors
    are preserved unchanged.
    """
    
    def __init__(self, action_executor=None):
        """
        Initialize the directive processor.
        
        Args:
            action_executor: Existing action executor integration (PRESERVED)
        """
        # CRITICAL: Preserve existing action_executor integration
        self.action_executor = action_executor
        
        # Load compressed directives (preserve existing behavior)
        self.compressed_directives = None
        self._load_compressed_directives()
        
        # Lazy-loaded modular components (only create when needed)
        self._skeleton_manager = None
        self._consultation_manager = None  
        self._state_manager = None
        self._escalation_engine = None
        self._action_determiner = None
        
        # Legacy support during transition (may be removed later)
        self._event_queue = asyncio.Queue()
        self._processing_events = False
        self._event_processor_task = None
        self._execution_stack = []  # Legacy recursion tracking
        
        logger.info("DirectiveProcessor initialized with modular architecture")
    
    def _load_compressed_directives(self):
        """Load compressed directives from file (preserve existing behavior)."""
        try:
            # Use same path resolution as before
            current_dir = Path(__file__).parent
            compressed_file = current_dir / ".." / "core-context" / "directive-compressed.json"
            
            if not compressed_file.exists():
                logger.warning(f"Compressed directives file not found: {compressed_file}")
                return
            
            with open(compressed_file, 'r') as f:
                self.compressed_directives = json.load(f)
            
            logger.info("Compressed directives loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load compressed directives: {e}")
            self.compressed_directives = {}
    
    # =================================================================
    # PUBLIC API METHODS - MUST MAINTAIN EXACT SAME INTERFACE
    # =================================================================
    
    async def execute_directive(self, directive_key: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main directive execution method.
        
        PRESERVED API: This method maintains exact same signature and behavior
        as the original DirectiveProcessor to ensure compatibility.
        """
        logger.info(f"DirectiveProcessor executing directive: {directive_key}")
        
        try:
            # Phase 1: Get action determiner (lazy load)
            action_determiner = self._get_action_determiner()
            
            # Phase 2: Determine actions needed (delegate to module)
            actions_result = await action_determiner.determine_actions(
                directive_key, context, self.compressed_directives,
                directive_content=None, tier=1
            )
            
            # Phase 3: Execute actions using EXISTING action_executor integration
            if self.action_executor and actions_result.get("actions"):
                logger.info(f"Executing {len(actions_result['actions'])} actions via action_executor")
                execution_results = await self.action_executor.execute_actions(actions_result["actions"])
                actions_result["execution_results"] = execution_results
            else:
                logger.warning("No action_executor available or no actions to execute")
            
            return actions_result
            
        except Exception as e:
            logger.error(f"Error executing directive {directive_key}: {e}")
            return {
                "directive_key": directive_key,
                "error": str(e),
                "actions_taken": [],
                "escalated": False
            }
    
    async def escalate_directive(self, directive_key: str, context: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Escalate directive to JSON level (preserve existing API)."""
        escalation_engine = self._get_escalation_engine()
        return await escalation_engine.escalate_to_json(directive_key, context, reason)
    
    async def escalate_to_markdown(self, directive_key: str, context: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Escalate directive to markdown level (preserve existing API)."""
        escalation_engine = self._get_escalation_engine()
        return await escalation_engine.escalate_to_markdown(directive_key, context, reason)
    
    def get_available_directives(self) -> List[str]:
        """Get list of available directives (preserve existing API)."""
        if not self.compressed_directives:
            return []
        return list(self.compressed_directives.keys())
    
    def is_directive_available(self, directive_key: str) -> bool:
        """Check if directive is available (preserve existing API)."""
        return directive_key in self.get_available_directives()
    
    async def shutdown(self):
        """Graceful shutdown (preserve existing API)."""
        logger.info("DirectiveProcessor shutting down")
        
        # Stop event processor if running (legacy support)
        if self._processing_events and self._event_processor_task:
            try:
                await asyncio.wait_for(self._event_processor_task, timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning("Event processor timeout - forcing stop")
                self._event_processor_task.cancel()
        
        # Shutdown modular components if they exist
        if self._consultation_manager:
            await self._consultation_manager.shutdown()
        
        logger.info("DirectiveProcessor shutdown complete")
    
    # =================================================================
    # LAZY LOADING FOR MODULAR COMPONENTS
    # =================================================================
    
    def _get_action_determiner(self):
        """Lazy load ActionDeterminer module."""
        if self._action_determiner is None:
            from .directive_modules.action_determiner import ActionDeterminer
            self._action_determiner = ActionDeterminer()
        return self._action_determiner
    
    def _get_escalation_engine(self):
        """Lazy load EscalationEngine module.""" 
        if self._escalation_engine is None:
            from .directive_modules.escalation_engine import EscalationEngine
            self._escalation_engine = EscalationEngine()
            # Set dependencies needed by escalation engine
            self._escalation_engine.set_dependencies(
                compressed_directives=self.compressed_directives,
                action_executor=self.action_executor,
                action_determiner=self._get_action_determiner()
            )
        return self._escalation_engine
    
    def _get_skeleton_manager(self):
        """Lazy load SkeletonManager module."""
        if self._skeleton_manager is None:
            from .directive_modules.skeleton_manager import SkeletonManager
            self._skeleton_manager = SkeletonManager()
        return self._skeleton_manager
    
    def _get_consultation_manager(self):
        """Lazy load ConsultationManager module."""
        if self._consultation_manager is None:
            from .directive_modules.consultation_manager import ConsultationManager
            self._consultation_manager = ConsultationManager()
        return self._consultation_manager
    
    def _get_state_manager(self):
        """Lazy load StateManager module."""
        if self._state_manager is None:
            from .directive_modules.state_manager import StateManager
            self._state_manager = StateManager()
        return self._state_manager
    
    # =================================================================
    # NEW METHODS FOR PAUSE/RESUME ARCHITECTURE (To be implemented)
    # =================================================================
    
    async def create_project_skeleton(self, project_path: str, mgmt_folder_name: str) -> Dict[str, Any]:
        """Create database-first project skeleton (NEW - for recursion fix)."""
        skeleton_manager = self._get_skeleton_manager()
        return await skeleton_manager.ensure_skeleton_exists(project_path, mgmt_folder_name)
    
    async def start_ai_consultation(self, directive_type: str, context: Dict[str, Any]) -> str:
        """Start AI consultation session (NEW - for recursion fix)."""
        consultation_manager = self._get_consultation_manager()
        return await consultation_manager.start_consultation(directive_type, context)
    
    async def resume_directive(self, resume_token: str) -> Dict[str, Any]:
        """Resume directive from token (NEW - for recursion fix)."""
        state_manager = self._get_state_manager()
        return await state_manager.resume_from_token(resume_token)


# =================================================================
# UTILITY FUNCTION - PRESERVE EXISTING CREATION PATTERN
# =================================================================

def create_directive_processor(action_executor=None) -> DirectiveProcessor:
    """
    Create a properly configured DirectiveProcessor instance.
    
    PRESERVED FUNCTION: This maintains exact same signature and behavior
    to ensure existing code continues working.
    """
    processor = DirectiveProcessor(action_executor=action_executor)
    
    if not processor.compressed_directives:
        logger.warning("DirectiveProcessor created but no directives loaded")
    
    return processor


# =================================================================
# LEGACY SUPPORT - PRESERVE EXISTING DECORATOR IMPORTS
# =================================================================

# Import decorators to maintain existing imports
try:
    from .directive_modules.decorators import (
        on_conversation_to_action,
        on_file_edit_complete,
        on_task_completion
    )
except ImportError:
    # Fallback until modules are implemented
    logger.warning("Decorator modules not yet implemented - using placeholder functions")
    
    def on_conversation_to_action(directive_processor):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                # TODO: Queue event when module is ready
                return result
            return wrapper
        return decorator
    
    def on_file_edit_complete(directive_processor):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                # TODO: Queue event when module is ready
                return result
            return wrapper
        return decorator
    
    def on_task_completion(directive_processor):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                # TODO: Queue event when module is ready
                return result
            return wrapper
        return decorator


if __name__ == "__main__":
    # Test basic functionality (preserve existing test)
    async def test_directive_processor():
        processor = create_directive_processor()
        
        # Test available directives
        directives = processor.get_available_directives()
        print(f"Available directives: {directives}")
        
        # Test basic directive execution
        if directives:
            test_directive = directives[0]
            result = await processor.execute_directive(test_directive, {"test": True})
            print(f"Test result: {result}")
    
    # Run test
    asyncio.run(test_directive_processor())