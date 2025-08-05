# System Initialization Directives

> **Note**: Throughout this document, `$$projectManagement` refers to the configurable project management folder name (defaults to "$projectManagement").

## Overview

This directive ensures proper system initialization with Git integration, instance management, and database setup. The initialization process establishes the foundation for Git-like instance management while maintaining backward compatibility with existing projects.

**Key Triggers**: MCP server startup, first connection, system boot, session start, instance initialization, Git repository setup needed

## 1.1 Automatic State Detection and Notification

**Directive**: Upon MCP server connection, immediately analyze project state using optimized two-tier system and make it available to user via MCP tools.

**Critical Requirement**: State analysis must be stored during server initialization and made available through get_project_state_analysis MCP tool.

**Optimized Two-Tier Analysis System**:

### 🚀 Fast Path (~100ms) - 95% Performance Improvement
**When Used**: Existing projects with stable `$projectManagement/` structure
**Conditions**:
- `$projectManagement/` directory exists
- Cached state available in `metadata.json`
- Cache age < 24 hours
- No Git repository changes detected

**Process**:
1. Read cached state from `ProjectBlueprint/metadata.json`
2. Quick Git hash comparison (`git rev-parse HEAD`)
3. Verify key components exist (blueprint.md, themes.json, flow-index.json)
4. Return cached analysis with fast path indicator

### 🔍 Comprehensive Path (~2-5s) - When Needed
**When Used**: New projects or when changes detected
**Conditions**:
- No `$projectManagement/` directory
- No cached state available
- Git repository changes detected
- Cache expired (>24 hours)
- User requests `force_full_analysis: true`

**Process**:
1. Full Git repository state analysis
2. Complete component structure analysis  
3. Software project indicator detection
4. Generate comprehensive state categorization
5. Cache results in metadata for future fast path

**MCP Communication Protocol**:
- **User Notification**: All user communication must be via MCP tool responses, never stderr/stdout
- **State Analysis**: Provide state analysis through dedicated MCP tools
- **User Choice Handling**: Implement MCP tools for processing user choices  
- **No Auto Execution**: Never execute actions without explicit user choice through MCP tools

**Implementation**:
```
1. Detect current project directory and structure
2. Check for $projectManagement/ directory existence and completeness
3. Analyze component status (blueprint, themes, flows, database, tasks)
4. Categorize state: none/partial/complete/unknown
5. Store formatted state analysis in server for MCP tool access
6. Provide clear next-step options based on current state
7. Wait for user choice via make_initialization_choice MCP tool before proceeding with any actions
```

**Required MCP Tools**:
- `get_project_state_analysis`: Returns formatted state analysis and available options
  - New parameter: `force_full_analysis: boolean` (default: false)
- `make_initialization_choice`: Processes user's choice and executes appropriate action

**Cache Structure** (stored in `ProjectBlueprint/metadata.json`):
```json
{
  "cached_state": {
    "state": "complete",
    "details": {...},
    "git_analysis": {...},
    "last_updated": "2024-01-15T10:30:00Z",
    "last_git_hash": "abc123def456"
  }
}
```

**Cache Management**:
- **Duration**: 24 hours for stable projects
- **Invalidation**: Git hash changes, component file deletions, cache corruption
- **Storage**: `$projectManagement/ProjectBlueprint/metadata.json`
- **Auto-Refresh**: Comprehensive analysis automatically updates cache

**State Categories and Responses**:

**No Project Structure**: 
- Message: "No project management structure found"
- Options: Initialize new project, Review project status, Check existing code

**Partial Project Structure**:
- Message: Show existing/missing components with status indicators
- Options: Complete initialization, Review current state, Continue with existing

**Complete Project Structure**:
- Message: Show component summary and task counts
- Options: Get detailed status, Start/resume session, View active tasks

**Unknown State**:
- Message: "Could not determine project state"
- Options: Manual analysis, Force initialization, Check logs

**Output Format**: State analysis and user options are available via MCP tools, ensuring proper protocol compliance.

## 1.2 MCP Server Connection Protocol

**Directive**: Always verify MCP server connectivity and tool availability before beginning any project work.

