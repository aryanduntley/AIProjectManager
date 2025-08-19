"""
Git Integration Module for AI Project Manager
Handles root-level Git repository management and project code change detection
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import hashlib

from ..database.db_manager import DatabaseManager
from ..utils.paths import load_template
from ..utils.project_paths import (
    get_project_management_path, get_themes_path, get_flows_path, 
    get_tasks_path, get_management_folder_name
)

# Import modular components
from .git_integration.repository_management import RepositoryManagement
from .git_integration.change_detection import ChangeDetection
from .git_integration.theme_impact_analysis import ThemeImpactAnalysis
from .git_integration.organizational_reconciliation import OrganizationalReconciliation
from .git_integration.branch_operations import BranchOperations
from .git_integration.validation_utilities import ValidationUtilities


class GitIntegrationManager:
    """
    Manages Git integration for AI Project Manager including:
    - Root-level Git repository initialization and validation
    - Project code change detection
    - Theme impact analysis when code changes occur
    - Integration with MCP instance management
    """
    
    def __init__(self, project_root: Path, db_manager: DatabaseManager, config_manager=None, server_instance=None):
        self.project_root = Path(project_root)
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.server_instance = server_instance  # For directive hook integration
        self.git_dir = self.project_root / ".git"
        self.project_management_dir = get_project_management_path(self.project_root, config_manager)
        
        # Initialize modular components
        self._repo_mgmt = RepositoryManagement(self)
        self._change_detection = ChangeDetection(self)
        self._theme_impact = ThemeImpactAnalysis(self)
        self._org_reconciliation = OrganizationalReconciliation(self)
        self._branch_ops = BranchOperations(self)
        self._validation = ValidationUtilities(self)

    # ============================================================================
    # GIT REPOSITORY MANAGEMENT - Delegates to RepositoryManagement
    # ============================================================================
    
    def is_git_repository(self) -> bool:
        """Check if project root is a Git repository"""
        return self._repo_mgmt.is_git_repository()
    
    async def initialize_git_repository(self) -> Dict[str, Any]:
        """Initialize Git repository at project root if it doesn't exist"""
        return await self._repo_mgmt.initialize_git_repository()
    
    async def _trigger_git_hook(self, trigger: str, operation_data: Dict[str, Any]):
        """Helper method to trigger directive hooks for Git operations."""
        return await self._repo_mgmt._trigger_git_hook(trigger, operation_data)
    
    def _generate_mcp_gitignore(self) -> str:
        """Generate .gitignore content for Git branch-based AI Project Manager from template"""
        return self._repo_mgmt._generate_mcp_gitignore()
    
    def get_current_git_hash(self) -> Optional[str]:
        """Get current Git commit hash"""
        return self._repo_mgmt.get_current_git_hash()
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get comprehensive Git repository status"""
        return self._repo_mgmt.get_git_status()
    
    def validate_git_configuration(self) -> Dict[str, Any]:
        """Validate Git configuration for AI Project Manager compatibility"""
        return self._repo_mgmt.validate_git_configuration()
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get comprehensive repository information"""
        return self._repo_mgmt.get_repository_info()

    # ============================================================================
    # PROJECT CODE CHANGE DETECTION - Delegates to ChangeDetection
    # ============================================================================
    
    def detect_project_code_changes(self) -> Dict[str, Any]:
        """Detect if project code has changed since last AI session"""
        return self._change_detection.detect_project_code_changes()
    
    def _get_last_known_git_state(self) -> Optional[Dict[str, Any]]:
        """Get the last known Git state from database"""
        return self._change_detection._get_last_known_git_state()
    
    def _analyze_git_changes(self, last_hash: Optional[str], current_hash: str) -> Dict[str, Any]:
        """Analyze Git changes between two commits"""
        return self._change_detection._analyze_git_changes(last_hash, current_hash)
    
    def _get_change_type_from_status(self, status: str) -> str:
        """Convert Git status character to change type"""
        return self._change_detection._get_change_type_from_status(status)
    
    def _generate_change_summary(self, change_types: Dict[str, int], total_files: int, affected_themes: List[str]) -> str:
        """Generate a human-readable summary of changes"""
        return self._change_detection._generate_change_summary(change_types, total_files, affected_themes)
    
    def _update_git_project_state(self, current_hash: str, changes: Dict[str, Any]) -> None:
        """Update the database with current Git state"""
        return self._change_detection._update_git_project_state(current_hash, changes)

    # ============================================================================
    # THEME IMPACT ANALYSIS - Delegates to ThemeImpactAnalysis
    # ============================================================================
    
    def _analyze_theme_impact(self, changed_files: List[Dict[str, Any]]) -> List[str]:
        """Analyze which themes are affected by file changes"""
        return self._theme_impact._analyze_theme_impact(changed_files)
    
    def _get_themes_for_file(self, file_path: str, theme_files: Dict[str, Any]) -> List[str]:
        """Get themes that include a specific file"""
        return self._theme_impact._get_themes_for_file(file_path, theme_files)
    
    def _infer_themes_from_directory(self, file_path: str) -> List[str]:
        """Infer themes based on directory structure"""
        return self._theme_impact._infer_themes_from_directory(file_path)
    
    def _infer_themes_from_patterns(self, file_path: str) -> List[str]:
        """Infer themes based on file patterns"""
        return self._theme_impact._infer_themes_from_patterns(file_path)
    
    def _analyze_deletion_impact(self, file_path: str, theme_files: Dict[str, Any]) -> List[str]:
        """Analyze impact of file deletion on themes"""
        return self._theme_impact._analyze_deletion_impact(file_path, theme_files)
    
    def _analyze_single_file_theme_impact(self, file_path: str) -> List[str]:
        """Analyze theme impact for a single file"""
        return self._theme_impact._analyze_single_file_theme_impact(file_path)

    # ============================================================================
    # ORGANIZATIONAL STATE RECONCILIATION - Delegates to OrganizationalReconciliation
    # ============================================================================
    
    async def reconcile_organizational_state_with_code(self, change_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile organizational state (themes, flows, tasks) with detected code changes"""
        return await self._org_reconciliation.reconcile_organizational_state_with_code(change_analysis)
    
    def _update_themes_with_file_changes(self, affected_themes: List[str], changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update theme definitions based on file changes"""
        return self._org_reconciliation._update_themes_with_file_changes(affected_themes, changed_files)
    
    def _update_flows_with_file_changes(self, affected_themes: List[str], changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update flow definitions based on file changes"""
        return self._org_reconciliation._update_flows_with_file_changes(affected_themes, changed_files)
    
    def _update_tasks_with_file_changes(self, changed_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update task definitions based on file changes"""
        return self._org_reconciliation._update_tasks_with_file_changes(changed_files)

    # ============================================================================
    # BRANCH OPERATIONS - Delegates to BranchOperations
    # ============================================================================
    
    def ensure_ai_main_branch_exists(self) -> Dict[str, Any]:
        """Ensure AI main branch exists with proper setup"""
        return self._branch_ops.ensure_ai_main_branch_exists()
    
    def _clone_ai_branch_from_remote(self, ai_main_branch: str) -> Dict[str, Any]:
        """Clone AI branch from remote repository"""
        return self._branch_ops._clone_ai_branch_from_remote(ai_main_branch)
    
    def _restore_ai_organizational_state(self, ai_main_branch: str, user_main_branch: str) -> Dict[str, Any]:
        """Restore AI organizational state from existing branch"""
        return self._branch_ops._restore_ai_organizational_state(ai_main_branch, user_main_branch)
    
    def _create_fresh_ai_branch(self, ai_main_branch: str, user_main_branch: str) -> Dict[str, Any]:
        """Create fresh AI branch with initial structure"""
        return self._branch_ops._create_fresh_ai_branch(ai_main_branch, user_main_branch)
    
    def switch_to_ai_branch(self, branch_name: str = "ai-pm-org-main") -> Dict[str, Any]:
        """Switch to specified AI branch"""
        return self._branch_ops.switch_to_ai_branch(branch_name)
    
    def get_user_code_changes(self, ai_main_branch: str = "ai-pm-org-main", user_main_branch: str = "main") -> Dict[str, Any]:
        """Get changes made by user since last AI session"""
        return self._branch_ops.get_user_code_changes(ai_main_branch, user_main_branch)
    
    def create_work_branch(self, branch_number: int) -> Dict[str, Any]:
        """Create a new work branch for AI operations"""
        return self._branch_ops.create_work_branch(branch_number)
    
    def get_next_branch_number(self) -> int:
        """Get the next available branch number"""
        return self._branch_ops.get_next_branch_number()
    
    def create_next_work_branch(self) -> Dict[str, Any]:
        """Create the next available work branch"""
        return self._branch_ops.create_next_work_branch()
    
    def list_ai_branches(self) -> Dict[str, Any]:
        """List all AI-related branches"""
        return self._branch_ops.list_ai_branches()

    # ============================================================================
    # VALIDATION UTILITIES - Delegates to ValidationUtilities
    # ============================================================================
    
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if branch exists locally or remotely"""
        return self._validation._branch_exists(branch_name)
    
    def _branch_exists_local(self, branch_name: str) -> bool:
        """Check if branch exists locally"""
        return self._validation._branch_exists_local(branch_name)
    
    def _branch_exists_remote(self, branch_name: str, remote_name: str = "origin") -> bool:
        """Check if branch exists on remote"""
        return self._validation._branch_exists_remote(branch_name, remote_name)
    
    def _has_remote_repository(self, remote_name: str = "origin") -> bool:
        """Check if remote repository is configured"""
        return self._validation._has_remote_repository(remote_name)
    
    def _has_previous_ai_state(self) -> bool:
        """Check if previous AI organizational state exists"""
        return self._validation._has_previous_ai_state()
    
    def _initialize_ai_structure_on_branch(self) -> None:
        """Initialize AI project structure on current branch"""
        return self._validation._initialize_ai_structure_on_branch()
    
    def sync_ai_branch_metadata(self, branch_name: str) -> None:
        """Synchronize AI branch metadata"""
        return self._validation.sync_ai_branch_metadata(branch_name)
    
    def _sync_with_remote_ai_state(self) -> None:
        """Synchronize with remote AI state if available"""
        return self._validation._sync_with_remote_ai_state()
    
    def _validate_organizational_consistency(self) -> None:
        """Validate organizational consistency across branches"""
        return self._validation._validate_organizational_consistency()