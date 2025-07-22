# MCP-Generated Project Structure & Organization

## Purpose

This structure is created automatically by the MCP server after it is installed and executed for the first time within a user's project. The MCP server itself is downloaded either as a ZIP archive (e.g. from GitHub) or via an NPM package. Upon running, it checks whether a `projectManagement/` folder already exists in the project root.

### MCP Initialization Behavior

- If `projectManagement/` **does not exist**, MCP creates it fresh with the full structure below.
- If `projectManagement/` **exists**, MCP checks:
  - Is it from the same MCP version?
  - If yes, MCP offers to **integrate** the existing data.
  - If no, MCP asks whether to **overwrite**, **rename** (based on a configurable default), or cancel.
- MCP uses an internal `firstRun` flag to determine whether it has been initialized in this project context before.

This document defines the structure that the MCP Server will generate inside a project's root directory (within `projectManagement/`) when it is initiated to manage that project.

The structure is designed to:

- Maintain persistent project context and task state
- Enable AI-driven modular development and task execution
- Support logical scoping, flow control, and task history tracking

## 1. Generated File/Folder Structure

> The `Logs/` directory is for historical analysis and context discussion only. It tracks AI decisions and user feedback for auditing or retrospection. It should be periodically archived and rotated. It is **not** used to determine the current project direction or logic flow.

```
/projectRoot
└── projectManagement/
    ├── .git/                      # Git repository for organizational state management
    ├── .gitignore                 # Ignore user-specific session data and temporary files  
    ├── .mcp-git-config.json       # Git integration configuration and settings
    ├── ProjectBlueprint/
    │   ├── blueprint.md           # High-level summary of the project (user-approved)
    │   └── metadata.json          # Metadata, tags, author, project date, etc.
    ├── ProjectFlow/
    │   ├── flow-index.json          # Master flow index with flow file references and cross-flow dependencies
    │   ├── authentication-flow.json  # Authentication and user management flows
    │   ├── payment-flow.json       # Payment processing and transaction flows
    │   ├── profile-flow.json       # User profile and settings management flows
    │   └── ...                      # Additional flow files organized by domain/theme
    ├── ProjectLogic/
    │   ├── projectlogic.jsonl     # Stateful record of AI/user discussion, decisions, logic evolution
    │   └── archived/
    │       └── projectlogic-archived-2025-07-13.jsonl  # Auto-archived when size limit reached
    ├── Themes/
    │   ├── themes.json            # Master theme index with descriptions
    │   ├── api.json               # Theme definition and structure mapping
    │   ├── walletconnect.json     # Another theme example
    │   └── ...                    # Dynamically added per discovered/defined theme
    ├── Tasks/
    |   ├── completion-path.json      # Evolving roadmap toward project finalization
    │   ├── active/
    │   │   └── TASK-<timestamp>.json         # Task file with milestone, theme, and flow references
    │   ├── sidequests/
    │   │   └── SQ-<tasktimestamp>-<seq>.json # Subtasks spun from main task context
    │   └── archive/
    │       ├── tasks/
    │       └── sidequests/
    ├── Implementations/
    │   ├── active/
    │   │   └── M01-v1-authentication-system.md    # Current milestone implementation plan
    │   └── completed/
    │       └── M00-v1-project-setup.md            # Completed implementation plans
    ├── Logs/
    │   ├── noteworthy.json                # AI decisions and user feedback for notable events
    │   └── archived/
    │       └── noteworthy-archived-2025-07-13.json  # Auto-archived when size limit reached
    ├── Placeholders/
    │   └── todos.jsonl            # Captures all deferred implementation notes and scaffolding TODOs
    ├── UserSettings/
    │   └── config.json            # User-specific configuration (not tracked in Git)
    ├── project.db                 # SQLite database for persistent theme-flow relationships, session tracking, and project analytics
    └── database/
        └── backups/               # Database backups for recovery (recommended periodic backups)
```

