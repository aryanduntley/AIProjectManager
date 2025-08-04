# Root-Level Git Integration Directives

## Overview

This directive provides comprehensive guidance for integrating root-level Git repository tracking with the AI Project Manager's organizational state. It enables detection of external code changes, Git safety validation, pull request creation, and automatic reconciliation of organizational structure with project reality.

**Core Purpose**: Bridge the gap between external code changes and internal AI project organization while ensuring safe Git operations through modular architecture and comprehensive validation.

## Git Safety & Collaboration Features

### Repository Type Detection
The system automatically detects repository type to ensure safe workflows:

**Detection Methods**:
- **GitHub CLI Integration**: Uses `gh repo view --json isFork` when available
- **Remote Analysis**: Analyzes `git remote -v` output for repository relationships  
- **Upstream Detection**: Checks for upstream relationships and fork indicators
- **Caching**: Results stored in `metadata.json` with 24-hour cache validity

**Repository Types & Adaptations**:
- **`original`**: Full workflow capabilities, direct merge and PR creation available
- **`clone`**: Safety validation prevents main branch work, requires work branches
- **`fork`**: Enhanced safety checks, PR creation preferred over direct merge

### Workflow Safety Validation
Comprehensive safety checks prevent dangerous Git operations:

**High-Severity Blocking**:
- Working on main branch in cloned/forked repositories
- Creating branches from wrong ancestry (not from ai-pm-org-main)
- Attempting unsafe operations without proper repository permissions

**Medium-Severity Warnings**:
- Creating branches while on feature branch instead of ai-pm-org-main
- GitHub CLI not available for GitHub repositories (limits PR creation)
- Network issues preventing remote repository validation

**Auto-Correction Features**:
- Automatic switching to ai-pm-org-main before branch creation
- Clear recommendations for resolving safety issues
- Comprehensive warnings with specific remediation steps

### Pull Request Integration
The system prioritizes pull request creation for better team collaboration:

**Pull Request Workflow**:
1. **Availability Check**: GitHub CLI available and authenticated
2. **Repository Validation**: GitHub repository with remote origin configured
3. **Branch Push**: Ensure branch is pushed to origin if needed
4. **PR Creation**: Generate comprehensive PR with user attribution
5. **Team Integration**: Return PR URL for team review and merge

**Direct Merge Fallback**: When GitHub CLI unavailable or not a GitHub repository

## Modular Architecture

The Git integration system has been refactored into specialized modules for 71% code reduction and better maintainability:

### Core Modules

#### RepositoryDetector (`core/repository_detector.py`)
- **Purpose**: Repository analysis, user detection, and metadata management
- **Key Functions**:
  - `detect_repository_type()`: Analyzes fork/clone/original status
  - `detect_user_info()`: Multi-source user identification  
  - `check_gh_cli_available()`: GitHub CLI availability checking
  - `load_metadata()` / `save_metadata()`: Project metadata management
- **Detection Sources**: Git config, environment variables, system calls, fallback

#### GitSafetyChecker (`core/git_safety.py`)
- **Purpose**: Comprehensive workflow safety validation and ancestry checking
- **Key Functions**:
  - `check_workflow_safety()`: Repository-aware safety validation
  - `check_branch_ancestry()`: Validates proper branch relationships
  - `validate_branch_creation()`: Pre-creation safety checks
- **Safety Features**: Blocking for dangerous operations, auto-correction, recommendations

#### MergeOperations (`core/merge_operations.py`)
- **Purpose**: Pull request creation and direct merge fallback operations
- **Key Functions**:
  - `merge_instance_branch()`: Orchestrates merge strategy selection
  - `create_pull_request()`: GitHub CLI PR creation with attribution
  - `direct_merge_fallback()`: Standard Git merge when PR not available
- **Strategy Priority**: Pull request creation preferred, direct merge as fallback

#### TeamCollaboration (`core/team_collaboration.py`)
- **Purpose**: Team member detection and collaborative AI structure setup
- **Key Functions**:
  - `detect_team_member_scenario()`: Identifies team collaboration needs
  - `ensure_ai_main_branch_exists()`: Remote-aware ai-pm-org-main setup
  - `initialize_for_team_member()`: Automatic work branch creation
- **Team Features**: Remote branch detection, priority logic, user attribution

#### GitUtils (`core/git_utils.py`)
- **Purpose**: Common Git operations and utility functions
- **Key Functions**:
  - `get_current_branch()`: Current branch detection
  - `branch_exists()`: Branch existence validation
  - `get_next_branch_number()`: Sequential numbering
  - `get_user_code_changes()`: Code change detection
