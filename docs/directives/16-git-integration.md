# Root-Level Git Integration Directives

## Overview

This directive provides comprehensive guidance for integrating root-level Git repository tracking with the AI Project Manager's organizational state. It enables detection of external code changes and automatic reconciliation of organizational structure with project reality.

**Core Purpose**: Bridge the gap between external code changes and internal AI project organization to maintain accurate, up-to-date project understanding.

## When This Directive Applies

### Triggers
- **Session boot with project code changes** - Code modified outside AI sessions
- **Git repository state detection needed** - Initial setup or validation required
- **External code modifications detected** - Files changed by users or other tools
- **Theme impact analysis required** - Code changes affect organizational themes
- **Organizational reconciliation needed** - AI structure needs updating

### Use Cases
- Developer adds new authentication files while AI was offline
- Team member refactors payment system structure
- Build processes generate or modify source files
- External tools create or remove project files
- Git operations (pull, merge, rebase) change project state

## Session Boot Git Detection

### Step 1: Detect Git Repository
**Purpose**: Ensure project root has properly configured Git repository

**Detection Process**:
1. **Check for .git/ directory** in project root
2. **Initialize Git repository** if not found and `auto_init_repo` enabled
3. **Verify Git repository integrity** - check for corruption
4. **Set up Git configuration** for MCP tracking and ignore rules

**AI Action**: Report Git repository status and any initialization actions taken.

**User Communication**: 
```
Git repository detected at project root.
Last tracked state: commit abc123 (2 days ago)
Repository status: Clean, ready for change detection
```

### Step 2: Compare Git State
**Purpose**: Identify if project code changed since last AI session

**Comparison Process**:
1. **Get current Git hash** from HEAD
2. **Retrieve last known hash** from `git_project_state` database table
3. **Determine if changes occurred** by comparing hashes
4. **Generate change summary** if differences found

**Database Query**: 
```sql
SELECT current_git_hash, last_known_hash, last_sync_timestamp 
FROM git_project_state 
WHERE project_root_path = ?
ORDER BY created_at DESC LIMIT 1
```

### Step 3: Analyze Project Code Changes
**Purpose**: Understand scope and nature of external changes

**Analysis Process**:
1. **Get list of changed files** using `git diff --name-status`
2. **Categorize changes** by file type (source, config, docs, etc.)
3. **Calculate impact metrics** (files changed, additions, deletions)
4. **Generate human-readable summary** for user review

**Change Categories**:
- **Source files** - .js, .ts, .py, .java, etc.
- **Configuration** - package.json, requirements.txt, config files
- **Documentation** - README.md, docs/, comments
- **Build artifacts** - Generated files, compiled output
- **Dependencies** - node_modules/, vendor/, lib/

### Step 4: Perform Theme Impact Analysis
**Purpose**: Map code changes to organizational themes for targeted updates

**Impact Analysis Methods**:

#### Direct File Mapping
Map files to themes through explicit theme file references:
1. Load all theme JSON files from `Themes/` directory
2. Check if changed file paths match theme file lists
3. Include themes that explicitly reference the changed files

#### Directory Structure Inference
Infer theme impact from directory structure patterns:
- `auth/` or `authentication/` → authentication, security themes
- `user/` or `users/` → user-management theme
- `payment/` or `billing/` → payment, billing themes
- `api/` → api, backend themes
- `ui/` or `components/` → ui, frontend themes
- `database/` or `db/` → database, data themes
- `admin/` → admin, management themes
- `config/` or `settings/` → configuration theme

#### File Naming Pattern Analysis
Analyze file names for theme keywords:
- Files containing "auth", "login", "signup" → authentication theme
- Files containing "payment", "billing" → payment theme
- Files containing "user", "profile" → user-management theme
- Files containing "api", "middleware" → api theme
- Files containing "config", "setting" → configuration theme
- Files containing "test", "spec" → testing theme

#### Deletion Impact Handling
Special handling for deleted files:
1. Identify themes that referenced deleted files
2. Mark themes for review due to file deletion
3. Update theme file lists to remove deleted files
4. Alert user about themes affected by deletions

## Organizational Reconciliation

### Step 1: Assess Reconciliation Needs
**Purpose**: Determine if and how organizational state should be updated

**Assessment Criteria**:
- **Theme updates needed** - New files require theme assignment
- **Flow revisions required** - Code changes affect user experience flows
- **Task/implementation impact** - Active work affected by changes
- **User notification level** - Automatic vs. approval-required changes

**Decision Matrix**:
- **Auto-reconcile**: File additions to existing themes, non-conflicting updates
- **User approval**: New theme creation, major flow changes, task impacts
- **Manual review**: Multiple possible assignments, structural changes

