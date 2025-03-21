"""
Path Finding Spark Job for Reflectly
Finds optimal emotional paths using A* search algorithm
"""
import sys
import json
import argparse
import heapq
from collections import defaultdict
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, collect_list, struct, lit
import pyspark.sql.functions as F

def create_spark_session(app_name="reflectly-path-finding"):
    """
    Create a Spark session
    
    Args:
        app_name (str): Application name
        
    Returns:
        SparkSession: Spark session
    """
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()

def heuristic(current_emotion, target_emotion, successful_transitions=None):
    """
    Heuristic function for A* search
    Estimates the cost to reach the target emotion from the current emotion
    
    Args:
        current_emotion (str): Current emotion
        target_emotion (str): Target emotion
        successful_transitions (dict): Dictionary of successful transitions
            
    Returns:
        float: Estimated cost
    """
    # Define base costs between emotion categories
    # Lower cost means emotions are closer/easier to transition between
    base_costs = {
        ('joy', 'joy'): 0.1,
        ('joy', 'neutral'): 0.5,
        ('joy', 'sadness'): 1.5,
        ('joy', 'anger'): 1.8,
        ('joy', 'fear'): 1.7,
        ('joy', 'disgust'): 1.6,
        
        ('neutral', 'joy'): 0.7,
        ('neutral', 'neutral'): 0.1,
        ('neutral', 'sadness'): 0.9,
        ('neutral', 'anger'): 1.2,
        ('neutral', 'fear'): 1.1,
        ('neutral', 'disgust'): 1.0,
        
        ('sadness', 'joy'): 2.0,
        ('sadness', 'neutral'): 1.0,
        ('sadness', 'sadness'): 0.1,
        ('sadness', 'anger'): 1.3,
        ('sadness', 'fear'): 1.2,
        ('sadness', 'disgust'): 1.1,
        
        ('anger', 'joy'): 2.2,
        ('anger', 'neutral'): 1.3,
        ('anger', 'sadness'): 1.2,
        ('anger', 'anger'): 0.1,
        ('anger', 'fear'): 0.9,
        ('anger', 'disgust'): 0.8,
        
        ('fear', 'joy'): 2.1,
        ('fear', 'neutral'): 1.2,
        ('fear', 'sadness'): 1.1,
        ('fear', 'anger'): 1.0,
        ('fear', 'fear'): 0.1,
        ('fear', 'disgust'): 0.9,
        
        ('disgust', 'joy'): 2.0,
        ('disgust', 'neutral'): 1.1,
        ('disgust', 'sadness'): 1.0,
        ('disgust', 'anger'): 0.9,
        ('disgust', 'fear'): 0.8,
        ('disgust', 'disgust'): 0.1,
    }
    
    # Get the base cost
    emotion_pair = (current_emotion, target_emotion)
    base_cost = base_costs.get(emotion_pair, 1.5)  # Default cost if pair not found
    
    # If successful_transitions is provided, adjust cost based on user's historical transitions
    if successful_transitions:
        # Check if this transition has been successful for the user before
        transition_key = f"{current_emotion}_{target_emotion}"
        if transition_key in successful_transitions:
            # Reduce cost based on success rate
            success_rate = successful_transitions[transition_key].get('success_rate', 0.5)
            adjusted_cost = base_cost * (1 - (success_rate * 0.5))  # Reduce cost by up to 50% based on success rate
            return max(0.1, adjusted_cost)  # Ensure cost is at least 0.1
    
    return base_cost

