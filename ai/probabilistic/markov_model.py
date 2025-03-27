"""
Markov model implementation for probabilistic reasoning about emotional states over time.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional


class MarkovModel:
    """
    A Markov model for probabilistic reasoning about sequences of emotional states.
    """
    
    def __init__(self, states: List[str], transition_matrix: Optional[np.ndarray] = None):
        """
        Initialize a Markov model.
        
        Args:
            states: List of possible states
            transition_matrix: Optional transition matrix (will be initialized to uniform if not provided)
        """
        self.states = states
        self.state_to_idx = {state: i for i, state in enumerate(states)}
        
        # Initialize transition matrix
        if transition_matrix is not None:
            if transition_matrix.shape != (len(states), len(states)):
                raise ValueError(f"Transition matrix shape {transition_matrix.shape} does not match number of states {len(states)}")
            self.transition_matrix = transition_matrix
        else:
            # Initialize with uniform transitions
            self.transition_matrix = np.ones((len(states), len(states))) / len(states)
    
    def set_transition_probability(self, from_state: str, to_state: str, probability: float):
        """
        Set the transition probability from one state to another.
        
        Args:
            from_state: Starting state
            to_state: Ending state
            probability: Transition probability
        """
        if from_state not in self.state_to_idx:
            raise ValueError(f"State '{from_state}' not in model")
        if to_state not in self.state_to_idx:
            raise ValueError(f"State '{to_state}' not in model")
        if probability < 0 or probability > 1:
            raise ValueError(f"Probability must be between 0 and 1, got {probability}")
        
        from_idx = self.state_to_idx[from_state]
        to_idx = self.state_to_idx[to_state]
        
        self.transition_matrix[from_idx, to_idx] = probability
        
        # Normalize row to ensure it sums to 1
        row_sum = np.sum(self.transition_matrix[from_idx, :])
        if row_sum > 0:
            self.transition_matrix[from_idx, :] /= row_sum
    
    def get_transition_probability(self, from_state: str, to_state: str) -> float:
        """
        Get the transition probability from one state to another.
        
        Args:
            from_state: Starting state
            to_state: Ending state
            
        Returns:
            Transition probability
        """
        if from_state not in self.state_to_idx:
            raise ValueError(f"State '{from_state}' not in model")
        if to_state not in self.state_to_idx:
            raise ValueError(f"State '{to_state}' not in model")
        
        from_idx = self.state_to_idx[from_state]
        to_idx = self.state_to_idx[to_state]
        
        return self.transition_matrix[from_idx, to_idx]
    
    def predict_next_state(self, current_state: str, emotion_history: List[str] = None) -> Dict[str, Any]:
        """
        Predict the next state given the current state.
        
        Args:
            current_state: Current state
            emotion_history: Optional list of previous emotional states
            
        Returns:
            Dictionary with predicted state and probability
        """
        if current_state not in self.state_to_idx:
            raise ValueError(f"State '{current_state}' not in model")
        
        # Update model with emotion history if provided
        if emotion_history and len(emotion_history) > 1:
            self.update_from_sequence(emotion_history)
        
        current_idx = self.state_to_idx[current_state]
        probabilities = self.transition_matrix[current_idx, :]
        
        # Get the most likely next state
        next_state_idx = np.argmax(probabilities)
        next_state = self.states[next_state_idx]
        probability = probabilities[next_state_idx]
        
        return {
            'state': next_state,
            'probability': float(probability),
            'all_probabilities': {state: float(probabilities[self.state_to_idx[state]]) for state in self.states}
        }
    
    def predict_state_after_n_steps(self, current_state: str, n: int) -> Dict[str, float]:
        """
        Predict the state after n steps given the current state.
        
        Args:
            current_state: Current state
            n: Number of steps
            
        Returns:
            Dictionary mapping states to their probabilities
        """
        if current_state not in self.state_to_idx:
            raise ValueError(f"State '{current_state}' not in model")
        if n < 0:
            raise ValueError(f"Number of steps must be non-negative, got {n}")
        
        current_idx = self.state_to_idx[current_state]
        
        # Initialize state distribution
        state_distribution = np.zeros(len(self.states))
        state_distribution[current_idx] = 1.0
        
        # Compute state distribution after n steps
        for _ in range(n):
            state_distribution = np.dot(state_distribution, self.transition_matrix)
        
        return {state: state_distribution[self.state_to_idx[state]] for state in self.states}
    
    def most_likely_path(self, start_state: str, end_state: str, max_length: int = 10) -> Tuple[List[str], float]:
        """
        Find the most likely path from start state to end state.
        
        Args:
            start_state: Starting state
            end_state: Ending state
            max_length: Maximum path length
            
        Returns:
            Tuple containing:
                - List of states representing the most likely path
                - Probability of the path
        """
        if start_state not in self.state_to_idx:
            raise ValueError(f"State '{start_state}' not in model")
        if end_state not in self.state_to_idx:
            raise ValueError(f"State '{end_state}' not in model")
        
        start_idx = self.state_to_idx[start_state]
        end_idx = self.state_to_idx[end_state]
        
        # Initialize dynamic programming table
        # dp[t][i] = (probability, predecessor)
        dp = [{} for _ in range(max_length + 1)]
        
        # Base case
        dp[0][start_idx] = (1.0, None)
        
        # Fill the table
        for t in range(1, max_length + 1):
            for j in range(len(self.states)):
                max_prob = 0.0
                max_pred = None
                
                for i in range(len(self.states)):
                    if i in dp[t-1]:
                        prob = dp[t-1][i][0] * self.transition_matrix[i, j]
                        if prob > max_prob:
                            max_prob = prob
                            max_pred = i
                
                if max_prob > 0:
                    dp[t][j] = (max_prob, max_pred)
            
            # If we've reached the end state, we're done
            if end_idx in dp[t]:
                # Reconstruct the path
                path = [end_state]
                prob = dp[t][end_idx][0]
                curr_idx = end_idx
                
                for s in range(t, 0, -1):
                    curr_idx = dp[s][curr_idx][1]
                    path.append(self.states[curr_idx])
                
                path.reverse()
                return path, prob
        
        # If we get here, there's no path from start to end within max_length
        return [], 0.0
    
    def predict_sequence(self, current_state: str, sequence_length: int) -> Tuple[List[str], List[float]]:
        """
        Predict a sequence of emotional states starting from the current state.
        
        Args:
            current_state: Current emotional state
            sequence_length: Length of the sequence to predict
            
        Returns:
            Tuple containing:
                - List of predicted states
                - List of probabilities for each transition
        """
        if current_state not in self.state_to_idx:
            raise ValueError(f"State '{current_state}' not in model")
        if sequence_length <= 0:
            raise ValueError(f"Sequence length must be positive, got {sequence_length}")
        
        # Initialize sequence with current state
        sequence = [current_state]
        probabilities = []
        
        # Current state
        state = current_state
        
        # Generate sequence
        for _ in range(sequence_length - 1):
            # Get transition probabilities from current state
            current_idx = self.state_to_idx[state]
            state_probs = self.transition_matrix[current_idx, :]
            
            # Get the most likely next state
            next_state_idx = np.argmax(state_probs)
            next_state = self.states[next_state_idx]
            probability = state_probs[next_state_idx]
            
            # Add to sequence
            sequence.append(next_state)
            probabilities.append(float(probability))
            
            # Update current state
            state = next_state
        
        return sequence, probabilities
    
    def sample_path(self, start_state: str, max_length: int = 10, end_state: Optional[str] = None) -> List[str]:
        """
        Sample a path from the Markov model.
        
        Args:
            start_state: Starting state
            max_length: Maximum path length
            end_state: Optional ending state
            
        Returns:
            List of states representing the sampled path
        """
        if start_state not in self.state_to_idx:
            raise ValueError(f"State '{start_state}' not in model")
        if end_state is not None and end_state not in self.state_to_idx:
            raise ValueError(f"State '{end_state}' not in model")
        
        path = [start_state]
        current_state = start_state
        
        for _ in range(max_length - 1):
            # Get transition probabilities from current state
            current_idx = self.state_to_idx[current_state]
            probabilities = self.transition_matrix[current_idx, :]
            
            # Sample next state
            next_idx = np.random.choice(len(self.states), p=probabilities)
            next_state = self.states[next_idx]
            
            path.append(next_state)
            current_state = next_state
            
            # Stop if we've reached the end state
            if end_state is not None and current_state == end_state:
                break
        
        return path
    
    def update_from_sequence(self, sequence: List[str], learning_rate: float = 0.1):
        """
        Update the transition matrix based on an observed sequence.
        
        Args:
            sequence: List of states
            learning_rate: Learning rate for updating the transition matrix
        """
        if len(sequence) < 2:
            return
        
        # Count transitions in the sequence
        counts = np.zeros((len(self.states), len(self.states)))
        
        for i in range(len(sequence) - 1):
            from_state = sequence[i]
            to_state = sequence[i + 1]
            
            if from_state in self.state_to_idx and to_state in self.state_to_idx:
                from_idx = self.state_to_idx[from_state]
                to_idx = self.state_to_idx[to_state]
                counts[from_idx, to_idx] += 1
        
        # Normalize counts to get probabilities
        row_sums = np.sum(counts, axis=1)
        normalized_counts = np.zeros_like(counts)
        
        for i in range(len(self.states)):
            if row_sums[i] > 0:
                normalized_counts[i, :] = counts[i, :] / row_sums[i]
        
        # Update transition matrix with learning rate
        self.transition_matrix = (1 - learning_rate) * self.transition_matrix + learning_rate * normalized_counts
    
    def stationary_distribution(self, max_iterations: int = 100, tolerance: float = 1e-6) -> Dict[str, float]:
        """
        Compute the stationary distribution of the Markov model.
        
        Args:
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            
        Returns:
            Dictionary mapping states to their stationary probabilities
        """
        # Initialize with uniform distribution
        distribution = np.ones(len(self.states)) / len(self.states)
        
        for _ in range(max_iterations):
            new_distribution = np.dot(distribution, self.transition_matrix)
            
            # Check for convergence
            if np.max(np.abs(new_distribution - distribution)) < tolerance:
                break
            
            distribution = new_distribution
        
        return {state: distribution[self.state_to_idx[state]] for state in self.states}
    
    @classmethod
    def create_from_data(cls, states: List[str], sequences: List[List[str]]) -> 'MarkovModel':
        """
        Create a Markov model from sequences of states.
        
        Args:
            states: List of possible states
            sequences: List of sequences of states
            
        Returns:
            A Markov model trained on the sequences
        """
        model = cls(states)
        
        for sequence in sequences:
            model.update_from_sequence(sequence, learning_rate=1.0)
        
        return model
    
    @classmethod
    def create_emotional_model(cls, emotions: List[str]) -> 'MarkovModel':
        """
        Create a Markov model for emotional transitions.
        
        Args:
            emotions: List of possible emotional states
            
        Returns:
            A Markov model for emotional transitions
        """
        # Create a model with uniform transitions
        model = cls(emotions)
        
        # In a real implementation, we would learn the transition probabilities from data
        # For now, just return the model with uniform transitions
        return model
        
    def get_transition_probabilities(self, emotion_history: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Get the transition probabilities as a dictionary of dictionaries.
        
        Args:
            emotion_history: List of emotions to use for updating the model
            
        Returns:
            Dictionary mapping from_state to a dictionary mapping to_state to probability
        """
        # Create a copy of the model to avoid modifying the original
        # If emotion_history is provided, update the model with it
        if emotion_history and len(emotion_history) > 1:
            self.update_from_sequence(emotion_history)
        
        # Convert transition matrix to dictionary format
        transitions = {}
        for from_state in self.states:
            from_idx = self.state_to_idx[from_state]
            transitions[from_state] = {}
            
            for to_state in self.states:
                to_idx = self.state_to_idx[to_state]
                prob = self.transition_matrix[from_idx, to_idx]
                
                # Only include non-zero probabilities
                if prob > 0:
                    transitions[from_state][to_state] = prob
        
        return transitions
