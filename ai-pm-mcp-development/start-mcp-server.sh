#!/bin/bash
# AI Project Manager MCP Server Launcher
# Simple bash script to start the MCP server

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "🚀 Starting AI Project Manager MCP Server..."
echo "📁 Server directory: $SCRIPT_DIR"
echo "🔧 Dependencies: $([ -d "deps" ] && echo "bundled" || echo "system")"
echo "⚡ Ready to connect with Claude or other MCP clients"
echo ""

# Start the server using our Python launcher
python3 start-mcp-server.py