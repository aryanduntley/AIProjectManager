"""
Event Logging and Management Tools for the AI Project Manager MCP Server.

Provides database-backed noteworthy event management, replacing the file-based
noteworthy.json system with intelligent event tracking and analytics.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.mcp_api import ToolDefinition
from database.event_queries import EventQueries

logger = logging.getLogger(__name__)


class LogTools:
    """Event logging and management tools with database integration."""
    
    def __init__(self, event_queries: Optional[EventQueries] = None):
        """Initialize with event queries for database operations."""
        self.event_queries = event_queries
    
    async def get_tools(self) -> List[ToolDefinition]:
        """Get available event logging and management tools."""
        return [
            ToolDefinition(
                name="log_event",
                description="Create a noteworthy event (replaces adding to noteworthy.json)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "event_type": {
                            "type": "string",
                            "enum": ["decision", "pivot", "issue", "milestone", "completion"],
                            "description": "Type of noteworthy event"
                        },
                        "title": {
                            "type": "string",
                            "description": "Brief title for the event"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the event"
                        },
                        "primary_theme": {
                            "type": "string",
                            "description": "Primary theme associated with the event"
                        },
                        "related_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional related themes"
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Related task ID if applicable"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Current session ID"
                        },
                        "impact_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "default": "medium",
                            "description": "Impact level of the event"
                        },
                        "decision_data": {
                            "type": "object",
                            "description": "Decision reasoning and options (for decision events)"
                        },
                        "ai_reasoning": {
                            "type": "string",
                            "description": "AI's reasoning for the decision or action"
                        },
                        "user_feedback": {
                            "type": "string",
                            "description": "User input or feedback on the event"
                        }
                    },
                    "required": ["event_type", "title", "description"]
                },
                handler=self.log_event
            ),
            ToolDefinition(
                name="get_recent_events",
                description="Get recent noteworthy events (replaces reading noteworthy.json)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "default": 20,
                            "description": "Maximum number of events to retrieve"
                        },
                        "event_type": {
                            "type": "string",
                            "enum": ["decision", "pivot", "issue", "milestone", "completion"],
                            "description": "Filter by event type"
                        },
                        "primary_theme": {
                            "type": "string",
                            "description": "Filter by primary theme"
                        }
                    }
                },
                handler=self.get_recent_events
            ),
            ToolDefinition(
                name="update_event_outcome",
                description="Update an event with outcome or resolution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "event_id": {
                            "type": "string",
                            "description": "ID of the event to update"
                        },
                        "outcome": {
                            "type": "string",
                            "description": "Outcome or resolution of the event"
                        },
                        "user_feedback": {
                            "type": "string",
                            "description": "Additional user feedback"
                        }
                    },
                    "required": ["event_id", "outcome"]
                },
                handler=self.update_event_outcome
            ),
            ToolDefinition(
                name="search_events",
                description="Search through event history by content",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for title, description, or reasoning"
                        },
                        "event_type": {
                            "type": "string",
                            "enum": ["decision", "pivot", "issue", "milestone", "completion"],
                            "description": "Filter by event type"
                        },
                        "impact_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Filter by impact level"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 25,
                            "description": "Maximum number of results"
                        }
                    },
                    "required": ["query"]
                },
                handler=self.search_events
            ),
            ToolDefinition(
                name="get_event_analytics",
                description="Get comprehensive event and decision analytics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "default": 30,
                            "description": "Number of days to analyze"
                        }
                    }
                },
                handler=self.get_event_analytics
            ),
            ToolDefinition(
                name="get_decision_history",
                description="Get project decision history for analysis",
                input_schema={
                    "type": "object",
                    "properties": {
                        "primary_theme": {
                            "type": "string",
                            "description": "Filter by primary theme"
                        },
                        "days": {
                            "type": "integer",
                            "default": 90,
                            "description": "Number of days to include"
                        }
                    }
                },
                handler=self.get_decision_history
            ),
            ToolDefinition(
                name="archive_old_events",
                description="Archive old events to maintain database performance",
                input_schema={
                    "type": "object",
                    "properties": {
                        "days_old": {
                            "type": "integer",
                            "default": 90,
                            "description": "Archive events older than this many days"
                        },
                        "max_active_events": {
                            "type": "integer",
                            "default": 1000,
                            "description": "Maximum number of active events to keep"
                        }
                    }
                },
                handler=self.archive_old_events
            )
        ]
    
    async def log_event(self, arguments: Dict[str, Any]) -> str:
        """Create a new noteworthy event."""
        try:
            if not self.event_queries:
                return "Event logging not available - database not initialized"
            
            # Prepare event data with current context
            event_data = {
                'event_type': arguments.get('event_type', 'decision'),
                'title': arguments['title'],
                'description': arguments['description'],
                'primary_theme': arguments.get('primary_theme'),
                'related_themes': arguments.get('related_themes', []),
                'task_id': arguments.get('task_id'),
                'session_id': arguments.get('session_id'),
                'impact_level': arguments.get('impact_level', 'medium'),
                'decision_data': arguments.get('decision_data', {}),
                'context_data': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'mcp_tool'
                },
                'ai_reasoning': arguments.get('ai_reasoning'),
                'user_feedback': arguments.get('user_feedback')
            }
            
            event_id = self.event_queries.create_event(event_data)
            
            return f"✅ Event logged: {event_id} - {arguments['title']}"
            
        except Exception as e:
            logger.error(f"Error logging event: {e}")
            return f"Error logging event: {str(e)}"
    
    async def get_recent_events(self, arguments: Dict[str, Any]) -> str:
        """Get recent noteworthy events."""
        try:
            if not self.event_queries:
                return "Event retrieval not available - database not initialized"
            
            limit = arguments.get('limit', 20)
            event_type = arguments.get('event_type')
            primary_theme = arguments.get('primary_theme')
            
            events = self.event_queries.get_recent_events(
                limit=limit,
                event_type=event_type,
                primary_theme=primary_theme
            )
            
            if not events:
                return "No recent events found"
            
            # Format events for display
            summary = f"📋 **Recent Events** ({len(events)} events)\n\n"
            
            for event in events:
                event_emoji = {
                    'decision': '🤔',
                    'pivot': '↩️',
                    'issue': '⚠️',
                    'milestone': '🎯',
                    'completion': '✅'
                }.get(event['event_type'], '📝')
                
                impact_emoji = {
                    'critical': '🚨',
                    'high': '❗',
                    'medium': 'ℹ️',
                    'low': '💭'
                }.get(event['impact_level'], 'ℹ️')
                
                summary += f"{event_emoji} **{event['title']}** {impact_emoji}\n"
                summary += f"*{event['event_type'].title()}* • "
                
                if event['primary_theme']:
                    summary += f"Theme: {event['primary_theme']} • "
                
                summary += f"*{event['created_at'][:19]}*\n"
                summary += f"{event['description'][:100]}{'...' if len(event['description']) > 100 else ''}\n"
                
                if event.get('outcome'):
                    summary += f"**Outcome**: {event['outcome']}\n"
                
                summary += "\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting recent events: {e}")
            return f"Error getting recent events: {str(e)}"
    
    async def update_event_outcome(self, arguments: Dict[str, Any]) -> str:
        """Update an event with outcome or resolution."""
        try:
            if not self.event_queries:
                return "Event updates not available - database not initialized"
            
            event_id = arguments['event_id']
            outcome = arguments['outcome']
            user_feedback = arguments.get('user_feedback')
            
            success = self.event_queries.update_event_outcome(
                event_id=event_id,
                outcome=outcome,
                user_feedback=user_feedback
            )
            
            if success:
                return f"✅ Updated event {event_id} with outcome"
            else:
                return f"❌ Failed to update event {event_id} (event not found?)"
            
        except Exception as e:
            logger.error(f"Error updating event outcome: {e}")
            return f"Error updating event: {str(e)}"
    
    async def search_events(self, arguments: Dict[str, Any]) -> str:
        """Search through event history."""
        try:
            if not self.event_queries:
                return "Event search not available - database not initialized"
            
            query = arguments['query']
            event_type = arguments.get('event_type')
            impact_level = arguments.get('impact_level')
            limit = arguments.get('limit', 25)
            
            events = self.event_queries.search_events(
                query=query,
                event_type=event_type,
                impact_level=impact_level,
                limit=limit
            )
            
            if not events:
                return f"No events found matching '{query}'"
            
            # Format search results
            summary = f"🔍 **Event Search Results** for '{query}' ({len(events)} found)\n\n"
            
            for event in events:
                event_emoji = {
                    'decision': '🤔',
                    'pivot': '↩️',
                    'issue': '⚠️',
                    'milestone': '🎯',
                    'completion': '✅'
                }.get(event['event_type'], '📝')
                
                summary += f"{event_emoji} **{event['title']}** ({event['event_id']})\n"
                summary += f"*{event['event_type'].title()}* • Impact: {event['impact_level']} • {event['created_at'][:19]}\n"
                
                # Highlight matching text (simple approach)
                description = event['description']
                if query.lower() in description.lower():
                    # Show context around match
                    query_pos = description.lower().find(query.lower())
                    start = max(0, query_pos - 50)
                    end = min(len(description), query_pos + len(query) + 50)
                    context = description[start:end]
                    if start > 0:
                        context = "..." + context
                    if end < len(description):
                        context = context + "..."
                    summary += f"...{context}...\n"
                else:
                    summary += f"{description[:100]}{'...' if len(description) > 100 else ''}\n"
                
                summary += "\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return f"Error searching events: {str(e)}"
    
    async def get_event_analytics(self, arguments: Dict[str, Any]) -> str:
        """Get comprehensive event analytics."""
        try:
            if not self.event_queries:
                return "Event analytics not available - database not initialized"
            
            days = arguments.get('days', 30)
            analytics = self.event_queries.get_event_analytics(days=days)
            
            if 'error' in analytics:
                return f"Error getting analytics: {analytics['error']}"
            
            # Format analytics summary
            summary = f"📊 **Event Analytics** (Last {days} days)\n\n"
            
            summary += f"**Overall Activity:**\n"
            summary += f"- Total Events: {analytics.get('total_events', 0)}\n"
            summary += f"- Active Events: {analytics.get('active_events', 0)}\n"
            summary += f"- Decision Resolution Rate: {analytics.get('decision_resolution_rate', 0):.1%}\n\n"
            
            # Event types
            event_types = analytics.get('event_types', {})
            if event_types:
                summary += "**Event Types:**\n"
                for event_type, count in event_types.items():
                    emoji = {
                        'decision': '🤔',
                        'pivot': '↩️',
                        'issue': '⚠️',
                        'milestone': '🎯',
                        'completion': '✅'
                    }.get(event_type, '📝')
                    summary += f"- {emoji} {event_type.title()}: {count}\n"
                summary += "\n"
            
            # Impact levels
            impact_levels = analytics.get('impact_levels', {})
            if impact_levels:
                summary += "**Impact Distribution:**\n"
                for impact, count in impact_levels.items():
                    emoji = {
                        'critical': '🚨',
                        'high': '❗',
                        'medium': 'ℹ️',
                        'low': '💭'
                    }.get(impact, 'ℹ️')
                    summary += f"- {emoji} {impact.title()}: {count}\n"
                summary += "\n"
            
            # Theme activity
            theme_activity = analytics.get('theme_activity', {})
            if theme_activity:
                summary += "**Most Active Themes:**\n"
                for theme, count in list(theme_activity.items())[:5]:
                    summary += f"- {theme}: {count} events\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting event analytics: {e}")
            return f"Error getting event analytics: {str(e)}"
    
    async def get_decision_history(self, arguments: Dict[str, Any]) -> str:
        """Get project decision history."""
        try:
            if not self.event_queries:
                return "Decision history not available - database not initialized"
            
            primary_theme = arguments.get('primary_theme')
            days = arguments.get('days', 90)
            
            decisions = self.event_queries.get_project_decision_history(
                primary_theme=primary_theme,
                days=days
            )
            
            if not decisions:
                filter_text = f" for theme '{primary_theme}'" if primary_theme else ""
                return f"No decisions found{filter_text} in the last {days} days"
            
            # Format decision history
            filter_text = f" for {primary_theme}" if primary_theme else ""
            summary = f"🤔 **Decision History**{filter_text} ({len(decisions)} decisions)\n\n"
            
            for decision in decisions:
                impact_emoji = {
                    'critical': '🚨',
                    'high': '❗',
                    'medium': 'ℹ️',
                    'low': '💭'
                }.get(decision['impact_level'], 'ℹ️')
                
                summary += f"{impact_emoji} **{decision['title']}**\n"
                summary += f"*{decision['created_at'][:19]}* • Impact: {decision['impact_level']}\n"
                
                if decision.get('ai_reasoning'):
                    summary += f"**Reasoning**: {decision['ai_reasoning'][:150]}{'...' if len(decision.get('ai_reasoning', '')) > 150 else ''}\n"
                
                if decision.get('outcome'):
                    summary += f"**Outcome**: {decision['outcome']}\n"
                elif decision.get('user_feedback'):
                    summary += f"**User Feedback**: {decision['user_feedback']}\n"
                
                summary += "\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting decision history: {e}")
            return f"Error getting decision history: {str(e)}"
    
    async def archive_old_events(self, arguments: Dict[str, Any]) -> str:
        """Archive old events to maintain performance."""
        try:
            if not self.event_queries:
                return "Event archiving not available - database not initialized"
            
            days_old = arguments.get('days_old', 90)
            max_active_events = arguments.get('max_active_events', 1000)
            
            from datetime import timedelta
            before_date = datetime.utcnow() - timedelta(days=days_old)
            
            archived_count = self.event_queries.archive_events(
                before_date=before_date,
                max_active_events=max_active_events
            )
            
            if archived_count > 0:
                return f"📦 Archived {archived_count} events older than {days_old} days"
            else:
                return f"ℹ️ No events needed archiving (under {max_active_events} active events)"
            
        except Exception as e:
            logger.error(f"Error archiving events: {e}")
            return f"Error archiving events: {str(e)}"