> **Note**: This structure is created inside `/projectRoot/projectManagement/` by the MCP server. It represents the project’s managed state and persists throughout development.

## 2. JSON Schemas & Examples

Schemas used in this structure are defined and referenced in `file-construction.md`, `retrieval-guidelines.md`, and other system directives.

## 3. ProjectFlow Outline

The `ProjectFlow/` directory contains multiple flow files organized by domain/theme, managed through a master flow index. This multi-flow structure scales better for complex applications while maintaining clear organization and cross-flow relationships.

### Multi-Flow Structure

**Master Flow Index** (`flow-index.json`):
- Lists all flow files with descriptions and metadata
- Defines cross-flow dependencies and relationships
- Tracks flow completion status and milestone integration
- Provides entry points for AI context loading

**Individual Flow Files** (e.g., `authentication-flow.json`):
- Contains flows specific to a particular domain/theme
- Maintains consistent structure for individual flow files
- Enables focused development and maintenance
- Supports parallel flow development across themes

### Structure Requirements

**Flow Index Requirements** (`flow-index.json`):
- **Flow Files**: List of flow files with descriptions and primary themes
- **Cross-Flow Dependencies**: Dependencies between flows across different files
- **Global Flow Settings**: Project-wide flow configuration and validation rules
- **Flow File Metadata**: Creation dates, update tracking, and status information

**Individual Flow File Requirements** (e.g., `authentication-flow.json`):
- **Trigger**: The initiating user action (button click, QR scan, URL visit, form submission)
- **Steps**: Sequential user experience steps with page navigation and interface elements
- **User Experience**: What users see, interact with, and experience at each step
- **Conditions**: User decision points and branching paths based on user state/choices
- **Outcomes**: Final user experience results and next available user actions
- **Cross-Flow References**: References to flows in other flow files
- **Theme Integration**: Primary and secondary themes associated with each flow

### JSON Format Examples

See complete example structures in:
- `reference/templates/flow-index.json` - Master flow index structure
- `reference/templates/authentication-flow.json` - Individual flow file structure

### User Experience Flow Management

**Flow-Level Status Tracking:**
- Each user flow has overall status: `pending`, `in-progress`, `complete`, `needs-review`
- Completion percentage based on user experience implementation
- Integration with completion path milestones for feature validation

**Step-Level Status Tracking:**
- Individual step status: `pending`, `in-progress`, `complete`, `needs-analyze`, `blocked`
- Step dependencies to ensure logical user experience progression
- Completion dates for implemented user experience steps
- Page/interface references with implementation status

**User Experience Validation:**
- Milestones reference required user flows for feature completion
- Flow progress validation ensures complete user journeys
- Clear mapping between strategic milestones and user experience implementation

### Flow Management

**Multi-Flow Organization:**
- **Theme-Based Grouping**: Flows organized by primary themes (authentication, payment, profile, etc.)
- **Cross-Flow Dependencies**: Flows can reference flows in other files through flow-index
- **Selective Loading**: AI loads only relevant flow files based on task context
- **Parallel Development**: Multiple flow files can be developed simultaneously

**Flow Status Management:**
- **Incomplete Flows**: Pages/interfaces can be `null`, `"pending"`, or `"not-implemented"` when not yet built
- **Interface Status**: Each page/interface reference can include status (`"exists"`, `"pending"`, `"needs-design"`)
- **User Testing Integration**: Can reference user testing scenarios per step
- **Status Progression**: Steps progress through defined status transitions with proper validation

### AI Usage Guidelines

The multi-flow structure enables AI to:
- **Selective Context Loading**: Load only relevant flow files based on task themes
- **Cross-Flow Validation**: Verify dependencies between flows in different files
- **Scalable Flow Management**: Handle complex applications with 20+ flows efficiently
- **Parse and traverse user flows programmatically within focused domains
- **Identify missing user experience implementations by checking page/interface existence
- **Generate user testing scenarios based on flow steps within specific themes
- **Validate user interface completeness against defined flows
- **Update flows when new user interactions, pages, or features are added

