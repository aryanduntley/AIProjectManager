# Metadata Management Directives

## 13.1 Project Metadata Overview

**Directive**: Maintain dynamic project characteristics in ProjectBlueprint/metadata.json as factual documentation, not user preferences.

**Purpose**: 
- Document project facts and characteristics discovered during development
- Store technical project data separate from user configuration
- Track project evolution and technical decisions over time
- Provide AI with project context for informed decision-making

**File Location**: `ProjectBlueprint/metadata.json`

## 13.2 Metadata Structure and Content

**Directive**: Metadata.json is a dynamic, evolving file that captures project characteristics as they are discovered or changed.

**Core Structure**:
```json
{
  "project": {
    "name": "Project Name",
    "version": "1.0.0",
    "description": "Brief project description",
    "type": "web-application|mobile-app|desktop-app|library|api|other",
    "status": "planning|development|testing|production|maintenance"
  },
  "mcp": {
    "version": "1.0.0",
    "namespace": "project.management.organization.{userprojectname}",
    "created": "2025-01-15T10:30:00Z",
    "compatibilityVersion": "1.0.0",
    "lastUpdated": "2025-01-15T10:30:00Z"
  },
  "technical": {
    "language": "javascript|typescript|python|java|other",
    "frameworks": ["react", "express", "node"],
    "databases": ["postgresql", "mongodb"],
    "testFramework": "jest|vitest|pytest|junit|other",
    "buildTool": "vite|webpack|rollup|maven|gradle|other",
    "packageManager": "npm|yarn|pnpm|pip|maven|other",
    "linter": "eslint|prettier|pylint|other",
    "typeChecker": "typescript|mypy|flow|other"
  },
  "deployment": {
    "environment": "development|staging|production",
    "platform": "web|mobile|desktop|server",
    "containerization": "docker|kubernetes|none",
    "cicd": "github-actions|gitlab-ci|jenkins|none",
    "hosting": "aws|azure|gcp|vercel|netlify|self-hosted|other"
  },
  "architecture": {
    "pattern": "mvc|mvp|mvvm|microservices|monolith|other",
    "api": "rest|graphql|grpc|soap|other",
    "frontend": "spa|mpa|ssr|ssg|other",
    "authentication": "jwt|oauth|session|none|other",
    "database": "relational|nosql|hybrid|none"
  },
  "integrations": {
    "external": ["stripe", "auth0", "sendgrid"],
    "apis": ["payment-gateway", "email-service", "maps"],
    "services": ["analytics", "monitoring", "logging"]
  },
  "compliance": {
    "gdpr": true,
    "hipaa": false,
    "sox": false,
    "pci": true,
    "accessibility": "wcag-aa|wcag-aaa|none"
  },
  "team": {
    "size": 3,
    "methodology": "agile|waterfall|kanban|scrum|other",
    "codeStyle": "functional|object-oriented|procedural|mixed",
    "reviewProcess": "mandatory|optional|none"
  },
  "timeline": {
    "startDate": "2025-01-01",
    "estimatedCompletion": "2025-06-01",
    "milestones": ["mvp", "beta", "production"]
  },
  "custom": {
    "domain": "e-commerce|healthcare|finance|education|other",
    "targetAudience": "consumers|businesses|developers|other",
    "scalability": "small|medium|large|enterprise",
    "performance": "standard|high|critical"
  }
}
```

## 13.3 Metadata Update Triggers

**Directive**: Update metadata.json whenever project characteristics change or are discovered.

**Primary Update Triggers**:
1. **ProjectBlueprint Creation/Update**: Always update metadata when blueprint changes
2. **ProjectLogic Modifications**: Update metadata when logic changes reveal new project characteristics
3. **Theme Discovery**: Update frameworks, languages, and technical stack
4. **Dependency Installation**: Update package managers, build tools, frameworks
5. **Architecture Decisions**: Update patterns, API types, database choices
6. **Integration Additions**: Update external services, APIs, third-party tools
7. **Deployment Changes**: Update hosting, CI/CD, containerization
8. **Compliance Requirements**: Update regulatory compliance needs

**Secondary Update Triggers**:
- New team members or methodology changes
- Performance or scalability requirement changes
- Timeline adjustments
- Custom domain or audience changes

## 13.4 Metadata vs Configuration Distinction

**Directive**: Clearly distinguish between metadata (project facts) and configuration (user preferences).

**Metadata (ProjectBlueprint/metadata.json)**:
- **Project Facts**: What the project IS
- **Technical Stack**: What tools/frameworks are USED
- **Architecture**: How the project is BUILT
- **Deployment**: Where the project RUNS
- **Compliance**: What regulations APPLY
- **Timeline**: When things HAPPEN

