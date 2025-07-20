# AI Project Manager MCP Server

A Model Context Protocol (MCP) server that provides AI-driven project management capabilities including persistent context management, theme-based organization, and seamless session continuity.

## Features

- **Project Structure Management**: Automatic initialization and management of project organization
- **Theme-Based Context Loading**: Intelligent context loading based on project themes
- **Task Management**: Comprehensive task tracking with milestones and completion paths
- **Session Continuity**: Persistent context across AI sessions
- **Configuration Management**: Flexible configuration with user settings

## Quick Start

### Prerequisites

- Python 3.8+
- Dependencies are installed in the `deps/` folder

### Installation

Dependencies are pre-installed in the `deps/` directory. No additional installation required.

### Basic Usage

1. **Test the server**:
   ```bash
   python3 test_basic.py
   ```

2. **Run the MCP server**:
   ```bash
   python3 server.py
   ```

3. **Initialize a project**:
   The server provides tools to initialize project management structure in any directory.

## Project Structure

```
mcp-server/
├── server.py              # Main MCP server entry point
├── core/                   # Core server components
│   ├── config_manager.py   # Configuration management
│   └── mcp_api.py         # MCP tool registry and API
├── tools/                  # MCP tools
│   └── project_tools.py   # Project management tools
├── deps/                   # Python dependencies
├── test_basic.py          # Basic functionality tests
└── README.md              # This file
```

## Available Tools

### Project Management Tools

- `project_initialize`: Initialize project management structure
- `project_get_blueprint`: Get current project blueprint  
- `project_update_blueprint`: Update project blueprint
- `project_get_status`: Get project status and structure info

### Configuration Tools

- `get_config`: Get current configuration settings
- `read_file`: Read files with project awareness

## Configuration

The server uses configuration files in this priority order:
1. `config.json` in current directory
2. `~/.ai-project-manager/config.json`
3. `/etc/ai-project-manager/config.json`
4. Environment variables (AI_PM_*)
5. Built-in defaults

### Environment Variables

- `AI_PM_DEBUG`: Enable debug mode (true/false)
- `AI_PM_MAX_FILE_LINES`: Maximum lines per file (default: 900)
- `AI_PM_LOG_LEVEL`: Logging level (default: INFO)
- `AI_PM_LOG_RETENTION`: Log retention days (default: 30)

## Development Status

This is the initial implementation focusing on Phase 1 of the development plan:

✅ **Completed**:
- Basic MCP server framework
- Configuration management
- Project initialization tools
- Tool registry system
- Basic testing

🚧 **In Progress**:
- Theme management tools
- Task management tools
- Session management
- Logging tools

📋 **Planned**:
- Advanced context loading
- Log management integration
- File operation tools
- Completion path tracking

## Testing

Run the basic test suite:
```bash
python3 test_basic.py
```

## Integration

This MCP server is designed to work with AI clients that support the Model Context Protocol. It provides tools for:

- Project structure management
- Context-aware file operations
- Task and milestone tracking
- Session state management

## Contributing

This server follows the implementation plan in `../docs/mcp-implementation-plan.md`. Each phase builds upon the previous one to create a comprehensive AI project management system.

## License

Part of the AI Project Manager system.