### Step 2: Update Affected Themes
**Purpose**: Modify theme files to reflect code reality

**Theme Update Process**:
1. **Add new files** to appropriate themes based on impact analysis
2. **Remove deleted files** from theme definitions
3. **Update shared file configurations** if files moved between themes
4. **Validate theme relationships** and dependencies remain intact

**Example Theme Update**:
```json
{
  "theme": "authentication",
  "files": [
    "src/auth/login.js",
    "src/auth/register.js",
    "src/auth/oauth.js",    // <- New file added
    "src/auth/mfa.js"       // <- New file added
  ],
  "linkedThemes": ["user-management", "security", "notifications"]
}
```

### Step 3: Review Flow Impact
**Purpose**: Update flows affected by code changes

**Flow Review Process**:
1. **Check if new files affect user flows** - Do changes alter user experience?
2. **Update flow step references** - Ensure flows reference correct code components
3. **Validate flow completion status** - Are flows still implementable?
4. **Update flow-index if needed** - Add/remove flow references

**Flow Impact Examples**:
- New OAuth files may require new authentication flow steps
- Deleted payment components may break billing flows
- UI changes may require flow user experience updates

### Step 4: Notify User of Changes
**Purpose**: Present changes and AI adaptations for user review and approval

**User Communication Format**:
```
🔄 Git Changes Detected (15 files changed)

Code Changes:
+ src/auth/oauth.js (new OAuth implementation)
+ src/auth/mfa.js (multi-factor authentication)
~ src/auth/login.js (modified login flow)
- src/auth/deprecated.js (removed old auth)

AI Adaptations:
✅ Added OAuth files to 'authentication' theme
✅ Updated authentication flow with OAuth steps
❓ New MFA flow needed - requires approval
❓ Login flow changes may affect user experience

Approve AI adaptations? (Y/n/review)
```

**Approval Levels**:
- **Automatic** - Low-impact additions to existing themes
- **User approval** - New themes, major flow changes, structural modifications
- **Manual review** - Complex changes requiring detailed user guidance

## Git State Tracking

### Step 1: Update Git Project State
**Purpose**: Record current Git state in database for next session

**Database Updates**:
```sql
INSERT INTO git_project_state (
    project_root_path,
    current_git_hash,
    last_known_hash,
    last_sync_timestamp,
    change_summary,
    affected_themes,
    reconciliation_status
) VALUES (?, ?, ?, ?, ?, ?, ?)
```

**Reconciliation Status Values**:
- `pending` - Changes detected, reconciliation not yet started
- `in-progress` - Currently reconciling organizational state
- `completed` - Reconciliation finished successfully
- `failed` - Reconciliation encountered errors, manual intervention needed

### Step 2: Track Individual File Changes
**Purpose**: Maintain detailed change history for analysis and rollback

**File Change Tracking**:
```sql
INSERT INTO git_change_impacts (
    git_state_id,
    file_path,
    change_type,
    affected_themes,
    impact_severity, 
    reconciliation_action,
    reconciliation_status
) VALUES (?, ?, ?, ?, ?, ?, ?)
```

**Change Types**:
- `added` - New file created
- `modified` - Existing file changed
- `deleted` - File removed
- `renamed` - File moved or renamed

**Impact Severity Levels**:
- `low` - Minor change, automatic reconciliation
- `medium` - Moderate change, user notification
- `high` - Significant change, user approval required
- `critical` - Major change, manual review needed

### Step 3: Maintain Change History
**Purpose**: Enable change analysis, rollback, and audit capabilities

**History Preservation**:
- Keep previous `git_project_state` records for analysis
- Enable change trend analysis over time
- Support rollback to previous organizational states
- Provide audit trail for all Git integration actions

**Cleanup Policy**: Archive records older than configurable threshold (default: 90 days)

## Instance Git Integration

### Step 1: Record Instance Git Base
**Purpose**: Track Git state when instance created for merge comparison

**Instance Git Tracking**:
```sql
UPDATE mcp_instances 
SET git_base_hash = ?, 
    created_at = CURRENT_TIMESTAMP
WHERE instance_id = ?
```

**Purpose**: Enable detection of external changes during instance development

### Step 2: Detect Code Changes in Instances
**Purpose**: Identify external changes that occurred during instance work

**Change Detection Process**:
1. **Compare current Git hash** with instance base hash
2. **Identify external changes** during instance development
3. **Include code changes** in merge conflict analysis
4. **Warn of potential integration issues** if conflicts detected

### Step 3: Integrate with Merge Process
**Purpose**: Include Git awareness in instance merge operations

