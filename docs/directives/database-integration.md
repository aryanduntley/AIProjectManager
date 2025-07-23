# Database Integration Directives

## Overview

The database integration system implements a hybrid architecture that preserves human-readable organizational files while providing database-powered operational intelligence and performance optimization. This approach ensures seamless session restoration, real-time state synchronization, and intelligent project insights while maintaining version control compatibility.

**Core Philosophy**: Files remain the human-readable source of truth, database provides operational intelligence and performance optimization.

## When This System Applies

### Primary Triggers
- **Project initialization** - Database setup and schema initialization
- **Session management** - Context preservation and restoration
- **State synchronization** - Real-time updates between files and database
- **Performance optimization** - Fast queries and intelligent recommendations
- **Task lifecycle management** - Progress tracking and coordination

### Critical For
- **Session continuity** - Complete session restoration across interruptions
- **State preservation** - Zero work loss from premature session termination
- **Performance optimization** - Fast context loading and intelligent queries
- **Multi-session coordination** - Instance management and conflict resolution

## Hybrid Architecture Design

### Files Preserved (Human-Readable Source of Truth)
**Purpose**: Maintain human readability and version control compatibility

**Preserved Files**:
- **`blueprint.md`** - Project overview and goals in plain language
- **`projectlogic.jsonl`** - Decision history and reasoning for review
- **`flow-index.json` + individual flow files** - User experience definitions
- **Task definition files** - Work item specifications and requirements
- **Theme definition files** - Project organization structure
- **`config.json`** - User preferences and configuration settings

**Benefits**:
- Human-readable and editable without database tools
- Version control friendly (Git diffs, merges, history)
- Portable across different database systems
- Backup and recovery through standard file operations

### Database Enhanced (Operational Intelligence)
**Purpose**: Enable fast queries, session restoration, and intelligent recommendations

**Database Enhancements**:
- **Real-time status tracking** - Tasks, subtasks, sidequests, flow progress
- **Session persistence** - Complete context snapshots for restoration
- **Theme-flow relationship optimization** - Fast lookup tables and indexes
- **Event analytics** - Decision tracking and pattern recognition
- **Performance metrics** - User learning and productivity analysis
- **File modification logging** - Change tracking and impact analysis

**Benefits**:
- Sub-second session restoration
- Complex queries for project analytics
- Real-time progress tracking and coordination
- Intelligent context recommendations
- Performance optimization for large projects

## Real-Time State Synchronization

### Mandatory Synchronization Requirement
**Critical Rule**: ALL organizational files MUST be synchronized with database records in real-time for seamless session restoration.

**Atomic Operations Principle**: File updates and database updates must succeed together or fail together.

### Atomic Operation Implementation
```
Database Transaction Process:
1. BEGIN database transaction
2. Update organizational files on disk
3. Update corresponding database records  
4. IF both succeed: COMMIT transaction
5. IF either fails: ROLLBACK transaction and retry
6. IF retry fails: Request user intervention
```

**Failure Handling**: If synchronization fails, retry entire operation or escalate to user with clear error message and recovery options.

### Synchronization Triggers

#### Task Management Triggers
- **Task status changes** - pending → in-progress → completed transitions
- **Subtask completion** - Progress updates and milestone integration
- **Sidequest creation** - Context preservation and limit tracking
- **Sidequest activation** - Parent task pausing and context switching
- **Sidequest completion** - Context restoration and task resumption
- **Task queue modifications** - Prioritization and coordination changes

#### Session Management Triggers  
- **Session start** - Context loading and theme initialization
- **Context mode escalation** - theme-focused → theme-expanded → project-wide
- **Theme switching** - Context updates and relationship changes
- **Session pause** - Context snapshot preservation
- **Session termination** - Final state preservation

#### Project Management Triggers
- **Theme modifications** - File associations and relationship updates
- **Flow status updates** - Progress tracking and milestone integration
- **Blueprint changes** - Logic evolution and decision tracking
- **Implementation plan progress** - Phase completion and archival

## Session Persistence System

### Database Tables for Session Management

#### `sessions` Table
**Purpose**: Track session lifecycle and high-level context
**Key Fields**:
- `session_id` - Unique session identifier  
- `start_time` - Session initiation timestamp
- `context_mode` - Current context loading mode
- `active_themes` - JSON array of currently loaded themes
- `active_tasks` - JSON array of active task IDs
- `active_sidequests` - JSON array of active sidequest IDs
- `project_path` - Project root directory path

