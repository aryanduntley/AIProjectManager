# System Initialization Directives

## 1.1 MCP Server Connection Protocol

**Directive**: Always verify MCP server connectivity and tool availability before beginning any project work.

**Implementation**:
```
1. Check MCP server status
2. Verify all required tools are available:
   - project_initialize, project_get_blueprint, project_update_blueprint, project_get_status
   - theme_discover, theme_create, theme_list, theme_get, theme_update, theme_delete, theme_get_context, theme_validate
   - get_config, read_file
3. Load server configuration and validate settings
4. Confirm project management structure exists or initialize if needed
```

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