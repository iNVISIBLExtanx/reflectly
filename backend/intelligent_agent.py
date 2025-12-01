"""
Enhanced Intelligent Agent with Pathfinding Algorithm Comparison
Compare A*, Bidirectional Search, and Dijkstra's Algorithm in real-time
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import re
import heapq
import time
from collections import defaultdict, deque
import uuid

app = Flask(__name__)

# ENHANCED CORS Configuration for Colab Environment
CORS(app, 
     resources={r"/*": {
         "origins": "*",
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Accept", "Authorization"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": False
     }})

# Critical: Add CORS headers to ALL responses (required for Colab)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    return response

# In-memory storage for the evolving memory map
memory_map = {
    "emotional_states": {},
    "transitions": {},
    "user_experiences": [],
    "graph_connections": defaultdict(list),
    "algorithm_comparisons": []  # NEW: Store comparison results
}

# Emotion analysis class
class EmotionAnalyzer:
    def __init__(self):
        self.emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'glad', 'content', 'pleased', 'thrilled', 'delighted'],
            'sad': ['sad', 'unhappy', 'down', 'depressed', 'blue', 'upset', 'miserable'],
            'anxious': ['anxious', 'worry', 'nervous', 'concerned', 'stressed', 'tense'],
            'angry': ['angry', 'mad', 'annoyed', 'irritated', 'frustrated', 'furious', 'rage'],
            'confused': ['confused', 'uncertain', 'puzzled', 'unsure', 'perplexed', 'lost'],
            'tired': ['tired', 'exhausted', 'drained', 'weary', 'fatigued', 'worn out'],
            'neutral': ['okay', 'fine', 'normal', 'average', 'regular', 'alright']
        }
        
        self.positive_emotions = ['happy']
        self.negative_emotions = ['sad', 'anxious', 'angry', 'confused', 'tired']
        self.neutral_emotions = ['neutral']
    
    def analyze(self, text):
        """Analyze emotion in text"""
        text_lower = text.lower()
        scores = {}
        
        # Calculate scores for each emotion
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[emotion] = score
        
        # Find primary emotion
        if not any(scores.values()):
            primary_emotion = 'neutral'
            confidence = 0.5
        else:
            primary_emotion = max(scores, key=scores.get)
            total_score = sum(scores.values())
            confidence = scores[primary_emotion] / total_score if total_score > 0 else 0.5
        
        # Determine emotion type
        if primary_emotion in self.positive_emotions:
            emotion_type = 'positive'
        elif primary_emotion in self.negative_emotions:
            emotion_type = 'negative'
        else:
            emotion_type = 'neutral'
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': confidence,
            'emotion_type': emotion_type
        }

# Activity extraction class
class ActivityExtractor:
    def __init__(self):
        self.activity_patterns = [
            r"(?:I|we)\s+(?:did|tried|enjoyed|attempted)\s+([\w\s]+)",
            r"(?:did|tried|enjoyed|attempted)\s+([\w\s]+)",
            r"(?:I|we)\s+(?:went|visited)\s+([\w\s]+)",
            r"(?:spent time|relaxed)\s+([\w\s]+)"
        ]
    
    def extract_activities(self, text):
        """Extract activities from text"""
        activities = []
        
        for pattern in self.activity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            activities.extend([match.strip() for match in matches if match.strip()])
        
        # Return empty list instead of a default "unspecified activity"
        return activities

# Import the pathfinding comparison classes (simplified for integration)
class PerformanceMetrics:
    def __init__(self, algorithm_name: str):
        self.algorithm_name = algorithm_name
        self.nodes_explored = 0
        self.start_time = None
        self.end_time = None
        self.path_found = False
        self.path_length = 0
    
    def start_timing(self):
        self.start_time = time.time()
        self.nodes_explored = 0
        
    def end_timing(self, path=None):
        self.end_time = time.time()
        if path:
            self.path_found = True
            self.path_length = len(path)
    
    def record_node_exploration(self):
        self.nodes_explored += 1
    
    @property
    def execution_time(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    def to_dict(self):
        return {
            'algorithm': self.algorithm_name,
            'execution_time_ms': round(self.execution_time * 1000, 3),
            'nodes_explored': self.nodes_explored,
            'path_found': self.path_found,
            'path_length': self.path_length,
            'efficiency_score': (self.execution_time * 1000) + (self.nodes_explored * 0.1)
        }

class PathfindingComparator:
    def __init__(self, memory_map):
        self.memory_map = memory_map
        self.emotion_hierarchy = {
            'happy': 1, 'neutral': 2, 'confused': 3, 
            'tired': 4, 'sad': 5, 'anxious': 5, 'angry': 6
        }
    
    def get_neighbors(self, emotion: str):
        """Get neighboring emotions with costs"""
        neighbors = []
        
        for next_emotion in self.memory_map.get("graph_connections", {}).get(emotion, []):
            transition_key = (emotion, next_emotion)
            if transition_key in self.memory_map.get("transitions", {}):
                actions = self.memory_map["transitions"][transition_key]
                if actions:
                    success_rates = [action.get('success_count', 1) for action in actions]
                    avg_success = sum(success_rates) / len(success_rates)
                    cost = 1.0 / max(0.1, avg_success)
                    neighbors.append((next_emotion, cost))
        
        if not neighbors:
            for emotion_name in self.emotion_hierarchy.keys():
                if emotion_name != emotion:
                    cost = abs(self.emotion_hierarchy[emotion] - self.emotion_hierarchy[emotion_name])
                    neighbors.append((emotion_name, cost))
        
        return neighbors
    
    def heuristic(self, current: str, target: str) -> float:
        current_level = self.emotion_hierarchy.get(current, 3)
        target_level = self.emotion_hierarchy.get(target, 3)
        return abs(current_level - target_level)
    
    def astar_search(self, start: str, goal: str, max_depth: int = 8):
        """A* Algorithm"""
        metrics = PerformanceMetrics("A*")
        metrics.start_timing()
        
        open_set = [(self.heuristic(start, goal), 0, start, [start])]
        closed_set = set()
        g_scores = {start: 0}
        
        while open_set:
            f_score, g_score, current, path = heapq.heappop(open_set)
            
            if current in closed_set:
                continue
                
            metrics.record_node_exploration()
            closed_set.add(current)
            
            if current == goal:
                metrics.end_timing(path)
                return path, metrics
            
            if len(path) >= max_depth:
                continue
            
            for neighbor, cost in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score + cost
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor, path + [neighbor]))
        
        metrics.end_timing()
        return [], metrics
    
    def bidirectional_search(self, start: str, goal: str, max_depth: int = 8):
        """Bidirectional Search Algorithm"""
        metrics = PerformanceMetrics("Bidirectional")
        metrics.start_timing()
        
        if start == goal:
            metrics.end_timing([start])
            return [start], metrics
        
        forward_queue = deque([(start, [start], 0)])
        backward_queue = deque([(goal, [goal], 0)])
        
        forward_visited = {start: [start]}
        backward_visited = {goal: [goal]}
        
        while forward_queue or backward_queue:
            # Forward search
            if forward_queue:
                current, path, cost = forward_queue.popleft()
                metrics.record_node_exploration()
                
                if current in backward_visited:
                    backward_path = backward_visited[current]
                    full_path = path + backward_path[-2::-1]
                    metrics.end_timing(full_path)
                    return full_path, metrics
                
                if len(path) < max_depth:
                    for neighbor, edge_cost in self.get_neighbors(current):
                        new_path = path + [neighbor]
                        if neighbor not in forward_visited:
                            forward_visited[neighbor] = new_path
                            forward_queue.append((neighbor, new_path, cost + edge_cost))
            
            # Backward search
            if backward_queue:
                current, path, cost = backward_queue.popleft()
                metrics.record_node_exploration()
                
                if current in forward_visited:
                    forward_path = forward_visited[current]
                    full_path = forward_path + path[-2::-1]
                    metrics.end_timing(full_path)
                    return full_path, metrics
                
                if len(path) < max_depth:
                    for neighbor, edge_cost in self.get_reverse_neighbors(current):
                        new_path = path + [neighbor]
                        if neighbor not in backward_visited:
                            backward_visited[neighbor] = new_path
                            backward_queue.append((neighbor, new_path, cost + edge_cost))
        
        metrics.end_timing()
        return [], metrics
    
    def dijkstra_search(self, start: str, goal: str, max_depth: int = 8):
        """Dijkstra's Algorithm"""
        metrics = PerformanceMetrics("Dijkstra")
        metrics.start_timing()
        
        open_set = [(0, start, [start])]
        visited = set()
        distances = {start: 0}
        
        while open_set:
            current_cost, current, path = heapq.heappop(open_set)
            
            if current in visited:
                continue
                
            metrics.record_node_exploration()
            visited.add(current)
            
            if current == goal:
                metrics.end_timing(path)
                return path, metrics
            
            if len(path) >= max_depth:
                continue
            
            for neighbor, edge_cost in self.get_neighbors(current):
                if neighbor in visited:
                    continue
                
                new_cost = current_cost + edge_cost
                
                if neighbor not in distances or new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    new_path = path + [neighbor]
                    heapq.heappush(open_set, (new_cost, neighbor, new_path))
        
        metrics.end_timing()
        return [], metrics
    
    def get_reverse_neighbors(self, emotion: str):
        """Get reverse neighbors for bidirectional search"""
        neighbors = []
        
        for (from_emotion, to_emotion), actions in self.memory_map.get("transitions", {}).items():
            if to_emotion == emotion:
                if actions:
                    success_rates = [action.get('success_count', 1) for action in actions]
                    avg_success = sum(success_rates) / len(success_rates)
                    cost = 1.0 / max(0.1, avg_success)
                    neighbors.append((from_emotion, cost))
        
        if not neighbors:
            for emotion_name in self.emotion_hierarchy.keys():
                if emotion_name != emotion:
                    cost = abs(self.emotion_hierarchy[emotion] - self.emotion_hierarchy[emotion_name])
                    neighbors.append((emotion_name, cost))
        
        return neighbors
    
    def compare_algorithms(self, start: str, goal: str):
        """Compare all three algorithms"""
        results = {}
        
        # Test A*
        path_astar, metrics_astar = self.astar_search(start, goal)
        results['A*'] = {
            'path': path_astar,
            'metrics': metrics_astar.to_dict()
        }
        
        # Test Bidirectional Search
        path_bid, metrics_bid = self.bidirectional_search(start, goal)
        results['Bidirectional'] = {
            'path': path_bid,
            'metrics': metrics_bid.to_dict()
        }
        
        # Test Dijkstra
        path_dij, metrics_dij = self.dijkstra_search(start, goal)
        results['Dijkstra'] = {
            'path': path_dij,
            'metrics': metrics_dij.to_dict()
        }
        
        # Determine winner
        successful = {name: data for name, data in results.items() if data['metrics']['path_found']}
        
        if successful:
            winner = min(successful.items(), key=lambda x: x[1]['metrics']['execution_time_ms'])
            winner_info = {
                'algorithm': winner[0],
                'time_ms': winner[1]['metrics']['execution_time_ms'],
                'nodes_explored': winner[1]['metrics']['nodes_explored']
            }
        else:
            winner_info = {'algorithm': 'None', 'time_ms': 0, 'nodes_explored': 0}
        
        comparison_result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'start_emotion': start,
            'goal_emotion': goal,
            'results': results,
            'winner': winner_info
        }
        
        return comparison_result

