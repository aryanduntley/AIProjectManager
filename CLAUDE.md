# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Project Manager is a Model Context Protocol (MCP) server that provides intelligent, persistent project management for AI-assisted software development. It uses a hybrid file-database architecture with SQLite for performance and maintains project context across sessions.

## Core Architecture

The system is built around several key concepts:

- **MCP Server**: Python-based server (`ai-pm-mcp/server.py`) that exposes 65+ tools via Model Context Protocol
- **Directive System**: JSON-based multi-tier guidance system that provides contextual intelligence
- **Hybrid Storage**: File-based project structure + SQLite database for relationships and analytics
- **3-Branch Git Model**: user-main ↔ ai-pm-org-main ↔ ai-pm-org-branch-{XXX} for safe collaboration

### Key Directories

- `ai-pm-mcp/` - Core MCP server implementation (production version)
- `ai-pm-mcp-production/` - Alternative production directory structure  
- `ai-pm-mcp/core/` - Core processing engines (processors, git integration, branch management)
- `ai-pm-mcp/database/` - SQLite integration with optimized queries
- `ai-pm-mcp/tools/` - MCP tool implementations organized by domain
- `ai-pm-mcp/reference/` - Directive system specifications and templates
- `projectManagement/` - Auto-generated project management structure (created in any project using this tool)

### Core Components

- **DirectiveProcessor**: Executes multi-step workflows based on context triggers
- **ActionExecutor**: Handles database operations and file modifications
- **GitBranchManager**: Manages 3-branch architecture with safety validation
- **ProjectStateAnalyzer**: Analyzes project state and recommends actions
- **MCPToolRegistry**: Registers and manages all MCP tools

## Development Commands

### Running the MCP Server
```bash
# Primary method (from any directory with ai-pm-mcp in Python path)
python3 -m ai-pm-mcp

# Alternative methods (from ai-pm-mcp directory)
python3 start-mcp-server.py
./start-mcp-server.sh
```

### Testing
```bash
# Basic functionality test
python3 ai-pm-mcp/tests/test_basic.py

# Comprehensive test suite  
python3 ai-pm-mcp/tests/test_comprehensive.py

# Specific system tests
python3 ai-pm-mcp/tests/test_database_infrastructure.py
python3 ai-pm-mcp/tests/test_directive_integration.py
python3 ai-pm-mcp/tests/test_theme_system.py
python3 ai-pm-mcp/tests/test_mcp_integration.py

# Root level integration tests
python3 test_directive_escalation.py
python3 test_file_metadata.py
python3 test_multiflow_integration.py
python3 test_help.py
```

### No Build/Lint Commands
This is a Python project with bundled dependencies in `ai-pm-mcp/deps/`. No separate build step or package manager is required.

## AI Project Manager Commands

When working with this codebase, these commands provide workflow-level automation:

### Essential Commands
- `/aipm-status` - Get current project state and next steps
- `/aipm-init` - Initialize AI project management 
- `/aipm-resume` - Resume previous work and active tasks
- `/aipm-help` - Show all available commands

### Development Workflow
- `/aipm-branch` - Create work branch for parallel development
- `/aipm-merge` - Merge completed work back to ai-pm-org-main
- `/aipm-deploy` - Deploy improvements to user's main branch
- `/aipm-pause` - Find stopping point and prepare for resumption

### Project Analysis  
- `/aipm-analyze` - Full project analysis and theme discovery
- `/aipm-themes` - Show discovered project themes and organization
- `/aipm-flows` - Show user experience flows

## Technical Implementation Notes

### Database Schema
The system uses SQLite with these key tables:
- `sessions` - Session lifecycle and context tracking
- `events` - All project events with timestamps  
- `tasks` - Task management with hierarchical structure
- `file_metadata` - File analysis and relationship tracking
- `themes` - Project theme discovery and organization

### Directive System
Located in `ai-pm-mcp/reference/directives/`, this provides multi-tier guidance:
- System initialization and project setup
- Context loading strategies (theme-focused → theme-expanded → project-wide)
- Task management with sidequest support
- Git integration with safety validation
- Quality assurance and validation

### Git Safety Features
- Repository type detection (fork/clone/original)
- Workflow safety validation with dangerous operation blocking
- Pull request automation using GitHub CLI when available
- Branch ancestry validation and auto-switching
- Team collaboration support with proper attribution

### Performance Optimizations
- **Lightning-fast session boot**: 95% performance improvement for existing projects
- **Smart caching**: Git hash-based change detection with 24-hour cache validity
- **Selective context loading**: Memory usage kept under 2GB
- **Database optimization**: Performance indexes for projects with 1000+ files

### Testing Philosophy
Tests cover:
- Basic functionality without MCP client requirements
- Database infrastructure and migration integrity
- Directive integration and execution flows
- Theme discovery and organization
- MCP tool registration and execution

### Configuration
Settings managed via `.ai-pm-config.json` in project management folder:
- `maxFileLineCount`: 900 (auto-modularization threshold)
- `avoidPlaceholders`: true (complete implementations, no TODOs)
- Context loading modes: theme-focused (default) → theme-expanded → project-wide

## Working with This Codebase

### Making Changes
1. Understand the modular architecture - each tool is self-contained
2. Follow the directive system patterns for multi-step operations
3. Use the database for persistent state, files for human-readable data
4. Test changes with the comprehensive test suite
5. Consider performance implications for large projects

### Adding New Features
1. Create MCP tools in appropriate `tools/` subdirectory
2. Add database schema changes to `database/migrations/`
3. Update directive specifications in `reference/directives/`
4. Add comprehensive tests for new functionality
5. Update command reference in COMMANDS.md if needed

### File Organization Principles
- Keep files under 900 lines (auto-modularization)
- Separate concerns: core logic, database operations, MCP interfaces
- Use descriptive module names that reflect their purpose
- Maintain consistency with existing naming patterns

This project prioritizes intelligent automation, session continuity, and safe collaborative development workflows.