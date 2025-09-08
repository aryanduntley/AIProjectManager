# AI Project Manager - Directive Recursion Fix Implementation Plan

**Status**: ✅ MODULARIZATION COMPLETE - Ready for Recursion Fix Implementation  
**Created**: 2025-09-07  
**Updated**: 2025-09-07 (Post-Modularization)  
**Target Completion**: 5-6 days (reduced due to completed modularization)  
**Priority**: CRITICAL - System non-functional  

## Executive Summary

Implementing universal pause/resume architecture to fix infinite recursion loops in DirectiveProcessor that prevent all project initialization and management functionality.

**✅ PREREQUISITE COMPLETED**: DirectiveProcessor has been successfully modularized into 6 focused modules with all critical functionality (238+ lines) extracted and preserved. The system now has a solid foundation for implementing the recursion fixes.

## Core Problem Summary

- **Current Issue**: Infinite recursion loop: ProjectInitialization → DirectiveProcessor → ActionExecutor → ProjectTools → ProjectInitialization
- **Impact**: Complete system failure - no projects can be created or managed
- **Root Cause**: Synchronous AI consultation treated as immediate code execution
- **Solution**: Universal pause/resume pattern with database-first state management

---

## Phase 1: Universal State Machine (Days 1-4)

### Day 1: Database-First Skeleton Infrastructure ⏳

#### Core Skeleton Creation System
- [ ] **1.1** Create `_ensure_skeleton_structure_exists()` method
  - [ ] Handle configurable `managementFolderName` from config.json
  - [ ] Create complete directory structure (ProjectBlueprint, Themes, Tasks, etc.)
  - [ ] Generate skeleton files with "AI consultation pending" indicators
  - [ ] Idempotent operation (safe to call multiple times)

- [ ] **1.2** Implement Database-First State Management
  - [ ] Add `directive_states` table to database schema
  - [ ] Create atomic token generation and storage
  - [ ] Implement state persistence in `{managementFolder}/Database/project.db`
  - [ ] Handle database initialization during skeleton creation

- [ ] **1.3** Update DirectiveProcessor Architecture **✅ FOUNDATION READY**
  - [ ] Replace `execute_directive()` with skeleton-first approach *(modular structure ready)*
  - [ ] Always create management structure BEFORE generating tokens *(SkeletonManager ready)*
  - [ ] Add database-backed state tracking *(StateManager ready)*
  - [ ] Implement proper separation of immediate tasks vs AI consultation *(ConsultationManager ready)*

#### Success Criteria Day 1
- [ ] Can create complete project structure without recursion
- [ ] Database exists with `directive_states` table
- [ ] Resume tokens can be generated and stored
- [ ] Skeleton files indicate AI consultation pending

### Day 2: AI Consultation Session Management ⏳

#### AI Session Infrastructure
- [ ] **2.1** Create `AIConsultationSession` class **✅ MODULE READY**
  - [ ] Support consultation types: blueprint, themes, tasks, implementation, database *(ConsultationManager skeleton ready)*
  - [ ] Session lifecycle management (start, progress, completion)
  - [ ] Proper timeout and error handling

- [ ] **2.2** Implement Consultation Type Mapping
  - [ ] Define AI task sequences for each directive type
  - [ ] Add estimated duration calculations
  - [ ] Create progress tracking and user notification system

- [ ] **2.3** Add Session Persistence
  - [ ] Save consultation state across system restarts
  - [ ] Handle interrupted consultations gracefully
  - [ ] Implement resume from any checkpoint

#### Success Criteria Day 2
- [ ] AI consultations can be started and tracked
- [ ] Consultation state persists across system restarts
- [ ] Clear user notifications about consultation progress

### Day 3: Fix Action Execution Circular Loop ⏳

#### Break the Recursion Chain
- [ ] **3.1** Split ProjectInitializationOperations
  - [ ] `initialize_project()` - High-level orchestration (calls DirectiveProcessor)
  - [ ] `_create_project_structure()` - Low-level creation (NO DirectiveProcessor calls)
  - [ ] Clear separation of concerns

- [ ] **3.2** Fix ActionExecutor Blueprint Creation
  - [ ] Change `create_project_blueprint` to call `_create_project_structure()`
  - [ ] Remove circular call to `initialize_project()`
  - [ ] Ensure actions don't trigger directive recursion