**Implementation**:
```
1. Check MCP server status
2. Verify all required tools are available:
   - project_initialize, project_get_blueprint, project_update_blueprint, project_get_status
   - theme_discover, theme_create, theme_list, theme_get, theme_update, theme_delete, theme_get_context, theme_validate
   - instance_create, instance_list, instance_status, instance_merge, instance_archive
   - detect_conflicts, resolve_conflicts
   - get_config, read_file
3. Load server configuration and validate settings
4. Confirm project management structure exists or initialize if needed
```

**Critical New Tools**:
- **Instance Management Tools**: Required for Git-like workflow support
- **Conflict Resolution Tools**: Essential for instance merge operations

## 1.2 Project Detection and Compatibility

**Directive**: Always detect existing project management structures and handle compatibility issues.

**Rules**:
- If `$projectManagement/` exists, check version compatibility
- If compatible, integrate existing data
- If incompatible, ask user for migration approach (upgrade, backup, or overwrite)
- Never overwrite existing data without explicit user permission
- Document any compatibility issues or migrations performed

## 1.3 Configuration Loading Protocol

**Directive**: Load configuration in this priority order:
1. Project-specific `$projectManagement/.ai-pm-config.json`
2. Current directory `config.json`
3. User home `~/.ai-project-manager/config.json`
4. System-wide `/etc/ai-project-manager/config.json`
5. Environment variables (AI_PM_*)
6. Built-in defaults

**Critical Settings**:
- `max_file_lines` (default: 900)
- `auto_modularize` (default: true)
- `theme_discovery` (default: true)
- Log retention policies
- Context loading preferences

## 1.4 Compatibility Verification

**Directive**: Verify compatibility of existing `$projectManagement/` structures and handle version differences.

**Required metadata.json fields for compatibility verification:**
- `mcp.version`: MCP system version used to create the structure
- `mcp.namespace`: Unique project identifier (project.management.organization.{userprojectname})
- `mcp.created`: ISO timestamp of initial structure creation
- `mcp.compatibilityVersion`: Version for backward compatibility checking

**Compatibility check process:**
1. Check if `$projectManagement/ProjectBlueprint/metadata.json` exists
2. Read `mcp.version` and `mcp.compatibilityVersion` fields
3. Compare with current MCP version
4. If version is lesser than current, ask user if they want to update existing structure
5. Files themselves should not need significant modification - updates should be backwards compatible

**Template available:** `reference/templates/metadata.json` includes all required MCP compatibility fields

**Update process:**
1. With any updates, directives will be added on how to approach updating outdated versions
2. Handle update according to provided update directives
3. Ask user if they want to run an initial complete evaluation which will compare the current state of the entire project to the $projectManagement state
4. If yes, make updates to files according to analysis. Always assess existing files for each step of analyzing before making updates, if updates are needed
5. Finally, continue with $projectManagement as normal

## 1.5 Git Repository Setup

**Directive**: Initialize and configure Git repository for project code and organizational state tracking.

**Git Repository Detection**:
1. Check if project root has existing Git repository (.git/ directory)
2. Verify Git repository integrity if found
3. Check Git configuration compatibility with MCP branch management

**Git Repository Initialization** (if needed and `git.auto_init_repo=true`):
1. Run `git init` in project root
2. Set up initial .gitignore for MCP branch management
3. Create initial commit with project structure

**Git Configuration for MCP**:
Update .gitignore with MCP-specific rules:
```gitignore
# Project Management - Track Organizational State, Not User Data
# $projectManagement/.ai-pm-config.json is tracked (branch-protected configuration)
$projectManagement/database/backups/
$projectManagement/.mcp-session-*

# Temporary Files
*.tmp
.ai-pm-temp/
```

**Git State Recording**:
- Insert initial git_project_state record in database
- Record current Git hash as baseline for change detection
- Set reconciliation status to 'initialized'

## 1.6 Instance Identification

**Directive**: Identify whether running in main instance or branch instance and establish authority.

**Instance Type Detection**:
- **Main Instance**: Look for `.mcp-instance-main` file in `$projectManagement/`
- **Branch Instance**: Look for `.mcp-branch-info.json` in workspace directory
- **Workspace Path**: Determine location to confirm instance type

**Authority Establishment**:

