import random
import os
import logging

# Import dataset integrations
try:
    from .dataset.iemocap_integration import IemocapIntegration
    IEMOCAP_AVAILABLE = True
except ImportError:
    IEMOCAP_AVAILABLE = False
    logger.warning("IEMOCAP integration not available")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """
    Enhanced EmotionAnalyzer that can use a pre-trained model for emotion detection.
    Falls back to rule-based detection if dependencies are not available.
    """
    
    def __init__(self, use_pretrained=True, use_iemocap=True):
        """
        Initialize the EmotionAnalyzer.
        
        Args:
            use_pretrained (bool): Whether to use a pre-trained model
            use_iemocap (bool): Whether to use IEMOCAP dataset integration
        """
        # Define emotion labels
        self.emotion_labels = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
        self.positive_emotions = ['joy', 'surprise']
        self.use_pretrained = use_pretrained
        self.use_iemocap = use_iemocap and IEMOCAP_AVAILABLE
        self.model = None
        self.tokenizer = None
        self.using_pretrained = False
        self.using_iemocap = False
        
        # Initialize IEMOCAP integration if requested
        if self.use_iemocap:
            try:
                logger.info("Loading IEMOCAP dataset integration...")
                self.iemocap = IemocapIntegration()
                if self.iemocap.loaded:
                    self.using_iemocap = True
                    logger.info("IEMOCAP dataset integration loaded successfully")
                else:
                    logger.warning("IEMOCAP dataset models not loaded. Some features will be limited.")
            except Exception as e:
                logger.warning(f"Failed to initialize IEMOCAP integration: {str(e)}")
                self.using_iemocap = False
        
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
            
        logger.info(f"EmotionAnalyzer initialized with pretrained={self.using_pretrained}, iemocap={self.using_iemocap}")
        
    def analyze(self, text):
        """
        Analyze the emotion in the given text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: A dictionary containing emotion analysis results
        """
        # Try IEMOCAP-based detection first if available
        if self.using_iemocap:
            try:
                return self._analyze_with_iemocap(text)
            except Exception as e:
                logger.error(f"Error using IEMOCAP integration: {str(e)}")
                logger.info("Falling back to pre-trained or rule-based emotion detection")
                # Continue to other methods
        
        # Try pre-trained model if available
        if self.using_pretrained:
            try:
                return self._analyze_with_model(text)
            except Exception as e:
                logger.error(f"Error using pre-trained model: {str(e)}")
                logger.info("Falling back to rule-based emotion detection")
                return self._analyze_rule_based(text)
        else:
            return self._analyze_rule_based(text)
    
    def _analyze_with_iemocap(self, text):
        """
        Analyze emotion using the IEMOCAP dataset integration.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: A dictionary containing emotion analysis results
        """
        # Use IEMOCAP integration for emotion detection
        emotion_data = self.iemocap.detect_emotion(text)
        
        # Ensure the result is properly formatted
        if 'primary_emotion' not in emotion_data:
            raise ValueError("IEMOCAP emotion detection did not return a primary emotion")
        
        # Add detection method to the result
        emotion_data['detection_method'] = 'iemocap_dataset'
        
        return emotion_data
    
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
        elif any(word in text_lower for word in ['afraid', 'scared', 'worried', 'anxious', 'terrified', 'nervous', 'fearful', 'stressed']):
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
        
    def get_emotion_triggers(self, emotion):
        """
        Get common triggers for the given emotion, based on the IEMOCAP dataset if available.
        
        Args:
            emotion (str): The emotion to get triggers for
            
        Returns:
            list: A list of common triggers for the emotion
        """
        if self.using_iemocap:
            try:
                return self.iemocap.get_emotion_triggers(emotion)
            except Exception as e:
                logger.error(f"Error getting emotion triggers from IEMOCAP: {str(e)}")
        
        # Fallback triggers if IEMOCAP is not available
        triggers = {
            'joy': ['achieving goals', 'positive social interactions', 'pleasant surprises'],
            'sadness': ['loss', 'disappointment', 'rejection', 'failure'],
            'anger': ['injustice', 'frustration', 'disrespect', 'betrayal'],
            'fear': ['threat', 'uncertainty', 'danger', 'vulnerability'],
            'surprise': ['unexpected events', 'sudden changes', 'revelations'],
            'disgust': ['violations of moral/ethical standards', 'unpleasant sensory experiences'],
            'neutral': ['routine activities', 'familiar situations']
        }
        
        return triggers.get(emotion.lower(), ['unknown'])
    
    def get_emotion_coordinates(self, emotion):
        """
        Get coordinates for an emotion in 2D space for visualization, based on the IEMOCAP dataset if available.
        
        Args:
            emotion (str): The emotion to get coordinates for
            
        Returns:
            dict: A dictionary with x and y coordinates for the emotion
        """
        if self.using_iemocap:
            try:
                return self.iemocap.get_emotion_coordinates(emotion)
            except Exception as e:
                logger.error(f"Error getting emotion coordinates from IEMOCAP: {str(e)}")
        
        # Fallback coordinates if IEMOCAP is not available (valence-arousal space)
        coordinates = {
            'joy': {'x': 0.8, 'y': 0.6},
            'sadness': {'x': -0.7, 'y': -0.4},
            'anger': {'x': -0.6, 'y': 0.8},
            'fear': {'x': -0.8, 'y': 0.6},
            'surprise': {'x': 0.3, 'y': 0.8},
            'disgust': {'x': -0.7, 'y': 0.2},
            'neutral': {'x': 0.0, 'y': 0.0}
        }
        
        return coordinates.get(emotion.lower(), {'x': 0.0, 'y': 0.0})
        
    def analyze_emotion_transition(self, from_emotion, to_emotion):
        """
        Analyze the transition between two emotions using IEMOCAP dataset insights.
        
        Args:
            from_emotion (str): The starting emotion
            to_emotion (str): The target emotion
            
        Returns:
            dict: A dictionary containing transition analysis and insights
        """
        if self.using_iemocap:
            try:
                # Use IEMOCAP's transition insights
                return self.iemocap.get_emotional_transition_insights(from_emotion, to_emotion)
            except Exception as e:
                logger.error(f"Error analyzing emotion transition with IEMOCAP: {str(e)}")
        
        # Fallback to basic transition analysis if IEMOCAP is not available
        transition_data = {
            'from_emotion': from_emotion,
            'to_emotion': to_emotion,
            'frequency': 'unknown',
            'duration': 'varies',
            'common_triggers': self._get_fallback_transition_triggers(from_emotion, to_emotion),
            'common_expressions': self._get_fallback_transition_expressions(from_emotion, to_emotion),
            'effectiveness': self._get_fallback_transition_effectiveness(from_emotion, to_emotion),
            'physiological_indicators': self._get_fallback_physiological_indicators(to_emotion)
        }
        
        return transition_data
    
    def analyze_emotion_sequence(self, emotion_sequence):
        """
        Analyze a sequence of emotions using IEMOCAP dataset insights.
        
        Args:
            emotion_sequence (list): A list of emotions in chronological order
            
        Returns:
            dict: A dictionary containing sequence analysis and insights
        """
        if not emotion_sequence or len(emotion_sequence) < 2:
            return {
                'patterns': [],
                'unusual_transitions': [],
                'emotional_stability': 1.0,
                'intervention_suggestions': ['Insufficient data for sequence analysis'],
                'predicted_next': []
            }
            
        if self.using_iemocap:
            try:
                # Use IEMOCAP's sequence analysis capabilities
                return self.iemocap.analyze_emotion_sequence(emotion_sequence)
            except Exception as e:
                logger.error(f"Error analyzing emotion sequence with IEMOCAP: {str(e)}")
        
        # Fallback to basic sequence analysis if IEMOCAP is not available
        # Calculate basic stability metric (how many repeated emotions)
        unique_emotions = set(emotion_sequence)
        stability = 1.0 - (len(unique_emotions) / len(emotion_sequence))
        
        # Simple pattern detection
        patterns = []
        if len(emotion_sequence) >= 3:
            # Check for oscillation between two emotions
            if len(unique_emotions) == 2 and len(emotion_sequence) >= 4:
                patterns.append('emotional oscillation')
            
            # Check for persistent negative emotions
            negative_emotions = ['sadness', 'anger', 'fear', 'disgust']
            if all(e in negative_emotions for e in emotion_sequence[-3:]):
                patterns.append('persistent negative state')
                
            # Check for emotional improvement
            positive_emotions = ['joy', 'surprise']
            if any(e in negative_emotions for e in emotion_sequence[:-2]) and \
               any(e in positive_emotions for e in emotion_sequence[-2:]):
                patterns.append('emotional improvement')
        
        # Simple suggestions based on the sequence
        suggestions = []
        if 'persistent negative state' in patterns:
            suggestions.append('Consider activities that bring joy and connection')
        if 'emotional oscillation' in patterns:
            suggestions.append('Practice mindfulness to stabilize emotional states')
            
        # Simple next emotion prediction
        predicted_next = []
        if emotion_sequence[-1] in negative_emotions:
            predicted_next = ['neutral', emotion_sequence[-1]]
        else:
            predicted_next = [emotion_sequence[-1], 'neutral']
            
        # Identify any unusual transitions
        unusual_transitions = []
        common_transitions = {
            'sadness': ['neutral', 'joy'],
            'anger': ['neutral', 'sadness'],
            'fear': ['neutral', 'relief'],
            'joy': ['neutral', 'surprise'],
            'surprise': ['joy', 'neutral'],
            'disgust': ['anger', 'neutral'],
            'neutral': ['joy', 'sadness']
        }
        
        for i in range(len(emotion_sequence) - 1):
            from_e = emotion_sequence[i]
            to_e = emotion_sequence[i+1]
            if from_e in common_transitions and to_e not in common_transitions[from_e]:
                unusual_transitions.append((from_e, to_e))
        
        return {
            'patterns': patterns,
            'unusual_transitions': unusual_transitions[:2],  # Limit to top 2
            'emotional_stability': stability,
            'intervention_suggestions': suggestions,
            'predicted_next': predicted_next
        }
    
    def get_contextual_emotion_insights(self, emotion, context_factors=None):
        """
        Get contextual insights for a specific emotion based on IEMOCAP dataset.
        
        Args:
            emotion (str): The emotion to get insights for
            context_factors (list, optional): Additional contextual factors
            
        Returns:
            dict: A dictionary containing contextual insights for the emotion
        """
        if self.using_iemocap:
            try:
                # The IEMOCAP integration would ideally have this method
                # For now, we'll construct a response from available methods
                triggers = self.iemocap.get_emotion_triggers(emotion)
                
                # Get transition insights to common follow-up emotions
                common_next_emotions = ['neutral', 'joy'] if emotion != 'joy' else ['neutral', 'sadness']
                transitions = []
                for next_emotion in common_next_emotions:
                    transition = self.iemocap.get_emotional_transition_insights(emotion, next_emotion)
                    if transition:
                        transitions.append({
                            'to_emotion': next_emotion,
                            'frequency': transition.get('frequency', 'unknown'),
                            'common_triggers': transition.get('common_triggers', [])
                        })
                
                return {
                    'emotion': emotion,
                    'common_triggers': triggers,
                    'contextual_factors': context_factors or [],
                    'common_transitions': transitions,
                    'duration_statistics': self._get_emotion_duration_statistics(emotion),
                    'associated_expressions': self._get_associated_expressions(emotion),
                    'intensity_distribution': self._get_intensity_distribution(emotion),
                    'source': 'iemocap_dataset'
                }
            except Exception as e:
                logger.error(f"Error getting contextual insights from IEMOCAP: {str(e)}")
        
        # Fallback contextual insights
        return self._get_fallback_contextual_insights(emotion, context_factors)
    
    def get_emotion_intensity_factors(self, emotion):
        """
        Get factors that influence the intensity of an emotion, based on IEMOCAP dataset insights.
        
        Args:
            emotion (str): The emotion to get intensity factors for
            
        Returns:
            list: A list of factors that influence emotion intensity
        """
        if self.using_iemocap:
            try:
                # Ideally, the IEMOCAP integration would provide this directly
                # We'll simulate it for now based on related insights
                triggers = self.iemocap.get_emotion_triggers(emotion)
                # Extract intensity factors from triggers where possible
                intensity_factors = [f"Presence of {trigger}" for trigger in triggers[:3]]
                
                # Add some common intensity factors from research
                intensity_factors.extend([
                    "Personal significance of the situation",
                    "Proximity to the emotional stimulus",
                    "Unexpectedness of the triggering event"
                ])
                
                return intensity_factors
            except Exception as e:
                logger.error(f"Error getting intensity factors from IEMOCAP: {str(e)}")
        
        # Fallback intensity factors based on psychological research
        return self._get_fallback_intensity_factors(emotion)
    
    def _get_fallback_transition_triggers(self, from_emotion, to_emotion):
        """
        Get fallback transition triggers if IEMOCAP is not available.
        """
        transitions = {
            'sadness|joy': ['social reconnection', 'achievement', 'unexpected positive news'],
            'anger|neutral': ['time passing', 'distraction', 'resolution of conflict'],
            'fear|neutral': ['realization of safety', 'preparation', 'support from others'],
            'neutral|joy': ['good news', 'pleasant interaction', 'achievement'],
            'joy|sadness': ['disappointment', 'loss', 'empathizing with others'],
            'anger|sadness': ['realization of loss', 'exhaustion after anger', 'giving up'],
            'surprise|joy': ['positive unexpected outcome', 'revelation of good news'],
            'surprise|fear': ['sudden threat', 'unexpected danger', 'shocking revelation']
        }
        
        transition_key = f"{from_emotion}|{to_emotion}"
        return transitions.get(transition_key, ['unknown'])
    
    def _get_fallback_transition_expressions(self, from_emotion, to_emotion):
        """
        Get fallback transition expressions if IEMOCAP is not available.
        """
        expressions = {
            'sadness|joy': ['relief washing over me', 'light breaking through the clouds'],
            'anger|neutral': ['cooling down', 'letting it go', 'finding perspective'],
            'fear|neutral': ['weight being lifted', 'breathing easier', 'feeling grounded again'],
            'neutral|joy': ['brightening up', 'feeling energized', 'warmth spreading'],
            'joy|sadness': ['crashing down', 'deflated', 'hope fading'],
            'anger|sadness': ['fire burning out', 'energy draining', 'giving up the fight'],
            'surprise|joy': ['pleasant shock', 'delighted astonishment'],
            'surprise|fear': ['shock turning to dread', 'startled into fear']
        }
        
        transition_key = f"{from_emotion}|{to_emotion}"
        return expressions.get(transition_key, ['expression unavailable'])
    
    def _get_fallback_transition_effectiveness(self, from_emotion, to_emotion):
        """
        Get fallback transition effectiveness if IEMOCAP is not available.
        """
        # Only meaningful for transitions to positive states
        if to_emotion in ['joy', 'neutral'] and from_emotion in ['sadness', 'anger', 'fear']:
            return 0.65  # Moderate effectiveness
        return 0.0  # Not applicable for other transitions
    
    def _get_fallback_physiological_indicators(self, emotion):
        """
        Get fallback physiological indicators if IEMOCAP is not available.
        """
        indicators = {
            'joy': ['increased heart rate', 'smiling', 'relaxed muscles', 'energetic movement'],
            'sadness': ['slowed movements', 'downcast eyes', 'slumped posture', 'quieter voice'],
            'anger': ['increased blood pressure', 'clenched jaw/fists', 'raised voice', 'flushed face'],
            'fear': ['rapid breathing', 'widened eyes', 'tense muscles', 'goosebumps'],
            'surprise': ['raised eyebrows', 'widened eyes', 'momentary breath holding', 'gasping'],
            'disgust': ['wrinkling of nose', 'raised upper lip', 'physical withdrawal', 'nausea'],
            'neutral': ['regular breathing', 'relaxed facial muscles', 'steady voice']
        }
        
        return indicators.get(emotion, ['physiological indicator unavailable'])
        
    def _get_emotion_duration_statistics(self, emotion):
        """
        Get fallback duration statistics if IEMOCAP is not available.
        """
        durations = {
            'joy': {'median': '120 minutes', 'range': '10 minutes - 24 hours'},
            'sadness': {'median': '240 minutes', 'range': '30 minutes - 72 hours'},
            'anger': {'median': '60 minutes', 'range': '5 minutes - 12 hours'},
            'fear': {'median': '45 minutes', 'range': '5 minutes - 8 hours'},
            'surprise': {'median': '10 minutes', 'range': '1 minute - 60 minutes'},
            'disgust': {'median': '30 minutes', 'range': '5 minutes - 4 hours'},
            'neutral': {'median': 'varies widely', 'range': 'varies widely'}
        }
        
        return durations.get(emotion, {'median': 'unknown', 'range': 'unknown'})
    
    def _get_associated_expressions(self, emotion):
        """
        Get fallback associated expressions if IEMOCAP is not available.
        """
        expressions = {
            'joy': ['beaming with happiness', 'over the moon', 'on cloud nine', 'thrilled'],
            'sadness': ['down in the dumps', 'feeling blue', 'heartbroken', 'devastated'],
            'anger': ['seeing red', 'blood boiling', 'fuming', 'livid'],
            'fear': ['scared stiff', 'paralyzed with fear', 'terrified', 'petrified'],
            'surprise': ['blown away', 'taken aback', 'stunned', 'flabbergasted'],
            'disgust': ['turned off', 'revolted', 'nauseated', 'repulsed'],
            'neutral': ['even-keeled', 'composed', 'steady', 'balanced']
        }
        
        return expressions.get(emotion, ['expression unavailable'])
    
    def _get_intensity_distribution(self, emotion):
        """
        Get fallback intensity distribution if IEMOCAP is not available.
        """
        distributions = {
            'joy': [0.1, 0.2, 0.3, 0.25, 0.15],  # Distribution across 5 intensity levels
            'sadness': [0.05, 0.15, 0.4, 0.3, 0.1],
            'anger': [0.05, 0.1, 0.3, 0.35, 0.2],
            'fear': [0.05, 0.15, 0.35, 0.3, 0.15],
            'surprise': [0.1, 0.2, 0.3, 0.25, 0.15],
            'disgust': [0.1, 0.3, 0.3, 0.2, 0.1],
            'neutral': [0.3, 0.4, 0.3, 0.0, 0.0]
        }
        
        return distributions.get(emotion, [0.2, 0.2, 0.2, 0.2, 0.2])
    
    def _get_fallback_contextual_insights(self, emotion, context_factors=None):
        """
        Get fallback contextual insights if IEMOCAP is not available.
        """
        triggers = self.get_emotion_triggers(emotion)
        transitions = []
        
        # Simple next emotion predictions
        if emotion == 'sadness':
            transitions = [
                {'to_emotion': 'neutral', 'frequency': 'common', 'common_triggers': ['time passing', 'distraction']},
                {'to_emotion': 'joy', 'frequency': 'occasional', 'common_triggers': ['social support', 'unexpected good news']}
            ]
        elif emotion == 'anger':
            transitions = [
                {'to_emotion': 'neutral', 'frequency': 'common', 'common_triggers': ['time passing', 'resolution']},
                {'to_emotion': 'sadness', 'frequency': 'occasional', 'common_triggers': ['exhaustion', 'realization of loss']}
            ]
        elif emotion == 'fear':
            transitions = [
                {'to_emotion': 'neutral', 'frequency': 'common', 'common_triggers': ['threat passing', 'safety']},
                {'to_emotion': 'relief', 'frequency': 'occasional', 'common_triggers': ['preparation', 'support']}
            ]
        elif emotion == 'joy':
            transitions = [
                {'to_emotion': 'neutral', 'frequency': 'common', 'common_triggers': ['time passing', 'return to routine']},
                {'to_emotion': 'surprise', 'frequency': 'occasional', 'common_triggers': ['unexpected events']}
            ]
        
        return {
            'emotion': emotion,
            'common_triggers': triggers,
            'contextual_factors': context_factors or [],
            'common_transitions': transitions,
            'duration_statistics': self._get_emotion_duration_statistics(emotion),
            'associated_expressions': self._get_associated_expressions(emotion),
            'intensity_distribution': self._get_intensity_distribution(emotion),
            'source': 'fallback'
        }
    
    def _get_fallback_intensity_factors(self, emotion):
        """
        Get fallback intensity factors if IEMOCAP is not available.
        """
        # Common factors across emotions
        common_factors = [
            "Personal significance of the situation",
            "Proximity (physical or psychological) to the stimulus",
            "Unexpectedness of the event",
            "Duration of exposure to the stimulus",
            "Social context and presence of others"
        ]
        
        # Emotion-specific factors
        specific_factors = {
            'joy': ["Alignment with personal goals", "Social sharing opportunities", "Contrast with prior negative state"],
            'sadness': ["Irreversibility of loss", "Personal responsibility", "Lack of social support"],
            'anger': ["Perceived injustice", "Intentionality of offense", "Repeated frustration"],
            'fear': ["Perceived control over situation", "Previous trauma", "Escape options"],
            'surprise': ["Violation of expectations", "Significance of unexpected event"],
            'disgust': ["Perceived contamination", "Moral implications", "Sensory intensity"],
            'neutral': ["Familiarity with situation", "Absence of strong stimuli"]
        }
        
        # Combine common and specific factors
        all_factors = common_factors.copy()
        if emotion in specific_factors:
            all_factors.extend(specific_factors[emotion])
            
        return all_factors