### Benefits of Multi-Flow Structure

**Scalability**: Handles complex applications like ChainSale with 20+ flows
**Maintainability**: Focused flow files easier to update and maintain
**Performance**: AI loads only relevant flows, reducing memory usage
**Collaboration**: Teams can work on different flow files simultaneously
**Organization**: Clear thematic organization matches project structure

> **Important**: The multi-flow system is the definitive map of user experience journeys organized by domain. It helps validate interface completeness, identify missing user paths, and serves as a blueprint for user testing and user experience development. The flow-index ensures cross-flow relationships are maintained while individual flow files enable focused development.

## 4. ProjectLogic Outline

`ProjectLogic/projectlogic.jsonl` is a stateful file that tracks the evolving logic of the project over time. Unlike logs or simple historical notes, this file records structured reasoning, key decisions, branching logic considerations, AI-user discussions about direction, and the rationale behind flow or architecture changes.

### Relationship to Blueprint and Flow

`projectlogic.jsonl`, the `ProjectFlow/` directory (flow-index.json + individual flow files), and `blueprint.md` are the **three central project-wide intelligence files**. They serve different purposes but must always remain aligned:

- `blueprint.md` – Plain-language, high-level purpose and summary of the project. For the user.
- `ProjectFlow/` directory – User experience flows, interactions, and interface journeys organized by domain. User flow modeling.
- `projectlogic.jsonl` – Compact AI/user logic map, state transitions, reasoning, and direction shifts.

### Evaluation Schedule

These three files must be evaluated:

- **Before and after** every task file (not per subtask)
- Especially when project **functionality** or **design logic** changes—not necessarily when simple code changes occur
- Before task execution to ensure current logic is available
- After task completion to verify if direction, themes, or design has shifted

### Format Consideration

- `blueprint.md`: Markdown, always human-readable, reviewed manually
- `flow-index.json` and individual flow files (e.g., `authentication-flow.json`): JSON format multi-flow system organized by domain, optionally generated via AI for validation and coverage checking
- `projectlogic.jsonl`: Structured JSONL format for efficient parsing and updating by AI

See complete example entries in `reference/templates/projectlogic.jsonl`.

All entries should include timestamp, category/type, and affected components. The AI should always present human-readable summaries before writing to this file.

## 5. Completion Path Outline

`Tasks/completion-path.json` defines a hierarchical, evolving roadmap toward project finalization. Unlike the flexible task system, this file focuses on long-term direction with a definitive goal. It exists to:

- Prevent infinite development loops or open-ended feature creep
- Anchor project progress toward a concrete `completionObjective`
- Track and update milestone steps throughout the development lifecycle
- Inform MCP of the project's current state, stalled areas, or final stages

### Structure and Maintenance

- Written in **JSON**, not JSONL, for easy AI parsing and editing
- Steps are individually tracked with status, related tasks, and optional completion dates
- Steps may be marked `pending`, `in-progress`, or `complete`
- May include `relatedTasks` array for traceability

This file works in tandem with the three base guideline files (blueprint, logic, and flow) to continuously check alignment with the end goal.

### JSON Structure Example

See complete example structure in `reference/templates/completion-path.json`.

### Field Definitions

- **completionObjective**: The final goal with success criteria
- **metadata**: Creation date, version, and project timeline info
- **milestones**: Major project phases with deliverables and dependencies
- **riskFactors**: Potential blockers and mitigation strategies
- **progressMetrics**: Current progress tracking and projections

### Usage Guidelines

- AI must present all changes to user for approval
- Steps can be added, reordered, or removed but only between current progress and end objective
- Dependencies between milestones must be maintained
- Progress metrics should be updated after each milestone completion

---

## 6. Implementation Plans System

The `Implementations/` directory provides strategic implementation planning for each milestone in the completion path. This system bridges the gap between high-level milestone objectives and detailed task execution.