# Enhanced Intelligent Agent with original functionality + algorithm comparison
class IntelligentAgent:
    def __init__(self):
        # Import locally to avoid circular import issues
        # The EmotionAnalyzer and ActivityExtractor classes are defined in this same file
        self.emotion_analyzer = EmotionAnalyzer()
        self.activity_extractor = ActivityExtractor()
        self.pathfinding_comparator = PathfindingComparator(memory_map)
        
    def process_input(self, text, user_id="default_user"):
        # ... (original process_input logic from previous code)
        # For brevity, using simplified version
        
        emotion_analysis = self.emotion_analyzer.analyze(text)
        primary_emotion = emotion_analysis['primary_emotion']
        emotion_type = emotion_analysis['emotion_type']
        
        extracted_activities = self.activity_extractor.extract_activities(text)
        
        experience = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'text': text,
            'emotion': primary_emotion,
            'emotion_type': emotion_type,
            'confidence': emotion_analysis['confidence'],
            'timestamp': datetime.datetime.now().isoformat(),
            'extracted_activities': extracted_activities
        }
        
        memory_map["user_experiences"].append(experience)
        
        if primary_emotion not in memory_map["emotional_states"]:
            memory_map["emotional_states"][primary_emotion] = []
        memory_map["emotional_states"][primary_emotion].append(experience)
        
        if extracted_activities:
            self._auto_learn_from_experience(experience, extracted_activities)
        
        if emotion_type == 'positive':
            # Always ask for steps when a positive emotion is detected
            # This ensures we always show the steps popup
            return self._handle_positive_emotion(experience)
        elif emotion_type == 'negative':
            return self._handle_negative_emotion(experience)
        else:
            return self._handle_neutral_emotion(experience)
    
    def _auto_learn_from_experience(self, experience, activities):
        prev_emotion = self._get_previous_emotion(experience)
        current_emotion = experience['emotion']
        
        if prev_emotion and prev_emotion != current_emotion:
            self._save_transition(prev_emotion, current_emotion, activities, experience['id'])
    
    def _save_transition(self, from_emotion, to_emotion, activities, experience_id):
        transition_key = (from_emotion, to_emotion)
        
        if transition_key not in memory_map["transitions"]:
            memory_map["transitions"][transition_key] = []
        
        for activity in activities:
            action_record = {
                'action': activity,
                'success_count': 1,
                'timestamp': datetime.datetime.now().isoformat(),
                'experience_id': experience_id
            }
            memory_map["transitions"][transition_key].append(action_record)
        
        if to_emotion not in memory_map["graph_connections"][from_emotion]:
            memory_map["graph_connections"][from_emotion].append(to_emotion)
    
    def _get_previous_emotion(self, current_experience):
        current_time = datetime.datetime.fromisoformat(current_experience['timestamp'])
        
        for exp in reversed(memory_map["user_experiences"]):
            exp_time = datetime.datetime.fromisoformat(exp['timestamp'])
            if (exp_time < current_time and 
                exp['emotion'] != current_experience['emotion'] and
                exp['user_id'] == current_experience['user_id']):
                return exp['emotion']
        
        return None
    
    def _handle_positive_with_activities(self, experience, activities):
        return {
            'type': 'learned_automatically',
            'message': f"Wonderful! I can see you're feeling {experience['emotion']}. I noticed: {', '.join(activities)}. I'll remember this!",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'learned_activities': activities,
            'suggestions': []
        }
    
    def _handle_positive_emotion(self, experience):
        return {
            'type': 'ask_for_steps',
            'message': f"That's wonderful! What steps led to this {experience['emotion']} feeling?",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': []
        }
    
    def _handle_negative_emotion(self, experience):
        # ENHANCED: Use algorithm comparison for suggestions
        current_emotion = experience['emotion']
        target_emotion = 'happy'
        
        # Run algorithm comparison
        comparison_result = self.pathfinding_comparator.compare_algorithms(current_emotion, target_emotion)
        memory_map["algorithm_comparisons"].append(comparison_result)
        
        # Get suggestions from the winning algorithm
        winner = comparison_result['winner']
        if winner['algorithm'] != 'None':
            winning_result = comparison_result['results'][winner['algorithm']]
            path = winning_result['path']
            
            # Convert path to action suggestions
            suggestions = self._path_to_suggestions(path)
            
            message = f"I understand you're feeling {current_emotion}. I used {winner['algorithm']} algorithm (found path in {winner['time_ms']:.1f}ms) to find these suggestions:"
        else:
            suggestions = self._get_default_suggestions(current_emotion)
            message = f"I understand you're feeling {current_emotion}. Here are some general suggestions:"
        
        return {
            'type': 'suggest_actions_with_algorithm',
            'message': message,
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': suggestions,
            'algorithm_used': winner['algorithm'],
            'algorithm_performance': winner,
            'comparison_details': comparison_result
        }
    
    def _handle_neutral_emotion(self, experience):
        return {
            'type': 'general_guidance',
            'message': f"I see you're feeling {experience['emotion']}. Would you like some suggestions?",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': ["Try engaging in a hobby", "Take a short walk", "Connect with a friend"]
        }
    
    def _path_to_suggestions(self, path):
        """Convert emotional path to action suggestions"""
        suggestions = []
        
        for i in range(len(path) - 1):
            from_emotion = path[i]
            to_emotion = path[i + 1]
            transition_key = (from_emotion, to_emotion)
            
            if transition_key in memory_map["transitions"]:
                actions = memory_map["transitions"][transition_key]
                if actions:
                    best_action = max(actions, key=lambda x: x.get('success_count', 1))
                    suggestions.append(best_action['action'])
        
        if not suggestions:
            suggestions = self._get_default_suggestions(path[0] if path else 'neutral')
        
        return suggestions[:3]
    
    def _get_default_suggestions(self, emotion):
        defaults = {
            'sad': ["Listen to uplifting music", "Call a friend", "Take a warm bath"],
            'anxious': ["Practice deep breathing", "Try grounding techniques", "Go for a walk"],
            'angry': ["Count to 10", "Write down feelings", "Do exercise"],
            'confused': ["Break down the problem", "Talk to someone", "Take time to reflect"],
            'tired': ["Take a short nap", "Drink water", "Get fresh air"],
            'neutral': ["Try something enjoyable", "Take a walk", "Practice gratitude"]
        }
        return defaults.get(emotion, ["Be kind to yourself"])

