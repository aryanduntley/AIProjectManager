#!/usr/bin/env python3
"""
AI Project Manager MCP Server

A Model Context Protocol server that provides AI-driven project management
capabilities including persistent context management, theme-based organization,
and seamless session continuity.
"""

import asyncio
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Add deps directory to Python path for project-specific dependencies
deps_path = Path(__file__).parent / "deps"
if deps_path.exists():
    sys.path.insert(0, str(deps_path))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .core.config_manager import ConfigManager
from .core.mcp_api import MCPToolRegistry


# Configure enhanced debugging logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Log startup info for debugging
logger.info(f"Starting AI Project Manager MCP Server")
logger.info(f"Python path: {sys.path}")
logger.info(f"Server file location: {__file__}")
logger.info(f"Working directory: {Path.cwd()}")


class AIProjectManagerServer:
    """Main MCP server for AI project management."""
    
    def __init__(self):
        self.server = Server("ai-project-manager")
        self.config_manager = ConfigManager()
        self.tool_registry = MCPToolRegistry(self.config_manager)
        
    async def initialize(self):
        """Initialize the server and register tools."""
        try:
            logger.debug("Starting server initialization")
            
            # Load configuration
            logger.debug("Loading configuration")
            await self.config_manager.load_config()
            logger.debug("Configuration loaded successfully")
            
            # Register all tools
            logger.debug("Registering tools")
            await self.tool_registry.register_all_tools(self.server)
            logger.debug("Tools registered successfully")
            
            # Perform automatic session boot sequence
            logger.debug("Starting automatic session boot sequence")
            await self.perform_session_boot()
            
            logger.info("AI Project Manager MCP Server initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}", exc_info=True)
            raise
    
    async def perform_session_boot(self):
        """Perform automatic session boot sequence using MCP tools."""
        try:
            project_path = Path.cwd()
            logger.info(f"Performing session boot for project at: {project_path}")
            
            # Check for projectManagement structure
            project_mgmt_dir = project_path / "projectManagement"
            
            # Check for Git repository and AI branches
            git_analysis = await self.analyze_git_project_state(project_path)
            
            # Execute appropriate MCP tool based on analysis
            if not project_mgmt_dir.exists():
                # No project structure found - check for Git branch history
                if git_analysis.get("has_ai_branches"):
                    await self.execute_git_history_recovery(project_path, git_analysis)
                else:
                    await self.execute_project_initialization(project_path)
            else:
                # Project structure exists - check completeness and boot session
                await self.execute_existing_project_boot(project_path, project_mgmt_dir, git_analysis)
                
        except Exception as e:
            logger.error(f"Error during session boot: {e}")
            # Continue anyway - don't block server startup
    
    async def execute_git_history_recovery(self, project_path: Path, git_analysis: dict):
        """Execute MCP tools for Git history recovery scenario."""
        try:
            from .tools.session_manager import SessionManager
            session_manager = SessionManager(db_manager=None)
            
            # Execute session boot with git detection - this will be visible to Claude
            arguments = {
                "project_path": str(project_path),
                "context_mode": "theme-focused", 
                "force_git_check": True
            }
            result = await session_manager.boot_session_with_git_detection(arguments)
            
            logger.info("Git history recovery session boot completed")
            return result
            
        except Exception as e:
            logger.error(f"Error during Git history recovery: {e}")
    
    async def execute_project_initialization(self, project_path: Path):
        """Execute MCP tools for new project initialization."""
        try:
            from .tools.project_tools import ProjectTools
            project_tools = ProjectTools(db_manager=None)
            
            # Check if this looks like a software project
            project_indicators = [
                'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 
                'composer.json', 'pom.xml', 'src/', 'app/', 'lib/', 'README.md'
            ]
            
            has_indicators = any((project_path / indicator).exists() for indicator in project_indicators)
            
            if has_indicators:
                # Auto-determine project name
                project_name = project_path.name
                readme_path = project_path / "README.md"
                if readme_path.exists():
                    try:
                        content = readme_path.read_text(encoding='utf-8')[:1000]
                        for line in content.split('\n'):
                            if line.startswith('# '):
                                project_name = line[2:].strip()
                                break
                    except:
                        pass
                
                # Execute project initialization - this will be visible to Claude
                arguments = {
                    "project_path": str(project_path),
                    "project_name": project_name,
                    "force": False
                }
                result = await project_tools.initialize_project(arguments)
                
                logger.info(f"Auto-initialized project: {project_name}")
                return result
            else:
                # Execute project status check - this will be visible to Claude
                arguments = {"project_path": str(project_path)}
                result = await project_tools.get_project_status(arguments)
                logger.info("Project status check completed")
                return result
                
        except Exception as e:
            logger.error(f"Error during project initialization: {e}")
    
    async def execute_existing_project_boot(self, project_path: Path, project_mgmt_dir: Path, git_analysis: dict):
        """Execute MCP tools for existing project session boot."""
        try:
            from .tools.session_manager import SessionManager
            session_manager = SessionManager(db_manager=None)
            
            # Execute enhanced session boot - this will be visible to Claude
            arguments = {
                "project_path": str(project_path),
                "context_mode": "theme-focused"
            }
            result = await session_manager.boot_session_with_git_detection(arguments)
            
            logger.info("Existing project session boot completed")
            return result
            
        except Exception as e:
            logger.error(f"Error during existing project boot: {e}")
    
    async def analyze_git_project_state(self, project_path: Path) -> Dict[str, Any]:
        """Analyze Git repository state for AI project management branches using proper branch manager logic."""
        analysis = {
            "is_git_repo": False,
            "has_ai_branches": False,
            "current_branch": None,
            "current_branch_type": "unknown",
            "ai_main_exists": False,
            "ai_instance_branches": [],
            "remote_ai_branches": [],
            "is_team_member": False,
            "has_remote": False
        }
        
        try:
            # Import and use the proper branch manager
            from .core.branch_manager import GitBranchManager
            branch_manager = GitBranchManager(project_path)
            
            # Check if this is a Git repository
            result = subprocess.run([
                'git', 'rev-parse', '--git-dir'
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                return analysis
                
            analysis["is_git_repo"] = True
            
            # Get current branch and identify its type
            current_branch = branch_manager.get_current_branch()
            analysis["current_branch"] = current_branch
            
            # Identify branch type
            if current_branch == "ai-pm-org-main":
                analysis["current_branch_type"] = "ai_main"
            elif current_branch.startswith("ai-pm-org-branch-"):
                analysis["current_branch_type"] = "ai_instance"
            elif current_branch in ["main", "master"]:
                analysis["current_branch_type"] = "user_main"
            else:
                analysis["current_branch_type"] = "user_other"
            
            # Check for AI main branch existence
            analysis["ai_main_exists"] = branch_manager._branch_exists("ai-pm-org-main")
            
            # Get all AI instance branches
            instance_branches = branch_manager.list_instance_branches()
            analysis["ai_instance_branches"] = [branch.name for branch in instance_branches]
            analysis["has_ai_branches"] = analysis["ai_main_exists"] or len(analysis["ai_instance_branches"]) > 0
            
            # Detect team member scenario
            analysis["is_team_member"] = branch_manager._detect_team_member_scenario()
            
            # Check for remote repository and remote AI branches
            result = subprocess.run([
                'git', 'remote'
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                analysis["has_remote"] = True
                
                # Check for remote AI branches
                result = subprocess.run([
                    'git', 'branch', '-r'
                ], cwd=project_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    remote_branches = [line.strip() for line in result.stdout.strip().split('\n')]
                    remote_ai_branches = [b for b in remote_branches if 'ai-pm-org-' in b]
                    analysis["remote_ai_branches"] = remote_ai_branches
                    
        except Exception as e:
            logger.error(f"Error analyzing Git state: {e}")
            
        return analysis
    
    async def check_auto_task_setting(self, project_mgmt_dir: Path) -> bool:
        """Check if auto task creation is enabled in user settings."""
        try:
            config_file = project_mgmt_dir / "UserSettings" / "config.json"
            if config_file.exists():
                import json
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return config.get("tasks", {}).get("resumeTasksOnStart", False)
        except Exception as e:
            logger.error(f"Error reading auto task setting: {e}")
        return False
    
    def notify_user_git_history_found(self, project_path: Path, git_analysis: Dict[str, Any]):
        """Notify user that AI project management Git history was found.""" 
        current_branch = git_analysis.get("current_branch", "unknown")
        current_branch_type = git_analysis.get("current_branch_type", "unknown")
        ai_main_exists = git_analysis.get("ai_main_exists", False)
        ai_instance_branches = git_analysis.get("ai_instance_branches", [])
        remote_ai_branches = git_analysis.get("remote_ai_branches", [])
        is_team_member = git_analysis.get("is_team_member", False)
        
        # Build branch information
        branch_list = ""
        if ai_main_exists:
            marker = " (current)" if current_branch == "ai-pm-org-main" else ""
            branch_list += f"• ai-pm-org-main{marker} - Canonical AI organizational state\n"
        
        if ai_instance_branches:
            branch_list += "\n**AI Instance Branches (Team Members):**\n"
            for branch in ai_instance_branches:
                marker = " (current)" if branch == current_branch else ""
                branch_list += f"• {branch}{marker}\n"
        
        if remote_ai_branches:
            branch_list += "\n**Remote AI Branches:**\n"
            for branch in remote_ai_branches:
                branch_list += f"• {branch}\n"
        
        # Determine user scenario and recommendations
        scenario_info = ""
        recommendations = []
        
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
        
        rec_list = "\n".join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)])
        
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
🔍 AI project management history detected in Git branches!

**AI Branches Found:**
{branch_list}

📊 **Current Status:**
• Working Directory: No projectManagement/ structure  
• Git Repository: ✅ Available
• Current Branch: {current_branch} ({current_branch_type})
• AI Project History: ✅ Found in Git branches
• Team Member: {"✅ Yes" if is_team_member else "❌ No"}

{scenario_info}

🎯 **Recommended Next Steps:**
{rec_list}

4. **Analyze History**: Use 'get_branch_status' to understand branch contents

ℹ️  Choose your approach based on your role and collaboration needs.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info(f"User notified: AI Git history found (branch: {current_branch}, type: {current_branch_type}, team: {is_team_member})")
    
    def notify_user_no_project_structure(self, project_path: Path):
        """Notify user that no project management structure was found."""
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
⚠️  No project management structure found.

🎯 **Next Steps Available:**
1. Initialize new project: Use 'project_initialize' tool
2. Review project status: Use 'project_get_status' tool  
3. Check for existing code: Use 'check_user_code_changes' tool

ℹ️  The AI Project Manager is ready to help you set up project management for this directory.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info("User notified: No project management structure found")
    
    async def check_and_notify_project_state(self, project_path: Path, project_mgmt_dir: Path, git_analysis: Optional[Dict[str, Any]] = None):
        """Check existing project state and notify user."""
        try:
            # Check component completeness
            components = {
                "blueprint": project_mgmt_dir / "ProjectBlueprint" / "blueprint.md",
                "metadata": project_mgmt_dir / "ProjectBlueprint" / "metadata.json", 
                "flow_index": project_mgmt_dir / "ProjectFlow" / "flow-index.json",
                "themes": project_mgmt_dir / "Themes" / "themes.json",
                "completion_path": project_mgmt_dir / "Tasks" / "completion-path.json",
                "database": project_mgmt_dir / "project.db"
            }
            
            existing = {}
            missing = {}
            
            for name, path in components.items():
                if path.exists() and path.stat().st_size > 0:
                    existing[name] = str(path)
                else:
                    missing[name] = str(path)
            
            # Count tasks
            active_tasks = list((project_mgmt_dir / "Tasks" / "active").glob("*.json")) if (project_mgmt_dir / "Tasks" / "active").exists() else []
            sidequests = list((project_mgmt_dir / "Tasks" / "sidequests").glob("*.json")) if (project_mgmt_dir / "Tasks" / "sidequests").exists() else []
            
            # Determine project state and check auto-task settings
            auto_task_enabled = await self.check_auto_task_setting(project_mgmt_dir)
            
            if len(missing) == 0:
                await self.notify_user_complete_project(project_path, existing, len(active_tasks), len(sidequests), git_analysis, auto_task_enabled)
            elif len(existing) > len(missing):
                self.notify_user_partial_project(project_path, existing, missing, len(active_tasks), len(sidequests), git_analysis)
            else:
                self.notify_user_incomplete_project(project_path, existing, missing, git_analysis)
                
        except Exception as e:
            logger.error(f"Error checking project state: {e}")
            self.notify_user_unknown_project_state(project_path)
    
    async def notify_user_complete_project(self, project_path: Path, existing: dict, active_tasks: int, sidequests: int, git_analysis: Optional[Dict[str, Any]] = None, auto_task_enabled: bool = False):
        """Notify user that project structure is complete."""
        
        # Git branch info
        git_info = ""
        if git_analysis and git_analysis.get("is_git_repo"):
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
        
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
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

ℹ️  Project is ready for continued development.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info(f"User notified: Complete project structure found (auto-task: {auto_task_enabled})")
    
    def notify_user_partial_project(self, project_path: Path, existing: dict, missing: dict, active_tasks: int, sidequests: int, git_analysis: Optional[Dict[str, Any]] = None):
        """Notify user that project structure is partially complete."""
        existing_list = "• " + "\n• ".join([f"{name}: ✅" for name in existing.keys()])
        missing_list = "• " + "\n• ".join([f"{name}: ❌" for name in missing.keys()])
        
        # Git branch info
        git_info = ""
        if git_analysis and git_analysis.get("is_git_repo"):
            current_branch = git_analysis.get("current_branch", "unknown")
            current_branch_type = git_analysis.get("current_branch_type", "unknown")
            is_team_member = git_analysis.get("is_team_member", False)
            git_info = f"• Git Branch: {current_branch} ({current_branch_type})\n"
            git_info += f"• Team Member: {'✅ Yes' if is_team_member else '❌ No'}\n"
        
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
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

ℹ️  Project can be completed or continued with partial state.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info("User notified: Partial project structure found")
    
    def notify_user_incomplete_project(self, project_path: Path, existing: dict, missing: dict, git_analysis: Optional[Dict[str, Any]] = None):
        """Notify user that project structure is mostly incomplete."""
        existing_list = "• " + "\n• ".join([f"{name}: ✅" for name in existing.keys()]) if existing else "• None"
        
        # Git branch info
        git_info = ""
        if git_analysis and git_analysis.get("is_git_repo"):
            current_branch = git_analysis.get("current_branch", "unknown")
            current_branch_type = git_analysis.get("current_branch_type", "unknown")
            is_team_member = git_analysis.get("is_team_member", False)
            git_info = f"• Git Branch: {current_branch} ({current_branch_type})\n"
            git_info += f"• Team Member: {'✅ Yes' if is_team_member else '❌ No'}\n"
        
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
⚠️  Incomplete project management structure found.

📊 **Found Components:**
{existing_list}
{git_info}
🎯 **Recommended Next Steps:**
1. **Initialize Project**: Use 'project_initialize' tool to set up complete structure
2. **Check Status**: Use 'project_get_status' for detailed analysis
3. **Review Existing**: Check what can be preserved before reinitializing
4. **Git Integration**: Use 'session_boot_with_git_detection' if you have Git history

ℹ️  Project needs initialization to enable full AI project management.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info("User notified: Incomplete project structure found")
    
    def notify_user_unknown_project_state(self, project_path: Path):
        """Notify user that project state could not be determined."""
        message = f"""
=== AI Project Manager - Session Boot ===
📍 Project Directory: {project_path}
❓ Could not determine project management state.

🎯 **Available Actions:**
• Use 'project_get_status' to analyze current state
• Use 'project_initialize' to set up project management
• Check server logs for detailed error information

ℹ️  Manual project analysis recommended.
==========================================
"""
        print(message, file=sys.stderr)
        logger.info("User notified: Unknown project state")
    
    async def run(self):
        """Run the MCP server with stdio transport."""
        try:
            logger.debug("Initializing server")
            await self.initialize()
            
            logger.debug("Starting stdio server")
            # Run the server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP Server ready for connections")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
                
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise


async def main():
    """Main entry point for the MCP server."""
    server = AIProjectManagerServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)