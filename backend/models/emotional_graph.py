import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

class EmotionalGraph:
    """
    Represents and manages emotional state transitions.
    Stores emotional states as nodes in a graph structure, with transitions between states as edges.
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
        previous_state = self._get_previous_emotional_state(user_email)
        
        if previous_state:
            self._record_transition(
                user_email, 
                previous_state['primary_emotion'],
                emotion_data.get('primary_emotion', 'neutral'),
                previous_state['_id'],
                emotion_state_id
            )
        
        return str(emotion_state_id)
    
    def _get_previous_emotional_state(self, user_email):
        """
        Get the user's previous emotional state.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Previous emotional state or None
        """
        # Find the most recent emotional state for this user
        return self.emotions_collection.find_one(
            {'user_email': user_email},
            sort=[('timestamp', -1)]  # Sort by timestamp descending
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
        # Create transition document
        transition = {
            'user_email': user_email,
            'from_emotion': from_emotion,
            'to_emotion': to_emotion,
            'from_state_id': str(from_state_id),
            'to_state_id': str(to_state_id),
            'timestamp': datetime.datetime.now()
        }
        
        # Insert into database
        result = self.transitions_collection.insert_one(transition)
        return str(result.inserted_id)
    
    def get_emotion_history(self, user_email, limit=10):
        """
        Get the user's emotion history.
        
        Args:
            user_email (str): The user's email
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of emotional states
        """
        # Find emotional states for this user
        states = list(self.emotions_collection.find(
            {'user_email': user_email},
            sort=[('timestamp', -1)],
            limit=limit
        ))
        
        # Convert ObjectId to string
        for state in states:
            state['_id'] = str(state['_id'])
        
        return states
    
    def get_suggested_actions(self, user_email, current_emotion):
        """
        Get suggested actions for transitioning from the current emotional state.
        This is a simplified implementation that returns generic suggestions.
        
        Args:
            user_email (str): The user's email
            current_emotion (str): Current emotional state
            
        Returns:
            list: List of suggested actions
        """
        # Define generic suggestions for each emotion type
        suggestions = {
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
        
        # Return suggestions for the current emotion, or default suggestions
        return suggestions.get(current_emotion, suggestions['neutral'])
