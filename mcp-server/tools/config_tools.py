"""
Configuration tools for the AI Project Manager MCP Server.
"""

from typing import List
from core.mcp_api import ToolDefinition

class ConfigTools:
    async def get_tools(self) -> List[ToolDefinition]:
        return []  # To be implemented