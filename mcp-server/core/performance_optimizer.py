"""
Performance Optimizer for MCP Git Branch Management
Handles optimization for large projects with many branches and complex organizational structures
"""

import os
import sqlite3
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

from ..database.db_manager import DatabaseManager


class PerformanceMetrics:
    """Track performance metrics for optimization"""
    def __init__(self):
        self.operation_times = {}
        self.memory_usage = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.database_queries = 0
        self.file_operations = 0
    
    def record_operation(self, operation: str, duration: float):
        if operation not in self.operation_times:
            self.operation_times[operation] = []
        self.operation_times[operation].append(duration)
    
    def get_average_time(self, operation: str) -> float:
        times = self.operation_times.get(operation, [])
        return sum(times) / len(times) if times else 0.0
    
    def get_cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


class ContentCache:
    """Intelligent caching system for frequently accessed content"""
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.access_times = {}
        self.access_counts = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached content with intelligent eviction"""
        with self.lock:
            if key not in self.cache:
                return None
            
            # Check TTL
            if self._is_expired(key):
                del self.cache[key]
                del self.access_times[key]
                self.access_counts.pop(key, None)
                return None
            
            # Update access metrics
            self.access_times[key] = datetime.now()
            self.access_counts[key] = self.access_counts.get(key, 0) + 1
            
            return self.cache[key]
    
    def set(self, key: str, value: Any):
        """Set cached content with LRU+LFU eviction"""
        with self.lock:
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_least_valuable()
            
            self.cache[key] = value
            self.access_times[key] = datetime.now()
            self.access_counts[key] = self.access_counts.get(key, 0) + 1
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.access_times:
            return True
        return datetime.now() - self.access_times[key] > timedelta(seconds=self.ttl_seconds)
    
    def _evict_least_valuable(self):
        """Evict least valuable item using combined LRU+LFU algorithm"""
        if not self.cache:
            return
        
        # Calculate value score: recent access + frequency
        scores = {}
        now = datetime.now()
        for key in self.cache:
            time_score = 1.0 / (1 + (now - self.access_times[key]).total_seconds() / 3600)  # Higher for recent
            freq_score = self.access_counts.get(key, 0) / 10  # Normalize frequency
            scores[key] = time_score + freq_score
        
        # Remove lowest scoring item
        least_valuable = min(scores.keys(), key=lambda k: scores[k])
        del self.cache[least_valuable]
        del self.access_times[least_valuable]
        self.access_counts.pop(least_valuable, None)
    
    def clear(self):
        """Clear all cached content"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.access_counts.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "utilization": len(self.cache) / self.max_size,
                "total_accesses": sum(self.access_counts.values()),
                "unique_keys": len(self.access_counts),
                "avg_access_per_key": sum(self.access_counts.values()) / len(self.access_counts) if self.access_counts else 0
            }


class ParallelProcessor:
    """Parallel processing support for multiple branch operations"""
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def parallel_branch_operations(self, operations: List[Tuple[str, callable, tuple]]) -> Dict[str, Any]:
        """Execute branch operations in parallel"""
        futures = {}
        
        for op_id, func, args in operations:
            future = self.executor.submit(func, *args)
            futures[future] = op_id
        
        results = {}
        for future in as_completed(futures):
            op_id = futures[future]
            try:
                results[op_id] = {"success": True, "result": future.result()}
            except Exception as e:
                results[op_id] = {"success": False, "error": str(e)}
        
        return results
    
    def shutdown(self):
        """Shutdown the thread pool executor"""
        self.executor.shutdown(wait=True)


