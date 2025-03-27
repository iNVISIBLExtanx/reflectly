"""
IntelligentAgent Module

This module implements an intelligent agent that manages user emotional states
and determines optimal actions and interventions based on current emotional state.
"""

import os
import json
import logging
import datetime
import uuid
from typing import Dict, List, Any, Optional, Tuple

# Import other models
from .emotion_analyzer import EmotionAnalyzer
from .probabilistic_reasoning import ProbabilisticReasoning
from .emotional_graph import EmotionalGraph

# Try to import dataset integrations
try:
    from .dataset.mental_health_integration import MentalHealthIntegration
    MENTAL_HEALTH_AVAILABLE = True
except ImportError:
    MENTAL_HEALTH_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState:
    """
    Represents the state of an intelligent agent, including current emotional state,
    target emotional state, and action plan.
    """
    
    def __init__(
        self, 
        user_email: str = None,
        current_emotion: str = 'neutral',
        target_emotion: str = None,
        action_plan: List[Dict[str, Any]] = None,
        current_action_index: int = 0,
        feedback_history: List[Dict[str, Any]] = None
    ):
        """
        Initialize agent state.
        
        Args:
            user_email: User's email for identification
            current_emotion: Current emotional state
            target_emotion: Target emotional state (goal)
            action_plan: List of actions to achieve the target state
            current_action_index: Index of the current action in the plan
            feedback_history: History of user feedback on actions
        """
        self.user_email = user_email
        self.current_emotion = current_emotion
        self.target_emotion = target_emotion or self._default_target_emotion(current_emotion)
        self.action_plan = action_plan or []
        self.current_action_index = current_action_index
        self.feedback_history = feedback_history or []
        self.state_id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.last_updated = self.created_at
    
    def _default_target_emotion(self, current_emotion: str) -> str:
        """
        Determine a default target emotion based on the current emotion.
        
        Args:
            current_emotion: Current emotional state
            
        Returns:
            A default target emotion
        """
        negative_emotions = ['sadness', 'anger', 'fear', 'disgust']
        
        # If current emotion is negative, default target is joy
        if current_emotion.lower() in negative_emotions:
            return 'joy'
        
        # Otherwise, maintain the current emotion or slightly enhance it
        return current_emotion
    
    def update_emotion(self, new_emotion: str):
        """
        Update the current emotional state.
        
        Args:
            new_emotion: New emotional state
        """
        self.current_emotion = new_emotion
        self.last_updated = datetime.datetime.now()
    
    def set_target_emotion(self, target_emotion: str):
        """
        Set the target emotional state.
        
        Args:
            target_emotion: Target emotional state
        """
        self.target_emotion = target_emotion
        self.last_updated = datetime.datetime.now()
    
    def set_action_plan(self, action_plan: List[Dict[str, Any]]):
        """
        Set the action plan.
        
        Args:
            action_plan: List of actions to take
        """
        self.action_plan = action_plan
        self.current_action_index = 0
        self.last_updated = datetime.datetime.now()
    
    def next_action(self) -> Dict[str, Any]:
        """
        Get the next action in the plan and advance the index.
        
        Returns:
            Next action to take
        """
        if not self.action_plan or self.current_action_index >= len(self.action_plan):
            return None
        
        action = self.action_plan[self.current_action_index]
        self.current_action_index += 1
        self.last_updated = datetime.datetime.now()
        
        return action
    
    def add_feedback(self, action_id: str, effective: bool, notes: str = None):
        """
        Add feedback about an action's effectiveness.
        
        Args:
            action_id: ID of the action
            effective: Whether the action was effective
            notes: Additional notes about the action
        """
        feedback = {
            'action_id': action_id,
            'effective': effective,
            'notes': notes,
            'timestamp': datetime.datetime.now()
        }
        
        self.feedback_history.append(feedback)
        self.last_updated = datetime.datetime.now()
    
    def reached_target(self) -> bool:
        """
        Check if the current emotional state matches the target state.
        
        Returns:
            True if target reached, False otherwise
        """
        return self.current_emotion.lower() == self.target_emotion.lower()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state to dictionary.
        
        Returns:
            Dictionary representation of state
        """
        return {
            'state_id': self.state_id,
            'user_email': self.user_email,
            'current_emotion': self.current_emotion,
            'target_emotion': self.target_emotion,
            'action_plan': self.action_plan,
            'current_action_index': self.current_action_index,
            'feedback_history': self.feedback_history,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """
        Create state from dictionary.
        
        Args:
            data: Dictionary representation of state
            
        Returns:
            AgentState object
        """
        state = cls(
            user_email=data.get('user_email'),
            current_emotion=data.get('current_emotion', 'neutral'),
            target_emotion=data.get('target_emotion'),
            action_plan=data.get('action_plan', []),
            current_action_index=data.get('current_action_index', 0),
            feedback_history=data.get('feedback_history', [])
        )
        
        # Set additional attributes
        state.state_id = data.get('state_id', str(uuid.uuid4()))
        
        # Convert ISO strings to datetime objects
        if 'created_at' in data:
            state.created_at = datetime.datetime.fromisoformat(data['created_at'])
        
        if 'last_updated' in data:
            state.last_updated = datetime.datetime.fromisoformat(data['last_updated'])
        
        return state


class IntelligentAgent:
    """
    Intelligent agent for managing user emotional states and determining optimal actions.
    """
    
    def __init__(self, user_email: str = None):
        """
        Initialize the intelligent agent.
        
        Args:
            user_email: User's email for personalization
        """
        self.user_email = user_email
        
        # Initialize components
        self.emotion_analyzer = EmotionAnalyzer(use_pretrained=True, use_iemocap=True)
        self.probabilistic_reasoning = ProbabilisticReasoning(user_email)
        # Use EmotionalGraphBigData if available, fall back to EmotionalGraph otherwise
        try:
            from .emotional_graph_bigdata import EmotionalGraphBigData
            self.emotional_graph = EmotionalGraphBigData(user_email=user_email)
            logger.info("Using enhanced EmotionalGraphBigData for user emotional tracking")
        except ImportError:
            logger.info("EmotionalGraphBigData not available, using basic EmotionalGraph")
            self.emotional_graph = EmotionalGraph()
        
        # Initialize mental health integration if available
        self.using_mental_health = MENTAL_HEALTH_AVAILABLE
        if self.using_mental_health:
            try:
                self.mental_health = MentalHealthIntegration()
            except Exception as e:
                logger.warning(f"Failed to initialize Mental Health integration: {e}")
                self.using_mental_health = False
        
        # Initialize agent state
        self.state = None
        if user_email:
            self._load_state()
    
    def _load_state(self):
        """
        Load agent state for the current user.
        """
        try:
            # In a production environment, this would load from a database
            # For this implementation, we create a new state
            self.state = AgentState(user_email=self.user_email)
            logger.info(f"Created new agent state for user {self.user_email}")
        except Exception as e:
            logger.error(f"Error loading agent state: {e}")
            self.state = None
    
    def _save_state(self):
        """
        Save agent state for the current user.
        """
        if not self.state:
            logger.warning("No agent state to save")
            return
        
        try:
            # In a production environment, this would save to a database
            # For this implementation, we just log the state
            logger.info(f"Saving agent state for user {self.user_email}")
        except Exception as e:
            logger.error(f"Error saving agent state: {e}")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text to determine emotional state.
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results including detected emotion
        """
        return self.emotion_analyzer.analyze(text)
    
    def update_emotional_state(self, emotion_data: Dict[str, Any], entry_id: str = None):
        """
        Update the agent's emotional state based on new data.
        
        Args:
            emotion_data: Emotion data from analysis
            entry_id: Associated journal entry ID (optional)
        """
        if not self.state:
            self._load_state()
        
        # Update current emotion
        if 'primary_emotion' in emotion_data:
            self.state.update_emotion(emotion_data['primary_emotion'])
        
        # Record emotion in emotional graph
        if self.user_email:
            self.emotional_graph.record_emotion(self.user_email, emotion_data, entry_id)
        
        # Update probabilistic models with new data
        try:
            # Get emotion history from emotional graph
            emotion_history = []
            if self.user_email:
                emotion_history = self.emotional_graph.get_emotion_history(self.user_email)
            
            # Update probabilistic reasoning with history
            self.probabilistic_reasoning.update_with_emotion_history(emotion_history)
        except Exception as e:
            logger.warning(f"Error updating probabilistic models: {e}")
        
        # Save updated state
        self._save_state()
    
    def set_target_emotion(self, target_emotion: str):
        """
        Set the target emotional state.
        
        Args:
            target_emotion: Target emotional state
        """
        if not self.state:
            self._load_state()
        
        self.state.set_target_emotion(target_emotion)
        self._generate_action_plan()
        self._save_state()
    
    def _generate_action_plan(self):
        """
        Generate an action plan to reach the target emotional state using A* search
        and probabilistic reasoning.
        """
        if not self.state:
            logger.warning("No agent state available")
            return
        
        try:
            current_emotion = self.state.current_emotion
            target_emotion = self.state.target_emotion
            
            # Get coordinates for current and target emotions
            current_coords = self.probabilistic_reasoning.get_emotion_coordinates(current_emotion)
            target_coords = self.probabilistic_reasoning.get_emotion_coordinates(target_emotion)
            
            # Try to find an optimal path using A* search
            optimal_path = self.find_emotional_path(current_emotion, target_emotion, max_steps=5)
            
            # Get emotional history for personalization
            emotion_history = []
            if self.user_email:
                emotion_history = self.emotional_graph.get_emotion_history(self.user_email, limit=10)
            
            # Generate action plan
            action_plan = []
            
            # If we have an optimal path with more than 1 step, use it to guide our plan
            if optimal_path and len(optimal_path) > 1:
                logger.info(f"Using optimal emotional path: {optimal_path}")
                
                # Add actions for each step in the optimal path
                for i in range(len(optimal_path) - 1):
                    from_emotion = optimal_path[i]['emotion']
                    to_emotion = optimal_path[i+1]['emotion']
                    
                    # Get effective interventions for this transition
                    interventions = self.probabilistic_reasoning.rank_interventions(from_emotion, limit=2)
                    
                    # Add suggested interventions from the path
                    if 'intervention' in optimal_path[i]:
                        path_intervention = {
                            'action_id': str(uuid.uuid4()),
                            'type': 'intervention',
                            'name': optimal_path[i]['intervention'],
                            'description': optimal_path[i].get('description', f"Try {optimal_path[i]['intervention']} to move from {from_emotion} to {to_emotion}"),
                            'effectiveness': optimal_path[i].get('effectiveness', 0.7),
                            'is_optimal_path': True,
                            'coordinates': {
                                'from': self.probabilistic_reasoning.get_emotion_coordinates(from_emotion),
                                'to': self.probabilistic_reasoning.get_emotion_coordinates(to_emotion)
                            }
                        }
                        action_plan.append(path_intervention)
                    
                    # Add other effective interventions
                    for intervention in interventions:
                        # Skip if similar to one we already added
                        if any(action['name'].lower() == intervention['intervention'].lower() for action in action_plan):
                            continue
                            
                        action = {
                            'action_id': str(uuid.uuid4()),
                            'type': 'intervention',
                            'name': intervention['intervention'],
                            'description': f"Try {intervention['intervention']} to help transition from {from_emotion} to {to_emotion}",
                            'effectiveness': intervention['effectiveness'],
                            'coordinates': {
                                'from': self.probabilistic_reasoning.get_emotion_coordinates(from_emotion),
                                'to': self.probabilistic_reasoning.get_emotion_coordinates(to_emotion)
                            }
                        }
                        action_plan.append(action)
            else:
                # Fallback: Get effective interventions for current emotion
                interventions = self.probabilistic_reasoning.rank_interventions(current_emotion, limit=3)
                
                # Add effective interventions as actions
                for intervention in interventions:
                    action = {
                        'action_id': str(uuid.uuid4()),
                        'type': 'intervention',
                        'name': intervention['intervention'],
                        'description': f"Try {intervention['intervention']} to help transition from {current_emotion} to {target_emotion}",
                        'effectiveness': intervention['effectiveness'],
                        'coordinates': {
                            'from': current_coords,
                            'to': target_coords
                        }
                    }
                    action_plan.append(action)
            
            # Add response templates if available
            if self.using_mental_health and hasattr(self, 'mental_health'):
                for action in action_plan:
                    if action['type'] == 'intervention':
                        templates = self.mental_health.get_response_templates(current_emotion)
                        if templates:
                            action['response_templates'] = templates[:3]  # Limit to 3 templates
            
            # Add additional suggested activities based on emotion
            activities = self._get_activities_for_emotion(current_emotion, target_emotion)
            for activity in activities:
                # Skip if we already have enough actions
                if len(action_plan) >= 6:
                    break
                    
                action_id = str(uuid.uuid4())
                action = {
                    'action_id': action_id,
                    'type': 'activity',
                    'name': activity['name'],
                    'description': activity['description'],
                    'effectiveness': activity.get('effectiveness', 0.6),
                    'duration': activity.get('duration', '15 minutes')
                }
                action_plan.append(action)
            
            # Set the action plan
            self.state.set_action_plan(action_plan)
            
        except Exception as e:
            logger.error(f"Error generating action plan: {e}")
    
    def _get_activities_for_emotion(self, current_emotion: str, target_emotion: str) -> List[Dict[str, Any]]:
        """
        Get suitable activities for transitioning between emotional states.
        
        Args:
            current_emotion: Current emotional state
            target_emotion: Target emotional state
            
        Returns:
            List of suitable activities
        """
        # Define activities for different emotional transitions
        activities = {
            'sadness': [
                {
                    'name': 'Physical Exercise',
                    'description': 'Go for a short walk or do light exercise to boost endorphins.',
                    'effectiveness': 0.7,
                    'duration': '20 minutes'
                },
                {
                    'name': 'Social Connection',
                    'description': 'Reach out to a friend or family member for a brief chat.',
                    'effectiveness': 0.75,
                    'duration': '15 minutes'
                },
                {
                    'name': 'Gratitude Journaling',
                    'description': 'Write down three things you are grateful for today.',
                    'effectiveness': 0.65,
                    'duration': '10 minutes'
                }
            ],
            'anger': [
                {
                    'name': 'Deep Breathing',
                    'description': 'Practice deep breathing exercises to calm your nervous system.',
                    'effectiveness': 0.8,
                    'duration': '5 minutes'
                },
                {
                    'name': 'Physical Release',
                    'description': 'Find a safe way to physically release tension, like a brisk walk or hitting a pillow.',
                    'effectiveness': 0.7,
                    'duration': '15 minutes'
                },
                {
                    'name': 'Reframing',
                    'description': 'Write down the situation that made you angry and try to reframe it from another perspective.',
                    'effectiveness': 0.6,
                    'duration': '10 minutes'
                }
            ],
            'fear': [
                {
                    'name': 'Grounding Technique',
                    'description': 'Use the 5-4-3-2-1 technique: name 5 things you see, 4 things you touch, 3 things you hear, 2 things you smell, and 1 thing you taste.',
                    'effectiveness': 0.8,
                    'duration': '5 minutes'
                },
                {
                    'name': 'Progressive Muscle Relaxation',
                    'description': 'Tense and release each muscle group in your body to reduce physical tension.',
                    'effectiveness': 0.75,
                    'duration': '10 minutes'
                },
                {
                    'name': 'Worry Time',
                    'description': 'Schedule a specific time to address your worries, and write them down now to revisit later.',
                    'effectiveness': 0.65,
                    'duration': '15 minutes'
                }
            ],
            'disgust': [
                {
                    'name': 'Sensory Reset',
                    'description': 'Engage with pleasant sensory experiences like smelling a nice scent or tasting something you enjoy.',
                    'effectiveness': 0.7,
                    'duration': '5 minutes'
                },
                {
                    'name': 'Cleansing Ritual',
                    'description': 'Wash your hands or face, take a shower, or tidy up your space.',
                    'effectiveness': 0.75,
                    'duration': '10 minutes'
                },
                {
                    'name': 'Compassion Practice',
                    'description': 'Practice self-compassion by acknowledging your feelings without judgment.',
                    'effectiveness': 0.65,
                    'duration': '10 minutes'
                }
            ],
            'neutral': [
                {
                    'name': 'Mindful Observation',
                    'description': 'Take a few minutes to mindfully observe your surroundings and notice details.',
                    'effectiveness': 0.6,
                    'duration': '5 minutes'
                },
                {
                    'name': 'Goal Setting',
                    'description': 'Set one small, achievable goal for the day or week.',
                    'effectiveness': 0.7,
                    'duration': '10 minutes'
                },
                {
                    'name': 'Creative Expression',
                    'description': 'Spend a few minutes drawing, writing, or engaging in another creative activity.',
                    'effectiveness': 0.65,
                    'duration': '15 minutes'
                }
            ],
            'joy': [
                {
                    'name': 'Savor the Moment',
                    'description': 'Take time to fully experience and appreciate your positive feelings.',
                    'effectiveness': 0.8,
                    'duration': '5 minutes'
                },
                {
                    'name': 'Share Your Joy',
                    'description': 'Share your positive feelings or good news with someone else.',
                    'effectiveness': 0.75,
                    'duration': '10 minutes'
                },
                {
                    'name': 'Capture the Feeling',
                    'description': 'Write down what brought you joy and how it made you feel to revisit later.',
                    'effectiveness': 0.7,
                    'duration': '10 minutes'
                }
            ],
            'surprise': [
                {
                    'name': 'Curiosity Exploration',
                    'description': 'Lean into your surprise by exploring what surprised you and why.',
                    'effectiveness': 0.7,
                    'duration': '10 minutes'
                },
                {
                    'name': 'Reflection',
                    'description': 'Reflect on how this surprise challenges your assumptions or expectations.',
                    'effectiveness': 0.65,
                    'duration': '10 minutes'
                },
                {
                    'name': 'Creative Response',
                    'description': 'Channel your surprise into a creative outlet like writing or drawing.',
                    'effectiveness': 0.6,
                    'duration': '15 minutes'
                }
            ]
        }
        
        # Use current emotion to select activities
        current_emotion = current_emotion.lower()
        
        # Map to known emotions
        emotion_mapping = {
            'happy': 'joy',
            'excited': 'joy',
            'sad': 'sadness',
            'depressed': 'sadness',
            'angry': 'anger',
            'frustrated': 'anger',
            'afraid': 'fear',
            'anxious': 'fear',
            'scared': 'fear',
            'surprised': 'surprise',
            'shocked': 'surprise',
            'disgusted': 'disgust',
            'repulsed': 'disgust',
            'calm': 'neutral',
            'balanced': 'neutral'
        }
        
        base_emotion = emotion_mapping.get(current_emotion, current_emotion)
        
        # Return activities for the emotion, or default to neutral if not found
        return activities.get(base_emotion, activities['neutral'])
    
    def get_next_action(self) -> Dict[str, Any]:
        """
        Get the next action in the plan.
        
        Returns:
            Next action to take
        """
        if not self.state:
            self._load_state()
            
        return self.state.next_action()
    
    def add_action_feedback(self, action_id: str, effective: bool, notes: str = None):
        """
        Add feedback about an action's effectiveness.
        
        Args:
            action_id: ID of the action
            effective: Whether the action was effective
            notes: Additional notes about the action
        """
        if not self.state:
            self._load_state()
            
        self.state.add_feedback(action_id, effective, notes)
        self._save_state()
    
    def predict_emotional_sequence(self, sequence_length: int = 5, include_metadata: bool = False) -> List[Any]:
        """
        Predict a sequence of future emotional states with rich metadata.
        
        Args:
            sequence_length: Length of the sequence to predict
            include_metadata: Whether to include detailed metadata
            
        Returns:
            List of predicted emotional states with optional metadata
        """
        if not self.state:
            self._load_state()
            
        if not self.state:
            logger.warning("No agent state available")
            return []
        
        try:
            current_emotion = self.state.current_emotion
            
            # Get emotion history for context
            emotion_history = []
            if self.user_email:
                emotion_history = self.emotional_graph.get_emotion_history(self.user_email, limit=10)
            
            # Get previous emotion if available
            previous_emotion = None
            if len(emotion_history) >= 2:
                previous_emotion = emotion_history[-2].get('emotion')
                
            # Get timestamp for time-dependent predictions
            timestamp = datetime.datetime.now()
            
            return self.probabilistic_reasoning.predict_emotional_sequence(
                current_emotion, 
                sequence_length=sequence_length,
                include_metadata=include_metadata,
                timestamp=timestamp
            )
        except Exception as e:
            logger.error(f"Error predicting emotional sequence: {e}")
            return []
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current agent state.
        
        Returns:
            Dictionary representation of the agent state with enhanced metadata
        """
        if not self.state:
            self._load_state()
            
        if not self.state:
            return {
                'error': 'No state available',
                'user_email': self.user_email
            }
        
        # Get basic state
        state_data = self.state.to_dict()
        
        # Add enhanced metadata
        try:
            current_emotion = self.state.current_emotion
            
            # Add emotional coordinates
            state_data['emotion_coordinates'] = self.probabilistic_reasoning.get_emotion_coordinates(current_emotion)
            
            # Add predicted next emotion with confidence
            next_emotion_data = self.probabilistic_reasoning.predict_next_emotion(current_emotion)
            state_data['predicted_next_emotion'] = next_emotion_data
            
            # Get emotion history for analysis
            emotion_history = []
            if self.user_email:
                emotion_history = self.emotional_graph.get_emotion_history(self.user_email, limit=10)
                
            # Add emotional stability/volatility metrics if we have enough history
            if len(emotion_history) >= 3:
                # Extract emotion sequence
                emotion_sequence = [entry.get('emotion', 'neutral') for entry in emotion_history]
                
                # Count unique transitions as a measure of volatility
                transitions = len(set(zip(emotion_sequence[:-1], emotion_sequence[1:])))
                stability_score = 1.0 - (transitions / max(1, len(emotion_sequence) - 1))
                state_data['emotional_stability'] = stability_score
                
                # Check for emotional anomalies
                anomalies = self.probabilistic_reasoning.detect_emotional_anomalies(emotion_sequence)
                if anomalies:
                    state_data['emotional_anomalies'] = anomalies
            
            # Add action effectiveness predictions
            if self.state.action_plan and len(self.state.action_plan) > 0:
                for action in state_data['action_plan']:
                    if 'name' in action:
                        effectiveness = self.probabilistic_reasoning.predict_intervention_effectiveness(
                            current_emotion, action['name']
                        )
                        action['predicted_effectiveness'] = effectiveness
        except Exception as e:
            logger.warning(f"Error enhancing state data: {e}")
        
        return state_data
    
    def generate_personalized_response(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a personalized response based on the user's input and emotional state.
        
        This method coordinates between multiple components:
        1. Analyzes the user's emotional state from text
        2. Updates the agent's state and history
        3. Plans appropriate interventions
        4. Generates contextually appropriate responses
        
        Args:
            user_input: Text input from the user
            context: Additional context (e.g., time of day, previous interactions)
            
        Returns:
            Response data with message, suggested activities, and metadata
        """
        if not user_input:
            return {
                'message': "I didn't receive any input. How are you feeling today?",
                'status': 'error'
            }
            
        try:
            # Analyze emotional state from text
            analysis = self.analyze_text(user_input)
            current_emotion = analysis.get('emotion', 'neutral')
            
            # Update agent state
            self.update_emotional_state(analysis)
            
            # Get emotion history
            emotion_history = []
            if self.user_email:
                emotion_history = self.emotional_graph.get_emotion_history(self.user_email, limit=10)
                
            # Analyze emotional journey
            journey_analysis = self.analyze_emotional_journey(emotion_history)
            
            # Get appropriate response templates
            response_templates = []
            if self.using_mental_health and hasattr(self, 'mental_health'):
                response_templates = self.mental_health.get_response_templates(current_emotion)
                
            # Choose a response template or create a default response
            if response_templates:
                response_message = response_templates[0]['template']
                
                # Personalize template with user details if available
                if self.user_email:
                    response_message = response_message.replace('[USER]', self.user_email.split('@')[0])
            else:
                # Default response based on emotional state
                emotion_responses = {
                    'joy': "You seem to be in good spirits! That's wonderful to hear.",
                    'sadness': "I notice you might be feeling down. Would you like to talk about it?",
                    'anger': "I sense some frustration in your message. Taking a deep breath might help.",
                    'fear': "You seem worried. Remember that addressing concerns one step at a time can help.",
                    'disgust': "It sounds like something's bothering you. Would talking about it help?",
                    'surprise': "That seems unexpected! How are you processing this situation?",
                    'neutral': "Thanks for sharing. How else are you feeling today?"
                }
                response_message = emotion_responses.get(
                    current_emotion, 
                    "Thank you for sharing. How else can I support you today?"
                )
            
            # Get next action if available
            next_action = self.get_next_action()
            
            # Build suggestion based on analysis
            suggestions = []
            if next_action:
                suggestions.append({
                    'action_id': next_action.get('action_id'),
                    'name': next_action.get('name'),
                    'description': next_action.get('description')
                })
            
            # Add predicted future emotions
            future_emotions = self.predict_emotional_sequence(3, include_metadata=True)
            
            return {
                'message': response_message,
                'detected_emotion': current_emotion,
                'emotion_confidence': analysis.get('confidence', 0.0),
                'suggestions': suggestions,
                'future_emotions': future_emotions,
                'journey_analysis': journey_analysis,
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"Error generating personalized response: {e}")
            return {
                'message': "I'm having trouble analyzing your message right now. How are you feeling today?",
                'status': 'error',
                'error': str(e)
            }
    
    def analyze_emotional_journey(self, emotion_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the user's emotional journey using the probabilistic reasoning component.
        
        Args:
            emotion_history: List of emotional states with timestamps
            
        Returns:
            Analysis results with patterns, anomalies, and insights
        """
        if not emotion_history or len(emotion_history) < 2:
            return {
                'status': 'insufficient_data',
                'message': 'Need more emotional data for journey analysis'
            }
            
        try:
            # Use the ProbabilisticReasoning analyze_emotional_journey method
            return self.probabilistic_reasoning.analyze_emotional_journey(emotion_history)
        except Exception as e:
            logger.error(f"Error analyzing emotional journey: {e}")
            return {
                'status': 'error',
                'message': 'Error analyzing emotional journey'
            }
    
    def detect_emotional_anomalies(self, sensitivity: float = 1.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in the user's emotional patterns that may require attention.
        
        Args:
            sensitivity: Adjustment factor for anomaly detection (higher = more sensitive)
            
        Returns:
            List of detected anomalies with metadata
        """
        try:
            # Get emotion history
            emotion_history = []
            if self.user_email:
                emotion_history = self.emotional_graph.get_emotion_history(self.user_email, limit=20)
                
            # Extract sequence of emotions
            emotion_sequence = [entry.get('emotion', 'neutral') for entry in emotion_history]
            
            # Use probabilistic reasoning to detect anomalies
            return self.probabilistic_reasoning.detect_emotional_anomalies(
                emotion_sequence, 
                sensitivity=sensitivity
            )
        except Exception as e:
            logger.error(f"Error detecting emotional anomalies: {e}")
            return []
    
    def find_emotional_path(
        self, 
        start_emotion: str, 
        target_emotion: str, 
        max_steps: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find a path from start emotion to target emotion.
        
        This uses an A* search algorithm to find the optimal path.
        
        Args:
            start_emotion: Starting emotional state
            target_emotion: Target emotional state
            max_steps: Maximum number of steps in the path
            
        Returns:
            List of steps in the path, including emotions and suggested interventions
        """
        try:
            # Initialize A* search
            start_coords = self.probabilistic_reasoning.get_emotion_coordinates(start_emotion)
            target_coords = self.probabilistic_reasoning.get_emotion_coordinates(target_emotion)
            
            # Define the emotion space (all possible emotions)
            emotions = [
                'joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust', 'neutral'
            ]
            
            # Get coordinates for all emotions
            emotion_coords = {}
            for emotion in emotions:
                emotion_coords[emotion] = self.probabilistic_reasoning.get_emotion_coordinates(emotion)
            
            # Define the heuristic function (Euclidean distance to target)
            def heuristic(emotion):
                coords = emotion_coords[emotion]
                return ((coords['x'] - target_coords['x'])**2 + (coords['y'] - target_coords['y'])**2)**0.5
            
            # Define the cost function (transition probability, inverted)
            def cost(from_emotion, to_emotion):
                # Get transition probability from Markov model
                # Higher probability means lower cost
                prob = 1.0
                if hasattr(self.probabilistic_reasoning.markov_model, 'transition_matrix'):
                    if from_emotion in self.probabilistic_reasoning.markov_model.transition_matrix:
                        if to_emotion in self.probabilistic_reasoning.markov_model.transition_matrix[from_emotion]:
                            prob = self.probabilistic_reasoning.markov_model.transition_matrix[from_emotion][to_emotion]
                
                # Invert probability to get cost (higher probability = lower cost)
                return 1.0 - prob
            
            # Initialize A* search
            open_set = {start_emotion}
            closed_set = set()
            
            # Track path and scores
            came_from = {}
            g_score = {emotion: float('inf') for emotion in emotions}
            g_score[start_emotion] = 0
            f_score = {emotion: float('inf') for emotion in emotions}
            f_score[start_emotion] = heuristic(start_emotion)
            
            # Track path steps
            steps = 0
            
            # A* search
            while open_set and steps < max_steps:
                # Get emotion with lowest f_score
                current = min(open_set, key=lambda e: f_score[e])
                
                # Check if we've reached the target
                if current == target_emotion:
                    # Reconstruct path
                    path = []
                    while current in came_from:
                        prev = came_from[current]
                        
                        # Get interventions for this transition
                        interventions = self.probabilistic_reasoning.rank_interventions(prev, limit=1)
                        intervention = interventions[0] if interventions else {'intervention': 'undefined', 'effectiveness': 0.5}
                        
                        # Add step to path
                        path.append({
                            'from_emotion': prev,
                            'to_emotion': current,
                            'from_coordinates': emotion_coords[prev],
                            'to_coordinates': emotion_coords[current],
                            'intervention': intervention['intervention'],
                            'effectiveness': intervention['effectiveness']
                        })
                        
                        current = prev
                    
                    # Reverse path to get start to target
                    path.reverse()
                    
                    # Add the final target state
                    if path:
                        last_step = path[-1]
                        path.append({
                            'from_emotion': last_step['to_emotion'],
                            'to_emotion': target_emotion,
                            'from_coordinates': emotion_coords[last_step['to_emotion']],
                            'to_coordinates': target_coords,
                            'intervention': 'Goal reached',
                            'effectiveness': 1.0
                        })
                    
                    return path
                
                # Move current from open to closed set
                open_set.remove(current)
                closed_set.add(current)
                
                # Explore neighbors (all other emotions)
                for neighbor in emotions:
                    # Skip if in closed set
                    if neighbor in closed_set:
                        continue
                    
                    # Calculate tentative g_score
                    tentative_g_score = g_score[current] + cost(current, neighbor)
                    
                    # Check if new path is better
                    if neighbor not in open_set:
                        open_set.add(neighbor)
                    elif tentative_g_score >= g_score[neighbor]:
                        continue
                    
                    # This path is better, record it
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor)
                
                steps += 1
            
            # If we get here, no path was found
            logger.warning(f"No path found from {start_emotion} to {target_emotion} within {max_steps} steps")
            
            # Return a direct transition as fallback
            interventions = self.probabilistic_reasoning.rank_interventions(start_emotion, limit=1)
            intervention = interventions[0] if interventions else {'intervention': 'undefined', 'effectiveness': 0.5}
            
            return [{
                'from_emotion': start_emotion,
                'to_emotion': target_emotion,
                'from_coordinates': start_coords,
                'to_coordinates': target_coords,
                'intervention': intervention['intervention'],
                'effectiveness': intervention['effectiveness']
            }]
            
        except Exception as e:
            logger.error(f"Error finding emotional path: {e}")
            return []