### 6.1 Implementation Plan Lifecycle

#### Creation Process
1. **Milestone Selection**: When a milestone from `completion-path.json` is ready for implementation
2. **Analysis Phase**: AI analyzes current project state, requirements, and dependencies
3. **Plan Generation**: Create detailed implementation plan with phases, architecture decisions, and strategy
4. **User Approval**: Present plan to user for review and approval before execution begins

#### Execution Process
1. **Phase Breakdown**: Implementation plan divided into logical phases
2. **Task Generation**: Each phase generates specific tasks in `Tasks/active/`
3. **Progress Tracking**: Track completion through phases toward milestone completion
4. **Adaptation**: Plan can be updated if requirements change during implementation

#### Completion Process
1. **Milestone Validation**: Verify all plan objectives and success criteria met
2. **Plan Archival**: Move completed plan to `completed/` directory
3. **Next Milestone**: Generate implementation plan for next milestone in completion path

### 6.2 File Naming Convention

**Format**: `M{milestone-id}-v{version}-{description}.md`

**Examples**:
- `M01-v1-authentication-system.md` - Initial implementation plan for milestone M01
- `M02-v1-payment-processing.md` - Implementation plan for milestone M02
- `M01-v2-authentication-system.md` - Revised plan if milestone M01 requirements change

**Versioning Rules**:
- **v1**: Initial implementation plan for milestone
- **v2, v3, etc.**: Revised plans if milestone scope or requirements change
- **Never overwrite**: Previous versions preserved to maintain decision history

### 6.3 Archival System

#### Automatic Archival Triggers
- **Milestone Completion**: When all plan phases completed and milestone marked complete
- **Plan Supersession**: When a new version of the implementation plan is created
- **Project Restructure**: When completion path milestones are reorganized

#### Archival Process
1. **Completion Validation**: Verify milestone completion criteria met
2. **File Movement**: Move from `active/` to `completed/` directory
3. **Metadata Update**: Update completion date and final status
4. **Reference Preservation**: Maintain links to related tasks and decisions in projectlogic.jsonl

#### Naming in Archive
- **Completed Plans**: Retain original naming (e.g., `M01-v1-authentication-system.md`)
- **Superseded Plans**: Add suffix (e.g., `M01-v1-authentication-system-superseded.md`)
- **Index Maintenance**: Update archive index with completion dates and outcomes

### 6.4 Integration with Session Boot Directive

The implementation plans system transforms the session boot process:

**Enhanced Session Boot Sequence**:
1. Read ProjectBlueprint, ProjectFlow, projectlogic.jsonl
2. Read completion-path.json for milestone status
3. **NEW**: Check for active implementation plan in `Implementations/active/`
4. **NEW**: Load current implementation plan context and phase progress
5. Review incomplete tasks in context of current implementation plan
6. Generate tasks for current implementation plan phase
7. Begin execution with full strategic context

**Benefits**:
- **Strategic Continuity**: AI maintains implementation strategy across sessions
- **Reduced Context Switching**: No need to re-explain complex implementation approaches
- **Focused Task Generation**: Tasks generated within framework of current implementation plan
- **Progress Clarity**: Clear understanding of current phase and next steps

### 6.5 Template Structure

Each implementation plan follows a standardized template:

```markdown
# Implementation Plan: M{milestone-id} - {Milestone Title}

## Metadata
- **Milestone**: M{milestone-id}
- **Status**: active|completed|superseded
- **Version**: v{version}
- **Created**: {date}
- **Updated**: {date}
- **Completion Target**: {date}

## Analysis
- Current state assessment
- Requirements breakdown
- Dependencies identification
- Risk factors and mitigation
- Architecture considerations

## Strategy
- Implementation approach and rationale
- Key architecture decisions
- Integration points with existing systems
- Testing and validation strategy
- Performance considerations

## Phases
### Phase 1: {Phase Name}
- **Objectives**: What this phase accomplishes
- **Deliverables**: Specific outputs
- **Tasks**: High-level task breakdown
- **Dependencies**: What must be completed first
- **Success Criteria**: How to validate phase completion

### Phase 2: {Phase Name}
[Similar structure]

## Success Criteria
- Completion markers for entire milestone
- Validation requirements
- Quality gates
- User acceptance criteria

## Notes
- Implementation decisions and rationale
- User feedback and modifications
- Lessons learned during execution
```

