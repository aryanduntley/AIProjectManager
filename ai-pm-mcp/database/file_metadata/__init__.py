"""
File Metadata Operations Module

This module provides file metadata operations split into focused components:
- directory_ops: Directory metadata management
- file_discovery: File discovery and categorization
- dependency_analysis: Language-specific dependency analysis
- impact_analysis: Impact analysis and file relationships
- initialization_tracking: Initialization progress tracking
- modification_logging: File modification logging and history
"""

from .directory_ops import DirectoryOperations
from .file_discovery import FileDiscovery
from .dependency_analysis import DependencyAnalysis
from .impact_analysis import ImpactAnalysis
from .initialization_tracking import InitializationTracking
from .modification_logging import ModificationLogging
from .theme_operations import ThemeOperations

__all__ = [
    'DirectoryOperations',
    'FileDiscovery', 
    'DependencyAnalysis',
    'ImpactAnalysis',
    'InitializationTracking',
    'ModificationLogging',
    'ThemeOperations'
]