**Configuration (.ai-pm-config.json)**:
- **User Preferences**: How AI should BEHAVE
- **Workflow Settings**: How tasks should be MANAGED
- **Validation Rules**: What validation should be ENFORCED
- **Context Loading**: How context should be LOADED
- **Archiving**: How data should be RETAINED

## 13.5 Integration with Project Workflows

**Directive**: Ensure metadata is consistently updated throughout project lifecycle.

### 13.5.1 Blueprint Integration

**When ProjectBlueprint is Created**:
1. Initialize metadata.json with basic project information
2. Set MCP version and compatibility data
3. Document known technical characteristics
4. Establish baseline project facts

**When ProjectBlueprint is Updated**:
1. Review metadata for outdated information
2. Update project description, status, or type if changed
3. Adjust timeline if scope changes
4. Update custom domain or audience if requirements shift

### 13.5.2 ProjectLogic Integration

**When ProjectLogic is Modified**:
1. Check if logic changes reveal new technical characteristics
2. Update architecture patterns if structural decisions change
3. Update integrations if new services are added
4. Update technical stack if new frameworks are adopted
5. Update deployment if hosting decisions change

**Examples of Logic-Triggered Updates**:
- Logic entry about switching from REST to GraphQL → Update `architecture.api`
- Logic entry about adding authentication → Update `architecture.authentication`
- Logic entry about new payment integration → Update `integrations.external`
- Logic entry about performance requirements → Update `custom.performance`

### 13.5.3 Theme Discovery Integration

**During Theme Discovery**:
1. Analyze detected frameworks and update `technical.frameworks`
2. Identify database usage and update `technical.databases`
3. Detect testing patterns and update `technical.testFramework`
4. Discover build tools and update `technical.buildTool`
5. Identify external integrations and update `integrations`

## 13.6 Metadata Maintenance Protocol

**Directive**: Maintain metadata accuracy and relevance through regular review and updates.

**Maintenance Actions**:
1. **Validation Check**: Ensure all metadata entries are current and accurate
2. **Consistency Review**: Verify metadata aligns with actual project state
3. **Obsolete Removal**: Remove outdated or irrelevant metadata entries
4. **Gap Analysis**: Identify missing metadata that should be documented
5. **Version Updates**: Update MCP version compatibility when system changes

**Maintenance Triggers**:
- Major milestone completion
- Significant architecture changes
- Technology stack updates
- Deployment environment changes
- Team or methodology changes

## 13.7 Metadata Access and Usage

**Directive**: Use metadata to inform AI decision-making and provide project context.

**AI Usage Guidelines**:
- **Context Loading**: Use metadata to understand project scope and complexity
- **Decision Making**: Consider technical stack when suggesting solutions
- **Validation**: Ensure suggestions align with project architecture and compliance
- **Integration**: Consider existing integrations when proposing new features
- **Testing**: Use testing framework information for appropriate test creation

**User Benefits**:
- **Project Overview**: Quick understanding of project characteristics
- **Onboarding**: New team members can quickly understand project setup
- **Documentation**: Comprehensive project documentation for stakeholders
- **Decision Support**: Historical context for architectural and technical decisions

## 13.8 Metadata Versioning and History

**Directive**: Track metadata changes over time for project evolution understanding.

**Version Management**:
- Update `mcp.lastUpdated` timestamp on every change
- Maintain compatibility version for MCP system updates
- Track major changes in projectlogic.jsonl with metadata references

**Change Documentation**:
- Log significant metadata changes in projectlogic.jsonl
- Reference metadata changes in task completion notes
- Document reasoning for metadata updates
- Maintain audit trail of project characteristic evolution

## 13.9 Error Handling and Validation

**Directive**: Ensure metadata integrity through proper validation and error handling.

**Validation Requirements**:
- All required fields must be present
- Enum values must be from predefined lists
- Dates must be valid ISO format
- Arrays must contain valid entries
- Custom fields must have clear descriptions

**Error Handling**:
- Validate metadata before saving
- Provide clear error messages for invalid data
- Offer correction suggestions for common errors
- Maintain backup of previous valid metadata
- Log validation errors for debugging

**Recovery Procedures**:
- Restore from backup if corruption detected
- Reconstruct from project analysis if backup unavailable
- Validate against project reality if inconsistencies found
- Update MCP compatibility if version conflicts arise

---

**Integration Points**:
- **Project Initialization**: Create initial metadata.json
- **Blueprint Updates**: Review and update metadata
- **Logic Changes**: Update metadata when characteristics change
- **Theme Discovery**: Update technical stack information
- **Task Completion**: Review metadata for updates
- **Session Boot**: Load metadata for project context
- **Validation**: Verify metadata accuracy during quality checks