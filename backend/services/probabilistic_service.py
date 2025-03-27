"""
ProbabilisticService - Service for probabilistic reasoning using Bayesian networks and Markov chains
"""
import random
from datetime import datetime

class ProbabilisticService:
    def __init__(self, db):
        """
        Initialize the probabilistic reasoning service
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.models = {
            'markov': self._predict_with_markov,
            'bayesian': self._predict_with_bayesian
        }
        
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
            # Get prediction using specified model
            if model_type not in self.models:
                model_type = 'markov'  # Default to Markov model
                
            prediction = self.models[model_type](user_email, current_emotion)
            
            return {
                'current_emotion': current_emotion,
                'predicted_emotion': prediction['emotion'],
                'probability': prediction['probability'],
                'model_type': model_type,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error in ProbabilisticService.predict_next_emotion: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'current_emotion': current_emotion,
                'predicted_emotion': current_emotion,  # Default to same emotion
                'probability': 0.0,
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
                
            # Get prediction using specified model
            if model_type not in self.models:
                model_type = 'markov'  # Default to Markov model
                
            # Generate sequence
            sequence = [current_emotion]
            probabilities = []
            
            for _ in range(sequence_length):
                prediction = self.models[model_type](user_email, sequence[-1])
                sequence.append(prediction['emotion'])
                probabilities.append(prediction['probability'])
                
            return {
                'starting_emotion': current_emotion,
                'sequence': sequence[1:],  # Exclude starting emotion
                'probabilities': probabilities,
                'model_type': model_type,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error in ProbabilisticService.predict_emotional_sequence: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'starting_emotion': current_emotion,
                'sequence': [current_emotion] * sequence_length,  # Default to same emotion
                'probabilities': [0.0] * sequence_length,
                'model_type': model_type,
                'error': str(e)
            }
            
    def _predict_with_markov(self, user_email, current_emotion):
        """
        Predict the next emotional state using a Markov chain model
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            
        Returns:
            Dictionary with emotion and probability
        """
        # Get user's emotional history
        history = self._get_emotion_history(user_email)
        
        if not history:
            # No history, return random positive emotion
            positive_emotions = ['calm', 'content', 'happy', 'excited', 'joy']
            return {
                'emotion': random.choice(positive_emotions),
                'probability': 0.5
            }
            
        # Build transition matrix from history
        transitions = {}
        for i in range(len(history) - 1):
            from_emotion = history[i]
            to_emotion = history[i + 1]
            
            if from_emotion not in transitions:
                transitions[from_emotion] = {}
                
            if to_emotion not in transitions[from_emotion]:
                transitions[from_emotion][to_emotion] = 0
                
            transitions[from_emotion][to_emotion] += 1
            
        # Normalize transitions to get probabilities
        for from_emotion in transitions:
            total = sum(transitions[from_emotion].values())
            for to_emotion in transitions[from_emotion]:
                transitions[from_emotion][to_emotion] /= total
                
        # Predict next emotion
        if current_emotion in transitions:
            # Get most likely transition
            next_emotion = max(transitions[current_emotion].items(), key=lambda x: x[1])
            return {
                'emotion': next_emotion[0],
                'probability': next_emotion[1]
            }
        else:
            # No transitions from current emotion, return random positive emotion
            positive_emotions = ['calm', 'content', 'happy', 'excited', 'joy']
            return {
                'emotion': random.choice(positive_emotions),
                'probability': 0.5
            }
            
    def _predict_with_bayesian(self, user_email, current_emotion):
        """
        Predict the next emotional state using a Bayesian network model
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            
        Returns:
            Dictionary with emotion and probability
        """
        # Get user's emotional history
        history = self._get_emotion_history(user_email)
        
        if not history:
            # No history, return random positive emotion
            positive_emotions = ['calm', 'content', 'happy', 'excited', 'joy']
            return {
                'emotion': random.choice(positive_emotions),
                'probability': 0.5
            }
            
        # For simplicity, we'll use a similar approach to Markov but with some Bayesian influence
        # In a real implementation, this would use a proper Bayesian network
        
        # Count emotion frequencies
        emotion_counts = {}
        for emotion in history:
            if emotion not in emotion_counts:
                emotion_counts[emotion] = 0
            emotion_counts[emotion] += 1
            
        # Calculate prior probabilities
        total = len(history)
        priors = {emotion: count / total for emotion, count in emotion_counts.items()}
        
        # Build conditional probabilities
        conditionals = {}
        for i in range(len(history) - 1):
            from_emotion = history[i]
            to_emotion = history[i + 1]
            
            if from_emotion not in conditionals:
                conditionals[from_emotion] = {}
                
            if to_emotion not in conditionals[from_emotion]:
                conditionals[from_emotion][to_emotion] = 0
                
            conditionals[from_emotion][to_emotion] += 1
            
        # Normalize conditionals
        for from_emotion in conditionals:
            total = sum(conditionals[from_emotion].values())
            for to_emotion in conditionals[from_emotion]:
                conditionals[from_emotion][to_emotion] /= total
                
        # Calculate posterior probabilities using Bayes' rule
        if current_emotion in conditionals:
            # Get emotion with highest posterior probability
            next_emotion = max(conditionals[current_emotion].items(), key=lambda x: x[1])
            return {
                'emotion': next_emotion[0],
                'probability': next_emotion[1]
            }
        else:
            # No conditionals for current emotion, use priors
            if priors:
                next_emotion = max(priors.items(), key=lambda x: x[1])
                return {
                    'emotion': next_emotion[0],
                    'probability': next_emotion[1]
                }
            else:
                # No priors, return random positive emotion
                positive_emotions = ['calm', 'content', 'happy', 'excited', 'joy']
                return {
                    'emotion': random.choice(positive_emotions),
                    'probability': 0.5
                }
                
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
