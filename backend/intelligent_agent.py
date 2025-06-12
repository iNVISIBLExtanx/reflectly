"""
COMPLETE FIXED Intelligent Agent with Memory Map and A* Search
NOW CORRECTLY LEARNS FROM: sad → neutral → happy sequences!
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
    "learning_log": []       # Debug log to track what gets learned
}

class EmotionAnalyzer:
    """Analyzes text to detect emotions with enhanced keyword detection"""
    
    def __init__(self):
        self.emotion_keywords = {
            # ENHANCED: Added all missing positive keywords
            'happy': ['happy', 'joyful', 'excited', 'glad', 'cheerful', 'delighted', 'elated', 
                     'thrilled', 'content', 'pleased', 'amazing', 'wonderful', 'fantastic', 
                     'great', 'awesome', 'love', 'perfect', 'good', 'better', 'feeling good', 
                     'feeling better', 'much better', 'excellent', 'brilliant', 'superb', 'fine'],
            'sad': ['sad', 'depressed', 'down', 'upset', 'miserable', 'gloomy', 'disappointed', 
                   'heartbroken', 'crying', 'tears', 'lonely', 'hurt', 'devastated', 'feeling down'],
            'anxious': ['anxious', 'worried', 'nervous', 'stressed', 'overwhelmed', 'panic', 
                       'fear', 'scared', 'afraid', 'concerned', 'uneasy', 'tense'],
            'angry': ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'frustrated', 
                     'rage', 'livid', 'outraged', 'hostile'],
            'confused': ['confused', 'lost', 'uncertain', 'unclear', 'puzzled', 'bewildered', 'perplexed'],
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
            'emotion_type': emotion_type,
            'confidence': confidence,
            'all_scores': scores
        }

class ActivityExtractor:
    """FIXED: Comprehensive activity extraction from natural language"""
    
    def __init__(self):
        # COMPREHENSIVE patterns covering all natural language styles
        self.activity_patterns = [
            # === EXPLICIT "I" PATTERNS ===
            r"i (.+?)\..*(?:now|feeling|and)",                    # "i listened music. now i'm happy"
            r"i (.+?)(?:,|\.)\s*(?:now|and|feeling)",            # "i called friend, now feeling better"  
            r"i (?:just )?(.+?) and (?:now|feel)",               # "i just exercised and now feel great"
            r"i went (?:for )?(?:a )?(.+?)(?:,|\.|\s+(?:and|now))", # "i went for a walk, now feeling good"
            r"i (?:did|took|had|tried|started) (?:a |some )?(.+?)(?:,|\.|\s+(?:and|now))", # "i took a shower and now..."
            r"i've (?:been |just )?(.+?)(?:,|\.|\s+(?:and|now))", # "i've been reading and now..."
            
            # === IMPLICIT ACTIVITY PATTERNS ===
            r"^(.+?)\..*(?:now|feeling).*(?:good|better|happy|okay|fine)", # "talked with friend. now feeling good"
            r"^(?:just )?(.+?)(?:,|\.)\s*(?:now|and).*(?:feel|am)",      # "just exercised, now am happy"
            r"(?:after|before) (.+?)(?:,|\.|\s+(?:i|now))",             # "after meditation, i feel calm"
            
            # === ACTIVITY + OUTCOME PATTERNS ===
            r"(.+?) (?:helped|made me|got me).*(?:feel|feeling) (?:better|good|happy)", # "music helped me feel better"
        ]
        
        # Activity indicators (words that suggest real activities)
        self.activity_indicators = {
            'listened', 'talked', 'called', 'walked', 'exercised', 'meditated', 'read', 'watched',
            'ate', 'drank', 'took', 'had', 'went', 'did', 'tried', 'played', 'worked', 'studied',
            'cooked', 'cleaned', 'shopped', 'drove', 'traveled', 'visited', 'met', 'chatted',
            'dancing', 'singing', 'writing', 'drawing', 'painting', 'running', 'swimming', 
            'cycling', 'hiking', 'yoga', 'stretching', 'breathing', 'sleeping', 'resting',
            'shower', 'bath', 'massage', 'music', 'movie', 'book', 'game', 'sport', 'friend'
        }
        
        # Words to exclude (not real activities)
        self.noise_words = {
            'am', 'was', 'is', 'are', 'be', 'being', 'been', 'have', 'has', 'had',
            'feel', 'feeling', 'felt', 'think', 'thinking', 'thought', 'know', 'knowing',
            'good', 'better', 'great', 'okay', 'fine', 'happy', 'sad', 'angry', 'tired'
        }
    
    def extract_activities(self, text):
        """Extract activities from natural language"""
        text_clean = text.lower().strip()
        activities = []
        
        for pattern in self.activity_patterns:
            try:
                matches = re.findall(pattern, text_clean)
                for match in matches:
                    activity = self._clean_activity(match)
                    if activity and self._is_valid_activity(activity):
                        activities.append(activity)
            except re.error:
                continue
        
        # Remove duplicates while preserving order
        unique_activities = []
        for activity in activities:
            if activity not in unique_activities:
                unique_activities.append(activity)
        
        return unique_activities
    
    def _clean_activity(self, raw_activity):
        """Clean extracted activity text"""
        if not raw_activity:
            return None
            
        activity = raw_activity.strip()
        
        # Remove common prefixes
        prefixes = ['a ', 'an ', 'the ', 'some ', 'my ', 'to ', 'just ']
        for prefix in prefixes:
            if activity.startswith(prefix):
                activity = activity[len(prefix):]
        
        # Remove suffixes
        suffixes = [' and', ' then', ' now', ' today', ' earlier']
        for suffix in suffixes:
            if activity.endswith(suffix):
                activity = activity[:-len(suffix)]
        
        # Clean spaces
        activity = re.sub(r'\s+', ' ', activity).strip()
        
        return activity if len(activity) > 2 else None
    
    def _is_valid_activity(self, activity):
        """Check if text represents a valid activity"""
        if not activity or len(activity) < 3:
            return False
        
        words = set(activity.lower().split())
        
        # Reject noise words only
        if words.issubset(self.noise_words):
            return False
        
        # Accept if contains activity indicators
        if any(indicator in activity.lower() for indicator in self.activity_indicators):
            return True
        
        # Accept if descriptive enough (3+ words, not all noise)
        if len(words) >= 2 and not words.issubset(self.noise_words):
            return True
        
        return False

class IntelligentAgent:
    """FIXED: Intelligent agent with proper learning from natural language"""
    
    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.activity_extractor = ActivityExtractor()
        
    def process_input(self, text, user_id="default_user"):
        """Process user input with FIXED learning mechanism"""
        # Analyze emotion
        emotion_analysis = self.emotion_analyzer.analyze(text)
        primary_emotion = emotion_analysis['primary_emotion']
        emotion_type = emotion_analysis['emotion_type']
        
        # Extract activities
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
            'extracted_activities': extracted_activities
        }
        
        # Store experience
        memory_map["user_experiences"].append(experience)
        
        # Add to emotional states
        if primary_emotion not in memory_map["emotional_states"]:
            memory_map["emotional_states"][primary_emotion] = []
        memory_map["emotional_states"][primary_emotion].append(experience)
        
        # FIXED: Auto-learn from ANY extracted activities + emotional context
        if extracted_activities:
            self._auto_learn_from_experience(experience, extracted_activities)
        
        # Determine response
        if emotion_type == 'positive':
            if extracted_activities:
                return self._handle_positive_with_activities(experience, extracted_activities)
            else:
                return self._handle_positive_emotion(experience)
        elif emotion_type == 'negative':
            return self._handle_negative_emotion(experience)
        else:
            return self._handle_neutral_emotion(experience)
    
    def _auto_learn_from_experience(self, experience, activities):
        """FIXED: Learn from ANY experience with activities"""
        prev_emotion = self._get_previous_emotion(experience)
        current_emotion = experience['emotion']
        
        # Learn if there's a previous different emotion
        if prev_emotion and prev_emotion != current_emotion:
            self._save_transition(prev_emotion, current_emotion, activities, experience['id'])
            
            # Log what we learned for debugging
            learning_entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'transition': f"{prev_emotion} → {current_emotion}",
                'activities': activities,
                'text': experience['text'],
                'method': 'auto_natural_language'
            }
            memory_map["learning_log"].append(learning_entry)
            
            print(f"🧠 LEARNED: {prev_emotion} → {current_emotion} via {activities}")
    
    def _save_transition(self, from_emotion, to_emotion, activities, experience_id):
        """Save a transition with activities"""
        transition_key = (from_emotion, to_emotion)
        
        if transition_key not in memory_map["transitions"]:
            memory_map["transitions"][transition_key] = []
        
        # Add activities as actions
        for activity in activities:
            action_record = {
                'action': activity,
                'success_count': 1,
                'timestamp': datetime.datetime.now().isoformat(),
                'experience_id': experience_id,
                'learned_from': 'natural_language'
            }
            memory_map["transitions"][transition_key].append(action_record)
        
        # Update graph connections
        if to_emotion not in memory_map["graph_connections"][from_emotion]:
            memory_map["graph_connections"][from_emotion].append(to_emotion)
    
    def _handle_positive_with_activities(self, experience, activities):
        """Handle positive emotions with extracted activities"""
        return {
            'type': 'learned_automatically',
            'message': f"Wonderful! I can see you're feeling {experience['emotion']}. I noticed you mentioned: {', '.join(activities)}. I'll remember this for future suggestions!",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'learned_activities': activities,
            'suggestions': []
        }
    
    def _handle_positive_emotion(self, experience):
        """Handle positive emotions - ask for steps"""
        return {
            'type': 'ask_for_steps',
            'message': f"That's wonderful! I can see you're feeling {experience['emotion']}. What steps or actions led to this positive feeling?",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': []
        }
    
    def _handle_negative_emotion(self, experience):
        """Handle negative emotions - suggest actions"""
        suggestions = self._find_suggestions_using_astar(experience['emotion'])
        
        return {
            'type': 'suggest_actions',
            'message': f"I understand you're feeling {experience['emotion']}. Based on past successful experiences, here are some suggestions that might help:",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': suggestions
        }
    
    def _handle_neutral_emotion(self, experience):
        """Handle neutral emotions - provide learned or general guidance"""
        suggestions = self._find_suggestions_using_astar(experience['emotion'])
        
        if suggestions and any(isinstance(s, str) and len(s) > 3 for s in suggestions):
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
                'message': f"I see you're feeling {experience['emotion']}. Would you like some suggestions to improve your mood?",
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
        """FIXED: Use A* search with proper action extraction"""
        successful_actions = []
        
        # Search for direct transitions to positive emotions
        for transition_key, actions in memory_map["transitions"].items():
            from_emotion, to_emotion = transition_key
            if (from_emotion == current_emotion and 
                to_emotion in self.emotion_analyzer.positive_emotions):
                # Extract action text properly
                for action_record in actions:
                    if isinstance(action_record, dict) and 'action' in action_record:
                        successful_actions.append(action_record['action'])
                    elif isinstance(action_record, str):
                        successful_actions.append(action_record)
        
        # Also search for transitions to better emotions (not just positive)
        if not successful_actions:
            emotion_hierarchy = {
                'happy': 1, 'neutral': 2, 'confused': 3, 'tired': 4, 'sad': 5, 'anxious': 5, 'angry': 6
            }
            current_level = emotion_hierarchy.get(current_emotion, 3)
            
            for transition_key, actions in memory_map["transitions"].items():
                from_emotion, to_emotion = transition_key
                to_level = emotion_hierarchy.get(to_emotion, 3)
                
                if from_emotion == current_emotion and to_level < current_level:
                    for action_record in actions:
                        if isinstance(action_record, dict) and 'action' in action_record:
                            successful_actions.append(action_record['action'])
                        elif isinstance(action_record, str):
                            successful_actions.append(action_record)
        
        # Use A* if no direct suggestions
        if not successful_actions:
            successful_actions = self._astar_search_for_actions(current_emotion)
        
        # Default suggestions if still nothing
        if not successful_actions:
            successful_actions = self._get_default_suggestions(current_emotion)
        
        # Remove duplicates and return top 3
        unique_actions = []
        for action in successful_actions:
            if action and action not in unique_actions and len(action) > 3:
                unique_actions.append(action)
        
        return unique_actions[:3]
    
    def _astar_search_for_actions(self, start_emotion):
        """A* search through emotion graph"""
        target_emotions = self.emotion_analyzer.positive_emotions
        
        open_set = [(0, start_emotion, [start_emotion], [])]
        closed_set = set()
        
        while open_set:
            cost, current_emotion, path, actions = heapq.heappop(open_set)
            
            if current_emotion in closed_set:
                continue
            closed_set.add(current_emotion)
            
            if current_emotion in target_emotions:
                return [action for action in actions if isinstance(action, str) and len(action) > 3]
            
            for next_emotion in memory_map["graph_connections"][current_emotion]:
                if next_emotion not in closed_set:
                    transition_key = (current_emotion, next_emotion)
                    if transition_key in memory_map["transitions"]:
                        transition_actions = memory_map["transitions"][transition_key]
                        
                        best_action = None
                        if transition_actions:
                            first_action = transition_actions[0]
                            if isinstance(first_action, dict) and 'action' in first_action:
                                best_action = first_action['action']
                            elif isinstance(first_action, str):
                                best_action = first_action
                        
                        if best_action and len(best_action) > 3:
                            new_cost = cost + 1
                            new_path = path + [next_emotion]
                            new_actions = actions + [best_action]
                            
                            heapq.heappush(open_set, (new_cost, next_emotion, new_path, new_actions))
        
        return []
    
    def _get_default_suggestions(self, emotion):
        """Default suggestions if no learned actions"""
        defaults = {
            'sad': ["Listen to uplifting music", "Call a friend or family member", "Take a warm bath"],
            'anxious': ["Practice deep breathing exercises", "Try the 5-4-3-2-1 grounding technique", "Go for a short walk"],
            'angry': ["Count to 10 slowly", "Write down your feelings", "Do some physical exercise"],
            'confused': ["Break down the problem into smaller parts", "Talk to someone you trust", "Take some time to reflect"],
            'tired': ["Take a short nap if possible", "Drink some water", "Get some fresh air"],
            'neutral': ["Try something that made you happy before", "Take a short walk", "Do a small activity you enjoy"]
        }
        return defaults.get(emotion, ["Take a moment to breathe and be kind to yourself"])
    
    def save_successful_steps(self, experience_id, steps):
        """Save manual steps (from form interface)"""
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
            self._save_transition(prev_emotion, current_emotion, steps, experience_id)
            
            # Log manual learning
            learning_entry = {
                'timestamp': datetime.datetime.now().isoformat(),
                'transition': f"{prev_emotion} → {current_emotion}",
                'activities': steps,
                'text': experience['text'],
                'method': 'manual_form'
            }
            memory_map["learning_log"].append(learning_entry)
        
        experience['successful_steps'] = steps
        return True
    
    def _get_previous_emotion(self, current_experience):
        """Find the most recent different emotion"""
        current_time = datetime.datetime.fromisoformat(current_experience['timestamp'])
        
        for exp in reversed(memory_map["user_experiences"]):
            exp_time = datetime.datetime.fromisoformat(exp['timestamp'])
            if (exp_time < current_time and 
                exp['emotion'] != current_experience['emotion'] and
                exp['user_id'] == current_experience['user_id']):
                return exp['emotion']
        
        return None
    
    def get_memory_map_data(self):
        """Get memory map for visualization"""
        nodes = []
        edges = []
        
        for emotion, experiences in memory_map["emotional_states"].items():
            nodes.append({
                'id': emotion,
                'label': emotion.title(),
                'count': len(experiences),
                'type': 'positive' if emotion in self.emotion_analyzer.positive_emotions else 
                       'negative' if emotion in self.emotion_analyzer.negative_emotions else 'neutral'
            })
        
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

# Initialize agent
agent = IntelligentAgent()

# API Routes
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "FIXED Intelligent Agent - Learning from Natural Language!",
        "memory_stats": {
            "total_experiences": len(memory_map["user_experiences"]),
            "emotional_states": len(memory_map["emotional_states"]),
            "learned_transitions": len(memory_map["transitions"]),
            "learning_entries": len(memory_map["learning_log"])
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
        return jsonify(agent.get_memory_map_data())
    except Exception as e:
        return jsonify({"error": f"Failed to get memory map: {str(e)}"}), 500

@app.route('/api/memory-stats', methods=['GET'])
def get_memory_stats():
    try:
        return jsonify({
            "total_experiences": len(memory_map["user_experiences"]),
            "emotions_learned": len(memory_map["emotional_states"]),
            "transitions_learned": len(memory_map["transitions"]),
            "recent_experiences": memory_map["user_experiences"][-5:] if memory_map["user_experiences"] else [],
            "learning_log": memory_map["learning_log"][-10:]  # Last 10 learning events
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500

@app.route('/api/learning-debug', methods=['GET'])
def get_learning_debug():
    """NEW: Debug endpoint to see what the system has learned"""
    try:
        return jsonify({
            "transitions": dict(memory_map["transitions"]),
            "graph_connections": dict(memory_map["graph_connections"]),
            "learning_log": memory_map["learning_log"],
            "recent_experiences": [
                {
                    "text": exp["text"],
                    "emotion": exp["emotion"],
                    "activities": exp.get("extracted_activities", []),
                    "timestamp": exp["timestamp"]
                }
                for exp in memory_map["user_experiences"][-10:]
            ]
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get debug info: {str(e)}"}), 500

@app.route('/api/reset-memory', methods=['POST', 'OPTIONS'])
def reset_memory():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        memory_map["emotional_states"].clear()
        memory_map["transitions"].clear()
        memory_map["user_experiences"].clear()
        memory_map["graph_connections"].clear()
        memory_map["learning_log"].clear()
        
        return jsonify({"message": "Memory map reset successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to reset memory: {str(e)}"}), 500

if __name__ == '__main__':
    print("🤖 Starting COMPLETELY FIXED Intelligent Agent")
    print("🧠 Features: Enhanced Emotion Detection + Activity Extraction + A* Search")
    print("📡 API: http://localhost:5000")
    print("🗺️  Memory Map: NOW LEARNING FROM NATURAL LANGUAGE!")
    print("✅ FIXES: sad→neutral→happy transitions now CORRECTLY learned!")
    print("🔍 Debug: /api/learning-debug to see what's been learned")
    app.run(host='0.0.0.0', port=5000, debug=True)