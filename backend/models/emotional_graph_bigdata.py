"""
Emotional Graph with Big Data Integration
Represents and manages emotional state transitions with Kafka, Hadoop, and Spark integration.
"""
import datetime
import json
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from services.kafka_service import KafkaService
from services.hdfs_service import HDFSService
from services.spark_service import SparkService
from models.search_algorithm import AStarSearch

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
        Initialize the EmotionalGraph with a database connection and big data services.
        
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
        
        # Initialize big data services
        self.kafka_service = KafkaService()
        self.hdfs_service = HDFSService()
        self.spark_service = SparkService()
        
        # Initialize A* search algorithm
        self.search_algorithm = AStarSearch(self)
        
    def record_emotion(self, user_email, emotion_data, entry_id=None):
        """
        Record an emotional state for a user and publish to Kafka.
        
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
        emotion_state['_id'] = str(emotion_state_id)
        
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
        
        Args:
            user_email (str): The user's email
            current_emotion (str): Current emotional state
            target_emotion (str): Target emotional state
            max_depth (int): Maximum path depth
            
        Returns:
            dict: Path information
        """
        # Try to use Spark for processing if available
        try:
            if self.spark_service.check_connection() and self.hdfs_service.check_connection():
                logger.info(f"Using Spark for path finding from {current_emotion} to {target_emotion}")
                
                # Prepare data for Spark job
                user_transitions = self.get_user_transitions(user_email)
                transitions_json = json.dumps(user_transitions)
                
                # Save transitions to HDFS for Spark job to use
                hdfs_input_path = f"/reflectly/emotional_graph/{user_email}/transitions.json"
                self.hdfs_service.write_file(hdfs_input_path, transitions_json)
                
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
        path_result = self.search_algorithm.find_path(user_email, current_emotion, target_emotion, max_depth)
        
        return path_result
    
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
    
    def get_available_emotions(self):
        """
        Get available emotions.
        
        Returns:
            list: Available emotions
        """
        return self.positive_emotions + self.negative_emotions + self.neutral_emotions
    
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
