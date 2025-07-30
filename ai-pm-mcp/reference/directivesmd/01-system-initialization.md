# System Initialization Directives

## Overview

This directive ensures proper system initialization with Git integration, instance management, and database setup. The initialization process establishes the foundation for Git-like instance management while maintaining backward compatibility with existing projects.

**Key Triggers**: MCP server startup, first connection, system boot, session start, instance initialization, Git repository setup needed

## 1.1 Automatic State Detection and Notification

**Directive**: Upon MCP server connection, immediately analyze project state and notify user with next-step options without waiting for user request.

**Critical Requirement**: This must happen automatically during server initialization, not when the user first asks for something.

**Implementation**:
```
1. Detect current project directory and structure
2. Check for projectManagement/ directory existence and completeness
3. Analyze component status (blueprint, themes, flows, database, tasks)
4. Categorize state: none/partial/complete/unknown
5. Present formatted state analysis directly to user via stderr
6. Provide clear next-step options based on current state
7. Wait for user choice before proceeding with any actions
```

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

**Output Format**: Use stderr for user notifications to avoid interfering with MCP protocol on stdout.

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
- If `projectManagement/` exists, check version compatibility
- If compatible, integrate existing data
- If incompatible, ask user for migration approach (upgrade, backup, or overwrite)
- Never overwrite existing data without explicit user permission
- Document any compatibility issues or migrations performed

## 1.3 Configuration Loading Protocol

**Directive**: Load configuration in this priority order:
1. Project-specific `projectManagement/UserSettings/config.json`
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

**Directive**: Verify compatibility of existing `projectManagement/` structures and handle version differences.

**Required metadata.json fields for compatibility verification:**
- `mcp.version`: MCP system version used to create the structure
- `mcp.namespace`: Unique project identifier (project.management.organization.{userprojectname})
- `mcp.created`: ISO timestamp of initial structure creation
- `mcp.compatibilityVersion`: Version for backward compatibility checking

**Compatibility check process:**
1. Check if `projectManagement/ProjectBlueprint/metadata.json` exists
2. Read `mcp.version` and `mcp.compatibilityVersion` fields
3. Compare with current MCP version
4. If version is lesser than current, ask user if they want to update existing structure
5. Files themselves should not need significant modification - updates should be backwards compatible

**Template available:** `reference/templates/metadata.json` includes all required MCP compatibility fields

**Update process:**
1. With any updates, directives will be added on how to approach updating outdated versions
2. Handle update according to provided update directives
3. Ask user if they want to run an initial complete evaluation which will compare the current state of the entire project to the projectManagement state
4. If yes, make updates to files according to analysis. Always assess existing files for each step of analyzing before making updates, if updates are needed
5. Finally, continue with projectManagement as normal

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
projectManagement/UserSettings/
projectManagement/database/backups/
projectManagement/.mcp-session-*

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
- **Main Instance**: Look for `.mcp-instance-main` file in `projectManagement/`
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

### Initialization Progress
```
🔧 System Initialization
✅ MCP server connection verified
✅ Git repository detected/initialized  
✅ Instance type: Main (authority established)
✅ Database initialized with complete schema
✅ Ready for project operations
```

### Error Communication
```
❌ Database initialization failed
   Issue: Unable to create project.db
   Solution: Check file permissions in projectManagement/
   Alternative: Continue with file-only mode (reduced performance)
   Would you like to retry or continue with file-only mode?
```

### Configuration Updates
```  
🔄 Configuration Update Detected
   Previous version: 1.0.0
   Current version: 1.1.0
   Changes: Added Git integration and instance management
   
   Update recommended for full functionality.
   Update project structure? (Y/n)
```

This enhanced system initialization directive ensures robust foundation for Git-like instance management while maintaining backward compatibility and user-friendly error handling.