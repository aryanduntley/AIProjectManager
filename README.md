# AI Project Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> **Intelligent AI-powered project management through persistent context and autonomous task orchestration**

AI Project Manager is a sophisticated Model Context Protocol (MCP) server that enables AI agents to autonomously manage large, complex software projects from start to finish. It provides persistent project memory, intelligent context loading, and advanced task orchestration to eliminate the need for constant human intervention and context re-establishment.

## Key Features

### 🧠 **Persistent Project Intelligence**
- **Project Blueprint**: Comprehensive project understanding maintained across sessions
- **Theme-Based Organization**: Automatic discovery and organization of project components
- **Multi-Flow Architecture**: Detailed user experience flows organized by domain
- **Session Continuity**: Complete context restoration across AI sessions

### 🎯 **Advanced Task Management**
- **Hierarchical Task System**: Main tasks with intelligent sidequest support
- **Real-Time State Preservation**: Never lose progress on task completion
- **Parallel Development**: Git branch management for team collaboration
- **Completion Path Tracking**: Strategic milestone-based project completion

### 🔧 **Smart Context Loading**
- **Three-Tier Context Modes**: theme-focused → theme-expanded → project-wide
- **Database-Enhanced Performance**: SQLite-powered relationship tracking
- **Intelligent File Discovery**: Load only what's needed for each task
- **Memory Optimization**: Efficient context management for large projects

### 🚀 **Developer Experience**
- **Anti-Placeholder Protocol**: Complete implementations, no TODO stubs
- **Automatic File Modularization**: Keep files under configurable line limits
- **Quality Assurance**: Built-in validation and cross-reference checking
- **Git Integration**: Native Git merge capabilities for parallel development

## Architecture

AI Project Manager uses a hybrid file-database architecture:

```
AI Project Manager
├── MCP Server (Python)           # Core intelligence engine
├── Core Systems                  # Task processing, context loading
├── Database Layer               # SQLite for relationships & analytics  
├── Tools & APIs                 # MCP-compliant tool interfaces
├── Directive System             # Multi-tier guidance system
└── Managed Projects             # Auto-generated project structure
    └── projectManagement/
        ├── ProjectBlueprint/    # High-level project understanding
        ├── ProjectFlow/         # User experience flows by domain
        ├── Themes/              # Auto-discovered project themes
        ├── Tasks/               # Active and archived task management
        ├── Implementations/     # Strategic implementation plans
        └── Database/            # Project-specific SQLite database
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Python 3.13+ recommended)
- **Git** (required for project tracking, branch management, and change detection)
- **SQLite 3.x** (included with Python)

### Dependencies

The project includes all Python dependencies in the `ai-pm-mcp/deps/` directory:

- **mcp>=1.0.0** - Model Context Protocol framework
- **pydantic>=2.0.0** - Data validation and serialization
- **aiofiles>=23.0.0** - Async file operations
- **click>=8.0.0** - Command-line interface
- **typing-extensions>=4.0.0** - Extended typing support
- **Additional dependencies**: See `ai-pm-mcp/deps/` for complete list

### 🚀 Simple Installation (Recommended)

```bash
# Option 1: Clone the repository
git clone https://github.com/aryanduntley/AIProjectManager.git
cd AIProjectManager

# Option 2: Download and extract the ZIP file
# Download from GitHub releases or repository

# Move the ai-pm-mcp directory to your desired location
mv ai-pm-mcp /path/to/your/preferred/location/
cd /path/to/your/preferred/location/ai-pm-mcp

# Run the server (all dependencies are bundled)
python3 start-mcp-server.py
```

### Alternative Startup Methods

```bash
# Navigate to the ai-pm-mcp directory
cd path/to/ai-pm-mcp

# Option 1: Using Python launcher (recommended)
python3 start-mcp-server.py

# Option 2: Using bash script
./start-mcp-server.sh

# Option 3: Direct execution
python3 server.py
```

### ✅ That's it!

The server will:
- ✨ Automatically set up all dependencies
- 🔧 Configure the Python environment  
- 🚀 Start the MCP server ready for Claude
- 📝 Display connection status and logs

### Basic Usage

1. **Start the MCP Server**:
   ```bash
   cd ai-pm-mcp
   python3 start-mcp-server.py
   ```

2. **Initialize a New Project** (via MCP tools):
   - The server provides MCP tools for project initialization
   - Connect with Claude or compatible AI client
   - Use the project management tools to set up your project structure

3. **Connect with Claude Code**:
   Add the following configuration to your `~/.claude.json` file:
   ```json
   "mcpServers": {
     "ai-project-manager": {
       "command": "python3",
       "args": ["-m", "server"],
       "cwd": "/path/to/your/ai-pm-mcp/"
     }
   }
   ```
   
   **Important**: Replace `/path/to/your/ai-pm-mcp/` with the actual path to your ai-pm-mcp directory.
   
   **Note**: Use the `-m server` module approach rather than `start-mcp-server.py` to avoid Python import issues.

4. **Restart Claude Code** to load the MCP server connection.

5. **Start Managing Your Project**:
   ```
   AI: "Continue development on this project"
   #  AI automatically loads project context and resumes work
   ```

### Testing the Installation

```bash
# Test basic functionality
python3 test_basic.py