def get_default_action(from_emotion, to_emotion):
    """
    Get default action for a transition
    
    Args:
        from_emotion (str): Source emotion
        to_emotion (str): Target emotion
        
    Returns:
        str: Default action
    """
    # Define default actions for transitions
    default_actions = {
        ('sadness', 'joy'): "Engage in activities you enjoy",
        ('sadness', 'neutral'): "Practice mindfulness",
        ('sadness', 'anger'): "Express your feelings constructively",
        ('sadness', 'fear'): "Identify specific concerns",
        ('sadness', 'disgust'): "Focus on positive aspects",
        
        ('anger', 'joy'): "Channel energy into positive activities",
        ('anger', 'neutral'): "Take deep breaths and count to 10",
        ('anger', 'sadness'): "Reflect on underlying feelings",
        ('anger', 'fear'): "Consider potential consequences",
        ('anger', 'disgust'): "Shift focus to solutions",
        
        ('fear', 'joy'): "Focus on positive outcomes",
        ('fear', 'neutral'): "Ground yourself in the present moment",
        ('fear', 'sadness'): "Share your concerns with someone you trust",
        ('fear', 'anger'): "Channel fear into productive action",
        ('fear', 'disgust'): "Challenge negative thoughts",
        
        ('disgust', 'joy'): "Focus on things you appreciate",
        ('disgust', 'neutral'): "Practice acceptance",
        ('disgust', 'sadness'): "Explore underlying values",
        ('disgust', 'anger'): "Set boundaries",
        ('disgust', 'fear'): "Examine core concerns",
        
        ('neutral', 'joy'): "Engage in activities you enjoy",
        ('neutral', 'sadness'): "Allow yourself to feel emotions",
        ('neutral', 'anger'): "Identify sources of frustration",
        ('neutral', 'fear'): "Acknowledge concerns",
        ('neutral', 'disgust'): "Identify values being challenged",
        
        ('joy', 'neutral'): "Practice mindfulness",
        ('joy', 'sadness'): "Reflect on meaningful experiences",
        ('joy', 'anger'): "Channel energy constructively",
        ('joy', 'fear'): "Consider growth opportunities",
        ('joy', 'disgust'): "Examine values and boundaries",
    }
    
    # Get default action
    emotion_pair = (from_emotion, to_emotion)
    default_action = default_actions.get(emotion_pair)
    
    # If no default action found, use generic action
    if not default_action:
        if to_emotion == "joy":
            default_action = "Focus on positive aspects of your life"
        elif to_emotion == "neutral":
            default_action = "Practice mindfulness and stay present"
        elif to_emotion == "sadness":
            default_action = "Allow yourself to process emotions"
        elif to_emotion == "anger":
            default_action = "Express feelings constructively"
        elif to_emotion == "fear":
            default_action = "Identify and address specific concerns"
        elif to_emotion == "disgust":
            default_action = "Examine your values and boundaries"
        else:
            default_action = "Reflect on your feelings"
            
    return default_action

def get_default_success_rate(from_emotion, to_emotion):
    """
    Get default success rate for a transition
    
    Args:
        from_emotion (str): Source emotion
        to_emotion (str): Target emotion
        
    Returns:
        float: Default success rate
    """
    # Define default success rates for transitions
    # Higher values indicate easier transitions
    default_success_rates = {
        ('sadness', 'joy'): 0.4,
        ('sadness', 'neutral'): 0.6,
        ('sadness', 'anger'): 0.5,
        ('sadness', 'fear'): 0.5,
        ('sadness', 'disgust'): 0.4,
        
        ('anger', 'joy'): 0.3,
        ('anger', 'neutral'): 0.5,
        ('anger', 'sadness'): 0.5,
        ('anger', 'fear'): 0.6,
        ('anger', 'disgust'): 0.6,
        
        ('fear', 'joy'): 0.3,
        ('fear', 'neutral'): 0.5,
        ('fear', 'sadness'): 0.6,
        ('fear', 'anger'): 0.6,
        ('fear', 'disgust'): 0.5,
        
        ('disgust', 'joy'): 0.3,
        ('disgust', 'neutral'): 0.5,
        ('disgust', 'sadness'): 0.6,
        ('disgust', 'anger'): 0.7,
        ('disgust', 'fear'): 0.6,
        
        ('neutral', 'joy'): 0.7,
        ('neutral', 'sadness'): 0.6,
        ('neutral', 'anger'): 0.5,
        ('neutral', 'fear'): 0.5,
        ('neutral', 'disgust'): 0.5,
        
        ('joy', 'neutral'): 0.8,
        ('joy', 'sadness'): 0.4,
        ('joy', 'anger'): 0.3,
        ('joy', 'fear'): 0.3,
        ('joy', 'disgust'): 0.3,
    }
    
    # Get default success rate
    emotion_pair = (from_emotion, to_emotion)
    default_success_rate = default_success_rates.get(emotion_pair, 0.5)  # Default to 0.5 if not found
    
    return default_success_rate

def get_successful_transitions(transitions):
    """
    Extract successful transitions from transition data
    
    Args:
        transitions (list): List of transition dictionaries
        
    Returns:
        dict: Dictionary of successful transitions
    """
    successful_transitions = {}
    
    for transition in transitions:
        from_emotion = transition.get("from_emotion")
        to_emotion = transition.get("to_emotion")
        actions = transition.get("actions", [])
        
        if not from_emotion or not to_emotion or not actions:
            continue
            
        # Calculate average success rate for this transition
        success_rates = [action.get("success_rate", 0.5) for action in actions if isinstance(action, dict)]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.5
        
        # Store transition with success rate
        transition_key = f"{from_emotion}_{to_emotion}"
        if transition_key not in successful_transitions or avg_success_rate > successful_transitions[transition_key].get("success_rate", 0):
            successful_transitions[transition_key] = {
                "from_emotion": from_emotion,
                "to_emotion": to_emotion,
                "success_rate": avg_success_rate,
                "actions": actions
            }
            
    return successful_transitions

