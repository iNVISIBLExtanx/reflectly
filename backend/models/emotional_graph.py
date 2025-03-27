import datetime
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from models.dataset.iemocap_integration import IemocapIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionalGraph:
    """
    Represents and manages emotional state transitions.
    Stores emotional states as nodes in a graph structure, with transitions between states as edges.
    """
    
    def __init__(self, db):
        """
        Initialize the EmotionalGraph with a database connection and IEMOCAP dataset integration.
        The IEMOCAP dataset provides data-driven transition probabilities between emotional states.
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
        self.emotions_collection = db.emotional_states
        self.transitions_collection = db.emotional_transitions
        
        # Initialize the IEMOCAP integration for data-driven transition probabilities
        try:
            self.iemocap = IemocapIntegration()
            self.using_dataset_transitions = True
            logger.info("IEMOCAP dataset integration initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize IEMOCAP integration: {e}. Using default transitions.")
            self.using_dataset_transitions = False
        
        # Define positive and negative emotions
        self.positive_emotions = ['joy', 'surprise', 'happy', 'excited', 'content', 'calm']
        self.negative_emotions = ['sadness', 'anger', 'fear', 'disgust', 'sad', 'anxious', 'frustrated', 'stressed']
        self.neutral_emotions = ['neutral']
        
        # Define stress-related emotions for special handling
        self.stress_emotions = ['stressed', 'anxious', 'overwhelmed', 'worried']
        
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
        
    def record_emotion(self, user_email, emotion_data, entry_id=None):
        """
        Record an emotional state for a user and update transition probabilities.
        Uses IEMOCAP data-driven insights to predict potential next emotions and
        identify unusual transitions.
        
        Args:
            user_email (str): The user's email
            emotion_data (dict): Emotion analysis data
            entry_id (str, optional): Associated journal entry ID
            
        Returns:
            dict: Dictionary containing the recorded emotional state ID and additional insights
        """
        # Extract primary emotion
        primary_emotion = emotion_data.get('primary_emotion', 'neutral')
        current_timestamp = datetime.datetime.now()
        
        # Create emotional state document with enhanced fields
        emotion_state = {
            'user_email': user_email,
            'primary_emotion': primary_emotion,
            'is_positive': emotion_data.get('is_positive', False),
            'emotion_scores': emotion_data.get('emotion_scores', {}),
            'secondary_emotion': emotion_data.get('secondary_emotion'),
            'intensity': emotion_data.get('intensity', 3),
            'context_factors': emotion_data.get('context_factors', []),
            'entry_id': entry_id,
            'timestamp': current_timestamp
        }
        
        # Get insights about this emotion from IEMOCAP if available
        if self.using_dataset_transitions and primary_emotion:
            try:
                # Map to IEMOCAP emotion category if needed
                mapped_emotion = self.emotion_mapping.get(primary_emotion, primary_emotion)
                # Get emotion triggers from IEMOCAP dataset
                triggers = self.iemocap.get_emotion_triggers(mapped_emotion)
                if triggers:
                    emotion_state['potential_triggers'] = triggers
                    logger.info(f"Added {len(triggers)} potential triggers for {primary_emotion} from IEMOCAP dataset")
            except Exception as e:
                logger.warning(f"Error getting emotion triggers from IEMOCAP: {e}")
        
        # Insert into database
        result = self.emotions_collection.insert_one(emotion_state)
        emotion_state_id = result.inserted_id
        
        # Prepare response with insights
        response = {
            'emotion_state_id': str(emotion_state_id),
            'insights': {}
        }
        
        # Get previous emotional state to create transition
        previous_state = self._get_previous_emotional_state(user_email)
        
        # If there's a previous state, record the transition and analyze it
        if previous_state:
            from_emotion = previous_state['primary_emotion']
            to_emotion = primary_emotion
            from_state_id = previous_state['_id']
            to_state_id = emotion_state_id
            
            # Record the transition in our database
            transition_id = self._record_transition(user_email, from_emotion, to_emotion, from_state_id, to_state_id)
            
            # Analyze this transition using the IEMOCAP dataset if available
            if self.using_dataset_transitions:
                try:
                    # Map our emotions to IEMOCAP categories if needed
                    mapped_from = self.emotion_mapping.get(from_emotion, from_emotion)
                    mapped_to = self.emotion_mapping.get(to_emotion, to_emotion)
                    
                    # Get the transition probability from IEMOCAP
                    dataset_prob = self.iemocap.get_transition_probability(mapped_from, mapped_to)
                    
                    # Determine if this is an unusual transition
                    is_unusual = dataset_prob < 0.1  # Less than 10% probability
                    
                    # Add transition analysis to response
                    response['insights']['transition_analysis'] = {
                        'from_emotion': from_emotion,
                        'to_emotion': to_emotion,
                        'dataset_probability': dataset_prob,
                        'is_unusual_transition': is_unusual
                    }
                    
                    # Update transition with probability from dataset
                    self.transitions_collection.update_one(
                        {'_id': ObjectId(transition_id)},
                        {'$set': {'probability': dataset_prob, 'is_unusual': is_unusual}}
                    )
                    logger.info(f"Updated transition {from_emotion} -> {to_emotion} with probability {dataset_prob}")
                    
                except Exception as e:
                    logger.warning(f"Error analyzing transition with IEMOCAP: {e}")
        
        # Predict potential next emotions using our transition model
        try:
            # Get transition probabilities for this user (blended model)
            transition_probs = self.get_transition_probabilities(user_email)
            
            # If we have probabilities for the current emotion, predict next emotions
            if primary_emotion in transition_probs:
                # Sort next emotions by probability
                next_emotions = sorted(
                    [(emotion, prob) for emotion, prob in transition_probs[primary_emotion].items()],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Take top 3 most likely next emotions
                top_next_emotions = next_emotions[:3]
                
                # Add to response
                response['insights']['likely_next_emotions'] = [
                    {'emotion': emotion, 'probability': prob}
                    for emotion, prob in top_next_emotions
                ]
                logger.info(f"Predicted {len(top_next_emotions)} likely next emotions from {primary_emotion}")
        except Exception as e:
            logger.warning(f"Error predicting next emotions: {e}")
        
        # Clear transition probability cache for this user to ensure fresh data next time
        cache_key = f"{user_email}_transitions"
        if cache_key in self.transition_probability_cache:
            del self.transition_probability_cache[cache_key]
        
        return response
    
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
        
    def analyze_stress_patterns(self, user_email, days=30):
        """
        Analyze stress patterns over a specified time period.
        
        Args:
            user_email (str): The user's email
            days (int): Number of days to analyze
            
        Returns:
            dict: Analysis of stress patterns including frequency, triggers, and recommendations
        """
        # Calculate the start date for analysis
        start_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        # Find all emotional states in the given time period
        states = list(self.emotions_collection.find(
            {
                'user_email': user_email,
                'timestamp': {'$gte': start_date}
            },
            sort=[('timestamp', 1)]  # Sort by timestamp ascending
        ))
        
        # Count stress-related emotions
        stress_count = 0
        stress_dates = []
        stress_entries = []
        
        for state in states:
            # Check if this is a stress-related emotion
            is_stress_related = False
            
            # Check primary emotion
            if state['primary_emotion'] in self.stress_emotions:
                is_stress_related = True
            # Also check if 'fear' with high score might indicate stress
            elif state['primary_emotion'] == 'fear' and state.get('entry_id'):
                # Look up the entry to check content
                entry = self.db.journal_entries.find_one({'_id': ObjectId(state['entry_id'])})
                if entry and 'content' in entry and 'stress' in entry['content'].lower():
                    is_stress_related = True
                    
            if is_stress_related:
                stress_count += 1
                stress_dates.append(state['timestamp'].strftime('%Y-%m-%d'))
                if state.get('entry_id'):
                    stress_entries.append(state['entry_id'])
        
        # Calculate frequency
        total_days = min(days, (datetime.datetime.now() - start_date).days + 1)
        frequency = stress_count / total_days if total_days > 0 else 0
        
        # Get common triggers if we have stress entries
        triggers = []
        if stress_entries:
            entries = list(self.db.journal_entries.find({'_id': {'$in': [ObjectId(id) for id in stress_entries]}}))            
            # Simple keyword analysis for common triggers
            trigger_keywords = ['work', 'deadline', 'meeting', 'family', 'health', 'money', 'relationship', 'sleep']
            trigger_counts = {keyword: 0 for keyword in trigger_keywords}
            
            for entry in entries:
                if 'content' in entry:
                    content = entry['content'].lower()
                    for keyword in trigger_keywords:
                        if keyword in content:
                            trigger_counts[keyword] += 1
            
            # Get top triggers
            triggers = [k for k, v in sorted(trigger_counts.items(), key=lambda item: item[1], reverse=True) if v > 0][:3]
        
        # Generate recommendations based on frequency and triggers
        recommendations = []
        if frequency > 0.5:  # More than 50% of days have stress
            recommendations.append("You're experiencing frequent stress. Consider speaking with a mental health professional.")
            recommendations.append("Daily stress management practices like meditation may be beneficial.")
        elif frequency > 0.2:  # More than 20% of days have stress
            recommendations.append("You're experiencing moderate stress levels. Regular exercise and mindfulness can help.")
        else:
            recommendations.append("Your stress levels appear manageable. Continue your current coping strategies.")
            
        # Add trigger-specific recommendations
        for trigger in triggers:
            if trigger == 'work' or trigger == 'deadline':
                recommendations.append("Work-related stress: Try time-blocking techniques and setting boundaries.")
            elif trigger == 'family' or trigger == 'relationship':
                recommendations.append("Relationship stress: Open communication and setting healthy boundaries may help.")
            elif trigger == 'health':
                recommendations.append("Health-related stress: Regular check-ups and self-care are important.")
            elif trigger == 'money':
                recommendations.append("Financial stress: Creating a budget and speaking with a financial advisor might help.")
            elif trigger == 'sleep':
                recommendations.append("Sleep-related stress: Establish a consistent sleep schedule and bedtime routine.")
        
        return {
            'stress_frequency': frequency,
            'stress_count': stress_count,
            'total_days': total_days,
            'common_triggers': triggers,
            'recommendations': recommendations,
            'stress_dates': stress_dates
        }
    
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
            'stressed': [
                "Try the 4-7-8 breathing technique (inhale for 4, hold for 7, exhale for 8)",
                "Take a 10-minute break from your current task",
                "Go for a short walk outside",
                "Practice mindfulness meditation for 5 minutes",
                "Write down your top 3 priorities to gain clarity",
                "Stretch or do gentle yoga poses",
                "Listen to calming music"
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
    
    def get_emotion_history(self, user_email, limit=5):
        """
        Get a user's emotional history, ordered by most recent first.
        
        Args:
            user_email (str): The user's email
            limit (int): Maximum number of emotional states to return
            
        Returns:
            list: List of emotional state documents
        """
        try:
            # Get the most recent emotional states for the user
            emotion_history = list(self.emotions_collection.find(
                {'user_email': user_email}
            ).sort('timestamp', -1).limit(limit))
            
            # Convert ObjectId to string for serialization
            for state in emotion_history:
                if '_id' in state:
                    state['_id'] = str(state['_id'])
                    
            return emotion_history
        except Exception as e:
            print(f"Error retrieving emotion history: {str(e)}")
            return []
    
    def _extract_activity_from_transition(self, transition):
        """
        Extract a potential activity that led to a positive emotional transition.
        This is a simplified implementation that could be enhanced with NLP in production.
        
        Args:
            transition: The emotional transition document
            
        Returns:
            str: A suggested activity or None
        """
        # This would ideally use NLP to extract activities from journal entries
        # For now, we'll return a simplified suggestion based on the emotions involved
        from_emotion = transition.get('from_emotion', '')
        to_emotion = transition.get('to_emotion', '')
        
        if from_emotion == 'sadness' and to_emotion == 'joy':
            return "connecting with friends or engaging in a favorite hobby"
        elif from_emotion == 'anger' and to_emotion in self.positive_emotions:
            return "physical exercise or creative expression"
        elif from_emotion == 'fear' and to_emotion in self.positive_emotions:
            return "meditation or talking through your concerns"
        elif from_emotion == 'disgust' and to_emotion in self.positive_emotions:
            return "focusing on gratitude or spending time in nature"
        elif from_emotion == 'neutral' and to_emotion in self.positive_emotions:
            return "setting and achieving small goals"
        else:
            return None
            
    def get_graph(self, user_email=None):
        """
        Get the emotional graph structure as a dictionary suitable for A* search.
        The graph is weighted by the transition costs derived from the IEMOCAP dataset
        and user history, if available.
        
        Args:
            user_email (str, optional): The user's email for personalized graph
            
        Returns:
            dict: A dictionary where keys are emotion names and values are dictionaries
                  mapping to connected emotions with their transition costs.
        """
        # Get all unique emotions from our defined emotions
        all_emotions = set(self.positive_emotions + self.negative_emotions + self.neutral_emotions)
        
        # Initialize the graph structure
        graph = {emotion: {} for emotion in all_emotions}
        
        # If we have a user email, get personalized transition probabilities
        if user_email:
            logger.info(f"Building personalized emotional graph for user: {user_email}")
            # Get transition probabilities for this user (dataset + user history blend)
            transition_probs = self.get_transition_probabilities(user_email)
        elif self.using_dataset_transitions:
            logger.info("Building dataset-derived emotional graph (no user personalization)")
            # Use only dataset-derived transition probabilities
            transition_probs = self._get_dataset_transition_probabilities()
        else:
            logger.info("Building default emotional graph (no dataset or user data)")
            # Fall back to database transitions
            transition_probs = {}
            
            # Populate transition_probs with data from the database
            pipeline = [
                {"$group": {
                    "_id": {"from": "$from_emotion", "to": "$to_emotion"},
                    "count": {"$sum": 1}
                }}
            ]
            
            transition_counts = list(self.transitions_collection.aggregate(pipeline))
            
            for transition in transition_counts:
                from_emotion = transition["_id"]["from"]
                to_emotion = transition["_id"]["to"]
                count = transition["count"]
                
                if from_emotion not in transition_probs:
                    transition_probs[from_emotion] = {}
                
                # Calculate probability from count
                total_from = sum(t["count"] for t in transition_counts 
                               if t["_id"]["from"] == from_emotion)
                probability = count / total_from if total_from > 0 else 0.0
                
                transition_probs[from_emotion][to_emotion] = probability
        
        # Convert transition probabilities to costs for A* search
        # For each emotion pair, cost = -log(probability) to make higher probabilities = lower costs
        import math
        for from_emotion, to_emotions in transition_probs.items():
            if from_emotion in graph:
                for to_emotion, probability in to_emotions.items():
                    if to_emotion in all_emotions:
                        # Avoid log(0) and ensure a minimum cost
                        p = max(probability, 0.01)
                        # Higher probability means lower cost
                        graph[from_emotion][to_emotion] = -math.log(p)
        
        # Ensure all emotions have at least some connections
        for emotion in all_emotions:
            if not graph[emotion]:
                logger.warning(f"No transitions found for emotion: {emotion}. Adding default connections.")
                for other in all_emotions:
                    if other != emotion:
                        # High cost for rarely observed transitions
                        graph[emotion][other] = 10.0
            else:
                # Ensure connections to all emotions
                for other in all_emotions:
                    if other != emotion and other not in graph[emotion]:
                        # Add with high cost, but lower than default for no transitions
                        graph[emotion][other] = 8.0
        
        return graph
        
    def get_transition_actions(self, user_email, from_emotion, to_emotion):
        """
        Get suggested actions for transitioning from one emotional state to another.
        
        Args:
            user_email (str): The user's email
            from_emotion (str): Starting emotional state
            to_emotion (str): Target emotional state
            
        Returns:
            list: List of suggested actions
        """
        # Check if there's a recorded transition between these emotions for this user
        transition = self.transitions_collection.find_one({
            'user_email': user_email,
            'from_emotion': from_emotion,
            'to_emotion': to_emotion
        })
        
        if transition and 'actions' in transition:
            return transition['actions']
        
        # If no user-specific transition, check for default transitions
        default_transition = self.transitions_collection.find_one({
            'user_email': 'default',
            'from_emotion': from_emotion,
            'to_emotion': to_emotion
        })
        
        if default_transition and 'actions' in default_transition:
            return default_transition['actions']
        
        # If still no actions, return empty list
        return []
        
    def get_transition_probabilities(self, user_email):
        """
        Get transition probabilities between emotional states for a user.
        Combines IEMOCAP dataset-derived probabilities with user-specific transition history.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Dictionary mapping from_emotion to a dictionary mapping to_emotion to probability
        """
        # Check if we've cached this result recently to avoid repeated computation
        cache_key = f"{user_email}_transitions"
        if cache_key in self.transition_probability_cache:
            return self.transition_probability_cache[cache_key]
        
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
        
    def get_user_history(self, user_email):
        """
        Get user's historical emotional transitions and their effectiveness.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Dictionary containing user's historical emotional transitions and their effectiveness
        """
        # Get all emotional states for this user
        emotional_states = list(self.emotions_collection.find({
            'user_email': user_email
        }).sort('timestamp', 1))  # Sort by timestamp ascending
        
        # Create user history dictionary
        user_history = {}
        
        # Process emotional states to extract transitions
        for i in range(len(emotional_states) - 1):
            current_state = emotional_states[i]
            next_state = emotional_states[i + 1]
            
            current_emotion = current_state.get('primary_emotion', 'neutral')
            next_emotion = next_state.get('primary_emotion', 'neutral')
            
            # Calculate time difference between states
            time_diff = (next_state.get('timestamp') - current_state.get('timestamp')).total_seconds()
            
            # Determine if transition was effective (shorter time is more effective)
            effectiveness = 1.0 / (1.0 + time_diff / 3600.0)  # Normalize by hours
            
            # Add to user history
            if current_emotion not in user_history:
                user_history[current_emotion] = {}
            
            if next_emotion not in user_history[current_emotion]:
                user_history[current_emotion][next_emotion] = []
            
            user_history[current_emotion][next_emotion].append(effectiveness)
        
        # Average effectiveness for each transition
        for from_emotion in user_history:
            for to_emotion in user_history[from_emotion]:
                effectiveness_list = user_history[from_emotion][to_emotion]
                user_history[from_emotion][to_emotion] = sum(effectiveness_list) / len(effectiveness_list)
        
        return user_history
