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

## 7.8 High-Priority Implementation Plan Creation

**Directive**: Create dedicated implementation plans for high-priority issues that exceed normal task scope, providing strategic implementation framework for complex scope-escalated issues.

### Purpose and Triggers

**System Purpose**: Provide strategic implementation framework for complex scope-escalated issues that require coordinated system changes and architectural planning.

**When to Create High-Priority Plans**:
- Issue requires architectural changes across multiple systems
- Security vulnerabilities needing systematic resolution approach
- Performance optimization requiring coordinated system changes
- Technical debt remediation affecting multiple components
- Integration challenges requiring comprehensive planning

### High-Priority Plan Structure

**Naming Convention**: `H-<timestamp>-<description>.md`

**File Location**: `Implementations/active/` (same directory as regular implementation plans)

**Template Source**: Uses existing `implementation-plan-template.md` with priority markers and enhanced sections

### Enhanced Plan Template for High-Priority Issues

```markdown
# [HIGH PRIORITY] Implementation Plan: H-{timestamp} - {Issue Title}

## Metadata
- **Plan Type**: High-Priority Escalation
- **Priority**: HIGH
- **Escalation Date**: {ISO timestamp}
- **Status**: active|completed|superseded
- **Created**: {date}
- **Updated**: {date}
- **Estimated Completion**: {date}
- **Original Task**: {TASK-ID that triggered escalation}
- **Urgency**: high|critical

## Escalation Analysis
- **Escalation Reason**: Why this issue required scope escalation
- **Impact Assessment**: Analysis of affected systems and coordination requirements
- **Resource Estimation**: Timeline and expertise needed for resolution
- **Risk Assessment**: Risks and mitigation strategies

## Current State Assessment
- Systems currently affected by the issue
- Scope of the problem and interconnected impacts
- Dependencies and coordination requirements
- Technical complexity analysis

## Strategic Resolution Approach
- High-level resolution strategy and rationale
- Key architectural decisions needed
- Integration points requiring coordination
- Testing and validation strategy for high-priority changes
- Performance and security considerations

## Implementation Phases
### Phase 1: {Critical Phase Name}
- **Objectives**: What this phase accomplishes for issue resolution
- **Priority Tasks**: HIGH-TASK subtasks for this phase
- **Coordination Requirements**: Cross-system coordination needed
- **Success Criteria**: How to validate phase completion
- **Risk Mitigation**: Phase-specific risk management

### Phase 2: {Implementation Phase Name}
[Similar structure with high-priority focus]

## Success Criteria
- Complete issue resolution markers
- System stability validation requirements
- Security and performance validation
- Integration testing completion
- User acceptance for resolution

## Coordination Requirements
- Teams/systems requiring coordination
- Communication protocols during implementation
- Dependencies on external factors
- Timeline coordination with regular project work

## Notes
- Implementation decisions and escalation rationale
- User feedback and scope modifications
- Lessons learned for future high-priority issues
```

### Integration with HIGH-TASK Files

**Relationship Structure**:
- HIGH-TASK files reference H- implementation plans in their metadata
- Implementation plan provides strategic framework for HIGH-TASK execution
- Plan phases align with HIGH-TASK subtask completion
- Progress tracking coordinated between plans and tasks

**Coordination Protocol**:
- H- plans created when HIGH-TASK requires strategic coordination
- Plan phases break down into HIGH-TASK subtasks
- Implementation plan progress tracked through HIGH-TASK completion
- Plan completion marks resolution of scope-escalated issue

### User Approval Requirements

**Creation Approval**: Always required for H- plan creation
- Present escalation reason and impact assessment
- Explain strategic coordination requirements
- Get approval for resource allocation and timeline

**Structural Changes Approval**: Required for major plan modifications
- Scope expansion requiring additional resources
- Timeline extensions due to complexity
- Architectural approach changes

**Scope Expansion Approval**: Required when high-priority issue grows in scope
- Additional systems affected during resolution
- New dependencies discovered during implementation
- Resource requirements exceed initial estimates

**Resource Allocation**: No approval required for tactical resource allocation within approved plan scope

### Benefits of High-Priority Plans

**Strategic Framework**: Provides comprehensive approach to complex scope-escalated issues rather than ad-hoc resolution attempts.

**Coordination Management**: Ensures proper coordination across affected systems and teams for complex multi-system issues.

**Risk Management**: Systematic identification and mitigation of risks associated with high-priority changes.

**Resource Planning**: Clear estimation of timeline, expertise, and coordination requirements for informed decision-making.

**Progress Tracking**: Structured phases enable tracking progress on complex issues that exceed normal task boundaries.

**Quality Assurance**: Ensures high-priority issues receive appropriate strategic planning rather than rushed tactical fixes.

### Integration with Regular Implementation Plans

**Parallel Execution**: H- plans can run parallel to regular milestone implementation plans when resources permit.

**Priority Coordination**: High-priority plans take precedence when resource conflicts arise with regular plans.

**Timeline Integration**: H- plan completion feeds back into regular milestone timeline planning and adjustments.

**Lessons Integration**: Learnings from high-priority implementations inform future regular implementation plan strategies.

This high-priority implementation plan system ensures that scope-escalated issues receive appropriate strategic planning and coordination while maintaining integration with the overall project implementation framework.