"""
ProbabilisticService - Class for probabilistic reasoning using Bayesian networks and Markov chains
"""
import random
from datetime import datetime
from .bayesian_network import BayesianNetwork
from .markov_model import MarkovModel

class ProbabilisticService:
    def __init__(self, db):
        """
        Initialize the probabilistic reasoning service
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        
        # Define basic emotional states
        self.emotions = [
            'joy', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral',
            'happy', 'sad', 'anxious', 'excited', 'content', 'calm', 'frustrated'
        ]
        
        # Initialize models
        self.bayesian_network = BayesianNetwork()
        self.markov_model = MarkovModel(states=self.emotions)
        
    def predict_next_emotion(self, user_email, current_emotion, model_type='markov'):
        """
        Predict the next emotional state based on the current emotion
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            model_type: Type of model to use ('markov' or 'bayesian')
            
        Returns:
            Dictionary with prediction results
        """
        try:
            # Get user's emotional history
            emotion_history = self._get_emotion_history(user_email)
            # Check if user has any emotional history
            if not emotion_history:
                # No emotional history, return a special prediction indicating this
                return {
                    "current_emotion": current_emotion,
                    "predicted_emotion": "neutral",
                    "probability": 0.0,
                    "model_type": model_type,
                    "timestamp": datetime.now(),
                    "is_default": True,
                    "message": "Not enough emotional data to make a prediction. Create more journal entries to improve predictions."
                }
            
            # Make prediction based on model type
            if model_type == 'bayesian':
                # Use Bayesian network for prediction
                prediction = self.bayesian_network.predict_next_state(
                    current_emotion, 
                    emotion_history
                )
            else:
                # Default to Markov model
                prediction = self.markov_model.predict_next_state(
                    current_emotion, 
                    emotion_history
                )
                
            return {
                'current_emotion': current_emotion,
                'predicted_emotion': prediction['state'],
                'probability': prediction['probability'],
                'model_type': model_type,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error in ProbabilisticService.predict_next_emotion: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Fallback to a simple prediction
            positive_emotions = ['calm', 'content', 'happy', 'excited', 'joy']
            return {
                'current_emotion': current_emotion,
                'predicted_emotion': random.choice(positive_emotions),
                'probability': 0.5,
                'model_type': model_type,
                'error': str(e)
            }
            
    def predict_emotional_sequence(self, user_email, current_emotion, sequence_length=3, model_type='markov'):
        """
        Predict a sequence of emotional states starting from the current emotion
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            sequence_length: Length of the sequence to predict
            model_type: Type of model to use ('markov' or 'bayesian')
            
        Returns:
            Dictionary with sequence prediction results
        """
        try:
            # Validate sequence length
            if sequence_length < 1:
                sequence_length = 1
            elif sequence_length > 10:
                sequence_length = 10  # Limit to 10 steps
                
            # Get user's emotional history
            emotion_history = self._get_emotion_history(user_email)
            
            # Generate sequence based on model type
            if model_type == 'bayesian':
                # Use Bayesian network for sequence prediction
                sequence = self.bayesian_network.predict_sequence(
                    current_emotion, 
                    emotion_history, 
                    sequence_length
                )
            else:
                # Default to Markov model
                # Update the Markov model with emotion history if available
                if emotion_history and len(emotion_history) > 1:
                    self.markov_model.update_from_sequence(emotion_history)
                
                # Call predict_sequence with only the required arguments
                sequence, probabilities = self.markov_model.predict_sequence(
                    current_emotion, 
                    sequence_length
                )
                
            return {
                'starting_emotion': current_emotion,
                'sequence': sequence,
                'probabilities': probabilities,
                'model_type': model_type,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error in ProbabilisticService.predict_emotional_sequence: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Fallback to a simple sequence
            positive_emotions = ['calm', 'content', 'happy', 'excited', 'joy']
            return {
                'starting_emotion': current_emotion,
                'sequence': [random.choice(positive_emotions) for _ in range(sequence_length)],
                'probabilities': [0.5] * sequence_length,
                'model_type': model_type,
                'error': str(e)
            }
            
    def retrain_model(self, user_email, model_type='markov'):
        """
        Retrain the probabilistic model with the latest emotional data
        
        Args:
            user_email: User's email
            model_type: Type of model to retrain ('markov' or 'bayesian')
            
        Returns:
            Boolean indicating success of retraining
        """
        try:
            # Get user's emotional history
            emotion_history = self._get_emotion_history(user_email, limit=50)
            
            # Check if we have enough data to retrain
            if len(emotion_history) < 2:
                print(f"Not enough emotional data to retrain model for user {user_email}")
                return False
                
            print(f"Retraining {model_type} model with {len(emotion_history)} emotional states")
            
            # Retrain based on model type
            if model_type == 'bayesian':
                # Update Bayesian network with new data
                self.bayesian_network.update_from_data(emotion_history)
                print("Bayesian network retrained successfully")
            else:
                # Update Markov model with new data
                self.markov_model.update_from_sequence(emotion_history)
                print("Markov model retrained successfully")
                
            return True
            
        except Exception as e:
            print(f"Error in ProbabilisticService.retrain_model: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    def _get_emotion_history(self, user_email, limit=20):
        """
        Get user's emotional history
        
        Args:
            user_email: User's email
            limit: Maximum number of entries to retrieve
            
        Returns:
            List of emotions
        """
        try:
            # Get user's journal entries
            entries = list(self.db.journal_entries.find(
                {'user_email': user_email, 'isUserMessage': True},
                {'emotion': 1}
            ).sort('created_at', -1).limit(limit))
            
            # Extract emotions
            emotions = []
            for entry in entries:
                if 'emotion' in entry and 'primary_emotion' in entry['emotion']:
                    emotions.append(entry['emotion']['primary_emotion'])
                    
            return emotions
            
        except Exception as e:
            print(f"Error in ProbabilisticService._get_emotion_history: {str(e)}")
            return []
            
    def get_emotional_graph(self, user_email, emotion_sequence=None):
        """
        Get the emotional graph for a user
        
        Args:
            user_email: User's email
            emotion_sequence: Optional list of emotions to use for calculating probabilities
            
        Returns:
            Dictionary representation of the emotional graph
        """
        try:
            # Get user's emotional history to build a personalized graph if not provided
            if emotion_sequence is None or len(emotion_sequence) == 0:
                emotion_sequence = self._get_emotion_history(user_email)
                # Only proceed with Markov model if we have actual emotion history
                if len(emotion_sequence) <= 1:
                    # Not enough data to build a meaningful graph, return default
                    print(f"Not enough emotional history for user {user_email}, returning default graph")
                    return self._get_default_emotional_graph()
                emotion_sequence = self._get_emotion_history(user_email)
            
            # Get transition probabilities from the Markov model
            transitions = self.markov_model.get_transition_probabilities(emotion_sequence)
            
            # Return the transitions directly for the frontend to display
            return transitions
            
        except Exception as e:
            print(f"Error in ProbabilisticService.get_emotional_graph: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a default graph with equal probabilities
            default_graph = {}
            for from_emotion in self.emotions:
                default_graph[from_emotion] = {}
                total = len(self.emotions)
                for to_emotion in self.emotions:
                    default_graph[from_emotion][to_emotion] = 1.0 / total
            return default_graph
            

    def _get_default_emotional_graph(self):
        """
        Get a default emotional graph with equal probabilities.
        
        Returns:
            Dictionary with default transition probabilities
        """
        default_graph = {}
        for from_emotion in self.emotions:
            default_graph[from_emotion] = {}
            total = len(self.emotions)
            for to_emotion in self.emotions:
                # Set a very low probability for all transitions in the default graph
                # to indicate these are not based on real data
                default_graph[from_emotion][to_emotion] = 0.01
        return default_graph

    def predict_emotional_impact(self, user_email, current_emotion, decision_text):
        """
        Predict the emotional impact of a decision
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            decision_text: Text description of the decision
            
        Returns:
            Dictionary with impact prediction
        """
        try:
            # Get user's emotional history
            emotion_history = self._get_emotion_history(user_email)
            
            # Analyze decision text for sentiment
            # This would ideally use NLP, but we'll use a simple approach for now
            positive_words = ['good', 'great', 'excellent', 'positive', 'happy', 'joy', 'calm', 'relax',
                              'peaceful', 'content', 'satisfied', 'confident', 'optimistic']
            negative_words = ['bad', 'terrible', 'awful', 'negative', 'sad', 'angry', 'anxious', 'stressed',
                             'worried', 'depressed', 'upset', 'frustrated', 'pessimistic']
                             
            # Count positive and negative words
            text_lower = decision_text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            # Calculate sentiment score (-1 to 1)
            total_count = positive_count + negative_count
            if total_count > 0:
                sentiment_score = (positive_count - negative_count) / total_count
            else:
                # No sentiment words found, use Markov model to predict
                prediction = self.markov_model.predict_next_state(current_emotion, emotion_history)
                positive_emotions = ['happy', 'excited', 'joy', 'content', 'calm']
                negative_emotions = ['sad', 'angry', 'anxious', 'stressed', 'depressed']
                
                predicted_emotion = prediction['state']
                if predicted_emotion in positive_emotions:
                    sentiment_score = 0.3  # Slightly positive
                elif predicted_emotion in negative_emotions:
                    sentiment_score = -0.3  # Slightly negative
                else:
                    sentiment_score = 0  # Neutral
            
            # Calculate confidence based on word count and history
            if total_count > 5:
                confidence = 0.8  # High confidence with more sentiment words
            elif total_count > 0:
                confidence = 0.6  # Medium confidence
            else:
                confidence = 0.4  # Lower confidence when relying on model
                
            return {
                'current_emotion': current_emotion,
                'emotional_impact': sentiment_score,  # -1 to 1 scale
                'confidence': confidence,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error in ProbabilisticService.predict_emotional_impact: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a default impact prediction
            return {
                'current_emotion': current_emotion,
                'emotional_impact': 0,  # Neutral impact
                'confidence': 0.5,
                'error': str(e)
            }
