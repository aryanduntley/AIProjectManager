### Additional Directives to Track

> Also includes evolving structure for clear project progression and end-goal definition

> Below is a list of MCP server-level directives planned for implementation. These govern AI decision-making and project integration workflows across managed projects. Each directive will eventually reside in the MCP's internal `/directives/` directory.
resumeTasksOnStart autoTaskCreation (theme)autoDiscovery

**Initial (First intall) Assessment**
### NEW PROJECT
Discuss with user goals of project. Be as detailed as needed to fulfil the goals and needs of the organization files, especially the core blueprint and flow files. 
Once you have enough information, create project blueprint
  ensure projectblueprint is assessed and approved by the user.
Once projectblueprint is in place, begin discussing project flow with the user.
  Discuss the user interactions with various parts of the software and the outcomes of those actions.
  create flow-index.json and individual flow files for different domains (authentication-flow.json, payment-flow.json, etc.)
Need to know the logic of how and why for the various parts of the project.
  Track the logic and reasoning of various parts of the project from user discussion
  As project progresses and new logic/decisions made, record in projectlogic
At this point, outline a starting point of themes
  create an assessment of themes based on the existing data and the newly created blueprint, flow files and logic file if created and already populated
  present to user the assessment for approval and once discussed and approved, generate the themes files
  for missing data (files not yet created) create todos and log in todos.jsonl
Once initial themes are generated (themes can evolve as anything else in a project) outline a completion path (also an evolving file)
  get user approval of completion path.
Generate the first implementation plan that should involve creating the scafolding for the project.
  A README.md and README.json file for every directory should be included in scaffolding and updates as changes are made to the files in the folder
  user approval if autoTaskCreation is false
With implementation plan, generate first task file
  user approval if autoTaskCreation is false
On begin task, handle as normal. Evolve completion path, themes, blueprint, flow, logic and any other organizatioal files and data as needed. 
  ensure that blueprint metadata is updates as the project progresses, especially at firt run during scaffolding when dependencies and infrastructure is being created
  ensure that todos are managed well through tasks
On scaffolding complete, review todos for file references needed for themes and any other core organizational files

### EXISTING PROJECT
Discuss with user goals of project. Be as detailed as needed to fulfil the goals and needs of the organization files, especially the core blueprint and flow files. 
Once you have enough information, create project blueprint
  ensure projectblueprint is assessed and approved by the user.
Once projectblueprint is in place, begin discussing project flow with the user.
  Discuss the user interactions with various parts of the software and the outcomes of those actions.
  create flow-index.json and individual flow files for different domains (authentication-flow.json, payment-flow.json, etc.)
Need to know the logic of how and why for the various parts of the project.
  Track the logic and reasoning of various parts of the project from user discussion
  As project progresses and new logic/decisions made, record in projectlogic
At this point, outline a starting point of themes
  create an assessment of themes based on the existing data and the newly created blueprint, flow files and logic file if created and already populated
  present to user the assessment for approval and once discussed and approved, generate the themes files
  for missing data (files not yet created) create todos and log in todos.jsonl
At this point entire project must be evaluated. Ask user if ready to begin (this may take a while).
  upon approval, begin reviewing the infrastructure. Once you have a full understanding, update the core organizational files and metadata accordingly
  Then evaluate the project folders
  Assess the size of the project and determin, based on size, whether you should be more or less aggressive with reading the files (smaller size, more files can be read; larger size, may need to read fewer files or read fewer lines in the files. ).
  This process is resource intensive, make sure it's know to the user that the initial read through will take time and credits.
  Begin reading files in each directory one by one
  Only project folders and files. Avoid dependency folders like deps, node_modules, git, etc. If unsure, do a quick review to ensure that it's a project folder/files from wich the code, flow, logic, blueprint, completion-path can be evolved.
    Once read for given directory
      Before moving to subdirectory, create or update existing README.md file in directory according to the directives for these README files. And create the README.json file
      Note in the README file last updated
      After README and before moving on to next directory or subdirectory, upate all relevant organizational files as needed, with the new information. Themes may need to be updated, discuss with user for approval. Blueprint may need to be updated, discuss with user for approval. Logic may need amending or clarification, discuss with user for approval. Steps in completion path can start to be defined. There may be noteworthy information that would be useful to log based on your discoveries during this project.
      Using this method, if premature termination of session occurs, tracking progress can be achieved by way of the README.json files. If folder does not have, or last updated not up to date, you know the folder has not been assessed and/or the data relative to the folder has not been incorporated fully into the organizational files.
  Recursive, and continue for each folder until complete.
  Once complete, review core files for consistency and accuracy. 
  If all is good, and initialization is complete

Generate the first implementation plan
  user approval if autoTaskCreation is false
With implementation plan, generate first task file
  user approval if autoTaskCreation is false
On begin task, handle as normal. Evolve completion path, themes, blueprint, flow, logic and any other organizatioal files and data as needed. 
  ensure that blueprint metadata is updates as the project progresses
  ensure that todos are managed well through tasks

**1. Session Boot Directive**

### Enhanced Session Boot Sequence with Implementation Plan Integration

**Core Requirements:**
- Defines the steps AI must follow at the beginning of each session
- Requires loading of `blueprint.md`, `flow-index.json` and relevant flow files, `projectlogic.jsonl`, `completion-path.json`, `noteworthy.json`, `Implementations/active/{activeImplementationPlan.md` if exists, `Tasks/active/{activeTask}.json` if exists
- **NEW**: Check for active implementation plan in `Implementations/active/`
- **NEW**: Load current implementation plan context and phase progress
- Ensures proposed updates are confirmed by user before changing anything