**Usage**: Session identification and basic context restoration

#### `session_context` Table  
**Purpose**: Detailed session context for complete restoration
**Key Fields**:
- `session_id` - Reference to sessions table
- `loaded_themes` - Comma-separated theme names loaded
- `loaded_flows` - Comma-separated flow file names loaded
- `context_escalations` - Count of escalations performed
- `files_accessed` - JSON array of accessed file paths

**Usage**: Detailed context snapshots for exact session restoration

### Context Snapshot System

#### When to Capture Context Snapshots
- **Before creating sidequests** - Preserve parent task context completely
- **During context escalation** - Preserve previous context before expansion
- **At regular intervals during long tasks** - Prevent work loss from interruptions
- **Before session termination** - Final state preservation
- **After significant work completion** - Milestone preservation

#### What to Capture in Snapshots
**Complete AI State Preservation**:
- **Current subtask ID and progress position** - Exact location in work
- **Loaded themes and flow files** - Context that was active
- **Active file contexts and modification state** - What was being worked on
- **User interaction history and preferences** - Communication context
- **AI reasoning state and decision context** - Thought process preservation

#### Context Restoration Process
```
Session Restoration Sequence:
1. Query database for latest session context
2. Restore theme and flow context from snapshots  
3. Load active tasks and subtasks with exact progress state
4. Resume from exact interruption point with full context
5. Present brief summary to user: "Resuming work on [specific context]"
```

### Session Boot Optimization

#### Fast Boot Sequence
**Performance Target**: Session restoration < 2 seconds
```
Optimized Boot Process:
1. Initialize database connection (< 100ms)
2. Query latest session context from database (< 200ms)  
3. Load active tasks and implementation plans from database status (< 300ms)
4. Restore theme-flow relationships from database cache (< 200ms)
5. Load only necessary files based on database intelligence (< 1000ms)
6. Resume exact work state with minimal user review (< 200ms)
Total: < 2 seconds for complete session restoration
```

#### Database Query Optimization
- **Indexed queries** - All session restoration queries use optimized indexes
- **Single query restoration** - One complex query retrieves all needed context
- **Pre-computed views** - Common session data pre-aggregated for speed
- **Connection pooling** - Database connections optimized for performance

## Task Status Tracking System

### Core Database Tables

#### `task_status` Table
**Purpose**: Real-time task lifecycle management
**Critical Fields**:
- `task_id` - Unique task identifier
- `status` - Current status (pending, in-progress, blocked, completed)
- `progress_percentage` - Current completion percentage
- `milestone_id` - Reference to completion-path.json milestone
- `primary_theme` - Primary theme for context loading
- `last_updated` - Timestamp of last modification

**Real-Time Updates**: Updated immediately after every work completion unit

#### `subtask_status` Table
**Purpose**: Detailed subtask progress and flow integration
**Critical Fields**:
- `subtask_id` - Unique subtask identifier
- `parent_id` - Reference to parent task or sidequest
- `status` - Current subtask status
- `flow_references` - JSON array of linked flow steps
- `context_mode` - Required context loading mode
- `progress_percentage` - Subtask completion percentage

**Flow Integration**: Links subtasks to specific flow steps for user experience tracking

#### `sidequest_status` Table
**Purpose**: Multiple sidequest coordination and limit enforcement
**Critical Fields**:
- `sidequest_id` - Unique sidequest identifier
- `parent_task_id` - Reference to parent task
- `status` - Current sidequest status
- `impact_on_parent` - How sidequest affects parent task
- `scope_description` - Clear description of sidequest purpose

**Limit Enforcement**: Automatic database triggers maintain sidequest count limits per task

### Multiple Sidequest Management

