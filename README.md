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
- **Parallel Development**: Git-like instance management for team collaboration
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
- **Conflict Resolution**: Advanced merge strategies for parallel development

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
- **Git** (required for project tracking, instance management, and change detection)
- **SQLite 3.x** (included with Python)

### Dependencies

The project includes all Python dependencies in the `mcp-server/deps/` directory:

- **mcp>=1.0.0** - Model Context Protocol framework
- **pydantic>=2.0.0** - Data validation and serialization
- **aiofiles>=23.0.0** - Async file operations
- **click>=8.0.0** - Command-line interface
- **typing-extensions>=4.0.0** - Extended typing support
- **Additional dependencies**: See `mcp-server/deps/` for complete list

### Installation

#### Option 1: Clone and Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/AIProjectManager.git
cd AIProjectManager

# Dependencies are bundled in mcp-server/deps/
# Verify Python can access them
cd mcp-server
python -c "import sys; sys.path.insert(0, 'deps'); import mcp; print('✓ Dependencies loaded')"

# Initialize the MCP server
python server.py --help
```

#### Option 2: Install Dependencies Manually

```bash
# If you prefer to install dependencies separately
cd AIProjectManager/mcp-server
pip install -r requirements.txt

# Run the server
python server.py
```

#### Option 3: npm Package (Recommended for Easy Installation)

```bash
# Install as a global npm package
npm install -g .

# Or install locally from the project directory
npm install

# Initialize in your project
ai-pm init

# Start the MCP server
ai-pm start
```

### Basic Usage

1. **Initialize a New Project**:
   ```bash
   # Using npm wrapper (recommended)
   ai-pm init /path/to/your/project
   
   # Or using Python directly
   python mcp-server/server.py --init /path/to/your/project
   ```

2. **Start the MCP Server**:
   ```bash
   # Using npm wrapper
   ai-pm start
   
   # Or using Python directly
   python mcp-server/server.py
   ```

3. **Connect with Claude or Compatible AI**:
   - Configure your AI client to connect to the MCP server
   - The server exposes tools for project management, task execution, and context loading

4. **Start Managing Your Project**:
   ```
   AI: "Continue development on this project"
   #  AI automatically loads project context and resumes work
   ```

## 🚀 Documentation

### Core Concepts

- **[Project Blueprint](docs/organization.md#projectblueprint)**: The canonical project understanding
- **[Theme System](docs/organization.md#themes)**: Automatic project component discovery
- **[Multi-Flow Architecture](docs/organization.md#projectflow)**: Domain-organized user experience flows
- **[Task Management](docs/directives/06-task-management.md)**: Hierarchical task and sidequest system
- **[Instance Management](docs/directives/14-instance-management.md)**: Git-like parallel development

### Implementation Guides

- **[Installation & Setup](docs/directives/01-system-initialization.md)**
- **[Project Initialization](docs/directives/02-project-initialization.md)**
- **[Session Management](docs/directives/03-session-management.md)**
- **[Context Loading Strategies](docs/directives/05-context-loading.md)**
- **[Quality Assurance](docs/directives/11-quality-assurance.md)**

### Advanced Features

- **[Database Integration](docs/directives/database-integration.md)**: Hybrid file-database architecture
- **[Git Integration](docs/directives/16-git-integration.md)**: Code change detection and reconciliation
- **[Conflict Resolution](docs/directives/15-conflict-resolution.md)**: Advanced merge strategies
- **[Performance Optimization](mcp-server/core/performance_optimizer.py)**: Memory and processing optimization

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
  "instanceManagement": {
    "enabled": true,
    "maxActiveInstances": 10,
    "mainInstanceAuthority": true
  }
}
```

### MCP Server Configuration

The server auto-configures based on your project needs, but you can customize:

```python
# mcp-server/server.py
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
git clone https://github.com/yourusername/AIProjectManager.git
cd AIProjectManager

# Dependencies are bundled in mcp-server/deps/
# Add to Python path or install manually
cd mcp-server
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
├── mcp-server/                   # Core MCP server implementation
│   ├── core/                     # Core processing engines (scope, git, conflict resolution)
│   ├── database/                 # SQLite integration with performance optimization
│   ├── tools/                    # MCP tool implementations (tasks, themes, sessions)
│   ├── deps/                     # Bundled Python dependencies (mcp, pydantic, etc.)
│   ├── reference/                # Directive system and templates
│   │   ├── directives/           # JSON directive specifications
│   │   └── templates/            # Project templates and examples
│   ├── core-context/             # Compressed directives for efficiency
│   ├── schemas/                  # JSON schema definitions  
│   ├── tests/                    # Comprehensive test suite
│   ├── requirements.txt          # Python dependency list
│   └── server.py                 # Main MCP server entry point
├── docs/                         # Documentation
│   ├── directives/               # Detailed implementation guides (Markdown)
│   └── *.md                      # Implementation plans and guides
└── test_*.py                     # Integration and system tests
```

## =' API Reference

### Core MCP Tools

The AI Project Manager exposes these tools through the MCP protocol:

#### Project Management
- `project_initialize()` - Initialize project structure
- `project_get_blueprint()` - Get project understanding
- `project_update_blueprint()` - Update project direction

#### Task Management  
- `task_create()` - Create new tasks with milestone integration
- `task_get_active()` - Get active tasks and sidequests
- `task_update_status()` - Update task progress and status
- `sidequest_create()` - Create tangential work sidequests

#### Context Loading
- `context_load_theme()` - Load theme-based context
- `context_escalate()` - Escalate to broader context
- `context_get_flows()` - Get relevant user experience flows

#### Instance Management
- `instance_create()` - Create parallel development instance
- `instance_merge()` - Merge instance changes with conflict resolution
- `instance_list()` - List active and completed instances

## 🚀 Performance & Scalability

- **Memory Efficient**: Selective context loading keeps memory usage under 2GB
- **Database Optimized**: SQLite with performance indexes for large projects
- **Scalable Architecture**: Handles projects with 1000+ files efficiently
- **Session Persistence**: Complete state restoration in <2 seconds

##  Security & Privacy

- **Local First**: All data stored locally, no external dependencies
- **Git Integration**: Full version control integration for change tracking
- **Audit Trail**: Complete operation logging for transparency
- **Sandboxed Execution**: Isolated project workspaces

## 🚀 Roadmap

### v1.0 (Current)
- Core MCP server implementation
- Theme-based project organization
- Multi-flow architecture
- Database integration
- Instance management system

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

- **Bug Reports**: [GitHub Issues](https://github.com/yourusername/AIProjectManager/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/AIProjectManager/discussions)
- **Documentation**: [Project Wiki](https://github.com/yourusername/AIProjectManager/wiki)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## =O Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the foundational architecture
- [Anthropic](https://anthropic.com/) for Claude AI integration capabilities
- The open-source community for inspiration and best practices

---

**Ready to revolutionize your AI-powered development workflow?** 

[Get Started](#quick-start) | [View Documentation](docs/) | [Join Community](https://github.com/yourusername/AIProjectManager/discussions)

---

*AI Project Manager - Enabling autonomous AI development for complex software projects*