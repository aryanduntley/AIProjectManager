"""
Action Determination Module for DirectiveProcessor.

Extracted from OLD_directive_processor.py _ai_determine_actions() method.
Handles AI analysis of directive content to determine appropriate actions.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ActionDeterminer:
    """
    Handles action determination logic for directives.
    
    Extracted the complete _ai_determine_actions() logic (238 lines) from 
    OLD_directive_processor.py into a focused, testable module.
    """
    
    def __init__(self):
        """Initialize the action determiner."""
        logger.info("ActionDeterminer initialized")
    
    async def determine_actions(
        self, 
        directive_key: str, 
        context: Dict[str, Any], 
        compressed_directives: Dict[str, Any],
        directive_content: Any = None,
        tier: int = 1
    ) -> Dict[str, Any]:
        """
        Determine actions needed for a directive.
        
        EXTRACTED from OLD_directive_processor.py _ai_determine_actions() method.
        Contains the complete AI analysis logic for determining appropriate actions
        based on directive guidance and context.
        
        Args:
            directive_key: The directive to process
            context: Execution context
            compressed_directives: Loaded directive definitions
            directive_content: Content of the directive (if escalated)
            tier: Escalation tier (1=compressed, 2=json, 3=markdown)
            
        Returns:
            Dictionary with determined actions and analysis
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