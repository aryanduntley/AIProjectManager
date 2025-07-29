# Context Loading Directives

## 5.1 Context Mode Selection Protocol

**Directive**: Always use appropriate context mode based on task complexity and theme relationships.

**Mode Definitions**:
- **theme-focused**: Primary theme only - DISCRETIONARY HIGH LIMIT. Theme scope defines maximum boundary, AI loads minimal files actually needed for task (~5-15 files, ~0.5-1MB memory)
- **theme-expanded**: Primary + linked themes. Requires user approval or context escalation (~15-25 files, ~1-2MB memory)
- **project-wide**: All themes. Always requires user approval (~23+ files, ~2+ MB memory)

**Selection Logic**:
1. Start with theme-focused for tasks within single theme
2. Escalate to theme-expanded if:
   - Task mentions cross-theme integration
   - Primary theme has >2 linked themes
   - Shared files are involved
3. Use project-wide only for:
   - Architecture changes
   - Global refactoring
   - Cross-cutting concerns

### Theme-Based Context Loading Strategy

#### Context Modes
- **theme-focused** (default): Load primary theme + directly related themes
- **theme-expanded**: Load theme group when themes are interconnected  
- **project-wide**: Full project context (rare, only for architectural changes)

#### Database-Enhanced Context Assessment
1. **Theme Structure Loading**: AI reads theme JSON files to understand project areas
2. **Database Metadata Query**: AI queries database for intelligent directory context and file relationships
3. **README.md Assessment**: AI reads README.md files in relevant directories for human-readable context
4. **File Selection**: AI determines specific code files needed based on task requirements and database insights
5. **Minimal Code Analysis**: AI avoids unnecessary code evaluation unless determined essential

#### Context Loading Process
1. Load primary theme files structure from `Themes/[theme].json`
2. **Database-Optimized Flow Loading**: AI queries database for optimal flow file selection based on theme-flow relationships
3. Query database for directory metadata and file relationships (replacing README.json approach)
4. Read README.md files in relevant directories for quick human-readable context
5. **Intelligent File Loading**: AI uses database insights to load only specific files needed for the task
6. AI can request theme-expanded if insufficient context (requires user approval)
7. User can override to project-wide if architectural changes needed (requires user approval)

#### Benefits
- **Database Intelligence**: Fast queries provide optimal file selection and relationship insights
- **Efficient Memory Usage**: Database metadata + README.md files provide context without excessive code analysis
- **Intelligent Assessment**: AI uses database analytics to determine file necessity
- **Flexible Escalation**: Natural expansion when more context needed
- **Smart Directory Context**: Database metadata provides intelligent folder-level understanding

## 5.2 Database-Enhanced Context Loading

**Directive**: Use database intelligence combined with README files for optimal context understanding.

**Configuration**: `contextLoading.readmeFirst` (default: true)

**Protocol**:
1. Load theme structure from JSON files
2. Query database for intelligent directory metadata and file relationship insights
3. When `contextLoading.readmeFirst` is true: Read README.md files in relevant directories (limit 2KB each)
4. Combine database insights with README context to assess task requirements
5. Use database analytics to determine optimal file selection and avoid unnecessary code analysis
5. Load specific code files only when determined essential
6. Maintain flexibility to access additional files when needed

**README Priority Order**:
1. Project root README.md
2. Theme directory READMEs
3. Subdirectory READMEs in loaded paths

## 5.3 Global File Access Protocol

**Directive**: Certain files are always accessible regardless of theme context.

**Always-Accessible Files**:
- Configuration: `package.json`, `requirements.txt`, `*.config.js`, `.env`
- Documentation: `README.md`, `LICENSE`, `CHANGELOG.md`
- Entry points: `index.js`, `main.ts`, `app.js`, `App.tsx`
- Global utilities: `src/config/`, `src/constants/`, `src/types/`, `src/utils/`
- Build/deployment: `Dockerfile`, `docker-compose.yml`, `Makefile`

**Access Rules**:
- Available when contextually relevant
- No forced loading
- Modification allowed when appropriate
- Cross-theme accessibility maintained

## 5.4 Task Creation and Theme Scope Selection

**Directive**: AI determines theme scope for task files at creation based on task requirements.

**Configuration**: `tasks.autoTaskCreation` in `UserSettings/config.json`

**Theme Scope Selection Protocol**:
1. AI analyzes task requirements to determine appropriate theme scope
2. Primary theme selection based on task domain and file requirements
3. Related themes identified based on cross-theme dependencies

**Approval Requirements**:
- **If `tasks.autoTaskCreation` = true**: AI can create task files with determined theme scope without user approval
- **If `tasks.autoTaskCreation` = false**: User approval required for task file creation with AI-determined theme scope
- **Context Escalation**: Always requires user approval regardless of `autoTaskCreation` setting

**Task File Theme Scope Documentation**:
- Theme scope must be documented in task file `contextMode` field
- Primary theme and related themes must be specified
- Rationale for theme selection should be included in task notes if `autoTaskCreation` = false

### Global Dependencies and Project Root Context

#### Always-Available Files
Certain files and folders are always accessible regardless of theme context, following normal AI assessment behavior:

**Project Root Level:**
- Configuration files: `package.json`, `requirements.txt`, `Cargo.toml`, `composer.json`
- Environment files: `.env`, `.env.local`, `config.json`, `settings.json`
- Build/deployment files: `Dockerfile`, `docker-compose.yml`, `Makefile`, `vite.config.js`
- Documentation: `README.md`, `LICENSE`, `CHANGELOG.md`
- Version control: `.gitignore`, `.gitattributes`

