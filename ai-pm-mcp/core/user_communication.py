#!/usr/bin/env python3
"""
User Communication Service

Centralizes all user communication to ensure proper MCP protocol compliance.
All user messages must go through MCP tool responses, never stderr/stdout.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class UserCommunicationService:
    """Centralized service for user communication via MCP protocol."""
    
    def format_state_analysis(self, state: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Format project state analysis for user presentation."""
        project_path = details.get("project_path", "unknown")
        
        base_response = {
            "type": "state_analysis",
            "state": state,
            "project_path": str(project_path),
            "details": details
        }
        
        if state == "git_history_found":
            return self._format_git_history_analysis(base_response, details)
        elif state == "no_structure":
            return self._format_no_structure_analysis(base_response, details)
        elif state == "complete":
            return self._format_complete_project_analysis(base_response, details)
        elif state == "partial":
            return self._format_partial_project_analysis(base_response, details)
        elif state == "incomplete":
            return self._format_incomplete_project_analysis(base_response, details)
        elif state == "unknown":
            return self._format_unknown_state_analysis(base_response, details)
        else:
            return base_response
    
    def _format_git_history_analysis(self, base: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        """Format Git history found analysis."""
        git_analysis = details.get("git_analysis", {})
        current_branch = git_analysis.get("current_branch", "unknown")
        current_branch_type = git_analysis.get("current_branch_type", "unknown")
        ai_main_exists = git_analysis.get("ai_main_exists", False)
        ai_instance_branches = git_analysis.get("ai_instance_branches", [])
        remote_ai_branches = git_analysis.get("remote_ai_branches", [])
        is_team_member = git_analysis.get("is_team_member", False)
        
        # Build branch information
        branch_list = []
        if ai_main_exists:
            marker = " (current)" if current_branch == "ai-pm-org-main" else ""
            branch_list.append(f"• ai-pm-org-main{marker} - Canonical AI organizational state")
        
        if ai_instance_branches:
            branch_list.append("\n**AI Instance Branches (Team Members):**")
            for branch in ai_instance_branches:
                marker = " (current)" if branch == current_branch else ""
                branch_list.append(f"• {branch}{marker}")
        
        if remote_ai_branches:
            branch_list.append("\n**Remote AI Branches:**")
            for branch in remote_ai_branches:
                branch_list.append(f"• {branch}")
        
        # Determine user scenario and recommendations
        scenario_info, recommendations = self._get_git_scenario_recommendations(
            current_branch_type, is_team_member
        )
        
        message = f"""=== AI Project Manager - Session Boot ===
📍 Project Directory: {base['project_path']}
🔍 AI project management history detected in Git branches!

**AI Branches Found:**
{chr(10).join(branch_list)}

📊 **Current Status:**
• Working Directory: No projectManagement/ structure  
• Git Repository: ✅ Available
• Current Branch: {current_branch} ({current_branch_type})
• AI Project History: ✅ Found in Git branches
• Team Member: {"✅ Yes" if is_team_member else "❌ No"}

{scenario_info}

🎯 **Recommended Next Steps:**
{chr(10).join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)])}

4. **Analyze History**: Use 'get_branch_status' to understand branch contents

ℹ️  Choose your approach based on your role and collaboration needs."""
        
        base.update({
            "message": message,
            "recommendations": recommendations,
            "scenario": current_branch_type,
            "is_team_member": is_team_member,
            "requires_user_choice": True
        })
        
        return base
    
    def _format_no_structure_analysis(self, base: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        """Format no project structure analysis."""
        message = f"""=== AI Project Manager - Session Boot ===
📍 Project Directory: {base['project_path']}
⚠️  No project management structure found.

🎯 **Next Steps Available:**
1. Initialize new project: Use 'project_initialize' tool
2. Review project status: Use 'project_get_status' tool  
3. Check for existing code: Use 'check_user_code_changes' tool

ℹ️  The AI Project Manager is ready to help you set up project management for this directory."""
        
        base.update({
            "message": message,
            "recommendations": ["initialize_project", "get_project_status", "check_existing_code"],
            "requires_user_choice": True
        })
        
        return base
    
    def _format_complete_project_analysis(self, base: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        """Format complete project analysis."""
        existing = details.get("existing", {})
        active_tasks = details.get("active_tasks", 0)
        sidequests = details.get("sidequests", 0)
        auto_task_enabled = details.get("auto_task_enabled", False)
        git_analysis = details.get("git_analysis", {})
        
        # Git branch info
        git_info = ""
        if git_analysis.get("is_git_repo"):
            current_branch = git_analysis.get("current_branch", "unknown")
            current_branch_type = git_analysis.get("current_branch_type", "unknown")
            is_team_member = git_analysis.get("is_team_member", False)
            git_info = f"• Git Branch: {current_branch} ({current_branch_type})\n"
            git_info += f"• Team Member: {'✅ Yes' if is_team_member else '❌ No'}\n"
        
        # Auto-task logic
        action_message = ""
        if auto_task_enabled and active_tasks == 0:
            action_message = "\n🚀 **Auto-task enabled**: Use 'session_boot_with_git_detection' to automatically continue work."
        elif auto_task_enabled and active_tasks > 0:
            action_message = "\n🚀 **Auto-task enabled**: Use 'session_boot_with_git_detection' to resume existing tasks."
        else:
            action_message = "\n🎯 **Manual mode**: Choose your next action from the options below."
        
        message = f"""=== AI Project Manager - Session Boot ===
📍 Project Directory: {base['project_path']}
✅ Complete project management structure found.

📊 **Project Status:**
• Blueprint: ✅ Available
• Themes: ✅ Available  
• Flows: ✅ Available
• Database: ✅ Available
{git_info}• Active Tasks: {active_tasks}
• Sidequests: {sidequests}
• Auto-task: {"✅ Enabled" if auto_task_enabled else "❌ Disabled"}{action_message}

🎯 **Available Actions:**
• 'session_boot_with_git_detection' - Enhanced session boot with Git integration
• 'project_get_status' - Detailed project information  
• 'session_start' - Begin/resume work session
• 'task_list_active' - See current tasks

ℹ️  Project is ready for continued development."""
        
        base.update({
            "message": message,
            "recommendations": ["session_boot_with_git_detection", "project_get_status", "session_start", "task_list_active"],
            "auto_task_enabled": auto_task_enabled,
            "requires_user_choice": not auto_task_enabled  # Auto-continue if enabled
        })
        
        return base
    
    def _format_partial_project_analysis(self, base: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        """Format partial project analysis."""
        existing = details.get("existing", {})
        missing = details.get("missing", {})
        active_tasks = details.get("active_tasks", 0)
        sidequests = details.get("sidequests", 0)
        git_analysis = details.get("git_analysis", {})
        
        existing_list = "• " + "\n• ".join([f"{name}: ✅" for name in existing.keys()])
        missing_list = "• " + "\n• ".join([f"{name}: ❌" for name in missing.keys()])
        
        # Git branch info
        git_info = ""
        if git_analysis.get("is_git_repo"):
            current_branch = git_analysis.get("current_branch", "unknown")
            current_branch_type = git_analysis.get("current_branch_type", "unknown")
            is_team_member = git_analysis.get("is_team_member", False)
            git_info = f"• Git Branch: {current_branch} ({current_branch_type})\n"
            git_info += f"• Team Member: {'✅ Yes' if is_team_member else '❌ No'}\n"
        
        message = f"""=== AI Project Manager - Session Boot ===
📍 Project Directory: {base['project_path']}
⚠️  Partial project management structure found.

📊 **Current Status:**
{existing_list}
{missing_list}
{git_info}• Active Tasks: {active_tasks}
• Sidequests: {sidequests}

🎯 **Next Steps Available:**
1. **Complete initialization**: Use 'project_initialize' with force=true
2. **Review current state**: Use 'project_get_status' tool
3. **Restore missing components**: Initialize individual components
4. **Continue with existing**: Use 'session_start' tool
5. **Git integration**: Use 'session_boot_with_git_detection' for enhanced boot

ℹ️  Project can be completed or continued with partial state."""
        
        base.update({
            "message": message,
            "recommendations": ["complete_initialization", "review_state", "restore_components", "continue_existing", "git_integration"],
            "existing_components": list(existing.keys()),
            "missing_components": list(missing.keys()),
            "requires_user_choice": True
        })
        
        return base
    
    def _format_incomplete_project_analysis(self, base: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        """Format incomplete project analysis."""
        existing = details.get("existing", {})
        git_analysis = details.get("git_analysis", {})
        
        existing_list = "• " + "\n• ".join([f"{name}: ✅" for name in existing.keys()]) if existing else "• None"
        
        # Git branch info
        git_info = ""
        if git_analysis.get("is_git_repo"):
            current_branch = git_analysis.get("current_branch", "unknown")
            current_branch_type = git_analysis.get("current_branch_type", "unknown")
            is_team_member = git_analysis.get("is_team_member", False)
            git_info = f"• Git Branch: {current_branch} ({current_branch_type})\n"
            git_info += f"• Team Member: {'✅ Yes' if is_team_member else '❌ No'}\n"
        
        message = f"""=== AI Project Manager - Session Boot ===
📍 Project Directory: {base['project_path']}
⚠️  Incomplete project management structure found.

📊 **Found Components:**
{existing_list}
{git_info}
🎯 **Recommended Next Steps:**
1. **Initialize Project**: Use 'project_initialize' tool to set up complete structure
2. **Check Status**: Use 'project_get_status' for detailed analysis
3. **Review Existing**: Check what can be preserved before reinitializing
4. **Git Integration**: Use 'session_boot_with_git_detection' if you have Git history

ℹ️  Project needs initialization to enable full AI project management."""
        
        base.update({
            "message": message,
            "recommendations": ["initialize_project", "check_status", "review_existing", "git_integration"],
            "existing_components": list(existing.keys()) if existing else [],
            "requires_user_choice": True
        })
        
        return base
    
    def _format_unknown_state_analysis(self, base: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        """Format unknown state analysis."""
        message = f"""=== AI Project Manager - Session Boot ===
📍 Project Directory: {base['project_path']}
❓ Could not determine project management state.

🎯 **Available Actions:**
• Use 'project_get_status' to analyze current state
• Use 'project_initialize' to set up project management
• Check server logs for detailed error information

ℹ️  Manual project analysis recommended."""
        
        base.update({
            "message": message,
            "recommendations": ["project_get_status", "project_initialize", "check_logs"],
            "requires_user_choice": True
        })
        
        return base
    
    def _get_git_scenario_recommendations(self, current_branch_type: str, is_team_member: bool) -> tuple:
        """Get scenario info and recommendations based on Git state."""
        if current_branch_type == "user_main":
            if is_team_member:
                scenario_info = "🏢 **Team Member Scenario**: You're on the user main branch with existing AI history."
                recommendations = [
                    "**Join Team**: Use 'switch_to_branch ai-pm-org-main' to access shared AI state",
                    "**Create Work Branch**: Use 'create_instance_branch' for your own AI work space",
                    "**Fresh Start**: Use 'project_initialize' to start independent AI management"
                ]
            else:
                scenario_info = "👤 **Project Owner**: You have AI history but are on the user main branch."
                recommendations = [
                    "**Resume AI Work**: Use 'switch_to_branch ai-pm-org-main' to continue AI management",
                    "**Create Instance**: Use 'create_instance_branch' for parallel AI work",
                    "**Fresh Start**: Use 'project_initialize' to restart AI management"
                ]
        elif current_branch_type == "ai_main":
            scenario_info = "🎯 **On AI Main Branch**: You're on the canonical AI organizational branch."
            recommendations = [
                "**Continue Work**: Use 'session_boot_with_git_detection' to resume AI management",
                "**Create Instance**: Use 'create_instance_branch' for experimental work"
            ]
        elif current_branch_type == "ai_instance":
            scenario_info = "🔧 **On AI Instance Branch**: You're on an AI work branch."
            recommendations = [
                "**Continue Instance Work**: Use 'session_boot_with_git_detection' to resume work",
                "**Switch to Main**: Use 'switch_to_branch ai-pm-org-main' to access main AI state",
                "**Merge Changes**: Use 'merge_instance_branch' to integrate your work"
            ]
        else:
            scenario_info = f"📍 **Unknown Branch Type**: You're on branch with type '{current_branch_type}'."
            recommendations = [
                "**Analyze Current State**: Use 'get_branch_status' to understand current situation",
                "**Switch to AI Main**: Use 'switch_to_branch ai-pm-org-main' to access AI management",
                "**Fresh Start**: Use 'project_initialize' to start new AI management"
            ]
        
        return scenario_info, recommendations
    
    def format_options_presentation(self, options: List[Dict[str, str]]) -> Dict[str, Any]:
        """Format options for user choice."""
        return {
            "type": "user_options",
            "options": options,
            "requires_user_choice": True
        }
    
    def create_user_choice_prompt(self, scenario: str, options: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create a user choice prompt."""
        return {
            "type": "user_choice_prompt",
            "scenario": scenario,
            "options": options,
            "requires_user_choice": True
        }
    
    def format_status_update(self, message: str, level: str = "info") -> Dict[str, Any]:
        """Format a status update message."""
        return {
            "type": "status_update",
            "level": level,
            "message": message,
            "requires_user_choice": False
        }
    
    def format_as_json_response(self, data: Dict[str, Any]) -> str:
        """Format data as JSON response for MCP tools."""
        return json.dumps(data, indent=2, ensure_ascii=False)