### 6.6 Version Control and Conflict Prevention

#### Duplicate Prevention
- **Milestone Completion Check**: Verify milestone not already completed before creating new plan
- **Version Increment**: Automatically increment version if plan already exists for milestone
- **User Confirmation**: Always confirm with user before creating new version

#### Change Management
- **Scope Changes**: New version created if milestone requirements change significantly
- **Minor Updates**: In-place updates for clarifications and small adjustments
- **Approval Process**: All plan modifications require user approval
- **Change Documentation**: All changes logged in projectlogic.jsonl

This implementation plans system provides the strategic planning layer that bridges high-level project goals with detailed task execution, ensuring consistent progress toward project completion.

---

## 6.7 Templates and Examples Directive

**Template Source**: All organizational file templates are located in the `reference/templates/` directory in the MCP server repository.

**AI Usage Directive**: When creating any organizational files (`completion-path.json`, `flow-index.json`, individual flow files, task files, implementation plans, etc.), AI must use the corresponding example file in `reference/templates/` as the template structure.

**Template Files Available**:
- `reference/templates/completion-path.json` - Completion path structure and milestones
- `reference/templates/flow-index.json` - Master flow index structure
- `reference/templates/authentication-flow.json` - Individual flow file structure with enhanced status tracking
- `reference/templates/task-active.json` - Active task file structure
- `reference/templates/sidequest.json` - Sidequest file structure
- `reference/templates/implementation-plan-template.md` - Implementation plan template
- `reference/templates/projectlogic.jsonl` - Project logic entry formats
- `reference/templates/noteworthy.json` - Noteworthy events logging
- `reference/templates/config.json` - User settings configuration
- `reference/templates/themes.json` - Theme definitions
- `reference/templates/todos.jsonl` - TODO tracking format
- `reference/templates/README-template.md` - Standard README template for directories
- `reference/templates/README-template.json` - AI-specific directory metadata template

**Implementation Requirement**: MCP server must reference `reference/templates/` directory when generating any organizational files to ensure consistency and proper structure across all managed projects.

---

## 7. Database Integration System

### 7.1 SQLite Database Overview

**Purpose**: Maintain persistent theme-flow relationships, session tracking, and project analytics using a cross-platform SQLite database.

**Database Location**: `projectManagement/project.db`

**Key Features**:
- **Theme-Flow Relationships**: Many-to-many relationships between themes and flows
- **Session Tracking**: Session start times, duration, context, and activity
- **File Modifications**: Track all file changes and operations
- **Task Metrics**: Task completion metrics and velocity tracking
- **User Preferences**: Learn and store user preferences over time
- **Theme Evolution**: Track theme changes and evolution over time

### 7.2 Database Schema

**Schema Location**: `mcp-server/database/schema.sql` (422-line comprehensive schema, source of truth)
**Security**: Schema never copied to project directories to prevent accidental corruption

**Core Tables**:
- `sessions` + `session_context` - Session persistence and context snapshots  
- `task_status` + `sidequest_status` + `subtask_status` - Complete task lifecycle management
- `task_queue` - Multi-task coordination with context preservation
- `task_sidequest_limits` - Multiple sidequest support with automatic enforcement
- `theme_flows` + `flow_status` + `flow_step_status` - Theme-flow intelligence with status tracking
- `file_modifications` + `directory_metadata` + `file_metadata` - Intelligent file operations
- `user_preferences` - AI learning and adaptation
- `task_metrics` + `theme_evolution` - Analytics and insights
- `noteworthy_events` + `event_relationships` - Real-time event analytics

