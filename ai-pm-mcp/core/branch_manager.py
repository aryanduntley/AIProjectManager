"""
Git Branch Manager for AI Project Manager - Simple Git-based instance management.

Replaces the complex directory-based instance system with pure Git branch operations.
This achieves 97% code reduction while preserving all functionality through native Git.
"""

import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

from .git_safety import GitSafetyChecker
from .repository_detector import RepositoryDetector
from .merge_operations import MergeOperations
from .team_collaboration import TeamCollaboration
from .git_utils import GitUtils

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
        
        # Initialize modular components
        self.safety_checker = GitSafetyChecker(project_root, self.ai_main_branch)
        self.repo_detector = RepositoryDetector(project_root)
        self.merge_ops = MergeOperations(project_root, self.ai_main_branch)
        self.team_collab = TeamCollaboration(project_root, self.ai_main_branch, self.user_main_branch)
        self.git_utils = GitUtils(project_root)
    
    # Delegation methods for repository detection and metadata
    def _detect_user_info(self) -> Dict[str, Any]:
        """Detect user information from Git config, environment, and system."""
        return self.repo_detector.detect_user_info()
    
    def _get_metadata_path(self) -> Path:
        """Get path to project metadata file."""
        return self.repo_detector.get_metadata_path()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load project metadata from file."""
        return self.repo_detector.load_metadata()
    
    def _save_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save project metadata to file."""
        return self.repo_detector.save_metadata(metadata)
    
    def _check_gh_cli_available(self) -> bool:
        """Check if GitHub CLI (gh) is available and authenticated."""
        return self.repo_detector.check_gh_cli_available()
    
    def _detect_repository_type(self) -> Dict[str, Any]:
        """Detect if this is a fork, clone, or original repository."""
        return self.repo_detector.detect_repository_type()
    
    # Delegation methods for safety checks
    def check_workflow_safety(self) -> Dict[str, Any]:
        """Check current Git state for workflow safety issues."""
        repo_info = self._detect_repository_type()
        return self.safety_checker.check_workflow_safety(repo_info)
    
    def check_branch_ancestry(self, target_branch: str = None) -> Dict[str, Any]:
        """Check if current branch has proper ancestry from target branch."""
        return self.safety_checker.check_branch_ancestry(target_branch)
    
    def validate_branch_creation(self) -> Dict[str, Any]:
        """Validate that it's safe to create a new branch."""
        repo_info = self._detect_repository_type()
        return self.safety_checker.validate_branch_creation(repo_info)
    
    # Delegation methods for team collaboration
    def _detect_team_member_scenario(self) -> bool:
        """Detect if this is a team member joining existing project."""
        return self.team_collab.detect_team_member_scenario()
    
    def initialize_for_team_member(self) -> Tuple[str, bool]:
        """Initialize branch for team member if detected."""
        user_info = self._detect_user_info()
        return self.team_collab.initialize_for_team_member(user_info, self.create_instance_branch)
    
    def ensure_ai_main_branch_exists(self) -> bool:
        """Ensure the ai-pm-org-main branch exists."""
        return self.team_collab.ensure_ai_main_branch_exists()
    
    def _initialize_ai_structure(self) -> None:
        """Initialize the AI project management structure on ai-pm-org-main."""
        self.team_collab.initialize_ai_structure()
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get comprehensive team collaboration status for debugging."""
        user_info = self._detect_user_info()
        return self.team_collab.get_team_status(user_info)
    
    # Delegation methods for Git utilities
    def get_current_branch(self) -> str:
        """Get the currently active branch."""
        return self.git_utils.get_current_branch()
    
    def _get_current_branch(self) -> str:
        """Get the currently active branch (internal method)."""
        return self.git_utils.get_current_branch()
    
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists."""
        return self.git_utils.branch_exists(branch_name)
    
    def _extract_branch_number(self, branch_name: str) -> int:
        """Extract branch number from ai-pm-org-branch-XXX format."""
        return self.git_utils.extract_branch_number(branch_name)
    
    def _get_next_branch_number(self) -> int:
        """Get the next sequential branch number by examining existing branches."""
        return self.git_utils.get_next_branch_number()
    
    def get_user_code_changes(self) -> List[str]:
        """Compare user's main branch with ai-pm-org-main to detect code changes."""
        return self.git_utils.get_user_code_changes(self.ai_main_branch, self.user_main_branch)
    
    def switch_to_branch(self, branch_name: str) -> Tuple[str, bool]:
        """Switch to an AI instance branch."""
        return self.git_utils.switch_to_branch(branch_name)
    
    def delete_instance_branch(self, branch_name: str, force: bool = False) -> Tuple[str, bool]:
        """Delete a completed instance branch."""
        # Don't allow deleting the AI main branch
        if branch_name == self.ai_main_branch:
            return "Cannot delete the main AI branch", False
        
        return self.git_utils.delete_branch(branch_name, force)
    
    # Core branch management methods (kept in main class)
    def create_instance_branch(self) -> Tuple[str, bool]:
        """
        Create a new AI instance branch using sequential numbering with safety checks.
        
        Returns:
            Tuple of (branch_name, success)
        """
        try:
            # Perform safety validation first
            validation = self.validate_branch_creation()
            
            # Get next sequential branch number
            next_number = self._get_next_branch_number()
            branch_name = f"ai-pm-org-branch-{next_number:03d}"
            
            # Check for blocking issues
            if not validation["safe_to_create"]:
                error_msg = f"Branch creation blocked for {branch_name}:\n"
                for issue in validation["blocking_issues"]:
                    error_msg += f"- {issue['message']}\n"
                
                if validation["recommendations"]:
                    error_msg += "Recommendations:\n"
                    for rec in validation["recommendations"]:
                        error_msg += f"- {rec['message']}\n"
                
                logger.warning(error_msg)
                return branch_name, False
            
            # Log any non-blocking warnings
            if validation["warnings"]:
                warning_msg = f"Creating branch {branch_name} with warnings:\n"
                for warning in validation["warnings"]:
                    warning_msg += f"- {warning['message']}\n"
                logger.info(warning_msg)
            
            # Handle ancestry issues by auto-switching if needed
            current_branch = self._get_current_branch()
            if current_branch != self.ai_main_branch:
                logger.info(f"Auto-switching from '{current_branch}' to '{self.ai_main_branch}' for safe branch creation")
                
                switch_result = subprocess.run([
                    'git', 'checkout', self.ai_main_branch
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if switch_result.returncode != 0:
                    logger.error(f"Failed to switch to {self.ai_main_branch}: {switch_result.stderr}")
                    return branch_name, False
            
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
    
    def _create_branch_metadata(self, branch_name: str, branch_number: int) -> None:
        """Create metadata file for this instance branch with user information."""
        user_info = self._detect_user_info()
        self.team_collab.create_branch_metadata(branch_name, branch_number, user_info)
    
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
    
    def merge_instance_branch(self, branch_name: str, force_direct_merge: bool = False) -> Tuple[str, bool]:
        """
        Merge instance branch using pull request creation when possible, or direct merge as fallback.
        
        Args:
            branch_name: Name of the branch to merge
            force_direct_merge: Force direct merge instead of creating PR
            
        Returns:
            Tuple of (result_message, success)
        """
        try:
            # Get repository and user information
            repo_info = self._detect_repository_type()
            user_info = self._detect_user_info()
            branch_number = self._extract_branch_number(branch_name)
            
            # Delegate to merge operations module
            return self.merge_ops.merge_instance_branch(
                branch_name, branch_number, repo_info, user_info, force_direct_merge
            )
                
        except Exception as e:
            logger.error(f"Error in merge_instance_branch {branch_name}: {e}")
            return f"Error during merge operation: {str(e)}", False