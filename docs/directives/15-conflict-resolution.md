# Git-Like Conflict Resolution Directives

## Overview

This directive provides comprehensive guidance for detecting and resolving conflicts during Git-like instance merges in the AI Project Manager system. The conflict resolution process uses familiar Git patterns while handling the complex organizational state of AI-managed projects.

**Core Principle**: Main instance has ultimate authority for all conflict resolution decisions, eliminating complex multi-party coordination.

## When This Directive Applies

### Triggers
- **Instance merge conflicts detected** - Organizational differences found during merge
- **Organizational state divergence** - Main and instance have incompatible changes
- **Database conflicts during merge** - Database schema or data conflicts
- **Theme/flow/task conflicts** - Specific organizational component conflicts
- **Main instance merge authority needed** - Resolution decisions required

### Conflict Scenarios
- Team member's authentication work conflicts with main's security updates
- Parallel payment integration conflicts with billing system changes
- Database schema changes incompatible between instances
- Theme definitions diverged during simultaneous development
- Task status conflicts from overlapping work

## Conflict Detection Process

### Step 1: Analyze Organizational Changes
**Purpose**: Compare instance workspace with main workspace comprehensively

**Analysis Areas**:
- **Theme file differences** - File paths, linked themes, descriptions
- **Flow definition changes** - Steps, cross-flow dependencies, status
- **Task status modifications** - Status, subtasks, completion data
- **Completion path updates** - Milestones, progress, dependencies
- **Implementation plan changes** - Plans, phases, strategies

**AI Action**: Generate detailed diff analysis showing exactly what changed in each area.

### Step 2: Detect Database Conflicts
**Purpose**: Identify database schema and data conflicts between instances

**Database Conflict Types**:
- **Schema differences** - Table structure, indexes, triggers
- **Task status conflicts** - Same task modified in both databases
- **Session data inconsistencies** - Session tracking conflicts
- **Theme-flow relationship conflicts** - Relationship mapping differences
- **Event log conflicts** - Conflicting event records

**AI Action**: Run database comparison queries and flag incompatible changes.

### Step 3: Categorize Conflicts
**Purpose**: Organize conflicts by type and impact for systematic resolution

**Conflict Categories**:
- **theme** - Same theme modified in both main and instance
- **task** - Task status changes in both locations
- **flow** - Flow definitions diverged between instances
- **database** - Incompatible database schema or data changes
- **completion-path** - Milestone or completion path conflicts

### Step 4: Assess Conflict Severity
**Purpose**: Determine resolution complexity and user communication needs

**Severity Levels**:
- **trivial** - Minor formatting or metadata changes (auto-resolvable)
- **moderate** - Content changes that can be easily merged
- **significant** - Major structural changes requiring user decision
- **critical** - Incompatible changes requiring manual resolution

## Conflict Presentation (Git-Like Format)

### Generate Familiar Conflict Markers
**Purpose**: Use Git conflict syntax for developer familiarity

**Format Example**:
```
<<<<<<< main
{
  "theme": "authentication",
  "files": ["src/auth/login.js", "src/auth/register.js"],
  "linkedThemes": ["user-management"]
}
=======
{
  "theme": "authentication", 
  "files": ["src/auth/login.js", "src/auth/register.js", "src/auth/oauth.js", "src/auth/mfa.js"],
  "linkedThemes": ["user-management", "security", "notifications"]
}
>>>>>>> auth-enhancement-alice
```

### Present Resolution Options
**Purpose**: Give main instance clear choices for each conflict

**Standard Options**:
1. **Accept Instance Changes** - Use branch instance modifications
2. **Keep Main** - Reject instance changes, maintain main version  
3. **Manual Merge** - Combine specific elements from both versions
4. **Split Approach** - Create separate components for conflicting functionality

### Provide Context Information
**Purpose**: Enable informed decision making

