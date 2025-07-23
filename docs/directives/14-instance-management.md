# Git-Like Instance Management Directives

## Overview

This directive provides comprehensive guidance for managing Git-like instances in the AI Project Manager system. Instances operate similar to Git branches, allowing parallel development with merge-based integration to a canonical `main` instance.

**Key Principle**: Main instance is the canonical source of truth and primary decision maker for all conflict resolution.

## When This Directive Applies

### Triggers
- **Instance creation request** - User or AI needs parallel development workspace
- **Multiple developer scenario** - Team coordination required
- **Parallel development needed** - Multiple simultaneous work streams
- **Instance merge operations** - Integrating branch work back to main
- **Workspace isolation required** - Independent development without interference

### Use Cases
- Team member working on authentication enhancements while main continues other work
- Autonomous AI working on payment integration in parallel with UI improvements
- Testing experimental approaches without affecting main development
- Code refactoring that might take several sessions to complete

## Instance Naming Conventions

### Format
`{theme/area}-{purpose}-{user}` (user-specific) or `{theme/area}-{purpose}` (autonomous)

### Examples
- `auth-enhancement-alice` - Alice working on authentication improvements
- `payment-integration` - Autonomous work on payment system integration  
- `ui-components-refactor-bob` - Bob refactoring UI components
- `database-optimization` - Database performance improvements
- `api-security-audit` - Security audit of API endpoints

### Validation Rules
- Must be descriptive of work being done
- Include theme/area being modified
- Include user name if user-specific work
- Use kebab-case format
- No spaces or special characters

## Main vs Branch Instance Authority

### Main Instance Responsibilities
- **Git repository change detection** - Monitor external code changes
- **Merge conflict resolution** - Primary decision authority for all conflicts
- **Instance coordination and management** - Oversee all active instances
- **Project code change impact assessment** - Interpret external changes

### Branch Instance Responsibilities  
- **Independent development** - Work within isolated workspace
- **Prepare organizational changes** - Ready work for merge
- **Maintain instance metadata** - Track work summaries and progress

### Authority Principle
Main instance is the **PRIMARY DECISION MAKER** for all conflict resolution. No complex coordination between instances - main decides, others adapt.

## Instance Creation Workflow

### Step 1: Validate Main Instance State
**Purpose**: Ensure main instance is ready for branch creation

**Requirements**:
- No uncommitted organizational changes
- Database is consistent
- No active conflicts
- Git repository is in clean state

**AI Action**: Run validation checks and report any issues to user before proceeding.

### Step 2: Generate Instance Name
**Purpose**: Create descriptive, unique instance identifier

**Process**:
1. Ask user for intended purpose and primary themes
2. Suggest instance name following convention
3. Validate name isn't already in use
4. Get user approval for final name

**User Communication**: 
```
Creating new instance for [purpose]. Suggested name: "auth-enhancement-alice"
Primary themes: authentication, security
Does this name accurately describe your work? (Y/n)
```

### Step 3: Create Instance Workspace
**Purpose**: Establish isolated development environment

**Process**:
1. Copy `projectManagement/` to `.mcp-instances/active/{instance-name}/`
2. Copy `project.db` to instance workspace for isolation
3. Create `.mcp-branch-info.json` with instance metadata
4. Create `.mcp-work-summary.md` for human-readable tracking

**Workspace Isolation**: Instance operates completely independently using its own copies of all organizational files and database.

### Step 4: Register Instance
**Purpose**: Track instance in system for coordination

**Database Operations**:
- Insert into `mcp_instances` table
- Record Git base hash for merge comparison
- Set status to 'active'
- Initialize instance workspace file tracking

## Instance Development Phase

### Complete Isolation
During development, instances operate with **complete isolation**:
- Instance only modifies files in its workspace
- Instance database changes are isolated  
- No cross-instance interference
- Main instance remains unaffected and available

### Change Tracking
**All changes within instance workspace are tracked**:
- File modifications with timestamps
- Organizational state changes
- Database modifications  
- Theme and flow updates

**Purpose**: Enable comprehensive merge conflict detection and resolution.

## Instance Merging Workflow

### Step 1: Pre-Merge Validation
**Purpose**: Ensure both main and instance are ready for merge

**Validation Checks**:
- Main instance is in clean state
- Instance is ready for merge (no incomplete tasks)
- Check for external project code changes since instance creation
- Validate instance workspace integrity

**User Communication**: Present validation results and get confirmation to proceed.

### Step 2: Comprehensive Conflict Detection
**Purpose**: Identify all organizational differences between main and instance

