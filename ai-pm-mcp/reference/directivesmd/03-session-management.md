# Session Management Directives

## 3.1 Session Boot Protocol

**Directive**: Follow exact sequence when starting new sessions or "continue development".

**Prerequisites**: This assumes automatic state detection (from 01-system-initialization) has already notified the user and they have chosen to proceed with session boot.

### Enhanced Session Boot Sequence with Implementation Plan Integration

**Core Requirements:**
- Defines the steps AI must follow at the beginning of each session with database-enhanced boot sequence
- **Database Integration**: Session context preserved in `project.db` for instant restoration
- **Context Snapshots**: Previous session state automatically restored from database
- File loading optimized: Core files (`blueprint.md`, `flow-index.json`, `projectlogic.jsonl`) + database context
- **Session Persistence**: Active themes, tasks, sidequests, and context mode restored from database
- **Implementation Plan Integration**: Current implementation plan status loaded from database
- Ensures proposed updates are confirmed by user before changing anything

## 🚨 **CRITICAL: State Preservation Protocol**

**MANDATORY FOR SESSION CONTINUITY**: The database-enhanced boot sequence is designed to restore AI to the exact state where previous work ended. This requires STRICT adherence to real-time state updates:

**Every Work Unit Completion Triggers**:
1. **Immediate Database Update**: Task/subtask status, progress, completion timestamps
2. **File Synchronization**: Update corresponding task files with current state  
3. **Context Snapshot**: Save current AI context to session database
4. **Event Logging**: Record completion for analytics and session restoration
5. **Atomic Operation**: All updates must succeed or entire completion fails

**Session Boot Restoration Guarantee**: AI must be able to resume from ANY point where work was interrupted, with complete context restoration and zero work loss.

**Implementation Requirement**: Every MCP tool that modifies project state must implement this update protocol before considering any work unit "complete".

**Database-Enhanced Boot Sequence:**
```
1. Initialize database connection and restore session context from project.db
2. Read ProjectBlueprint for project understanding  
3. Read ProjectFlow (flow-index.json) for interaction understanding
4. Read projectlogic.jsonl for reasoning history
5. Load completion-path.json + implementation plan status from database
6. Restore active themes, tasks, sidequests from session database context
7. Load recent noteworthy events from database (instead of file scanning)
7a. Check for high-priority items (HIGH-TASK files, H- plans, database events)
7b. Surface high-priority items prominently if found, recommend immediate attention
8. Assess current state using database task/sidequest status queries
9. Determine next steps with priority suggestions based on database analytics
10. Get user approval for direction
11. Determine/restore context mode from session database
12. Generate/restore task context using database theme-flow relationships
13. Begin task execution with preserved session state
```

**Session Boot Sequence:**
1. **Core Project Files**: Load `blueprint.md`, `flow-index.json`, `projectlogic.jsonl`
2. **Strategic Context**: Read `projectManagement/Tasks/completion-path.json` for milestone status
3. **Implementation Plan Context**: Check `Implementations/active/` for current implementation plan
4. **Noteworthy Context**: Check `noteworthy.json` for latest noteworthy data
5. **User Flow Status Assessment**: Load user flow status and completion percentages
6. **Task Context**: Review `Tasks/active/{activeTask}.json` for any incomplete tasks
7. **Next Steps Determination**: Generate tasks for current implementation plan phase or identify next milestone
  - If settings in config.json resumeTasksOnStart true AND incomplete tasks, summarize incomplete task list to user and note that resumeTasksOnStart is set to true and continuing task.
  - If no incomplete tasks and autoTaskCreation is true
    - If current implementation plan and not complete
      - assess state and create next tasks, summarize tasks for user and create new task file.
     - If no current implementation plan or current implementation plan is complete
      - review all statuses, review projectManagement/Tasks/completion-path.json, assess state, summarize to user state and indicate ready for next implementation plan
        - if approved, archive complete implementation plan if not already, generate new implementation plan, generate new task file, summarize tasks, ask user to start.
        - if not, await further instructions.
  - If no incomplete tasks and autoTaskCreation is false
    - If current implementation plan and not complete
      - assess state and summarize tasks for user; await approval
     - If no current implementation plan or current implementation plan is complete
      - review all statuses, review projectManagement/Tasks/completion-path.json, assess state, summarize to user state and indicate ready for next implementation plan
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
   b. Compare last completed tasks to projectManagement/Tasks/completion-path.json
   c. Identify next milestone or implementation plan phase
   d. Check for active implementation plan in Implementations/active/
   e. If no implementation plan, analyze next milestone for plan creation
