"""
Event Queries for AI Project Manager Database.

Handles noteworthy events, decision tracking, and event analytics
to replace the file-based noteworthy.json system with database intelligence.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class EventQueries:
    """Database queries for noteworthy events and decision tracking."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db_manager = db_manager
        
    def create_event(self, event_data: Dict[str, Any]) -> str:
        """Create a new noteworthy event in the database."""
        try:
            # Generate event ID if not provided
            event_id = event_data.get('event_id')
            if not event_id:
                timestamp = datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')
                event_id = f"event-{timestamp}"
            
            # Prepare event data
            title = event_data.get('title', 'Untitled Event')
            description = event_data.get('description', 'No description provided')
            event_type = event_data.get('event_type', 'decision')
            primary_theme = event_data.get('primary_theme')
            related_themes = json.dumps(event_data.get('related_themes', []))
            task_id = event_data.get('task_id')
            session_id = event_data.get('session_id')
            impact_level = event_data.get('impact_level', 'medium')
            
            # Decision and context data
            decision_data = json.dumps(event_data.get('decision_data', {}))
            context_data = json.dumps(event_data.get('context_data', {}))
            user_feedback = event_data.get('user_feedback')
            ai_reasoning = event_data.get('ai_reasoning')
            outcome = event_data.get('outcome')
            
            # Insert into database
            self.db_manager.execute("""
                INSERT INTO noteworthy_events 
                (event_id, event_type, title, description, primary_theme, related_themes,
                 task_id, session_id, impact_level, decision_data, context_data,
                 user_feedback, ai_reasoning, outcome)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, event_type, title, description, primary_theme, related_themes,
                task_id, session_id, impact_level, decision_data, context_data,
                user_feedback, ai_reasoning, outcome
            ))
            
            logger.info(f"Created event {event_id}: {title}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            raise
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific event by ID."""
        try:
            result = self.db_manager.execute(
                "SELECT * FROM noteworthy_events WHERE event_id = ?",
                (event_id,)
            )
            
            if result:
                event = result[0]
                # Parse JSON fields
                event['related_themes'] = json.loads(event.get('related_themes', '[]'))
                event['decision_data'] = json.loads(event.get('decision_data', '{}'))
                event['context_data'] = json.loads(event.get('context_data', '{}'))
                return event
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting event {event_id}: {e}")
            return None
    
    def get_recent_events(self, limit: int = 50, event_type: Optional[str] = None,
                         primary_theme: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent events with optional filtering."""
        try:
            query = "SELECT * FROM recent_events"
            params = []
            conditions = []
            
            if event_type:
                conditions.append("event_type = ?")
                params.append(event_type)
            
            if primary_theme:
                conditions.append("primary_theme = ?")
                params.append(primary_theme)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.db_manager.execute(query, tuple(params))
            
            # Parse JSON fields for each event
            events = []
            for event in results:
                event_dict = dict(event)
                event_dict['related_themes'] = json.loads(event.get('related_themes', '[]'))
                event_dict['decision_data'] = json.loads(event.get('decision_data', '{}'))
                event_dict['context_data'] = json.loads(event.get('context_data', '{}'))
                events.append(event_dict)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting recent events: {e}")
            return []
    
    def update_event_outcome(self, event_id: str, outcome: str, 
                           user_feedback: Optional[str] = None) -> bool:
        """Update an event with outcome and optional user feedback."""
        try:
            params = [outcome]
            updates = ["outcome = ?"]
            
            if user_feedback:
                updates.append("user_feedback = ?")
                params.append(user_feedback)
            
            params.append(event_id)
            
            result = self.db_manager.execute(f"""
                UPDATE noteworthy_events 
                SET {', '.join(updates)}
                WHERE event_id = ?
            """, tuple(params))
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error updating event outcome: {e}")
            return False
    
    def create_event_relationship(self, parent_event_id: str, child_event_id: str,
                                relationship_type: str = 'causes') -> bool:
        """Create a relationship between two events."""
        try:
            self.db_manager.execute("""
                INSERT INTO event_relationships 
                (parent_event_id, child_event_id, relationship_type)
                VALUES (?, ?, ?)
            """, (parent_event_id, child_event_id, relationship_type))
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating event relationship: {e}")
            return False
    
    def get_event_relationships(self, event_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all relationships for an event (both parent and child)."""
        try:
            # Get events this event causes (children)
            children = self.db_manager.execute("""
                SELECT er.child_event_id, er.relationship_type, ne.title, ne.event_type
                FROM event_relationships er
                JOIN noteworthy_events ne ON er.child_event_id = ne.event_id
                WHERE er.parent_event_id = ?
                ORDER BY er.created_at
            """, (event_id,))
            
            # Get events that cause this event (parents)
            parents = self.db_manager.execute("""
                SELECT er.parent_event_id, er.relationship_type, ne.title, ne.event_type
                FROM event_relationships er
                JOIN noteworthy_events ne ON er.parent_event_id = ne.event_id
                WHERE er.child_event_id = ?
                ORDER BY er.created_at
            """, (event_id,))
            
            return {
                'causes': children,
                'caused_by': parents
            }
            
        except Exception as e:
            logger.error(f"Error getting event relationships: {e}")
            return {'causes': [], 'caused_by': []}
    
    def archive_events(self, before_date: Optional[datetime] = None,
                      max_active_events: int = 1000) -> int:
        """Archive old events to maintain database performance."""
        try:
            if not before_date:
                # Archive events older than 90 days by default
                before_date = datetime.utcnow() - timedelta(days=90)
            
            # Count current active events
            active_count = self.db_manager.execute(
                "SELECT COUNT(*) as count FROM noteworthy_events WHERE archived_at IS NULL"
            )[0]['count']
            
            if active_count <= max_active_events:
                return 0
            
            # Archive older events
            result = self.db_manager.execute("""
                UPDATE noteworthy_events 
                SET archived_at = CURRENT_TIMESTAMP
                WHERE created_at < ? AND archived_at IS NULL
            """, (before_date,))
            
            archived_count = self.db_manager.connection.total_changes
            logger.info(f"Archived {archived_count} events older than {before_date}")
            
            return archived_count
            
        except Exception as e:
            logger.error(f"Error archiving events: {e}")
            return 0
    
    def get_event_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive event analytics."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            analytics = {
                'time_period_days': days,
                'total_events': 0,
                'active_events': 0,
                'event_types': {},
                'impact_levels': {},
                'theme_activity': {},
                'decision_resolution_rate': 0.0,
                'recent_trends': {}
            }
            
            # Basic counts
            basic_stats = self.db_manager.execute("""
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN archived_at IS NULL THEN 1 END) as active_events,
                    COUNT(CASE WHEN event_type = 'decision' AND outcome IS NOT NULL THEN 1 END) as resolved_decisions,
                    COUNT(CASE WHEN event_type = 'decision' THEN 1 END) as total_decisions
                FROM noteworthy_events 
                WHERE created_at >= ?
            """, (cutoff_date,))
            
            if basic_stats:
                stats = basic_stats[0]
                analytics['total_events'] = stats['total_events']
                analytics['active_events'] = stats['active_events']
                
                # Decision resolution rate
                if stats['total_decisions'] > 0:
                    analytics['decision_resolution_rate'] = stats['resolved_decisions'] / stats['total_decisions']
            
            # Event type distribution
            event_types = self.db_manager.execute("""
                SELECT event_type, COUNT(*) as count
                FROM noteworthy_events 
                WHERE created_at >= ?
                GROUP BY event_type
                ORDER BY count DESC
            """, (cutoff_date,))
            
            analytics['event_types'] = {et['event_type']: et['count'] for et in event_types}
            
            # Impact level distribution
            impact_levels = self.db_manager.execute("""
                SELECT impact_level, COUNT(*) as count
                FROM noteworthy_events 
                WHERE created_at >= ?
                GROUP BY impact_level
                ORDER BY 
                    CASE impact_level 
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                    END
            """, (cutoff_date,))
            
            analytics['impact_levels'] = {il['impact_level']: il['count'] for il in impact_levels}
            
            # Theme activity
            theme_activity = self.db_manager.execute("""
                SELECT primary_theme, COUNT(*) as count
                FROM noteworthy_events 
                WHERE created_at >= ? AND primary_theme IS NOT NULL
                GROUP BY primary_theme
                ORDER BY count DESC
                LIMIT 10
            """, (cutoff_date,))
            
            analytics['theme_activity'] = {ta['primary_theme']: ta['count'] for ta in theme_activity}
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting event analytics: {e}")
            return {'error': str(e)}
    
    def search_events(self, query: str, event_type: Optional[str] = None,
                     impact_level: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search events by title, description, or AI reasoning."""
        try:
            sql_query = """
                SELECT * FROM noteworthy_events 
                WHERE (title LIKE ? OR description LIKE ? OR ai_reasoning LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%"]
            
            if event_type:
                sql_query += " AND event_type = ?"
                params.append(event_type)
            
            if impact_level:
                sql_query += " AND impact_level = ?"
                params.append(impact_level)
            
            sql_query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.db_manager.execute(sql_query, tuple(params))
            
            # Parse JSON fields
            events = []
            for event in results:
                event_dict = dict(event)
                event_dict['related_themes'] = json.loads(event.get('related_themes', '[]'))
                event_dict['decision_data'] = json.loads(event.get('decision_data', '{}'))
                event_dict['context_data'] = json.loads(event.get('context_data', '{}'))
                events.append(event_dict)
            
            return events
            
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return []
    
    def get_project_decision_history(self, primary_theme: Optional[str] = None,
                                   days: int = 90) -> List[Dict[str, Any]]:
        """Get decision history for project or theme analysis."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = """
                SELECT event_id, title, description, decision_data, ai_reasoning,
                       user_feedback, outcome, created_at, impact_level
                FROM noteworthy_events 
                WHERE event_type = 'decision' AND created_at >= ?
            """
            params = [cutoff_date]
            
            if primary_theme:
                query += " AND primary_theme = ?"
                params.append(primary_theme)
            
            query += " ORDER BY created_at DESC"
            
            results = self.db_manager.execute(query, tuple(params))
            
            decisions = []
            for decision in results:
                decision_dict = dict(decision)
                decision_dict['decision_data'] = json.loads(decision.get('decision_data', '{}'))
                decisions.append(decision_dict)
            
            return decisions
            
        except Exception as e:
            logger.error(f"Error getting decision history: {e}")
            return []
    
    def export_events_for_archival(self, before_date: datetime) -> List[Dict[str, Any]]:
        """Export events for file-based archival (mimics old noteworthy.json format)."""
        try:
            results = self.db_manager.execute("""
                SELECT * FROM noteworthy_events 
                WHERE created_at < ? OR archived_at IS NOT NULL
                ORDER BY created_at DESC
            """, (before_date,))
            
            archived_events = []
            for event in results:
                # Convert to noteworthy.json compatible format
                archived_event = {
                    'eventId': event['event_id'],
                    'type': event['event_type'],
                    'timestamp': event['created_at'],
                    'title': event['title'],
                    'description': event['description'],
                    'primaryTheme': event['primary_theme'],
                    'relatedThemes': json.loads(event.get('related_themes', '[]')),
                    'impactLevel': event['impact_level'],
                    'decisionData': json.loads(event.get('decision_data', '{}')),
                    'contextData': json.loads(event.get('context_data', '{}')),
                    'aiReasoning': event['ai_reasoning'],
                    'userFeedback': event['user_feedback'],
                    'outcome': event['outcome']
                }
                
                # Remove None values
                archived_event = {k: v for k, v in archived_event.items() if v is not None}
                archived_events.append(archived_event)
            
            return archived_events
            
        except Exception as e:
            logger.error(f"Error exporting events for archival: {e}")
            return []
    
    def import_legacy_events(self, noteworthy_json_data: List[Dict[str, Any]]) -> int:
        """Import events from legacy noteworthy.json format."""
        try:
            imported_count = 0
            
            for legacy_event in noteworthy_json_data:
                try:
                    event_data = {
                        'event_id': legacy_event.get('eventId'),
                        'event_type': legacy_event.get('type', 'decision'),
                        'title': legacy_event.get('title', 'Imported Event'),
                        'description': legacy_event.get('description', ''),
                        'primary_theme': legacy_event.get('primaryTheme'),
                        'related_themes': legacy_event.get('relatedThemes', []),
                        'impact_level': legacy_event.get('impactLevel', 'medium'),
                        'decision_data': legacy_event.get('decisionData', {}),
                        'context_data': legacy_event.get('contextData', {}),
                        'ai_reasoning': legacy_event.get('aiReasoning'),
                        'user_feedback': legacy_event.get('userFeedback'),
                        'outcome': legacy_event.get('outcome')
                    }
                    
                    self.create_event(event_data)
                    imported_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error importing legacy event: {e}")
                    continue
            
            logger.info(f"Imported {imported_count} legacy events")
            return imported_count
            
        except Exception as e:
            logger.error(f"Error importing legacy events: {e}")
            return 0