**Merge Integration**:
- **Consider code changes** in conflict detection algorithms
- **Update organizational state** for external code changes during merge
- **Reconcile both instance changes AND code changes** simultaneously
- **Ensure main instance authority** over code change interpretation

## Git Configuration Management

### Repository Structure
**Expected structure for optimal Git integration**:
```
/projectRoot/
├── .git/                              # Root-level Git repository
├── [project source files...]          # All tracked source code
├── projectManagement/                 # MAIN instance (tracked)
├── .mcp-instances/                    # Instance management (tracked structure)
└── .gitignore                        # Updated for MCP
```

### .gitignore Configuration
**Tracked in Git**:
- All project source code (existing behavior)
- Main `projectManagement/` organizational state
- Instance management structure (`.mcp-instances/`)
- Merge history and conflict resolution logs
- Instance metadata and branch information

**NOT Tracked**:
- User-specific settings (`projectManagement/UserSettings/`)
- Database backups (`projectManagement/database/backups/`)
- Temporary session files
- Active work logs during development

**Updated .gitignore**:
```gitignore
# MCP Instance Management - Track Structure, Not Content
.mcp-instances/active/*/projectManagement/UserSettings/
.mcp-instances/active/*/projectManagement/database/backups/
.mcp-instances/*/logs/
.mcp-instances/*/temp/

# Project Management - Track Organizational State
projectManagement/UserSettings/
projectManagement/database/backups/
projectManagement/.mcp-session-*
```

## Reconciliation Strategies

### Auto-Reconcile Strategy
**When to Use**: Minor, non-conflicting changes

**Auto-Reconcile Criteria**:
- File additions to existing, well-defined themes
- Non-conflicting theme file list updates
- Flow reference updates that don't change user experience logic
- Documentation updates that don't affect functionality

**Process**: Update organizational files automatically, notify user of changes

### User Approval Required Strategy
**When to Use**: Significant changes requiring decision

**Approval Required Criteria**:
- New theme creation needed for unrecognized files
- Major flow changes required due to code modifications
- Task or milestone impacts detected
- Conflicting organizational interpretations possible

**Process**: Present changes and proposed adaptations, get explicit user approval

### Manual Reconciliation Strategy
**When to Use**: Complex changes requiring user guidance

**Manual Review Criteria**:
- Multiple possible theme assignments for new files
- Structural project changes affecting multiple themes
- Deleted core files affecting multiple themes and flows
- Changes that could break existing workflows or user experience

**Process**: Request user guidance for interpretation and organizational updates

## Error Handling

### Git Repository Issues
- **Missing repository**: Initialize if `auto_init_repo` enabled, otherwise report error
- **Corrupted repository**: Attempt repair, report status to user
- **Permission issues**: Clear error message with resolution steps

### Theme Impact Analysis Failure
- **Unknown file types**: Fall back to user-guided theme assignment
- **Multiple theme candidates**: Present options for user decision
- **No theme matches**: Suggest new theme creation with user approval

### Organizational Reconciliation Failure
- **Conflicting updates**: Preserve original state, request manual review
- **File system errors**: Report clear error, suggest manual intervention
- **Theme relationship errors**: Validate and repair relationships

### Database Update Failure
- **Connection issues**: Retry with exponential backoff
- **Constraint violations**: Roll back changes, report conflict
- **Schema errors**: Suggest database schema update

## Integration Points

### Instance Management System
Coordinate with instance management for:
- Git-aware instance creation with base hash tracking
- Merge conflict detection including code changes
- Instance archival with Git state preservation

### Conflict Resolution Engine
Provide Git context for:
- Enhanced conflict detection including code changes
- Resolution options that consider external modifications
- Merge completion with Git state synchronization

### Audit System
Log Git integration actions for:
- Compliance tracking of organizational changes
- Performance analysis of reconciliation effectiveness
- Historical analysis of code change patterns

### Theme Management System
Update theme definitions based on:
- Code structure changes detected through Git
- File addition/deletion/movement patterns
- Directory structure evolution over time

## User Communication Guidelines

### Change Detection Notification
- **Clear summary** of detected changes with file counts and types
- **Impact assessment** showing which themes/flows are affected
- **Proposed actions** with rationale for each adaptation
- **Approval options** with clear explanation of consequences

### Reconciliation Progress
- **Progress indicators** during long reconciliation operations
- **Intermediate confirmations** for significant changes
- **Success summaries** showing what was updated and why

### Error Communication
- **Clear error messages** with specific causes and solutions
- **Recovery options** when reconciliation fails
- **Contact points** for manual intervention when needed

This directive ensures seamless integration between external code changes and internal AI project organization, maintaining accuracy and consistency while minimizing user intervention for routine changes.