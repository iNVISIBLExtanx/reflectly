"""
Bayesian network implementation for probabilistic reasoning about emotional states.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Set


class Node:
    """
    A node in a Bayesian network representing a random variable.
    """
    
    def __init__(self, name: str, states: List[str]):
        """
        Initialize a node.
        
        Args:
            name: Name of the node
            states: Possible states of the node
        """
        self.name = name
        self.states = states
        self.parents = []
        self.children = []
        self.cpt = None  # Conditional probability table
    
    def add_parent(self, parent: 'Node'):
        """
        Add a parent node.
        
        Args:
            parent: Parent node
        """
        if parent not in self.parents:
            self.parents.append(parent)
            parent.children.append(self)
    
    def set_cpt(self, cpt: Dict[Tuple, List[float]]):
        """
        Set the conditional probability table.
        
        Args:
            cpt: Dictionary mapping parent state combinations to probability distributions
        """
        self.cpt = cpt


class BayesianNetwork:
    """
    A Bayesian network for probabilistic reasoning.
    """
    
    def __init__(self):
        """Initialize an empty Bayesian network."""
        self.nodes = {}  # Maps node names to Node objects
    
    def add_node(self, name: str, states: List[str]) -> Node:
        """
        Add a node to the network.
        
        Args:
            name: Name of the node
            states: Possible states of the node
            
        Returns:
            The created node
        """
        if name in self.nodes:
            raise ValueError(f"Node '{name}' already exists")
        
        node = Node(name, states)
        self.nodes[name] = node
        return node
    
    def add_edge(self, parent_name: str, child_name: str):
        """
        Add a directed edge from parent to child.
        
        Args:
            parent_name: Name of the parent node
            child_name: Name of the child node
        """
        if parent_name not in self.nodes:
            raise ValueError(f"Parent node '{parent_name}' does not exist")
        if child_name not in self.nodes:
            raise ValueError(f"Child node '{child_name}' does not exist")
        
        parent = self.nodes[parent_name]
        child = self.nodes[child_name]
        child.add_parent(parent)
    
    def set_cpt(self, node_name: str, cpt: Dict[Tuple, List[float]]):
        """
        Set the conditional probability table for a node.
        
        Args:
            node_name: Name of the node
            cpt: Dictionary mapping parent state combinations to probability distributions
        """
        if node_name not in self.nodes:
            raise ValueError(f"Node '{node_name}' does not exist")
        
        self.nodes[node_name].set_cpt(cpt)
    
    def get_ancestors(self, node_name: str) -> Set[str]:
        """
        Get all ancestors of a node.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Set of ancestor node names
        """
        if node_name not in self.nodes:
            raise ValueError(f"Node '{node_name}' does not exist")
        
        ancestors = set()
        queue = [self.nodes[node_name]]
        
        while queue:
            node = queue.pop(0)
            for parent in node.parents:
                if parent.name not in ancestors:
                    ancestors.add(parent.name)
                    queue.append(parent)
        
        return ancestors
    
    def is_valid_evidence(self, evidence: Dict[str, str]) -> bool:
        """
        Check if evidence is valid.
        
        Args:
            evidence: Dictionary mapping node names to observed states
            
        Returns:
            True if evidence is valid, False otherwise
        """
        for node_name, state in evidence.items():
            if node_name not in self.nodes:
                return False
            if state not in self.nodes[node_name].states:
                return False
        
        return True
    
    def _sample_node(self, node: Node, parent_states: Dict[str, str]) -> str:
        """
        Sample a state for a node given its parents' states.
        
        Args:
            node: Node to sample
            parent_states: Dictionary mapping parent node names to their states
            
        Returns:
            Sampled state
        """
        # If node has no parents, use its prior distribution
        if not node.parents:
            probs = node.cpt[()]
            return np.random.choice(node.states, p=probs)
        
        # Otherwise, use conditional distribution given parent states
        parent_state_tuple = tuple(parent_states[parent.name] for parent in node.parents)
        probs = node.cpt[parent_state_tuple]
        return np.random.choice(node.states, p=probs)
    
    def _topological_sort(self) -> List[str]:
        """
        Perform a topological sort of the nodes.
        
        Returns:
            List of node names in topological order
        """
        # Count incoming edges for each node
        in_degree = {node_name: len(node.parents) for node_name, node in self.nodes.items()}
        
        # Start with nodes that have no incoming edges
        queue = [node_name for node_name, count in in_degree.items() if count == 0]
        result = []
        
        while queue:
            node_name = queue.pop(0)
            result.append(node_name)
            
            # Decrease in-degree of neighbors
            for child in self.nodes[node_name].children:
                in_degree[child.name] -= 1
                if in_degree[child.name] == 0:
                    queue.append(child.name)
        
        # Check if we visited all nodes
        if len(result) != len(self.nodes):
            raise ValueError("Graph has cycles")
        
        return result
    
    def likelihood_weighting(self, query_node: str, evidence: Dict[str, str], num_samples: int = 1000) -> Dict[str, float]:
        """
        Perform likelihood weighting to estimate the posterior distribution of a query node.
        
        Args:
            query_node: Name of the query node
            evidence: Dictionary mapping node names to observed states
            num_samples: Number of samples to generate
            
        Returns:
            Dictionary mapping states to their probabilities
        """
        if query_node not in self.nodes:
            raise ValueError(f"Query node '{query_node}' does not exist")
        
        if not self.is_valid_evidence(evidence):
            raise ValueError("Invalid evidence")
        
        # Get topological ordering of nodes
        ordering = self._topological_sort()
        
        # Initialize counts for each state of the query node
        counts = {state: 0.0 for state in self.nodes[query_node].states}
        
        # Generate weighted samples
        for _ in range(num_samples):
            sample = {}
            weight = 1.0
            
            # Generate a sample for each node in topological order
            for node_name in ordering:
                node = self.nodes[node_name]
                
                # If node is in evidence, use the observed value
                if node_name in evidence:
                    sample[node_name] = evidence[node_name]
                    
                    # Update weight based on likelihood of evidence
                    if node.parents:
                        parent_state_tuple = tuple(sample[parent.name] for parent in node.parents)
                        state_idx = node.states.index(evidence[node_name])
                        weight *= node.cpt[parent_state_tuple][state_idx]
                else:
                    # Otherwise, sample from conditional distribution
                    parent_states = {parent.name: sample[parent.name] for parent in node.parents}
                    sample[node_name] = self._sample_node(node, parent_states)
            
            # Update counts for the query node
            counts[sample[query_node]] += weight
        
        # Normalize counts to get probabilities
        total = sum(counts.values())
        if total > 0:
            return {state: count / total for state, count in counts.items()}
        else:
            # If all weights are zero, return uniform distribution
            return {state: 1.0 / len(counts) for state in counts}
    
    def predict_emotion(self, current_emotion: str, actions: List[str], evidence: Dict[str, str] = None) -> Dict[str, float]:
        """
        Predict the next emotional state given the current emotion and actions.
        
        Args:
            current_emotion: Current emotional state
            actions: List of actions taken
            evidence: Additional evidence
            
        Returns:
            Dictionary mapping emotional states to their probabilities
        """
        # Combine current emotion and actions into evidence
        combined_evidence = {'current_emotion': current_emotion}
        
        for i, action in enumerate(actions):
            combined_evidence[f'action_{i}'] = action
        
        # Add additional evidence if provided
        if evidence:
            combined_evidence.update(evidence)
        
        # Perform inference to predict next emotion
        return self.likelihood_weighting('next_emotion', combined_evidence)
    
    def recommend_actions(self, current_emotion: str, target_emotion: str, available_actions: List[str],
                         evidence: Dict[str, str] = None, num_recommendations: int = 3) -> List[Dict[str, Any]]:
        """
        Recommend actions to transition from current emotion to target emotion.
        
        Args:
            current_emotion: Current emotional state
            target_emotion: Target emotional state
            available_actions: List of available actions
            evidence: Additional evidence
            num_recommendations: Number of actions to recommend
            
        Returns:
            List of dictionaries with action recommendations and their probabilities
        """
        recommendations = []
        
        for action in available_actions:
            # Predict next emotion given current emotion and this action
            combined_evidence = {'current_emotion': current_emotion, 'action_0': action}
            
            # Add additional evidence if provided
            if evidence:
                combined_evidence.update(evidence)
            
            # Perform inference to predict next emotion
            prediction = self.likelihood_weighting('next_emotion', combined_evidence)
            
            # Calculate probability of reaching target emotion
            target_prob = prediction.get(target_emotion, 0.0)
            
            # Add to recommendations
            recommendations.append({
                'action': action,
                'probability': target_prob,
                'predictions': prediction
            })
        
        # Sort recommendations by probability (descending)
        recommendations.sort(key=lambda x: x['probability'], reverse=True)
        
        # Return top recommendations
        return recommendations[:num_recommendations]
    
    @classmethod
    def create_emotional_network(cls, emotions: List[str], actions: List[str]) -> 'BayesianNetwork':
        """
        Create a Bayesian network for emotional transitions.
        
        Args:
            emotions: List of possible emotional states
            actions: List of possible actions
            
        Returns:
            A Bayesian network for emotional transitions
        """
        network = cls()
        
        # Add nodes
        network.add_node('current_emotion', emotions)
        network.add_node('action', actions)
        network.add_node('next_emotion', emotions)
        
        # Add edges
        network.add_edge('current_emotion', 'next_emotion')
        network.add_edge('action', 'next_emotion')
        
        # Set CPTs based on data-driven approach
        
        # Prior for current_emotion - based on distribution in the dataset
        # We'll use a slightly higher probability for neutral and joy states as starting points
        current_emotion_probs = [0.0] * len(emotions)
        for i, emotion in enumerate(emotions):
            if emotion == 'neutral':
                current_emotion_probs[i] = 0.3
            elif emotion == 'joy':
                current_emotion_probs[i] = 0.2
            elif emotion in ['sadness', 'fear']:
                current_emotion_probs[i] = 0.15
            else:
                current_emotion_probs[i] = 0.1 / (len(emotions) - 4)  # Distribute remaining probability
        
        # Normalize to ensure probabilities sum to 1
        total = sum(current_emotion_probs)
        current_emotion_probs = [p / total for p in current_emotion_probs]
        
        network.set_cpt('current_emotion', {
            (): current_emotion_probs
        })
        
        # Prior for action - some actions are more common than others
        action_probs = [0.0] * len(actions)
        for i, action in enumerate(actions):
            if action in ['journal', 'meditate', 'talk']:
                action_probs[i] = 0.2
            elif action in ['exercise', 'rest']:
                action_probs[i] = 0.15
            else:
                action_probs[i] = 0.1 / (len(actions) - 5)  # Distribute remaining probability
        
        # Normalize to ensure probabilities sum to 1
        total = sum(action_probs)
        action_probs = [p / total for p in action_probs]
        
        network.set_cpt('action', {
            (): action_probs
        })
        
        # CPT for next_emotion - transitions depend on current emotion and action
        cpt = {}
        for i, emotion in enumerate(emotions):
            for j, action in enumerate(actions):
                # Initialize with some bias towards maintaining the current emotion
                next_probs = [0.1] * len(emotions)
                
                # Find the index of the current emotion
                current_idx = emotions.index(emotion)
                
                # Higher probability to stay in the same emotion
                next_probs[current_idx] = 0.3
                
                # Model the effects of different actions
                if action == 'meditate':
                    # Meditation tends to move towards neutral or calm states
                    neutral_idx = emotions.index('neutral') if 'neutral' in emotions else -1
                    if neutral_idx >= 0:
                        next_probs[neutral_idx] = 0.25
                
                elif action == 'exercise':
                    # Exercise tends to improve mood towards joy
                    joy_idx = emotions.index('joy') if 'joy' in emotions else -1
                    if joy_idx >= 0:
                        next_probs[joy_idx] = 0.25
                
                elif action == 'talk':
                    # Talking helps with negative emotions
                    if emotion in ['sadness', 'anger', 'fear']:
                        neutral_idx = emotions.index('neutral') if 'neutral' in emotions else -1
                        if neutral_idx >= 0:
                            next_probs[neutral_idx] = 0.25
                
                # Normalize to ensure probabilities sum to 1
                total = sum(next_probs)
                next_probs = [p / total for p in next_probs]
                
                cpt[(emotion, action)] = next_probs
        
        network.set_cpt('next_emotion', cpt)
        
        return network