#### Automatic Limit Enforcement
**Database Table**: `task_sidequest_limits`
```sql
CREATE TABLE task_sidequest_limits (
    task_id TEXT PRIMARY KEY,
    active_sidequests_count INTEGER DEFAULT 0,
    max_allowed_sidequests INTEGER DEFAULT 3,
    warning_threshold INTEGER DEFAULT 2,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Automatic Triggers**: Database triggers maintain accurate active sidequest counts
**Limit Checking**: Check limits before creating new sidequests
**User Options**: Present clear options when limits exceeded

#### Context Preservation During Sidequests

**Sidequest Creation Process**:
1. **Save complete parent task context** to `task_queue.context_snapshot`
2. **Update subtask_sidequest_relationships** for coordination tracking
3. **Switch AI focus completely to sidequest** with preserved context
4. **Notify user** of context switch and expected resumption

**Sidequest Completion Process**:  
1. **Archive sidequest** to completed status in database
2. **Update parent task** if sidequest changes requirements
3. **Restore exact parent task context** from preserved snapshot
4. **Resume parent task** from exact pause point with full context
5. **Notify user** of successful context restoration

### Progress Tracking System

#### Real-Time Progress Updates
**Requirement**: Progress updates immediately after EVERY work completion unit

**Granularity Levels**:
- **Subtask-level progress** - Percentage completion for each subtask
- **Task progress calculation** - Rollup from subtask completion percentages  
- **Milestone integration** - Task completion updates milestone progress
- **Completion path updates** - Overall project progress tracking

#### Status Transition Management
**Valid Transitions**:
```
pending → in-progress → completed
pending → blocked → in-progress → completed  
in-progress → blocked → in-progress → completed
```

**Automatic Database Triggers**:
- Update timestamps on all status changes
- Maintain dependent record consistency
- Trigger event logging and analytics
- Update rollup calculations and summaries

## Theme-Flow Intelligence System

### Database Tables for Theme-Flow Optimization

#### `theme_flows` Table
**Purpose**: Many-to-many theme-flow relationships with relevance ordering
**Critical Fields**:
- `theme_name` - Reference to theme file
- `flow_id` - Flow identifier
- `flow_file` - Flow file name (authentication-flow.json, etc.)
- `relevance_order` - Ordering for selective loading (1=most relevant)

**Optimization**: Enables fast theme-based context loading queries

#### `flow_status` Table
**Purpose**: Flow completion tracking and milestone integration
**Critical Fields**:
- `flow_id` - Unique flow identifier
- `flow_file` - Flow file name
- `status` - Flow completion status
- `completion_percentage` - Flow progress calculation
- `primary_themes` - JSON array of associated themes

**Milestone Integration**: Flow progress contributes to milestone completion validation

### Context Optimization Capabilities

#### Fast Database Lookup Functions
- **`get_themes_for_flow(flow_id)`** - Find all themes associated with a flow
- **`get_flows_for_theme(theme_name)`** - Get relevant flows for theme-based context loading
- **`sync_theme_flows()`** - Synchronize file definitions with database relationships

#### Selective Loading Intelligence
**Principle**: AI loads only relevant flow files based on task themes and database relationships

**Implementation Process**:
1. **Query theme_flows table** for task's primary and related themes
2. **Load only flow files** with high relevance_order for current themes
3. **Expand to additional flows** only when context escalation needed
4. **Cache loaded flows** to avoid redundant loading

**Memory Optimization**: Prevents loading all flow files, focuses on task-relevant flows for better performance

### Performance Query Views
**Pre-computed Database Views**:
- **`theme_flow_summary`** - Aggregated theme-flow statistics
- **`flow_theme_summary`** - Flow association overview  
- **`active_sidequests_by_task`** - Real-time sidequest counts for limit management
- **`session_activity_summary`** - Session productivity analytics

## Event Analytics System

### Real-Time Event Logging

#### `noteworthy_events` Table
**Purpose**: Real-time event logging for fast queries and pattern analysis
**Critical Fields**:
- `event_id` - Unique event identifier (event-YYYY-MM-DD-HHMMSS format)
- `event_type` - Category (decision, pivot, issue, milestone, completion)
- `primary_theme` - Theme associated with event
- `task_id` - Related task if applicable
- `session_id` - Session when event occurred
- `impact_level` - Severity (low, medium, high, critical)
- `decision_data` - JSON object with reasoning and context

**Real-Time Logging**: Current events stored in database for immediate querying and analysis

#### `event_relationships` Table
**Purpose**: Track cascading decisions and event dependencies
**Critical Fields**:
- `parent_event_id` - Reference to causing event
- `child_event_id` - Reference to resulting event
- `relationship_type` - Relationship (causes, blocks, enables, relates_to)

**Analytics**: Enables pattern recognition and decision impact analysis

### Hybrid Logging Architecture

#### Current Events (Database Storage)
**Storage**: `noteworthy_events` table in database
**Benefits**:
- Fast queries by theme, task, session
- Real-time pattern analysis and correlation
- Immediate event relationship tracking
- Session activity correlation

**Archival Trigger**: When database events exceed `noteworthySizeLimit` (default: 1MB)

#### Archived Events (File Storage)  
**Storage**: `noteworthy-archived-YYYY-MM-DD.json` files
**Benefits**:
- Long-term historical analysis
- Reduced database size and improved performance
- Human-readable format for manual review
- Version control compatibility

**Retention**: Configurable retention policy for archived files (default: 90 days)

### Analytics Capabilities

#### Pattern Recognition
- **Context escalation patterns** - By theme and task type
- **User correction and feedback patterns** - Learning from user input
- **Decision outcome tracking** - Success rates and effectiveness
- **Session productivity analysis** - Workflow efficiency metrics

#### Real-Time Insights
- **Active event impact assessment** - Current event correlation
- **Theme-based decision clustering** - Pattern recognition by theme
- **Session activity correlation** - Productivity pattern analysis
- **Performance bottleneck identification** - System optimization opportunities

## Performance Optimization

### Database Design for Performance

#### Strategic Indexes
```sql
-- Critical performance indexes
CREATE INDEX idx_theme_flows_theme ON theme_flows(theme_name);
CREATE INDEX idx_task_status_status ON task_status(status);  
CREATE INDEX idx_task_status_milestone ON task_status(milestone_id);
CREATE INDEX idx_session_context_session ON session_context(session_id);
CREATE INDEX idx_noteworthy_events_theme ON noteworthy_events(primary_theme);
```

#### Performance Views
- **Session restoration views** - Pre-aggregated session context data
- **Theme-flow relationship views** - Optimized theme context loading
- **Progress tracking views** - Efficient milestone progress calculation
- **Analytics summary views** - Common analytics patterns pre-computed

#### Automatic Database Triggers
- **Timestamp maintenance** - Automatic update timestamps on modifications
- **Count maintenance** - Sidequest count tracking for limit enforcement
- **Cache updates** - Theme-flow relationship cache synchronization

### Query Optimization Strategies

#### Session Boot Optimization
- **Single complex query** - Retrieve complete session context in one operation
- **Indexed lookups** - All session queries use optimized indexes
- **Cached relationships** - Pre-computed theme-flow relationships

#### Theme Loading Optimization  
- **Optimized joins** - Efficient theme-flow-task relationship queries
- **Selective loading** - Load only relevant themes and flows
- **Context caching** - Cache loaded context to avoid redundant queries

### Scalability Features

#### Large Project Support
- **Handles 20+ themes efficiently** - Optimized theme management
- **50+ flows with cross-references** - Fast flow relationship queries
- **100+ tasks with complex dependencies** - Efficient task coordination
- **Multiple concurrent sessions** - Isolated context management

#### Cross-Platform Compatibility
- **SQLite foundation** - Works on Windows, Mac, Linux without modification
- **No server dependencies** - Embedded database with project files
- **Portable database files** - Easy backup and migration
- **Version compatibility** - Database schema evolution support

## Data Integrity and Validation

### Consistency Checks
**Automated Validation**:
- Task milestone references must exist in `completion-path.json`
- Theme references must exist in `Themes/` directory
- Flow references must exist in `ProjectFlow/` directory and `flow-index.json`
- Database records must synchronize with organizational files

### Recovery Procedures
**Multi-Level Recovery**:
- **Database corruption recovery** - Rebuild from organizational files
- **File corruption recovery** - Restore from database records
- **Session context recovery** - Multiple snapshot sources for resilience
- **Consistency repair utilities** - Automated repair for data mismatches

## Implementation Requirements

### MCP Server Integration
**Required Components**:
- **Database initialization** - Automatic setup during project creation
- **Connection management** - Thread-safe connection pooling
- **Transaction management** - Atomic operations for data consistency
- **Error handling** - Graceful recovery from database errors

### Tool Integration Requirements  
**All MCP Tools Must**:
- Use database for real-time status tracking
- Update database context during operations
- Trigger database synchronization after file operations
- Query database for intelligent insights and recommendations

### Configuration Support
**Configurable Parameters**:
- Database file location and naming
- Synchronization behavior and retry policies  
- Performance tuning parameters and cache sizes
- Archival and retention policies for historical data

This database integration system ensures optimal performance while preserving the human-readable nature of the AI Project Manager's organizational approach, enabling seamless session continuity and intelligent project insights.