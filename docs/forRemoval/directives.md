# Complete AI Project Manager Directives

## Purpose & Scope

This document defines comprehensive directives for AI behavior when using the AI Project Manager MCP Server. These directives ensure consistent, intelligent, and efficient project management across all sessions and tasks.

**Critical**: All directives must be followed. They govern how AI interacts with projects, manages context, handles tasks, and maintains project organization.

---

## Table of Contents

1. [System Initialization Directives](#1-system-initialization-directives)
2. [Project Management Directives](#2-project-management-directives)
3. [Theme Management Directives](#3-theme-management-directives)
4. [Context Loading Directives](#4-context-loading-directives)
5. [Task Management Directives](#5-task-management-directives)
6. [File Operation Directives](#6-file-operation-directives)
7. [Session Management Directives](#7-session-management-directives)
8. [Logging & Documentation Directives](#8-logging--documentation-directives)
9. [Quality Assurance Directives](#9-quality-assurance-directives)
10. [Error Handling Directives](#10-error-handling-directives)
11. [User Interaction Directives](#11-user-interaction-directives)

---

## 1. System Initialization Directives

### 1.1 MCP Server Connection Protocol

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

### 1.2 Project Detection and Compatibility

**Directive**: Always detect existing project management structures and handle compatibility issues.

**Rules**:
- If `projectManagement/` exists, check version compatibility
- If compatible, integrate existing data
- If incompatible, ask user for migration approach (upgrade, backup, or overwrite)
- Never overwrite existing data without explicit user permission
- Document any compatibility issues or migrations performed

### 1.3 Configuration Loading Protocol

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

---

## 2. Project Management Directives

### 2.1 Project Initialization Protocol

**Directive**: Follow this exact sequence when initializing projects:

```
1. Validate project path exists and is accessible
2. Check for existing projectManagement/ structure
3. If exists, run compatibility check (see 1.2)
4. Create complete directory structure:
   - ProjectBlueprint/
   - ProjectFlow/
   - ProjectLogic/
   - Themes/
   - Tasks/{active,sidequests,archive/{tasks,sidequests}}
   - Logs/{current,archived,compressed}
   - Placeholders/
   - UserSettings/
5. Initialize all required files with proper templates
6. Set appropriate metadata (creation date, version, etc.)
7. Confirm successful initialization
```

### 2.2 Project Blueprint Management

**Directive**: ProjectBlueprint is the single source of truth for project purpose and scope.

**Rules**:
- Blueprint must be user-approved before any development begins
- Changes to blueprint require explicit user confirmation
- Blueprint must be plain language, not technical specifications
- Always reference that detailed scope information is in Themes/
- Update blueprint metadata on any changes
- Blueprint should be 1-3 pages maximum for clarity

**Required Content**:
- Project overview and purpose
- Key features and scope
- Success criteria
- Constraints and limitations
- References to detailed technical specifications in themes

### 2.3 Multi-Flow System Documentation

**Directive**: ProjectFlow/ directory must contain organized flow files managed through a master flow index.

**Multi-Flow Structure Requirements**:
- **Master Flow Index** (`flow-index.json`): Lists all flow files with dependencies and metadata
- **Individual Flow Files** (`*-flow.json`): Domain-specific flows organized by theme
- **Cross-Flow Dependencies**: Managed through flow-index.json for complex user journeys
- **Selective Loading**: AI loads only relevant flow files based on task context

**Flow File Organization**:
- **Theme-Based Grouping**: Flows organized by primary themes (authentication-flow.json, payment-flow.json)
- **Naming Convention**: `{domain}-flow.json` (e.g., authentication-flow.json, profile-flow.json)
- **JSON Format**: Machine-readable for AI processing and validation
- **Flow File Limits**: Configurable via `contextLoading.maxFlowFiles` (default: 3)

**Individual Flow Requirements**:
- Each flow must specify: trigger, steps, file trails, conditions, outcomes
- Files can be marked as `null`, `"pending"`, or `"not-implemented"`
- Cross-reference with theme files for implementation details
- Cross-flow references must specify both flowId and flowFile
- Update flows when new features or interactions are added

### 2.4 Project Logic Tracking

**Directive**: ProjectLogic/projectlogic.jsonl tracks evolving project reasoning and decisions.

**Entry Requirements**:
- Timestamp and session ID
- Decision type and reasoning
- Impact on project direction
- User interactions and approvals
- Logic changes and their rationale

**Update Triggers**:
- Major architecture decisions
- Theme modifications
- Flow changes
- User-requested direction changes
- Significant technical pivots

---

## 3. Theme Management Directives

### 3.1 Automatic Theme Discovery Protocol

**Directive**: Theme discovery is mandatory for new projects and must follow user review process.

**Discovery Sequence**:
```
1. Analyze project structure using FileAnalyzer
2. Identify themes across 6 categories:
   - Functional Domains (auth, payment, user-management, etc.)
   - Technical Layers (database, api, security, testing, etc.)
   - User Interface (components, pages, layout, styling)
   - External Integrations (social-media, analytics, maps, etc.)
   - Data Management (validation, transformation)
   - Operational (logging, monitoring, deployment)
3. Calculate confidence scores with evidence collection
4. Identify custom themes from project-specific patterns
5. MANDATORY: Present to user for review
6. Incorporate user feedback and modifications
7. Get explicit approval before creating theme files
8. Document theme decisions in projectlogic.jsonl
```

**Critical**: NEVER create theme files without user approval.

### 3.2 Theme Presentation Format

**Directive**: Always present discovered themes using this exact format:

```
## Discovered Project Themes

I've analyzed your project and identified the following themes:

**Functional Domains:**
1. **Authentication** - User login, registration, session management
2. **Payment Processing** - Transaction handling, billing, checkout flows

**Technical Layers:**
3. **Database** - Models, schemas, migrations, queries
4. **API** - Controllers, routes, middleware, endpoints

**User Interface:**
5. **UI Components** - Reusable components, forms, layouts

**External Integrations:**
6. **Email Service** - Notifications, verification, communications

Would you like to:
- Add additional themes I may have missed?
- Modify descriptions of existing themes?
- Remove themes that aren't relevant?
- Rename themes to better match your project terminology?
```

### 3.3 Theme File Structure Requirements

**Directive**: All theme files must follow this exact JSON structure:

```json
{
  "theme": "theme-name",
  "category": "functional_domains|technical_layers|user_interface|external_integrations|data_management|operational|user-defined",
  "description": "Clear description of theme purpose and scope",
  "confidence": 0.0-1.0,
  "paths": ["src/theme-dir", "components/theme-components"],
  "files": ["specific/files.ts", "related/files.js"],
  "linkedThemes": ["related-theme-1", "related-theme-2"],
  "sharedFiles": {
    "shared/file.ts": {
      "sharedWith": ["theme1", "theme2"],
      "description": "Description of sharing relationship"
    }
  },
  "frameworks": ["react", "express"],
  "keywords": ["keyword1", "keyword2"],
  "createdDate": "ISO timestamp",
  "lastModified": "ISO timestamp"
}
```

### 3.4 Theme Validation Requirements

**Directive**: Validate theme consistency before any theme-related operations.

**Configuration**: `themes.sharedFileThreshold` (default: 3)

**Validation Checks**:
- All referenced files and paths exist
- Linked themes are valid and exist
- No circular dependencies in theme relationships
- Shared files are properly documented
- Theme descriptions are clear and distinct
- File coverage is comprehensive (all project files in at least one theme)
- Shared file limit: No single file should be shared by more than `themes.sharedFileThreshold` themes
- When threshold exceeded: Suggest theme reorganization or file refactoring, note that threshold can be increased if necessary

### 3.5 Theme Modification Protocol

**Directive**: Handle theme modifications through proper approval process.

**User-Requested Changes**:
1. Analyze current theme structure
2. Propose modification with impact assessment
3. Show before/after comparison
4. Get explicit user approval
5. Update theme files and relationships
6. Update themes index
7. Document changes in projectlogic.jsonl

**AI-Initiated Updates**:
1. Identify improvement opportunity
2. Present proposed change with clear reasoning
3. Explain benefits to project organization
4. Get explicit user approval
5. Implement changes only after approval
6. Document rationale and impact

---

## 4. Context Loading Directives

### 4.1 Context Mode Selection Protocol

**Directive**: Always use appropriate context mode based on task complexity and theme relationships.

**Mode Definitions**:
- **theme-focused**: Primary theme only (~15 files, ~1MB memory)
- **theme-expanded**: Primary + linked themes (~15-25 files, ~1-2MB memory)
- **project-wide**: All themes (~23+ files, ~2+ MB memory)

**Selection Logic**:
1. Start with theme-focused for simple tasks
2. Escalate to theme-expanded if:
   - Task mentions cross-theme integration
   - Primary theme has >2 linked themes
   - Shared files are involved
3. Use project-wide only for:
   - Architecture changes
   - Global refactoring
   - Cross-cutting concerns

### 4.2 README-Guided Context Loading

**Directive**: Always prioritize README files for quick context understanding.

**Configuration**: `contextLoading.readmeFirst` (default: true)

**Multi-Flow Context Loading Protocol**:
1. Load theme structure from JSON files
2. **Load flow-index.json** to understand available flow files and cross-flow dependencies
3. **Selective Flow Loading**: Load only relevant flow files based on task requirements
4. When `contextLoading.readmeFirst` is true: Read README.md files in relevant directories (limit 2KB each)
5. Assess task requirements to determine needed files
6. Use README context to avoid unnecessary code analysis
7. Load specific code files only when determined essential
8. Maintain flexibility to access additional files when needed

**Flow File Loading Rules**:
- **Theme-Focused**: Load flow files associated with primary theme
- **Theme-Expanded**: Load flow files from primary + related themes  
- **Project-Wide**: Load all flow files (subject to `contextLoading.maxFlowFiles` limit)
- **Cross-Flow Dependencies**: Always load referenced flow files from flow-index.json

**Flow Scope vs Theme Scope Protocol**:
- **Flow Scope**: Initial context loading for resource management and performance optimization
- **Theme Scope**: Always available as the defined scope boundary for complete context
- **Automatic Expansion**: AI can expand from flow scope to theme scope without user approval
- **Resource Management**: Start with flow scope, expand to theme scope when needed
- **No Restrictions**: Flow scope is a performance optimization, not a limitation
- **Self-Implemented**: AI determines when flow scope is insufficient and expands automatically

**README Priority Order**:
1. Project root README.md
2. Theme directory READMEs
3. Subdirectory READMEs in loaded paths

### 4.3 Global File Access Protocol

**Directive**: Certain files are always accessible regardless of theme context.

**Always-Accessible Files**:
- Configuration: `package.json`, `requirements.txt`, `*.config.js`, `.env`
- Documentation: `README.md`, `LICENSE`, `CHANGELOG.md`
- Entry points: `index.js`, `main.ts`, `app.js`, `App.tsx`
- Global utilities: `src/config/`, `src/constants/`, `src/types/`, `src/utils/`
- Build/deployment: `Dockerfile`, `docker-compose.yml`, `Makefile`

**Access Rules**:
- Available when contextually relevant
- No forced loading
- Modification allowed when appropriate
- Cross-theme accessibility maintained

### 4.4 Context Escalation Protocol

**Directive**: Handle mid-task context escalation through structured decision process.

**Escalation Decision Tree**:
```
1. Assess if sidequest can resolve the issue
   - If yes: Create sidequest instead of escalating
   - If no: Proceed to context escalation

2. Determine escalation need:
   - Current context insufficient for proper implementation
   - Cross-theme dependencies discovered
   - Architectural changes needed
   - Risk of breaking changes without broader context

3. User communication:
   - Explain specific need for broader context
   - Present options (sidequest vs escalation)
   - Request explicit permission
   - Document escalation reasoning

4. Implementation:
   - Maximum one escalation per task
   - Log escalation in ai-decisions.jsonl
   - Update noteworthy.json
   - Prepare rollback if escalation doesn't resolve issue
```

**User Notification Format**:
```
I need to expand context to properly implement [specific requirement].

Current context: [theme-focused: payment]
Needed context: [theme-expanded: payment + security + api]

Reason: [Discovered that payment validation requires security middleware that affects API responses]

Options:
1. Create sidequest to handle security middleware separately
2. Expand context to theme-expanded mode
3. Defer this requirement to a separate task

Recommended approach: [2 - Context expansion]
```

### 4.5 Memory Optimization Requirements

**Directive**: Maintain optimal memory usage and performance.

**Optimization Rules**:
- Limit README files to 2KB each
- Stream large files instead of loading into memory
- Use lazy loading for theme definitions
- Estimate memory usage and warn if >100MB
- Recommend context reduction if memory usage excessive
- Cache frequently accessed theme data

---

## 5. Task Management Directives

### 5.1 Task File Structure Requirements

**Directive**: All task files must integrate with themes, milestones, and multi-flow system.

**Required Task File Structure**:
```json
{
  "id": "TASK-YYYYMMDDTHHMMSS",
  "title": "Clear, concise task title",
  "description": "Detailed task description",
  "status": "pending|in-progress|completed|blocked",
  "priority": "high|medium|low",
  "milestone": "M-XX",
  "primaryTheme": "theme-name",
  "relatedThemes": ["theme1", "theme2"],
  "contextMode": "theme-focused|theme-expanded|project-wide",
  "createdDate": "ISO timestamp",
  "lastModified": "ISO timestamp",
  "subtasks": [
    {
      "id": "ST-XX",
      "description": "Subtask description",
      "status": "pending|in-progress|completed",
      "flowReferences": [
        {
          "flowId": "flow-id",
          "flowFile": "domain-flow.json",
          "steps": ["step-id-1", "step-id-2"]
        }
      ],
      "files": ["affected/files.ts"],
      "estimatedTime": "duration"
    }
  ],
  "dependencies": ["TASK-ID-1", "TASK-ID-2"],
  "blockers": ["Description of blocking issues"],
  "notes": ["Task progress notes"],
  "completionCriteria": ["Criteria for completion"]
}
```

### 5.2 Task Lifecycle Management

**Directive**: Follow proper task lifecycle and status management.

**Status Transitions**:
- `pending` → `in-progress`: When task work begins
- `in-progress` → `completed`: When all completion criteria met
- `in-progress` → `blocked`: When external dependency prevents progress
- `blocked` → `in-progress`: When blocker resolved
- Any status → `pending`: When task needs to be reset

**Update Requirements**:
- Update status immediately when changed
- Document status change reasons
- Maintain task history for retrospection
- Archive completed tasks according to retention policy

### 5.3 Sidequest Management Protocol

**Directive**: Use sidequests for tangential work that doesn't fit main task flow.

**Sidequest Creation Criteria**:
- Work is related but not central to main task
- Can be completed independently
- Doesn't require main task context
- May benefit from different theme context

**Sidequest File Structure**:
```json
{
  "id": "SQ-PARENTTASK-SEQUENCE",
  "parentTask": "TASK-YYYYMMDDTHHMMSS",
  "title": "Sidequest title",
  "scopeDescription": "Why this sidequest was created",
  "status": "pending|in-progress|completed",
  "theme": "primary-theme",
  "contextMode": "theme-focused|theme-expanded",
  "dateTimeStarted": "ISO timestamp",
  "estimatedDuration": "duration",
  "completionCriteria": ["Criteria for completion"]
}
```

### 5.4 Completion Path Integration

**Directive**: All tasks must align with project completion path and milestones.

**Integration Requirements**:
- Every task must reference a milestone from completion-path.json
- Task completion moves milestone progress forward
- Milestone completion unlocks dependent milestones
- Changes to completion path require user approval
- Track progress metrics and projections

**Completion Path Structure**:
```json
{
  "completionObjective": "Clear end goal definition",
  "metadata": {
    "createdDate": "ISO timestamp",
    "version": "1.0.0",
    "estimatedCompletion": "target date"
  },
  "milestones": [
    {
      "id": "M-01",
      "description": "Milestone description",
      "status": "pending|in-progress|completed",
      "dependencies": ["M-00"],
      "deliverables": ["List of deliverables"],
      "relatedTasks": ["TASK-IDs"],
      "estimatedEffort": "duration",
      "completedOn": "ISO timestamp"
    }
  ],
  "riskFactors": ["Identified risks and mitigation"],
  "progressMetrics": {
    "currentProgress": 0.0-1.0,
    "estimatedCompletion": "projected date",
    "velocity": "tasks per unit time"
  }
}
```

### 5.5 Parallel Task Management

**Directive**: Support multiple concurrent tasks with proper coordination.

**Parallel Task Rules**:
- Only one task can be `in-progress` per session
- Tasks can be `pending` or `blocked` concurrently
- Sidequests can run parallel to main tasks
- Coordinate shared file modifications
- Prevent conflicting changes to same files
- Document dependencies and relationships

---

## 6. File Operation Directives

### 6.1 Line Limit Enforcement

**Directive**: Enforce maximum file line limits to prevent unwieldy files.

**Configuration**: `project.maxFileLineCount` (default: 900)

**Rules**:
- Read line limit from `project.maxFileLineCount` in config.json
- Check line count after every file modification
- If limit exceeded, modularize into logical functional groups
- Create properly named module files
- Update imports and references
- Maintain proper linking system (index files)

**Modularization Guidelines**:
- Group by function/responsibility
- Maintain clear naming conventions
- Preserve all functionality
- Update all references
- Document modularization in README.md

### 6.2 Anti-Placeholder Protocol

**Directive**: Never use placeholder text or truncated outputs.

**Configuration**: `project.avoidPlaceholders` (default: true)

**Prohibited Patterns**:
- `...continued`
- `rest of file unchanged`
- `// TODO: implement this`
- `/* placeholder */`
- Truncated code blocks
- Incomplete implementations without explicit user permission

**Required Behavior**:
- When `project.avoidPlaceholders` is true: Always output complete implementations
- If file too large, modularize before outputting
- If scope unclear, ask for clarification
- No speculative summarization
- Full content required unless user explicitly allows partial output
- Track any TODO items in Placeholders/todos.jsonl for later resolution

### 6.3 File Modification Protocol

**Directive**: Handle file operations with proper validation and backup.

**Configuration**: `project.backwardsCompatibility` (default: false), `project.productionMode` (default: false)

**Backwards Compatibility Behavior**:
- When `project.backwardsCompatibility` is false: AI can make breaking changes directly, overwrite/remove old code
- When `project.backwardsCompatibility` is true: AI must preserve existing interfaces and create migration paths
- When `project.productionMode` is true: Forces backwards compatibility regardless of setting

**Pre-Modification Checks**:
1. Verify file exists and is accessible
2. Check if file is shared across themes
3. Assess impact on related themes
4. Review README context for directory
5. Consider backwards compatibility requirements
5. Validate against line limits
6. Consider backup if destructive operation

**Shared File Handling**:
1. Identify all themes sharing the file
2. Read READMEs for affected themes
3. Assess cross-theme impact
4. Document modifications in ai-decisions.jsonl
5. Note potential impacts in noteworthy.json
6. Update theme READMEs if necessary

### 6.4 README Management Requirements

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

---

## 7. Session Management Directives

### 7.1 Session Boot Protocol

**Directive**: Follow exact sequence when starting new sessions or "continue development".

**Boot Sequence**:
```
1. Read ProjectBlueprint for project understanding
2. Read ProjectBlueprint for project understanding
3. Read ProjectFlow for interaction understanding
4. Read projectlogic.jsonl for reasoning history
5. Read completion-path.json for current objectives
6. Review active tasks (Tasks/active/*.json)
7. If no active tasks, review last completed tasks
8. If needed, review archived task lists
9. Determine next steps with priority suggestions
10. Get user approval for direction
11. Determine context mode based on selected work
12. Generate task list for approved direction
13. Load theme context for selected tasks
14. Begin task execution
14. Begin task execution
```

### 7.2 Session Summary Management

**Directive**: Maintain session state through persistent project files.

**Required Content**:
```json
{
  "lastUpdated": "ISO timestamp",
  "sessionId": "SESSION-YYYYMMDDTHHMMSS",
  "context": "Brief current context description",
  "activeTasks": ["TASK-IDs currently in progress"],
  "recentTasks": ["Recently completed TASK-IDs"],
  "currentTheme": "primary-theme-being-worked-on",
  "contextMode": "current context mode",
  "nextSteps": ["Planned next actions"],
  "blockers": ["Current blocking issues"],
  "recentDecisions": ["Recent key decisions"],
  "memoryUsage": "estimated MB",
  "loadedThemes": ["currently loaded themes"]
}
```

**Update Frequency**:
- After every task status change
- After context escalation
- After significant decisions
- At session end
- When switching between tasks

### 7.3 Session Continuity Requirements

**Directive**: Ensure seamless transitions between sessions.

**State Preservation**:
- All work states saved in appropriate files
- Context loading can recreate working environment
- Task dependencies and relationships maintained
- User preferences and decisions preserved
- Project logic evolution tracked

**Recovery Capabilities**:
- Can resume from any interruption point
- Previous session state fully recoverable
- Context can be recreated from saved state
- Task progress maintained across sessions

---

## 8. Logging & Documentation Directives

### 8.1 Simplified Logging Protocol

**Directive**: Use simplified dual-file approach for project tracking.

**Primary Files**:
- `ProjectLogic/projectlogic.jsonl` - Major logic shifts and direction changes
- `Logs/noteworthy.json` - Technical decisions and notable events

**What Gets Logged in projectlogic.jsonl**:
- Architecture pivots with direction changes
- Major logic modifications affecting project flow
- Technical discoveries that change project approach
- User-driven direction changes with reasoning

**What Gets Logged in noteworthy.json**:
- Context escalations (theme-focused → theme-expanded → project-wide)
- User corrections to AI understanding
- Shared file modifications affecting multiple themes
- Notable technical discussions impacting implementation

**What Does NOT Get Logged**:
- Normal task progress (tracked in task files)
- Routine file modifications
- Standard AI responses to clear requests

### 8.2 Automatic Archiving Protocol

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

### 8.3 Logging Triggers

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

### 8.4 Documentation Update Requirements

**Directive**: Keep all documentation current with project evolution.

**Update Triggers**:
- Theme changes → Update theme descriptions and relationships
- Flow changes → Update ProjectFlow documentation
- Logic changes → Update projectlogic.jsonl entries
- Completion path changes → Update completion-path.json
- File structure changes → Update affected README.md files

---

## 9. Quality Assurance Directives

### 9.1 Testing Protocol

**Directive**: Maintain standard testing practices without theme-based over-testing.

**Standard Testing Scope**:
- Test specific components/functions being developed
- Test actual integration points (APIs, databases, etc.)
- Test specific user flows being implemented
- Follow project's existing test frameworks

**Theme Context for Testing**:
- Use themes for understanding component purpose
- Use themes for locating appropriate test file placement
- Use themes for understanding dependencies
- DO NOT test entire themes comprehensively unless explicitly requested

**Prohibited Testing**:
- Automatic comprehensive theme testing
- Artificial test suites based solely on theme membership
- Cross-theme testing without specific integration work
- Testing unrelated components just because they share a theme

### 9.2 Validation Requirements

**Directive**: Validate all project artifacts for consistency and correctness.

**Theme Validation**:
- All referenced files and paths exist
- Linked themes are valid
- No circular dependencies
- Shared files properly documented
- Theme coverage is complete

**Task Validation**:
- All referenced milestones exist
- Theme references are valid
- Flow step references are correct
- Dependencies are properly defined
- Completion criteria are clear

**File Validation**:
- Line limits respected
- No placeholder content
- Proper modularization
- All imports/exports functional
- README files current

### 9.3 Code Quality Standards

**Directive**: Maintain high code quality without introducing placeholders.

**Quality Requirements**:
- Complete implementations only
- Proper error handling
- Clear naming conventions
- Appropriate comments (but not placeholder comments)
- Consistent formatting
- Modular architecture

**Quality Checks**:
- No TODO comments without associated tasks
- No placeholder functions
- No dead code
- No unused imports
- Proper type definitions where applicable

---

## 10. Error Handling Directives

### 10.1 Error Recovery Protocol

**Directive**: Handle errors gracefully with proper recovery mechanisms.

**Error Categories**:
- File system errors (permissions, missing files)
- Configuration errors (invalid settings, missing config)
- Theme errors (invalid definitions, missing themes)
- Task errors (invalid references, circular dependencies)
- Context errors (memory issues, loading failures)

**Recovery Actions**:
1. Log error with full context
2. Assess impact on current task
3. Determine recovery options
4. Present options to user if manual intervention needed
5. Implement recovery or fallback
6. Document recovery in decision log
7. Update affected artifacts

### 10.2 Validation Error Handling

**Directive**: Handle validation failures with clear explanations and recovery options.

**Validation Failure Response**:
1. Identify specific validation failure
2. Explain impact on project/task
3. Provide specific correction steps
4. Offer to fix automatically if possible
5. Get user approval for corrections
6. Document validation issues and resolutions

### 10.3 Context Loading Error Recovery

**Directive**: Handle context loading failures with graceful degradation.

**Recovery Strategy**:
1. If theme loading fails, fall back to basic file operations
2. If README loading fails, use file system exploration
3. If memory limits exceeded, recommend context reduction
4. If theme references invalid, validate and repair
5. Always maintain minimum viable context for progress

---

## 11. User Interaction Directives

### 11.1 User Approval Requirements

**Directive**: Certain operations require explicit user approval before execution.

**Mandatory Approval Operations**:
- Theme creation or modification
- ProjectBlueprint changes
- Completion path modifications
- Context escalation
- File structure changes affecting multiple themes
- Breaking changes to shared files

**Approval Format**:
```
I need your approval to [specific action].

Current state: [description]
Proposed change: [detailed change description]
Impact: [assessment of effects]
Alternatives: [other options if applicable]

Do you approve this change? (yes/no)
```

### 11.2 User Communication Protocol

**Directive**: Communicate clearly and concisely with users about system operations.

**Communication Guidelines**:
- Explain technical decisions in plain language
- Provide context for why actions are needed
- Offer multiple options when possible
- Explain impact of decisions
- Request clarification when requirements unclear
- Confirm understanding before proceeding

### 11.3 Preference Learning and Adaptation

**Directive**: Learn from user preferences and adapt behavior accordingly.

**Adaptation Areas**:
- Preferred context modes for different task types
- Theme organization preferences
- Documentation detail levels
- Testing scope preferences
- Communication style preferences

**Preference Storage**:
- Document preferences in UserSettings/config.json
- Include preference reasoning in projectlogic.jsonl
- Respect established patterns unless user requests changes
- Ask for clarification when preferences conflict

---

## 12. Compliance and Audit Directives

### 12.1 Audit Trail Requirements

**Directive**: Maintain complete audit trails for all significant operations.

**Audit Trail Components**:
- All AI decisions with reasoning
- All user interactions and approvals
- All file modifications with context
- All theme changes with impact assessment
- All task state changes with triggers
- All context escalations with justification

### 12.2 Data Integrity Protocol

**Directive**: Ensure data integrity across all project management artifacts.

**Integrity Checks**:
- Cross-reference validation between files
- Consistency checks between themes and tasks
- File existence validation for all references
- JSON schema validation for structured files
- Backup verification for critical operations

### 12.3 Version Control Integration

**Directive**: Work harmoniously with version control systems.

**Version Control Awareness**:
- Respect .gitignore and similar patterns
- Document significant changes in appropriate commit contexts
- Consider impact on code reviews
- Maintain clean file states for commits
- Avoid creating conflicts with development workflows

---

## Implementation Notes

### Priority Levels

**Critical (Must Follow)**: System initialization, user approval requirements, anti-placeholder protocol
**High (Standard Practice)**: Theme management, context loading, file operations
**Medium (Best Practice)**: Logging protocols, documentation updates, quality assurance
**Low (Optimization)**: Performance optimizations, preference learning

### Validation Checklist

Before completing any significant operation, verify:
- [ ] User approval obtained for required operations
- [ ] All file modifications logged appropriately
- [ ] Theme consistency maintained
- [ ] Context loading performed efficiently
- [ ] Task states updated correctly
- [ ] Documentation kept current
- [ ] Quality standards maintained
- [ ] Error handling implemented

### Continuous Improvement

These directives should evolve based on:
- User feedback and preferences
- System performance metrics
- Error patterns and resolutions
- Workflow efficiency observations
- Technology updates and capabilities

---

**Version**: 1.0.0  
**Last Updated**: 2025-07-12  
**Status**: Complete and Ready for Implementation