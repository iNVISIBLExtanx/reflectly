"""
Ultra-Simple Reflectly Backend for Algorithm Development
Pure Python Flask app with in-memory storage - no databases, no Docker
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
from collections import defaultdict
import re
import math
import heapq

app = Flask(__name__)
CORS(app)

# In-memory storage (replace database)
emotional_states = []
emotional_transitions = []
user_data = defaultdict(list)

# Available emotions
EMOTIONS = ['joy', 'sadness', 'anger', 'fear', 'disgust', 'surprise', 'neutral']
POSITIVE_EMOTIONS = ['joy', 'surprise']
NEGATIVE_EMOTIONS = ['sadness', 'anger', 'fear', 'disgust']

class SimpleEmotionAnalyzer:
    """Simple emotion analysis using keyword matching"""
    
    def __init__(self):
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'joy', 'cheerful', 'glad', 'delighted', 'pleased', 'thrilled', 'elated'],
            'sadness': ['sad', 'depressed', 'down', 'upset', 'miserable', 'gloomy', 'sorrowful', 'melancholy'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated', 'rage', 'livid'],
            'fear': ['scared', 'afraid', 'frightened', 'worried', 'anxious', 'nervous', 'terrified', 'panic'],
            'disgust': ['disgusted', 'revolted', 'sickened', 'appalled', 'repulsed', 'nauseated'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'unexpected'],
        }
    
    def analyze(self, text):
        """Analyze emotion in text using simple keyword matching"""
        text_lower = text.lower()
        scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[emotion] = score
        
        # If no emotions detected, default to neutral
        if not any(scores.values()):
            scores['neutral'] = 1
        
        # Get primary emotion
        primary_emotion = max(scores, key=scores.get)
        
        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            normalized_scores = {k: v/total_score for k, v in scores.items()}
        else:
            normalized_scores = {emotion: 1/len(EMOTIONS) for emotion in EMOTIONS}
        
        return {
            'primary_emotion': primary_emotion,
            'is_positive': primary_emotion in POSITIVE_EMOTIONS,
            'emotion_scores': normalized_scores,
            'confidence': max(normalized_scores.values())
        }

class AStarPathfinder:
    """A* algorithm for finding optimal emotional paths"""
    
    def __init__(self):
        # Default transition costs (can be personalized later)
        self.base_costs = {
            ('sadness', 'joy'): 2.0,
            ('sadness', 'neutral'): 1.0,
            ('anger', 'joy'): 2.2,
            ('anger', 'neutral'): 1.3,
            ('fear', 'joy'): 2.1,
            ('fear', 'neutral'): 1.2,
            ('disgust', 'joy'): 2.0,
            ('disgust', 'neutral'): 1.1,
            ('neutral', 'joy'): 0.7,
            # Add reverse and other combinations
        }
        
        # Fill in missing combinations with default values
        for from_emotion in EMOTIONS:
            for to_emotion in EMOTIONS:
                if from_emotion != to_emotion and (from_emotion, to_emotion) not in self.base_costs:
                    if to_emotion in POSITIVE_EMOTIONS:
                        self.base_costs[(from_emotion, to_emotion)] = 1.5
                    elif to_emotion == 'neutral':
                        self.base_costs[(from_emotion, to_emotion)] = 1.0
                    else:
                        self.base_costs[(from_emotion, to_emotion)] = 1.2
    
    def heuristic(self, current, target):
        """Heuristic function for A* search"""
        if current == target:
            return 0
        return self.base_costs.get((current, target), 1.5)
    
    def get_neighbors(self, emotion):
        """Get possible transitions from an emotion"""
        neighbors = {}
        for target in EMOTIONS:
            if target != emotion:
                cost = self.base_costs.get((emotion, target), 1.5)
                action = self.get_action(emotion, target)
                neighbors[target] = {
                    'cost': cost,
                    'action': action,
                    'success_rate': 1.0 / cost  # Higher cost = lower success rate
                }
        return neighbors
    
    def get_action(self, from_emotion, to_emotion):
        """Get recommended action for transition"""
        actions = {
            ('sadness', 'joy'): "Engage in activities you enjoy",
            ('sadness', 'neutral'): "Practice mindfulness meditation",
            ('anger', 'joy'): "Channel energy into positive activities",
            ('anger', 'neutral'): "Take deep breaths and count to 10",
            ('fear', 'joy'): "Focus on positive outcomes",
            ('fear', 'neutral'): "Ground yourself in the present moment",
            ('disgust', 'joy'): "Focus on things you appreciate",
            ('disgust', 'neutral'): "Practice acceptance",
            ('neutral', 'joy'): "Engage in activities you enjoy",
        }
        return actions.get((from_emotion, to_emotion), f"Work on transitioning from {from_emotion} to {to_emotion}")
    
    def find_path(self, start, goal, max_depth=5):
        """Find optimal path using A* algorithm"""
        if start == goal:
            return {
                'path': [start],
                'actions': [],
                'total_cost': 0,
                'estimated_success_rate': 1.0
            }
        
        # A* algorithm implementation
        open_set = [(0, start, [])]  # (f_score, current_node, path)
        closed_set = set()
        g_score = {start: 0}
        
        while open_set:
            current_f, current, path = heapq.heappop(open_set)
            
            if len(path) >= max_depth:
                continue
                
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            if current == goal:
                # Reconstruct path with actions
                full_path = path + [current]
                actions = []
                total_cost = g_score[current]
                
                for i in range(len(full_path) - 1):
                    from_emotion = full_path[i]
                    to_emotion = full_path[i + 1]
                    action = self.get_action(from_emotion, to_emotion)
                    cost = self.base_costs.get((from_emotion, to_emotion), 1.5)
                    
                    actions.append({
                        'from': from_emotion,
                        'to': to_emotion,
                        'action': action,
                        'success_rate': min(1.0, 1.0 / cost)
                    })
                
                # Calculate estimated success rate
                if actions:
                    success_rates = [action['success_rate'] for action in actions]
                    estimated_success_rate = 1.0
                    for rate in success_rates:
                        estimated_success_rate *= rate
                else:
                    estimated_success_rate = 1.0
                
                return {
                    'path': full_path,
                    'actions': actions,
                    'total_cost': total_cost,
                    'estimated_success_rate': estimated_success_rate
                }
            
            # Explore neighbors
            neighbors = self.get_neighbors(current)
            for neighbor, info in neighbors.items():
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current] + info['cost']
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor, path + [current]))
        
        # No path found, return direct transition
        return {
            'path': [start, goal],
            'actions': [{
                'from': start,
                'to': goal,
                'action': self.get_action(start, goal),
                'success_rate': 0.5
            }],
            'total_cost': self.base_costs.get((start, goal), 2.0),
            'estimated_success_rate': 0.5
        }

# Initialize AI components
emotion_analyzer = SimpleEmotionAnalyzer()
pathfinder = AStarPathfinder()

# API Routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Simple AI backend running"})

@app.route('/api/emotions/analyze', methods=['POST'])
def analyze_emotion():
    data = request.get_json()
    text = data.get('text', '')
    user_email = data.get('user_email', 'demo@example.com')
    
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    # Analyze emotion
    result = emotion_analyzer.analyze(text)
    
    # Store in memory
    emotion_entry = {
        'id': len(emotional_states),
        'user_email': user_email,
        'text': text,
        'timestamp': datetime.datetime.now().isoformat(),
        **result
    }
    emotional_states.append(emotion_entry)
    user_data[user_email].append(emotion_entry)
    
    return jsonify(result)

@app.route('/api/emotions/path', methods=['POST'])
def find_path():
    data = request.get_json()
    current_emotion = data.get('current_emotion', '')
    target_emotion = data.get('target_emotion', '')
    
    if not current_emotion or not target_emotion:
        return jsonify({"error": "current_emotion and target_emotion are required"}), 400
    
    if current_emotion not in EMOTIONS or target_emotion not in EMOTIONS:
        return jsonify({"error": "Invalid emotion"}), 400
    
    # Find optimal path
    result = pathfinder.find_path(current_emotion, target_emotion)
    
    return jsonify({
        'current_emotion': current_emotion,
        'target_emotion': target_emotion,
        **result
    })

@app.route('/api/emotions/available', methods=['GET'])
def get_emotions():
    return jsonify({"emotions": EMOTIONS})

@app.route('/api/emotions/suggestions', methods=['POST'])
def get_suggestions():
    data = request.get_json()
    current_emotion = data.get('current_emotion', '')
    
    suggestions = {
        'sadness': [
            "Listen to uplifting music",
            "Call a friend or family member", 
            "Take a walk in nature",
            "Practice gratitude by writing 3 good things"
        ],
        'anger': [
            "Take 10 deep breaths",
            "Do some physical exercise",
            "Write down your feelings",
            "Count to 10 slowly"
        ],
        'fear': [
            "Practice grounding techniques",
            "Challenge negative thoughts",
            "Talk to someone you trust",
            "Focus on what you can control"
        ],
        'disgust': [
            "Focus on positive aspects",
            "Practice acceptance",
            "Engage in a pleasant activity",
            "Connect with supportive people"
        ],
        'neutral': [
            "Set a small goal for today",
            "Practice mindfulness",
            "Try something new",
            "Express gratitude"
        ],
        'joy': [
            "Share your happiness with others",
            "Savor the moment",
            "Use this energy for creative activities",
            "Help someone else"
        ],
        'surprise': [
            "Reflect on what surprised you",
            "Consider what you can learn",
            "Share the experience",
            "Embrace the unexpected"
        ]
    }
    
    return jsonify({"suggestions": suggestions.get(current_emotion, [])})

@app.route('/api/emotions/graph-data/<user_email>', methods=['GET'])
def get_graph_data(user_email):
    # Create simple graph data for visualization
    nodes = [{'id': emotion, 'label': emotion.title()} for emotion in EMOTIONS]
    
    # Create edges based on common transitions
    edges = []
    common_transitions = [
        ('sadness', 'neutral'), ('neutral', 'joy'),
        ('anger', 'neutral'), ('fear', 'neutral'),
        ('disgust', 'neutral'), ('surprise', 'joy')
    ]
    
    for from_emotion, to_emotion in common_transitions:
        edges.append({
            'from': from_emotion,
            'to': to_emotion,
            'weight': 1
        })
    
    # Add user's emotional history
    history = user_data.get(user_email, [])
    
    return jsonify({
        'nodes': nodes,
        'edges': edges,
        'history': history[-10:]  # Last 10 entries
    })

@app.route('/api/test-algorithm', methods=['GET'])
def test_algorithm():
    """Test endpoint to verify A* algorithm is working"""
    test_results = []
    
    test_cases = [
        ('sadness', 'joy'),
        ('anger', 'neutral'),
        ('fear', 'joy'),
        ('disgust', 'neutral')
    ]
    
    for start, goal in test_cases:
        result = pathfinder.find_path(start, goal)
        test_results.append({
            'test': f"{start} -> {goal}",
            'path': result['path'],
            'cost': result['total_cost'],
            'success_rate': result['estimated_success_rate']
        })
    
    return jsonify({"algorithm_tests": test_results})

if __name__ == '__main__':
    print("🧠 Starting Simple Reflectly AI Backend")
    print("🎯 Focus: Algorithm Development")
    print("📡 API: http://localhost:5000")
    print("🔬 Test endpoint: http://localhost:5000/api/test-algorithm")
    app.run(host='0.0.0.0', port=5000, debug=True)
