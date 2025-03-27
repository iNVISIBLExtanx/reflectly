"""
Implementation of the A* search algorithm for finding optimal paths through emotional states.
"""

import heapq
import math
from typing import Dict, List, Tuple, Callable, Set, Any, Optional

class AStarSearch:
    """
    A* search algorithm implementation for finding optimal paths through emotional states.
    """
    
    def __init__(self, graph: Dict[str, Dict[str, float]]):
        """
        Initialize the A* search algorithm with a graph.
        
        Args:
            graph: A dictionary representing the graph where keys are node IDs and values are
                  dictionaries mapping neighbor node IDs to edge costs.
        """
        self.graph = graph
    
    def heuristic(self, node: str, goal: str, node_data: Dict[str, Any] = None) -> float:
        """
        Heuristic function for A* search. Estimates the cost from node to goal.
        
        Args:
            node: Current node ID
            goal: Goal node ID
            node_data: Optional dictionary containing additional data about nodes
            
        Returns:
            Estimated cost from node to goal
        """
        # Default implementation uses a simple heuristic
        # In a real implementation, this would use emotional state data
        if node_data and 'coordinates' in node_data.get(node, {}) and 'coordinates' in node_data.get(goal, {}):
            # If we have coordinates, use Euclidean distance
            x1, y1 = node_data[node]['coordinates']
            x2, y2 = node_data[goal]['coordinates']
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        # Default to 0 (Dijkstra's algorithm) if no better heuristic is available
        return 0
    
    def search(self, start: str, goal: str, node_data: Dict[str, Any] = None,
               custom_heuristic: Callable[[str, str, Dict[str, Any]], float] = None) -> Tuple[List[str], float]:
        """
        Perform A* search from start to goal.
        
        Args:
            start: Start node ID
            goal: Goal node ID
            node_data: Optional dictionary containing additional data about nodes
            custom_heuristic: Optional custom heuristic function
            
        Returns:
            Tuple containing:
                - List of node IDs representing the path from start to goal
                - Total cost of the path
        """
        if start not in self.graph:
            raise ValueError(f"Start node '{start}' not in graph")
        if goal not in self.graph:
            raise ValueError(f"Goal node '{goal}' not in graph")
        
        # Use custom heuristic if provided, otherwise use default
        h = custom_heuristic if custom_heuristic else self.heuristic
        
        # Priority queue for open set
        open_set = [(0, start)]  # (f_score, node)
        
        # For node n, came_from[n] is the node immediately preceding it on the cheapest path from start to n
        came_from = {}
        
        # For node n, g_score[n] is the cost of the cheapest path from start to n currently known
        g_score = {start: 0}
        
        # For node n, f_score[n] = g_score[n] + h(n, goal)
        f_score = {start: h(start, goal, node_data)}
        
        # Set of nodes already evaluated
        closed_set = set()
        
        while open_set:
            # Get node with lowest f_score
            current_f, current = heapq.heappop(open_set)
            
            # If we reached the goal, reconstruct and return the path
            if current == goal:
                path = self._reconstruct_path(came_from, current)
                return path, g_score[current]
            
            # Mark current node as evaluated
            closed_set.add(current)
            
            # Check all neighbors
            for neighbor, cost in self.graph[current].items():
                # Skip if neighbor has been evaluated
                if neighbor in closed_set:
                    continue
                
                # Tentative g_score is the g_score of current plus the cost to move to neighbor
                tentative_g_score = g_score[current] + cost
                
                # If neighbor is not in open set or tentative g_score is better than current g_score
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # This path to neighbor is better than any previous one, record it
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + h(neighbor, goal, node_data)
                    
                    # Add neighbor to open set if not already there
                    if all(node != neighbor for _, node in open_set):
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # If we get here, there's no path from start to goal
        return [], float('inf')
    
    def _reconstruct_path(self, came_from: Dict[str, str], current: str) -> List[str]:
        """
        Reconstruct the path from start to goal using the came_from dictionary.
        
        Args:
            came_from: Dictionary mapping each node to the node that preceded it on the path
            current: Current node (goal)
            
        Returns:
            List of node IDs representing the path from start to goal
        """
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        
        # Reverse to get path from start to goal
        return list(reversed(total_path))
    
    def multi_criteria_search(self, start: str, goal: str, 
                             criteria: List[Tuple[Dict[str, Dict[str, float]], float]],
                             node_data: Dict[str, Any] = None) -> Tuple[List[str], Dict[str, float]]:
        """
        Perform A* search with multiple criteria.
        
        Args:
            start: Start node ID
            goal: Goal node ID
            criteria: List of tuples (graph, weight) where:
                     - graph is a dictionary representing a graph with edge costs for a specific criterion
                     - weight is the importance of that criterion
            node_data: Optional dictionary containing additional data about nodes
            
        Returns:
            Tuple containing:
                - List of node IDs representing the path from start to goal
                - Dictionary mapping criteria names to their costs
        """
        # Create a combined graph with weighted edge costs
        combined_graph = {}
        
        # Initialize the combined graph with nodes from the main graph
        for node in self.graph:
            combined_graph[node] = {}
        
        # Combine edge costs from all criteria
        for criterion_graph, weight in criteria:
            for node, edges in criterion_graph.items():
                if node not in combined_graph:
                    combined_graph[node] = {}
                
                for neighbor, cost in edges.items():
                    if neighbor not in combined_graph[node]:
                        combined_graph[node][neighbor] = 0
                    
                    # Add weighted cost for this criterion
                    combined_graph[node][neighbor] += cost * weight
        
        # Perform A* search on the combined graph
        path, total_cost = self.search(start, goal, node_data)
        
        # Calculate individual costs for each criterion
        criterion_costs = {}
        for i, (criterion_graph, weight) in enumerate(criteria):
            criterion_cost = 0
            for j in range(len(path) - 1):
                from_node, to_node = path[j], path[j + 1]
                if from_node in criterion_graph and to_node in criterion_graph[from_node]:
                    criterion_cost += criterion_graph[from_node][to_node]
            
            criterion_costs[f"criterion_{i}"] = criterion_cost
        
        return path, criterion_costs