**Advanced Features**:
- Multiple sidequest support with configurable limits and relationship tracking
- Views and triggers for automated updates and complex query optimization  
- Performance indexes optimized for large-project scalability
- Subtask-sidequest relationship coordination for complex workflow management

### 7.3 Database Architecture

**Project Database Instance**: `projectManagement/project.db` (SQLite database file)
**Database Backups**: `projectManagement/database/backups/` - Periodic database backups for recovery

**MCP Server Database Infrastructure**: `mcp-server/database/`
- `schema.sql` - Master schema definition (source of truth, never copied)
- `db_manager.py` - Enhanced connection management with thread safety and transactions
- `session_queries.py` (490 lines) - Session persistence, context snapshots, boot optimization
- `task_status_queries.py` (771 lines) - Task/subtask/sidequest lifecycle with multiple sidequest support
- `theme_flow_queries.py` (831 lines) - Theme-flow intelligence, fast context loading, flow status tracking
- `file_metadata_queries.py` (561 lines) - Intelligent file discovery, impact analysis
- `user_preference_queries.py` (561 lines) - User learning and AI adaptation system
- `event_queries.py` (500+ lines) - Real-time event analytics and pattern recognition

### 7.4 Database Operations

**Core Database Components**:
- `DatabaseManager` - Enhanced connection management with transactions and optimization
- `SessionQueries` - Complete session lifecycle with context preservation
- `TaskStatusQueries` - Full task/sidequest/subtask management with analytics
- `ThemeFlowQueries` - Theme-flow intelligence with fast lookup capabilities
- `FileMetadataQueries` - Intelligent file operations and impact analysis
- `UserPreferenceQueries` - User learning and AI adaptation
- `EventQueries` - Real-time event tracking and analytics

**Key Operations**:
- **Session Management**: `start_session()`, `get_session_context()`, `save_context_snapshot()`
- **Task Operations**: `create_task()`, `update_task_status()`, `manage_sidequests()`
- **Theme-Flow Intelligence**: `get_themes_for_flow()`, `get_flows_for_theme()`, `sync_theme_flows()`
- **File Operations**: `log_file_modification()`, `get_file_impact()`, `discover_file_relationships()`
- **User Learning**: `learn_preference()`, `get_user_patterns()`, `adapt_behavior()`
- **Analytics**: `get_project_health()`, `analyze_performance()`, `predict_context_needs()`

### 7.5 Theme-Flow Relationship Management

**Flow Reference Structure in Themes**:
```json
{
  "flows": [
    "most-relevant-flow-id",
    "second-most-relevant-flow-id",
    "least-relevant-flow-id"
  ]
}
```

**Database Integration**:
- Themes reference flows by ID only (single source of truth in theme files)
- Database maintains fast lookup tables in `theme_flows` table with relevance ordering
- MCP uses flow-index.json + database queries for optimal context loading
- Supports complex many-to-many relationships with automatic sync capabilities
- Real-time updates via database triggers maintain consistency between files and database
- Context optimization through database queries enables efficient large-project handling

### 7.6 Session Tracking

**Enhanced Session Management**:
- Complete session state preserved across disconnections
- Context snapshots save/restore complete AI context for seamless continuity  
- Multi-session support handles multiple concurrent AI sessions
- Activity tracking monitors session duration, themes accessed, tasks worked on
- Boot optimization enables quick session restoration from database context
- Session analytics provide productivity patterns and performance insights

**Advanced Capabilities**:
- Uninterrupted workflow with task switching and complete context preservation
- Sidequest coordination via context snapshots for seamless task-sidequest transitions
- Performance analytics deliver session productivity metrics and optimization recommendations
- User adaptation learns optimal session patterns for improved efficiency

### 7.7 Cross-Platform Compatibility

**SQLite Advantages**:
- Works on Windows, Mac, and Linux
- Same database file works across all platforms
- No separate server or configuration required
- Portable and embeddable
- Excellent performance for project-scale data

