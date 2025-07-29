# File Operations Directives

## 10.1 Line Limit Enforcement

**Directive**: Enforce maximum file line limits to prevent unwieldy files.

**Configuration**: `project.maxFileLineCount` (default: 900)

**Rules**:
- Read line limit from `project.maxFileLineCount` in config.json
- Check line count after every file modification
- If limit exceeded, modularize into logical functional groups
- Create properly named module files
- Update imports and references
- Maintain proper linking system (index files)

**Modularization Guidelines**:
- Group by function/responsibility
- Maintain clear naming conventions
- Preserve all functionality
- Update all references
- Document modularization in README.md

Use UserSettings/config.json to define the maximum number of lines allowed in a single code file.

The default is 900 lines.
After any code edit, the AI must:
- Evaluate the file's line count
- If it exceeds the configured limit, modularize the content into smaller, logically grouped files (e.g., by function groups, routes, utilities, etc.)

Modularized files must be properly named and referenced in their original location or through an appropriate linking system (e.g., index files).

## 10.2 Anti-Placeholder Protocol

**Directive**: Never use placeholder text or truncated outputs.

**Configuration**: `project.avoidPlaceholders` (default: true)

**Prohibited Patterns**:
- `...continued`
- `rest of file unchanged`
- `// TODO: implement this`
- `/* placeholder */`
- Truncated code blocks
- Incomplete implementations without explicit user permission
- `in a real implementation`
- `for now`
- `simplified`
- `for simplicity`
- `todo`
- `fixme`
- `temporary`
- `future`

**Required Behavior**:
- When `project.avoidPlaceholders` is true: Always output complete implementations
- If file too large, modularize before outputting
- If scope unclear, ask for clarification
- No speculative summarization
- Full content required unless user explicitly allows partial output
- Track any TODO items in Placeholders/todos.jsonl for later resolution

### Avoiding Placeholders

This MCP is intended for use in software and coding projects where placeholder text or truncated edits can cause confusion, break flow continuity, or damage structured files.

To minimize and ideally eliminate placeholder behavior:

**Avoid partial edits**: AI must never use placeholder markers like ...continued, rest of file unchanged, or truncated. All output must be complete unless the user explicitly allows otherwise.

**Modularization requirement**: If a file exceeds the limit post-edit, AI must modularize the file into functional groups (e.g. utility functions, route handlers, view logic) and store them in appropriately named files and folders.

**Directive scope awareness**: Before editing or outputting a file, AI must evaluate whether the full content can be handled within the set limit. If not, AI must restructure or summarize internally but output the full result to the user.

**No speculative summarization**: Summaries are allowed only when requested. AI must not assume what the user already knows or insert editorialized commentary.

#### Why Placeholders Get Added (When They Shouldn't)

**Context Window Misjudgment**: The model may wrongly assume that output size exceeds token limits, even when it's safe.

**Legacy Training Behavior**: AI models were trained to avoid full replacements due to constraints in older environments. This behavior has persisted.

**False Efficiency Heuristic**: AI may wrongly prioritize brevity or assume the user prefers cleaner deltas.

**Internal Tooling Mismatch**: LLM-connected tools often chunk code updates or show diffs, reinforcing this habit.

**Human Training Oversight**: Human raters often rewarded compact edits, inadvertently training models to truncate unless explicitly told not to.

## 10.3 File Modification Protocol

**Directive**: Handle file operations with proper validation and backup.

**Pre-Modification Checks**:
1. Verify file exists and is accessible
2. Check if file is shared across themes
3. Assess impact on related themes
4. Review README context for directory
5. Validate against line limits
6. Consider backup if destructive operation

**Shared File Handling**:
1. Identify all themes sharing the file
2. Read READMEs for affected themes
3. Assess cross-theme impact
4. Document modifications in ai-decisions.jsonl
5. Note potential impacts in noteworthy.json
6. Update theme READMEs if necessary

## 10.4 Global Dependencies Access Directive

### Global File Access Protocol

Certain files and directories are always accessible regardless of theme context, following normal AI assessment behavior.

#### Always-Accessible Files
**Project Root Level:**
- Configuration files: `package.json`, `requirements.txt`, `Cargo.toml`, `composer.json`
- Environment files: `.env`, `.env.local`, `config.json`, `settings.json`
- Build/deployment files: `Dockerfile`, `docker-compose.yml`, `Makefile`, `*.config.js`
- Documentation: `README.md`, `LICENSE`, `CHANGELOG.md`
- Version control: `.gitignore`, `.gitattributes`

**Source Root Level (e.g., `src/`):**
- Entry points: `index.js`, `main.ts`, `app.js`, `App.tsx`
- Global configuration: `config/`, `constants/`, `types/`, `utils/`
- Core application files: `app.js`, `router.js`, `store.js`