**Session Boot Sequence:**
1. **Core Project Files**: Load `blueprint.md`, `flow-index.json` and relevant flow files, `projectlogic.jsonl`
2. **Strategic Context**: Read `completion-path.json` for milestone status
3. **Implementation Plan Context**: Check `Implementations/active/` for current implementation plan
4. **Noteworthy Context**: Check `noteworthy.json` for latest noteworthy data
5. **Flow Status Assessment**: Load project flow status and completion percentages
6. **Task Context**: Review `Tasks/active/{activeTask}.json` for any incomplete tasks
7. **Next Steps Determination**: Generate tasks for current implementation plan phase or identify next milestone
  - If settings in config.json resumeTasksOnStart true AND incomplete tasks, summarize incomplete task list to user and note that resumeTasksOnStart is set to true and continuing task.
  - If no incomplete tasks and autoTaskCreation is true
    - If current implementation plan and not complete
      - assess state and create next tasks, summarize tasks for user and create new task file.
     - If no current implementation plan or current implementation plan is complete
      - review all statuses, review completion-path, asses state, summarize to user state and indicate ready for next implementation plan
        - if approved, archive complete implementation plan if not already, generate new implementation plan, generate new task file, summarize tasks, ask user to start.
        - if not, await further instructions.
  - If no incomplete tasks and autoTaskCreation is false
    - If current implementation plan and not complete
      - assess state and summarize tasks for user; await approval
     - If no current implementation plan or current implementation plan is complete
      - review all statuses, review completion-path, asses state, summarize to user state and indicate ready for next implementation plan
        - if approved, archive complete implementation plan if not already, generate new implementation plan
          - assess state and next tasks, summarize tasks, ask user if ready to create next task file
            - if approved create new task file
              - ask user if they are ready to begin tasks
            - if not, await further instruction
        - if not, await further instruction

**Implementation Plan Integration:**
- **Active Implementation Plan**: If exists, load current phase and progress
- **Phase Context**: Understanding of current implementation phase and objectives
- **Task Generation**: Create tasks based on current implementation plan phase
- **Strategic Continuity**: Maintain implementation strategy across sessions
- **No Implementation Plan**: If no active plan, analyze next milestone and create implementation plan

**Task Management Logic:**
```
1. Check for active/incomplete tasks in Tasks/active/ directory
2. Load configuration setting: tasks.resumeTasksOnStart (default: false)
3. If active/incomplete tasks found:
   a. If resumeTasksOnStart = true:
      - Automatically resume active tasks
      - Load appropriate context for task continuation
      - Begin task execution with full context
   b. If resumeTasksOnStart = false:
      - List all incomplete tasks with status and descriptions
      - Present user with clear options:
        "I found the following incomplete tasks:
        - TASK-ID: Description (status: in-progress)
        - TASK-ID: Description (status: pending)
        
        Would you like to resume these tasks or start with a new objective?"
      - Wait for user decision before proceeding
4. If no active tasks found:
   a. Read last completed tasks from Tasks/archive/
   b. Compare last completed tasks to completion-path.json
   c. Identify next milestone or implementation plan phase
   d. Check for active implementation plan in Implementations/active/
   e. If no implementation plan, analyze next milestone for plan creation
```

**Task Completion Updates**
review completed task or sidequest file
if sidequest, review and update task file if needed
review completion-path update if needed
review implementation plan update if needed, archive if needed
review flow-index.json and individual flow files, update if needed
make any noteworthy notes to noteworthy.json (if needed, do not feel obligated to add things here)

if sidequest, archvie sidequest file

if task file,  ensure no fragmented sidequests
  if fragments exists, review and complete sidequests
    if issues arise, handle normally, involve user in decisions on how to proceed
    once complete review fragmented sidequest file
      review completion-path update if needed
      review implementation plan update if needed, archive if needed
      review flow-index.json and individual flow files, update if needed
      make any noteworthy notes to noteworthy.json (if needed, do not feel obligated to add things here)
      archive fragmented sidequest files
archive task file

**User Discussion Assessments**
Discussion with user about flow, logic, structure, dependecies, enhancements, refactoring, UI, coding practice, etc. Things that could change the project blueprint, things that could change the way the themes are defined or the files they may relate to, things that could change the logic or understanding of the project as a whole, things that could change the logic of a certain aspect of the project, decision about the workings of any part of the project, etc. The core project files and other organizatin files need to be reviewed and changed if needed. Change what is needed and try not to make changes just because "you're there". All changes to these files EXCEPT noteworthy and projectlogic, must be explicity aproved by the user. For projectlogic, since it's a historical record, make a generalized summary of changes made to projectlogic based on recent discussion.

When these discussions occur and decisions are made:

review blueprint update if needed
review metadata update if needed
review projectlogic, update if needed
review themes.json update if needed
review theme files in Themes, update if needed according to themes.json, theme files must always match themes.json
review completion-path update if needed
review implementation plan update if needed, archive if needed
review flow-index.json and individual flow files, update if needed
make any noteworthy notes to noteworthy.json (if needed, do not feel obligated to add things here)

**Flow Status Integration:**
- **Flow Progress Assessment**: Check completion percentage of flows required for current milestone
- **Milestone Validation**: Ensure milestone cannot be completed until required flows are complete
- **Step-Level Context**: Understand which flow steps are pending or in-progress
- **Context Mode Determination**: Choose appropriate context mode based on flow requirements

**Implementation Plan Lifecycle Management:**
- **Plan Creation**: When milestone is ready, create detailed implementation plan
- **Phase Execution**: Break plan into phases, generate tasks for current phase
- **Progress Tracking**: Monitor phase completion and flow step progress
- **Plan Completion**: Archive completed plan, generate next milestone's implementation plan
- **Strategic Continuity**: Each plan references previous learnings and decisions

**2. Simplified Logging Protocol**

**Purpose**: Capture noteworthy events that affect project direction without duplicating task or chat history.

**Primary Approach**: Use existing `projectlogic.jsonl` for major logic shifts/direction changes, plus simplified `Logs/noteworthy.json` for technical decisions.

**Structure**:
```
Logs/
├── noteworthy.json                # AI decisions and user feedback for notable events  
└── archived/
    └── noteworthy-archived-2025-07-13.json  # Auto-archived when size limit reached
```
**What Gets Logged in `noteworthy.json`**:
- Context escalations (theme-focused → theme-expanded → project-wide)
- User corrections to AI understanding ("No, that's not what I want")
- Shared file modifications affecting multiple themes
- Notable technical discussions that impact implementation

