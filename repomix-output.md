This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

## Additional Info

# Directory Structure
```
backend/
  models/
    emotion_analyzer.py
    emotional_graph_bigdata.py
    emotional_graph.py
    goal_tracker.py
    memory_manager.py
    response_generator.py
    search_algorithm.py
  services/
    hdfs_service.py
    kafka_service.py
    spark_service.py
  admin_viewer.py
  app.py
  Dockerfile
  intelligent_agent.py
  requirements.txt
  simple_app.py
  simple_requirements.txt
  start_backend.sh
  user_management.py
docs/
  context.md
  contextV2.md
  contextV3.md
  technical_documentation_V2.md
  technical_documentation.md
frontend/
  public/
    index.html
    manifest.json
  src/
    components/
      journal/
        MemoryCard.js
      layout/
        Footer.js
        Header.js
    context/
      AuthContext.js
      ThemeContext.js
    pages/
      EmotionalJourneyGraph.js
      Goals.js
      Home.js
      Journal.js
      Login.js
      Memories.js
      NotFound.js
      Profile.js
      Register.js
    utils/
      axiosConfig.js
    App.js
    index.css
    index.js
    IntelligentAgentApp.js
    SimpleAIDemo.js
  Dockerfile
  package.json
spark/
  jobs/
    dataset_import.py
    emotion_analysis.py
    graph_processing.py
    path_finding.py
.gitignore
.repomixignore
cleanup-all.sh
cleanup-for-ai.sh
copy_spark_jobs.sh
docker-compose.yml
README_BIGDATA.md
README.md
repomix.config.json
run_spark_jobs.sh
start_reflectly.sh
start-agent.sh
start-ai-demo.sh
start-backend.sh
start-frontend.sh
start-intelligent-agent.sh
start-simple.sh
stop_reflectly.sh
test-backend.sh
TROUBLESHOOTING.md
```

# Files

## File: backend/models/emotional_graph_bigdata.py
````python
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
````

## File: backend/models/goal_tracker.py
````python
from datetime import datetime
from bson import ObjectId

class GoalTracker:
    """
    Class for tracking and analyzing user goals.
    """
    
    def __init__(self, db):
        """
        Initialize the goal tracker.
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
    
    def create_goal(self, user_email, goal_data):
        """
        Create a new goal for a user.
        
        Args:
            user_email (str): The user's email
            goal_data (dict): Goal data including title, description, and target date
            
        Returns:
            str: ID of the created goal
        """
        goal = {
            'user_email': user_email,
            'title': goal_data['title'],
            'description': goal_data.get('description', ''),
            'target_date': goal_data.get('target_date'),
            'progress': 0,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'milestones': goal_data.get('milestones', []),
            'completed': False
        }
        
        result = self.db.goals.insert_one(goal)
        return str(result.inserted_id)
    
    def update_progress(self, goal_id, progress):
        """
        Update the progress of a goal.
        
        Args:
            goal_id (str): ID of the goal
            progress (int): New progress value (0-100)
            
        Returns:
            bool: True if the goal was completed with this update, False otherwise
        """
        # Ensure progress is between 0 and 100
        progress = max(0, min(100, progress))
        
        # Check if goal was already completed
        goal = self.db.goals.find_one({'_id': ObjectId(goal_id)})
        was_completed = goal.get('completed', False)
        
        # Update goal progress
        self.db.goals.update_one(
            {'_id': ObjectId(goal_id)},
            {
                '$set': {
                    'progress': progress,
                    'updated_at': datetime.now(),
                    'completed': progress >= 100
                }
            }
        )
        
        # Return True if the goal was just completed
        return progress >= 100 and not was_completed
    
    def get_user_goals(self, user_email, include_completed=True):
        """
        Get all goals for a user.
        
        Args:
            user_email (str): The user's email
            include_completed (bool): Whether to include completed goals
            
        Returns:
            list: List of goals
        """
        query = {'user_email': user_email}
        
        if not include_completed:
            query['completed'] = False
        
        goals = list(self.db.goals.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string
        for goal in goals:
            goal['_id'] = str(goal['_id'])
        
        return goals
    
    def get_goal_by_id(self, goal_id):
        """
        Get a goal by its ID.
        
        Args:
            goal_id (str): ID of the goal
            
        Returns:
            dict: Goal data or None if not found
        """
        goal = self.db.goals.find_one({'_id': ObjectId(goal_id)})
        
        if goal:
            goal['_id'] = str(goal['_id'])
        
        return goal
    
    def add_milestone(self, goal_id, milestone_data):
        """
        Add a milestone to a goal.
        
        Args:
            goal_id (str): ID of the goal
            milestone_data (dict): Milestone data including title and target date
            
        Returns:
            str: ID of the created milestone
        """
        milestone = {
            '_id': ObjectId(),
            'title': milestone_data['title'],
            'target_date': milestone_data.get('target_date'),
            'completed': False,
            'created_at': datetime.now()
        }
        
        self.db.goals.update_one(
            {'_id': ObjectId(goal_id)},
            {
                '$push': {'milestones': milestone},
                '$set': {'updated_at': datetime.now()}
            }
        )
        
        return str(milestone['_id'])
    
    def complete_milestone(self, goal_id, milestone_id):
        """
        Mark a milestone as completed.
        
        Args:
            goal_id (str): ID of the goal
            milestone_id (str): ID of the milestone
            
        Returns:
            bool: True if successful, False otherwise
        """
        result = self.db.goals.update_one(
            {
                '_id': ObjectId(goal_id),
                'milestones._id': ObjectId(milestone_id)
            },
            {
                '$set': {
                    'milestones.$.completed': True,
                    'milestones.$.completed_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    
    def analyze_goal_progress(self, user_email):
        """
        Analyze the progress of all goals for a user.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Analysis results
        """
        goals = self.get_user_goals(user_email)
        
        # Calculate statistics
        total_goals = len(goals)
        completed_goals = sum(1 for goal in goals if goal.get('completed', False))
        active_goals = total_goals - completed_goals
        
        # Calculate average progress for active goals
        if active_goals > 0:
            active_goal_progress = [goal['progress'] for goal in goals if not goal.get('completed', False)]
            avg_progress = sum(active_goal_progress) / len(active_goal_progress)
        else:
            avg_progress = 0
        
        # Get goals due soon (within 7 days)
        now = datetime.now()
        due_soon = []
        for goal in goals:
            if goal.get('target_date') and not goal.get('completed', False):
                target_date = goal['target_date']
                if isinstance(target_date, str):
                    target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                
                days_remaining = (target_date - now).days
                if 0 <= days_remaining <= 7:
                    due_soon.append({
                        'id': goal['_id'],
                        'title': goal['title'],
                        'days_remaining': days_remaining,
                        'progress': goal['progress']
                    })
        
        return {
            'total_goals': total_goals,
            'completed_goals': completed_goals,
            'active_goals': active_goals,
            'completion_rate': completed_goals / total_goals if total_goals > 0 else 0,
            'average_progress': avg_progress,
            'goals_due_soon': due_soon
        }
````

## File: backend/models/search_algorithm.py
````python
"""
Search Algorithm for Reflectly
Implements A* search algorithm for finding optimal emotional paths
"""
import heapq
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AStarSearch:
    def __init__(self, emotional_graph):
        """
        Initialize A* search algorithm
        
        Args:
            emotional_graph: Reference to the EmotionalGraph instance
        """
        self.emotional_graph = emotional_graph
        
    def heuristic(self, current_emotion, target_emotion, user_email=None):
        """
        Heuristic function for A* search
        Estimates the cost to reach the target emotion from the current emotion
        
        Args:
            current_emotion (str): Current emotion
            target_emotion (str): Target emotion
            user_email (str): User email for personalized heuristics
            
        Returns:
            float: Estimated cost
        """
        # Define base costs between emotion categories
        # Lower cost means emotions are closer/easier to transition between
        base_costs = {
            ('joy', 'joy'): 0.1,
            ('joy', 'neutral'): 0.5,
            ('joy', 'sadness'): 1.5,
            ('joy', 'anger'): 1.8,
            ('joy', 'fear'): 1.7,
            ('joy', 'disgust'): 1.6,
            
            ('neutral', 'joy'): 0.7,
            ('neutral', 'neutral'): 0.1,
            ('neutral', 'sadness'): 0.9,
            ('neutral', 'anger'): 1.2,
            ('neutral', 'fear'): 1.1,
            ('neutral', 'disgust'): 1.0,
            
            ('sadness', 'joy'): 2.0,
            ('sadness', 'neutral'): 1.0,
            ('sadness', 'sadness'): 0.1,
            ('sadness', 'anger'): 1.3,
            ('sadness', 'fear'): 1.2,
            ('sadness', 'disgust'): 1.1,
            
            ('anger', 'joy'): 2.2,
            ('anger', 'neutral'): 1.3,
            ('anger', 'sadness'): 1.2,
            ('anger', 'anger'): 0.1,
            ('anger', 'fear'): 0.9,
            ('anger', 'disgust'): 0.8,
            
            ('fear', 'joy'): 2.1,
            ('fear', 'neutral'): 1.2,
            ('fear', 'sadness'): 1.1,
            ('fear', 'anger'): 1.0,
            ('fear', 'fear'): 0.1,
            ('fear', 'disgust'): 0.9,
            
            ('disgust', 'joy'): 2.0,
            ('fear', 'neutral'): 1.1,
            ('disgust', 'sadness'): 1.0,
            ('disgust', 'anger'): 0.9,
            ('disgust', 'fear'): 0.8,
            ('disgust', 'disgust'): 0.1,
        }
        
        # Get the base cost
        emotion_pair = (current_emotion, target_emotion)
        base_cost = base_costs.get(emotion_pair, 1.5)  # Default cost if pair not found
        
        # If user_email is provided, adjust cost based on user's historical transitions
        if user_email:
            # Get user's successful transitions
            successful_transitions = self.emotional_graph.get_successful_transitions(user_email)
            
            # Check if this transition has been successful for the user before
            transition_key = f"{current_emotion}_{target_emotion}"
            if transition_key in successful_transitions:
                # Reduce cost based on success rate
                success_rate = successful_transitions[transition_key].get('success_rate', 0.5)
                adjusted_cost = base_cost * (1 - (success_rate * 0.5))  # Reduce cost by up to 50% based on success rate
                return max(0.1, adjusted_cost)  # Ensure cost is at least 0.1
        
        return base_cost
        
    def find_path(self, user_email, current_emotion, target_emotion, max_depth=10):
        """
        Find the optimal path from current_emotion to target_emotion using A* search
        
        Args:
            user_email (str): User email
            current_emotion (str): Starting emotion
            target_emotion (str): Target emotion
            max_depth (int): Maximum path depth
            
        Returns:
            dict: Optimal path information
        """
        logger.info(f"Finding optimal path for user {user_email} from {current_emotion} to {target_emotion}")
        
        # Check if current and target emotions are the same
        if current_emotion == target_emotion:
            return {
                "current_emotion": current_emotion,
                "target_emotion": target_emotion,
                "path": [current_emotion],
                "actions": [],
                "total_cost": 0,
                "estimated_success_rate": 1.0
            }
            
        # Get available emotions from the emotional graph
        available_emotions = self.emotional_graph.get_available_emotions()
        if not available_emotions:
            available_emotions = ["joy", "sadness", "anger", "fear", "disgust", "neutral"]
            
        # Check if current and target emotions are valid
        if current_emotion not in available_emotions:
            logger.warning(f"Current emotion {current_emotion} not in available emotions, defaulting to neutral")
            current_emotion = "neutral"
            
        if target_emotion not in available_emotions:
            logger.warning(f"Target emotion {target_emotion} not in available emotions, defaulting to joy")
            target_emotion = "joy"
            
        # Initialize data structures for A* search
        open_set = []  # Priority queue of nodes to explore
        closed_set = set()  # Set of explored nodes
        
        # For each node, g_score[node] is the cost of the cheapest path from start to node
        g_score = defaultdict(lambda: float('inf'))
        g_score[current_emotion] = 0
        
        # For each node, f_score[node] = g_score[node] + heuristic(node, goal)
        f_score = defaultdict(lambda: float('inf'))
        f_score[current_emotion] = self.heuristic(current_emotion, target_emotion, user_email)
        
        # For each node, came_from[node] is the node immediately preceding it on the cheapest path
        came_from = {}
        
        # For each node, actions[node] is the action to take to get from came_from[node] to node
        actions = {}
        
        # Add start node to open set
        heapq.heappush(open_set, (f_score[current_emotion], current_emotion, 0))  # (f_score, node, depth)
        
        while open_set:
            # Get node with lowest f_score
            _, current, depth = heapq.heappop(open_set)
            
            # Check if we've reached the target
            if current == target_emotion:
                # Reconstruct path
                path = [current]
                path_actions = []
                node = current
                
                while node in came_from:
                    prev_node = came_from[node]
                    path.append(prev_node)
                    
                    # Add action to path_actions
                    if node in actions and prev_node in actions[node]:
                        action_info = actions[node][prev_node]
                        path_actions.append({
                            "from": prev_node,
                            "to": node,
                            "action": action_info["action"],
                            "success_rate": action_info["success_rate"]
                        })
                        
                    node = prev_node
                    
                # Reverse path and actions
                path = path[::-1]
                path_actions = path_actions[::-1]
                
                # Calculate estimated success rate
                if path_actions:
                    success_rates = [action["success_rate"] for action in path_actions]
                    estimated_success_rate = 1.0
                    for rate in success_rates:
                        estimated_success_rate *= rate
                else:
                    estimated_success_rate = 0.8  # Default if no actions
                    
                return {
                    "current_emotion": current_emotion,
                    "target_emotion": target_emotion,
                    "path": path,
                    "actions": path_actions,
                    "total_cost": g_score[current],
                    "estimated_success_rate": estimated_success_rate
                }
                
            # Add current node to closed set
            closed_set.add(current)
            
            # Check if we've reached maximum depth
            if depth >= max_depth:
                continue
                
            # Get neighbors (possible transitions)
            neighbors = self.get_neighbors(user_email, current)
            
            for neighbor, transition_info in neighbors.items():
                # Skip if neighbor is in closed set
                if neighbor in closed_set:
                    continue
                    
                # Calculate tentative g_score
                tentative_g_score = g_score[current] + transition_info["cost"]
                
                # Check if this path is better than any previous path
                if tentative_g_score < g_score[neighbor]:
                    # Update path
                    came_from[neighbor] = current
                    
                    # Update actions
                    if neighbor not in actions:
                        actions[neighbor] = {}
                    actions[neighbor][current] = {
                        "action": transition_info["action"],
                        "success_rate": transition_info["success_rate"]
                    }
                    
                    # Update scores
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, target_emotion, user_email)
                    
                    # Add to open set if not already there
                    for i, (_, node, _) in enumerate(open_set):
                        if node == neighbor:
                            open_set[i] = (f_score[neighbor], neighbor, depth + 1)
                            heapq.heapify(open_set)
                            break
                    else:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor, depth + 1))
                        
        # If we get here, no path was found
        logger.warning(f"No path found from {current_emotion} to {target_emotion}")
        
        # Return a default path through neutral
        if current_emotion != "neutral" and target_emotion != "neutral":
            # Try to go through neutral
            return {
                "current_emotion": current_emotion,
                "target_emotion": target_emotion,
                "path": [current_emotion, "neutral", target_emotion],
                "actions": [
                    {
                        "from": current_emotion,
                        "to": "neutral",
                        "action": "Practice mindfulness",
                        "success_rate": 0.7
                    },
                    {
                        "from": "neutral",
                        "to": target_emotion,
                        "action": self.get_default_action("neutral", target_emotion),
                        "success_rate": 0.6
                    }
                ],
                "total_cost": 3.0,
                "estimated_success_rate": 0.42  # 0.7 * 0.6
            }
        else:
            # Direct path
            return {
                "current_emotion": current_emotion,
                "target_emotion": target_emotion,
                "path": [current_emotion, target_emotion],
                "actions": [
                    {
                        "from": current_emotion,
                        "to": target_emotion,
                        "action": self.get_default_action(current_emotion, target_emotion),
                        "success_rate": 0.5
                    }
                ],
                "total_cost": 2.0,
                "estimated_success_rate": 0.5
            }
            
    def get_neighbors(self, user_email, emotion):
        """
        Get possible transitions from the current emotion
        
        Args:
            user_email (str): User email
            emotion (str): Current emotion
            
        Returns:
            dict: Dictionary of neighbors with transition information
        """
        # Get user's historical transitions
        user_transitions = self.emotional_graph.get_user_transitions(user_email)
        
        # Get available emotions
        available_emotions = self.emotional_graph.get_available_emotions()
        if not available_emotions:
            available_emotions = ["joy", "sadness", "anger", "fear", "disgust", "neutral"]
            
        # Initialize neighbors
        neighbors = {}
        
        # Add transitions based on user history
        for transition in user_transitions:
            if transition["from_emotion"] == emotion:
                to_emotion = transition["to_emotion"]
                
                # Skip self-transitions
                if to_emotion == emotion:
                    continue
                    
                # Get actions and success rates
                actions = []
                success_rates = []
                
                for action_info in transition.get("actions", []):
                    actions.append(action_info["description"])
                    success_rates.append(action_info["success_rate"])
                    
                # Calculate average success rate
                avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.5
                
                # Get most successful action
                if actions and success_rates:
                    best_action_index = success_rates.index(max(success_rates))
                    best_action = actions[best_action_index]
                else:
                    best_action = self.get_default_action(emotion, to_emotion)
                    
                # Calculate cost (inverse of success rate)
                cost = 1.0 / max(0.1, avg_success_rate)
                
                # Add to neighbors
                neighbors[to_emotion] = {
                    "action": best_action,
                    "success_rate": avg_success_rate,
                    "cost": cost
                }
                
        # If no transitions found in user history, add default transitions
        if not neighbors:
            for to_emotion in available_emotions:
                # Skip self-transitions
                if to_emotion == emotion:
                    continue
                    
                # Add default transition
                action = self.get_default_action(emotion, to_emotion)
                success_rate = self.get_default_success_rate(emotion, to_emotion)
                cost = 1.0 / max(0.1, success_rate)
                
                neighbors[to_emotion] = {
                    "action": action,
                    "success_rate": success_rate,
                    "cost": cost
                }
                
        return neighbors
        
    def get_default_action(self, from_emotion, to_emotion):
        """
        Get default action for a transition
        
        Args:
            from_emotion (str): Source emotion
            to_emotion (str): Target emotion
            
        Returns:
            str: Default action
        """
        # Define default actions for transitions
        default_actions = {
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
        }
        
        # Get default action
        emotion_pair = (from_emotion, to_emotion)
        default_action = default_actions.get(emotion_pair)
        
        # If no default action found, use generic action
        if not default_action:
            if to_emotion == "joy":
                default_action = "Focus on positive aspects of your life"
            elif to_emotion == "neutral":
                default_action = "Practice mindfulness and stay present"
            elif to_emotion == "sadness":
                default_action = "Allow yourself to process emotions"
            elif to_emotion == "anger":
                default_action = "Express feelings constructively"
            elif to_emotion == "fear":
                default_action = "Identify and address specific concerns"
            elif to_emotion == "disgust":
                default_action = "Examine your values and boundaries"
            else:
                default_action = "Reflect on your feelings"
                
        return default_action
        
    def get_default_success_rate(self, from_emotion, to_emotion):
        """
        Get default success rate for a transition
        
        Args:
            from_emotion (str): Source emotion
            to_emotion (str): Target emotion
            
        Returns:
            float: Default success rate
        """
        # Define default success rates for transitions
        # Higher values indicate easier transitions
        default_success_rates = {
            ('sadness', 'joy'): 0.4,
            ('sadness', 'neutral'): 0.6,
            ('sadness', 'anger'): 0.5,
            ('sadness', 'fear'): 0.5,
            ('sadness', 'disgust'): 0.4,
            
            ('anger', 'joy'): 0.3,
            ('anger', 'neutral'): 0.5,
            ('anger', 'sadness'): 0.5,
            ('anger', 'fear'): 0.6,
            ('anger', 'disgust'): 0.6,
            
            ('fear', 'joy'): 0.3,
            ('fear', 'neutral'): 0.5,
            ('fear', 'sadness'): 0.6,
            ('fear', 'anger'): 0.6,
            ('fear', 'disgust'): 0.5,
            
            ('disgust', 'joy'): 0.3,
            ('disgust', 'neutral'): 0.5,
            ('disgust', 'sadness'): 0.6,
            ('disgust', 'anger'): 0.7,
            ('disgust', 'fear'): 0.6,
            
            ('neutral', 'joy'): 0.7,
            ('neutral', 'sadness'): 0.6,
            ('neutral', 'anger'): 0.5,
            ('neutral', 'fear'): 0.5,
            ('neutral', 'disgust'): 0.5,
            
            ('joy', 'neutral'): 0.8,
            ('joy', 'sadness'): 0.4,
            ('joy', 'anger'): 0.3,
            ('joy', 'fear'): 0.3,
            ('joy', 'disgust'): 0.3,
        }
        
        # Get default success rate
        emotion_pair = (from_emotion, to_emotion)
        default_success_rate = default_success_rates.get(emotion_pair, 0.5)  # Default to 0.5 if not found
        
        return default_success_rate
````

## File: backend/services/hdfs_service.py
````python
"""
HDFS Service for Reflectly
Handles reading from and writing to HDFS
"""
import os
import tempfile
import logging
import subprocess
import json
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HDFSService:
    def __init__(self, namenode="namenode:9000", hdfs_bin="hdfs"):
        """
        Initialize HDFS configuration
        
        Args:
            namenode (str): HDFS namenode host:port
            hdfs_bin (str): Path to HDFS binary
        """
        self.namenode = namenode
        self.hdfs_bin = hdfs_bin
        self.hdfs_url = f"hdfs://{namenode}"
        self._check_hdfs_connection()
        
    def _check_hdfs_connection(self):
        """Check if HDFS is reachable"""
        try:
            result = self._run_hdfs_command(["dfs", "-ls", "/"])
            if result["exit_code"] == 0:
                logger.info(f"Successfully connected to HDFS at {self.hdfs_url}")
                return True
            else:
                logger.warning(f"HDFS at {self.hdfs_url} returned error: {result['stderr']}")
                return False
        except Exception as e:
            logger.warning(f"Failed to connect to HDFS at {self.hdfs_url}: {e}")
            return False
            
    def _run_hdfs_command(self, args):
        """
        Run an HDFS command
        
        Args:
            args (list): Command arguments
            
        Returns:
            dict: Command result with stdout, stderr, and exit_code
        """
        cmd = [self.hdfs_bin] + args
        logger.debug(f"Running HDFS command: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            result = {
                "stdout": stdout.strip(),
                "stderr": stderr.strip(),
                "exit_code": exit_code
            }
            
            if exit_code != 0:
                logger.error(f"HDFS command failed with exit code {exit_code}: {stderr.strip()}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to run HDFS command: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1
            }
            
    def read_file(self, hdfs_path):
        """
        Read a file from HDFS
        
        Args:
            hdfs_path (str): HDFS path to the file
            
        Returns:
            str: File content if successful, None otherwise
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Reading file from HDFS: {hdfs_path}")
        
        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Run HDFS command to get the file
            result = self._run_hdfs_command(["dfs", "-get", path, temp_path])
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to read file from HDFS: {result['stderr']}")
                return None
                
            # Read the content from the temporary file
            with open(temp_path, 'r') as f:
                content = f.read()
                
            return content
        except Exception as e:
            logger.error(f"Failed to read file from HDFS: {e}")
            return None
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def write_file(self, content, hdfs_path):
        """
        Write content to a file in HDFS
        
        Args:
            content (str): Content to write
            hdfs_path (str): HDFS path to write to
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Writing file to HDFS: {hdfs_path}")
        
        # Create a temporary file to store the content
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
            
        try:
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(path)
            if parent_dir:
                mkdir_result = self._run_hdfs_command(["dfs", "-mkdir", "-p", parent_dir])
                if mkdir_result["exit_code"] != 0:
                    logger.error(f"Failed to create parent directory in HDFS: {mkdir_result['stderr']}")
                    return False
                    
            # Run HDFS command to put the file
            result = self._run_hdfs_command(["dfs", "-put", "-f", temp_path, path])
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to write file to HDFS: {result['stderr']}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed to write file to HDFS: {e}")
            return False
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def write_local_file(self, local_path, hdfs_path):
        """
        Write a local file to HDFS
        
        Args:
            local_path (str): Path to local file
            hdfs_path (str): HDFS path to write to
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Writing local file {local_path} to HDFS: {hdfs_path}")
        
        try:
            # Check if local file exists
            if not os.path.exists(local_path):
                logger.error(f"Local file {local_path} not found")
                return False
                
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(path)
            if parent_dir:
                mkdir_result = self._run_hdfs_command(["dfs", "-mkdir", "-p", parent_dir])
                if mkdir_result["exit_code"] != 0:
                    logger.error(f"Failed to create parent directory in HDFS: {mkdir_result['stderr']}")
                    return False
                    
            # Run HDFS command to put the file
            result = self._run_hdfs_command(["dfs", "-put", "-f", local_path, path])
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to write local file to HDFS: {result['stderr']}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed to write local file to HDFS: {e}")
            return False
            
    def list_directory(self, hdfs_path):
        """
        List files in an HDFS directory
        
        Args:
            hdfs_path (str): HDFS path to list
            
        Returns:
            list: List of file information dictionaries
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Listing directory in HDFS: {hdfs_path}")
        
        try:
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Run HDFS command to list the directory
            result = self._run_hdfs_command(["dfs", "-ls", "-R", path])
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to list directory in HDFS: {result['stderr']}")
                return []
                
            # Parse the output
            files = []
            for line in result["stdout"].split("\n"):
                if not line or line.startswith("Found"):
                    continue
                    
                parts = line.split()
                if len(parts) < 8:
                    continue
                    
                file_info = {
                    "permissions": parts[0],
                    "replication": parts[1],
                    "owner": parts[2],
                    "group": parts[3],
                    "size": parts[4],
                    "modified_date": parts[5],
                    "modified_time": parts[6],
                    "path": parts[7]
                }
                
                files.append(file_info)
                
            return files
        except Exception as e:
            logger.error(f"Failed to list directory in HDFS: {e}")
            return []
            
    def delete_file(self, hdfs_path, recursive=False):
        """
        Delete a file or directory from HDFS
        
        Args:
            hdfs_path (str): HDFS path to delete
            recursive (bool): Whether to delete recursively
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure path is absolute
        if not hdfs_path.startswith("hdfs://") and not hdfs_path.startswith("/"):
            hdfs_path = f"/{hdfs_path}"
            
        # If path doesn't have hdfs:// prefix, add it
        if not hdfs_path.startswith("hdfs://"):
            hdfs_path = f"{self.hdfs_url}{hdfs_path}"
            
        logger.info(f"Deleting {'recursively ' if recursive else ''}from HDFS: {hdfs_path}")
        
        try:
            # Parse the HDFS URL to get the path
            parsed_url = urlparse(hdfs_path)
            path = parsed_url.path
            
            # Run HDFS command to delete the file or directory
            cmd = ["dfs", "-rm"]
            if recursive:
                cmd.append("-r")
            cmd.append(path)
            
            result = self._run_hdfs_command(cmd)
            
            if result["exit_code"] != 0:
                logger.error(f"Failed to delete from HDFS: {result['stderr']}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed to delete from HDFS: {e}")
            return False
````

## File: backend/services/kafka_service.py
````python
"""
Kafka Service for Reflectly
Handles publishing and consuming messages from Kafka topics
"""
import json
import threading
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaService:
    def __init__(self, bootstrap_servers="kafka:9092"):
        """
        Initialize Kafka producer and consumer configurations
        
        Args:
            bootstrap_servers (str): Kafka bootstrap servers
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumers = {}
        self.consumer_threads = {}
        
        # Initialize producer
        self._init_producer()
        
    def _init_producer(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            logger.info(f"Kafka producer initialized with bootstrap servers: {self.bootstrap_servers}")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None
            
    def publish_message(self, topic, key, value):
        """
        Publish a message to a Kafka topic
        
        Args:
            topic (str): Kafka topic
            key (str): Message key
            value (dict): Message value
            
        Returns:
            bool: True if message was published successfully, False otherwise
        """
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
            
        try:
            future = self.producer.send(topic, key=key, value=value)
            self.producer.flush()
            record_metadata = future.get(timeout=10)
            logger.info(f"Message published to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message to topic {topic}: {e}")
            return False
            
    def consume_messages(self, topic, callback, group_id=None):
        """
        Consume messages from a Kafka topic and process them using the provided callback
        
        Args:
            topic (str): Kafka topic
            callback (function): Callback function to process messages
            group_id (str): Consumer group ID
            
        Returns:
            bool: True if consumer was started successfully, False otherwise
        """
        if topic in self.consumers:
            logger.warning(f"Consumer for topic {topic} already exists")
            return False
            
        try:
            # Create consumer
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=group_id or f"reflectly-{topic}-consumer",
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            
            # Store consumer
            self.consumers[topic] = consumer
            
            # Start consumer thread
            thread = threading.Thread(target=self._consume_loop, args=(topic, callback))
            thread.daemon = True
            thread.start()
            
            # Store thread
            self.consumer_threads[topic] = thread
            
            logger.info(f"Started consumer for topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to start consumer for topic {topic}: {e}")
            return False
            
    def _consume_loop(self, topic, callback):
        """
        Consume messages in a loop
        
        Args:
            topic (str): Kafka topic
            callback (function): Callback function to process messages
        """
        consumer = self.consumers.get(topic)
        if not consumer:
            logger.error(f"Consumer for topic {topic} not found")
            return
            
        logger.info(f"Starting consume loop for topic {topic}")
        try:
            for message in consumer:
                try:
                    logger.info(f"Received message from topic {topic}: {message.value}")
                    callback(message.value)
                except Exception as e:
                    logger.error(f"Error processing message from topic {topic}: {e}")
        except Exception as e:
            logger.error(f"Error in consume loop for topic {topic}: {e}")
        finally:
            logger.info(f"Consume loop for topic {topic} ended")
            
    def stop_consumer(self, topic):
        """
        Stop a consumer for a topic
        
        Args:
            topic (str): Kafka topic
            
        Returns:
            bool: True if consumer was stopped successfully, False otherwise
        """
        if topic not in self.consumers:
            logger.warning(f"Consumer for topic {topic} not found")
            return False
            
        try:
            consumer = self.consumers.pop(topic)
            consumer.close()
            logger.info(f"Stopped consumer for topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop consumer for topic {topic}: {e}")
            return False
            
    def stop_all_consumers(self):
        """
        Stop all consumers
        
        Returns:
            bool: True if all consumers were stopped successfully, False otherwise
        """
        success = True
        for topic in list(self.consumers.keys()):
            if not self.stop_consumer(topic):
                success = False
        return success
````

## File: backend/services/spark_service.py
````python
"""
Spark Service for Reflectly
Handles submitting and managing Spark jobs
"""
import os
import uuid
import subprocess
import logging
import json
import time
from urllib.parse import urlparse
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkService:
    def __init__(self, spark_master="spark://spark-master:7077", spark_submit_path="spark-submit"):
        """
        Initialize Spark configuration
        
        Args:
            spark_master (str): Spark master URL
            spark_submit_path (str): Path to spark-submit command
        """
        self.spark_master = spark_master
        self.spark_submit_path = spark_submit_path
        self.jobs = {}
        self._check_spark_connection()
        
    def _check_spark_connection(self):
        """Check if Spark master is reachable"""
        try:
            # Parse the Spark master URL to get host and port
            parsed_url = urlparse(self.spark_master)
            host = parsed_url.netloc.split(':')[0]
            port = parsed_url.netloc.split(':')[1]
            
            # Try to connect to Spark master UI
            url = f"http://{host}:8080/json/"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"Successfully connected to Spark master at {self.spark_master}")
                return True
            else:
                logger.warning(f"Spark master at {self.spark_master} returned status code {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"Failed to connect to Spark master at {self.spark_master}: {e}")
            return False
            
    def submit_job(self, job_path, job_args=None, job_name=None, executor_memory="1g", executor_cores=1):
        """
        Submit a PySpark job to the Spark cluster
        
        Args:
            job_path (str): Path to the PySpark job script
            job_args (list): Arguments to pass to the job
            job_name (str): Name of the job
            executor_memory (str): Memory per executor
            executor_cores (int): Number of cores per executor
            
        Returns:
            str: Job ID if job was submitted successfully, None otherwise
        """
        if not os.path.exists(job_path):
            logger.error(f"Job script {job_path} not found")
            return None
            
        # Generate job ID and name
        job_id = str(uuid.uuid4())
        if not job_name:
            job_name = f"reflectly-{os.path.basename(job_path)}-{job_id[:8]}"
            
        # Build command
        cmd = [
            self.spark_submit_path,
            "--master", self.spark_master,
            "--name", job_name,
            "--executor-memory", executor_memory,
            "--executor-cores", str(executor_cores),
            job_path
        ]
        
        # Add job arguments if provided
        if job_args:
            cmd.extend(job_args)
            
        logger.info(f"Submitting Spark job: {' '.join(cmd)}")
        
        try:
            # Start job process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Store job information
            self.jobs[job_id] = {
                "id": job_id,
                "name": job_name,
                "path": job_path,
                "args": job_args,
                "process": process,
                "status": "running",
                "start_time": time.time(),
                "end_time": None,
                "exit_code": None,
                "stdout": [],
                "stderr": []
            }
            
            # Start threads to capture stdout and stderr
            self._start_output_capture(job_id)
            
            logger.info(f"Submitted Spark job with ID {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"Failed to submit Spark job: {e}")
            return None
            
    def _start_output_capture(self, job_id):
        """
        Start threads to capture stdout and stderr from the job process
        
        Args:
            job_id (str): Job ID
        """
        import threading
        
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job with ID {job_id} not found")
            return
            
        def capture_output(stream, output_list):
            for line in stream:
                output_list.append(line.strip())
                
        # Start stdout thread
        stdout_thread = threading.Thread(
            target=capture_output,
            args=(job["process"].stdout, job["stdout"])
        )
        stdout_thread.daemon = True
        stdout_thread.start()
        
        # Start stderr thread
        stderr_thread = threading.Thread(
            target=capture_output,
            args=(job["process"].stderr, job["stderr"])
        )
        stderr_thread.daemon = True
        stderr_thread.start()
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self._monitor_job,
            args=(job_id,)
        )
        monitor_thread.daemon = True
        monitor_thread.start()
            
    def _monitor_job(self, job_id):
        """
        Monitor a job and update its status when it completes
        
        Args:
            job_id (str): Job ID
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job with ID {job_id} not found")
            return
            
        # Wait for process to complete
        exit_code = job["process"].wait()
        
        # Update job status
        job["status"] = "completed" if exit_code == 0 else "failed"
        job["exit_code"] = exit_code
        job["end_time"] = time.time()
        
        logger.info(f"Job {job_id} {job['status']} with exit code {exit_code}")
            
    def get_job_status(self, job_id):
        """
        Get the status of a submitted job
        
        Args:
            job_id (str): Job ID
            
        Returns:
            dict: Job status information
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job with ID {job_id} not found")
            return None
            
        # Create a copy of job info without the process object
        job_info = job.copy()
        job_info.pop("process", None)
        
        return job_info
        
    def get_all_jobs(self):
        """
        Get information about all jobs
        
        Returns:
            list: List of job information dictionaries
        """
        return [
            {k: v for k, v in job.items() if k != "process"}
            for job in self.jobs.values()
        ]
        
    def cancel_job(self, job_id):
        """
        Cancel a running job
        
        Args:
            job_id (str): Job ID
            
        Returns:
            bool: True if job was cancelled successfully, False otherwise
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job with ID {job_id} not found")
            return False
            
        if job["status"] != "running":
            logger.warning(f"Job {job_id} is not running (status: {job['status']})")
            return False
            
        try:
            job["process"].terminate()
            job["status"] = "cancelled"
            job["end_time"] = time.time()
            logger.info(f"Cancelled job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
````

## File: backend/admin_viewer.py
````python
import os
from flask import Flask, jsonify, render_template_string
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection
mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/reflectly')
mongo_client = MongoClient(mongo_uri)
db = mongo_client.reflectly

# HTML template for the admin viewer
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Reflectly MongoDB Viewer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1, h2 {
            color: #333;
        }
        .collection {
            background-color: white;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .document {
            background-color: #f9f9f9;
            border-radius: 3px;
            padding: 10px;
            margin: 10px 0;
            border-left: 3px solid #2196F3;
            overflow-x: auto;
        }
        pre {
            margin: 0;
            white-space: pre-wrap;
        }
        .stats {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>Reflectly MongoDB Viewer</h1>
    
    <div class="stats">
        <p>Database: <strong>{{ db_name }}</strong></p>
        <p>Collections: <strong>{{ collections|length }}</strong></p>
    </div>
    
    {% for collection_name in collections %}
    <div class="collection">
        <h2>{{ collection_name }} ({{ collection_counts[collection_name] }} documents)</h2>
        
        {% for document in collection_data[collection_name] %}
        <div class="document">
            <pre>{{ document }}</pre>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
</body>
</html>
'''

@app.route('/')
def index():
    # Get all collections in the database
    collections = db.list_collection_names()
    
    # Get document counts for each collection
    collection_counts = {}
    for collection in collections:
        collection_counts[collection] = db[collection].count_documents({})
    
    # Get all documents from each collection
    collection_data = {}
    for collection in collections:
        documents = list(db[collection].find())
        collection_data[collection] = [dumps(doc, indent=2) for doc in documents]
    
    # Render the HTML template
    return render_template_string(
        HTML_TEMPLATE, 
        db_name='reflectly',
        collections=collections,
        collection_counts=collection_counts,
        collection_data=collection_data
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
````

## File: backend/intelligent_agent.py
````python
"""
Intelligent Agent with Memory Map and A* Search
Learns from user experiences and suggests actions based on past successful transitions
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import re
import heapq
from collections import defaultdict
import uuid

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# In-memory storage for the evolving memory map
memory_map = {
    "emotional_states": {},  # emotion -> list of experiences
    "transitions": {},       # (from_emotion, to_emotion) -> list of successful actions
    "user_experiences": [],  # chronological list of all experiences
    "graph_connections": defaultdict(list)  # emotion -> list of connected emotions
}

class EmotionAnalyzer:
    """Analyzes text to detect emotions"""
    
    def __init__(self):
        self.emotion_keywords = {
            'happy': ['happy', 'joyful', 'excited', 'glad', 'cheerful', 'delighted', 'elated', 'thrilled', 'content', 'pleased', 'amazing', 'wonderful', 'fantastic', 'great', 'awesome', 'love', 'perfect'],
            'sad': ['sad', 'depressed', 'down', 'upset', 'miserable', 'gloomy', 'disappointed', 'heartbroken', 'crying', 'tears', 'lonely', 'hurt', 'devastated'],
            'anxious': ['anxious', 'worried', 'nervous', 'stressed', 'overwhelmed', 'panic', 'fear', 'scared', 'afraid', 'concerned', 'uneasy', 'tense'],
            'angry': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated', 'rage', 'livid', 'outraged', 'hostile'],
            'confused': ['confused', 'lost', 'uncertain', 'unclear', 'puzzled', 'bewildered', 'perplexed'],
            'tired': ['tired', 'exhausted', 'drained', 'weary', 'fatigued', 'worn out'],
            'neutral': ['okay', 'fine', 'normal', 'average', 'regular']
        }
        
        # Define positive and negative emotions
        self.positive_emotions = ['happy']
        self.negative_emotions = ['sad', 'anxious', 'angry', 'confused', 'tired']
        self.neutral_emotions = ['neutral']
    
    def analyze(self, text):
        """Analyze emotion in text"""
        text_lower = text.lower()
        scores = {}
        
        # Calculate scores for each emotion
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[emotion] = score
        
        # Find primary emotion
        if not any(scores.values()):
            primary_emotion = 'neutral'
            confidence = 0.5
        else:
            primary_emotion = max(scores, key=scores.get)
            total_score = sum(scores.values())
            confidence = scores[primary_emotion] / total_score if total_score > 0 else 0.5
        
        # Determine emotion type
        if primary_emotion in self.positive_emotions:
            emotion_type = 'positive'
        elif primary_emotion in self.negative_emotions:
            emotion_type = 'negative'
        else:
            emotion_type = 'neutral'
        
        return {
            'primary_emotion': primary_emotion,
            'emotion_type': emotion_type,
            'confidence': confidence,
            'all_scores': scores
        }

class IntelligentAgent:
    """Intelligent agent that learns and suggests actions using A* search"""
    
    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        
    def process_input(self, text, user_id="default_user"):
        """Process user input and determine appropriate response"""
        # Analyze emotion
        emotion_analysis = self.emotion_analyzer.analyze(text)
        primary_emotion = emotion_analysis['primary_emotion']
        emotion_type = emotion_analysis['emotion_type']
        
        # Create experience record
        experience = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'text': text,
            'emotion': primary_emotion,
            'emotion_type': emotion_type,
            'confidence': emotion_analysis['confidence'],
            'timestamp': datetime.datetime.now().isoformat(),
            'all_scores': emotion_analysis['all_scores']
        }
        
        # Store experience
        memory_map["user_experiences"].append(experience)
        
        # Add to emotional states
        if primary_emotion not in memory_map["emotional_states"]:
            memory_map["emotional_states"][primary_emotion] = []
        memory_map["emotional_states"][primary_emotion].append(experience)
        
        # Determine response based on emotion type
        if emotion_type == 'positive':
            return self._handle_positive_emotion(experience)
        elif emotion_type == 'negative':
            return self._handle_negative_emotion(experience)
        else:
            return self._handle_neutral_emotion(experience)
    
    def _handle_positive_emotion(self, experience):
        """Handle positive emotions - ask for steps taken"""
        return {
            'type': 'ask_for_steps',
            'message': f"That's wonderful! I can see you're feeling {experience['emotion']}. What steps or actions led to this positive feeling? This will help me learn and suggest similar actions to others in the future.",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': []
        }
    
    def _handle_negative_emotion(self, experience):
        """Handle negative emotions - suggest actions using A* search"""
        suggestions = self._find_suggestions_using_astar(experience['emotion'])
        
        return {
            'type': 'suggest_actions',
            'message': f"I understand you're feeling {experience['emotion']}. Based on past successful experiences, here are some suggestions that might help:",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': suggestions
        }
    
    def _handle_neutral_emotion(self, experience):
        """Handle neutral emotions - provide general guidance"""
        return {
            'type': 'general_guidance',
            'message': f"I see you're feeling {experience['emotion']}. Would you like some suggestions to improve your mood, or would you prefer to share what's on your mind?",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': [
                "Try engaging in a hobby you enjoy",
                "Take a short walk or do light exercise",
                "Connect with a friend or family member",
                "Practice gratitude by listing three good things in your life"
            ]
        }
    
    def _find_suggestions_using_astar(self, current_emotion):
        """Use A* search to find best actions from memory map"""
        # Get all successful transitions from this emotion to positive emotions
        successful_actions = []
        
        # Search for direct transitions to positive emotions
        for transition_key, actions in memory_map["transitions"].items():
            from_emotion, to_emotion = transition_key
            if (from_emotion == current_emotion and 
                to_emotion in self.emotion_analyzer.positive_emotions):
                successful_actions.extend(actions)
        
        # If no direct transitions, use A* to find path through intermediate emotions
        if not successful_actions:
            successful_actions = self._astar_search_for_actions(current_emotion)
        
        # If still no actions, provide default suggestions
        if not successful_actions:
            successful_actions = self._get_default_suggestions(current_emotion)
        
        # Return top 3 most successful actions
        return successful_actions[:3]
    
    def _astar_search_for_actions(self, start_emotion):
        """A* search through emotion graph to find actions leading to positive emotions"""
        target_emotions = self.emotion_analyzer.positive_emotions
        
        # Priority queue: (cost, emotion, path, actions)
        open_set = [(0, start_emotion, [start_emotion], [])]
        closed_set = set()
        
        while open_set:
            cost, current_emotion, path, actions = heapq.heappop(open_set)
            
            if current_emotion in closed_set:
                continue
            
            closed_set.add(current_emotion)
            
            # Check if we reached a target emotion
            if current_emotion in target_emotions:
                return actions
            
            # Explore neighbors
            for next_emotion in memory_map["graph_connections"][current_emotion]:
                if next_emotion not in closed_set:
                    transition_key = (current_emotion, next_emotion)
                    if transition_key in memory_map["transitions"]:
                        transition_actions = memory_map["transitions"][transition_key]
                        new_cost = cost + 1  # Simple cost function
                        new_path = path + [next_emotion]
                        new_actions = actions + transition_actions[:1]  # Take best action
                        
                        heapq.heappush(open_set, (new_cost, next_emotion, new_path, new_actions))
        
        return []  # No path found
    
    def _get_default_suggestions(self, emotion):
        """Get default suggestions if no learned actions exist"""
        defaults = {
            'sad': [
                "Listen to uplifting music",
                "Call a friend or family member",
                "Take a warm bath or shower"
            ],
            'anxious': [
                "Practice deep breathing exercises",
                "Try the 5-4-3-2-1 grounding technique",
                "Go for a short walk"
            ],
            'angry': [
                "Count to 10 slowly",
                "Write down your feelings",
                "Do some physical exercise"
            ],
            'confused': [
                "Break down the problem into smaller parts",
                "Talk to someone you trust",
                "Take some time to reflect"
            ],
            'tired': [
                "Take a short nap if possible",
                "Drink some water",
                "Get some fresh air"
            ]
        }
        return defaults.get(emotion, ["Take a moment to breathe and be kind to yourself"])
    
    def save_successful_steps(self, experience_id, steps):
        """Save steps that led to positive emotion"""
        # Find the experience
        experience = None
        for exp in memory_map["user_experiences"]:
            if exp['id'] == experience_id:
                experience = exp
                break
        
        if not experience:
            return False
        
        # Get previous negative emotion if exists
        prev_emotion = self._get_previous_emotion(experience)
        current_emotion = experience['emotion']
        
        # Create transition record
        if prev_emotion and prev_emotion != current_emotion:
            transition_key = (prev_emotion, current_emotion)
            if transition_key not in memory_map["transitions"]:
                memory_map["transitions"][transition_key] = []
            
            # Add each step as an action
            for step in steps:
                action_record = {
                    'action': step,
                    'success_count': 1,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'experience_id': experience_id
                }
                memory_map["transitions"][transition_key].append(action_record)
            
            # Update graph connections
            memory_map["graph_connections"][prev_emotion].append(current_emotion)
        
        # Also store steps directly with the positive emotion
        experience['successful_steps'] = steps
        
        return True
    
    def _get_previous_emotion(self, current_experience):
        """Find the most recent different emotion before current experience"""
        current_time = datetime.datetime.fromisoformat(current_experience['timestamp'])
        
        for exp in reversed(memory_map["user_experiences"]):
            exp_time = datetime.datetime.fromisoformat(exp['timestamp'])
            if (exp_time < current_time and 
                exp['emotion'] != current_experience['emotion'] and
                exp['user_id'] == current_experience['user_id']):
                return exp['emotion']
        
        return None
    
    def get_memory_map_data(self):
        """Get current memory map for visualization"""
        # Create nodes and edges for visualization
        nodes = []
        edges = []
        
        # Create nodes for each emotion with experience count
        for emotion, experiences in memory_map["emotional_states"].items():
            nodes.append({
                'id': emotion,
                'label': emotion.title(),
                'count': len(experiences),
                'type': 'positive' if emotion in self.emotion_analyzer.positive_emotions else 
                       'negative' if emotion in self.emotion_analyzer.negative_emotions else 'neutral'
            })
        
        # Create edges for transitions
        for (from_emotion, to_emotion), actions in memory_map["transitions"].items():
            edges.append({
                'from': from_emotion,
                'to': to_emotion,
                'actions': len(actions),
                'weight': len(actions)  # Thicker lines for more learned transitions
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_experiences': len(memory_map["user_experiences"]),
            'total_transitions': len(memory_map["transitions"])
        }

# Initialize the intelligent agent
agent = IntelligentAgent()

# API Routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Intelligent Agent with Memory Map",
        "memory_stats": {
            "total_experiences": len(memory_map["user_experiences"]),
            "emotional_states": len(memory_map["emotional_states"]),
            "learned_transitions": len(memory_map["transitions"])
        }
    })

@app.route('/api/process-input', methods=['POST', 'OPTIONS'])
def process_input():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        user_id = data.get('user_id', 'default_user')
        
        if not text.strip():
            return jsonify({"error": "Text input is required"}), 400
        
        # Process input through intelligent agent
        response = agent.process_input(text, user_id)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Failed to process input: {str(e)}"}), 500

@app.route('/api/save-steps', methods=['POST', 'OPTIONS'])
def save_steps():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        experience_id = data.get('experience_id', '')
        steps = data.get('steps', [])
        
        if not experience_id or not steps:
            return jsonify({"error": "Experience ID and steps are required"}), 400
        
        # Save steps through intelligent agent
        success = agent.save_successful_steps(experience_id, steps)
        
        if success:
            return jsonify({
                "message": "Steps saved successfully! I'll remember these for future suggestions.",
                "saved_steps": steps
            })
        else:
            return jsonify({"error": "Failed to save steps"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to save steps: {str(e)}"}), 500

@app.route('/api/memory-map', methods=['GET'])
def get_memory_map():
    try:
        map_data = agent.get_memory_map_data()
        return jsonify(map_data)
    except Exception as e:
        return jsonify({"error": f"Failed to get memory map: {str(e)}"}), 500

@app.route('/api/memory-stats', methods=['GET'])
def get_memory_stats():
    try:
        stats = {
            "total_experiences": len(memory_map["user_experiences"]),
            "emotions_learned": len(memory_map["emotional_states"]),
            "transitions_learned": len(memory_map["transitions"]),
            "recent_experiences": memory_map["user_experiences"][-5:] if memory_map["user_experiences"] else []
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500

@app.route('/api/reset-memory', methods=['POST', 'OPTIONS'])
def reset_memory():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Reset the memory map
        memory_map["emotional_states"].clear()
        memory_map["transitions"].clear()
        memory_map["user_experiences"].clear()
        memory_map["graph_connections"].clear()
        
        return jsonify({"message": "Memory map reset successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to reset memory: {str(e)}"}), 500

if __name__ == '__main__':
    print("🤖 Starting Intelligent Agent with Memory Map")
    print("🧠 Features: Emotion Analysis + A* Search + Learning")
    print("📡 API: http://localhost:5000")
    print("🗺️  Memory Map: Growing with each interaction")
    app.run(host='0.0.0.0', port=5000, debug=True)
````

## File: backend/simple_requirements.txt
````
# Minimal requirements for algorithm development
Flask==2.3.3
Flask-CORS==4.0.0
````

## File: backend/start_backend.sh
````bash
#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install requirements if needed
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Start the Flask application
echo "Starting Flask application..."
export FLASK_APP=app.py
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5002
````

## File: backend/user_management.py
````python
import os
from pymongo import MongoClient
import bcrypt
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/reflectly')
mongo_client = MongoClient(mongo_uri)
db = mongo_client.reflectly

def create_user(email, password, name):
    """
    Create a new user in the database
    """
    # Check if user already exists
    existing_user = db.users.find_one({'email': email})
    if existing_user:
        return {'success': False, 'message': f'User with email {email} already exists'}
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user document
    user = {
        'email': email,
        'password': hashed_password,
        'name': name,
        'created_at': datetime.utcnow()
    }
    
    # Insert into database
    result = db.users.insert_one(user)
    
    if result.inserted_id:
        return {'success': True, 'message': f'User {email} created successfully'}
    else:
        return {'success': False, 'message': 'Failed to create user'}

def verify_user_credentials(email, password):
    """
    Verify user credentials
    """
    # Find user
    user = db.users.find_one({'email': email})
    
    if not user:
        return {'success': False, 'message': f'User with email {email} not found'}
    
    # Check password
    password_match = bcrypt.checkpw(password.encode('utf-8'), user['password'])
    
    if password_match:
        return {'success': True, 'message': 'Credentials verified', 'user': user}
    else:
        return {'success': False, 'message': 'Invalid password'}

def list_users():
    """
    List all users in the database
    """
    users = list(db.users.find({}, {'password': 0}))  # Exclude password field
    return users

def delete_user(email):
    """
    Delete a user from the database
    """
    result = db.users.delete_one({'email': email})
    
    if result.deleted_count > 0:
        return {'success': True, 'message': f'User {email} deleted successfully'}
    else:
        return {'success': False, 'message': f'User with email {email} not found'}

# Add admin routes to app.py to manage users
if __name__ == "__main__":
    # Example usage
    print("User Management Module")
    print("Available functions:")
    print("1. create_user(email, password, name)")
    print("2. verify_user_credentials(email, password)")
    print("3. list_users()")
    print("4. delete_user(email)")
````

## File: docs/context.md
````markdown
## **1. Project Breakdown**

### **App Name:** Reflectly  
### **Platform:** Web  
### **App Summary:**  
Reflectly is a personal journaling app designed to help users engage in meaningful self-reflection through a conversational interface. Users can chat with themselves, documenting their daily experiences, emotions, and goals. The app provides a safe space for users to express their feelings, celebrate achievements, and receive encouragement during tough times. It combines the familiarity of a chat interface (like ChatGPT) with the emotional intelligence of a personal journal, fostering self-awareness and growth.

### **Primary Use Case:**  
- **Core Function:** Personal journaling and self-reflection tool with intelligent emotional support.  
- **Category:** Mental health, productivity, and self-improvement.  

### **Authentication Requirements:**  
- **User Accounts:** Required to save and sync journal entries across devices.  
- **Guest Users:** Allowed for limited trial usage (e.g., 3 entries).  
- **Social Login Options:** Google, Apple, and email/password.  
- **User Roles:** Single role (general user).  

---

## **2. Core Features**

1. **Conversational Journaling Interface:**  
   - Chat-like UI where users can type or speak their thoughts.  
   - AI-powered responses with emotion-aware interactions.  
   - Intelligent agent with state management and action planning.

2. **Emotion Tracking and Support System:**  
   - Dual-path emotional processing (Happy and Support flows).
   - Advanced emotion detection using BERT and RoBERTa.
   - Pattern recognition using Markov chains.
   - Probabilistic reasoning for emotional state analysis.

3. **Goal Setting and Progress Analysis:**  
   - Users can set personal goals (e.g., "Exercise 3 times a week").  
   - Progress charts and milestone celebrations.  
   - A* search algorithms for relevant achievement tracking.
   - Probabilistic reasoning for goal progress prediction.

4. **Memory Management System:**  
   - Multi-tier storage for journal entries and emotions.
   - Intelligent retrieval of past positive experiences.
   - Real-time emotional pattern analysis.
   - Bayesian networks for memory relevance scoring.

---

## **3. User Flow**

1. **Onboarding:**  
   - Welcome screen with app introduction.  
   - Prompt to create an account or log in.  

2. **Home Screen:**  
   - Chat interface with a prompt to start journaling.  
   - Quick access to goals and achievements.  

3. **Journaling Session:**  
   - User types or speaks their thoughts.  
   - Real-time emotion analysis and classification.  
   - AI responds with reflective prompts or encouragement.  

4. **Emotion Processing:**  
   - Happy Path: Celebration flow and positive memory storage.
   - Support Path: Retrieval of relevant positive memories.
   - Intelligent response generation based on emotional context.

5. **Goal Tracking:**  
   - User sets or updates goals.   
   - Pattern recognition for achievement analysis.
   - Probabilistic prediction of goal completion.

6. **Achievement Reminders:**  
   - Browser notifications remind users of past achievements.  
   - Context-aware memory retrieval.
   - Bayesian selection of most impactful memories.

---

## **4. Design and UI/UX**

### **Visual Design:**  
- **Color Palette:** Calming tones (e.g., soft blues, greens, and neutrals).  
- **Typography:** Clean, sans-serif fonts for readability.  
- **Icons:** Minimalistic and intuitive.  

### **User Experience:**  
- **Chat Interface:** Familiar and conversational, mimicking messaging apps.  
- **Emotion Tagging:** Simple emoji-based selection.  
- **Responsive Design:** Optimized for desktop, tablet, and mobile browsers.

---

## **5. Technical Implementation**

### **Frontend:**  
- **Framework:** React.js or Vue.js
- **UI Library:** Material-UI or Bootstrap for pre-built components.
- **State Management:** Redux or Vuex.
- **Real-time Updates:** WebSocket integration for live updates.
- **Containerization:** Docker container for frontend deployment.

### **Backend Core:**  
- **API Layer:** Python/Flask or FastAPI for RESTful/GraphQL services.
- **Service Layer:** Python 3.9 services for business logic.
- **Real-time Updates:** WebSocket implementation.
- **Containerization:** Docker container for API services.

### **Data Infrastructure (Docker-Based):**  
- **Message Broker:** Apache Kafka in Docker
  - Kafka and Zookeeper containers
  - Topics for journal entries, emotions, activities
  - Stream processing for real-time data
- **Processing Engine:** Apache Spark in Docker
  - Spark master and worker containers
  - Batch and stream processing capabilities
- **Storage Systems:** Hadoop Ecosystem in Docker
  - HDFS namenode (master) and datanode containers
  - Distributed file storage for journal data and analytics

### **Database Layer:**  
- **Primary Storage:** MongoDB container
- **Cache Layer:** Redis container for frequent data access
- **Long-term Storage:** HDFS on Docker
- **Metadata:** HBase or direct HDFS storage for MVP

### **AI/ML Components:**  
- **Language Models:**
  - GPT for response generation
  - BERT for sentiment analysis
  - RoBERTa for emotion detection (Hugging Face Transformers)
- **Intelligent Systems:**
  - A* search for memory retrieval
  - Bayesian networks for goal prediction
  - Markov chains for patterns
  - Probabilistic reasoning for emotion analysis
- **ML Environment:** Optimized Python 3.9 environment in Docker

### **Deployment:**  
- **Container Orchestration:** Docker Compose for development
- **Web Hosting:** Containerized web server (Nginx)
- **Backend:** Docker containers for Python services
- **Analytics:** Spark processing inside Docker
- **Infrastructure:** All services running in Docker containers on Mac M1 (development) and cloud platforms (production)

---

## **6. Workflow Links and Setup Instructions**

### **Docker Environment Setup:**  
1. **Docker Installation:**  
   - Install Docker Desktop on development machine.
   - Clone repository with docker-compose.yml file.
   - Run `docker-compose up` to start all services.

2. **Big Data Infrastructure:**  
   - Hadoop services configuration:
     ```yaml
     # Example docker-compose.yml snippet for Hadoop
     namenode:
       image: hadoop-namenode:latest
       ports:
         - "9870:9870"
       volumes:
         - hadoop_namenode:/hadoop/dfs/name
     datanode:
       image: hadoop-datanode:latest
       depends_on:
         - namenode
       volumes:
         - hadoop_datanode:/hadoop/dfs/data
     ```
   
   - Spark services configuration:
     ```yaml
     # Example docker-compose.yml snippet for Spark
     spark-master:
       image: spark-master:latest
       ports:
         - "8080:8080"
         - "7077:7077"
       environment:
         - SPARK_HOME=/spark
         - PATH=$PATH:$SPARK_HOME/bin
     spark-worker:
       image: spark-worker:latest
       depends_on:
         - spark-master
     ```
   
   - Kafka services configuration:
     ```yaml
     # Example docker-compose.yml snippet for Kafka
     zookeeper:
       image: confluentinc/cp-zookeeper:latest
       ports:
         - "2181:2181"
     kafka:
       image: confluentinc/cp-kafka:latest
       depends_on:
         - zookeeper
       ports:
         - "9092:9092"
       environment:
         - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
     ```

3. **Python Environment Setup:**  
   - Build Python 3.9 in namenode container:
     ```bash
     # Inside namenode container
     wget https://www.python.org/ftp/python/3.9.x/Python-3.9.x.tgz
     tar -xf Python-3.9.x.tgz
     cd Python-3.9.x
     ./configure --enable-optimizations
     make -j $(nproc)
     make install
     ln -s /usr/local/bin/python3.9 /usr/local/bin/python
     ```
   - Install Python dependencies:
     ```bash
     python -m pip install flask fastapi pyspark kafka-python transformers torch pandas numpy
     ```

4. **Application Deployment:**  
   - Frontend Docker container:
     ```yaml
     # Example docker-compose.yml snippet for frontend
     frontend:
       build: ./frontend
       ports:
         - "80:80"
       depends_on:
         - backend
     ```
   - Backend Docker container:
     ```yaml
     # Example docker-compose.yml snippet for backend
     backend:
       build: ./backend
       ports:
         - "5000:5000"
       depends_on:
         - mongodb
         - kafka
     ```

5. **Testing and Verification:**  
   - HDFS commands:
     ```bash
     hdfs dfs -ls /
     hdfs dfs -mkdir -p /user/reflectly/data
     ```
   - Kafka topic creation:
     ```bash
     kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 3 --topic journal-entries
     ```
   - Spark job submission:
     ```bash
     spark-submit --master spark://spark-master:7077 /path/to/emotion_analysis.py
     ```

### **Development Workflow:**
1. **Local Development:**
   - Run all services with `docker-compose up -d`
   - Develop frontend code with hot-reloading
   - Use Docker volumes to persist data
   - Access Hadoop UI at http://localhost:9870
   - Access Spark UI at http://localhost:8080

2. **Version Control:**
   - Use Git for version control
   - Separate repositories for frontend, backend, and data processing
   - CI/CD pipelines to build Docker images

3. **Progressive Web App Features:**
   - Service Workers for offline capability
   - Web manifest for home screen installation
   - Responsive design for all device sizes
   - Push notifications through browser API
````

## File: docs/contextV2.md
````markdown
# Reflectly Technical Documentation - Phase One

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Directory Structure](#directory-structure)
5. [Backend Components](#backend-components)
6. [Frontend Components](#frontend-components)
7. [Data Flow](#data-flow)
8. [Key Features Implementation](#key-features-implementation)
9. [Authentication and User Management](#authentication-and-user-management)
10. [Deployment Instructions](#deployment-instructions)
11. [Development Workflow](#development-workflow)
12. [API Documentation](#api-documentation)

## Project Overview

Reflectly is a personal journaling application with a conversational interface designed to help users engage in meaningful self-reflection. The application combines a chat-like interface with intelligent emotional support, memory management, and goal tracking features. The system uses emotional analysis to provide personalized responses and help users navigate from negative emotional states to positive ones.

### Core Functionality
- **Conversational Journaling**: Users interact with the application through a chat interface
- **Emotion Analysis**: The system analyzes user emotions from journal entries
- **Emotional Graph**: Tracks transitions between emotional states and effective interventions
- **Memory Management**: Past positive experiences are stored and retrieved when needed
- **Goal Tracking**: Users can set and track personal goals

## System Architecture

Reflectly follows a modern microservices architecture with containerized components:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    Frontend     │◄────►│    Backend      │◄────►│    Database     │
│    (React.js)   │      │    (Flask)      │      │    (MongoDB)    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                  ▲
                                  │
                                  ▼
                         ┌─────────────────┐
                         │                 │
                         │  Cache Layer    │
                         │    (Redis)      │
                         │                 │
                         └─────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Containerization**: Docker

### Backend
- **Framework**: Flask (Python)
- **API**: RESTful endpoints
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker
- **ML Framework**: Transformers (Hugging Face) for emotion detection

### Database
- **Primary Database**: MongoDB
- **Caching**: Redis
- **Data Persistence**: Docker volumes

### AI/ML Components
- **Emotion Analysis**: BERT-based model from Hugging Face
- **Emotional Graph**: In-memory graph structure with MongoDB persistence
- **Response Generation**: Template-based with contextual awareness
- **Memory Management**: Multi-tier storage with intelligent retrieval

## Directory Structure

```
/Refection/
├── backend/                  # Backend Flask application
│   ├── models/               # Core business logic components
│   │   ├── emotion_analyzer.py  # Enhanced emotion analysis module
│   │   ├── emotional_graph.py   # NEW: Emotional state graph representation
│   │   ├── goal_tracker.py      # Goal tracking functionality
│   │   ├── memory_manager.py    # Memory storage and retrieval
│   │   └── response_generator.py # AI response generation
│   ├── app.py                # Main Flask application
│   ├── admin_viewer.py       # Admin interface for database viewing
│   ├── user_management.py    # User authentication and management
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
├── frontend/                 # React frontend application
│   ├── public/               # Static assets
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable UI components
│   │   ├── context/          # React context providers
│   │   ├── pages/            # Application pages
│   │   │   └── EmotionalJourney.js # NEW: Emotional state visualization
│   │   ├── services/         # API service integrations
│   │   └── utils/            # Utility functions
│   ├── package.json          # NPM dependencies
│   └── Dockerfile            # Frontend container definition
├── docker/                   # Docker configuration files
├── data/                     # NEW: Data directory for datasets
│   └── emotion_datasets/     # NEW: Directory for emotional datasets
├── docker-compose.yml        # Multi-container orchestration
├── docs/                     # Documentation
│   └── context.md            # Project context and specifications
└── README.md                 # Project overview
```

## Backend Components

### Flask Application (app.py)
The main application entry point that defines API routes, initializes components, and handles HTTP requests.

Key endpoints:
- `/api/auth/login`: User authentication
- `/api/auth/register`: User registration
- `/api/journal/entries`: CRUD operations for journal entries
- `/api/emotions/graph`: NEW: Endpoints for emotional graph data
- `/api/goals`: Goal management endpoints
- `/api/admin/*`: Administrative endpoints

### Emotion Analyzer (emotion_analyzer.py)
Enhanced to use a pre-trained BERT model for more accurate emotion detection:
- Detects primary emotion (joy, sadness, anger, fear, disgust, surprise)
- Determines if the emotion is positive or negative
- Calculates confidence scores for each emotion
- Uses Hugging Face Transformers library for inference
- Optionally utilizes a fine-tuned model on IEMOCAP dataset

### Emotional Graph (emotional_graph.py)
NEW component that represents and manages the emotional state transitions:
- Graph structure with emotional states as nodes
- Edges represent transitions between states with weights
- Stores actions that led to emotional state changes
- Simple pathfinding to suggest actions for emotional improvement
- Persistence layer to save graph to MongoDB

### Memory Manager (memory_manager.py)
Manages the storage and retrieval of journal entries and memories:
- Multi-tier storage system (short-term, medium-term, long-term)
- Redis caching for frequently accessed memories
- Intelligent retrieval of relevant memories based on emotional context
- Stores positive memories for future encouragement
- NEW: Associates memories with emotional state transitions

### Response Generator (response_generator.py)
Generates AI responses to user journal entries:
- Template-based responses customized to emotional context
- Incorporates past memories when appropriate
- Provides encouragement during negative emotional states
- Reinforces positive experiences
- NEW: Suggests actions based on emotional graph pathfinding

### Goal Tracker (goal_tracker.py)
Manages user goals and tracks progress:
- Goal creation and update functionality
- Progress tracking and milestone recognition
- Pattern recognition for achievement analysis
- NEW: Relates goals to emotional states

### User Management (user_management.py)
Handles user authentication and account management:
- User registration and login
- Password hashing with bcrypt
- JWT token generation and validation
- User profile management

## Frontend Components

### App Structure
- **App.js**: Main application component with routing
- **index.js**: Entry point that renders the React application

### Pages
- **Login.js**: User authentication interface
- **Register.js**: New user registration
- **Journal.js**: Main journaling interface with chat functionality
- **Goals.js**: Goal setting and tracking interface
- **Profile.js**: User profile management
- **Dashboard.js**: Overview of journal entries and emotions
- **EmotionalJourney.js**: NEW: Visualization of user's emotional journey

### Components
- **journal/MemoryCard.js**: Displays memory cards in the journal chat
- **journal/ChatBubble.js**: Individual chat message bubbles
- **journal/EmotionIndicator.js**: NEW: Visual indication of detected emotions
- **common/Navbar.js**: Application navigation
- **goals/GoalItem.js**: Individual goal display and tracking
- **emotional/StateGraph.js**: NEW: Visual representation of emotional states

### Context Providers
- **AuthContext.js**: Authentication state management
- **JournalContext.js**: Journal entries and chat state
- **EmotionContext.js**: NEW: Emotion tracking and graph state

## Data Flow

### Journal Entry Creation
1. User enters text in the journal interface
2. Frontend sends entry to backend via API
3. Backend processes the entry:
   - Analyzes emotions using the enhanced emotion analyzer
   - Updates the emotional graph with the new state
   - Finds potential paths to better emotional states
   - Generates an AI response using the response generator
   - Stores the entry in MongoDB
   - Caches positive memories in Redis
4. Response is sent back to frontend with:
   - AI-generated text response
   - Memory card data (if applicable)
   - Suggested actions based on emotional graph
5. Frontend displays the response and any memory cards

### Emotional Graph Update Logic
1. When a user submits a journal entry:
   - The system detects the current emotional state
   - Adds it to the emotional graph if new
   - Updates transition weights based on frequency
   - Records actions mentioned in the entry
2. When suggesting responses:
   - The system finds paths from current emotion to positive emotions
   - Suggests actions based on successful past transitions
   - Prioritizes actions with higher success rates

## Key Features Implementation

### Conversational Journaling Interface
The journal interface mimics a chat application with:
- User messages displayed on the right
- AI responses displayed on the left
- Memory cards appearing inline when triggered
- Real-time emotion analysis feedback
- NEW: Suggested actions based on emotional graph

### Emotion Tracking System
- **Enhanced Emotion Detection**: BERT-based model identifies emotions
- **Emotion Storage**: Emotions are stored with journal entries
- **Emotion Trends**: Patterns are analyzed over time
- **NEW: Emotional Graph**: Tracks transitions between emotional states

### Memory Management System
- **Short-term Memory**: Recent entries cached in Redis (7 days)
- **Medium-term Memory**: Active entries in MongoDB (30 days)
- **Long-term Memory**: Historical entries for pattern analysis (365 days)
- **Memory Retrieval**: Intelligent retrieval based on emotional context
- **NEW: Action Association**: Memories linked to successful emotional transitions

### Goal Setting and Tracking
- **Goal Creation**: Users define goals with measurable criteria
- **Progress Tracking**: System tracks progress through user updates
- **Achievement Recognition**: Milestones are celebrated with notifications
- **NEW: Emotional Impact**: Goals are linked to emotional states

## Authentication and User Management

### User Registration
1. User provides email and password
2. Password is hashed using bcrypt
3. User account is created in MongoDB
4. JWT token is generated and returned

### User Authentication
1. User submits login credentials
2. Backend verifies email and password
3. JWT token is generated with user information
4. Token is returned to frontend and stored in local storage

### Admin Functionality
- List all users in the system
- Create new users with specified credentials
- Delete users from the system
- View database structure and contents
- NEW: View emotional graphs and transitions

## Deployment Instructions

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- Node.js and npm for frontend development
- Python for backend development

### Development Environment Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Refection
   ```

2. Download and place emotion datasets in the data directory:
   ```bash
   mkdir -p data/emotion_datasets
   # Place IEMOCAP dataset files here (if available)
   ```

3. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5002
   - MongoDB Viewer: http://localhost:5003

### Manual Backend Setup (Alternative)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask application:
   ```bash
   python app.py
   ```

### Manual Frontend Setup (Alternative)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Development Workflow

### Code Organization
- **Backend**: Modular Python code with clear separation of concerns
- **Frontend**: Component-based React architecture
- **Shared**: Docker configuration for consistent environments

### Version Control
- Use feature branches for new development
- Pull requests for code review
- Semantic versioning for releases

### Testing
- Unit tests for backend components
- Integration tests for API endpoints
- End-to-end tests for critical user flows

## API Documentation

### Authentication Endpoints

#### POST /api/auth/login
Authenticates a user and returns a JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

#### POST /api/auth/register
Registers a new user.

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "New User"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "newuser@example.com",
    "name": "New User"
  }
}
```

### Journal Endpoints

#### POST /api/journal/entries
Creates a new journal entry.

**Request:**
```json
{
  "content": "I'm feeling sad today because I had an argument with a friend."
}
```

**Response:**
```json
{
  "entry": {
    "id": "60c72b2f9b1d8a1234567890",
    "content": "I'm feeling sad today because I had an argument with a friend.",
    "created_at": "2023-06-14T12:30:45Z",
    "emotion": {
      "primary_emotion": "sadness",
      "is_positive": false,
      "emotion_scores": {
        "joy": 0.05,
        "sadness": 0.85,
        "anger": 0.02,
        "fear": 0.03,
        "disgust": 0.01,
        "surprise": 0.04
      }
    }
  },
  "response": {
    "text": "I'm sorry to hear you're feeling sad about the argument. In the past, talking things through has helped you resolve conflicts. Would you like to think about how to approach your friend for a conversation?",
    "memory": {
      "id": "60c72b2f9b1d8a1234567880",
      "content": "I called my friend and apologized for the misunderstanding. I feel much better now.",
      "created_at": "2023-05-20T15:45:30Z"
    },
    "suggested_actions": [
      "Reach out to your friend",
      "Take some time for self-care",
      "Journal about what you learned from the situation"
    ]
  }
}
```

#### GET /api/journal/entries
Retrieves journal entries for the authenticated user.

**Response:**
```json
{
  "entries": [
    {
      "id": "60c72b2f9b1d8a1234567890",
      "content": "I'm feeling sad today because I had an argument with a friend.",
      "created_at": "2023-06-14T12:30:45Z",
      "emotion": {
        "primary_emotion": "sadness",
        "is_positive": false
      }
    },
    {
      "id": "60c72b2f9b1d8a1234567891",
      "content": "I'm feeling happy today because I resolved the issue with my friend.",
      "created_at": "2023-06-15T10:15:30Z",
      "emotion": {
        "primary_emotion": "joy",
        "is_positive": true
      }
    }
  ]
}
```

### NEW: Emotion Graph Endpoints

#### GET /api/emotions/graph
Retrieves the user's emotional state graph.

**Response:**
```json
{
  "nodes": [
    {
      "id": "joy",
      "count": 25,
      "last_experienced": "2023-06-15T10:15:30Z"
    },
    {
      "id": "sadness",
      "count": 15,
      "last_experienced": "2023-06-14T12:30:45Z"
    },
    {
      "id": "anger",
      "count": 8,
      "last_experienced": "2023-06-10T09:20:15Z"
    }
  ],
  "edges": [
    {
      "source": "sadness",
      "target": "joy",
      "weight": 0.7,
      "actions": [
        {
          "description": "Reached out to friend",
          "count": 5
        },
        {
          "description": "Practiced self-care",
          "count": 3
        }
      ]
    },
    {
      "source": "anger",
      "target": "joy",
      "weight": 0.5,
      "actions": [
        {
          "description": "Took a walk",
          "count": 2
        },
        {
          "description": "Practiced deep breathing",
          "count": 4
        }
      ]
    }
  ]
}
```

#### GET /api/emotions/suggestions
Retrieves suggestions for transitioning from current emotional state.

**Request:**
```json
{
  "current_emotion": "sadness"
}
```

**Response:**
```json
{
  "target_emotion": "joy",
  "path": ["sadness", "joy"],
  "suggested_actions": [
    {
      "description": "Reach out to friend",
      "success_rate": 0.85
    },
    {
      "description": "Practice self-care",
      "success_rate": 0.75
    },
    {
      "description": "Listen to uplifting music",
      "success_rate": 0.65
    }
  ]
}
```

### Admin Endpoints

#### GET /api/admin/users
Retrieves all users (requires admin authentication).

**Response:**
```json
{
  "users": [
    {
      "email": "user1@example.com",
      "name": "User One",
      "created_at": "2023-05-01T09:00:00Z"
    },
    {
      "email": "user2@example.com",
      "name": "User Two",
      "created_at": "2023-05-02T10:30:00Z"
    }
  ]
}
```

#### NEW: GET /api/admin/emotions/graphs
Retrieves all user emotional graphs (requires admin authentication).

**Response:**
```json
{
  "graphs": [
    {
      "user_id": "user1@example.com",
      "node_count": 6,
      "edge_count": 12,
      "most_common_emotion": "joy"
    },
    {
      "user_id": "user2@example.com",
      "node_count": 5,
      "edge_count": 8,
      "most_common_emotion": "sadness"
    }
  ]
}
```
````

## File: docs/contextV3.md
````markdown
# Reflectly Technical Documentation - Phase Two

**Version:** 2.0.0  
**Last Updated:** March 14, 2025  
**Author:** Reflectly Development Team

## Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Backend Components](#backend-components)
  - [Emotional Graph](#emotional-graph)
  - [Response Generator](#response-generator)
  - [Journal Entry Processing](#journal-entry-processing)
  - [Big Data Integration](#big-data-integration)
  - [Message Processing Pipeline](#message-processing-pipeline)
- [Frontend Components](#frontend-components)
- [Data Flow](#data-flow)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)

## Project Overview

Reflectly is a personal journaling application with a conversational interface designed to help users engage in meaningful self-reflection. The application combines a chat-like interface with intelligent emotional support and goal tracking features. The system uses emotional analysis to provide personalized responses and help users navigate from negative emotional states to positive ones.

### Core Functionality
- **Conversational Journaling**: Users interact with the application through a chat interface
- **Emotion Analysis**: The system analyzes user emotions from journal entries using distributed processing
- **Emotional Graph**: Tracks transitions between emotional states and suggests personalized interventions based on user history
- **Personalized Responses**: Generates responses tailored to the user's emotional context and history
- **Goal Tracking**: Users can set and track personal goals
- **Big Data Processing**: Processes journal entries using Hadoop, Spark, and Kafka for scalable analysis
- **Advanced Search**: Uses A* search algorithm to find optimal paths between emotional states

## System Architecture

Reflectly now follows a distributed microservices architecture with big data processing capabilities:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    Frontend     │◄────►│    Backend      │◄────►│    Database     │
│    (React.js)   │      │    (Flask)      │      │    (MongoDB)    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                  ▲                        ▲
                                  │                        │
                                  ▼                        │
                         ┌─────────────────┐              │
                         │                 │              │
                         │     Redis       │              │
                         │    (Cache)      │              │
                         │                 │              │
                         └─────────────────┘              │
                                                          │
┌─────────────────┐      ┌─────────────────┐      ┌──────┴──────────┐
│                 │      │                 │      │                 │
│     Kafka       │◄────►│     Spark       │◄────►│     HDFS        │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        ▲
        │
        ▼
┌─────────────────┐
│                 │
│   Zookeeper     │
│                 │
└─────────────────┘
```

- **Frontend**: React.js application providing the user interface
- **Backend**: Flask application handling business logic, emotion analysis, and response generation
- **Database**: MongoDB for persistent storage of user data, journal entries, and emotional states
- **Cache**: Redis for temporary data storage and session management
- **Kafka**: Message broker for handling journal entry streams
- **Spark**: Distributed processing for emotion analysis and graph computations
- **HDFS**: Distributed file system for storing datasets and processed data
- **Zookeeper**: Coordination service for Kafka

## Technology Stack

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Date Handling**: date-fns

### Backend
- **Framework**: Flask (Python)
- **Authentication**: JWT (JSON Web Tokens)
- **Database ORM**: PyMongo
- **Message Processing**: Kafka Python client
- **Emotion Analysis**: Custom implementation with BERT/RoBERTa models
- **Response Generation**: Template-based with personalization logic
- **Graph Processing**: NetworkX for emotional graph implementation
- **Search Algorithms**: A* implementation for finding optimal emotional paths

### Big Data Infrastructure
- **Distributed Storage**: Hadoop HDFS
- **Distributed Processing**: Apache Spark
- **Stream Processing**: Apache Kafka
- **Coordination**: Apache Zookeeper
- **Dataset Processing**: PySpark for processing IEMOCAP and mental health datasets

### Database
- **Primary Database**: MongoDB
- **Caching**: Redis
- **Long-term Storage**: HDFS

### DevOps
- **Containerization**: Docker and Docker Compose
- **Version Control**: Git
- **CI/CD**: GitHub Actions

## Directory Structure

```
/
├── backend/                # Flask backend application
│   ├── models/             # Business logic models
│   │   ├── emotional_graph.py     # Emotional state tracking and transitions
│   │   ├── response_generator.py  # AI response generation
│   │   ├── search_algorithm.py    # NEW: A* search implementation
│   │   └── ...
│   ├── services/           # NEW: External service integrations
│   │   ├── kafka_service.py       # NEW: Kafka integration
│   │   ├── spark_service.py       # NEW: Spark job submission
│   │   └── hdfs_service.py        # NEW: HDFS operations
│   ├── utils/              # Utility functions
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── start_backend.sh    # Script to start the backend server
│
├── spark/                  # NEW: Spark job definitions
│   ├── jobs/               # Spark job implementations
│   │   ├── emotion_analysis.py    # Emotion analysis job
│   │   ├── graph_processing.py    # Emotional graph processing
│   │   └── dataset_import.py      # Dataset import and processing
│   ├── utils/              # Spark utility functions
│   └── submit_job.sh       # Script to submit Spark jobs
│
├── data/                   # NEW: Data directory
│   ├── datasets/           # Raw datasets
│   │   ├── iemocap/        # IEMOCAP dataset
│   │   └── mental_health/  # Mental health conversations dataset
│   └── preprocessing/      # Data preprocessing scripts
│
├── frontend/               # React frontend application
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   │   ├── components/     # Reusable UI components
│   │   │   ├── journal/    # Journal-related components
│   │   │   └── layout/     # Layout components
│   │   ├── context/        # React context providers
│   │   ├── pages/          # Application pages
│   │   │   └── EmotionalJourneyGraph.js # NEW: Emotional path visualization
│   │   ├── utils/          # Utility functions
│   │   ├── App.js          # Main application component
│   │   └── index.js        # Entry point
│   ├── package.json        # NPM dependencies
│   └── README.md           # Frontend documentation
│
├── docker/                 # Docker configuration
│   ├── backend/            # Backend Docker configuration
│   ├── frontend/           # Frontend Docker configuration
│   └── hadoop/             # NEW: Hadoop configuration files
│
├── docker-compose.yml      # Multi-container orchestration
├── docs/                   # Project documentation
│   ├── technical_documentation.md  # Technical documentation
│   └── context.md          # Project context and requirements
└── README.md               # Project overview
```

## Backend Components

### Emotional Graph

The `EmotionalGraph` class has been enhanced to leverage big data processing for more sophisticated analysis:

#### Key Enhancements

- **Distributed Storage**: Emotional graph data is now stored in both MongoDB (for quick access) and HDFS (for long-term storage and analytics)
- **Spark Processing**: Graph computations now use Spark for distributed processing
- **A* Search Integration**: Uses A* search algorithm to find optimal paths between emotional states
- **Dataset Integration**: Incorporates insights from the IEMOCAP and mental health datasets

#### Implementation

The enhanced `EmotionalGraph` class now integrates with Spark and HDFS:

1. **Recording Emotions with Kafka**: The `record_emotion` method now publishes emotion data to Kafka for asynchronous processing.

```python
def record_emotion(self, user_email, emotion_data, entry_id=None):
    # Store the emotional state in MongoDB
    # Publish emotion data to Kafka for processing
    # Return the stored emotion document
```

2. **Finding Optimal Emotional Paths**: The `find_optimal_path` method uses A* search to find the optimal path from the current emotional state to a target positive state.

```python
def find_optimal_path(self, user_email, current_emotion, target_emotion="joy"):
    # Use A* search algorithm to find the optimal path
    # Consider past successful transitions as heuristics
    # Return the optimal path and suggested actions
```

3. **Retrieving Insights from Datasets**: The `get_dataset_insights` method retrieves insights from the processed IEMOCAP and mental health datasets.

```python
def get_dataset_insights(self, emotion):
    # Get insights from processed datasets in HDFS
    # Use Spark to query the datasets efficiently
    # Return relevant insights for the given emotion
```

### Response Generator

The `ResponseGenerator` class has been enhanced to incorporate insights from big data processing:

#### Key Enhancements

- **Dataset-Driven Responses**: Incorporates insights from processed datasets
- **Optimal Path Suggestions**: Suggests actions based on optimal emotional paths
- **Personalized Heuristics**: Uses personalized heuristics for response generation

#### Implementation

The enhanced `ResponseGenerator` class now integrates with the big data processing pipeline:

1. **Generating Responses with Dataset Insights**: The `generate_with_insights` method incorporates insights from processed datasets.

```python
def generate_with_insights(self, text, emotion_data, dataset_insights=None):
    # Generate a response incorporating dataset insights
    # Use a more sophisticated template system
    # Return a response with insights from datasets
```

2. **Generating Responses with Optimal Paths**: The `generate_with_optimal_path` method suggests actions based on the optimal emotional path.

```python
def generate_with_optimal_path(self, text, emotion_data, optimal_path=None):
    # Generate a response suggesting actions from the optimal path
    # Incorporate insights from A* search results
    # Return a response with suggested actions
```

### Journal Entry Processing

The journal entry processing logic has been enhanced to use the big data infrastructure:

#### Key Enhancements

- **Kafka Integration**: Journal entries are published to Kafka for asynchronous processing
- **Spark Processing**: Emotion analysis is performed using Spark jobs
- **HDFS Storage**: Processed journal entries are stored in HDFS for long-term analytics
- **A* Search Integration**: Uses A* search to find optimal emotional paths

#### Implementation

The enhanced journal entry processing logic now integrates with the big data infrastructure:

1. **Asynchronous Processing**: Journal entries are published to Kafka for asynchronous processing.
2. **Distributed Emotion Analysis**: Emotion analysis is performed using Spark jobs.
3. **Optimal Path Finding**: A* search is used to find optimal emotional paths.
4. **Dataset Insight Integration**: Insights from processed datasets are incorporated into responses.

### Big Data Integration

This new component integrates the Flask backend with the big data infrastructure:

#### Key Features

- **Kafka Integration**: Publishes and consumes messages from Kafka topics
- **Spark Job Submission**: Submits Spark jobs for distributed processing
- **HDFS Operations**: Reads from and writes to HDFS
- **Dataset Processing**: Processes and analyzes datasets using Spark

#### Implementation

The big data integration component consists of several services:

1. **Kafka Service**: Manages Kafka producers and consumers.

```python
class KafkaService:
    def __init__(self, bootstrap_servers="kafka:9092"):
        # Initialize Kafka producer and consumer configurations
        
    def publish_message(self, topic, key, value):
        # Publish a message to a Kafka topic
        
    def consume_messages(self, topic, callback):
        # Consume messages from a Kafka topic and process them
```

2. **Spark Service**: Manages Spark job submissions.

```python
class SparkService:
    def __init__(self, spark_master="spark://spark-master:7077"):
        # Initialize Spark configuration
        
    def submit_job(self, job_path, job_args=None):
        # Submit a PySpark job to the Spark cluster
        
    def get_job_status(self, job_id):
        # Get the status of a submitted job
```

3. **HDFS Service**: Manages HDFS operations.

```python
class HDFSService:
    def __init__(self, namenode="namenode:9000"):
        # Initialize HDFS configuration
        
    def read_file(self, hdfs_path):
        # Read a file from HDFS
        
    def write_file(self, local_path, hdfs_path):
        # Write a file to HDFS
        
    def list_directory(self, hdfs_path):
        # List files in an HDFS directory
```

### Message Processing Pipeline

This new component processes messages from Kafka topics:

#### Key Features

- **Journal Entry Processing**: Processes journal entries from the journal-entries topic
- **Emotion Analysis**: Analyzes emotions using PySpark jobs
- **Emotional Graph Updates**: Updates the emotional graph with processed data
- **Response Generation**: Generates responses based on processed data

#### Implementation

The message processing pipeline consists of several Kafka consumers:

1. **Journal Entry Consumer**: Processes journal entries from the journal-entries topic.

```python
def process_journal_entry(message):
    # Extract journal entry data from message
    # Submit a Spark job for emotion analysis
    # Update the emotional graph
    # Generate a response
    # Store the processed data in HDFS and MongoDB
```

2. **Emotion Analysis Consumer**: Processes emotion analysis results from the emotion-analysis topic.

```python
def process_emotion_analysis(message):
    # Extract emotion analysis data from message
    # Update the emotional graph
    # Generate insights based on the analysis
    # Store the processed data in HDFS and MongoDB
```

## Frontend Components

The frontend has been enhanced to visualize the emotional journey and optimal paths:

### Key Enhancements

- **Emotional Journey Graph**: Visualizes the user's emotional journey over time
- **Optimal Path Visualization**: Displays optimal paths between emotional states
- **Action Suggestions**: Displays suggested actions from the A* search results
- **Dataset Insights**: Displays insights from processed datasets

### Implementation

The enhanced frontend implementation includes:

1. **Emotional Journey Graph**: Visualizes the user's emotional journey using a graph.

```jsx
<EmotionalJourneyGraph 
  emotionalStates={emotionalStates} 
  transitions={transitions} 
  optimalPaths={optimalPaths} 
/>
```

2. **Suggested Actions Display**: Displays suggested actions from the A* search results.

```jsx
<SuggestedActions 
  actions={suggestedActions} 
  onActionSelect={handleActionSelect} 
/>
```

3. **Dataset Insights Display**: Displays insights from processed datasets.

```jsx
<DatasetInsights 
  insights={datasetInsights} 
/>
```

## Data Flow

The enhanced data flow in Reflectly follows these steps:

1. **User Input**: The user enters a journal entry in the frontend.
2. **API Request**: The frontend sends the journal entry to the backend API.
3. **Kafka Publishing**: The backend publishes the journal entry to the journal-entries Kafka topic.
4. **Spark Processing**: A Spark job analyzes emotions from the journal entry text.
5. **Emotional Graph Update**: The emotional graph is updated with the new emotional state.
6. **A* Search**: A* search finds the optimal path from the current to a target positive emotional state.
7. **Dataset Integration**: Insights from processed datasets are incorporated.
8. **Response Generation**: A personalized response is generated based on emotional context, history, optimal path, and dataset insights.
9. **API Response**: The backend sends the response back to the frontend.
10. **UI Update**: The frontend displays the response with suggested actions and visualizations.

## API Endpoints

### Authentication

#### POST /api/auth/register
Registers a new user.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "60a1e2c3d4e5f6a7b8c9d0e1"
}
```

#### POST /api/auth/login
Authenticates a user and returns a JWT token.

**Request:**
```json
{
  "email": "john.doe@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "60a1e2c3d4e5f6a7b8c9d0e1",
    "name": "John Doe",
    "email": "john.doe@example.com"
  }
}
```

### Journal Entries

#### GET /api/journal/entries
Retrieves all journal entries for the authenticated user.

**Response:**
```json
[
  {
    "_id": "60a1e2c3d4e5f6a7b8c9d0e2",
    "user_email": "john.doe@example.com",
    "content": "I had a great day today!",
    "created_at": "2025-03-14T12:00:00Z",
    "emotion": {
      "primary_emotion": "joy",
      "is_positive": true,
      "emotion_scores": {
        "joy": 0.8,
        "sadness": 0.1,
        "anger": 0.05,
        "fear": 0.03,
        "disgust": 0.02
      }
    }
  }
]
```

#### POST /api/journal/entries
Creates a new journal entry and returns an AI response.

**Request:**
```json
{
  "content": "I had a great day today!"
}
```

**Response:**
```json
{
  "message": "Journal entry created",
  "entry_id": "60a1e2c3d4e5f6a7b8c9d0e3",
  "response_id": "60a1e2c3d4e5f6a7b8c9d0e4",
  "response": {
    "text": "That's wonderful to hear! What made your day so great?",
    "suggested_actions": [
      "Share your positive experience with others",
      "Practice gratitude",
      "Savor the moment",
      "Set new goals"
    ],
    "dataset_insights": {
      "common_followups": [
        "Express gratitude for specific events",
        "Plan more activities that bring joy"
      ],
      "success_rate": 0.85
    },
    "optimal_path": {
      "current_emotion": "joy",
      "target_emotion": "joy",
      "path": ["joy"],
      "actions": [
        "Continue practicing gratitude",
        "Share your positive experiences"
      ]
    }
  }
}
```

### NEW: Emotional Path Endpoints

#### GET /api/emotions/optimal-path
Retrieves the optimal path from the current emotional state to a target positive state.

**Request:**
```json
{
  "current_emotion": "sadness",
  "target_emotion": "joy"
}
```

**Response:**
```json
{
  "optimal_path": {
    "current_emotion": "sadness",
    "target_emotion": "joy",
    "path": ["sadness", "neutral", "joy"],
    "actions": [
      {
        "from": "sadness",
        "to": "neutral",
        "action": "Practice mindfulness",
        "success_rate": 0.75
      },
      {
        "from": "neutral",
        "to": "joy",
        "action": "Engage in a favorite activity",
        "success_rate": 0.8
      }
    ],
    "total_cost": 2.45,
    "estimated_success_rate": 0.6
  }
}
```

#### GET /api/emotions/dataset-insights
Retrieves insights from processed datasets for a specific emotion.

**Request:**
```json
{
  "emotion": "sadness"
}
```

**Response:**
```json
{
  "emotion": "sadness",
  "insights": {
    "common_causes": [
      "Interpersonal conflicts",
      "Loss or disappointment",
      "Failure or setback"
    ],
    "effective_interventions": [
      "Social support",
      "Physical activity",
      "Expressive writing"
    ],
    "average_duration": "3.2 days",
    "common_transitions": [
      {
        "to_emotion": "neutral",
        "probability": 0.65
      },
      {
        "to_emotion": "joy",
        "probability": 0.25
      }
    ]
  }
}
```

### NEW: Big Data Status Endpoints

#### GET /api/bigdata/status
Retrieves the status of the big data infrastructure.

**Response:**
```json
{
  "kafka": {
    "status": "online",
    "topics": [
      "journal-entries",
      "emotion-analysis",
      "emotional-graph-updates"
    ]
  },
  "spark": {
    "status": "online",
    "active_jobs": 2,
    "completed_jobs": 145,
    "failed_jobs": 3
  },
  "hdfs": {
    "status": "online",
    "total_space": "100GB",
    "used_space": "45GB",
    "free_space": "55GB"
  }
}
```

#### GET /api/bigdata/datasets
Retrieves information about processed datasets.

**Response:**
```json
{
  "datasets": [
    {
      "name": "IEMOCAP",
      "status": "processed",
      "size": "5.2GB",
      "last_updated": "2025-03-10T15:30:00Z",
      "emotions": [
        "anger",
        "sadness",
        "happiness",
        "neutrality",
        "excitement",
        "frustration"
      ]
    },
    {
      "name": "Mental Health Conversations",
      "status": "processed",
      "size": "2.8GB",
      "last_updated": "2025-03-12T09:45:00Z",
      "topics": [
        "depression",
        "anxiety",
        "stress",
        "coping mechanisms",
        "support strategies"
      ]
    }
  ]
}
```

## Database Schema

### Users Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e1"),
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "hashed_password",
  "created_at": ISODate("2025-03-14T12:00:00Z"),
  "updated_at": ISODate("2025-03-14T12:00:00Z")
}
```

### Journal Entries Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e2"),
  "user_email": "john.doe@example.com",
  "content": "I had a great day today!",
  "created_at": ISODate("2025-03-14T12:00:00Z"),
  "emotion": {
    "primary_emotion": "joy",
    "is_positive": true,
    "emotion_scores": {
      "joy": 0.8,
      "sadness": 0.1,
      "anger": 0.05,
      "fear": 0.03,
      "disgust": 0.02
    }
  },
  "hdfs_path": "hdfs://namenode:9000/user/reflectly/journal-entries/60a1e2c3d4e5f6a7b8c9d0e2"
}
```

### AI Responses Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e3"),
  "user_email": "john.doe@example.com",
  "entry_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e2"),
  "content": "That's wonderful to hear! What made your day so great?",
  "suggested_actions": [
    "Share your positive experience with others",
    "Practice gratitude",
    "Savor the moment",
    "Set new goals"
  ],
  "dataset_insights": {
    "common_followups": [
      "Express gratitude for specific events",
      "Plan more activities that bring joy"
    ],
    "success_rate": 0.85
  },
  "optimal_path": {
    "current_emotion": "joy",
    "target_emotion": "joy",
    "path": ["joy"],
    "actions": [
      "Continue practicing gratitude",
      "Share your positive experiences"
    ]
  },
  "created_at": ISODate("2025-03-14T12:00:00Z")
}
```

### Emotional States Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e4"),
  "user_email": "john.doe@example.com",
  "primary_emotion": "joy",
  "is_positive": true,
  "emotion_scores": {
    "joy": 0.8,
    "sadness": 0.1,
    "anger": 0.05,
    "fear": 0.03,
    "disgust": 0.02
  },
  "entry_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e2"),
  "timestamp": ISODate("2025-03-14T12:00:00Z"),
  "hdfs_path": "hdfs://namenode:9000/user/reflectly/emotional-states/60a1e2c3d4e5f6a7b8c9d0e4"
}
```

### Emotional Transitions Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f2"),
  "user_email": "john.doe@example.com",
  "from_emotion": "sadness",
  "to_emotion": "joy",
  "from_state_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e5"),
  "to_state_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e4"),
  "actions": [
    {
      "description": "Called a friend",
      "success_rate": 0.75
    },
    {
      "description": "Went for a walk",
      "success_rate": 0.8
    }
  ],
  "timestamp": ISODate("2025-03-14T12:00:00Z"),
  "hdfs_path": "hdfs://namenode:9000/user/reflectly/emotional-transitions/60a1e2c3d4e5f6a7b8c9d0f2"
}
```

### NEW: A* Path Cache Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f3"),
  "user_email": "john.doe@example.com",
  "from_emotion": "sadness",
  "to_emotion": "joy",
  "path": ["sadness", "neutral", "joy"],
  "actions": [
    {
      "from": "sadness",
      "to": "neutral",
      "action": "Practice mindfulness",
      "success_rate": 0.75
    },
    {
      "from": "neutral",
      "to": "joy",
      "action": "Engage in a favorite activity",
      "success_rate": 0.8
    }
  ],
  "total_cost": 2.45,
  "estimated_success_rate": 0.6,
  "created_at": ISODate("2025-03-14T12:00:00Z"),
  "expires_at": ISODate("2025-03-15T12:00:00Z")
}
```

### NEW: Dataset Insights Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f4"),
  "dataset": "IEMOCAP",
  "emotion": "sadness",
  "insights": {
    "common_causes": [
      "Interpersonal conflicts",
      "Loss or disappointment",
      "Failure or setback"
    ],
    "effective_interventions": [
      "Social support",
      "Physical activity",
      "Expressive writing"
    ],
    "average_duration": "3.2 days",
    "common_transitions": [
      {
        "to_emotion": "neutral",
        "probability": 0.65
      },
      {
        "to_emotion": "joy",
        "probability": 0.25
      }
    ]
  },
  "created_at": ISODate("2025-03-10T15:30:00Z"),
  "updated_at": ISODate("2025-03-10T15:30:00Z")
}
```

## Authentication

Reflectly continues to use JWT (JSON Web Tokens) for authentication. The authentication flow remains the same:

1. **Registration**: The user registers with their name, email, and password.
2. **Login**: The user logs in with their email and password, and receives a JWT token.
3. **Authentication**: The JWT token is included in the Authorization header for authenticated requests.
4. **Verification**: The backend verifies the JWT token for protected routes.

## Deployment

Reflectly is now deployed using Docker Compose with additional containers for the big data infrastructure:

```yaml
version: '3'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - reflectly_network

  backend:
    build: ./backend
    ports:
      - "5002:5002"
    depends_on:
      - mongodb
      - redis
      - kafka
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/reflectly
      - REDIS_URI=redis://redis:6379/0
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - HDFS_NAMENODE=namenode:9000
      - SPARK_MASTER=spark://spark-master:7077
    networks:
      - reflectly_network
      - hadoop_network

  mongodb:
    image: mongo:4.4
    ports:
    mongodb:
    image: mongo:4.4
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - reflectly_network

  redis:
    image: redis:6.2
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - reflectly_network

  namenode:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: namenode
    hostname: namenode
    volumes:
      - hadoop_namenode:/hadoop/dfs/name
    environment:
      - CLUSTER_NAME=reflectly
      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    ports:
      - "9870:9870"
      - "9000:9000"
    networks:
      - hadoop_network

  datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: datanode
    hostname: datanode
    volumes:
      - hadoop_datanode:/hadoop/dfs/data
    environment:
      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    depends_on:
      - namenode
    networks:
      - hadoop_network
    ports:
      - "9864:9864"

  spark-master:
    image: bde2020/spark-master:3.3.0-hadoop3.3
    container_name: spark-master
    hostname: spark-master
    ports:
      - "8080:8080"
      - "7077:7077"
    environment:
      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    volumes:
      - spark_data:/spark/data
    networks:
      - hadoop_network

  spark-worker:
    image: bde2020/spark-worker:3.3.0-hadoop3.3
    container_name: spark-worker
    hostname: spark-worker
    environment:
      - SPARK_MASTER=spark://spark-master:7077
      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    volumes:
      - spark_data:/spark/data
    depends_on:
      - spark-master
    networks:
      - hadoop_network
    ports:
      - "8081:8081"

  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    hostname: zookeeper
    ports:
      - "2181:2181"
    networks:
      - hadoop_network

  kafka:
    image: wurstmeister/kafka
    container_name: kafka
    hostname: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_ADVERTISED_HOST_NAME=kafka
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_CREATE_TOPICS=journal-entries:3:1,emotion-analysis:3:1,emotional-graph-updates:3:1
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - zookeeper
    networks:
      - hadoop_network

networks:
  reflectly_network:
    driver: bridge
  hadoop_network:
    driver: bridge

volumes:
  mongodb_data:
  redis_data:
  hadoop_namenode:
  hadoop_datanode:
  spark_data:
```

The deployment process involves:

1. **Building Docker Images**: Build Docker images for the frontend and backend components.
2. **Starting the Infrastructure**: Start the MongoDB, Redis, Hadoop, Spark, and Kafka containers.
3. **Initializing HDFS**: Create necessary directories in HDFS for storing journal entries, emotional states, and processed datasets.
4. **Importing Datasets**: Import the IEMOCAP and mental health datasets into HDFS.
5. **Processing Datasets**: Process the datasets using Spark jobs.
6. **Starting the Application**: Start the frontend and backend containers.

## Environment Variables

### Backend Environment Variables

```
# MongoDB Configuration
MONGODB_URI=mongodb://mongodb:27017/reflectly

# Redis Configuration
REDIS_URI=redis://redis:6379/0

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Admin Configuration
ADMIN_SECRET=your_admin_secret

# Server Configuration
PORT=5002
DEBUG=True

# Big Data Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
HDFS_NAMENODE=namenode:9000
SPARK_MASTER=spark://spark-master:7077

# Kafka Topics
KAFKA_TOPIC_JOURNAL_ENTRIES=journal-entries
KAFKA_TOPIC_EMOTION_ANALYSIS=emotion-analysis
KAFKA_TOPIC_EMOTIONAL_GRAPH_UPDATES=emotional-graph-updates

# Dataset Paths
DATASET_IEMOCAP_PATH=hdfs://namenode:9000/user/reflectly/datasets/iemocap
DATASET_MENTAL_HEALTH_PATH=hdfs://namenode:9000/user/reflectly/datasets/mental_health
```

### Frontend Environment Variables

```
# API Configuration
REACT_APP_API_URL=http://localhost:5002

# Feature Flags
REACT_APP_ENABLE_VOICE_INPUT=true
REACT_APP_ENABLE_GOAL_TRACKING=true
REACT_APP_ENABLE_EMOTIONAL_JOURNEY_GRAPH=true
REACT_APP_ENABLE_OPTIMAL_PATH_VISUALIZATION=true

# Big Data Status
REACT_APP_SHOW_BIG_DATA_STATUS=true
```

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Git
- Web browser

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/reflectly.git
cd reflectly
```

2. Download the datasets (optional - needed for full functionality):
```bash
mkdir -p data/datasets/iemocap
mkdir -p data/datasets/mental_health
# Download datasets from Kaggle and place them in the respective directories
```

3. Start the infrastructure:
```bash
docker-compose up -d namenode datanode spark-master spark-worker zookeeper kafka mongodb redis
```

4. Initialize HDFS directories:
```bash
docker exec -it namenode hdfs dfs -mkdir -p /user/reflectly/journal-entries
docker exec -it namenode hdfs dfs -mkdir -p /user/reflectly/emotional-states
docker exec -it namenode hdfs dfs -mkdir -p /user/reflectly/emotional-transitions
docker exec -it namenode hdfs dfs -mkdir -p /user/reflectly/datasets
```

5. Import datasets to HDFS (if downloaded):
```bash
docker exec -it namenode hdfs dfs -put /path/to/data/datasets/iemocap /user/reflectly/datasets/
docker exec -it namenode hdfs dfs -put /path/to/data/datasets/mental_health /user/reflectly/datasets/
```

6. Start the application:
```bash
docker-compose up -d frontend backend
```

7. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5002
- Hadoop UI: http://localhost:9870
- Spark UI: http://localhost:8080
````

## File: docs/technical_documentation_V2.md
````markdown
# Reflectly Technical Documentation

**Version:** 1.1.0  
**Last Updated:** March 14, 2025  
**Author:** Reflectly Development Team

## Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Backend Components](#backend-components)
  - [Emotional Graph](#emotional-graph)
  - [Response Generator](#response-generator)
  - [Journal Entry Processing](#journal-entry-processing)
- [Frontend Components](#frontend-components)
- [Data Flow](#data-flow)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)

## Project Overview

Reflectly is a personal journaling application with a conversational interface designed to help users engage in meaningful self-reflection. The application combines a chat-like interface with intelligent emotional support and goal tracking features. The system uses emotional analysis to provide personalized responses and help users navigate from negative emotional states to positive ones.

### Core Functionality
- **Conversational Journaling**: Users interact with the application through a chat interface
- **Emotion Analysis**: The system analyzes user emotions from journal entries
- **Emotional Graph**: Tracks transitions between emotional states and suggests personalized interventions based on user history
- **Personalized Responses**: Generates responses tailored to the user's emotional context and history
- **Goal Tracking**: Users can set and track personal goals

## System Architecture

Reflectly follows a client-server architecture with separate frontend and backend components:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    Frontend     │◄────►│    Backend      │◄────►│    Database     │
│    (React.js)   │      │    (Flask)      │      │    (MongoDB)    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                  ▲
                                  │
                                  ▼
                         ┌─────────────────┐
                         │                 │
                         │     Redis       │
                         │    (Cache)      │
                         │                 │
                         └─────────────────┘
```

- **Frontend**: React.js application providing the user interface
- **Backend**: Flask application handling business logic, emotion analysis, and response generation
- **Database**: MongoDB for persistent storage of user data, journal entries, and emotional states
- **Cache**: Redis for temporary data storage and session management

## Technology Stack

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Date Handling**: date-fns

### Backend
- **Framework**: Flask (Python)
- **Authentication**: JWT (JSON Web Tokens)
- **Database ORM**: PyMongo
- **Emotion Analysis**: Custom implementation with BERT/RoBERTa models
- **Response Generation**: Template-based with personalization logic

### Database
- **Primary Database**: MongoDB
- **Caching**: Redis

### DevOps
- **Containerization**: Docker
- **Version Control**: Git
- **CI/CD**: GitHub Actions

## Directory Structure

```
/
├── backend/                # Flask backend application
│   ├── models/             # Business logic models
│   │   ├── emotional_graph.py  # Emotional state tracking and transitions
│   │   ├── response_generator.py  # AI response generation
│   │   └── ...
│   ├── utils/              # Utility functions
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── start_backend.sh    # Script to start the backend server
│
├── frontend/               # React frontend application
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   │   ├── components/     # Reusable UI components
│   │   │   ├── journal/    # Journal-related components
│   │   │   └── layout/     # Layout components
│   │   ├── context/        # React context providers
│   │   ├── pages/          # Application pages
│   │   ├── utils/          # Utility functions
│   │   ├── App.js          # Main application component
│   │   └── index.js        # Entry point
│   ├── package.json        # NPM dependencies
│   └── README.md           # Frontend documentation
│
└── docs/                   # Project documentation
    ├── technical_documentation.md  # Technical documentation
    └── context.md          # Project context and requirements
```

## Backend Components

### Emotional Graph

The `EmotionalGraph` class is responsible for tracking and analyzing user emotional states and transitions between them. It provides methods for recording emotions, retrieving emotional history, and suggesting personalized actions based on the user's emotional patterns.

#### Key Features

- **Emotion Recording**: Records user emotional states in MongoDB
- **Transition Tracking**: Tracks transitions between emotional states
- **Personalized Suggestions**: Provides personalized suggestions for transitioning from negative to positive emotional states
- **Emotional History**: Retrieves a user's emotional history for context-aware responses

#### Implementation

The `EmotionalGraph` class uses a graph-like structure to represent emotional states and transitions. Each node in the graph represents an emotional state, and edges represent transitions between states. The class provides methods for:

1. **Recording Emotions**: The `record_emotion` method records a user's emotional state and creates transitions between states.

```python
def record_emotion(self, user_email, emotion_data, entry_id=None):
    # Store the emotional state in MongoDB
    # Create transitions between states
    # Return the stored emotion document
```

2. **Getting Personalized Suggestions**: The `get_suggested_actions` method provides personalized suggestions for transitioning from the current emotional state based on the user's history.

```python
def get_suggested_actions(self, user_email, current_emotion):
    # If current emotion is positive, return generic suggestions
    # Find personalized suggestions based on user's emotional history
    # Return personalized or generic suggestions
```

3. **Finding Personalized Path Suggestions**: The `_find_personalized_path_suggestions` method identifies paths that have previously led from the current emotion to positive emotions.

```python
def _find_personalized_path_suggestions(self, user_email, current_emotion):
    # Get transitions from the current emotion to any positive emotion
    # Extract personalized suggestions based on content analysis
    # Return personalized suggestions
```

4. **Retrieving Emotional History**: The `get_emotion_history` method retrieves a user's emotional history for context-aware responses.

```python
def get_emotion_history(self, user_email, limit=5):
    # Get the most recent emotional states for the user
    # Convert ObjectId to string for serialization
    # Return emotional history
```

### Response Generator

The `ResponseGenerator` class generates personalized responses based on user input, emotion analysis, and emotional history. It provides methods for generating responses with different levels of personalization.

#### Key Features

- **Template-Based Responses**: Uses templates for different emotional states
- **Personalized Responses**: Incorporates user's emotional history for personalized responses
- **Suggested Actions**: Includes suggested actions for emotional improvement

#### Implementation

The `ResponseGenerator` class uses a template-based approach for generating responses, with additional personalization based on the user's emotional history. The class provides methods for:

1. **Generating Basic Responses**: The `generate` method generates a basic response based on user input and emotion analysis.

```python
def generate(self, text, emotion_data):
    # Generate a response based on the primary emotion
    # Return a formatted response
```

2. **Generating Personalized Responses**: The `generate_with_memory` method generates a personalized response incorporating emotional history and suggested actions.

```python
def generate_with_memory(self, text, emotion_data, memories=None, suggested_actions=None, emotion_history=None):
    # Generate a personalized response based on emotional context
    # Use provided suggested actions or generate generic ones
    # Add context about emotional journey
    # Return a response object with text and suggested actions
```

3. **Generating Context-Aware Responses**: The `_generate_personalized_response` method enhances responses with insights from the user's emotional history.

```python
def _generate_personalized_response(self, text, emotion_data, emotion_history=None):
    # Start with a base response
    # Enhance with personalized insights based on emotional history
    # Return a personalized response
```

### Journal Entry Processing

The journal entry processing logic in `app.py` handles the creation of journal entries, emotion analysis, and response generation. It integrates the `EmotionalGraph` and `ResponseGenerator` components to provide a complete journaling experience.

#### Key Features

- **Journal Entry Creation**: Creates journal entries in MongoDB
- **Emotion Analysis**: Analyzes emotions from journal entry text
- **Emotional Graph Integration**: Records emotions and transitions in the emotional graph
- **Personalized Response Generation**: Generates personalized responses based on emotional context and history

#### Implementation

The journal entry processing logic is implemented in the `create_journal_entry` route in `app.py`. The route handles:

1. **Journal Entry Creation**: Creates a journal entry in MongoDB.
2. **Emotion Analysis**: Analyzes emotions from the journal entry text.
3. **Emotional Graph Integration**: Records emotions and transitions in the emotional graph.
4. **Emotional History Retrieval**: Retrieves the user's emotional history for context.
5. **Personalized Suggestion Generation**: Gets personalized suggested actions from the emotional graph.
6. **Personalized Response Generation**: Generates a personalized response based on emotional context and history.

```python
@app.route('/api/journal/entries', methods=['POST'])
def create_journal_entry():
    # Create journal entry
    # Analyze emotions
    # Record emotion in emotional graph
    # Get emotional history
    # Get personalized suggested actions
    # Generate personalized response
    # Return response to frontend
```

## Frontend Components

The frontend of Reflectly is built with React.js and Material-UI. It provides a chat-like interface for journaling and displays AI responses with suggested actions.

### Key Components

- **Journal Page**: The main page for journaling, displaying the chat interface and handling user input.
- **Message Bubbles**: Components for displaying user messages and AI responses.
- **Suggested Actions**: Chips displaying suggested actions for emotional improvement.
- **Emotion Icons**: Icons representing different emotional states.

### Implementation

The frontend implementation includes:

1. **Journal Entry Creation**: Sends journal entries to the backend API and displays responses.

```javascript
const handleSubmit = async (e) => {
  // Send journal entry to API
  // Display AI response with suggested actions
};
```

2. **Response Display**: Displays AI responses with suggested actions.

```jsx
<Typography variant="body1">{entry.content}</Typography>

{/* Display suggested actions if available */}
{!entry.isUserMessage && entry.suggested_actions && entry.suggested_actions.length > 0 && (
  <Box sx={{ mt: 2 }}>
    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
      Suggested Actions:
    </Typography>
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
      {entry.suggested_actions.map((action, index) => (
        <Chip 
          key={index}
          label={action}
          size="small"
          color="primary"
          variant="outlined"
          sx={{ 
            borderRadius: 1,
            '&:hover': { backgroundColor: 'primary.light', color: 'white', cursor: 'pointer' }
          }}
        />
      ))}
    </Box>
  </Box>
)}
```

## Data Flow

The data flow in Reflectly follows these steps:

1. **User Input**: The user enters a journal entry in the frontend.
2. **API Request**: The frontend sends the journal entry to the backend API.
3. **Emotion Analysis**: The backend analyzes emotions from the journal entry text.
4. **Emotional Graph**: The backend records emotions and transitions in the emotional graph.
5. **Emotional History**: The backend retrieves the user's emotional history for context.
6. **Personalized Suggestions**: The backend gets personalized suggested actions from the emotional graph.
7. **Personalized Response**: The backend generates a personalized response based on emotional context and history.
8. **API Response**: The backend sends the response back to the frontend.
9. **UI Update**: The frontend displays the response with suggested actions.

## API Endpoints

### Authentication

#### POST /api/auth/register
Registers a new user.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "60a1e2c3d4e5f6a7b8c9d0e1"
}
```

#### POST /api/auth/login
Authenticates a user and returns a JWT token.

**Request:**
```json
{
  "email": "john.doe@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "60a1e2c3d4e5f6a7b8c9d0e1",
    "name": "John Doe",
    "email": "john.doe@example.com"
  }
}
```

### Journal Entries

#### GET /api/journal/entries
Retrieves all journal entries for the authenticated user.

**Response:**
```json
[
  {
    "_id": "60a1e2c3d4e5f6a7b8c9d0e2",
    "user_email": "john.doe@example.com",
    "content": "I had a great day today!",
    "created_at": "2025-03-14T12:00:00Z",
    "emotion": {
      "primary_emotion": "joy",
      "is_positive": true,
      "emotion_scores": {
        "joy": 0.8,
        "sadness": 0.1,
        "anger": 0.05,
        "fear": 0.03,
        "disgust": 0.02
      }
    }
  }
]
```

#### POST /api/journal/entries
Creates a new journal entry and returns an AI response.

**Request:**
```json
{
  "content": "I had a great day today!"
}
```

**Response:**
```json
{
  "message": "Journal entry created",
  "entry_id": "60a1e2c3d4e5f6a7b8c9d0e3",
  "response_id": "60a1e2c3d4e5f6a7b8c9d0e4",
  "response": {
    "text": "That's wonderful to hear! What made your day so great?",
    "suggested_actions": [
      "Share your positive experience with others",
      "Practice gratitude",
      "Savor the moment",
      "Set new goals"
    ]
  }
}
```

## Database Schema

### Users Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e1"),
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "hashed_password",
  "created_at": ISODate("2025-03-14T12:00:00Z"),
  "updated_at": ISODate("2025-03-14T12:00:00Z")
}
```

### Journal Entries Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e2"),
  "user_email": "john.doe@example.com",
  "content": "I had a great day today!",
  "created_at": ISODate("2025-03-14T12:00:00Z"),
  "emotion": {
    "primary_emotion": "joy",
    "is_positive": true,
    "emotion_scores": {
      "joy": 0.8,
      "sadness": 0.1,
      "anger": 0.05,
      "fear": 0.03,
      "disgust": 0.02
    }
  }
}
```

### AI Responses Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e3"),
  "user_email": "john.doe@example.com",
  "entry_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e2"),
  "content": "That's wonderful to hear! What made your day so great?",
  "suggested_actions": [
    "Share your positive experience with others",
    "Practice gratitude",
    "Savor the moment",
    "Set new goals"
  ],
  "created_at": ISODate("2025-03-14T12:00:00Z")
}
```

### Emotional States Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e4"),
  "user_email": "john.doe@example.com",
  "primary_emotion": "joy",
  "is_positive": true,
  "emotion_scores": {
    "joy": 0.8,
    "sadness": 0.1,
    "anger": 0.05,
    "fear": 0.03,
    "disgust": 0.02
  },
  "entry_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e2"),
  "timestamp": ISODate("2025-03-14T12:00:00Z")
}
```

### Emotional Transitions Collection

```json
{
  "_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0f2"),
  "user_email": "john.doe@example.com",
  "from_emotion": "sadness",
  "to_emotion": "joy",
  "from_state_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e5"),
  "to_state_id": ObjectId("60a1e2c3d4e5f6a7b8c9d0e4"),
  "timestamp": ISODate("2025-03-14T12:00:00Z")
}
```

## Authentication

Reflectly uses JWT (JSON Web Tokens) for authentication. The authentication flow is as follows:

1. **Registration**: The user registers with their name, email, and password.
2. **Login**: The user logs in with their email and password, and receives a JWT token.
3. **Authentication**: The JWT token is included in the Authorization header for authenticated requests.
4. **Verification**: The backend verifies the JWT token for protected routes.

## Deployment

Reflectly can be deployed using Docker containers for both the frontend and backend components. The deployment process involves:

1. **Building Docker Images**: Building Docker images for the frontend and backend components.
2. **Running Containers**: Running Docker containers for the frontend, backend, MongoDB, and Redis.
3. **Configuring Environment Variables**: Setting environment variables for the containers.
4. **Setting Up Networking**: Configuring networking between the containers.

## Environment Variables

### Backend Environment Variables

```
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/reflectly

# Redis Configuration
REDIS_URI=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Admin Configuration
ADMIN_SECRET=your_admin_secret

# Server Configuration
PORT=5002
DEBUG=True
```

### Frontend Environment Variables

```
# API Configuration
REACT_APP_API_URL=http://localhost:5002

# Feature Flags
REACT_APP_ENABLE_VOICE_INPUT=true
REACT_APP_ENABLE_GOAL_TRACKING=true
```
````

## File: docs/technical_documentation.md
````markdown
# Reflectly Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Directory Structure](#directory-structure)
5. [Backend Components](#backend-components)
6. [Frontend Components](#frontend-components)
7. [Data Flow](#data-flow)
8. [Key Features Implementation](#key-features-implementation)
9. [Authentication and User Management](#authentication-and-user-management)
10. [Deployment Instructions](#deployment-instructions)
11. [Development Workflow](#development-workflow)
12. [API Documentation](#api-documentation)

## Project Overview

Reflectly is a personal journaling application with a conversational interface designed to help users engage in meaningful self-reflection. The application combines a chat-like interface with intelligent emotional support, memory management, and goal tracking features.

### Core Functionality
- **Conversational Journaling**: Users interact with the application through a chat interface
- **Emotion Analysis**: The system analyzes user emotions from journal entries
- **Memory Management**: Past positive experiences are stored and retrieved when needed
- **Goal Tracking**: Users can set and track personal goals

## System Architecture

Reflectly follows a modern microservices architecture with containerized components:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    Frontend     │◄────►│    Backend      │◄────►│    Database     │
│    (React.js)   │      │    (Flask)      │      │    (MongoDB)    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                  ▲
                                  │
                                  ▼
                         ┌─────────────────┐
                         │                 │
                         │  Cache Layer    │
                         │    (Redis)      │
                         │                 │
                         └─────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React.js
- **UI Library**: Material-UI
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Containerization**: Docker

### Backend
- **Framework**: Flask (Python)
- **API**: RESTful endpoints
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker

### Database
- **Primary Database**: MongoDB
- **Caching**: Redis
- **Data Persistence**: Docker volumes

### AI/ML Components
- **Emotion Analysis**: BERT-based sentiment analysis
- **Response Generation**: Template-based with contextual awareness
- **Memory Management**: Multi-tier storage with intelligent retrieval

## Directory Structure

```
/Refection/
├── backend/                  # Backend Flask application
│   ├── models/               # Core business logic components
│   │   ├── emotion_analyzer.py  # Emotion analysis module
│   │   ├── goal_tracker.py      # Goal tracking functionality
│   │   ├── memory_manager.py    # Memory storage and retrieval
│   │   └── response_generator.py # AI response generation
│   ├── app.py                # Main Flask application
│   ├── admin_viewer.py       # Admin interface for database viewing
│   ├── user_management.py    # User authentication and management
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
├── frontend/                 # React frontend application
│   ├── public/               # Static assets
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable UI components
│   │   ├── context/          # React context providers
│   │   ├── pages/            # Application pages
│   │   ├── services/         # API service integrations
│   │   └── utils/            # Utility functions
│   ├── package.json          # NPM dependencies
│   └── Dockerfile            # Frontend container definition
├── docker/                   # Docker configuration files
├── docker-compose.yml        # Multi-container orchestration
├── docs/                     # Documentation
│   └── context.md            # Project context and specifications
└── README.md                 # Project overview
```

## Backend Components

### Flask Application (app.py)
The main application entry point that defines API routes, initializes components, and handles HTTP requests.

Key endpoints:
- `/api/auth/login`: User authentication
- `/api/auth/register`: User registration
- `/api/journal/entries`: CRUD operations for journal entries
- `/api/goals`: Goal management endpoints
- `/api/admin/*`: Administrative endpoints

### Emotion Analyzer (emotion_analyzer.py)
Analyzes text to identify emotions and sentiment:
- Detects primary emotion (joy, sadness, anger, fear, disgust, surprise)
- Determines if the emotion is positive or negative
- Calculates confidence scores for each emotion

### Memory Manager (memory_manager.py)
Manages the storage and retrieval of journal entries and memories:
- Multi-tier storage system (short-term, medium-term, long-term)
- Redis caching for frequently accessed memories
- Intelligent retrieval of relevant memories based on emotional context
- Stores positive memories for future encouragement

### Response Generator (response_generator.py)
Generates AI responses to user journal entries:
- Template-based responses customized to emotional context
- Incorporates past memories when appropriate
- Provides encouragement during negative emotional states
- Reinforces positive experiences

### Goal Tracker (goal_tracker.py)
Manages user goals and tracks progress:
- Goal creation and update functionality
- Progress tracking and milestone recognition
- Pattern recognition for achievement analysis

### User Management (user_management.py)
Handles user authentication and account management:
- User registration and login
- Password hashing with bcrypt
- JWT token generation and validation
- User profile management

## Frontend Components

### App Structure
- **App.js**: Main application component with routing
- **index.js**: Entry point that renders the React application

### Pages
- **Login.js**: User authentication interface
- **Register.js**: New user registration
- **Journal.js**: Main journaling interface with chat functionality
- **Goals.js**: Goal setting and tracking interface
- **Profile.js**: User profile management
- **Dashboard.js**: Overview of journal entries and emotions

### Components
- **journal/MemoryCard.js**: Displays memory cards in the journal chat
- **journal/ChatBubble.js**: Individual chat message bubbles
- **common/Navbar.js**: Application navigation
- **goals/GoalItem.js**: Individual goal display and tracking

### Context Providers
- **AuthContext.js**: Authentication state management
- **JournalContext.js**: Journal entries and chat state

## Data Flow

### Journal Entry Creation
1. User enters text in the journal interface
2. Frontend sends entry to backend via API
3. Backend processes the entry:
   - Analyzes emotions using the emotion analyzer
   - Generates an AI response using the response generator
   - Stores the entry in MongoDB
   - Caches positive memories in Redis
4. Response is sent back to frontend with:
   - AI-generated text response
   - Memory card data (if applicable)
5. Frontend displays the response and any memory cards

### Memory Card Display Logic
1. When a user expresses negative emotions:
   - The system retrieves past positive memories
   - A memory card is displayed to provide encouragement
2. When a user expresses positive emotions:
   - The system stores the memory for future reference
   - No memory card is displayed to avoid unnecessary distractions

## Key Features Implementation

### Conversational Journaling Interface
The journal interface mimics a chat application with:
- User messages displayed on the right
- AI responses displayed on the left
- Memory cards appearing inline when triggered
- Real-time emotion analysis feedback

### Emotion Tracking System
- **Emotion Detection**: Text analysis identifies primary emotions
- **Emotion Storage**: Emotions are stored with journal entries
- **Emotion Trends**: Patterns are analyzed over time

### Memory Management System
- **Short-term Memory**: Recent entries cached in Redis (7 days)
- **Medium-term Memory**: Active entries in MongoDB (30 days)
- **Long-term Memory**: Historical entries for pattern analysis (365 days)
- **Memory Retrieval**: Intelligent retrieval based on emotional context

### Goal Setting and Tracking
- **Goal Creation**: Users define goals with measurable criteria
- **Progress Tracking**: System tracks progress through user updates
- **Achievement Recognition**: Milestones are celebrated with notifications

## Authentication and User Management

### User Registration
1. User provides email and password
2. Password is hashed using bcrypt
3. User account is created in MongoDB
4. JWT token is generated and returned

### User Authentication
1. User submits login credentials
2. Backend verifies email and password
3. JWT token is generated with user information
4. Token is returned to frontend and stored in local storage

### Admin Functionality
- List all users in the system
- Create new users with specified credentials
- Delete users from the system
- View database structure and contents

## Deployment Instructions

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- Node.js and npm for frontend development
- Python for backend development

### Development Environment Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Refection
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5002
   - MongoDB Viewer: http://localhost:5003

### Manual Backend Setup (Alternative)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask application:
   ```bash
   python app.py
   ```

### Manual Frontend Setup (Alternative)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Development Workflow

### Code Organization
- **Backend**: Modular Python code with clear separation of concerns
- **Frontend**: Component-based React architecture
- **Shared**: Docker configuration for consistent environments

### Version Control
- Use feature branches for new development
- Pull requests for code review
- Semantic versioning for releases

### Testing
- Unit tests for backend components
- Integration tests for API endpoints
- End-to-end tests for critical user flows

## API Documentation

### Authentication Endpoints

#### POST /api/auth/login
Authenticates a user and returns a JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

#### POST /api/auth/register
Registers a new user.

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "New User"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "newuser@example.com",
    "name": "New User"
  }
}
```

### Journal Endpoints

#### POST /api/journal/entries
Creates a new journal entry.

**Request:**
```json
{
  "content": "I'm feeling happy today because I accomplished my goal."
}
```

**Response:**
```json
{
  "entry": {
    "id": "60c72b2f9b1d8a1234567890",
    "content": "I'm feeling happy today because I accomplished my goal.",
    "created_at": "2023-06-14T12:30:45Z",
    "emotion": {
      "primary_emotion": "joy",
      "is_positive": true,
      "emotion_scores": {
        "joy": 0.85,
        "sadness": 0.05,
        "anger": 0.02,
        "fear": 0.03,
        "disgust": 0.01,
        "surprise": 0.04
      }
    }
  },
  "response": {
    "text": "That's wonderful! I'm glad to hear you're feeling happy. What goal did you accomplish?",
    "memory": null
  }
}
```

#### GET /api/journal/entries
Retrieves journal entries for the authenticated user.

**Response:**
```json
{
  "entries": [
    {
      "id": "60c72b2f9b1d8a1234567890",
      "content": "I'm feeling happy today because I accomplished my goal.",
      "created_at": "2023-06-14T12:30:45Z",
      "emotion": {
        "primary_emotion": "joy",
        "is_positive": true
      }
    },
    {
      "id": "60c72b2f9b1d8a1234567891",
      "content": "I'm feeling sad today.",
      "created_at": "2023-06-13T10:15:30Z",
      "emotion": {
        "primary_emotion": "sadness",
        "is_positive": false
      }
    }
  ]
}
```

### Admin Endpoints

#### GET /api/admin/users
Retrieves all users (requires admin authentication).

**Response:**
```json
{
  "users": [
    {
      "email": "user1@example.com",
      "name": "User One",
      "created_at": "2023-05-01T09:00:00Z"
    },
    {
      "email": "user2@example.com",
      "name": "User Two",
      "created_at": "2023-05-02T10:30:00Z"
    }
  ]
}
```

#### POST /api/admin/users
Creates a new user (requires admin authentication).

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "New User"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "email": "newuser@example.com",
    "name": "New User"
  }
}
```

#### DELETE /api/admin/users/<email>
Deletes a user (requires admin authentication).

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

## Conclusion

Reflectly is a sophisticated journaling application that combines modern web technologies with AI-powered emotional intelligence. The application's architecture is designed for scalability, maintainability, and extensibility, making it well-suited for future enhancements and feature additions.

The modular design of both frontend and backend components allows for independent development and testing, while the containerized deployment ensures consistency across different environments.
````

## File: frontend/public/manifest.json
````json
{
  "short_name": "Reflectly",
  "name": "Reflectly - Personal Journaling",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "logo192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "logo512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#4dabf5",
  "background_color": "#ffffff"
}
````

## File: frontend/src/components/journal/MemoryCard.js
````javascript
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  useTheme
} from '@mui/material';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import BookmarkIcon from '@mui/icons-material/Bookmark';

/**
 * Component for displaying a memory card in the journal chat
 */
const MemoryCard = ({ memoryData, memoryType }) => {
  const theme = useTheme();
  
  // Different styling based on memory type
  const getCardStyle = () => {
    if (memoryType === 'encouragement') {
      return {
        backgroundColor: theme.palette.mode === 'dark' 
          ? 'rgba(129, 199, 132, 0.15)' 
          : 'rgba(129, 199, 132, 0.1)',
        borderLeft: `4px solid ${theme.palette.success.main}`
      };
    } else if (memoryType === 'reinforcement') {
      return {
        backgroundColor: theme.palette.mode === 'dark' 
          ? 'rgba(144, 202, 249, 0.15)' 
          : 'rgba(144, 202, 249, 0.1)',
        borderLeft: `4px solid ${theme.palette.primary.main}`
      };
    }
    return {};
  };
  
  if (!memoryData) return null;
  
  return (
    <Card 
      variant="outlined" 
      sx={{
        my: 1,
        mx: 0,
        width: '100%',
        borderRadius: 2,
        ...getCardStyle()
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <BookmarkIcon 
            color={memoryType === 'encouragement' ? 'success' : 'primary'} 
            fontSize="small" 
            sx={{ mr: 1 }} 
          />
          <Typography variant="subtitle2" color="textSecondary">
            Memory from your journal
          </Typography>
        </Box>
        
        <Typography variant="body1" sx={{ mb: 2 }}>
          {memoryData.summary}
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <CalendarTodayIcon fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
            <Typography variant="caption" color="textSecondary">
              {memoryData.date}
            </Typography>
          </Box>
          
          <Chip
            icon={<SentimentSatisfiedAltIcon fontSize="small" />}
            label={memoryData.emotion}
            size="small"
            color={memoryType === 'encouragement' ? 'success' : 'primary'}
            variant="outlined"
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default MemoryCard;
````

## File: frontend/src/components/layout/Footer.js
````javascript
import React from 'react';
import { Box, Container, Typography, Link, Divider } from '@mui/material';
import { useTheme } from '@mui/material/styles';

const Footer = () => {
  const theme = useTheme();
  const currentYear = new Date().getFullYear();

  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: theme.palette.mode === 'light' 
          ? theme.palette.grey[100] 
          : theme.palette.grey[900],
      }}
    >
      <Container maxWidth="lg">
        <Divider sx={{ mb: 3 }} />
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © {currentYear} Reflectly. All rights reserved.
          </Typography>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              mt: { xs: 2, sm: 0 },
            }}
          >
            <Link href="#" color="inherit" sx={{ mx: 1 }}>
              Privacy
            </Link>
            <Link href="#" color="inherit" sx={{ mx: 1 }}>
              Terms
            </Link>
            <Link href="#" color="inherit" sx={{ mx: 1 }}>
              Contact
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
````

## File: frontend/src/context/ThemeContext.js
````javascript
import React, { createContext, useState, useContext, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles';

const ThemeContext = createContext();

export const useThemeContext = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
  const [mode, setMode] = useState(() => {
    const savedMode = localStorage.getItem('themeMode');
    return savedMode || 'light';
  });

  const toggleTheme = () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setMode(newMode);
    localStorage.setItem('themeMode', newMode);
  };

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: {
            main: '#4dabf5',
            light: '#80d8ff',
            dark: '#0077c2',
            contrastText: '#fff',
          },
          secondary: {
            main: '#66bb6a',
            light: '#98ee99',
            dark: '#338a3e',
            contrastText: '#fff',
          },
          background: {
            default: mode === 'light' ? '#f5f5f5' : '#121212',
            paper: mode === 'light' ? '#fff' : '#1e1e1e',
          },
        },
        typography: {
          fontFamily: [
            'Roboto',
            '"Helvetica Neue"',
            'Arial',
            'sans-serif',
          ].join(','),
          h1: {
            fontSize: '2.5rem',
            fontWeight: 500,
          },
          h2: {
            fontSize: '2rem',
            fontWeight: 500,
          },
          h3: {
            fontSize: '1.75rem',
            fontWeight: 500,
          },
          h4: {
            fontSize: '1.5rem',
            fontWeight: 500,
          },
          h5: {
            fontSize: '1.25rem',
            fontWeight: 500,
          },
          h6: {
            fontSize: '1rem',
            fontWeight: 500,
          },
        },
        shape: {
          borderRadius: 8,
        },
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: 'none',
                borderRadius: 8,
                padding: '8px 16px',
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 12,
                boxShadow: mode === 'light' 
                  ? '0 4px 12px rgba(0,0,0,0.05)' 
                  : '0 4px 12px rgba(0,0,0,0.2)',
              },
            },
          },
          MuiTextField: {
            styleOverrides: {
              root: {
                marginBottom: 16,
              },
            },
          },
        },
      }),
    [mode],
  );

  const value = {
    mode,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={theme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
````

## File: frontend/src/pages/Goals.js
````javascript
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Paper,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  LinearProgress,
  Chip,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Divider,
  Alert,
  Snackbar,
  Tooltip,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import DateRangeIcon from '@mui/icons-material/DateRange';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { format, isAfter, differenceInDays } from 'date-fns';
import axios from '../utils/axiosConfig';

const Goals = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingGoal, setEditingGoal] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    target_date: null,
    progress: 0
  });
  const [progressDialogOpen, setProgressDialogOpen] = useState(false);
  const [currentGoalId, setCurrentGoalId] = useState(null);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Fetch goals on component mount
  useEffect(() => {
    fetchGoals();
  }, []);
  
  const fetchGoals = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/goals');
      setGoals(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching goals:', err);
      setError('Failed to load goals. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleOpenDialog = (goal = null) => {
    if (goal) {
      // Edit existing goal
      setEditingGoal(goal);
      setFormData({
        title: goal.title,
        description: goal.description || '',
        target_date: goal.target_date ? new Date(goal.target_date) : null,
        progress: goal.progress || 0
      });
    } else {
      // Create new goal
      setEditingGoal(null);
      setFormData({
        title: '',
        description: '',
        target_date: null,
        progress: 0
      });
    }
    setOpenDialog(true);
  };
  
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingGoal(null);
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  
  const handleDateChange = (date) => {
    setFormData({ ...formData, target_date: date });
  };
  
  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      if (editingGoal) {
        // Update existing goal
        await axios.put(`/api/goals/${editingGoal._id}`, formData);
        setSnackbar({
          open: true,
          message: 'Goal updated successfully!',
          severity: 'success'
        });
      } else {
        // Create new goal
        await axios.post('/api/goals', formData);
        setSnackbar({
          open: true,
          message: 'Goal created successfully!',
          severity: 'success'
        });
      }
      
      // Refresh goals
      fetchGoals();
      handleCloseDialog();
    } catch (err) {
      console.error('Error saving goal:', err);
      setSnackbar({
        open: true,
        message: 'Failed to save goal. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleDeleteGoal = async (goalId) => {
    if (!window.confirm('Are you sure you want to delete this goal?')) {
      return;
    }
    
    try {
      setLoading(true);
      await axios.delete(`/api/goals/${goalId}`);
      
      // Update local state
      setGoals(goals.filter(goal => goal._id !== goalId));
      
      setSnackbar({
        open: true,
        message: 'Goal deleted successfully!',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error deleting goal:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete goal. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleOpenProgressDialog = (goalId, currentProgress) => {
    setCurrentGoalId(goalId);
    setCurrentProgress(currentProgress);
    setProgressDialogOpen(true);
  };
  
  const handleCloseProgressDialog = () => {
    setProgressDialogOpen(false);
    setCurrentGoalId(null);
  };
  
  const handleProgressChange = (e) => {
    setCurrentProgress(Number(e.target.value));
  };
  
  const handleUpdateProgress = async () => {
    try {
      setLoading(true);
      await axios.put(`/api/goals/${currentGoalId}/progress`, {
        progress: currentProgress
      });
      
      // Update local state
      setGoals(goals.map(goal => 
        goal._id === currentGoalId 
          ? { ...goal, progress: currentProgress } 
          : goal
      ));
      
      setSnackbar({
        open: true,
        message: currentProgress >= 100 
          ? 'Congratulations! Goal completed!' 
          : 'Progress updated successfully!',
        severity: 'success'
      });
      
      handleCloseProgressDialog();
    } catch (err) {
      console.error('Error updating progress:', err);
      setSnackbar({
        open: true,
        message: 'Failed to update progress. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };
  
  const getGoalStatusColor = (goal) => {
    if (goal.progress >= 100) {
      return theme.palette.success.main;
    }
    
    if (goal.target_date) {
      const targetDate = new Date(goal.target_date);
      const today = new Date();
      
      if (isAfter(today, targetDate)) {
        return theme.palette.error.main; // Overdue
      }
      
      const daysRemaining = differenceInDays(targetDate, today);
      if (daysRemaining <= 7) {
        return theme.palette.warning.main; // Due soon
      }
    }
    
    return theme.palette.info.main; // In progress
  };
  
  const getGoalStatusText = (goal) => {
    if (goal.progress >= 100) {
      return 'Completed';
    }
    
    if (goal.target_date) {
      const targetDate = new Date(goal.target_date);
      const today = new Date();
      
      if (isAfter(today, targetDate)) {
        return 'Overdue';
      }
      
      const daysRemaining = differenceInDays(targetDate, today);
      if (daysRemaining <= 7) {
        return `Due soon (${daysRemaining} days)`;
      }
      
      return `${daysRemaining} days remaining`;
    }
    
    return 'In progress';
  };
  
  // Group goals by status
  const groupedGoals = {
    completed: goals.filter(goal => goal.progress >= 100),
    active: goals.filter(goal => goal.progress < 100)
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Your Goals
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Goal
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      {loading && goals.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : goals.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            You don't have any goals yet
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Set your first goal to start tracking your progress
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Create Your First Goal
          </Button>
        </Paper>
      ) : (
        <>
          {/* Active Goals */}
          <Typography variant="h5" component="h2" sx={{ mb: 2, mt: 4 }}>
            Active Goals
          </Typography>
          
          {groupedGoals.active.length === 0 ? (
            <Paper sx={{ p: 3, mb: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                You don't have any active goals. All your goals are completed!
              </Typography>
            </Paper>
          ) : (
            <Grid container spacing={3} sx={{ mb: 4 }}>
              {groupedGoals.active.map(goal => (
                <Grid item xs={12} sm={6} md={4} key={goal._id}>
                  <Card 
                    sx={{ 
                      height: '100%', 
                      display: 'flex', 
                      flexDirection: 'column',
                      position: 'relative',
                      overflow: 'visible'
                    }}
                  >
                    {/* Progress indicator */}
                    <Box 
                      sx={{ 
                        position: 'absolute', 
                        top: -8, 
                        left: 16, 
                        right: 16, 
                        zIndex: 1 
                      }}
                    >
                      <LinearProgress 
                        variant="determinate" 
                        value={goal.progress} 
                        sx={{ 
                          height: 8, 
                          borderRadius: 4,
                          backgroundColor: theme.palette.grey[300],
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getGoalStatusColor(goal)
                          }
                        }} 
                      />
                    </Box>
                    
                    <CardContent sx={{ pt: 3, flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="h6" component="h3" gutterBottom>
                          {goal.title}
                        </Typography>
                        <Chip 
                          label={`${goal.progress}%`} 
                          size="small" 
                          color={goal.progress >= 100 ? "success" : "primary"} 
                        />
                      </Box>
                      
                      {goal.description && (
                        <Typography variant="body2" color="text.secondary" paragraph>
                          {goal.description}
                        </Typography>
                      )}
                      
                      {goal.target_date && (
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <DateRangeIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            Due: {format(new Date(goal.target_date), 'MMM d, yyyy')}
                          </Typography>
                        </Box>
                      )}
                      
                      <Chip 
                        label={getGoalStatusText(goal)} 
                        size="small" 
                        sx={{ 
                          backgroundColor: getGoalStatusColor(goal),
                          color: '#fff',
                          mt: 1
                        }} 
                      />
                    </CardContent>
                    
                    <Divider />
                    
                    <CardActions>
                      <Button 
                        size="small" 
                        startIcon={<TrendingUpIcon />}
                        onClick={() => handleOpenProgressDialog(goal._id, goal.progress)}
                      >
                        Update Progress
                      </Button>
                      <Box sx={{ flexGrow: 1 }} />
                      <Tooltip title="Edit">
                        <IconButton 
                          size="small" 
                          onClick={() => handleOpenDialog(goal)}
                          aria-label="edit"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteGoal(goal._id)}
                          aria-label="delete"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
          
          {/* Completed Goals */}
          {groupedGoals.completed.length > 0 && (
            <>
              <Typography variant="h5" component="h2" sx={{ mb: 2, mt: 4, display: 'flex', alignItems: 'center' }}>
                <CheckCircleIcon sx={{ mr: 1, color: 'success.main' }} />
                Completed Goals
              </Typography>
              
              <Grid container spacing={3}>
                {groupedGoals.completed.map(goal => (
                  <Grid item xs={12} sm={6} md={4} key={goal._id}>
                    <Card 
                      sx={{ 
                        height: '100%', 
                        display: 'flex', 
                        flexDirection: 'column',
                        opacity: 0.8
                      }}
                    >
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                          <Typography variant="h6" component="h3" gutterBottom>
                            {goal.title}
                          </Typography>
                          <Chip 
                            label="100%" 
                            size="small" 
                            color="success" 
                          />
                        </Box>
                        
                        {goal.description && (
                          <Typography variant="body2" color="text.secondary" paragraph>
                            {goal.description}
                          </Typography>
                        )}
                        
                        {goal.target_date && (
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <DateRangeIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                            <Typography variant="body2" color="text.secondary">
                              Completed: {format(new Date(goal.updated_at || goal.target_date), 'MMM d, yyyy')}
                            </Typography>
                          </Box>
                        )}
                      </CardContent>
                      
                      <Divider />
                      
                      <CardActions>
                        <Tooltip title="Delete">
                          <IconButton 
                            size="small" 
                            onClick={() => handleDeleteGoal(goal._id)}
                            aria-label="delete"
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </>
          )}
        </>
      )}
      
      {/* Create/Edit Goal Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingGoal ? 'Edit Goal' : 'Create New Goal'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Goal Title"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.title}
            onChange={handleInputChange}
            required
            sx={{ mb: 2, mt: 1 }}
          />
          
          <TextField
            margin="dense"
            name="description"
            label="Description (Optional)"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.description}
            onChange={handleInputChange}
            multiline
            rows={3}
            sx={{ mb: 2 }}
          />
          
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="Target Date (Optional)"
              value={formData.target_date}
              onChange={handleDateChange}
              renderInput={(params) => (
                <TextField 
                  {...params} 
                  fullWidth 
                  margin="dense"
                  sx={{ mb: 2 }}
                />
              )}
              minDate={new Date()}
            />
          </LocalizationProvider>
          
          {editingGoal && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Current Progress: {formData.progress}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={formData.progress} 
                sx={{ height: 10, borderRadius: 5 }} 
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={!formData.title.trim() || loading}
          >
            {loading ? <CircularProgress size={24} /> : editingGoal ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Update Progress Dialog */}
      <Dialog open={progressDialogOpen} onClose={handleCloseProgressDialog} maxWidth="xs" fullWidth>
        <DialogTitle>Update Progress</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>
              Current Progress: {currentProgress}%
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={currentProgress} 
              sx={{ 
                height: 10, 
                borderRadius: 5,
                mb: 3
              }} 
            />
            
            <TextField
              type="number"
              label="Progress Percentage"
              value={currentProgress}
              onChange={handleProgressChange}
              inputProps={{ min: 0, max: 100 }}
              fullWidth
              variant="outlined"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseProgressDialog}>Cancel</Button>
          <Button 
            onClick={handleUpdateProgress} 
            variant="contained" 
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Goals;
````

## File: frontend/src/pages/Home.js
````javascript
import React from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Import icons
import ChatIcon from '@mui/icons-material/Chat';
import EmojiEmotionsIcon from '@mui/icons-material/EmojiEmotions';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import MemoryIcon from '@mui/icons-material/Memory';

const Home = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isAuthenticated } = useAuth();

  const features = [
    {
      title: 'Conversational Journaling',
      description: 'Chat with yourself in a familiar interface. Document your daily experiences, emotions, and goals with ease.',
      icon: <ChatIcon fontSize="large" color="primary" />
    },
    {
      title: 'Emotion Tracking',
      description: 'Our AI analyzes your emotions and provides support when you need it most, celebrating your happiness and helping during tough times.',
      icon: <EmojiEmotionsIcon fontSize="large" color="primary" />
    },
    {
      title: 'Goal Setting',
      description: 'Set personal goals and track your progress. Receive encouragement and celebrate milestones along the way.',
      icon: <TrackChangesIcon fontSize="large" color="primary" />
    },
    {
      title: 'Memory Management',
      description: 'Intelligent retrieval of past positive experiences when you need them most, helping you remember the good times.',
      icon: <MemoryIcon fontSize="large" color="primary" />
    }
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box 
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: { xs: 8, md: 12 },
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography 
                variant="h2" 
                component="h1" 
                gutterBottom
                sx={{ 
                  fontWeight: 700,
                  fontSize: { xs: '2.5rem', md: '3.5rem' }
                }}
              >
                Reflect on Your Journey
              </Typography>
              <Typography 
                variant="h5" 
                component="p" 
                gutterBottom
                sx={{ mb: 4, opacity: 0.9 }}
              >
                A personal journaling app designed to help you engage in meaningful self-reflection through a conversational interface.
              </Typography>
              <Box sx={{ mt: 4 }}>
                <Button
                  component={RouterLink}
                  to={isAuthenticated ? "/journal" : "/register"}
                  variant="contained"
                  size="large"
                  color="secondary"
                  sx={{ 
                    mr: 2, 
                    px: 4, 
                    py: 1.5,
                    fontSize: '1.1rem'
                  }}
                >
                  {isAuthenticated ? "Start Journaling" : "Get Started"}
                </Button>
                {!isAuthenticated && (
                  <Button
                    component={RouterLink}
                    to="/login"
                    variant="outlined"
                    size="large"
                    sx={{ 
                      px: 4, 
                      py: 1.5,
                      fontSize: '1.1rem',
                      color: 'white',
                      borderColor: 'white',
                      '&:hover': {
                        borderColor: 'white',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)'
                      }
                    }}
                  >
                    Login
                  </Button>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={6} sx={{ display: { xs: 'none', md: 'block' } }}>
              <Box 
                component="img"
                src="/hero-image.png" 
                alt="Reflectly App"
                sx={{
                  width: '100%',
                  maxWidth: 500,
                  height: 'auto',
                  display: 'block',
                  margin: '0 auto',
                  filter: 'drop-shadow(0 10px 20px rgba(0,0,0,0.2))',
                  transform: 'translateY(20px)'
                }}
              />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography 
          variant="h3" 
          component="h2" 
          align="center" 
          gutterBottom
          sx={{ mb: 6 }}
        >
          Key Features
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 20px rgba(0,0,0,0.1)'
                  }
                }}
                elevation={2}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
                  <Box sx={{ mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography gutterBottom variant="h5" component="h3">
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* How It Works Section */}
      <Box sx={{ bgcolor: theme.palette.grey[50], py: 8 }}>
        <Container maxWidth="lg">
          <Typography 
            variant="h3" 
            component="h2" 
            align="center" 
            gutterBottom
            sx={{ mb: 6 }}
          >
            How It Works
          </Typography>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box 
                component="img"
                src="/app-screenshot.png" 
                alt="Reflectly App Screenshot"
                sx={{
                  width: '100%',
                  height: 'auto',
                  borderRadius: 2,
                  boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box>
                <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600 }}>
                  1. Start a Conversation
                </Typography>
                <Typography variant="body1" paragraph>
                  Begin by typing or speaking your thoughts in our chat-like interface. Share your day, express your feelings, or document your achievements.
                </Typography>

                <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600, mt: 3 }}>
                  2. Receive Intelligent Responses
                </Typography>
                <Typography variant="body1" paragraph>
                  Our AI analyzes your emotions and provides thoughtful responses to help you reflect deeper and gain insights about yourself.
                </Typography>

                <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600, mt: 3 }}>
                  3. Track Your Progress
                </Typography>
                <Typography variant="body1" paragraph>
                  Set personal goals and monitor your progress over time. Celebrate achievements and learn from setbacks with our visual tracking tools.
                </Typography>

                <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600, mt: 3 }}>
                  4. Reflect on Your Journey
                </Typography>
                <Typography variant="body1" paragraph>
                  Access your past entries and see how you've grown. Our memory system highlights positive experiences when you need encouragement.
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Call to Action */}
      <Box 
        sx={{ 
          bgcolor: 'secondary.main', 
          color: 'white', 
          py: 8, 
          textAlign: 'center' 
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h3" component="h2" gutterBottom>
            Start Your Reflection Journey Today
          </Typography>
          <Typography variant="h6" component="p" sx={{ mb: 4, opacity: 0.9 }}>
            Join thousands of users who are discovering themselves through meaningful journaling.
          </Typography>
          <Button
            component={RouterLink}
            to={isAuthenticated ? "/journal" : "/register"}
            variant="contained"
            size="large"
            color="primary"
            sx={{ 
              px: 4, 
              py: 1.5,
              fontSize: '1.1rem'
            }}
          >
            {isAuthenticated ? "Go to Journal" : "Sign Up Now"}
          </Button>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;
````

## File: frontend/src/pages/Login.js
````javascript
import React, { useState } from 'react';
import { Link as RouterLink, Navigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Link,
  Paper,
  Grid,
  Alert,
  IconButton,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState({});
  
  const { login, isAuthenticated, loading, error, clearError } = useAuth();

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/journal" />;
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    // Clear field error when user types
    if (formErrors[name]) {
      setFormErrors({ ...formErrors, [name]: '' });
    }
    
    // Clear API error when user makes changes
    if (error) {
      clearError();
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      errors.password = 'Password is required';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      await login(formData);
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Container component="main" maxWidth="sm" sx={{ py: 8 }}>
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          borderRadius: 2
        }}
      >
        <Typography component="h1" variant="h4" sx={{ mb: 3 }}>
          Welcome Back
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            value={formData.email}
            onChange={handleChange}
            error={!!formErrors.email}
            helperText={formErrors.email}
            disabled={loading}
          />
          
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type={showPassword ? 'text' : 'password'}
            id="password"
            autoComplete="current-password"
            value={formData.password}
            onChange={handleChange}
            error={!!formErrors.password}
            helperText={formErrors.password}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleClickShowPassword}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            sx={{ mt: 3, mb: 2, py: 1.5 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Sign In'}
          </Button>
          
          <Grid container justifyContent="space-between" sx={{ mt: 2 }}>
            <Grid item>
              <Link href="#" variant="body2">
                Forgot password?
              </Link>
            </Grid>
            <Grid item>
              <Link component={RouterLink} to="/register" variant="body2">
                {"Don't have an account? Sign Up"}
              </Link>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login;
````

## File: frontend/src/pages/Memories.js
````javascript
import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  InputAdornment,
  Snackbar,
  Alert,
  Tooltip,
  Menu,
  MenuItem,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import FilterListIcon from '@mui/icons-material/FilterList';
import SortIcon from '@mui/icons-material/Sort';
import { format } from 'date-fns';
import axios from '../utils/axiosConfig';
import { useAuth } from '../context/AuthContext';

const Memories = () => {
  const [memories, setMemories] = useState([]);
  const [filteredMemories, setFilteredMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingMemory, setEditingMemory] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    tags: ''
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  const [anchorElFilter, setAnchorElFilter] = useState(null);
  const [anchorElSort, setAnchorElSort] = useState(null);
  const [selectedTags, setSelectedTags] = useState([]);
  const [sortOption, setSortOption] = useState('newest');
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [activeMemoryId, setActiveMemoryId] = useState(null);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user } = useAuth();
  
  // Fetch memories on component mount
  useEffect(() => {
    fetchMemories();
  }, []);
  
  // Filter memories when search query or selected tags change
  useEffect(() => {
    filterMemories();
  }, [memories, searchQuery, selectedTags, sortOption]);
  
  const fetchMemories = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/memories');
      setMemories(response.data);
    } catch (err) {
      console.error('Error fetching memories:', err);
      setSnackbar({
        open: true,
        message: 'Failed to load memories. Please try again later.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const filterMemories = () => {
    let filtered = [...memories];
    
    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(memory => 
        memory.title.toLowerCase().includes(query) || 
        memory.content.toLowerCase().includes(query) ||
        memory.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }
    
    // Filter by selected tags
    if (selectedTags.length > 0) {
      filtered = filtered.filter(memory => 
        selectedTags.every(tag => memory.tags.includes(tag))
      );
    }
    
    // Sort memories
    switch (sortOption) {
      case 'newest':
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        break;
      case 'alphabetical':
        filtered.sort((a, b) => a.title.localeCompare(b.title));
        break;
      case 'favorite':
        filtered.sort((a, b) => (b.is_favorite ? 1 : 0) - (a.is_favorite ? 1 : 0));
        break;
      default:
        break;
    }
    
    setFilteredMemories(filtered);
  };
  
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };
  
  const handleOpenDialog = (memory = null) => {
    if (memory) {
      // Edit existing memory
      setEditingMemory(memory);
      setFormData({
        title: memory.title,
        content: memory.content,
        tags: memory.tags.join(', ')
      });
    } else {
      // Create new memory
      setEditingMemory(null);
      setFormData({
        title: '',
        content: '',
        tags: ''
      });
    }
    setOpenDialog(true);
  };
  
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingMemory(null);
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  
  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const tags = formData.tags
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
      
      const memoryData = {
        title: formData.title,
        content: formData.content,
        tags
      };
      
      if (editingMemory) {
        // Update existing memory
        await axios.put(`/api/memories/${editingMemory._id}`, memoryData);
        
        // Update local state
        setMemories(memories.map(memory => 
          memory._id === editingMemory._id 
            ? { ...memory, ...memoryData } 
            : memory
        ));
        
        setSnackbar({
          open: true,
          message: 'Memory updated successfully!',
          severity: 'success'
        });
      } else {
        // Create new memory
        const response = await axios.post('/api/memories', memoryData);
        
        // Update local state
        setMemories([...memories, response.data]);
        
        setSnackbar({
          open: true,
          message: 'Memory created successfully!',
          severity: 'success'
        });
      }
      
      handleCloseDialog();
    } catch (err) {
      console.error('Error saving memory:', err);
      setSnackbar({
        open: true,
        message: 'Failed to save memory. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleDeleteMemory = async (memoryId) => {
    if (!window.confirm('Are you sure you want to delete this memory?')) {
      return;
    }
    
    try {
      setLoading(true);
      await axios.delete(`/api/memories/${memoryId}`);
      
      // Update local state
      setMemories(memories.filter(memory => memory._id !== memoryId));
      
      setSnackbar({
        open: true,
        message: 'Memory deleted successfully!',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error deleting memory:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete memory. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleToggleFavorite = async (memory) => {
    try {
      const updatedMemory = { ...memory, is_favorite: !memory.is_favorite };
      
      await axios.put(`/api/memories/${memory._id}/favorite`, {
        is_favorite: updatedMemory.is_favorite
      });
      
      // Update local state
      setMemories(memories.map(m => 
        m._id === memory._id ? updatedMemory : m
      ));
      
      setSnackbar({
        open: true,
        message: updatedMemory.is_favorite 
          ? 'Added to favorites!' 
          : 'Removed from favorites!',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error updating favorite status:', err);
      setSnackbar({
        open: true,
        message: 'Failed to update favorite status. Please try again.',
        severity: 'error'
      });
    }
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };
  
  const handleOpenFilterMenu = (event) => {
    setAnchorElFilter(event.currentTarget);
  };
  
  const handleCloseFilterMenu = () => {
    setAnchorElFilter(null);
  };
  
  const handleOpenSortMenu = (event) => {
    setAnchorElSort(event.currentTarget);
  };
  
  const handleCloseSortMenu = () => {
    setAnchorElSort(null);
  };
  
  const handleTagSelect = (tag) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };
  
  const handleSortSelect = (option) => {
    setSortOption(option);
    handleCloseSortMenu();
  };
  
  const handleOpenMenu = (event, memoryId) => {
    setMenuAnchorEl(event.currentTarget);
    setActiveMemoryId(memoryId);
  };
  
  const handleCloseMenu = () => {
    setMenuAnchorEl(null);
    setActiveMemoryId(null);
  };
  
  // Get all unique tags from memories
  const getAllTags = () => {
    const tagSet = new Set();
    memories.forEach(memory => {
      memory.tags.forEach(tag => tagSet.add(tag));
    });
    return Array.from(tagSet);
  };
  
  const allTags = getAllTags();
  
  const formatDate = (dateString) => {
    return format(new Date(dateString), 'MMM d, yyyy');
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
        <Typography variant="h4" component="h1" sx={{ mb: { xs: 2, sm: 0 } }}>
          Your Memories
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Memory
        </Button>
      </Box>
      
      {/* Search and Filter Bar */}
      <Paper 
        elevation={2} 
        sx={{ 
          p: 2, 
          mb: 4, 
          display: 'flex', 
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2
        }}
      >
        <TextField
          placeholder="Search memories..."
          variant="outlined"
          size="small"
          fullWidth={isMobile}
          sx={{ flexGrow: 1, maxWidth: { sm: '50%' } }}
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            )
          }}
        />
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<FilterListIcon />}
            onClick={handleOpenFilterMenu}
            color={selectedTags.length > 0 ? "primary" : "inherit"}
          >
            {selectedTags.length > 0 ? `Filters (${selectedTags.length})` : "Filter"}
          </Button>
          
          <Button
            variant="outlined"
            size="small"
            startIcon={<SortIcon />}
            onClick={handleOpenSortMenu}
          >
            Sort
          </Button>
        </Box>
        
        {/* Filter Menu */}
        <Menu
          anchorEl={anchorElFilter}
          open={Boolean(anchorElFilter)}
          onClose={handleCloseFilterMenu}
          PaperProps={{
            style: {
              maxHeight: 300,
              width: 250
            }
          }}
        >
          <MenuItem disabled>
            <Typography variant="subtitle2">Filter by Tags</Typography>
          </MenuItem>
          <Divider />
          {allTags.length === 0 ? (
            <MenuItem disabled>
              <Typography variant="body2">No tags available</Typography>
            </MenuItem>
          ) : (
            allTags.map(tag => (
              <MenuItem 
                key={tag} 
                onClick={() => handleTagSelect(tag)}
                selected={selectedTags.includes(tag)}
              >
                {tag}
              </MenuItem>
            ))
          )}
          {selectedTags.length > 0 && (
            <>
              <Divider />
              <MenuItem onClick={() => setSelectedTags([])}>
                <Typography color="error">Clear Filters</Typography>
              </MenuItem>
            </>
          )}
        </Menu>
        
        {/* Sort Menu */}
        <Menu
          anchorEl={anchorElSort}
          open={Boolean(anchorElSort)}
          onClose={handleCloseSortMenu}
        >
          <MenuItem 
            onClick={() => handleSortSelect('newest')}
            selected={sortOption === 'newest'}
          >
            Newest First
          </MenuItem>
          <MenuItem 
            onClick={() => handleSortSelect('oldest')}
            selected={sortOption === 'oldest'}
          >
            Oldest First
          </MenuItem>
          <MenuItem 
            onClick={() => handleSortSelect('alphabetical')}
            selected={sortOption === 'alphabetical'}
          >
            Alphabetical
          </MenuItem>
          <MenuItem 
            onClick={() => handleSortSelect('favorite')}
            selected={sortOption === 'favorite'}
          >
            Favorites First
          </MenuItem>
        </Menu>
      </Paper>
      
      {/* Selected Filters */}
      {selectedTags.length > 0 && (
        <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {selectedTags.map(tag => (
            <Chip
              key={tag}
              label={tag}
              onDelete={() => handleTagSelect(tag)}
              color="primary"
              variant="outlined"
              size="small"
            />
          ))}
          <Chip
            label="Clear All"
            onClick={() => setSelectedTags([])}
            color="error"
            size="small"
          />
        </Box>
      )}
      
      {/* Memories Grid */}
      {loading && memories.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : filteredMemories.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          {memories.length === 0 ? (
            <>
              <Typography variant="h6" gutterBottom>
                You don't have any memories yet
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Start creating memories to preserve your important moments
              </Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={() => handleOpenDialog()}
              >
                Create Your First Memory
              </Button>
            </>
          ) : (
            <>
              <Typography variant="h6" gutterBottom>
                No memories match your search
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Try adjusting your search terms or filters
              </Typography>
              <Button
                variant="outlined"
                onClick={() => {
                  setSearchQuery('');
                  setSelectedTags([]);
                }}
              >
                Clear Search & Filters
              </Button>
            </>
          )}
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredMemories.map(memory => (
            <Grid item xs={12} sm={6} md={4} key={memory._id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  position: 'relative',
                  transition: 'transform 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                  }
                }}
              >
                {memory.is_favorite && (
                  <Box 
                    sx={{ 
                      position: 'absolute', 
                      top: 8, 
                      right: 8, 
                      zIndex: 1,
                      bgcolor: 'error.main',
                      color: 'white',
                      borderRadius: '50%',
                      width: 32,
                      height: 32,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <FavoriteIcon fontSize="small" />
                  </Box>
                )}
                
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography variant="h6" component="h3" gutterBottom>
                      {memory.title}
                    </Typography>
                    <IconButton 
                      size="small" 
                      onClick={(e) => handleOpenMenu(e, memory._id)}
                      aria-label="memory options"
                    >
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {formatDate(memory.created_at)}
                  </Typography>
                  
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      mb: 2,
                      display: '-webkit-box',
                      WebkitLineClamp: 4,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    }}
                  >
                    {memory.content}
                  </Typography>
                  
                  {memory.tags.length > 0 && (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 'auto' }}>
                      {memory.tags.map(tag => (
                        <Chip 
                          key={tag} 
                          label={tag} 
                          size="small" 
                          onClick={() => {
                            if (!selectedTags.includes(tag)) {
                              setSelectedTags([...selectedTags, tag]);
                            }
                          }}
                          sx={{ cursor: 'pointer' }}
                        />
                      ))}
                    </Box>
                  )}
                </CardContent>
                
                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={memory.is_favorite ? <FavoriteIcon /> : <FavoriteBorderIcon />}
                    onClick={() => handleToggleFavorite(memory)}
                    color={memory.is_favorite ? "error" : "default"}
                  >
                    {memory.is_favorite ? "Favorited" : "Favorite"}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Memory Options Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleCloseMenu}
      >
        <MenuItem 
          onClick={() => {
            const memory = memories.find(m => m._id === activeMemoryId);
            handleOpenDialog(memory);
            handleCloseMenu();
          }}
        >
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem 
          onClick={() => {
            handleDeleteMemory(activeMemoryId);
            handleCloseMenu();
          }}
          sx={{ color: 'error.main' }}
        >
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
      
      {/* Create/Edit Memory Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingMemory ? 'Edit Memory' : 'Create New Memory'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Memory Title"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.title}
            onChange={handleInputChange}
            required
            sx={{ mb: 2, mt: 1 }}
          />
          
          <TextField
            margin="dense"
            name="content"
            label="Memory Content"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.content}
            onChange={handleInputChange}
            multiline
            rows={6}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            name="tags"
            label="Tags (comma separated)"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.tags}
            onChange={handleInputChange}
            helperText="Example: personal, important, work"
            sx={{ mb: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={!formData.title.trim() || !formData.content.trim() || loading}
          >
            {loading ? <CircularProgress size={24} /> : editingMemory ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Memories;
````

## File: frontend/src/pages/NotFound.js
````javascript
import React from 'react';
import { Box, Container, Typography, Button, Paper } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';

const NotFound = () => {
  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Paper 
        elevation={3} 
        sx={{ 
          p: 5, 
          textAlign: 'center',
          borderRadius: 2
        }}
      >
        <SentimentDissatisfiedIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
        
        <Typography variant="h3" component="h1" gutterBottom>
          404 - Page Not Found
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph sx={{ mb: 4 }}>
          The page you are looking for doesn't exist or has been moved.
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button 
            variant="contained" 
            component={RouterLink} 
            to="/"
            size="large"
          >
            Go to Home
          </Button>
          
          <Button 
            variant="outlined" 
            component={RouterLink} 
            to="/journal"
            size="large"
          >
            Go to Journal
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NotFound;
````

## File: frontend/src/pages/Register.js
````javascript
import React, { useState } from 'react';
import { Link as RouterLink, Navigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Link,
  Paper,
  Grid,
  Alert,
  IconButton,
  InputAdornment,
  CircularProgress,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const steps = ['Account Details', 'Personal Information'];

const Register = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    bio: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState({});
  
  const { register, isAuthenticated, loading, error, clearError } = useAuth();

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/journal" />;
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    
    // Clear field error when user types
    if (formErrors[name]) {
      setFormErrors({ ...formErrors, [name]: '' });
    }
    
    // Clear API error when user makes changes
    if (error) {
      clearError();
    }
  };

  const validateStep = (step) => {
    const errors = {};
    
    if (step === 0) {
      if (!formData.email) {
        errors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        errors.email = 'Email is invalid';
      }
      
      if (!formData.password) {
        errors.password = 'Password is required';
      } else if (formData.password.length < 8) {
        errors.password = 'Password must be at least 8 characters';
      }
      
      if (!formData.confirmPassword) {
        errors.confirmPassword = 'Please confirm your password';
      } else if (formData.password !== formData.confirmPassword) {
        errors.confirmPassword = 'Passwords do not match';
      }
    } else if (step === 1) {
      if (!formData.name) {
        errors.name = 'Name is required';
      }
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (validateStep(activeStep)) {
      await register(formData);
    }
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={formData.email}
              onChange={handleChange}
              error={!!formErrors.email}
              helperText={formErrors.email}
              disabled={loading}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="new-password"
              value={formData.password}
              onChange={handleChange}
              error={!!formErrors.password}
              helperText={formErrors.password}
              disabled={loading}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleClickShowPassword}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="Confirm Password"
              type={showPassword ? 'text' : 'password'}
              id="confirmPassword"
              autoComplete="new-password"
              value={formData.confirmPassword}
              onChange={handleChange}
              error={!!formErrors.confirmPassword}
              helperText={formErrors.confirmPassword}
              disabled={loading}
            />
          </>
        );
      case 1:
        return (
          <>
            <TextField
              margin="normal"
              required
              fullWidth
              id="name"
              label="Full Name"
              name="name"
              autoComplete="name"
              value={formData.name}
              onChange={handleChange}
              error={!!formErrors.name}
              helperText={formErrors.name}
              disabled={loading}
            />
            
            <TextField
              margin="normal"
              fullWidth
              id="bio"
              label="Bio (Optional)"
              name="bio"
              multiline
              rows={4}
              value={formData.bio}
              onChange={handleChange}
              disabled={loading}
            />
          </>
        );
      default:
        return null;
    }
  };

  return (
    <Container component="main" maxWidth="sm" sx={{ py: 8 }}>
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          borderRadius: 2
        }}
      >
        <Typography component="h1" variant="h4" sx={{ mb: 3 }}>
          Create Account
        </Typography>
        
        <Stepper activeStep={activeStep} sx={{ width: '100%', mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
          {renderStepContent(activeStep)}
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
            <Button
              disabled={activeStep === 0 || loading}
              onClick={handleBack}
              variant="outlined"
            >
              Back
            </Button>
            
            {activeStep === steps.length - 1 ? (
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Create Account'}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={loading}
              >
                Next
              </Button>
            )}
          </Box>
          
          <Grid container justifyContent="center" sx={{ mt: 3 }}>
            <Grid item>
              <Link component={RouterLink} to="/login" variant="body2">
                {"Already have an account? Sign In"}
              </Link>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default Register;
````

## File: frontend/src/utils/axiosConfig.js
````javascript
import axios from 'axios';

// Configure axios to use our backend API running on port 5002
axios.defaults.baseURL = 'http://localhost:5002';

export default axios;
````

## File: spark/jobs/dataset_import.py
````python
"""
Dataset Import Spark Job for Reflectly
Imports and processes IEMOCAP and mental health datasets
"""
import sys
import json
import argparse
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, regexp_replace, lower, trim
from pyspark.sql.types import StringType, StructType, StructField, FloatType, ArrayType, BooleanType
import pyspark.sql.functions as F

def create_spark_session(app_name="reflectly-dataset-import"):
    """
    Create a Spark session
    
    Args:
        app_name (str): Application name
        
    Returns:
        SparkSession: Spark session
    """
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()

def process_iemocap_dataset(spark, input_path, output_path):
    """
    Process IEMOCAP dataset
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path to IEMOCAP dataset
        output_path (str): Output path in HDFS
        
    Returns:
        int: Number of processed records
    """
    # Check if input path exists
    if not os.path.exists(input_path):
        print(f"IEMOCAP dataset not found at {input_path}")
        return 0
        
    print(f"Processing IEMOCAP dataset from {input_path}")
    
    # Define schema for IEMOCAP dataset
    # This is a simplified schema and would need to be adjusted based on the actual dataset structure
    iemocap_schema = StructType([
        StructField("utterance", StringType(), True),
        StructField("emotion", StringType(), True),
        StructField("valence", FloatType(), True),
        StructField("activation", FloatType(), True),
        StructField("dominance", FloatType(), True)
    ])
    
    try:
        # Read IEMOCAP dataset
        # The actual file format and structure would depend on the dataset
        iemocap_df = spark.read.csv(input_path, header=True, schema=iemocap_schema)
        
        # Clean and preprocess data
        cleaned_df = iemocap_df.withColumn("utterance", trim(lower(col("utterance"))))
        
        # Map emotions to our standard set
        emotion_mapping = {
            "happiness": "joy",
            "excited": "joy",
            "sadness": "sadness",
            "anger": "anger",
            "frustrated": "anger",
            "fear": "fear",
            "disgust": "disgust",
            "neutral": "neutral",
            "surprise": "joy"  # Mapping surprise to joy as a simplification
        }
        
        # Apply emotion mapping
        for original, mapped in emotion_mapping.items():
            cleaned_df = cleaned_df.withColumn(
                "emotion",
                F.when(F.lower(col("emotion")) == original, mapped).otherwise(col("emotion"))
            )
        
        # Extract insights for each emotion
        emotions = ["joy", "sadness", "anger", "fear", "disgust", "neutral"]
        
        for emotion in emotions:
            # Filter by emotion
            emotion_df = cleaned_df.filter(col("emotion") == emotion)
            
            # Calculate average valence, activation, and dominance
            avg_metrics = emotion_df.agg(
                F.avg("valence").alias("avg_valence"),
                F.avg("activation").alias("avg_activation"),
                F.avg("dominance").alias("avg_dominance")
            ).collect()[0]
            
            # Create insights DataFrame
            insights = {
                "emotion": emotion,
                "dataset": "IEMOCAP",
                "metrics": {
                    "avg_valence": float(avg_metrics["avg_valence"]) if avg_metrics["avg_valence"] else 0.0,
                    "avg_activation": float(avg_metrics["avg_activation"]) if avg_metrics["avg_activation"] else 0.0,
                    "avg_dominance": float(avg_metrics["avg_dominance"]) if avg_metrics["avg_dominance"] else 0.0
                },
                "common_utterances": [row["utterance"] for row in 
                                     emotion_df.orderBy(F.length("utterance").desc())
                                     .limit(10).select("utterance").collect()]
            }
            
            # Write insights to HDFS
            insights_df = spark.createDataFrame([insights])
            insights_df.write.mode("overwrite").json(f"{output_path}/{emotion}")
        
        return cleaned_df.count()
    except Exception as e:
        print(f"Error processing IEMOCAP dataset: {e}")
        return 0

def process_mental_health_dataset(spark, input_path, output_path):
    """
    Process mental health dataset
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path to mental health dataset
        output_path (str): Output path in HDFS
        
    Returns:
        int: Number of processed records
    """
    # Check if input path exists
    if not os.path.exists(input_path):
        print(f"Mental health dataset not found at {input_path}")
        return 0
        
    print(f"Processing mental health dataset from {input_path}")
    
    # Define schema for mental health dataset
    # This is a simplified schema and would need to be adjusted based on the actual dataset structure
    mental_health_schema = StructType([
        StructField("text", StringType(), True),
        StructField("emotion", StringType(), True),
        StructField("intervention", StringType(), True),
        StructField("effectiveness", FloatType(), True)
    ])
    
    try:
        # Read mental health dataset
        # The actual file format and structure would depend on the dataset
        mental_health_df = spark.read.csv(input_path, header=True, schema=mental_health_schema)
        
        # Clean and preprocess data
        cleaned_df = mental_health_df.withColumn("text", trim(lower(col("text"))))
        
        # Map emotions to our standard set
        emotion_mapping = {
            "happiness": "joy",
            "excited": "joy",
            "sadness": "sadness",
            "depression": "sadness",
            "anger": "anger",
            "frustrated": "anger",
            "anxiety": "fear",
            "fear": "fear",
            "disgust": "disgust",
            "neutral": "neutral",
            "surprise": "joy"  # Mapping surprise to joy as a simplification
        }
        
        # Apply emotion mapping
        for original, mapped in emotion_mapping.items():
            cleaned_df = cleaned_df.withColumn(
                "emotion",
                F.when(F.lower(col("emotion")) == original, mapped).otherwise(col("emotion"))
            )
        
        # Extract insights for each emotion
        emotions = ["joy", "sadness", "anger", "fear", "disgust", "neutral"]
        
        for emotion in emotions:
            # Filter by emotion
            emotion_df = cleaned_df.filter(col("emotion") == emotion)
            
            # Group interventions by effectiveness
            interventions_df = emotion_df.groupBy("intervention") \
                .agg(F.avg("effectiveness").alias("avg_effectiveness")) \
                .orderBy(col("avg_effectiveness").desc())
            
            # Get top interventions
            top_interventions = [
                {
                    "intervention": row["intervention"],
                    "effectiveness": float(row["avg_effectiveness"])
                }
                for row in interventions_df.limit(5).collect()
            ]
            
            # Create insights DataFrame
            insights = {
                "emotion": emotion,
                "dataset": "mental_health",
                "effective_interventions": top_interventions,
                "common_texts": [row["text"] for row in 
                               emotion_df.orderBy(F.length("text").desc())
                               .limit(10).select("text").collect()]
            }
            
            # Write insights to HDFS
            insights_df = spark.createDataFrame([insights])
            insights_df.write.mode("overwrite").json(f"{output_path}/{emotion}")
        
        return cleaned_df.count()
    except Exception as e:
        print(f"Error processing mental health dataset: {e}")
        return 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Dataset Import Spark Job")
    parser.add_argument("--iemocap", required=False, help="Input path to IEMOCAP dataset")
    parser.add_argument("--mental-health", required=False, help="Input path to mental health dataset")
    parser.add_argument("--output", required=True, help="Output path in HDFS")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        total_count = 0
        
        # Process IEMOCAP dataset if provided
        if args.iemocap:
            iemocap_count = process_iemocap_dataset(spark, args.iemocap, f"{args.output}/iemocap")
            print(f"Processed {iemocap_count} records from IEMOCAP dataset")
            total_count += iemocap_count
        
        # Process mental health dataset if provided
        if args.mental_health:
            mental_health_count = process_mental_health_dataset(spark, args.mental_health, f"{args.output}/mental_health")
            print(f"Processed {mental_health_count} records from mental health dataset")
            total_count += mental_health_count
        
        print(f"Total processed records: {total_count}")
    finally:
        # Stop Spark session
        spark.stop()

if __name__ == "__main__":
    main()
````

## File: spark/jobs/emotion_analysis.py
````python
"""
Emotion Analysis Spark Job for Reflectly
Analyzes emotions from journal entries using distributed processing
"""
import sys
import json
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, explode
from pyspark.sql.types import StringType, StructType, StructField, FloatType, ArrayType, BooleanType
import pyspark.sql.functions as F

def create_spark_session(app_name="reflectly-emotion-analysis"):
    """
    Create a Spark session
    
    Args:
        app_name (str): Application name
        
    Returns:
        SparkSession: Spark session
    """
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()

def analyze_emotion(text):
    """
    Analyze emotion from text
    This is a simplified version that would be replaced with a more sophisticated model
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Emotion analysis result
    """
    # This is a placeholder for the actual emotion analysis
    # In a real implementation, this would use a pre-trained model
    
    # Simple keyword-based analysis for demonstration
    joy_keywords = ["happy", "joy", "excited", "great", "wonderful", "love", "pleased", "delighted"]
    sadness_keywords = ["sad", "unhappy", "depressed", "miserable", "gloomy", "disappointed", "upset"]
    anger_keywords = ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "enraged"]
    fear_keywords = ["afraid", "scared", "fearful", "terrified", "anxious", "worried", "nervous"]
    disgust_keywords = ["disgusted", "revolted", "repulsed", "gross", "nauseous", "distasteful"]
    
    text_lower = text.lower()
    
    # Count occurrences of keywords
    joy_count = sum(1 for keyword in joy_keywords if keyword in text_lower)
    sadness_count = sum(1 for keyword in sadness_keywords if keyword in text_lower)
    anger_count = sum(1 for keyword in anger_keywords if keyword in text_lower)
    fear_count = sum(1 for keyword in fear_keywords if keyword in text_lower)
    disgust_count = sum(1 for keyword in disgust_keywords if keyword in text_lower)
    
    # Calculate total count
    total_count = joy_count + sadness_count + anger_count + fear_count + disgust_count
    
    # Calculate scores
    if total_count > 0:
        joy_score = joy_count / total_count
        sadness_score = sadness_count / total_count
        anger_score = anger_count / total_count
        fear_score = fear_count / total_count
        disgust_score = disgust_count / total_count
    else:
        # Default to neutral if no keywords found
        joy_score = 0.2
        sadness_score = 0.2
        anger_score = 0.2
        fear_score = 0.2
        disgust_score = 0.2
    
    # Determine primary emotion
    emotions = {
        "joy": joy_score,
        "sadness": sadness_score,
        "anger": anger_score,
        "fear": fear_score,
        "disgust": disgust_score
    }
    
    primary_emotion = max(emotions, key=emotions.get)
    is_positive = primary_emotion == "joy"
    
    return {
        "primary_emotion": primary_emotion,
        "is_positive": is_positive,
        "emotion_scores": {
            "joy": joy_score,
            "sadness": sadness_score,
            "anger": anger_score,
            "fear": fear_score,
            "disgust": disgust_score
        }
    }

def process_journal_entries(spark, input_path, output_path):
    """
    Process journal entries from HDFS
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path in HDFS
        output_path (str): Output path in HDFS
    """
    # Define schema for journal entries
    journal_schema = StructType([
        StructField("_id", StringType(), True),
        StructField("user_email", StringType(), True),
        StructField("content", StringType(), True),
        StructField("created_at", StringType(), True)
    ])
    
    # Read journal entries from HDFS
    journal_df = spark.read.json(input_path, schema=journal_schema)
    
    # Define UDF for emotion analysis
    emotion_analysis_udf = udf(analyze_emotion, 
        StructType([
            StructField("primary_emotion", StringType(), True),
            StructField("is_positive", BooleanType(), True),
            StructField("emotion_scores", 
                StructType([
                    StructField("joy", FloatType(), True),
                    StructField("sadness", FloatType(), True),
                    StructField("anger", FloatType(), True),
                    StructField("fear", FloatType(), True),
                    StructField("disgust", FloatType(), True)
                ]), True)
        ])
    )
    
    # Apply emotion analysis to journal entries
    result_df = journal_df.withColumn("emotion", emotion_analysis_udf(col("content")))
    
    # Write results to HDFS
    result_df.write.mode("overwrite").json(output_path)
    
    # Return count of processed entries
    return result_df.count()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Emotion Analysis Spark Job")
    parser.add_argument("--input", required=True, help="Input path in HDFS")
    parser.add_argument("--output", required=True, help="Output path in HDFS")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Process journal entries
        count = process_journal_entries(spark, args.input, args.output)
        print(f"Processed {count} journal entries")
    finally:
        # Stop Spark session
        spark.stop()

if __name__ == "__main__":
    main()
````

## File: spark/jobs/graph_processing.py
````python
"""
Graph Processing Spark Job for Reflectly
Processes emotional transitions and builds the emotional graph
"""
import sys
import json
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, collect_list, struct, lit
from pyspark.sql.types import StringType, StructType, StructField, FloatType, ArrayType, BooleanType
import pyspark.sql.functions as F

def create_spark_session(app_name="reflectly-graph-processing"):
    """
    Create a Spark session
    
    Args:
        app_name (str): Application name
        
    Returns:
        SparkSession: Spark session
    """
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()

def process_emotional_states(spark, input_path, output_path):
    """
    Process emotional states and build the emotional graph
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path in HDFS (emotional states)
        output_path (str): Output path in HDFS (emotional transitions)
    """
    # Define schema for emotional states
    emotional_state_schema = StructType([
        StructField("_id", StringType(), True),
        StructField("user_email", StringType(), True),
        StructField("primary_emotion", StringType(), True),
        StructField("is_positive", BooleanType(), True),
        StructField("emotion_scores", 
            StructType([
                StructField("joy", FloatType(), True),
                StructField("sadness", FloatType(), True),
                StructField("anger", FloatType(), True),
                StructField("fear", FloatType(), True),
                StructField("disgust", FloatType(), True)
            ]), True),
        StructField("entry_id", StringType(), True),
        StructField("timestamp", StringType(), True)
    ])
    
    # Read emotional states from HDFS
    emotional_states_df = spark.read.json(input_path, schema=emotional_state_schema)
    
    # Register the DataFrame as a temporary view
    emotional_states_df.createOrReplaceTempView("emotional_states")
    
    # Find transitions between emotional states
    transitions_df = spark.sql("""
        SELECT 
            a.user_email,
            a.primary_emotion as from_emotion,
            b.primary_emotion as to_emotion,
            a._id as from_state_id,
            b._id as to_state_id,
            a.timestamp as from_timestamp,
            b.timestamp as to_timestamp
        FROM 
            emotional_states a
        JOIN 
            emotional_states b
        ON 
            a.user_email = b.user_email AND
            a.timestamp < b.timestamp
        WHERE 
            NOT EXISTS (
                SELECT 1 
                FROM emotional_states c 
                WHERE 
                    c.user_email = a.user_email AND
                    c.timestamp > a.timestamp AND
                    c.timestamp < b.timestamp
            )
    """)
    
    # Add default actions based on emotion transitions
    transitions_with_actions_df = transitions_df.withColumn(
        "actions",
        F.array(
            F.struct(
                F.lit("Practice mindfulness").alias("description"),
                F.lit(0.7).alias("success_rate")
            ),
            F.struct(
                F.lit("Engage in physical activity").alias("description"),
                F.lit(0.6).alias("success_rate")
            )
        )
    )
    
    # Write transitions to HDFS
    transitions_with_actions_df.write.mode("overwrite").json(output_path)
    
    # Return count of processed transitions
    return transitions_with_actions_df.count()

def analyze_transition_patterns(spark, transitions_path, patterns_output_path):
    """
    Analyze patterns in emotional transitions
    
    Args:
        spark (SparkSession): Spark session
        transitions_path (str): Path to emotional transitions in HDFS
        patterns_output_path (str): Output path for patterns in HDFS
    """
    # Read transitions from HDFS
    transitions_df = spark.read.json(transitions_path)
    
    # Register the DataFrame as a temporary view
    transitions_df.createOrReplaceTempView("transitions")
    
    # Analyze transition frequencies
    transition_frequencies_df = spark.sql("""
        SELECT 
            user_email,
            from_emotion,
            to_emotion,
            COUNT(*) as frequency
        FROM 
            transitions
        GROUP BY 
            user_email, from_emotion, to_emotion
        ORDER BY 
            user_email, frequency DESC
    """)
    
    # Analyze common paths
    common_paths_df = spark.sql("""
        SELECT 
            t1.user_email,
            t1.from_emotion as start_emotion,
            t1.to_emotion as middle_emotion,
            t2.to_emotion as end_emotion,
            COUNT(*) as frequency
        FROM 
            transitions t1
        JOIN 
            transitions t2
        ON 
            t1.user_email = t2.user_email AND
            t1.to_emotion = t2.from_emotion AND
            t1.to_timestamp < t2.from_timestamp
        GROUP BY 
            t1.user_email, start_emotion, middle_emotion, end_emotion
        ORDER BY 
            t1.user_email, frequency DESC
    """)
    
    # Combine results
    transition_frequencies_df.write.mode("overwrite").json(f"{patterns_output_path}/frequencies")
    common_paths_df.write.mode("overwrite").json(f"{patterns_output_path}/paths")
    
    return {
        "frequencies": transition_frequencies_df.count(),
        "paths": common_paths_df.count()
    }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Graph Processing Spark Job")
    parser.add_argument("--input", required=True, help="Input path in HDFS (emotional states)")
    parser.add_argument("--output", required=True, help="Output path in HDFS (emotional transitions)")
    parser.add_argument("--patterns", required=False, help="Output path for patterns in HDFS")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Process emotional states
        count = process_emotional_states(spark, args.input, args.output)
        print(f"Processed {count} emotional transitions")
        
        # Analyze transition patterns if patterns output path is provided
        if args.patterns:
            pattern_counts = analyze_transition_patterns(spark, args.output, args.patterns)
            print(f"Analyzed {pattern_counts['frequencies']} transition frequencies and {pattern_counts['paths']} common paths")
    finally:
        # Stop Spark session
        spark.stop()

if __name__ == "__main__":
    main()
````

## File: spark/jobs/path_finding.py
````python
"""
Path Finding Spark Job for Reflectly
Finds optimal emotional paths using A* search algorithm
"""
import sys
import json
import argparse
import heapq
from collections import defaultdict
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, collect_list, struct, lit
import pyspark.sql.functions as F

def create_spark_session(app_name="reflectly-path-finding"):
    """
    Create a Spark session
    
    Args:
        app_name (str): Application name
        
    Returns:
        SparkSession: Spark session
    """
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()

def heuristic(current_emotion, target_emotion, successful_transitions=None):
    """
    Heuristic function for A* search
    Estimates the cost to reach the target emotion from the current emotion
    
    Args:
        current_emotion (str): Current emotion
        target_emotion (str): Target emotion
        successful_transitions (dict): Dictionary of successful transitions
            
    Returns:
        float: Estimated cost
    """
    # Define base costs between emotion categories
    # Lower cost means emotions are closer/easier to transition between
    base_costs = {
        ('joy', 'joy'): 0.1,
        ('joy', 'neutral'): 0.5,
        ('joy', 'sadness'): 1.5,
        ('joy', 'anger'): 1.8,
        ('joy', 'fear'): 1.7,
        ('joy', 'disgust'): 1.6,
        
        ('neutral', 'joy'): 0.7,
        ('neutral', 'neutral'): 0.1,
        ('neutral', 'sadness'): 0.9,
        ('neutral', 'anger'): 1.2,
        ('neutral', 'fear'): 1.1,
        ('neutral', 'disgust'): 1.0,
        
        ('sadness', 'joy'): 2.0,
        ('sadness', 'neutral'): 1.0,
        ('sadness', 'sadness'): 0.1,
        ('sadness', 'anger'): 1.3,
        ('sadness', 'fear'): 1.2,
        ('sadness', 'disgust'): 1.1,
        
        ('anger', 'joy'): 2.2,
        ('anger', 'neutral'): 1.3,
        ('anger', 'sadness'): 1.2,
        ('anger', 'anger'): 0.1,
        ('anger', 'fear'): 0.9,
        ('anger', 'disgust'): 0.8,
        
        ('fear', 'joy'): 2.1,
        ('fear', 'neutral'): 1.2,
        ('fear', 'sadness'): 1.1,
        ('fear', 'anger'): 1.0,
        ('fear', 'fear'): 0.1,
        ('fear', 'disgust'): 0.9,
        
        ('disgust', 'joy'): 2.0,
        ('disgust', 'neutral'): 1.1,
        ('disgust', 'sadness'): 1.0,
        ('disgust', 'anger'): 0.9,
        ('disgust', 'fear'): 0.8,
        ('disgust', 'disgust'): 0.1,
    }
    
    # Get the base cost
    emotion_pair = (current_emotion, target_emotion)
    base_cost = base_costs.get(emotion_pair, 1.5)  # Default cost if pair not found
    
    # If successful_transitions is provided, adjust cost based on user's historical transitions
    if successful_transitions:
        # Check if this transition has been successful for the user before
        transition_key = f"{current_emotion}_{target_emotion}"
        if transition_key in successful_transitions:
            # Reduce cost based on success rate
            success_rate = successful_transitions[transition_key].get('success_rate', 0.5)
            adjusted_cost = base_cost * (1 - (success_rate * 0.5))  # Reduce cost by up to 50% based on success rate
            return max(0.1, adjusted_cost)  # Ensure cost is at least 0.1
    
    return base_cost

def get_default_action(from_emotion, to_emotion):
    """
    Get default action for a transition
    
    Args:
        from_emotion (str): Source emotion
        to_emotion (str): Target emotion
        
    Returns:
        str: Default action
    """
    # Define default actions for transitions
    default_actions = {
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
    }
    
    # Get default action
    emotion_pair = (from_emotion, to_emotion)
    default_action = default_actions.get(emotion_pair)
    
    # If no default action found, use generic action
    if not default_action:
        if to_emotion == "joy":
            default_action = "Focus on positive aspects of your life"
        elif to_emotion == "neutral":
            default_action = "Practice mindfulness and stay present"
        elif to_emotion == "sadness":
            default_action = "Allow yourself to process emotions"
        elif to_emotion == "anger":
            default_action = "Express feelings constructively"
        elif to_emotion == "fear":
            default_action = "Identify and address specific concerns"
        elif to_emotion == "disgust":
            default_action = "Examine your values and boundaries"
        else:
            default_action = "Reflect on your feelings"
            
    return default_action

def get_default_success_rate(from_emotion, to_emotion):
    """
    Get default success rate for a transition
    
    Args:
        from_emotion (str): Source emotion
        to_emotion (str): Target emotion
        
    Returns:
        float: Default success rate
    """
    # Define default success rates for transitions
    # Higher values indicate easier transitions
    default_success_rates = {
        ('sadness', 'joy'): 0.4,
        ('sadness', 'neutral'): 0.6,
        ('sadness', 'anger'): 0.5,
        ('sadness', 'fear'): 0.5,
        ('sadness', 'disgust'): 0.4,
        
        ('anger', 'joy'): 0.3,
        ('anger', 'neutral'): 0.5,
        ('anger', 'sadness'): 0.5,
        ('anger', 'fear'): 0.6,
        ('anger', 'disgust'): 0.6,
        
        ('fear', 'joy'): 0.3,
        ('fear', 'neutral'): 0.5,
        ('fear', 'sadness'): 0.6,
        ('fear', 'anger'): 0.6,
        ('fear', 'disgust'): 0.5,
        
        ('disgust', 'joy'): 0.3,
        ('disgust', 'neutral'): 0.5,
        ('disgust', 'sadness'): 0.6,
        ('disgust', 'anger'): 0.7,
        ('disgust', 'fear'): 0.6,
        
        ('neutral', 'joy'): 0.7,
        ('neutral', 'sadness'): 0.6,
        ('neutral', 'anger'): 0.5,
        ('neutral', 'fear'): 0.5,
        ('neutral', 'disgust'): 0.5,
        
        ('joy', 'neutral'): 0.8,
        ('joy', 'sadness'): 0.4,
        ('joy', 'anger'): 0.3,
        ('joy', 'fear'): 0.3,
        ('joy', 'disgust'): 0.3,
    }
    
    # Get default success rate
    emotion_pair = (from_emotion, to_emotion)
    default_success_rate = default_success_rates.get(emotion_pair, 0.5)  # Default to 0.5 if not found
    
    return default_success_rate

def get_successful_transitions(transitions):
    """
    Extract successful transitions from transition data
    
    Args:
        transitions (list): List of transition dictionaries
        
    Returns:
        dict: Dictionary of successful transitions
    """
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

def get_neighbors(transitions, emotion, available_emotions):
    """
    Get possible transitions from the current emotion
    
    Args:
        transitions (list): List of transition dictionaries
        emotion (str): Current emotion
        available_emotions (list): List of available emotions
        
    Returns:
        dict: Dictionary of neighbors with transition information
    """
    # Initialize neighbors
    neighbors = {}
    
    # Extract user's historical transitions
    user_transitions = []
    for transition in transitions:
        if transition.get("from_emotion") == emotion:
            user_transitions.append(transition)
    
    # Add transitions based on user history
    for transition in user_transitions:
        to_emotion = transition.get("to_emotion")
        
        # Skip self-transitions
        if to_emotion == emotion:
            continue
            
        # Get actions and success rates
        actions = []
        success_rates = []
        
        for action_info in transition.get("actions", []):
            if isinstance(action_info, dict):
                actions.append(action_info.get("description", ""))
                success_rates.append(action_info.get("success_rate", 0.5))
            
        # Calculate average success rate
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.5
        
        # Get most successful action
        if actions and success_rates:
            best_action_index = success_rates.index(max(success_rates))
            best_action = actions[best_action_index]
        else:
            best_action = get_default_action(emotion, to_emotion)
            
        # Calculate cost (inverse of success rate)
        cost = 1.0 / max(0.1, avg_success_rate)
        
        # Add to neighbors
        neighbors[to_emotion] = {
            "action": best_action,
            "success_rate": avg_success_rate,
            "cost": cost
        }
    
    # If no transitions found in user history, add default transitions
    if not neighbors:
        for to_emotion in available_emotions:
            # Skip self-transitions
            if to_emotion == emotion:
                continue
                
            # Add default transition
            action = get_default_action(emotion, to_emotion)
            success_rate = get_default_success_rate(emotion, to_emotion)
            cost = 1.0 / max(0.1, success_rate)
            
            neighbors[to_emotion] = {
                "action": action,
                "success_rate": success_rate,
                "cost": cost
            }
            
    return neighbors

def find_path(transitions, current_emotion, target_emotion, max_depth=10):
    """
    Find the optimal path from current_emotion to target_emotion using A* search
    
    Args:
        transitions (list): List of transition dictionaries
        current_emotion (str): Starting emotion
        target_emotion (str): Target emotion
        max_depth (int): Maximum path depth
        
    Returns:
        dict: Optimal path information
    """
    # Check if current and target emotions are the same
    if current_emotion == target_emotion:
        return {
            "current_emotion": current_emotion,
            "target_emotion": target_emotion,
            "path": [current_emotion],
            "actions": [],
            "total_cost": 0,
            "estimated_success_rate": 1.0
        }
        
    # Get available emotions
    available_emotions = ["joy", "sadness", "anger", "fear", "disgust", "neutral"]
        
    # Check if current and target emotions are valid
    if current_emotion not in available_emotions:
        current_emotion = "neutral"
        
    if target_emotion not in available_emotions:
        target_emotion = "joy"
        
    # Get successful transitions for heuristic function
    successful_transitions = get_successful_transitions(transitions)
    
    # Initialize data structures for A* search
    open_set = []  # Priority queue of nodes to explore
    closed_set = set()  # Set of explored nodes
    
    # For each node, g_score[node] is the cost of the cheapest path from start to node
    g_score = defaultdict(lambda: float('inf'))
    g_score[current_emotion] = 0
    
    # For each node, f_score[node] = g_score[node] + heuristic(node, goal)
    f_score = defaultdict(lambda: float('inf'))
    f_score[current_emotion] = heuristic(current_emotion, target_emotion, successful_transitions)
    
    # For each node, came_from[node] is the node immediately preceding it on the cheapest path
    came_from = {}
    
    # For each node, actions[node] is the action to take to get from came_from[node] to node
    actions = {}
    
    # Add start node to open set
    heapq.heappush(open_set, (f_score[current_emotion], current_emotion, 0))  # (f_score, node, depth)
    
    while open_set:
        # Get node with lowest f_score
        _, current, depth = heapq.heappop(open_set)
        
        # Check if we've reached the target
        if current == target_emotion:
            # Reconstruct path
            path = [current]
            path_actions = []
            node = current
            
            while node in came_from:
                prev_node = came_from[node]
                path.append(prev_node)
                
                # Add action to path_actions
                if node in actions and prev_node in actions[node]:
                    action_info = actions[node][prev_node]
                    path_actions.append({
                        "from": prev_node,
                        "to": node,
                        "action": action_info["action"],
                        "success_rate": action_info["success_rate"]
                    })
                    
                node = prev_node
                
            # Reverse path and actions
            path = path[::-1]
            path_actions = path_actions[::-1]
            
            # Calculate estimated success rate
            if path_actions:
                success_rates = [action["success_rate"] for action in path_actions]
                estimated_success_rate = 1.0
                for rate in success_rates:
                    estimated_success_rate *= rate
            else:
                estimated_success_rate = 0.8  # Default if no actions
                
            return {
                "current_emotion": current_emotion,
                "target_emotion": target_emotion,
                "path": path,
                "actions": path_actions,
                "total_cost": g_score[current],
                "estimated_success_rate": estimated_success_rate
            }
            
        # Add current node to closed set
        closed_set.add(current)
        
        # Check if we've reached maximum depth
        if depth >= max_depth:
            continue
            
        # Get neighbors (possible transitions)
        neighbors = get_neighbors(transitions, current, available_emotions)
        
        for neighbor, transition_info in neighbors.items():
            # Skip if neighbor is in closed set
            if neighbor in closed_set:
                continue
                
            # Calculate tentative g_score
            tentative_g_score = g_score[current] + transition_info["cost"]
            
            # Check if this path is better than any previous path
            if tentative_g_score < g_score[neighbor]:
                # Update path
                came_from[neighbor] = current
                
                # Update actions
                if neighbor not in actions:
                    actions[neighbor] = {}
                actions[neighbor][current] = {
                    "action": transition_info["action"],
                    "success_rate": transition_info["success_rate"]
                }
                
                # Update scores
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, target_emotion, successful_transitions)
                
                # Add to open set if not already there
                for i, (_, node, _) in enumerate(open_set):
                    if node == neighbor:
                        open_set[i] = (f_score[neighbor], neighbor, depth + 1)
                        heapq.heapify(open_set)
                        break
                else:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor, depth + 1))
                    
    # If we get here, no path was found
    
    # Return a default path through neutral
    if current_emotion != "neutral" and target_emotion != "neutral":
        # Try to go through neutral
        return {
            "current_emotion": current_emotion,
            "target_emotion": target_emotion,
            "path": [current_emotion, "neutral", target_emotion],
            "actions": [
                {
                    "from": current_emotion,
                    "to": "neutral",
                    "action": "Practice mindfulness",
                    "success_rate": 0.7
                },
                {
                    "from": "neutral",
                    "to": target_emotion,
                    "action": get_default_action("neutral", target_emotion),
                    "success_rate": 0.6
                }
            ],
            "total_cost": 3.0,
            "estimated_success_rate": 0.42  # 0.7 * 0.6
        }
    else:
        # Direct path
        return {
            "current_emotion": current_emotion,
            "target_emotion": target_emotion,
            "path": [current_emotion, target_emotion],
            "actions": [
                {
                    "from": current_emotion,
                    "to": target_emotion,
                    "action": get_default_action(current_emotion, target_emotion),
                    "success_rate": 0.5
                }
            ],
            "total_cost": 2.0,
            "estimated_success_rate": 0.5
        }

def process_path_finding(spark, input_path, output_path, user_email, current_emotion, target_emotion, max_depth):
    """
    Process path finding using Spark
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path to transitions in HDFS
        output_path (str): Output path for path result in HDFS
        user_email (str): User email
        current_emotion (str): Current emotion
        target_emotion (str): Target emotion
        max_depth (int): Maximum path depth
    """
    # Read transitions from HDFS
    transitions_df = spark.read.json(input_path)
    
    # Convert to list of dictionaries
    transitions = [row.asDict() for row in transitions_df.collect()]
    
    # Find path
    path_result = find_path(transitions, current_emotion, target_emotion, max_depth)
    
    # Convert to DataFrame
    path_result_df = spark.createDataFrame([path_result])
    
    # Write to HDFS
    path_result_df.write.mode("overwrite").json(output_path)
    
    return path_result

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Path Finding Spark Job")
    parser.add_argument("--user-email", required=True, help="User email")
    parser.add_argument("--current-emotion", required=True, help="Current emotion")
    parser.add_argument("--target-emotion", required=True, help="Target emotion")
    parser.add_argument("--max-depth", type=int, default=10, help="Maximum path depth")
    parser.add_argument("--input-path", required=True, help="Input path to transitions in HDFS")
    parser.add_argument("--output-path", required=True, help="Output path for path result in HDFS")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Process path finding
        path_result = process_path_finding(
            spark,
            args.input_path,
            args.output_path,
            args.user_email,
            args.current_emotion,
            args.target_emotion,
            args.max_depth
        )
        print(f"Path finding completed: {path_result}")
    finally:
        # Stop Spark session
        spark.stop()

if __name__ == "__main__":
    main()
````

## File: .gitignore
````
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
venv/
.env

# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
.pnp/
.pnp.js
.npm
.yarn-integrity

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# MongoDB
data/db/

# Redis
dump.rdb

# Logs
logs/
*.log
````

## File: .repomixignore
````
# Add patterns to ignore here, one per line
# Example:
# *.log
# tmp/
````

## File: cleanup-all.sh
````bash
#!/bin/bash

echo "🧹 Cleaning up unnecessary files for simple AI-focused setup..."
echo "============================================================"

# Remove complex backend models (keep only simple_app.py)
echo "Removing complex backend models..."
rm -f backend/models/emotional_graph.py
rm -f backend/models/emotional_graph_bigdata.py
rm -f backend/models/emotion_analyzer.py
rm -f backend/models/memory_manager.py
rm -f backend/models/goal_tracker.py
rm -f backend/models/response_generator.py
rm -f backend/models/search_algorithm.py
rm -rf backend/models/

# Remove all services
echo "Removing backend services..."
rm -rf backend/services/

# Remove complex backend files
echo "Removing complex backend files..."
rm -f backend/app.py  # Keep only simple_app.py
rm -f backend/requirements.txt  # Keep only simple_requirements.txt
rm -f backend/user_management.py
rm -f backend/admin_viewer.py
rm -f backend/start_backend.sh
rm -f backend/Dockerfile

# Remove all Spark components
echo "Removing Spark components..."
rm -rf spark/
rm -f run_spark_jobs.sh
rm -f copy_spark_jobs.sh

# Remove complex frontend components (keep only SimpleAIDemo.js and App.js)
echo "Removing complex frontend components..."
rm -f frontend/src/pages/EmotionalJourneyGraph.js
rm -f frontend/src/pages/Goals.js
rm -f frontend/src/pages/Home.js
rm -f frontend/src/pages/Journal.js
rm -f frontend/src/pages/Login.js
rm -f frontend/src/pages/Memories.js
rm -f frontend/src/pages/NotFound.js
rm -f frontend/src/pages/Profile.js
rm -f frontend/src/pages/Register.js
rm -rf frontend/src/pages/

rm -rf frontend/src/components/
rm -rf frontend/src/context/
rm -rf frontend/src/utils/

# Remove Docker files
echo "Removing Docker configurations..."
rm -f backend/Dockerfile
rm -f frontend/Dockerfile

# Remove complex documentation
echo "Removing complex documentation..."
rm -f README_BIGDATA.md
rm -f docs/context.md
rm -f docs/contextV2.md
rm -f docs/contextV3.md
rm -f docs/technical_documentation_V2.md
rm -f docs/technical_documentation.md
rm -rf docs/

# Remove unnecessary scripts
echo "Removing unnecessary scripts..."
rm -f start_reflectly.sh
rm -f stop_reflectly.sh
rm -f start-ai-demo.sh
rm -f cleanup-for-ai.sh

# Remove repomix files
echo "Removing repomix files..."
rm -f repomix-output.md
rm -f .repomixignore
rm -f repomix.config.json

# Create a simple .gitignore for the simplified project
echo "Creating simple .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
.env
venv/
env/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# OS
Thumbs.db
EOF

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📁 Remaining files:"
echo "├── backend/"
echo "│   ├── simple_app.py           # 🧠 Complete AI backend"
echo "│   └── simple_requirements.txt # 📦 Minimal dependencies"
echo "├── frontend/"
echo "│   ├── src/"
echo "│   │   ├── SimpleAIDemo.js     # 🎨 Complete demo interface"
echo "│   │   ├── App.js              # ⚛️ Simple wrapper"
echo "│   │   └── index.js            # ⚛️ React entry point"
echo "│   └── package.json            # 📦 React dependencies"
echo "├── start-simple.sh             # 🚀 One-command startup"
echo "├── start-backend.sh            # 🐍 Backend only"
echo "├── start-frontend.sh           # ⚛️ Frontend only"
echo "└── README.md                   # 📖 Simple setup guide"
echo ""
echo "🎯 Ready for algorithm development!"
echo "🚀 Run: ./start-simple.sh"
````

## File: cleanup-for-ai.sh
````bash
#!/bin/bash

# Cleanup script for AI-focused Reflectly
# Removes big data components and unnecessary files

echo "🧹 Cleaning up AI-focused Reflectly repository..."

# Remove big data services
echo "Removing big data services..."
rm -rf backend/services/

# Remove Spark jobs
echo "Removing Spark components..."
rm -rf spark/
rm -f run_spark_jobs.sh
rm -f copy_spark_jobs.sh

# Remove big data documentation
echo "Removing big data documentation..."
rm -f README_BIGDATA.md

# Remove big data models
echo "Removing big data models..."
rm -f backend/models/emotional_graph_bigdata.py

# Remove unused scripts
echo "Removing deployment scripts..."
rm -f start_reflectly.sh
rm -f stop_reflectly.sh

# Remove goal tracker (not AI-focused)
echo "Removing non-AI components..."
rm -f backend/models/goal_tracker.py

# Remove admin viewer (not essential for AI demo)
rm -f backend/admin_viewer.py
rm -f backend/user_management.py

# Remove Docker files for big data services
echo "Cleaning up Docker configurations..."
# Note: We've already replaced docker-compose.yml with simplified version

# Keep only essential Dockerfiles
echo "Keeping only essential Docker configurations..."

# Clean up frontend - remove non-AI pages
echo "Cleaning up frontend..."
rm -f frontend/src/pages/Goals.js
rm -f frontend/src/pages/Profile.js
rm -f frontend/src/pages/Memories.js

# Update gitignore for AI-focused development
echo "Updating .gitignore..."
cat >> .gitignore << EOF

# AI-focused development
*.pyc
__pycache__/
.pytest_cache/
*.log

# Node modules
node_modules/
npm-debug.log*

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/

# AI models (if downloaded locally)
models/
*.bin
*.safetensors

EOF

echo "✅ Cleanup complete!"
echo ""
echo "🎯 AI-focused Reflectly is ready!"
echo ""
echo "Core AI components kept:"
echo "  ✅ A* search algorithm (backend/models/search_algorithm.py)"
echo "  ✅ Emotional graph (backend/models/emotional_graph.py)"
echo "  ✅ Emotion analyzer (backend/models/emotion_analyzer.py)"
echo "  ✅ Memory manager (backend/models/memory_manager.py)"
echo "  ✅ AI-focused Flask API (backend/app.py)"
echo "  ✅ Emotional journey visualization (frontend/src/pages/EmotionalJourneyGraph.js)"
echo ""
echo "Removed components:"
echo "  ❌ Kafka streaming service"
echo "  ❌ Spark distributed computing"
echo "  ❌ HDFS storage service"
echo "  ❌ Big data orchestration"
echo "  ❌ Goal tracking system"
echo "  ❌ User management complexity"
echo ""
echo "🚀 Next steps:"
echo "  1. Run: docker-compose up -d"
echo "  2. Open: http://localhost:3000"
echo "  3. Test AI pathfinding endpoints"
````

## File: copy_spark_jobs.sh
````bash
#!/bin/bash

# Script to copy Spark jobs to the Spark data directory in the Docker container

# Create directory structure in Spark data volume
echo "Creating directory structure in Spark data volume..."
docker exec -it spark-master mkdir -p /spark/data/spark/jobs

# Copy Spark jobs to the Spark data volume
echo "Copying Spark jobs to the Spark data volume..."
docker cp /Users/manodhyaopallage/Refection/spark/jobs/emotion_analysis.py spark-master:/spark/data/spark/jobs/
docker cp /Users/manodhyaopallage/Refection/spark/jobs/graph_processing.py spark-master:/spark/data/spark/jobs/
docker cp /Users/manodhyaopallage/Refection/spark/jobs/dataset_import.py spark-master:/spark/data/spark/jobs/
docker cp /Users/manodhyaopallage/Refection/spark/jobs/path_finding.py spark-master:/spark/data/spark/jobs/

# Set permissions
echo "Setting permissions..."
docker exec -it spark-master chmod +x /spark/data/spark/jobs/*.py

echo "Spark jobs copied successfully!"
````

## File: README_BIGDATA.md
````markdown
# Reflectly Big Data Infrastructure

This document provides information on the big data infrastructure integrated with the Reflectly project, which includes Kafka, Hadoop, and Spark.

## Overview

The Reflectly project has been enhanced with big data capabilities to improve emotional analysis, path finding, and data processing. The following components have been integrated:

- **Kafka**: Message broker for streaming emotional states and transitions
- **Hadoop (HDFS)**: Distributed file system for storing datasets and results
- **Spark**: Distributed processing engine for emotion analysis and path finding

## Directory Structure

- `/Users/manodhyaopallage/Refection/spark/jobs/`: Contains Spark jobs for various data processing tasks
- `/Users/manodhyaopallage/Refection/backend/models/emotional_graph_bigdata.py`: Enhanced emotional graph with big data integration
- `/Users/manodhyaopallage/Refection/backend/models/search_algorithm.py`: A* search algorithm for emotional path finding

## Setup Instructions

1. Start the Docker containers for the big data infrastructure:

```bash
cd /Users/manodhyaopallage/Refection
docker-compose up -d
```

2. Copy the Spark jobs to the Spark data volume:

```bash
./copy_spark_jobs.sh
```

3. Start the Reflectly backend:

```bash
cd /Users/manodhyaopallage/Refection/backend
./start_backend.sh
```

4. Start the Reflectly frontend:

```bash
cd /Users/manodhyaopallage/Refection/frontend
npm start
```

## Spark Jobs

The following Spark jobs have been implemented:

### 1. Emotion Analysis

Analyzes emotions from journal entries.

```bash
./run_spark_jobs.sh --user-email <email> emotion_analysis
```

### 2. Graph Processing

Processes emotional transitions and builds the emotional graph.

```bash
./run_spark_jobs.sh --user-email <email> graph_processing
```

### 3. Dataset Import

Imports and processes the IEMOCAP and mental health datasets.

```bash
./run_spark_jobs.sh dataset_import
```

### 4. Path Finding

Finds optimal emotional paths using the A* search algorithm.

```bash
./run_spark_jobs.sh --user-email <email> --current-emotion <emotion> --target-emotion <emotion> path_finding
```

## Running All Jobs

To run all jobs in sequence:

```bash
./run_spark_jobs.sh --user-email <email> --current-emotion <emotion> --target-emotion <emotion> all
```

## Accessing Web Interfaces

- **Spark Master**: http://localhost:8080
- **Spark Worker**: http://localhost:8081
- **Hadoop NameNode**: http://localhost:9870
- **Hadoop DataNode**: http://localhost:9864

## Integration with Reflectly

The big data infrastructure is integrated with the Reflectly application through the `EmotionalGraphBigData` class, which extends the original `EmotionalGraph` class with Kafka, HDFS, and Spark integration.

Key features include:
- Publishing emotional states and transitions to Kafka
- Storing and retrieving data from HDFS
- Processing emotional data using Spark
- Finding optimal emotional paths using A* search algorithm

## Troubleshooting

If you encounter issues with the big data infrastructure, try the following:

1. Check if all Docker containers are running:

```bash
docker ps
```

2. Restart the Docker containers:

```bash
docker-compose down
docker-compose up -d
```

3. Check the logs for any errors:

```bash
docker logs namenode
docker logs spark-master
docker logs kafka
```

4. Ensure that the Spark jobs have been copied to the Spark data volume:

```bash
./copy_spark_jobs.sh
```

5. If you're having issues with HDFS, try formatting the namenode:

```bash
docker exec -it namenode hdfs namenode -format
```

## Next Steps

1. Implement more advanced emotion analysis using deep learning models
2. Enhance the emotional graph with more sophisticated path finding algorithms
3. Integrate real-time processing of emotional data
4. Develop more personalized recommendations based on emotional transitions
````

## File: repomix.config.json
````json
{
  "input": {
    "maxFileSize": 52428800
  },
  "output": {
    "filePath": "repomix-output.md",
    "style": "markdown",
    "parsableStyle": false,
    "fileSummary": true,
    "directoryStructure": true,
    "files": true,
    "removeComments": false,
    "removeEmptyLines": false,
    "compress": false,
    "topFilesLength": 5,
    "showLineNumbers": false,
    "copyToClipboard": false,
    "git": {
      "sortByChanges": true,
      "sortByChangesMaxCommits": 100
    }
  },
  "include": [],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": []
  },
  "security": {
    "enableSecurityCheck": true
  },
  "tokenCount": {
    "encoding": "o200k_base"
  }
}
````

## File: run_spark_jobs.sh
````bash
#!/bin/bash

# Script to run Spark jobs for Reflectly

# Default values
USER_EMAIL=""
CURRENT_EMOTION=""
TARGET_EMOTION=""
MAX_DEPTH=10
HDFS_BASE_PATH="/reflectly"
SPARK_MASTER="spark://spark-master:7077"
SPARK_SUBMIT="/spark/bin/spark-submit"

# Function to display usage
function display_usage {
    echo "Usage: $0 [options] <job_name>"
    echo ""
    echo "Options:"
    echo "  --user-email <email>         User email (required for all jobs)"
    echo "  --current-emotion <emotion>  Current emotion (required for path_finding)"
    echo "  --target-emotion <emotion>   Target emotion (required for path_finding)"
    echo "  --max-depth <depth>          Maximum path depth (default: 10)"
    echo "  --hdfs-base-path <path>      Base path in HDFS (default: /reflectly)"
    echo "  --spark-master <url>         Spark master URL (default: spark://spark-master:7077)"
    echo "  --help                       Display this help message"
    echo ""
    echo "Available jobs:"
    echo "  emotion_analysis   - Analyze emotions from journal entries"
    echo "  graph_processing   - Process emotional transitions and build graph"
    echo "  dataset_import     - Import and process IEMOCAP and mental health datasets"
    echo "  path_finding       - Find optimal emotional paths"
    echo "  all                - Run all jobs in sequence"
    echo ""
    echo "Example:"
    echo "  $0 --user-email user@example.com path_finding --current-emotion sadness --target-emotion joy"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --user-email)
            USER_EMAIL="$2"
            shift 2
            ;;
        --current-emotion)
            CURRENT_EMOTION="$2"
            shift 2
            ;;
        --target-emotion)
            TARGET_EMOTION="$2"
            shift 2
            ;;
        --max-depth)
            MAX_DEPTH="$2"
            shift 2
            ;;
        --hdfs-base-path)
            HDFS_BASE_PATH="$2"
            shift 2
            ;;
        --spark-master)
            SPARK_MASTER="$2"
            shift 2
            ;;
        --help)
            display_usage
            exit 0
            ;;
        *)
            JOB_NAME="$1"
            shift
            ;;
    esac
done

# Check if job name is provided
if [ -z "$JOB_NAME" ]; then
    echo "Error: Job name is required"
    display_usage
    exit 1
fi

# Check if user email is provided
if [ -z "$USER_EMAIL" ]; then
    echo "Error: User email is required"
    display_usage
    exit 1
fi

# Function to run emotion analysis job
function run_emotion_analysis {
    echo "Running emotion analysis job..."
    
    # Define paths
    INPUT_PATH="${HDFS_BASE_PATH}/journal_entries/${USER_EMAIL}"
    OUTPUT_PATH="${HDFS_BASE_PATH}/emotion_analysis/${USER_EMAIL}"
    
    # Run job
    docker exec -it spark-master ${SPARK_SUBMIT} \
        --master ${SPARK_MASTER} \
        --py-files /spark/data/spark/jobs/emotion_analysis.py \
        /spark/data/spark/jobs/emotion_analysis.py \
        --user-email ${USER_EMAIL} \
        --input-path ${INPUT_PATH} \
        --output-path ${OUTPUT_PATH}
        
    echo "Emotion analysis job completed"
}

# Function to run graph processing job
function run_graph_processing {
    echo "Running graph processing job..."
    
    # Define paths
    INPUT_PATH="${HDFS_BASE_PATH}/emotion_analysis/${USER_EMAIL}"
    OUTPUT_PATH="${HDFS_BASE_PATH}/emotional_graph/${USER_EMAIL}"
    
    # Run job
    docker exec -it spark-master ${SPARK_SUBMIT} \
        --master ${SPARK_MASTER} \
        --py-files /spark/data/spark/jobs/graph_processing.py \
        /spark/data/spark/jobs/graph_processing.py \
        --user-email ${USER_EMAIL} \
        --input-path ${INPUT_PATH} \
        --output-path ${OUTPUT_PATH}
        
    echo "Graph processing job completed"
}

# Function to run dataset import job
function run_dataset_import {
    echo "Running dataset import job..."
    
    # Define paths
    IEMOCAP_PATH="${HDFS_BASE_PATH}/datasets/iemocap"
    MENTAL_HEALTH_PATH="${HDFS_BASE_PATH}/datasets/mental_health"
    OUTPUT_PATH="${HDFS_BASE_PATH}/datasets/processed"
    
    # Run job
    docker exec -it spark-master ${SPARK_SUBMIT} \
        --master ${SPARK_MASTER} \
        --py-files /spark/data/spark/jobs/dataset_import.py \
        /spark/data/spark/jobs/dataset_import.py \
        --iemocap-path ${IEMOCAP_PATH} \
        --mental-health-path ${MENTAL_HEALTH_PATH} \
        --output-path ${OUTPUT_PATH}
        
    echo "Dataset import job completed"
}

# Function to run path finding job
function run_path_finding {
    echo "Running path finding job..."
    
    # Check if current and target emotions are provided
    if [ -z "$CURRENT_EMOTION" ] || [ -z "$TARGET_EMOTION" ]; then
        echo "Error: Current emotion and target emotion are required for path finding job"
        display_usage
        exit 1
    fi
    
    # Define paths
    INPUT_PATH="${HDFS_BASE_PATH}/emotional_graph/${USER_EMAIL}"
    OUTPUT_PATH="${HDFS_BASE_PATH}/emotional_paths/${USER_EMAIL}/${CURRENT_EMOTION}_to_${TARGET_EMOTION}"
    
    # Run job
    docker exec -it spark-master ${SPARK_SUBMIT} \
        --master ${SPARK_MASTER} \
        --py-files /spark/data/spark/jobs/path_finding.py \
        /spark/data/spark/jobs/path_finding.py \
        --user-email ${USER_EMAIL} \
        --current-emotion ${CURRENT_EMOTION} \
        --target-emotion ${TARGET_EMOTION} \
        --max-depth ${MAX_DEPTH} \
        --input-path ${INPUT_PATH} \
        --output-path ${OUTPUT_PATH}
        
    echo "Path finding job completed"
}

# Function to run all jobs
function run_all_jobs {
    echo "Running all jobs..."
    
    run_dataset_import
    run_emotion_analysis
    run_graph_processing
    
    # Check if current and target emotions are provided for path finding
    if [ -n "$CURRENT_EMOTION" ] && [ -n "$TARGET_EMOTION" ]; then
        run_path_finding
    else
        echo "Skipping path finding job (current and target emotions not provided)"
    fi
    
    echo "All jobs completed"
}

# Run the specified job
case $JOB_NAME in
    emotion_analysis)
        run_emotion_analysis
        ;;
    graph_processing)
        run_graph_processing
        ;;
    dataset_import)
        run_dataset_import
        ;;
    path_finding)
        run_path_finding
        ;;
    all)
        run_all_jobs
        ;;
    *)
        echo "Error: Invalid job name: $JOB_NAME"
        display_usage
        exit 1
        ;;
esac

exit 0
````

## File: start_reflectly.sh
````bash
#!/bin/bash

# Script to start the entire Reflectly application with big data infrastructure

# Function to display usage
function display_usage {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help                Display this help message"
    echo "  --skip-docker         Skip starting Docker containers"
    echo "  --skip-backend        Skip starting the backend"
    echo "  --skip-frontend       Skip starting the frontend"
    echo "  --skip-copy-jobs      Skip copying Spark jobs"
    echo ""
    echo "Example:"
    echo "  $0                    Start everything"
    echo "  $0 --skip-docker      Start everything except Docker containers"
}

# Parse command line arguments
SKIP_DOCKER=false
SKIP_BACKEND=false
SKIP_FRONTEND=false
SKIP_COPY_JOBS=false

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --help)
            display_usage
            exit 0
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --skip-copy-jobs)
            SKIP_COPY_JOBS=true
            shift
            ;;
        *)
            echo "Error: Unknown option: $key"
            display_usage
            exit 1
            ;;
    esac
done

# Start Docker containers
if [ "$SKIP_DOCKER" = false ]; then
    echo "Starting Docker containers..."
    docker-compose up -d
    
    # Wait for containers to start
    echo "Waiting for containers to start..."
    sleep 10
else
    echo "Skipping Docker containers startup..."
fi

# Copy Spark jobs
if [ "$SKIP_COPY_JOBS" = false ]; then
    echo "Copying Spark jobs..."
    ./copy_spark_jobs.sh
else
    echo "Skipping copying Spark jobs..."
fi

# Start backend
if [ "$SKIP_BACKEND" = false ]; then
    echo "Starting backend..."
    cd backend
    ./start_backend.sh &
    cd ..
    
    # Wait for backend to start
    echo "Waiting for backend to start..."
    sleep 5
else
    echo "Skipping backend startup..."
fi

# Start frontend
if [ "$SKIP_FRONTEND" = false ]; then
    echo "Starting frontend..."
    cd frontend
    npm start &
    cd ..
else
    echo "Skipping frontend startup..."
fi

echo ""
echo "Reflectly application started!"
echo ""
echo "Access the application at: http://localhost:3000"
echo "Access Spark Master at: http://localhost:8080"
echo "Access Hadoop NameNode at: http://localhost:9870"
echo ""
echo "To stop the application, press Ctrl+C and then run: docker-compose down"
````

## File: start-agent.sh
````bash
#!/bin/bash

echo "🤖 Starting Intelligent Agent Backend"
echo "===================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python3 is available"

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install Flask Flask-CORS

echo ""
echo "🚀 Starting Intelligent Agent Backend..."
echo "📡 Backend will be available at: http://localhost:5000"
echo "🧠 Features: Memory Learning + A* Search + Emotion Analysis"
echo ""
echo "💡 To stop: Press Ctrl+C"
echo ""

# Start the intelligent agent
python intelligent_agent.py
````

## File: start-ai-demo.sh
````bash
#!/bin/bash

echo "🚀 Starting Reflectly AI - Emotional Pathfinding Demo"
echo "================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Make cleanup script executable
chmod +x cleanup-for-ai.sh

echo ""
echo "🧹 Running cleanup to remove big data components..."
./cleanup-for-ai.sh

echo ""
echo "🔧 Starting core AI services..."

# Stop any existing containers
docker-compose down

# Build and start services
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."

# Wait for backend to be ready
echo "Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:5002/health >/dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check logs with: docker-compose logs backend"
        exit 1
    fi
    sleep 2
done

# Wait for frontend to be ready
echo "Checking frontend..."
for i in {1..20}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "⚠️  Frontend might still be starting. Check logs with: docker-compose logs frontend"
    fi
    sleep 3
done

echo ""
echo "🎉 Reflectly AI is now running!"
echo ""
echo "🌐 Access Points:"
echo "   Frontend (AI Demo): http://localhost:3000"
echo "   Backend API:        http://localhost:5002"
echo "   Health Check:       http://localhost:5002/health"
echo ""
echo "🧠 Core AI Features Available:"
echo "   ✅ A* Emotional Pathfinding"
echo "   ✅ Emotion Analysis from Text"
echo "   ✅ Interactive Graph Visualization"
echo "   ✅ Personalized Action Suggestions"
echo ""
echo "🔬 Test the AI API:"
echo ""
echo "1. Analyze emotion from text:"
echo "   curl -X POST http://localhost:5002/api/emotions/analyze \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"text\": \"I feel excited about this new project!\", \"user_email\": \"demo@example.com\"}'"
echo ""
echo "2. Find optimal emotional path:"
echo "   curl -X POST http://localhost:5002/api/emotions/path \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"user_email\": \"demo@example.com\", \"current_emotion\": \"sadness\", \"target_emotion\": \"joy\"}'"
echo ""
echo "3. Get graph visualization data:"
echo "   curl http://localhost:5002/api/emotions/graph-data/demo@example.com"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
echo ""
echo "🎯 Focus Areas:"
echo "   - A* search algorithm in backend/models/search_algorithm.py"
echo "   - Emotional graph theory in backend/models/emotional_graph.py"
echo "   - AI visualization in frontend/src/pages/EmotionalJourneyGraph.js"
echo ""
echo "Happy pathfinding! 🎯✨"
````

## File: start-backend.sh
````bash
#!/bin/bash

echo "🐍 Starting Simple Python Backend for Algorithm Development"
echo "========================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python3 is available"

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing minimal requirements..."
pip install -r simple_requirements.txt

echo ""
echo "🚀 Starting Flask backend..."
echo "📡 Backend will be available at: http://localhost:5000"
echo "🔬 Test algorithm endpoint: http://localhost:5000/api/test-algorithm"
echo ""
echo "💡 To stop: Press Ctrl+C"
echo ""

# Start the simple Flask app
python simple_app.py
````

## File: start-frontend.sh
````bash
#!/bin/bash

echo "⚛️  Starting Simple React Frontend for Algorithm Development"
echo "=========================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are available"

# Navigate to frontend directory
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🚀 Starting React development server..."
echo "🌐 Frontend will be available at: http://localhost:3000"
echo "🔗 Make sure backend is running at: http://localhost:5000"
echo ""
echo "💡 To stop: Press Ctrl+C"
echo ""

# Start the React development server
npm start
````

## File: start-intelligent-agent.sh
````bash
#!/bin/bash

echo "🤖 Starting Intelligent Agent with Memory Map"
echo "============================================"
echo "🧠 Features: Learning + A* Search + Memory Evolution"
echo ""

# Make scripts executable
chmod +x start-agent.sh

# Check requirements
echo "🔍 Checking requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.7+ first."
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi
echo "✅ Node.js: $(node --version)"

echo ""
echo "🔧 Setting up backend..."

# Setup backend
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install requirements
echo "📥 Installing backend dependencies..."
source venv/bin/activate
pip install Flask Flask-CORS

cd ..

echo ""
echo "🔧 Setting up frontend..."

# Setup frontend
cd frontend

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    npm install
else
    echo "✅ React dependencies already installed"
fi

cd ..

echo ""
echo "🎯 Starting Intelligent Agent..."
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Start backend in background
echo "🤖 Starting Intelligent Agent Backend..."
cd backend
source venv/bin/activate
python intelligent_agent.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🗺️  Starting Memory Map Frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Intelligent Agent is now running!"
echo ""
echo "🌐 Access Points:"
echo "   Frontend (Memory Map): http://localhost:3000"
echo "   Backend API:           http://localhost:5000"
echo ""
echo "🤖 How it works:"
echo "   😊 Share happy emotions → Agent asks for steps → Learns for future"
echo "   😢 Share sad emotions → Agent suggests actions using A* search"
echo "   🗺️  Memory map grows and evolves with each interaction"
echo ""
echo "🔬 Try these examples:"
echo "   • 'I'm feeling really happy and excited today!'"
echo "   • 'I'm sad and don't know what to do'"
echo "   • 'I'm anxious about my presentation tomorrow'"
echo ""
echo "💡 Press Ctrl+C to stop both services"

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
````

## File: start-simple.sh
````bash
#!/bin/bash

echo "🚀 Simple Reflectly AI - Algorithm Development Setup"
echo "=================================================="
echo "🎯 Focus: Pure Algorithm Development"
echo "🏗️  Architecture: Python Flask + React (No Docker, No Database)"
echo ""

# Make scripts executable
chmod +x start-backend.sh
chmod +x start-frontend.sh

# Check requirements
echo "🔍 Checking requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.7+ first."
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi
echo "✅ npm: $(npm --version)"

echo ""
echo "🔧 Setting up backend..."

# Setup backend
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install requirements
echo "📥 Installing backend dependencies..."
source venv/bin/activate
pip install -r simple_requirements.txt

cd ..

echo ""
echo "🔧 Setting up frontend..."

# Setup frontend
cd frontend

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    npm install
else
    echo "✅ React dependencies already installed"
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Starting both backend and frontend..."
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Start backend in background
echo "🐍 Starting Python backend..."
cd backend
source venv/bin/activate
python simple_app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "⚛️  Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Simple Reflectly AI is now running!"
echo ""
echo "🌐 Access Points:"
echo "   Frontend (AI Demo): http://localhost:3000"
echo "   Backend API:        http://localhost:5000"
echo "   Algorithm Test:     http://localhost:5000/api/test-algorithm"
echo ""
echo "🧠 Core Features:"
echo "   ✅ A* Emotional Pathfinding"
echo "   ✅ Simple Emotion Analysis"
echo "   ✅ Interactive Visualization"
echo "   ✅ Real-time Algorithm Testing"
echo ""
echo "📁 Key Files for Development:"
echo "   🔬 backend/simple_app.py           - Main AI algorithms"
echo "   🎨 frontend/src/SimpleAIDemo.js    - React interface"
echo "   📊 AStarPathfinder class           - A* implementation"
echo "   🧮 SimpleEmotionAnalyzer class     - Emotion detection"
echo ""
echo "🔬 Quick API Tests:"
echo ""
echo "# Test emotion analysis:"
echo "curl -X POST http://localhost:5000/api/emotions/analyze \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"text\": \"I feel excited about this!\", \"user_email\": \"demo@example.com\"}'"
echo ""
echo "# Test pathfinding:"
echo "curl -X POST http://localhost:5000/api/emotions/path \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"current_emotion\": \"sadness\", \"target_emotion\": \"joy\"}'"
echo ""
echo "# Test algorithm:"
echo "curl http://localhost:5000/api/test-algorithm"
echo ""
echo "💡 Press Ctrl+C to stop both services"
echo "🔄 Both services will restart automatically on file changes"

# Wait for background processes
wait $BACKEND_PID $FRONTEND_PID
````

## File: stop_reflectly.sh
````bash
#!/bin/bash

# Script to stop the entire Reflectly application with big data infrastructure

echo "Stopping Reflectly application..."

# Find and kill frontend process (npm)
echo "Stopping frontend..."
pkill -f "node.*start"

# Find and kill backend process (Flask)
echo "Stopping backend..."
pkill -f "python.*app.py"

# Stop Docker containers
echo "Stopping Docker containers..."
docker-compose down

echo "All Reflectly components have been stopped."
````

## File: test-backend.sh
````bash
#!/bin/bash

echo "🔍 Testing Intelligent Agent Backend"
echo "=================================="

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Backend is running on port 5000"
else
    echo "❌ Backend is NOT running on port 5000"
    echo "💡 Start it with: ./start-agent.sh or python backend/intelligent_agent.py"
    exit 1
fi

echo ""
echo "2. Testing health endpoint..."
curl -s http://localhost:5000/api/health | python -m json.tool

echo ""
echo ""
echo "3. Testing emotion analysis..."
curl -X POST http://localhost:5000/api/process-input \
  -H "Content-Type: application/json" \
  -d '{"text": "I am feeling really happy today!", "user_id": "test_user"}' \
  | python -m json.tool

echo ""
echo ""
echo "4. Testing memory map..."
curl -s http://localhost:5000/api/memory-map | python -m json.tool

echo ""
echo ""
echo "5. Testing memory stats..."
curl -s http://localhost:5000/api/memory-stats | python -m json.tool

echo ""
echo ""
echo "✅ Backend testing complete!"
echo "If you see JSON responses above, the backend is working correctly."
echo "If you see errors, check the backend logs for details."
````

## File: TROUBLESHOOTING.md
````markdown
# 🔧 Troubleshooting Guide - 403 Forbidden Error

## 🚨 **Problem: 403 Forbidden Error**

When you type input, you see:
```
POST http://localhost:3000/api/process-input 403 (Forbidden)
```

## 🎯 **Quick Fix (Most Common)**

### **Step 1: Make sure backend is running**
```bash
# Option 1: Run backend only
./start-agent.sh

# Option 2: Run both frontend and backend
./start-intelligent-agent.sh

# Option 3: Manual backend start
cd backend
python3 intelligent_agent.py
```

### **Step 2: Test backend directly**
```bash
# Make test script executable and run it
chmod +x test-backend.sh
./test-backend.sh
```

**Expected output:**
```json
{
  "status": "healthy",
  "service": "Intelligent Agent with Memory Map"
}
```

### **Step 3: Check frontend connection**
Open browser console (F12) and look for:
- ✅ "Backend connected" message
- ✅ Green status indicator in the UI

## 🔍 **Detailed Diagnosis**

### **Check 1: Is backend running?**
```bash
curl http://localhost:5000/api/health
```

**If this fails:**
- Backend is not running
- **Solution**: Start backend with `./start-agent.sh`

### **Check 2: CORS issues?**
```bash
curl -X POST http://localhost:5000/api/process-input \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "user_id": "test"}'
```

**If this works but browser fails:**
- CORS configuration issue
- **Solution**: Check backend CORS settings

### **Check 3: Port conflicts?**
```bash
# Check what's running on port 5000
lsof -i :5000

# Check what's running on port 3000  
lsof -i :3000
```

**If wrong services are running:**
- Kill conflicting processes
- Restart with correct scripts

## 🛠️ **Step-by-Step Solution**

### **1. Stop everything**
```bash
# Kill any running processes
pkill -f "intelligent_agent.py"
pkill -f "npm start"
pkill -f "react-scripts"
```

### **2. Start backend first**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-CORS
python3 intelligent_agent.py
```

**Wait for this message:**
```
🤖 Starting Intelligent Agent with Memory Map
📡 API: http://localhost:5000
```

### **3. Test backend works**
```bash
# In new terminal
curl http://localhost:5000/api/health
```

**Should see:**
```json
{
  "status": "healthy",
  "service": "Intelligent Agent with Memory Map"
}
```

### **4. Start frontend**
```bash
# In new terminal
cd frontend
npm start
```

### **5. Check browser**
- Go to http://localhost:3000
- Look for **green "Backend connected"** status
- Try typing: "I'm feeling happy today!"

## ⚠️ **Common Issues & Solutions**

### **Issue 1: Backend won't start**
```bash
# Error: ModuleNotFoundError: No module named 'flask'
pip install Flask Flask-CORS

# Error: Permission denied
chmod +x start-agent.sh

# Error: Port already in use
lsof -i :5000
kill -9 <PID>
```

### **Issue 2: Frontend shows red status**
- Check browser console for exact error
- Make sure backend is running first
- Try refreshing the page

### **Issue 3: CORS still blocked**
- Make sure you're using the updated frontend code
- Clear browser cache (Ctrl+Shift+R)
- Check backend console for CORS messages

### **Issue 4: Proxy not working**
The updated frontend tries direct connection first, so proxy issues are avoided.

## 🧪 **Test Commands**

### **Test 1: Backend Health**
```bash
curl http://localhost:5000/api/health
```

### **Test 2: Emotion Processing**
```bash
curl -X POST http://localhost:5000/api/process-input \
  -H "Content-Type: application/json" \
  -d '{"text": "I am happy", "user_id": "test"}'
```

### **Test 3: Memory Map**
```bash
curl http://localhost:5000/api/memory-map
```

## 📋 **Checklist for Working System**

- [ ] Backend running on port 5000
- [ ] Frontend running on port 3000  
- [ ] Green "Backend connected" status in UI
- [ ] Can type text and get response
- [ ] Memory map shows in right panel
- [ ] No 403 or CORS errors in console

## 🚀 **Quick Reset (Nuclear Option)**

If nothing works, start completely fresh:

```bash
# 1. Kill everything
pkill -f python
pkill -f node
pkill -f react

# 2. Clean start backend
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-CORS
python3 intelligent_agent.py

# 3. Clean start frontend (new terminal)
cd frontend
rm -rf node_modules
npm install
npm start

# 4. Test
curl http://localhost:5000/api/health
```

## 🆘 **Still Not Working?**

### **Check browser console (F12) for:**
- Network errors
- CORS errors  
- JavaScript errors

### **Check backend console for:**
- Flask startup messages
- CORS configuration
- Request logs

### **Common error messages:**
- `EADDRINUSE`: Port already in use
- `Connection refused`: Backend not running
- `CORS error`: CORS misconfiguration
- `403 Forbidden`: Permission/routing issue

## ✅ **Success Indicators**

**Backend console should show:**
```
🤖 Starting Intelligent Agent with Memory Map
🧠 Features: Emotion Analysis + A* Search + Learning
📡 API: http://localhost:5000
✅ CORS enabled for http://localhost:3000
```

**Frontend should show:**
- ✅ Green "Backend connected" status
- 🗺️ Memory map visualization (even if empty)
- 💬 Conversation interface ready for input

**Browser console should show:**
```
✅ Backend connected: {status: "healthy", service: "Intelligent Agent with Memory Map"}
```

---

**After following this guide, your intelligent agent should work correctly! The 403 error is almost always caused by the backend not running or CORS misconfiguration.** 🔧✨
````

## File: backend/models/emotion_analyzer.py
````python
import random
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """
    Enhanced EmotionAnalyzer that can use a pre-trained model for emotion detection.
    Falls back to rule-based detection if dependencies are not available.
    """
    
    def __init__(self, use_pretrained=True):
        """
        Initialize the EmotionAnalyzer.
        
        Args:
            use_pretrained (bool): Whether to use a pre-trained model
        """
        # Define emotion labels
        self.emotion_labels = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
        self.positive_emotions = ['joy', 'surprise']
        self.use_pretrained = use_pretrained
        self.model = None
        self.tokenizer = None
        
        # Try to initialize the pre-trained model if requested
        if use_pretrained:
            try:
                from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
                
                # Check if we should use CPU or GPU
                device = -1  # CPU by default
                
                # Load emotion classification pipeline
                try:
                    logger.info("Loading emotion classification model...")
                    self.pipeline = pipeline(
                        "text-classification", 
                        model="j-hartmann/emotion-english-distilroberta-base", 
                        top_k=None,
                        device=device
                    )
                    logger.info("Emotion classification model loaded successfully")
                    self.using_pretrained = True
                except Exception as e:
                    logger.warning(f"Failed to load pre-trained model: {str(e)}")
                    logger.warning("Falling back to rule-based emotion detection")
                    self.using_pretrained = False
            except ImportError:
                logger.warning("Transformers library not found. Falling back to rule-based emotion detection")
                self.using_pretrained = False
        else:
            self.using_pretrained = False
            
        logger.info(f"EmotionAnalyzer initialized with pretrained={self.using_pretrained}")
        
    def analyze(self, text):
        """
        Analyze the emotion in the given text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: A dictionary containing emotion analysis results
        """
        if self.using_pretrained:
            try:
                return self._analyze_with_model(text)
            except Exception as e:
                logger.error(f"Error using pre-trained model: {str(e)}")
                logger.info("Falling back to rule-based emotion detection")
                return self._analyze_rule_based(text)
        else:
            return self._analyze_rule_based(text)
    
    def _analyze_with_model(self, text):
        """
        Analyze emotion using the pre-trained model.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: A dictionary containing emotion analysis results
        """
        # Get predictions from the model
        results = self.pipeline(text)
        
        # Extract emotion scores
        emotion_scores = {}
        for result in results[0]:
            label = result['label']
            score = result['score']
            # Map model labels to our standard labels if needed
            if label == 'LABEL_0':
                label = 'anger'
            elif label == 'LABEL_1':
                label = 'disgust'
            elif label == 'LABEL_2':
                label = 'fear'
            elif label == 'LABEL_3':
                label = 'joy'
            elif label == 'LABEL_4':
                label = 'neutral'
            elif label == 'LABEL_5':
                label = 'sadness'
            elif label == 'LABEL_6':
                label = 'surprise'
            
            emotion_scores[label] = float(score)
        
        # Find the primary emotion (highest score)
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # Create emotion data dictionary
        emotion_data = {
            'primary_emotion': primary_emotion,
            'emotion_scores': emotion_scores,
            'is_positive': primary_emotion in self.positive_emotions,
            'detection_method': 'pretrained_model'
        }
        
        return emotion_data
    
    def _analyze_rule_based(self, text):
        """
        Analyze emotion using rule-based detection.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: A dictionary containing emotion analysis results
        """
        # Simple keyword-based emotion detection for demo purposes
        text_lower = text.lower()
        
        # Determine primary emotion based on simple keyword matching
        if any(word in text_lower for word in ['happy', 'glad', 'joy', 'exciting', 'wonderful', 'delighted', 'pleased']):
            primary_emotion = 'joy'
        elif any(word in text_lower for word in ['sad', 'upset', 'unhappy', 'depressed', 'miserable', 'gloomy', 'heartbroken']):
            primary_emotion = 'sadness'
        elif any(word in text_lower for word in ['angry', 'mad', 'furious', 'annoyed', 'irritated', 'enraged', 'frustrated']):
            primary_emotion = 'anger'
        elif any(word in text_lower for word in ['afraid', 'scared', 'worried', 'anxious', 'terrified', 'nervous', 'fearful']):
            primary_emotion = 'fear'
        elif any(word in text_lower for word in ['surprised', 'shocked', 'amazed', 'astonished', 'stunned']):
            primary_emotion = 'surprise'
        elif any(word in text_lower for word in ['disgusted', 'gross', 'repulsed', 'revolted', 'appalled']):
            primary_emotion = 'disgust'
        else:
            primary_emotion = 'neutral'
        
        # Generate random scores for each emotion, with the primary emotion having the highest score
        emotion_scores = {}
        for emotion in self.emotion_labels:
            if emotion == primary_emotion:
                emotion_scores[emotion] = random.uniform(0.7, 0.9)
            else:
                emotion_scores[emotion] = random.uniform(0.0, 0.3)
        
        # Normalize scores
        total = sum(emotion_scores.values())
        for emotion in emotion_scores:
            emotion_scores[emotion] = emotion_scores[emotion] / total
        
        # Create emotion data dictionary
        emotion_data = {
            'primary_emotion': primary_emotion,
            'emotion_scores': emotion_scores,
            'is_positive': primary_emotion in self.positive_emotions,
            'detection_method': 'rule_based'
        }
        
        return emotion_data
    
    def _is_positive_emotion(self, emotion):
        """
        Determine if the given emotion is positive.
        
        Args:
            emotion (str): The emotion to check
            
        Returns:
            bool: True if the emotion is positive, False otherwise
        """
        return emotion in self.positive_emotions
````

## File: backend/simple_app.py
````python
"""
Ultra-Simple Reflectly Backend for Algorithm Development
Pure Python Flask app with in-memory storage - no databases, no Docker
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
from collections import defaultdict
import re
import math
import heapq

app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# In-memory storage (replace database)
emotional_states = []
emotional_transitions = []
user_data = defaultdict(list)

# Available emotions
EMOTIONS = ['joy', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral']
POSITIVE_EMOTIONS = ['joy', 'surprise']
NEGATIVE_EMOTIONS = ['sadness', 'anger', 'fear', 'disgust']

class SimpleEmotionAnalyzer:
    """Simple emotion analysis using keyword matching"""
    
    def __init__(self):
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'joy', 'cheerful', 'glad', 'delighted', 'pleased', 'thrilled', 'elated', 'amazing', 'awesome', 'fantastic', 'wonderful', 'great'],
            'sadness': ['sad', 'depressed', 'down', 'upset', 'miserable', 'gloomy', 'sorrowful', 'melancholy', 'disappointed', 'heartbroken', 'crying', 'tears'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated', 'rage', 'livid', 'pissed', 'outraged', 'hostile', 'aggressive'],
            'fear': ['scared', 'afraid', 'frightened', 'worried', 'anxious', 'nervous', 'terrified', 'panic', 'overwhelmed', 'stressed', 'concerned', 'uneasy'],
            'disgust': ['disgusted', 'revolted', 'sickened', 'appalled', 'repulsed', 'nauseated', 'grossed', 'revolting', 'disgusting'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'unexpected', 'wow', 'incredible', 'unbelievable'],
        }
    
    def analyze(self, text):
        """Analyze emotion in text using simple keyword matching"""
        text_lower = text.lower()
        scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[emotion] = score
        
        # If no emotions detected, default to neutral
        if not any(scores.values()):
            scores['neutral'] = 1
        
        # Get primary emotion
        primary_emotion = max(scores, key=scores.get)
        
        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            normalized_scores = {k: v/total_score for k, v in scores.items()}
        else:
            normalized_scores = {emotion: 1/len(EMOTIONS) for emotion in EMOTIONS}
        
        return {
            'primary_emotion': primary_emotion,
            'is_positive': primary_emotion in POSITIVE_EMOTIONS,
            'emotion_scores': normalized_scores,
            'confidence': max(normalized_scores.values())
        }

class AStarPathfinder:
    """A* algorithm for finding optimal emotional paths"""
    
    def __init__(self):
        # Default transition costs (can be personalized later)
        self.base_costs = {
            ('sadness', 'joy'): 2.0,
            ('sadness', 'neutral'): 1.0,
            ('sadness', 'anger'): 1.3,
            ('sadness', 'fear'): 1.2,
            ('sadness', 'disgust'): 1.1,
            ('sadness', 'surprise'): 1.8,
            
            ('anger', 'joy'): 2.2,
            ('anger', 'neutral'): 1.3,
            ('anger', 'sadness'): 1.2,
            ('anger', 'fear'): 1.1,
            ('anger', 'disgust'): 0.9,
            ('anger', 'surprise'): 1.5,
            
            ('fear', 'joy'): 2.1,
            ('fear', 'neutral'): 1.2,
            ('fear', 'sadness'): 1.1,
            ('fear', 'anger'): 1.0,
            ('fear', 'disgust'): 0.9,
            ('fear', 'surprise'): 1.4,
            
            ('disgust', 'joy'): 2.0,
            ('disgust', 'neutral'): 1.1,
            ('disgust', 'sadness'): 1.0,
            ('disgust', 'anger'): 0.8,
            ('disgust', 'fear'): 0.9,
            ('disgust', 'surprise'): 1.3,
            
            ('neutral', 'joy'): 0.7,
            ('neutral', 'sadness'): 0.8,
            ('neutral', 'anger'): 0.9,
            ('neutral', 'fear'): 0.8,
            ('neutral', 'disgust'): 0.9,
            ('neutral', 'surprise'): 0.6,
            
            ('joy', 'neutral'): 0.8,
            ('joy', 'sadness'): 1.5,
            ('joy', 'anger'): 1.8,
            ('joy', 'fear'): 1.7,
            ('joy', 'disgust'): 1.6,
            ('joy', 'surprise'): 0.5,
            
            ('surprise', 'joy'): 0.6,
            ('surprise', 'neutral'): 0.7,
            ('surprise', 'sadness'): 1.2,
            ('surprise', 'anger'): 1.4,
            ('surprise', 'fear'): 1.3,
            ('surprise', 'disgust'): 1.2,
        }
        
        # Fill in missing combinations with default values
        for from_emotion in EMOTIONS:
            for to_emotion in EMOTIONS:
                if from_emotion != to_emotion and (from_emotion, to_emotion) not in self.base_costs:
                    if to_emotion in POSITIVE_EMOTIONS:
                        self.base_costs[(from_emotion, to_emotion)] = 1.5
                    elif to_emotion == 'neutral':
                        self.base_costs[(from_emotion, to_emotion)] = 1.0
                    else:
                        self.base_costs[(from_emotion, to_emotion)] = 1.2
    
    def heuristic(self, current, target):
        """Heuristic function for A* search"""
        if current == target:
            return 0
        return self.base_costs.get((current, target), 1.5)
    
    def get_neighbors(self, emotion):
        """Get possible transitions from an emotion"""
        neighbors = {}
        for target in EMOTIONS:
            if target != emotion:
                cost = self.base_costs.get((emotion, target), 1.5)
                action = self.get_action(emotion, target)
                neighbors[target] = {
                    'cost': cost,
                    'action': action,
                    'success_rate': min(1.0, 1.0 / cost)  # Higher cost = lower success rate
                }
        return neighbors
    
    def get_action(self, from_emotion, to_emotion):
        """Get recommended action for transition"""
        actions = {
            ('sadness', 'joy'): "Engage in activities you enjoy",
            ('sadness', 'neutral'): "Practice mindfulness meditation",
            ('sadness', 'anger'): "Express your feelings constructively",
            ('sadness', 'fear'): "Identify specific concerns",
            ('sadness', 'disgust'): "Focus on positive aspects",
            ('sadness', 'surprise'): "Try something new and unexpected",
            
            ('anger', 'joy'): "Channel energy into positive activities",
            ('anger', 'neutral'): "Take deep breaths and count to 10",
            ('anger', 'sadness'): "Reflect on underlying feelings",
            ('anger', 'fear'): "Consider potential consequences",
            ('anger', 'disgust'): "Shift focus to solutions",
            ('anger', 'surprise'): "Do something unexpected to break the pattern",
            
            ('fear', 'joy'): "Focus on positive outcomes",
            ('fear', 'neutral'): "Ground yourself in the present moment",
            ('fear', 'sadness'): "Share your concerns with someone you trust",
            ('fear', 'anger'): "Channel fear into productive action",
            ('fear', 'disgust'): "Challenge negative thoughts",
            ('fear', 'surprise'): "Embrace uncertainty as opportunity",
            
            ('disgust', 'joy'): "Focus on things you appreciate",
            ('disgust', 'neutral'): "Practice acceptance",
            ('disgust', 'sadness'): "Explore underlying values",
            ('disgust', 'anger'): "Set boundaries",
            ('disgust', 'fear'): "Examine core concerns",
            ('disgust', 'surprise'): "Look for unexpected positive aspects",
            
            ('neutral', 'joy'): "Engage in activities you enjoy",
            ('neutral', 'sadness'): "Allow yourself to feel emotions",
            ('neutral', 'anger'): "Identify sources of frustration",
            ('neutral', 'fear'): "Acknowledge concerns",
            ('neutral', 'disgust'): "Identify values being challenged",
            ('neutral', 'surprise'): "Seek out new experiences",
            
            ('joy', 'neutral'): "Practice mindfulness",
            ('joy', 'sadness'): "Reflect on meaningful experiences",
            ('joy', 'anger'): "Channel energy constructively",
            ('joy', 'fear'): "Consider growth opportunities",
            ('joy', 'disgust'): "Examine values and boundaries",
            ('joy', 'surprise'): "Share your joy with others",
            
            ('surprise', 'joy'): "Embrace the unexpected",
            ('surprise', 'neutral'): "Reflect on what surprised you",
            ('surprise', 'sadness'): "Process your feelings about the surprise",
            ('surprise', 'anger'): "Consider why this triggered anger",
            ('surprise', 'fear'): "Identify what feels threatening",
            ('surprise', 'disgust'): "Examine your boundaries",
        }
        return actions.get((from_emotion, to_emotion), f"Work on transitioning from {from_emotion} to {to_emotion}")
    
    def find_path(self, start, goal, max_depth=5):
        """Find optimal path using A* algorithm"""
        if start == goal:
            return {
                'path': [start],
                'actions': [],
                'total_cost': 0,
                'estimated_success_rate': 1.0
            }
        
        # A* algorithm implementation
        open_set = [(0, start, [])]  # (f_score, current_node, path)
        closed_set = set()
        g_score = {start: 0}
        
        while open_set:
            current_f, current, path = heapq.heappop(open_set)
            
            if len(path) >= max_depth:
                continue
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            if current == goal:
                # Reconstruct path with actions
                full_path = path + [current]
                actions = []
                total_cost = g_score[current]
                
                for i in range(len(full_path) - 1):
                    from_emotion = full_path[i]
                    to_emotion = full_path[i + 1]
                    action = self.get_action(from_emotion, to_emotion)
                    cost = self.base_costs.get((from_emotion, to_emotion), 1.5)
                    
                    actions.append({
                        'from': from_emotion,
                        'to': to_emotion,
                        'action': action,
                        'success_rate': min(1.0, 1.0 / cost)
                    })
                
                # Calculate estimated success rate
                if actions:
                    success_rates = [action['success_rate'] for action in actions]
                    estimated_success_rate = 1.0
                    for rate in success_rates:
                        estimated_success_rate *= rate
                else:
                    estimated_success_rate = 1.0
                
                return {
                    'path': full_path,
                    'actions': actions,
                    'total_cost': total_cost,
                    'estimated_success_rate': estimated_success_rate
                }
            
            # Explore neighbors
            neighbors = self.get_neighbors(current)
            for neighbor, info in neighbors.items():
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current] + info['cost']
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor, path + [current]))
        
        # No path found, return direct transition
        return {
            'path': [start, goal],
            'actions': [{
                'from': start,
                'to': goal,
                'action': self.get_action(start, goal),
                'success_rate': 0.5
            }],
            'total_cost': self.base_costs.get((start, goal), 2.0),
            'estimated_success_rate': 0.5
        }

# Initialize AI components
emotion_analyzer = SimpleEmotionAnalyzer()
pathfinder = AStarPathfinder()

# API Routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy", 
        "message": "Simple AI backend running",
        "cors_enabled": True,
        "endpoints": [
            "/api/emotions/analyze",
            "/api/emotions/path", 
            "/api/emotions/available",
            "/api/emotions/suggestions",
            "/api/test-algorithm"
        ]
    })

@app.route('/api/emotions/analyze', methods=['POST', 'OPTIONS'])
def analyze_emotion():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 200
        
    try:
        data = request.get_json()
        text = data.get('text', '')
        user_email = data.get('user_email', 'demo@example.com')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Analyze emotion
        result = emotion_analyzer.analyze(text)
        
        # Store in memory
        emotion_entry = {
            'id': len(emotional_states),
            'user_email': user_email,
            'text': text,
            'timestamp': datetime.datetime.now().isoformat(),
            **result
        }
        emotional_states.append(emotion_entry)
        user_data[user_email].append(emotion_entry)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/emotions/path', methods=['POST', 'OPTIONS'])
def find_path():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        current_emotion = data.get('current_emotion', '')
        target_emotion = data.get('target_emotion', '')
        
        if not current_emotion or not target_emotion:
            return jsonify({"error": "current_emotion and target_emotion are required"}), 400
        
        if current_emotion not in EMOTIONS or target_emotion not in EMOTIONS:
            return jsonify({"error": "Invalid emotion"}), 400
        
        # Find optimal path
        result = pathfinder.find_path(current_emotion, target_emotion)
        
        return jsonify({
            'current_emotion': current_emotion,
            'target_emotion': target_emotion,
            **result
        })
    except Exception as e:
        return jsonify({"error": f"Pathfinding failed: {str(e)}"}), 500

@app.route('/api/emotions/available', methods=['GET'])
def get_emotions():
    return jsonify({"emotions": EMOTIONS})

@app.route('/api/emotions/suggestions', methods=['POST', 'OPTIONS'])
def get_suggestions():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        current_emotion = data.get('current_emotion', '')
        
        suggestions = {
            'sadness': [
                "Listen to uplifting music",
                "Call a friend or family member", 
                "Take a walk in nature",
                "Practice gratitude by writing 3 good things"
            ],
            'anger': [
                "Take 10 deep breaths",
                "Do some physical exercise",
                "Write down your feelings",
                "Count to 10 slowly"
            ],
            'fear': [
                "Practice grounding techniques (5-4-3-2-1 method)",
                "Challenge negative thoughts",
                "Talk to someone you trust",
                "Focus on what you can control"
            ],
            'disgust': [
                "Focus on positive aspects",
                "Practice acceptance",
                "Engage in a pleasant activity",
                "Connect with supportive people"
            ],
            'neutral': [
                "Set a small goal for today",
                "Practice mindfulness",
                "Try something new",
                "Express gratitude"
            ],
            'joy': [
                "Share your happiness with others",
                "Savor the moment",
                "Use this energy for creative activities",
                "Help someone else"
            ],
            'surprise': [
                "Reflect on what surprised you",
                "Consider what you can learn",
                "Share the experience",
                "Embrace the unexpected"
            ]
        }
        
        return jsonify({"suggestions": suggestions.get(current_emotion, [])})
    except Exception as e:
        return jsonify({"error": f"Failed to get suggestions: {str(e)}"}), 500

@app.route('/api/emotions/graph-data/<user_email>', methods=['GET'])
def get_graph_data(user_email):
    try:
        # Create simple graph data for visualization
        nodes = [{'id': emotion, 'label': emotion.title()} for emotion in EMOTIONS]
        
        # Create edges based on common transitions
        edges = []
        common_transitions = [
            ('sadness', 'neutral'), ('neutral', 'joy'),
            ('anger', 'neutral'), ('fear', 'neutral'),
            ('disgust', 'neutral'), ('surprise', 'joy')
        ]
        
        for from_emotion, to_emotion in common_transitions:
            edges.append({
                'from': from_emotion,
                'to': to_emotion,
                'weight': 1
            })
        
        # Add user's emotional history
        history = user_data.get(user_email, [])
        
        return jsonify({
            'nodes': nodes,
            'edges': edges,
            'history': history[-10:]  # Last 10 entries
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get graph data: {str(e)}"}), 500

@app.route('/api/test-algorithm', methods=['GET'])
def test_algorithm():
    """Test endpoint to verify A* algorithm is working"""
    try:
        test_results = []
        
        test_cases = [
            ('sadness', 'joy'),
            ('anger', 'neutral'),
            ('fear', 'joy'),
            ('disgust', 'neutral'),
            ('anger', 'joy'),
            ('fear', 'surprise'),
            ('sadness', 'surprise')
        ]
        
        for start, goal in test_cases:
            result = pathfinder.find_path(start, goal)
            test_results.append({
                'test': f"{start} -> {goal}",
                'path': result['path'],
                'cost': result['total_cost'],
                'success_rate': result['estimated_success_rate'],
                'steps': len(result['path']) - 1
            })
        
        return jsonify({
            "algorithm_tests": test_results,
            "total_tests": len(test_cases),
            "algorithm": "A* Search",
            "average_success_rate": sum(t['success_rate'] for t in test_results) / len(test_results)
        })
    except Exception as e:
        return jsonify({"error": f"Algorithm test failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("🧠 Starting Simple Reflectly AI Backend")
    print("🎯 Focus: Algorithm Development")
    print("📡 API: http://localhost:5000")
    print("🔬 Test endpoint: http://localhost:5000/api/test-algorithm")
    print("✅ CORS enabled for http://localhost:3000")
    app.run(host='0.0.0.0', port=5000, debug=True)
````

## File: frontend/public/index.html
````html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Simple Reflectly AI - Algorithm Development" />
    <title>Simple Reflectly AI</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
````

## File: frontend/src/components/layout/Header.js
````javascript
import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Box,
  Toolbar,
  IconButton,
  Typography,
  Menu,
  Container,
  Avatar,
  Button,
  Tooltip,
  MenuItem,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import MenuIcon from '@mui/icons-material/Menu';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useAuth } from '../../context/AuthContext';
import { useThemeContext } from '../../context/ThemeContext';

const Header = () => {
  const [anchorElNav, setAnchorElNav] = useState(null);
  const [anchorElUser, setAnchorElUser] = useState(null);
  const { isAuthenticated, user, logout } = useAuth();
  const { mode, toggleTheme } = useThemeContext();
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleOpenNavMenu = (event) => {
    setAnchorElNav(event.currentTarget);
  };
  
  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseNavMenu = () => {
    setAnchorElNav(null);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  const handleMenuItemClick = (path) => {
    navigate(path);
    handleCloseNavMenu();
  };

  const handleLogout = () => {
    logout();
    handleCloseUserMenu();
  };

  const pages = isAuthenticated 
    ? [
        { title: 'Journal', path: '/journal' },
        { title: 'Goals', path: '/goals' }
      ]
    : [];

  const settings = isAuthenticated
    ? [
        { title: 'Profile', action: () => { handleCloseUserMenu(); navigate('/profile'); } },
        { title: 'Logout', action: handleLogout }
      ]
    : [
        { title: 'Login', action: () => { handleCloseUserMenu(); navigate('/login'); } },
        { title: 'Register', action: () => { handleCloseUserMenu(); navigate('/register'); } }
      ];

  return (
    <AppBar position="static" color="primary" elevation={1}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          {/* Logo for desktop */}
          <Typography
            variant="h6"
            noWrap
            component={RouterLink}
            to="/"
            sx={{
              mr: 2,
              display: { xs: 'none', md: 'flex' },
              fontWeight: 700,
              color: 'inherit',
              textDecoration: 'none',
            }}
          >
            Reflectly
          </Typography>

          {/* Mobile menu */}
          <Box sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}>
            <IconButton
              size="large"
              aria-label="menu"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleOpenNavMenu}
              color="inherit"
            >
              <MenuIcon />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorElNav}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'left',
              }}
              open={Boolean(anchorElNav)}
              onClose={handleCloseNavMenu}
              sx={{
                display: { xs: 'block', md: 'none' },
              }}
            >
              {pages.map((page) => (
                <MenuItem key={page.title} onClick={() => handleMenuItemClick(page.path)}>
                  <Typography textAlign="center">{page.title}</Typography>
                </MenuItem>
              ))}
            </Menu>
          </Box>

          {/* Logo for mobile */}
          <Typography
            variant="h6"
            noWrap
            component={RouterLink}
            to="/"
            sx={{
              mr: 2,
              display: { xs: 'flex', md: 'none' },
              flexGrow: 1,
              fontWeight: 700,
              color: 'inherit',
              textDecoration: 'none',
            }}
          >
            Reflectly
          </Typography>

          {/* Desktop menu */}
          <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>
            {pages.map((page) => (
              <Button
                key={page.title}
                component={RouterLink}
                to={page.path}
                onClick={handleCloseNavMenu}
                sx={{ my: 2, color: 'white', display: 'block' }}
              >
                {page.title}
              </Button>
            ))}
          </Box>

          {/* Theme toggle button */}
          <Box sx={{ mr: 2 }}>
            <IconButton onClick={toggleTheme} color="inherit">
              {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Box>

          {/* User menu */}
          <Box sx={{ flexGrow: 0 }}>
            <Tooltip title={isAuthenticated ? "Open settings" : "Account"}>
              <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                <Avatar 
                  alt={user?.name || "User"} 
                  src={user?.avatar || "/static/images/avatar/default.jpg"} 
                />
              </IconButton>
            </Tooltip>
            <Menu
              sx={{ mt: '45px' }}
              id="menu-appbar"
              anchorEl={anchorElUser}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorElUser)}
              onClose={handleCloseUserMenu}
            >
              {settings.map((setting) => (
                <MenuItem key={setting.title} onClick={setting.action}>
                  <Typography textAlign="center">{setting.title}</Typography>
                </MenuItem>
              ))}
            </Menu>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;
````

## File: frontend/src/context/AuthContext.js
````javascript
import React, { createContext, useState, useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../utils/axiosConfig';
import jwtDecode from 'jwt-decode';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();
  
  // Check if user is authenticated
  const checkAuth = useCallback(async () => {
    setLoading(true);
    try {
      console.log('checkAuth: Checking authentication status');
      const token = localStorage.getItem('token');
      console.log('checkAuth: Token exists:', !!token);
      
      if (!token) {
        console.log('checkAuth: No token found, user is not authenticated');
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }
      
      // Check if token is expired
      console.log('checkAuth: Decoding token');
      const decodedToken = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      console.log('checkAuth: Token expiration:', new Date(decodedToken.exp * 1000).toLocaleString());
      console.log('checkAuth: Current time:', new Date(currentTime * 1000).toLocaleString());
      
      if (decodedToken.exp < currentTime) {
        console.log('checkAuth: Token is expired');
        localStorage.removeItem('token');
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }
      
      // Set auth header
      console.log('checkAuth: Setting Authorization header');
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Get user data
      console.log('checkAuth: Fetching user data from API');
      const response = await axios.get('/api/auth/user');
      console.log('checkAuth: User data received:', response.data);
      setUser(response.data);
      setIsAuthenticated(true);
      console.log('checkAuth: User authenticated successfully');
    } catch (err) {
      console.error('checkAuth: Authentication error:', err);
      console.error('checkAuth: Error response:', err.response?.data);
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);
  
  // Register user
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/auth/register', userData);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await checkAuth();
      navigate('/journal');
      return true;
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  // Login user
  const login = async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Login attempt with credentials:', credentials);
      const response = await axios.post('/api/auth/login', credentials);
      console.log('Login API response:', response.data);
      const { access_token } = response.data;
      
      console.log('Storing token in localStorage');
      localStorage.setItem('token', access_token);
      console.log('Setting Authorization header');
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      console.log('Checking authentication status');
      await checkAuth();
      console.log('Authentication check completed, navigating to journal');
      navigate('/journal');
      return true;
    } catch (err) {
      console.error('Login error:', err);
      console.error('Error response:', err.response?.data);
      setError(err.response?.data?.message || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  // Logout user
  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setUser(null);
    navigate('/login');
  };
  
  // Clear error
  const clearError = () => {
    setError(null);
  };
  
  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    register,
    login,
    logout,
    checkAuth,
    clearError
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
````

## File: frontend/src/pages/EmotionalJourneyGraph.js
````javascript
import React, { useState, useEffect, useCallback } from 'react';
import axios from '../utils/axiosConfig';

const EmotionalJourneyGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [], history: [] });
  const [currentEmotion, setCurrentEmotion] = useState('');
  const [targetEmotion, setTargetEmotion] = useState('');
  const [pathResult, setPathResult] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [availableEmotions, setAvailableEmotions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userEmail] = useState('demo@reflectly.ai'); // Demo user for AI testing

  // Emotion colors for visualization
  const emotionColors = {
    joy: '#FFD700',
    sadness: '#4169E1', 
    anger: '#DC143C',
    fear: '#9932CC',
    disgust: '#228B22',
    surprise: '#FF69B4',
    neutral: '#808080'
  };

  // Load available emotions on component mount
  useEffect(() => {
    loadAvailableEmotions();
    loadGraphData();
  }, []);

  const loadAvailableEmotions = async () => {
    try {
      const response = await axios.get('/api/emotions/available');
      setAvailableEmotions(response.data.emotions);
      if (response.data.emotions.length > 0) {
        setCurrentEmotion(response.data.emotions[0]);
        setTargetEmotion('joy'); // Default target
      }
    } catch (error) {
      console.error('Error loading emotions:', error);
    }
  };

  const loadGraphData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/emotions/graph-data/${userEmail}`);
      setGraphData(response.data);
    } catch (error) {
      console.error('Error loading graph data:', error);
    } finally {
      setLoading(false);
    }
  };

  const findOptimalPath = async () => {
    if (!currentEmotion || !targetEmotion) return;
    
    try {
      setLoading(true);
      const response = await axios.post('/api/emotions/path', {
        user_email: userEmail,
        current_emotion: currentEmotion,
        target_emotion: targetEmotion,
        max_depth: 10
      });
      setPathResult(response.data);
    } catch (error) {
      console.error('Error finding path:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSuggestions = async () => {
    if (!currentEmotion) return;
    
    try {
      const response = await axios.post('/api/emotions/suggestions', {
        user_email: userEmail,
        current_emotion: currentEmotion
      });
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Error getting suggestions:', error);
    }
  };

  const analyzeText = async (text) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/emotions/analyze', {
        text: text,
        user_email: userEmail
      });
      
      // Update current emotion based on analysis
      setCurrentEmotion(response.data.primary_emotion);
      
      // Reload graph data to show new transition
      await loadGraphData();
      
      return response.data;
    } catch (error) {
      console.error('Error analyzing text:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderGraph = () => {
    const { nodes, edges } = graphData;
    
    if (!nodes.length) {
      return (
        <div className=\"graph-placeholder\">
          <p>No emotional data yet. Try analyzing some text or finding a path!</p>
        </div>
      );
    }

    return (
      <div className=\"emotion-graph\">
        <svg width=\"600\" height=\"400\" viewBox=\"0 0 600 400\">
          {/* Render edges */}
          {edges.map((edge, index) => {
            const fromNode = nodes.find(n => n.id === edge.from);
            const toNode = nodes.find(n => n.id === edge.to);
            if (!fromNode || !toNode) return null;
            
            const fromIndex = nodes.indexOf(fromNode);
            const toIndex = nodes.indexOf(toNode);
            
            // Simple circular layout
            const centerX = 300, centerY = 200, radius = 120;
            const fromAngle = (fromIndex / nodes.length) * 2 * Math.PI;
            const toAngle = (toIndex / nodes.length) * 2 * Math.PI;
            
            const x1 = centerX + radius * Math.cos(fromAngle);
            const y1 = centerY + radius * Math.sin(fromAngle);
            const x2 = centerX + radius * Math.cos(toAngle);
            const y2 = centerY + radius * Math.sin(toAngle);
            
            return (
              <line
                key={index}
                x1={x1} y1={y1} x2={x2} y2={y2}
                stroke=\"#ccc\"
                strokeWidth={Math.min(edge.weight, 5)}
                opacity={0.6}
              />
            );
          })}
          
          {/* Render nodes */}
          {nodes.map((node, index) => {
            const centerX = 300, centerY = 200, radius = 120;
            const angle = (index / nodes.length) * 2 * Math.PI;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            
            const isCurrentEmotion = node.id === currentEmotion;
            const isTargetEmotion = node.id === targetEmotion;
            const isInPath = pathResult && pathResult.path && pathResult.path.includes(node.id);
            
            return (
              <g key={node.id}>
                <circle
                  cx={x} cy={y} r={isCurrentEmotion || isTargetEmotion ? \"25\" : \"20\"}
                  fill={emotionColors[node.id] || '#808080'}
                  stroke={isInPath ? '#ff6b35' : (isCurrentEmotion ? '#000' : '#666')}
                  strokeWidth={isInPath ? \"4\" : (isCurrentEmotion ? \"3\" : \"1\")}
                  opacity={isInPath ? 1 : 0.8}
                />
                <text
                  x={x} y={y + 5}
                  textAnchor=\"middle\"
                  fontSize=\"12\"
                  fontWeight={isCurrentEmotion ? \"bold\" : \"normal\"}
                  fill={isCurrentEmotion ? \"#000\" : \"#333\"}
                >
                  {node.label}
                </text>
                {isCurrentEmotion && (
                  <text x={x} y={y - 35} textAnchor=\"middle\" fontSize=\"10\" fill=\"#000\">
                    CURRENT
                  </text>
                )}
                {isTargetEmotion && (
                  <text x={x} y={y - 35} textAnchor=\"middle\" fontSize=\"10\" fill=\"#000\">
                    TARGET
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    );
  };

  const renderPathResult = () => {
    if (!pathResult) return null;
    
    return (
      <div className=\"path-result\">
        <h3>🎯 Optimal Emotional Path</h3>
        <div className=\"path-info\">
          <p><strong>Path:</strong> {pathResult.path ? pathResult.path.join(' → ') : 'No path found'}</p>
          <p><strong>Estimated Success Rate:</strong> {(pathResult.estimated_success_rate * 100).toFixed(1)}%</p>
          <p><strong>Total Cost:</strong> {pathResult.total_cost?.toFixed(2)}</p>
        </div>
        
        {pathResult.actions && pathResult.actions.length > 0 && (
          <div className=\"path-actions\">
            <h4>📋 Recommended Actions:</h4>
            {pathResult.actions.map((action, index) => (
              <div key={index} className=\"action-step\">
                <div className=\"action-transition\">
                  <strong>{action.from} → {action.to}</strong>
                </div>
                <div className=\"action-description\">{action.action}</div>
                <div className=\"action-success\">
                  Success Rate: {(action.success_rate * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className=\"emotional-journey-page\">
      <div className=\"page-header\">
        <h1>🧠 AI Emotional Pathfinding</h1>
        <p>Discover optimal paths between emotional states using A* search algorithm</p>
      </div>

      <div className=\"ai-controls\">
        <div className=\"pathfinding-section\">
          <h2>🔍 Find Optimal Path</h2>
          <div className=\"emotion-selectors\">
            <div className=\"selector-group\">
              <label>Current Emotion:</label>
              <select 
                value={currentEmotion} 
                onChange={(e) => setCurrentEmotion(e.target.value)}
              >
                {availableEmotions.map(emotion => (
                  <option key={emotion} value={emotion}>{emotion}</option>
                ))}
              </select>
            </div>
            
            <div className=\"selector-group\">
              <label>Target Emotion:</label>
              <select 
                value={targetEmotion} 
                onChange={(e) => setTargetEmotion(e.target.value)}
              >
                {availableEmotions.map(emotion => (
                  <option key={emotion} value={emotion}>{emotion}</option>
                ))}
              </select>
            </div>
            
            <button 
              onClick={findOptimalPath}
              disabled={loading || !currentEmotion || !targetEmotion}
              className=\"find-path-btn\"
            >
              {loading ? 'Finding Path...' : '🎯 Find Optimal Path'}
            </button>
          </div>
        </div>

        <div className=\"text-analysis-section\">
          <h2>📝 Analyze Text</h2>
          <div className=\"text-input-group\">
            <textarea
              placeholder=\"Enter text to analyze emotional state...\"
              rows=\"3\"
              id=\"text-input\"
            />
            <button 
              onClick={() => {
                const text = document.getElementById('text-input').value;
                if (text.trim()) {
                  analyzeText(text);
                  document.getElementById('text-input').value = '';
                }
              }}
              disabled={loading}
              className=\"analyze-btn\"
            >
              {loading ? 'Analyzing...' : '🔬 Analyze Emotion'}
            </button>
          </div>
        </div>

        <button 
          onClick={getSuggestions}
          disabled={loading || !currentEmotion}
          className=\"suggestions-btn\"
        >
          💡 Get Suggestions for {currentEmotion}
        </button>
      </div>

      <div className=\"visualization-section\">
        <h2>🗺️ Emotional Graph Visualization</h2>
        {loading ? (
          <div className=\"loading\">Loading graph data...</div>
        ) : (
          renderGraph()
        )}
      </div>

      {pathResult && renderPathResult()}

      {suggestions.length > 0 && (
        <div className=\"suggestions-section\">
          <h3>💡 Personalized Suggestions</h3>
          <ul className=\"suggestions-list\">
            {suggestions.map((suggestion, index) => (
              <li key={index} className=\"suggestion-item\">
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className=\"graph-legend\">
        <h3>🎨 Graph Legend</h3>
        <div className=\"legend-items\">
          {Object.entries(emotionColors).map(([emotion, color]) => (
            <div key={emotion} className=\"legend-item\">
              <div 
                className=\"legend-color\" 
                style={{ backgroundColor: color }}
              ></div>
              <span>{emotion}</span>
            </div>
          ))}
        </div>
      </div>

      <style jsx>{`
        .emotional-journey-page {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .page-header {
          text-align: center;
          margin-bottom: 30px;
        }

        .page-header h1 {
          color: #2c3e50;
          margin-bottom: 10px;
        }

        .ai-controls {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 30px;
        }

        .pathfinding-section, .text-analysis-section {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #e9ecef;
        }

        .emotion-selectors {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .selector-group {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .selector-group label {
          font-weight: 600;
          color: #495057;
        }

        .selector-group select {
          padding: 8px;
          border: 1px solid #ced4da;
          border-radius: 5px;
          font-size: 14px;
        }

        .find-path-btn, .analyze-btn, .suggestions-btn {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 25px;
          cursor: pointer;
          font-weight: 600;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .find-path-btn:hover, .analyze-btn:hover, .suggestions-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .find-path-btn:disabled, .analyze-btn:disabled, .suggestions-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .suggestions-btn {
          grid-column: 1 / -1;
          justify-self: center;
          margin-top: 10px;
        }

        .text-input-group {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .text-input-group textarea {
          padding: 10px;
          border: 1px solid #ced4da;
          border-radius: 5px;
          resize: vertical;
          font-family: inherit;
        }

        .visualization-section {
          background: #ffffff;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #e9ecef;
          margin-bottom: 20px;
          text-align: center;
        }

        .emotion-graph {
          display: flex;
          justify-content: center;
          margin: 20px 0;
        }

        .graph-placeholder {
          padding: 60px;
          color: #6c757d;
          font-style: italic;
        }

        .loading {
          padding: 40px;
          color: #6c757d;
          font-style: italic;
        }

        .path-result {
          background: #e8f5e8;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #c3e6c3;
          margin-bottom: 20px;
        }

        .path-info {
          margin-bottom: 15px;
        }

        .path-info p {
          margin: 5px 0;
        }

        .path-actions {
          margin-top: 15px;
        }

        .action-step {
          background: #f8f9fa;
          padding: 12px;
          margin: 8px 0;
          border-radius: 5px;
          border-left: 4px solid #28a745;
        }

        .action-transition {
          font-weight: 600;
          color: #495057;
          margin-bottom: 5px;
        }

        .action-description {
          color: #343a40;
          margin-bottom: 5px;
        }

        .action-success {
          font-size: 12px;
          color: #28a745;
          font-weight: 600;
        }

        .suggestions-section {
          background: #fff3cd;
          padding: 20px;
          border-radius: 10px;
          border: 1px solid #ffeaa7;
          margin-bottom: 20px;
        }

        .suggestions-list {
          list-style: none;
          padding: 0;
        }

        .suggestion-item {
          background: #ffffff;
          padding: 12px;
          margin: 8px 0;
          border-radius: 5px;
          border-left: 4px solid #ffc107;
        }

        .graph-legend {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 10px;
          border: 1px solid #e9ecef;
        }

        .legend-items {
          display: flex;
          flex-wrap: wrap;
          gap: 15px;
          margin-top: 10px;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .legend-color {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 1px solid #ccc;
        }

        @media (max-width: 768px) {
          .ai-controls {
            grid-template-columns: 1fr;
          }
          
          .emotion-selectors {
            gap: 10px;
          }
          
          .legend-items {
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default EmotionalJourneyGraph;
````

## File: frontend/src/pages/Profile.js
````javascript
import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Avatar,
  Button,
  Grid,
  TextField,
  Divider,
  CircularProgress,
  Alert,
  Snackbar,
  Card,
  CardContent,
  IconButton,
  Tabs,
  Tab,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import MoodIcon from '@mui/icons-material/Mood';
import TodayIcon from '@mui/icons-material/Today';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import RouteIcon from '@mui/icons-material/Route';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, BarElement } from 'chart.js';
import { Pie, Line, Bar } from 'react-chartjs-2';
import { format, subDays } from 'date-fns';
import axios from '../utils/axiosConfig';
import { useAuth } from '../context/AuthContext';
import EmotionalJourneyGraph from './EmotionalJourneyGraph';

// Register ChartJS components
ChartJS.register(
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title
);

const Profile = () => {
  const [tabValue, setTabValue] = useState(0);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [userData, setUserData] = useState({
    name: '',
    email: '',
    bio: '',
    password: '',
    confirmPassword: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user, updateUser } = useAuth();
  
  useEffect(() => {
    if (user) {
      setUserData({
        name: user.name || '',
        email: user.email || '',
        bio: user.bio || '',
        password: '',
        confirmPassword: ''
      });
    }
  }, [user]);
  
  useEffect(() => {
    fetchStats();
    console.log('Current tab value:', tabValue);
  }, []);
  
  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/user/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching user stats:', err);
      setSnackbar({
        open: true,
        message: 'Failed to load user statistics',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleTabChange = (event, newValue) => {
    console.log('Changing tab to:', newValue);
    setTabValue(newValue);
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserData({ ...userData, [name]: value });
    
    // Clear field error when user types
    if (formErrors[name]) {
      setFormErrors({ ...formErrors, [name]: '' });
    }
  };
  
  const validateForm = () => {
    const errors = {};
    
    if (!userData.name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (userData.password) {
      if (userData.password.length < 8) {
        errors.password = 'Password must be at least 8 characters';
      }
      
      if (userData.password !== userData.confirmPassword) {
        errors.confirmPassword = 'Passwords do not match';
      }
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Only include password if it was changed
      const dataToUpdate = {
        name: userData.name,
        bio: userData.bio
      };
      
      if (userData.password) {
        dataToUpdate.password = userData.password;
      }
      
      await updateUser(dataToUpdate);
      
      setSnackbar({
        open: true,
        message: 'Profile updated successfully!',
        severity: 'success'
      });
      
      setEditing(false);
      
      // Clear password fields
      setUserData({
        ...userData,
        password: '',
        confirmPassword: ''
      });
    } catch (err) {
      console.error('Error updating profile:', err);
      setSnackbar({
        open: true,
        message: 'Failed to update profile. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };
  
  const toggleEditing = () => {
    if (editing) {
      // Cancel editing - reset form
      setUserData({
        name: user.name || '',
        email: user.email || '',
        bio: user.bio || '',
        password: '',
        confirmPassword: ''
      });
      setFormErrors({});
    }
    setEditing(!editing);
  };
  
  // Generate sample data for charts if real data is not available
  const generateSampleData = () => {
    if (stats) return stats;
    
    // Sample data for demonstration
    const emotions = {
      joy: 35,
      sadness: 15,
      anger: 10,
      fear: 8,
      surprise: 12,
      neutral: 20
    };
    
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = subDays(new Date(), i);
      return format(date, 'MMM dd');
    }).reverse();
    
    const entriesPerDay = last7Days.map(() => Math.floor(Math.random() * 5));
    
    return {
      total_entries: 87,
      streak_days: 12,
      avg_entries_per_day: 2.3,
      emotions,
      entries_timeline: {
        dates: last7Days,
        counts: entriesPerDay
      },
      emotion_timeline: {
        dates: last7Days,
        emotions: {
          joy: last7Days.map(() => Math.floor(Math.random() * 100)),
          sadness: last7Days.map(() => Math.floor(Math.random() * 100)),
          anger: last7Days.map(() => Math.floor(Math.random() * 100))
        }
      }
    };
  };
  
  const sampleData = generateSampleData();
  
  // Prepare chart data
  const emotionChartData = {
    labels: Object.keys(sampleData.emotions).map(emotion => 
      emotion.charAt(0).toUpperCase() + emotion.slice(1)
    ),
    datasets: [
      {
        data: Object.values(sampleData.emotions),
        backgroundColor: [
          '#4CAF50', // joy
          '#5C6BC0', // sadness
          '#EF5350', // anger
          '#FFA726', // fear
          '#42A5F5', // surprise
          '#BDBDBD'  // neutral
        ],
        borderWidth: 1
      }
    ]
  };
  
  const entriesTimelineData = {
    labels: sampleData.entries_timeline.dates,
    datasets: [
      {
        label: 'Journal Entries',
        data: sampleData.entries_timeline.counts,
        backgroundColor: theme.palette.primary.main,
        borderColor: theme.palette.primary.main,
        borderWidth: 2,
        tension: 0.4
      }
    ]
  };
  
  const emotionTimelineData = {
    labels: sampleData.emotion_timeline.dates,
    datasets: [
      {
        label: 'Joy',
        data: sampleData.emotion_timeline.emotions.joy,
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        borderColor: '#4CAF50',
        borderWidth: 2,
        tension: 0.4,
        fill: true
      },
      {
        label: 'Sadness',
        data: sampleData.emotion_timeline.emotions.sadness,
        backgroundColor: 'rgba(92, 107, 192, 0.2)',
        borderColor: '#5C6BC0',
        borderWidth: 2,
        tension: 0.4,
        fill: true
      },
      {
        label: 'Anger',
        data: sampleData.emotion_timeline.emotions.anger,
        backgroundColor: 'rgba(239, 83, 80, 0.2)',
        borderColor: '#EF5350',
        borderWidth: 2,
        tension: 0.4,
        fill: true
      }
    ]
  };
  
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  };
  
  const lineChartOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={4}>
        {/* Profile Section */}
        <Grid item xs={12} md={4}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3, 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              borderRadius: 2
            }}
          >
            <Avatar 
              sx={{ 
                width: 120, 
                height: 120, 
                mb: 2,
                bgcolor: theme.palette.primary.main,
                fontSize: '3rem'
              }}
            >
              {userData.name ? userData.name.charAt(0).toUpperCase() : 'U'}
            </Avatar>
            
            {!editing ? (
              <Box sx={{ width: '100%', textAlign: 'center' }}>
                <Typography variant="h5" gutterBottom>
                  {userData.name || 'User'}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {userData.email}
                </Typography>
                
                {userData.bio && (
                  <Typography variant="body1" sx={{ mt: 2, mb: 2 }}>
                    {userData.bio}
                  </Typography>
                )}
                
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={toggleEditing}
                  sx={{ mt: 2 }}
                >
                  Edit Profile
                </Button>
              </Box>
            ) : (
              <Box component="form" sx={{ width: '100%', mt: 2 }}>
                <TextField
                  fullWidth
                  label="Name"
                  name="name"
                  value={userData.name}
                  onChange={handleInputChange}
                  margin="normal"
                  error={!!formErrors.name}
                  helperText={formErrors.name}
                  disabled={loading}
                />
                
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  value={userData.email}
                  disabled
                  margin="normal"
                />
                
                <TextField
                  fullWidth
                  label="Bio"
                  name="bio"
                  value={userData.bio}
                  onChange={handleInputChange}
                  margin="normal"
                  multiline
                  rows={3}
                  disabled={loading}
                />
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle2" gutterBottom>
                  Change Password (leave blank to keep current)
                </Typography>
                
                <TextField
                  fullWidth
                  label="New Password"
                  name="password"
                  type="password"
                  value={userData.password}
                  onChange={handleInputChange}
                  margin="normal"
                  error={!!formErrors.password}
                  helperText={formErrors.password}
                  disabled={loading}
                />
                
                <TextField
                  fullWidth
                  label="Confirm New Password"
                  name="confirmPassword"
                  type="password"
                  value={userData.confirmPassword}
                  onChange={handleInputChange}
                  margin="normal"
                  error={!!formErrors.confirmPassword}
                  helperText={formErrors.confirmPassword}
                  disabled={loading}
                />
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
                  <Button
                    variant="outlined"
                    startIcon={<CancelIcon />}
                    onClick={toggleEditing}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  
                  <Button
                    variant="contained"
                    startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
                    onClick={handleSubmit}
                    disabled={loading}
                  >
                    Save Changes
                  </Button>
                </Box>
              </Box>
            )}
          </Paper>
          
          {/* Stats Cards */}
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={6}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <TodayIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h4">{sampleData.total_entries}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Entries
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={6}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <TrendingUpIcon color="secondary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h4">{sampleData.streak_days}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Day Streak
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <AccessTimeIcon color="info" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h4">{sampleData.avg_entries_per_day}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg. Entries Per Day
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
        
        {/* Analytics Section */}
        <Grid item xs={12} md={8}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3, 
              borderRadius: 2,
              height: '100%'
            }}
          >
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
              <Tabs 
                value={tabValue} 
                onChange={handleTabChange}
                aria-label="analytics tabs"
                variant="scrollable"
                scrollButtons="auto"
                sx={{ maxWidth: '100%', overflowX: 'auto' }}
              >
                <Tab label="Emotions" icon={<MoodIcon />} iconPosition="start" />
                <Tab label="Journal Activity" icon={<TodayIcon />} iconPosition="start" />
                <Tab label="Emotion Trends" icon={<TrendingUpIcon />} iconPosition="start" />
                <Tab label="Emotional Journey" icon={<RouteIcon />} iconPosition="start" />
              </Tabs>
            </Box>
            
            {/* Emotions Tab */}
            {tabValue === 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Your Emotion Distribution
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  This chart shows the distribution of emotions detected in your journal entries.
                </Typography>
                
                <Box sx={{ height: 300, mt: 4 }}>
                  <Pie data={emotionChartData} options={chartOptions} />
                </Box>
              </Box>
            )}
            
            {/* Journal Activity Tab */}
            {tabValue === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Your Journaling Activity
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  This chart shows your journaling frequency over the past week.
                </Typography>
                
                <Box sx={{ height: 300, mt: 4 }}>
                  <Bar data={entriesTimelineData} options={lineChartOptions} />
                </Box>
              </Box>
            )}
            
            {/* Emotion Trends Tab */}
            {tabValue === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Your Emotion Trends
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  This chart shows how your emotions have changed over time.
                </Typography>
                
                <Box sx={{ height: 300, mt: 4 }}>
                  <Line data={emotionTimelineData} options={lineChartOptions} />
                </Box>
              </Box>
            )}
            
            {/* Emotional Journey Tab */}
            {tabValue === 3 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Your Emotional Journey
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  This is a placeholder for the Emotional Journey Graph.
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Profile;
````

## File: frontend/src/index.js
````javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
````

## File: frontend/src/IntelligentAgentApp.js
````javascript
import React, { useState, useEffect } from 'react';

const IntelligentAgentApp = () => {
  const [inputText, setInputText] = useState('');
  const [conversation, setConversation] = useState([]);
  const [memoryMap, setMemoryMap] = useState({ nodes: [], edges: [] });
  const [memoryStats, setMemoryStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [showingStepsForm, setShowingStepsForm] = useState(false);
  const [currentExperienceId, setCurrentExperienceId] = useState('');
  const [stepsInput, setStepsInput] = useState(['']);
  const [backendStatus, setBackendStatus] = useState('checking');

  // Try proxy first, fallback to direct API
  const API_BASE = process.env.NODE_ENV === 'development' ? 'http://localhost:5000/api' : '/api';

  // Emotion colors for map visualization
  const emotionColors = {
    happy: '#4CAF50',      // Green
    sad: '#2196F3',        // Blue  
    anxious: '#FF9800',    // Orange
    angry: '#F44336',      // Red
    confused: '#9C27B0',   // Purple
    tired: '#607D8B',      // Blue Grey
    neutral: '#9E9E9E'     // Grey
  };

  useEffect(() => {
    checkBackendStatus();
  }, []);

  const checkBackendStatus = async () => {
    try {
      // Try direct connection first
      let response = await fetch('http://localhost:5000/api/health');
      let apiBase = 'http://localhost:5000/api';
      
      if (!response.ok) {
        // Try proxy
        response = await fetch('/api/health');
        apiBase = '/api';
      }
      
      if (response.ok) {
        const data = await response.json();
        setBackendStatus('connected');
        console.log('✅ Backend connected:', data);
        
        // Load initial data
        await loadMemoryMap(apiBase);
        await loadMemoryStats(apiBase);
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      console.error('❌ Backend connection failed:', error);
      setBackendStatus('error');
    }
  };

  const makeApiCall = async (endpoint, options = {}) => {
    // Try direct connection first, then proxy
    const urls = [
      `http://localhost:5000/api${endpoint}`,
      `/api${endpoint}`
    ];
    
    for (const url of urls) {
      try {
        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers
          }
        });
        
        if (response.ok) {
          return response;
        }
      } catch (error) {
        console.log(`Failed to connect to ${url}:`, error.message);
      }
    }
    
    throw new Error('Could not connect to backend');
  };

  const loadMemoryMap = async (apiBase = API_BASE) => {
    try {
      const response = await makeApiCall('/memory-map');
      if (response.ok) {
        const data = await response.json();
        setMemoryMap(data);
      }
    } catch (error) {
      console.error('Error loading memory map:', error);
    }
  };

  const loadMemoryStats = async (apiBase = API_BASE) => {
    try {
      const response = await makeApiCall('/memory-stats');
      if (response.ok) {
        const data = await response.json();
        setMemoryStats(data);
      }
    } catch (error) {
      console.error('Error loading memory stats:', error);
    }
  };

  const processInput = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    try {
      const response = await makeApiCall('/process-input', {
        method: 'POST',
        body: JSON.stringify({
          text: inputText,
          user_id: 'user1'
        })
      });

      if (response.ok) {
        const agentResponse = await response.json();
        
        // Add user input and agent response to conversation
        setConversation(prev => [
          ...prev,
          {
            type: 'user',
            text: inputText,
            timestamp: new Date().toLocaleTimeString()
          },
          {
            type: 'agent',
            ...agentResponse,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);

        // Clear input
        setInputText('');

        // If agent asks for steps, show steps form
        if (agentResponse.type === 'ask_for_steps') {
          setShowingStepsForm(true);
          setCurrentExperienceId(agentResponse.experience_id);
          setStepsInput(['']);
        }

        // Reload memory map and stats
        await loadMemoryMap();
        await loadMemoryStats();
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error processing input:', error);
      
      // Add error message to conversation
      setConversation(prev => [
        ...prev,
        {
          type: 'user',
          text: inputText,
          timestamp: new Date().toLocaleTimeString()
        },
        {
          type: 'agent',
          message: `❌ Sorry, I couldn't process your input. Error: ${error.message}. Make sure the backend is running on port 5000.`,
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
      
      setInputText('');
    } finally {
      setLoading(false);
    }
  };

  const saveSteps = async () => {
    const steps = stepsInput.filter(step => step.trim() !== '');
    if (steps.length === 0) return;

    setLoading(true);
    try {
      const response = await makeApiCall('/save-steps', {
        method: 'POST',
        body: JSON.stringify({
          experience_id: currentExperienceId,
          steps: steps
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        // Add confirmation to conversation
        setConversation(prev => [
          ...prev,
          {
            type: 'agent',
            message: result.message,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);

        // Clear steps form
        setShowingStepsForm(false);
        setCurrentExperienceId('');
        setStepsInput(['']);

        // Reload memory map and stats
        await loadMemoryMap();
        await loadMemoryStats();
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error saving steps:', error);
      alert(`Failed to save steps: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const addStepInput = () => {
    setStepsInput(prev => [...prev, '']);
  };

  const updateStepInput = (index, value) => {
    setStepsInput(prev => {
      const newSteps = [...prev];
      newSteps[index] = value;
      return newSteps;
    });
  };

  const removeStepInput = (index) => {
    setStepsInput(prev => prev.filter((_, i) => i !== index));
  };

  const resetMemory = async () => {
    if (window.confirm('Are you sure you want to reset the memory map? This will clear all learned experiences.')) {
      try {
        const response = await makeApiCall('/reset-memory', {
          method: 'POST'
        });

        if (response.ok) {
          setConversation([]);
          setMemoryMap({ nodes: [], edges: [] });
          setMemoryStats({});
          alert('Memory map reset successfully!');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        console.error('Error resetting memory:', error);
        alert(`Failed to reset memory: ${error.message}`);
      }
    }
  };

  const renderBackendStatus = () => {
    const statusInfo = {
      checking: { color: '#ffc107', text: 'Checking backend...', icon: '🔍' },
      connected: { color: '#28a745', text: 'Backend connected', icon: '✅' },
      error: { color: '#dc3545', text: 'Backend not connected', icon: '❌' }
    };

    const status = statusInfo[backendStatus] || statusInfo.error;

    return (
      <div style={{
        background: status.color,
        color: 'white',
        padding: '8px 15px',
        borderRadius: '5px',
        margin: '10px 0',
        textAlign: 'center',
        fontSize: '14px',
        fontWeight: 'bold'
      }}>
        {status.icon} {status.text}
        {backendStatus === 'error' && (
          <div style={{fontSize: '12px', marginTop: '5px', fontWeight: 'normal'}}>
            Make sure to run: ./start-agent.sh or python backend/intelligent_agent.py
          </div>
        )}
      </div>
    );
  };

  const renderMemoryMap = () => {
    const { nodes, edges } = memoryMap;
    
    if (!nodes.length) {
      return (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          color: '#666',
          fontStyle: 'italic'
        }}>
          No experiences yet. Start by sharing how you're feeling!
        </div>
      );
    }

    // Simple circular layout
    const centerX = 250;
    const centerY = 200;
    const radius = 120;
    const nodePositions = {};

    // Position nodes in a circle
    nodes.forEach((node, index) => {
      const angle = (index / nodes.length) * 2 * Math.PI;
      nodePositions[node.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });

    return (
      <div style={{ position: 'relative', width: '500px', height: '400px', border: '1px solid #ddd', borderRadius: '8px', background: '#f9f9f9' }}>
        <svg width="500" height="400">
          {/* Render edges */}
          {edges.map((edge, index) => {
            const fromPos = nodePositions[edge.from];
            const toPos = nodePositions[edge.to];
            if (!fromPos || !toPos) return null;

            return (
              <g key={index}>
                <line
                  x1={fromPos.x}
                  y1={fromPos.y}
                  x2={toPos.x}
                  y2={toPos.y}
                  stroke="#999"
                  strokeWidth={Math.min(edge.weight + 1, 5)}
                  opacity={0.7}
                />
                <text
                  x={(fromPos.x + toPos.x) / 2}
                  y={(fromPos.y + toPos.y) / 2}
                  fill="#666"
                  fontSize="10"
                  textAnchor="middle"
                >
                  {edge.actions}
                </text>
              </g>
            );
          })}

          {/* Render nodes */}
          {nodes.map((node) => {
            const pos = nodePositions[node.id];
            const color = emotionColors[node.id] || '#999';
            
            return (
              <g key={node.id}>
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={20 + (node.count * 2)}
                  fill={color}
                  stroke="#fff"
                  strokeWidth="2"
                  opacity={0.8}
                />
                <text
                  x={pos.x}
                  y={pos.y + 4}
                  fill="#fff"
                  fontSize="12"
                  fontWeight="bold"
                  textAnchor="middle"
                >
                  {node.label}
                </text>
                <text
                  x={pos.x}
                  y={pos.y + 35}
                  fill="#333"
                  fontSize="10"
                  textAnchor="middle"
                >
                  ({node.count})
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    );
  };

  const renderConversation = () => {
    return (
      <div style={{
        height: '400px',
        overflowY: 'auto',
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '15px',
        background: '#fff',
        marginBottom: '15px'
      }}>
        {conversation.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#666', fontStyle: 'italic', marginTop: '150px' }}>
            👋 Hi! I'm your intelligent agent. Tell me how you're feeling and I'll learn from your experiences to help you better.
            <br /><br />
            <div style={{ fontSize: '12px', color: '#999' }}>
              {backendStatus === 'error' ? 
                '⚠️ Make sure to start the backend first!' : 
                '✅ Ready to learn from your experiences!'
              }
            </div>
          </div>
        ) : (
          conversation.map((message, index) => (
            <div key={index} style={{
              marginBottom: '15px',
              display: 'flex',
              flexDirection: message.type === 'user' ? 'row-reverse' : 'row'
            }}>
              <div style={{
                maxWidth: '70%',
                padding: '10px 15px',
                borderRadius: '18px',
                background: message.type === 'user' ? '#007bff' : '#f1f1f1',
                color: message.type === 'user' ? '#fff' : '#333'
              }}>
                <div>{message.message || message.text}</div>
                <div style={{ fontSize: '11px', opacity: 0.7, marginTop: '5px' }}>
                  {message.timestamp}
                </div>
                {message.suggestions && message.suggestions.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <strong>💡 Suggestions:</strong>
                    <ul style={{ margin: '5px 0', paddingLeft: '15px' }}>
                      {message.suggestions.map((suggestion, i) => (
                        <li key={i} style={{ marginBottom: '3px' }}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    );
  };

  const renderStepsForm = () => {
    if (!showingStepsForm) return null;

    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}>
        <div style={{
          background: '#fff',
          padding: '30px',
          borderRadius: '12px',
          maxWidth: '500px',
          width: '90%',
          maxHeight: '80vh',
          overflowY: 'auto'
        }}>
          <h3 style={{ marginTop: 0, color: '#4CAF50' }}>🌟 Share Your Success Steps!</h3>
          <p>What specific steps or actions led to this positive feeling? This helps me learn and suggest similar actions to help in the future.</p>
          
          {stepsInput.map((step, index) => (
            <div key={index} style={{ marginBottom: '10px', display: 'flex', gap: '10px' }}>
              <input
                type="text"
                value={step}
                onChange={(e) => updateStepInput(index, e.target.value)}
                placeholder={`Step ${index + 1}...`}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px'
                }}
              />
              {stepsInput.length > 1 && (
                <button
                  onClick={() => removeStepInput(index)}
                  style={{
                    padding: '8px',
                    background: '#f44336',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer'
                  }}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
          
          <button
            onClick={addStepInput}
            style={{
              padding: '8px 16px',
              background: '#4CAF50',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            + Add Step
          </button>
          
          <div style={{ marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button
              onClick={() => setShowingStepsForm(false)}
              style={{
                padding: '10px 20px',
                background: '#666',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              onClick={saveSteps}
              disabled={loading || stepsInput.every(step => !step.trim())}
              style={{
                padding: '10px 20px',
                background: '#4CAF50',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                opacity: (loading || stepsInput.every(step => !step.trim())) ? 0.6 : 1
              }}
            >
              {loading ? 'Saving...' : 'Save Steps'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ textAlign: 'center', color: '#333', marginBottom: '10px' }}>
        🤖 Intelligent Agent with Memory Map
      </h1>
      <p style={{ textAlign: 'center', color: '#666', marginBottom: '20px' }}>
        An AI that learns from your experiences and uses A* search to suggest helpful actions
      </p>

      {renderBackendStatus()}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
        {/* Left Side - Conversation */}
        <div>
          <h2 style={{ color: '#333', marginBottom: '15px' }}>💬 Conversation</h2>
          
          {renderConversation()}
          
          {/* Input Area */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && processInput()}
              placeholder="Tell me how you're feeling... (e.g., 'I'm feeling really happy today' or 'I'm sad and stressed')"
              style={{
                flex: 1,
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                fontSize: '14px'
              }}
              disabled={backendStatus !== 'connected'}
            />
            <button
              onClick={processInput}
              disabled={loading || !inputText.trim() || backendStatus !== 'connected'}
              style={{
                padding: '12px 24px',
                background: backendStatus === 'connected' ? '#007bff' : '#ccc',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: backendStatus === 'connected' ? 'pointer' : 'not-allowed',
                fontWeight: 'bold'
              }}
            >
              {loading ? '🤔' : '💭'}
            </button>
          </div>

          {/* Example inputs */}
          <div style={{ marginTop: '15px', fontSize: '12px', color: '#666' }}>
            <strong>Try these examples:</strong>
            <div style={{ marginTop: '5px' }}>
              • "I'm feeling really happy and excited!"
            </div>
            <div>
              • "I'm sad and don't know what to do"
            </div>
            <div>
              • "I'm feeling anxious about work"
            </div>
          </div>
        </div>

        {/* Right Side - Memory Map */}
        <div>
          <h2 style={{ color: '#333', marginBottom: '15px' }}>🗺️ Memory Map</h2>
          
          {renderMemoryMap()}
          
          {/* Memory Stats */}
          <div style={{
            marginTop: '15px',
            padding: '15px',
            background: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #e9ecef'
          }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>📊 Learning Stats</h4>
            <div style={{ fontSize: '14px', color: '#666' }}>
              <div>Total Experiences: <strong>{memoryStats.total_experiences || 0}</strong></div>
              <div>Emotions Learned: <strong>{memoryStats.emotions_learned || 0}</strong></div>
              <div>Transitions Learned: <strong>{memoryStats.transitions_learned || 0}</strong></div>
            </div>
          </div>

          {/* Legend */}
          <div style={{
            marginTop: '15px',
            padding: '10px',
            background: '#fff',
            borderRadius: '8px',
            border: '1px solid #ddd'
          }}>
            <h5 style={{ margin: '0 0 8px 0', color: '#333' }}>🎨 Map Legend</h5>
            <div style={{ fontSize: '12px', color: '#666' }}>
              <div>• Circle size = Number of experiences</div>
              <div>• Line thickness = Number of learned transitions</div>
              <div>• Numbers on lines = Available action suggestions</div>
            </div>
          </div>

          {/* Reset Button */}
          <button
            onClick={resetMemory}
            disabled={backendStatus !== 'connected'}
            style={{
              marginTop: '15px',
              padding: '8px 16px',
              background: backendStatus === 'connected' ? '#dc3545' : '#ccc',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: backendStatus === 'connected' ? 'pointer' : 'not-allowed',
              fontSize: '12px'
            }}
          >
            🗑️ Reset Memory
          </button>
        </div>
      </div>

      {/* How it Works */}
      <div style={{
        marginTop: '40px',
        padding: '20px',
        background: '#e8f5e8',
        borderRadius: '10px',
        border: '1px solid #c3e6c3'
      }}>
        <h3 style={{ color: '#2e7d32', marginTop: 0 }}>🧠 How the Intelligent Agent Works</h3>
        <div style={{ color: '#1b5e20', lineHeight: 1.6 }}>
          <p><strong>😊 When you share positive emotions:</strong> The agent asks what steps led to that feeling and saves them to its memory map.</p>
          <p><strong>😢 When you share negative emotions:</strong> The agent uses A* search through its learned experiences to suggest actions that previously helped transition to positive emotions.</p>
          <p><strong>🗺️ Memory Map Evolution:</strong> Each interaction builds the emotional graph, creating connections between emotions and the actions that successfully bridge them.</p>
          <p><strong>🎯 A* Search:</strong> The algorithm finds optimal paths through emotional states, suggesting the most effective sequences of actions based on past successes.</p>
        </div>
      </div>

      {renderStepsForm()}
    </div>
  );
};

export default IntelligentAgentApp;
````

## File: frontend/src/SimpleAIDemo.js
````javascript
import React, { useState, useEffect } from 'react';

const SimpleAIDemo = () => {
  const [emotions, setEmotions] = useState([]);
  const [currentEmotion, setCurrentEmotion] = useState('');
  const [targetEmotion, setTargetEmotion] = useState('');
  const [pathResult, setPathResult] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [testText, setTestText] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking');

  // Use relative URLs - React proxy will forward to backend
  const API_BASE = '/api';

  // Emotion colors for visualization
  const emotionColors = {
    joy: '#FFD700',
    sadness: '#4169E1',
    anger: '#DC143C',
    fear: '#9932CC',
    disgust: '#228B22',
    surprise: '#FF69B4',
    neutral: '#808080'
  };

  useEffect(() => {
    checkBackendStatus();
    loadEmotions();
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      if (response.ok) {
        const data = await response.json();
        setBackendStatus('connected');
        console.log('✅ Backend connected:', data);
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      setBackendStatus('error');
      console.error('❌ Backend connection failed:', error);
    }
  };

  const loadEmotions = async () => {
    try {
      const response = await fetch(`${API_BASE}/emotions/available`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setEmotions(data.emotions);
      if (data.emotions.length > 0) {
        setCurrentEmotion(data.emotions[0]);
        setTargetEmotion('joy');
      }
    } catch (error) {
      console.error('Error loading emotions:', error);
      setBackendStatus('error');
    }
  };

  const analyzeText = async () => {
    if (!testText.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/emotions/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: testText,
          user_email: 'demo@example.com'
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setAnalysisResult(data);
      setCurrentEmotion(data.primary_emotion);
      console.log('✅ Emotion analysis result:', data);
    } catch (error) {
      console.error('Error analyzing text:', error);
      alert('Failed to analyze text. Make sure the backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const findPath = async () => {
    if (!currentEmotion || !targetEmotion) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/emotions/path`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_emotion: currentEmotion,
          target_emotion: targetEmotion
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setPathResult(data);
      console.log('✅ Path finding result:', data);
    } catch (error) {
      console.error('Error finding path:', error);
      alert('Failed to find path. Make sure the backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const getSuggestions = async () => {
    if (!currentEmotion) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/emotions/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_emotion: currentEmotion })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setSuggestions(data.suggestions);
    } catch (error) {
      console.error('Error getting suggestions:', error);
      alert('Failed to get suggestions. Make sure the backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const testAlgorithm = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/test-algorithm`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      alert('Algorithm test results logged to console. Check browser console for details!');
      console.log('🧪 Algorithm Test Results:');
      console.table(data.algorithm_tests);
      console.log('📊 Summary:', {
        'Total Tests': data.total_tests,
        'Algorithm': data.algorithm,
        'Average Success Rate': (data.average_success_rate * 100).toFixed(1) + '%'
      });
    } catch (error) {
      console.error('Error testing algorithm:', error);
      alert('Failed to test algorithm. Make sure the backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const renderEmotionCircle = (emotion, isSelected = false, isTarget = false) => (
    <div
      key={emotion}
      style={{
        width: '60px',
        height: '60px',
        borderRadius: '50%',
        backgroundColor: emotionColors[emotion] || '#ccc',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '5px',
        border: isSelected ? '3px solid black' : isTarget ? '3px solid orange' : '1px solid #ccc',
        fontSize: '12px',
        fontWeight: isSelected || isTarget ? 'bold' : 'normal',
        cursor: 'pointer',
        textAlign: 'center',
        position: 'relative'
      }}
      onClick={() => {
        if (isTarget) {
          setTargetEmotion(emotion);
        } else {
          setCurrentEmotion(emotion);
        }
      }}
    >
      {emotion}
      {isSelected && <div style={{fontSize: '8px', position: 'absolute', top: '70px'}}>CURRENT</div>}
      {isTarget && <div style={{fontSize: '8px', position: 'absolute', top: '70px'}}>TARGET</div>}
    </div>
  );

  const renderPath = () => {
    if (!pathResult || !pathResult.path) return null;
    
    return (
      <div style={{margin: '20px 0'}}>
        <h3>🎯 Optimal Path Found!</h3>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '10px 0', flexWrap: 'wrap'}}>
          {pathResult.path.map((emotion, index) => (
            <React.Fragment key={index}>
              {renderEmotionCircle(emotion, emotion === currentEmotion, emotion === targetEmotion)}
              {index < pathResult.path.length - 1 && (
                <div style={{margin: '0 10px', fontSize: '20px'}}>→</div>
              )}
            </React.Fragment>
          ))}
        </div>
        <div style={{textAlign: 'center', marginTop: '15px'}}>
          <p><strong>Success Rate:</strong> {(pathResult.estimated_success_rate * 100).toFixed(1)}%</p>
          <p><strong>Total Cost:</strong> {pathResult.total_cost?.toFixed(2)}</p>
        </div>
        
        {pathResult.actions && pathResult.actions.length > 0 && (
          <div style={{marginTop: '20px'}}>
            <h4>📋 Step-by-Step Actions:</h4>
            {pathResult.actions.map((action, index) => (
              <div key={index} style={{
                background: '#f0f8ff',
                padding: '10px',
                margin: '5px 0',
                borderRadius: '5px',
                borderLeft: '4px solid #4169E1'
              }}>
                <div style={{fontWeight: 'bold'}}>{action.from} → {action.to}</div>
                <div>{action.action}</div>
                <div style={{fontSize: '12px', color: '#666'}}>
                  Success Rate: {(action.success_rate * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderBackendStatus = () => {
    const statusInfo = {
      checking: { color: '#ffc107', text: 'Checking backend...', icon: '🔍' },
      connected: { color: '#28a745', text: 'Backend connected', icon: '✅' },
      error: { color: '#dc3545', text: 'Backend not connected', icon: '❌' }
    };

    const status = statusInfo[backendStatus] || statusInfo.error;

    return (
      <div style={{
        background: status.color,
        color: 'white',
        padding: '8px 15px',
        borderRadius: '5px',
        margin: '10px 0',
        textAlign: 'center',
        fontSize: '14px',
        fontWeight: 'bold'
      }}>
        {status.icon} {status.text}
        {backendStatus === 'error' && (
          <div style={{fontSize: '12px', marginTop: '5px', fontWeight: 'normal'}}>
            Make sure to run: ./start-backend.sh
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{padding: '20px', maxWidth: '1000px', margin: '0 auto', fontFamily: 'Arial, sans-serif'}}>
      <h1 style={{textAlign: 'center', color: '#333'}}>
        🧠 Simple AI Emotional Pathfinding Demo
      </h1>
      <p style={{textAlign: 'center', color: '#666', marginBottom: '20px'}}>
        Algorithm Development Focus - No Docker, No Database, Pure Python + React
      </p>

      {renderBackendStatus()}

      {/* Text Analysis Section */}
      <div style={{background: '#f8f9fa', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
        <h2>📝 1. Analyze Text Emotion</h2>
        <div style={{display: 'flex', gap: '10px', marginBottom: '10px', flexWrap: 'wrap'}}>
          <input
            type="text"
            value={testText}
            onChange={(e) => setTestText(e.target.value)}
            placeholder="Enter text to analyze emotion (e.g., 'I feel really excited about this!')"
            style={{
              flex: 1,
              minWidth: '300px',
              padding: '10px',
              border: '1px solid #ccc',
              borderRadius: '5px',
              fontSize: '14px'
            }}
          />
          <button
            onClick={analyzeText}
            disabled={loading || !testText.trim() || backendStatus !== 'connected'}
            style={{
              padding: '10px 20px',
              background: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
        
        {analysisResult && (
          <div style={{background: '#e8f5e8', padding: '15px', borderRadius: '5px', marginTop: '10px'}}>
            <h4>Analysis Result:</h4>
            <p><strong>Primary Emotion:</strong> {analysisResult.primary_emotion}</p>
            <p><strong>Confidence:</strong> {(analysisResult.confidence * 100).toFixed(1)}%</p>
            <p><strong>Is Positive:</strong> {analysisResult.is_positive ? 'Yes' : 'No'}</p>
            <div style={{marginTop: '10px'}}>
              <strong>All Emotion Scores:</strong>
              <div style={{display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '5px'}}>
                {Object.entries(analysisResult.emotion_scores || {}).map(([emotion, score]) => (
                  <span key={emotion} style={{
                    background: emotionColors[emotion] || '#ccc',
                    color: 'white',
                    padding: '3px 8px',
                    borderRadius: '15px',
                    fontSize: '12px'
                  }}>
                    {emotion}: {(score * 100).toFixed(0)}%
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Emotion Selection */}
      <div style={{background: '#f8f9fa', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
        <h2>🎯 2. Select Emotions for Pathfinding</h2>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px'}}>
          <div>
            <h4>Current Emotion:</h4>
            <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center'}}>
              {emotions.map(emotion => renderEmotionCircle(emotion, emotion === currentEmotion, false))}
            </div>
          </div>
          <div>
            <h4>Target Emotion:</h4>
            <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center'}}>
              {emotions.map(emotion => renderEmotionCircle(emotion, false, emotion === targetEmotion))}
            </div>
          </div>
        </div>
        
        <div style={{textAlign: 'center', marginTop: '20px'}}>
          <button
            onClick={findPath}
            disabled={loading || !currentEmotion || !targetEmotion || backendStatus !== 'connected'}
            style={{
              padding: '15px 30px',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
          >
            {loading ? 'Finding Path...' : '🔍 Find Optimal Path (A* Algorithm)'}
          </button>
        </div>
      </div>

      {/* Path Result */}
      {pathResult && (
        <div style={{background: '#e8f5e8', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
          {renderPath()}
        </div>
      )}

      {/* Suggestions */}
      <div style={{background: '#f8f9fa', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
        <h2>💡 3. Get Suggestions</h2>
        <div style={{textAlign: 'center'}}>
          <button
            onClick={getSuggestions}
            disabled={loading || !currentEmotion || backendStatus !== 'connected'}
            style={{
              padding: '10px 20px',
              background: '#ffc107',
              color: 'black',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Loading...' : `Get Suggestions for ${currentEmotion}`}
          </button>
        </div>
        
        {suggestions.length > 0 && (
          <div style={{marginTop: '15px'}}>
            <h4>Suggestions for {currentEmotion}:</h4>
            <ul style={{listStyle: 'none', padding: 0}}>
              {suggestions.map((suggestion, index) => (
                <li key={index} style={{
                  background: '#fff3cd',
                  padding: '10px',
                  margin: '5px 0',
                  borderRadius: '5px',
                  borderLeft: '4px solid #ffc107'
                }}>
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Algorithm Testing */}
      <div style={{background: '#e3f2fd', padding: '20px', borderRadius: '10px', marginBottom: '20px'}}>
        <h2>🔬 4. Test Algorithm</h2>
        <p>Run automated tests to verify the A* pathfinding algorithm is working correctly.</p>
        <div style={{textAlign: 'center'}}>
          <button
            onClick={testAlgorithm}
            disabled={loading || backendStatus !== 'connected'}
            style={{
              padding: '10px 20px',
              background: '#2196F3',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            {loading ? 'Testing...' : '🧪 Run Algorithm Tests'}
          </button>
        </div>
        <p style={{fontSize: '12px', color: '#666', textAlign: 'center', marginTop: '10px'}}>
          Check browser console (F12) for detailed test results
        </p>
      </div>

      {/* Development Info */}
      <div style={{background: '#f8f9fa', padding: '20px', borderRadius: '10px', border: '1px solid #ddd'}}>
        <h3>🔧 Development Info</h3>
        <p><strong>Backend:</strong> Simple Python Flask (proxied via React dev server)</p>
        <p><strong>Frontend:</strong> Basic React (this page)</p>
        <p><strong>Storage:</strong> In-memory (no database)</p>
        <p><strong>Focus:</strong> Algorithm development and testing</p>
        
        <div style={{marginTop: '15px'}}>
          <h4>Key Algorithm Files:</h4>
          <ul style={{fontSize: '14px', color: '#666'}}>
            <li><code>backend/simple_app.py</code> - Main backend with A* algorithm</li>
            <li><code>SimpleEmotionAnalyzer</code> - Text emotion analysis</li>
            <li><code>AStarPathfinder</code> - A* pathfinding implementation</li>
          </ul>
        </div>

        <div style={{marginTop: '15px'}}>
          <h4>🚀 Quick Commands:</h4>
          <ul style={{fontSize: '14px', color: '#666'}}>
            <li><code>./start-simple.sh</code> - Start both frontend and backend</li>
            <li><code>./start-backend.sh</code> - Start backend only</li>
            <li><code>./start-frontend.sh</code> - Start frontend only</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SimpleAIDemo;
````

## File: frontend/package.json
````json
{
  "name": "simple-reflectly-frontend",
  "version": "1.0.0",
  "description": "Simple React frontend for Reflectly AI algorithm development",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:5000"
}
````

## File: backend/models/emotional_graph.py
````python
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
````

## File: backend/models/memory_manager.py
````python
from datetime import datetime, timedelta
import json
import random
from bson.objectid import ObjectId

# Custom JSON encoder to handle MongoDB ObjectId and datetime objects
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)

class MemoryManager:
    """
    Class for managing the storage and retrieval of journal entries and memories.
    """
    
    def __init__(self, db, redis_client):
        """
        Initialize the memory manager.
        
        Args:
            db: MongoDB database connection
            redis_client: Redis client for caching
        """
        self.db = db
        self.redis_client = redis_client
        
        # Define memory tiers
        self.tiers = {
            'short_term': {'max_age': timedelta(days=7)},
            'medium_term': {'max_age': timedelta(days=30)},
            'long_term': {'max_age': timedelta(days=365)}
        }
    
    def store_entry(self, user_email, entry):
        """
        Store a journal entry in the memory system.
        
        Args:
            user_email (str): The user's email
            entry (dict): The journal entry to store
        """
        try:
            print(f"MemoryManager.store_entry called with user_email: {user_email}")
            print(f"Entry before processing: {entry}")
            
            # Create a copy of the entry to avoid modifying the original
            entry_copy = entry.copy()
            print(f"Entry copy created: {entry_copy}")
            
            # Convert datetime objects to strings for JSON serialization
            if isinstance(entry_copy.get('created_at'), datetime):
                print("Converting datetime to ISO format")
                entry_copy['created_at'] = entry_copy['created_at'].isoformat()
                print(f"Datetime converted: {entry_copy['created_at']}")
            
            # Check for ObjectId in the entry
            if '_id' in entry_copy and isinstance(entry_copy['_id'], ObjectId):
                print(f"Converting ObjectId to string: {entry_copy['_id']}")
                entry_copy['_id'] = str(entry_copy['_id'])
                print(f"ObjectId converted: {entry_copy['_id']}")
            
            # Store in Redis for short-term access (7 days)
            entry_key = f"entry:{user_email}:{entry_copy['_id']}"
            print(f"Redis key: {entry_key}")
            
            # Serialize the entry with our custom JSON encoder
            json_data = json.dumps(entry_copy, cls=MongoJSONEncoder)
            print(f"JSON serialized data: {json_data}")
            
            # Convert timedelta to integer seconds for Redis
            expiry_seconds = int(self.tiers['short_term']['max_age'].total_seconds())
            print(f"Setting expiry time: {expiry_seconds} seconds")
            
            self.redis_client.setex(
                entry_key,
                expiry_seconds,
                json_data
            )
            print(f"Entry stored in Redis with key: {entry_key}")
        except Exception as e:
            print(f"Error in store_entry: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        
        # If the entry has positive emotion, store in positive memories
        if entry['emotion']['is_positive']:
            positive_key = f"positive_memories:{user_email}"
            
            # Handle the date formatting - check if it's already a string or still a datetime
            date_str = entry['created_at']
            if isinstance(entry['created_at'], datetime):
                date_str = entry['created_at'].strftime('%Y-%m-%d')
            elif isinstance(entry['created_at'], str):
                # Try to parse the ISO format string
                try:
                    date_obj = datetime.fromisoformat(entry['created_at'])
                    date_str = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    # If parsing fails, just use the first 10 chars (YYYY-MM-DD)
                    date_str = entry['created_at'][:10]
                    
            memory_data = {
                'entry_id': str(entry['_id']),
                'date': date_str,
                'emotion': entry['emotion']['primary_emotion'],
                'summary': self._generate_summary(entry['content']),
                'score': self._calculate_memory_score(entry)
            }
            
            # Store in Redis list with higher priority for more recent positive memories
            self.redis_client.lpush(positive_key, json.dumps(memory_data, cls=MongoJSONEncoder))
            # Trim list to keep only the top 100 memories (increased from 50 to store more positive memories)
            self.redis_client.ltrim(positive_key, 0, 99)
    
    def get_positive_memories(self, user_email, limit=5):
        """
        Retrieve positive memories for a user.
        
        Args:
            user_email (str): The user's email
            limit (int): Maximum number of memories to retrieve
            
        Returns:
            list: List of positive memories
        """
        positive_key = f"positive_memories:{user_email}"
        
        # Get all memories from Redis
        memory_items = self.redis_client.lrange(positive_key, 0, -1)
        
        if not memory_items:
            # If Redis is empty, fetch from MongoDB
            entries = list(self.db.journal_entries.find({
                'user_email': user_email,
                'emotion.is_positive': True
            }).sort('created_at', -1).limit(20))
            
            memory_items = []
            for entry in entries:
                memory_data = {
                    'entry_id': str(entry['_id']),
                    'date': entry['created_at'].strftime('%Y-%m-%d'),
                    'emotion': entry['emotion']['primary_emotion'],
                    'summary': self._generate_summary(entry['content']),
                    'score': self._calculate_memory_score(entry)
                }
                memory_items.append(json.dumps(memory_data))
                
                # Store in Redis for future use
                self.redis_client.lpush(positive_key, json.dumps(memory_data, cls=MongoJSONEncoder))
            
            # Trim list to keep only the top 50 memories
            self.redis_client.ltrim(positive_key, 0, 49)
        
        # Parse JSON strings to dictionaries
        memories = [json.loads(item) for item in memory_items]
        
        # Sort by score and select top memories
        memories.sort(key=lambda x: x['score'], reverse=True)
        
        # Return a random selection from the top memories
        top_memories = memories[:min(10, len(memories))]
        selected_memories = random.sample(top_memories, min(limit, len(top_memories)))
        
        return selected_memories
    
    def get_relevant_memories(self, user_email, current_entry, limit=3):
        """
        Retrieve memories relevant to the current entry.
        
        Args:
            user_email (str): The user's email
            current_entry (dict): The current journal entry
            limit (int): Maximum number of memories to retrieve
            
        Returns:
            list: List of relevant memories
        """
        try:
            # Validate input
            if not user_email or not current_entry:
                print("Invalid input to get_relevant_memories")
                return []
                
            # Ensure current_entry has required fields
            if 'emotion' not in current_entry:
                print("No emotion data in current entry")
                return []
                
            # Ensure emotion has required fields
            if 'is_positive' not in current_entry['emotion']:
                print("Missing is_positive in emotion data")
                current_entry['emotion']['is_positive'] = False
                
            if 'primary_emotion' not in current_entry['emotion']:
                print("Missing primary_emotion in emotion data")
                current_entry['emotion']['primary_emotion'] = 'neutral'
            
            # In a production system, this would use semantic search or embeddings
            # For now, we'll use a sophisticated approach based on emotion and content
            
            # If current emotion is negative, get positive memories to provide encouragement
            if not current_entry['emotion']['is_positive']:
                print(f"User is feeling {current_entry['emotion']['primary_emotion']} - retrieving positive memories for encouragement")
                return self.get_positive_memories(user_email, limit)
            
            # For positive emotions, don't return any memories to avoid showing unnecessary memory cards
            # Instead, just store the positive memory for future reference
            print(f"User is feeling {current_entry['emotion']['primary_emotion']} - storing as positive memory without showing memory card")
            return []
            
            # The code below is intentionally unreachable - keeping for reference
            if 'content' not in current_entry:
                print("No content in current entry")
                return []
                
            content_words = set(current_entry['content'].lower().split())
            
            # Remove common words that don't add much meaning
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                          'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                          'to', 'from', 'in', 'out', 'on', 'off', 'over', 'under', 'again'}
            content_words = content_words - stop_words
        except Exception as e:
            print(f"Error in get_relevant_memories initial processing: {str(e)}")
            return []
        
        try:
            # Get recent entries
            entries = list(self.db.journal_entries.find({
                'user_email': user_email,
                '_id': {'$ne': ObjectId(current_entry.get('_id', ''))}
            }).sort('created_at', -1).limit(20))
            
            # Score entries based on content similarity and emotion
            scored_entries = []
            for entry in entries:
                try:
                    # Skip entries without content
                    if 'content' not in entry:
                        continue
                        
                    entry_words = set(entry['content'].lower().split()) - stop_words
                    
                    # Calculate word overlap
                    common_words = content_words.intersection(entry_words)
                    similarity_score = len(common_words) / max(len(content_words), 1)
                    
                    # Boost score for entries with the same emotion
                    if 'emotion' in entry and 'primary_emotion' in entry.get('emotion', {}) and \
                       'emotion' in current_entry and 'primary_emotion' in current_entry.get('emotion', {}):
                        if entry.get('emotion', {}).get('primary_emotion') == current_entry['emotion'].get('primary_emotion'):
                            similarity_score *= 1.5
                    
                    # Boost score for positive memories
                    if entry.get('emotion', {}).get('is_positive', False):
                        similarity_score *= 1.2
                        
                    scored_entries.append((entry, similarity_score))
                except Exception as e:
                    print(f"Error processing entry in get_relevant_memories: {str(e)}")
                    continue
            
            # Sort by score
            scored_entries.sort(key=lambda x: x[1], reverse=True)
            
            # Get top entries
            top_entries = [entry for entry, score in scored_entries[:10]]
            
            memories = []
            for entry in top_entries:
                try:
                    # Ensure created_at is a datetime object
                    created_at = entry.get('created_at')
                    date_str = 'Unknown date'
                    
                    if isinstance(created_at, datetime):
                        date_str = created_at.strftime('%Y-%m-%d')
                    elif isinstance(created_at, str):
                        try:
                            date_obj = datetime.fromisoformat(created_at)
                            date_str = date_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            # If parsing fails, just use the first 10 chars (YYYY-MM-DD)
                            date_str = created_at[:10] if len(created_at) >= 10 else created_at
                    
                    # Ensure emotion data exists
                    emotion = 'neutral'
                    if 'emotion' in entry and 'primary_emotion' in entry['emotion']:
                        emotion = entry['emotion']['primary_emotion']
                        
                    memory_data = {
                        'entry_id': str(entry.get('_id', '')),
                        'date': date_str,
                        'emotion': emotion,
                        'summary': self._generate_summary(entry.get('content', '')),
                        'score': self._calculate_memory_score(entry)
                    }
                    memories.append(memory_data)
                except Exception as e:
                    print(f"Error creating memory data: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error in get_relevant_memories processing: {str(e)}")
            return []
        
        # Sort by score and select top memories
        memories.sort(key=lambda x: x['score'], reverse=True)
        
        # Return a random selection from the top memories
        selected_memories = random.sample(memories[:min(5, len(memories))], min(limit, len(memories[:5])))
        
        return selected_memories
    
    def get_memories(self, user_email, emotion=None, tag=None, favorite=None):
        """
        Retrieve memories for a user with optional filters.
        
        Args:
            user_email (str): The user's email
            emotion (str, optional): Filter by emotion
            tag (str, optional): Filter by tag
            favorite (bool, optional): Filter by favorite status
            
        Returns:
            list: List of memories
        """
        # Build query
        query = {'user_email': user_email}
        
        if emotion:
            query['emotion'] = emotion
        
        if tag:
            query['tags'] = tag
        
        if favorite is not None:
            query['favorite'] = favorite
        
        # Get memories from database
        memories = list(self.db.memories.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string
        for memory in memories:
            memory['_id'] = str(memory['_id'])
            memory['created_at'] = memory['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if 'updated_at' in memory:
                memory['updated_at'] = memory['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return memories
    
    def get_memory_by_id(self, user_email, memory_id):
        """
        Retrieve a specific memory by ID.
        
        Args:
            user_email (str): The user's email
            memory_id (str): The memory ID
            
        Returns:
            dict: The memory or None if not found
        """
        try:
            # Get memory from database
            memory = self.db.memories.find_one({
                '_id': ObjectId(memory_id),
                'user_email': user_email
            })
            
            if memory:
                # Convert ObjectId to string
                memory['_id'] = str(memory['_id'])
                memory['created_at'] = memory['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if 'updated_at' in memory:
                    memory['updated_at'] = memory['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return memory
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return None
    
    def _generate_summary(self, content, max_length=100):
        """
        Generate a summary of the content.
        
        Args:
            content (str): The content to summarize
            max_length (int): Maximum length of the summary
            
        Returns:
            str: A summary of the content
        """
        # In a production system, this would use a summarization model
        # For now, we'll use a simple approach
        if len(content) <= max_length:
            return content
        
        # Truncate and add ellipsis
        return content[:max_length - 3] + "..."
    
    def _calculate_memory_score(self, entry):
        """
        Calculate a relevance score for a memory.
        
        Args:
            entry (dict): The journal entry
            
        Returns:
            float: A relevance score
        """
        # In a production system, this would use a more sophisticated approach
        # For now, we'll use a simple heuristic
        
        # Base score
        score = 1.0
        
        # Adjust based on emotion intensity
        primary_emotion = entry['emotion']['primary_emotion']
        emotion_score = entry['emotion']['emotion_scores'][primary_emotion]
        score *= (1.0 + emotion_score)
        
        # Adjust based on recency (newer entries get higher scores)
        days_old = (datetime.now() - entry['created_at']).days
        recency_factor = max(0.5, 1.0 - (days_old / 365.0))
        score *= recency_factor
        
        return score
````

## File: backend/Dockerfile
````
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5002"]
````

## File: frontend/src/index.css
````css
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

* {
  box-sizing: border-box;
}

.App {
  min-height: 100vh;
}

/* Simple button styles */
button {
  cursor: pointer;
  border: none;
  border-radius: 5px;
  font-family: inherit;
  transition: all 0.2s ease;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Simple input styles */
input, textarea, select {
  font-family: inherit;
  border-radius: 5px;
  border: 1px solid #ddd;
  padding: 8px;
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

/* Utility classes */
.text-center {
  text-align: center;
}

.mb-1 { margin-bottom: 8px; }
.mb-2 { margin-bottom: 16px; }
.mb-3 { margin-bottom: 24px; }
.mt-1 { margin-top: 8px; }
.mt-2 { margin-top: 16px; }
.mt-3 { margin-top: 24px; }
````

## File: frontend/Dockerfile
````
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
````

## File: backend/requirements.txt
````
# Core Flask dependencies
Flask==2.3.3
Flask-CORS==4.0.0

# Database
pymongo==4.5.0

# Machine Learning & NLP
transformers==4.33.2
torch==2.0.1
numpy==1.24.3
scikit-learn==1.3.0

# Text processing
textblob==0.17.1
nltk==3.8.1

# Utilities
python-dotenv==1.0.0
requests==2.31.0

# Authentication (if needed)
bcrypt==4.0.1
PyJWT==2.8.0

# Development
pytest==7.4.2
pytest-flask==1.2.0
````

## File: frontend/src/App.js
````javascript
import React from 'react';
import IntelligentAgentApp from './IntelligentAgentApp';
import './index.css';

function App() {
  return (
    <div className="App">
      <IntelligentAgentApp />
    </div>
  );
}

export default App;
````

## File: backend/models/response_generator.py
````python
import random

class ResponseGenerator:
    """
    Class for generating responses based on user input and emotion analysis.
    In a production environment, this would use GPT or a similar model.
    """
    
    def __init__(self):
        # Define response templates for different emotions
        self.positive_templates = [
            "That's wonderful! I'm glad to hear you're feeling {emotion}. What made you feel this way?",
            "It's great that you're experiencing {emotion}! Would you like to share more about it?",
            "I'm happy to see you're feeling {emotion}. How can you maintain this positive energy?",
            "That sounds really positive! How does this {emotion} compare to how you felt yesterday?",
            "It's always nice to feel {emotion}. What's one thing you're grateful for right now?"
        ]
        
        self.negative_templates = [
            "I'm sorry to hear you're feeling {emotion}. Would you like to talk more about what's bothering you?",
            "It sounds like you're going through a difficult time. Remember that it's okay to feel {emotion} sometimes.",
            "I notice you're feeling {emotion}. What's one small thing that might help you feel better?",
            "When you feel {emotion}, it can be helpful to remember past times when you overcame similar feelings.",
            "I'm here for you during this {emotion}. What support do you need right now?"
        ]
        
        self.neutral_templates = [
            "Thanks for sharing that. How do you feel about it?",
            "I appreciate you writing this down. Is there anything specific you'd like to reflect on?",
            "That's interesting. How does this relate to your goals?",
            "Thank you for your entry. Is there anything else on your mind?",
            "I see. Would you like to explore this topic further?"
        ]
        
        # Define follow-up questions for deeper reflection
        self.follow_up_questions = [
            "How did this experience affect your perspective?",
            "What did you learn from this situation?",
            "How might this connect to your long-term goals?",
            "What patterns do you notice in how you respond to similar situations?",
            "If you could change one thing about this experience, what would it be?"
        ]
        
        # Define suggested actions for different emotions
        self.suggested_actions = {
            'sadness': [
                "Reach out to a friend or family member",
                "Practice self-care activities",
                "Listen to uplifting music",
                "Take a short walk outside",
                "Write down three things you're grateful for"
            ],
            'anger': [
                "Take deep breaths for a few minutes",
                "Write down your thoughts",
                "Engage in physical activity",
                "Practice mindfulness meditation",
                "Step away from the situation temporarily"
            ],
            'fear': [
                "Focus on your breathing",
                "Challenge negative thoughts",
                "Talk to someone you trust",
                "Create a plan to address your concerns",
                "Practice progressive muscle relaxation"
            ],
            'disgust': [
                "Redirect your attention to something positive",
                "Practice acceptance",
                "Engage in a pleasant activity",
                "Connect with supportive people",
                "Focus on things you appreciate"
            ],
            'neutral': [
                "Set a goal for today",
                "Practice gratitude",
                "Learn something new",
                "Connect with nature",
                "Reflect on your recent achievements"
            ],
            'joy': [
                "Share your positive experience with others",
                "Practice gratitude",
                "Savor the moment",
                "Set new goals",
                "Pay it forward with a kind act"
            ],
            'surprise': [
                "Reflect on what surprised you",
                "Consider what you can learn from this experience",
                "Share your experience with others",
                "Use this energy for creative activities",
                "Journal about your unexpected insights"
            ]
        }
    
    def generate(self, text, emotion_data):
        """
        Generate a response based on the user's input and emotion analysis.
        
        Args:
            text (str): The user's input text
            emotion_data (dict): Emotion analysis data
            
        Returns:
            str: A generated response
        """
        # Ensure emotion_data has all required fields
        if not emotion_data or not isinstance(emotion_data, dict):
            # Default to neutral if no emotion data
            emotion_data = {
                'primary_emotion': 'neutral',
                'is_positive': False,
                'emotion_scores': {}
            }
        
        # Ensure all required keys exist
        if 'primary_emotion' not in emotion_data:
            emotion_data['primary_emotion'] = 'neutral'
        if 'is_positive' not in emotion_data:
            emotion_data['is_positive'] = False
        if 'emotion_scores' not in emotion_data:
            emotion_data['emotion_scores'] = {}
            
        primary_emotion = emotion_data['primary_emotion']
        is_positive = emotion_data['is_positive']
        
        # Select appropriate template based on emotion
        if primary_emotion in ['joy', 'surprise']:
            template = random.choice(self.positive_templates)
        elif primary_emotion in ['anger', 'disgust', 'fear', 'sadness']:
            template = random.choice(self.negative_templates)
        else:
            template = random.choice(self.neutral_templates)
        
        # Format the template with the emotion
        response = template.format(emotion=primary_emotion)
        
        # Add a follow-up question 50% of the time
        if random.random() > 0.5:
            response += " " + random.choice(self.follow_up_questions)
        
        return response
        
    def generate_with_memory(self, text, emotion_data, memories=None, suggested_actions=None, emotion_history=None):
        """
        Generate a personalized response incorporating emotional history and suggested actions.
        
        Args:
            text (str): The user's input text
            emotion_data (dict): Emotion analysis data
            memories (list): Optional memory data for context
            suggested_actions (list): Optional suggested actions from emotional graph
            emotion_history (list): Optional emotional state history
            
        Returns:
            dict: A response object with text and suggested actions
        """
        # Ensure emotion_data has all required fields
        if not emotion_data or not isinstance(emotion_data, dict):
            # Default to neutral if no emotion data
            emotion_data = {
                'primary_emotion': 'neutral',
                'is_positive': False,
                'emotion_scores': {}
            }
            
        # Ensure all required keys exist
        if 'primary_emotion' not in emotion_data:
            emotion_data['primary_emotion'] = 'neutral'
        if 'is_positive' not in emotion_data:
            emotion_data['is_positive'] = False
        if 'emotion_scores' not in emotion_data:
            emotion_data['emotion_scores'] = {}
        
        primary_emotion = emotion_data['primary_emotion']
        is_positive = emotion_data['is_positive']
        
        # Generate a personalized response based on emotional context
        personalized_response = self._generate_personalized_response(text, emotion_data, emotion_history)
        
        # Use provided suggested actions if available, otherwise generate generic ones
        if not suggested_actions:
            suggested_actions = self._get_suggested_actions(primary_emotion)
        
        # Create a more personalized response by adding context about emotional journey
        if emotion_history and not is_positive:
            # Add encouragement based on past positive emotions if current emotion is negative
            positive_history = [state for state in emotion_history if state.get('is_positive', False)]
            if positive_history:
                # Add a reminder of past positive experiences
                personalized_response += f" Remember that you've felt positive emotions before, and you can get there again."
        
        response_obj = {
            'text': personalized_response,
            'suggested_actions': suggested_actions
        }
        
        return response_obj
        
    def _generate_personalized_response(self, text, emotion_data, emotion_history=None):
        """
        Generate a personalized response based on the user's emotional context and history.
        
        Args:
            text (str): The user's input text
            emotion_data (dict): Emotion analysis data
            emotion_history (list): Optional emotional state history
            
        Returns:
            str: A personalized response
        """
        primary_emotion = emotion_data['primary_emotion']
        is_positive = emotion_data['is_positive']
        
        # Start with a base response
        base_response = self.generate(text, emotion_data)
        
        # If we have emotional history, enhance the response with personalized insights
        if emotion_history and len(emotion_history) > 1:
            # Check for patterns in emotional states
            recent_emotions = [state.get('primary_emotion') for state in emotion_history[:5]]
            
            # If there's a pattern of negative emotions
            if all(emotion in ['sadness', 'anger', 'fear', 'disgust'] for emotion in recent_emotions[:3]):
                base_response += " I've noticed you've been experiencing challenging emotions lately. Let's work together to find ways to improve how you're feeling."
            
            # If there's improvement in emotional state
            if not is_positive and any(state.get('is_positive', False) for state in emotion_history[1:3]):
                base_response += " It seems your emotions have shifted recently. What do you think contributed to this change?"
            
            # If there's a consistent positive trend
            if is_positive and all(state.get('is_positive', False) for state in emotion_history[:3]):
                base_response += " You've been maintaining positive emotions consistently. That's wonderful progress!"
        
        return base_response
        
    def _get_suggested_actions(self, emotion, count=3):
        """
        Get suggested actions for the given emotion.
        
        Args:
            emotion (str): The emotion to get suggestions for
            count (int): Number of suggestions to return
            
        Returns:
            list: List of suggested actions
        """
        # Get suggestions for the emotion, or default to neutral
        all_suggestions = self.suggested_actions.get(emotion, self.suggested_actions['neutral'])
        
        # Randomly select a subset of suggestions
        if len(all_suggestions) <= count:
            return all_suggestions
        else:
            return random.sample(all_suggestions, count)
````

## File: frontend/src/pages/Journal.js
````javascript
import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Divider,
  CircularProgress,
  Chip,
  Avatar,
  Tooltip,
  Fade,
  useMediaQuery
} from '@mui/material';
import MemoryCard from '../components/journal/MemoryCard';
import { useTheme } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral';
import axios from '../utils/axiosConfig';
import { format } from 'date-fns';
import { useAuth } from '../context/AuthContext';

const Journal = () => {
  const [entries, setEntries] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [speechRecognition, setSpeechRecognition] = useState(null);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user } = useAuth();
  
  // Initialize speech recognition if available
  useEffect(() => {
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0])
          .map(result => result.transcript)
          .join('');
        
        setCurrentMessage(transcript);
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsRecording(false);
      };
      
      setSpeechRecognition(recognition);
    }
  }, []);
  
  // This useEffect was moved above
  
  // Scroll to bottom of messages when entries change
  useEffect(() => {
    scrollToBottom();
  }, [entries]);
  
  // Ensure messages are always displayed in chronological order
  const sortEntries = (entriesToSort) => {
    // Sort entries by created_at in ascending order (oldest first)
    return [...entriesToSort].sort((a, b) => {
      return new Date(a.created_at) - new Date(b.created_at);
    });
  };
  
  // Fetch journal entries on component mount
  useEffect(() => {
    fetchEntries();
  }, []);
  
  const fetchEntries = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get('/api/journal/entries');
      // Sort entries when they're fetched from the API
      setEntries(sortEntries(response.data));
      setError(null);
    } catch (err) {
      console.error('Error fetching journal entries:', err);
      setError('Failed to load journal entries. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!currentMessage.trim()) return;
    
    // Generate a temporary ID that we can reference later
    const tempId = `temp-${Date.now()}`;
    
    try {
      setIsLoading(true);
      
      // Optimistically add user message to UI
      const userEntry = {
        _id: tempId,
        content: currentMessage,
        user_email: user.email,
        created_at: new Date().toISOString(),
        isUserMessage: true
      };
      
      setEntries(prev => sortEntries([...prev, userEntry]));
      setCurrentMessage('');
      
      // Send to API
      console.log('Sending journal entry to API:', userEntry.content);
      const response = await axios.post('/api/journal/entries', {
        content: userEntry.content
      });
      console.log('API response:', response.data);
      
      // Add AI response with the response_id from the backend
      const aiResponse = {
        _id: response.data.response_id,
        content: response.data.response.text, // Extract the text from the response object
        suggested_actions: response.data.response.suggested_actions, // Store suggested actions
        created_at: new Date(new Date().getTime() + 1000).toISOString(), // 1 second after user message
        isUserMessage: false,
        parent_entry_id: response.data.entry_id
      };
      
      // Replace the temporary user message with the permanent one and add AI response
      setEntries(prev => {
        // First replace the temporary user message with the permanent one
        const updatedPrev = prev.map(entry => 
          entry._id === tempId 
            ? { ...entry, _id: response.data.entry_id } 
            : entry
        );
        
        // Then add the AI response
        let withAiResponse = [...updatedPrev, aiResponse];
        
        // If there's a memory reference, add it as a separate message
        if (response.data.memory && response.data.memory_id) {
          const memoryResponse = {
            _id: response.data.memory_id,
            content: response.data.memory.message,
            created_at: new Date(new Date().getTime() + 2000).toISOString(), // 2 seconds after user message
            isUserMessage: false,
            isMemory: true,
            memoryData: response.data.memory.data,
            memoryType: response.data.memory.type,
            parent_entry_id: response.data.entry_id
          };
          
          withAiResponse = [...withAiResponse, memoryResponse];
        }
        
        // Always sort the entries by date before returning
        return sortEntries(withAiResponse);
      });
      
      setError(null);
    } catch (err) {
      console.error('Error creating journal entry:', err);
      setError('Failed to send your message. Please try again.');
      
      // Remove the optimistic entry using the stored tempId
      setEntries(prev => prev.filter(entry => entry._id !== tempId));
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleInputChange = (e) => {
    setCurrentMessage(e.target.value);
  };
  
  const toggleRecording = () => {
    if (!speechRecognition) return;
    
    if (isRecording) {
      speechRecognition.stop();
      setIsRecording(false);
    } else {
      speechRecognition.start();
      setIsRecording(true);
    }
  };
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const getEmotionIcon = (emotion) => {
    if (!emotion) return null;
    
    switch (emotion.primary_emotion) {
      case 'joy':
      case 'surprise':
        return <SentimentSatisfiedAltIcon color="success" />;
      case 'anger':
      case 'disgust':
      case 'fear':
      case 'sadness':
        return <SentimentDissatisfiedIcon color="error" />;
      default:
        return <SentimentNeutralIcon color="action" />;
    }
  };
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return format(date, 'MMM d, yyyy h:mm a');
  };
  
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper 
        elevation={3} 
        sx={{ 
          height: 'calc(100vh - 160px)', 
          display: 'flex', 
          flexDirection: 'column',
          borderRadius: 2,
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <Box 
          sx={{ 
            p: 2, 
            backgroundColor: theme.palette.primary.main, 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <Typography variant="h6">Journal</Typography>
          <Chip 
            icon={<CalendarTodayIcon />} 
            label={format(new Date(), 'EEEE, MMMM d')} 
            sx={{ 
              color: 'white', 
              '& .MuiChip-icon': { color: 'white' } 
            }} 
            variant="outlined" 
          />
        </Box>
        
        {/* Messages area */}
        <Box 
          sx={{ 
            flexGrow: 1, 
            p: 2, 
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          {isLoading && entries.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress />
            </Box>
          ) : entries.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', textAlign: 'center' }}>
              <Box>
                <Typography variant="h6" gutterBottom>Welcome to your journal!</Typography>
                <Typography variant="body1" color="text.secondary">
                  Start by typing a message below to begin your reflection journey.
                </Typography>
              </Box>
            </Box>
          ) : (
            <>
              {entries.map((entry, index) => (
                <Fade in={true} key={entry._id} timeout={500}>
                  <Box sx={{ mb: 2 }}>
                    {/* Date divider if it's a new day */}
                    {index === 0 || 
                      format(new Date(entry.created_at), 'yyyy-MM-dd') !== 
                      format(new Date(entries[index - 1].created_at), 'yyyy-MM-dd') ? (
                      <Box 
                        sx={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          my: 3
                        }}
                      >
                        <Divider sx={{ flexGrow: 1 }} />
                        <Chip 
                          label={format(new Date(entry.created_at), 'EEEE, MMMM d')} 
                          size="small" 
                          sx={{ mx: 2 }} 
                        />
                        <Divider sx={{ flexGrow: 1 }} />
                      </Box>
                    ) : null}
                    
                    {/* Message bubble */}
                    <Box 
                      sx={{ 
                        display: 'flex',
                        flexDirection: entry.isUserMessage ? 'row-reverse' : 'row',
                        alignItems: 'flex-start',
                        mb: 1
                      }}
                    >
                      <Avatar 
                        sx={{ 
                          bgcolor: entry.isUserMessage ? 'primary.main' : 'secondary.main',
                          width: 36,
                          height: 36,
                          mr: entry.isUserMessage ? 0 : 1,
                          ml: entry.isUserMessage ? 1 : 0
                        }}
                      >
                        {entry.isUserMessage ? user?.name?.charAt(0) || 'U' : 'R'}
                      </Avatar>
                      
                      <Box>
                        {entry.isMemory ? (
                          <MemoryCard 
                            memoryData={entry.memoryData} 
                            memoryType={entry.memoryType} 
                          />
                        ) : (
                          <Box 
                            className={`chat-bubble ${entry.isUserMessage ? 'user-bubble' : 'ai-bubble'}`}
                            sx={{
                              backgroundColor: entry.isUserMessage 
                                ? 'primary.light' 
                                : theme.palette.mode === 'dark' 
                                  ? 'grey.800' 
                                  : 'grey.100',
                              color: entry.isUserMessage 
                                ? 'white' 
                                : 'text.primary',
                            }}
                          >
                            <Typography variant="body1">{entry.content}</Typography>
                          
                          {/* Display suggested actions if available */}
                          {!entry.isUserMessage && entry.suggested_actions && entry.suggested_actions.length > 0 && (
                            <Box sx={{ mt: 2 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                                Suggested Actions:
                              </Typography>
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                {entry.suggested_actions.map((action, index) => (
                                  <Chip 
                                    key={index}
                                    label={action}
                                    size="small"
                                    color="primary"
                                    variant="outlined"
                                    sx={{ 
                                      borderRadius: 1,
                                      '&:hover': { backgroundColor: 'primary.light', color: 'white', cursor: 'pointer' }
                                    }}
                                  />
                                ))}
                              </Box>
                            </Box>
                          )}
                          </Box>
                        )}
                        
                        <Box 
                          sx={{ 
                            display: 'flex', 
                            alignItems: 'center',
                            justifyContent: entry.isUserMessage ? 'flex-end' : 'flex-start',
                            mt: 0.5,
                            ml: entry.isUserMessage ? 0 : 1,
                            mr: entry.isUserMessage ? 1 : 0
                          }}
                        >
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                            {formatDate(entry.created_at)}
                          </Typography>
                          
                          {!entry.isUserMessage && entry.emotion && (
                            <Tooltip title={`Emotion: ${entry.emotion.primary_emotion}`}>
                              <Box component="span" sx={{ display: 'inline-flex', ml: 1 }}>
                                {getEmotionIcon(entry.emotion)}
                              </Box>
                            </Tooltip>
                          )}
                        </Box>
                      </Box>
                    </Box>
                  </Box>
                </Fade>
              ))}
              
              {/* Error message */}
              {error && (
                <Box 
                  sx={{ 
                    p: 2, 
                    backgroundColor: theme.palette.error.light,
                    color: theme.palette.error.contrastText,
                    borderRadius: 1,
                    mb: 2
                  }}
                >
                  <Typography variant="body2">{error}</Typography>
                </Box>
              )}
              
              {/* Scroll anchor */}
              <div ref={messagesEndRef} />
            </>
          )}
        </Box>
        
        {/* Input area */}
        <Box 
          component="form" 
          onSubmit={handleSubmit}
          sx={{ 
            p: 2, 
            borderTop: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.background.paper
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              fullWidth
              placeholder="Type your thoughts here..."
              variant="outlined"
              value={currentMessage}
              onChange={handleInputChange}
              disabled={isLoading}
              multiline
              maxRows={4}
              sx={{ mr: 1 }}
            />
            
            {speechRecognition && (
              <Tooltip title={isRecording ? "Stop recording" : "Start voice input"}>
                <IconButton 
                  color={isRecording ? "error" : "primary"} 
                  onClick={toggleRecording}
                  disabled={isLoading}
                >
                  {isRecording ? <MicOffIcon /> : <MicIcon />}
                </IconButton>
              </Tooltip>
            )}
            
            <Button
              variant="contained"
              color="primary"
              endIcon={<SendIcon />}
              type="submit"
              disabled={!currentMessage.trim() || isLoading}
              sx={{ ml: 1, height: 56, px: isMobile ? 2 : 3 }}
            >
              {isLoading ? <CircularProgress size={24} /> : isMobile ? null : "Send"}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Journal;
````

## File: docker-compose.yml
````yaml
# Simple Reflectly AI - No Docker Needed!

This project now uses a simplified setup without Docker.

## Quick Start:
```bash
# One command to start everything
chmod +x start-simple.sh
./start-simple.sh
```

## Requirements:
- Python 3.7+
- Node.js 16+
- npm

## What was removed:
- docker-compose.yml (replaced with simple scripts)
- Dockerfiles (no containerization needed)
- Complex orchestration (direct Python/Node execution)

## Benefits:
- Faster startup (no container building)
- Easier debugging (direct access to processes)
- Simpler development (direct file editing)
- No Docker installation required
- Native performance (no container overhead)

For the previous Docker setup, check the earlier commits in this branch.
````

## File: README.md
````markdown
# Intelligent Agent with Memory Map

> **Learning AI System**: An intelligent agent that learns from your emotional experiences and uses A* search to suggest helpful actions

## 🎯 **What Does This Do?**

This is a focused implementation of an intelligent agent that:

1. **📝 Analyzes your emotional text input** (happy, sad, anxious, etc.)
2. **🧠 Learns from positive experiences** by asking what steps led to good feelings
3. **💡 Suggests helpful actions** for negative emotions using A* search through learned experiences
4. **🗺️ Evolves a memory map** that grows smarter with each interaction

## 🤖 **How the Intelligent Agent Works**

### **When you input POSITIVE emotions (happy, excited):**
- 🤔 Agent asks: *"What steps led to this positive feeling?"*
- 💾 Saves your successful actions to memory map
- 🔗 Creates connections between emotions and successful strategies

### **When you input NEGATIVE emotions (sad, anxious, angry):**
- 🔍 Agent uses **A* search** through memory map
- 🎯 Finds optimal path from current emotion to positive emotions
- 💡 Suggests actions that previously worked for similar situations

### **Memory Map Evolution:**
- 🌱 Starts empty, grows with each interaction
- 📈 Learns patterns of successful emotional transitions
- 🧭 Guides future suggestions using past successes

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.7+
- Node.js 16+

### **One-Command Start**
```bash
# Clone and switch to intelligent agent branch
git clone https://github.com/iNVISIBLExtanx/reflectly.git
cd reflectly
git checkout intelligent-agent-memory

# Start the intelligent agent system
chmod +x start-intelligent-agent.sh
./start-intelligent-agent.sh
```

**Access at**: http://localhost:3000

## 🧪 **Try These Examples**

### **1. Teach the Agent (Positive Input)**
**Input**: *"I'm feeling really happy and excited today!"*
**Agent Response**: *"What steps led to this positive feeling?"*
**Your Steps**: 
- "Went for a morning run"
- "Had coffee with a friend" 
- "Listened to my favorite music"

### **2. Get Suggestions (Negative Input)**
**Input**: *"I'm feeling sad and don't know what to do"*
**Agent Response**: *"Based on past experiences, try these actions..."*
**Suggestions**: 
- "Go for a morning run" (learned from previous success)
- "Have coffee with a friend" 
- "Listen to your favorite music"

### **3. Watch Memory Map Evolve**
- Circle sizes grow with more experiences
- Lines connect emotions based on successful transitions
- Numbers show available learned actions

## 🗺️ **Memory Map Visualization**

The interactive memory map shows:
- **🟢 Green circles**: Positive emotions (happy)
- **🔴 Red circles**: Negative emotions (sad, anxious, angry)
- **⚪ Gray circles**: Neutral emotions
- **➡️ Lines**: Learned transitions between emotions
- **📊 Numbers**: Count of available action suggestions

## 🧠 **A* Search Algorithm**

The agent uses A* search to:
1. **Start** from current negative emotion
2. **Search** through memory map for paths to positive emotions
3. **Find optimal route** based on past success rates
4. **Suggest actions** from the most successful transitions

**Example Path**: `sad → neutral → happy`
- Suggests actions that previously helped transition `sad → neutral`
- Then actions that helped transition `neutral → happy`

## 📁 **Simple Architecture**

```
intelligent-agent-memory/
├── backend/
│   └── intelligent_agent.py     # 🤖 Complete agent with A* search
├── frontend/
│   └── src/
│       ├── IntelligentAgentApp.js   # 🗺️ Memory map visualization
│       └── App.js                   # ⚛️ Simple wrapper
├── start-intelligent-agent.sh      # 🚀 One-command startup
└── README.md                       # 📖 This guide
```

## 🔧 **API Endpoints**

### **Process User Input**
```bash
curl -X POST http://localhost:5000/api/process-input \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel really happy today!", "user_id": "user1"}'
```

### **Save Successful Steps**
```bash
curl -X POST http://localhost:5000/api/save-steps \
  -H "Content-Type: application/json" \
  -d '{"experience_id": "abc123", "steps": ["Went for a run", "Called a friend"]}'
```

### **Get Memory Map Data**
```bash
curl http://localhost:5000/api/memory-map
```

## 💻 **Development & Customization**

### **Add New Emotions**
```python
# In EmotionAnalyzer.__init__()
self.emotion_keywords = {
    'happy': ['happy', 'joyful', 'excited'],
    'proud': ['proud', 'accomplished', 'successful'],  # Add new emotion
    # ... existing emotions
}
```

### **Modify A* Search**
```python
# In IntelligentAgent._astar_search_for_actions()
# Customize the search algorithm:
# - Change cost functions
# - Adjust heuristics  
# - Add path preferences
```

### **Enhance Memory Learning**
```python
# In IntelligentAgent.save_successful_steps()
# Modify how steps are stored and weighted:
# - Add success rate tracking
# - Implement step effectiveness scoring
# - Add temporal decay for old experiences
```

## 🎮 **Interactive Features**

### **Conversation Interface**
- 💬 Chat-like interface with the intelligent agent
- 📝 Natural language input processing
- 🤖 Contextual responses based on emotion type
- ⏰ Timestamped conversation history

### **Memory Map Visualization**
- 🎨 Color-coded emotional states
- 📏 Dynamic sizing based on experience count
- 🔗 Visual connections showing learned transitions
- 📊 Real-time learning statistics

### **Learning System**
- 📚 Automatic experience categorization
- 💾 Persistent memory storage (session-based)
- 🔄 Continuous map evolution
- 🎯 Personalized suggestion improvement

## 🔬 **Algorithm Details**

### **Emotion Classification**
- **Method**: Keyword-based analysis with scoring
- **Emotions**: 7 categories (happy, sad, anxious, angry, confused, tired, neutral)
- **Output**: Primary emotion + confidence score

### **A* Search Implementation**
- **Goal**: Find optimal path to positive emotions
- **Heuristic**: Distance to target emotional state
- **Cost**: Inverse of historical success rate
- **Path**: Sequence of emotions and actions

### **Memory Management**
- **Storage**: In-memory dictionary structures
- **Indexing**: By emotion type and transition pairs
- **Retrieval**: O(1) lookup for common patterns
- **Evolution**: Continuous learning from new experiences

## 🎯 **Use Cases**

### **Personal Emotional Learning**
- Track what makes you happy and apply it when sad
- Build personal emotional intelligence
- Discover effective coping strategies

### **AI Research & Development**
- Study human emotional patterns
- Test reinforcement learning approaches
- Develop personalized recommendation systems

### **Educational Demonstrations**
- Show A* search in practical applications
- Demonstrate machine learning concepts
- Illustrate graph theory in psychology

## 📊 **Learning Metrics**

The system tracks:
- **Total Experiences**: Number of emotional inputs processed
- **Emotions Learned**: Unique emotional states encountered  
- **Transitions Learned**: Successful emotional pathways discovered
- **Success Rate**: Effectiveness of suggested actions

## 🛠️ **Troubleshooting**

### **Agent Not Learning**
- Make sure you provide steps when asked after positive emotions
- Check that memory map shows connections between emotions
- Verify backend is saving experiences (check learning stats)

### **No Suggestions for Negative Emotions**
- First input positive emotions and teach successful steps
- The agent needs learned experiences to make suggestions
- Use "Reset Memory" to start fresh if needed

### **Memory Map Not Updating**
- Check browser console for API errors
- Ensure backend is running on port 5000
- Try refreshing the page to reload memory data

## 🔮 **Future Enhancements**

### **Advanced Learning**
- Weight actions by success frequency
- Implement temporal decay for old experiences
- Add user feedback on suggestion effectiveness

### **Improved Search**
- Multi-objective optimization (time, effort, success rate)
- Dynamic cost adjustment based on user feedback
- Context-aware pathfinding (time of day, situation)

### **Enhanced Visualization**
- 3D memory map representation
- Animated transition paths
- Historical timeline view
- Success rate heat maps

---

**This intelligent agent demonstrates how AI can learn from human experiences and use graph algorithms to provide personalized emotional support. The memory map evolves with each interaction, becoming a more effective guide over time.** 🧠✨

**Start learning**: `./start-intelligent-agent.sh` 🚀
````

## File: backend/app.py
````python
"""
Simplified Reflectly Flask App - AI-Focused Version
Contains only the core AI functionality for emotional pathfinding and analysis.
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from models.emotional_graph import EmotionalGraph
from models.emotion_analyzer import EmotionAnalyzer
from models.memory_manager import MemoryManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB connection
mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/reflectly')
mongo_client = MongoClient(mongo_uri)
db = mongo_client.reflectly

# Initialize AI models
emotional_graph = EmotionalGraph(db)
emotion_analyzer = EmotionAnalyzer()
memory_manager = MemoryManager(db)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "reflectly-ai"})

@app.route('/api/emotions/analyze', methods=['POST'])
def analyze_emotion():
    """Analyze emotion from text input"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        user_email = data.get('user_email', '')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
            
        # Analyze emotion
        emotion_result = emotion_analyzer.analyze_emotion(text)
        
        # Record emotion if user_email provided
        if user_email:
            emotion_id = emotional_graph.record_emotion(user_email, emotion_result)
            emotion_result['emotion_id'] = emotion_id
            
        return jsonify(emotion_result)
        
    except Exception as e:
        logger.error(f"Error analyzing emotion: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/path', methods=['POST'])
def find_emotional_path():
    """Find optimal path between emotions using A* search"""
    try:
        data = request.get_json()
        user_email = data.get('user_email', '')
        current_emotion = data.get('current_emotion', '')
        target_emotion = data.get('target_emotion', '')
        max_depth = data.get('max_depth', 10)
        
        if not all([user_email, current_emotion, target_emotion]):
            return jsonify({"error": "user_email, current_emotion, and target_emotion are required"}), 400
            
        # Find optimal path
        path_result = emotional_graph.get_emotional_path(
            user_email, current_emotion, target_emotion, max_depth
        )
        
        return jsonify(path_result)
        
    except Exception as e:
        logger.error(f"Error finding emotional path: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/suggestions', methods=['POST'])
def get_emotion_suggestions():
    """Get personalized action suggestions for current emotion"""
    try:
        data = request.get_json()
        user_email = data.get('user_email', '')
        current_emotion = data.get('current_emotion', '')
        
        if not all([user_email, current_emotion]):
            return jsonify({"error": "user_email and current_emotion are required"}), 400
            
        # Get suggestions
        suggestions = emotional_graph.get_suggested_actions(user_email, current_emotion)
        
        return jsonify({"suggestions": suggestions})
        
    except Exception as e:
        logger.error(f"Error getting emotion suggestions: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/history/<user_email>', methods=['GET'])
def get_emotion_history(user_email):
    """Get user's emotion history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get emotion history
        history = emotional_graph.get_emotion_history(user_email, limit)
        
        return jsonify({"history": history})
        
    except Exception as e:
        logger.error(f"Error getting emotion history: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/transitions/<user_email>', methods=['GET'])
def get_user_transitions(user_email):
    """Get user's emotional transitions for graph visualization"""
    try:
        # Get transitions
        transitions = emotional_graph.get_user_transitions(user_email)
        
        # Get available emotions for graph nodes
        available_emotions = emotional_graph.get_available_emotions()
        
        return jsonify({
            "transitions": transitions,
            "emotions": available_emotions
        })
        
    except Exception as e:
        logger.error(f"Error getting user transitions: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/graph-data/<user_email>', methods=['GET'])
def get_graph_data(user_email):
    """Get formatted data for emotional journey graph visualization"""
    try:
        # Get transitions
        transitions = emotional_graph.get_user_transitions(user_email)
        
        # Get emotion history
        history = emotional_graph.get_emotion_history(user_email, 50)
        
        # Format for graph visualization
        nodes = set()
        edges = []
        
        # Create nodes from emotions
        for emotion in emotional_graph.get_available_emotions():
            nodes.add(emotion)
            
        # Create edges from transitions
        for transition in transitions:
            from_emotion = transition.get('from_emotion')
            to_emotion = transition.get('to_emotion')
            
            if from_emotion and to_emotion:
                # Calculate edge weight based on frequency
                edge_exists = False
                for edge in edges:
                    if edge['from'] == from_emotion and edge['to'] == to_emotion:
                        edge['weight'] += 1
                        edge_exists = True
                        break
                        
                if not edge_exists:
                    edges.append({
                        'from': from_emotion,
                        'to': to_emotion,
                        'weight': 1,
                        'actions': transition.get('actions', [])
                    })
        
        # Convert nodes set to list of objects
        node_list = [{'id': emotion, 'label': emotion.title()} for emotion in nodes]
        
        return jsonify({
            "nodes": node_list,
            "edges": edges,
            "history": history
        })
        
    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/emotions/available', methods=['GET'])
def get_available_emotions():
    """Get list of available emotions"""
    try:
        emotions = emotional_graph.get_available_emotions()
        return jsonify({"emotions": emotions})
        
    except Exception as e:
        logger.error(f"Error getting available emotions: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/journal/analyze', methods=['POST'])
def analyze_journal_entry():
    """Analyze a journal entry and record emotional state"""
    try:
        data = request.get_json()
        user_email = data.get('user_email', '')
        content = data.get('content', '')
        
        if not all([user_email, content]):
            return jsonify({"error": "user_email and content are required"}), 400
            
        # Save journal entry
        entry_id = memory_manager.save_memory(user_email, content)
        
        # Analyze emotion
        emotion_result = emotion_analyzer.analyze_emotion(content)
        
        # Record emotion with entry link
        emotion_id = emotional_graph.record_emotion(user_email, emotion_result, entry_id)
        
        return jsonify({
            "entry_id": entry_id,
            "emotion_id": emotion_id,
            "emotion_analysis": emotion_result
        })
        
    except Exception as e:
        logger.error(f"Error analyzing journal entry: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Health check for AI services
@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    """Check status of AI components"""
    try:
        status = {
            "emotional_graph": True,
            "emotion_analyzer": True,
            "search_algorithm": True,
            "database_connection": True
        }
        
        # Test database connection
        try:
            db.list_collection_names()
        except:
            status["database_connection"] = False
            
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error checking AI status: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
````