- **Utilities**: Standard Git operations, error handling, branch utilities

## When This Directive Applies

### Triggers
- **Session boot with project code changes** - Code modified outside AI sessions
- **Git repository state detection needed** - Initial setup or validation required
- **External code modifications detected** - Files changed by users or other tools
- **Theme impact analysis required** - Code changes affect organizational themes
- **Organizational reconciliation needed** - AI structure needs updating
- **Repository type detection required** - Fork/clone/original analysis needed
- **Git safety validation needed** - Workflow safety checks before operations
- **Pull request merge operations** - PR creation and merge handling
- **Team collaboration initialization** - Multi-developer setup and coordination

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
5. **Check for remote repository** if configured (team collaboration)

**AI Action**: Report Git repository status and any initialization actions taken.

**User Communication**: 
```
Git repository detected at project root.
Remote repository: origin (team collaboration enabled)
Last tracked state: commit abc123 (2 days ago)
Repository status: Clean, ready for change detection
```

### Step 1.5: Ensure AI Main Branch Exists (NEW: Team Collaboration Support)
**Purpose**: Establish ai-pm-org-main branch with proper remote/local/restoration handling

**Priority Logic**: Remote clone > Local restoration > Fresh creation

**Branch Establishment Process**:
1. **Check if ai-pm-org-main exists locally**
2. **If missing locally, check remote repository** for ai-pm-org-main
3. **If exists on remote**: Clone from remote (team collaboration scenario)
4. **If no remote but has previous AI state**: Restore from previous organizational state
5. **If completely new**: Create fresh branch from user's main

**Team Collaboration Support**:
- **Remote Clone**: `git checkout -b ai-pm-org-main origin/ai-pm-org-main`
- **Automatic Sync**: Sync local database with remote organizational state
- **State Inheritance**: Multiple team members can inherit shared AI organizational state

**User Communication Examples**:
```
✅ Cloned ai-pm-org-main from remote repository (team collaboration)
   Synced organizational state with team's shared configuration
```
```
✅ Restored ai-pm-org-main with previous organizational state
   Found existing themes and tasks from previous sessions
```
```
✅ Created fresh ai-pm-org-main from main (first-time setup)
   Initialized AI project management structure
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

## Git Safety Validation Workflow

### Step 1: Repository Type Detection
**Purpose**: Analyze repository to determine safe workflow adaptations

**Detection Process**:
1. **GitHub CLI Check**: Use `gh repo view --json isFork` when available
2. **Remote Analysis**: Analyze `git remote -v` for repository relationships
3. **Upstream Detection**: Check for upstream relationships and fork indicators
4. **Cache Results**: Store in metadata.json with 24-hour validity
5. **Network Resilience**: Handle failures gracefully with timeout

**User Communication Examples**:
```
🔍 Repository Analysis Complete
📂 Type: Clone (cloned from upstream repository)
⚠️  Safety: Work branches required, main branch protected
🛡️  Workflow: Pull request creation enabled for safe collaboration
```

### Step 2: Workflow Safety Validation
**Purpose**: Check current Git state for workflow safety issues

**Safety Check Process**:
1. **Current Branch Validation**: Ensure appropriate branch for operation
2. **Repository Type Compatibility**: Verify operation safe for repo type
3. **Branch Ancestry Verification**: Validate proper branch relationships
4. **Conflict Detection**: Identify potential dangerous operations

**Safety Response Levels**:
- **High-Severity Blocking**: Block operation, require manual intervention
- **Medium-Severity Warning**: Warn user, provide auto-correction options
- **Low-Severity Info**: Informational messages, operation proceeds

**Auto-Correction Examples**:
```
🔄 Auto-Correction Applied
❌ Blocked: Cannot create branch from 'main' in cloned repository
✅ Switched to 'ai-pm-org-main' for safe branch creation
ℹ️  Recommendation: Work branches should always be created from ai-pm-org-main
```

### Step 3: Branch Ancestry Validation
**Purpose**: Ensure proper Git branch relationships

**Validation Process**:
1. **Ancestry Check**: Verify branch created from ai-pm-org-main
2. **Merge-Base Analysis**: Validate branch relationships using Git
3. **Auto-Switch Logic**: Switch to safe branch when needed
4. **User Communication**: Explain why switching occurred

## Pull Request Integration Workflow

### Step 1: Merge Strategy Determination
**Purpose**: Select appropriate merge strategy based on capabilities

**Strategy Selection Logic**:
1. **Check GitHub CLI**: Available and authenticated?
2. **Validate Repository**: GitHub repository with remote origin?
3. **Assess Conditions**: All PR creation conditions met?
4. **Select Strategy**: Pull request creation or direct merge fallback

**Strategy Communication**:
```
🔀 Merge Strategy: Pull Request Creation
✅ GitHub CLI available and authenticated
✅ GitHub repository detected (origin: github.com/user/repo)
✅ Remote origin configured
📝 Creating pull request for team review...
```

### Step 2: Pull Request Creation Workflow
**Purpose**: Create comprehensive pull request using GitHub CLI

**PR Creation Process**:
1. **Branch Push**: Ensure branch pushed to origin
2. **Title Generation**: Include branch number and user attribution
3. **Description Creation**: Comprehensive description with commit log
4. **PR Execution**: `gh pr create --title "..." --body "..." --base ai-pm-org-main --head branch-name`
5. **URL Return**: Provide PR URL and next steps

**PR Description Template**:
```
## Branch: ai-pm-org-branch-003 by john-doe

