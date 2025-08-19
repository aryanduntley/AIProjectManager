"""
Scope and context loading engine for the AI Project Manager MCP Server.

Handles intelligent context loading based on themes, README guidance, context modes,
compressed context management, and database-driven optimization for optimal AI session continuity.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import os

# Database integration
from ..database.theme_flow_queries import ThemeFlowQueries
from ..database.session_queries import SessionQueries
from ..database.file_metadata_queries import FileMetadataQueries
from ..utils.project_paths import get_project_management_path, get_themes_path, get_flows_path

# Import modular components
from .scope_engine.compressed_context import CompressedContextManager, ContextMode, ContextResult
from .scope_engine.context_loading import ContextLoading
from .scope_engine.database_loading import DatabaseLoading
from .scope_engine.flow_intelligence import FlowIntelligence
from .scope_engine.multi_flow_optimization import MultiFlowOptimization

logger = logging.getLogger(__name__)


class ScopeEngine:
    """
    Enhanced scope and context engine with database-driven optimization and intelligent context loading.
    """
    
    def __init__(self, mcp_server_path: Optional[Path] = None, 
                 theme_flow_queries: Optional[ThemeFlowQueries] = None,
                 session_queries: Optional[SessionQueries] = None, 
                 file_metadata_queries: Optional[FileMetadataQueries] = None,
                 config_manager=None):
        # Initialize compressed context manager
        self.compressed_context_manager = CompressedContextManager(mcp_server_path)
        
        # Database connections for optimization
        self.theme_flow_queries = theme_flow_queries
        self.session_queries = session_queries
        self.file_metadata_queries = file_metadata_queries
        self.config_manager = config_manager
        
        # Initialize modular components
        self._context_loading = ContextLoading(self)
        self._database_loading = DatabaseLoading(self)
        self._flow_intelligence = FlowIntelligence(self)
        self._multi_flow_optimization = MultiFlowOptimization(self)

    # ============================================================================
    # CORE CONTEXT MANAGEMENT - Delegates to ContextLoading
    # ============================================================================
    
    async def ensure_core_context_loaded(self):
        """Ensure core context is loaded from compressed files"""
        return await self._context_loading.ensure_core_context_loaded()
    
    async def get_session_boot_context(self, project_path: Path) -> Dict[str, Any]:
        """Get comprehensive context for session boot"""
        return await self._context_loading.get_session_boot_context(project_path)
    
    async def get_situational_context(self, project_path: Path, situation: str) -> Dict[str, Any]:
        """Get context optimized for specific situation"""
        return await self._context_loading.get_situational_context(project_path, situation)
    
    async def load_context(self, project_path: Path, primary_theme: str, 
                          context_mode: ContextMode = ContextMode.THEME_FOCUSED,
                          force_mode: bool = False) -> ContextResult:
        """Load context with intelligent mode determination and file optimization"""
        return await self._context_loading.load_context(project_path, primary_theme, context_mode, force_mode)
    
    async def _load_theme(self, themes_dir: Path, theme_name: str) -> Optional[Dict[str, Any]]:
        """Load theme data from file"""
        return await self._context_loading._load_theme(themes_dir, theme_name)
    
    async def _determine_context_mode(self, themes_dir: Path, primary_theme_data: Dict[str, Any],
                                    requested_mode: ContextMode, force_mode: bool = False) -> ContextMode:
        """Determine optimal context mode based on theme complexity"""
        return await self._context_loading._determine_context_mode(themes_dir, primary_theme_data, requested_mode, force_mode)
    
    async def _load_context_by_mode(self, project_path: Path, themes_dir: Path, 
                                  primary_theme: str, primary_theme_data: Dict[str, Any],
                                  mode: ContextMode) -> ContextResult:
        """Load context based on determined mode"""
        return await self._context_loading._load_context_by_mode(project_path, themes_dir, primary_theme, primary_theme_data, mode)
    
    async def _get_global_paths(self, project_path: Path) -> List[str]:
        """Get global paths that should always be included"""
        return await self._context_loading._get_global_paths(project_path)
    
    async def _load_readmes(self, project_path: Path, paths: List[str]) -> Dict[str, str]:
        """Load README files from specified paths"""
        return await self._context_loading._load_readmes(project_path, paths)

    # ============================================================================
    # DATABASE OPTIMIZATION - Delegates to DatabaseLoading
    # ============================================================================
    
    async def _load_database_metadata(self, project_path: Path, paths: List[str]) -> Dict[str, str]:
        """Load database metadata for paths"""
        return await self._database_loading._load_database_metadata(project_path, paths)
    
    async def load_context_with_database_optimization(self, project_path: Path, primary_theme: str,
                                                    task_id: Optional[str] = None,
                                                    session_id: Optional[str] = None) -> ContextResult:
        """Load context with database optimization"""
        return await self._database_loading.load_context_with_database_optimization(project_path, primary_theme, task_id, session_id)
    
    async def _track_context_usage(self, session_id: str, context: ContextResult, task_id: Optional[str]):
        """Track context usage for optimization"""
        return await self._database_loading._track_context_usage(session_id, context, task_id)
    
    def _determine_required_mode_for_task(self, task_id: str, current_context: ContextResult) -> ContextMode:
        """Determine required context mode for specific task"""
        return self._database_loading._determine_required_mode_for_task(task_id, current_context)
    
    async def _enhance_context_with_file_intelligence(self, project_path: Path, context: ContextResult):
        """Enhance context with file intelligence from database"""
        return await self._database_loading._enhance_context_with_file_intelligence(project_path, context)

    # ============================================================================
    # FLOW INTELLIGENCE - Delegates to FlowIntelligence
    # ============================================================================
    
    async def _enhance_context_with_flows(self, context: ContextResult, primary_theme: str):
        """Enhance context with relevant flows"""
        return await self._flow_intelligence._enhance_context_with_flows(context, primary_theme)
    
    async def get_optimized_flow_context(self, project_path: Path, flow_ids: List[str],
                                       include_dependencies: bool = True,
                                       max_depth: int = 2) -> Dict[str, Any]:
        """Get optimized context for specific flows"""
        return await self._flow_intelligence.get_optimized_flow_context(project_path, flow_ids, include_dependencies, max_depth)
    
    async def get_intelligent_context_recommendations(self, project_path: Path, 
                                                    current_theme: str,
                                                    task_description: Optional[str] = None,
                                                    session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get intelligent context recommendations"""
        return await self._flow_intelligence.get_intelligent_context_recommendations(project_path, current_theme, task_description, session_id)
    
    async def load_selective_flows_for_context(self, project_path: Path, 
                                             primary_theme: str,
                                             max_flows: int = 3,
                                             intelligence_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Load selective flows for context optimization"""
        return await self._flow_intelligence.load_selective_flows_for_context(project_path, primary_theme, max_flows, intelligence_threshold)
    
    async def get_context_with_selective_flows(self, project_path: Path, 
                                             primary_theme: str,
                                             task_themes: Optional[List[str]] = None,
                                             max_flows: int = 3,
                                             session_id: Optional[str] = None) -> ContextResult:
        """Get context enhanced with selective flows"""
        return await self._flow_intelligence.get_context_with_selective_flows(project_path, primary_theme, task_themes, max_flows, session_id)
    
    async def _select_flows_with_database_intelligence(self, task_themes: List[str],
                                                     session_id: Optional[str] = None,
                                                     max_flows: int = 3) -> List[str]:
        """Select flows using database intelligence"""
        return await self._flow_intelligence._select_flows_with_database_intelligence(task_themes, session_id, max_flows)

    # ============================================================================
    # MULTI-FLOW OPTIMIZATION - Delegates to MultiFlowOptimization
    # ============================================================================
    
    async def _analyze_cross_flow_dependencies_for_context(self, flow_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze cross-flow dependencies for context loading"""
        return await self._multi_flow_optimization._analyze_cross_flow_dependencies_for_context(flow_ids)
    
    async def optimize_multi_flow_context_loading(self, project_path: Path,
                                                primary_flow_ids: List[str],
                                                dependency_depth: int = 2,
                                                max_total_files: int = 100) -> Dict[str, Any]:
        """Optimize context loading for multiple flows"""
        return await self._multi_flow_optimization.optimize_multi_flow_context_loading(project_path, primary_flow_ids, dependency_depth, max_total_files)
    
    async def _generate_dependency_aware_loading_order(self, flow_ids: List[str],
                                                     dependencies: List[Dict[str, Any]]) -> List[str]:
        """Generate dependency-aware loading order for flows"""
        return await self._multi_flow_optimization._generate_dependency_aware_loading_order(flow_ids, dependencies)

    # ============================================================================
    # UTILITY METHODS - Delegates to MultiFlowOptimization (shared utilities)
    # ============================================================================
    
    async def _estimate_memory_usage(self, context: ContextResult) -> int:
        """Estimate memory usage for context"""
        return await self._multi_flow_optimization._estimate_memory_usage(context)
    
    async def _generate_recommendations(self, context: ContextResult, 
                                      theme_files: Dict[str, Dict[str, Any]],
                                      project_path: Path) -> List[str]:
        """Generate context recommendations"""
        return await self._multi_flow_optimization._generate_recommendations(context, theme_files, project_path)
    
    async def assess_context_escalation(self, current_context: ContextResult, 
                                      task_description: str,
                                      session_patterns: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Assess if context escalation is needed"""
        return await self._multi_flow_optimization.assess_context_escalation(current_context, task_description, session_patterns)
    
    async def get_context_summary(self, context: ContextResult) -> str:
        """Get formatted context summary"""
        return await self._multi_flow_optimization.get_context_summary(context)
    
    async def filter_files_by_relevance(self, context: ContextResult, 
                                      task_description: str,
                                      max_files: Optional[int] = None) -> ContextResult:
        """Filter files by relevance to task"""
        return await self._multi_flow_optimization.filter_files_by_relevance(context, task_description, max_files)
    
    async def validate_context_integrity(self, project_path: Path, context: ContextResult) -> Dict[str, Any]:
        """Validate context integrity"""
        return await self._multi_flow_optimization.validate_context_integrity(project_path, context)
    
    async def get_compressed_directive(self, directive_key: str) -> Optional[Dict[str, Any]]:
        """Get compressed directive data"""
        return await self._multi_flow_optimization.get_compressed_directive(directive_key)
    
    async def _calculate_coverage_score(self, context: ContextResult) -> float:
        """Calculate context coverage score"""
        return await self._multi_flow_optimization._calculate_coverage_score(context)

    # ============================================================================
    # COMPRESSED CONTEXT MANAGER ACCESS - Delegates to CompressedContextManager
    # ============================================================================
    
    async def load_core_context(self) -> Dict[str, Any]:
        """Load compressed core context files"""
        return await self.compressed_context_manager.load_core_context()
    
    def get_workflow_for_scenario(self, scenario: str) -> Optional[Dict[str, Any]]:
        """Get workflow definition for a specific scenario"""
        return self.compressed_context_manager.get_workflow_for_scenario(scenario)
    
    def get_directive_summary(self, directive_key: str) -> Optional[Dict[str, Any]]:
        """Get compressed directive information"""
        return self.compressed_context_manager.get_directive_summary(directive_key)
    
    def get_validation_rules(self, validation_type: str) -> Optional[Dict[str, Any]]:
        """Get validation rules for specific validation type"""
        return self.compressed_context_manager.get_validation_rules(validation_type)
    
    def get_session_boot_sequence(self) -> List[str]:
        """Get the session boot sequence steps"""
        return self.compressed_context_manager.get_session_boot_sequence()
    
    def get_core_rules(self) -> List[str]:
        """Get critical rules for AI behavior"""
        return self.compressed_context_manager.get_core_rules()
    
    def should_escalate_context(self, issue_description: str) -> Tuple[bool, str]:
        """Determine if context escalation is needed based on issue"""
        return self.compressed_context_manager.should_escalate_context(issue_description)
    
    def _directive_id_to_compressed_key(self, directive_id: str) -> str:
        """Convert numbered directive ID to compressed directive key"""
        return self.compressed_context_manager._directive_id_to_compressed_key(directive_id)
    
    def _has_implementation_note(self, obj: Any) -> bool:
        """Recursively search for implementationNote in a nested object"""
        return self.compressed_context_manager._has_implementation_note(obj)
    
    def get_directive_escalation_level(self, directive_id: str, operation_context: str = "") -> str:
        """Determine appropriate directive escalation level"""
        return self.compressed_context_manager.get_directive_escalation_level(directive_id, operation_context)
    
    def should_escalate_to_markdown(self, directive_id: str, json_context_insufficient: bool = False, 
                                   error_context: str = "") -> bool:
        """Determine if should escalate from JSON to Markdown directives"""
        return self.compressed_context_manager.should_escalate_to_markdown(directive_id, json_context_insufficient, error_context)
    
    async def load_directive_with_escalation(self, directive_id: str, operation_context: str = "", 
                                           force_level: Optional[str] = None) -> Dict[str, Any]:
        """Load directive with appropriate escalation level"""
        return await self.compressed_context_manager.load_directive_with_escalation(directive_id, operation_context, force_level)
    
    async def generate_situational_context(self, project_path: Path, situation: str) -> Dict[str, Any]:
        """Generate context specific to current project situation"""
        return await self.compressed_context_manager.generate_situational_context(project_path, situation)
    
    async def _analyze_project_state(self, project_path: Path) -> Dict[str, Any]:
        """Analyze current project state for context generation"""
        return await self.compressed_context_manager._analyze_project_state(project_path)