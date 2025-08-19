"""
Compressed Context Module
Handles compressed context management and core context loading.
Contains the CompressedContextManager class and related data structures.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Import utilities from parent module paths  
from ...utils.project_paths import get_project_management_path

logger = logging.getLogger(__name__)


class ContextMode(Enum):
    """Available context loading modes."""
    THEME_FOCUSED = "theme-focused"
    THEME_EXPANDED = "theme-expanded"
    PROJECT_WIDE = "project-wide"


@dataclass
class ContextResult:
    """Result of context loading operation."""
    mode: ContextMode
    primary_theme: str
    loaded_themes: List[str]
    files: List[str]
    paths: List[str]
    readmes: Dict[str, str]
    shared_files: Dict[str, List[str]]
    recommendations: List[str]
    memory_estimate: int


class CompressedContextManager:
    """Manages compressed context files for optimal AI session continuity."""
    
    def __init__(self, mcp_server_path: Optional[Path] = None):
        """Initialize with MCP server path for core context loading."""
        if mcp_server_path is None:
            # Auto-detect MCP server path relative to this file
            mcp_server_path = Path(__file__).parent.parent
        
        self.mcp_server_path = mcp_server_path
        self.core_context_path = mcp_server_path / "core-context"
        
        # Core context (always loaded)
        self._core_context = {}
        self._loaded = False
    
    async def load_core_context(self) -> Dict[str, Any]:
        """Load compressed core context files."""
        if self._loaded:
            return self._core_context
        
        try:
            # Load all core context files
            core_files = [
                "system-essence.json",
                "workflow-triggers.json", 
                "directive-compressed.json",
                "validation-core.json"
            ]
            
            for filename in core_files:
                file_path = self.core_context_path / filename
                if file_path.exists():
                    context_data = json.loads(file_path.read_text())
                    self._core_context[filename.replace('.json', '')] = context_data
                else:
                    logger.warning(f"Core context file not found: {file_path}")
            
            self._loaded = True
            logger.info(f"Loaded {len(self._core_context)} core context files")
            
        except Exception as e:
            logger.error(f"Error loading core context: {e}")
            raise
        
        return self._core_context
    
    def get_workflow_for_scenario(self, scenario: str) -> Optional[Dict[str, Any]]:
        """Get workflow definition for a specific scenario."""
        if not self._loaded:
            return None
            
        workflow_triggers = self._core_context.get('workflow-triggers', {})
        scenarios = workflow_triggers.get('commonScenarios', {})
        
        return scenarios.get(scenario)
    
    def get_directive_summary(self, directive_key: str) -> Optional[Dict[str, Any]]:
        """Get compressed directive information."""
        if not self._loaded:
            return None
            
        directives = self._core_context.get('directive-compressed', {})
        return directives.get(directive_key)
    
    def get_validation_rules(self, validation_type: str) -> Optional[Dict[str, Any]]:
        """Get validation rules for specific validation type."""
        if not self._loaded:
            return None
            
        validation_core = self._core_context.get('validation-core', {})
        return validation_core.get(validation_type)
    
    def get_session_boot_sequence(self) -> List[str]:
        """Get the session boot sequence steps."""
        if not self._loaded:
            return []
            
        system_essence = self._core_context.get('system-essence', {})
        return system_essence.get('sessionBootSequence', [])
    
    def get_core_rules(self) -> List[str]:
        """Get critical rules for AI behavior."""
        if not self._loaded:
            return []
            
        system_essence = self._core_context.get('system-essence', {})
        return system_essence.get('criticalRules', [])
    
    def should_escalate_context(self, issue_description: str) -> Tuple[bool, str]:
        """Determine if context escalation is needed based on issue."""
        if not self._loaded:
            return False, "Core context not loaded"
        
        workflow_triggers = self._core_context.get('workflow-triggers', {})
        escalation_scenario = workflow_triggers.get('commonScenarios', {}).get('context_escalation_needed')
        
        if not escalation_scenario:
            return False, "No escalation rules found"
        
        # Check if issue contains escalation trigger keywords
        triggers = escalation_scenario.get('triggers', [])
        issue_lower = issue_description.lower()
        
        for trigger in triggers:
            if trigger.lower() in issue_lower:
                return True, f"Issue matches escalation trigger: {trigger}"
        
        return False, "No escalation triggers found in issue"
    
    def _directive_id_to_compressed_key(self, directive_id: str) -> str:
        """Convert numbered directive ID to compressed directive key."""
        # Handle already converted keys
        if not directive_id.startswith(('0', '1', '2')):
            return directive_id
            
        # Remove number prefix and convert to camelCase
        parts = directive_id.split('-', 1)
        if len(parts) == 2:
            name_parts = parts[1].split('-')
            # First part lowercase, rest title case
            camel_case = name_parts[0] + ''.join(word.capitalize() for word in name_parts[1:])
            return camel_case
        
        return directive_id
    
    def _has_implementation_note(self, obj: Any) -> bool:
        """Recursively search for implementationNote in a nested object."""
        if isinstance(obj, dict):
            if 'implementationNote' in obj:
                return True
            for value in obj.values():
                if self._has_implementation_note(value):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if self._has_implementation_note(item):
                    return True
        return False
    
    def get_directive_escalation_level(self, directive_id: str, operation_context: str = "") -> str:
        """Determine appropriate directive escalation level based on new escalation logic."""
        if not self._loaded:
            return "compressed"  # Default fallback
        
        # Get escalation rules from compressed directives
        directive_escalation = self._core_context.get('directive-compressed', {}).get('directiveEscalation', {})
        escalation_protocol = directive_escalation.get('escalationProtocol', {})
        
        # Check for forced JSON operations
        forced_json_ops = escalation_protocol.get('forcedJSONOperations', [])
        if directive_id in forced_json_ops:
            logger.info(f"Forcing JSON escalation for {directive_id} (complex system operation)")
            return "json"
        
        # Check for implementationNote in compressed directive (search recursively)
        compressed_key = self._directive_id_to_compressed_key(directive_id)
        compressed_directive = self.get_directive_summary(compressed_key)
        if compressed_directive and self._has_implementation_note(compressed_directive):
            logger.info(f"Auto-escalating {directive_id} to JSON (implementationNote present)")
            return "json"
        
        # Check escalation triggers
        when_to_escalate = directive_escalation.get('whenToEscalate', {})
        
        # Check for force JSON triggers
        force_json = when_to_escalate.get('forceJSON', [])
        auto_json = when_to_escalate.get('autoJSON', [])
        
        operation_lower = operation_context.lower()
        
        for trigger in force_json + auto_json:
            if trigger.lower() in operation_lower:
                logger.info(f"Auto-escalating {directive_id} to JSON (trigger: {trigger})")
                return "json"
        
        # Default to compressed for routine operations
        logger.debug(f"Using compressed directives for {directive_id} (routine operation)")
        return "compressed"
    
    def should_escalate_to_markdown(self, directive_id: str, json_context_insufficient: bool = False, 
                                   error_context: str = "") -> bool:
        """Determine if should escalate from JSON to Markdown directives."""
        if not self._loaded:
            return False
        
        # Always escalate if JSON context is insufficient
        if json_context_insufficient:
            logger.info(f"Escalating {directive_id} to MD (JSON context insufficient)")
            return True
        
        # Check escalation triggers
        directive_escalation = self._core_context.get('directive-compressed', {}).get('directiveEscalation', {})
        when_to_escalate = directive_escalation.get('whenToEscalate', {})
        auto_md = when_to_escalate.get('autoMD', [])
        
        error_lower = error_context.lower()
        
        for trigger in auto_md:
            if trigger.lower() in error_lower:
                logger.info(f"Auto-escalating {directive_id} to MD (trigger: {trigger})")
                return True
        
        return False
    
    async def load_directive_with_escalation(self, directive_id: str, operation_context: str = "", 
                                           force_level: Optional[str] = None) -> Dict[str, Any]:
        """Load directive with appropriate escalation level."""
        try:
            # Determine escalation level
            if force_level:
                escalation_level = force_level
                logger.info(f"Using forced escalation level {force_level} for {directive_id}")
            else:
                escalation_level = self.get_directive_escalation_level(directive_id, operation_context)
            
            directive_content = {}
            
            # Always start with compressed (for context preservation)
            compressed = self.get_directive_summary(directive_id)
            if compressed:
                directive_content['compressed'] = compressed
            
            # Load JSON if needed
            if escalation_level in ['json', 'markdown']:
                json_path = self.mcp_server_path / "reference" / "directives" / f"{directive_id}.json"
                if json_path.exists():
                    json_content = json.loads(json_path.read_text())
                    directive_content['json'] = json_content
                    logger.debug(f"Loaded JSON directive for {directive_id}")
                else:
                    logger.warning(f"JSON directive not found: {json_path}")
            
            # Load Markdown if needed
            if escalation_level == 'markdown':
                md_path = self.mcp_server_path / "reference" / "directivesmd" / f"{directive_id}.md"
                if md_path.exists():
                    md_content = md_path.read_text()
                    directive_content['markdown'] = md_content
                    logger.debug(f"Loaded MD directive for {directive_id}")
                else:
                    logger.warning(f"MD directive not found: {md_path}")
            
            directive_content['escalation_level'] = escalation_level
            directive_content['escalation_reason'] = f"Auto-escalated based on {operation_context}" if operation_context else "Default level"
            
            return directive_content
            
        except Exception as e:
            logger.error(f"Error loading directive {directive_id}: {e}")
            return {"error": str(e), "escalation_level": "compressed"}
    
    async def generate_situational_context(self, project_path: Path, situation: str) -> Dict[str, Any]:
        """Generate context specific to current project situation."""
        try:
            # Load project state
            project_state = await self._analyze_project_state(project_path)
            
            # Get workflow for situation
            workflow = self.get_workflow_for_scenario(situation)
            if not workflow:
                return {"error": f"No workflow found for situation: {situation}"}
            
            # Generate contextual response
            context = {
                "situation": situation,
                "workflow": workflow,
                "projectState": project_state,
                "requiredFiles": workflow.get('requiredFiles', []),
                "actions": workflow.get('actions', []),
                "contextMode": workflow.get('contextMode', 'theme-focused'),
                "priority": workflow.get('priority', 'medium')
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error generating situational context: {e}")
            return {"error": str(e)}
    
    async def _analyze_project_state(self, project_path: Path) -> Dict[str, Any]:
        """Analyze current project state for context generation."""
        state = {
            "hasProjectManagement": False,
            "hasActiveImplementationPlan": False,
            "hasActiveTasks": False,
            "themesCount": 0,
            "milestonesCount": 0
        }
        
        try:
            pm_path = get_project_management_path(project_path, self.config_manager)
            if pm_path.exists():
                state["hasProjectManagement"] = True
                
                # Check for active implementation plan
                impl_active = pm_path / "Implementations" / "active"
                if impl_active.exists():
                    active_plans = list(impl_active.glob("*.md"))
                    state["hasActiveImplementationPlan"] = len(active_plans) > 0
                
                # Check for active tasks
                tasks_active = pm_path / "Tasks" / "active"
                if tasks_active.exists():
                    active_tasks = list(tasks_active.glob("TASK-*.json"))
                    state["hasActiveTasks"] = len(active_tasks) > 0
                
                # Count themes
                themes_dir = pm_path / "Themes"
                if themes_dir.exists():
                    theme_files = list(themes_dir.glob("*.json"))
                    # Exclude themes.json index file
                    state["themesCount"] = len([f for f in theme_files if f.name != "themes.json"])
                
                # Count milestones
                completion_path = pm_path / "Tasks" / "completion-path.json"
                if completion_path.exists():
                    try:
                        cp_data = json.loads(completion_path.read_text())
                        state["milestonesCount"] = len(cp_data.get('milestones', []))
                    except:
                        pass
        
        except Exception as e:
            logger.debug(f"Error analyzing project state: {e}")
        
        return state
