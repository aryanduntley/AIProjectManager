# Theme Management Directives

## 4.1 Automatic Theme Discovery Protocol

**Directive**: Theme discovery is mandatory for new projects and must follow user review process.

**Discovery Sequence**:
```
1. Analyze project structure using FileAnalyzer
2. Identify themes across 6 categories:
   - Functional Domains (auth, payment, user-management, etc.)
   - Technical Layers (database, api, security, testing, etc.)
   - User Interface (components, pages, layout, styling)
   - External Integrations (social-media, analytics, maps, etc.)
   - Data Management (validation, transformation)
   - Operational (logging, monitoring, deployment)
3. Calculate confidence scores with evidence collection
4. Identify custom themes from project-specific patterns
5. MANDATORY: Present to user for review
6. Incorporate user feedback and modifications
7. Get explicit approval before creating theme files
8. Document theme decisions in projectlogic.jsonl
```

**Critical**: NEVER create theme files without user approval.

### Auto-Maintenance Logic for Theme Discovery:

- MCP uses keyword matching, folder path structure, and import reference graphs to discover thematic relevance
- Any time files/folders are created, moved, or deleted, MCP will:
  - Reassess related theme files and update paths and links accordingly
  - Flag conflicts or duplicates and propose merges if overlapping themes are detected
- Theme files include:
  ```json
  {
    "theme": "transaction",
    "paths": ["src/services/transactions/", "src/components/transaction/"],
    "files": ["src/hooks/transaction/useTransaction.ts"],
    "linkedThemes": ["wallet"],
    "sharedFiles": {
      "src/types/Transaction.ts": {
        "sharedWith": ["wallet", "api"],
        "description": "Transaction type definitions"
      }
    }
  }
  ```
- MCP will maintain a `themes.json` root-level theme index with:
  ```json
  {
    "transaction": "Handles all transaction-related logic, UI, and service calls",
    "wallet": "Internal wallet, key signing, connection flows"
  }
  ```
- If a file clearly belongs to multiple themes, it may appear in both and be flagged as `shared: ["theme1", "theme2"]`
- When AI modifies a shared file, it should assess impact on all listed themes before proceeding

## 4.2 Theme Presentation Format

**Directive**: Always present discovered themes using this exact format:

```
## Discovered Project Themes

I've analyzed your project and identified the following themes:

**Functional Domains:**
1. **Authentication** - User login, registration, session management
2. **Payment Processing** - Transaction handling, billing, checkout flows

**Technical Layers:**
3. **Database** - Models, schemas, migrations, queries
4. **API** - Controllers, routes, middleware, endpoints

**User Interface:**
5. **UI Components** - Reusable components, forms, layouts

**External Integrations:**
6. **Email Service** - Notifications, verification, communications

Would you like to:
- Add additional themes I may have missed?
- Modify descriptions of existing themes?
- Remove themes that aren't relevant?
- Rename themes to better match your project terminology?
```

## 4.3 Theme File Structure Requirements

**Directive**: All theme files must follow this exact JSON structure:

```json
{
  "theme": "theme-name",
  "category": "functional_domains|technical_layers|user_interface|external_integrations|data_management|operational|user-defined",
  "description": "Clear description of theme purpose and scope",
  "confidence": 0.0-1.0,
  "paths": ["src/theme-dir", "components/theme-components"],
  "files": ["specific/files.ts", "related/files.js"],
  "linkedThemes": ["related-theme-1", "related-theme-2"],
  "sharedFiles": {
    "shared/file.ts": {
      "sharedWith": ["theme1", "theme2"],
      "description": "Description of sharing relationship"
    }
  },
  "frameworks": ["react", "express"],
  "keywords": ["keyword1", "keyword2"],
  "createdDate": "ISO timestamp",
  "lastModified": "ISO timestamp"
}
```

## 4.4 Theme Validation Requirements

**Directive**: Validate theme consistency before any theme-related operations.

**Configuration**: `themes.sharedFileThreshold` (default: 3)

**Validation Checks**:
- All referenced files and paths exist
- Linked themes are valid and exist
- No circular dependencies in theme relationships
- Shared files are properly documented
- Theme descriptions are clear and distinct
- File coverage is comprehensive (all project files in at least one theme)
- Shared file limit: No single file should be shared by more than `themes.sharedFileThreshold` themes
- When threshold exceeded: Suggest theme reorganization or file refactoring

## 4.5 Theme Modification Protocol

**Directive**: Handle theme modifications through proper approval process.

**User-Requested Changes**:
1. Analyze current theme structure
2. Propose modification with impact assessment
3. Show before/after comparison
4. Get explicit user approval
5. Update theme files and relationships
6. Update themes index
7. Document changes in projectlogic.jsonl

**AI-Initiated Updates**:
1. Identify improvement opportunity
2. Present proposed change with clear reasoning
3. Explain benefits to project organization
4. Get explicit user approval
5. Implement changes only after approval
6. Document rationale and impact

## 4.6 Theme Discovery and User Review Directive

### Theme Auto-Discovery Process

When initializing a new project or analyzing an existing codebase, the AI must follow this structured theme discovery process:

