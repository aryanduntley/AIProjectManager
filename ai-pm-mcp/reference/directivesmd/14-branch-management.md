# Git Branch-Based Management Directives

## Overview

This directive provides comprehensive guidance for managing Git branches in the AI Project Manager system. The system uses pure Git branch operations instead of complex directory-based instances, leveraging Git's native branching and merging capabilities with automatic team member detection and user attribution.

**Key Principles**: 
- ai-pm-org-main branch is the canonical organizational state and primary decision maker for all merge decisions
- Team members are automatically detected and given work branches
- Full user attribution in branch metadata and Git commits

## When This Directive Applies

### Triggers
- **Branch creation request** - User or AI needs parallel development workspace
- **Team member joins project** - Clone detection and automatic work branch creation
- **Multiple developer scenario** - Team coordination required
- **Parallel development needed** - Multiple simultaneous work streams
- **Branch merge operations** - Integrating branch work back to ai-pm-org-main
- **Sequential branch numbering** - Automatic generation of unique branch numbers
- **User identification needed** - Automatic detection from Git config, environment, or system

### Use Cases
- Authentication enhancement work: `ai-pm-org-branch-001`
- Independent authentication approach: `ai-pm-org-branch-002` (different strategy, parallel development)
- Payment integration development: `ai-pm-org-branch-003`
- Testing experimental approaches without affecting main organizational state
- Code refactoring that might take several sessions to complete

## Branch Naming Conventions

### Format
`ai-pm-org-branch-3 digits)

### Examples
- `ai-pm-org-branch-001` - First parallel development branch
- `ai-pm-org-branch-002` - Second parallel development branch  
- `ai-pm-org-branch-003` - Third parallel development branch
- `ai-pm-org-branch-015` - Fifteenth branch (handles growth automatically)

### Sequential Numbering System
**Automatic Generation Process**:
1. Query database for highest existing branch number
2. Increment by 1 for new branch creation
3. Format with zero-padding: `ai-pm-org-branch-{XXX}
4. Guaranteed uniqueness with no duplication possible

**Branch Metadata Storage**: Basic metadata stored in `.ai-pm-meta.json` within branch

### Validation Rules
- Must start with 'ai-pm-org-branch-{XXX}
- Sequential numbering prevents any name conflicts
- Zero-padded 3 digits (supports up to 999 branches)
- No user input required for naming
- Fully automated branch creation process

## ai-pm-org-main vs Work Branch Authority

### ai-pm-org-main Branch Responsibilities
- **Git repository change detection** - Monitor external user code changes
- **Merge conflict resolution** - Primary decision authority for all conflicts
- **Branch coordination and management** - Oversee all active branches
- **Project code change impact assessment** - Interpret external changes
- **Canonical organizational state** - Single source of truth for all organizational files

### Work Branch Responsibilities  
- **Independent development** - Work within isolated Git branch context
- **Prepare organizational changes** - Ready work for standard Git merge
- **Maintain branch metadata** - Store basic tracking info in .ai-pm-meta.json
- **Sequential identification** - Clear branch numbering for easy reference and management

### Authority Principle
ai-pm-org-main branch is the **PRIMARY DECISION MAKER** for all merge decisions. Uses standard Git merge tools - no complex coordination needed.

## Team Collaboration Workflow

### Project Creator (First User)
**Description**: First user to initialize AI Project Manager on a project

**Behavior**:
1. Creates `ai-pm-org-main` branch from user's main branch
2. Initializes `projectManagement/` structure  
3. Works directly on `ai-pm-org-main` (single user mode)

### Team Member (Additional Users)
**Description**: Additional users who clone the repository and install MCP server

**Detection Criteria**:
- `ai-pm-org-main` branch already exists (from clone)
- `projectManagement/` structure exists
- Git remote 'origin' is configured
- Currently on `ai-pm-org-main` branch

**Automatic Behavior**:
1. Detects team collaboration scenario
2. Automatically creates work branch with sequential numbering
3. Includes user attribution in branch metadata
4. Switches to work branch for development

### User Detection System

**Detection Priority Order**:
1. **Git Config** (High reliability) - `git config user.name` and `user.email`
2. **Environment** (Medium reliability) - `USER` or `USERNAME` environment variables  
3. **System** (Medium reliability) - `getpass.getuser()` system call
4. **Fallback** (Low reliability) - Default to `"ai-user"`