- [ ] **3.3** Database Manager Integration
  - [ ] Verify ActionExecutors receive proper database manager reference
  - [ ] Add debug logging for database manager availability
  - [ ] Fix "No database manager available" errors

#### Success Criteria Day 3
- [ ] No recursive calls between actions and initialization
- [ ] ActionExecutors can access database manager
- [ ] Blueprint creation works without recursion

### Day 4: Update All Directive Types ⏳

#### Apply Universal Pattern to All Directives
- [ ] **4.1** Project Initialization Directives
  - [ ] Immediate: Directory creation, basic setup
  - [ ] AI Consultation: Blueprint creation, user discussion
  - [ ] Resume: Apply blueprint, finalize structure

- [ ] **4.2** Theme Management Directives
  - [ ] Immediate: Theme directory setup
  - [ ] AI Consultation: Pattern analysis, theme discovery
  - [ ] Resume: Apply discovered themes

- [ ] **4.3** Task Management Directives
  - [ ] Immediate: Task database setup
  - [ ] AI Consultation: Task planning, workflow creation
  - [ ] Resume: Create tasks with AI structure

- [ ] **4.4** Implementation Planning Directives
  - [ ] Immediate: Planning directory creation
  - [ ] AI Consultation: Architecture analysis
  - [ ] Resume: Generate implementation plans

- [ ] **4.5** Database Operation Directives
  - [ ] Immediate: Schema setup, validation
  - [ ] AI Consultation: Optimization analysis
  - [ ] Resume: Apply optimizations

#### Success Criteria Day 4
- [ ] ALL directive types support pause/resume
- [ ] No circular calls possible in any directive
- [ ] Consistent user experience across all directive types

---

## Phase 2: Testing and Validation (Days 5-6)

### Day 5: Comprehensive Directive Testing ⏳

#### Functionality Testing
- [ ] **5.1** Test Each Directive Type
  - [ ] Project initialization with pause/resume
  - [ ] Theme management with consultation pause
  - [ ] Task management with planning pause
  - [ ] Implementation planning with analysis pause
  - [ ] Database operations with optimization pause

- [ ] **5.2** Test Interrupted Scenarios
  - [ ] System restart during AI consultation
  - [ ] User cancellation of consultations
  - [ ] Resume with partial consultation results
  - [ ] Multiple concurrent consultations

- [ ] **5.3** Validate State Persistence
  - [ ] All directive states survive system restarts
  - [ ] Token-based resume works for all types
  - [ ] State cleanup after completion

#### Success Criteria Day 5
- [ ] All directive types work without recursion
- [ ] State persistence works across system restarts
- [ ] Resume functionality works for all directive types

### Day 6: User Experience and Error Handling ⏳

#### User Flow Testing
- [ ] **6.1** User Experience Validation
  - [ ] Clear messaging for pause/resume cycles
  - [ ] Progress indicators during consultations
  - [ ] Completion notifications and next steps

- [ ] **6.2** Error Handling for All Directive Types
  - [ ] Failed AI consultations (timeout, error, cancellation)
  - [ ] Invalid resume tokens
  - [ ] Corrupted state files
  - [ ] System resource issues

- [ ] **6.3** Performance Validation
  - [ ] State file size management
  - [ ] Resume time optimization (target: <2 seconds)
  - [ ] Memory usage during long consultations

#### Success Criteria Day 6
- [ ] User experience is clear and consistent
- [ ] All error scenarios handled gracefully
- [ ] Performance meets requirements

---

## Phase 3: Finalization (Day 7)

### Day 7: Documentation and Cleanup ⏳

#### Documentation Updates
- [ ] **7.1** Update All Directive Documentation
  - [ ] Document pause/resume behavior for each type
  - [ ] User guide for AI consultation workflows
  - [ ] Developer guide for adding new directive types

- [ ] **7.2** Code Cleanup
  - [ ] Remove ALL old recursive call patterns
  - [ ] Remove unused event queue architecture
  - [ ] Clean up debug logging and temporary files

- [ ] **7.3** Final Validation
  - [ ] End-to-end testing of complete workflows
  - [ ] User acceptance testing for all directive types
  - [ ] Performance benchmarking

#### Success Criteria Day 7
- [ ] Documentation complete and accurate
- [ ] Code clean and maintainable
- [ ] System ready for production use

---

## Commands and Tools Implementation

### New Commands to Implement
- [ ] **Universal Resume**: `run-aimp-resume <token>` - Works for ALL directive types
- [ ] **Consultation Status**: `run-aimp-status <token>` - Check consultation progress
- [ ] **General Status**: `run-aimp-status` - Show all pending operations

