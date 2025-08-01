"""
Git Branch Manager for AI Project Manager - Simple Git-based instance management.

Replaces the complex directory-based instance system with pure Git branch operations.
This achieves 97% code reduction while preserving all functionality through native Git.
"""

import subprocess
import logging
import os
import datetime
import getpass
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BranchInfo:
    """Information about an AI instance branch."""
    name: str
    number: int
    created_at: Optional[str] = None
    is_current: bool = False


class GitBranchManager:
    """
    Simple Git branch manager for AI Project Manager instances.
    
    Replaces complex directory-based instance management with pure Git operations.
    Uses sequential branch naming convention: ai-pm-org-branch-{XXX}
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.ai_main_branch = "ai-pm-org-main"
        self.user_main_branch = "main"
        
    def _detect_user_info(self) -> Dict[str, Any]:
        """
        Detect user information from Git config, environment, and system.
        Follows detection order: Git config -> Environment -> System -> Fallback
        """
        user_info = {
            "name": None,
            "email": None,
            "source": None
        }
        
        try:
            # Try Git config user.name
            result = subprocess.run([
                'git', 'config', 'user.name'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                user_info["name"] = result.stdout.strip()
                user_info["source"] = "git_config"
                
                # Also get email if available
                email_result = subprocess.run([
                    'git', 'config', 'user.email'
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if email_result.returncode == 0 and email_result.stdout.strip():
                    user_info["email"] = email_result.stdout.strip()
                    
                return user_info
        except Exception:
            pass
        
        # Try environment variables
        try:
            env_user = os.environ.get('USER') or os.environ.get('USERNAME')
            if env_user:
                user_info["name"] = env_user
                user_info["source"] = "environment"
                return user_info
        except Exception:
            pass
        
        # Try system username
        try:
            system_user = getpass.getuser()
            if system_user:
                user_info["name"] = system_user
                user_info["source"] = "system"
                return user_info
        except Exception:
            pass
        
        # Fallback
        user_info["name"] = "ai-user"
        user_info["source"] = "fallback"
        return user_info
    
    def _detect_team_member_scenario(self) -> bool:
        """
        Detect if this is a team member joining existing project.
        Returns True if user should get a work branch, False if main contributor.
        """
        try:
            # 1. Check if ai-pm-org-main exists from clone
            if not self._branch_exists(self.ai_main_branch):
                return False  # Original creator scenario
            
            # 2. Check if projectManagement/ structure exists (means cloned project)
            proj_mgmt = self.project_root / "projectManagement"
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
    
    def initialize_for_team_member(self) -> Tuple[str, bool]:
        """
        Initialize branch for team member if detected.
        Returns (branch_name, created_new_branch)
        """
        try:
            if self._detect_team_member_scenario():
                logger.info("Team member detected - creating work branch")
                user_info = self._detect_user_info()
                logger.info(f"Detected user: {user_info['name']} ({user_info['source']})")
                
                # Create work branch for team member
                branch_name, success = self.create_instance_branch()
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
                self._initialize_ai_structure()
                
                logger.info(f"Successfully created {self.ai_main_branch}")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring AI main branch exists: {e}")
            return False
    
    def _initialize_ai_structure(self) -> None:
        """Initialize the AI project management structure on ai-pm-org-main."""
        try:
            # Create projectManagement directory structure
            proj_mgmt_dir = self.project_root / "projectManagement"
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
                "UserSettings",
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
            
            import json
            with open(proj_mgmt_dir / ".ai-pm-meta.json", 'w') as f:
                json.dump(ai_meta, f, indent=2)
            
            # Commit the initial structure
            subprocess.run(['git', 'add', 'projectManagement/'], cwd=self.project_root)
            subprocess.run([
                'git', 'commit', '-m', 'Initialize AI Project Manager structure'
            ], cwd=self.project_root, capture_output=True)
            
            logger.info("Initialized AI project management structure")
            
        except Exception as e:
            logger.error(f"Error initializing AI structure: {e}")
    
    def create_instance_branch(self) -> Tuple[str, bool]:
        """
        Create a new AI instance branch using sequential numbering.
        
        Returns:
            Tuple of (branch_name, success)
        """
        try:
            # Get next sequential branch number
            next_number = self._get_next_branch_number()
            branch_name = f"ai-pm-org-branch-{next_number:03d}"
            
            # Ensure ai-pm-org-main exists
            if not self.ensure_ai_main_branch_exists():
                return branch_name, False
            
            # Create new branch from ai-pm-org-main
            result = subprocess.run([
                'git', 'checkout', '-b', branch_name, self.ai_main_branch
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to create branch {branch_name}: {result.stderr}")
                return branch_name, False
            
            # Create branch metadata
            self._create_branch_metadata(branch_name, next_number)
            
            logger.info(f"Successfully created instance branch: {branch_name}")
            return branch_name, True
            
        except Exception as e:
            logger.error(f"Error creating instance branch: {e}")
            return "", False
    
    def _get_next_branch_number(self) -> int:
        """Get the next sequential branch number by examining existing branches."""
        try:
            # Get all branches matching ai-pm-org-branch-* pattern
            result = subprocess.run([
                'git', 'branch', '--list', 'ai-pm-org-branch-*'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                return 1  # Start with 1 if no branches exist
            
            max_number = 0
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                # Remove * and whitespace from current branch indicator
                branch_name = line.replace('*', '').strip()
                
                # Extract number from ai-pm-org-branch-XXX format
                if branch_name.startswith('ai-pm-org-branch-'):
                    try:
                        number_str = branch_name[17:]  # Remove 'ai-pm-org-branch-' prefix
                        number = int(number_str)
                        max_number = max(max_number, number)
                    except ValueError:
                        continue
            
            return max_number + 1
            
        except Exception as e:
            logger.error(f"Error getting next branch number: {e}")
            return 1
    
    def _create_branch_metadata(self, branch_name: str, branch_number: int) -> None:
        """Create metadata file for this instance branch with user information."""
        try:
            proj_mgmt_dir = self.project_root / "projectManagement"
            if not proj_mgmt_dir.exists():
                return
            
            meta_file = proj_mgmt_dir / ".ai-pm-meta.json"
            
            # Detect user information for metadata
            user_info = self._detect_user_info()
            
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
            
            import json
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
    
    def list_instance_branches(self) -> List[BranchInfo]:
        """List all AI instance branches with sequential numbering."""
        try:
            # Get all branches matching ai-pm-org-* pattern
            result = subprocess.run([
                'git', 'branch', '--list', 'ai-pm-org-*'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to list branches: {result.stderr}")
                return []
            
            branches = []
            current_branch = self._get_current_branch()
            
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                # Remove Git markers (* for current branch)
                branch_name = line.strip('* ').strip()
                
                # Skip the main AI branch
                if branch_name == self.ai_main_branch:
                    continue
                
                # Parse branch number
                branch_number = self._extract_branch_number(branch_name)
                is_current = branch_name == current_branch
                
                branches.append(BranchInfo(
                    name=branch_name,
                    number=branch_number,
                    is_current=is_current
                ))
            
            return branches
            
        except Exception as e:
            logger.error(f"Error listing instance branches: {e}")
            return []
    
    def merge_instance_branch(self, branch_name: str) -> Tuple[str, bool]:
        """
        Merge instance branch into ai-pm-org-main using standard Git merge.
        
        Args:
            branch_name: Name of the branch to merge
            
        Returns:
            Tuple of (result_message, success)
        """
        try:
            # Switch to ai-pm-org-main
            result = subprocess.run([
                'git', 'checkout', self.ai_main_branch
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                return f"Failed to switch to {self.ai_main_branch}: {result.stderr}", False
            
            # Attempt merge
            result = subprocess.run([
                'git', 'merge', branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                branch_number = self._extract_branch_number(branch_name)
                return f"Successfully merged branch {branch_name} (#{branch_number:03d})", True
            else:
                # Check if it's a merge conflict
                if "CONFLICT" in result.stdout or "conflict" in result.stderr.lower():
                    return f"Merge conflicts detected. Manual resolution required.", False
                else:
                    return f"Merge failed: {result.stderr}", False
                    
        except Exception as e:
            logger.error(f"Error merging branch {branch_name}: {e}")
            return f"Error during merge: {str(e)}", False
    
    def delete_instance_branch(self, branch_name: str, force: bool = False) -> Tuple[str, bool]:
        """
        Delete a completed instance branch.
        
        Args:
            branch_name: Name of the branch to delete
            force: Force delete even if not merged
            
        Returns:
            Tuple of (result_message, success)
        """
        try:
            # Don't allow deleting the AI main branch
            if branch_name == self.ai_main_branch:
                return "Cannot delete the main AI branch", False
            
            # Use -D for force delete, -d for safe delete
            delete_flag = '-D' if force else '-d'
            
            result = subprocess.run([
                'git', 'branch', delete_flag, branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                branch_number = self._extract_branch_number(branch_name)
                return f"Deleted branch: {branch_name} (#{branch_number:03d})", True
            else:
                return f"Failed to delete branch: {result.stderr}", False
                
        except Exception as e:
            logger.error(f"Error deleting branch {branch_name}: {e}")
            return f"Error deleting branch: {str(e)}", False
    
    def switch_to_branch(self, branch_name: str) -> Tuple[str, bool]:
        """
        Switch to an AI instance branch.
        
        Args:
            branch_name: Name of the branch to switch to
            
        Returns:
            Tuple of (result_message, success)
        """
        try:
            result = subprocess.run([
                'git', 'checkout', branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                return f"Switched to branch: {branch_name}", True
            else:
                return f"Failed to switch to branch: {result.stderr}", False
                
        except Exception as e:
            logger.error(f"Error switching to branch {branch_name}: {e}")
            return f"Error switching to branch: {str(e)}", False
    
    def _extract_branch_number(self, branch_name: str) -> int:
        """Extract branch number from ai-pm-org-branch-XXX format."""
        if branch_name.startswith('ai-pm-org-branch-'):
            try:
                number_str = branch_name[17:]  # Remove 'ai-pm-org-branch-' prefix
                return int(number_str)
            except ValueError:
                return 0
        return 0
    
    def get_user_code_changes(self) -> List[str]:
        """
        Compare user's main branch with ai-pm-org-main to detect code changes.
        
        Returns:
            List of changed files
        """
        try:
            result = subprocess.run([
                'git', 'diff', '--name-only',
                f'{self.ai_main_branch}..{self.user_main_branch}'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting user code changes: {e}")
            return []
    
    def get_current_branch(self) -> str:
        """Get the currently active branch."""
        return self._get_current_branch()
    
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
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get comprehensive team collaboration status for debugging."""
        try:
            user_info = self._detect_user_info()
            is_team_member = self._detect_team_member_scenario()
            current_branch = self._get_current_branch()
            
            # Check project state
            proj_mgmt_exists = (self.project_root / "projectManagement").exists()
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
    
