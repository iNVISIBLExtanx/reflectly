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
        self.positive_emotions = ['joy', 'surprise', 'happy', 'excited', 'content', 'calm']
        self.negative_emotions = ['sadness', 'anger', 'fear', 'disgust', 'sad', 'anxious', 'frustrated', 'stressed']
        self.neutral_emotions = ['neutral']
        
        # Define stress-related emotions for special handling
        self.stress_emotions = ['stressed', 'anxious', 'overwhelmed', 'worried']
        
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
            
    def get_graph(self):
        """
        Get the emotional graph structure as a dictionary suitable for A* search.
        
        Returns:
            dict: A dictionary where keys are emotion names and values are dictionaries
                  mapping to connected emotions with their transition costs.
        """
        # Get all unique emotions from the database
        all_emotions = set(self.positive_emotions + self.negative_emotions + self.neutral_emotions)
        
        # Initialize the graph structure
        graph = {emotion: {} for emotion in all_emotions}
        
        # Populate the graph with transitions from the database
        # Aggregate transitions to get counts and calculate probabilities
        pipeline = [
            {"$group": {
                "_id": {"from": "$from_emotion", "to": "$to_emotion"},
                "count": {"$sum": 1}
            }}
        ]
        
        transition_counts = list(self.transitions_collection.aggregate(pipeline))
        
        # Calculate transition costs (inverse of frequency)
        for transition in transition_counts:
            from_emotion = transition["_id"]["from"]
            to_emotion = transition["_id"]["to"]
            count = transition["count"]
            
            # Higher count means lower cost (1/count)
            # Add a small constant to avoid division by zero
            cost = 1.0 / (count + 0.1)
            
            if from_emotion in graph and to_emotion in all_emotions:
                graph[from_emotion][to_emotion] = cost
        
        # Ensure all emotions have at least some connections
        # If an emotion has no outgoing transitions, add connections to all emotions with high cost
        for emotion in all_emotions:
            if not graph[emotion]:
                for other in all_emotions:
                    if other != emotion:
                        graph[emotion][other] = 10.0  # High cost for rarely observed transitions
        
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
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Dictionary mapping from_emotion to a dictionary mapping to_emotion to probability
        """
        # Get all transitions for this user
        transitions = list(self.transitions_collection.find({
            'user_email': user_email
        }))
        
        # If no user-specific transitions, get default transitions
        if not transitions:
            transitions = list(self.transitions_collection.find({
                'user_email': 'default'
            }))
        
        # Create transition probability dictionary
        transition_probs = {}
        for transition in transitions:
            from_emotion = transition.get('from_emotion')
            to_emotion = transition.get('to_emotion')
            probability = transition.get('probability', 0.5)  # Default to 0.5 if not specified
            
            if from_emotion not in transition_probs:
                transition_probs[from_emotion] = {}
            
            transition_probs[from_emotion][to_emotion] = probability
        
        return transition_probs
        
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
