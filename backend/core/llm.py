"""
LLM-Based Emotion Analyzer using Ollama
Replaces regex-based emotion detection with intelligent LLM analysis
Falls back to regex if LLM is unavailable
"""

import json
import logging
import re
import time
from typing import Dict, Optional, List
from datetime import datetime

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama not installed. LLM features will be disabled.")

from config import LLMConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMEmotionAnalyzer:
    """
    Advanced emotion analyzer using local LLM (Ollama)
    with regex fallback for robustness
    """
    
    def __init__(self):
        """Initialize the LLM emotion analyzer"""
        self.llm_enabled = LLMConfig.LLM_ENABLED and OLLAMA_AVAILABLE
        self.primary_model = LLMConfig.PRIMARY_MODEL
        self.fallback_models = LLMConfig.FALLBACK_MODELS
        
        # Performance tracking
        self.stats = {
            'total_analyses': 0,
            'llm_successes': 0,
            'llm_failures': 0,
            'regex_fallbacks': 0,
            'avg_llm_time_ms': 0,
            'model_used': {}
        }
        
        # Regex-based analyzer as fallback
        self.regex_analyzer = RegexEmotionAnalyzer()
        
        # Check if Ollama is available
        if self.llm_enabled:
            self._check_ollama_connection()
        else:
            logger.info("LLM disabled or unavailable. Using regex-only mode.")
    
    def _check_ollama_connection(self) -> bool:
        """Check if Ollama is running and models are available"""
        try:
            response = ollama.list()
            available_models = [model['name'] for model in response.get('models', [])]
            
            # Check if primary model is available
            primary_available = any(self.primary_model in model for model in available_models)
            
            if not primary_available:
                logger.warning(f"Primary model {self.primary_model} not found. Available: {available_models}")
                logger.info(f"Pull model with: ollama pull {self.primary_model}")
                return False
            
            logger.info(f"Ollama connected. Using model: {self.primary_model}")
            return True
            
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            self.llm_enabled = False
            return False
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze emotion in text using LLM or regex fallback
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict with keys: primary_emotion, confidence, emotion_type
        """
        self.stats['total_analyses'] += 1
        
        # Try LLM analysis first if enabled
        if self.llm_enabled:
            result = self._llm_analyze(text)
            if result:
                self.stats['llm_successes'] += 1
                return result
            else:
                self.stats['llm_failures'] += 1
                logger.warning("LLM analysis failed, falling back to regex")
        
        # Fallback to regex
        self.stats['regex_fallbacks'] += 1
        return self.regex_analyzer.analyze(text)
    
    def _llm_analyze(self, text: str) -> Optional[Dict]:
        """
        Perform LLM-based emotion analysis
        
        Args:
            text: Input text
            
        Returns:
            Emotion analysis dict or None if failed
        """
        models_to_try = [self.primary_model] + self.fallback_models
        
        for model in models_to_try:
            try:
                start_time = time.time()
                
                # Create prompt
                prompt = LLMConfig.EMOTION_PROMPT_TEMPLATE.format(text=text)
                
                # Call Ollama
                response = ollama.generate(
                    model=model,
                    prompt=prompt,
                    options={
                        'temperature': LLMConfig.TEMPERATURE,
                        'top_p': LLMConfig.TOP_P,
                        'num_predict': LLMConfig.MAX_TOKENS,
                    }
                )
                
                # Track performance
                elapsed_ms = (time.time() - start_time) * 1000
                self._update_performance_stats(elapsed_ms, model)
                
                # Parse response
                result = self._parse_llm_response(response['response'])
                
                if result:
                    result['method'] = 'llm'
                    result['model'] = model
                    result['processing_time_ms'] = round(elapsed_ms, 2)
                    logger.info(f"LLM analysis successful with {model}: {result['primary_emotion']}")
                    return result
                
            except Exception as e:
                logger.warning(f"LLM analysis failed with {model}: {e}")
                continue
        
        return None
    
    def _parse_llm_response(self, response: str) -> Optional[Dict]:
        """
        Parse LLM response and extract emotion data
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Parsed emotion dict or None if parsing failed
        """
        try:
            # Try to extract JSON from response
            # Look for JSON-like content between curly braces
            json_match = re.search(r'\{[^}]+\}', response)
            
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # Validate required fields
                if all(key in data for key in ['primary_emotion', 'confidence', 'emotion_type']):
                    # Normalize emotion name
                    emotion = data['primary_emotion'].lower().strip()
                    
                    # Validate emotion is in allowed list
                    allowed_emotions = ['happy', 'sad', 'anxious', 'angry', 'confused', 'tired', 'neutral']
                    if emotion not in allowed_emotions:
                        # Try to map to closest emotion
                        emotion = self._map_to_valid_emotion(emotion)
                    
                    # Validate confidence is between 0 and 1
                    confidence = float(data['confidence'])
                    confidence = max(0.0, min(1.0, confidence))
                    
                    # Validate emotion_type
                    emotion_type = data['emotion_type'].lower()
                    if emotion_type not in ['positive', 'negative', 'neutral']:
                        emotion_type = self._infer_emotion_type(emotion)
                    
                    return {
                        'primary_emotion': emotion,
                        'confidence': confidence,
                        'emotion_type': emotion_type
                    }
            
            # If JSON parsing fails, try to extract values with regex
            emotion_pattern = r'(?:primary_emotion|emotion)[\s:\"\']+(\w+)'
            confidence_pattern = r'(?:confidence)[\s:\"\']+([0-9.]+)'
            type_pattern = r'(?:emotion_type|type)[\s:\"\']+(\w+)'
            
            emotion_match = re.search(emotion_pattern, response, re.IGNORECASE)
            confidence_match = re.search(confidence_pattern, response)
            type_match = re.search(type_pattern, response, re.IGNORECASE)
            
            if emotion_match:
                emotion = emotion_match.group(1).lower()
                confidence = float(confidence_match.group(1)) if confidence_match else 0.7
                emotion_type = type_match.group(1).lower() if type_match else self._infer_emotion_type(emotion)
                
                return {
                    'primary_emotion': self._map_to_valid_emotion(emotion),
                    'confidence': confidence,
                    'emotion_type': emotion_type
                }
            
        except Exception as e:
            logger.debug(f"Failed to parse LLM response: {e}")
        
        return None
    
    def _map_to_valid_emotion(self, emotion: str) -> str:
        """Map any emotion string to a valid emotion category"""
        emotion_mapping = {
            'joy': 'happy', 'joyful': 'happy', 'excited': 'happy', 'glad': 'happy',
            'unhappy': 'sad', 'depressed': 'sad', 'down': 'sad', 'blue': 'sad',
            'worried': 'anxious', 'nervous': 'anxious', 'stressed': 'anxious',
            'mad': 'angry', 'furious': 'angry', 'irritated': 'angry',
            'uncertain': 'confused', 'puzzled': 'confused',
            'exhausted': 'tired', 'weary': 'tired', 'fatigued': 'tired',
            'ok': 'neutral', 'okay': 'neutral', 'fine': 'neutral'
        }
        return emotion_mapping.get(emotion, 'neutral')
    
    def _infer_emotion_type(self, emotion: str) -> str:
        """Infer emotion type from emotion name"""
        positive_emotions = ['happy']
        negative_emotions = ['sad', 'anxious', 'angry', 'confused', 'tired']
        
        if emotion in positive_emotions:
            return 'positive'
        elif emotion in negative_emotions:
            return 'negative'
        else:
            return 'neutral'
    
    def _update_performance_stats(self, elapsed_ms: float, model: str):
        """Update performance tracking statistics"""
        # Update average time
        total = self.stats['llm_successes'] + 1
        current_avg = self.stats['avg_llm_time_ms']
        self.stats['avg_llm_time_ms'] = (current_avg * (total - 1) + elapsed_ms) / total
        
        # Track model usage
        if model not in self.stats['model_used']:
            self.stats['model_used'][model] = 0
        self.stats['model_used'][model] += 1
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            **self.stats,
            'llm_success_rate': (
                self.stats['llm_successes'] / self.stats['total_analyses'] * 100
                if self.stats['total_analyses'] > 0 else 0
            ),
            'llm_enabled': self.llm_enabled
        }


class RegexEmotionAnalyzer:
    """
    Fallback regex-based emotion analyzer
    (Original implementation from intelligent_agent.py)
    """
    
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
    
    def analyze(self, text: str) -> Dict:
        """Analyze emotion using keyword matching"""
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
            'emotion_type': emotion_type,
            'method': 'regex'
        }


# Utility function for easy import
def create_emotion_analyzer() -> LLMEmotionAnalyzer:
    """Factory function to create emotion analyzer"""
    return LLMEmotionAnalyzer()


if __name__ == "__main__":
    # Test the analyzer
    analyzer = LLMEmotionAnalyzer()
    
    test_texts = [
        "I'm feeling really happy and excited today!",
        "I'm so sad and don't know what to do",
        "I'm anxious about the presentation tomorrow",
        "This is making me so angry!",
        "I'm confused about what to do next",
        "I'm just tired and exhausted",
        "Everything is fine, just a normal day"
    ]
    
    print("\\n=== LLM Emotion Analyzer Test ===\\n")
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"Text: {text}")
        print(f"Result: {result}\\n")
    
    print("\\n=== Performance Statistics ===")
    print(json.dumps(analyzer.get_stats(), indent=2))
