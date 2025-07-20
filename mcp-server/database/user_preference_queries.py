"""
User Preference Queries for AI Project Manager Database.

Handles user preference learning, adaptation tracking, and behavioral analytics
to enable intelligent AI adaptation to user workflow patterns.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class UserPreferenceQueries:
    """Database queries for user preference learning and AI adaptation."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db_manager = db_manager
        
    def learn_context_preference(self, context_data: Dict[str, Any]) -> str:
        """Learn user's context loading preferences from behavior."""
        try:
            preference_key = f"context_mode_{context_data.get('task_type', 'general')}"
            preferred_mode = context_data.get('final_mode')
            context_info = json.dumps({
                "task_description": context_data.get('task_description', ''),
                "escalated_from": context_data.get('initial_mode'),
                "escalated_to": preferred_mode,
                "session_id": context_data.get('session_id'),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Check if preference exists
            existing = self.db_manager.execute(
                "SELECT * FROM user_preferences WHERE preference_key = ?",
                (preference_key,)
            )
            
            if existing:
                # Update confidence score based on consistency
                current_value = existing[0]['preference_value']
                if current_value == preferred_mode:
                    # Increase confidence for consistent choice
                    new_confidence = min(existing[0]['confidence_score'] + 0.1, 1.0)
                else:
                    # Decrease confidence for inconsistent choice, then update
                    new_confidence = max(existing[0]['confidence_score'] - 0.2, 0.1)
                
                self.db_manager.execute("""
                    UPDATE user_preferences 
                    SET preference_value = ?, confidence_score = ?, 
                        context = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE preference_key = ?
                """, (preferred_mode, new_confidence, context_info, preference_key))
            else:
                # Create new preference
                self.db_manager.execute("""
                    INSERT INTO user_preferences 
                    (preference_key, preference_value, context, confidence_score)
                    VALUES (?, ?, ?, 0.6)
                """, (preference_key, preferred_mode, context_info))
            
            return f"Learned context preference: {preferred_mode} for {context_data.get('task_type', 'general')} tasks"
            
        except Exception as e:
            logger.error(f"Error learning context preference: {e}")
            return f"Error learning preference: {str(e)}"
    
    def learn_theme_preference(self, theme_data: Dict[str, Any]) -> str:
        """Learn user's theme organization preferences."""
        try:
            preference_key = f"theme_organization_{theme_data.get('domain', 'general')}"
            preferred_structure = json.dumps({
                "preferred_themes": theme_data.get('selected_themes', []),
                "avoided_themes": theme_data.get('avoided_themes', []),
                "cross_theme_patterns": theme_data.get('cross_theme_usage', {})
            })
            
            context_info = json.dumps({
                "project_type": theme_data.get('project_type'),
                "decision_context": theme_data.get('context'),
                "session_id": theme_data.get('session_id'),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.db_manager.execute("""
                INSERT OR REPLACE INTO user_preferences
                (preference_key, preference_value, context, confidence_score)
                VALUES (?, ?, ?, 0.7)
            """, (preference_key, preferred_structure, context_info))
            
            return f"Learned theme preference for {theme_data.get('domain')} domain"
            
        except Exception as e:
            logger.error(f"Error learning theme preference: {e}")
            return f"Error learning theme preference: {str(e)}"
    
    def learn_workflow_preference(self, workflow_data: Dict[str, Any]) -> str:
        """Learn user's workflow and task management preferences."""
        try:
            workflow_type = workflow_data.get('workflow_type', 'general')
            preference_key = f"workflow_{workflow_type}"
            
            workflow_pattern = {
                "typical_sequence": workflow_data.get('task_sequence', []),
                "preferred_batch_size": workflow_data.get('batch_size', 3),
                "escalation_threshold": workflow_data.get('escalation_threshold', 0.7),
                "sidequest_tolerance": workflow_data.get('sidequest_tolerance', 2),
                "context_switching_frequency": workflow_data.get('context_switches', 0)
            }
            
            context_info = json.dumps({
                "session_duration": workflow_data.get('session_duration_minutes'),
                "completion_rate": workflow_data.get('completion_rate'),
                "session_id": workflow_data.get('session_id'),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.db_manager.execute("""
                INSERT OR REPLACE INTO user_preferences
                (preference_key, preference_value, context, confidence_score)
                VALUES (?, ?, ?, 0.5)
            """, (preference_key, json.dumps(workflow_pattern), context_info))
            
            return f"Learned workflow preference: {workflow_type}"
            
        except Exception as e:
            logger.error(f"Error learning workflow preference: {e}")
            return f"Error learning workflow preference: {str(e)}"
    
    def get_context_recommendations(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get context mode recommendations based on learned preferences."""
        try:
            task_type = self._classify_task_type(task_context.get('description', ''))
            preference_key = f"context_mode_{task_type}"
            
            preference = self.db_manager.execute(
                "SELECT preference_value, confidence_score FROM user_preferences WHERE preference_key = ?",
                (preference_key,)
            )
            
            if preference and preference[0]['confidence_score'] > 0.6:
                return {
                    "recommended_mode": preference[0]['preference_value'],
                    "confidence": preference[0]['confidence_score'],
                    "reason": f"Based on learned preferences for {task_type} tasks",
                    "should_suggest": True
                }
            
            # Fallback to pattern-based recommendation
            description = task_context.get('description', '').lower()
            
            if any(word in description for word in ['integration', 'cross', 'shared', 'between']):
                return {
                    "recommended_mode": "theme-expanded",
                    "confidence": 0.7,
                    "reason": "Task appears to involve cross-theme integration",
                    "should_suggest": True
                }
            elif any(word in description for word in ['architecture', 'refactor', 'migrate', 'global']):
                return {
                    "recommended_mode": "project-wide", 
                    "confidence": 0.8,
                    "reason": "Task appears to be architectural or global in scope",
                    "should_suggest": True
                }
            else:
                return {
                    "recommended_mode": "theme-focused",
                    "confidence": 0.5,
                    "reason": "Default recommendation - no specific patterns detected",
                    "should_suggest": False
                }
                
        except Exception as e:
            logger.error(f"Error getting context recommendations: {e}")
            return {
                "recommended_mode": "theme-focused",
                "confidence": 0.5,
                "reason": f"Error in recommendation system: {str(e)}",
                "should_suggest": False
            }
    
    def get_theme_recommendations(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get theme organization recommendations based on learned preferences."""
        try:
            domain = project_context.get('domain', 'general')
            preference_key = f"theme_organization_{domain}"
            
            preference = self.db_manager.execute(
                "SELECT preference_value, confidence_score FROM user_preferences WHERE preference_key = ?",
                (preference_key,)
            )
            
            recommendations = {
                "suggested_themes": [],
                "avoid_themes": [],
                "cross_theme_suggestions": {},
                "confidence": 0.5
            }
            
            if preference and preference[0]['confidence_score'] > 0.5:
                pref_data = json.loads(preference[0]['preference_value'])
                recommendations.update({
                    "suggested_themes": pref_data.get('preferred_themes', []),
                    "avoid_themes": pref_data.get('avoided_themes', []),
                    "cross_theme_suggestions": pref_data.get('cross_theme_patterns', {}),
                    "confidence": preference[0]['confidence_score']
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting theme recommendations: {e}")
            return {
                "suggested_themes": [],
                "avoid_themes": [],
                "cross_theme_suggestions": {},
                "confidence": 0.0,
                "error": str(e)
            }
    
    def get_workflow_recommendations(self, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get workflow recommendations based on learned preferences."""
        try:
            workflow_type = session_context.get('workflow_type', 'general')
            preference_key = f"workflow_{workflow_type}"
            
            preference = self.db_manager.execute(
                "SELECT preference_value, confidence_score FROM user_preferences WHERE preference_key = ?",
                (preference_key,)
            )
            
            if preference and preference[0]['confidence_score'] > 0.4:
                workflow_data = json.loads(preference[0]['preference_value'])
                return {
                    "recommended_batch_size": workflow_data.get('preferred_batch_size', 3),
                    "escalation_threshold": workflow_data.get('escalation_threshold', 0.7),
                    "sidequest_tolerance": workflow_data.get('sidequest_tolerance', 2),
                    "typical_sequence": workflow_data.get('typical_sequence', []),
                    "confidence": preference[0]['confidence_score']
                }
            
            # Default workflow recommendations
            return {
                "recommended_batch_size": 3,
                "escalation_threshold": 0.7,
                "sidequest_tolerance": 2,
                "typical_sequence": [],
                "confidence": 0.3
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow recommendations: {e}")
            return {
                "recommended_batch_size": 3,
                "escalation_threshold": 0.7,
                "sidequest_tolerance": 2,
                "typical_sequence": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def track_decision_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """Track user feedback on AI decisions for preference learning."""
        try:
            decision_type = feedback_data.get('decision_type')
            user_approval = feedback_data.get('approved', True)
            
            # Learn from positive and negative feedback
            if decision_type == 'context_escalation':
                context_data = {
                    'task_type': feedback_data.get('task_type', 'general'),
                    'final_mode': feedback_data.get('suggested_mode') if user_approval else feedback_data.get('user_preferred_mode'),
                    'initial_mode': feedback_data.get('initial_mode'),
                    'task_description': feedback_data.get('task_description', ''),
                    'session_id': feedback_data.get('session_id')
                }
                return self.learn_context_preference(context_data)
            
            elif decision_type == 'theme_selection':
                theme_data = {
                    'domain': feedback_data.get('domain', 'general'),
                    'selected_themes': feedback_data.get('themes') if user_approval else feedback_data.get('user_selected_themes'),
                    'context': feedback_data.get('context'),
                    'session_id': feedback_data.get('session_id')
                }
                return self.learn_theme_preference(theme_data)
            
            # Track general feedback
            preference_key = f"feedback_{decision_type}"
            feedback_value = json.dumps({
                "approval_rate": 1.0 if user_approval else 0.0,
                "context": feedback_data.get('context', ''),
                "details": feedback_data.get('details', '')
            })
            
            self.db_manager.execute("""
                INSERT INTO user_preferences
                (preference_key, preference_value, context, confidence_score)
                VALUES (?, ?, ?, 0.4)
            """, (preference_key, feedback_value, json.dumps(feedback_data)))
            
            return f"Tracked feedback for {decision_type}: {'positive' if user_approval else 'negative'}"
            
        except Exception as e:
            logger.error(f"Error tracking decision feedback: {e}")
            return f"Error tracking feedback: {str(e)}"
    
    def get_user_adaptation_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of user adaptation and learning over time period."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all preferences within time range
            preferences = self.db_manager.execute("""
                SELECT preference_key, preference_value, confidence_score, 
                       created_at, updated_at
                FROM user_preferences 
                WHERE updated_at >= ?
                ORDER BY updated_at DESC
            """, (cutoff_date,))
            
            summary = {
                "learning_period_days": days,
                "total_preferences": len(preferences),
                "high_confidence_preferences": 0,
                "medium_confidence_preferences": 0,
                "low_confidence_preferences": 0,
                "preference_categories": {},
                "adaptation_insights": []
            }
            
            for pref in preferences:
                confidence = pref['confidence_score']
                if confidence >= 0.8:
                    summary["high_confidence_preferences"] += 1
                elif confidence >= 0.5:
                    summary["medium_confidence_preferences"] += 1
                else:
                    summary["low_confidence_preferences"] += 1
                
                # Categorize preferences
                pref_type = pref['preference_key'].split('_')[0]
                if pref_type not in summary["preference_categories"]:
                    summary["preference_categories"][pref_type] = 0
                summary["preference_categories"][pref_type] += 1
            
            # Generate insights
            if summary["high_confidence_preferences"] > 5:
                summary["adaptation_insights"].append("AI has learned strong user preferences in multiple areas")
            
            if summary["preference_categories"].get("context", 0) > 3:
                summary["adaptation_insights"].append("Context loading preferences are well-established")
            
            if summary["preference_categories"].get("workflow", 0) > 2:
                summary["adaptation_insights"].append("Workflow patterns have been identified")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting adaptation summary: {e}")
            return {"error": str(e)}
    
    def _classify_task_type(self, description: str) -> str:
        """Classify task type based on description for preference learning."""
        description = description.lower()
        
        if any(word in description for word in ['bug', 'fix', 'error', 'debug']):
            return 'debugging'
        elif any(word in description for word in ['feature', 'implement', 'add', 'create']):
            return 'feature_development'
        elif any(word in description for word in ['refactor', 'clean', 'optimize', 'improve']):
            return 'refactoring'
        elif any(word in description for word in ['test', 'testing', 'coverage', 'unit']):
            return 'testing'
        elif any(word in description for word in ['config', 'setup', 'initialize', 'install']):
            return 'configuration'
        elif any(word in description for word in ['document', 'docs', 'readme', 'comment']):
            return 'documentation'
        else:
            return 'general'
    
    def export_preferences(self) -> Dict[str, Any]:
        """Export all user preferences for backup or analysis."""
        try:
            preferences = self.db_manager.execute("""
                SELECT preference_key, preference_value, context, confidence_score,
                       created_at, updated_at
                FROM user_preferences
                ORDER BY preference_key
            """)
            
            return {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_preferences": len(preferences),
                "preferences": preferences
            }
            
        except Exception as e:
            logger.error(f"Error exporting preferences: {e}")
            return {"error": str(e)}
    
    def import_preferences(self, preferences_data: Dict[str, Any]) -> str:
        """Import user preferences from backup or external source."""
        try:
            imported_count = 0
            
            for pref in preferences_data.get('preferences', []):
                self.db_manager.execute("""
                    INSERT OR REPLACE INTO user_preferences
                    (preference_key, preference_value, context, confidence_score)
                    VALUES (?, ?, ?, ?)
                """, (
                    pref['preference_key'],
                    pref['preference_value'], 
                    pref['context'],
                    pref['confidence_score']
                ))
                imported_count += 1
            
            return f"Imported {imported_count} user preferences successfully"
            
        except Exception as e:
            logger.error(f"Error importing preferences: {e}")
            return f"Error importing preferences: {str(e)}"