**Context Provided**:
- **When changes were made** - Timestamps for both versions
- **Who made the changes** - User identification for instance work
- **Purpose of the instance work** - From instance metadata
- **Impact assessment** - Consequences of each resolution option
- **Dependencies affected** - What other components are impacted

## Theme Conflict Resolution

### Identify Theme Conflicts
**Purpose**: Detect specific areas of theme definition conflicts

**Conflict Areas**:
- **File path lists** - Different sets of files assigned to theme
- **Linked theme relationships** - Different theme connections
- **Shared file configurations** - Conflicting shared file assignments
- **Theme descriptions and metadata** - Incompatible theme information

### Apply Theme Resolution Strategy
**Purpose**: Implement chosen resolution approach

**Resolution Strategies**:
- **accept_instance** - Copy instance theme to main completely
- **accept_main** - Keep main theme version unchanged
- **merge_files** - Combine file lists from both versions intelligently
- **split_themes** - Create separate themes for new functionality

### Update Theme Relationships
**Purpose**: Maintain theme system integrity after resolution

**Updates Required**:
- Sync theme-flow database relationships
- Update flow-index references to themes
- Validate linked theme consistency
- Update shared file mappings across all themes

## Flow Conflict Resolution

### Identify Flow Conflicts
**Purpose**: Detect conflicts in flow definitions and cross-references

**Conflict Areas**:
- **Flow step definitions** - Different step implementations
- **Cross-flow dependencies** - Conflicting flow relationships
- **Flow completion status** - Different progress states
- **User experience changes** - Incompatible UX modifications

### Apply Flow Resolution Strategy
**Purpose**: Resolve flow conflicts while maintaining UX integrity

**Resolution Strategies**:
- **accept_instance** - Use instance flow version completely
- **accept_main** - Keep main flow version unchanged
- **manual_merge** - Combine flow steps manually with user guidance
- **split_flows** - Create separate flows for different functionality

### Update Flow Index
**Purpose**: Maintain flow system consistency after resolution

**Updates Required**:
- Add/remove flow file references in flow-index.json
- Update cross-flow dependencies
- Sync flow completion status across related flows
- Update flow metadata and descriptions

## Task Conflict Resolution

### Identify Task Conflicts
**Purpose**: Detect conflicts in task definitions and progress tracking

**Conflict Areas**:
- **Task status changes** - Different completion states
- **Subtask modifications** - Added, removed, or changed subtasks
- **Completion path milestones** - Conflicting milestone updates
- **Sidequest additions** - Different sidequest sets

### Apply Task Resolution Strategy
**Purpose**: Resolve task conflicts while preserving work progress

**Resolution Strategies**:
- **accept_instance** - Use instance task changes completely
- **accept_main** - Keep main task version unchanged
- **merge_subtasks** - Combine subtasks from both versions intelligently
- **preserve_both** - Keep both versions with different names/IDs

### Update Completion Path
**Purpose**: Maintain project completion tracking after resolution

**Updates Required**:
- Merge milestone changes from both versions
- Update progress tracking calculations
- Validate milestone dependencies remain intact
- Update completion criteria and success metrics

## Database Conflict Resolution

### Identify Database Conflicts
**Purpose**: Detect schema and data conflicts requiring special handling

**Conflict Areas**:
- **Schema differences** - Table structure, column, constraint changes
- **Data conflicts in shared tables** - Same records modified differently
- **Index and trigger differences** - Database optimization conflicts
- **Session data inconsistencies** - Session tracking state conflicts

### Apply Database Resolution Strategy
**Purpose**: Resolve database conflicts while maintaining data integrity

**Resolution Strategies**:
- **accept_instance** - Apply instance database changes to main
- **accept_main** - Keep main database state, discard instance changes
- **merge_data** - Merge database changes using custom logic
- **schema_upgrade** - Apply database schema upgrade to resolve conflicts

### Validate Database Integrity
**Purpose**: Ensure database remains consistent after resolution

**Validation Steps**:
- Check referential integrity constraints
- Validate all table constraints and relationships
- Test critical queries for performance
- Verify data consistency across related tables

