-- AI Project Manager Database Schema (Enhanced)
-- Hybrid approach: Keep decision files (projectlogic.jsonl, blueprint.md) as files
-- Migrate operational/state data to database for better performance and queries

-- ============================================================================
-- SESSION MANAGEMENT & PERSISTENCE
-- ============================================================================

-- Enhanced Session Management
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_mode TEXT DEFAULT 'theme-focused',
    active_themes TEXT DEFAULT '[]', -- JSON array of theme names
    active_tasks TEXT DEFAULT '[]',  -- JSON array of task IDs
    active_sidequests TEXT DEFAULT '[]', -- JSON array of sidequest IDs
    project_path TEXT,
    status TEXT DEFAULT 'active', -- active, paused, completed, terminated
    metadata TEXT DEFAULT '{}', -- JSON: user preferences, session config
    notes TEXT
);

CREATE TABLE IF NOT EXISTS session_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    loaded_themes TEXT, -- comma-separated theme names
    loaded_flows TEXT, -- comma-separated flow file names
    context_escalations INTEGER DEFAULT 0,
    files_accessed TEXT DEFAULT '[]', -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- ============================================================================
-- TASK & SIDEQUEST STATUS TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_status (
    task_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending', -- pending, in-progress, blocked, completed, cancelled
    priority TEXT DEFAULT 'medium', -- high, medium, low
    milestone_id TEXT,
    implementation_plan_id TEXT,
    primary_theme TEXT,
    related_themes TEXT DEFAULT '[]', -- JSON array
    progress_percentage INTEGER DEFAULT 0,
    estimated_effort TEXT,
    actual_effort TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    assigned_to TEXT DEFAULT 'ai-agent',
    review_required BOOLEAN DEFAULT false,
    acceptance_criteria TEXT DEFAULT '[]', -- JSON array
    testing_requirements TEXT DEFAULT '{}' -- JSON object
);

-- Critical addition: Sidequest management with parent-child relationships
CREATE TABLE IF NOT EXISTS sidequest_status (
    sidequest_id TEXT PRIMARY KEY,
    parent_task_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    scope_description TEXT,
    reason TEXT,
    urgency TEXT DEFAULT 'medium',
    impact_on_parent TEXT DEFAULT 'minimal', -- minimal, moderate, significant
    primary_theme TEXT,
    related_themes TEXT DEFAULT '[]', -- JSON array
    progress_percentage INTEGER DEFAULT 0,
    estimated_effort TEXT,
    actual_effort TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    completion_trigger TEXT DEFAULT '{}', -- JSON: completion criteria
    notes TEXT DEFAULT '[]', -- JSON array
    FOREIGN KEY (parent_task_id) REFERENCES task_status(task_id)
);

-- Subtasks for both tasks and sidequests
CREATE TABLE IF NOT EXISTS subtask_status (
    subtask_id TEXT PRIMARY KEY,
    parent_id TEXT NOT NULL, -- either task_id or sidequest_id
    parent_type TEXT NOT NULL, -- 'task' or 'sidequest'
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    context_mode TEXT DEFAULT 'theme-focused',
    flow_references TEXT DEFAULT '[]', -- JSON: flowId, flowFile, steps
    files TEXT DEFAULT '[]', -- JSON array
    dependencies TEXT DEFAULT '[]', -- JSON array
    blockers TEXT DEFAULT '[]', -- JSON array
    progress_percentage INTEGER DEFAULT 0,
    estimated_effort TEXT,
    actual_effort TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    notes TEXT
);

-- ============================================================================
-- MULTI-TASK & SIDEQUEST ORDERING (Critical for Workflow Management)
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    sidequest_id TEXT NULL, -- NULL for main tasks, populated for sidequests
    queue_position INTEGER,
    status TEXT DEFAULT 'queued', -- queued, active, paused, completed
    context_snapshot TEXT DEFAULT '{}', -- JSON: Save context when pausing for sidequest
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activated_at TIMESTAMP NULL,
    paused_at TIMESTAMP NULL, -- When main task paused for sidequest
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (task_id) REFERENCES task_status(task_id),
    FOREIGN KEY (sidequest_id) REFERENCES sidequest_status(sidequest_id),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- ============================================================================
