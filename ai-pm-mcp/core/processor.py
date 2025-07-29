"""
Task interpreter and processor for the AI Project Manager MCP Server.

Handles task lifecycle management, context resolution, execution coordination,
and intelligent workflow management with database-driven optimization.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio

# Database integration
from database.task_status_queries import TaskStatusQueries
from database.session_queries import SessionQueries
from database.theme_flow_queries import ThemeFlowQueries
from database.file_metadata_queries import FileMetadataQueries

# Core components
from core.scope_engine import ScopeEngine, ContextMode, ContextResult

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProcessingResult(Enum):
    """Task processing result types."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    REQUIRES_ESCALATION = "requires_escalation"
    REQUIRES_SIDEQUEST = "requires_sidequest"


@dataclass
class TaskExecutionContext:
    """Context for task execution."""
    task_id: str
    session_id: str
    primary_theme: str
    context_mode: ContextMode
    loaded_context: Optional[ContextResult]
    implementation_plan_id: Optional[str]
    milestone_id: Optional[str]
    dependencies: List[str]
    blockers: List[str]
    estimated_effort: Optional[str]
    priority: TaskPriority


@dataclass  
class ProcessingOutput:
    """Result of task processing."""
    result: ProcessingResult
    task_id: str
    session_id: str
    output_data: Dict[str, Any]
    context_used: Optional[ContextResult]
    recommendations: List[str]
    next_actions: List[str]
    errors: List[str]
    warnings: List[str]
    execution_time_ms: int


