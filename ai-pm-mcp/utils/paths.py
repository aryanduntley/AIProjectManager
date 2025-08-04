"""
Path resolution utilities for AI Project Manager MCP Server.

This module provides reliable path resolution for templates, configuration files,
and other resources by locating the MCP server root directory marker.
"""

import os
from pathlib import Path
from typing import Optional

# Global cache for MCP server root path
_mcp_server_root: Optional[Path] = None

def get_mcp_server_root() -> Path:
    """
    Get the AI Project Manager MCP server root directory.
    
    This function searches upward from the current module location to find
    the .ai-pm-mcp-root marker file, which identifies the server root.
    
    Returns:
        Path: Absolute path to the MCP server root directory
        
    Raises:
        RuntimeError: If the MCP server root cannot be found
    """
    global _mcp_server_root
    
    # Return cached path if available
    if _mcp_server_root is not None:
        return _mcp_server_root
    
    # Start from this file's directory and search upward
    current_path = Path(__file__).parent.absolute()
    
    # Search up the directory tree for the marker file
    while current_path != current_path.parent:  # Stop at filesystem root
        marker_file = current_path / ".ai-pm-mcp-root"
        if marker_file.exists():
            _mcp_server_root = current_path
            return _mcp_server_root
        current_path = current_path.parent
    
    # If not found, raise an error with helpful information
    raise RuntimeError(
        "Could not locate AI Project Manager MCP server root directory. "
        "The .ai-pm-mcp-root marker file was not found in any parent directory. "
        "This usually means the MCP server directory structure is corrupted or "
        "this module is being run from an unexpected location."
    )

def get_template_path(template_name: str) -> Path:
    """
    Get the full path to a template file.
    
    Args:
        template_name: Name of the template file (e.g., 'project-gitignore-additions.txt')
        
    Returns:
        Path: Full path to the template file
        
    Raises:
        FileNotFoundError: If the template file doesn't exist
    """
    template_path = get_mcp_server_root() / "reference" / "templates" / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template file '{template_name}' not found at {template_path}. "
            f"Available templates: {list_available_templates()}"
        )
    
    return template_path

def get_directive_path(directive_name: str, format_type: str = "json") -> Path:
    """
    Get the full path to a directive file.
    
    Args:
        directive_name: Name of the directive (e.g., '01-system-initialization')
        format_type: Format type - 'json' or 'md' (default: 'json')
        
    Returns:
        Path: Full path to the directive file
        
    Raises:
        FileNotFoundError: If the directive file doesn't exist
        ValueError: If format_type is not 'json' or 'md'
    """
    if format_type not in ['json', 'md']:
        raise ValueError(f"format_type must be 'json' or 'md', got '{format_type}'")
    
    if format_type == 'json':
        directive_path = get_mcp_server_root() / "reference" / "directives" / f"{directive_name}.json"
    else:  # md
        directive_path = get_mcp_server_root() / "reference" / "directivesmd" / f"{directive_name}.md"
    
    if not directive_path.exists():
        raise FileNotFoundError(
            f"Directive file '{directive_name}.{format_type}' not found at {directive_path}"
        )
    
    return directive_path

def list_available_templates() -> list[str]:
    """
    List all available template files.
    
    Returns:
        List of template file names
    """
    try:
        templates_dir = get_mcp_server_root() / "reference" / "templates"
        if templates_dir.exists():
            return [f.name for f in templates_dir.iterdir() if f.is_file()]
        return []
    except RuntimeError:
        return []

def load_template(template_name: str) -> str:
    """
    Load the content of a template file.
    
    Args:
        template_name: Name of the template file
        
    Returns:
        Content of the template file
        
    Raises:
        FileNotFoundError: If the template file doesn't exist
        IOError: If the file cannot be read
    """
    template_path = get_template_path(template_name)
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        raise IOError(f"Failed to read template '{template_name}': {e}")

# Convenience function for backward compatibility and common use case
def get_project_root() -> Path:
    """
    Get the project root directory (where the MCP server is installed).
    
    This is typically the user's project directory where they copied the ai-pm-mcp folder.
    
    Returns:
        Path: Absolute path to the project root directory
    """
    # The project root is the parent of the MCP server root
    return get_mcp_server_root().parent