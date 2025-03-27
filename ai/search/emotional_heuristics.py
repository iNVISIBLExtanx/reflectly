"""
Heuristic functions for A* search in emotional state graphs.
"""

from typing import Dict, Any, Callable


def create_valence_arousal_heuristic(emotion_coordinates: Dict[str, tuple]) -> Callable:
    """
    Create a heuristic function based on valence-arousal coordinates of emotions.
    
    Args:
        emotion_coordinates: Dictionary mapping emotion names to (valence, arousal) coordinates
        
    Returns:
        A heuristic function that calculates Euclidean distance between emotions
    """
    def heuristic(current: str, goal: str, node_data: Dict[str, Any] = None) -> float:
        """
        Calculate the Euclidean distance between two emotions in valence-arousal space.
        
        Args:
            current: Current emotion
            goal: Goal emotion
            node_data: Additional node data (not used in this heuristic)
            
        Returns:
            Euclidean distance between the emotions
        """
        if current not in emotion_coordinates or goal not in emotion_coordinates:
            return 0  # Default to 0 if coordinates are not available
        
        current_valence, current_arousal = emotion_coordinates[current]
        goal_valence, goal_arousal = emotion_coordinates[goal]
        
        # Calculate Euclidean distance
        return ((current_valence - goal_valence) ** 2 + (current_arousal - goal_arousal) ** 2) ** 0.5
    
    return heuristic


def create_transition_probability_heuristic(transition_probs: Dict[str, Dict[str, float]]) -> Callable:
    """
    Create a heuristic function based on transition probabilities between emotions.
    
    Args:
        transition_probs: Dictionary mapping from emotions to dictionaries mapping to emotions with probabilities
        
    Returns:
        A heuristic function that uses transition probabilities
    """
    def heuristic(current: str, goal: str, node_data: Dict[str, Any] = None) -> float:
        """
        Calculate a heuristic value based on transition probabilities.
        
        Args:
            current: Current emotion
            goal: Goal emotion
            node_data: Additional node data (not used in this heuristic)
            
        Returns:
            A heuristic value (lower is better)
        """
        # Initialize with a high value
        result = 10.0
        
        # If we have direct transition probability data
        if current in transition_probs and goal in transition_probs[current]:
            # Convert probability to a cost (higher probability = lower cost)
            prob = transition_probs[current][goal]
            if prob > 0:
                result = 1.0 / prob
        
        return result
    
    return heuristic


def create_user_history_heuristic(user_history: Dict[str, Dict[str, Any]]) -> Callable:
    """
    Create a heuristic function based on user's historical emotional transitions.
    
    Args:
        user_history: Dictionary containing user's historical emotional transitions and their effectiveness
        
    Returns:
        A heuristic function that uses user history
    """
    def heuristic(current: str, goal: str, node_data: Dict[str, Any] = None) -> float:
        """
        Calculate a heuristic value based on user's historical transitions.
        
        Args:
            current: Current emotion
            goal: Goal emotion
            node_data: Additional node data (not used in this heuristic)
            
        Returns:
            A heuristic value (lower is better)
        """
        # Default to a moderate value
        result = 5.0
        
        # Check if we have historical data for this transition
        transition_key = f"{current}_to_{goal}"
        if transition_key in user_history:
            # Use historical effectiveness as a heuristic
            effectiveness = user_history[transition_key].get('effectiveness', 0.5)
            if effectiveness > 0:
                result = 1.0 / effectiveness
        
        return result
    
    return heuristic


def create_combined_heuristic(heuristics: list, weights: list) -> Callable:
    """
    Create a combined heuristic function from multiple heuristics with weights.
    
    Args:
        heuristics: List of heuristic functions
        weights: List of weights for each heuristic
        
    Returns:
        A combined heuristic function
    """
    def heuristic(current: str, goal: str, node_data: Dict[str, Any] = None) -> float:
        """
        Calculate a combined heuristic value.
        
        Args:
            current: Current emotion
            goal: Goal emotion
            node_data: Additional node data
            
        Returns:
            A combined heuristic value
        """
        result = 0.0
        
        # Combine heuristics with weights
        for h, w in zip(heuristics, weights):
            result += h(current, goal, node_data) * w
        
        return result
    
    return heuristic
