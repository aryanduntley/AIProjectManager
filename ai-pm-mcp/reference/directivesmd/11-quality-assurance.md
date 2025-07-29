# Quality Assurance Directives

## 11.1 Testing Protocol

**Directive**: Maintain standard testing practices without theme-based over-testing.

**Standard Testing Scope**:
- Test specific components/functions being developed
- Test actual integration points (APIs, databases, etc.)
- Test specific user flows being implemented
- Follow project's existing test frameworks

**Theme Context for Testing**:
- Use themes for understanding component purpose
- Use themes for locating appropriate test file placement
- Use themes for understanding dependencies
- DO NOT test entire themes comprehensively unless explicitly requested

**Prohibited Testing**:
- Automatic comprehensive theme testing
- Artificial test suites based solely on theme membership
- Cross-theme testing without specific integration work
- Testing unrelated components just because they share a theme

### Standard Testing Behavior Directive

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

## 11.2 Validation Requirements

**Directive**: Validate all project artifacts for consistency and correctness.

**Configuration Settings**:
- `validation.enforceTaskMilestoneReference` (default: true)
- `validation.enforceTaskThemeReference` (default: true)
- `validation.flowReferenceValidation` (default: "smart")
- `validation.crossFlowAwareness` (default: true)
- `validation.contextEscalationAllowed` (default: true)
- `validation.warnOnMissingReferences` (default: true)
- `validation.validateFileExistence` (default: true)
- `validation.requireApprovalForStructureChanges` (default: true)
- `validation.validateJsonSchemas` (default: true)

**Theme Validation**:
- All referenced files and paths exist
- Linked themes are valid
- No circular dependencies
- Shared files properly documented
- Theme coverage is complete

**Task Validation**:
- When `validation.enforceTaskMilestoneReference` is true: All tasks must reference valid milestones
- When `validation.enforceTaskThemeReference` is true: All tasks must specify primary and related themes
- **Smart Flow Reference Validation**: Validate flow references exist but allow cross-flow and context escalation
- **Cross-Flow Awareness**: Sidequests can reference any flows needed to address discovered issues during development
- **Context Escalation Allowed**: AI can load related flows within theme scope without user approval
- Dependencies are properly defined
- Completion criteria are clear

**Smart Validation Approach**:
- **Purpose**: Prevent artificial restrictions that could cause AI to break connected functionality
- **Smart Mode** (default): Validate flow references exist, warn on missing, allow cross-flow and context escalation
- **Strict Mode**: Enforce exact flow references as specified in task files
- **Disabled Mode**: No flow reference validation (not recommended)

**Preventing Broken Code**: 
- AI can see full context to avoid breaking connected functionality
- Flow scope is performance optimization, not artificial limitation
- Theme scope provides safety boundary for complete understanding
- Context escalation ensures holistic solutions over isolated fixes

**File Validation**:
- When `validation.validateFileExistence` is true: All referenced files must exist or be marked as pending
- Line limits respected
- No placeholder content
- Proper modularization
- All imports/exports functional
- README files current

**JSON Schema Validation**:
- When `validation.validateJsonSchemas` is true: All JSON files must conform to their schemas
- Validate task files, theme files, projectManagement/Tasks/completion-path.json, etc.

**Structure Change Validation**:
- When `validation.requireApprovalForStructureChanges` is true: All modifications to project structure, themes, or completion path require explicit user approval

## 11.3 Code Quality Standards

**Directive**: Maintain high code quality without introducing placeholders.

**Quality Requirements**:
- Complete implementations only
- Proper error handling
- Clear naming conventions
- Appropriate comments (but not placeholder comments)
- Consistent formatting
- Modular architecture

**Quality Checks**:
- No TODO comments without associated tasks
- No placeholder functions
- No dead code
- No unused imports
- Proper type definitions where applicable

## 11.4 Data Integrity Protocol

**Directive**: Ensure data integrity across all project management artifacts.

**Integrity Checks**:
- Cross-reference validation between files
- Consistency checks between themes and tasks
- File existence validation for all references
- JSON schema validation for structured files
- Backup verification for critical operations

## 11.5 Audit Trail Requirements

**Directive**: Maintain complete audit trails for all significant operations.

**Audit Trail Components**:
- All AI decisions with reasoning
- All user interactions and approvals
- All file modifications with context
- All theme changes with impact assessment
- All task state changes with triggers
- All context escalations with justification