# Task Management Directives

## 6.1 Task File Structure Requirements

**Directive**: All task files integrate with themes, milestones, and multi-flow system through hybrid file-database approach.

**Database Integration**: Task status, progress, and relationships tracked in real-time via database while task definitions remain in files for user visibility and modification.

## 🚨 **CRITICAL: Real-Time State Preservation Directive**

**MANDATORY REQUIREMENT**: After EVERY subtask completion, step completion, or any work unit of any sort, ALL organizational files and database records that relate MUST be immediately updated before proceeding.

**Purpose**: Ensure seamless session restoration and prevent loss of work in case of premature session termination.

**Update Requirements**:
- **Database**: Update task/subtask status, progress percentages, completion timestamps
- **Task Files**: Update subtask status, progress, completion criteria  
- **Session Database**: Save current context snapshot
- **Implementation Plans**: Update phase progress if applicable
- **Related Themes**: Update any affected theme relationships
- **Event Logging**: Log completion event for analytics and recovery

**Session Restoration Goal**: Upon any restart, MCP/AI must be able to resume exactly where work left off with minimal review and zero lost progress.

**Implementation**: This requirement is built into every tool and must be executed atomically - if any update fails, the entire completion step fails and must be retried.

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
  "contextMode": "theme-focused|theme-expanded|project-wide", // AI determines at task creation
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

**Task File Structure** (`reference/templates/task-active.json`):
- **Core Identity**: `taskId`, `title`, `description`, `created`, `lastUpdated`, `status`
- **Milestone Integration**: References milestone from `completion-path.json`
- **Theme Integration**: Primary theme and related themes for context loading
- **Subtasks**: Array of subtasks with individual scope, flow references, and file lists
- **Multi-Flow Integration**: Each subtask references specific flows with flowId, flowFile, and step IDs
- **Context Mode**: Per-subtask context mode (theme-focused/theme-expanded/project-wide)
- **Dependencies**: Inter-subtask dependencies and blockers
- **Testing**: Unit, integration, e2e, and security testing requirements
- **Documentation**: API docs, user guides, and technical specifications

**Sidequest File Structure** (`examples/sidequest.json`):
- **Sidequest Identity**: `sidequestId`, `parentTask`, `title`, `description`
- **Scope Context**: `scopeDescription`, `reason`, `urgency`, `impactOnParentTask`
- **Inheritance**: Inherits milestone and themes from parent task
- **Subtasks**: Similar structure to main tasks but with sidequest-specific IDs
- **Completion Trigger**: Defines what constitutes completion
- **Notes**: Additional considerations and observations

**Key Integration Requirements**:
- All tasks must reference valid milestones from `projectManagement/Tasks/completion-path.json`
- All subtasks must reference specific user flows and experience steps
- Context mode determines theme loading scope
- File lists enable targeted context loading
- Dependencies ensure proper execution order
- Tasks should reference active implementation plans when applicable

## 6.2 Task Lifecycle Management

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

## 6.3 Multiple Sidequest Management Protocol

**Directive**: Support multiple simultaneous sidequests for tangential work discovered during task execution, with configurable limits to prevent overwhelming complexity.

### Multiple Sidequest Configuration

**Configuration Settings** (`.ai-pm-config.json`):
```json
{
  "tasks": {
    "sidequestManagement": {
      "allowMultipleSidequests": true,
      "maxSimultaneousSidequests": 3,
      "warnWhenApproachingLimit": true,
      "limitExceededBehavior": "prompt_user_options"
    }
  }
}
```

### Sidequest Limit Management

**When Limit is Reached:**
- AI must check active sidequest count before creating new sidequests
- If limit exceeded, AI presents user with options:
  1. **Wait**: "You have reached the maximum of [X] active sidequests. Please complete current sidequests before creating new ones."
  2. **Modify Existing**: "Would you like to modify an existing sidequest to include this new requirement?"
  3. **Replace**: "Would you like to complete and replace one of the current sidequests?"
  4. **Increase Limit**: "Would you like to temporarily increase the sidequest limit for this session?"

**Approaching Limit Warning:**
When at 80% of limit: "You currently have [X] of [Y] maximum sidequests active. Consider completing some before creating additional sidequests."

