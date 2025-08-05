"""
Project path utilities for AI Project Manager MCP Server.

This module provides utilities for getting project management paths with
configurable folder names, ensuring all modules use the same configuration.
"""

import subprocess
from pathlib import Path
from typing import Optional, Union

# Global cache for management folder name
_cached_management_folder: Optional[str] = None
_default_management_folder = "projectManagement"

def get_management_folder_name(config_manager=None) -> str:
    """
    Get the configured management folder name.
    
    Args:
        config_manager: Optional ConfigManager instance
        
    Returns:
        Configured management folder name or default
    """
    global _cached_management_folder
    
    # Return cached value if available
    if _cached_management_folder is not None:
        return _cached_management_folder
    
    # Try to get from config manager
    if config_manager is not None:
        try:
            from ..core.config_manager import ConfigManager
            if isinstance(config_manager, ConfigManager):
                _cached_management_folder = config_manager.get_management_folder_name()
                return _cached_management_folder
        except Exception:
            pass
    
    # Try to import and use default config manager
    try:
        from ..core.config_manager import ConfigManager
        default_config = ConfigManager()
        if default_config._config_loaded:
            _cached_management_folder = default_config.get_management_folder_name()
            return _cached_management_folder
    except Exception:
        pass
    
    # Fall back to default
    _cached_management_folder = _default_management_folder
    return _cached_management_folder

def get_project_management_path(project_root: Union[str, Path], config_manager=None) -> Path:
    """
    Get the full path to the project management directory.
    
    Args:
        project_root: Path to the project root directory
        config_manager: Optional ConfigManager instance
        
    Returns:
        Path to the project management directory
    """
    project_root = Path(project_root)
    management_folder = get_management_folder_name(config_manager)
    return project_root / management_folder

def clear_cache():
    """Clear the cached management folder name, forcing reload on next access."""
    global _cached_management_folder
    _cached_management_folder = None

# Convenience functions for common subdirectories
def get_themes_path(project_root: Union[str, Path], config_manager=None) -> Path:
    """Get path to Themes directory."""
    return get_project_management_path(project_root, config_manager) / "Themes"

def get_flows_path(project_root: Union[str, Path], config_manager=None) -> Path:
    """Get path to ProjectFlow directory."""
    return get_project_management_path(project_root, config_manager) / "ProjectFlow"

def get_tasks_path(project_root: Union[str, Path], config_manager=None) -> Path:
    """Get path to Tasks directory."""
    return get_project_management_path(project_root, config_manager) / "Tasks"

def get_blueprint_path(project_root: Union[str, Path], config_manager=None) -> Path:
    """Get path to ProjectBlueprint directory."""
    return get_project_management_path(project_root, config_manager) / "ProjectBlueprint"

def get_database_path(project_root: Union[str, Path], config_manager=None) -> Path:
    """Get path to project database file."""
    return get_project_management_path(project_root, config_manager) / "project.db"

def get_config_path(project_root: Union[str, Path], config_manager=None) -> Path:
    """Get path to branch-aware configuration file."""
    return get_project_management_path(project_root, config_manager) / ".ai-pm-config.json"

def get_current_git_branch(project_root: Union[str, Path] = None) -> Optional[str]:
    """
    Get the current Git branch name.
    
    Args:
        project_root: Optional project root path for context
        
    Returns:
        Current branch name or None if not in a Git repository
    """
    try:
        if project_root:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        if result.returncode == 0:
            branch_name = result.stdout.strip()
            return branch_name if branch_name else None
        return None
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return None

def is_on_main_branch(project_root: Union[str, Path] = None) -> bool:
    """
    Check if currently on the ai-pm-org-main branch.
    
    Args:
        project_root: Optional project root path for context
        
    Returns:
        True if on ai-pm-org-main branch, False otherwise
    """
    current_branch = get_current_git_branch(project_root)
    return current_branch == "ai-pm-org-main"

def can_modify_config(project_root: Union[str, Path] = None) -> bool:
    """
    Check if configuration can be modified (only on ai-pm-org-main branch).
    
    Args:
        project_root: Optional project root path for context
        
    Returns:
        True if configuration can be modified, False otherwise
    """
    return is_on_main_branch(project_root)