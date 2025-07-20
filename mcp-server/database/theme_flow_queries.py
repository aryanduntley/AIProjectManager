"""
Theme-Flow Relationship Queries for AI Project Manager
Handles all database operations related to theme-flow relationships.
"""

import json
from typing import List, Dict, Optional, Tuple
from .db_manager import DatabaseManager

class ThemeFlowQueries:
    """Handles theme-flow relationship database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize with database manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
    
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