```

## 3.2 Session State Management

**Directive**: Maintain session state through persistent project files.

**State Tracking**:
- Active tasks in `Tasks/active/` directory
- Project progress in `Tasks/completion-path.json`
- Implementation plans in `Implementations/active/`
- Recent decisions in `projectlogic.jsonl`
- Noteworthy items in `Logs/noteworthy.json`

**Session Context Recovery**:
- Boot sequence loads all relevant project files
- Active tasks provide immediate context
- Project logic maintains reasoning history
- Implementation plans track current objectives

## 3.3 Session Continuity Requirements

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

## 3.4 Task Completion Updates

**Directive**: Follow systematic update process after task completion.

**Process:**
1. Review completed task or sidequest file
2. If sidequest, review and update task file if needed
3. Review projectManagement/Tasks/completion-path.json update if needed
4. Review implementation plan update if needed, archive if needed
5. Review flow-index and flow files update if needed
6. Make any noteworthy notes to noteworthy.json (if needed, do not feel obligated to add things here)

**If sidequest:**
- Archive sidequest file

**If task file:**
- Ensure no fragmented sidequests
- If fragments exist, review and complete sidequests
  - If issues arise, handle normally, involve user in decisions on how to proceed
  - Once complete review fragmented sidequest file
    - Review projectManagement/Tasks/completion-path.json update if needed
    - Review implementation plan update if needed, archive if needed
    - Review flow-index and flow files update if needed
    - Make any noteworthy notes to noteworthy.json (if needed, do not feel obligated to add things here)
    - Archive fragmented sidequest files
- Archive task file

## 3.5 User Discussion Assessments

**Directive**: Handle user discussions that may impact project organization.

**Triggers for organizational file updates:**
- Discussion about flow, logic, structure, dependencies, enhancements, refactoring, UI, coding practice, etc.
- Things that could change the project blueprint
- Things that could change the way the themes are defined or the files they may relate to
- Things that could change the logic or understanding of the project as a whole
- Things that could change the logic of a certain aspect of the project
- Decision about the workings of any part of the project

**Update Process:**
When these discussions occur and decisions are made:
1. Review blueprint update if needed
2. Review metadata update if needed
3. Review projectlogic, update if needed
4. Review themes.json update if needed
5. Review theme files in Themes, update if needed according to themes.json, theme files must always match themes.json
6. Review projectManagement/Tasks/completion-path.json update if needed
7. Review implementation plan update if needed, archive if needed
8. Review flow-index and flow files update if needed
9. Make any noteworthy notes to noteworthy.json (if needed, do not feel obligated to add things here)

**Important**: All changes to these files EXCEPT noteworthy and projectlogic, must be explicitly approved by the user. For projectlogic, since it's a historical record, make a generalized summary of changes made to projectlogic based on recent discussion.

## 3.6 High-Priority Boot Detection System

**Directive**: Detect and surface high-priority items during session boot to ensure immediate attention for scope-escalated issues.

### Purpose and Integration

**System Purpose**: Automatically surface scope-escalated issues that require user attention during work period initialization, ensuring high-priority items don't get overlooked and receive immediate focus.

**Integration with Boot Sequence**: High-priority detection occurs after database connection establishment but before regular task assessment, allowing early identification and user decision-making on priority workflow.

### Detection Process

**Comprehensive High-Priority Scanning**:

1. **HIGH-TASK File Detection**: Scan `Tasks/active/` directory for `HIGH-TASK-*.json` files
2. **H- Implementation Plan Detection**: Scan `Implementations/active/` directory for `H-*.md` implementation plans  
3. **Database Event Queries**: Query database for events with `exist_high_priority=true` and `requires_escalation=true`
4. **Recent Event Filtering**: Check recent noteworthy events (within 30 days) for unresolved high-priority items

### Surfacing Protocol

**When High-Priority Items Found**:

```
AI: "High-priority items detected that require attention:

