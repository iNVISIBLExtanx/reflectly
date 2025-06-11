"""
Simplified Emotional Graph for AI-Focused Reflectly
Represents and manages emotional state transitions with core AI functionality only.
"""
import datetime
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from models.search_algorithm import AStarSearch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionalGraph:
    """
    Simplified EmotionalGraph focused on AI search algorithms and emotional mapping.
    """
    
    def __init__(self, db):
        """
        Initialize the EmotionalGraph with a database connection.
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
        self.emotions_collection = db.emotional_states
        self.transitions_collection = db.emotional_transitions
        
        # Define positive and negative emotions
        self.positive_emotions = ['joy', 'surprise']
        self.negative_emotions = ['sadness', 'anger', 'fear', 'disgust']
        self.neutral_emotions = ['neutral']
        
        # Initialize A* search algorithm
        self.search_algorithm = AStarSearch(self)
        
    def record_emotion(self, user_email, emotion_data, entry_id=None):
        """
        Record an emotional state for a user.
        
        Args:
            user_email (str): The user's email
            emotion_data (dict): Emotion analysis data
            entry_id (str, optional): Associated journal entry ID
            
        Returns:
            str: ID of the recorded emotional state
        """
        # Create emotional state document
        emotion_state = {
            'user_email': user_email,
            'primary_emotion': emotion_data.get('primary_emotion', 'neutral'),
            'is_positive': emotion_data.get('is_positive', False),
            'emotion_scores': emotion_data.get('emotion_scores', {}),
            'entry_id': entry_id,
            'timestamp': datetime.datetime.now()
        }
        
        # Insert into database
        result = self.emotions_collection.insert_one(emotion_state)
        emotion_state_id = result.inserted_id
        
        # Get previous emotional state to create transition
        previous_state = self._get_previous_emotional_state(user_email, exclude_id=emotion_state_id)
        
        if previous_state:
            self._record_transition(
                user_email, 
                previous_state['primary_emotion'],
                emotion_data.get('primary_emotion', 'neutral'),
                previous_state['_id'],
                emotion_state_id
            )
        
        return str(emotion_state_id)
    
    def _get_previous_emotional_state(self, user_email, exclude_id=None):
        """
        Get the user's previous emotional state.
        
        Args:
            user_email (str): The user's email
            exclude_id: ID to exclude from the search
            
        Returns:
            dict: Previous emotional state or None
        """
        query = {'user_email': user_email}
        if exclude_id:
            query['_id'] = {'$ne': exclude_id}
            
        return self.emotions_collection.find_one(
            query,
            sort=[('timestamp', -1)]
        )
    
    def _record_transition(self, user_email, from_emotion, to_emotion, from_state_id, to_state_id):
        """
        Record a transition between emotional states.
        
        Args:
            user_email (str): The user's email
            from_emotion (str): Source emotion
            to_emotion (str): Target emotion
            from_state_id: Source state ID
            to_state_id: Target state ID
            
        Returns:
            str: ID of the recorded transition
        """
        transition = {
            'user_email': user_email,
            'from_emotion': from_emotion,
            'to_emotion': to_emotion,
            'from_state_id': str(from_state_id),
            'to_state_id': str(to_state_id),
            'timestamp': datetime.datetime.now(),
            'actions': self._get_default_actions(from_emotion, to_emotion)
        }
        
        result = self.transitions_collection.insert_one(transition)
        return str(result.inserted_id)
    
    def _get_default_actions(self, from_emotion, to_emotion):
        """Get default actions for a transition."""
        primary_action = {
            "description": self._get_default_action(from_emotion, to_emotion),
            "timestamp": datetime.datetime.now().isoformat(),
            "success_rate": 0.6
        }
        
        secondary_actions = [
            {
                "description": "Practice mindfulness and deep breathing",
                "timestamp": datetime.datetime.now().isoformat(),
                "success_rate": 0.5
            },
            {
                "description": "Engage in physical activity",
                "timestamp": datetime.datetime.now().isoformat(),
                "success_rate": 0.4
            }
        ]
        
        return [primary_action] + secondary_actions
    
    def _get_default_action(self, from_emotion, to_emotion):
        """Get a default action for a transition."""
        actions = {
            ('sadness', 'joy'): "Engage in activities you enjoy",
            ('sadness', 'neutral'): "Practice mindfulness",
            ('anger', 'joy'): "Channel energy into positive activities",
            ('anger', 'neutral'): "Take deep breaths and count to 10",
            ('fear', 'joy'): "Focus on positive outcomes",
            ('fear', 'neutral'): "Ground yourself in the present moment",
            ('disgust', 'joy'): "Focus on things you appreciate",
            ('disgust', 'neutral'): "Practice acceptance",
            ('neutral', 'joy'): "Engage in activities you enjoy",
            ('joy', 'neutral'): "Practice mindfulness",
        }
        
        return actions.get((from_emotion, to_emotion), "Reflect on your feelings")
    
    def get_emotion_history(self, user_email, limit=10):
        """Get the user's emotion history."""
        states = list(self.emotions_collection.find(
            {'user_email': user_email},
            sort=[('timestamp', -1)],
            limit=limit
        ))
        
        for state in states:
            state['_id'] = str(state['_id'])
            if 'timestamp' in state and isinstance(state['timestamp'], datetime.datetime):
                state['timestamp'] = state['timestamp'].isoformat()
        
        return states
    
    def get_suggested_actions(self, user_email, current_emotion):
        """Get suggested actions for transitioning from the current emotional state."""
        generic_suggestions = {
            'sadness': [
                "Reach out to a friend or family member",
                "Practice self-care activities",
                "Listen to uplifting music",
                "Take a short walk outside"
            ],
            'anger': [
                "Take deep breaths for a few minutes",
                "Write down your thoughts",
                "Engage in physical activity",
                "Practice mindfulness meditation"
            ],
            'fear': [
                "Focus on your breathing",
                "Challenge negative thoughts",
                "Talk to someone you trust",
                "Create a plan to address your concerns"
            ],
            'disgust': [
                "Redirect your attention to something positive",
                "Practice acceptance",
                "Engage in a pleasant activity",
                "Connect with supportive people"
            ],
            'neutral': [
                "Set a goal for today",
                "Practice gratitude",
                "Learn something new",
                "Connect with nature"
            ],
            'joy': [
                "Share your positive experience with others",
                "Practice gratitude",
                "Savor the moment",
                "Set new goals"
            ],
            'surprise': [
                "Reflect on what surprised you",
                "Consider what you can learn from this experience",
                "Share your experience with others",
                "Use this energy for creative activities"
            ]
        }
        
        return generic_suggestions.get(current_emotion, generic_suggestions['neutral'])
    
    def get_emotional_path(self, user_email, current_emotion, target_emotion, max_depth=10):
        """
        Get a path from current_emotion to target_emotion using A* search.
        
        Args:
            user_email (str): The user's email
            current_emotion (str): Current emotional state
            target_emotion (str): Target emotional state
            max_depth (int): Maximum path depth
            
        Returns:
            dict: Path information
        """
        logger.info(f"Finding optimal path for user {user_email} from {current_emotion} to {target_emotion}")
        return self.search_algorithm.find_path(user_email, current_emotion, target_emotion, max_depth)
    
    def get_user_transitions(self, user_email):
        """Get all transitions for a user."""
        transitions = list(self.transitions_collection.find({'user_email': user_email}))
        
        for transition in transitions:
            transition['_id'] = str(transition['_id'])
            if 'timestamp' in transition and isinstance(transition['timestamp'], datetime.datetime):
                transition['timestamp'] = transition['timestamp'].isoformat()
        
        return transitions
    
    def get_available_emotions(self):
        """Get available emotions."""
        return self.positive_emotions + self.negative_emotions + self.neutral_emotions
    
    def get_successful_transitions(self, user_email):
        """Get successful transitions for a user."""
        transitions = self.get_user_transitions(user_email)
        successful_transitions = {}
        
        for transition in transitions:
            from_emotion = transition.get("from_emotion")
            to_emotion = transition.get("to_emotion")
            actions = transition.get("actions", [])
            
            if not from_emotion or not to_emotion or not actions:
                continue
                
            success_rates = [action.get("success_rate", 0.5) for action in actions if isinstance(action, dict)]
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.5
            
            transition_key = f"{from_emotion}_{to_emotion}"
            if transition_key not in successful_transitions or avg_success_rate > successful_transitions[transition_key].get("success_rate", 0):
                successful_transitions[transition_key] = {
                    "from_emotion": from_emotion,
                    "to_emotion": to_emotion,
                    "success_rate": avg_success_rate,
                    "actions": actions
                }
                
        return successful_transitions