# The server will start and show connection info
```

### Troubleshooting Claude Code Integration

**Problem**: "1 MCP server failed" message in Claude Code

**Solution**: Ensure you're using the module approach in your `~/.claude.json`:
```json
"args": ["-m", "server"]
```
**Not**: `"args": ["start-mcp-server.py"]`

**Why**: The module approach (`-m server`) properly resolves Python relative imports, while running the script directly can cause import failures.

**Steps to Fix**:
1. Update your `~/.claude.json` configuration as shown above
2. Restart Claude Code completely
3. Check that the MCP server loads without errors

## 🚀 Documentation

### Core Concepts

- **[Project Blueprint](ai-pm-mcp/reference/organization.md#projectblueprint)**: The canonical project understanding
- **[Theme System](ai-pm-mcp/reference/organization.md#themes)**: Automatic project component discovery
- **[Multi-Flow Architecture](ai-pm-mcp/reference/organization.md#projectflow)**: Domain-organized user experience flows
- **[Task Management](ai-pm-mcp/reference/directivesmd/06-task-management.md)**: Hierarchical task and sidequest system
- **[Branch Management](ai-pm-mcp/reference/directivesmd/14-branch-management.md)**: Git branch-based parallel development

### Implementation Guides

- **[Installation & Setup](ai-pm-mcp/reference/directivesmd/01-system-initialization.md)**
- **[Project Initialization](ai-pm-mcp/reference/directivesmd/02-project-initialization.md)**
- **[Session Management](ai-pm-mcp/reference/directivesmd/03-session-management.md)**
- **[Context Loading Strategies](ai-pm-mcp/reference/directivesmd/05-context-loading.md)**
- **[Quality Assurance](ai-pm-mcp/reference/directivesmd/11-quality-assurance.md)**

### Advanced Features

- **[Database Integration](ai-pm-mcp/reference/directivesmd/database-integration.md)**: Hybrid file-database architecture
- **[Git Integration](ai-pm-mcp/reference/directivesmd/15-git-integration.md)**: Code change detection and native Git merge
- **[Performance Optimization](ai-pm-mcp/core/performance_optimizer.py)**: Memory and processing optimization

## 🚀 Available MCP Tools

The AI Project Manager exposes these tools through the MCP protocol:

### Project Management Tools
- **`project_initialize`**: Initialize project management structure
- **`project_get_blueprint`**: Get current project blueprint  
- **`project_update_blueprint`**: Update project blueprint
- **`project_get_status`**: Get project status and structure info

### Task Management  
- **`task_create`**: Create new tasks with milestone integration
- **`task_get_active`**: Get active tasks and sidequests
- **`task_update_status`**: Update task progress and status
- **`sidequest_create`**: Create tangential work sidequests

### Context Loading
- **`context_load_theme`**: Load theme-based context
- **`context_escalate`**: Escalate to broader context
- **`context_get_flows`**: Get relevant user experience flows

### Branch Management
- **`create_instance_branch`**: Create parallel development branch with user attribution
- **`merge_instance_branch`**: Merge branch changes using native Git merge
- **`list_instance_branches`**: List active work branches with user info

### Configuration Tools
- **`get_config`**: Get current configuration settings
- **`read_file`**: Read files with project awareness

## Configuration

### User Settings

Create a `projectManagement/UserSettings/config.json`:

```json
{
  "project": {
    "maxFileLineCount": 900,
    "avoidPlaceholders": true,
    "backwardsCompatibility": false
  },
  "tasks": {
    "maxActiveSidequests": 3,
    "resumeTasksOnStart": true,
    "parallelTasksEnabled": true
  },
  "contextLoading": {
    "defaultMode": "theme-focused",
    "maxFlowFiles": 5,
    "readmeFirst": true
  },
  "git": {
    "enabled": true,
    "autoInitRepo": true,
    "codeChangeDetection": true
  },
  "branchManagement": {
    "enabled": true,
    "maxActiveBranches": 10,
    "mainBranchAuthority": true
  }
}
```

### MCP Server Configuration

The server uses configuration files in this priority order:
1. `config.json` in current directory
2. `~/.ai-project-manager/config.json`
3. `/etc/ai-project-manager/config.json`
4. Environment variables (AI_PM_*)
5. Built-in defaults

#### Environment Variables

- **`AI_PM_DEBUG`**: Enable debug mode (true/false)
- **`AI_PM_MAX_FILE_LINES`**: Maximum lines per file (default: 900)
- **`AI_PM_LOG_LEVEL`**: Logging level (default: INFO)
- **`AI_PM_LOG_RETENTION`**: Log retention days (default: 30)

#### Server Configuration

The server auto-configures based on your project needs, but you can customize:

```python
# ai-pm-mcp/server.py
SERVER_CONFIG = {
    "max_concurrent_sessions": 5,
    "context_cache_size": "500MB",
    "database_backup_interval": "1h",
    "cleanup_archives_older_than": "90d"
}
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/aryanduntley/AIProjectManager.git
cd AIProjectManager