---

## 8. Integrated Task Structure

### Task File Integration Requirements

All TASK files must integrate with the three core organizational systems to ensure coherency and traceability:

1. **Milestone Integration**: Every task must reference a milestone from `completion-path.json`
2. **Theme Integration**: Every task must specify primary and related themes
3. **Multi-Flow Integration**: Every subtask must reference specific flow steps with flow file context

### TASK File Structure Example

See complete example structure in `reference/templates/task-active.json` and `reference/templates/sidequest.json`.

### Integration Benefits

**Hierarchical Context:**
- **Milestone** → **TASK** → **Subtask** → **Flow File** → **Flow Steps**
- Each level provides progressively more detailed context

**Complete Traceability:**
- From high-level project goals down to specific user interactions
- AI can understand both "why" (milestone) and "how" (flows) for each task
- Flow file context provides focused domain understanding

**Efficient Context Loading:**
- AI knows which themes to load for understanding project boundaries
- AI knows which flow files to load for user experience consistency
- Selective flow loading reduces memory usage and improves performance
- README-guided approach prevents unnecessary code analysis while ensuring completeness

**Cross-Reference Validation:**
- Tasks must align with milestone deliverables
- Subtasks must implement specific flow steps from identified flow files
- Flow files must exist in ProjectFlow/ directory
- Flow steps must exist within referenced flow files
- Themes must contain referenced files

### Usage Guidelines

**Task Creation:**
- Must reference valid milestone ID from completion-path.json
- Must specify primary theme and related themes
- Each subtask must reference specific flow steps with flow file context
- ContextMode determines how much theme context to load

**Multi-Flow Context Loading (README-Guided):**
- AI loads milestone context for high-level goals
- AI loads theme structure via README files first
- AI loads flow-index.json to understand available flow files
- AI loads only relevant flow files based on task requirements
- AI determines necessary code files based on task requirements
- AI loads flow steps for implementation details from specific flow files

**Validation Rules:**
- Referenced milestone must exist in completion-path.json
- Referenced themes must exist in Themes/ directory
- Referenced flow files must exist in ProjectFlow/ directory
- Referenced flow steps must exist within specified flow files
- Flow files must be registered in flow-index.json
- Referenced files should exist or be marked as pending

---

## 9. MCP Theme Directive (Auto-Discovery)

- During initial project scan or when creating a project from scratch, the MCP will auto-discover and define "themes" based on folder clusters, naming patterns, imports, or user-designated categories.
- For each new theme discovered:
  - Create a file in `/projectManagement/Themes/` named after the theme (e.g. `transactions.json`, `walletconnect.json`)
  - Define all file paths and folders related to that theme, even if they span across `components/`, `hooks/`, `services/`, etc.
  - These files are updated dynamically as new files/folders are added to the project
  - If a file/folder is removed or moved, the theme file must also be updated
  - A global `themes.json` file is maintained to describe all current themes and provide definitions

### Auto-Maintenance Logic for Theme Discovery:

- MCP uses keyword matching, folder path structure, and import reference graphs to discover thematic relevance
- Any time files/folders are created, moved, or deleted, MCP will:
  - Reassess related theme files and update paths and links accordingly
  - Flag conflicts or duplicates and propose merges if overlapping themes are detected
- Theme files include:
  ```json
  {
    "theme": "transaction",
    "paths": ["src/services/transactions/", "src/components/transaction/"],
    "files": ["src/hooks/transaction/useTransaction.ts"],
    "linkedThemes": ["wallet"],
    "sharedFiles": {
      "src/types/Transaction.ts": {
        "sharedWith": ["wallet", "api"],
        "description": "Transaction type definitions"
      }
    }
  }
  ```
- MCP will maintain a `themes.json` root-level theme index with:
  ```json
  {
    "transaction": "Handles all transaction-related logic, UI, and service calls",
    "wallet": "Internal wallet, key signing, connection flows"
  }
  ```