🔴 HIGH-PRIORITY TASKS:
- HIGH-TASK-20250711T140000: [HIGH PRIORITY] Security Vulnerability Remediation
  Escalation: Authentication bypass affecting multiple systems
  Created: 2025-07-11, Status: pending

🔴 HIGH-PRIORITY IMPLEMENTATION PLANS:
- H-20250711T141500-security-remediation.md: Security vulnerability systematic resolution
  Impact: Blocks production deployment until resolved
  
🔴 DATABASE ESCALATION EVENTS:
- 2025-07-11 15:30: Performance bottleneck requiring cross-system optimization
  Affected systems: payment, authentication, user-management
  
RECOMMENDATION: Address high-priority items before regular work continuation.

OPTIONS:
1. Address high-priority items immediately
2. Continue with regular boot and address high-priority items after context loading  
3. Review high-priority items in detail before deciding approach

Which approach would you prefer?"
```

### User Interaction Options

**Immediate High-Priority Focus**:
- Load context specifically for high-priority items
- Begin work on HIGH-TASK or H- implementation plan execution
- Preserve regular boot context for later resumption if needed

**Regular Boot with High-Priority Awareness**:
- Complete standard boot sequence with high-priority items noted
- Surface high-priority items again after regular context loading
- Allow user to transition to high-priority work when ready

**Detailed Review First**:
- Present comprehensive details on each high-priority item
- Show impact assessments, escalation reasons, and coordination requirements
- Enable informed decision-making on approach and resource allocation

### Context Preservation and Workflow

**Early Detection Benefits**:
- High-priority items identified immediately upon session start
- User can make informed decisions about work priority before loading regular task context
- Prevents high-priority issues from being buried in regular workflow

**Context Preservation**: 
- If user chooses immediate high-priority focus, preserve regular boot context for later
- Enable seamless transition between high-priority work and regular task flow
- Maintain session state for both workflows simultaneously when needed

**Priority Workflow Integration**:
- High-priority work follows same context loading and execution patterns as regular tasks
- Database tracking maintains separation between high-priority and regular work progress
- Session restoration works for both high-priority and regular work contexts

### Performance Optimization

**Time-Limited Queries**: 
- Database queries limited to last 30 days to prevent performance issues in large projects
- File scanning checks modification times to focus on recent high-priority items
- Result limits prevent overwhelming output while ensuring comprehensive detection

**Efficient Detection**:
- Combined file system and database queries for comprehensive coverage
- Optimized query patterns to minimize boot time impact
- Cached results when appropriate to avoid repeated expensive operations

### Configuration and Control

**Configuration Setting**: `sessions.highPriorityChecks` (boolean, default: true)
- Enable/disable high-priority item detection during session boot
- Can be disabled for projects that prefer manual high-priority management
- Provides user control over boot sequence complexity

**Escalation Integration**: 
- Works seamlessly with high-priority task creation from scope escalation workflow
- Surfaces items created during previous sessions for continued attention
- Ensures high-priority items remain visible across session boundaries

### Benefits of High-Priority Boot Detection

**Immediate Visibility**: High-priority items surface immediately upon session start, ensuring they receive proper attention rather than being lost in regular workflow.

**Informed Decision-Making**: Users can make informed decisions about work priority with full context on high-priority items and their impact.

**Workflow Flexibility**: Multiple interaction options allow users to choose appropriate approach based on context and available time.

**Performance Balance**: Efficient detection ensures comprehensive coverage without significantly impacting boot time or system performance.

**Context Preservation**: System maintains both high-priority and regular work contexts, enabling smooth transitions between different types of work.

**Cross-Session Continuity**: High-priority items remain visible and actionable across multiple work sessions until resolved.