#### Access Protocol
**Natural AI behavior:**
- Files are available for assessment when contextually relevant
- AI determines necessity using standard evaluation methods
- No forced loading - files accessed only when needed

**Cross-theme accessibility:**
- Global files accessible from any theme context
- No theme boundaries for global dependencies
- Modification allowed when contextually appropriate

#### Shared File Impact Assessment
When modifying files marked as `shared: ["theme1", "theme2"]`:

**Assessment process:**
1. **Identify affected themes**: Check the `sharedWith` array in theme files
2. **Quick impact review**: Read README.md files for each affected theme
3. **Conflict assessment**: Evaluate if changes might break other theme functionality
4. **Proceed with awareness**: Make changes while considering cross-theme implications

**Documentation requirements:**
- Log cross-theme modifications in ai-decisions.jsonl
- Update affected theme README files if necessary

#### Modification Guidelines
**When to modify global files:**
- Changes are contextually appropriate for the current task
- Modifications align with project-wide standards
- Updates improve overall project consistency

**Assessment criteria:**
- Will this change affect other themes negatively?
- Are there alternative approaches that minimize cross-theme impact?
- Is this the appropriate time to make this change?

**Documentation format:**
```json
{
  "timestamp": "2025-07-12T10:30:00Z",
  "type": "shared-file-modification",
  "file": "src/types/User.ts",
  "sharedWith": ["authentication", "user-management"],
  "changes": "Added optional avatar field to User interface",
  "impactAssessment": "Low impact - optional field, backward compatible",
  "themeReadmeReviewed": ["authentication", "user-management"]
}
```

## 10.5 JSON Minification Protocol

**Directive**: Control JSON file formatting based on configuration.

**Configuration**: `project.minifyJson` (default: true)

**Rules**:
- Read minification setting from `project.minifyJson` in config.json
- Apply minification rules when writing organizational JSON files
- Preserve readability when minification is disabled

**Minifiable Files**:
- All organizational JSON files in `projectManagement/` directory
- Task files: `Tasks/active/*.json`, `Tasks/sidequests/*.json`
- Theme files: `Themes/*.json`
- Configuration files: `UserSettings/config.json`
- Template files: `reference/templates/*.json`
- Directive files: `reference/directives/*.json`

**Non-Minifiable Files**:
- `Logs/noteworthy.json` (session-specific items)
- Log files: `Logs/noteworthy.json`
- Archive files (maintain original format)
- User-edited configuration files (preserve user formatting)

**Minification Behavior**:
- When `project.minifyJson` is `true`: Use `JSON.stringify()` with no spacing
- When `project.minifyJson` is `false`: Use `JSON.stringify()` with 2-space indentation
- Always validate JSON structure before writing
- Preserve all data content regardless of formatting

**Implementation Example**:
```javascript
// Read minification setting
const minifyJson = config.project.minifyJson || true;

// Apply formatting
const jsonOutput = minifyJson 
  ? JSON.stringify(data) 
  : JSON.stringify(data, null, 2);
```

**Benefits**:
- Reduced file sizes for organizational data
- Faster parsing and loading times
- Configurable based on user preference
- Maintains data integrity

## 10.6 Shared File Impact Assessment

**Directive**: Assess and document modifications to files shared across themes.

**Assessment Process**:
1. Identify affected themes from sharedWith array
2. Quick impact review by reading README.md files for affected themes
3. Conflict assessment - evaluate if changes might break other functionality
4. Proceed with awareness considering cross-theme implications

**Documentation Requirements**:
- Log cross-theme modifications in noteworthy.json
- Update affected theme README files if necessary

**Modification Guidelines**:
- Changes are contextually appropriate for current task
- Modifications align with project-wide standards
- Updates improve overall project consistency

**Assessment Criteria**:
- Will this change affect other themes negatively?
- Are there alternative approaches that minimize cross-theme impact?
- Is this the appropriate time to make this change?

## 10.7 Version Control Integration

**Directive**: Work harmoniously with version control systems.

**Version Control Awareness**:
- Respect .gitignore and similar patterns
- Document significant changes in appropriate commit contexts
- Consider impact on code reviews
- Maintain clean file states for commits
- Avoid creating conflicts with development workflows

## 10.8 Enforcement Triggers

**When File Operation Rules Apply**:
- Before any file write operation
- After any file modification
- During code generation
- When creating new files
- During refactoring operations

## 10.9 Documentation Format

**Shared File Modification Log Format**:
```json
{
  "timestamp": "ISO 8601 format",
  "type": "shared-file-modification",
  "file": "file path",
  "sharedWith": "array of theme names",
  "changes": "description of changes made",
  "impactAssessment": "impact level and description",
  "themeReadmeReviewed": "array of reviewed theme READMEs"
}
```