def get_neighbors(transitions, emotion, available_emotions):
    """
    Get possible transitions from the current emotion
    
    Args:
        transitions (list): List of transition dictionaries
        emotion (str): Current emotion
        available_emotions (list): List of available emotions
        
    Returns:
        dict: Dictionary of neighbors with transition information
    """
    # Initialize neighbors
    neighbors = {}
    
    # Extract user's historical transitions
    user_transitions = []
    for transition in transitions:
        if transition.get("from_emotion") == emotion:
            user_transitions.append(transition)
    
    # Add transitions based on user history
    for transition in user_transitions:
        to_emotion = transition.get("to_emotion")
        
        # Skip self-transitions
        if to_emotion == emotion:
            continue
            
        # Get actions and success rates
        actions = []
        success_rates = []
        
        for action_info in transition.get("actions", []):
            if isinstance(action_info, dict):
                actions.append(action_info.get("description", ""))
                success_rates.append(action_info.get("success_rate", 0.5))
            
        # Calculate average success rate
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.5
        
        # Get most successful action
        if actions and success_rates:
            best_action_index = success_rates.index(max(success_rates))
            best_action = actions[best_action_index]
        else:
            best_action = get_default_action(emotion, to_emotion)
            
        # Calculate cost (inverse of success rate)
        cost = 1.0 / max(0.1, avg_success_rate)
        
        # Add to neighbors
        neighbors[to_emotion] = {
            "action": best_action,
            "success_rate": avg_success_rate,
            "cost": cost
        }
    
    # If no transitions found in user history, add default transitions
    if not neighbors:
        for to_emotion in available_emotions:
            # Skip self-transitions
            if to_emotion == emotion:
                continue
                
            # Add default transition
            action = get_default_action(emotion, to_emotion)
            success_rate = get_default_success_rate(emotion, to_emotion)
            cost = 1.0 / max(0.1, success_rate)
            
            neighbors[to_emotion] = {
                "action": action,
                "success_rate": success_rate,
                "cost": cost
            }
            
    return neighbors

