"""
Action planning for the intelligent agent.
"""

import uuid
from typing import Dict, List, Any, Optional, Tuple
import requests
import json
import logging

from .state import AgentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ActionPlanner:
    """
    Plans actions for the intelligent agent.
    """
    
    def __init__(self, astar_service_url: str, probabilistic_service_url: str):
        """
        Initialize action planner.
        
        Args:
            astar_service_url: URL of the A* search service
            probabilistic_service_url: URL of the probabilistic reasoning service
        """
        self.astar_service_url = astar_service_url
        self.probabilistic_service_url = probabilistic_service_url
    
    def plan_actions(self, state: AgentState) -> List[Dict[str, Any]]:
        """
        Plan actions based on the current state.
        
        Args:
            state: Current agent state
            
        Returns:
            List of planned actions
        """
        # Check if we have current and target emotions
        if not state.current_emotion or not state.target_emotion:
            return []
        
        # Try to find a path using A* search
        path_actions = self._plan_with_astar(state)
        
        # If A* search failed or returned no actions, try probabilistic reasoning
        if not path_actions:
            path_actions = self._plan_with_probabilistic(state)
        
        # Add unique IDs to actions
        for action in path_actions:
            action['id'] = str(uuid.uuid4())
        
        return path_actions
    
    def _plan_with_astar(self, state: AgentState) -> List[Dict[str, Any]]:
        """
        Plan actions using A* search.
        
        Args:
            state: Current agent state
            
        Returns:
            List of planned actions
        """
        try:
            # Prepare request data
            request_data = {
                'from_emotion': state.current_emotion,
                'to_emotion': state.target_emotion,
                'user_email': state.user_id,
                'request_id': str(uuid.uuid4())
            }
            
            # Send request to A* search service
            response = requests.post(
                f"{self.astar_service_url}/search",
                json=request_data,
                timeout=5
            )
            
            # Check if request was successful
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract actions from the response
                actions = []
                for transition in response_data.get('actions', []):
                    for action in transition.get('actions', []):
                        actions.append({
                            'type': action.get('action'),
                            'from_emotion': transition.get('from'),
                            'to_emotion': transition.get('to'),
                            'effectiveness': action.get('effectiveness', 0.5),
                            'certainty': action.get('certainty', 0.5)
                        })
                
                return actions
            else:
                logger.error(f"A* search request failed with status code {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error in A* search planning: {str(e)}")
            return []
    
    def _plan_with_probabilistic(self, state: AgentState) -> List[Dict[str, Any]]:
        """
        Plan actions using probabilistic reasoning.
        
        Args:
            state: Current agent state
            
        Returns:
            List of planned actions
        """
        try:
            # Prepare request data
            request_data = {
                'type': 'action_recommendation',
                'current_emotion': state.current_emotion,
                'target_emotion': state.target_emotion,
                'evidence': state.context,
                'request_id': str(uuid.uuid4())
            }
            
            # Send request to probabilistic reasoning service
            response = requests.post(
                f"{self.probabilistic_service_url}/predict",
                json=request_data,
                timeout=5
            )
            
            # Check if request was successful
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract actions from the response
                actions = []
                for recommendation in response_data.get('recommendations', []):
                    actions.append({
                        'type': recommendation.get('action'),
                        'from_emotion': state.current_emotion,
                        'to_emotion': state.target_emotion,
                        'effectiveness': recommendation.get('probability', 0.5),
                        'certainty': 0.5  # Default certainty
                    })
                
                return actions
            else:
                logger.error(f"Probabilistic reasoning request failed with status code {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error in probabilistic reasoning planning: {str(e)}")
            return []
    
    def evaluate_action(self, state: AgentState, action: Dict[str, Any]) -> float:
        """
        Evaluate the expected effectiveness of an action.
        
        Args:
            state: Current agent state
            action: Action to evaluate
            
        Returns:
            Expected effectiveness (0-1)
        """
        # Start with the action's own effectiveness
        effectiveness = action.get('effectiveness', 0.5)
        
        # Adjust based on historical effectiveness for this action type
        historical_effectiveness = state.get_action_effectiveness(action.get('type', ''))
        
        # Combine current and historical effectiveness
        combined_effectiveness = 0.7 * effectiveness + 0.3 * historical_effectiveness
        
        return combined_effectiveness
    
    def rank_actions(self, state: AgentState, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank actions by expected effectiveness.
        
        Args:
            state: Current agent state
            actions: List of actions to rank
            
        Returns:
            Ranked list of actions
        """
        # Evaluate each action
        evaluated_actions = []
        for action in actions:
            effectiveness = self.evaluate_action(state, action)
            evaluated_actions.append((action, effectiveness))
        
        # Sort by effectiveness (descending)
        evaluated_actions.sort(key=lambda x: x[1], reverse=True)
        
        # Return ranked actions
        return [action for action, _ in evaluated_actions]
    
    def get_next_action(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """
        Get the next action to take.
        
        Args:
            state: Current agent state
            
        Returns:
            Next action or None if no action is available
        """
        # Plan actions
        actions = self.plan_actions(state)
        
        # Rank actions
        ranked_actions = self.rank_actions(state, actions)
        
        # Return the highest-ranked action
        return ranked_actions[0] if ranked_actions else None
    
    def process_feedback(self, state: AgentState, action_id: str, effectiveness: float, notes: Optional[str] = None):
        """
        Process feedback for an action.
        
        Args:
            state: Current agent state
            action_id: Action ID
            effectiveness: Effectiveness score (0-1)
            notes: Optional notes
        """
        # Add feedback to state
        state.add_feedback(action_id, effectiveness, notes)
        
        # Update action in state
        for action in state.actions:
            if action.get('id') == action_id:
                # Update action's effectiveness based on feedback
                action['actual_effectiveness'] = effectiveness
                break