**Main Instance Authority** (Primary Decision Maker):
- Git repository change detection authority
- Merge conflict resolution primary decision maker
- Instance coordination and management
- Project code change impact assessment

**Branch Instance Capabilities** (Isolated Development):
- Independent development within isolated workspace
- Prepare organizational changes for merge
- Maintain instance metadata and work summaries

**Instance Configuration Validation**:
- Verify workspace isolation for branch instances
- Check instance metadata completeness (.mcp-branch-info.json)
- Validate database isolation for branch instances
- Confirm main instance authority if main

## 1.7 Database Initialization

**Directive**: Initialize database components and establish hybrid file-database architecture.

**Database Setup Process**:
1. **Create project.db** from `ai-pm-mcp/database/schema.sql`
2. **Initialize all required tables and indexes** for performance
3. **Set up database triggers** for real-time file-database synchronization
4. **Create performance optimization views** for fast queries

**Hybrid Architecture Configuration**:
- **Real-time synchronization**: File updates trigger database updates atomically
- **Session persistence**: Complete session context preservation and restoration
- **Event analytics**: Real-time event logging for pattern analysis
- **Performance optimization**: Fast context loading and intelligent recommendations

**Database Integrity Validation**:
- Test all database tables and relationships
- Verify trigger functionality for sync operations
- Test atomic operation rollback capabilities
- Confirm performance index effectiveness

## Configuration Settings

### Git Integration Settings
```json
{
  "git": {
    "enabled": true,
    "auto_init_repo": true,
    "code_change_detection": true,
    "auto_reconcile_on_boot": true
  }
}
```

### Instance Management Settings
```json
{
  "instance_management": {
    "enabled": true,
    "main_instance_authority": true,
    "max_active_instances": 10,
    "instance_naming_validation": true,
    "auto_archive_completed": true
  }
}
```

### Database Integration Settings
```json
{
  "database": {
    "enabled": true,
    "real_time_sync": true,
    "session_persistence": true
  }
}
```

## Error Handling

### Git Repository Issues
- **Missing Repository**: Initialize if `auto_init_repo` enabled, otherwise report clear error
- **Repository Corruption**: Attempt repair and report status to user
- **Permission Issues**: Provide clear error message with resolution steps

### Instance Identification Failures
- **Unknown Instance Type**: Default to main instance and warn user
- **Authority Conflicts**: Enforce main instance authority and log conflict
- **Metadata Issues**: Create missing metadata with defaults

### Database Initialization Failures
- **Schema Errors**: Report error clearly and offer file-only mode
- **Permission Issues**: Check file permissions and suggest fixes
- **Corruption**: Attempt recovery or reinitialize with user approval

## Integration Points

This directive integrates with:
- **02-project-initialization**: Project structure setup
- **03-session-management**: Git-aware session boot
- **13-metadata-management**: Compatibility verification  
- **14-instance-management**: Instance authority establishment
- **15-git-integration**: Repository configuration
- **database-integration**: Hybrid architecture setup

## User Communication Guidelines

### MCP Tool Responses

**Initialization State Analysis** (via `get_project_state_analysis`):
```json
{
  "type": "state_analysis",
  "state": "partial",
  "message": "Project partially initialized",
  "details": {
    "existing_components": ["blueprint", "themes"],
    "missing_components": ["database", "flow_index"],
    "completeness_ratio": 0.6
  },
  "options": [
    "complete_initialization",
    "review_state", 
    "continue_existing"
  ]
}
```

**Initialization Choice Response** (via `make_initialization_choice`):
```json
{
  "type": "success",
  "action": "project_initialization",
  "message": "Project initialized successfully",
  "result": {
    "components_created": ["database", "flow_index"],
    "git_repository": "initialized",
    "ready_for_session": true
  }
}
```

**Error Communication** (via MCP tool responses):
```json
{
  "type": "error",
  "action": "database_initialization",
  "message": "Failed to initialize database",
  "details": {
    "issue": "Permission denied creating project.db",
    "solution": "Check file permissions in $projectManagement/",
    "alternative": "Continue with file-only mode"
  }
}
```

This enhanced system initialization directive ensures robust foundation for Git-like instance management while maintaining backward compatibility and user-friendly error handling.