-- SUBTASK-SIDEQUEST RELATIONSHIP TRACKING (Multiple Sidequests Support)
-- ============================================================================

CREATE TABLE IF NOT EXISTS subtask_sidequest_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subtask_id TEXT NOT NULL,
    sidequest_id TEXT NOT NULL,
    relationship_type TEXT DEFAULT 'spawned_from', -- spawned_from, blocks, supports
    impact_level TEXT DEFAULT 'minimal', -- minimal, moderate, significant
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    notes TEXT,
    FOREIGN KEY (subtask_id) REFERENCES subtask_status(subtask_id),
    FOREIGN KEY (sidequest_id) REFERENCES sidequest_status(sidequest_id),
    UNIQUE(subtask_id, sidequest_id) -- Prevent duplicate relationships
);

-- Active sidequests count tracking for limit enforcement
CREATE TABLE IF NOT EXISTS task_sidequest_limits (
    task_id TEXT PRIMARY KEY,
    active_sidequests_count INTEGER DEFAULT 0,
    max_allowed_sidequests INTEGER DEFAULT 3,
    warning_threshold INTEGER DEFAULT 2, -- Warn when approaching limit
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task_status(task_id)
);

-- ============================================================================
-- ENHANCED FLOW & THEME RELATIONSHIP TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS flow_status (
    flow_id TEXT PRIMARY KEY,
    flow_file TEXT NOT NULL, -- authentication-flow.json, payment-flow.json, etc
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, in-progress, complete, needs-review, blocked
    completion_percentage INTEGER DEFAULT 0,
    primary_themes TEXT DEFAULT '[]', -- JSON array
    secondary_themes TEXT DEFAULT '[]', -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS flow_step_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id TEXT NOT NULL,
    step_id TEXT NOT NULL, -- URF-001, ULF-002, etc
    step_number INTEGER,
    description TEXT,
    status TEXT DEFAULT 'pending',
    dependencies TEXT DEFAULT '[]', -- JSON: step_ids this depends on
    completed_at TIMESTAMP NULL,
    files_referenced TEXT DEFAULT '[]', -- JSON array
    implementation_status TEXT DEFAULT 'pending', -- pending, exists, needs-design
    FOREIGN KEY (flow_id) REFERENCES flow_status(flow_id)
);

-- Theme-Flow Relationships Table (Enhanced)
CREATE TABLE IF NOT EXISTS theme_flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme_name TEXT NOT NULL,
    flow_id TEXT NOT NULL,
    flow_file TEXT NOT NULL,
    relevance_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(theme_name, flow_id)
);

-- Note: sessions table defined above in SESSION MANAGEMENT section

-- File Modification Tracking
CREATE TABLE IF NOT EXISTS file_modifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL, -- 'theme', 'flow', 'task', 'blueprint', etc.
    operation TEXT NOT NULL, -- 'create', 'update', 'delete'
    session_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT, -- JSON with additional context
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Task Completion Metrics
CREATE TABLE IF NOT EXISTS task_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    milestone_id TEXT,
    theme_name TEXT,
    estimated_effort_hours REAL,
    actual_effort_hours REAL,
    completed_at TIMESTAMP,
    session_id TEXT,
    complexity_score INTEGER, -- 1-10 scale
    notes TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- User Preferences and Learning
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preference_key TEXT UNIQUE NOT NULL,
    preference_value TEXT NOT NULL,
    context TEXT, -- When/where this preference was learned
    confidence_score REAL DEFAULT 0.5, -- 0-1 scale
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- NOTEWORTHY EVENTS & DECISION TRACKING
-- ============================================================================