### Sidequest Workflow Mechanics

**When to Create a Sidequest:**
- User notices missing functionality during task execution (e.g., "registration isn't handled" during checkout implementation)
- AI discovers dependency gaps that need immediate resolution
- Technical debt or security issues are identified that block progress
- User requests exploration or implementation of related but non-core functionality

### Subtask Sidequest Tracking

**During Subtask Execution, AI Must:**
1. **Check for Related Sidequests**: Review `relatedSidequests` field in current subtask
2. **Update Sidequest Status**: Monitor progress of related sidequests
3. **Coordinate Dependencies**: Consider sidequest completion when planning subtask work
4. **Update Tracking**: Add new sidequests to `relatedSidequests` array when created

**Subtask Structure with Sidequest Tracking**:
```json
{
  "id": "ST-02",
  "title": "User Registration API",
  "status": "in-progress",
  "progress": 75,
  "relatedSidequests": [
    {
      "sidequestId": "SQ-20250711T140000-001",
      "title": "Add Rate Limiting to Authentication Endpoints", 
      "status": "completed|in-progress|pending",
      "impact": "minimal|moderate|significant",
      "createdDate": "2025-07-11T17:00:00Z",
      "completedDate": "2025-07-11T16:45:00Z"
    }
  ]
}
```

**Before Creating New Sidequests:**
1. **Check Current Count**: Query active sidequests for current task across all subtasks
2. **Validate Against Limit**: Compare against `maxSimultaneousSidequests` setting  
3. **Present Options if Exceeded**: Offer user choices for handling limit
4. **Update Subtask Tracking**: Add new sidequest to current subtask's `relatedSidequests` array

### Configuration Settings Details

**`allowMultipleSidequests` (boolean, default: true)**:
- `true`: Enable multiple simultaneous sidequests per task
- `false`: Restrict to single sidequest at a time (legacy behavior)

**`maxSimultaneousSidequests` (integer, default: 3)**:
- Maximum number of active sidequests allowed per task
- Range: 1-10 (higher values may cause complexity issues)
- AI enforces this limit before creating new sidequests

**`warnWhenApproachingLimit` (boolean, default: true)**:
- `true`: Warn user when reaching 80% of sidequest limit
- `false`: Only notify when limit is actually exceeded

**`limitExceededBehavior` (string, default: "prompt_user_options")**:
- `"prompt_user_options"`: Present user with multiple resolution options
- `"block_creation"`: Simply refuse to create additional sidequests
- `"auto_queue"`: Queue new sidequests until existing ones complete

**Critical Workflow Steps:**

1. **Context Preservation Phase**:
   - **REQUIRED**: Save current task state, including:
     - Current subtask ID and progress percentage
     - Loaded themes and files in context
     - Any in-progress work or temporary state
     - Exact position in implementation flow
   - Document why sidequest is needed in `reason` field
   - Assess impact on parent task (`minimal|moderate|significant`)

2. **Sidequest Activation Phase**:
   - Create sidequest file using template structure
   - **Pause parent task** - mark parent task as `blocked` with reason
   - Switch AI focus completely to sidequest
   - Load appropriate context for sidequest theme (may be different from parent)
   - Begin sidequest execution as independent work stream

3. **Sidequest Completion Phase**:
   - Complete all sidequest subtasks and acceptance criteria
   - **Update parent task if needed** - if sidequest changed needs or details of original task, update parent task file accordingly
   - Archive sidequest file to `Tasks/archive/sidequests/`
   - **Restore parent task context** - reload exact saved state
   - Resume parent task from exact pause point
   - Update parent task with any integration needed from sidequest work

### Context Switching Protocol

**Pause Main Task:**
```
AI Message: "I'm creating a sidequest to handle [requirement]. Pausing current work on [subtask] at [progress]..."
- Save current subtask state and loaded context
- Mark parent task as blocked with sidequest reference
- Set status message indicating sidequest in progress
```

**Resume Main Task:**
```
AI Message: "Sidequest '[title]' completed. Resuming [parent task] at [subtask] where we left off..."
- Restore exact subtask state and progress
- Reload previously loaded themes and files
- Continue implementation from exact pause point
```

