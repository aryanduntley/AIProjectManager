"""
Git integration operations for session management.

Handles Git-aware session booting with change detection and reconciliation.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ...core.git_integration import GitIntegrationManager
from ...database.session_queries import SessionQueries
from ...database.git_queries import GitQueries

logger = logging.getLogger(__name__)


class GitIntegration:
    """Git integration for session management."""
    
    def __init__(self, session_queries: Optional[SessionQueries] = None,
                 git_queries: Optional[GitQueries] = None,
                 db_manager=None):
        self.session_queries = session_queries
        self.git_queries = git_queries
        self.db_manager = db_manager

    async def boot_session_with_git_detection(self, arguments: Dict[str, Any]) -> str:
        """
        Enhanced session boot with Git change detection and organizational reconciliation.
        This implements the enhanced boot sequence from the unified Git implementation plan.
        """
        try:
            project_path = Path(arguments["project_path"])
            context_mode = arguments.get("context_mode", "theme-focused")
            force_git_check = arguments.get("force_git_check", False)
            
            if not self.db_manager or not self.git_queries:
                return "Git integration not available. Database and Git queries required."
            
            # Initialize Git integration manager
            git_manager = GitIntegrationManager(project_path, self.db_manager)
            
            # Phase 1: Instance Identification
            instance_type = self._identify_instance_type(project_path)
            
            # Phase 2: Git Change Detection (Main instance only)
            git_changes = None
            if instance_type == "main" or force_git_check:
                git_changes = git_manager.detect_project_code_changes()
                
                if git_changes.get("success") and git_changes.get("changes_detected"):
                    logger.info(f"Git changes detected: {git_changes['change_summary']}")
                else:
                    logger.info("No Git changes detected since last session")
            
            # Phase 3: Organizational Reconciliation (if changes detected)
            reconciliation_result = None
            if git_changes and git_changes.get("reconciliation_needed"):
                reconciliation_result = git_manager.reconcile_organizational_state_with_code(git_changes)
                logger.info(f"Organizational reconciliation: {reconciliation_result.get('message', 'Completed')}")
            
            # Phase 4: Standard Session Boot
            from .core_operations import CoreOperations
            core_ops = CoreOperations(self.session_queries, None)
            session_result = await core_ops.start_work_period({
                "project_path": str(project_path),
                "context_mode": context_mode
            })
            
            # Phase 5: Enhanced Boot Report
            boot_report = self._generate_boot_report(
                instance_type, git_changes, reconciliation_result, session_result
            )
            
            return boot_report
            
        except Exception as e:
            logger.error(f"Error in Git-aware session boot: {e}")
            return f"Error in Git-aware session boot: {str(e)}"

    def _identify_instance_type(self, project_path: Path) -> str:
        """
        Identify if this is a main instance, team member instance, or other.
        
        Main instance criteria:
        - Repository owner/primary developer
        - Has .aipm/config/core-settings.json with main_instance=true
        - Or is on a main development branch pattern
        
        Team member criteria:
        - Working on feature/personal branches
        - Has team member configuration
        """
        try:
            # Check for explicit configuration
            config_file = project_path / ".aipm" / "config" / "core-settings.json"
            if config_file.exists():
                import json
                config = json.loads(config_file.read_text())
                if config.get("main_instance", False):
                    return "main"
                elif config.get("team_member", False):
                    return "team_member"
            
            # Check Git branch patterns
            try:
                import subprocess
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                current_branch = result.stdout.strip()
                
                # Main instance branches
                main_patterns = ["main", "master", "ai-pm-org-main", "develop"]
                if current_branch in main_patterns:
                    return "main"
                
                # Team member branch patterns
                team_patterns = ["feature/", "team/", "personal/", "work/"]
                if any(current_branch.startswith(pattern) for pattern in team_patterns):
                    return "team_member"
                    
            except Exception as e:
                logger.debug(f"Could not determine Git branch: {e}")
                
            # Default to main if uncertain
            return "main"
            
        except Exception as e:
            logger.error(f"Error identifying instance type: {e}")
            return "unknown"

    def _generate_boot_report(self, instance_type: str, git_changes: Optional[Dict],
                            reconciliation_result: Optional[Dict], session_result: str) -> str:
        """Generate comprehensive boot report."""
        
        report_lines = [
            f"🚀 **AI Project Manager Boot Complete**",
            f"",
            f"**Instance Type:** {instance_type.title()}",
            f"**Session Status:** {session_result.split('.')[0] if '.' in session_result else session_result}",
            f""
        ]
        
        # Git Changes Section
        if git_changes:
            if git_changes.get("changes_detected"):
                report_lines.extend([
                    f"📝 **Git Changes Detected:**",
                    f"- Files Changed: {git_changes.get('files_changed', 0)}",
                    f"- Summary: {git_changes.get('change_summary', 'Changes detected')}",
                    f""
                ])
            else:
                report_lines.extend([
                    f"✅ **Git Status:** No changes since last session",
                    f""
                ])
        elif instance_type == "team_member":
            report_lines.extend([
                f"👥 **Team Member Instance:** Git change detection skipped",
                f""
            ])
        
        # Reconciliation Section
        if reconciliation_result:
            if reconciliation_result.get("success"):
                report_lines.extend([
                    f"🔄 **Organizational Reconciliation:** Completed",
                    f"- {reconciliation_result.get('message', 'State synchronized')}",
                    f""
                ])
            else:
                report_lines.extend([
                    f"⚠️ **Reconciliation Warning:** {reconciliation_result.get('error', 'See logs')}",
                    f""
                ])
        
        # Recommendations
        if instance_type == "team_member":
            report_lines.extend([
                f"💡 **Team Member Tips:**",
                f"- Use `session_sync_with_main` periodically to stay up to date",
                f"- Focus on your assigned themes and tasks",
                f"- Coordinate with the main instance for organizational changes"
            ])
        else:
            report_lines.extend([
                f"💡 **Main Instance Ready:**",
                f"- Full organizational management available",
                f"- Use `flow_process` for automated theme/task management",
                f"- Monitor team member progress with session analytics"
            ])
        
        return "\n".join(report_lines)