# Initialize agent
agent = IntelligentAgent()

# Enhanced API Routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Enhanced Intelligent Agent with Algorithm Comparison",
        "features": ["emotion_analysis", "natural_language_learning", "algorithm_comparison"],
        "algorithms": ["A*", "Bidirectional Search", "Dijkstra"],
        "memory_stats": {
            "total_experiences": len(memory_map["user_experiences"]),
            "emotional_states": len(memory_map["emotional_states"]),
            "learned_transitions": len(memory_map["transitions"]),
            "algorithm_comparisons": len(memory_map["algorithm_comparisons"])
        }
    })

@app.route('/api/process-input', methods=['POST', 'OPTIONS'])
def process_input():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        user_id = data.get('user_id', 'default_user')
        
        if not text.strip():
            return jsonify({"error": "Text input is required"}), 400
        
        response = agent.process_input(text, user_id)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Failed to process input: {str(e)}"}), 500

@app.route('/api/compare-algorithms', methods=['POST', 'OPTIONS'])
def compare_algorithms():
    """NEW: Direct algorithm comparison endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        start_emotion = data.get('start_emotion', 'sad')
        goal_emotion = data.get('goal_emotion', 'happy')
        
        comparator = PathfindingComparator(memory_map)
        result = comparator.compare_algorithms(start_emotion, goal_emotion)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to compare algorithms: {str(e)}"}), 500

@app.route('/api/algorithm-performance', methods=['GET'])
def get_algorithm_performance():
    """NEW: Get algorithm performance statistics"""
    try:
        if not memory_map["algorithm_comparisons"]:
            return jsonify({"message": "No algorithm comparisons performed yet"})
        
        # Analyze performance across all comparisons
        algorithm_stats = defaultdict(lambda: {
            'total_uses': 0,
            'wins': 0,
            'avg_time_ms': 0,
            'avg_nodes_explored': 0,
            'success_rate': 0
        })
        
        for comparison in memory_map["algorithm_comparisons"]:
            winner = comparison['winner']['algorithm']
            
            for algorithm, data in comparison['results'].items():
                stats = algorithm_stats[algorithm]
                stats['total_uses'] += 1
                
                if data['metrics']['path_found']:
                    stats['success_rate'] += 1
                    stats['avg_time_ms'] += data['metrics']['execution_time_ms']
                    stats['avg_nodes_explored'] += data['metrics']['nodes_explored']
                
                if algorithm == winner:
                    stats['wins'] += 1
        
        # Calculate averages
        for algorithm, stats in algorithm_stats.items():
            if stats['success_rate'] > 0:
                stats['avg_time_ms'] /= stats['success_rate']
                stats['avg_nodes_explored'] /= stats['success_rate']
            stats['success_rate'] = (stats['success_rate'] / stats['total_uses']) * 100
            stats['win_rate'] = (stats['wins'] / stats['total_uses']) * 100
        
        return jsonify({
            'total_comparisons': len(memory_map["algorithm_comparisons"]),
            'algorithm_statistics': dict(algorithm_stats),
            'recent_comparisons': memory_map["algorithm_comparisons"][-5:]
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get performance data: {str(e)}"}), 500

@app.route('/api/memory-map', methods=['GET'])
def get_memory_map():
    try:
        nodes = []
        edges = []
        
        for emotion, experiences in memory_map["emotional_states"].items():
            nodes.append({
                'id': emotion,
                'label': emotion.title(),
                'count': len(experiences),
                'type': 'positive' if emotion == 'happy' else 'negative' if emotion in ['sad', 'anxious', 'angry'] else 'neutral'
            })
        
        for (from_emotion, to_emotion), actions in memory_map["transitions"].items():
            edges.append({
                'from': from_emotion,
                'to': to_emotion,
                'actions': len(actions),
                'weight': len(actions)
            })
        
        return jsonify({
            'nodes': nodes,
            'edges': edges,
            'total_experiences': len(memory_map["user_experiences"]),
            'total_transitions': len(memory_map["transitions"])
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get memory map: {str(e)}"}), 500

@app.route('/api/reset-memory', methods=['POST', 'OPTIONS'])
def reset_memory():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        memory_map["emotional_states"].clear()
        memory_map["transitions"].clear()
        memory_map["user_experiences"].clear()
        memory_map["graph_connections"].clear()
        memory_map["algorithm_comparisons"].clear()
        
        return jsonify({"message": "Memory map and algorithm comparisons reset successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to reset memory: {str(e)}"}), 500

@app.route('/api/save-steps', methods=['POST', 'OPTIONS'])
def save_steps():
    """Save steps that led to a positive emotion"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        experience_id = data.get('experience_id')
        steps = data.get('steps', [])
        
        if not experience_id or not steps:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Find the experience
        experience = None
        for exp in memory_map["user_experiences"]:
            if exp["id"] == experience_id:
                experience = exp
                break
                
        if not experience:
            return jsonify({'error': f'Experience {experience_id} not found'}), 404
            
        # Add steps to the experience
        experience["activities"] = steps
        
        # Process transition learning if this was a positive emotion
        agent = IntelligentAgent()
        prev_emotion = agent._get_previous_emotion(experience)
        current_emotion = experience['emotion']
        
        # Only create transition if there was a previous emotion and it's different
        if prev_emotion and prev_emotion != current_emotion:
            agent._save_transition(prev_emotion, current_emotion, steps, experience_id)
        
        return jsonify({
            'message': f"Great! I've learned that {', '.join(steps)} can lead to feeling {experience['emotion']}!",
            'experience_id': experience_id,
            'emotion': experience['emotion'],
            'learned_activities': steps
        })
    except Exception as e:
        return jsonify({'error': f'Failed to save steps: {str(e)}'}), 500