def find_path(transitions, current_emotion, target_emotion, max_depth=10):
    """
    Find the optimal path from current_emotion to target_emotion using A* search
    
    Args:
        transitions (list): List of transition dictionaries
        current_emotion (str): Starting emotion
        target_emotion (str): Target emotion
        max_depth (int): Maximum path depth
        
    Returns:
        dict: Optimal path information
    """
    # Check if current and target emotions are the same
    if current_emotion == target_emotion:
        return {
            "current_emotion": current_emotion,
            "target_emotion": target_emotion,
            "path": [current_emotion],
            "actions": [],
            "total_cost": 0,
            "estimated_success_rate": 1.0
        }
        
    # Get available emotions
    available_emotions = ["joy", "sadness", "anger", "fear", "disgust", "neutral"]
        
    # Check if current and target emotions are valid
    if current_emotion not in available_emotions:
        current_emotion = "neutral"
        
    if target_emotion not in available_emotions:
        target_emotion = "joy"
        
    # Get successful transitions for heuristic function
    successful_transitions = get_successful_transitions(transitions)
    
    # Initialize data structures for A* search
    open_set = []  # Priority queue of nodes to explore
    closed_set = set()  # Set of explored nodes
    
    # For each node, g_score[node] is the cost of the cheapest path from start to node
    g_score = defaultdict(lambda: float('inf'))
    g_score[current_emotion] = 0
    
    # For each node, f_score[node] = g_score[node] + heuristic(node, goal)
    f_score = defaultdict(lambda: float('inf'))
    f_score[current_emotion] = heuristic(current_emotion, target_emotion, successful_transitions)
    
    # For each node, came_from[node] is the node immediately preceding it on the cheapest path
    came_from = {}
    
    # For each node, actions[node] is the action to take to get from came_from[node] to node
    actions = {}
    
    # Add start node to open set
    heapq.heappush(open_set, (f_score[current_emotion], current_emotion, 0))  # (f_score, node, depth)
    
    while open_set:
        # Get node with lowest f_score
        _, current, depth = heapq.heappop(open_set)
        
        # Check if we've reached the target
        if current == target_emotion:
            # Reconstruct path
            path = [current]
            path_actions = []
            node = current
            
            while node in came_from:
                prev_node = came_from[node]
                path.append(prev_node)
                
                # Add action to path_actions
                if node in actions and prev_node in actions[node]:
                    action_info = actions[node][prev_node]
                    path_actions.append({
                        "from": prev_node,
                        "to": node,
                        "action": action_info["action"],
                        "success_rate": action_info["success_rate"]
                    })
                    
                node = prev_node
                
            # Reverse path and actions
            path = path[::-1]
            path_actions = path_actions[::-1]
            
            # Calculate estimated success rate
            if path_actions:
                success_rates = [action["success_rate"] for action in path_actions]
                estimated_success_rate = 1.0
                for rate in success_rates:
                    estimated_success_rate *= rate
            else:
                estimated_success_rate = 0.8  # Default if no actions
                
            return {
                "current_emotion": current_emotion,
                "target_emotion": target_emotion,
                "path": path,
                "actions": path_actions,
                "total_cost": g_score[current],
                "estimated_success_rate": estimated_success_rate
            }
            
        # Add current node to closed set
        closed_set.add(current)
        
        # Check if we've reached maximum depth
        if depth >= max_depth:
            continue
            
        # Get neighbors (possible transitions)
        neighbors = get_neighbors(transitions, current, available_emotions)
        
        for neighbor, transition_info in neighbors.items():
            # Skip if neighbor is in closed set
            if neighbor in closed_set:
                continue
                
            # Calculate tentative g_score
            tentative_g_score = g_score[current] + transition_info["cost"]
            
            # Check if this path is better than any previous path
            if tentative_g_score < g_score[neighbor]:
                # Update path
                came_from[neighbor] = current
                
                # Update actions
                if neighbor not in actions:
                    actions[neighbor] = {}
                actions[neighbor][current] = {
                    "action": transition_info["action"],
                    "success_rate": transition_info["success_rate"]
                }
                
                # Update scores
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, target_emotion, successful_transitions)
                
                # Add to open set if not already there
                for i, (_, node, _) in enumerate(open_set):
                    if node == neighbor:
                        open_set[i] = (f_score[neighbor], neighbor, depth + 1)
                        heapq.heapify(open_set)
                        break
                else:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor, depth + 1))
                    
    # If we get here, no path was found
    
    # Return a default path through neutral
    if current_emotion != "neutral" and target_emotion != "neutral":
        # Try to go through neutral
        return {
            "current_emotion": current_emotion,
            "target_emotion": target_emotion,
            "path": [current_emotion, "neutral", target_emotion],
            "actions": [
                {
                    "from": current_emotion,
                    "to": "neutral",
                    "action": "Practice mindfulness",
                    "success_rate": 0.7
                },
                {
                    "from": "neutral",
                    "to": target_emotion,
                    "action": get_default_action("neutral", target_emotion),
                    "success_rate": 0.6
                }
            ],
            "total_cost": 3.0,
            "estimated_success_rate": 0.42  # 0.7 * 0.6
        }
    else:
        # Direct path
        return {
            "current_emotion": current_emotion,
            "target_emotion": target_emotion,
            "path": [current_emotion, target_emotion],
            "actions": [
                {
                    "from": current_emotion,
                    "to": target_emotion,
                    "action": get_default_action(current_emotion, target_emotion),
                    "success_rate": 0.5
                }
            ],
            "total_cost": 2.0,
            "estimated_success_rate": 0.5
        }

def process_path_finding(spark, input_path, output_path, user_email, current_emotion, target_emotion, max_depth):
    """
    Process path finding using Spark
    
    Args:
        spark (SparkSession): Spark session
        input_path (str): Input path to transitions in HDFS
        output_path (str): Output path for path result in HDFS
        user_email (str): User email
        current_emotion (str): Current emotion
        target_emotion (str): Target emotion
        max_depth (int): Maximum path depth
    """
    # Read transitions from HDFS
    transitions_df = spark.read.json(input_path)
    
    # Convert to list of dictionaries
    transitions = [row.asDict() for row in transitions_df.collect()]
    
    # Find path
    path_result = find_path(transitions, current_emotion, target_emotion, max_depth)
    
    # Convert to DataFrame
    path_result_df = spark.createDataFrame([path_result])
    
    # Write to HDFS
    path_result_df.write.mode("overwrite").json(output_path)
    
    return path_result

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Path Finding Spark Job")
    parser.add_argument("--user-email", required=True, help="User email")
    parser.add_argument("--current-emotion", required=True, help="Current emotion")
    parser.add_argument("--target-emotion", required=True, help="Target emotion")
    parser.add_argument("--max-depth", type=int, default=10, help="Maximum path depth")
    parser.add_argument("--input-path", required=True, help="Input path to transitions in HDFS")
    parser.add_argument("--output-path", required=True, help="Output path for path result in HDFS")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Process path finding
        path_result = process_path_finding(
            spark,
            args.input_path,
            args.output_path,
            args.user_email,
            args.current_emotion,
            args.target_emotion,
            args.max_depth
        )
        print(f"Path finding completed: {path_result}")
    finally:
        # Stop Spark session
        spark.stop()

if __name__ == "__main__":
    main()