**Conflict Types Detected**:
- **Theme conflicts** - Same theme modified in both locations
- **Task conflicts** - Task status changes in both locations  
- **Flow conflicts** - Flow definitions diverged
- **Database conflicts** - Incompatible database changes

**AI Action**: Generate detailed conflict analysis for main instance review.

### Step 3: Present Conflicts to Main Instance
**Purpose**: Main instance makes all resolution decisions

**Conflict Presentation**:
- Show Git-like conflict markers for familiarity
- Present clear resolution options
- Provide context about changes and impact
- Allow main instance to choose strategy for each conflict

**Resolution Options**:
1. **Accept Instance Changes** - Use branch instance modifications
2. **Keep Main** - Reject instance changes, maintain main version
3. **Manual Merge** - Combine specific elements from both versions
4. **Split Approach** - Create separate components for conflicting functionality

### Step 4: Apply Resolution Strategy
**Purpose**: Implement chosen conflict resolutions

**Process**:
- Apply all resolutions atomically (all succeed or merge fails)
- Update main workspace with resolved changes
- Update main database with merged state
- Sync organizational relationships

**User Communication**: Show progress and confirm successful application.

### Step 5: Complete Merge and Archive
**Purpose**: Finalize merge and clean up instance

**Completion Steps**:
- Apply resolved changes to main `projectManagement/`
- Update main database with merged state
- Archive instance to `.mcp-instances/completed/`
- Log merge decisions in `.mcp-merge-log.jsonl`

**User Communication**: Provide merge summary and confirm instance archival.

## Instance Management Tools

### List Active Instances
**Purpose**: Show all currently active instances

**Information Provided**:
- Instance names and purposes
- Creation dates and creators
- Primary themes being worked on
- Last activity timestamps

### Get Instance Status  
**Purpose**: Detailed status of specific instance

**Status Information**:
- Instance metadata and configuration
- Workspace file changes since creation
- Database modifications
- Merge readiness assessment

### Archive Instance
**Purpose**: Clean up completed or cancelled instances

**Archival Process**:
- Move to `.mcp-instances/completed/`
- Update database status to 'archived'
- Preserve instance metadata for history
- Clean up active workspace

## Instance Cleanup and Retention System

### Overview
The cleanup system prevents instance accumulation and data bloat through automated monitoring, warning systems, and retention policies. This ensures optimal performance while maintaining necessary audit trails.

### Merge Frequency and Triggers

**Manual Merge Philosophy**: The system NEVER automatically merges instances without user approval. All merges are user-initiated with safety checks.

**Merge Trigger Conditions**:
- **User-initiated completion** - When instance work is finished
- **Stale instance warnings** - After 7+ days of inactivity (prompts only)
- **Timeout enforcement** - At 30-day limit (archival, not merge)
- **Pre-merge validation** - Must pass before any merge attempt

### Stale Instance Management

**Detection Criteria**:
- No activity for more than 14 days (configurable)
- Instance age exceeds 30 days (configurable)
- No active tasks in progress
- No recent file modifications

**Warning Escalation Schedule**:
1. **Day 7**: First warning notification with options
2. **Day 14**: Second warning with merge reminder
3. **Day 21**: Final warning about approaching timeout
4. **Day 30**: Forced archival (if `autoArchiveStale=true`)

**User Options When Warned**:
- **Extend Duration**: Request additional time for completion
- **Merge Immediately**: Complete work and integrate with main
- **Archive Manually**: Preserve work but stop active development
- **Delete Instance**: Remove instance entirely (requires confirmation)

### Automated Cleanup Schedules

#### Daily Cleanup Operations
- **Stale Instance Detection**: Scan for inactive instances
- **Warning Notifications**: Alert users about approaching timeouts
- **Orphaned File Cleanup**: Remove files from deleted instances
- **Activity Monitoring**: Track instance usage patterns

#### Weekly Cleanup Operations  
- **Archive Retention Enforcement**: Delete completed instances older than retention period
- **Cleanup Summary Reports**: Generate activity summaries for review
- **Disk Space Optimization**: Compress old logs and backup files
- **Performance Monitoring**: Check system resource usage

#### Monthly Cleanup Operations
- **Deep Archive Review**: Comprehensive review of all archived instances
- **Log Retention Enforcement**: Archive merge logs older than specified period
- **Database Optimization**: Defragment database and rebuild indexes
- **Audit Trail Maintenance**: Ensure compliance with retention policies

### Retention Policies

**Instance Lifecycle**:
```
Active Instance (expected: 7 days)
    ↓ (completion OR 30-day timeout)
Completed Archive (retention: 90 days)
    ↓ (retention period expires)
Permanent Deletion
```