**User Attribution**:
- **Branch Metadata**: User info stored in `.ai-pm-meta.json` `created_by` field
- **Git Commits**: User attribution in branch initialization commits
- **Logging**: User detection logged for debugging

### Branch Metadata with User Attribution

```json
{
  "branch_type": "ai-pm-org-instance",
  "branch_name": "ai-pm-org-branch-001",
  "branch_number": 1,
  "created_at": "2025-01-17T12:00:00.000Z",
  "status": "active",
  "created_by": {
    "name": "john-doe",
    "email": "john.doe@example.com",
    "detection_source": "git_config"
  }
}
```

## Branch Creation Workflow

### Step 1: Ensure ai-pm-org-main Branch Exists (Enhanced for Team Collaboration)
**Purpose**: Initialize canonical organizational branch with remote/local/restoration handling

**Priority Logic**: Remote clone > Local restoration > Fresh creation

**Enhanced Process**:
1. **Check if ai-pm-org-main exists locally**: `git branch --list ai-pm-org-main`
2. **If missing locally, check remote**: `git branch -r --list origin/ai-pm-org-main`
3. **Branch establishment logic**:
   - **Remote exists**: Clone from remote (team collaboration)
   - **No remote but has previous AI state**: Restore from local organizational state
   - **Completely new**: Create fresh from user's main branch

**Team Collaboration Implementation**:
```bash
# Priority 1: Clone from remote (team member scenario)
git checkout -b ai-pm-org-main origin/ai-pm-org-main

# Priority 2: Restore from local state (branch was deleted but org state exists) 
git checkout -b ai-pm-org-main main
# Organizational files already exist, validate consistency

# Priority 3: Fresh creation (first-time setup)
git checkout -b ai-pm-org-main main
# Initialize new AI organizational structure
```

**Team Collaboration Benefits**:
- **Multiple developers can share organizational state**
- **Automatic detection of existing team setup**
- **No manual coordination needed between team members**
- **Consistent organizational structure across team**

**AI Action**: Automatic branch establishment with appropriate source detection and user communication.

### Step 2: Generate Sequential Branch Number
**Purpose**: Create unique branch number automatically without user input

**Process**:
1. Query database: `SELECT MAX(branch_number) FROM ai_instance_branches`
2. Increment highest number by 1 (start at 001 if no branches exist)
3. Format with zero-padding: `ai-pm-org-branch-{XXX}
4. No duplication possible, no user input required

**Database Query Example**:
```sql
-- Get next branch number
SELECT COALESCE(MAX(branch_number), 0) + 1 AS next_number 
FROM ai_instance_branches 
WHERE branch_name LIKE 'ai-pm-org-branch-{XXX}
```

### Step 3: Create Git Branch (Always Clone from ai-pm-org-main)
**Purpose**: Pure Git operation to create branch that ALWAYS clones organizational state

**Critical Principle**: Work branches ALWAYS clone from ai-pm-org-main, NOT from user's main

**Enhanced Process**:
1. **Ensure ai-pm-org-main exists** (may trigger remote clone for team scenarios)
2. **Switch to ai-pm-org-main first**: `git checkout ai-pm-org-main`
3. **Create work branch FROM ai-pm-org-main**: `git checkout -b ai-pm-org-branch-{XXX} ai-pm-org-main`
4. **Branch inherits complete organizational state** from AI canonical branch
5. **Create .ai-pm-meta.json** with branch metadata

**Why Always Clone from ai-pm-org-main**:
- **Organizational State Consistency**: All work branches have same starting AI context
- **Team Collaboration**: Multiple developers get consistent organizational state
- **Theme/Flow Inheritance**: Work branches inherit latest AI structure
- **Database State**: Proper AI database state in all work branches

**Team Collaboration Example**:
```bash
# Developer A creates first work branch
git checkout -b ai-pm-org-branch-001 ai-pm-org-main  # Gets full AI state