### Sidequest File Structure

**Enhanced Template** (`reference/templates/sidequest.json`):
```json
{
  "sidequestId": "SQ-20250711T140000-001",
  "parentTask": "TASK-20250711T140000",
  "title": "Descriptive sidequest title",
  "description": "Detailed description of what needs to be accomplished",
  "scopeDescription": "Specific explanation of why this sidequest was created",
  "reason": "User discovered missing registration during checkout implementation",
  "urgency": "low|medium|high",
  "impactOnParentTask": "minimal|moderate|significant",
  
  "contextPreservation": {
    "pausedSubtaskId": "ST-02",
    "pausedProgress": 75,
    "loadedThemes": ["payment", "checkout"],
    "loadedFiles": ["CheckoutController.ts", "PaymentService.ts"],
    "pauseTimestamp": "2025-07-11T15:30:00Z",
    "notes": "Paused during payment validation implementation"
  },
  
  "status": "pending|in-progress|completed",
  "priority": "low|medium|high",
  "themes": {
    "primary": "registration",
    "related": ["authentication", "user-management"]
  },
  
  "subtasks": [
    {
      "id": "SQ-ST-01",
      "title": "Create registration form component",
      "status": "pending",
      "priority": "high"
    }
  ],
  
  "completionTrigger": {
    "type": "all-subtasks-complete",
    "additionalRequirements": [
      "Integration with parent task verified",
      "No regressions in parent task functionality"
    ]
  }
}
```

### AI Behavior Requirements

**Strict Workflow Adherence:**
- **NEVER** continue parent task work while sidequest is active
- **ALWAYS** preserve complete context when creating sidequest
- **MUST** restore exact context when resuming parent task
- **REQUIRED** to communicate workflow transitions clearly to user

**User Communication:**
```
Example Flow:
User: "Wait, I notice registration isn't handled in this checkout flow"
AI: "You're right - registration is missing. I'll create a sidequest to implement registration functionality. 

Pausing current checkout implementation at subtask 'Payment Validation' (75% complete)...
Creating sidequest: 'Implement User Registration System'
Switching context to registration theme...

Working on registration sidequest..."

[After completing registration sidequest]

AI: "Registration sidequest completed successfully. 
Resuming checkout implementation...
Restored context: Payment Validation subtask at 75% complete
Continuing with payment validation implementation..."
```

### Validation Rules

**Before Creating Sidequest:**
- Sidequest work must be genuinely independent from current subtask
- Must have clear completion criteria
- Should not create circular dependencies

**Before Resuming Parent Task:**
- All sidequest acceptance criteria must be met
- Parent task file updated if sidequest changed original task needs or requirements
- Sidequest file must be archived
- Integration points with parent task must be documented
- No breaking changes introduced that affect parent task

## 6.4 Completion Path Integration

**Directive**: All tasks must align with project completion path and milestones.

**Integration Requirements**:
- Every task must reference a milestone from projectManagement/Tasks/completion-path.json
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

## 6.5 Parallel Task Management

**Directive**: Support multiple concurrent tasks with proper coordination.

**Parallel Task Rules**:
- Only one task can be `in-progress` per session
- Tasks can be `pending` or `blocked` concurrently
- Sidequests can run parallel to main tasks
- Coordinate shared file modifications
- Prevent conflicting changes to same files
- Document dependencies and relationships

## 6.6 Multi-Flow Task Integration

**Directive**: Tasks must properly integrate with the multi-flow system for efficient context loading and validation.

### Multi-Flow Task Requirements

**Flow References Structure**:
- **Flow ID**: Unique identifier for the flow within its flow file
- **Flow File**: Specific flow file containing the referenced flow
- **Step IDs**: Specific step identifiers within the flow
- **Cross-Flow Dependencies**: References to flows in other flow files

**Task Integration Rules**:
- Each subtask must specify flowId, flowFile, and specific step IDs
- Tasks spanning multiple flows must reference all relevant flow files
- Referenced flow files must exist in ProjectFlow/ directory
- Referenced step IDs must exist within specified flow files
- All flow files must be registered in flow-index.json

