# Logging & Documentation Directives

## 9.1 Hybrid Logging Protocol

**Directive**: Use hybrid file-database approach for comprehensive project tracking.

**Primary Logging**:
- `ProjectLogic/projectlogic.jsonl` - Major logic shifts and direction changes (file-based)
- Database: `noteworthy_events` table - Real-time technical decisions and notable events
- `Logs/noteworthy.json` - Archive file created automatically when database events exceed size limits

**What Gets Logged in projectlogic.jsonl**:
- Architecture pivots with direction changes
- Major logic modifications affecting project flow
- Technical discoveries that change project approach
- User-driven direction changes with reasoning

**What Gets Logged in Database (noteworthy_events)**:
- Context escalations (theme-focused → theme-expanded → project-wide)
- User corrections to AI understanding
- Shared file modifications affecting multiple themes
- Notable technical discussions impacting implementation
- Session events, task status changes, and decision patterns
- Real-time analytics for pattern recognition and learning

**What Does NOT Get Logged**:
- Normal task progress (tracked in task files)
- Routine file modifications
- Standard AI responses to clear requests

**Note**: Project logic should hold most of the important logical decisions for the project. Noteworthy should be for more minor decisions or discussion that may need reference. Like asking "why did we do this?", and we hope that there is a note in noteworthy about the change.

### Noteworthy Event Examples

**More potential examples (not exclusive, not limited to, not limited by, not required):**

#### Codebase Structural Adjustments
1. **File Consolidation or Modularization**
   - Merging two modules for simplicity or splitting one for clarity
   - E.g., "Split auth-handler.js into auth-request.js and auth-session.js for testability and separation of concerns."

2. **Directory Structure Changes**
   - E.g., "Moved all theme-related utils into /utils/themes/."

3. **Naming Conventions**
   - Adopting new naming conventions for functions, files, components, etc.
   - E.g., "Renamed all async functions to use fetchXYZ format for clarity."

#### Documentation Decisions
4. **Internal Commenting Practices**
   - "Decided to use JSDoc format in all shared utilities moving forward."

#### Tooling & Workflow Decisions
6. **Linting/Formatting Standard Updates**
   - Adopting Prettier, switching ESLint rules, changing indentation
   - E.g., "Switched from 2-space to 4-space indentation project-wide."

7. **Build Tool / Script Changes**
   - E.g., "Migrated dev script from webpack to vite for faster builds."

8. **Test Coverage Threshold Changes**
   - "Lowered test coverage requirement temporarily from 90% to 80% due to legacy code in /core/legacy/."

#### Design & UX Decisions
9. **UI/UX Adjustments Outside Theme Scope**
   - Minor layout shifts not worth updating themes files
   - E.g., "Centered CTA buttons site-wide for mobile consistency."

#### Dependency Management
11. **Dependency Locking or Switching**
    - "Pinned axios@0.27 to avoid breaking changes in 0.28+."
    - "Switched from moment to date-fns for bundle size reduction."

12. **Polyfill or Shimming Decisions**
    - "Added polyfill for Intl.DisplayNames for Safari 14 compatibility."

#### Performance / Optimization Decisions
13. **Lazy Loading or Code Splitting**
    - "Enabled lazy loading on dashboard widgets to reduce initial load time."

14. **Caching Strategy Tweaks**
    - "Switched to stale-while-revalidate for user profile endpoint."

#### Data and API Modeling
15. **Non-Schema Data Adjustments**
    - "Decided to include userAgent in telemetry logs for session tracing."

16. **Temporary Data Models**
    - "Introduced interim schema for orders while backend finalizes v2."

#### Environment / Debugging / Experiments
17. **Feature Flags / Experimental Toggles**
    - "Introduced isNewOnboardingEnabled flag for A/B test group."

18. **Debug Output Strategy**
    - "Log all payment failures to console.warn during MVP phase."

#### Legacy Cleanup or Deprecation Notices
19. **Marking Legacy Code**
    - "Marked v1/ routes as deprecated; will remove post-launch."

20. **Temporary Workarounds**
    - "Added try-catch around API v1 due to known timeout bug (remove once backend hotfix deployed)."

#### Cross-Cutting Concerns
21. **Cross-Theme Impacts**
    - "Refactored sanitizeInput() to global utility used by both auth and search themes."

22. **Broad Assumption Change**
    - "Stopped assuming all users have email → switched to username || email logic in auth."

#### Decision Confirmations from User Input
23. **User Overrides**
    - "User confirmed preference for manual pagination over infinite scroll."

24. **Preference Lock-Ins**
    - "User prefers explicit file naming over nested folder structure for themes."

File deletions should be noted - it's not too often that files should be deleted, so this is probably a valid reason. Many file deletions due to some decision should be in one note entry, not one note entry for each file. Also note structural changes, discussions on dependencies where new decisions are made, using a different language for a specific file or implementation. File renaming should be noted in noteworthy, but also all other documentation should be reviewed to ensure that any mention of the file is adjusted accordingly.

