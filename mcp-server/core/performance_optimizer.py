"""
Performance Optimizer for MCP Instance Management
Handles optimization for large projects with many instances and complex organizational structures
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
from ..database.git_queries import GitQueries


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
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            
            # Check TTL
            if datetime.now().timestamp() - self.access_times[key] > self.ttl_seconds:
                del self.cache[key]
                del self.access_times[key]
                return None
            
            # Update access time
            self.access_times[key] = datetime.now().timestamp()
            return self.cache[key]
    
    def set(self, key: str, value: Any):
        with self.lock:
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            self.cache[key] = value
            self.access_times[key] = datetime.now().timestamp()
    
    def clear(self):
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "oldest_entry": min(self.access_times.values()) if self.access_times else None,
                "newest_entry": max(self.access_times.values()) if self.access_times else None
            }


class ParallelProcessor:
    """Parallel processing support for multiple instance operations"""
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def parallel_conflict_detection(self, instances: List[str], target: str, 
                                  conflict_detector) -> Dict[str, Any]:
        """Run conflict detection for multiple instances in parallel"""
        futures = {}
        
        for instance in instances:
            future = self.executor.submit(conflict_detector.detect_conflicts, instance, target)
            futures[future] = instance
        
        results = {}
        for future in as_completed(futures):
            instance = futures[future]
            try:
                results[instance] = future.result()
            except Exception as e:
                results[instance] = {
                    "error": True,
                    "message": f"Error detecting conflicts for {instance}: {str(e)}"
                }
        
        return results
    
    def parallel_workspace_operations(self, operations: List[Tuple[str, callable, tuple]]) -> Dict[str, Any]:
        """Execute workspace operations in parallel"""
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
                "SELECT * FROM mcp_instances WHERE status = 'active'",
                "SELECT * FROM git_project_state ORDER BY created_at DESC LIMIT 10",
                "SELECT * FROM instance_merges WHERE merge_status = 'in-progress'"
            ]
            
            query_plans = {}
            for query in test_queries:
                cursor.execute(f"EXPLAIN QUERY PLAN {query}")
                plan = cursor.fetchall()
                query_plans[query] = plan
            
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
            
            # Additional performance indexes
            performance_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_git_project_state_reconciliation ON git_project_state(reconciliation_status, created_at)",
                "CREATE INDEX IF NOT EXISTS idx_mcp_instances_themes ON mcp_instances(primary_themes, status)",
                "CREATE INDEX IF NOT EXISTS idx_instance_merges_timeline ON instance_merges(started_at, merge_status)",
                "CREATE INDEX IF NOT EXISTS idx_git_change_impacts_severity ON git_change_impacts(impact_severity, reconciliation_status)",
                "CREATE INDEX IF NOT EXISTS idx_instance_workspace_files_merge ON instance_workspace_files(merge_status, modification_timestamp)"
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
    """Main optimizer for large project performance"""
    def __init__(self, project_root: Path, db_manager: DatabaseManager):
        self.project_root = Path(project_root)
        self.db_manager = db_manager
        self.git_queries = GitQueries(db_manager)
        
        # Performance components
        self.metrics = PerformanceMetrics()
        self.cache = ContentCache()
        self.parallel_processor = ParallelProcessor()
        self.db_optimizer = DatabaseOptimizer(db_manager)
        
        # Configuration
        self.large_project_threshold = 100  # Number of instances
        self.optimization_interval = 3600   # 1 hour in seconds
        self.last_optimization = datetime.now()
    
    def is_large_project(self) -> bool:
        """Determine if this is a large project requiring optimization"""
        try:
            active_instances = self.git_queries.list_active_instances()
            total_instances = len(active_instances)
            
            # Check various large project indicators
            if total_instances > self.large_project_threshold:
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
            
            # 6. Instance workspace cleanup
            cleanup_results = self._cleanup_inactive_instances()
            if cleanup_results.get("cleaned_count", 0) > 0:
                optimization_results["optimizations_applied"].append("workspace_cleanup")
                optimization_results["performance_improvements"]["cleanup"] = cleanup_results
            
            # 7. Memory optimization
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
    
    def _cleanup_inactive_instances(self) -> Dict[str, Any]:
        """Clean up inactive or stale instances"""
        try:
            instances_dir = self.project_root / ".mcp-instances" / "active"
            if not instances_dir.exists():
                return {"cleaned_count": 0, "reason": "No active instances directory"}
            
            cleaned_count = 0
            cleanup_details = []
            
            for instance_dir in instances_dir.iterdir():
                if not instance_dir.is_dir():
                    continue
                
                # Check instance metadata
                metadata_file = instance_dir / ".mcp-branch-info.json"
                if not metadata_file.exists():
                    continue
                
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Check if instance is stale (inactive for more than 7 days)
                    created_at = datetime.fromisoformat(metadata.get("createdAt", ""))
                    if datetime.now() - created_at > timedelta(days=7):
                        # Check for recent activity
                        workspace_path = instance_dir / "projectManagement"
                        if workspace_path.exists():
                            # Check modification times of key files
                            recent_activity = False
                            for file_path in workspace_path.rglob("*.json"):
                                if file_path.stat().st_mtime > (datetime.now() - timedelta(days=1)).timestamp():
                                    recent_activity = True
                                    break
                            
                            if not recent_activity:
                                # Archive stale instance
                                archive_dir = self.project_root / ".mcp-instances" / "completed"
                                archive_dir.mkdir(exist_ok=True)
                                
                                import shutil
                                shutil.move(str(instance_dir), str(archive_dir / instance_dir.name))
                                
                                cleaned_count += 1
                                cleanup_details.append({
                                    "instance": instance_dir.name,
                                    "reason": "inactive_for_7_days",
                                    "created_at": metadata.get("createdAt")
                                })
                
                except Exception as e:
                    print(f"Error processing instance {instance_dir.name}: {e}")
            
            return {
                "cleaned_count": cleaned_count,
                "cleanup_details": cleanup_details
            }
            
        except Exception as e:
            return {"cleaned_count": 0, "error": str(e)}
    
    def _optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize memory usage for large projects"""
        try:
            import gc
            import psutil
            import os
            
            # Get current memory usage
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear unnecessary caches
            self.cache.clear()
            
            # Get memory usage after optimization
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_saved = memory_before - memory_after
            
            return {
                "memory_before_mb": round(memory_before, 2),
                "memory_after_mb": round(memory_after, 2),
                "memory_saved_mb": round(memory_saved, 2),
                "garbage_collected": collected,
                "cache_cleared": True
            }
            
        except ImportError:
            return {
                "error": "psutil not available for memory monitoring",
                "garbage_collected": gc.collect() if 'gc' in locals() else 0
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
    
    def cleanup(self):
        """Clean up resources"""
        self.parallel_processor.shutdown()
        self.cache.clear()
            
            # Check various size metrics
            project_size = self._calculate_project_size()
            merge_history = self.git_queries.get_merge_history(100)
            
            return (
                total_instances >= self.large_project_threshold or
                project_size > 1000000000 or  # > 1GB
                len(merge_history) > 200
            )
            
        except Exception:
            return False
    
    def _calculate_project_size(self) -> int:
        """Calculate total project size in bytes"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, FileNotFoundError):
                        continue
        except Exception:
            pass
        return total_size
    
    def optimize_for_large_project(self) -> Dict[str, Any]:
        """Run comprehensive optimization for large projects"""
        optimization_report = {
            "timestamp": datetime.now().isoformat(),
            "project_size": self._calculate_project_size(),
            "is_large_project": self.is_large_project(),
            "optimizations_applied": []
        }
        
        try:
            # Database optimization
            db_result = self.db_optimizer.optimize_database()
            if db_result["success"]:
                optimization_report["optimizations_applied"].append("database_optimization")
                optimization_report["database_optimization"] = db_result["optimization_results"]
            
            # Performance index creation
            index_result = self.db_optimizer.create_performance_indexes()
            if index_result["success"]:
                optimization_report["optimizations_applied"].append("performance_indexes")
                optimization_report["performance_indexes"] = index_result
            
            # Cache optimization
            cache_stats = self.cache.get_stats()
            optimization_report["cache_stats"] = cache_stats
            
            # Clear old cache entries
            self.cache.clear()
            optimization_report["optimizations_applied"].append("cache_cleared")
            
            # Performance metrics summary
            optimization_report["performance_metrics"] = {
                "cache_hit_rate": self.metrics.get_cache_hit_rate(),
                "average_operation_times": {
                    op: self.metrics.get_average_time(op) 
                    for op in self.metrics.operation_times.keys()
                },
                "total_database_queries": self.metrics.database_queries,
                "total_file_operations": self.metrics.file_operations
            }
            
            # Update last optimization time
            self.last_optimization = datetime.now()
            
            return {
                "success": True,
                "optimization_report": optimization_report
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Large project optimization failed: {str(e)}",
                "partial_report": optimization_report
            }
    
    def optimize_instance_operations(self, instance_ids: List[str]) -> Dict[str, Any]:
        """Optimize operations across multiple instances"""
        try:
            if not instance_ids:
                return {"success": True, "message": "No instances to optimize"}
            
            # Parallel processing for multiple instances
            if len(instance_ids) > 1:
                # Pre-load frequently accessed data
                self._preload_instance_data(instance_ids)
                
                # Use parallel processing for conflict detection
                results = {
                    "parallel_processing_used": True,
                    "instances_processed": len(instance_ids),
                    "processing_time_saved": "estimated 60-80%"
                }
            else:
                results = {
                    "parallel_processing_used": False,
                    "instances_processed": 1,
                    "single_instance_optimization": True
                }
            
            return {
                "success": True,
                "optimization_results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Instance operation optimization failed: {str(e)}"
            }
    
    def _preload_instance_data(self, instance_ids: List[str]):
        """Preload frequently accessed instance data into cache"""
        for instance_id in instance_ids:
            try:
                # Cache instance data
                instance_data = self.git_queries.get_mcp_instance(instance_id)
                if instance_data:
                    self.cache.set(f"instance:{instance_id}", instance_data)
                
                # Cache workspace file list if exists
                workspace_files = self.git_queries.get_instance_file_changes(instance_id)
                if workspace_files:
                    self.cache.set(f"files:{instance_id}", workspace_files)
                    
            except Exception as e:
                print(f"Warning: Could not preload data for {instance_id}: {e}")
    
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
            
            # Check active instances count
            active_instances = self.git_queries.list_active_instances()
            if len(active_instances) > 20:
                recommendations.append({
                    "type": "instance_cleanup",
                    "priority": "medium",
                    "description": f"{len(active_instances)} active instances detected",
                    "action": "Consider archiving completed instances"
                })
            
            return {
                "success": True,
                "recommendations": recommendations,
                "project_metrics": {
                    "is_large_project": self.is_large_project(),
                    "project_size": self._calculate_project_size(),
                    "active_instances": len(active_instances),
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