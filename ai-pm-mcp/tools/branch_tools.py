"""
Branch Tools for AI Project Manager - Modular Implementation

Provides MCP tools for managing AI project instances using pure Git branches.
This is a refactored version that delegates to specialized handlers for better maintainability.

REFACTORED: The original 1533-line monolithic file has been broken down into:
- branch/base_operations.py - Core branch operations (create, merge, delete, etc.)
- branch/remote_operations.py - Git remote operations (push, pull, fetch, sync)  
- branch/setup_operations.py - AI branch setup and initialization
- branch/deployment_operations.py - Critical AI-User deployment workflows

Original implementation backed up to docs/oldFiles/branch_tools_original_backup.py
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel

from ..core.branch_manager import GitBranchManager
from .branch.base_operations import BaseOperationsHandler
from .branch.remote_operations import RemoteOperationsHandler  
from .branch.setup_operations import SetupOperationsHandler
from .branch.deployment_operations import DeploymentOperationsHandler

logger = logging.getLogger(__name__)


class ToolDefinition(BaseModel):
    """Definition of an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Any = None


class BranchTools:
    """MCP tools for Git branch-based instance management."""
    
    def __init__(self, project_root: str = None, server_instance=None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.branch_manager = GitBranchManager(self.project_root)
        self.server_instance = server_instance
        
        # Initialize specialized handlers
        self.base_ops = BaseOperationsHandler(self.branch_manager, server_instance)
        self.remote_ops = RemoteOperationsHandler(self.branch_manager, server_instance)
        self.setup_ops = SetupOperationsHandler(self.branch_manager, server_instance)
        self.deployment_ops = DeploymentOperationsHandler(self.branch_manager, server_instance)
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get all branch management tools from specialized handlers."""
        tools = []
        
        # Core branch operations (7 tools)
        tools.extend(self.base_ops.get_tools())
        
        # Remote operations (7 tools)
        tools.extend(self.remote_ops.get_tools())
        
        # Setup operations (2 tools) 
        tools.extend(self.setup_ops.get_tools())
        
        # Deployment operations (2 tools)
        tools.extend(self.deployment_ops.get_tools())
        
        logger.info(f"BranchTools: Registered {len(tools)} tools across 4 specialized handlers")
        return tools