"""
Intelligent Agent with Memory Map and A* Search - FIXED VERSION
Learns from user experiences and suggests actions based on past successful transitions
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import re
import heapq
from collections import defaultdict
import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# In-memory storage for the evolving memory map
memory_map = {
    "emotional_states": {},  # emotion -> list of experiences
    "transitions": {},       # (from_emotion, to_emotion) -> list of successful actions
    "user_experiences": [],  # chronological list of all experiences
    "graph_connections": defaultdict(list),  # emotion -> list of connected emotions
    "activity_patterns": {}  # Learned activity extraction patterns
}

class EmotionAnalyzer:
    """Analyzes text to detect emotions"""
    
    def __init__(self):
        self.emotion_keywords = {
            # FIXED: Added missing positive keywords
            'happy': ['happy', 'joyful', 'excited', 'glad', 'cheerful', 'delighted', 'elated', 
                     'thrilled', 'content', 'pleased', 'amazing', 'wonderful', 'fantastic', 
                     'great', 'awesome', 'love', 'perfect', 'good', 'better', 'feeling good', 
                     'feeling better', 'much better', 'excellent', 'brilliant', 'superb'],
            'sad': ['sad', 'depressed', 'down', 'upset', 'miserable', 'gloomy', 'disappointed', 
                   'heartbroken', 'crying', 'tears', 'lonely', 'hurt', 'devastated'],
            'anxious': ['anxious', 'worried', 'nervous', 'stressed', 'overwhelmed', 'panic', 
                       'fear', 'scared', 'afraid', 'concerned', 'uneasy', 'tense'],
            'angry': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated', 
                     'rage', 'livid', 'outraged', 'hostile'],
            'confused': ['confused', 'lost', 'uncertain', 'unclear', 'puzzled', 'bewildered', 'perplexed'],
            'tired': ['tired', 'exhausted', 'drained', 'weary', 'fatigued', 'worn out'],
            'neutral': ['okay', 'fine', 'normal', 'average', 'regular']
        }
        
        # Define positive and negative emotions
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
            'emotion_type': emotion_type,
            'confidence': confidence,
            'all_scores': scores
        }

class ActivityExtractor:
    """Extracts activities from natural language"""
    
    def __init__(self):
        # Common activity patterns
        self.activity_patterns = [
            r"i went (?:for )?(.+?)(?:,|\.|\s+(?:and|now))",
            r"i (?:did|took|had) (.+?)(?:,|\.|\s+(?:and|now))",
            r"(?:after|before) (.+?)(?:,|\.|\s+(?:and|now|i))",
            r"i (.+?) and (?:now|feel)",
            r"just (.+?) and",
            r"(?:went|did|took|had|tried) (.+?)(?:\s+(?:and|now|which))"
        ]
    
    def extract_activities(self, text):
        """Extract activities mentioned in text"""
        text_lower = text.lower().strip()
        activities = []
        
        for pattern in self.activity_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                activity = match.strip()
                if len(activity) > 2:  # Avoid single words or very short matches
                    # Clean up the activity
                    activity = re.sub(r'\s+', ' ', activity)  # Normalize spaces
                    activities.append(activity)
        
        # Remove duplicates while preserving order
        unique_activities = []
        for activity in activities:
            if activity not in unique_activities and len(activity) > 3:
                unique_activities.append(activity)
        
        return unique_activities

class IntelligentAgent:
    """Intelligent agent that learns and suggests actions using A* search"""
    
    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.activity_extractor = ActivityExtractor()
        
    def process_input(self, text, user_id="default_user"):
        """Process user input and determine appropriate response"""
        # Analyze emotion
        emotion_analysis = self.emotion_analyzer.analyze(text)
        primary_emotion = emotion_analysis['primary_emotion']
        emotion_type = emotion_analysis['emotion_type']
        
        # Extract activities from text
        extracted_activities = self.activity_extractor.extract_activities(text)
        
        # Create experience record
        experience = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'text': text,
            'emotion': primary_emotion,
            'emotion_type': emotion_type,
            'confidence': emotion_analysis['confidence'],
            'timestamp': datetime.datetime.now().isoformat(),
            'all_scores': emotion_analysis['all_scores'],
            'extracted_activities': extracted_activities  # NEW: Store extracted activities
        }
        
        # Store experience
        memory_map["user_experiences"].append(experience)
        
        # Add to emotional states
        if primary_emotion not in memory_map["emotional_states"]:
            memory_map["emotional_states"][primary_emotion] = []
        memory_map["emotional_states"][primary_emotion].append(experience)
        
        # FIXED: Auto-learn from natural language if activities detected and emotion improved
        if extracted_activities and self._is_emotional_improvement(experience):
            self._auto_learn_from_natural_language(experience, extracted_activities)
        
        # Determine response based on emotion type
        if emotion_type == 'positive':
            if extracted_activities:
                # Activities already extracted, learn automatically
                return self._handle_positive_with_activities(experience, extracted_activities)
            else:
                return self._handle_positive_emotion(experience)
        elif emotion_type == 'negative':
            return self._handle_negative_emotion(experience)
        else:
            return self._handle_neutral_emotion(experience)
    
    def _is_emotional_improvement(self, current_experience):
        """Check if current emotion is an improvement from previous emotion"""
        prev_emotion = self._get_previous_emotion(current_experience)
        current_emotion = current_experience['emotion']
        
        if not prev_emotion:
            return False
            
        # Define emotion hierarchy (lower is better)
        emotion_hierarchy = {
            'happy': 1,
            'neutral': 2,
            'confused': 3,
            'tired': 4,
            'sad': 5,
            'anxious': 5,
            'angry': 6
        }
        
        prev_level = emotion_hierarchy.get(prev_emotion, 3)
        current_level = emotion_hierarchy.get(current_emotion, 3)
        
        return current_level < prev_level  # Lower number = better emotion
    
    def _auto_learn_from_natural_language(self, experience, activities):
        """Automatically learn from natural language activity descriptions"""
        prev_emotion = self._get_previous_emotion(experience)
        current_emotion = experience['emotion']
        
        if prev_emotion and prev_emotion != current_emotion:
            transition_key = (prev_emotion, current_emotion)
            if transition_key not in memory_map["transitions"]:
                memory_map["transitions"][transition_key] = []
            
            # Add activities as learned actions
            for activity in activities:
                action_record = {
                    'action': activity,
                    'success_count': 1,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'experience_id': experience['id'],
                    'learned_from': 'natural_language'
                }
                memory_map["transitions"][transition_key].append(action_record)
            
            # Update graph connections
            if current_emotion not in memory_map["graph_connections"][prev_emotion]:
                memory_map["graph_connections"][prev_emotion].append(current_emotion)
    
    def _handle_positive_with_activities(self, experience, activities):
        """Handle positive emotions when activities are already extracted"""
        # Save the activities automatically
        self.save_extracted_activities(experience['id'], activities)
        
        return {
            'type': 'learned_automatically',
            'message': f"Great! I can see you're feeling {experience['emotion']}. I noticed you mentioned: {', '.join(activities)}. I'll remember this for future suggestions!",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'learned_activities': activities,
            'suggestions': []
        }
    
    def _handle_positive_emotion(self, experience):
        """Handle positive emotions - ask for steps taken"""
        return {
            'type': 'ask_for_steps',
            'message': f"That's wonderful! I can see you're feeling {experience['emotion']}. What steps or actions led to this positive feeling? This will help me learn and suggest similar actions to others in the future.",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': []
        }
    
    def _handle_negative_emotion(self, experience):
        """Handle negative emotions - suggest actions using A* search"""
        suggestions = self._find_suggestions_using_astar(experience['emotion'])
        
        return {
            'type': 'suggest_actions',
            'message': f"I understand you're feeling {experience['emotion']}. Based on past successful experiences, here are some suggestions that might help:",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': suggestions
        }
    
    def _handle_neutral_emotion(self, experience):
        """Handle neutral emotions - provide guidance or learned suggestions"""
        # Try to get learned suggestions first
        suggestions = self._find_suggestions_using_astar(experience['emotion'])
        
        if suggestions and any(isinstance(s, str) for s in suggestions):
            return {
                'type': 'learned_suggestions',
                'message': f"I see you're feeling {experience['emotion']}. Based on what worked before, here are some suggestions:",
                'experience_id': experience['id'],
                'emotion': experience['emotion'],
                'suggestions': suggestions
            }
        else:
            return {
                'type': 'general_guidance',
                'message': f"I see you're feeling {experience['emotion']}. Would you like some suggestions to improve your mood, or would you prefer to share what's on your mind?",
                'experience_id': experience['id'],
                'emotion': experience['emotion'],
                'suggestions': [
                    "Try engaging in a hobby you enjoy",
                    "Take a short walk or do light exercise",
                    "Connect with a friend or family member",
                    "Practice gratitude by listing three good things in your life"
                ]
            }
    
    def _find_suggestions_using_astar(self, current_emotion):
        """Use A* search to find best actions from memory map"""
        successful_actions = []
        
        # Search for direct transitions to positive emotions
        for transition_key, actions in memory_map["transitions"].items():
            from_emotion, to_emotion = transition_key
            if (from_emotion == current_emotion and 
                to_emotion in self.emotion_analyzer.positive_emotions):
                # FIXED: Extract action text from action records
                for action_record in actions:
                    if isinstance(action_record, dict) and 'action' in action_record:
                        successful_actions.append(action_record['action'])
                    elif isinstance(action_record, str):
                        successful_actions.append(action_record)
        
        # Also search for transitions from current emotion to better emotions (not just positive)
        if not successful_actions:
            emotion_hierarchy = {
                'happy': 1, 'neutral': 2, 'confused': 3, 'tired': 4, 'sad': 5, 'anxious': 5, 'angry': 6
            }
            current_level = emotion_hierarchy.get(current_emotion, 3)
            
            for transition_key, actions in memory_map["transitions"].items():
                from_emotion, to_emotion = transition_key
                to_level = emotion_hierarchy.get(to_emotion, 3)
                
                if from_emotion == current_emotion and to_level < current_level:
                    # This is an improvement
                    for action_record in actions:
                        if isinstance(action_record, dict) and 'action' in action_record:
                            successful_actions.append(action_record['action'])
                        elif isinstance(action_record, str):
                            successful_actions.append(action_record)
        
        # If no direct transitions, use A* to find path through intermediate emotions
        if not successful_actions:
            successful_actions = self._astar_search_for_actions(current_emotion)
        
        # If still no actions, provide default suggestions
        if not successful_actions:
            successful_actions = self._get_default_suggestions(current_emotion)
        
        # Remove duplicates and return top 3
        unique_actions = []
        for action in successful_actions:
            if action not in unique_actions:
                unique_actions.append(action)
        
        return unique_actions[:3]
    
    def _astar_search_for_actions(self, start_emotion):
        """A* search through emotion graph to find actions leading to positive emotions"""
        target_emotions = self.emotion_analyzer.positive_emotions
        
        # Priority queue: (cost, emotion, path, actions)
        open_set = [(0, start_emotion, [start_emotion], [])]
        closed_set = set()
        
        while open_set:
            cost, current_emotion, path, actions = heapq.heappop(open_set)
            
            if current_emotion in closed_set:
                continue
            
            closed_set.add(current_emotion)
            
            # Check if we reached a target emotion
            if current_emotion in target_emotions:
                return [action for action in actions if isinstance(action, str)]
            
            # Explore neighbors
            for next_emotion in memory_map["graph_connections"][current_emotion]:
                if next_emotion not in closed_set:
                    transition_key = (current_emotion, next_emotion)
                    if transition_key in memory_map["transitions"]:
                        transition_actions = memory_map["transitions"][transition_key]
                        
                        # FIXED: Extract action text from first action record
                        best_action = None
                        if transition_actions:
                            first_action = transition_actions[0]
                            if isinstance(first_action, dict) and 'action' in first_action:
                                best_action = first_action['action']
                            elif isinstance(first_action, str):
                                best_action = first_action
                        
                        if best_action:
                            new_cost = cost + 1
                            new_path = path + [next_emotion]
                            new_actions = actions + [best_action]
                            
                            heapq.heappush(open_set, (new_cost, next_emotion, new_path, new_actions))
        
        return []  # No path found
    
    def _get_default_suggestions(self, emotion):
        """Get default suggestions if no learned actions exist"""
        defaults = {
            'sad': [
                "Listen to uplifting music",
                "Call a friend or family member",
                "Take a warm bath or shower"
            ],
            'anxious': [
                "Practice deep breathing exercises",
                "Try the 5-4-3-2-1 grounding technique",
                "Go for a short walk"
            ],
            'angry': [
                "Count to 10 slowly",
                "Write down your feelings",
                "Do some physical exercise"
            ],
            'confused': [
                "Break down the problem into smaller parts",
                "Talk to someone you trust",
                "Take some time to reflect"
            ],
            'tired': [
                "Take a short nap if possible",
                "Drink some water",
                "Get some fresh air"
            ],
            'neutral': [
                "Try something that made you happy before",
                "Take a short walk",
                "Do a small activity you enjoy"
            ]
        }
        return defaults.get(emotion, ["Take a moment to breathe and be kind to yourself"])
    
    def save_successful_steps(self, experience_id, steps):
        """Save steps that led to positive emotion"""
        experience = None
        for exp in memory_map["user_experiences"]:
            if exp['id'] == experience_id:
                experience = exp
                break
        
        if not experience:
            return False
        
        prev_emotion = self._get_previous_emotion(experience)
        current_emotion = experience['emotion']
        
        if prev_emotion and prev_emotion != current_emotion:
            transition_key = (prev_emotion, current_emotion)
            if transition_key not in memory_map["transitions"]:
                memory_map["transitions"][transition_key] = []
            
            # Add each step as an action
            for step in steps:
                action_record = {
                    'action': step,
                    'success_count': 1,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'experience_id': experience_id
                }
                memory_map["transitions"][transition_key].append(action_record)
            
            # Update graph connections
            if current_emotion not in memory_map["graph_connections"][prev_emotion]:
                memory_map["graph_connections"][prev_emotion].append(current_emotion)
        
        experience['successful_steps'] = steps
        return True
    
    def save_extracted_activities(self, experience_id, activities):
        """Save automatically extracted activities"""
        return self.save_successful_steps(experience_id, activities)
    
    def _get_previous_emotion(self, current_experience):
        """Find the most recent different emotion before current experience"""
        current_time = datetime.datetime.fromisoformat(current_experience['timestamp'])
        
        for exp in reversed(memory_map["user_experiences"]):
            exp_time = datetime.datetime.fromisoformat(exp['timestamp'])
            if (exp_time < current_time and 
                exp['emotion'] != current_experience['emotion'] and
                exp['user_id'] == current_experience['user_id']):
                return exp['emotion']
        
        return None
    
    def get_memory_map_data(self):
        """Get current memory map for visualization"""
        nodes = []
        edges = []
        
        # Create nodes for each emotion with experience count
        for emotion, experiences in memory_map["emotional_states"].items():
            nodes.append({
                'id': emotion,
                'label': emotion.title(),
                'count': len(experiences),
                'type': 'positive' if emotion in self.emotion_analyzer.positive_emotions else 
                       'negative' if emotion in self.emotion_analyzer.negative_emotions else 'neutral'
            })
        
        # Create edges for transitions
        for (from_emotion, to_emotion), actions in memory_map["transitions"].items():
            edges.append({
                'from': from_emotion,
                'to': to_emotion,
                'actions': len(actions),
                'weight': len(actions)
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_experiences': len(memory_map["user_experiences"]),
            'total_transitions': len(memory_map["transitions"])
        }

# Initialize the intelligent agent
agent = IntelligentAgent()

# API Routes (unchanged)
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Intelligent Agent with Memory Map - FIXED",
        "memory_stats": {
            "total_experiences": len(memory_map["user_experiences"]),
            "emotional_states": len(memory_map["emotional_states"]),
            "learned_transitions": len(memory_map["transitions"])
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

@app.route('/api/save-steps', methods=['POST', 'OPTIONS'])
def save_steps():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        experience_id = data.get('experience_id', '')
        steps = data.get('steps', [])
        
        if not experience_id or not steps:
            return jsonify({"error": "Experience ID and steps are required"}), 400
        
        success = agent.save_successful_steps(experience_id, steps)
        
        if success:
            return jsonify({
                "message": "Steps saved successfully! I'll remember these for future suggestions.",
                "saved_steps": steps
            })
        else:
            return jsonify({"error": "Failed to save steps"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to save steps: {str(e)}"}), 500

@app.route('/api/memory-map', methods=['GET'])
def get_memory_map():
    try:
        map_data = agent.get_memory_map_data()
        return jsonify(map_data)
    except Exception as e:
        return jsonify({"error": f"Failed to get memory map: {str(e)}"}), 500

@app.route('/api/memory-stats', methods=['GET'])
def get_memory_stats():
    try:
        stats = {
            "total_experiences": len(memory_map["user_experiences"]),
            "emotions_learned": len(memory_map["emotional_states"]),
            "transitions_learned": len(memory_map["transitions"]),
            "recent_experiences": memory_map["user_experiences"][-5:] if memory_map["user_experiences"] else []
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500

@app.route('/api/reset-memory', methods=['POST', 'OPTIONS'])
def reset_memory():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        memory_map["emotional_states"].clear()
        memory_map["transitions"].clear()
        memory_map["user_experiences"].clear()
        memory_map["graph_connections"].clear()
        memory_map["activity_patterns"].clear()
        
        return jsonify({"message": "Memory map reset successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to reset memory: {str(e)}"}), 500

if __name__ == '__main__':
    print("🤖 Starting FIXED Intelligent Agent with Memory Map")
    print("🧠 Features: Emotion Analysis + A* Search + Natural Language Learning")
    print("📡 API: http://localhost:5000")
    print("🗺️  Memory Map: Growing with each interaction")
    print("✅ FIXES: Better emotion classification + Activity extraction + Learning logic")
    app.run(host='0.0.0.0', port=5000, debug=True)