### Flow Scope Context Loading for Tasks

**Initial Context Loading**:
1. **Flow Scope**: Load only flow files referenced in task for initial context
2. **Performance Optimization**: Minimize initial memory usage with targeted flow loading
3. **Automatic Expansion**: AI expands to theme scope when flow scope insufficient
4. **No Barriers**: Expansion from flow scope to theme scope requires no approval

**Context Escalation Logic**:
- **Flow Scope Insufficient**: AI determines when flow context is inadequate
- **Theme Scope Authority**: Theme scope is always available for complete context
- **Self-Managed**: AI manages context expansion without user intervention
- **Resource Efficiency**: Start minimal, expand as needed

**Multi-Flow Validation**:
- **Flow File Existence**: Validate all referenced flow files exist
- **Step ID Validation**: Ensure all step IDs exist within referenced flows
- **Cross-Flow Dependencies**: Validate dependencies declared in flow-index.json
- **Flow Index Consistency**: Ensure flow-index.json is always up-to-date

### Flow Reference Structure

```json
{
  "flowReferences": [
    {
      "flowId": "user-registration-flow",
      "flowFile": "authentication-flow.json",
      "steps": ["URF-001", "URF-002", "URF-003"]
    },
    {
      "flowId": "payment-processing-flow",
      "flowFile": "payment-flow.json", 
      "steps": ["PPF-001"]
    }
  ]
}
```

### Benefits of Multi-Flow Integration

**Efficient Context Loading**:
- **Targeted Loading**: Load only relevant flow files for specific tasks
- **Resource Management**: Optimize memory usage with selective flow loading
- **Scalable Architecture**: Handle projects with 20+ flows efficiently

**Precise Flow Tracking**:
- **Step-Level Precision**: Reference specific flow steps for implementation
- **Cross-Flow Coordination**: Manage dependencies between different flow files
- **Progress Validation**: Track completion against specific flow requirements

## 6.6 Completion Path Tracking with Flow Integration

### Enhanced Completion Path Management

**Core Structure:**
- MCP will manage a structured file at `projectManagement/Tasks/completion-path.json`
- This file provides a hierarchical, evolving list of major objectives leading to a finalized project
- A required top-level `completionObjective` string defines the true end goal (e.g. "Launch stable MVP on mainnet with full payment and storefront features")
- AI will maintain and update this list between sessions, but all changes require user approval
- File format is JSON (not JSONL) for structural clarity and efficient traversal by AI
- **TODO Review Milestone**: A dedicated milestone for reviewing and resolving all TODO items from `Placeholders/todos.jsonl` must be included before project completion

**TODO Review Requirements:**
- **Mandatory Pre-Completion**: All TODO items in `Placeholders/todos.jsonl` must be reviewed and resolved before project completion
- **User-Initiated Review**: TODO review can be initiated at any time upon user request
- **Implementation Process**: When TODO review is triggered:
  1. Create implementation plan based on TODO complexity and priority
  2. Generate task list to systematically address all TODO items
  3. Work continues until `todos.jsonl` is empty (all items handled)
- **Resolution Options**: TODO items can be:
  - Implemented as full features
  - Converted to proper implementations
  - Documented as future work (with user approval)
  - Removed if no longer relevant

