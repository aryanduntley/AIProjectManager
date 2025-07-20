"""
Theme-Flow Relationship Queries for AI Project Manager
Handles all database operations related to theme-flow relationships.
"""

import json
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from .db_manager import DatabaseManager

class ThemeFlowQueries:
    """
    Enhanced theme-flow relationship management with comprehensive database operations.
    
    Key Features:
    - Many-to-many theme-flow relationships with relevance ordering
    - Fast context loading with optimized queries
    - Flow status tracking with completion percentage
    - Cross-platform compatibility with SQLite
    - Theme evolution tracking and analytics
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
    
    def add_theme_flow_relationship(self, theme_name: str, flow_id: str, relevance_order: int = 1) -> bool:
        """
        Add a theme-flow relationship.
        
        Args:
            theme_name: The theme name
            flow_id: The flow identifier
            relevance_order: Order of relevance (1 = most relevant)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.execute_insert(
                """
                INSERT OR REPLACE INTO theme_flows 
                (theme_name, flow_id, flow_file, relevance_order) 
                VALUES (?, ?, ?, ?)
                """,
                (theme_name, flow_id, f"{flow_id}.json", relevance_order)
            )
            return True
        except Exception as e:
            self.db.logger.error(f"Error adding theme-flow relationship: {e}")
            return False
    
    def get_themes_for_flow(self, flow_id: str) -> List[str]:
        """
        Get all themes that use a specific flow.
        
        Args:
            flow_id: The flow identifier
            
        Returns:
            List of theme names that use this flow
        """
        query = """
        SELECT theme_name 
        FROM theme_flows 
        WHERE flow_id = ? 
        ORDER BY relevance_order
        """
        results = self.db.execute_query(query, (flow_id,))
        return [row['theme_name'] for row in results]
    
    def get_flows_for_theme(self, theme_name: str) -> List[Dict[str, any]]:
        """
        Get all flows for a specific theme.
        
        Args:
            theme_name: The theme name
            
        Returns:
            List of flow information dictionaries
        """
        query = """
        SELECT flow_id, flow_file, relevance_order, created_at, updated_at
        FROM theme_flows 
        WHERE theme_name = ? 
        ORDER BY relevance_order
        """
        results = self.db.execute_query(query, (theme_name,))
        return [
            {
                'flow_id': row['flow_id'],
                'flow_file': row['flow_file'],
                'relevance_order': row['relevance_order'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            for row in results
        ]
    
    def update_theme_flows(self, theme_name: str, flow_ids: List[str], flow_index_data: Dict) -> bool:
        """
        Update all flows for a theme.
        
        Args:
            theme_name: The theme name
            flow_ids: List of flow IDs in order of relevance
            flow_index_data: Flow index data to resolve flow files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First, remove existing flows for this theme
            self.db.execute_update(
                "DELETE FROM theme_flows WHERE theme_name = ?",
                (theme_name,)
            )
            
            # Insert new flows
            for order, flow_id in enumerate(flow_ids):
                flow_file = self._resolve_flow_file(flow_id, flow_index_data)
                if flow_file:
                    self.db.execute_insert(
                        """
                        INSERT INTO theme_flows (theme_name, flow_id, flow_file, relevance_order)
                        VALUES (?, ?, ?, ?)
                        """,
                        (theme_name, flow_id, flow_file, order)
                    )
            
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error updating theme flows for {theme_name}: {e}")
            return False
    
    def add_theme_flow(self, theme_name: str, flow_id: str, flow_file: str, relevance_order: int) -> bool:
        """
        Add a single flow to a theme.
        
        Args:
            theme_name: The theme name
            flow_id: The flow identifier
            flow_file: The flow file name
            relevance_order: Order of relevance (0 = most relevant)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.execute_insert(
                """
                INSERT OR REPLACE INTO theme_flows (theme_name, flow_id, flow_file, relevance_order)
                VALUES (?, ?, ?, ?)
                """,
                (theme_name, flow_id, flow_file, relevance_order)
            )
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error adding flow {flow_id} to theme {theme_name}: {e}")
            return False
    
    def remove_theme_flow(self, theme_name: str, flow_id: str) -> bool:
        """
        Remove a flow from a theme.
        
        Args:
            theme_name: The theme name
            flow_id: The flow identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            affected_rows = self.db.execute_update(
                "DELETE FROM theme_flows WHERE theme_name = ? AND flow_id = ?",
                (theme_name, flow_id)
            )
            return affected_rows > 0
            
        except Exception as e:
            self.db.logger.error(f"Error removing flow {flow_id} from theme {theme_name}: {e}")
            return False
    
    def get_theme_flow_summary(self) -> List[Dict[str, any]]:
        """
        Get summary of all theme-flow relationships.
        
        Returns:
            List of theme summaries
        """
        query = """
        SELECT 
            theme_name,
            flow_count,
            flows,
            first_flow_added,
            last_updated
        FROM theme_flow_summary
        ORDER BY theme_name
        """
        results = self.db.execute_query(query)
        return [
            {
                'theme_name': row['theme_name'],
                'flow_count': row['flow_count'],
                'flows': row['flows'].split(',') if row['flows'] else [],
                'first_flow_added': row['first_flow_added'],
                'last_updated': row['last_updated']
            }
            for row in results
        ]
    
    def get_flow_theme_summary(self) -> List[Dict[str, any]]:
        """
        Get summary of all flow-theme relationships.
        
        Returns:
            List of flow summaries
        """
        query = """
        SELECT 
            flow_id,
            flow_file,
            theme_count,
            themes,
            first_theme_added,
            last_updated
        FROM flow_theme_summary
        ORDER BY flow_id
        """
        results = self.db.execute_query(query)
        return [
            {
                'flow_id': row['flow_id'],
                'flow_file': row['flow_file'],
                'theme_count': row['theme_count'],
                'themes': row['themes'].split(',') if row['themes'] else [],
                'first_theme_added': row['first_theme_added'],
                'last_updated': row['last_updated']
            }
            for row in results
        ]
    
    def sync_theme_flows_from_files(self, theme_files_data: Dict[str, Dict], flow_index_data: Dict) -> Dict[str, any]:
        """
        Synchronize database with theme files from the filesystem.
        
        Args:
            theme_files_data: Dictionary of theme file contents
            flow_index_data: Flow index data to resolve flow files
            
        Returns:
            Dictionary with sync results
        """
        results = {
            'themes_processed': 0,
            'flows_added': 0,
            'flows_removed': 0,
            'errors': []
        }
        
        try:
            # Get current database state
            current_db_state = {}
            for theme_summary in self.get_theme_flow_summary():
                current_db_state[theme_summary['theme_name']] = set(theme_summary['flows'])
            
            # Process each theme file
            for theme_name, theme_data in theme_files_data.items():
                results['themes_processed'] += 1
                
                # Get flows from theme file
                theme_flows = theme_data.get('flows', [])
                new_flows = set(theme_flows)
                
                # Get current flows from database
                current_flows = current_db_state.get(theme_name, set())
                
                # Calculate differences
                flows_to_add = new_flows - current_flows
                flows_to_remove = current_flows - new_flows
                
                # Remove flows no longer in theme
                for flow_id in flows_to_remove:
                    if self.remove_theme_flow(theme_name, flow_id):
                        results['flows_removed'] += 1
                
                # Add/update flows in theme
                if theme_flows:  # Only update if there are flows
                    if self.update_theme_flows(theme_name, theme_flows, flow_index_data):
                        results['flows_added'] += len(flows_to_add)
                
            return results
            
        except Exception as e:
            results['errors'].append(f"Error during sync: {e}")
            self.db.logger.error(f"Error syncing theme flows: {e}")
            return results
    
    def _resolve_flow_file(self, flow_id: str, flow_index_data: Dict) -> Optional[str]:
        """
        Resolve flow ID to flow file using flow index data.
        
        Args:
            flow_id: The flow identifier
            flow_index_data: Flow index data
            
        Returns:
            Flow file name or None if not found
        """
        # Look through flow files in the index
        for flow_file_data in flow_index_data.get('flowFiles', []):
            flow_file = flow_file_data.get('filename')
            if flow_file:
                # This is a simplified resolution - in practice, we'd need to
                # load the actual flow file to check if it contains the flow_id
                # For now, we'll return the first match or a default
                return flow_file
        
        # Default fallback - this should be improved based on actual flow file structure
        return f"{flow_id.split('-')[0]}-flow.json"
    
    def get_orphaned_flows(self) -> List[str]:
        """
        Get flows that are not referenced by any theme.
        
        Returns:
            List of flow IDs that are orphaned
        """
        query = """
        SELECT DISTINCT flow_id
        FROM theme_flows
        WHERE flow_id NOT IN (
            SELECT DISTINCT flow_id 
            FROM theme_flows 
            WHERE theme_name IS NOT NULL
        )
        """
        results = self.db.execute_query(query)
        return [row['flow_id'] for row in results]
    
    def get_theme_flow_statistics(self) -> Dict[str, any]:
        """
        Get statistics about theme-flow relationships.
        
        Returns:
            Dictionary with statistics
        """
        stats = {}
        
        # Total counts
        stats['total_themes'] = len(self.get_theme_flow_summary())
        
        # Flow distribution
        flow_counts = self.db.execute_query("""
            SELECT theme_name, COUNT(*) as flow_count
            FROM theme_flows
            GROUP BY theme_name
            ORDER BY flow_count DESC
        """)
        
        stats['theme_flow_distribution'] = [
            {'theme': row['theme_name'], 'flow_count': row['flow_count']}
            for row in flow_counts
        ]
        
        # Most referenced flows
        flow_usage = self.db.execute_query("""
            SELECT flow_id, COUNT(*) as theme_count
            FROM theme_flows
            GROUP BY flow_id
            ORDER BY theme_count DESC
            LIMIT 10
        """)
        
        stats['most_referenced_flows'] = [
            {'flow_id': row['flow_id'], 'theme_count': row['theme_count']}
            for row in flow_usage
        ]
        
        return stats
    
    # Enhanced Flow Status Management (following database implementation plan)
    
    def create_or_update_flow_status(
        self,
        flow_id: str,
        flow_file: str,
        name: str,
        status: str = "pending",
        completion_percentage: int = 0,
        primary_themes: List[str] = None,
        secondary_themes: List[str] = None
    ) -> bool:
        """
        Create or update flow status.
        
        Args:
            flow_id: Flow identifier
            flow_file: Flow file name
            name: Human-readable flow name
            status: Flow status (pending, in-progress, complete, needs-review, blocked)
            completion_percentage: Completion percentage (0-100)
            primary_themes: List of primary themes
            secondary_themes: List of secondary themes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT OR REPLACE INTO flow_status (
                    flow_id, flow_file, name, status, completion_percentage,
                    primary_themes, secondary_themes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                flow_id, flow_file, name, status, completion_percentage,
                json.dumps(primary_themes or []), json.dumps(secondary_themes or [])
            )
            
            self.db.execute_update(query, params)
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error creating/updating flow status: {e}")
            return False
    
    def update_flow_status(
        self,
        flow_id: str,
        status: str,
        completion_percentage: int = None
    ) -> bool:
        """Update flow status and completion percentage."""
        try:
            update_fields = ["status = ?"]
            params = [status]
            
            if completion_percentage is not None:
                update_fields.append("completion_percentage = ?")
                params.append(completion_percentage)
            
            # Set completion timestamp if flow is complete
            if status == "complete":
                update_fields.append("completed_at = CURRENT_TIMESTAMP")
            
            params.append(flow_id)
            
            query = f"""
                UPDATE flow_status 
                SET {', '.join(update_fields)}
                WHERE flow_id = ?
            """
            
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
            
        except Exception as e:
            self.db.logger.error(f"Error updating flow status: {e}")
            return False
    
    def get_flow_status(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """Get flow status by ID."""
        query = "SELECT * FROM flow_status WHERE flow_id = ?"
        result = self.db.execute_query(query, (flow_id,))
        
        if result:
            row = result[0]
            return {
                "flow_id": row["flow_id"],
                "flow_file": row["flow_file"],
                "name": row["name"],
                "status": row["status"],
                "completion_percentage": row["completion_percentage"],
                "primary_themes": json.loads(row["primary_themes"]) if row["primary_themes"] else [],
                "secondary_themes": json.loads(row["secondary_themes"]) if row["secondary_themes"] else [],
                "created_at": row["created_at"],
                "last_updated": row["last_updated"],
                "completed_at": row["completed_at"]
            }
        return None
    
    def get_flows_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get flows by status."""
        query = """
            SELECT * FROM flow_status 
            WHERE status = ?
            ORDER BY last_updated DESC
        """
        
        results = []
        for row in self.db.execute_query(query, (status,)):
            results.append({
                "flow_id": row["flow_id"],
                "flow_file": row["flow_file"],
                "name": row["name"],
                "status": row["status"],
                "completion_percentage": row["completion_percentage"],
                "primary_themes": json.loads(row["primary_themes"]) if row["primary_themes"] else [],
                "secondary_themes": json.loads(row["secondary_themes"]) if row["secondary_themes"] else [],
                "created_at": row["created_at"],
                "last_updated": row["last_updated"],
                "completed_at": row["completed_at"]
            })
        
        return results
    
    def get_flows_by_theme_enhanced(self, theme_name: str, include_secondary: bool = True) -> List[Dict[str, Any]]:
        """Get flows that belong to a theme from flow_status table."""
        if include_secondary:
            query = """
                SELECT * FROM flow_status 
                WHERE JSON_EXTRACT(primary_themes, '$') LIKE '%"' || ? || '"%'
                   OR JSON_EXTRACT(secondary_themes, '$') LIKE '%"' || ? || '"%'
                ORDER BY completion_percentage DESC, last_updated DESC
            """
            params = (theme_name, theme_name)
        else:
            query = """
                SELECT * FROM flow_status 
                WHERE JSON_EXTRACT(primary_themes, '$') LIKE '%"' || ? || '"%'
                ORDER BY completion_percentage DESC, last_updated DESC
            """
            params = (theme_name,)
        
        results = []
        for row in self.db.execute_query(query, params):
            results.append({
                "flow_id": row["flow_id"],
                "flow_file": row["flow_file"],
                "name": row["name"],
                "status": row["status"],
                "completion_percentage": row["completion_percentage"],
                "primary_themes": json.loads(row["primary_themes"]) if row["primary_themes"] else [],
                "secondary_themes": json.loads(row["secondary_themes"]) if row["secondary_themes"] else [],
                "created_at": row["created_at"],
                "last_updated": row["last_updated"],
                "completed_at": row["completed_at"]
            })
        
        return results
    
    # Flow Step Status Management
    
    def create_flow_step(
        self,
        flow_id: str,
        step_id: str,
        step_number: int,
        description: str,
        dependencies: List[str] = None,
        files_referenced: List[str] = None,
        implementation_status: str = "pending"
    ) -> bool:
        """
        Create a flow step.
        
        Args:
            flow_id: Flow identifier
            step_id: Step identifier (e.g., URF-001)
            step_number: Step number in sequence
            description: Step description
            dependencies: List of step IDs this depends on
            files_referenced: List of file paths
            implementation_status: Implementation status (pending, exists, needs-design)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO flow_step_status (
                    flow_id, step_id, step_number, description, dependencies,
                    files_referenced, implementation_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                flow_id, step_id, step_number, description,
                json.dumps(dependencies or []), json.dumps(files_referenced or []),
                implementation_status
            )
            
            self.db.execute_update(query, params)
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error creating flow step: {e}")
            return False
    
    def update_flow_step_status(
        self,
        step_id: str,
        status: str,
        implementation_status: str = None
    ) -> bool:
        """Update flow step status."""
        try:
            update_fields = ["status = ?"]
            params = [status]
            
            if implementation_status is not None:
                update_fields.append("implementation_status = ?")
                params.append(implementation_status)
            
            # Set completion timestamp if step is completed
            if status == "completed":
                update_fields.append("completed_at = CURRENT_TIMESTAMP")
            
            params.append(step_id)
            
            query = f"""
                UPDATE flow_step_status 
                SET {', '.join(update_fields)}
                WHERE step_id = ?
            """
            
            affected_rows = self.db.execute_update(query, tuple(params))
            return affected_rows > 0
            
        except Exception as e:
            self.db.logger.error(f"Error updating flow step status: {e}")
            return False
    
    def get_flow_steps(self, flow_id: str) -> List[Dict[str, Any]]:
        """Get all steps for a flow."""
        query = """
            SELECT * FROM flow_step_status 
            WHERE flow_id = ?
            ORDER BY step_number ASC
        """
        
        results = []
        for row in self.db.execute_query(query, (flow_id,)):
            results.append({
                "id": row["id"],
                "flow_id": row["flow_id"],
                "step_id": row["step_id"],
                "step_number": row["step_number"],
                "description": row["description"],
                "status": row["status"],
                "dependencies": json.loads(row["dependencies"]) if row["dependencies"] else [],
                "completed_at": row["completed_at"],
                "files_referenced": json.loads(row["files_referenced"]) if row["files_referenced"] else [],
                "implementation_status": row["implementation_status"]
            })
        
        return results
    
    # Context Loading Optimization
    
    def get_context_for_themes(
        self,
        theme_names: List[str],
        include_flow_status: bool = True,
        include_step_details: bool = False
    ) -> Dict[str, Any]:
        """
        Get optimized context for multiple themes.
        
        Args:
            theme_names: List of theme names
            include_flow_status: Include flow status information
            include_step_details: Include detailed step information
            
        Returns:
            Context dictionary with theme-flow relationships and status
        """
        if not theme_names:
            return {"themes": {}, "flows": {}}
        
        # Get theme-flow relationships
        theme_flows = {}
        for theme_name in theme_names:
            theme_flows[theme_name] = self.get_flows_for_theme(theme_name)
        
        # Collect all unique flow IDs
        all_flow_ids = set()
        for flows in theme_flows.values():
            for flow in flows:
                all_flow_ids.add(flow["flow_id"])
        
        context = {
            "themes": theme_flows,
            "flows": {}
        }
        
        if include_flow_status and all_flow_ids:
            # Get flow status information
            placeholders = ",".join(["?" for _ in all_flow_ids])
            query = f"""
                SELECT flow_id, flow_file, name, status, completion_percentage,
                       primary_themes, secondary_themes
                FROM flow_status 
                WHERE flow_id IN ({placeholders})
            """
            
            for row in self.db.execute_query(query, tuple(all_flow_ids)):
                flow_info = {
                    "flow_id": row["flow_id"],
                    "flow_file": row["flow_file"],
                    "name": row["name"],
                    "status": row["status"],
                    "completion_percentage": row["completion_percentage"],
                    "primary_themes": json.loads(row["primary_themes"]) if row["primary_themes"] else [],
                    "secondary_themes": json.loads(row["secondary_themes"]) if row["secondary_themes"] else []
                }
                
                if include_step_details:
                    flow_info["steps"] = self.get_flow_steps(row["flow_id"])
                
                context["flows"][row["flow_id"]] = flow_info
        
        return context
    
    def get_flows_for_themes_optimized(self, theme_names: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get flows for multiple themes efficiently with single query.
        
        Args:
            theme_names: List of theme names
            
        Returns:
            Dictionary mapping theme names to their flow lists
        """
        if not theme_names:
            return {}
        
        placeholders = ",".join(["?" for _ in theme_names])
        query = f"""
            SELECT theme_name, flow_id, flow_file, relevance_order
            FROM theme_flows 
            WHERE theme_name IN ({placeholders})
            ORDER BY theme_name, relevance_order ASC
        """
        
        result_dict = {theme: [] for theme in theme_names}
        
        for row in self.db.execute_query(query, tuple(theme_names)):
            result_dict[row["theme_name"]].append({
                "flow_id": row["flow_id"],
                "flow_file": row["flow_file"],
                "relevance_order": row["relevance_order"]
            })
        
        return result_dict
    
    # Theme Evolution Tracking
    
    def log_theme_evolution(
        self,
        theme_name: str,
        change_type: str,
        change_details: Dict[str, Any],
        session_id: str = None
    ) -> bool:
        """
        Log theme evolution for tracking theme changes over time.
        
        Args:
            theme_name: Theme name
            change_type: Type of change (created, modified, deleted, files_added, files_removed)
            change_details: JSON with specific changes
            session_id: Optional session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                INSERT INTO theme_evolution (
                    theme_name, change_type, change_details, session_id
                ) VALUES (?, ?, ?, ?)
            """
            
            self.db.execute_update(query, (
                theme_name, change_type, json.dumps(change_details), session_id
            ))
            return True
            
        except Exception as e:
            self.db.logger.error(f"Error logging theme evolution: {e}")
            return False
    
    def get_theme_evolution_history(
        self,
        theme_name: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get theme evolution history."""
        query = """
            SELECT change_type, change_details, session_id, timestamp
            FROM theme_evolution
            WHERE theme_name = ? 
            AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
        """.format(days)
        
        results = []
        for row in self.db.execute_query(query, (theme_name,)):
            results.append({
                "change_type": row["change_type"],
                "change_details": json.loads(row["change_details"]) if row["change_details"] else {},
                "session_id": row["session_id"],
                "timestamp": row["timestamp"]
            })
        
        return results
    
    # Analytics and Performance
    
    def get_flow_completion_analytics(self, theme_name: str = None) -> Dict[str, Any]:
        """Get flow completion analytics."""
        base_query = "FROM flow_status"
        params = []
        
        if theme_name:
            base_query += """ 
                WHERE JSON_EXTRACT(primary_themes, '$') LIKE '%"' || ? || '"%'
                   OR JSON_EXTRACT(secondary_themes, '$') LIKE '%"' || ? || '"%'
            """
            params = [theme_name, theme_name]
        
        # Total flows
        total_query = f"SELECT COUNT(*) as count {base_query}"
        total_flows = self.db.execute_query(total_query, tuple(params))[0]["count"]
        
        # Flows by status
        status_query = f"""
            SELECT status, COUNT(*) as count {base_query}
            GROUP BY status
        """
        
        status_counts = {row["status"]: row["count"] 
                        for row in self.db.execute_query(status_query, tuple(params))}
        
        # Average completion percentage
        avg_completion_query = f"""
            SELECT AVG(completion_percentage) as avg_completion {base_query}
        """
        avg_completion = self.db.execute_query(avg_completion_query, tuple(params))[0]["avg_completion"]
        
        return {
            "total_flows": total_flows,
            "flows_by_status": status_counts,
            "avg_completion_percentage": round(avg_completion or 0, 1),
            "theme_filter": theme_name
        }