## 9.2 Automatic Archiving Protocol

**Directive**: Prevent unbounded file growth through size-based archiving.

**Archiving Process**:
1. Before every write, check file size against configured limit
2. If size >= limit: rename file with archive date suffix
3. Create new file with latest entry + archive reference
4. Archives remain available for deeper historical context

**Configuration**:
```json
{
  "archiving": {
    "projectlogic_size_limit": "2MB",
    "noteworthy_size_limit": "1MB"
  }
}
```

**Archive Reference Entry**:
- Links to archived file with entry count and last entry summary
- Provides continuity without loading full archive

### Log Lifecycle Management

The Logs directory contains a single primary file for notable events with automatic archiving to prevent unbounded growth.

#### Primary Log File
- **File**: `Logs/noteworthy.json`
- **Purpose**: Captures AI decisions and user feedback for events worthy of logging
- **Content**: Context escalations, user corrections, shared file modifications, notable discussions
- **Size Limit**: Configurable (default: 1MB)

#### Automatic Archiving
- **Trigger**: Before every write, check if file >= size limit
- **Process**: 
  1. Rename existing file: `noteworthy.json` → `noteworthy-archived-YYYY-MM-DD.json`
  2. Create new file with latest entry + archive reference
- **Archives**: Available for deeper historical context when needed

## 9.3 Logging Triggers

**Directive**: Define specific events that require log entries.

**projectlogic.jsonl Triggers**:
- User states "No, that's not what I want" or similar corrections
- Architecture decisions affecting multiple themes
- Discovery of technical limitations requiring project direction change
- Major flow modifications based on user feedback

**noteworthy.json Triggers**:
- AI escalates context mode due to insufficient information
- AI modifies files shared across multiple themes
- User provides significant technical clarification
- AI makes decisions affecting cross-theme integration

**No Logging Required**:
- Task completion (tracked in task files)
- Normal file edits within single theme
- Standard AI responses to clear instructions

## 9.4 Documentation Update Requirements

**Directive**: Keep all documentation current with project evolution.

**Update Triggers**:
- Theme changes → Update theme descriptions and relationships
- Flow changes → Update ProjectFlow documentation
- Logic changes → Update projectlogic.jsonl entries
- Completion path changes → Update projectManagement/Tasks/completion-path.json
- File structure changes → Update affected README.md files

### Directory Documentation Requirements

**Dual Documentation System**: Every significant directory must maintain both README.md (human-readable) and README.json (AI-optimized) files.

#### README.md Management
With every significant change to code, the README.md in the housing directory must be updated to reflect:

- Purpose of the directory and files included
- Current state assessment for AI quick reference
- Exports and code that can be called externally
- Changes that affect directory information

**Last Updated Section**: The "Last Updated" section should be overwritten each time with only the most recent changes. Do not accumulate historical changes - this avoids redundancy with existing change tracking systems (projectlogic.jsonl, noteworthy.json, task files, git history).

#### README.json Management
The README.json file provides structured AI-optimized directory metadata and must be updated whenever:

- **File Changes**: Files are added, removed, or significantly modified
- **Export Changes**: Functions, classes, or components are added/removed/modified
- **Dependency Changes**: New dependencies added or removed
- **Theme References**: Directory's theme association changes
- **Implementation Status**: File implementation status changes (pending, complete, needs-refactor)

**README.json Update Content**:
- **File inventory**: Complete list of files with descriptions
- **Exports**: Functions, classes, components that can be imported
- **Dependencies**: Internal and external dependencies
- **Theme references**: Which themes this directory relates to
- **File chains**: Logical connections between files
- **Implementation status**: Current state of files and components

**Configuration**: The `lastUpdatedBehavior` setting in config.json controls this behavior:
- `"overwrite"` (default): Replace with most recent changes only - avoids duplicate tracking since we have comprehensive change tracking in projectlogic.jsonl, noteworthy.json, task files, and git history
- `"append"`: Add new changes to existing list (if historical tracking needed for specific use cases)

**Purpose**: Allow AI to assess folder state/files by reading structured metadata instead of investigating code every time.

**Templates available:**
- `reference/templates/README-template.md`
- `reference/templates/README-template.json`

The README.json filename should be configurable in UserSettings/config.json to avoid conflicts if projects already use this naming convention.

## 9.5 README Management Requirements

**Directive**: Maintain README.md files in every significant directory.

**Update Triggers**:
- Any significant code change in directory
- Addition/removal of files
- Change in directory purpose
- New exports or external interfaces
- Architectural changes

**Required Content**:
- Directory purpose and scope
- List of files and their purposes
- Exported functions/classes/components
- Usage examples where appropriate
- Dependencies and relationships
- Recent changes summary