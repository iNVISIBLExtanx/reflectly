"""
AgentService - Class for intelligent agent functionality, state management, and action planning
"""
import json
import uuid
from datetime import datetime
from .state import AgentState
from .planner import ActionPlanner

class AgentService:
    def __init__(self, db, astar_service, probabilistic_service):
        """
        Initialize the agent service
        
        Args:
            db: MongoDB database instance
            astar_service: Instance of AStarSearchService
            probabilistic_service: Instance of ProbabilisticService
        """
        self.db = db
        self.astar_service = astar_service
        self.probabilistic_service = probabilistic_service
        self.planner = ActionPlanner(astar_service, probabilistic_service)
        self.user_states = {}  # In-memory cache of user states
        
    def get_agent_state(self, user_email, include_predictions=False, include_journey=False, include_anomalies=False):
        """
        Get the current agent state for a user with optional emotional intelligence enhancements
        
        Args:
            user_email: User's email
            include_predictions: Whether to include emotional predictions
            include_journey: Whether to include emotional journey
            include_anomalies: Whether to detect and include emotional anomalies
            
        Returns:
            Dictionary with enhanced agent state
        """
        try:
            # Start with basic state retrieval
            state = None
            basic_state = None
            
            # Check if state exists in memory cache
            if user_email in self.user_states:
                state = self.user_states[user_email]
                basic_state = state.to_dict()
                
            # Check if state exists in database
            else:
                state_doc = self.db.agent_states.find_one({'user_email': user_email})
                
                if state_doc:
                    # Convert document to AgentState object
                    state = AgentState.from_dict(state_doc)
                    self.user_states[user_email] = state
                    basic_state = state.to_dict()
                else:
                    # Create new state if not found
                    state = self._create_new_state(user_email)
                    basic_state = state.to_dict()
            
            # Prepare enhanced response
            enhanced_state = dict(basic_state)  # Start with basic state
            
            # Extract current emotion
            current_emotion = state.current_emotion if state else 'neutral'
            
            # Add emotional predictions if requested
            if include_predictions:
                try:
                    # Get predictions for future emotional states
                    predictions = self.probabilistic_service.predict_emotional_sequence(
                        user_email, 
                        current_emotion, 
                        sequence_length=5, 
                        include_metadata=True
                    )
                    enhanced_state['emotional_predictions'] = predictions
                except Exception as e:
                    print(f"Error getting emotional predictions: {str(e)}")
                    enhanced_state['predictions_error'] = str(e)
            
            # Add emotional journey if requested
            if include_journey:
                try:
                    # Get emotional journey for the past week
                    journey = self.analyze_emotional_journey(
                        user_email, 
                        time_period='week',
                        include_insights=True
                    )
                    enhanced_state['emotional_journey'] = journey
                except Exception as e:
                    print(f"Error getting emotional journey: {str(e)}")
                    enhanced_state['journey_error'] = str(e)
            
            # Add emotional anomalies if requested
            if include_anomalies:
                try:
                    # Detect anomalies in emotional patterns
                    anomalies = self.detect_emotional_anomalies(
                        user_email,
                        lookback_period='month',
                        sensitivity=0.7
                    )
                    enhanced_state['emotional_anomalies'] = anomalies
                except Exception as e:
                    print(f"Error detecting emotional anomalies: {str(e)}")
                    enhanced_state['anomalies_error'] = str(e)
            
            # Add timestamp
            enhanced_state['timestamp'] = datetime.now().isoformat()
            
            return enhanced_state
            
        except Exception as e:
            print(f"Error in AgentService.get_agent_state: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a default state
            return {
                'user_email': user_email,
                'current_emotion': 'neutral',
                'target_emotion': None,
                'action_plan': [],
                'current_action_index': 0,
                'feedback_history': [],
                'error': str(e)
            }
            
    def analyze_decision(self, user_email, current_emotion, decision, options):
        """
        Analyze a decision with multiple options and predict emotional outcomes
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            decision: Description of the decision to be made
            options: List of options available (each should be a string)
            
        Returns:
            Dictionary with decision analysis
        """
        try:
            # Get user state
            user_state = self.get_agent_state(user_email, include_predictions=False)
            
            # Prepare results container
            results = {
                'decision': decision,
                'current_emotion': current_emotion,
                'options': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # Analyze each option
            for i, option in enumerate(options):
                # Predict emotional outcome of this option
                prediction = self.probabilistic_service.predict_next_emotion(
                    user_email,
                    current_emotion,
                    model_type='bayesian',
                    context={'decision': decision, 'option': option}
                )
                
                # Get potential path to a positive emotion if outcome is negative
                emotional_path = None
                if prediction.get('emotion') in ['sadness', 'anger', 'fear', 'disgust']:
                    # Find path to happiness or contentment
                    path_result = self.astar_service.find_emotional_path(
                        user_email,
                        prediction.get('emotion', 'neutral'),
                        'happiness',
                        include_actions=True
                    )
                    if path_result and 'path' in path_result:
                        emotional_path = path_result
                
                # Build option analysis
                option_analysis = {
                    'option': option,
                    'predicted_emotion': prediction.get('emotion'),
                    'confidence': prediction.get('confidence', 0),
                    'potential_impact': self._evaluate_emotional_impact(current_emotion, prediction.get('emotion')),
                    'recovery_path': emotional_path
                }
                
                results['options'].append(option_analysis)
            
            # Sort options by potential impact (most positive first)
            results['options'] = sorted(results['options'], key=lambda x: x['potential_impact'], reverse=True)
            
            # Add overall recommendation
            if results['options']:
                results['recommended_option'] = results['options'][0]['option']
                results['recommendation_reason'] = f"This option is predicted to lead to {results['options'][0]['predicted_emotion']} "\
                                              f"with {int(results['options'][0]['confidence']*100)}% confidence."
            
            return results
            
        except Exception as e:
            print(f"Error in analyze_decision: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'decision': decision,
                'current_emotion': current_emotion,
                'options': options
            }
    
    def _evaluate_emotional_impact(self, current_emotion, predicted_emotion):
        """
        Evaluate the emotional impact of a transition from current to predicted emotion
        Returns a score from -10 to 10, where positive means improvement
        """
        emotion_values = {
            'joy': 10,
            'happiness': 8,
            'contentment': 6,
            'excitement': 7,
            'gratitude': 9,
            'pride': 7,
            'interest': 5,
            'amusement': 6,
            'love': 9,
            'neutral': 0,
            'boredom': -2,
            'sadness': -6,
            'anger': -7,
            'fear': -8,
            'anxiety': -7,
            'guilt': -5,
            'shame': -6,
            'disgust': -6,
            'confusion': -3,
            'disappointment': -5
        }
        
        # Handle emotions not in our mapping
        current_value = emotion_values.get(current_emotion.lower(), 0)
        predicted_value = emotion_values.get(predicted_emotion.lower(), 0)
        
        # Calculate impact (-10 to 10 scale)
        impact = predicted_value - current_value
        return max(min(impact, 10), -10)  # Clamp between -10 and 10
            
    def analyze_emotional_journey(self, user_email, time_period=None, include_insights=False):
        """
        Analyze the user's emotional journey over a specific time period
        
        Args:
            user_email: User's email
            time_period: Time period to analyze ('day', 'week', 'month', 'all')
            include_insights: Whether to include detailed insights
            
        Returns:
            Dictionary with emotional journey analysis
        """
        try:
            # Set default time period if not specified
            if not time_period:
                time_period = 'week'
                
            # Get user's journal entries within time period
            query = {'user_email': user_email}
            
            # Add time filter based on time_period
            now = datetime.now()
            if time_period == 'day':
                # Last 24 hours
                from datetime import timedelta
                one_day_ago = now - timedelta(days=1)
                query['created_at'] = {'$gte': one_day_ago}
            elif time_period == 'week':
                # Last 7 days
                from datetime import timedelta
                one_week_ago = now - timedelta(days=7)
                query['created_at'] = {'$gte': one_week_ago}
            elif time_period == 'month':
                # Last 30 days
                from datetime import timedelta
                one_month_ago = now - timedelta(days=30)
                query['created_at'] = {'$gte': one_month_ago}
            # For 'all', we don't add any time filter
            
            # Get entries with emotions
            entries = list(self.db.journal_entries.find(
                query,
                {'emotion': 1, 'created_at': 1, 'content': 1, '_id': 0}
            ).sort('created_at', 1))  # Sort by creation time (oldest first)
            
            # Extract emotions and timeline
            emotions = []
            timeline = []
            for entry in entries:
                if 'emotion' in entry and 'primary_emotion' in entry.get('emotion', {}):
                    emotions.append(entry['emotion']['primary_emotion'])
                    timeline.append({
                        'timestamp': entry.get('created_at', now),
                        'emotion': entry['emotion']['primary_emotion'],
                        'intensity': entry['emotion'].get('intensity', 0.5),
                        'content_snippet': entry.get('content', '')[:50] + '...' if entry.get('content') else ''
                    })
            
            # If not enough data, return basic response
            if len(emotions) < 3:
                return {
                    'user_email': user_email,
                    'time_period': time_period,
                    'emotions_count': len(emotions),
                    'timeline': timeline,
                    'message': 'Not enough emotional data for meaningful analysis',
                    'analysis': None
                }
                
            # Create an instance of ProbabilisticReasoning
            from models.probabilistic_reasoning import ProbabilisticReasoning
            
            # Try to use EmotionalGraphBigData if available
            try:
                from models.emotional_graph_bigdata import EmotionalGraphBigData
                emotional_graph = EmotionalGraphBigData(self.db)
            except ImportError:
                from models.emotional_graph import EmotionalGraph
                emotional_graph = EmotionalGraph(self.db)
                
            reasoning = ProbabilisticReasoning(emotional_graph)
            
            # Analyze emotional journey
            analysis = reasoning.analyze_emotional_journey(emotions, include_insights=include_insights)
            
            # Prepare response
            result = {
                'user_email': user_email,
                'time_period': time_period,
                'emotions_count': len(emotions),
                'timeline': timeline,
                'analysis': analysis
            }
            
            # Add recent emotions trend
            if len(emotions) >= 3:
                recent_emotions = emotions[-3:]
                result['recent_trend'] = reasoning.analyze_emotional_trend(recent_emotions)
                
            # Add predicted next emotions
            if emotions:
                last_emotion = emotions[-1]
                next_predictions = self.probabilistic_service.predict_emotional_sequence(
                    user_email,
                    last_emotion,
                    sequence_length=3,
                    include_metadata=True
                )
                result['next_predictions'] = next_predictions
                
            return result
                
        except Exception as e:
            print(f"Error in AgentService.analyze_emotional_journey: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return basic error response
            return {
                'user_email': user_email,
                'time_period': time_period,
                'emotions_count': 0,
                'timeline': [],
                'error': str(e)
            }
            
    def detect_emotional_anomalies(self, user_email, lookback_period=None, sensitivity=0.7):
        """
        Detect anomalies in the user's emotional patterns
        
        Args:
            user_email: User's email
            lookback_period: Period to look back for analysis ('week', 'month', 'all')
            sensitivity: Threshold for anomaly detection (0.0-1.0)
            
        Returns:
            Dictionary with detected anomalies
        """
        try:
            # Set default lookback period if not specified
            if not lookback_period:
                lookback_period = 'month'
                
            # Get emotional journey analysis
            journey = self.analyze_emotional_journey(user_email, time_period=lookback_period)
            
            # If not enough data, return early
            if journey.get('emotions_count', 0) < 5:
                return {
                    'user_email': user_email,
                    'lookback_period': lookback_period,
                    'anomalies_detected': False,
                    'message': 'Not enough emotional data for anomaly detection',
                    'anomalies': []
                }
                
            # Get timeline of emotions
            timeline = journey.get('timeline', [])
            
            # Create an instance of ProbabilisticReasoning
            from models.probabilistic_reasoning import ProbabilisticReasoning
            from models.emotional_graph import EmotionalGraph
            
            # Try to use EmotionalGraphBigData if available
            try:
                from models.emotional_graph_bigdata import EmotionalGraphBigData
                emotional_graph = EmotionalGraphBigData(self.db)
            except ImportError:
                emotional_graph = EmotionalGraph(self.db)
                
            reasoning = ProbabilisticReasoning(emotional_graph)
            
            # Extract emotions from timeline
            emotions = [item.get('emotion') for item in timeline]
            
            # Detect anomalies
            anomalies = reasoning.detect_emotional_anomalies(
                emotions, 
                sensitivity=sensitivity
            )
            
            # Enrich anomalies with timeline data
            enriched_anomalies = []
            for anomaly in anomalies:
                anomaly_index = anomaly.get('index', 0)
                if 0 <= anomaly_index < len(timeline):
                    enriched_anomaly = {
                        **anomaly,
                        **timeline[anomaly_index]
                    }
                    enriched_anomalies.append(enriched_anomaly)
            
            return {
                'user_email': user_email,
                'lookback_period': lookback_period,
                'sensitivity': sensitivity,
                'anomalies_detected': len(enriched_anomalies) > 0,
                'anomalies_count': len(enriched_anomalies),
                'anomalies': enriched_anomalies
            }
                
        except Exception as e:
            print(f"Error in AgentService.detect_emotional_anomalies: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return basic error response
            return {
                'user_email': user_email,
                'lookback_period': lookback_period,
                'anomalies_detected': False,
                'error': str(e)
            }
            
    def generate_response(self, user_email, user_input, current_emotion=None, include_agent_state=False):
        """
        Generate a personalized response based on user input and emotional state
        
        Args:
            user_email: User's email
            user_input: Input text from the user
            current_emotion: Current emotional state (optional)
            include_agent_state: Whether to include the agent state in the response
            
        Returns:
            Dictionary with personalized response
        """
        try:
            # Get or create agent state
            state = self._get_or_create_state(user_email)
            
            # Update current emotion if provided
            if current_emotion:
                state.current_emotion = current_emotion
                
            # Extract current emotion from state
            emotion = state.current_emotion if state else 'neutral'
            
            # Create an intelligent response generator
            from models.intelligent_agent import IntelligentAgent
            
            # Create emotional graph
            try:
                from models.emotional_graph_bigdata import EmotionalGraphBigData
                emotional_graph = EmotionalGraphBigData(self.db)
            except ImportError:
                from models.emotional_graph import EmotionalGraph
                emotional_graph = EmotionalGraph(self.db)
                
            # Create agent
            agent = IntelligentAgent(emotional_graph, self.probabilistic_service)
            
            # Generate response
            response_data = agent.generate_response(
                user_input, 
                emotion,
                user_email
            )
            
            # Update agent state
            if 'next_emotion' in response_data:
                state.current_emotion = response_data['next_emotion']
                
            # Add action suggestions if available
            if 'action_suggestions' not in response_data and emotion:
                # Get intervention recommendations
                interventions = self.probabilistic_service.rank_interventions(
                    user_email,
                    emotion,
                    limit=3
                )
                response_data['action_suggestions'] = interventions
                
            # Save state
            self._save_state(state)
            
            # Include agent state if requested
            if include_agent_state:
                response_data['agent_state'] = state.to_dict()
                
                # Add emotional predictions
                response_data['emotional_predictions'] = self.probabilistic_service.predict_emotional_sequence(
                    user_email,
                    emotion,
                    sequence_length=3,
                    include_metadata=True
                )
                
            return response_data
                
        except Exception as e:
            print(f"Error in AgentService.generate_response: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return basic error response
            return {
                'user_email': user_email,
                'response': f"I'm having trouble processing that right now. Can you try again later?",
                'error': str(e)
            }
            
    def create_action_plan(self, user_email, current_emotion, target_emotion):
        """
        Create an action plan to transition from current emotion to target emotion
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            target_emotion: Target emotional state
            
        Returns:
            Dictionary with action plan
        """
        try:
            # Get or create agent state
            state = self._get_or_create_state(user_email)
            
            # Update state with current and target emotions
            state.current_emotion = current_emotion
            state.target_emotion = target_emotion
            
            # Create action plan using the planner
            action_plan = self.planner.create_plan(
                user_email,
                current_emotion,
                target_emotion
            )
            
            # Update state with new action plan
            state.action_plan = action_plan
            state.current_action_index = 0
            
            # Save state
            self._save_state(state)
            
            return {
                'user_email': user_email,
                'current_emotion': current_emotion,
                'target_emotion': target_emotion,
                'action_plan': action_plan,
                'current_action_index': 0
            }
            
        except Exception as e:
            print(f"Error in AgentService.create_action_plan: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a default action plan
            return {
                'user_email': user_email,
                'current_emotion': current_emotion,
                'target_emotion': target_emotion,
                'action_plan': [
                    {
                        'action_id': str(uuid.uuid4()),
                        'description': 'Take deep breaths and practice mindfulness',
                        'expected_emotion': 'calm',
                        'confidence': 0.7
                    }
                ],
                'current_action_index': 0,
                'error': str(e)
            }
            
    def execute_action(self, user_email, action_id, feedback=None):
        """
        Execute an action and update the agent state
        
        Args:
            user_email: User's email
            action_id: ID of the action to execute
            feedback: Optional feedback for the action
            
        Returns:
            Dictionary with updated state and next action
        """
        try:
            # Get agent state
            state = self._get_or_create_state(user_email)
            
            # Find the action in the plan
            action_index = -1
            for i, action in enumerate(state.action_plan):
                if action.get('action_id') == action_id:
                    action_index = i
                    break
                    
            if action_index == -1:
                raise ValueError(f"Action with ID {action_id} not found in the plan")
                
            # Record feedback if provided
            if feedback:
                state.feedback_history.append({
                    'action_id': action_id,
                    'feedback': feedback,
                    'timestamp': datetime.now()
                })
                
            # Update current action index to the next action
            state.current_action_index = action_index + 1
            
            # If we've reached the end of the plan, predict the next emotion
            next_action = None
            if state.current_action_index >= len(state.action_plan):
                # Predict next emotion
                prediction = self.probabilistic_service.predict_next_emotion(
                    user_email,
                    state.current_emotion
                )
                
                # Update current emotion based on prediction
                state.current_emotion = prediction['predicted_emotion']
                
                # Check if we've reached the target emotion
                if state.current_emotion == state.target_emotion:
                    state.action_plan = []
                    state.current_action_index = 0
                else:
                    # Create a new plan if needed
                    self.create_action_plan(
                        user_email,
                        state.current_emotion,
                        state.target_emotion
                    )
                    
                    # Get the state again with the new plan
                    state = self._get_or_create_state(user_email)
            
            # Get the next action if available
            if state.current_action_index < len(state.action_plan):
                next_action = state.action_plan[state.current_action_index]
                
            # Save state
            self._save_state(state)
            
            return {
                'user_email': user_email,
                'current_emotion': state.current_emotion,
                'target_emotion': state.target_emotion,
                'current_action_index': state.current_action_index,
                'next_action': next_action,
                'plan_complete': state.current_action_index >= len(state.action_plan)
            }
            
        except Exception as e:
            print(f"Error in AgentService.execute_action: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a default response
            return {
                'user_email': user_email,
                'error': str(e),
                'next_action': None,
                'plan_complete': True
            }
            
    def _get_or_create_state(self, user_email):
        """
        Get or create an agent state for a user
        
        Args:
            user_email: User's email
            
        Returns:
            AgentState object
        """
        # Check if state exists in memory cache
        if user_email in self.user_states:
            return self.user_states[user_email]
            
        # Check if state exists in database
        state_doc = self.db.agent_states.find_one({'user_email': user_email})
        
        if state_doc:
            # Convert document to AgentState object
            state = AgentState.from_dict(state_doc)
            self.user_states[user_email] = state
            return state
            
        # Create new state if not found
        return self._create_new_state(user_email)
        
    def _create_new_state(self, user_email):
        """
        Create a new agent state for a user
        
        Args:
            user_email: User's email
            
        Returns:
            AgentState object
        """
        # Get user's latest emotion from journal entries
        # Check if user has any journal entries
        entry_count = self.db.journal_entries.count_documents({"user_email": user_email})
        if entry_count == 0:
            # No journal entries, return a special state indicating this
            state = AgentState(
                user_id=str(uuid.uuid4()),  # Generate a unique user_id
                user_email=user_email,
                current_emotion="neutral",
                target_emotion=None,
                action_plan=[{
                    "id": "default-action-1",
                    "type": "journal",
                    "description": "Create your first journal entry to start tracking your emotional journey",
                    "from_emotion": "neutral",
                    "to_emotion": "neutral",
                    "effectiveness": 1.0,
                    "certainty": 1.0
                }],
                current_action_index=0,
                feedback_history=[]
            )
            
            # Save to database
            self._save_state(state)
            
            # Add to memory cache
            self.user_states[user_email] = state
            
            return state
        
        latest_entry = self.db.journal_entries.find_one(
            {'user_email': user_email, 'isUserMessage': True},
            {'emotion': 1}
        )
        
        current_emotion = 'neutral'
        if latest_entry and 'emotion' in latest_entry and 'primary_emotion' in latest_entry['emotion']:
            current_emotion = latest_entry['emotion']['primary_emotion']
            
        # Create new state
        state = AgentState(
            user_id=str(uuid.uuid4()),  # Generate a unique user_id
            user_email=user_email,
            current_emotion=current_emotion,
            target_emotion=None,
            action_plan=[],
            current_action_index=0,
            feedback_history=[]
        )
        
        # Save to database
        self._save_state(state)
        
        # Add to memory cache
        self.user_states[user_email] = state
        
        return state
        
    def _save_state(self, state):
        """
        Save agent state to the database
        
        Args:
            state: AgentState object to save
        """
        # Convert state to dictionary
        state_dict = state.to_dict()
        
        # Update or insert state in database
        self.db.agent_states.update_one(
            {'user_email': state.user_email},
            {'$set': state_dict},
            upsert=True
        )
        
    def analyze_decision(self, user_email, current_emotion, decision, options):
        """
        Analyze a decision with multiple options based on emotional impact
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            decision: The decision to be made
            options: List of options to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Get the user's emotional graph
            emotional_graph = self.probabilistic_service.get_emotional_graph(user_email)
            
            # Analyze each option
            analyzed_options = []
            best_option_index = 0
            best_score = -float('inf')
            
            for i, option in enumerate(options):
                # Predict emotional impact using probabilistic model
                impact = self.probabilistic_service.predict_emotional_impact(
                    user_email,
                    current_emotion,
                    option.get('text', '')
                )
                
                # Calculate recommendation score based on emotional impact
                # Higher positive impact = higher score
                confidence = impact.get('confidence', 0.5)
                emotional_impact = impact.get('emotional_impact', 0)
                recommendation_score = emotional_impact * 5 + 5  # Scale to 0-10
                
                # Track best option
                if recommendation_score > best_score:
                    best_score = recommendation_score
                    best_option_index = i
                
                # Add analysis to option
                analyzed_options.append({
                    **option,
                    'analysis': {
                        'emotional_impact': emotional_impact,
                        'confidence': confidence,
                        'recommendation_score': recommendation_score
                    }
                })
            
            # Generate explanation
            explanation = self._generate_decision_explanation(
                current_emotion,
                analyzed_options,
                best_option_index
            )
            
            return {
                'decision': decision,
                'current_emotion': current_emotion,
                'options': analyzed_options,
                'best_option': best_option_index + 1,  # 1-indexed for user display
                'explanation': explanation
            }
            
        except Exception as e:
            print(f"Error in AgentService.analyze_decision: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a default analysis
            return {
                'decision': decision,
                'current_emotion': current_emotion,
                'options': options,
                'best_option': 1,
                'explanation': "Unable to analyze decision due to an error: " + str(e),
                'error': str(e)
            }
            
    def _generate_decision_explanation(self, current_emotion, options, best_option_index):
        """
        Generate an explanation for the decision recommendation
        
        Args:
            current_emotion: Current emotional state
            options: List of analyzed options
            best_option_index: Index of the best option
            
        Returns:
            String explanation
        """
        best_option = options[best_option_index]
        best_impact = best_option['analysis']['emotional_impact']
        best_score = best_option['analysis']['recommendation_score']
        
        # Generate explanation based on impact
        if best_impact > 0.5:
            return f"Option {best_option_index + 1} is strongly recommended because it's likely to significantly improve your emotional state from '{current_emotion}' to a more positive state."
        elif best_impact > 0:
            return f"Option {best_option_index + 1} is recommended because it may help improve your emotional state from '{current_emotion}' to a slightly more positive state."
        elif best_impact > -0.3:
            return f"Option {best_option_index + 1} is recommended as the best choice, though it may have a neutral effect on your current '{current_emotion}' state."
        else:
            return f"All options may have some negative emotional impact, but option {best_option_index + 1} is the least likely to worsen your current '{current_emotion}' state."