-- Current noteworthy events (replaced noteworthy.json for fast queries)
CREATE TABLE IF NOT EXISTS noteworthy_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL, -- event-YYYY-MM-DD-HHMMSS format
    event_type TEXT NOT NULL, -- decision, pivot, issue, milestone, completion
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    primary_theme TEXT,
    related_themes TEXT DEFAULT '[]', -- JSON array
    task_id TEXT, -- Related task if applicable
    session_id TEXT, -- Session when event occurred
    impact_level TEXT DEFAULT 'medium', -- low, medium, high, critical
    decision_data TEXT DEFAULT '{}', -- JSON: reasoning, options, choice
    context_data TEXT DEFAULT '{}', -- JSON: session context, active themes
    user_feedback TEXT, -- User input or approval
    ai_reasoning TEXT, -- AI's reasoning for the decision
    outcome TEXT, -- Result or consequences if known
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived_at TIMESTAMP NULL, -- When moved to archived files
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Event relationships for tracking cascading decisions
CREATE TABLE IF NOT EXISTS event_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_event_id TEXT NOT NULL,
    child_event_id TEXT NOT NULL,
    relationship_type TEXT DEFAULT 'causes', -- causes, blocks, enables, relates_to
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_event_id) REFERENCES noteworthy_events(event_id),
    FOREIGN KEY (child_event_id) REFERENCES noteworthy_events(event_id)
);

-- Theme Evolution Tracking
CREATE TABLE IF NOT EXISTS theme_evolution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme_name TEXT NOT NULL,
    change_type TEXT NOT NULL, -- 'created', 'modified', 'deleted', 'files_added', 'files_removed'
    change_details TEXT, -- JSON with specific changes
    session_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_theme_flows_theme ON theme_flows(theme_name);
