"""
State management for the intelligent agent.
"""

from typing import Dict, List, Any, Optional
import json
import time


class AgentState:
    """
    Represents the state of the intelligent agent.
    """
    
    def __init__(self, user_id: str, user_email=None, current_emotion=None, target_emotion=None, action_plan=None, current_action_index=0, feedback_history=None):
        """
        Initialize agent state.
        
        Args:
            user_id: User ID
            user_email: User email (optional)
            current_emotion: Current emotional state (optional)
            target_emotion: Target emotional state (optional)
            action_plan: List of actions to take (optional)
            current_action_index: Index of the current action in the action plan (optional)
            feedback_history: List of feedback items (optional)
        """
        self.user_id = user_id
        self.user_email = user_email
        self.current_emotion = current_emotion
        self.target_emotion = target_emotion
        self.history = []
        self.last_updated = time.time()
        self.context = {}
        self.actions = action_plan if action_plan is not None else []
        self.current_action_index = current_action_index
        self.feedback = feedback_history if feedback_history is not None else []
    
    def update_emotion(self, emotion: str):
        """
        Update the current emotional state.
        
        Args:
            emotion: New emotional state
        """
        # Add current emotion to history if it exists
        if self.current_emotion:
            self.history.append({
                'emotion': self.current_emotion,
                'timestamp': self.last_updated,
                'duration': time.time() - self.last_updated
            })
        
        # Update current emotion
        self.current_emotion = emotion
        self.last_updated = time.time()
    
    def set_target_emotion(self, emotion: str):
        """
        Set the target emotional state.
        
        Args:
            emotion: Target emotional state
        """
        self.target_emotion = emotion
    
    def add_context(self, key: str, value: Any):
        """
        Add context information.
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
    
    def remove_context(self, key: str):
        """
        Remove context information.
        
        Args:
            key: Context key
        """
        if key in self.context:
            del self.context[key]
    
    def add_action(self, action: Dict[str, Any]):
        """
        Add an action to the action list.
        
        Args:
            action: Action dictionary
        """
        action['timestamp'] = time.time()
        self.actions.append(action)
    
    def add_feedback(self, action_id: str, effectiveness: float, notes: Optional[str] = None):
        """
        Add feedback for an action.
        
        Args:
            action_id: Action ID
            effectiveness: Effectiveness score (0-1)
            notes: Optional notes
        """
        self.feedback.append({
            'action_id': action_id,
            'effectiveness': effectiveness,
            'notes': notes,
            'timestamp': time.time()
        })
    
    def get_recent_emotions(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent emotions from history.
        
        Args:
            count: Number of emotions to retrieve
            
        Returns:
            List of recent emotions
        """
        result = self.history[-count:] if len(self.history) > 0 else []
        
        # Add current emotion if it exists
        if self.current_emotion:
            result.append({
                'emotion': self.current_emotion,
                'timestamp': self.last_updated,
                'duration': time.time() - self.last_updated
            })
        
        return result
    
    def get_recent_actions(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent actions.
        
        Args:
            count: Number of actions to retrieve
            
        Returns:
            List of recent actions
        """
        return self.actions[-count:] if len(self.actions) > 0 else []
    
    def get_action_effectiveness(self, action_type: str) -> float:
        """
        Get the average effectiveness of an action type.
        
        Args:
            action_type: Action type
            
        Returns:
            Average effectiveness (0-1)
        """
        # Find all feedback for actions of this type
        relevant_feedback = []
        
        for action in self.actions:
            if action.get('type') == action_type:
                action_id = action.get('id')
                if action_id:
                    # Find feedback for this action
                    for feedback in self.feedback:
                        if feedback.get('action_id') == action_id:
                            relevant_feedback.append(feedback.get('effectiveness', 0))
        
        # Calculate average effectiveness
        if len(relevant_feedback) > 0:
            return sum(relevant_feedback) / len(relevant_feedback)
        else:
            return 0.5  # Default to neutral if no feedback
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state to dictionary.
        
        Returns:
            Dictionary representation of state
        """
        return {
            'user_id': self.user_id,
            'user_email': self.user_email,
            'current_emotion': self.current_emotion,
            'target_emotion': self.target_emotion,
            'history': self.history,
            'last_updated': self.last_updated,
            'context': self.context,
            'actions': self.actions,
            'current_action_index': self.current_action_index,
            'feedback': self.feedback
        }
    
    def to_json(self) -> str:
        """
        Convert state to JSON.
        
        Returns:
            JSON representation of state
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """
        Create state from dictionary.
        
        Args:
            data: Dictionary representation of state
            
        Returns:
            AgentState object
        """
        # Generate a random user_id if not provided
        user_id = data.get('user_id', str(time.time()))
        
        # Create the state with all parameters
        state = cls(
            user_id=user_id,
            user_email=data.get('user_email'),
            current_emotion=data.get('current_emotion'),
            target_emotion=data.get('target_emotion'),
            action_plan=data.get('actions', []),
            current_action_index=data.get('current_action_index', 0),
            feedback_history=data.get('feedback', [])
        )
        
        # Set additional properties
        state.history = data.get('history', [])
        state.last_updated = data.get('last_updated', time.time())
        state.context = data.get('context', {})
        
        return state
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentState':
        """
        Create state from JSON.
        
        Args:
            json_str: JSON representation of state
            
        Returns:
            AgentState object
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