- If a file clearly belongs to multiple themes, it may appear in both and be flagged as `shared: ["theme1", "theme2"]`
- When AI modifies a shared file, it should assess impact on all listed themes before proceeding

### Theme-Based Context Loading Strategy

#### Context Modes
- **theme-focused** (default): Load primary theme + directly related themes
- **theme-expanded**: Load theme group when themes are interconnected  
- **project-wide**: Full project context (rare, only for architectural changes)

#### README-Guided Context Assessment
1. **Theme Structure Loading**: AI reads theme JSON files to understand project areas
2. **Directory README Assessment**: AI reads README.md files in relevant directories for context
3. **File Selection**: AI determines specific code files needed based on task requirements
4. **Minimal Code Analysis**: AI avoids unnecessary code evaluation unless determined essential

#### Context Loading Process
1. Load primary theme files structure from `Themes/[theme].json`
2. Load related theme interfaces and shared files
3. Read README.md files in relevant directories for quick context
4. AI assesses specific files needed for the task
5. AI can request theme-expanded if insufficient context
6. User can override to project-wide if architectural changes needed

#### Benefits
- **Efficient Memory Usage**: READMEs provide context without code analysis
- **Intelligent Assessment**: AI determines necessity rather than rigid rules
- **Flexible Escalation**: Natural expansion when more context needed
- **Directory-Level Context**: README files provide folder-level understanding

### Global Dependencies and Project Root Context

#### Always-Available Files
Certain files and folders are always accessible regardless of theme context, following normal AI assessment behavior:

**Project Root Level:**
- Configuration files: `package.json`, `requirements.txt`, `Cargo.toml`, `composer.json`
- Environment files: `.env`, `.env.local`, `config.json`, `settings.json`
- Build/deployment files: `Dockerfile`, `docker-compose.yml`, `Makefile`, `vite.config.js`
- Documentation: `README.md`, `LICENSE`, `CHANGELOG.md`
- Version control: `.gitignore`, `.gitattributes`

**Source Root Level (e.g., `src/`):**
- Entry points: `index.js`, `main.ts`, `app.js`, `App.tsx`
- Global configuration: `config/`, `constants/`, `types/`, `utils/`
- Core application files: `app.js`, `router.js`, `store.js`

#### Context Accessibility
- **Available as needed**: Files are not force-loaded but remain accessible for AI assessment
- **Normal AI behavior**: AI determines relevance and necessity using standard evaluation
- **Cross-theme relevance**: Global files can be accessed from any theme context
- **Modification allowed**: AI can modify these files when contextually appropriate

#### Shared File Impact Assessment
When modifying shared files, AI should:
1. **Identify affected themes**: Check `shared: ["theme1", "theme2"]` array
2. **Quick impact assessment**: Review each theme's README for potential conflicts
3. **Proceed with awareness**: Make changes while considering cross-theme implications
4. **Document cross-theme changes**: Log modifications affecting multiple themes

## 10. Log Management Strategy

### Simplified Log Management

The Logs directory contains a single primary file for notable events with automatic archiving to prevent unbounded growth.

### Log Lifecycle Management

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

### Noteworthy Event Entry Structure

See complete entry format examples in `reference/templates/noteworthy.json` and `reference/templates/projectlogic.jsonl`.

### Configuration Options

Logging configuration in `UserSettings/config.json`:
```json
{
  "archiving": {
    "projectlogic_size_limit": "2MB",
    "noteworthy_size_limit": "1MB"
  }
}
```

**Note**: Detailed directives for both `projectlogic.jsonl` and `noteworthy.json` logging triggers will need to be defined in the complete directive set.

---

## 11. Key Interaction Directives (For MCP Server Only)

> These are not part of the projectManagement structure. They live in the MCP server and govern AI behavior when managing any project.

- `retrieval-guidelines.md`: how to determine what context to load
- `file-construction.md`: rules for structuring and writing files
- `revision-rules.md`: how and when to revise the structure with user approval

---