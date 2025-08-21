"""
Project status monitoring operations.

Handles project status checking, high priority item detection, and overall project health monitoring.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_operations import BaseProjectOperations
from ...database.session_queries import SessionQueries
from ...database.task_status_queries import TaskStatusQueries
from ...database.theme_flow_queries import ThemeFlowQueries
from ...database.file_metadata_queries import FileMetadataQueries
from ...database.event_queries import EventQueries

logger = logging.getLogger(__name__)


class ProjectStatusMonitor(BaseProjectOperations):
    """Monitors project status and health."""
    
    def __init__(self, db_manager=None, config_manager=None, directive_processor=None, **kwargs):
        super().__init__(db_manager, config_manager, directive_processor)
        self.session_queries = SessionQueries(db_manager) if db_manager else None
        self.task_queries = TaskStatusQueries(db_manager) if db_manager else None
        self.theme_flow_queries = ThemeFlowQueries(db_manager) if db_manager else None
        self.file_metadata_queries = FileMetadataQueries(db_manager) if db_manager else None
        self.event_queries = EventQueries(db_manager) if db_manager else None
    
    async def get_project_status(self, project_path: Path) -> str:
        """Get overall project status and structure information."""
        try:
            project_path = Path(project_path)
            project_mgmt_dir = self.get_project_management_dir(project_path)
            
            # Check if project is initialized
            if not project_mgmt_dir.exists():
                return f"Project not initialized at {project_path}. Use project_initialize to set up the project."
            
            # Load blueprint for basic info
            blueprint_data = self.load_blueprint(project_path)
            
            # Start building status report
            result = f"Project Status Report\n"
            result += f"{'='*50}\n"
            result += f"Project Path: {project_path}\n"
            
            if blueprint_data:
                result += f"Project Name: {blueprint_data.get('project_name', 'Unknown')}\n"
                result += f"Version: {blueprint_data.get('version', 'Unknown')}\n"
                result += f"Description: {blueprint_data.get('description', 'No description')}\n"
                result += f"Created: {blueprint_data.get('created', 'Unknown')}\n"
                result += f"Last Updated: {blueprint_data.get('last_updated', 'Unknown')}\n"
            else:
                result += "Blueprint: Not found or corrupted\n"
            
            result += f"\nManagement Directory: {project_mgmt_dir}\n"
            
            # Check management directory structure
            result += f"\nProject Structure:\n"
            for item in sorted(project_mgmt_dir.iterdir()):
                if item.is_dir():
                    item_count = len(list(item.iterdir())) if item.exists() else 0
                    result += f"  📁 {item.name}/ ({item_count} items)\n"
                else:
                    size_kb = item.stat().st_size / 1024 if item.exists() else 0
                    result += f"  📄 {item.name} ({size_kb:.1f} KB)\n"
            
            # Database status
            db_path = self.get_database_file_path(project_path)
            if db_path.exists():
                db_size = db_path.stat().st_size / 1024  # KB
                result += f"\n📊 Database: {db_path.name} ({db_size:.1f} KB)\n"
                
                # Get database statistics if available
                if self.db_manager:
                    try:
                        if self.session_queries:
                            session_count = await self.session_queries.get_session_count()
                            result += f"  - Sessions: {session_count}\n"
                        
                        if self.task_queries:
                            task_stats = await self.task_queries.get_task_statistics()
                            if task_stats:
                                result += f"  - Tasks: {task_stats.get('total', 0)} total\n"
                                result += f"  - Completed: {task_stats.get('completed', 0)}\n"
                                result += f"  - In Progress: {task_stats.get('in_progress', 0)}\n"
                        
                        if self.file_metadata_queries:
                            file_count = await self.file_metadata_queries.get_file_count(str(project_path))
                            result += f"  - Tracked Files: {file_count}\n"
                    
                    except Exception as e:
                        result += f"  - Error getting database stats: {str(e)}\n"
            else:
                result += f"\n⚠️ Database: Not found at {db_path}\n"
            
            # Check for high priority items
            high_priority = await self._check_high_priority_items(project_path, project_mgmt_dir)
            
            if high_priority['warnings'] or high_priority['errors']:
                result += f"\n🚨 High Priority Items:\n"
                
                for error in high_priority['errors']:
                    result += f"  ❌ ERROR: {error}\n"
                
                for warning in high_priority['warnings']:
                    result += f"  ⚠️ WARNING: {warning}\n"
            else:
                result += f"\n✅ No high priority issues detected.\n"
            
            # Health score
            health_score = self._calculate_health_score(project_mgmt_dir, blueprint_data, high_priority)
            result += f"\n📊 Project Health Score: {health_score}/100\n"
            
            if health_score >= 90:
                result += "🟢 Excellent - Project is well-maintained\n"
            elif health_score >= 70:
                result += "🟡 Good - Minor issues detected\n"
            elif health_score >= 50:
                result += "🟠 Fair - Several issues need attention\n"
            else:
                result += "🔴 Poor - Major issues require immediate attention\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            return f"Error getting project status: {str(e)}"
    
    async def _check_high_priority_items(self, project_path: Path, project_mgmt_dir: Path) -> Dict[str, Any]:
        """Check for high priority items that need attention."""
        high_priority = {
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'events': []
        }
        
        try:
            # Check for missing critical files
            blueprint_path = self.get_blueprint_file_path(project_path)
            if not blueprint_path.exists():
                high_priority['errors'].append("Blueprint file missing")
            
            db_path = self.get_database_file_path(project_path)
            if not db_path.exists():
                high_priority['errors'].append("Database not initialized")
            
            # Check for empty or corrupted files
            if blueprint_path.exists():
                try:
                    blueprint_data = json.loads(blueprint_path.read_text())
                    if not blueprint_data.get('project_name'):
                        high_priority['warnings'].append("Blueprint missing project name")
                except json.JSONDecodeError:
                    high_priority['errors'].append("Blueprint file corrupted")
            
            # Check directory structure
            required_dirs = ['ProjectFlow', 'ProjectThemes', 'Documentation']
            for req_dir in required_dirs:
                dir_path = project_mgmt_dir / req_dir
                if not dir_path.exists():
                    high_priority['warnings'].append(f"Missing required directory: {req_dir}")
                elif not any(dir_path.iterdir()):
                    high_priority['recommendations'].append(f"Empty directory: {req_dir}")
            
            # Check database integrity if available
            if db_path.exists() and self.db_manager:
                try:
                    # Try to connect to database
                    await self.db_manager.initialize_database(str(db_path))
                except Exception as e:
                    high_priority['errors'].append(f"Database connection failed: {str(e)}")
            
            # Check for very large files that might cause issues
            for item in project_mgmt_dir.rglob('*'):
                if item.is_file():
                    size_mb = item.stat().st_size / (1024 * 1024)
                    if size_mb > 100:  # Files larger than 100MB
                        high_priority['warnings'].append(f"Large file detected: {item.name} ({size_mb:.1f} MB)")
            
            # Check for old backup files or temp files
            temp_patterns = ['*.tmp', '*.temp', '*.bak', '*~']
            for pattern in temp_patterns:
                temp_files = list(project_mgmt_dir.rglob(pattern))
                if temp_files:
                    high_priority['recommendations'].append(f"Clean up {len(temp_files)} temporary files ({pattern})")
            
            # Check database for high-priority events (if database exists)
            db_path = self.get_database_file_path(project_path)
            if db_path.exists() and self.event_queries:
                try:
                    # Check if high priority exists in database
                    has_db_priority = await self.event_queries.check_high_priority_exists(days_lookback=7)
                    if has_db_priority:
                        # Get recent high priority events (limit to 3 for status display)
                        recent_events = await self.event_queries.get_high_priority_events(limit=3, days_lookback=7)
                        high_priority["events"] = [
                            {
                                "title": event.get("title", "Unknown"),
                                "type": event.get("event_type", "unknown"),
                                "created": event.get("created_at", "unknown"),
                                "impact": event.get("impact_level", "unknown")
                            }
                            for event in recent_events
                        ]
                except Exception as e:
                    logger.warning(f"Error checking database for high priority events: {e}")
            
        except Exception as e:
            high_priority['errors'].append(f"Error during high priority check: {str(e)}")
        
        return high_priority
    
    def _calculate_health_score(self, project_mgmt_dir: Path, blueprint_data: Optional[Dict], 
                              high_priority: Dict[str, Any]) -> int:
        """Calculate project health score (0-100)."""
        score = 100
        
        # Deduct points for errors and warnings
        score -= len(high_priority['errors']) * 20  # 20 points per error
        score -= len(high_priority['warnings']) * 10  # 10 points per warning
        score -= len(high_priority['recommendations']) * 2  # 2 points per recommendation
        
        # Deduct points for missing blueprint
        if not blueprint_data:
            score -= 15
        
        # Deduct points for missing required directories
        required_dirs = ['ProjectFlow', 'ProjectThemes', 'Documentation']
        missing_dirs = sum(1 for dir_name in required_dirs 
                          if not (project_mgmt_dir / dir_name).exists())
        score -= missing_dirs * 10
        
        # Bonus points for good structure
        if blueprint_data and blueprint_data.get('project_name'):
            score += 5
        
        if blueprint_data and blueprint_data.get('description'):
            score += 5
        
        # Ensure score is within bounds
        return max(0, min(100, score))