@app.route('/api/memory-stats', methods=['GET'])
def get_memory_stats():
    """Get learning statistics about the memory map"""
    try:
        # Count unique emotions
        emotions_learned = len(memory_map["emotional_states"])
        
        # Count total experiences
        total_experiences = len(memory_map["user_experiences"])
        
        # Count transitions learned
        transitions_learned = len(memory_map["transitions"])
        
        # Count algorithm comparisons
        algorithm_comparisons = len(memory_map["algorithm_comparisons"])
        
        # Get algorithm performance if any comparisons exist
        algorithm_stats = {}
        if memory_map["algorithm_comparisons"]:
            # Count algorithm usage
            for comp in memory_map["algorithm_comparisons"]:
                if "results" in comp:
                    for algo, result in comp["results"].items():
                        if algo not in algorithm_stats:
                            algorithm_stats[algo] = {
                                "uses": 0,
                                "wins": 0,
                                "avg_time_ms": 0,
                                "avg_path_length": 0
                            }
                        algorithm_stats[algo]["uses"] += 1
                        
                        # Track time and path length
                        if "execution_time_ms" in result:
                            algorithm_stats[algo]["avg_time_ms"] += result["execution_time_ms"]
                        
                        if "path_length" in result:
                            algorithm_stats[algo]["avg_path_length"] += result.get("path_length", 0)
                    
                # Track wins
                if "winner" in comp and comp["winner"].get("algorithm") != "None":
                    algo = comp["winner"]["algorithm"]
                    if algo in algorithm_stats:
                        algorithm_stats[algo]["wins"] += 1
            
            # Calculate averages
            for algo, stats in algorithm_stats.items():
                uses = stats["uses"]
                if uses > 0:
                    stats["avg_time_ms"] = round(stats["avg_time_ms"] / uses, 2)
                    stats["avg_path_length"] = round(stats["avg_path_length"] / uses, 2)
                    stats["win_rate"] = round((stats["wins"] / uses) * 100, 1)
        
        return jsonify({
            "total_experiences": total_experiences,
            "emotions_learned": emotions_learned,
            "transitions_learned": transitions_learned,
            "algorithm_comparisons": algorithm_comparisons,
            "algorithm_performance": algorithm_stats
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get memory stats: {str(e)}"}), 500

if __name__ == '__main__':
    print("🤖 Starting Enhanced Intelligent Agent with Algorithm Comparison")
    print("🧠 Features: A* vs Bidirectional vs Dijkstra")
    print("📡 API: http://localhost:5000")
    print("🗺️  Memory Map: Learning + Real-time algorithm comparison")
    print("⚡ NEW: /api/compare-algorithms endpoint")
    print("📊 NEW: /api/algorithm-performance endpoint")
    print("🌐 CORS: Enabled for Colab environment")
    # Get port from environment variable, defaulting to 5000
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
