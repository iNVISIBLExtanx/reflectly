"""
AgentService - Service for intelligent agent functionality, state management and action planning
"""
import uuid
from datetime import datetime

class AgentService:
    def __init__(self, db, emotional_graph, astar_search_service, probabilistic_service):
        """
        Initialize the agent service
        
        Args:
            db: MongoDB database instance
            emotional_graph: Instance of EmotionalGraph
            astar_search_service: Instance of AStarSearchService
            probabilistic_service: Instance of ProbabilisticService
        """
        self.db = db
        self.emotional_graph = emotional_graph
        self.astar_search_service = astar_search_service
        self.probabilistic_service = probabilistic_service
        
    def get_agent_state(self, user_email):
        """
        Get the current state of the agent for a user
        
        Args:
            user_email: User's email
            
        Returns:
            Dictionary with agent state
        """
        try:
            # Get user's current emotional state
            current_emotion = self._get_current_emotion(user_email)
            
            # Get user's emotional history
            emotion_history = self.emotional_graph.get_emotion_history(user_email, limit=5)
            
            # Get active action plans
            action_plans = list(self.db.action_plans.find({
                'user_email': user_email,
                'status': 'active'
            }).sort('created_at', -1))
            
            # Format action plans
            formatted_plans = []
            for plan in action_plans:
                formatted_plans.append({
                    'id': str(plan.get('_id')),
                    'current_emotion': plan.get('current_emotion'),
                    'target_emotion': plan.get('target_emotion'),
                    'actions': plan.get('actions', []),
                    'progress': plan.get('progress', 0),
                    'created_at': plan.get('created_at')
                })
            
            # Get prediction for next emotional state
            prediction = self.probabilistic_service.predict_next_emotion(
                user_email, 
                current_emotion
            )
            
            return {
                'user_email': user_email,
                'current_emotion': current_emotion,
                'emotion_history': emotion_history,
                'active_plans': formatted_plans,
                'prediction': prediction,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error in AgentService.get_agent_state: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'user_email': user_email,
                'current_emotion': 'neutral',
                'emotion_history': [],
                'active_plans': [],
                'error': str(e)
            }
            
    def create_action_plan(self, user_email, current_emotion, target_emotion, context=None):
        """
        Create an action plan to move from current_emotion to target_emotion
        
        Args:
            user_email: User's email
            current_emotion: Current emotional state
            target_emotion: Target emotional state
            context: Additional context for the plan
            
        Returns:
            Dictionary with action plan
        """
        try:
            # Check if user has any journal entries
            entry_count = self.db.journal_entries.count_documents({"user_email": user_email})
            if entry_count == 0:
                # No journal entries, return a special action plan for new users
                return {
                    "user_email": user_email,
                    "current_emotion": current_emotion,
                    "target_emotion": target_emotion,
                    "path": ["neutral"],
                    "actions": [{
                        "id": "new-user-action-1",
                        "from_emotion": "neutral",
                        "to_emotion": "neutral",
                        "description": "Create your first journal entry to start your emotional journey",
                        "status": "pending",
                        "feedback": None,
                        "created_at": datetime.now()
                    }],
                    "context": context,
                    "status": "active",
                    "progress": 0,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "is_default": True,
                    "message": "This is a default plan for new users. Create journal entries to get personalized action plans."
                }
            if context is None:
                context = {}
                
            # Get path using A* search
            path_result = self.astar_search_service.find_path(
                user_email, 
                current_emotion, 
                target_emotion
            )
            
            if not path_result or 'path' not in path_result or not path_result['path']:
                return {
                    'message': 'Could not create action plan - no path found',
                    'status': 'error'
                }
                
            # Create actions for each step in the path
            actions = []
            for i in range(len(path_result['path']) - 1):
                from_emotion = path_result['path'][i]
                to_emotion = path_result['path'][i + 1]
                
                # Get suggested actions for this transition
                suggested_actions = self.emotional_graph.get_transition_actions(
                    user_email, 
                    from_emotion, 
                    to_emotion
                )
                
                # If no suggested actions, provide default ones
                if not suggested_actions:
                    if to_emotion in ['happy', 'joy', 'excited', 'content', 'calm']:
                        suggested_actions = [
                            'Practice gratitude',
                            'Engage in physical activity',
                            'Connect with a loved one',
                            'Spend time in nature',
                            'Listen to uplifting music'
                        ]
                    else:
                        suggested_actions = [
                            'Practice mindfulness',
                            'Write in your journal',
                            'Take deep breaths',
                            'Talk to someone you trust',
                            'Focus on what you can control'
                        ]
                
                # Create action for this step
                for action in suggested_actions[:3]:  # Limit to 3 actions per step
                    actions.append({
                        'id': str(uuid.uuid4()),
                        'from_emotion': from_emotion,
                        'to_emotion': to_emotion,
                        'description': action,
                        'status': 'pending',
                        'feedback': None,
                        'created_at': datetime.now()
                    })
            
            # Create action plan
            plan = {
                'user_email': user_email,
                'current_emotion': current_emotion,
                'target_emotion': target_emotion,
                'path': path_result['path'],
                'actions': actions,
                'context': context,
                'status': 'active',
                'progress': 0,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Store in database
            result = self.db.action_plans.insert_one(plan)
            plan_id = result.inserted_id
            
            # Return plan with ID
            plan['id'] = str(plan_id)
            return plan
        except Exception as e:
            print(f"Error in AgentService.create_action_plan: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'message': f'Error creating action plan: {str(e)}',
                'status': 'error'
            }
            
    def analyze_emotional_journey(self, user_email, time_period='week', include_insights=False):
        """
        Analyze a user's emotional journey over a specified time period
        
        Args:
            user_email: User's email
            time_period: Time period for analysis (week, month, all)
            include_insights: Whether to include insights in the result
            
        Returns:
            Dictionary with emotional journey data
        """
        try:
            print(f"DEBUG: analyze_emotional_journey called for user {user_email}, time_period={time_period}, include_insights={include_insights}")
            # Get time filter based on time period
            time_filter = {}
            from datetime import datetime, timedelta
            now = datetime.now()
            print(f"DEBUG: Current time: {now}")
            
            if time_period != 'all':
                if time_period == 'week':
                    start_date = now - timedelta(days=7)
                    time_filter = {'created_at': {'$gte': start_date}}
                    print(f"DEBUG: Week filter from {start_date}")
                elif time_period == 'month':
                    start_date = now - timedelta(days=30)
                    time_filter = {'created_at': {'$gte': start_date}}
                    print(f"DEBUG: Month filter from {start_date}")
            
            # Query database for journal entries
            query = {'user_email': user_email}
            query.update(time_filter)
            print(f"DEBUG: MongoDB query: {query}")
            
            # Check total entries for user regardless of time filter
            total_entries = self.db.journal_entries.count_documents({'user_email': user_email})
            print(f"DEBUG: Total entries for user: {total_entries}")
            
            # Get a sample entry to examine its structure
            sample_entry = self.db.journal_entries.find_one({'user_email': user_email})
            if sample_entry:
                print(f"DEBUG: Sample entry: {sample_entry}")
                print(f"DEBUG: Sample entry created_at type: {type(sample_entry.get('created_at'))}")
                print(f"DEBUG: Sample entry created_at value: {sample_entry.get('created_at')}")
            
            # Get entries sorted by date
            entries = list(self.db.journal_entries.find(query).sort('created_at', 1))
            print(f"DEBUG: Found {len(entries)} entries matching the time filter")
                        # Process entries to create data points
            data_points = []
            for entry in entries:
                # Skip entries that are explicitly marked as AI responses (not user messages)
                # If isUserMessage is None or not present, assume it's a user message
                if entry.get('isUserMessage') is False:  # explicitly check for False
                    print(f"DEBUG: Skipping AI response entry: {entry.get('_id')}")
                    continue
                    
                print(f"DEBUG: Processing entry with isUserMessage={entry.get('isUserMessage')}")
                    
                # Extract the emotion - handle both old and new data format
                emotion_data = entry.get('emotion', {})
                if isinstance(emotion_data, dict) and 'primary_emotion' in emotion_data:
                    # New format - emotion is an object with primary_emotion
                    emotion = emotion_data.get('primary_emotion', 'neutral')
                    intensity = max(emotion_data.get('emotion_scores', {}).values()) if emotion_data.get('emotion_scores') else 0.5
                else:
                    # Old format - emotion is a string
                    emotion = emotion_data if isinstance(emotion_data, str) else 'neutral'
                    intensity = entry.get('intensity', 0.5)
                
                # Format the timestamp properly
                created_at = entry.get('created_at')
                if isinstance(created_at, datetime):
                    timestamp = created_at.isoformat()
                else:
                    timestamp = str(created_at)
                    
                print(f"DEBUG: Creating data point for entry {entry.get('_id')} with emotion {emotion}")
                
                data_points.append({
                    'id': str(entry.get('_id')),
                    'emotion': emotion,
                    'intensity': intensity,
                    'timestamp': timestamp,  # Use formatted timestamp
                    'content': entry.get('content', '')
                })
            
            # Generate insights if requested
            insights = []
            if include_insights and len(data_points) > 0:
                # Find most common emotion
                emotion_counts = {}
                for point in data_points:
                    emotion = point['emotion']
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
                most_common = max(emotion_counts.items(), key=lambda x: x[1]) if emotion_counts else ('neutral', 0)
                
                insights.append({
                    'type': 'most_common_emotion',
                    'content': f"Your most common emotion was {most_common[0]}",
                    'data': {'emotion': most_common[0], 'count': most_common[1]}
                })
                
                # Add trend insight if we have enough data points
                if len(data_points) >= 3:
                    first_emotion = data_points[0]['emotion']
                    last_emotion = data_points[-1]['emotion']
                    
                    positive_emotions = ['joy', 'happy', 'content', 'excited', 'calm']
                    negative_emotions = ['sad', 'angry', 'fear', 'disgust', 'bored']
                    
                    trend = 'neutral'
                    if first_emotion in negative_emotions and last_emotion in positive_emotions:
                        trend = 'improving'
                    elif first_emotion in positive_emotions and last_emotion in negative_emotions:
                        trend = 'declining'
                    elif first_emotion == last_emotion:
                        trend = 'stable'
                    
                    insights.append({
                        'type': 'emotional_trend',
                        'content': f"Your emotional state appears to be {trend}",
                        'data': {'trend': trend, 'first': first_emotion, 'last': last_emotion}
                    })
            
            return {
                'data': data_points,
                'time_period': time_period,
                'insights': insights if include_insights else None
            }
        except Exception as e:
            print(f"Error in AgentService.analyze_emotional_journey: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'data': [],
                'time_period': time_period,
                'error': str(e)
            }
            
        except Exception as e:
            print(f"Error in AgentService.create_action_plan: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'message': f'Error creating action plan: {str(e)}',
                'status': 'error'
            }
            
    def execute_action(self, user_email, action_id, feedback=None):
        """
        Execute an action from a plan and update its status
        
        Args:
            user_email: User's email
            action_id: ID of the action to execute
            feedback: Optional feedback on the action
            
        Returns:
            Dictionary with execution result
        """
        try:
            if feedback is None:
                feedback = {}
                
            # Find the action plan containing this action
            plan = self.db.action_plans.find_one({
                'user_email': user_email,
                'status': 'active',
                'actions.id': action_id
            })
            
            if not plan:
                return {
                    'message': 'Action not found or plan not active',
                    'status': 'error'
                }
                
            # Update action status
            for i, action in enumerate(plan['actions']):
                if action['id'] == action_id:
                    plan['actions'][i]['status'] = 'completed'
                    plan['actions'][i]['feedback'] = feedback
                    plan['actions'][i]['completed_at'] = datetime.now()
                    break
            
            # Calculate progress
            completed_actions = sum(1 for action in plan['actions'] if action['status'] == 'completed')
            total_actions = len(plan['actions'])
            progress = (completed_actions / total_actions) * 100 if total_actions > 0 else 0
            
            # Update plan
            plan['progress'] = progress
            plan['updated_at'] = datetime.now()
            
            # Check if all actions are completed
            if progress >= 100:
                plan['status'] = 'completed'
            
            # Update in database
            self.db.action_plans.update_one(
                {'_id': plan['_id']},
                {'$set': {
                    'actions': plan['actions'],
                    'progress': plan['progress'],
                    'status': plan['status'],
                    'updated_at': plan['updated_at']
                }}
            )
            
            # Get next action if available
            next_action = None
            for action in plan['actions']:
                if action['status'] == 'pending':
                    next_action = action
                    break
            
            return {
                'message': 'Action executed successfully',
                'status': 'success',
                'progress': progress,
                'plan_status': plan['status'],
                'next_action': next_action
            }
            
        except Exception as e:
            print(f"Error in AgentService.execute_action: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'message': f'Error executing action: {str(e)}',
                'status': 'error'
            }
    
    def _get_current_emotion(self, user_email):
        """
        Get user's current emotional state
        
        Args:
            user_email: User's email
            
        Returns:
            Current emotion string
        """
        try:
            # Get user's most recent journal entry
            entry = self.db.journal_entries.find_one(
                {'user_email': user_email, 'isUserMessage': True},
                {'emotion': 1},
                sort=[('created_at', -1)]
            )
            
            if entry and 'emotion' in entry and 'primary_emotion' in entry['emotion']:
                return entry['emotion']['primary_emotion']
            else:
                return 'neutral'
                
        except Exception as e:
            print(f"Error in AgentService._get_current_emotion: {str(e)}")
            return 'neutral'
