# Session Management Directives

## 3.1 Session Boot Protocol

**Directive**: Follow exact sequence when starting new sessions or "continue development".

### Enhanced Session Boot Sequence with Implementation Plan Integration

**Core Requirements:**
- Defines the steps AI must follow at the beginning of each session
- Requires loading of `projectManagement/ProjectBlueprint/blueprint.md`, `projectManagement/ProjectFlow/flow-index.json`, `projectManagement/ProjectLogic/projectlogic.jsonl`, `projectManagement/Tasks/completion-path.json`, `projectManagement/Logs/noteworthy.json`, `projectManagement/Implementations/active/{activeImplementationPlan.md}` if exists, `projectManagement/Tasks/active/{activeTask}.json` if exists
- **NEW**: Check for active implementation plan in `Implementations/active/`
- **NEW**: Load current implementation plan context and phase progress
- Ensures proposed updates are confirmed by user before changing anything

**Boot Sequence:**
```
1. Read ProjectBlueprint for project understanding
2. Read ProjectFlow (flow-index.json) for interaction understanding
3. Read projectlogic.jsonl for reasoning history
4. Read projectManagement/Tasks/completion-path.json for current objectives
5. Review active tasks (Tasks/active/*.json)
6. If no active tasks, review last completed tasks
7. If needed, review archived task lists
8. Determine next steps with priority suggestions
9. Get user approval for direction
10. Determine context mode based on selected work
11. Generate task list for approved direction
12. Load theme context for selected tasks
13. Begin task execution
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