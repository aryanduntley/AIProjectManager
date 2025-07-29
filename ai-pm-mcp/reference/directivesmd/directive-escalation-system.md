# Directive Escalation System

## Overview

The directive escalation system enables AI to access progressively more detailed directive information when facing ambiguity or complex scenarios. This three-tier system balances efficiency with comprehensive coverage, ensuring AI can handle both routine operations and complex edge cases effectively.

**Core Philosophy**: Start with compressed directives for routine operations, escalate to detailed directive specifications when needed for complex operations, and preserve findings to avoid redundant file access.

## When This System Applies

### Primary Purpose
Enable AI to resolve directive ambiguity and handle complex workflows without over-loading context or under-serving user needs.

### Critical For
- **Complex workflow execution** - First-time sidequests, branch management, Git operations
- **User communication protocols** - When specific messaging templates and procedures needed  
- **Edge case handling** - Unusual situations not covered by basic workflows
- **Configuration limit management** - When configurable limits reached and user options needed

## Three-Tier Escalation System

### Forced Escalation Operations
**Always Skip Compressed, Start with JSON**:
- **Git operations**: 01-system-initialization, 15-git-integration  
- **Session management**: 03-session-management (session start/end)
- **Branch operations**: 14-branch-management
- **Database operations**: database-integration
- **Logging/Documentation**: 09-logging-documentation
- **Theme discovery/changes**: 04-theme-management
- **Project structure changes**: 08-project-management

**Rationale**: These operations involve complex system coordination, state management, and multi-component interaction that requires detailed implementation specifications from the start.

### Tier 1: Compressed Directives
**File**: `ai-pm-mcp/core-context/directive-compressed.json`
**Purpose**: Basic workflow understanding and quick reference
**Coverage**: ~60% of directive information

**Always Start Here**:
- Initial directive understanding for all workflows
- Quick reference for routine operations
- Basic workflow steps and decision trees
- Configuration settings and validation rules

**Limitations**:
- No user communication protocols or message templates
- No detailed behavioral examples or edge case handling  
- No comprehensive error recovery procedures
- Limited context for complex workflow transitions

**Usage Pattern**: Every directive consultation begins at this level

### Tier 2: JSON Directives  
**Files**: `reference/directives/{directive-id}.json`
**Purpose**: Detailed implementation specifications and structured workflows
**Coverage**: ~85% of directive information

**Escalate When**:
- Implementation details needed beyond basic workflow
- Configuration validation required with specific rules
- Workflow step clarification needed for complex scenarios
- Integration requirements unclear between system components
- Validation rules ambiguous in compressed format

**Advantages**:
- Detailed step-by-step workflow procedures
- Complete configuration specifications and validation rules
- Integration requirements and system interfaces
- Structured error handling and recovery options

**Limitations**:
- Limited user communication examples and templates
- Reduced behavioral context and rationale
- Fewer edge case scenarios and recovery procedures

**Auto-Escalation**: AI automatically escalates to this level when compressed context insufficient

### Tier 3: Markdown Directives
**Files**: `reference/directivesmd/{directive-id}.md`  
**Purpose**: Comprehensive context with examples, edge cases, and communication protocols
**Coverage**: 100% of directive information

**Auto-Escalate When**:
- Any ambiguity encountered at JSON level
- First-time complex workflow execution (sidequests, context switching)
- User communication protocols needed for approvals or transitions
- Configuration limit handling with user option presentations
- Complex validation scenarios with edge cases
- Error recovery procedures needed for system failures
- Workflow transition messaging required for user clarity

**Complete Coverage**:
- Detailed user communication protocols and message templates
- Comprehensive examples and behavioral templates
- Edge case handling and recovery procedures  
- Implementation rationale and behavioral context
- Troubleshooting guides and failure recovery

**No User Approval Required**: AI can access any directive level automatically based on need

## Escalation Scenarios and Triggers

### First Sidequest Creation
**Trigger**: User requests sidequest or AI detects sidequest need
**Escalation Path**: compressed → 06-task-management.json → 06-task-management.md
**User Approval**: Required for MD escalation

**Why Escalation Needed**:
- Need specific messaging templates for sidequest creation communication
- Context preservation procedures for parent task state
- Limit exceeded handling options and user choice presentations  
- Workflow transition communication protocols

