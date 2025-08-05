# User Interaction Directives

## 12.1 User Approval Requirements

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

## 12.2 User Communication Protocol

**Directive**: Communicate clearly and concisely with users about system operations.

**Communication Guidelines**:
- Explain technical decisions in plain language
- Provide context for why actions are needed
- Offer multiple options when possible
- Explain impact of decisions
- Request clarification when requirements unclear
- Confirm understanding before proceeding

## 12.3 Preference Learning and Adaptation

**Directive**: Learn from user preferences and adapt behavior accordingly.

**Adaptation Areas**:
- Preferred context modes for different task types
- Theme organization preferences
- Documentation detail levels
- Testing scope preferences
- Communication style preferences

**Preference Storage**:
- Document preferences in .ai-pm-config.json
- Include preference reasoning in projectlogic.jsonl
- Respect established patterns unless user requests changes
- Ask for clarification when preferences conflict

## 12.4 Configuration Management

**Directive**: Respect user configuration settings and provide clear explanations of behavior.

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
5. **No Active Tasks**: If no active tasks, read last completed tasks and compare to projectManagement/Tasks/completion-path.json

**User Notification Format** (when `resumeTasksOnStart = false`):
```
I found the following incomplete tasks:
- TASK-20250713T143000: Implement user authentication flow (status: in-progress)
- TASK-20250713T151500: Add payment validation (status: pending)

Would you like to resume these tasks or start with a new objective?
```

### Backwards Compatibility Configuration

**Setting**: `project.backwardsCompatibility` (default: false)

**Purpose**: Determines whether AI maintains backwards compatibility when making changes.

**Behavior**:
- **If `backwardsCompatibility = true`**: AI preserves existing interfaces and creates migration paths
- **If `backwardsCompatibility = false`**: AI can make breaking changes directly, overwriting/removing outdated code
- **Production Mode Impact**: If `productionMode = true`, overrides backwards compatibility to `true`

### Context Loading Configuration

**Settings**:
- `defaultMode`: Default context loading mode (theme-focused/theme-expanded/project-wide)
- `escalationEnabled`: Allow mid-task context escalation
- `readmeFirst`: Prioritize README files for directory context

### Validation Configuration

**Purpose**: Enforce integration requirements and validation rules.

**Settings**:
- `enforceTaskMilestoneReference`: Require all tasks to reference milestones
- `enforceTaskThemeReference`: Require all tasks to reference themes
- `enforceSubtaskFlowReference`: Require all subtasks to reference flow steps
- `requireApprovalForStructureChanges`: Require user approval for structural changes

## 12.5 Error Handling and User Communication

**Directive**: Handle errors gracefully with clear user communication.

**Error Communication**:
- Explain what went wrong in plain language
- Provide specific steps to resolve the issue
- Offer multiple resolution options when possible
- Document the error and resolution for future reference

**User Input Validation**:
- Validate user inputs before processing
- Provide clear error messages for invalid inputs
- Suggest corrections when validation fails
- Confirm understanding before proceeding

## 12.6 Feedback and Adaptation

**Directive**: Continuously improve based on user feedback and interaction patterns.

**Feedback Collection**:
- Monitor user corrections and preferences
- Track frequently changed decisions
- Note user frustrations or confusion points
- Document successful interaction patterns

**Adaptation Implementation**:
- Adjust default behaviors based on user patterns
- Update configuration recommendations
- Improve communication clarity
- Refine approval processes based on user feedback

**Documentation Requirements**:
- Log significant user feedback in projectlogic.jsonl
- Update configuration files with learned preferences
- Document behavior changes and their rationale
- Maintain history of user interaction improvements