**Source Root Level (e.g., `src/`):**
- Entry points: `index.js`, `main.ts`, `app.js`, `App.tsx`
- Global configuration: `config/`, `constants/`, `types/`, `utils/`
- Core application files: `app.js`, `router.js`, `store.js`

#### Context Accessibility
- **Available as needed**: Files are not force-loaded but remain accessible for AI assessment
- **Normal AI behavior**: AI determines relevance and necessity using standard evaluation
- **Cross-theme relevance**: Global files can be accessed from any theme context
- **Modification allowed**: AI can modify these files when contextually appropriate

#### Shared File Impact Assessment
When modifying shared files, AI should:
1. **Identify affected themes**: Check `shared: ["theme1", "theme2"]` array
2. **Quick impact assessment**: Review each theme's README for potential conflicts
3. **Proceed with awareness**: Make changes while considering cross-theme implications
4. **Document cross-theme changes**: Log modifications affecting multiple themes

## 5.4 Context Escalation Protocol

**Directive**: Handle mid-task context escalation through structured decision process.

**Escalation Decision Tree**:
```
1. Assess if sidequest can resolve the issue
   - If yes: Create sidequest instead of escalating
   - If no: Proceed to context escalation

2. Determine escalation need:
   - Current context insufficient for proper implementation
   - Cross-theme dependencies discovered
   - Architectural changes needed
   - Risk of breaking changes without broader context

3. User communication:
   - Explain specific need for broader context
   - Present options (sidequest vs escalation)
   - Request explicit permission
   - Document escalation reasoning

4. Implementation:
   - Maximum one escalation per task
   - Log escalation in ai-decisions.jsonl
   - Update noteworthy.json
   - Prepare rollback if escalation doesn't resolve issue
```

**User Notification Format**:
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
- Note escalation reason in task progress

#### 5. Escalation Constraints
- **Maximum one escalation per task**: Avoid cascading context expansion
- **User approval required**: Never escalate without explicit permission
- **Rollback capability**: Be prepared to revert if escalation doesn't resolve the issue
- **Impact assessment**: Consider how escalation affects task completion time

## 5.5 Memory Optimization Requirements

**Directive**: Maintain optimal memory usage and performance.

**Optimization Rules**:
- Limit README files to 2KB each
- Stream large files instead of loading into memory
- Use lazy loading for theme definitions
- Estimate memory usage and warn if >100MB
- Recommend context reduction if memory usage excessive
- Cache frequently accessed theme data

## 5.6 Context Loading Optimization Directive

### README-Guided Theme Context Loading

AI must follow this logic sequence for efficient context loading:

1. Load primary theme structure from `Themes/[theme].json`
2. Read README.md files in relevant theme directories for context
3. Assess task requirements and determine specific files needed
4. Use contextMode (theme-focused/theme-expanded/project-wide) as guidance
5. AI can escalate context when determining code analysis is necessary
6. Optimize cache usage by avoiding unnecessary code evaluation unless essential

**Purpose**: Allow AI to work efficiently by reading READMEs for directory context rather than analyzing code files immediately, while maintaining flexibility to access code when determined necessary.

## 5.7 Multi-Flow Context Loading Protocol

**Directive**: Handle multi-flow system context loading with flow scope optimization and theme scope fallback.

### Multi-Flow Structure Support

**Flow Index Loading**:
1. **Load flow-index.json** to understand available flow files and cross-flow dependencies
2. **Selective Flow Loading**: Load only relevant flow files based on task requirements
3. **Cross-Flow Dependencies**: Always load referenced flow files from flow-index.json
4. **Flow File Limits**: Respect `contextLoading.maxFlowFiles` (default: 3)

**Flow File Loading Rules**:
- **Theme-Focused**: Load flow files associated with primary theme
- **Theme-Expanded**: Load flow files from primary + related themes
- **Project-Wide**: Load all flow files (subject to maxFlowFiles limit)
- **Cross-Flow Dependencies**: Always load referenced flow files from flow-index.json

### Flow Scope vs Theme Scope Protocol

**Critical Directive**: Flow scope is a performance optimization, not a limitation. Theme scope is always available.

**Flow Scope Implementation**:
- **Initial Context**: Start with flow scope for resource management and performance
- **Automatic Expansion**: AI can expand from flow scope to theme scope without user approval
- **No Restrictions**: Flow scope is self-implemented optimization, not a boundary
- **Resource Management**: Use flow scope to minimize initial memory usage

**Theme Scope Authority**:
- **Always Available**: Theme scope is the defined scope boundary for complete context
- **Automatic Escalation**: AI determines when flow scope is insufficient and expands automatically
- **No User Approval**: Expansion from flow scope to theme scope requires no approval or notification
- **Performance Optimization**: Flow scope improves performance, theme scope ensures completeness

**Implementation Guidelines**:
1. **Start with Flow Scope**: Load only flow files referenced in task for initial context
2. **Evaluate Sufficiency**: AI determines if flow scope provides adequate context
3. **Automatic Expansion**: If insufficient, immediately expand to theme scope
4. **No Barriers**: No approval, notification, or consideration needed for expansion
5. **Theme Scope Definition**: Theme scope handles all scope expansion decisions

**Benefits**:
- **Optimized Performance**: Start with minimal flow context for resource efficiency
- **Guaranteed Completeness**: Theme scope always available for full context
- **AI Autonomy**: AI determines context needs without user interruption
- **Flexible Implementation**: Self-managed optimization with complete fallback