import random

class EmotionAnalyzer:
    """
    Mock implementation of the EmotionAnalyzer for development without ML dependencies.
    """
    
    def __init__(self):
        # Define emotion labels
        self.emotion_labels = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
        self.positive_emotions = ['joy', 'surprise']
        
    def analyze(self, text):
        """
        Analyze the emotion in the given text (mock implementation).
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: A dictionary containing emotion analysis results
        """
        # Simple keyword-based emotion detection for demo purposes
        text_lower = text.lower()
        
        # Determine primary emotion based on simple keyword matching
        if any(word in text_lower for word in ['happy', 'glad', 'joy', 'exciting', 'wonderful']):
            primary_emotion = 'joy'
        elif any(word in text_lower for word in ['sad', 'upset', 'unhappy', 'depressed']):
            primary_emotion = 'sadness'
        elif any(word in text_lower for word in ['angry', 'mad', 'furious', 'annoyed']):
            primary_emotion = 'anger'
        elif any(word in text_lower for word in ['afraid', 'scared', 'worried', 'anxious']):
            primary_emotion = 'fear'
        elif any(word in text_lower for word in ['surprised', 'shocked', 'amazed']):
            primary_emotion = 'surprise'
        elif any(word in text_lower for word in ['disgusted', 'gross', 'repulsed']):
            primary_emotion = 'disgust'
        else:
            primary_emotion = 'neutral'
        
        # Generate random scores for each emotion, with the primary emotion having the highest score
        emotion_scores = {}
        for emotion in self.emotion_labels:
            if emotion == primary_emotion:
                emotion_scores[emotion] = random.uniform(0.7, 0.9)
            else:
                emotion_scores[emotion] = random.uniform(0.0, 0.3)
        
        # Normalize scores
        total = sum(emotion_scores.values())
        for emotion in emotion_scores:
            emotion_scores[emotion] = emotion_scores[emotion] / total
        
        # Create emotion data dictionary
        emotion_data = {
            'primary_emotion': primary_emotion,
            'emotion_scores': emotion_scores,
            'is_positive': primary_emotion in self.positive_emotions
        }
        
        return emotion_data
    
    def _is_positive_emotion(self, emotion):
        """
        Determine if the given emotion is positive.
        
        Args:
            emotion (str): The emotion to check
            
        Returns:
            bool: True if the emotion is positive, False otherwise
        """
        return emotion in self.positive_emotions