**User Flow Integration Requirements:**
- **Required Flows**: Each milestone must specify `requiredFlows` array with user flow completion requirements
- **Flow Validation**: Milestones cannot be completed until all required user flows reach specified status
- **Progress Tracking**: Real-time completion percentage tracking for each required user flow
- **Flow Dependencies**: Clear mapping between milestone deliverables and user experience steps

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
      "implementationPlans": [
        {
          "id": "M02-v1-authentication-system",
          "filename": "M02-v1-authentication-system.md",
          "status": "active",
          "version": "v1",
          "createdDate": "2025-07-02T09:00:00Z",
          "description": "Authentication system implementation plan"
        }
      ]
    }
  ]
}
```

**Implementation Plan Integration:**
- **Plan References**: Each milestone references its implementation plan files
- **Phase Tracking**: Implementation plan phases align with milestone progress
- **Strategic Continuity**: Plans bridge high-level milestones to tactical execution
- **Plan Lifecycle**: Plans archived upon milestone completion, new plan created for next milestone

**Milestone Completion Validation:**
- **Flow Completion Check**: All required user flows must reach specified status
- **Implementation Plan Validation**: All implementation plan phases must be complete
- **Deliverable Verification**: All milestone deliverables must be validated
- **Quality Gates**: Success metrics and quality criteria must be met

**Progress Tracking Integration:**
- **Flow Progress**: Real-time tracking of user flow step completion percentages
- **Milestone Progress**: Calculated from flow completion and implementation plan phases
- **Overall Progress**: Project-wide completion percentage based on milestone progress
- **Predictive Analytics**: Estimated completion dates based on current velocity

**User Approval Requirements:**
- **Milestone Changes**: Any changes to milestone structure require user approval
- **Flow Requirements**: Changes to required user flows must be approved
- **Completion Criteria**: Modifications to success criteria need user confirmation
- **Implementation Plan Updates**: Major changes to implementation approach require approval

**Benefits:**
- **Clear Progression**: Explicit mapping from high-level goals to tactical implementation
- **Validation Gates**: Prevents milestone completion without proper user flow validation
- **Strategic Context**: Implementation plans provide detailed execution strategy
- **Session Continuity**: AI can resume work with full strategic and tactical context

## 6.7 Project Flow Status Tracking System

**Directive**: Provide detailed progress tracking for user flows with step-level status management and milestone integration.

### Flow-Level Status Tracking
- **Overall Flow Status**: `pending`, `in-progress`, `complete`, `needs-review`, `needs-analyze`
- **Completion Percentage**: Calculated from individual step completion status
- **Integration with Milestones**: Flows referenced in milestone `requiredFlows` array
- **Progress Validation**: Milestone completion blocked until required flows complete

### Step-Level Status Tracking
- **Individual Step Status**: `pending`, `in-progress`, `complete`, `needs-analyze`, `blocked`
- **Step Dependencies**: Ensure logical user experience progression
- **Completion Dates**: Track when user experience steps are implemented
- **User Experience Validation**: Verify step implementation meets user experience requirements

### Status Management Protocol
- **Status Transitions**: Steps must progress through valid status transitions
- **Dependency Validation**: Blocked steps cannot complete until dependencies resolve
- **User Experience Testing**: Steps marked complete must have user experience validation
- **Progress Reporting**: Real-time completion percentage updates for flows and milestones

### Integration with Milestones
- **Required Flows**: Milestones specify which user flows must be complete
- **Validation Gates**: Milestone completion blocked until all required flows reach specified status
- **Progress Tracking**: Real-time completion tracking for milestone flow requirements
- **User Experience Validation**: Ensure user flows provide complete user experience before milestone completion

## 6.8 TODO Tracking Logic

**Directive**: Systematically track and manage TODO items and placeholders.

**Purpose**: The `/Placeholders/todos.jsonl` file collects all placeholder tasks, `TODO:` notes, and deferred scaffolding from AI-generated code

**Entry Requirements**:
- Each entry contains:
  - Timestamp
  - File and line reference
  - Reason for deferral or notes
  
**Capabilities**:
- This log enables MCP to:
  - Aggregate incomplete logic across the project
  - Propose task creation for unhandled `TODO` items
  - Review code quality and scaffolding completeness
  
**Integration**: These entries are optional and can be cross-referenced with `Tasks/` if any are formalized into proper subtasks

## 6.8 Completion Path Definition Process

### completionObjective Management

**Directive**: Define how completion objectives are initially defined and managed.

**Requirements**:
- Initially defined based on user requirements
- When and how they can be changed
- User approval process for modifications
- Documentation requirements for changes
- Version control and tracking

**Process**:
1. **Initial Definition**: Based on business requirements and user stories gathered during discovery phase
2. **Change Process**: Only with explicit user approval after reviewing impact on timeline and resources
3. **Change Steps**: 1. Propose change with rationale, 2. Review with stakeholders, 3. Update timeline/resources, 4. Document decision
4. **Version Control**: All changes tracked in projectlogic.jsonl with timestamp and reasoning