"""
Escalation Engine Module for DirectiveProcessor.

Extracted from OLD_directive_processor.py escalation methods.
Handles escalation from compressed -> JSON -> Markdown directive levels.
"""

import json
import re
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class EscalationEngine:
    """
    Handles directive escalation logic.
    
    EXTRACTED complete escalation_directive() and escalate_to_markdown() methods
    from OLD_directive_processor.py (~120 lines) into a focused module.
    """
    
    def __init__(self):
        """Initialize the escalation engine."""
        self.compressed_directives = {}
        self.action_executor = None
        self.action_determiner = None
        logger.info("EscalationEngine initialized")
    
    def set_dependencies(self, compressed_directives: Dict[str, Any], action_executor=None, action_determiner=None):
        """Set dependencies needed for escalation processing."""
        self.compressed_directives = compressed_directives
        self.action_executor = action_executor
        self.action_determiner = action_determiner
    
    async def escalate_to_json(self, directive_key: str, context: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """
        Escalate to JSON or MD directive files when compressed insufficient.
        
        EXTRACTED from OLD_directive_processor.py escalate_directive() method.
        Implements the 3-tier escalation system: compressed -> JSON -> MD
        
        Args:
            directive_key: The directive to escalate
            context: Execution context
            reason: Reason for escalation
            
        Returns:
            Dictionary with escalation results
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
            match = re.search(r'reference/directives/([^.]+)\.json', implementation_note)
            if match:
                actual_directive_name = match.group(1)
                logger.info(f"[DEBUG_DIRECTIVE] Extracted directive name from implementationNote: {actual_directive_name}")
        
        # Try JSON first (Tier 2)
        json_path = Path(__file__).parent.parent.parent / "reference" / "directives" / f"{actual_directive_name}.json"
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_content = json.load(f)
                
                logger.info(f"Escalated to JSON directive: {directive_key}")
                
                # AI analyzes detailed JSON directive + context
                if self.action_determiner:
                    actions = await self.action_determiner.determine_actions(
                        directive_key, context, self.compressed_directives,
                        directive_content=json_content, tier=2
                    )
                else:
                    logger.warning("No action_determiner available for JSON escalation")
                    actions = {"actions": [], "analysis": "No action determiner available", "needs_escalation": False}
                
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
        """
        Final escalation to Markdown directive files.
        
        EXTRACTED from OLD_directive_processor.py escalate_to_markdown() method.
        This is the final tier of the escalation system.
        
        Args:
            directive_key: The directive to escalate
            context: Execution context  
            reason: Reason for escalation
            
        Returns:
            Dictionary with escalation results
        """
        logger.info(f"[DEBUG_DIRECTIVE] Final escalation to MD for directive {directive_key}")
        
        # Check if directive has implementationNote with specific file path (same logic as JSON escalation)
        directive_content = self.compressed_directives.get(directive_key, {})
        implementation_note = directive_content.get("implementationNote", "")
        
        # Extract file path from implementationNote if available
        actual_directive_name = directive_key  # default fallback
        if implementation_note and "reference/directives/" in implementation_note:
            match = re.search(r'reference/directives/([^.]+)\.json', implementation_note)
            if match:
                actual_directive_name = match.group(1)
                logger.info(f"[DEBUG_DIRECTIVE] Using directive name for MD: {actual_directive_name}")
        
        md_path = Path(__file__).parent.parent.parent / "reference" / "directivesmd" / f"{actual_directive_name}.md"
        if md_path.exists():
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                logger.info(f"Escalated to MD directive: {directive_key}")
                
                # AI analyzes comprehensive Markdown directive + context  
                if self.action_determiner:
                    actions = await self.action_determiner.determine_actions(
                        directive_key, context, self.compressed_directives,
                        directive_content=md_content, tier=3
                    )
                else:
                    logger.warning("No action_determiner available for MD escalation")
                    actions = {"actions": [], "analysis": "No action determiner available", "needs_escalation": False}
                
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