CREATE INDEX IF NOT EXISTS idx_theme_flows_flow ON theme_flows(flow_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX IF NOT EXISTS idx_file_modifications_path ON file_modifications(file_path);
CREATE INDEX IF NOT EXISTS idx_file_modifications_timestamp ON file_modifications(timestamp);
CREATE INDEX IF NOT EXISTS idx_task_metrics_task_id ON task_metrics(task_id);
CREATE INDEX IF NOT EXISTS idx_task_metrics_theme ON task_metrics(theme_name);
CREATE INDEX IF NOT EXISTS idx_theme_evolution_theme ON theme_evolution(theme_name);
CREATE INDEX IF NOT EXISTS idx_theme_evolution_timestamp ON theme_evolution(timestamp);

-- Enhanced indexes for multiple sidequests
CREATE INDEX IF NOT EXISTS idx_task_status_status ON task_status(status);
CREATE INDEX IF NOT EXISTS idx_task_status_milestone ON task_status(milestone_id);
CREATE INDEX IF NOT EXISTS idx_sidequest_status_parent ON sidequest_status(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_sidequest_status_status ON sidequest_status(status);
CREATE INDEX IF NOT EXISTS idx_subtask_status_parent ON subtask_status(parent_id, parent_type);
CREATE INDEX IF NOT EXISTS idx_subtask_sidequest_rel_subtask ON subtask_sidequest_relationships(subtask_id);
CREATE INDEX IF NOT EXISTS idx_subtask_sidequest_rel_sidequest ON subtask_sidequest_relationships(sidequest_id);
CREATE INDEX IF NOT EXISTS idx_task_queue_task ON task_queue(task_id);
CREATE INDEX IF NOT EXISTS idx_task_queue_session ON task_queue(session_id);
CREATE INDEX IF NOT EXISTS idx_task_sidequest_limits_task ON task_sidequest_limits(task_id);

-- Noteworthy events indexes
CREATE INDEX IF NOT EXISTS idx_noteworthy_events_type ON noteworthy_events(event_type);
CREATE INDEX IF NOT EXISTS idx_noteworthy_events_theme ON noteworthy_events(primary_theme);
CREATE INDEX IF NOT EXISTS idx_noteworthy_events_task ON noteworthy_events(task_id);
CREATE INDEX IF NOT EXISTS idx_noteworthy_events_session ON noteworthy_events(session_id);
CREATE INDEX IF NOT EXISTS idx_noteworthy_events_created ON noteworthy_events(created_at);
CREATE INDEX IF NOT EXISTS idx_noteworthy_events_impact ON noteworthy_events(impact_level);
CREATE INDEX IF NOT EXISTS idx_event_relationships_parent ON event_relationships(parent_event_id);
CREATE INDEX IF NOT EXISTS idx_event_relationships_child ON event_relationships(child_event_id);

-- Views for Common Queries
CREATE VIEW IF NOT EXISTS theme_flow_summary AS
SELECT 
    theme_name,
    COUNT(*) as flow_count,
    GROUP_CONCAT(flow_id ORDER BY relevance_order) as flows,
    MIN(created_at) as first_flow_added,
    MAX(updated_at) as last_updated
FROM theme_flows 
GROUP BY theme_name;

CREATE VIEW IF NOT EXISTS flow_theme_summary AS
SELECT 
    flow_id,
    flow_file,
    COUNT(*) as theme_count,
    GROUP_CONCAT(theme_name) as themes,
    MIN(created_at) as first_theme_added,
    MAX(updated_at) as last_updated
FROM theme_flows 
GROUP BY flow_id;

CREATE VIEW IF NOT EXISTS session_activity_summary AS
SELECT 
    session_id,
    start_time,
    last_activity,
    ROUND((julianday(last_activity) - julianday(start_time)) * 24, 2) as duration_hours,
    context,
    active_themes,
    active_tasks
FROM sessions
ORDER BY start_time DESC;

-- Multiple Sidequest Views for Enhanced Query Capabilities
CREATE VIEW IF NOT EXISTS active_sidequests_by_task AS
SELECT 
    parent_task_id,
    COUNT(*) as active_sidequests_count,
    GROUP_CONCAT(sidequest_id) as active_sidequest_ids,
    GROUP_CONCAT(title) as active_sidequest_titles,
    AVG(progress_percentage) as avg_progress
FROM sidequest_status 
WHERE status IN ('pending', 'in-progress')
GROUP BY parent_task_id;

CREATE VIEW IF NOT EXISTS subtask_sidequest_summary AS
SELECT 
    ssr.subtask_id,
    st.title as subtask_title,
    COUNT(ssr.sidequest_id) as related_sidequests_count,
    GROUP_CONCAT(ss.sidequest_id) as sidequest_ids,
    GROUP_CONCAT(ss.title) as sidequest_titles,
    GROUP_CONCAT(ssr.relationship_type) as relationship_types,
    GROUP_CONCAT(ssr.impact_level) as impact_levels
FROM subtask_sidequest_relationships ssr
JOIN subtask_status st ON ssr.subtask_id = st.subtask_id
JOIN sidequest_status ss ON ssr.sidequest_id = ss.sidequest_id
GROUP BY ssr.subtask_id;

CREATE VIEW IF NOT EXISTS sidequest_limit_status AS
SELECT 
    tsl.task_id,
    ts.title as task_title,
    tsl.active_sidequests_count,
    tsl.max_allowed_sidequests,
    tsl.warning_threshold,
    CASE 
        WHEN tsl.active_sidequests_count >= tsl.max_allowed_sidequests THEN 'at_limit'
        WHEN tsl.active_sidequests_count >= tsl.warning_threshold THEN 'approaching_limit'
        ELSE 'normal'
    END as limit_status,
    (tsl.max_allowed_sidequests - tsl.active_sidequests_count) as remaining_capacity
FROM task_sidequest_limits tsl
JOIN task_status ts ON tsl.task_id = ts.task_id;

-- Noteworthy Events Views
CREATE VIEW IF NOT EXISTS recent_events AS
SELECT 
    event_id,
    event_type,
    title,
    description,
    primary_theme,
    impact_level,
    created_at,
    CASE 
        WHEN archived_at IS NOT NULL THEN 'archived'
        ELSE 'active'
    END as status
FROM noteworthy_events
WHERE archived_at IS NULL
ORDER BY created_at DESC;

CREATE VIEW IF NOT EXISTS event_impact_summary AS
SELECT 
    event_type,
    impact_level,
    COUNT(*) as event_count,
    COUNT(CASE WHEN archived_at IS NULL THEN 1 END) as active_count,
    AVG(CASE WHEN outcome IS NOT NULL THEN 1.0 ELSE 0.0 END) as resolution_rate
FROM noteworthy_events
GROUP BY event_type, impact_level
ORDER BY 
    CASE impact_level 
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    event_count DESC;

CREATE VIEW IF NOT EXISTS theme_event_activity AS
SELECT 
    primary_theme,
    COUNT(*) as total_events,
    COUNT(CASE WHEN event_type = 'decision' THEN 1 END) as decisions,
    COUNT(CASE WHEN event_type = 'issue' THEN 1 END) as issues,
    COUNT(CASE WHEN impact_level IN ('high', 'critical') THEN 1 END) as high_impact_events,
    MAX(created_at) as last_activity
FROM noteworthy_events
WHERE primary_theme IS NOT NULL
GROUP BY primary_theme
ORDER BY total_events DESC;

-- Triggers for Automatic Updates
CREATE TRIGGER IF NOT EXISTS update_theme_flows_timestamp
    AFTER UPDATE ON theme_flows
    FOR EACH ROW
BEGIN
    UPDATE theme_flows SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_sessions_activity
    AFTER UPDATE ON sessions
    FOR EACH ROW
BEGIN
    UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_user_preferences_timestamp
    AFTER UPDATE ON user_preferences
    FOR EACH ROW
BEGIN
    UPDATE user_preferences SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Multiple Sidequest Management Triggers
CREATE TRIGGER IF NOT EXISTS sidequest_created_update_limits
    AFTER INSERT ON sidequest_status
    FOR EACH ROW
    WHEN NEW.status IN ('pending', 'in-progress')
BEGIN
    INSERT OR REPLACE INTO task_sidequest_limits (task_id, active_sidequests_count, last_updated)
    VALUES (
        NEW.parent_task_id, 
        COALESCE(
            (SELECT active_sidequests_count FROM task_sidequest_limits WHERE task_id = NEW.parent_task_id), 
            0
        ) + 1,
        CURRENT_TIMESTAMP
    );
END;

CREATE TRIGGER IF NOT EXISTS sidequest_completed_update_limits
    AFTER UPDATE ON sidequest_status
    FOR EACH ROW
    WHEN OLD.status IN ('pending', 'in-progress') AND NEW.status = 'completed'
BEGIN
    UPDATE task_sidequest_limits 
    SET 
        active_sidequests_count = GREATEST(active_sidequests_count - 1, 0),
        last_updated = CURRENT_TIMESTAMP
    WHERE task_id = NEW.parent_task_id;
END;

CREATE TRIGGER IF NOT EXISTS update_task_status_timestamps
    AFTER UPDATE ON task_status
    FOR EACH ROW
BEGIN
    UPDATE task_status SET last_updated = CURRENT_TIMESTAMP WHERE task_id = NEW.task_id;
END;

CREATE TRIGGER IF NOT EXISTS update_sidequest_status_timestamps
    AFTER UPDATE ON sidequest_status
    FOR EACH ROW
BEGIN
    UPDATE sidequest_status SET last_updated = CURRENT_TIMESTAMP WHERE sidequest_id = NEW.sidequest_id;
END;

CREATE TRIGGER IF NOT EXISTS update_subtask_status_timestamps
    AFTER UPDATE ON subtask_status
    FOR EACH ROW
BEGIN
    UPDATE subtask_status SET last_updated = CURRENT_TIMESTAMP WHERE subtask_id = NEW.subtask_id;
END;