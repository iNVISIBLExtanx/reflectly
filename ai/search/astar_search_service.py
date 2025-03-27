"""
AStarSearchService - Class for finding optimal emotional paths using A* search algorithm
"""
from .astar import AStarSearch
from .emotional_heuristics import (
    create_valence_arousal_heuristic,
    create_transition_probability_heuristic,
    create_user_history_heuristic,
    create_combined_heuristic
)
from .emotion_coordinates import EMOTION_COORDINATES

class AStarSearchService:
    def __init__(self, emotional_graph):
        """
        Initialize the A* search service
        
        Args:
            emotional_graph: Instance of EmotionalGraph
        """
        self.emotional_graph = emotional_graph
        # Pass the graph structure to the AStarSearch constructor
        self.astar = AStarSearch(emotional_graph.get_graph())
        
    def find_path(self, user_email, current_emotion, target_emotion, max_depth=10):
        """
        Find an optimal path from current_emotion to target_emotion using A* search
        
        Args:
            user_email: User's email
            current_emotion: Starting emotional state
            target_emotion: Target emotional state
            max_depth: Maximum depth for the search
            
        Returns:
            Dictionary with path and actions
        """
        try:
            # Create heuristic for the user
            heuristic = self._create_heuristic_for_user(user_email)
            
            # Perform A* search
            path, cost = self.astar.search(current_emotion, target_emotion, None, heuristic)
            
            if not path:
                return {
                    'path': [],
                    'actions': [],
                    'cost': 0,
                    'message': 'No path found'
                }
                
            # Add actions for each transition in the path
            actions = []
            for i in range(len(path) - 1):
                from_state = path[i]
                to_state = path[i + 1]
                
                # Get suggested actions for this transition
                suggested_actions = self.emotional_graph.get_transition_actions(
                    user_email, 
                    from_state, 
                    to_state
                )
                
                # If no suggested actions, provide default ones
                if not suggested_actions:
                    if to_state in ['happy', 'joy', 'excited', 'content', 'calm']:
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
                
                actions.append({
                    'from': from_state,
                    'to': to_state,
                    'actions': suggested_actions
                })
                
            return {
                'path': path,
                'actions': actions,
                'cost': cost,
                'message': 'Path found successfully'
            }
            
        except Exception as e:
            print(f"Error in AStarSearchService.find_path: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'path': [],
                'actions': [],
                'cost': 0,
                'message': f'Error finding path: {str(e)}'
            }
            
    def _create_heuristic_for_user(self, user_email):
        """
        Create a heuristic function for a specific user
        
        Args:
            user_email: User's email
            
        Returns:
            A heuristic function tailored for the user
        """
        # Get user's emotional history
        try:
            emotion_history = self.emotional_graph.get_emotion_history(user_email)
        except Exception as e:
            print(f"Error getting emotion history: {str(e)}")
            emotion_history = []
            
        # Create individual heuristics
        valence_arousal_heuristic = create_valence_arousal_heuristic(EMOTION_COORDINATES)
        
        # Get transition probabilities from the emotional graph
        transition_probs = self.emotional_graph.get_transition_probabilities(user_email)
        transition_probability_heuristic = create_transition_probability_heuristic(transition_probs)
        
        # Create user history heuristic
        user_history = self.emotional_graph.get_user_history(user_email) if emotion_history else {}
        user_history_heuristic = create_user_history_heuristic(user_history)
        
        # Combine heuristics with weights
        heuristics = [valence_arousal_heuristic, transition_probability_heuristic, user_history_heuristic]
        weights = [0.4, 0.3, 0.3]
        
        return create_combined_heuristic(heuristics, weights)