class DatabaseOptimizer:
    """Database optimization for large-scale operations"""
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.connection_pool = []
        self.pool_size = 5
        self.lock = threading.Lock()
    
    def optimize_database(self) -> Dict[str, Any]:
        """Run comprehensive database optimization"""
        try:
            cursor = self.db_manager.connection.cursor()
            optimization_results = {}
            
            # Analyze database size and performance
            cursor.execute("PRAGMA page_count;")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size;")
            page_size = cursor.fetchone()[0]
            
            db_size = page_count * page_size
            optimization_results["database_size"] = db_size
            
            # Run VACUUM to reclaim space
            cursor.execute("VACUUM;")
            optimization_results["vacuum_completed"] = True
            
            # Analyze table statistics
            cursor.execute("ANALYZE;")
            optimization_results["analyze_completed"] = True
            
            # Update statistics
            cursor.execute("PRAGMA optimize;")
            optimization_results["optimize_completed"] = True
            
            # Check index usage
            cursor.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='index' AND sql IS NOT NULL
            """)
            indexes = cursor.fetchall()
            optimization_results["indexes_count"] = len(indexes)
            
            # Get query plan statistics for key queries
            test_queries = [
                "SELECT * FROM git_branches WHERE status = 'active'",
                "SELECT * FROM git_project_state ORDER BY created_at DESC LIMIT 10"
            ]
            
            query_plans = {}
            for query in test_queries:
                try:
                    cursor.execute(f"EXPLAIN QUERY PLAN {query}")
                    plan = cursor.fetchall()
                    query_plans[query] = plan
                except Exception:
                    # Skip queries for tables that don't exist
                    continue
            
            optimization_results["query_plans"] = query_plans
            
            return {
                "success": True,
                "optimization_results": optimization_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Database optimization failed: {str(e)}"
            }
    
    def create_performance_indexes(self) -> Dict[str, Any]:
        """Create additional performance indexes for large-scale operations"""
        try:
            cursor = self.db_manager.connection.cursor()
            
            # Performance indexes for branch-based system
            performance_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_git_project_state_branch ON git_project_state(current_branch, current_git_hash)",
                "CREATE INDEX IF NOT EXISTS idx_git_branches_number ON git_branches(branch_number, status)"
            ]
            
            created_indexes = []
            for index_sql in performance_indexes:
                try:
                    cursor.execute(index_sql)
                    created_indexes.append(index_sql.split("idx_")[1].split(" ")[0])
                except Exception as e:
                    print(f"Warning: Could not create index: {e}")
            
            self.db_manager.connection.commit()
            
            return {
                "success": True,
                "created_indexes": created_indexes,
                "total_indexes": len(created_indexes)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Index creation failed: {str(e)}"
            }


class LargeProjectOptimizer:
    """Main optimizer for large project performance - adapted for Git branches"""
    def __init__(self, project_root: Path, db_manager: DatabaseManager):
        self.project_root = Path(project_root)
        self.db_manager = db_manager
        
        # Performance components
        self.metrics = PerformanceMetrics()
        self.cache = ContentCache()
        self.parallel_processor = ParallelProcessor()
        self.db_optimizer = DatabaseOptimizer(db_manager)
        
        # Configuration
        self.large_project_threshold = 50   # Number of branches (reduced from instances)
        self.optimization_interval = 3600   # 1 hour in seconds
        self.last_optimization = datetime.now()
    
    def is_large_project(self) -> bool:
        """Determine if this is a large project requiring optimization"""
        try:
            # Check Git branches instead of instances
            import subprocess
            result = subprocess.run(['git', 'branch', '--list', 'ai-pm-org-*'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                branches = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                total_branches = len(branches)
                
                if total_branches > self.large_project_threshold:
                    return True
            
            # Check project file count
            project_files = list(self.project_root.rglob("*"))
            if len(project_files) > 10000:  # 10k+ files
                return True
            
            # Check database size
            db_path = self.project_root / "projectManagement" / "project.db"
            if db_path.exists() and db_path.stat().st_size > 100 * 1024 * 1024:  # 100MB+
                return True
            
            # Check theme count
            themes_dir = self.project_root / "projectManagement" / "Themes"
            if themes_dir.exists():
                theme_files = list(themes_dir.glob("*.json"))
                if len(theme_files) > 50:  # 50+ themes
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking if large project: {e}")
            return False
    
    def optimize_for_large_project(self) -> Dict[str, Any]:
        """Comprehensive optimization for large projects"""
        optimization_results = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": [],
            "performance_improvements": {},
            "warnings": []
        }
        
        try:
            # 1. Database optimization
            db_results = self.db_optimizer.optimize_database()
            if db_results.get("success"):
                optimization_results["optimizations_applied"].append("database_optimization")
                optimization_results["performance_improvements"]["database"] = db_results
            
            # 2. Index optimization
            index_results = self.db_optimizer.create_performance_indexes()
            if index_results.get("success"):
                optimization_results["optimizations_applied"].append("index_creation")
                optimization_results["performance_improvements"]["indexes"] = index_results
            
            # 3. Theme file optimization
            theme_results = self._optimize_theme_files()
            if theme_results.get("success"):
                optimization_results["optimizations_applied"].append("theme_optimization")
                optimization_results["performance_improvements"]["themes"] = theme_results
            
            # 4. Flow file optimization
            flow_results = self._optimize_flow_files()
            if flow_results.get("success"):
                optimization_results["optimizations_applied"].append("flow_optimization")
                optimization_results["performance_improvements"]["flows"] = flow_results
            
            # 5. Cache optimization
            cache_results = self._optimize_caching()
            optimization_results["optimizations_applied"].append("cache_optimization")
            optimization_results["performance_improvements"]["cache"] = cache_results
            
            # 6. Memory optimization
            memory_results = self._optimize_memory_usage()
            optimization_results["optimizations_applied"].append("memory_optimization")
            optimization_results["performance_improvements"]["memory"] = memory_results
            
            self.last_optimization = datetime.now()
            
            return optimization_results
            
        except Exception as e:
            optimization_results["error"] = f"Optimization failed: {str(e)}"
            return optimization_results
    
    def _optimize_theme_files(self) -> Dict[str, Any]:
        """Optimize theme file structure and relationships"""
        try:
            themes_dir = self.project_root / "projectManagement" / "Themes"
            if not themes_dir.exists():
                return {"success": False, "reason": "Themes directory not found"}
            
            theme_files = list(themes_dir.glob("*.json"))
            optimizations = {
                "files_processed": len(theme_files),
                "size_reductions": [],
                "relationship_optimizations": 0
            }
            
            for theme_file in theme_files:
                try:
                    with open(theme_file, 'r') as f:
                        theme_data = json.load(f)
                    
                    original_size = theme_file.stat().st_size
                    
                    # Optimize theme structure
                    optimized_data = self._optimize_theme_data(theme_data)
                    
                    # Write optimized data back
                    with open(theme_file, 'w') as f:
                        json.dump(optimized_data, f, indent=2, separators=(',', ': '))
                    
                    new_size = theme_file.stat().st_size
                    if new_size < original_size:
                        optimizations["size_reductions"].append({
                            "file": theme_file.name,
                            "original_size": original_size,
                            "new_size": new_size,
                            "reduction": original_size - new_size
                        })
                    
                except Exception as e:
                    print(f"Error optimizing theme file {theme_file}: {e}")
            
            return {"success": True, **optimizations}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _optimize_theme_data(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize individual theme data structure"""
        # Remove duplicate file references
        if "files" in theme_data and isinstance(theme_data["files"], list):
            theme_data["files"] = list(set(theme_data["files"]))
        
        # Optimize linked themes
        if "linkedThemes" in theme_data and isinstance(theme_data["linkedThemes"], list):
            theme_data["linkedThemes"] = list(set(theme_data["linkedThemes"]))
        
        # Remove empty shared files
        if "sharedFiles" in theme_data and isinstance(theme_data["sharedFiles"], dict):
            theme_data["sharedFiles"] = {
                k: v for k, v in theme_data["sharedFiles"].items() 
                if v and (isinstance(v, dict) and v.get("sharedWith"))
            }
        
        return theme_data
    
    def _optimize_flow_files(self) -> Dict[str, Any]:
        """Optimize flow file structure and cross-references"""
        try:
            flows_dir = self.project_root / "projectManagement" / "ProjectFlow"
            if not flows_dir.exists():
                return {"success": False, "reason": "ProjectFlow directory not found"}
            
            flow_files = list(flows_dir.glob("*-flow.json"))
            flow_index_path = flows_dir / "flow-index.json"
            
            optimizations = {
                "files_processed": len(flow_files),
                "cross_references_optimized": 0,
                "index_updated": False
            }
            
            # Optimize individual flow files
            for flow_file in flow_files:
                try:
                    with open(flow_file, 'r') as f:
                        flow_data = json.load(f)
                    
                    # Optimize flow structure
                    optimized_flow = self._optimize_flow_data(flow_data)
                    
                    with open(flow_file, 'w') as f:
                        json.dump(optimized_flow, f, indent=2)
                    
                    optimizations["cross_references_optimized"] += 1
                    
                except Exception as e:
                    print(f"Error optimizing flow file {flow_file}: {e}")
            
            # Optimize flow index
            if flow_index_path.exists():
                try:
                    with open(flow_index_path, 'r') as f:
                        index_data = json.load(f)
                    
                    # Remove references to non-existent flow files
                    if "flowFiles" in index_data:
                        existing_flows = [f.name for f in flow_files]
                        index_data["flowFiles"] = [
                            flow for flow in index_data["flowFiles"]
                            if flow.get("fileName") in existing_flows
                        ]
                    
                    with open(flow_index_path, 'w') as f:
                        json.dump(index_data, f, indent=2)
                    
                    optimizations["index_updated"] = True
                    
                except Exception as e:
                    print(f"Error optimizing flow index: {e}")
            
            return {"success": True, **optimizations}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _optimize_flow_data(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize individual flow data structure"""
        # Optimize flow steps - remove duplicates and empty entries
        if "flows" in flow_data and isinstance(flow_data["flows"], dict):
            for flow_id, flow_content in flow_data["flows"].items():
                if "steps" in flow_content and isinstance(flow_content["steps"], list):
                    # Remove empty steps
                    flow_content["steps"] = [
                        step for step in flow_content["steps"]
                        if step and isinstance(step, dict) and step.get("description")
                    ]
        
        return flow_data
    
    def _optimize_caching(self) -> Dict[str, Any]:
        """Optimize caching configuration for large projects"""
        # Increase cache size for large projects
        if self.is_large_project():
            self.cache.max_size = 2000  # Double cache size
            self.cache.ttl_seconds = 7200  # Increase TTL to 2 hours
        
        # Clear expired entries
        expired_count = 0
        current_time = datetime.now()
        
        with self.cache.lock:
            expired_keys = [
                key for key, access_time in self.cache.access_times.items()
                if current_time - access_time > timedelta(seconds=self.cache.ttl_seconds)
            ]
            
            for key in expired_keys:
                if key in self.cache.cache:
                    del self.cache.cache[key]
                if key in self.cache.access_times:
                    del self.cache.access_times[key]
                self.cache.access_counts.pop(key, None)
                expired_count += 1
        
        return {
            "cache_size": self.cache.max_size,
            "ttl_seconds": self.cache.ttl_seconds,
            "expired_entries_cleared": expired_count,
            "current_utilization": len(self.cache.cache) / self.cache.max_size
        }
    
    def _optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize memory usage for large projects"""
        try:
            import gc
            
            # Get current memory usage if psutil available
            memory_before = 0
            memory_after = 0
            
            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                memory_before = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                pass
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear unnecessary caches
            self.cache.clear()
            
            # Get memory usage after optimization
            if memory_before > 0:
                try:
                    memory_after = process.memory_info().rss / 1024 / 1024  # MB
                except:
                    pass
            
            memory_saved = memory_before - memory_after
            
            return {
                "memory_before_mb": round(memory_before, 2),
                "memory_after_mb": round(memory_after, 2),
                "memory_saved_mb": round(memory_saved, 2),
                "garbage_collected": collected,
                "cache_cleared": True
            }
            
        except Exception as e:
            return {"error": f"Memory optimization failed: {str(e)}"}
    
    def should_optimize(self) -> bool:
        """Check if optimization should be run"""
        if not self.is_large_project():
            return False
        
        time_since_last = datetime.now() - self.last_optimization
        return time_since_last.total_seconds() > self.optimization_interval
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            "project_classification": {
                "is_large_project": self.is_large_project(),
                "optimization_needed": self.should_optimize()
            },
            "metrics": {
                "cache_stats": self.cache.get_stats(),
                "operation_averages": {
                    op: self.metrics.get_average_time(op)
                    for op in self.metrics.operation_times.keys()
                },
                "cache_hit_rate": self.metrics.get_cache_hit_rate(),
                "total_db_queries": self.metrics.database_queries,
                "total_file_operations": self.metrics.file_operations
            },
            "last_optimization": self.last_optimization.isoformat(),
            "recommendations": self._generate_performance_recommendations()
        }
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if self.is_large_project() and self.should_optimize():
            recommendations.append("Run comprehensive optimization - project qualifies as large")
        
        if self.metrics.get_cache_hit_rate() < 0.7:
            recommendations.append("Cache hit rate is low - consider increasing cache size or TTL")
        
        if self.metrics.database_queries > 1000:
            recommendations.append("High database query count - consider query optimization")
        
        cache_utilization = len(self.cache.cache) / self.cache.max_size
        if cache_utilization > 0.9:
            recommendations.append("Cache is nearly full - consider increasing cache size")
        
        return recommendations
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Analyze project and provide optimization recommendations"""
        recommendations = []
        
        try:
            # Check if optimization is needed
            if self.is_large_project():
                recommendations.append({
                    "type": "large_project_optimization",
                    "priority": "high",
                    "description": "Project size indicates need for performance optimization",
                    "action": "Run optimize_for_large_project()"
                })
            
            # Check last optimization time
            time_since_optimization = datetime.now() - self.last_optimization
            if time_since_optimization.total_seconds() > self.optimization_interval:
                recommendations.append({
                    "type": "periodic_optimization",
                    "priority": "medium",
                    "description": f"Last optimization was {time_since_optimization} ago",
                    "action": "Run periodic database optimization"
                })
            
            # Check cache performance
            cache_hit_rate = self.metrics.get_cache_hit_rate()
            if cache_hit_rate < 0.7 and self.metrics.cache_hits + self.metrics.cache_misses > 100:
                recommendations.append({
                    "type": "cache_optimization",
                    "priority": "medium",
                    "description": f"Cache hit rate is low ({cache_hit_rate:.2%})",
                    "action": "Increase cache size or adjust TTL"
                })
            
            # Check active branches count
            try:
                import subprocess
                result = subprocess.run(['git', 'branch', '--list', 'ai-pm-org-*'], 
                                      capture_output=True, text=True, cwd=self.project_root)
                if result.returncode == 0:
                    branches = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                    if len(branches) > 20:
                        recommendations.append({
                            "type": "branch_cleanup",
                            "priority": "medium",
                            "description": f"{len(branches)} AI branches detected",
                            "action": "Consider cleaning up completed branches"
                        })
            except Exception:
                pass
            
            return {
                "success": True,
                "recommendations": recommendations,
                "project_metrics": {
                    "is_large_project": self.is_large_project(),
                    "cache_hit_rate": cache_hit_rate,
                    "last_optimization": self.last_optimization.isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Could not generate recommendations: {str(e)}",
                "recommendations": recommendations
            }
    
    def cleanup_resources(self):
        """Clean up optimization resources"""
        try:
            self.parallel_processor.shutdown()
            self.cache.clear()
        except Exception as e:
            print(f"Warning: Error cleaning up optimizer resources: {e}")
    
    def __del__(self):
        """Ensure resources are cleaned up"""
        self.cleanup_resources()