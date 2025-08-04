#!/usr/bin/env python3
"""
Git Utilities Module

Common Git utility functions for AI Project Manager.
Extracted from GitBranchManager to reduce file size.
"""

import subprocess
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class GitUtils:
    """
    Common Git utility functions.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
    
    def get_current_branch(self) -> str:
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
    
    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists."""
        try:
            result = subprocess.run([
                'git', 'branch', '--list', branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
        except Exception as e:
            logger.error(f"Error checking if branch exists: {e}")
            return False
    
    def extract_branch_number(self, branch_name: str) -> int:
        """Extract branch number from ai-pm-org-branch-XXX format."""
        if branch_name.startswith('ai-pm-org-branch-'):
            try:
                number_str = branch_name[17:]  # Remove 'ai-pm-org-branch-' prefix
                return int(number_str)
            except ValueError:
                return 0
        return 0
    
    def get_next_branch_number(self) -> int:
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
    
    def get_user_code_changes(self, ai_main_branch: str, user_main_branch: str) -> List[str]:
        """
        Compare user's main branch with ai-pm-org-main to detect code changes.
        
        Returns:
            List of changed files
        """
        try:
            result = subprocess.run([
                'git', 'diff', '--name-only',
                f'{ai_main_branch}..{user_main_branch}'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting user code changes: {e}")
            return []
    
    def switch_to_branch(self, branch_name: str) -> tuple[str, bool]:
        """
        Switch to a Git branch.
        
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
    
    def delete_branch(self, branch_name: str, force: bool = False) -> tuple[str, bool]:
        """
        Delete a Git branch.
        
        Args:
            branch_name: Name of the branch to delete
            force: Force delete even if not merged
            
        Returns:
            Tuple of (result_message, success)
        """
        try:
            # Use -D for force delete, -d for safe delete
            delete_flag = '-D' if force else '-d'
            
            result = subprocess.run([
                'git', 'branch', delete_flag, branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                branch_number = self.extract_branch_number(branch_name)
                return f"Deleted branch: {branch_name} (#{branch_number:03d})", True
            else:
                return f"Failed to delete branch: {result.stderr}", False
                
        except Exception as e:
            logger.error(f"Error deleting branch {branch_name}: {e}")
            return f"Error deleting branch: {str(e)}", False