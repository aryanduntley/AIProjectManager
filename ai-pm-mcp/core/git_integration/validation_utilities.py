"""
Validation Utilities Module
Handles Git branch validation and utility operations.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Import utilities from parent module paths
from ...utils.project_paths import get_project_management_path, get_management_folder_name


class ValidationUtilities:
    """Git validation and utility operations."""
    
    def __init__(self, parent_instance):
        self.parent = parent_instance
        # Access parent properties
        self.project_root = parent_instance.project_root
        self.db_manager = parent_instance.db_manager
        self.config_manager = parent_instance.config_manager
        self.server_instance = parent_instance.server_instance
        self.git_dir = parent_instance.git_dir
    
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists locally."""
        return self._branch_exists_local(branch_name)
    
    def _branch_exists_local(self, branch_name: str) -> bool:
        """Check if a branch exists locally."""
        try:
            result = subprocess.run([
                'git', 'branch', '--list', branch_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
        except Exception:
            return False
    
    def _branch_exists_remote(self, branch_name: str, remote_name: str = "origin") -> bool:
        """Check if a branch exists on the remote repository."""
        try:
            # First, try to fetch latest remote refs
            subprocess.run([
                'git', 'fetch', remote_name, '--quiet'
            ], cwd=self.project_root, capture_output=True, text=True, timeout=10)
            
            # Check if remote branch exists
            result = subprocess.run([
                'git', 'branch', '-r', '--list', f'{remote_name}/{branch_name}'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            # Network issues or no remote - return False
            return False
        except Exception:
            return False
    
    def _has_remote_repository(self, remote_name: str = "origin") -> bool:
        """Check if a remote repository is configured."""
        try:
            result = subprocess.run([
                'git', 'remote', 'get-url', remote_name
            ], cwd=self.project_root, capture_output=True, text=True)
            
            return bool(result.stdout.strip())
            
        except Exception:
            return False
    
    def _has_previous_ai_state(self) -> bool:
        """Check if there's evidence of previous AI Project Manager state."""
        try:
            # Check for project management directory with content
            proj_mgmt_dir = get_project_management_path(self.project_root, self.config_manager)
            if proj_mgmt_dir.exists():
                # Check for key organizational files
                key_files = [
                    "ProjectBlueprint/blueprint.md",
                    "Themes/themes.json",
                    "Tasks/completion-path.json",
                    "project.db"
                ]
                
                if any((proj_mgmt_dir / key_file).exists() for key_file in key_files):
                    return True
            
            # Check database for previous sessions or branches
            try:
                cursor = self.db_manager.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM sessions WHERE project_root_path = ?", 
                             (str(self.project_root),))
                session_count = cursor.fetchone()[0]
                
                if session_count > 0:
                    return True
                    
                cursor.execute("SELECT COUNT(*) FROM git_project_state WHERE project_root_path = ?", 
                             (str(self.project_root),))
                git_state_count = cursor.fetchone()[0]
                
                if git_state_count > 0:
                    return True
                    
            except Exception:
                # Database might not exist yet
                pass
            
            # Check Git history for AI commits
            try:
                result = subprocess.run([
                    'git', 'log', '--oneline', '--grep=AI Project Manager', '--all'
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if result.stdout.strip():
                    return True
                    
            except Exception:
                pass
            
            return False
            
        except Exception:
            return False
    
    def _initialize_ai_structure_on_branch(self) -> None:
        """Initialize the AI project management structure on current branch."""
        try:
            # Create project management directory structure if it doesn't exist
            proj_mgmt_dir = get_project_management_path(self.project_root, self.config_manager)
            proj_mgmt_dir.mkdir(exist_ok=True)
            
            # Basic AI metadata file
            ai_meta = {
                "branch_type": "ai-pm-org-main",
                "created_at": datetime.now().isoformat(),
                "description": "Canonical AI Project Manager organizational state"
            }
            
            with open(proj_mgmt_dir / ".ai-pm-meta.json", 'w') as f:
                json.dump(ai_meta, f, indent=2)
            
            # Commit the initial structure if there are changes
            status_result = subprocess.run([
                'git', 'status', '--porcelain'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if status_result.stdout.strip():
                management_folder = get_management_folder_name(self.config_manager)
                subprocess.run(['git', 'add', f'{management_folder}/'], cwd=self.project_root)
                subprocess.run([
                    'git', 'commit', '-m', 'Initialize AI Project Manager structure'
                ], cwd=self.project_root, capture_output=True)
                
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Warning: Could not initialize AI structure: {e}")
    
    def sync_ai_branch_metadata(self, branch_name: str) -> None:
        """Sync branch metadata with the simplified database."""
        try:
            # Extract branch number from name
            branch_number = None
            if branch_name.startswith('ai-pm-org-branch-'):
                try:
                    number_str = branch_name[17:]  # Remove 'ai-pm-org-branch-' prefix
                    branch_number = int(number_str)
                except ValueError:
                    pass
            
            # Insert or update branch metadata in database
            query = """
                INSERT OR REPLACE INTO git_branches 
                (branch_name, branch_number, created_at, status)
                VALUES (?, ?, CURRENT_TIMESTAMP, 'active')
            """
            
            self.db_manager.execute_query(query, (branch_name, branch_number))
            
        except Exception as e:
            # Log error but don't fail the operation
            print(f"Warning: Could not sync branch metadata: {e}")
    
    def _sync_with_remote_ai_state(self) -> None:
        """Sync local database with remote organizational state after cloning."""
        try:
            # Update database to reflect that we're now working with remote state
            cursor = self.db_manager.connection.cursor()
            cursor.execute("""
                INSERT INTO git_project_state (
                    project_root_path, current_git_hash, change_summary,
                    reconciliation_status
                ) VALUES (?, ?, ?, ?)
            """, (
                str(self.project_root),
                self.parent.get_current_git_hash(),
                "Synced with remote AI organizational state",
                "completed"
            ))
            self.db_manager.connection.commit()
            
        except Exception as e:
            print(f"Warning: Could not sync remote AI state: {e}")
    
    def _validate_organizational_consistency(self) -> None:
        """Validate organizational file consistency after restoration."""
        try:
            # Basic validation that key organizational files exist
            proj_mgmt_dir = get_project_management_path(self.project_root, self.config_manager)
            if not proj_mgmt_dir.exists():
                proj_mgmt_dir.mkdir(exist_ok=True)
            
            # Ensure database exists and is accessible
            db_path = proj_mgmt_dir / "project.db"
            if db_path.exists():
                # Test database connectivity
                self.db_manager.connection.execute("SELECT 1").fetchone()
            
        except Exception as e:
            print(f"Warning: Organizational consistency validation failed: {e}")
    