# Developer B (remote team member) gets work branch  
git checkout -b ai-pm-org-branch-002 ai-pm-org-main  # Same AI state as Developer A
```

**Git Benefits**: Zero file copying, natural state inheritance, complete isolation, consistent team state

**Branch Metadata (.ai-pm-meta.json)**:
```json
{
  "branch_number": 3,
  "branch_name": "ai-pm-org-branch-003",
  "created_timestamp": "2025-01-24T10:30:00Z",
  "created_from": "ai-pm-org-main"
}
```

### Step 4: Register Branch in Database
**Purpose**: Track branch for management and lifecycle

**Database Operations**:
- Insert into `ai_instance_branches` table
- Record branch number and generated name
- Store basic metadata for tracking
- Set status to 'active'
- Track creation timestamp

## Branch Development Phase

### Complete Git Isolation
During development, Git branches provide **natural complete isolation**:
- Branch only modifies files within its Git context
- All organizational changes isolated to branch
- No cross-branch interference
- ai-pm-org-main remains unaffected and available
- Multiple branches can work independently

### Change Tracking
**Git handles all change tracking automatically**:
- File modifications tracked in Git history
- Organizational state changes in Git commits
- Database modifications branch-specific
- Theme and flow updates tracked per branch

**Git Benefits**: Native conflict detection, standard merge tools, familiar workflow

## Branch Merging Workflow

### Step 1: Pre-Merge Validation
**Purpose**: Ensure both ai-pm-org-main and work branch are ready for merge

**Validation Checks**:
- ai-pm-org-main is in clean state
- Branch has committed all changes
- Check for external user code changes since branch creation
- Identify which branch work is being merged

**User Communication**: Present validation results and show branch information.

### Step 2: Execute Standard Git Merge
**Purpose**: Use native Git merge operation with conflict detection

**Git Operations**:
1. Switch to ai-pm-org-main: `git checkout ai-pm-org-main`
2. Execute merge: `git merge ai-pm-org-branch-{XXX}
3. Git handles conflict detection automatically
4. Show which branch work is being merged

**Branch Identification**: All operations clearly show which branch is being processed.

### Step 3: Handle Conflicts (If Any)
**Purpose**: Use standard Git tools for conflict resolution

**Conflict Handling**:
- Git presents conflicts in familiar format
- Use standard Git resolution tools (git mergetool, manual editing)
- No custom conflict resolution system needed
- ai-pm-org-main has authority for all decisions

**Resolution Tools**:
- `git mergetool` for GUI-based resolution
- Manual editing of conflict markers
- Standard Git workflow developers already know

### Step 4: Complete Merge
**Purpose**: Finalize merge and update tracking

**Completion Steps**:
- Git merge completes successfully
- Update `ai_instance_branches` table with merge timestamp
- Report successful merge with branch identification
- Optionally delete branch: `git branch -d ai-pm-org-branch-{XXX}

**User Communication**: Show merge success and branch that was integrated.

## Branch Management Tools

### List Active Branches
**Purpose**: Show all AI organizational branches with sequential numbering

**Git Command**: `git branch --list 'ai-pm-org-branch-{XXX}

**Information Provided**:
- Branch numbers in sequential order
- Current branch indicator
- Purpose from .ai-pm-meta.json metadata
- Last activity from database

### Get Branch Status  
**Purpose**: Detailed status of specific branch with metadata context

**Status Information**:
- Branch number from sequential system
- Git status: ahead/behind ai-pm-org-main
- Uncommitted changes
- Branch creation date and activity

### Delete Branch
**Purpose**: Clean up completed or merged branches

