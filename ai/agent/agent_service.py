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
        
    def get_agent_state(self, user_email):
        """
        Get the current agent state for a user
        
        Args:
            user_email: User's email
            
        Returns:
            Dictionary with agent state
        """
        try:
            # Check if state exists in memory cache
            if user_email in self.user_states:
                return self.user_states[user_email].to_dict()
                
            # Check if state exists in database
            state_doc = self.db.agent_states.find_one({'user_email': user_email})
            
            if state_doc:
                # Convert document to AgentState object
                state = AgentState.from_dict(state_doc)
                self.user_states[user_email] = state
                return state.to_dict()
                
            # Create new state if not found
            return self._create_new_state(user_email).to_dict()
            
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
