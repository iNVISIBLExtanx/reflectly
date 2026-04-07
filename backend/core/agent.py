import datetime
import uuid
from collections import defaultdict

from .emotion_analyzer import EmotionAnalyzer, ActivityExtractor
from .pathfinding import PathfindingComparator


# Shared in-memory store (imported by app.py routes too)
memory_map = {
    "emotional_states": {},
    "transitions": {},
    "user_experiences": [],
    "graph_connections": defaultdict(list),
    "algorithm_comparisons": []
}


class IntelligentAgent:
    DEFAULT_SUGGESTIONS = {
        'sad': ["Listen to uplifting music", "Call a friend", "Take a warm bath"],
        'anxious': ["Practice deep breathing", "Try grounding techniques", "Go for a walk"],
        'angry': ["Count to 10", "Write down feelings", "Do exercise"],
        'confused': ["Break down the problem", "Talk to someone", "Take time to reflect"],
        'tired': ["Take a short nap", "Drink water", "Get fresh air"],
        'neutral': ["Try something enjoyable", "Take a walk", "Practice gratitude"]
    }

    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.activity_extractor = ActivityExtractor()
        self.pathfinding_comparator = PathfindingComparator(memory_map)

    def process_input(self, text, user_id="default_user"):
        analysis = self.emotion_analyzer.analyze(text)
        activities = self.activity_extractor.extract_activities(text)

        experience = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'text': text,
            'emotion': analysis['primary_emotion'],
            'emotion_type': analysis['emotion_type'],
            'confidence': analysis['confidence'],
            'timestamp': datetime.datetime.now().isoformat(),
            'extracted_activities': activities
        }

        memory_map["user_experiences"].append(experience)
        memory_map["emotional_states"].setdefault(analysis['primary_emotion'], []).append(experience)

        if activities:
            self._auto_learn_from_experience(experience, activities)

        if analysis['emotion_type'] == 'positive':
            return self._handle_positive_emotion(experience)
        elif analysis['emotion_type'] == 'negative':
            return self._handle_negative_emotion(experience)
        else:
            return self._handle_neutral_emotion(experience)

    def _auto_learn_from_experience(self, experience, activities):
        prev = self._get_previous_emotion(experience)
        if prev and prev != experience['emotion']:
            self._save_transition(prev, experience['emotion'], activities, experience['id'])

    def _save_transition(self, from_emotion, to_emotion, activities, experience_id):
        key = (from_emotion, to_emotion)
        memory_map["transitions"].setdefault(key, [])
        for activity in activities:
            memory_map["transitions"][key].append({
                'action': activity,
                'success_count': 1,
                'timestamp': datetime.datetime.now().isoformat(),
                'experience_id': experience_id
            })
        if to_emotion not in memory_map["graph_connections"][from_emotion]:
            memory_map["graph_connections"][from_emotion].append(to_emotion)

    def _get_previous_emotion(self, current_experience):
        current_time = datetime.datetime.fromisoformat(current_experience['timestamp'])
        for exp in reversed(memory_map["user_experiences"]):
            exp_time = datetime.datetime.fromisoformat(exp['timestamp'])
            if (exp_time < current_time
                    and exp['emotion'] != current_experience['emotion']
                    and exp['user_id'] == current_experience['user_id']):
                return exp['emotion']
        return None

    def _handle_positive_emotion(self, experience):
        return {
            'type': 'ask_for_steps',
            'message': f"That's wonderful! What steps led to this {experience['emotion']} feeling?",
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': []
        }

    def _handle_negative_emotion(self, experience):
        comparison = self.pathfinding_comparator.compare_algorithms(experience['emotion'], 'happy')
        memory_map["algorithm_comparisons"].append(comparison)

        winner = comparison['winner']
        if winner['algorithm'] != 'None':
            path = comparison['results'][winner['algorithm']]['path']
            suggestions = self._path_to_suggestions(path)
            message = (f"I understand you're feeling {experience['emotion']}. "
                       f"I used {winner['algorithm']} (found path in {winner['time_ms']:.1f}ms):")
        else:
            suggestions = self.DEFAULT_SUGGESTIONS.get(experience['emotion'], ["Be kind to yourself"])
            message = f"I understand you're feeling {experience['emotion']}. Here are some suggestions:"

        return {
            'type': 'suggest_actions_with_algorithm',
            'message': message,
            'experience_id': experience['id'],
            'emotion': experience['emotion'],
            'suggestions': suggestions,
            'algorithm_used': winner['algorithm'],
            'algorithm_performance': winner,
            'comparison_details': comparison
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
        suggestions = []
        for i in range(len(path) - 1):
            key = (path[i], path[i + 1])
            if key in memory_map["transitions"]:
                actions = memory_map["transitions"][key]
                if actions:
                    best = max(actions, key=lambda x: x.get('success_count', 1))
                    suggestions.append(best['action'])
        if not suggestions:
            suggestions = self.DEFAULT_SUGGESTIONS.get(path[0] if path else 'neutral',
                                                        ["Be kind to yourself"])
        return suggestions[:3]