### Modified Commands
- [ ] `run-aimp-init` - Returns resume token when AI consultation needed
- [ ] `run-aimp-themes` - Pause/resume pattern for theme discovery
- [ ] `run-aimp-tasks` - Pause/resume pattern for task planning

---

## Technical Implementation Details

### Database Schema Addition
```sql
CREATE TABLE IF NOT EXISTS directive_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    directive_type TEXT NOT NULL,
    project_path TEXT NOT NULL,
    management_folder TEXT NOT NULL,
    status TEXT NOT NULL,
    phase TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    consultation_id TEXT,
    context_data TEXT,
    ai_results TEXT,
    skeleton_created BOOLEAN DEFAULT FALSE,
    consultation_complete BOOLEAN DEFAULT FALSE
);
```

### Key Files to Modify
- [x] ✅ **COMPLETED** `ai-pm-mcp/core/directive_processor.py` - Modularized with 6 focused modules
- [x] ✅ **COMPLETED** `ai-pm-mcp/core/directive_modules/` - New modular architecture created
  - [x] ActionDeterminer (238 lines extracted) 
  - [x] EscalationEngine (120 lines extracted)
  - [x] Decorators (60 lines extracted)
  - [ ] SkeletonManager (ready for implementation)
  - [ ] ConsultationManager (ready for implementation) 
  - [ ] StateManager (ready for implementation)
- [ ] `ai-pm-mcp/tools/project/initialization_operations.py` - Split initialization logic
- [ ] `ai-pm-mcp/core/action_executors/project_actions.py` - Fix circular calls
- [ ] `ai-pm-mcp/database/schema.sql` - Add directive_states table
- [ ] `ai-pm-mcp/tools/run_command_processor.py` - Add new resume commands
- [ ] **CLEANUP**: Remove legacy code from OLD_directive_processor.py patterns

---

## Success Criteria

### Before Fix (Current State)
- ❌ `run-aimp-init` causes infinite recursion
- ❌ No projectManagement/ folder created
- ❌ Database initialization fails
- ❌ System non-functional for primary purpose

### After Fix (Target State)
- ✅ ALL directive types work without recursion
- ✅ Universal pause/resume for AI consultations
- ✅ Database-first state management with configurable folder names
- ✅ Complete project management functionality
- ✅ Enterprise-ready reliability and scalability

---

## Risk Mitigation

### Implementation Risks
- **Low Risk**: Targeting specific, identified issues with clear solutions
- **Rollback Available**: Can revert to pre-architectural-fix state if needed
- **Isolated Changes**: Fixes don't affect other system components significantly

### Testing Strategy
- **Essential**: Complete initialization workflow end-to-end testing
- **Critical**: Verify no new recursion sources introduced
- **Important**: Confirm database operations work correctly

---

## Progress Tracking

**Overall Progress**: 15% Complete (Modularization Foundation Complete)

**✅ MODULARIZATION PHASE**: DirectiveProcessor Architecture Prepared
- [x] ✅ **COMPLETED**: Modular architecture with 6 focused modules
- [x] ✅ **COMPLETED**: 418+ lines of critical logic extracted and preserved
- [x] ✅ **COMPLETED**: Full backward compatibility maintained
- [x] ✅ **COMPLETED**: Skeleton modules ready for recursion fix implementation

**🚀 REMAINING PHASES**:
- [ ] Phase 1 Complete (Days 1-4): Universal State Machine *(foundation ready)*
- [ ] Phase 2 Complete (Days 5-6): Testing and Validation  
- [ ] Phase 3 Complete (Day 7): Documentation and Cleanup

**Next Action**: Begin Day 1 - Database-First Skeleton Infrastructure *(using prepared SkeletonManager)*

## 📝 **IMPORTANT CLEANUP NOTES**

### Legacy Code Removal Tasks
- [ ] **Remove event queue legacy code** from DirectiveProcessor after pause/resume implemented
- [ ] **Clean up OLD_directive_processor.py references** in any remaining code
- [ ] **Remove placeholder fallback decorators** after new architecture verified
- [ ] **Deprecate unused import patterns** from old monolithic structure
- [ ] **Archive or remove docs/oldFiles/core/OLD_directive_processor.py** after successful deployment

---

*This implementation plan will be updated daily with progress, blockers, and completion status.*