**Git Operations**:
- Verify branch is merged: `git branch --merged`
- Execute: `git branch -d ai-pm-org-branch-{XXX}
- Update database status to 'deleted'
- Report which branch was deleted

## Branch Cleanup and Management System

### Overview
Git branch management is inherently simpler than directory-based systems. Git handles most cleanup naturally, but we provide monitoring and user guidance for optimal workflow.

### Merge Philosophy

**User-Initiated Merges**: The system NEVER automatically merges branches without user approval. All merges use standard Git operations with user control.

**Merge Trigger Guidance**:
- **User-initiated completion** - When branch work is finished
- **Stale branch warnings** - After extended inactivity (guidance only)
- **Branch lifecycle management** - Help users maintain clean Git history
- **Standard Git validation** - Use Git's built-in safety checks

### Stale Branch Management

**Detection Criteria**:
- No commits for more than 14 days (configurable)
- Branch age exceeds 30 days (configurable)
- No database activity recorded
- Branch appears abandoned

**User Guidance Options**:
- **Merge and Complete**: Standard Git merge to ai-pm-org-main
- **Continue Work**: Switch to branch and resume development
- **Delete Branch**: Remove if work is no longer needed
- **Archive Reference**: Keep branch for future reference

**No Automated Actions**: All decisions made by user, system provides guidance only

### Simple Git Branch Lifecycle

**Branch States**:
```
Active Branch (ai-pm-org-branch-{XXX}
    ↓ (user merge decision)
Merged to ai-pm-org-main
    ↓ (optional user decision)
Branch Deleted (git branch -d)
```

**No Complex Cleanup Needed**: Git handles branch lifecycle naturally

### Configuration Options

**Key Settings in user configuration**:
```json
{
  "branch_management": {
    "enabled": true,
    "max_active_branches": 10,
    "auto_delete_merged": false,
    "branch_naming_validation": true
  }
}
```

**Simplification Benefits**:
- No directory copying or cleanup
- No complex retention policies  
- No orphaned file management
- Git handles all version control
- Standard Git tools for all operations

## Error Handling

### Branch Creation Failure
- Report Git error and suggest alternative branch name
- No cleanup needed (Git handles partial operations)
- Preserve ai-pm-org-main state

### Merge Conflicts
- Use standard Git conflict resolution - no custom logic needed
- Present Git conflict markers to user
- Allow standard Git resolution tools (git mergetool, manual editing)

### Sequential Number Generation Failure
- Fall back to timestamp-based unique identifier if database query fails
- Continue with branch creation using fallback numbering

### Branch Number Conflicts
- Sequential numbering prevents conflicts by design
- Database transaction ensures atomic number generation
- No manual conflict resolution needed

## Integration Points

### Git Integration
Core dependency - all operations are Git operations:
- Branch creation and management
- Code change detection at project root level
- Standard Git merge operations
- Repository state tracking

### Audit System
Log branch operations for tracking:
- Branch creation and deletion with sequential numbers
- Merge operations with branch identification
- Sequential numbering system

### Performance Optimizer
Optimized for many branches instead of directories:
- Efficient branch enumeration by number
- Minimal metadata tracking in .ai-pm-meta.json
- Git's natural performance characteristics
- Fast database queries for next branch number

### Sequential Numbering System
Automatic branch number generation:
- Database-driven sequential numbering
- Zero-padded 3-digit format for consistency
- No user input or detection complexity
- Guaranteed uniqueness and conflict prevention

## User Communication Guidelines

### Branch Creation
- Show generated branch number
- Explain automatic sequential numbering system
- Explain Git branch isolation benefits
- Set expectations for independent development

### Merge Operations
- Show which branch work is being merged
- Use standard Git conflict presentation
- Leverage familiar Git workflow patterns
- Confirm merge completion with branch identification

### Status Updates
- Show branch numbers for all branch operations
- Clear Git command feedback
- Success confirmations with branch identification
- Standard Git error messages when operations fail

## Best Practices

### When to Create Branches
- Experimental work that might not be integrated
- Long-running tasks that span multiple sessions
- Parallel development on different themes
- Multiple parallel development approaches
- Work that might conflict with ongoing ai-pm-org-main development

### When NOT to Create Branches
- Quick fixes or small changes
- When ai-pm-org-main is idle and no conflicts expected
- When Git switching overhead exceeds benefits
- For tasks that require frequent main branch interaction

### Branch Purpose Documentation
- Store minimal metadata in .ai-pm-meta.json
- Be specific about scope and approach
- Document any special considerations or dependencies

### Merge Timing
- Complete major work units before merging
- Ensure branch work is stable and committed
- Use standard Git merge practices
- Multiple branches can merge independently without coordination

### Parallel Development Benefits
- Multiple branches can work independently: `ai-pm-org-branch-001`, `ai-pm-org-branch-002`
- Complete isolation through Git branches with sequential numbering
- Independent merge timing for each branch
- Clear branch identification for all operations
- No naming conflicts or user detection complexity

This directive ensures effective Git branch-based management while maintaining the AI Project Manager's sophisticated organizational capabilities and leveraging familiar Git workflow patterns.