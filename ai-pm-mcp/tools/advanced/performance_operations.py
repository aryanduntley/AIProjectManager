"""
Performance optimization operations for the AI Project Manager.

Handles performance optimization and recommendations for large projects.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ...core.performance_optimizer import LargeProjectOptimizer
from ...database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class PerformanceOperations:
    """Performance optimization operations."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None, server_instance=None):
        self.db_manager = db_manager
        self.server_instance = server_instance

    async def optimize_performance(self, arguments: Dict[str, Any]) -> str:
        """Run comprehensive performance optimization."""
        try:
            project_path = Path(arguments["project_path"])
            optimization_level = arguments.get("optimization_level", "comprehensive")
            
            if not self.db_manager:
                return "Database not available. Performance optimization requires database connection."
            
            # Initialize performance optimizer
            optimizer = LargeProjectOptimizer(project_path, self.db_manager)
            
            # Run optimization based on level
            if optimization_level == "basic":
                # Basic database optimization only
                result = optimizer.db_optimizer.optimize_database()
            elif optimization_level == "comprehensive":
                # Full large project optimization
                result = optimizer.optimize_for_large_project()
            elif optimization_level == "aggressive":
                # Comprehensive optimization plus additional tuning
                result = optimizer.optimize_for_large_project()
                if result.get("optimizations_applied"):
                    # Additional aggressive optimizations
                    index_result = optimizer.db_optimizer.create_performance_indexes()
                    result["additional_indexes"] = index_result
            
            if result.get("optimizations_applied"):
                # Add directive hook for server notification
                if self.server_instance and hasattr(self.server_instance, 'on_advanced_operation_complete'):
                    hook_context = {
                        "trigger": "performance_optimization_complete",
                        "operation_type": "performance_optimization",
                        "project_path": str(project_path),
                        "optimization_level": optimization_level,
                        "optimizations_applied": result.get("optimizations_applied", []),
                        "is_large_project": optimizer.is_large_project(),
                        "timestamp": datetime.now().isoformat()
                    }
                    try:
                        await self.server_instance.on_advanced_operation_complete(hook_context, "systemInitialization")
                    except Exception as e:
                        logger.warning(f"Performance optimization hook failed: {e}")
                
                response = f"""🚀 Performance Optimization Complete!

Optimization Level: {optimization_level.upper()}
Large Project: {'Yes' if optimizer.is_large_project() else 'No'}

Optimizations Applied:
"""
                
                for optimization in result.get("optimizations_applied", []):
                    response += f"• {optimization.replace('_', ' ').title()}\n"
                
                if "performance_improvements" in result:
                    improvements = result["performance_improvements"]
                    
                    if "database" in improvements:
                        db_info = improvements["database"]["optimization_results"]
                        response += f"""
Database Optimization:
• Database Size: {db_info.get('database_size', 0):,} bytes
• Indexes: {db_info.get('indexes_count', 0)} active indexes
• Operations: VACUUM, ANALYZE, OPTIMIZE completed
"""
                    
                    if "indexes" in improvements:
                        idx_info = improvements["indexes"]
                        response += f"""
Performance Indexes:
• Created {idx_info.get('total_indexes', 0)} new performance indexes
"""
                    
                    if "cache" in improvements:
                        cache_info = improvements["cache"]
                        response += f"""
Cache Optimization:
• Cache Size: {cache_info.get('cache_size', 0)}
• TTL: {cache_info.get('ttl_seconds', 0)} seconds
• Utilization: {cache_info.get('current_utilization', 0):.1%}
"""
                
                return response
            else:
                return f"❌ Performance optimization failed: {result.get('error', 'Unknown error')}"
            
        except Exception as e:
            logger.error(f"Error optimizing performance: {e}")
            return f"Error optimizing performance: {str(e)}"

    async def get_performance_recommendations(self, arguments: Dict[str, Any]) -> str:
        """Get performance optimization recommendations."""
        try:
            project_path = Path(arguments["project_path"])
            
            if not self.db_manager:
                return "Database not available. Performance analysis requires database connection."
            
            optimizer = LargeProjectOptimizer(project_path, self.db_manager)
            recommendations_result = optimizer.get_optimization_recommendations()
            
            if recommendations_result["success"]:
                recommendations = recommendations_result["recommendations"]
                metrics = recommendations_result["project_metrics"]
                
                response = f"""📊 Performance Analysis Report

Project Metrics:
• Large Project: {'Yes' if metrics.get('is_large_project', False) else 'No'}
• Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.2%}
• Last Optimization: {metrics.get('last_optimization', 'Never')[:19]}

"""
                
                if recommendations:
                    response += "🎯 Recommendations:\n\n"
                    for i, rec in enumerate(recommendations, 1):
                        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "⚪")
                        response += f"{priority_icon} **{rec['type'].replace('_', ' ').title()}** ({rec['priority']} priority)\n"
                        response += f"   {rec['description']}\n"
                        response += f"   Action: {rec['action']}\n\n"
                else:
                    response += "✅ No performance recommendations - system is optimally configured!"
                
                return response
            else:
                return f"❌ Performance analysis failed: {recommendations_result.get('error', 'Unknown error')}"
            
        except Exception as e:
            logger.error(f"Error getting performance recommendations: {e}")
            return f"Error getting performance recommendations: {str(e)}"