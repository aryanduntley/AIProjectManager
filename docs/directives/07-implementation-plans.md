# Implementation Plans Directives

## 7.1 Implementation Plan System Integration

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
   - Milestone selected from projectManagement/Tasks/completion-path.json
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

## 7.2 Implementation Plan Lifecycle Management

### Creation Process
1. **Milestone Selection**: When a milestone from `projectManagement/Tasks/completion-path.json` is ready for implementation
2. **Analysis Phase**: AI analyzes current project state, requirements, and dependencies
3. **Plan Generation**: Create detailed implementation plan with phases, architecture decisions, and strategy
4. **User Approval**: Present plan to user for review and approval before execution begins

### Execution Process
1. **Phase Breakdown**: Implementation plan divided into logical phases
2. **Task Generation**: Each phase generates specific tasks in `Tasks/active/`
3. **Progress Tracking**: Track completion through phases toward milestone completion
4. **Adaptation**: Plan can be updated if requirements change during implementation

### Completion Process
1. **Milestone Validation**: Verify all plan objectives and success criteria met
2. **Plan Archival**: Move completed plan to `completed/` directory
3. **Next Milestone**: Generate implementation plan for next milestone in completion path

## 7.3 File Naming Convention

**Format**: `M{milestone-id}-v{version}-{description}.md`

**Examples**:
- `M01-v1-authentication-system.md` - Initial implementation plan for milestone M01
- `M02-v1-payment-processing.md` - Implementation plan for milestone M02
- `M01-v2-authentication-system.md` - Revised plan if milestone M01 requirements change

**Versioning Rules**:
- **v1**: Initial implementation plan for milestone
- **v2, v3, etc.**: Revised plans if milestone scope or requirements change
- **Never overwrite**: Previous versions preserved to maintain decision history

## 7.4 Archival System

### Automatic Archival Triggers
- **Milestone Completion**: When all plan phases completed and milestone marked complete
- **Plan Supersession**: When a new version of the implementation plan is created
- **Project Restructure**: When completion path milestones are reorganized

### Archival Process
1. **Completion Validation**: Verify milestone completion criteria met
2. **File Movement**: Move from `active/` to `completed/` directory
3. **Metadata Update**: Update completion date and final status
4. **Reference Preservation**: Maintain links to related tasks and decisions in projectlogic.jsonl

### Naming in Archive
- **Completed Plans**: Retain original naming (e.g., `M01-v1-authentication-system.md`)
- **Superseded Plans**: Add suffix (e.g., `M01-v1-authentication-system-superseded.md`)
- **Index Maintenance**: Update archive index with completion dates and outcomes

## 7.5 Integration with Session Boot Directive

The implementation plans system transforms the session boot process:

**Enhanced Session Boot Sequence**:
1. Read ProjectBlueprint, ProjectFlow, projectlogic.jsonl
2. Read projectManagement/Tasks/completion-path.json for milestone status
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

## 7.6 Template Structure

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

## 7.7 Version Control and Conflict Prevention

### Duplicate Prevention
- **Milestone Completion Check**: Verify milestone not already completed before creating new plan
- **Version Increment**: Automatically increment version if plan already exists for milestone
- **User Confirmation**: Always confirm with user before creating new version

### Change Management
- **Scope Changes**: New version created if milestone requirements change significantly
- **Minor Updates**: In-place updates for clarifications and small adjustments
- **Approval Process**: All plan modifications require user approval
- **Change Documentation**: All changes logged in projectlogic.jsonl

This implementation plans system provides the strategic planning layer that bridges high-level project goals with detailed task execution, ensuring consistent progress toward project completion.