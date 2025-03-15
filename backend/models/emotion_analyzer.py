import random
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """
    Enhanced EmotionAnalyzer that can use a pre-trained model for emotion detection.
    Falls back to rule-based detection if dependencies are not available.
    """
    
    def __init__(self, use_pretrained=True):
        """
        Initialize the EmotionAnalyzer.
        
        Args:
            use_pretrained (bool): Whether to use a pre-trained model
        """
        # Define emotion labels
        self.emotion_labels = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
        self.positive_emotions = ['joy', 'surprise']
        self.use_pretrained = use_pretrained
        self.model = None
        self.tokenizer = None
        
        # Try to initialize the pre-trained model if requested
        if use_pretrained:
            try:
                from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
                
                # Check if we should use CPU or GPU
                device = -1  # CPU by default
                
                # Load emotion classification pipeline
                try:
                    logger.info("Loading emotion classification model...")
                    self.pipeline = pipeline(
                        "text-classification", 
                        model="j-hartmann/emotion-english-distilroberta-base", 
                        top_k=None,
                        device=device
                    )
                    logger.info("Emotion classification model loaded successfully")
                    self.using_pretrained = True
                except Exception as e:
                    logger.warning(f"Failed to load pre-trained model: {str(e)}")
                    logger.warning("Falling back to rule-based emotion detection")
                    self.using_pretrained = False
            except ImportError:
                logger.warning("Transformers library not found. Falling back to rule-based emotion detection")
                self.using_pretrained = False
        else:
            self.using_pretrained = False
            
        logger.info(f"EmotionAnalyzer initialized with pretrained={self.using_pretrained}")
        
    def analyze(self, text):
        """
        Analyze the emotion in the given text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: A dictionary containing emotion analysis results
        """
        if self.using_pretrained:
            try:
                return self._analyze_with_model(text)
            except Exception as e:
                logger.error(f"Error using pre-trained model: {str(e)}")
                logger.info("Falling back to rule-based emotion detection")
                return self._analyze_rule_based(text)
        else:
            return self._analyze_rule_based(text)
    
    def _analyze_with_model(self, text):
        """
        Analyze emotion using the pre-trained model.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: A dictionary containing emotion analysis results
        """
        # Get predictions from the model
        results = self.pipeline(text)
        
        # Extract emotion scores
        emotion_scores = {}
        for result in results[0]:
            label = result['label']
            score = result['score']
            # Map model labels to our standard labels if needed
            if label == 'LABEL_0':
                label = 'anger'
            elif label == 'LABEL_1':
                label = 'disgust'
            elif label == 'LABEL_2':
                label = 'fear'
            elif label == 'LABEL_3':
                label = 'joy'
            elif label == 'LABEL_4':
                label = 'neutral'
            elif label == 'LABEL_5':
                label = 'sadness'
            elif label == 'LABEL_6':
                label = 'surprise'
            
            emotion_scores[label] = float(score)
        
        # Find the primary emotion (highest score)
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # Create emotion data dictionary
        emotion_data = {
            'primary_emotion': primary_emotion,
            'emotion_scores': emotion_scores,
            'is_positive': primary_emotion in self.positive_emotions,
            'detection_method': 'pretrained_model'
        }
        
        return emotion_data
    
    def _analyze_rule_based(self, text):
        """
        Analyze emotion using rule-based detection.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: A dictionary containing emotion analysis results
        """
        # Simple keyword-based emotion detection for demo purposes
        text_lower = text.lower()
        
        # Determine primary emotion based on simple keyword matching
        if any(word in text_lower for word in ['happy', 'glad', 'joy', 'exciting', 'wonderful', 'delighted', 'pleased']):
            primary_emotion = 'joy'
        elif any(word in text_lower for word in ['sad', 'upset', 'unhappy', 'depressed', 'miserable', 'gloomy', 'heartbroken']):
            primary_emotion = 'sadness'
        elif any(word in text_lower for word in ['angry', 'mad', 'furious', 'annoyed', 'irritated', 'enraged', 'frustrated']):
            primary_emotion = 'anger'
        elif any(word in text_lower for word in ['afraid', 'scared', 'worried', 'anxious', 'terrified', 'nervous', 'fearful']):
            primary_emotion = 'fear'
        elif any(word in text_lower for word in ['surprised', 'shocked', 'amazed', 'astonished', 'stunned']):
            primary_emotion = 'surprise'
        elif any(word in text_lower for word in ['disgusted', 'gross', 'repulsed', 'revolted', 'appalled']):
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
            'is_positive': primary_emotion in self.positive_emotions,
            'detection_method': 'rule_based'
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
