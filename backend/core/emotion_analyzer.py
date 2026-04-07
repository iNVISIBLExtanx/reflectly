import re


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
        text_lower = text.lower()
        scores = {emotion: sum(1 for kw in kws if kw in text_lower)
                  for emotion, kws in self.emotion_keywords.items()}

        if not any(scores.values()):
            primary_emotion = 'neutral'
            confidence = 0.5
        else:
            primary_emotion = max(scores, key=scores.get)
            total = sum(scores.values())
            confidence = scores[primary_emotion] / total if total > 0 else 0.5

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


class ActivityExtractor:
    def __init__(self):
        self.activity_patterns = [
            r"(?:I|we)\s+(?:did|tried|enjoyed|attempted)\s+([\w\s]+)",
            r"(?:did|tried|enjoyed|attempted)\s+([\w\s]+)",
            r"(?:I|we)\s+(?:went|visited)\s+([\w\s]+)",
            r"(?:spent time|relaxed)\s+([\w\s]+)"
        ]

    def extract_activities(self, text):
        activities = []
        for pattern in self.activity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            activities.extend([m.strip() for m in matches if m.strip()])
        return activities
