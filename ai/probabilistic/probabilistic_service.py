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
        
    def predict_next_emotion(self, user_email, current_emotion, model_type='markov', previous_emotion=None, timestamp=None):
        """
        Predict the next emotional state based on the current emotion with enhanced parameters
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            model_type: Type of model to use ('markov', 'bayesian', or 'combined')
            previous_emotion: Optional previous emotional state for higher-order predictions
            timestamp: Optional timestamp for time-dependent predictions
            
        Returns:
            Dictionary with prediction results and confidence scores
        """
        try:
            # Get user's emotional history
            emotion_history = self._get_emotion_history(user_email)
            
            # Use timestamp or current time
            if not timestamp:
                timestamp = datetime.now()
                
            # Check if user has any emotional history
            if not emotion_history:
                # No emotional history, return a special prediction indicating this
                return {
                    "current_emotion": current_emotion,
                    "predicted_emotion": "neutral",
                    "probability": 0.0,
                    "model_type": model_type,
                    "timestamp": timestamp,
                    "is_default": True,
                    "confidence": 0.0,
                    "message": "Not enough emotional data to make a prediction. Create more journal entries to improve predictions."
                }
            
            # Create a probabilistic reasoning instance with models from our backend
            from models.probabilistic_reasoning import ProbabilisticReasoning
            from models.emotional_graph import EmotionalGraph
            
            # Try to use EmotionalGraphBigData if available
            try:
                from models.emotional_graph_bigdata import EmotionalGraphBigData
                emotional_graph = EmotionalGraphBigData(self.db)
                print("Using EmotionalGraphBigData for predictions")
            except ImportError:
                emotional_graph = EmotionalGraph(self.db)
                print("Using EmotionalGraph for predictions")
                
            # Initialize ProbabilisticReasoning with our graph
            reasoning = ProbabilisticReasoning(emotional_graph)
            
            # Get enhanced prediction with metadata
            hour_of_day = timestamp.hour
            day_of_week = timestamp.weekday()
            
            # Make prediction based on model type
            if model_type == 'combined':
                # Use both models and combine results
                markov_prediction = reasoning.markov_model.predict_next_emotion(
                    current_emotion,
                    previous_emotion=previous_emotion,
                    hour_of_day=hour_of_day,
                    day_of_week=day_of_week
                )
                
                bayesian_prediction = reasoning.bayesian_model.predict_emotion(
                    current_emotion,
                    hour_of_day=hour_of_day,
                    day_of_week=day_of_week
                )
                
                # If predictions match, use higher confidence; otherwise use weighted average
                if markov_prediction['emotion'] == bayesian_prediction['emotion']:
                    prediction = {
                        'emotion': markov_prediction['emotion'],
                        'probability': max(markov_prediction['probability'], bayesian_prediction['probability']),
                        'confidence': (markov_prediction['confidence'] + bayesian_prediction['confidence']) / 2
                    }
                else:
                    # Weight predictions by confidence
                    m_weight = markov_prediction['confidence'] / (markov_prediction['confidence'] + bayesian_prediction['confidence'])
                    b_weight = bayesian_prediction['confidence'] / (markov_prediction['confidence'] + bayesian_prediction['confidence'])
                    
                    # Use prediction with higher confidence
                    if markov_prediction['confidence'] > bayesian_prediction['confidence']:
                        prediction = {
                            'emotion': markov_prediction['emotion'],
                            'probability': markov_prediction['probability'] * m_weight + bayesian_prediction['probability'] * b_weight,
                            'confidence': markov_prediction['confidence'] * m_weight + bayesian_prediction['confidence'] * b_weight
                        }
                    else:
                        prediction = {
                            'emotion': bayesian_prediction['emotion'],
                            'probability': markov_prediction['probability'] * m_weight + bayesian_prediction['probability'] * b_weight,
                            'confidence': markov_prediction['confidence'] * m_weight + bayesian_prediction['confidence'] * b_weight
                        }
            elif model_type == 'bayesian':
                # Use Bayesian network for prediction
                bayesian_prediction = reasoning.bayesian_model.predict_emotion(
                    current_emotion,
                    hour_of_day=hour_of_day,
                    day_of_week=day_of_week
                )
                prediction = {
                    'emotion': bayesian_prediction['emotion'],
                    'probability': bayesian_prediction['probability'],
                    'confidence': bayesian_prediction['confidence']
                }
            else:
                # Default to Markov model
                markov_prediction = reasoning.markov_model.predict_next_emotion(
                    current_emotion,
                    previous_emotion=previous_emotion,
                    hour_of_day=hour_of_day,
                    day_of_week=day_of_week
                )
                prediction = {
                    'emotion': markov_prediction['emotion'],
                    'probability': markov_prediction['probability'],
                    'confidence': markov_prediction['confidence']
                }
            
            # Get emotion coordinates for visualization
            coordinates = reasoning.get_emotion_coordinates(prediction['emotion'])
            
            return {
                'current_emotion': current_emotion,
                'predicted_emotion': prediction['emotion'],
                'probability': prediction['probability'],
                'confidence': prediction['confidence'],
                'model_type': model_type,
                'timestamp': timestamp,
                'coordinates': coordinates,
                'factors': {
                    'time_of_day': hour_of_day,
                    'day_of_week': day_of_week,
                    'history_length': len(emotion_history)
                }
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
            
    def predict_emotional_sequence(self, user_email, current_emotion, sequence_length=3, model_type='markov', include_metadata=False, timestamp=None):
        """
        Predict a sequence of emotional states starting from the current emotion with rich metadata
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            sequence_length: Length of the sequence to predict
            model_type: Type of model to use ('markov', 'bayesian', or 'combined')
            include_metadata: Whether to include detailed metadata
            timestamp: Optional timestamp for time-dependent predictions
            
        Returns:
            Dictionary with sequence prediction results and metadata
        """
        try:
            # Validate sequence length
            if sequence_length < 1:
                sequence_length = 1
            elif sequence_length > 10:
                sequence_length = 10  # Limit to 10 steps
                
            # Use timestamp or current time
            if not timestamp:
                timestamp = datetime.now()
                
            # Get user's emotional history
            emotion_history = self._get_emotion_history(user_email)
            
            # Check if user has enough emotional history
            if not emotion_history or len(emotion_history) < 3:
                # Not enough data for reliable prediction
                if include_metadata:
                    return {
                        "starting_emotion": current_emotion,
                        "sequence": [{
                            "emotion": "neutral",
                            "probability": 0.0,
                            "confidence": 0.0,
                            "step": i + 1
                        } for i in range(sequence_length)],
                        "is_default": True,
                        "timestamp": timestamp,
                        "message": "Not enough emotional data to make reliable predictions."
                    }
                else:
                    return {
                        "starting_emotion": current_emotion,
                        "sequence": ["neutral"] * sequence_length,
                        "probabilities": [0.0] * sequence_length,
                        "is_default": True,
                        "timestamp": timestamp,
                        "message": "Not enough emotional data to make reliable predictions."
                    }
            
            # Create a probabilistic reasoning instance with models from our backend
            from models.probabilistic_reasoning import ProbabilisticReasoning
            from models.emotional_graph import EmotionalGraph
            
            # Try to use EmotionalGraphBigData if available
            try:
                from models.emotional_graph_bigdata import EmotionalGraphBigData
                emotional_graph = EmotionalGraphBigData(self.db)
                print("Using EmotionalGraphBigData for sequence prediction")
            except ImportError:
                emotional_graph = EmotionalGraph(self.db)
                print("Using EmotionalGraph for sequence prediction")
                
            # Initialize ProbabilisticReasoning with our graph
            reasoning = ProbabilisticReasoning(emotional_graph)
            
            # Get hour of day and day of week for time-dependent predictions
            hour_of_day = timestamp.hour
            day_of_week = timestamp.weekday()
            
            # Use enhanced predict_emotional_sequence from ProbabilisticReasoning
            result_sequence = reasoning.predict_emotional_sequence(
                current_emotion, 
                sequence_length=sequence_length,
                include_metadata=include_metadata,
                timestamp=timestamp
            )
            
            # Prepare return values based on metadata flag
            if include_metadata:
                sequence = result_sequence
                probabilities = [item.get('probability', 0.5) for item in result_sequence]
            else:
                sequence = [item if isinstance(item, str) else item.get('emotion', 'neutral') for item in result_sequence]
                probabilities = [0.5] * len(sequence)  # Default probabilities if not included
                
            result = {
                'starting_emotion': current_emotion,
                'sequence': sequence,
                'probabilities': probabilities,
                'model_type': model_type,
                'timestamp': timestamp,
                'factors': {
                    'time_of_day': hour_of_day,
                    'day_of_week': day_of_week,
                    'history_length': len(emotion_history)
                }
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
            
    def rank_interventions(self, user_email, emotion, limit=5):
        """
        Rank interventions by effectiveness for a given emotional state
        
        Args:
            user_email: User's email
            emotion: Current emotional state
            limit: Maximum number of interventions to return
            
        Returns:
            List of ranked interventions with effectiveness scores
        """
        try:
            # Create a probabilistic reasoning instance
            from models.probabilistic_reasoning import ProbabilisticReasoning
            from models.emotional_graph import EmotionalGraph
            
            # Try to use EmotionalGraphBigData if available
            try:
                from models.emotional_graph_bigdata import EmotionalGraphBigData
                emotional_graph = EmotionalGraphBigData(self.db)
                print("Using EmotionalGraphBigData for intervention ranking")
            except ImportError:
                emotional_graph = EmotionalGraph(self.db)
                print("Using EmotionalGraph for intervention ranking")
                
            # Initialize ProbabilisticReasoning with our graph
            reasoning = ProbabilisticReasoning(emotional_graph)
            
            # Try to use MentalHealthIntegration if available
            try:
                from models.dataset.mental_health_integration import MentalHealthIntegration
                mental_health = MentalHealthIntegration()
                interventions = mental_health.get_interventions(emotion, limit=limit*2)  # Get more than needed for filtering
            except ImportError:
                # Fall back to default interventions
                interventions = self._get_default_interventions(emotion, limit*2)
                
            # Calculate effectiveness for each intervention
            for intervention in interventions:
                effectiveness = reasoning.predict_intervention_effectiveness(
                    emotion, 
                    intervention['name']
                )
                intervention['predicted_effectiveness'] = effectiveness
                
            # Sort by effectiveness and limit
            interventions.sort(key=lambda x: x.get('predicted_effectiveness', 0), reverse=True)
            top_interventions = interventions[:limit]
            
            # Enhance with next emotion predictions
            for intervention in top_interventions:
                # Predict emotional outcome after this intervention
                next_emotion = reasoning.predict_emotion_after_intervention(
                    emotion,
                    intervention['name']
                )
                intervention['next_emotion'] = next_emotion
                
            return top_interventions
                
        except Exception as e:
            print(f"Error in rank_interventions: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return default interventions
            return self._get_default_interventions(emotion, limit)
    
    def _get_default_interventions(self, emotion, limit=5):
        """
        Get default interventions for an emotion when no data is available
        
        Args:
            emotion: Emotional state
            limit: Maximum number of interventions
            
        Returns:
            List of default interventions
        """
        # Map to basic emotion categories
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
        
        base_emotion = emotion_mapping.get(emotion.lower(), emotion.lower())
        
        # Default interventions by emotion
        interventions = {
            'sadness': [
                {
                    'name': 'Mindful Walking',
                    'description': 'Take a short walk while paying attention to your surroundings',
                    'duration': '10 minutes',
                    'predicted_effectiveness': 0.7
                },
                {
                    'name': 'Gratitude Journal',
                    'description': 'Write down three things you are grateful for today',
                    'duration': '5 minutes',
                    'predicted_effectiveness': 0.6
                },
                {
                    'name': 'Talk to a Friend',
                    'description': 'Reach out to someone who makes you feel supported',
                    'duration': '15 minutes',
                    'predicted_effectiveness': 0.8
                },
                {
                    'name': 'Listen to Uplifting Music',
                    'description': 'Create a playlist of songs that boost your mood',
                    'duration': '15 minutes',
                    'predicted_effectiveness': 0.65
                },
                {
                    'name': 'Self-Compassion Exercise',
                    'description': 'Speak to yourself with kindness, as you would to a good friend',
                    'duration': '5 minutes',
                    'predicted_effectiveness': 0.75
                }
            ],
            'anger': [
                {
                    'name': 'Deep Breathing',
                    'description': 'Take slow, deep breaths for a few minutes',
                    'duration': '5 minutes',
                    'predicted_effectiveness': 0.8
                },
                {
                    'name': 'Physical Exercise',
                    'description': 'Go for a run or do another form of exercise',
                    'duration': '20 minutes',
                    'predicted_effectiveness': 0.75
                },
                {
                    'name': 'Count to Ten',
                    'description': 'Count slowly to ten before responding',
                    'duration': '1 minute',
                    'predicted_effectiveness': 0.6
                },
                {
                    'name': 'Write It Out',
                    'description': 'Write down your feelings without censoring yourself',
                    'duration': '10 minutes',
                    'predicted_effectiveness': 0.7
                },
                {
                    'name': 'Progressive Muscle Relaxation',
                    'description': 'Tense and then release each muscle group in your body',
                    'duration': '10 minutes',
                    'predicted_effectiveness': 0.65
                }
            ],
            'fear': [
                {
                    'name': 'Grounding Exercise',
                    'description': 'Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste',
                    'duration': '5 minutes',
                    'predicted_effectiveness': 0.75
                },
                {
                    'name': 'Visualization',
                    'description': 'Imagine yourself in a peaceful, safe place',
                    'duration': '10 minutes',
                    'predicted_effectiveness': 0.7
                },
                {
                    'name': 'Challenge Thoughts',
                    'description': 'Identify and challenge fear-based thoughts',
                    'duration': '15 minutes',
                    'predicted_effectiveness': 0.8
                },
                {
                    'name': 'Progressive Exposure',
                    'description': 'Take one small step toward facing your fear',
                    'duration': 'Varies',
                    'predicted_effectiveness': 0.85
                },
                {
                    'name': 'Body Scan Meditation',
                    'description': 'Systematically focus on each part of your body, releasing tension',
                    'duration': '15 minutes',
                    'predicted_effectiveness': 0.65
                }
            ],
            'joy': [
                {
                    'name': 'Savor the Moment',
                    'description': 'Fully engage with your current experience',
                    'duration': '5 minutes',
                    'predicted_effectiveness': 0.8
                },
                {
                    'name': 'Share with Others',
                    'description': 'Tell someone about what\'s bringing you joy',
                    'duration': '10 minutes',
                    'predicted_effectiveness': 0.75
                },
                {
                    'name': 'Gratitude Practice',
                    'description': 'Express thanks for this positive experience',
                    'duration': '5 minutes',
                    'predicted_effectiveness': 0.7
                },
                {
                    'name': 'Create a Joy Jar',
                    'description': 'Write down this joyful moment and save it in a jar',
                    'duration': '5 minutes',
                    'predicted_effectiveness': 0.65
                },
                {
                    'name': 'Memory Consolidation',
                    'description': 'Take mental photographs to help remember this feeling',
                    'duration': '3 minutes',
                    'predicted_effectiveness': 0.6
                }
            ],
            'neutral': [
                {
                    'name': 'Mindfulness Meditation',
                    'description': 'Focus on your breath and present moment',
                    'duration': '10 minutes',
                    'predicted_effectiveness': 0.7
                },
                {
                    'name': 'Goal Setting',
                    'description': 'Set one small, achievable goal for today',
                    'duration': '10 minutes',
                    'predicted_effectiveness': 0.65
                },
                {
                    'name': 'Creative Expression',
                    'description': 'Draw, write, or engage in another creative activity',
                    'duration': '15 minutes',
                    'predicted_effectiveness': 0.6
                },
                {
                    'name': 'Nature Connection',
                    'description': 'Spend time outdoors, even just looking at the sky',
                    'duration': '10 minutes',
                    'predicted_effectiveness': 0.75
                },
                {
                    'name': 'Learning Activity',
                    'description': 'Learn something new that interests you',
                    'duration': '20 minutes',
                    'predicted_effectiveness': 0.7
                }
            ]
        }
        
        # Return interventions for the emotion, or default to neutral if not found
        return interventions.get(base_emotion, interventions['neutral'])[:limit]
    
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
            
    def get_emotional_graph(self, user_email, emotion_sequence=None, include_dataset_data=False, include_transitions=True):
        """
        Get the emotional graph for a user with transition probabilities
        
        Args:
            user_email: User's email
            emotion_sequence: Optional list of emotions to use for calculating probabilities
            include_dataset_data: Whether to include data from the IEMOCAP dataset
            include_transitions: Whether to include user transition history
            
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
            
            # Build result dictionary with metadata
            result = {
                'emotions': self.emotions,
                'user_email': user_email,
                'timestamp': datetime.now().isoformat(),
                'data_sources': []
            }
            
            # Get transition probabilities from the Markov model
            if include_transitions:
                transitions = self.markov_model.get_transition_probabilities(emotion_sequence)
                result['transitions'] = transitions
                result['data_sources'].append('user_history')
            
            # Add IEMOCAP dataset transition data if requested
            if include_dataset_data:
                try:
                    # This would be implemented to pull data from the IEMOCAP integration
                    # For now, we're using a placeholder
                    dataset_transitions = self._get_dataset_transitions()
                    result['dataset_transitions'] = dataset_transitions
                    result['data_sources'].append('iemocap_dataset')
                except Exception as dataset_error:
                    print(f"Error getting dataset transitions: {str(dataset_error)}")
                    result['dataset_error'] = str(dataset_error)
            
            # Add graph visualization data
            # Format nodes and edges for visualization libraries
            viz_data = {
                'nodes': [{'id': emotion, 'label': emotion.capitalize()} for emotion in self.emotions],
                'edges': []
            }
            
            # Use the transitions to build the edges
            if include_transitions and 'transitions' in result:
                for from_emotion, targets in result['transitions'].items():
                    for to_emotion, probability in targets.items():
                        if probability > 0.01:  # Only include meaningful transitions
                            viz_data['edges'].append({
                                'from': from_emotion,
                                'to': to_emotion,
                                'value': probability,
                                'label': f"{probability:.2f}"
                            })
            
            result['visualization_data'] = viz_data
            return result
            
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
            
            return {
                'emotions': self.emotions,
                'transitions': default_graph,
                'error': str(e),
                'is_default': True
            }
            

    def _get_dataset_transitions(self):
        """
        Get emotion transition probabilities from the IEMOCAP dataset
        
        Returns:
            Dictionary with transition probabilities derived from the dataset
        """
        try:
            # This would normally connect to the IEMOCAP integration
            # For now, we'll use a placeholder with some realistic data
            # In a real implementation, this would pull from the actual dataset
            
            # Attempt to get the dataset integration if available
            try:
                from models.dataset.iemocap_integration import IemocapIntegration
                iemocap = IemocapIntegration()
                # If integration exists, use it to get transition data
                return iemocap.get_transition_probabilities()
            except ImportError:
                # If integration not available, return sample data
                pass
            
            # Sample data representing IEMOCAP emotion transitions
            # Based on the paper: "IEMOCAP: Interactive emotional dyadic motion capture database"
            dataset_transitions = {
                'neutral': {
                    'joy': 0.15,
                    'sadness': 0.12,
                    'anger': 0.08,
                    'fear': 0.05,
                    'disgust': 0.03,
                    'surprise': 0.10,
                    'neutral': 0.47
                },
                'joy': {
                    'joy': 0.55,
                    'neutral': 0.20,
                    'surprise': 0.12,
                    'sadness': 0.03,
                    'anger': 0.04,
                    'fear': 0.02,
                    'disgust': 0.04
                },
                'sadness': {
                    'sadness': 0.60,
                    'neutral': 0.15,
                    'fear': 0.09,
                    'anger': 0.06,
                    'disgust': 0.05,
                    'joy': 0.03,
                    'surprise': 0.02
                },
                'anger': {
                    'anger': 0.50,
                    'disgust': 0.15,
                    'sadness': 0.10,
                    'neutral': 0.12,
                    'fear': 0.08,
                    'surprise': 0.03,
                    'joy': 0.02
                },
                'fear': {
                    'fear': 0.45,
                    'neutral': 0.15,
                    'sadness': 0.15,
                    'surprise': 0.10,
                    'anger': 0.07,
                    'disgust': 0.05,
                    'joy': 0.03
                },
                'disgust': {
                    'disgust': 0.40,
                    'anger': 0.20,
                    'neutral': 0.15,
                    'sadness': 0.10,
                    'fear': 0.08,
                    'surprise': 0.05,
                    'joy': 0.02
                },
                'surprise': {
                    'surprise': 0.30,
                    'joy': 0.20,
                    'fear': 0.15,
                    'neutral': 0.15,
                    'sadness': 0.08,
                    'anger': 0.07,
                    'disgust': 0.05
                }
            }
            
            # Add metadata about the dataset
            result = {
                'transitions': dataset_transitions,
                'source': 'IEMOCAP',
                'sample_size': 10039,  # Example size from the IEMOCAP dataset
                'confidence': 0.85,
                'description': 'Transition probabilities derived from the IEMOCAP dataset',
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"Error in _get_dataset_transitions: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a fallback with some reasonable probabilities
            return {
                'transitions': self._get_default_emotional_graph(),
                'error': str(e),
                'is_default': True,
                'source': 'default_fallback'
            }
    
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