**Critical Missing Context from Compressed**:
```
User: "I noticed we need OAuth integration while working on login"
AI: [Without MD context] "I can create a sidequest for OAuth"
User: "What are my options if I'm at the limit?"
AI: [Needs escalation for proper option presentation]
```

### Configuration Limit Exceeded
**Trigger**: Any configurable limit reached (sidequests, file lines, themes, etc.)
**Escalation Path**: compressed → {directive}.json → {directive}.md  
**User Approval**: Required for MD escalation

**Limit Types**:
- Maximum simultaneous sidequests per task
- File line count limits requiring modularization
- Theme count or complexity thresholds
- Session context memory limits

**User Communication Needed**:
```
Sidequest limit reached (3/3 active sidequests)
Options:
1. Wait for current sidequest completion
2. Modify existing sidequest scope
3. Replace current sidequest with new one
4. Increase limit (requires approval)
Which approach would you prefer?
```

### User Communication Required
**Trigger**: Complex user interaction needed (approvals, transitions, errors)
**Escalation Path**: compressed → {directive}.json → {directive}.md
**User Approval**: Required for MD escalation

**Communication Scenarios**:
- **Approval Requests**: Project blueprint changes, theme modifications
- **Transition Messages**: Task switching, context escalation, workflow changes
- **Error Communication**: System failures, recovery options, alternative approaches
- **Status Updates**: Progress reports, completion confirmations, next steps

### Workflow Ambiguity
**Trigger**: Uncertain workflow step or validation requirement
**Escalation Path**: compressed → {directive}.json
**User Approval**: Not required for JSON escalation

**Ambiguity Types**:
- Step-by-step procedure details unclear in compressed format
- Validation rule specifics needed for implementation
- Error condition handling not sufficiently detailed
- Integration requirements between system components ambiguous

### Edge Case Handling
**Trigger**: Unusual situation not covered by basic workflows
**Escalation Path**: compressed → {directive}.json → {directive}.md
**User Approval**: Required for MD escalation

**Edge Case Examples**:
- Database corruption during instance merge
- Git repository conflicts during organizational reconciliation
- Theme discovery conflicts in complex project structures
- Session restoration failures with partial context

## Escalation Protocols

### Context Preservation
**Requirement**: Maintain findings from each escalation level to avoid re-reading same files

**Implementation**:
```
Escalation Session:
1. Read directive-compressed.json [cached]
2. Identify need for JSON escalation
3. Read 06-task-management.json [add to cache]
4. Identify need for MD escalation  
5. Request user approval for comprehensive analysis
6. Read 06-task-management.md [add to cache]
7. Use combined context from all three levels
```

**Cache Management**:
- Cache directive content from each tier accessed during workflow
- Build comprehensive understanding progressively
- Avoid redundant file access within same workflow session
- Clear cache on session end or major context mode change

### User Approval Process

**Approval Message Template**:
```
I need to access more detailed directive documentation to handle this complex scenario properly. 

Scenario: [Specific situation requiring escalation]
Directive: [directive-name]
Reason: [Why additional context is needed]

This will help me:
- [Specific benefit 1]
- [Specific benefit 2]  
- [Specific benefit 3]

May I read the comprehensive markdown documentation to provide you with the best guidance?

Alternatives: [Offer simpler alternatives if user declines]
```

**Reasoning Required**: Always explain specifically why additional context is needed

**Graceful Degradation**: If user declines escalation, proceed with available context and document limitations

**Alternative Offerings**: Provide simpler workflow alternatives when comprehensive context denied

### Escalation Logging
**Requirement**: Log all directive escalations for analytics and system learning

**Log Elements**:
- **Trigger scenario** - What situation caused the escalation need
- **Escalation path taken** - Which tiers accessed and in what order
- **User approval status** - Whether user approved MD access when required
- **Context found at each tier** - What information was discovered
- **Successful resolution** - Whether escalation resolved the ambiguity
- **User satisfaction** - Whether outcome met user expectations

**Analytics Purpose**: Improve escalation triggers and optimize directive content distribution across tiers

## Directive Mapping and Complexity

