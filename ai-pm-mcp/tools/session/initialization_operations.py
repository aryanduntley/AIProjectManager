"""
Initialization operations for session management.

Handles initialization status checking, summaries, and reset operations.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ...database.session_queries import SessionQueries
from ...database.file_metadata_queries import FileMetadataQueries
from ...utils.project_paths import get_project_management_path

logger = logging.getLogger(__name__)


class InitializationOperations:
    """Initialization management operations."""
    
    def __init__(self, session_queries: Optional[SessionQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None):
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries

    async def check_initialization_status(self, session_id: str) -> str:
        """Check file metadata initialization status and provide user feedback."""
        try:
            if not self.session_queries or not self.file_metadata_queries:
                return " (Initialization check skipped - database not available)"
            
            # Get initialization status
            status = self.session_queries.get_initialization_status()
            
            if not status:
                return " (No initialization history found)"
            
            phase = status.get('initialization_phase', 'unknown')
            
            if phase == 'complete':
                return " (File metadata initialization complete)"
            elif phase == 'failed':
                return " (⚠️ Previous initialization failed - use resume_initialization to retry)"
            elif phase in ['not_started', 'discovering_files', 'analyzing_themes', 'building_flows']:
                files_processed = status.get('files_processed', 0)
                total_files = status.get('total_files_discovered', 0)
                
                if total_files > 0:
                    percentage = (files_processed / total_files) * 100
                    return f" (🔄 Initialization {percentage:.1f}% complete - use resume_initialization to continue)"
                else:
                    return " (🔄 Initialization in progress - use resume_initialization to continue)"
            else:
                return f" (Unknown initialization phase: {phase})"
                
        except Exception as e:
            logger.error(f"Error checking initialization status: {e}")
            return " (Error checking initialization status)"

    async def get_initialization_summary(self, arguments: Dict[str, Any]) -> str:
        """Get detailed summary of file metadata initialization progress."""
        try:
            project_path = arguments["project_path"]
            
            if not self.session_queries or not self.file_metadata_queries:
                return "Database not available. Initialization tracking requires database connection."
            
            # Get current status
            status = self.session_queries.get_initialization_status()
            
            if not status:
                return "No initialization sessions found. Run project initialization first."
            
            # Get detailed progress
            progress = self.file_metadata_queries.get_initialization_progress()
            
            # Format comprehensive summary
            summary = f"""📋 **File Metadata Initialization Summary**

**Session Information:**
- Session ID: {status['session_id']}
- Project Path: {status.get('project_path', 'Unknown')}
- Started: {status.get('initialization_started_at', 'Unknown')}
- Status: {status['initialization_phase']}

**Progress Details:**
- Phase: {status['initialization_phase']}
- Files Processed: {status['files_processed']}/{status['total_files_discovered']}
- Completion: {progress['completion_percentage']:.1f}%
- Remaining: {progress['remaining_files']} files

**Performance:**
- Analysis Rate: {progress.get('analysis_rate', 'Calculating...')} files/min
- Estimated Completion: {progress.get('estimated_completion', 'Unknown')}

**Next Steps:**
"""
            
            if status['initialization_phase'] == 'complete':
                summary += "✅ Initialization complete! All project files have been analyzed."
            elif status['initialization_phase'] == 'failed':
                summary += "❌ Initialization failed. Use `resume_initialization` to retry."
            else:
                summary += "🔄 Initialization in progress. Use `resume_initialization` to continue."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting initialization summary: {e}")
            return f"Error getting initialization summary: {str(e)}"

    async def reset_initialization(self, arguments: Dict[str, Any]) -> str:
        """Reset file metadata initialization to start fresh."""
        try:
            project_path = arguments["project_path"]
            confirm = arguments.get("confirm", False)
            
            if not confirm:
                return """⚠️ This will reset all file metadata initialization progress and start fresh.

To confirm, call this tool again with: {"project_path": "...", "confirm": true}

This will:
- Clear all existing file metadata
- Reset initialization phase to 'not_started'
- Remove all initialization progress tracking
- Require complete re-analysis of all project files"""
            
            if not self.session_queries or not self.file_metadata_queries:
                return "Database not available. Reset requires database connection."
            
            # Reset initialization in database
            success = self.session_queries.reset_initialization()
            if not success:
                return "Failed to reset initialization in session tracking."
            
            # Clear all file metadata
            cleared_count = self.file_metadata_queries.clear_all_file_metadata()
            
            return f"✅ Initialization reset complete. Cleared {cleared_count} file metadata records. Run project initialization to start fresh analysis."
            
        except Exception as e:
            logger.error(f"Error resetting initialization: {e}")
            return f"Error resetting initialization: {str(e)}"

    def identify_instance_type(self, project_path: Path) -> str:
        """
        Identify if this is a main instance or branch instance based on marker files.
        Returns 'main', 'branch', or 'unknown'
        """
        project_mgmt_dir = get_project_management_path(project_path, None)         
        # Check for main instance marker
        if (project_mgmt_dir / ".mcp-instance-main").exists():
            return "main"
        # Check for branch instance marker
        elif (project_mgmt_dir / ".mcp-instance-branch").exists():
            return "branch"
        else:
            return "unknown"

    def generate_boot_report(self, instance_type: str, git_changes: Optional[Dict],
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
        elif instance_type == "branch":
            report_lines.extend([
                f"🌿 **Branch Instance:** Git change detection handled by main instance",
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
        if instance_type == "branch":
            report_lines.extend([
                f"💡 **Branch Instance Tips:**",
                f"- Focus on your assigned work themes",
                f"- Use theme and task tools for work tracking",
                f"- Coordinate with main instance for organizational changes"
            ])
        else:
            report_lines.extend([
                f"💡 **Main Instance Ready:**",
                f"- Full organizational management available",
                f"- Use `flow_process` for automated theme/task management",
                f"- Monitor progress with session analytics"
            ])
        
        return "\n".join(report_lines)