### Changes Summary
- Enhanced authentication system with OAuth support
- Added multi-factor authentication capabilities
- Updated login flow with improved security

### Commits
- abc123: Add OAuth integration module
- def456: Implement MFA verification system
- ghi789: Update login flow with security enhancements

### Testing
- [ ] OAuth integration tested
- [ ] MFA workflows verified
- [ ] Security validation completed

### AI Project Manager
Created by AI Project Manager for user: john-doe
Branch: ai-pm-org-branch-003
Creation time: 2025-01-20T15:30:00Z
```

### Step 3: Direct Merge Fallback
**Purpose**: Perform direct Git merge when PR creation not available

**Fallback Triggers**:
- GitHub CLI not available or not authenticated
- Not a GitHub repository
- No remote origin configured
- User explicitly requests direct merge

**Fallback Process**:
1. **Pre-merge Validation**: Ensure branches ready for merge
2. **User Attribution**: Show whose work is being merged
3. **Git Merge**: Standard `git merge` with conflict handling
4. **Explanation**: Explain why direct merge was used
5. **Documentation**: Update tracking with merge details

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
├── .git/
│   ├── main                               # User's project code (untouched)
│   ├── ai-pm-org-main                    # Canonical AI organizational state
│   ├── ai-pm-org-branch-{XXX}
│   ├── ai-pm-org-branch-{XXX}
│   └── ai-pm-org-branch-{XXX}
├── [project source files...]             # All tracked source code
├── projectManagement/                    # AI organizational state (on current branch)
└── .gitignore                           # Updated for MCP
```

### .gitignore Configuration
**Tracked in Git**:
- All project source code (existing behavior)
- AI organizational state (`projectManagement/`) on all branches
- Branch metadata (`.ai-pm-meta.json` on work branches)
- Git merge history (native Git log)

**NOT Tracked**:
- User-specific settings (`projectManagement/UserSettings/`)
- Database backups (`projectManagement/database/backups/`)
- Temporary session files
- Active work logs during development

**Updated .gitignore**:
```gitignore
# Project Management - Track Organizational State, Not User Data
projectManagement/UserSettings/
projectManagement/database/backups/
projectManagement/.mcp-session-*

# Temporary Files
*.tmp
.ai-pm-temp/
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

### Branch Management System
Coordinate with Git branch system using modular architecture:
- Repository type detection through RepositoryDetector module
- Workflow safety validation through GitSafetyChecker module
- Pull request creation and merge operations through MergeOperations module
- Team collaboration setup through TeamCollaboration module

### Git Merge Operations
Enhanced merge capabilities with pull request integration:
- Native Git merge capabilities through GitUtils module
- Pull request creation using GitHub CLI when available
- Direct merge fallback with comprehensive workflow validation
- User attribution and merge documentation across all strategies

### Safety Validation System
Comprehensive Git safety through GitSafetyChecker module:
- Repository-aware workflow safety checks
- Branch ancestry validation and auto-correction
- High-severity blocking for dangerous operations
- Auto-switching to safe branches when needed

### Team Collaboration System
Multi-developer support through TeamCollaboration module:
- Team member detection and AI structure setup
- Remote ai-pm-org-main branch detection and cloning
- Priority logic for branch establishment (Remote > Local > Fresh)
- Automatic user attribution and branch metadata

### Audit System
Enhanced logging with modular error handling:
- Compliance tracking of organizational changes
- Performance analysis of reconciliation effectiveness
- Historical analysis of code change patterns
- Specialized error handling distributed across modules

### Theme Management System
Update theme definitions based on modular impact analysis:
- Code structure changes detected through Git integration
- File addition/deletion/movement patterns
- Directory structure evolution over time
- Repository type-aware theme adaptations

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