"""
Emotional Graph with Big Data Integration
Represents and manages emotional state transitions with Kafka, Hadoop, and Spark integration.
"""
import datetime
import json
import logging
import math
from pymongo import MongoClient
from bson.objectid import ObjectId
from services.kafka_service import KafkaService
from services.hdfs_service import HDFSService
from services.spark_service import SparkService
from models.search_algorithm import AStarSearch
from models.dataset.iemocap_integration import IemocapIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionalGraphBigData:
    """
    Enhanced EmotionalGraph with Big Data capabilities.
    Extends the original EmotionalGraph with Kafka, HDFS, and Spark integration.
    """
    
    def __init__(self, db):
        """
        Initialize the EmotionalGraph with a database connection, big data services,
        and IEMOCAP dataset integration for data-driven transition probabilities.
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
        self.emotions_collection = db.emotional_states
        self.transitions_collection = db.emotional_transitions
        
        # Define positive and negative emotions
        self.positive_emotions = ['joy', 'surprise', 'happy', 'excited', 'content', 'calm']
        self.negative_emotions = ['sadness', 'anger', 'fear', 'disgust', 'sad', 'anxious', 'frustrated', 'stressed']
        self.neutral_emotions = ['neutral']
        
        # Define stress-related emotions for special handling
        self.stress_emotions = ['stressed', 'anxious', 'overwhelmed', 'worried']
        
        # Initialize big data services
        self.kafka_service = KafkaService()
        self.hdfs_service = HDFSService()
        self.spark_service = SparkService()
        
        # Initialize the IEMOCAP integration for data-driven transition probabilities
        try:
            self.iemocap = IemocapIntegration()
            self.using_dataset_transitions = True
            logger.info("IEMOCAP dataset integration initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize IEMOCAP integration: {e}. Using default transitions.")
            self.using_dataset_transitions = False
            
        # Map standard emotions to IEMOCAP emotions for compatibility
        self.emotion_mapping = {
            # Map our standard emotions to IEMOCAP emotion categories
            'joy': 'happy',
            'happy': 'happy',
            'excited': 'happy',
            'content': 'happy',
            'calm': 'neutral',
            'sadness': 'sad',
            'sad': 'sad',
            'anger': 'angry',
            'angry': 'angry',
            'frustration': 'angry',
            'frustrated': 'angry',
            'fear': 'fear',
            'afraid': 'fear',
            'scared': 'fear',
            'anxiety': 'anxious',
            'anxious': 'anxious',
            'worried': 'anxious',
            'disgust': 'disgust',
            'surprise': 'surprise',
            'neutral': 'neutral',
            'stressed': 'anxious',
            'overwhelmed': 'anxious'
        }
        
        # Cache for transition probabilities to avoid repeated computation
        self.transition_probability_cache = {}
        
        # Initialize A* search algorithm
        self.search_algorithm = AStarSearch(self)
        
    def record_emotion(self, user_email, emotion_data, entry_id=None):
        """
        Record an emotional state for a user, publish to Kafka, and provide insights.
        Leverages IEMOCAP dataset for enhanced emotion transition modeling.
        
        Args:
            user_email (str): The user's email
            emotion_data (dict): Emotion analysis data
            entry_id (str, optional): Associated journal entry ID
            
        Returns:
            dict: Dictionary containing emotional state ID, transition insights, and next emotion predictions
        """
        # Create emotional state document
        current_emotion = emotion_data.get('primary_emotion', 'neutral')
        emotion_state = {
            'user_email': user_email,
            'primary_emotion': current_emotion,
            'is_positive': emotion_data.get('is_positive', False),
            'emotion_scores': emotion_data.get('emotion_scores', {}),
            'entry_id': entry_id,
            'timestamp': datetime.datetime.now()
        }
        
        # Insert into database
        result = self.emotions_collection.insert_one(emotion_state)
        emotion_state_id = result.inserted_id
        emotion_state['_id'] = str(emotion_state_id)
        
        # Get transition insights and initialize response
        response = {
            'emotion_state_id': str(emotion_state_id),
            'primary_emotion': current_emotion,
            'is_positive': emotion_data.get('is_positive', False),
            'timestamp': emotion_state['timestamp'].isoformat(),
            'next_emotions': {},
            'insights': []
        }
        
        # Publish to Kafka
        try:
            self.kafka_service.publish_message(
                "emotional-states",
                user_email,
                json.dumps(emotion_state)
            )
            logger.info(f"Published emotional state to Kafka: {emotion_state_id}")
        except Exception as e:
            logger.error(f"Failed to publish emotional state to Kafka: {e}")
            response['insights'].append(f"Warning: Failed to publish to real-time processing pipeline: {str(e)}")
        
        # Get previous emotional state to create transition
        previous_state = self._get_previous_emotional_state(user_email, exclude_id=emotion_state_id)
        transition_id = None
        
        # If previous state exists, record transition
        if previous_state:
            from_emotion = previous_state['primary_emotion']
            to_emotion = current_emotion
            
            # Record the transition
            transition_id = self._record_transition(
                user_email, 
                from_emotion,
                to_emotion,
                previous_state['_id'],
                emotion_state_id
            )
            
            # Calculate time difference between states
            prev_time = previous_state.get('timestamp')
            time_diff = (datetime.datetime.now() - prev_time).total_seconds() / 3600  # in hours
            
            # Add transition insight
            if from_emotion != to_emotion:
                # Add transition insight to response
                if from_emotion in self.positive_emotions and to_emotion in self.negative_emotions:
                    response['insights'].append(f"You've transitioned from a positive emotion ({from_emotion}) to a negative one ({to_emotion}). Consider what factors may have contributed to this shift.")
                elif from_emotion in self.negative_emotions and to_emotion in self.positive_emotions:
                    response['insights'].append(f"Great job transitioning from {from_emotion} to {to_emotion}! This positive shift often indicates successful emotional regulation.")
                elif from_emotion in self.negative_emotions and to_emotion in self.negative_emotions:
                    response['insights'].append(f"You've moved from {from_emotion} to {to_emotion}. Both are challenging emotions, but this transition can provide insights into your emotional patterns.")
                
                # Add time-based insight
                if time_diff < 1:  # Less than 1 hour
                    response['insights'].append(f"Your emotional state changed relatively quickly (within {int(time_diff * 60)} minutes). Rapid transitions can be normal during active emotional processing.")
                elif time_diff > 24:  # More than a day
                    response['insights'].append(f"It's been over a day since your last recorded emotion. Regular reflection can help maintain emotional awareness.")
            else:
                response['insights'].append(f"Your emotional state has remained as {current_emotion} since your last entry. Emotional consistency can indicate stability.")
        
        # Get next emotion predictions based on transition probabilities
        if self.using_dataset_transitions:
            # Get transition probabilities
            transition_probs = self.get_transition_probabilities(user_email)
            
            # If we have probabilities for the current emotion, add them to the response
            if current_emotion in transition_probs:
                # Sort emotions by probability (descending)
                next_emotions = sorted(
                    [(e, p) for e, p in transition_probs[current_emotion].items() if p > 0.05],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Add top 3 most likely next emotions
                for emotion, probability in next_emotions[:3]:
                    response['next_emotions'][emotion] = probability
                    
                # Add insight about most likely next emotion
                if next_emotions:
                    most_likely_emotion, prob = next_emotions[0]
                    if most_likely_emotion in self.positive_emotions:
                        response['insights'].append(f"Based on emotional patterns, you're likely to transition toward {most_likely_emotion} next. This would be a positive development!")
                    elif most_likely_emotion in self.negative_emotions:
                        response['insights'].append(f"Your current emotional state often leads to {most_likely_emotion}. Being aware of this pattern can help you navigate toward more positive emotions.")
                    else:
                        response['insights'].append(f"Your current emotional state commonly transitions to {most_likely_emotion} next.")
        
        # Save to HDFS for batch processing
        try:
            if self.hdfs_service.check_connection():
                # Store in user-specific directory
                hdfs_path = f"/user/reflectly/emotional_states/{user_email}/{str(emotion_state_id)}.json"
                self.hdfs_service.write_file(hdfs_path, json.dumps(emotion_state))
                logger.info(f"Saved emotional state to HDFS: {hdfs_path}")
                
                # Also save insights response
                insights_path = f"/user/reflectly/emotional_insights/{user_email}/{str(emotion_state_id)}.json"
                self.hdfs_service.write_file(insights_path, json.dumps(response))
                logger.info(f"Saved emotional insights to HDFS: {insights_path}")
        except Exception as e:
            logger.error(f"Failed to save emotional state to HDFS: {e}")
            response['insights'].append(f"Warning: Unable to save to distributed storage: {str(e)}")
            
        # Trigger a Spark job to update emotion analytics if available
        try:
            if self.spark_service.check_connection():
                self.spark_service.submit_job(
                    "emotion_analytics",
                    {
                        "user_email": user_email,
                        "emotion_state_id": str(emotion_state_id),
                        "timestamp": emotion_state['timestamp'].isoformat()
                    }
                )
                logger.info(f"Submitted emotion analytics job for user {user_email}")
        except Exception as e:
            logger.warning(f"Failed to submit emotion analytics job: {e}")
            
        return response
    
    def _get_previous_emotional_state(self, user_email, exclude_id=None):
        """
        Get the user's previous emotional state.
        
        Args:
            user_email (str): The user's email
            exclude_id: ID to exclude from the search
            
        Returns:
            dict: Previous emotional state or None
        """
        # Find the most recent emotional state for this user
        query = {'user_email': user_email}
        if exclude_id:
            query['_id'] = {'$ne': exclude_id}
            
        return self.emotions_collection.find_one(
            query,
            sort=[('timestamp', -1)]  # Sort by timestamp descending
        )
    
    def _record_transition(self, user_email, from_emotion, to_emotion, from_state_id, to_state_id):
        """
        Record a transition between emotional states and publish to Kafka.
        
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
            'timestamp': datetime.datetime.now(),
            'actions': self._get_default_actions(from_emotion, to_emotion)
        }
        
        # Insert into database
        result = self.transitions_collection.insert_one(transition)
        transition_id = result.inserted_id
        transition['_id'] = str(transition_id)
        
        # Publish to Kafka
        try:
            self.kafka_service.publish_message(
                "emotional-transitions",
                user_email,
                json.dumps(transition)
            )
            logger.info(f"Published emotional transition to Kafka: {transition_id}")
        except Exception as e:
            logger.error(f"Failed to publish emotional transition to Kafka: {e}")
        
        return str(transition_id)
    
    def _get_default_actions(self, from_emotion, to_emotion):
        """
        Get default actions for a transition.
        
        Args:
            from_emotion (str): Source emotion
            to_emotion (str): Target emotion
            
        Returns:
            list: Default actions
        """
        # Primary action
        primary_action = {
            "description": self._get_default_action(from_emotion, to_emotion),
            "timestamp": datetime.datetime.now().isoformat(),
            "success_rate": 0.6
        }
        
        # Secondary actions
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
        """
        Get a default action for a transition.
        
        Args:
            from_emotion (str): Source emotion
            to_emotion (str): Target emotion
            
        Returns:
            str: Default action
        """
        actions = {
            ('sadness', 'joy'): "Engage in activities you enjoy",
            ('sadness', 'neutral'): "Practice mindfulness",
            ('sadness', 'anger'): "Express your feelings constructively",
            ('sadness', 'fear'): "Identify specific concerns",
            ('sadness', 'disgust'): "Focus on positive aspects",
            
            ('anger', 'joy'): "Channel energy into positive activities",
            ('anger', 'neutral'): "Take deep breaths and count to 10",
            ('anger', 'sadness'): "Reflect on underlying feelings",
            ('anger', 'fear'): "Consider potential consequences",
            ('anger', 'disgust'): "Shift focus to solutions",
            
            ('fear', 'joy'): "Focus on positive outcomes",
            ('fear', 'neutral'): "Ground yourself in the present moment",
            ('fear', 'sadness'): "Share your concerns with someone you trust",
            ('fear', 'anger'): "Channel fear into productive action",
            ('fear', 'disgust'): "Challenge negative thoughts",
            
            ('disgust', 'joy'): "Focus on things you appreciate",
            ('disgust', 'neutral'): "Practice acceptance",
            ('disgust', 'sadness'): "Explore underlying values",
            ('disgust', 'anger'): "Set boundaries",
            ('disgust', 'fear'): "Examine core concerns",
            
            ('neutral', 'joy'): "Engage in activities you enjoy",
            ('neutral', 'sadness'): "Allow yourself to feel emotions",
            ('neutral', 'anger'): "Identify sources of frustration",
            ('neutral', 'fear'): "Acknowledge concerns",
            ('neutral', 'disgust'): "Identify values being challenged",
            
            ('joy', 'neutral'): "Practice mindfulness",
            ('joy', 'sadness'): "Reflect on meaningful experiences",
            ('joy', 'anger'): "Channel energy constructively",
            ('joy', 'fear'): "Consider growth opportunities",
            ('joy', 'disgust'): "Examine values and boundaries",
            
            ('surprise', 'joy'): "Embrace the unexpected",
            ('surprise', 'neutral'): "Reflect on what surprised you",
            ('surprise', 'sadness'): "Process your feelings about the surprise",
            ('surprise', 'anger'): "Consider why this triggered anger",
            ('surprise', 'fear'): "Identify what feels threatening",
            ('surprise', 'disgust'): "Examine your boundaries"
        }
        
        # Get default action
        emotion_pair = (from_emotion, to_emotion)
        action = actions.get(emotion_pair)
        
        # If no default action found, use generic action
        if not action:
            if to_emotion == "joy" or to_emotion == "surprise":
                action = "Focus on positive aspects of your life"
            elif to_emotion == "neutral":
                action = "Practice mindfulness and stay present"
            elif to_emotion == "sadness":
                action = "Allow yourself to process emotions"
            elif to_emotion == "anger":
                action = "Express feelings constructively"
            elif to_emotion == "fear":
                action = "Identify and address specific concerns"
            elif to_emotion == "disgust":
                action = "Examine your values and boundaries"
            else:
                action = "Reflect on your feelings"
                
        return action
    
    def get_emotion_history(self, user_email, limit=10):
        """
        Get the user's emotion history.
        
        Args:
            user_email (str): The user's email
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of emotional states
        """
        # Try to get from HDFS first if available
        try:
            hdfs_path = f"/user/reflectly/emotional_states/{user_email}/history.json"
            if self.hdfs_service.check_file_exists(hdfs_path):
                history_json = self.hdfs_service.read_file(hdfs_path)
                history = json.loads(history_json)
                logger.info(f"Retrieved emotion history from HDFS for user {user_email}")
                return history[:limit]  # Limit the results
        except Exception as e:
            logger.warning(f"Failed to retrieve emotion history from HDFS: {e}. Falling back to MongoDB.")
        
        # Fall back to MongoDB
        states = list(self.emotions_collection.find(
            {'user_email': user_email},
            sort=[('timestamp', -1)],
            limit=limit
        ))
        
        # Convert ObjectId to string
        for state in states:
            state['_id'] = str(state['_id'])
            # Convert datetime to string for JSON serialization
            if 'timestamp' in state and isinstance(state['timestamp'], datetime.datetime):
                state['timestamp'] = state['timestamp'].isoformat()
        
        return states
    
    def get_suggested_actions(self, user_email, current_emotion):
        """
        Get suggested actions for transitioning from the current emotional state.
        This implementation returns personalized suggestions based on the user's emotional history.
        
        Args:
            user_email (str): The user's email
            current_emotion (str): Current emotional state
            
        Returns:
            list: List of suggested actions
        """
        # Define generic suggestions for each emotion type as fallback
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
        
        # If current emotion is already positive, return generic suggestions
        if current_emotion in self.positive_emotions:
            return generic_suggestions.get(current_emotion, generic_suggestions['neutral'])
        
        # Try to get personalized suggestions from Spark analysis if available
        try:
            if self.spark_service.check_connection() and self.hdfs_service.check_connection():
                hdfs_path = f"/user/reflectly/recommendations/{user_email}/{current_emotion}.json"
                if self.hdfs_service.check_file_exists(hdfs_path):
                    recommendations_json = self.hdfs_service.read_file(hdfs_path)
                    recommendations = json.loads(recommendations_json)
                    if 'actions' in recommendations and len(recommendations['actions']) >= 2:
                        logger.info(f"Retrieved personalized recommendations from HDFS for user {user_email}")
                        return recommendations['actions']
        except Exception as e:
            logger.warning(f"Failed to retrieve recommendations from HDFS: {e}. Falling back to database.")
        
        # Find personalized suggestions based on user's emotional history
        personalized_suggestions = self._find_personalized_path_suggestions(user_email, current_emotion)
        
        # If we have personalized suggestions, use them; otherwise fall back to generic
        if personalized_suggestions and len(personalized_suggestions) >= 2:
            return personalized_suggestions
        else:
            return generic_suggestions.get(current_emotion, generic_suggestions['neutral'])
    
    def _find_personalized_path_suggestions(self, user_email, current_emotion):
        """
        Find personalized suggestions based on the user's emotional transition history.
        Identifies paths that have previously led from the current emotion to positive emotions.
        
        Args:
            user_email (str): The user's email
            current_emotion (str): Current emotional state
            
        Returns:
            list: List of personalized suggested actions
        """
        # Get transitions from the current emotion to any positive emotion
        transitions = list(self.transitions_collection.find({
            'user_email': user_email,
            'from_emotion': current_emotion,
            'to_emotion': {'$in': self.positive_emotions}
        }).sort('timestamp', -1).limit(10))
        
        if not transitions:
            return []
        
        # Get the emotional states involved in these transitions
        state_ids = []
        for transition in transitions:
            state_ids.append(ObjectId(transition['from_state_id']))
            state_ids.append(ObjectId(transition['to_state_id']))
        
        # Get the journal entries associated with these emotional states
        states = list(self.emotions_collection.find({
            '_id': {'$in': state_ids}
        }))
        
        # Create a mapping of state IDs to entry IDs
        state_to_entry = {}
        for state in states:
            if state.get('entry_id'):
                state_to_entry[str(state['_id'])] = state['entry_id']
        
        # Extract personalized suggestions based on content analysis
        personalized_suggestions = [
            f"Try activities that helped you before: {self._extract_activity_from_transition(transition)}"
            for transition in transitions
            if self._extract_activity_from_transition(transition)
        ]
        
        # Add some generic transition suggestions if we don't have enough
        if len(personalized_suggestions) < 3:
            if current_emotion == 'sadness':
                personalized_suggestions.append("Recall a happy memory and focus on the positive feelings")
            elif current_emotion == 'anger':
                personalized_suggestions.append("Practice deep breathing and count to 10 before responding")
            elif current_emotion == 'fear':
                personalized_suggestions.append("Write down your fears and challenge each one with evidence")
            elif current_emotion == 'disgust':
                personalized_suggestions.append("Focus on something beautiful or inspiring in your environment")
        
        # Limit to 4 suggestions
        return personalized_suggestions[:4]
    
    def _extract_activity_from_transition(self, transition):
        """
        Extract a potential activity that led to a positive emotional transition.
        This is a simplified implementation that could be enhanced with NLP in production.
        
        Args:
            transition: The emotional transition document
            
        Returns:
            str: A suggested activity or None
        """
        # Check if the transition has actions
        if 'actions' in transition and transition['actions']:
            # Get the most successful action
            actions = transition['actions']
            if isinstance(actions, list) and actions:
                # Find the action with the highest success rate
                best_action = max(actions, key=lambda x: x.get('success_rate', 0) if isinstance(x, dict) else 0)
                if isinstance(best_action, dict) and 'description' in best_action:
                    return best_action['description']
        
        return None
    
    def get_emotional_path(self, user_email, current_emotion, target_emotion, max_depth=10):
        """
        Get a path from current_emotion to target_emotion using A* search.
        Leverages data-driven transition probabilities and log-transformed costs.
        
        Args:
            user_email (str): The user's email
            current_emotion (str): Current emotional state
            target_emotion (str): Target emotional state
            max_depth (int): Maximum path depth
            
        Returns:
            dict: Path information with path, actions, cost metrics and success status
        """
        # Try to use Spark for processing if available
        try:
            if self.spark_service.check_connection() and self.hdfs_service.check_connection():
                logger.info(f"Using Spark for path finding from {current_emotion} to {target_emotion}")
                
                # Create the graph using our data-driven transition probabilities
                graph = self.get_graph(user_email)
                
                # Save graph to HDFS for Spark job to use
                graph_json = json.dumps(graph)
                hdfs_input_path = f"/reflectly/emotional_graph/{user_email}/graph.json"
                self.hdfs_service.write_file(hdfs_input_path, graph_json)
                
                # Set up output path
                hdfs_output_path = f"/reflectly/emotional_paths/{user_email}/{current_emotion}_to_{target_emotion}"
                
                # Run the path finding job using our script
                cmd = [
                    "/Users/manodhyaopallage/Refection/run_spark_jobs.sh",
                    "--user-email", user_email,
                    "--current-emotion", current_emotion,
                    "--target-emotion", target_emotion,
                    "--max-depth", str(max_depth),
                    "--hdfs-base-path", "/reflectly",
                    "path_finding"
                ]
                
                # Execute the command
                import subprocess
                try:
                    logger.info(f"Executing path finding command: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        logger.info("Path finding job completed successfully")
                        
                        # Read result from HDFS
                        if self.hdfs_service.check_file_exists(hdfs_output_path):
                            result_json = self.hdfs_service.read_file(hdfs_output_path)
                            path_result = json.loads(result_json)
                            logger.info(f"Retrieved path result from Spark job: {path_result}")
                            return path_result
                    else:
                        logger.warning(f"Path finding job failed: {result.stderr}. Falling back to local processing.")
                except subprocess.TimeoutExpired:
                    logger.warning("Path finding job timed out. Falling back to local processing.")
                except Exception as e:
                    logger.warning(f"Error executing path finding job: {e}. Falling back to local processing.")
        except Exception as e:
            logger.warning(f"Failed to use Spark for path finding: {e}. Falling back to local processing.")
        
        # Fall back to local processing using A* search algorithm
        logger.info(f"Using local A* search for path finding from {current_emotion} to {target_emotion}")
        
        # Update our search algorithm with the latest graph
        graph = self.get_graph(user_email)
        self.search_algorithm.update_graph(graph)
        
        # Find path using enhanced A* search algorithm
        path = self.search_algorithm.find_path(user_email, current_emotion, target_emotion, max_depth)
        
        # If no path was found, return empty path info
        if not path or len(path) == 0:
            path_info = {
                'path': [],
                'actions': [],
                'length': 0,
                'success': False,
                'message': "No path found"
            }
            
            # Publish failed path attempt to Kafka for analysis
            try:
                self.kafka_service.publish_message(
                    "emotional-path-attempts",
                    user_email,
                    json.dumps({
                        "user_email": user_email,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "from_emotion": current_emotion,
                        "to_emotion": target_emotion,
                        "success": False,
                        "reason": "No path found"
                    })
                )
            except Exception as e:
                logger.warning(f"Failed to publish failed path attempt to Kafka: {e}")
                
            return path_info
            
        # Calculate path cost based on transition probabilities
        path_cost = 0
        transition_probs = self.get_transition_probabilities(user_email)
        
        # Extract actions for each transition in the path
        actions = []
        transitions = []
        
        for i in range(len(path) - 1):
            from_emotion = path[i]
            to_emotion = path[i + 1]
            
            # Get probability for this transition
            prob = transition_probs.get(from_emotion, {}).get(to_emotion, 0)
            
            # Add to path cost (-log transformation as in get_graph)
            transition_cost = -math.log(prob + 1e-10) if prob > 0 else float('inf')
            path_cost += transition_cost
            
            # Get personalized action for this transition if available
            action = self._get_personalized_action(user_email, from_emotion, to_emotion)
            if not action:
                # Fall back to default action
                action = self._get_default_action(from_emotion, to_emotion)
                
            actions.append(action)
            transitions.append({
                "from": from_emotion,
                "to": to_emotion,
                "probability": prob,
                "cost": transition_cost,
                "action": action
            })
            
        path_info = {
            'path': path,
            'actions': actions,
            'transitions': transitions,
            'length': len(path) - 1,
            'cost': path_cost,
            'avg_probability': math.exp(-path_cost / max(1, len(path) - 1)),  # Convert back from log space
            'success': True,
            'message': "Path found successfully"
        }
        
        # Publish successful path to Kafka for analysis
        try:
            self.kafka_service.publish_message(
                "emotional-paths",
                user_email,
                json.dumps({
                    "user_email": user_email,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "from_emotion": current_emotion,
                    "to_emotion": target_emotion,
                    "path_length": len(path) - 1,
                    "path": path,
                    "cost": path_cost,
                    "success": True
                })
            )
            
            # Also save the path to HDFS for later analysis
            if self.hdfs_service.check_connection():
                hdfs_path = f"/user/reflectly/emotional_paths/{user_email}/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                self.hdfs_service.write_file(hdfs_path, json.dumps(path_info))
        except Exception as e:
            logger.warning(f"Failed to publish path to Kafka or HDFS: {e}")
            
        return path_info
    
    def get_user_transitions(self, user_email):
        """
        Get all transitions for a user.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            list: List of transitions
        """
        # Try to get from HDFS first if available
        try:
            hdfs_path = f"/user/reflectly/emotional_transitions/{user_email}/transitions.json"
            if self.hdfs_service.check_file_exists(hdfs_path):
                transitions_json = self.hdfs_service.read_file(hdfs_path)
                transitions = json.loads(transitions_json)
                logger.info(f"Retrieved transitions from HDFS for user {user_email}")
                return transitions
        except Exception as e:
            logger.warning(f"Failed to retrieve transitions from HDFS: {e}. Falling back to MongoDB.")
        
        # Fall back to MongoDB
        transitions = list(self.transitions_collection.find({'user_email': user_email}))
        
        # Convert ObjectId to string and datetime to string for JSON serialization
        for transition in transitions:
            transition['_id'] = str(transition['_id'])
            if 'timestamp' in transition and isinstance(transition['timestamp'], datetime.datetime):
                transition['timestamp'] = transition['timestamp'].isoformat()
        
        return transitions
    
    def add_action_to_transition(self, transition_id, action_description, success_rate=0.5):
        """
        Add an action to a transition.
        
        Args:
            transition_id (str): Transition ID
            action_description (str): Action description
            success_rate (float): Success rate
            
        Returns:
            dict: Added action
        """
        action = {
            "description": action_description,
            "timestamp": datetime.datetime.now().isoformat(),
            "success_rate": success_rate
        }
        
        # Update in MongoDB
        result = self.transitions_collection.update_one(
            {"_id": ObjectId(transition_id)},
            {"$push": {"actions": action}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Added action to transition {transition_id}: {action_description}")
            
            # Get the updated transition
            transition = self.transitions_collection.find_one({"_id": ObjectId(transition_id)})
            
            # Publish to Kafka for processing
            if transition:
                try:
                    # Convert ObjectId to string and datetime to string for JSON serialization
                    transition['_id'] = str(transition['_id'])
                    if 'timestamp' in transition and isinstance(transition['timestamp'], datetime.datetime):
                        transition['timestamp'] = transition['timestamp'].isoformat()
                    
                    self.kafka_service.publish_message(
                        "emotional-transitions", 
                        transition["user_email"], 
                        json.dumps(transition)
                    )
                    logger.info(f"Published updated transition to Kafka: {transition_id}")
                except Exception as e:
                    logger.error(f"Failed to publish updated transition to Kafka: {e}")
        
        return action
        
    def _get_personalized_action(self, user_email, from_emotion, to_emotion):
        """
        Get a personalized action for a transition based on user history.
        
        Args:
            user_email (str): The user's email
            from_emotion (str): Source emotion
            to_emotion (str): Target emotion
            
        Returns:
            str: Personalized action or None if not available
        """        
        # First check if there's a cached recommendation in HDFS
        try:
            if self.hdfs_service.check_connection():
                hdfs_path = f"/user/reflectly/personalized_actions/{user_email}/{from_emotion}_to_{to_emotion}.json"
                if self.hdfs_service.check_file_exists(hdfs_path):
                    action_json = self.hdfs_service.read_file(hdfs_path)
                    action_data = json.loads(action_json)
                    if 'action' in action_data and action_data.get('timestamp', '') > (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat():
                        # Only use if less than a week old
                        return action_data['action']
        except Exception as e:
            logger.warning(f"Failed to retrieve personalized action from HDFS: {e}")
        
        # Look for successful transitions in user history
        transitions = list(self.transitions_collection.find({
            'user_email': user_email,
            'from_emotion': from_emotion,
            'to_emotion': to_emotion,
            'actions': {"$exists": True, "$ne": []}
        }))
        
        if transitions:
            # Find the most successful action based on effectiveness
            best_action = None
            best_effectiveness = 0
            
            for transition in transitions:
                for action in transition.get('actions', []):
                    if action.get('success_rate', 0) > best_effectiveness:
                        best_effectiveness = action.get('success_rate', 0)
                        best_action = action.get('description')
            
            if best_action:
                return best_action
                
        return None
        
    def _get_default_action(self, from_emotion, to_emotion):
        """
        Get a default action for transitioning from one emotion to another.
        Used when no personalized actions are available.
        
        Args:
            from_emotion (str): Source emotion
            to_emotion (str): Target emotion
            
        Returns:
            str: Default action recommendation
        """
        # Define default actions for common transitions
        default_actions = {
            # From negative to positive emotions
            ('anxious', 'calm'): "Practice deep breathing exercises for 5 minutes",
            ('anxious', 'happy'): "List three things you're grateful for today",
            ('anxious', 'relaxed'): "Take a short walk outside or practice progressive muscle relaxation",
            
            ('angry', 'calm'): "Count to ten slowly and practice deep breathing",
            ('angry', 'happy'): "Engage in a physical activity you enjoy",
            ('angry', 'neutral'): "Write down your thoughts in a journal",
            
            ('sad', 'happy'): "Listen to uplifting music or watch a comedy show",
            ('sad', 'calm'): "Practice mindfulness meditation for 5-10 minutes",
            ('sad', 'neutral'): "Reach out to a friend or family member for a brief chat",
            
            ('stressed', 'calm'): "Take a tech break and enjoy a cup of tea",
            ('stressed', 'relaxed'): "Practice progressive muscle relaxation",
            ('stressed', 'happy'): "Take a short break to do something you enjoy",
            
            ('fear', 'calm'): "Practice the 5-4-3-2-1 grounding technique",
            ('fear', 'neutral'): "Write down what you're afraid of and evaluate if it's realistic",
            
            # From neutral to positive emotions
            ('neutral', 'happy'): "Do something creative or engage in a hobby you enjoy",
            ('neutral', 'excited'): "Plan an activity you're looking forward to",
            ('neutral', 'relaxed'): "Listen to calming music or take a warm bath",
            
            # General positive reinforcement
            ('happy', 'excited'): "Share your happiness with someone else",
            ('calm', 'relaxed'): "Continue with mindfulness practices that work for you",
            
            # Handling negative transitions
            ('happy', 'sad'): "Acknowledge your feelings and remember that all emotions are temporary",
            ('calm', 'anxious'): "Notice your anxious thoughts and try to reframe them",
            ('relaxed', 'stressed'): "Break down stressors into manageable tasks"
        }
        
        # Map from IEMOCAP emotions to standard emotions if needed
        if self.using_dataset_transitions and (from_emotion in self.iemocap_to_standard or to_emotion in self.iemocap_to_standard):
            mapped_from = self.iemocap_to_standard.get(from_emotion, from_emotion)
            mapped_to = self.iemocap_to_standard.get(to_emotion, to_emotion)
            key = (mapped_from, mapped_to)
            if key in default_actions:
                return default_actions[key]
        
        # Check if we have a default action for this transition
        key = (from_emotion, to_emotion)
        if key in default_actions:
            return default_actions[key]
        
        # If we don't have a specific action, provide category-based actions
        if from_emotion in self.negative_emotions and to_emotion in self.positive_emotions:
            return "Practice self-care and positive reframing of your thoughts"
        elif from_emotion in self.negative_emotions and to_emotion in self.negative_emotions:
            return "Acknowledge your feelings without judgment and consider what might help you move toward a more positive state"
        elif from_emotion in self.positive_emotions and to_emotion in self.negative_emotions:
            return "Remember that all emotions provide valuable information. Take note of what might have shifted your emotional state"
        elif from_emotion in self.positive_emotions and to_emotion in self.positive_emotions:
            return "Continue with activities and thoughts that maintain your positive emotional state"
        
        # Default fallback
        return f"Reflect on what helps you transition from {from_emotion} to {to_emotion}"
        
    def _find_personalized_path_suggestions(self, user_email, current_emotion, target_emotions=None, max_paths=3, max_depth=5):
        """
        Find personalized suggestions for emotional paths based on user history and IEMOCAP dataset.
        
        This method leverages both the user's historical emotional transitions and the IEMOCAP dataset
        to recommend optimal emotional paths - either to specific target emotions or to generally
        positive emotional states.
        
        Args:
            user_email (str): The user's email
            current_emotion (str): Current emotional state
            target_emotions (list, optional): Specific target emotions to reach. If None, will 
                                            suggest paths to positive emotions.
            max_paths (int): Maximum number of paths to suggest
            max_depth (int): Maximum path depth
            
        Returns:
            list: List of suggested emotional paths with actions and insights
        """
        logger.info(f"Finding personalized path suggestions for user {user_email} from {current_emotion}")
        
        # If no target emotions specified, suggest paths to positive emotions
        if not target_emotions:
            target_emotions = self.positive_emotions
            logger.info(f"No target emotions specified, using positive emotions: {target_emotions}")
        
        # Get user's emotion profile to personalize suggestions
        user_profile = self._get_user_emotion_profile(user_email)
        
        # Get transition probabilities using our data-driven approach
        transition_probs = self.get_transition_probabilities(user_email)
        
        # Find most frequent positive emotions for this user if we have history
        if user_profile and 'frequent_positive_emotions' in user_profile:
            # Prioritize user's most frequent positive emotions if they're in our target list
            prioritized_targets = [e for e in user_profile['frequent_positive_emotions'] 
                                 if e in target_emotions][:max_paths]
            
            # Add other target emotions if we don't have enough
            remaining_targets = [e for e in target_emotions 
                              if e not in prioritized_targets][:max_paths-len(prioritized_targets)]
            
            target_emotions = prioritized_targets + remaining_targets
            logger.info(f"Prioritized target emotions based on user profile: {target_emotions}")
        
        # Initialize results
        path_suggestions = []
        
        # Try using Spark for batch processing of multiple paths if available
        try:
            if self.spark_service.check_connection() and len(target_emotions) > 1:
                logger.info(f"Using Spark for batch pathfinding from {current_emotion} to {target_emotions}")
                
                # Create the graph using our data-driven transition probabilities
                graph = self.get_graph(user_email)
                
                # Save graph to HDFS for Spark job to use
                graph_json = json.dumps(graph)
                hdfs_input_path = f"/reflectly/emotional_graph/{user_email}/graph.json"
                self.hdfs_service.write_file(hdfs_input_path, graph_json)
                
                # Save target emotions to HDFS
                targets_json = json.dumps({
                    "current_emotion": current_emotion,
                    "target_emotions": target_emotions,
                    "max_depth": max_depth
                })
                targets_path = f"/reflectly/emotional_graph/{user_email}/targets.json"
                self.hdfs_service.write_file(targets_path, targets_json)
                
                # Set up output path
                hdfs_output_path = f"/reflectly/emotional_paths/{user_email}/batch_suggestions"
                
                # Run the batch path finding job
                cmd = [
                    "/Users/manodhyaopallage/Refection/run_spark_jobs.sh",
                    "--user-email", user_email,
                    "--hdfs-base-path", "/reflectly",
                    "batch_path_finding"
                ]
                
                # Execute the command
                import subprocess
                try:
                    logger.info(f"Executing batch path finding command: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # Allow more time for batch
                    
                    if result.returncode == 0:
                        logger.info("Batch path finding job completed successfully")
                        
                        # Read result from HDFS
                        if self.hdfs_service.check_file_exists(hdfs_output_path):
                            result_json = self.hdfs_service.read_file(hdfs_output_path)
                            path_suggestions = json.loads(result_json)
                            logger.info(f"Retrieved {len(path_suggestions)} paths from Spark job")
                            return path_suggestions
                    else:
                        logger.warning(f"Batch path finding job failed: {result.stderr}. Falling back to sequential processing.")
                except Exception as e:
                    logger.warning(f"Error executing batch path finding job: {e}. Falling back to sequential processing.")
        except Exception as e:
            logger.warning(f"Failed to use Spark for batch path finding: {e}. Falling back to sequential processing.")
        
        # Fall back to sequential processing - find path to each target emotion
        logger.info(f"Using sequential A* search for finding paths from {current_emotion} to {target_emotions}")
        
        # Get common transitions for this emotion from the dataset
        common_next_emotions = self._get_common_next_emotions(current_emotion, user_email)
        
        # Process each target emotion to find best path
        for target in target_emotions[:max_paths]:
            # Skip if target is the same as current emotion
            if target == current_emotion:
                continue
                
            # Find path using our enhanced A* search
            path_info = self.get_emotional_path(user_email, current_emotion, target, max_depth)
            
            # Only include successful paths
            if path_info and path_info.get('success', False):
                # Add target emotion metadata
                path_info['target_emotion'] = target
                path_info['is_common_path'] = target in common_next_emotions
                
                # Generate personalized insight for this path
                path_info['personalized_insight'] = self._generate_path_insight(path_info, user_profile)
                
                # Add to suggestions
                path_suggestions.append(path_info)
        
        # If we have fewer than desired paths, try finding paths to common positive transitions 
        # that weren't in our original target list
        if len(path_suggestions) < max_paths and common_next_emotions:
            additional_targets = [e for e in common_next_emotions 
                               if e not in target_emotions and e != current_emotion][:max_paths-len(path_suggestions)]
            
            for target in additional_targets:
                path_info = self.get_emotional_path(user_email, current_emotion, target, max_depth)
                
                if path_info and path_info.get('success', False):
                    path_info['target_emotion'] = target
                    path_info['is_common_path'] = True
                    path_info['personalized_insight'] = self._generate_path_insight(path_info, user_profile)
                    path_suggestions.append(path_info)
        
        # Sort paths by cost (lower is better)
        path_suggestions.sort(key=lambda x: x.get('cost', float('inf')))
        
        # Limit to max_paths
        return path_suggestions[:max_paths]
    
    def _get_common_next_emotions(self, emotion, user_email):
        """
        Get common next emotions for a given emotion from IEMOCAP dataset
        and user history.
        
        Args:
            emotion (str): The emotion to find common transitions from
            user_email (str): The user's email
            
        Returns:
            list: List of common next emotions sorted by probability
        """
        # Get transition probabilities
        transition_probs = self.get_transition_probabilities(user_email)
        
        # If we have probabilities for the current emotion, return the top ones
        if emotion in transition_probs:
            # Sort emotions by probability (descending) and filter those with probability > 0.1
            next_emotions = sorted(
                [(e, p) for e, p in transition_probs[emotion].items() if p > 0.1],
                key=lambda x: x[1],
                reverse=True
            )
            
            # Return emotion names
            return [e for e, _ in next_emotions]
            
        return []
    
    def _get_user_emotion_profile(self, user_email):
        """
        Get a user's emotional profile based on their history.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: User emotion profile with patterns and preferences
        """
        # Check if we have a cached profile in HDFS
        try:
            if self.hdfs_service.check_connection():
                profile_path = f"/user/reflectly/emotional_profiles/{user_email}/profile.json"
                if self.hdfs_service.check_file_exists(profile_path):
                    profile_json = self.hdfs_service.read_file(profile_path)
                    profile = json.loads(profile_json)
                    
                    # Check if profile is recent (less than a day old)
                    profile_time = datetime.datetime.fromisoformat(profile.get('timestamp', '2000-01-01T00:00:00'))
                    if (datetime.datetime.now() - profile_time).total_seconds() < 86400:  # 24 hours
                        return profile
        except Exception as e:
            logger.warning(f"Failed to retrieve user emotion profile from HDFS: {e}")
        
        # If no recent profile found, generate one
        profile = self._generate_user_emotion_profile(user_email)
        
        # Save profile to HDFS if available
        try:
            if self.hdfs_service.check_connection() and profile:
                profile_path = f"/user/reflectly/emotional_profiles/{user_email}/profile.json"
                self.hdfs_service.write_file(profile_path, json.dumps(profile))
                logger.info(f"Saved user emotion profile to HDFS: {profile_path}")
        except Exception as e:
            logger.warning(f"Failed to save user emotion profile to HDFS: {e}")
            
        return profile
    
    def _generate_user_emotion_profile(self, user_email):
        """
        Generate a user's emotional profile based on their history.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: User emotion profile with patterns and preferences
        """
        # Get user's emotion history
        emotions = list(self.emotions_collection.find({'user_email': user_email}).sort('timestamp', -1).limit(100))
        
        if not emotions:
            return None
            
        # Initialize profile
        profile = {
            'user_email': user_email,
            'timestamp': datetime.datetime.now().isoformat(),
            'emotion_counts': {},
            'frequent_emotions': [],
            'frequent_positive_emotions': [],
            'frequent_negative_emotions': [],
            'common_transitions': {},
            'average_duration': {}
        }
        
        # Count emotions
        emotion_counts = {}
        for emotion_doc in emotions:
            emotion = emotion_doc.get('primary_emotion', 'neutral')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
        # Get frequent emotions (appearing more than once)
        frequent_emotions = sorted(
            [(e, c) for e, c in emotion_counts.items() if c > 1],
            key=lambda x: x[1],
            reverse=True
        )
        
        profile['emotion_counts'] = emotion_counts
        profile['frequent_emotions'] = [e for e, _ in frequent_emotions[:5]]
        
        # Get frequent positive and negative emotions
        for emotion, count in frequent_emotions:
            if emotion in self.positive_emotions:
                profile['frequent_positive_emotions'].append(emotion)
            elif emotion in self.negative_emotions:
                profile['frequent_negative_emotions'].append(emotion)
                
        # Limit to top 5
        profile['frequent_positive_emotions'] = profile['frequent_positive_emotions'][:5]
        profile['frequent_negative_emotions'] = profile['frequent_negative_emotions'][:5]
        
        # Get transitions
        transitions = list(self.transitions_collection.find({'user_email': user_email}))
        
        # Count transitions
        transition_counts = {}
        for transition in transitions:
            from_emotion = transition.get('from_emotion', 'neutral')
            to_emotion = transition.get('to_emotion', 'neutral')
            
            if from_emotion not in transition_counts:
                transition_counts[from_emotion] = {}
                
            transition_counts[from_emotion][to_emotion] = transition_counts[from_emotion].get(to_emotion, 0) + 1
            
        # Get common transitions (sort by count)
        common_transitions = {}
        for from_emotion, to_counts in transition_counts.items():
            sorted_transitions = sorted(
                [(to, count) for to, count in to_counts.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            common_transitions[from_emotion] = [to for to, _ in sorted_transitions[:3]]
            
        profile['common_transitions'] = common_transitions
        
        # Calculate average duration of emotions (if we have timestamps)
        if len(emotions) > 1:
            emotion_durations = {}
            emotion_timestamps = {}
            
            # Sort emotions by timestamp
            sorted_emotions = sorted(emotions, key=lambda x: x.get('timestamp', datetime.datetime.min))
            
            for i in range(len(sorted_emotions) - 1):
                current = sorted_emotions[i]
                next_doc = sorted_emotions[i + 1]
                
                current_emotion = current.get('primary_emotion', 'neutral')
                current_time = current.get('timestamp')
                next_time = next_doc.get('timestamp')
                
                if current_time and next_time and current_emotion == next_doc.get('primary_emotion', 'neutral'):
                    duration = (next_time - current_time).total_seconds() / 3600  # hours
                    
                    if current_emotion not in emotion_durations:
                        emotion_durations[current_emotion] = []
                        
                    emotion_durations[current_emotion].append(duration)
            
            # Calculate averages
            for emotion, durations in emotion_durations.items():
                if durations:
                    profile['average_duration'][emotion] = sum(durations) / len(durations)
        
        return profile
    
    def _generate_path_insight(self, path_info, user_profile):
        """
        Generate personalized insight for an emotional path.
        
        Args:
            path_info (dict): Path information
            user_profile (dict): User emotion profile
            
        Returns:
            str: Personalized insight
        """
        if not path_info or not path_info.get('path'):
            return "No path available to generate insights."
            
        path = path_info.get('path', [])
        if len(path) < 2:
            return "Path is too short to generate meaningful insights."
            
        current_emotion = path[0]
        target_emotion = path[-1]
        intermediate_emotions = path[1:-1] if len(path) > 2 else []
        
        insights = []
        
        # Check if this is a common path for the user
        if user_profile and 'common_transitions' in user_profile:
            common_transitions = user_profile.get('common_transitions', {})
            
            if current_emotion in common_transitions and target_emotion in common_transitions.get(current_emotion, []):
                insights.append(f"This is a path you've successfully taken before, moving from {current_emotion} to {target_emotion}.")
        
        # Check if path goes through common positive emotions for this user
        if user_profile and 'frequent_positive_emotions' in user_profile:
            frequent_positive = user_profile.get('frequent_positive_emotions', [])
            positive_in_path = [e for e in intermediate_emotions if e in frequent_positive]
            
            if positive_in_path:
                emotions_str = ", ".join(positive_in_path)
                insights.append(f"This path includes {emotions_str}, which you frequently experience positively.")
        
        # Comment on path complexity
        if len(path) > 3:
            insights.append(f"This is a more complex emotional journey with {len(path)-1} transitions, but each step is achievable.")
        else:
            insights.append("This is a direct path with minimal transitions.")
            
        # Add insight about the target emotion
        if target_emotion in self.positive_emotions:
            insights.append(f"Reaching {target_emotion} can help increase your overall emotional well-being.")
            
        # Return combined insights
        if insights:
            return " ".join(insights)
        else:
            return f"This path from {current_emotion} to {target_emotion} represents an achievable emotional transition."
    
    def get_emotional_improvement_paths(self, user_email, current_emotion=None, target_emotions=None, max_paths=3, max_depth=5):
        """
        Find and return optimal emotional improvement paths for a user.
        
        This public method leverages the personalized path suggestions functionality
        to provide tailored recommendations for improving emotional state.
        It combines data-driven insights from the IEMOCAP dataset with the user's
        emotional history to suggest the most effective paths.
        
        Args:
            user_email (str): The user's email
            current_emotion (str, optional): Current emotional state. If None, will be retrieved from the most recent record.
            target_emotions (list, optional): Specific target emotions to reach. If None, will suggest paths to positive emotions.
            max_paths (int): Maximum number of paths to suggest
            max_depth (int): Maximum path depth
            
        Returns:
            dict: Response containing suggested paths and metadata
        """
        try:
            # If current emotion not provided, get the most recent one
            if not current_emotion:
                most_recent = self._get_most_recent_emotion(user_email)
                if most_recent:
                    current_emotion = most_recent.get('primary_emotion', 'neutral')
                else:
                    return {
                        'success': False,
                        'error': 'No recent emotional states found for user',
                        'suggestions': []
                    }
            
            # Validate current emotion is in our standard set
            if current_emotion not in self.positive_emotions + self.negative_emotions + self.neutral_emotions and current_emotion not in self.iemocap_emotions:
                return {
                    'success': False,
                    'error': f'Invalid emotion: {current_emotion}',
                    'suggestions': []
                }
                
            # If target emotions provided, validate them
            if target_emotions:
                valid_targets = []
                invalid_targets = []
                valid_emotions = self.positive_emotions + self.negative_emotions + self.neutral_emotions + self.iemocap_emotions
                
                for emotion in target_emotions:
                    if emotion in valid_emotions:
                        valid_targets.append(emotion)
                    else:
                        invalid_targets.append(emotion)
                        
                if invalid_targets:
                    logger.warning(f"Invalid target emotions provided: {invalid_targets}")
                    
                target_emotions = valid_targets
                
                # If no valid targets, return error
                if not target_emotions:
                    return {
                        'success': False,
                        'error': 'No valid target emotions provided',
                        'suggestions': []
                    }
            
            # Get personalized path suggestions
            path_suggestions = self._find_personalized_path_suggestions(
                user_email, 
                current_emotion, 
                target_emotions, 
                max_paths, 
                max_depth
            )
            
            # If no suggestions found, return empty response
            if not path_suggestions:
                return {
                    'success': True,
                    'message': 'No suitable emotional paths found',
                    'current_emotion': current_emotion,
                    'suggestions': []
                }
                
            # Format the response
            response = {
                'success': True,
                'message': f'Found {len(path_suggestions)} possible emotional improvement paths',
                'current_emotion': current_emotion,
                'generated_at': datetime.datetime.now().isoformat(),
                'suggestions': path_suggestions
            }
            
            # Add additional metadata
            emotion_profile = self._get_user_emotion_profile(user_email)
            if emotion_profile:
                response['user_profile'] = {
                    'frequent_emotions': emotion_profile.get('frequent_emotions', []),
                    'frequent_positive_emotions': emotion_profile.get('frequent_positive_emotions', []),
                    'frequent_negative_emotions': emotion_profile.get('frequent_negative_emotions', [])
                }
                
            # Record this suggestion in HDFS if available
            try:
                if self.hdfs_service.check_connection():
                    path = f"/user/reflectly/emotional_improvements/{user_email}/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                    self.hdfs_service.write_file(path, json.dumps(response))
                    logger.info(f"Saved emotional improvement paths to HDFS: {path}")
            except Exception as e:
                logger.warning(f"Failed to save emotional improvement paths to HDFS: {e}")
                
            # Publish to Kafka for analytics
            try:
                self.kafka_service.publish_message(
                    "emotional-improvements",
                    user_email,
                    json.dumps({
                        'user_email': user_email,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'current_emotion': current_emotion,
                        'num_suggestions': len(path_suggestions),
                        'target_emotions': [p.get('target_emotion') for p in path_suggestions if 'target_emotion' in p]
                    })
                )
                logger.info(f"Published emotional improvement paths to Kafka for user {user_email}")
            except Exception as e:
                logger.warning(f"Failed to publish emotional improvement paths to Kafka: {e}")
                
            return response
            
        except Exception as e:
            logger.error(f"Error generating emotional improvement paths: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Failed to generate emotional improvement paths: {str(e)}',
                'suggestions': []
            }
    
    def _get_most_recent_emotion(self, user_email):
        """
        Get the most recent emotional state for a user.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Most recent emotional state or None if not found
        """
        # Try to use HDFS for larger datasets if available
        try:
            if self.hdfs_service.check_connection():
                history_path = f"/user/reflectly/emotional_states/{user_email}/history.json"
                if self.hdfs_service.check_file_exists(history_path):
                    history_json = self.hdfs_service.read_file(history_path)
                    history = json.loads(history_json)
                    if history:
                        return history[0]  # First item is most recent
        except Exception as e:
            logger.warning(f"Failed to retrieve most recent emotional state from HDFS: {e}")
        
        # Fall back to MongoDB
        most_recent = self.emotions_collection.find_one(
            {'user_email': user_email},
            sort=[('timestamp', -1)]
        )
        
        if most_recent:
            # Convert ObjectId to string for JSON serialization
            most_recent['_id'] = str(most_recent['_id'])
            # Convert datetime to string for JSON serialization if needed
            if 'timestamp' in most_recent and isinstance(most_recent['timestamp'], datetime.datetime):
                most_recent['timestamp'] = most_recent['timestamp'].isoformat()
                
        return most_recent
        
    def get_available_emotions(self):
        """
        Get available emotions.
        
        Returns:
            list: Available emotions
        """
        return self.positive_emotions + self.negative_emotions + self.neutral_emotions
    
    def get_graph(self, user_email):
        """
        Convert transition probabilities to a graph representation for A* search.
        Uses log-transformed probabilities for better pathfinding.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Graph representation for A* search
        """
        # Get transition probabilities (using the enhanced method that incorporates IEMOCAP data)
        transition_probs = self.get_transition_probabilities(user_email)
        
        # Initialize graph
        graph = {}
        
        # Build graph with log-transformed edge weights for better pathfinding
        for from_emotion, to_emotions in transition_probs.items():
            graph[from_emotion] = {}
            
            for to_emotion, probability in to_emotions.items():
                # Skip impossible transitions (probability = 0)
                if probability <= 0:
                    continue
                    
                # Transform probability to cost (log transformation)
                # Higher probability = lower cost, add small epsilon to avoid log(0)
                cost = -math.log(probability + 1e-10)
                
                # Add edge to graph
                graph[from_emotion][to_emotion] = cost
                
                # Add special modifiers for specific types of transitions
                # Make it slightly easier to move toward positive emotions and slightly harder to move toward negative
                if to_emotion in self.positive_emotions and from_emotion not in self.positive_emotions:
                    # Slight discount for transitions to positive emotions
                    graph[from_emotion][to_emotion] *= 0.95
                elif to_emotion in self.negative_emotions and from_emotion not in self.negative_emotions:
                    # Slight penalty for transitions to negative emotions (unless from similar emotion)
                    graph[from_emotion][to_emotion] *= 1.05
                elif to_emotion in self.stress_emotions and from_emotion in self.stress_emotions:
                    # Make transitions between stress-related emotions easier, as they're often related
                    graph[from_emotion][to_emotion] *= 0.9
        
        # Publish the graph structure to Kafka for monitoring
        try:
            self.kafka_service.publish_message(
                "emotional-graphs",
                user_email,
                json.dumps({
                    "user_email": user_email,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "graph_size": len(graph),
                    "edge_count": sum(len(edges) for edges in graph.values())
                })
            )
            
            # Also save the graph to HDFS for later analysis
            if self.hdfs_service.check_connection():
                hdfs_path = f"/user/reflectly/emotional_graphs/{user_email}/graph.json"
                self.hdfs_service.write_file(hdfs_path, json.dumps(graph))
        except Exception as e:
            logger.warning(f"Failed to publish graph to Kafka or HDFS: {e}")
        
        return graph
        
    def get_transition_probabilities(self, user_email):
        """
        Get transition probabilities between emotional states for a user.
        Combines IEMOCAP dataset-derived probabilities with user-specific transition history.
        Also leverages Spark-computed transition probabilities if available.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Dictionary mapping from_emotion to a dictionary mapping to_emotion to probability
        """
        # Check if we've cached this result recently to avoid repeated computation
        cache_key = f"{user_email}_transitions"
        if cache_key in self.transition_probability_cache:
            return self.transition_probability_cache[cache_key]
            
        # Try to get transition probabilities from Spark-computed data in HDFS
        try:
            if self.hdfs_service.check_connection():
                hdfs_path = f"/user/reflectly/transition_probabilities/{user_email}/probabilities.json"
                if self.hdfs_service.check_file_exists(hdfs_path):
                    probabilities_json = self.hdfs_service.read_file(hdfs_path)
                    transition_probs = json.loads(probabilities_json)
                    logger.info(f"Retrieved transition probabilities from HDFS for user {user_email}")
                    self.transition_probability_cache[cache_key] = transition_probs
                    return transition_probs
        except Exception as e:
            logger.warning(f"Failed to retrieve transition probabilities from HDFS: {e}. Computing locally.")
        
        # Initialize with dataset-derived transition probabilities if available
        if self.using_dataset_transitions:
            # Start with the IEMOCAP dataset model as our baseline
            transition_probs = self._get_dataset_transition_probabilities()
            logger.info("Using IEMOCAP dataset-derived transition probabilities as baseline")
        else:
            # Initialize with empty transition probabilities if dataset integration not available
            transition_probs = {}
            logger.info("Using default transition probabilities (no dataset integration)")
        
        # Get user-specific transitions to blend with the dataset model
        user_transitions = list(self.transitions_collection.find({
            'user_email': user_email
        }))
        
        # If we have user-specific transitions, blend them with the dataset model
        if user_transitions:
            self._blend_user_transitions(transition_probs, user_transitions)
            logger.info(f"Blended {len(user_transitions)} user-specific transitions with dataset model")
        
        # If we still have no transitions at all (no dataset and no user history),
        # fall back to default transitions
        if not transition_probs:
            default_transitions = list(self.transitions_collection.find({
                'user_email': 'default'
            }))
            
            for transition in default_transitions:
                from_emotion = transition.get('from_emotion')
                to_emotion = transition.get('to_emotion')
                probability = transition.get('probability', 0.5)  # Default to 0.5 if not specified
                
                if from_emotion not in transition_probs:
                    transition_probs[from_emotion] = {}
                
                transition_probs[from_emotion][to_emotion] = probability
            
            logger.info(f"Using {len(default_transitions)} default transitions (no dataset or user history)")
        
        # Cache the result to avoid repeated computation
        self.transition_probability_cache[cache_key] = transition_probs
        
        # If we have Spark and HDFS, save the computed probabilities for future use
        try:
            if self.spark_service.check_connection() and self.hdfs_service.check_connection():
                hdfs_path = f"/user/reflectly/transition_probabilities/{user_email}/probabilities.json"
                self.hdfs_service.write_file(hdfs_path, json.dumps(transition_probs))
                logger.info(f"Saved transition probabilities to HDFS for user {user_email}")
        except Exception as e:
            logger.warning(f"Failed to save transition probabilities to HDFS: {e}")
        
        return transition_probs
    
    def _get_dataset_transition_probabilities(self):
        """
        Get transition probabilities derived from the IEMOCAP dataset.
        
        Returns:
            dict: Dictionary mapping from_emotion to a dictionary mapping to_emotion to probability
        """
        # Initialize transition probabilities dictionary
        transition_probs = {}
        
        # Get all unique emotions from our standard emotions
        all_emotions = set(self.positive_emotions + self.negative_emotions + self.neutral_emotions)
        
        # For each emotion pair, get the transition probability from the IEMOCAP dataset
        for from_emotion in all_emotions:
            # Map our emotion to IEMOCAP emotion category
            mapped_from = self.emotion_mapping.get(from_emotion, from_emotion)
            
            transition_probs[from_emotion] = {}
            
            for to_emotion in all_emotions:
                # Map our emotion to IEMOCAP emotion category
                mapped_to = self.emotion_mapping.get(to_emotion, to_emotion)
                
                # Get the transition probability from the IEMOCAP dataset
                probability = self.iemocap.get_transition_probability(mapped_from, mapped_to)
                
                # Store the probability in our transition probabilities dictionary
                transition_probs[from_emotion][to_emotion] = probability
        
        return transition_probs
    
    def _blend_user_transitions(self, transition_probs, user_transitions):
        """
        Blend user-specific transitions with dataset-derived transitions.
        This gives more weight to the user's actual emotional patterns while still
        leveraging the broader patterns from the dataset.
        
        Args:
            transition_probs (dict): Dictionary of transition probabilities to update
            user_transitions (list): List of user-specific transition documents
        """
        # Count user transitions for each emotion pair
        user_counts = {}
        for transition in user_transitions:
            from_emotion = transition.get('from_emotion')
            to_emotion = transition.get('to_emotion')
            
            if from_emotion not in user_counts:
                user_counts[from_emotion] = {}
            
            if to_emotion not in user_counts[from_emotion]:
                user_counts[from_emotion][to_emotion] = 0
            
            user_counts[from_emotion][to_emotion] += 1
        
        # For each emotion, calculate total transitions and then probabilities
        for from_emotion, to_emotions in user_counts.items():
            total_transitions = sum(to_emotions.values())
            
            # Ensure from_emotion is in transition_probs
            if from_emotion not in transition_probs:
                transition_probs[from_emotion] = {}
            
            # For each destination emotion, calculate the blended probability
            for to_emotion, count in to_emotions.items():
                # Calculate user-specific probability
                user_prob = count / total_transitions
                
                # Get dataset probability, defaulting to 0 if not available
                dataset_prob = transition_probs.get(from_emotion, {}).get(to_emotion, 0.0)
                
                # Blend probabilities: 70% user, 30% dataset when we have sufficient user data
                # As user data increases, we give it more weight
                user_weight = min(0.7, 0.1 + (count / 10) * 0.6)  # 0.1 to 0.7 based on count
                dataset_weight = 1.0 - user_weight
                
                # Calculate blended probability
                blended_prob = (user_prob * user_weight) + (dataset_prob * dataset_weight)
                
                # Update transition probability
                transition_probs[from_emotion][to_emotion] = blended_prob
    
    def get_successful_transitions(self, user_email):
        """
        Get successful transitions for a user.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Successful transitions
        """
        transitions = self.get_user_transitions(user_email)
        
        successful_transitions = {}
        
        for transition in transitions:
            from_emotion = transition.get("from_emotion")
            to_emotion = transition.get("to_emotion")
            actions = transition.get("actions", [])
            
            if not from_emotion or not to_emotion or not actions:
                continue
                
            # Calculate average success rate for this transition
            success_rates = [action.get("success_rate", 0.5) for action in actions if isinstance(action, dict)]
            avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.5
            
            # Store transition with success rate
            transition_key = f"{from_emotion}_{to_emotion}"
            if transition_key not in successful_transitions or avg_success_rate > successful_transitions[transition_key].get("success_rate", 0):
                successful_transitions[transition_key] = {
                    "from_emotion": from_emotion,
                    "to_emotion": to_emotion,
                    "success_rate": avg_success_rate,
                    "actions": actions
                }
                
        return successful_transitions
    
    def process_emotional_data(self):
        """
        Process emotional data using Spark.
        
        Returns:
            bool: Success status
        """
        try:
            # Check if Spark and HDFS are available
            if not self.spark_service.check_connection() or not self.hdfs_service.check_connection():
                logger.warning("Spark or HDFS not available for processing emotional data")
                return False
                
            # Submit Spark job for processing emotional data
            spark_job_path = "/spark/jobs/graph_processing.py"
            
            # Set up job arguments
            job_args = [
                "--input", "/user/reflectly/emotional_states",
                "--output", "/user/reflectly/emotional_transitions",
                "--patterns", "/user/reflectly/emotional_patterns"
            ]
            
            # Submit Spark job
            job_id = self.spark_service.submit_job(spark_job_path, job_args)
            logger.info(f"Submitted emotional data processing job to Spark: {job_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to process emotional data: {e}")
            return False
    
    def import_datasets(self, iemocap_path=None, mental_health_path=None):
        """
        Import IEMOCAP and mental health datasets.
        
        Args:
            iemocap_path (str): Path to IEMOCAP dataset
            mental_health_path (str): Path to mental health dataset
            
        Returns:
            bool: Success status
        """
        try:
            # Check if Spark and HDFS are available
            if not self.spark_service.check_connection() or not self.hdfs_service.check_connection():
                logger.warning("Spark or HDFS not available for importing datasets")
                return False
                
            # Submit Spark job for importing datasets
            spark_job_path = "/spark/jobs/dataset_import.py"
            
            # Set up job arguments
            job_args = ["--output", "/user/reflectly/datasets"]
            
            if iemocap_path:
                job_args.extend(["--iemocap", iemocap_path])
                
            if mental_health_path:
                job_args.extend(["--mental-health", mental_health_path])
            
            # Submit Spark job
            job_id = self.spark_service.submit_job(spark_job_path, job_args)
            logger.info(f"Submitted dataset import job to Spark: {job_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to import datasets: {e}")
            return False