### High Complexity Directives
These directives frequently require escalation due to complex workflows:
- **06-task-management** - Sidequest creation, context switching, limit management
- **03-session-management** - Session boot, context restoration, database integration
- **05-context-loading** - Context escalation, memory optimization, mode selection
- **04-theme-management** - Auto-discovery, conflict resolution, validation
- **12-user-interaction** - Communication protocols, approval processes

### User Communication Critical Directives  
These directives frequently need MD escalation for user interaction:
- **06-task-management** - Sidequest messaging, limit exceeded options
- **12-user-interaction** - All approval and communication scenarios
- **02-project-initialization** - Blueprint creation, user discussion protocols
- **04-theme-management** - Theme approval, conflict resolution communication

### All Directive Availability
| Directive ID | Compressed | JSON | MD |
|--------------|------------|------|----| 
| 01-system-initialization | ✅ | ✅ | ✅ |
| 02-project-initialization | ✅ | ✅ | ✅ |
| 03-session-management | ✅ | ✅ | ✅ |
| 04-theme-management | ✅ | ✅ | ✅ |
| 05-context-loading | ✅ | ✅ | ✅ |
| 06-task-management | ✅ | ✅ | ✅ |
| 07-implementation-plans | ✅ | ✅ | ✅ |
| 08-project-management | ✅ | ✅ | ✅ |
| 09-logging-documentation | ✅ | ✅ | ✅ |
| 10-file-operations | ✅ | ✅ | ✅ |
| 11-quality-assurance | ✅ | ✅ | ✅ |
| 12-user-interaction | ✅ | ✅ | ✅ |
| 13-metadata-management | ✅ | ✅ | ✅ |
| 14-branch-management | ✅ | ✅ | ✅ |
| 15-git-integration | ✅ | ✅ | ✅ |
| database-integration | ✅ | ✅ | ❌ |
| context-escalation-system | ✅ | ✅ | ✅ |

## Performance Optimization

### Escalation Caching
**Requirement**: Cache accessed directive content within session to avoid re-reading
**Implementation**: 
- Maintain directive content cache during workflow execution
- Clear cache on session end or major context mode change
- Track cache hit rates for performance analysis

### Intelligent Escalation  
**Requirement**: Learn which scenarios typically require which escalation levels
**Implementation**:
- Track escalation success patterns to optimize future escalations
- Adjust escalation triggers based on effectiveness patterns
- Reduce unnecessary escalations through pattern learning

## Quality Assurance

### Escalation Validation
**Requirement**: Validate that escalation resolved the ambiguity

**Validation Checkpoints**:
- **Was sufficient context found?** - Did escalation provide needed information
- **Was user interaction successful?** - Did communication achieve objectives  
- **Was workflow completed correctly?** - Did escalation enable proper execution
- **Did escalation improve outcome?** - Was result better than compressed-only approach

### Fallback Procedures

**Insufficient Context**: If all escalation levels insufficient, request user clarification with specific questions

**Access Denied**: If user denies MD escalation, proceed with best available context and clearly document limitations

**Escalation Failure**: If escalation doesn't resolve ambiguity, revert to simpler workflow alternatives when possible

## Common Escalation Examples

### Example 1: First Sidequest Creation
```
User: "I need to add OAuth while working on the login system"

AI Workflow:
1. Check compressed directives - basic sidequest process found
2. Escalate to JSON - detailed creation steps found  
3. Request MD access - "I need detailed user communication protocols for sidequest creation"
4. User approves
5. Read MD - Get complete messaging templates and limit handling
6. Present proper options to user with clear communication
```

### Example 2: Configuration Limit Exceeded
```
AI detects: File reaching 900 line limit during edit

AI Workflow:
1. Check compressed directives - basic modularization requirement found
2. Escalate to JSON - detailed modularization steps found
3. Request MD access - "I need user communication templates for limit exceeded scenarios"
4. User approves  
5. Read MD - Get complete option presentation and recovery procedures
6. Present modularization options with clear explanations
```

### Example 3: Workflow Ambiguity (No User Approval Needed)
```
AI encounters: Uncertain theme validation rules

AI Workflow:
1. Check compressed directives - basic validation mentioned
2. Escalate to JSON automatically - detailed validation rules found
3. Apply proper validation without MD escalation needed
4. Complete workflow successfully
```

This escalation system ensures AI can handle the full spectrum of scenarios from routine operations to complex edge cases while maintaining efficiency and user control over comprehensive context access.