#### 1. Initial Theme Discovery
- **Analyze File Structure**: Examine directory names, file names, and folder organization
- **Parse Import Graphs**: Analyze import/export relationships to identify functional clusters
- **Keyword Matching**: Use predefined keywords and patterns to identify thematic areas
- **Code Analysis**: Examine function names, class names, and component names for thematic patterns

#### 2. Theme Identification Categories
The AI should identify themes in these categories:
- **Functional Domains**: Core business logic areas (authentication, payment, user management)
- **Technical Layers**: Infrastructure concerns (database, api, security, testing)
- **User Interface**: UI components, pages, layouts, forms
- **External Integrations**: Third-party services, APIs, external tools
- **Data Management**: Models, schemas, validation, transformation
- **Operational**: Deployment, configuration, monitoring, logging

#### 3. User Review and Modification Process
- **Present Complete List**: Show all discovered themes with descriptions
- **Request User Input**: Explicitly ask for modifications, additions, or removals
- **Iterative Refinement**: Allow multiple rounds of theme adjustment
- **Confirm Final List**: Get explicit user approval before proceeding
- **Document Changes**: Log all user-requested theme modifications in projectlogic.jsonl

#### 4. User-Driven Theme Additions
Users may identify domain-specific themes that automated discovery missed. Common examples:
- **Domain-Specific**: `transactionRequests`, `transactionMonitoring`, `transactionSigning`
- **Business Logic**: `coinSelection`, `userSettings`, `affiliateManagement`
- **Workflow-Specific**: `qrCodeProcessing`, `walletConnectFlow`, `recoveryProcess`

#### 5. Theme Validation Rules
Before finalizing themes, ensure:
- **No Overlapping Domains**: Each theme has distinct responsibility
- **Balanced Granularity**: Themes are neither too broad nor too narrow
- **Clear Descriptions**: Each theme has unambiguous purpose
- **File Coverage**: All project files belong to at least one theme
- **Logical Relationships**: Related themes are properly linked

#### 6. Theme File Creation
Only after user approval:
- Create individual theme JSON files in `Themes/` directory
- Generate master `themes.json` index file
- Update `projectlogic.jsonl` with theme decisions
- Link themes to existing user flows and tasks

#### 7. Mandatory User Approval
**CRITICAL**: AI must **NEVER** proceed with theme creation without explicit user approval. The theme discovery process is:
1. Discover themes automatically
2. Present to user for review
3. Incorporate user feedback
4. Confirm final theme list
5. Only then create theme files

## 4.8 Theme-Flow Relationship

**Purpose**: Themes and user flows serve complementary but distinct purposes in project organization.

**Relationship Definition**:
- **Themes** organize code structure and implementation files ("what" - static organization)
- **User Flows** define user experience journeys ("how" - dynamic processes)
- **Bidirectional Awareness**: Each system can reference the other for context

**Theme Flow References**:
- Themes maintain a `flows` array listing relevant flow IDs in order of relevance
- Flow IDs reference flows across the multi-file flow system
- MCP uses flow-index.json to resolve flow IDs to specific flow files
- Maximum flows per theme configurable via `themes.maxFlowsPerTheme` setting

**Flow Reference Structure**:
```json
{
  "flows": [
    "most-relevant-flow-id",
    "second-most-relevant-flow-id",
    "least-relevant-flow-id"
  ]
}
```

**Many-to-Many Relationship**:
- One theme can contain multiple flows
- One flow can be used by multiple themes
- MCP maintains theme-flow relationships in project database (`projectManagement/project.db`)
- Relationships discovered by evaluating theme files during session boot

**AI Usage Guidelines**:
- Use themes to understand code organization when implementing flow steps
- Use flows to understand user experience when working within theme contexts
- Query database for efficient "which themes use this flow" lookups
- Update database when theme flow references change

**Integration Through Tasks**:
- Tasks reference both themes (for context) and flows (for user experience)
- Subtasks specify which flow steps they implement using which theme files
- Database provides fast lookups for theme-flow relationships during task planning

#### 8. Ongoing Theme Management Protocol

**User-Requested Theme Changes:**
Users can request theme modifications at any time during development:
- **Add new themes**: "We need a theme for currency selection"
- **Modify existing themes**: "The payment theme should include subscription logic"
- **Remove themes**: "The testing theme isn't needed anymore"
- **Reorganize themes**: "Move wallet integration from payment to security theme"

**AI Response to User Theme Requests:**
1. **Assess project structure**: Analyze existing files and structure for the requested theme
2. **Present theme proposal**: Show proposed theme structure with files and relationships
3. **Get user approval**: Confirm theme structure before implementation
4. **Update theme files**: Create or modify theme JSON files after approval
5. **Document changes**: Log theme modifications in projectlogic.jsonl

**AI-Initiated Theme Updates:**
If AI identifies theme improvements during development:
- Present proposed changes to user with clear reasoning
- Explain why the modification would improve project organization
- Get explicit approval before updating theme files
- Document all changes with rationale

This directive ensures themes evolve with the project and accurately represent the user's mental model rather than AI assumptions.