## Merge Completion Process

### Apply All Resolutions Atomically
**Purpose**: Ensure merge either completely succeeds or completely fails

**Atomic Operation**: All conflict resolutions must succeed together, or entire merge operation fails and can be retried.

### Update Main Workspace
**Purpose**: Integrate all resolved changes into main instance

**Update Process**:
- Copy resolved files to main `projectManagement/`
- Update main database with merged state
- Update Git tracking if applicable
- Sync all organizational relationships

### Log Merge Decisions
**Purpose**: Maintain audit trail and enable analysis

**Logging Information**:
- Conflict types and chosen resolutions
- Resolution strategies selected for each conflict
- Who made resolution decisions (main instance user)
- Timestamp and unique merge ID
- Impact assessment and affected components

### Archive Instance
**Purpose**: Clean up completed merge and preserve history

**Archival Process**:
- Move instance to `.mcp-instances/completed/`
- Update instance status in database to 'completed'
- Preserve instance work summary for reference
- Clean up temporary merge conflict files

## Resolution Strategy Details

### Accept Instance Strategy
**Description**: Use the branch instance changes, overriding main

**When to Use**:
- Instance has more complete or correct implementation
- Main version is outdated or incomplete
- Instance work represents intended project direction

**Caution**: Ensure main instance user approves overriding their changes

### Accept Main Strategy
**Description**: Keep the main instance version, discard branch changes

**When to Use**:
- Instance changes conflict with established project direction
- Main has newer, more authoritative updates
- Instance work was experimental and shouldn't be integrated

**Caution**: May lose valuable work from branch instance - document reasoning

### Manual Merge Strategy
**Description**: Manually combine elements from both versions

**When to Use**:
- Both versions have valuable contributions
- Complex integration needed to preserve all benefits
- Selective merging can create optimal solution

**Process**: Present both versions side-by-side for selective element merging

### Split Approach Strategy
**Description**: Create separate components to preserve both approaches

**When to Use**:
- Fundamentally different approaches, both valuable
- Both solutions needed for different use cases
- Approaches serve different user needs

**Result**: Creates multiple themes/flows/tasks instead of forcing merge

## Error Handling

### Resolution Failure
- Provide rollback option to pre-merge state
- Preserve both versions for manual review
- Document failure reason for debugging

### Atomicity Failure
- Roll back entire merge operation
- Preserve instance for retry with different approach
- Maintain data integrity throughout process

### Database Corruption
- Use database backup and recovery system
- Restore to last known good state
- Rebuild from organizational files if necessary

### Conflict Detection Failure
- Err on side of caution
- Request manual review of all changes
- Provide detailed logs for troubleshooting

## User Communication Guidelines

### Conflict Presentation
- Use familiar Git conflict syntax when possible
- Provide clear explanations of each conflict type
- Show impact assessment for each resolution option
- Allow time for careful consideration of complex conflicts

### Resolution Guidance
- Explain implications of each resolution strategy
- Provide recommendations based on conflict analysis
- Offer to show additional context if needed
- Confirm understanding before applying resolutions

### Progress Updates
- Show progress during long merge operations
- Provide intermediate status updates
- Confirm successful completion of each phase
- Summarize final merge results clearly

## Integration Points

### Instance Management
Coordinate closely with instance management system for:
- Instance lifecycle tracking
- Workspace isolation maintenance
- Merge initiation and completion

### Audit System
Integrate with audit system for:
- Comprehensive conflict logging
- Decision tracking and compliance
- Performance analysis and optimization

### Error Recovery
Use error recovery system for:
- Failed merge operation rollback
- Data integrity restoration
- System state recovery

### Git Integration
Consider Git integration for:
- Code change conflicts during organizational merges
- Repository state consistency
- External change impact on conflict resolution

This directive ensures systematic, user-friendly conflict resolution while maintaining the integrity and consistency of the AI Project Manager's organizational state across all instances.