**What Does NOT Get Logged**:
- Normal task progress (that's in task files)
- Chat history (stored in Claude/AI system)
- Routine file modifications
- Standard AI responses to clear user requests

**Archiving**: 
- File size limit configurable (default: 1MB)
- Before every write: check size → archive if needed → create new file with latest entry + archive reference
- Archives available for deeper context when needed

**Integration with Existing Files**:
- Major logic shifts → Use existing `projectlogic.jsonl` (with archive support)
- Task progress → Task files (active/archive)
- Project direction → `completion-path.json`

**Crypto Payment Example**: Your wallet-connect pivot belongs in `projectlogic.jsonl`:
```json
{
  "type": "architecture-pivot",
  "description": "Shifted from app-managed to wallet-as-black-box approach",
  "previousDirection": "App manages all transaction logic internally", 
  "newDirection": "User wallet handles all transactions, app only provides interface",
  "reasoning": "WalletConnect doesn't provide private key access"
}
```

**Note**: Project logic should hold most of the important logical decisions for the project. Noteworthy should be for mor minor decisions or discussion that may need reference. Like asking "why did we do this?", and we hope that there is a note in noteworthy about the change.
file deletions. It's not too often that files should be deleted, so this is probably a valid reason. Many file deletions due to some decision should be in one note entry, not one note entry for each file.
structural changes
discussions on dependecies where new decisions are made could be useful notes
using a different language for a specific file or implementation of a specific feature. If not significant enough to be noted in project logic.
file renaming. If files are removed or renamed, it should be noted in noteworthy but also all other documenttion should be reviewed to ensure that any mention of the file is adjusted accordingly.

More potetial examples (not exclusive, not limited to, not limited by, not required)
Codebase Structural Adjustments
1. File Consolidation or Modularization
Merging two modules for simplicity or splitting one for clarity.
E.g., “Split auth-handler.js into auth-request.js and auth-session.js for testability and separation of concerns.”

2. Directory Structure Changes
E.g., “Moved all theme-related utils into /utils/themes/.”

3. Naming Conventions
Adopting new naming conventions for functions, files, components, etc.
E.g., “Renamed all async functions to use fetchXYZ format for clarity.”

Documentation Decisions
4. Internal Commenting Practices
“Decided to use JSDoc format in all shared utilities moving forward.”

Tooling & Workflow Decisions
6. Linting/Formatting Standard Updates
Adopting Prettier, switching ESLint rules, changing indentation.
E.g., “Switched from 2-space to 4-space indentation project-wide.”

7. Build Tool / Script Changes
E.g., “Migrated dev script from webpack to vite for faster builds.”

8. Test Coverage Threshold Changes
“Lowered test coverage requirement temporarily from 90% to 80% due to legacy code in /core/legacy/.”

Design & UX Decisions
9. UI/UX Adjustments Outside Theme Scope
Minor layout shifts not worth updating themes files.
E.g., “Centered CTA buttons site-wide for mobile consistency.”

Dependency Management
11. Dependency Locking or Switching
“Pinned axios@0.27 to avoid breaking changes in 0.28+.”
“Switched from moment to date-fns for bundle size reduction.”

12. Polyfill or Shimming Decisions
“Added polyfill for Intl.DisplayNames for Safari 14 compatibility.”

Performance / Optimization Decisions
13. Lazy Loading or Code Splitting
“Enabled lazy loading on dashboard widgets to reduce initial load time.”

14. Caching Strategy Tweaks
“Switched to stale-while-revalidate for user profile endpoint.”

Data and API Modeling
15. Non-Schema Data Adjustments
“Decided to include userAgent in telemetry logs for session tracing.”

16. Temporary Data Models
“Introduced interim schema for orders while backend finalizes v2.”

Environment / Debugging / Experiments
17. Feature Flags / Experimental Toggles
“Introduced isNewOnboardingEnabled flag for A/B test group.”

18. Debug Output Strategy
“Log all payment failures to console.warn during MVP phase.”

Legacy Cleanup or Deprecation Notices
19. Marking Legacy Code
“Marked v1/ routes as deprecated; will remove post-launch.”

20. Temporary Workarounds
“Added try-catch around API v1 due to known timeout bug (remove once backend hotfix deployed).”

Cross-Cutting Concerns
21. Cross-Theme Impacts
“Refactored sanitizeInput() to global utility used by both auth and search themes.”

22. Broad Assumption Change
“Stopped assuming all users have email → switched to username || email logic in auth.”

Decision Confirmations from User Input
23. User Overrides
“User confirmed preference for manual pagination over infinite scroll.”

24. Preference Lock-Ins
“User prefers explicit file naming over nested folder structure for themes.”

**3. Compatibility Verification**

- Directive for how MCP checks the compatibility of an existing `projectManagement/` structure
- Includes logic to detect mismatched or outdated MCP formats
- ProjectBlueprint/metadata.json should have version, date created, namespace (project.management.organization.{userprojectname})

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

**7. Task File Structure**

**Task File Structure** (`reference/templates/task-active.json`):
- **Core Identity**: `taskId`, `title`, `description`, `created`, `lastUpdated`, `status`
- **Milestone Integration**: References milestone from `completion-path.json`
- **Theme Integration**: Primary theme and related themes for context loading
- **Subtasks**: Array of subtasks with individual scope, flow references, and file lists
- **Project Flow Integration**: Each subtask references specific `projectFlows` and `flowSteps`
- **Context Mode**: Per-subtask context mode (theme-focused/theme-expanded/project-wide)
- **Dependencies**: Inter-subtask dependencies and blockers
- **Testing**: Unit, integration, e2e, and security testing requirements
- **Documentation**: API docs, user guides, and technical specifications

**Sidequest File Structure** (`reference/templates/sidequest.json`):
- **Sidequest Identity**: `sidequestId`, `parentTask`, `title`, `description`
- **Scope Context**: `scopeDescription`, `reason`, `urgency`, `impactOnParentTask`
- **Inheritance**: Inherits milestone and themes from parent task
- **Subtasks**: Similar structure to main tasks but with sidequest-specific IDs
- **Completion Trigger**: Defines what constitutes completion
- **Notes**: Additional considerations and observations

**Key Integration Requirements**:
- All tasks must reference valid milestones from `completion-path.json`
- All subtasks must reference specific project flows and flow steps
- Context mode determines theme loading scope
- File lists enable targeted context loading
- Dependencies ensure proper execution order
- Tasks should reference active implementation plans when applicable

**8. TODO Tracking Logic**

- The `/Placeholders/todos.jsonl` file collects all placeholder tasks, `TODO:` notes, and deferred scaffolding from AI-generated code
- Each entry contains:
  - Timestamp
  - File and line reference
  - Reason for deferral or notes
- This log enables MCP to:
  - Aggregate incomplete logic across the project
  - Propose task creation for unhandled `TODO` items
  - Review code quality and scaffolding completeness
- These entries are optional and can be cross-referenced with `Tasks/` if any are formalized into proper subtasks

**9. Completion Path Tracking with Flow Integration**

### Enhanced Completion Path Management

**Core Structure:**
- MCP will manage a structured file at `/projectManagement/Tasks/completion-path.json`
- This file provides a hierarchical, evolving list of major objectives leading to a finalized project
- A required top-level `completionObjective` string defines the true end goal (e.g. "Launch stable MVP on mainnet with full payment and storefront features")
- AI will maintain and update this list between sessions, but all changes require user approval
- File format is JSON (not JSONL) for structural clarity and efficient traversal by AI
- Last entry before completionObjective should always be a full review of TODO's

**Flow Integration Requirements:**
- **Required Flows**: Each milestone must specify `requiredFlows` array with flow completion requirements
- **Flow Validation**: Milestones cannot be completed until all required flows reach specified status
- **Progress Tracking**: Real-time completion percentage tracking for each required flow
- **Flow Dependencies**: Clear mapping between milestone deliverables and project flow steps

**Enhanced Milestone Structure:**
```json
{
  "completionObjective": "Deploy finished ChainSale app with all defined features, tested, stable, and production-ready",
  "milestones": [
    {
      "id": "M-02",
      "description": "Complete user authentication and payment processing",
      "status": "in-progress",
      "requiredFlows": [
        {
          "flowId": "user-registration-flow",
          "requiredStatus": "complete",
          "currentStatus": "in-progress", 
          "completionPercentage": 75
        },
        {
          "flowId": "payment-processing-flow",
          "requiredStatus": "complete",
          "currentStatus": "needs-analyze",
          "completionPercentage": 0
        }
      ],
      "relatedTasks": ["TASK-20250708T171400"],
      "implementationPlan": "M02-v1-authentication-payment.md"
    }
  ]
}
```

**Implementation Plan Integration:**
- **Plan References**: Each milestone references its implementation plan file
- **Phase Tracking**: Implementation plan phases align with milestone progress
- **Strategic Continuity**: Plans bridge high-level milestones to tactical execution
- **Plan Lifecycle**: Plans archived upon milestone completion, new plan created for next milestone

**Milestone Completion Validation:**
- **Flow Completion Check**: All required flows must reach specified status
- **Implementation Plan Validation**: All implementation plan phases must be complete
- **Deliverable Verification**: All milestone deliverables must be validated
- **Quality Gates**: Success metrics and quality criteria must be met

**Progress Tracking Integration:**
- **Flow Progress**: Real-time tracking of flow step completion percentages
- **Milestone Progress**: Calculated from flow completion and implementation plan phases
- **Overall Progress**: Project-wide completion percentage based on milestone progress
- **Predictive Analytics**: Estimated completion dates based on current velocity

**User Approval Requirements:**
- **Milestone Changes**: Any changes to milestone structure require user approval
- **Flow Requirements**: Changes to required flows must be approved
- **Completion Criteria**: Modifications to success criteria need user confirmation
- **Implementation Plan Updates**: Major changes to implementation approach require approval

**Benefits:**
- **Clear Progression**: Explicit mapping from high-level goals to tactical implementation
- **Validation Gates**: Prevents milestone completion without proper flow validation
- **Strategic Context**: Implementation plans provide detailed execution strategy
- **Session Continuity**: AI can resume work with full strategic and tactical context

---

**9.1 Implementation Plan System Integration**

### Strategic Implementation Planning

**Purpose**: Bridge the gap between high-level milestone objectives and detailed task execution through structured implementation planning.

**System Overview:**
- **Implementation Plans Directory**: `Implementations/active/` and `Implementations/completed/`
- **File Naming**: `M{milestone-id}-v{version}-{description}.md`
- **Lifecycle Management**: Creation → Execution → Archival → Next Milestone
- **Template Source**: `reference/templates/implementation-plan-template.md`

**Integration Points:**
- **Completion Path**: Each milestone references its implementation plan
- **Project Flow**: Implementation plans align with flow step requirements
- **Task Generation**: Plans break down into phases, phases generate tasks
- **Session Boot**: AI loads active implementation plan context

**Implementation Plan Lifecycle:**

1. **Creation Phase**:
   - Milestone selected from completion-path.json
   - AI analyzes current project state and requirements
   - Detailed implementation plan created with phases and strategy
   - User approval required before execution begins

2. **Execution Phase**:
   - Plan divided into logical phases with clear objectives
   - Each phase generates specific tasks in Tasks/active/
   - Progress tracked through phase completion and flow step progress
   - Plan can be updated if requirements change during implementation

3. **Completion Phase**:
   - All plan phases completed and milestone objectives met
   - Plan archived to Implementations/completed/
   - Next milestone analyzed and new implementation plan created
   - Lessons learned documented for future reference

**Version Control and Conflict Prevention:**
- **Version Increment**: Automatic versioning if plan already exists for milestone
- **Duplicate Prevention**: Milestone completion check before creating new plan
- **Change Management**: New version for significant scope changes
- **User Confirmation**: Always confirm before creating new version

**Benefits:**
- **Strategic Continuity**: Implementation strategy maintained across sessions
- **Reduced Context Switching**: No need to re-explain complex approaches
- **Focused Task Generation**: Tasks generated within strategic framework
- **Progress Clarity**: Clear understanding of current phase and next steps

---

**10. Line Limit Directive**
Use UserSettings/config.json to define the maximum number of lines allowed in a single code file.

The default is 900 lines.
After any code edit, the AI must:
Evaluate the file’s line count
If it exceeds the configured limit, modularize the content into smaller, logically grouped files (e.g., by function groups, routes, utilities, etc.)

Modularized files must be properly named and referenced in their original location or through an appropriate linking system (e.g., index files).

**11. Avoiding Placeholders**

NEED UPDATES TO 6.2 Anti-Placeholder Protocol directives.md

This MCP is intended for use in software and coding projects where placeholder text or truncated edits can cause confusion, break flow continuity, or damage structured files.

To minimize and ideally eliminate placeholder behavior:

Avoid partial edits: AI must never use placeholder markers like ...continued, rest of file unchanged, or truncated. All output must be complete unless the user explicitly allows otherwise.

Modularization requirement: If a file exceeds the limit post-edit, AI must modularize the file into functional groups (e.g. utility functions, route handlers, view logic) and store them in appropriately named files and folders.

Directive scope awareness: Before editing or outputting a file, AI must evaluate whether the full content can be handled within the set limit. If not, AI must restructure or summarize internally but output the full result to the user.

No speculative summarization: Summaries are allowed only when requested. AI must not assume what the user already knows or insert editorialized commentary.

Why Placeholders Get Added (When They Shouldn't)

Context Window Misjudgment: The model may wrongly assume that output size exceeds token limits, even when it's safe.

Legacy Training Behavior: AI models were trained to avoid full replacements due to constraints in older environments. This behavior has persisted.

False Efficiency Heuristic: AI may wrongly prioritize brevity or assume the user prefers cleaner deltas.

Internal Tooling Mismatch: LLM-connected tools often chunk code updates or show diffs, reinforcing this habit.

Human Training Oversight: Human raters often rewarded compact edits, inadvertently training models to truncate unless explicitly told not to.

---

**12. Theme Discovery and User Review Directive**

### Theme Auto-Discovery Process

When initializing a new project or analyzing an existing codebase, the AI must follow this structured theme discovery process:

#### 1. Initial Theme Discovery
- **Analyze File Structure**: Examine directory names, file names, and folder organization
- **Parse Import Graphs**: Analyze import/export relationships to identify functional clusters
- **Keyword Matching**: Use predefined keywords and patterns to identify thematic areas
- **Code Analysis**: Examine function names, class names, and component names for thematic patterns

#### 2. Theme Identification Categories
The AI should identify themes in these categories:
- **Functional Domains**: Core business logic areas (authentication, payment, user management)
- **Technical Layers**: Infrastructure concerns (database, api, security, testing)
- **User Interface**: UI components, pages, layouts, forms
- **External Integrations**: Third-party services, APIs, external tools
- **Data Management**: Models, schemas, validation, transformation
- **Operational**: Deployment, configuration, monitoring, logging

#### 3. Theme Presentation to User
After completing initial discovery, the AI **MUST** present the discovered themes to the user in this format:

```
## Discovered Project Themes

I've analyzed your project and identified the following themes:

**Functional Domains:**
1. **Authentication** - User login, registration, session management
2. **Payment Processing** - Transaction handling, billing, checkout flows
3. **User Management** - Profile management, preferences, account settings

**Technical Layers:**
4. **Database** - Models, schemas, migrations, queries
5. **API** - Controllers, routes, middleware, endpoints
6. **Security** - Access control, encryption, validation

**User Interface:**
7. **UI Components** - Reusable components, forms, layouts
8. **Dashboard** - Admin interface, analytics, reporting

**External Integrations:**
9. **Email Service** - Notifications, verification, communications
10. **Payment Gateway** - Stripe integration, webhook handling

Would you like to:
- Add additional themes I may have missed?
- Modify descriptions of existing themes?
- Remove themes that aren't relevant?
- Rename themes to better match your project terminology?
```

#### 4. User Review and Modification Process
- **Present Complete List**: Show all discovered themes with descriptions
- **Request User Input**: Explicitly ask for modifications, additions, or removals
- **Iterative Refinement**: Allow multiple rounds of theme adjustment
- **Confirm Final List**: Get explicit user approval before proceeding
- **Document Changes**: Log all user-requested theme modifications in projectlogic.jsonl

#### 5. User-Driven Theme Additions
Users may identify domain-specific themes that automated discovery missed. Common examples:
- **Domain-Specific**: `transactionRequests`, `transactionMonitoring`, `transactionSigning`
- **Business Logic**: `coinSelection`, `userSettings`, `affiliateManagement`
- **Workflow-Specific**: `qrCodeProcessing`, `walletConnectFlow`, `recoveryProcess`

#### 6. Theme Validation Rules
Before finalizing themes, ensure:
- **No Overlapping Domains**: Each theme has distinct responsibility
- **Balanced Granularity**: Themes are neither too broad nor too narrow
- **Clear Descriptions**: Each theme has unambiguous purpose
- **File Coverage**: All project files belong to at least one theme
- **Logical Relationships**: Related themes are properly linked

#### 7. Theme File Creation
Only after user approval:
- Create individual theme JSON files in `Themes/` directory
- Generate master `themes.json` index file
- Update `projectlogic.jsonl` with theme decisions
- Link themes to existing flows and tasks

#### 8. Mandatory User Approval
**CRITICAL**: AI must **NEVER** proceed with theme creation without explicit user approval. The theme discovery process is:
1. Discover themes automatically
2. Present to user for review
3. Incorporate user feedback
4. Confirm final theme list
5. Only then create theme files

#### 9. Ongoing Theme Management Protocol

**User-Requested Theme Changes:**
Users can request theme modifications at any time during development:
- **Add new themes**: "We need a theme for currency selection"
- **Modify existing themes**: "The payment theme should include subscription logic"
- **Remove themes**: "The testing theme isn't needed anymore"
- **Reorganize themes**: "Move wallet integration from payment to security theme"

**AI Response to User Theme Requests:**
1. **Assess project structure**: Analyze existing files and structure for the requested theme
2. **Present theme proposal**: Show proposed theme structure with files and relationships
3. **Get user approval**: Confirm theme structure before implementation
4. **Update theme files**: Create or modify theme JSON files after approval
5. **Document changes**: Log theme modifications in projectlogic.jsonl

**AI-Initiated Theme Updates:**
If AI identifies theme improvements during development:
- Present proposed changes to user with clear reasoning
- Explain why the modification would improve project organization
- Get explicit approval before updating theme files
- Document all changes with rationale

**Theme Modification Examples:**
```
User: "We need a theme for currency selection"
AI Response:
- Analyzes project for currency-related files
- Proposes new "currency-selection" theme structure
- Shows which files would belong to this theme
- Gets user approval before creating theme files

User: "Move payment validation to the security theme"
AI Response:
- Shows current payment validation files
- Proposes moving files to security theme
- Explains impact on both themes
- Updates both theme files after approval
```

This directive ensures themes evolve with the project and accurately represent the user's mental model rather than AI assumptions.

---

**12.1 Project Flow Status Tracking System**

### Enhanced Flow Management with Status Tracking

**Purpose**: Provide detailed progress tracking for project flows with step-level status management and milestone integration.

**Flow-Level Status Tracking:**
- **Overall Flow Status**: `pending`, `in-progress`, `complete`, `needs-review`, `needs-analyze`
- **Completion Percentage**: Calculated from individual step completion status
- **Integration with Milestones**: Flows referenced in milestone `requiredFlows` array
- **Progress Validation**: Milestone completion blocked until required flows complete

**Step-Level Status Tracking:**
- **Individual Step Status**: `pending`, `in-progress`, `complete`, `needs-analyze`, `blocked`
- **Step Dependencies**: Clear dependency chain ensuring logical implementation order
- **Completion Timestamps**: Date/time tracking for completed steps
- **File References**: Implementation status for each referenced file

**Enhanced Flow Structure:**
```json
{
  "flowId": "user-registration-flow",
  "name": "User Registration",
  "status": "in-progress",
  "completionPercentage": 75,
  "steps": [
    {
      "stepId": "URF-001",
      "step": 1,
      "description": "Display registration form",
      "status": "complete",
      "completedDate": "2025-07-10T14:30:00Z"
    },
    {
      "stepId": "URF-004",
      "step": 4,
      "description": "Complete profile setup",
      "status": "pending",
      "dependencies": ["URF-003"]
    }
  ]
}
```

**Milestone Integration:**
- **Required Flows**: Milestones specify required flows and target completion status
- **Progress Validation**: Real-time validation of flow completion against milestone requirements
- **Blocking Logic**: Milestones cannot be completed until required flows reach specified status
- **Progress Tracking**: Milestone progress calculated from flow completion percentages

**Implementation Plan Alignment:**
- **Flow Requirements**: Implementation plans specify which flows must be completed
- **Phase Mapping**: Implementation plan phases aligned with flow step completion
- **Progress Synchronization**: Flow progress updates reflected in implementation plan status
- **Completion Validation**: Implementation plan phases cannot complete without flow validation

**Status Transition Rules:**
- **Step Dependencies**: Steps cannot move to `in-progress` until dependencies are `complete`
- **Flow Completion**: Flow marked `complete` only when all steps are `complete`
- **Milestone Validation**: Milestone completion requires all required flows to be `complete`
- **Quality Gates**: Status transitions may require validation checkpoints

**Benefits:**
- **Clear Progress Tracking**: Step-level visibility into flow implementation status
- **Milestone Integration**: Explicit connection between flow progress and milestone completion
- **Session Continuity**: AI can quickly identify next pending flow steps
- **Quality Assurance**: Dependency validation ensures logical implementation order

---

**12.2 Templates and Examples System**

### Centralized Template Management

**Purpose**: Provide consistent, centralized template system for all organizational file creation with explicit AI usage directives.

**Template Source Location:**
- **Primary Directory**: `reference/templates/` directory in MCP server repository
- **Template Files**: All organizational file templates consolidated in single location
- **AI Usage Requirement**: MCP server must reference `reference/templates/` when generating organizational files

**Available Templates:**
- `reference/templates/completion-path.json` - Completion path structure with milestone and flow integration
- `reference/templates/flow-index.json` - Master flow index structure
- `reference/templates/authentication-flow.json` - Individual flow file structure with enhanced status tracking
- `reference/templates/task-active.json` - Active task file structure with theme and milestone integration
- `reference/templates/sidequest.json` - Sidequest file structure
- `reference/templates/implementation-plan-template.md` - Implementation plan template with phases
- `reference/templates/projectlogic.jsonl` - Project logic entry formats
- `reference/templates/noteworthy.json` - Noteworthy events logging
- `reference/templates/config.json` - User settings configuration
- `reference/templates/themes.json` - Theme definitions
- `reference/templates/todos.jsonl` - TODO tracking format

**AI Usage Directive:**
- **Mandatory Reference**: AI must use corresponding example file as template structure
- **Consistency Requirement**: All organizational files must follow example patterns
- **Integration Compliance**: Templates include all interconnection requirements
- **User Approval**: Templates provide structure, user approval required for content

**Template Integration Requirements:**
- **Flow Integration**: Templates include flow status tracking and milestone integration
- **Implementation Plan Integration**: Templates reference implementation plan system
- **Theme Integration**: Templates include theme context and dependencies
- **Status Tracking**: Templates include appropriate status fields and validation

**Benefits:**
- **Consistency**: Single source of truth for organizational file structure
- **Integration**: Templates ensure proper interconnection between system components
- **Maintenance**: Updates to templates automatically improve all future file generation
- **Quality**: Templates include validation and status tracking requirements

---

**13. Session Boot Directive** *(To be detailed)*

### Session Initialization Sequence

When a user requests "continue development" or starts a new session, the AI must follow this exact sequence:

1. 
2. Read ProjectBlueprint
3. Read ProjectFlow  
4. Read projectlogic.jsonl
5. Read completion-path.json
6. Review incomplete tasks if any
7. If no incomplete tasks, review historical notes on last completed tasks
8. If needed, review latest archived task lists
9. Determine next steps with suggested importance hierarchy for user decision
10. Once path decided, determine contextMode based on theme requirements
11. Generate task list
12. Assess current state within determined context by reviewing necessary files
13. Begin task(s)
14. 

**Note**: This directive will be fully detailed during complete directive planning phase.

---

**14. README Management Directive** *(To be detailed)*

We should have both a README.md file and a README.json file. README.md should be for generalized purpose for folder
README.json should be for AI evaluation and upkeep of the directory, listing files, exports, uses, file chains (interconnected files), theme references, and any other useful data that AI can quickly assess instead of needing to read through the various files themselves for most contextual data.

Templates for these files are available in reference/templates/:
- reference/templates/README-template.md
- reference/templates/README-template.json

The README.json filename should be configurable in UserSettings/config.json to avoid conflicts if projects already use this naming convention.

Include last updated in json.

### Directory Documentation Requirements

With every significant change to code, the README.md in the housing directory must be updated to reflect:

- Purpose of the directory and files included
- Current state assessment for AI quick reference
- Exports and code that can be called externally
- Changes that affect directory information

**Last Updated Section**: The "Last Updated" section should be overwritten each time with only the most recent changes. Do not accumulate historical changes - this avoids redundancy with existing change tracking systems (projectlogic.jsonl, noteworthy.json, task files, git history).

**Configuration**: The `lastUpdatedBehavior` setting in config.json controls this behavior:
- `"overwrite"` (default): Replace with most recent changes only - avoids duplicate tracking since we have comprehensive change tracking in projectlogic.jsonl, noteworthy.json, task files, and git history
- `"append"`: Add new changes to existing list (if historical tracking needed for specific use cases)

**Purpose**: Allow AI to assess folder state/files by reading one file instead of investigating code every time.

**Note**: This directive will be fully detailed during complete directive planning phase. README.md files must be created if not exist

---

**15. Context Loading Optimization Directive** *(To be detailed)*

### README-Guided Theme Context Loading

AI must follow this logic sequence for efficient context loading:

1. Load primary theme structure from `Themes/[theme].json`
2. Read README.md files in relevant theme directories for context
3. Assess task requirements and determine specific files needed
4. Use contextMode (theme-focused/theme-expanded/project-wide) as guidance
5. AI can escalate context when determining code analysis is necessary
6. Optimize cache usage by avoiding unnecessary code evaluation unless essential

**Purpose**: Allow AI to work efficiently by reading READMEs for directory context rather than analyzing code files immediately, while maintaining flexibility to access code when determined necessary.

**Note**: This directive will be fully detailed during complete directive planning phase.

---

**16. Completion Path Definition Process Directive** *(To be detailed)*

### completionObjective Management

Defines how completion objectives are:
- Initially defined based on user requirements
- When and how they can be changed
- User approval process for modifications
- Documentation requirements for changes
- Version control and tracking

**Note**: This directive will be fully detailed during complete directive planning phase.

---

**17. Mid-Task Context Escalation Directive**

### Context Escalation Protocol

When AI realizes mid-task that broader context is needed, it must follow this escalation sequence:

#### 1. Assess Sidequest Viability First
Before escalating context, AI must evaluate if the issue can be resolved through a sidequest:
- **Create sidequest**: If the needed work is tangential to the current task
- **Focused solution**: If the issue can be addressed without expanding theme context
- **Minimal disruption**: If a sidequest would be less disruptive than context escalation

#### 2. Context Escalation Decision Tree
If sidequest is not viable, proceed with context escalation:

**When to escalate:**
- Current theme context is insufficient for proper implementation
- Cross-theme dependencies discovered that affect current task
- Architectural changes needed that impact multiple themes
- Missing crucial context that could lead to breaking changes

**Escalation sequence:**
1. **theme-focused** → **theme-expanded** (load related themes)
2. **theme-expanded** → **project-wide** (load full project context)

#### 3. User Communication Protocol
Before escalating context, AI must:
1. **Explain the need**: Clearly describe why broader context is required
2. **Present options**: Offer sidequest alternative if viable
3. **Request permission**: Get explicit user approval for context expansion
4. **Document reasoning**: Log the escalation decision and rationale

#### 4. Implementation Guidelines
**User notification format:**
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

**Documentation requirements:**
- Log context escalation in ai-decisions.jsonl
- 
- Note escalation reason in task progress

#### 5. Escalation Constraints
- **Maximum one escalation per task**: Avoid cascading context expansion
- **User approval required**: Never escalate without explicit permission
- **Rollback capability**: Be prepared to revert if escalation doesn't resolve the issue
- **Impact assessment**: Consider how escalation affects task completion time

---

**18. Standard Testing Behavior Directive**

### Testing Approach Guidelines

AI should maintain standard testing behavior and **never** test entire themes comprehensively unless explicitly requested by the user. Theme context is purely for understanding, not for determining test scope.

#### 1. Standard Testing Scope
**What AI should test naturally:**
- Individual functions, methods, and components
- Specific features being implemented or modified
- Integration points relevant to current work
- Specific user flows being developed

**What AI should NOT test automatically:**
- **Entire themes from top to bottom** - This is excessive and outside standard procedure
- **Cross-theme comprehensive testing** - This is manual QA work, not standard development testing
- **Full theme integration testing** - Only test actual integration points being worked on

#### 2. Theme Context Usage for Testing
Themes are **organizational tools only**. Use theme context for:
- **Understanding component purpose**: What does this payment component do?
- **Locating test files**: Where should tests be placed in the project structure?
- **Understanding dependencies**: What other components does this interact with?

**Do NOT use themes for:**
- Determining comprehensive test coverage
- Creating artificial test suites for entire themes
- Forcing tests just because files are in the same theme

#### 3. User-Requested Comprehensive Testing
**If user specifically requests theme-wide testing:**
- Ask for clarification on scope and requirements
- Work out the best approach with the user
- Create a systematic plan for comprehensive coverage
- This is a special request, not standard AI behavior

#### 4. Standard Testing Practices
**Unit Testing:**
- Test the specific component/function being developed
- Use standard testing frameworks and patterns
- Follow project's existing test structure

**Integration Testing:**
- Test actual integration points (API calls, database interactions, etc.)
- Focus on the integration being implemented, not theme relationships
- Test what naturally integrates, not what's thematically related

**Flow Testing:**
- Test specific user flows from ProjectFlow files
- Test complete user journeys when implementing those flows
- Don't test flows just because they involve files in the same theme

#### 5. Testing Guidelines Summary
```
✓ Test what you're building or modifying
✓ Test actual integration points
✓ Test specific user flows being implemented
✓ Use standard testing practices for the technology stack

✗ Never automatically test entire themes
✗ Don't create comprehensive theme test suites
✗ Don't force testing based on theme relationships
✗ Don't override standard testing patterns for theme compliance
```

**Example scenarios:**
```
Scenario: Implementing a payment processing function
✓ Test the payment processing function
✓ Test integration with payment gateway
✓ Test payment flow if that's what's being built
✗ Don't test all payment theme components
✗ Don't test payment + user-management integration unless specifically building that

Scenario: User requests "test the authentication theme"
✓ Ask user to clarify scope and requirements
✓ Work out systematic approach with user approval
✓ Create comprehensive test plan as special request
✗ Don't assume what "test the theme" means
```

---

**19. Global Dependencies Access Directive**

### Global File Access Protocol

Certain files and directories are always accessible regardless of theme context, following normal AI assessment behavior.

#### 1. Always-Accessible Files
**Project Root Level:**
- Configuration files: `package.json`, `requirements.txt`, `Cargo.toml`, `composer.json`
- Environment files: `.env`, `.env.local`, `config.json`, `settings.json`
- Build/deployment files: `Dockerfile`, `docker-compose.yml`, `Makefile`, `*.config.js`
- Documentation: `README.md`, `LICENSE`, `CHANGELOG.md`
- Version control: `.gitignore`, `.gitattributes`

**Source Root Level (e.g., `src/`):**
- Entry points: `index.js`, `main.ts`, `app.js`, `App.tsx`
- Global configuration: `config/`, `constants/`, `types/`, `utils/`
- Core application files: `app.js`, `router.js`, `store.js`

#### 2. Access Protocol
**Natural AI behavior:**
- Files are available for assessment when contextually relevant
- AI determines necessity using standard evaluation methods
- No forced loading - files accessed only when needed

**Cross-theme accessibility:**
- Global files accessible from any theme context
- No theme boundaries for global dependencies
- Modification allowed when contextually appropriate

#### 3. Shared File Impact Assessment
When modifying files marked as `shared: ["theme1", "theme2"]`:

**Assessment process:**
1. **Identify affected themes**: Check the `sharedWith` array in theme files
2. **Quick impact review**: Read README.md files for each affected theme
3. **Conflict assessment**: Evaluate if changes might break other theme functionality
4. **Proceed with awareness**: Make changes while considering cross-theme implications

**Documentation requirements:**
- Log cross-theme modifications in ai-decisions.jsonl
- 
- Update affected theme README files if necessary

#### 4. Modification Guidelines
**When to modify global files:**
- Changes are contextually appropriate for the current task
- Modifications align with project-wide standards
- Updates improve overall project consistency

**Assessment criteria:**
- Will this change affect other themes negatively?
- Are there alternative approaches that minimize cross-theme impact?
- Is this the appropriate time to make this change?

**Documentation format:**
```json
{
  "timestamp": "2025-07-12T10:30:00Z",
  "type": "shared-file-modification",
  "file": "src/types/User.ts",
  "sharedWith": ["authentication", "user-management"],
  "changes": "Added optional avatar field to User interface",
  "impactAssessment": "Low impact - optional field, backward compatible",
  "themeReadmeReviewed": ["authentication", "user-management"]
}
```

---

## System Integration Summary

### Comprehensive Interconnection Overview

The AI Project Manager system has been enhanced with deep integration between all organizational components:

**Core Integration Flow:**
1. **Completion Path** → defines milestones with required flows
2. **Implementation Plans** → bridge milestones to tactical execution with phases
3. **Project Flows** → track step-level progress with status validation
4. **Tasks** → generated from implementation plan phases, reference flows and themes
5. **Session Boot** → loads complete context from implementation plans, flows, and milestones

**Key Interconnections:**

**Milestone ↔ Flow Integration:**
- Milestones specify `requiredFlows` array with completion requirements
- Flow completion percentages block milestone completion until requirements met
- Real-time validation ensures milestone progress accuracy

**Implementation Plan ↔ System Integration:**
- Plans reference milestone objectives and required flows
- Plans break down into phases that generate specific tasks
- Plans archived upon completion, new plan created for next milestone
- Session boot loads active implementation plan context

**Flow ↔ Task Integration:**
- Tasks reference specific flow steps for implementation
- Flow step completion tracked through task execution
- Step dependencies ensure logical implementation order
- Status validation prevents premature progression

**Template ↔ Integration Requirements:**
- All templates in `reference/templates/` directory include integration requirements
- Templates ensure proper interconnection between system components
- AI must use templates to maintain consistency and integration

**Session Continuity Benefits:**
- **Strategic Context**: Implementation plans provide ongoing strategy across sessions
- **Tactical Context**: Flow status shows specific next steps to implement
- **Progress Tracking**: Clear understanding of current phase and completion status
- **Quality Assurance**: Validation gates ensure proper progression through system

This integrated system transforms AI project management from reactive task execution to strategic, continuous project completion with full context preservation across sessions.

---

## Configuration Directives

### User Settings Configuration Management

**Purpose**: Define comprehensive user-configurable settings that govern AI behavior, project management, and system operation.

**Configuration File Location**: `reference/templates/config.json` provides the template structure for all user settings.

**Key Configuration Areas:**

### Task Management Configuration
```json
{
  "tasks": {
    "parallelTasksEnabled": true,
    "maxActiveTasks": 3,
    "autoArchive": true,
    "archiveAfterDays": 30,
    "maxArchiveFiles": 100,
    "resumeTasksOnStart": false,
    "statusMarkers": [
      "pending", "in-progress", "blocked", 
      "reviewing", "completed", "cancelled"
    ]
  }
}
```

### Session Boot Configuration: resumeTasksOnStart

**Setting**: `tasks.resumeTasksOnStart` (default: false)

**Purpose**: Controls AI behavior when active/incomplete tasks are found during session boot.

**Behavior Logic**:
- **If `resumeTasksOnStart = true`**: AI automatically resumes active/incomplete tasks
- **If `resumeTasksOnStart = false`**: AI lists incomplete tasks and asks user permission to resume

**Session Boot Task Logic**:
1. **Check for Active/Incomplete Tasks**: Scan `Tasks/active/` directory for pending tasks
2. **Apply Configuration Setting**: Use `resumeTasksOnStart` to determine behavior
3. **Resume Tasks**: If enabled, automatically resume with context loading
4. **User Prompt**: If disabled, list tasks and ask "Would you like to resume these tasks?"
5. **No Active Tasks**: If no active tasks, read last completed tasks and compare to completion-path.json

**User Notification Format** (when `resumeTasksOnStart = false`):
```
I found the following incomplete tasks:
- TASK-20250713T143000: Implement user authentication flow (status: in-progress)
- TASK-20250713T151500: Add payment validation (status: pending)

Would you like to resume these tasks or start with a new objective?
```

### Backwards Compatibility Configuration
```json
{
  "project": {
    "backwardsCompatibility": false,
    "productionMode": false
  }
}
```

**Setting**: `project.backwardsCompatibility` (default: false)

**Purpose**: Determines whether AI maintains backwards compatibility when making changes.

**Behavior**:
- **If `backwardsCompatibility = true`**: AI preserves existing interfaces and creates migration paths
- **If `backwardsCompatibility = false`**: AI can make breaking changes directly, overwriting/removing outdated code
- **Production Mode Impact**: If `productionMode = true`, overrides backwards compatibility to `true`

### Context Loading Configuration
```json
{
  "contextLoading": {
    "defaultMode": "theme-focused",
    "escalationEnabled": true,
    "readmeFirst": true
  }
}
```

**Settings**:
- `defaultMode`: Default context loading mode (theme-focused/theme-expanded/project-wide)
- `escalationEnabled`: Allow mid-task context escalation
- `readmeFirst`: Prioritize README files for directory context

### Validation Configuration
```json
{
  "validation": {
    "enforceTaskMilestoneReference": true,
    "enforceTaskThemeReference": true,
    "enforceSubtaskFlowReference": true,
    "requireApprovalForStructureChanges": true
  }
}
```

**Purpose**: Enforce integration requirements and validation rules.

**Benefits**:
- **Consistent Behavior**: User-defined settings ensure consistent AI behavior across sessions
- **Project Customization**: Settings can be tailored to specific project needs
- **Team Preferences**: Configuration supports team-wide standards and preferences
- **Integration Control**: Settings control how system components interact

### Implementation Requirements
- **MCP Server**: Must load configuration from `UserSettings/config.json`
- **Default Values**: Use example config as fallback for missing settings
- **Validation**: Validate configuration values against acceptable ranges
- **User Override**: Allow runtime configuration changes with user approval

---
