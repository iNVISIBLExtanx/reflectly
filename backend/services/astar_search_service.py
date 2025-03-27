"""
AStarSearchService - Service for finding optimal emotional paths using A* search algorithm
"""
from models.search_algorithm import AStarSearch

class AStarSearchService:
    def __init__(self, emotional_graph):
        """
        Initialize the A* search service
        
        Args:
            emotional_graph: Instance of EmotionalGraph
        """
        self.emotional_graph = emotional_graph
        self.astar = AStarSearch()
        
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
            # Get path using A* search
            path_result = self.astar.find_path(
                user_email, 
                current_emotion, 
                target_emotion, 
                max_depth
            )
            
            if not path_result or 'path' not in path_result:
                return {
                    'path': [],
                    'actions': [],
                    'cost': 0,
                    'message': 'No path found'
                }
                
            # Get suggested actions for each step in the path
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
                
                actions.append({
                    'from': from_emotion,
                    'to': to_emotion,
                    'actions': suggested_actions
                })
                
            return {
                'path': path_result['path'],
                'actions': actions,
                'cost': path_result.get('cost', 0),
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