**Data Retention Periods**:
- **Active Instances**: No retention limit (managed by timeout system)
- **Completed Instances**: 90 days (configurable via `archiveRetention`)
- **Merge Operation Logs**: 1 year (configurable via `logRetention`)
- **Database Backups**: 30 days (configurable via `backupRetention`)
- **Orphaned Files**: Deleted immediately when detected

### Configuration Options

**Key Settings in `.mcp-instances/.mcp-config.json`**:
```json
{
  "instanceManagement": {
    "instanceTimeout": "30 days",
    "warningThreshold": "7 days", 
    "staleInstanceCleanup": true,
    "inactivityThreshold": "14 days",
    "autoArchiveCompleted": true
  },
  "cleanup": {
    "archiveRetention": "90 days",
    "logRetention": "1 year",
    "backupRetention": "30 days",
    "deleteOldArchives": true,
    "cleanupOrphanedFiles": true
  }
}
```

### Cleanup Operations Detail

#### Archive Instance
**Trigger**: Instance completion or timeout reached
**Process**:
1. Move instance directory to `.mcp-instances/completed/`
2. Add timestamp suffix to prevent naming conflicts
3. Log archival operation in `.mcp-merge-log.jsonl`
4. Update database instance status to 'archived'
5. Notify user of archival completion

#### Delete Old Archives
**Trigger**: Weekly cleanup + archive age exceeds retention period
**Process**:
1. Identify archives older than `archiveRetention` setting
2. Log deletion operation for audit compliance
3. Remove archive directory and all associated files
4. Update database to mark as permanently deleted
5. Generate cleanup report for review

#### Cleanup Orphaned Files
**Trigger**: Daily cleanup scan
**Process**:
1. Scan filesystem for files not referenced in database
2. Verify files are not part of any active instances
3. Remove orphaned files and empty directories
4. Log cleanup operations for audit trail
5. Update performance metrics

### Safety Measures

**Before Any Destructive Operation**:
- Verify instance is not currently active
- Confirm no uncommitted work exists
- Create backup if required by configuration
- Log operation details for audit trail
- Provide user notification and confirmation options

**Rollback Capabilities**:
- Database transaction rollback for failed operations
- File system snapshots before major cleanup operations
- Instance resurrection from archives (within retention period)
- Manual override options for emergency situations

## Error Handling

### Instance Creation Failure
- Clean up partial workspace
- Report clear error to user
- Preserve main instance state

### Merge Conflict Resolution Failure
- Provide rollback option
- Preserve both versions if resolution fails
- Allow retry with different strategy

### Workspace Corruption
- Use error recovery system to restore from backup
- Maintain data integrity
- Report issue clearly to user

### Database Conflicts
- Use database conflict resolution with schema upgrade options
- Maintain referential integrity
- Provide rollback capabilities

## Integration Points

### Git Integration
Coordinate with Git integration for:
- Code change detection during instance lifecycle
- Git-aware merge conflict resolution
- Repository state tracking

### Conflict Resolution Engine
Use conflict resolution engine for:
- Comprehensive conflict detection
- Git-like conflict presentation
- Resolution strategy application

### Audit System
Log all instance operations for:
- Compliance and tracking
- Merge decision history
- Performance analysis

### Performance Optimizer
Optimize for large projects with:
- Many active instances
- Large workspace sizes
- Complex merge operations

## User Communication Guidelines

### Instance Creation
- Explain purpose and benefits of instance isolation
- Get clear approval for instance name and purpose
- Set expectations for independent development

### Merge Conflicts
- Present conflicts in familiar Git-like format
- Provide clear context for decision making
- Explain impact of each resolution option
- Confirm decisions before applying

### Status Updates
- Regular progress updates during long operations
- Clear error messages with actionable guidance
- Success confirmations with summary information

## Best Practices

### When to Create Instances
- Experimental work that might not be integrated
- Long-running tasks that span multiple sessions
- Parallel development on different themes
- Work that might conflict with ongoing main development

### When NOT to Create Instances
- Quick fixes or small changes
- When main instance is idle
- When coordination overhead exceeds benefits
- For tasks that require frequent main instance interaction

### Instance Naming
- Be specific about purpose and scope
- Include theme/area for context
- Use consistent naming patterns
- Avoid generic names like "test" or "temp"

### Merge Timing
- Complete major work units before merging
- Ensure instance work is stable and tested
- Coordinate with main instance for optimal timing
- Document changes clearly in work summaries

This directive ensures effective Git-like instance management while maintaining the AI Project Manager's sophisticated organizational capabilities and user-friendly interaction patterns.