class TaskProcessor:
    """Main task interpreter and processor with database optimization."""
    
    def __init__(self, 
                 scope_engine: ScopeEngine,
                 task_queries: Optional[TaskStatusQueries] = None,
                 session_queries: Optional[SessionQueries] = None,
                 theme_flow_queries: Optional[ThemeFlowQueries] = None,
                 file_metadata_queries: Optional[FileMetadataQueries] = None):
        """Initialize with scope engine and database components."""
        self.scope_engine = scope_engine
        self.task_queries = task_queries
        self.session_queries = session_queries
        self.theme_flow_queries = theme_flow_queries
        self.file_metadata_queries = file_metadata_queries
        
        # Processing configuration
        self.max_processing_time_ms = 300000  # 5 minutes
        self.max_sidequest_depth = 3
        self.auto_context_escalation = True
        
    async def process_task(self, project_path: Path, task_data: Dict[str, Any], 
                          session_id: str) -> ProcessingOutput:
        """Process a task with intelligent context loading and execution coordination."""
        start_time = datetime.utcnow()
        
        try:
            # Create execution context
            exec_context = await self._create_execution_context(task_data, session_id)
            
            # Load appropriate context
            context_result = await self._load_task_context(project_path, exec_context)
            exec_context.loaded_context = context_result
            
            # Execute task processing
            processing_result = await self._execute_task_processing(
                project_path, exec_context, task_data
            )
            
            # Update database state
            if self.task_queries:
                await self._update_task_status(exec_context, processing_result)
            
            # Calculate execution time
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return ProcessingOutput(
                result=processing_result["result"],
                task_id=exec_context.task_id,
                session_id=session_id,
                output_data=processing_result.get("output", {}),
                context_used=context_result,
                recommendations=processing_result.get("recommendations", []),
                next_actions=processing_result.get("next_actions", []),
                errors=processing_result.get("errors", []),
                warnings=processing_result.get("warnings", []),
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return ProcessingOutput(
                result=ProcessingResult.FAILED,
                task_id=task_data.get("taskId", "unknown"),
                session_id=session_id,
                output_data={},
                context_used=None,
                recommendations=[],
                next_actions=[],
                errors=[str(e)],
                warnings=[],
                execution_time_ms=execution_time
            )
    
    async def _create_execution_context(self, task_data: Dict[str, Any], 
                                      session_id: str) -> TaskExecutionContext:
        """Create execution context from task data."""
        return TaskExecutionContext(
            task_id=task_data.get("taskId", f"task-{datetime.utcnow().isoformat()}"),
            session_id=session_id,
            primary_theme=task_data.get("primaryTheme", "general"),
            context_mode=ContextMode(task_data.get("contextMode", "theme-focused")),
            loaded_context=None,
            implementation_plan_id=task_data.get("implementationPlanId"),
            milestone_id=task_data.get("milestoneId"),
            dependencies=task_data.get("dependencies", []),
            blockers=task_data.get("blockers", []),
            estimated_effort=task_data.get("estimatedEffort"),
            priority=TaskPriority(task_data.get("priority", "medium"))
        )
    
    async def _load_task_context(self, project_path: Path, 
                               exec_context: TaskExecutionContext) -> ContextResult:
        """Load appropriate context for task execution."""
        try:
            # Use database-optimized context loading if available
            if hasattr(self.scope_engine, 'load_context_with_database_optimization'):
                context = await self.scope_engine.load_context_with_database_optimization(
                    project_path=project_path,
                    primary_theme=exec_context.primary_theme,
                    context_mode=exec_context.context_mode,
                    task_id=exec_context.task_id,
                    session_id=exec_context.session_id
                )
            else:
                # Fallback to regular context loading
                context = await self.scope_engine.load_context(
                    project_path=project_path,
                    primary_theme=exec_context.primary_theme,
                    context_mode=exec_context.context_mode
                )
            
            return context
            
        except Exception as e:
            logger.error(f"Error loading task context: {e}")
            raise
    
    async def _execute_task_processing(self, project_path: Path, 
                                     exec_context: TaskExecutionContext,
                                     task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual task processing logic."""
        processing_result = {
            "result": ProcessingResult.SUCCESS,
            "output": {},
            "recommendations": [],
            "next_actions": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            # Analyze task requirements
            task_analysis = await self._analyze_task_requirements(task_data, exec_context)
            processing_result["output"]["task_analysis"] = task_analysis
            
            # Check for context adequacy
            context_check = await self._check_context_adequacy(exec_context, task_data)
            if not context_check["adequate"]:
                if self.auto_context_escalation:
                    # Attempt context escalation
                    escalation_result = await self._escalate_context(
                        project_path, exec_context, context_check["reason"]
                    )
                    processing_result["recommendations"].extend(escalation_result["recommendations"])
                    
                    if escalation_result["success"]:
                        exec_context.loaded_context = escalation_result["new_context"]
                    else:
                        processing_result["result"] = ProcessingResult.REQUIRES_ESCALATION
                        processing_result["warnings"].append("Context escalation failed")
                else:
                    processing_result["result"] = ProcessingResult.REQUIRES_ESCALATION
                    processing_result["recommendations"].append(
                        f"Consider escalating context: {context_check['reason']}"
                    )
            
            # Execute subtasks if present
            subtasks = task_data.get("subtasks", [])
            if subtasks:
                subtask_results = await self._process_subtasks(
                    project_path, exec_context, subtasks
                )
                processing_result["output"]["subtask_results"] = subtask_results
                
                # Check if any subtasks require sidequests
                sidequest_needs = [
                    result for result in subtask_results 
                    if result.get("requires_sidequest")
                ]
                
                if sidequest_needs:
                    processing_result["result"] = ProcessingResult.REQUIRES_SIDEQUEST
                    processing_result["output"]["sidequest_requirements"] = sidequest_needs
            
            # Generate intelligent recommendations
            if exec_context.loaded_context:
                intelligent_recs = await self.scope_engine.get_intelligent_context_recommendations(
                    project_path=project_path,
                    current_context=exec_context.loaded_context,
                    task_description=task_data.get("description", ""),
                    session_id=exec_context.session_id
                )
                processing_result["recommendations"].extend(
                    intelligent_recs.get("escalation_recommendations", [])
                )
            
            # Determine next actions based on task status
            next_actions = await self._determine_next_actions(exec_context, task_data)
            processing_result["next_actions"] = next_actions
            
        except Exception as e:
            processing_result["result"] = ProcessingResult.FAILED
            processing_result["errors"].append(str(e))
            logger.error(f"Error in task processing execution: {e}")
        
        return processing_result
    
    async def _analyze_task_requirements(self, task_data: Dict[str, Any], 
                                       exec_context: TaskExecutionContext) -> Dict[str, Any]:
        """Analyze task requirements and complexity."""
        analysis = {
            "complexity_score": 0,
            "required_themes": [exec_context.primary_theme],
            "estimated_context_mode": exec_context.context_mode.value,
            "dependency_analysis": {},
            "risk_factors": []
        }
        
        try:
            # Analyze description for complexity indicators
            description = task_data.get("description", "")
            complexity_keywords = [
                "integrate", "refactor", "migrate", "architecture", "design",
                "implementation", "system", "database", "API", "authentication"
            ]
            
            complexity_score = sum(1 for keyword in complexity_keywords 
                                 if keyword.lower() in description.lower())
            analysis["complexity_score"] = min(complexity_score / len(complexity_keywords), 1.0)
            
            # Analyze dependencies
            dependencies = exec_context.dependencies
            if dependencies:
                analysis["dependency_analysis"] = {
                    "count": len(dependencies),
                    "dependencies": dependencies,
                    "risk_level": "high" if len(dependencies) > 3 else "medium" if len(dependencies) > 1 else "low"
                }
            
            # Check for risk factors
            if exec_context.blockers:
                analysis["risk_factors"].append(f"Has {len(exec_context.blockers)} blockers")
            
            if exec_context.priority == TaskPriority.CRITICAL:
                analysis["risk_factors"].append("Critical priority task")
            
            if analysis["complexity_score"] > 0.7:
                analysis["risk_factors"].append("High complexity score")
                analysis["estimated_context_mode"] = ContextMode.PROJECT_WIDE.value
            elif analysis["complexity_score"] > 0.4:
                analysis["estimated_context_mode"] = ContextMode.THEME_EXPANDED.value
            
            # Analyze related themes if database available
            if self.theme_flow_queries:
                related_themes = await self.theme_flow_queries.get_themes_for_flow(
                    task_data.get("flowReferences", [{}])[0].get("flowId", "")
                )
                if related_themes:
                    theme_names = [t['theme_name'] for t in related_themes]
                    analysis["required_themes"].extend(theme_names)
                    analysis["required_themes"] = list(set(analysis["required_themes"]))
            
        except Exception as e:
            logger.debug(f"Error in task requirements analysis: {e}")
        
        return analysis
    
    async def _check_context_adequacy(self, exec_context: TaskExecutionContext, 
                                    task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if current context is adequate for task execution."""
        if not exec_context.loaded_context:
            return {"adequate": False, "reason": "No context loaded"}
        
        context = exec_context.loaded_context
        
        # Check basic adequacy criteria
        adequacy_checks = {
            "theme_coverage": len(context.loaded_themes) > 0,
            "file_availability": len(context.files) > 0,
            "readme_guidance": len(context.readmes) > 0,
            "memory_reasonable": context.memory_estimate < 150  # MB
        }
        
        # Check for cross-theme references in task
        task_description = task_data.get("description", "").lower()
        cross_theme_indicators = ["integration", "shared", "cross", "between", "connect"]
        has_cross_theme_needs = any(indicator in task_description for indicator in cross_theme_indicators)
        
        if has_cross_theme_needs and context.mode == ContextMode.THEME_FOCUSED:
            return {
                "adequate": False, 
                "reason": "Task appears to require cross-theme context but using theme-focused mode"
            }
        
        # Check if all adequacy criteria are met
        failed_checks = [check for check, passed in adequacy_checks.items() if not passed]
        
        if failed_checks:
            return {
                "adequate": False,
                "reason": f"Context inadequate: {', '.join(failed_checks)}"
            }
        
        return {"adequate": True, "reason": "Context appears adequate"}
    
    async def _escalate_context(self, project_path: Path, exec_context: TaskExecutionContext,
                              reason: str) -> Dict[str, Any]:
        """Attempt to escalate context for better task execution."""
        escalation_result = {
            "success": False,
            "new_context": None,
            "recommendations": []
        }
        
        try:
            current_mode = exec_context.context_mode
            
            # Determine escalation path
            if current_mode == ContextMode.THEME_FOCUSED:
                new_mode = ContextMode.THEME_EXPANDED
            elif current_mode == ContextMode.THEME_EXPANDED:
                new_mode = ContextMode.PROJECT_WIDE
            else:
                escalation_result["recommendations"].append("Already at maximum context level")
                return escalation_result
            
            # Load new context
            new_context = await self.scope_engine.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=exec_context.primary_theme,
                context_mode=new_mode,
                task_id=exec_context.task_id,
                session_id=exec_context.session_id
            )
            
            escalation_result["success"] = True
            escalation_result["new_context"] = new_context
            escalation_result["recommendations"].append(
                f"Context escalated from {current_mode.value} to {new_mode.value}: {reason}"
            )
            
            # Update execution context
            exec_context.context_mode = new_mode
            
            # Track escalation in database if available
            if self.session_queries:
                await self.session_queries.log_context_escalation(
                    session_id=exec_context.session_id,
                    from_mode=current_mode.value,
                    to_mode=new_mode.value,
                    reason=reason,
                    task_id=exec_context.task_id
                )
            
        except Exception as e:
            escalation_result["recommendations"].append(f"Context escalation failed: {str(e)}")
            logger.error(f"Error escalating context: {e}")
        
        return escalation_result
    
    async def _process_subtasks(self, project_path: Path, exec_context: TaskExecutionContext,
                              subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process subtasks and determine execution requirements."""
        subtask_results = []
        
        for subtask in subtasks:
            subtask_result = {
                "subtask_id": subtask.get("id", f"subtask-{len(subtask_results)}"),
                "title": subtask.get("title", "Untitled subtask"),
                "requires_sidequest": False,
                "context_requirements": {},
                "recommendations": []
            }
            
            try:
                # Analyze subtask complexity
                description = subtask.get("description", "")
                flow_refs = subtask.get("flowReferences", [])
                
                # Check if subtask might need sidequest based on flow references
                if flow_refs and self.theme_flow_queries:
                    for flow_ref in flow_refs:
                        flow_id = flow_ref.get("flowId")
                        if flow_id:
                            # Check if flow exists and is complete
                            flow_status = await self.theme_flow_queries.get_flow_status(flow_id)
                            if not flow_status or flow_status.get("completion_percentage", 0) < 50:
                                subtask_result["requires_sidequest"] = True
                                subtask_result["recommendations"].append(
                                    f"Flow {flow_id} incomplete - may require sidequest for implementation"
                                )
                
                # Analyze context requirements
                if "integration" in description.lower() or "api" in description.lower():
                    subtask_result["context_requirements"]["suggested_mode"] = ContextMode.THEME_EXPANDED.value
                
                if "database" in description.lower() or "migration" in description.lower():
                    subtask_result["context_requirements"]["suggested_mode"] = ContextMode.PROJECT_WIDE.value
                
            except Exception as e:
                subtask_result["recommendations"].append(f"Error analyzing subtask: {str(e)}")
                logger.debug(f"Error processing subtask {subtask_result['subtask_id']}: {e}")
            
            subtask_results.append(subtask_result)
        
        return subtask_results
    
    async def _determine_next_actions(self, exec_context: TaskExecutionContext,
                                    task_data: Dict[str, Any]) -> List[str]:
        """Determine next actions based on task execution context."""
        next_actions = []
        
        try:
            # Basic next actions based on task status
            current_status = task_data.get("status", "pending")
            
            if current_status == "pending":
                next_actions.append("Begin task execution with loaded context")
                
                if exec_context.dependencies:
                    next_actions.append("Verify all dependencies are satisfied")
            
            elif current_status == "in-progress":
                next_actions.append("Continue task execution")
                
                if exec_context.blockers:
                    next_actions.append("Address blockers before proceeding")
            
            elif current_status == "blocked":
                next_actions.append("Resolve blockers to continue")
                
                if exec_context.blockers:
                    for blocker in exec_context.blockers:
                        next_actions.append(f"Address blocker: {blocker}")
            
            # Context-based next actions
            if exec_context.loaded_context:
                if len(exec_context.loaded_context.recommendations) > 0:
                    next_actions.append("Review context recommendations for optimization")
                
                if exec_context.loaded_context.memory_estimate > 100:
                    next_actions.append("Consider context optimization due to high memory usage")
            
            # Database-driven next actions
            if self.task_queries:
                # Check for active sidequests
                active_sidequests = await self.task_queries.get_active_sidequests_for_task(exec_context.task_id)
                if active_sidequests:
                    next_actions.append(f"Monitor {len(active_sidequests)} active sidequests")
                
                # Check sidequest limits
                sidequest_status = await self.task_queries.get_sidequest_limit_status(exec_context.task_id)
                if sidequest_status and sidequest_status.get("limit_status") == "approaching_limit":
                    next_actions.append("Consider completing some sidequests before creating new ones")
            
            # Implementation plan integration
            if exec_context.implementation_plan_id:
                next_actions.append(f"Follow implementation plan: {exec_context.implementation_plan_id}")
        
        except Exception as e:
            next_actions.append(f"Error determining next actions: {str(e)}")
            logger.debug(f"Error in next actions determination: {e}")
        
        return next_actions
    
    async def _update_task_status(self, exec_context: TaskExecutionContext, 
                                processing_result: Dict[str, Any]):
        """Update task status in database."""
        if not self.task_queries:
            return
        
        try:
            # Update task progress
            progress_data = {
                "context_mode": exec_context.context_mode.value,
                "memory_usage": exec_context.loaded_context.memory_estimate if exec_context.loaded_context else 0,
                "themes_loaded": len(exec_context.loaded_context.loaded_themes) if exec_context.loaded_context else 0,
                "processing_result": processing_result["result"].value
            }
            
            await self.task_queries.update_task_progress(
                task_id=exec_context.task_id,
                progress_data=progress_data
            )
            
            # Log any errors or warnings
            if processing_result.get("errors"):
                for error in processing_result["errors"]:
                    await self.task_queries.log_task_error(exec_context.task_id, error)
            
            if processing_result.get("warnings"):
                for warning in processing_result["warnings"]:
                    await self.task_queries.log_task_warning(exec_context.task_id, warning)
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
    
    async def create_sidequest_from_processing(self, project_path: Path, 
                                             parent_task_id: str,
                                             sidequest_requirements: Dict[str, Any],
                                             session_id: str) -> Dict[str, Any]:
        """Create a sidequest based on processing requirements."""
        if not self.task_queries:
            return {"error": "Task queries not available for sidequest creation"}
        
        try:
            # Check sidequest limits
            limit_status = await self.task_queries.get_sidequest_limit_status(parent_task_id)
            if limit_status and limit_status.get("limit_status") == "at_limit":
                return {
                    "error": "Sidequest limit reached",
                    "limit_status": limit_status,
                    "recommendations": [
                        "Complete existing sidequests first",
                        "Consider modifying existing sidequest scope",
                        "Request temporary limit increase"
                    ]
                }
            
            # Create sidequest data structure
            sidequest_data = {
                "parent_task_id": parent_task_id,
                "title": sidequest_requirements.get("title", "Generated Sidequest"),
                "description": sidequest_requirements.get("description", "Auto-generated sidequest from task processing"),
                "scope_description": sidequest_requirements.get("scope", "Automated scope"),
                "reason": sidequest_requirements.get("reason", "Required for parent task completion"),
                "priority": sidequest_requirements.get("priority", "medium"),
                "urgency": sidequest_requirements.get("urgency", "medium"),
                "primary_theme": sidequest_requirements.get("theme", "general"),
                "estimated_effort": sidequest_requirements.get("effort", "medium")
            }
            
            # Create sidequest in database
            sidequest_id = await self.task_queries.create_sidequest(sidequest_data)
            
            # Create context for sidequest
            sidequest_context = await self.scope_engine.load_context_with_database_optimization(
                project_path=project_path,
                primary_theme=sidequest_data["primary_theme"],
                context_mode=ContextMode.THEME_FOCUSED,
                task_id=sidequest_id,
                session_id=session_id
            )
            
            return {
                "success": True,
                "sidequest_id": sidequest_id,
                "sidequest_data": sidequest_data,
                "context": {
                    "mode": sidequest_context.mode.value,
                    "themes": sidequest_context.loaded_themes,
                    "memory_estimate": sidequest_context.memory_estimate
                },
                "recommendations": [
                    f"Sidequest {sidequest_id} created successfully",
                    "Switch focus to sidequest for completion",
                    "Parent task context will be preserved"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating sidequest: {e}")
            return {"error": str(e)}
    
    async def get_processing_analytics(self, session_id: str, 
                                     time_range_hours: int = 24) -> Dict[str, Any]:
        """Get processing analytics for performance optimization."""
        analytics = {
            "session_summary": {},
            "context_usage": {},
            "task_performance": {},
            "error_patterns": {},
            "recommendations": []
        }
        
        try:
            if self.session_queries:
                # Get session analytics
                session_data = await self.session_queries.get_session_analytics(
                    session_id=session_id,
                    hours=time_range_hours
                )
                analytics["session_summary"] = session_data
                
                # Get context usage patterns
                context_patterns = await self.session_queries.get_context_usage_patterns(
                    session_id=session_id,
                    hours=time_range_hours
                )
                analytics["context_usage"] = context_patterns
            
            if self.task_queries:
                # Get task performance metrics
                task_performance = await self.task_queries.get_task_performance_metrics(
                    session_id=session_id,
                    hours=time_range_hours
                )
                analytics["task_performance"] = task_performance
                
                # Get error patterns
                error_patterns = await self.task_queries.get_error_patterns(
                    session_id=session_id,
                    hours=time_range_hours
                )
                analytics["error_patterns"] = error_patterns
            
            # Generate recommendations based on analytics
            recommendations = []
            
            # Context optimization recommendations
            if analytics["context_usage"].get("average_memory_mb", 0) > 80:
                recommendations.append("Consider using more focused context modes to reduce memory usage")
            
            # Performance recommendations
            avg_processing_time = analytics["task_performance"].get("average_processing_time_ms", 0)
            if avg_processing_time > 30000:  # 30 seconds
                recommendations.append("Task processing time is high - consider context optimization")
            
            # Error pattern recommendations
            common_errors = analytics["error_patterns"].get("most_common", [])
            if common_errors:
                recommendations.append(f"Address common error pattern: {common_errors[0]['error_type']}")
            
            analytics["recommendations"] = recommendations
            
        except Exception as e:
            analytics["error"] = f"Error generating analytics: {str(e)}"
            logger.error(f"Error in processing analytics: {e}")
        
        return analytics