# Dependencies are bundled in ai-pm-mcp/deps/
# Add to Python path or install manually
cd ai-pm-mcp
export PYTHONPATH="$PWD/deps:$PYTHONPATH"

# Install additional development dependencies (optional)
pip install pytest pytest-asyncio  # For testing

# Run tests
python test_comprehensive.py
python test_database_infrastructure.py
python test_directive_escalation.py

# Run specific test suites
python -m pytest tests/ -v  # If pytest installed
```

### Project Structure

```
AIProjectManager/
├── ai-pm-mcp/                    # Core MCP server implementation
│   ├── core/                     # Core processing engines (scope, git, branch management)
│   ├── database/                 # SQLite integration with performance optimization
│   ├── tools/                    # MCP tool implementations (tasks, themes, sessions)
│   ├── deps/                     # Bundled Python dependencies (mcp, pydantic, etc.)
│   ├── reference/                # Directive system and templates
│   │   ├── directives/           # JSON directive specifications
│   │   └── templates/            # Project templates and examples
│   ├── core-context/             # Compressed directives for efficiency
│   ├── schemas/                  # JSON schema definitions  
│   ├── tests/                    # Comprehensive test suite
│   ├── start-mcp-server.py       # Main startup script
│   ├── start-mcp-server.sh       # Bash startup script
│   ├── server.py                 # Main MCP server entry point
│   └── test_basic.py             # Basic functionality tests
├── docs/                         # Documentation
│   ├── directives/               # Detailed implementation guides (Markdown)
│   └── *.md                      # Implementation plans and guides
└── test_*.py                     # Integration and system tests
```


## 🚀 Performance & Scalability

- **Memory Efficient**: Selective context loading keeps memory usage under 2GB
- **Database Optimized**: SQLite with performance indexes for large projects
- **Scalable Architecture**: Handles projects with 1000+ files efficiently
- **Session Persistence**: Complete state restoration in <2 seconds

## Security & Privacy

- **Local First**: All data stored locally, no external dependencies
- **Git Integration**: Full version control integration for change tracking
- **Audit Trail**: Complete operation logging for transparency
- **Sandboxed Execution**: Isolated project workspaces

## Development Status

### ✅ Completed
- Basic MCP server framework
- Configuration management with environment variables
- Project initialization tools
- Tool registry system
- Database integration with SQLite
- Theme management and auto-discovery
- Task management with sidequest support
- Session management and persistence
- Git integration with branch management
- Multi-flow architecture

### 🚧 In Progress
- Advanced context loading optimization
- Analytics dashboard
- Performance optimization
- Team collaboration features

### 📋 Planned
- Web dashboard for project monitoring
- Enhanced analytics and insights
- Plugin system for custom tools
- Cloud synchronization options

## 🚀 Roadmap

### v1.0 (Current)
- Core MCP server implementation
- Theme-based project organization
- Multi-flow architecture
- Database integration
- Git branch management system

### v1.1 (Next Release)
- npm package distribution
- Web dashboard for project monitoring
- Enhanced analytics and insights
- Plugin system for custom tools

### v2.0 (Future)
- Multi-project workspace management
- Team collaboration features
- 📋 Cloud synchronization options
- Visual project flow editor

## Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/aryanduntley/AIProjectManager/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/aryanduntley/AIProjectManager/discussions)
- **Documentation**: [Project Wiki](https://github.com/aryanduntley/AIProjectManager/wiki)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the foundational architecture
- [Anthropic](https://anthropic.com/) for Claude AI integration capabilities
- The open-source community for inspiration and best practices

---

**Ready to revolutionize your AI-powered development workflow?** 

[Get Started](#quick-start) | [Join Community](https://github.com/aryanduntley/AIProjectManager/discussions)

---

*AI Project Manager - Enabling autonomous AI development for complex software projects*