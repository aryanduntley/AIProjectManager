# Project Management Directives

## 8.1 Project Initialization Protocol

**Directive**: Follow this exact sequence when initializing projects:

```
1. Validate project path exists and is accessible
2. Check for existing projectManagement/ structure
3. If exists, run compatibility check (see system initialization)
4. Initialize database: Create project.db from ai-pm-mcp/database/schema.sql
5. Create complete directory structure:
   - ProjectBlueprint/
   - ProjectFlow/
   - ProjectLogic/
   - Themes/
   - Tasks/{active,sidequests,archive/{tasks,sidequests}}
   - Implementations/{active,completed}
   - Logs/{archived} (noteworthy events in database)
   - Placeholders/
   - .ai-pm-config.json (branch-protected configuration)
   - database/{backups}
6. Initialize all required files with proper templates
7. Initialize database with default session and project metadata
8. Set appropriate metadata (creation date, version, etc.)
9. Confirm successful initialization and database connectivity

## 🚨 **CRITICAL: Organizational File Synchronization Protocol**

**MANDATORY REQUIREMENT**: All organizational files (blueprint, flows, logic, themes, completion path, implementation plans) and their corresponding database records MUST be kept in perfect synchronization at all times.

**Triggers for Synchronization**:
- After every subtask completion
- After every significant step in any work unit
- Before session termination (automatic)
- After any structural changes to project organization
- After any user-approved modifications

**Files That Must Be Synchronized**:
- **ProjectBlueprint/blueprint.md** ↔ Project metadata in database
- **ProjectFlow/*.json** ↔ `flow_status` and `flow_step_status` tables
- **ProjectLogic/projectlogic.jsonl** ↔ `noteworthy_events` table
- **Tasks/active/*.json** ↔ `task_status`, `subtask_status`, `sidequest_status` tables
- **Implementations/active/*.md** ↔ Implementation progress in database
- **Themes/*.json** ↔ `theme_flows` table

**Session Restoration Guarantee**: Upon restart, AI must be able to continue exactly where previous session ended, with complete understanding of project state, current work context, and next steps.
```

## 8.2 Project Blueprint Management

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

## 8.3 Multi-Flow Project Documentation

**Directive**: ProjectFlow/ directory must contain organized flow files managed through a master flow index.

### Multi-Flow Structure Requirements

**Master Flow Index** (`flow-index.json`):
- Lists all flow files with dependencies and metadata
- Manages cross-flow dependencies for complex user journeys
- Enables selective loading of relevant flow files based on task context
- Provides project-wide flow coordination and validation

**Individual Flow Files** (`*-flow.json`):
- Domain-specific flows organized by theme
- Naming convention: `{domain}-flow.json` (e.g., authentication-flow.json, payment-flow.json)
- JSON format for machine readability and AI processing
- Cross-flow references must specify both flowId and flowFile

**Flow File Organization**:
- **Theme-Based Grouping**: Flows organized by primary themes
- **Selective Loading**: AI loads only relevant flow files based on task requirements
- **Flow File Limits**: Configurable via `contextLoading.maxFlowFiles` (default: 3)
- **Cross-Flow Dependencies**: Managed through flow-index.json

**Flow Scope vs Theme Scope Protocol**:
- **Flow Scope**: Initial context loading for resource management and performance optimization
- **Theme Scope**: Always available as the defined scope boundary for complete context
- **Automatic Expansion**: AI can expand from flow scope to theme scope without user approval
- **Resource Management**: Start with flow scope, expand to theme scope when needed
- **No Restrictions**: Flow scope is a performance optimization, not a limitation
- **Self-Implemented**: AI determines when flow scope is insufficient and expands automatically

**Structure Requirements**:
- Each flow must specify: trigger, steps, file trails, conditions, outcomes
- Files can be marked as `null`, `"pending"`, or `"not-implemented"`
- Cross-reference with theme files for implementation details
- Update flows when new features or interactions are added

### Enhanced Flow Management with Status Tracking

**Flow-Level Status Tracking:**
- Each flow has overall status: `pending`, `in-progress`, `complete`, `needs-review`
- Completion percentage calculated from step statuses
- Integration with completion path milestones for validation

**Step-Level Status Tracking:**
- Individual step status: `pending`, `in-progress`, `complete`, `needs-analyze`, `blocked`
- Step dependencies to ensure logical implementation order
- Completion dates for completed steps
- File references with implementation status

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

**Completion Path Integration:**
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

## 8.4 Project Logic Tracking

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

### Relationship to Blueprint and Multi-Flow System

`projectlogic.jsonl`, `flow-index.json`, and `blueprint.md` are the **three central project-wide intelligence files**. They serve different purposes but must always remain aligned:

- `blueprint.md` – Plain-language, high-level purpose and summary of the project. For the user.
- `flow-index.json` – Master index for user experience flows, interactions, and interface journeys across multiple flow files. User flow modeling and multi-flow coordination. **Important**: User experience paths (action, outcome, etc) distinct from themes (programmatic paths and file linkage).
- `projectlogic.jsonl` – Compact AI/user logic map, state transitions, reasoning, and direction shifts.

### Evaluation Schedule

These three files must be evaluated:

- **Before and after** every task file (not per subtask)
- Especially when project **functionality** or **design logic** changes—not necessarily when simple code changes occur
- Before task execution to ensure current logic is available
- After task completion to verify if direction, themes, or design has shifted

### Format Consideration

- `blueprint.md`: Markdown, always human-readable, reviewed manually
- `flow-index.json` and individual flow files: Multi-flow JSON system organized by domain, optionally generated via AI for validation and coverage checking
- `projectlogic.jsonl`: Structured JSONL format for efficient parsing and updating by AI

All entries should include timestamp, category/type, and affected components. The AI should always present human-readable summaries before writing to this file.

## 8.5 Templates and Examples System

### Centralized Template Management

**Purpose**: Provide consistent, centralized template system for all organizational file creation with explicit AI usage directives.

**Template Source Location:**
- **Primary Directory**: `reference/templates/` directory in MCP server repository
- **Template Files**: All organizational file templates consolidated in single location
- **AI Usage Requirement**: MCP server must reference `reference/templates/` when generating organizational files

**Available Templates:**
- `reference/templates/completion-path.json` - Completion path structure with milestone and flow integration
- `reference/templates/flow-index.json` - Master flow index structure
- `reference/templates/authentication-flow.json` - Individual flow file structure
- `reference/templates/task-active.json` - Active task file structure with theme and milestone integration
- `reference/templates/sidequest.json` - Sidequest file structure
- `reference/templates/implementation-plan-template.md` - Implementation plan template with phases
- `reference/templates/projectlogic.jsonl` - Project logic entry formats
- `reference/templates/noteworthy.json` - Noteworthy events logging
- `reference/templates/config.json` - User settings configuration
- `reference/templates/themes.json` - Theme definitions
- `reference/templates/todos.jsonl` - TODO tracking format
- `reference/templates/README-template.md` - Standard README template for directories
- `reference/templates/README-template.json` - AI-specific directory metadata template

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