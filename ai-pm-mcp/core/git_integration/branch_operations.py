"""
Branch Operations Module
Handles AI branch management and work branch operations.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import re


class BranchOperations:
    """AI branch management and work branch operations."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties
        self.project_root = parent_instance.project_root
        self.db_manager = parent_instance.db_manager
        self.config_manager = parent_instance.config_manager
        self.server_instance = parent_instance.server_instance
        self.git_dir = parent_instance.git_dir
    
    # ============================================================================
    # AI BRANCH MANAGEMENT INTEGRATION
    # ============================================================================
    
    def ensure_ai_main_branch_exists(self) -> Dict[str, Any]:
        """
        Ensure the ai-pm-org-main branch exists with proper remote/local handling.
        Priority: Remote clone > Local restoration > Fresh creation
        """
        result = {
            "success": False,
            "action": "none",
            "message": "",
            "branch_created": False,
            "source": None
        }
        
        try:
            ai_main_branch = "ai-pm-org-main"
            user_main_branch = "main"
            
            # Check if ai-pm-org-main exists locally
            if self._branch_exists_local(ai_main_branch):
                result["success"] = True
                result["action"] = "exists"
                result["message"] = f"{ai_main_branch} already exists locally"
                result["source"] = "local"
                return result
            
            # Branch doesn't exist locally - check remote and previous state
            has_remote = self._has_remote_repository()
            remote_branch_exists = has_remote and self._branch_exists_remote(ai_main_branch)
            has_previous_state = self._has_previous_ai_state()
            
            if remote_branch_exists:
                # Priority 1: Clone from remote (team collaboration)
                result = self._clone_ai_branch_from_remote(ai_main_branch)
                
            elif has_previous_state and not remote_branch_exists:
                # Priority 2: Restore from previous local state
                result = self._restore_ai_organizational_state(ai_main_branch, user_main_branch)
                
            else:
                # Priority 3: Create fresh branch (first-time setup)
                result = self._create_fresh_ai_branch(ai_main_branch, user_main_branch)
            
            return result
            
        except Exception as e:
            result["message"] = f"Error ensuring AI main branch: {str(e)}"
            return result
    
    def _clone_ai_branch_from_remote(self, ai_main_branch: str) -> Dict[str, Any]:
        """Clone AI main branch from remote repository."""
        result = {
            "success": False,
            "action": "cloned_from_remote",
            "message": "",
            "branch_created": True,
            "source": "remote"
        }
        
        try:
            # Clone branch from remote
            subprocess.run([
                'git', 'checkout', '-b', ai_main_branch, f'origin/{ai_main_branch}'
            ], cwd=self.project_root, check=True, capture_output=True, text=True)
            
            result["success"] = True
            result["message"] = f"Cloned {ai_main_branch} from remote repository (team collaboration)"
            
            # Sync local database with remote organizational state
            self._sync_with_remote_ai_state()
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Failed to clone {ai_main_branch} from remote: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error cloning from remote: {str(e)}"
            return result
    
    def _restore_ai_organizational_state(self, ai_main_branch: str, user_main_branch: str) -> Dict[str, Any]:
        """Restore AI branch from previous local organizational state."""
        result = {
            "success": False,
            "action": "restored_from_local",
            "message": "",
            "branch_created": True,
            "source": "restoration"
        }
        
        try:
            # Create branch from user main but preserve organizational state
            subprocess.run([
                'git', 'checkout', '-b', ai_main_branch, user_main_branch
            ], cwd=self.project_root, check=True, capture_output=True, text=True)
            
            result["success"] = True
            result["message"] = f"Restored {ai_main_branch} with previous organizational state"
            
            # The organizational files should already exist from previous state
            # Just ensure database consistency
            self._validate_organizational_consistency()
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Failed to restore {ai_main_branch}: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error restoring organizational state: {str(e)}"
            return result
    
    def _create_fresh_ai_branch(self, ai_main_branch: str, user_main_branch: str) -> Dict[str, Any]:
        """Create fresh AI main branch for first-time setup."""
        result = {
            "success": False,
            "action": "created_fresh",
            "message": "",
            "branch_created": True,
            "source": "fresh"
        }
        
        try:
            # Create fresh branch from user main
            subprocess.run([
                'git', 'checkout', '-b', ai_main_branch, user_main_branch
            ], cwd=self.project_root, check=True, capture_output=True, text=True)
            
            result["success"] = True
            result["message"] = f"Created fresh {ai_main_branch} from {user_main_branch} (first-time setup)"
            
            # Initialize AI project management structure
            self._initialize_ai_structure_on_branch()
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Failed to create fresh {ai_main_branch}: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error creating fresh branch: {str(e)}"
            return result
    
    def switch_to_ai_branch(self, branch_name: str = "ai-pm-org-main") -> Dict[str, Any]:
        """Switch to AI main branch or specified AI branch for operations."""
        result = {
            "success": False,
            "previous_branch": None,
            "current_branch": None,
            "message": ""
        }
        
        try:
            # Get current branch before switching
            current_branch_result = subprocess.run([
                'git', 'rev-parse', '--abbrev-ref', 'HEAD'
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            result["previous_branch"] = current_branch_result.stdout.strip()
            
            # Switch to specified branch
            subprocess.run([
                'git', 'checkout', branch_name
            ], cwd=self.project_root, check=True, capture_output=True)
            
            result["success"] = True
            result["current_branch"] = branch_name
            result["message"] = f"Switched to branch: {branch_name}"
            
            return result
            
        except Exception as e:
            result["message"] = f"Error switching to branch {branch_name}: {str(e)}"
            return result
    
    def get_user_code_changes(self, ai_main_branch: str = "ai-pm-org-main", user_main_branch: str = "main") -> Dict[str, Any]:
        """
        Compare user's main branch with ai-pm-org-main to see user changes.
        Returns analysis of what the user has changed outside of AI management.
        """
        result = {
            "success": False,
            "changed_files": [],
            "change_summary": "",
            "themes_affected": [],
            "message": ""
        }
        
        try:
            # Ensure both branches exist
            if not self._branch_exists(ai_main_branch):
                result["message"] = f"AI main branch {ai_main_branch} does not exist"
                return result
                
            if not self._branch_exists(user_main_branch):
                result["message"] = f"User main branch {user_main_branch} does not exist"
                return result
            
            # Get diff between branches
            diff_result = subprocess.run([
                'git', 'diff', '--name-status',
                f'{ai_main_branch}..{user_main_branch}'
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            if not diff_result.stdout.strip():
                result["success"] = True
                result["message"] = "No changes detected between AI and user branches"
                return result
            
            # Parse changed files
            changed_files = []
            for line in diff_result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        status = parts[0]
                        file_path = parts[1]
                        changed_files.append({
                            "file": file_path,
                            "status": self.parent._get_change_type_from_status(status),
                            "raw_status": status
                        })
            
            result["changed_files"] = changed_files
            
            # Analyze theme impact
            affected_themes = self.parent._analyze_theme_impact(changed_files)
            result["themes_affected"] = affected_themes
            
            # Generate summary
            total_files = len(changed_files)
            change_types = {}
            for file in changed_files:
                change_type = file["status"]
                change_types[change_type] = change_types.get(change_type, 0) + 1
            
            result["change_summary"] = self.parent._generate_change_summary(change_types, total_files, affected_themes)
            result["success"] = True
            result["message"] = f"Found {total_files} changed files affecting {len(affected_themes)} themes"
            
            return result
            
        except Exception as e:
            result["message"] = f"Error comparing user code changes: {str(e)}"
            return result

    def create_work_branch(self, branch_number: int) -> Dict[str, Any]:
        """
        Create a new work branch from ai-pm-org-main (not user's main).
        This ensures work branches always clone the organizational state.
        """
        result = {
            "success": False,
            "action": "none",
            "message": "",
            "branch_name": None,
            "branch_created": False
        }
        
        try:
            ai_main_branch = "ai-pm-org-main"
            work_branch = f"ai-pm-org-branch-{branch_number}"
            
            # Ensure ai-pm-org-main exists first
            main_result = self.ensure_ai_main_branch_exists()
            if not main_result["success"]:
                result["message"] = f"Cannot create work branch: {main_result['message']}"
                return result
            
            # Check if work branch already exists
            if self._branch_exists_local(work_branch):
                result["success"] = True
                result["action"] = "exists"
                result["message"] = f"Work branch {work_branch} already exists"
                result["branch_name"] = work_branch
                return result
            
            # Switch to ai-pm-org-main first to ensure we're on the right base
            switch_result = self.switch_to_ai_branch(ai_main_branch)
            if not switch_result["success"]:
                result["message"] = f"Could not switch to {ai_main_branch}: {switch_result['message']}"
                return result
            
            # Create work branch from ai-pm-org-main (cloning organizational state)
            subprocess.run([
                'git', 'checkout', '-b', work_branch, ai_main_branch
            ], cwd=self.project_root, check=True, capture_output=True, text=True)
            
            # Create minimal branch metadata
            branch_metadata = {
                "branchId": work_branch,
                "branchNumber": branch_number,
                "createdFrom": ai_main_branch,
                "createdAt": datetime.now().isoformat(),
                "primaryThemes": [],
                "status": "active",
                "description": f"Work branch {branch_number} cloned from {ai_main_branch}"
            }
            
            metadata_path = self.project_root / ".ai-pm-meta.json"
            with open(metadata_path, 'w') as f:
                json.dump(branch_metadata, f, indent=2)
            
            # Commit the metadata
            subprocess.run(['git', 'add', '.ai-pm-meta.json'], cwd=self.project_root, check=True)
            subprocess.run([
                'git', 'commit', '-m', f'Initialize work branch {work_branch} metadata'
            ], cwd=self.project_root, check=True, capture_output=True)
            
            # Update database tracking
            self.sync_ai_branch_metadata(work_branch)
            
            result["success"] = True
            result["action"] = "created"
            result["message"] = f"Created work branch {work_branch} from {ai_main_branch}"
            result["branch_name"] = work_branch
            result["branch_created"] = True
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Git command failed creating work branch: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error creating work branch: {str(e)}"
            return result
    
    def get_next_branch_number(self) -> int:
        """Get the next available branch number for work branches."""
        try:
            # Get all existing AI work branches
            result = subprocess.run([
                'git', 'branch', '-a', '--list', 'ai-pm-org-branch-*'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            branch_numbers = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                # Extract branch name from output (remove * and whitespace)
                branch_name = line.strip().lstrip('* ').replace('remotes/origin/', '')
                
                # Extract number from branch name
                if branch_name.startswith('ai-pm-org-branch-'):
                    try:
                        number_str = branch_name[17:]  # Remove 'ai-pm-org-branch-' prefix
                        branch_numbers.append(int(number_str))
                    except ValueError:
                        continue
            
            # Return next available number
            if not branch_numbers:
                return 1
            else:
                return max(branch_numbers) + 1
                
        except Exception as e:
            print(f"Warning: Could not determine next branch number: {e}")
            return 1
    
    def create_next_work_branch(self) -> Dict[str, Any]:
        """Create a new work branch with the next available number."""
        next_number = self.get_next_branch_number()
        return self.create_work_branch(next_number)
    
    def list_ai_branches(self) -> Dict[str, Any]:
        """List all AI-related branches (local and remote)."""
        result = {
            "success": False,
            "branches": {
                "main": None,
                "work_branches": []
            },
            "message": ""
        }
        
        try:
            # Get all branches
            branch_result = subprocess.run([
                'git', 'branch', '-a'
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            ai_main_exists = False
            work_branches = []
            
            for line in branch_result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                    
                # Clean branch name
                branch_name = line.strip().lstrip('* ').replace('remotes/origin/', '')
                is_current = line.strip().startswith('*')
                is_remote = 'remotes/origin/' in line
                
                if branch_name == 'ai-pm-org-main':
                    ai_main_exists = True
                    result["branches"]["main"] = {
                        "name": branch_name,
                        "current": is_current,
                        "remote": is_remote,
                        "local": not is_remote or self._branch_exists_local(branch_name)
                    }
                elif branch_name.startswith('ai-pm-org-branch-'):
                    # Extract branch number
                    try:
                        number_str = branch_name[17:]
                        branch_number = int(number_str)
                        work_branches.append({
                            "name": branch_name,
                            "number": branch_number,
                            "current": is_current,
                            "remote": is_remote,
                            "local": not is_remote or self._branch_exists_local(branch_name)
                        })
                    except ValueError:
                        continue
            
            # Sort work branches by number
            work_branches.sort(key=lambda x: x["number"])
            result["branches"]["work_branches"] = work_branches
            
            result["success"] = True
            result["message"] = f"Found {len(work_branches)} work branches"
            
            if not ai_main_exists:
                result["message"] += " (ai-pm-org-main not found)"
            
            return result
            
        except subprocess.CalledProcessError as e:
            result["message"] = f"Git command failed: {e.stderr}"
            return result
        except Exception as e:
            result["message"] = f"Error listing AI branches: {str(e)}"
            return result