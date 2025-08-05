#!/usr/bin/env python3
"""
Team Collaboration Module

Handles team member detection, initialization, and AI project structure setup
for AI Project Manager. Extracted from GitBranchManager to reduce file size.
"""

import subprocess
import logging
import datetime
import json
from pathlib import Path
from typing import Dict, Any, Tuple

from ..utils.project_paths import get_project_management_path, get_management_folder_name

logger = logging.getLogger(__name__)


class TeamCollaboration:
    """
    Handles team collaboration features including member detection and initialization.
    """
    
    def __init__(self, project_root: Path, ai_main_branch: str = "ai-pm-org-main", user_main_branch: str = "main", config_manager=None):
        self.project_root = Path(project_root)
        self.ai_main_branch = ai_main_branch
        self.user_main_branch = user_main_branch
        self.config_manager = config_manager
    
    def detect_team_member_scenario(self) -> bool:
        """
        Detect if this is a team member joining existing project.
        Returns True if user should get a work branch, False if main contributor.
        """
        try:
            # 1. Check if ai-pm-org-main exists from clone
            if not self._branch_exists(self.ai_main_branch):
                return False  # Original creator scenario
            
            # 2. Check if project management structure exists (means cloned project)
            proj_mgmt = get_project_management_path(self.project_root, self.config_manager)
            if not proj_mgmt.exists():
                return False  # Fresh project
            
            # 3. Check Git remote - if has origin, likely cloned
            try:
                result = subprocess.run([
                    'git', 'remote', '-v'
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if result.returncode == 0 and "origin" not in result.stdout:
                    return False  # Local project only
            except Exception:
                return False
            
            # 4. Check if currently on ai-pm-org-main (team members shouldn't be)
            current_branch = self._get_current_branch()
            if current_branch == self.ai_main_branch:
                return True  # Team member should get work branch
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting team member scenario: {e}")
            return False
    
    def initialize_for_team_member(self, user_info: Dict[str, Any], branch_creator) -> Tuple[str, bool]:
        """
        Initialize branch for team member if detected.
        
        Args:
            user_info: User information from detector
            branch_creator: Function to create instance branch
            
        Returns:
            Tuple of (branch_name, created_new_branch)
        """
        try:
            if self.detect_team_member_scenario():
                logger.info("Team member detected - creating work branch")
                logger.info(f"Detected user: {user_info['name']} ({user_info['source']})")
                
                # Create work branch for team member
                branch_name, success = branch_creator()
                if success:
                    return branch_name, True
                else:
                    logger.warning("Failed to create team member branch, staying on ai-pm-org-main")
                    return self.ai_main_branch, False
            else:
                logger.info("Main contributor detected or single-user project")
                return self.ai_main_branch, False
                
        except Exception as e:
            logger.error(f"Error initializing for team member: {e}")
            return self.ai_main_branch, False
    
    def ensure_ai_main_branch_exists(self) -> bool:
        """
        Ensure the ai-pm-org-main branch exists.
        Creates it from user's main branch if it doesn't exist.
        """
        try:
            # Check if ai-pm-org-main exists
            if not self._branch_exists(self.ai_main_branch):
                logger.info(f"Creating {self.ai_main_branch} branch from {self.user_main_branch}")
                
                # Create ai-pm-org-main from main
                result = subprocess.run([
                    'git', 'checkout', '-b', self.ai_main_branch, self.user_main_branch
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Failed to create {self.ai_main_branch}: {result.stderr}")
                    return False
                
                # Initialize AI project management structure on this branch
                self.initialize_ai_structure()
                
                logger.info(f"Successfully created {self.ai_main_branch}")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring AI main branch exists: {e}")
            return False
    
    def initialize_ai_structure(self) -> None:
        """Initialize the AI project management structure on ai-pm-org-main."""
        try:
            # Create project management directory structure
            proj_mgmt_dir = get_project_management_path(self.project_root, self.config_manager)
            proj_mgmt_dir.mkdir(exist_ok=True)
            
            # Basic directory structure
            directories = [
                "ProjectBlueprint",
                "ProjectFlow",
                "ProjectLogic",
                "Themes",
                "Tasks/active",
                "Tasks/sidequests",
                "Tasks/archive/tasks",
                "Tasks/archive/sidequests",
                "Implementations/active",
                "Implementations/completed",
                "Logs/archived",
                "Placeholders",
                ".ai-pm-config.json",
                "database"
            ]
            
            for dir_path in directories:
                (proj_mgmt_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
            # Basic AI metadata file
            ai_meta = {
                "branch_type": "ai-pm-org-main",
                "created_at": datetime.datetime.now().isoformat(),
                "description": "Canonical AI Project Manager organizational state"
            }
            
            with open(proj_mgmt_dir / ".ai-pm-meta.json", 'w') as f:
                json.dump(ai_meta, f, indent=2)
            
            # Commit the initial structure
            management_folder = get_management_folder_name(self.config_manager)
            subprocess.run(['git', 'add', f'{management_folder}/'], cwd=self.project_root)
            subprocess.run([
                'git', 'commit', '-m', 'Initialize AI Project Manager structure'
            ], cwd=self.project_root, capture_output=True)
            
            logger.info("Initialized AI project management structure")
            
        except Exception as e:
            logger.error(f"Error initializing AI structure: {e}")
    
    def create_branch_metadata(self, branch_name: str, branch_number: int, user_info: Dict[str, Any]) -> None:
        """Create metadata file for this instance branch with user information."""
        try:
            proj_mgmt_dir = get_project_management_path(self.project_root, self.config_manager)
            if not proj_mgmt_dir.exists():
                return
            
            meta_file = proj_mgmt_dir / ".ai-pm-meta.json"
            
            # Create metadata with sequential numbering and user info
            ai_meta = {
                "branch_type": "ai-pm-org-instance",
                "branch_name": branch_name,
                "branch_number": branch_number,
                "created_at": datetime.datetime.now().isoformat(),
                "status": "active",
                "created_by": {
                    "name": user_info["name"],
                    "email": user_info.get("email"),
                    "detection_source": user_info["source"]
                }
            }
            
            with open(meta_file, 'w') as f:
                json.dump(ai_meta, f, indent=2)
            
            # Commit the metadata update with user attribution
            subprocess.run(['git', 'add', '.ai-pm-meta.json'], cwd=proj_mgmt_dir)
            
            commit_message = f'Initialize branch: {branch_name}'
            if user_info["name"] != "ai-user":
                commit_message += f' (created by {user_info["name"]})'
                
            subprocess.run([
                'git', 'commit', '-m', commit_message
            ], cwd=self.project_root, capture_output=True)
            
        except Exception as e:
            logger.error(f"Error creating branch metadata: {e}")
    
    def get_team_status(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive team collaboration status for debugging."""
        try:
            is_team_member = self.detect_team_member_scenario()
            current_branch = self._get_current_branch()
            
            # Check project state
            proj_mgmt_exists = get_project_management_path(self.project_root, self.config_manager).exists()
            ai_main_exists = self._branch_exists(self.ai_main_branch)
            
            # Check Git remote
            has_origin = False
            try:
                result = subprocess.run([
                    'git', 'remote', '-v'
                ], cwd=self.project_root, capture_output=True, text=True)
                has_origin = "origin" in result.stdout if result.returncode == 0 else False
            except Exception:
                has_origin = False
            
            return {
                "user_detection": user_info,
                "team_member_scenario": is_team_member,
                "current_branch": current_branch,
                "project_state": {
                    "project_management_exists": proj_mgmt_exists,
                    "ai_main_branch_exists": ai_main_exists,
                    "has_git_origin": has_origin
                },
                "recommendation": (
                    "Create work branch" if is_team_member 
                    else "Work on ai-pm-org-main"
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting team status: {e}")
            return {"error": str(e)}
    
    def _get_current_branch(self) -> str:
        """Get the currently active branch."""
        try:
            result = subprocess.run([
                'git', 'rev-parse', '--abbrev-ref', 'HEAD'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "unknown"
                
        except Exception as e:
            logger.error(f"Error getting current branch: {e}")
            return "unknown"
    
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists."""
        try:
            result = subprocess.run([
                'git', 'branch', '--list', branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
        except Exception as e:
            logger.error(f"Error checking if branch exists: {e}")
            return False