"""
ProbabilisticReasoning Module

This module implements probabilistic reasoning capabilities using Bayesian networks
and Markov models to model emotional transitions and intervention effectiveness.
"""

import os
import json
import logging
import numpy as np
import datetime
from typing import Dict, List, Any, Optional, Tuple

# Try to import dataset integrations
try:
    from .dataset.iemocap_integration import IemocapIntegration
    IEMOCAP_AVAILABLE = True
except ImportError:
    IEMOCAP_AVAILABLE = False
    
try:
    from .dataset.mental_health_integration import MentalHealthIntegration
    MENTAL_HEALTH_AVAILABLE = True
except ImportError:
    MENTAL_HEALTH_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BayesianModel:
    """
    Implements a sophisticated Bayesian network for emotional reasoning and intervention effectiveness.
    
    The BayesianModel uses data-driven probabilities derived from the IEMOCAP and Mental Health 
    datasets to model relationships between emotions, contexts, and interventions. It features:
    
    1. Prior probabilities for emotional states based on population averages
    2. Conditional probabilities for intervention effectiveness given emotional states
    3. Context-dependent probabilities that consider situational factors
    4. Personalized models that adapt to individual users' emotional patterns
    5. Integration with HDFS for model storage and retrieval
    """
    
    def __init__(self, user_email=None, models_path=None):
        """
        Initialize the Bayesian model.
        
        Args:
            user_email: User email for personalization
            models_path: Path to pre-trained models
        """
        self.user_email = user_email
        self.models_path = models_path or os.environ.get(
            "BAYESIAN_MODELS_PATH", 
            "hdfs://namenode:9000/user/reflectly/models/bayesian"
        )
        
        # Initialize variables
        self.conditional_probs = {}  # P(Intervention | Emotion)
        self.prior_probs = {}        # P(Emotion)
        self.context_probs = {}      # P(Intervention | Context)
        self.emotion_relations = {}  # Relationships between emotions
        self.intervention_efficacy = {} # Dataset-derived efficacy data
        self.user_specific_probs = {} # Personalized probabilities
        self.loaded = False
        self.cache_ttl = datetime.timedelta(hours=1)
        self.last_cache_update = datetime.datetime.min
        
        # Integration with HDFS
        try:
            from ..services.hdfs_service import HDFSService
            self.hdfs_service = HDFSService()
        except ImportError:
            logger.warning("HDFS service not available, will use local storage for models")
            self.hdfs_service = None
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """
        Load Bayesian models from files or HDFS storage.
        
        This method first attempts to load user-specific models if a user_email is provided.
        If no user-specific model is found, it falls back to default models, then enhances them
        with dataset-derived probabilities from IEMOCAP and Mental Health datasets.
        """
        try:
            logger.info(f"Loading Bayesian models from {self.models_path}")
            
            # Try to load user-specific model if user_email is provided
            user_model_loaded = False
            if self.user_email and self.hdfs_service and self.hdfs_service.check_connection():
                user_model_path = f"{self.models_path}/{self.user_email}/bayesian_model.json"
                if self.hdfs_service.check_file_exists(user_model_path):
                    try:
                        model_json = self.hdfs_service.read_file(user_model_path)
                        user_model = json.loads(model_json)
                        
                        # Check if model is recent (less than a week old)
                        model_time = datetime.datetime.fromisoformat(user_model.get('timestamp', '2000-01-01T00:00:00'))
                        if (datetime.datetime.now() - model_time).total_seconds() < 604800:  # 7 days
                            self.prior_probs = user_model.get('prior_probs', {})
                            self.conditional_probs = user_model.get('conditional_probs', {})
                            self.context_probs = user_model.get('context_probs', {})
                            self.emotion_relations = user_model.get('emotion_relations', {})
                            self.user_specific_probs = user_model.get('user_specific_probs', {})
                            user_model_loaded = True
                            logger.info(f"Loaded personalized Bayesian model for user {self.user_email}")
                    except Exception as e:
                        logger.warning(f"Failed to load user-specific Bayesian model: {e}")
            
            # Load default model if user model not loaded
            if not user_model_loaded:
                # Define prior probabilities for emotions (expanded set)
                self.prior_probs = {
                    'joy': 0.15,
                    'sadness': 0.15,
                    'anger': 0.10,
                    'fear': 0.10,
                    'surprise': 0.05,
                    'disgust': 0.05,
                    'neutral': 0.40,
                    'relaxed': 0.12,
                    'excited': 0.08,
                    'anxious': 0.12,
                    'frustrated': 0.10,
                    'content': 0.10,
                    'stressed': 0.15,
                    'bored': 0.08,
                    'hopeful': 0.08,
                    'grateful': 0.07
                }
                
                # Define conditional probabilities for interventions (expanded set)
                self.conditional_probs = {
                    'social_connection': {
                        'joy': 0.80,
                        'sadness': 0.75,
                        'anger': 0.30,
                        'fear': 0.55,
                        'surprise': 0.60,
                        'disgust': 0.25,
                        'neutral': 0.50,
                        'relaxed': 0.65,
                        'excited': 0.75,
                        'anxious': 0.60,
                        'frustrated': 0.35,
                        'content': 0.70,
                        'stressed': 0.55,
                        'bored': 0.70,
                        'hopeful': 0.75,
                        'grateful': 0.85
                    },
                    'physical_activity': {
                        'joy': 0.70,
                        'sadness': 0.65,
                        'anger': 0.80,
                        'fear': 0.60,
                        'surprise': 0.50,
                        'disgust': 0.40,
                        'neutral': 0.60,
                        'relaxed': 0.50,
                        'excited': 0.85,
                        'anxious': 0.75,
                        'frustrated': 0.80,
                        'content': 0.55,
                        'stressed': 0.80,
                        'bored': 0.75,
                        'hopeful': 0.65,
                        'grateful': 0.50
                    },
                    'mindfulness': {
                        'joy': 0.60,
                        'sadness': 0.55,
                        'anger': 0.65,
                        'fear': 0.75,
                        'surprise': 0.40,
                        'disgust': 0.50,
                        'neutral': 0.70,
                        'relaxed': 0.85,
                        'excited': 0.45,
                        'anxious': 0.85,
                        'frustrated': 0.70,
                        'content': 0.75,
                        'stressed': 0.85,
                        'bored': 0.40,
                        'hopeful': 0.60,
                        'grateful': 0.75
                    },
                    'creative_expression': {
                        'joy': 0.75,
                        'sadness': 0.65,
                        'anger': 0.55,
                        'fear': 0.45,
                        'surprise': 0.70,
                        'disgust': 0.35,
                        'neutral': 0.55,
                        'relaxed': 0.60,
                        'excited': 0.80,
                        'anxious': 0.50,
                        'frustrated': 0.60,
                        'content': 0.65,
                        'stressed': 0.55,
                        'bored': 0.80,
                        'hopeful': 0.70,
                        'grateful': 0.65
                    },
                    'cognitive_reframing': {
                        'joy': 0.55,
                        'sadness': 0.75,
                        'anger': 0.65,
                        'fear': 0.80,
                        'surprise': 0.45,
                        'disgust': 0.60,
                        'neutral': 0.55,
                        'relaxed': 0.50,
                        'excited': 0.40,
                        'anxious': 0.80,
                        'frustrated': 0.75,
                        'content': 0.45,
                        'stressed': 0.70,
                        'bored': 0.45,
                        'hopeful': 0.60,
                        'grateful': 0.50
                    },
                    'gratitude_practice': {
                        'joy': 0.80,
                        'sadness': 0.65,
                        'anger': 0.40,
                        'fear': 0.55,
                        'surprise': 0.50,
                        'disgust': 0.35,
                        'neutral': 0.65,
                        'relaxed': 0.70,
                        'excited': 0.60,
                        'anxious': 0.60,
                        'frustrated': 0.50,
                        'content': 0.85,
                        'stressed': 0.65,
                        'bored': 0.55,
                        'hopeful': 0.80,
                        'grateful': 0.90
                    },
                    'structured_problem_solving': {
                        'joy': 0.50,
                        'sadness': 0.60,
                        'anger': 0.70,
                        'fear': 0.75,
                        'surprise': 0.45,
                        'disgust': 0.50,
                        'neutral': 0.65,
                        'relaxed': 0.45,
                        'excited': 0.55,
                        'anxious': 0.75,
                        'frustrated': 0.85,
                        'content': 0.50,
                        'stressed': 0.80,
                        'bored': 0.60,
                        'hopeful': 0.70,
                        'grateful': 0.45
                    }
                }
                
                # Define context-dependent probabilities for interventions
                self.context_probs = {
                    'work_stress': {
                        'social_connection': 0.50,  # Less effective during work stress
                        'physical_activity': 0.75,  # Very effective for work stress
                        'mindfulness': 0.85,        # Extremely effective for work stress
                        'creative_expression': 0.55,
                        'cognitive_reframing': 0.80,
                        'gratitude_practice': 0.65,
                        'structured_problem_solving': 0.90
                    },
                    'relationship_issues': {
                        'social_connection': 0.80,  # Very effective for relationship issues
                        'physical_activity': 0.60,
                        'mindfulness': 0.70,
                        'creative_expression': 0.65,
                        'cognitive_reframing': 0.85,
                        'gratitude_practice': 0.75,
                        'structured_problem_solving': 0.80
                    },
                    'health_concerns': {
                        'social_connection': 0.70,
                        'physical_activity': 0.65,  # May be limited by health concerns
                        'mindfulness': 0.80,
                        'creative_expression': 0.60,
                        'cognitive_reframing': 0.75,
                        'gratitude_practice': 0.70,
                        'structured_problem_solving': 0.75
                    },
                    'financial_stress': {
                        'social_connection': 0.65,
                        'physical_activity': 0.60,  # Free but may be limited by time/resources
                        'mindfulness': 0.75,        # Free and accessible
                        'creative_expression': 0.55,
                        'cognitive_reframing': 0.80,
                        'gratitude_practice': 0.70,
                        'structured_problem_solving': 0.90
                    },
                    'daily_hassles': {
                        'social_connection': 0.75,
                        'physical_activity': 0.80,
                        'mindfulness': 0.75,
                        'creative_expression': 0.65,
                        'cognitive_reframing': 0.70,
                        'gratitude_practice': 0.80,
                        'structured_problem_solving': 0.70
                    }
                }
                
                # Define emotion relationship model
                self.emotion_relations = {
                    'joy': {
                        'relaxed': 0.7,
                        'excited': 0.8,
                        'content': 0.8,
                        'grateful': 0.7,
                        'hopeful': 0.6
                    },
                    'sadness': {
                        'anxious': 0.5,
                        'stressed': 0.6,
                        'frustrated': 0.4,
                        'bored': 0.3
                    },
                    'anger': {
                        'frustrated': 0.8,
                        'stressed': 0.7,
                        'anxious': 0.4
                    },
                    'fear': {
                        'anxious': 0.9,
                        'stressed': 0.7
                    },
                    'neutral': {
                        'content': 0.5,
                        'bored': 0.4,
                        'relaxed': 0.5
                    }
                }
                
                # Initialize empty user-specific probabilities
                self.user_specific_probs = {
                    'intervention_history': {},
                    'emotion_transitions': {},
                    'context_efficacy': {}
                }
            
            # If IEMOCAP data is available, enhance with dataset-derived probabilities
            if IEMOCAP_AVAILABLE:
                try:
                    iemocap = IemocapIntegration()
                    if iemocap.loaded:
                        logger.info("Enhancing Bayesian model with IEMOCAP data")
                        
                        # Update emotion relations from IEMOCAP dataset
                        emotion_pairs = iemocap.get_emotion_correlations()
                        
                        for primary, related_emotions in emotion_pairs.items():
                            if primary not in self.emotion_relations:
                                self.emotion_relations[primary] = {}
                                
                            for related, strength in related_emotions.items():
                                self.emotion_relations[primary][related] = strength
                        
                        # Update prior probabilities based on IEMOCAP frequency
                        emotion_frequencies = iemocap.get_emotion_frequencies()
                        total_freq = sum(emotion_frequencies.values())
                        
                        if total_freq > 0:
                            for emotion, freq in emotion_frequencies.items():
                                normalized_freq = freq / total_freq
                                
                                # Blend with existing prior (30% IEMOCAP, 70% existing)
                                if emotion in self.prior_probs:
                                    self.prior_probs[emotion] = 0.3 * normalized_freq + 0.7 * self.prior_probs[emotion]
                except Exception as e:
                    logger.warning(f"Failed to enhance Bayesian model with IEMOCAP data: {e}")
            
            # If Mental Health data is available, enhance with dataset-derived probabilities
            if MENTAL_HEALTH_AVAILABLE:
                try:
                    mental_health = MentalHealthIntegration()
                    if mental_health.loaded:
                        logger.info("Enhancing Bayesian model with Mental Health Conversations data")
                        
                        # Get intervention efficacy data from Mental Health dataset
                        intervention_efficacy = mental_health.get_intervention_efficacy()
                        
                        # Update conditional probabilities with dataset-derived efficacies
                        for emotion, interventions in intervention_efficacy.items():
                            for intervention, efficacy in interventions.items():
                                # Map to our intervention categories
                                mapped_intervention = self._map_to_intervention_category(intervention)
                                
                                if mapped_intervention and mapped_intervention in self.conditional_probs:
                                    if emotion in self.conditional_probs[mapped_intervention]:
                                        # Blend dataset efficacy with our model (60% dataset, 40% existing)
                                        current_prob = self.conditional_probs[mapped_intervention][emotion]
                                        self.conditional_probs[mapped_intervention][emotion] = 0.6 * efficacy + 0.4 * current_prob
                        
                        # Get context efficacy data
                        context_efficacy = mental_health.get_context_specific_interventions()
                        
                        # Update context probabilities
                        for context, interventions in context_efficacy.items():
                            mapped_context = self._map_to_context_category(context)
                            
                            if mapped_context:
                                if mapped_context not in self.context_probs:
                                    self.context_probs[mapped_context] = {}
                                    
                                for intervention, efficacy in interventions.items():
                                    mapped_intervention = self._map_to_intervention_category(intervention)
                                    
                                    if mapped_intervention:
                                        if mapped_intervention in self.context_probs[mapped_context]:
                                            # Blend with existing (50/50)
                                            current = self.context_probs[mapped_context][mapped_intervention]
                                            self.context_probs[mapped_context][mapped_intervention] = 0.5 * efficacy + 0.5 * current
                                        else:
                                            self.context_probs[mapped_context][mapped_intervention] = efficacy
                except Exception as e:
                    logger.warning(f"Failed to enhance Bayesian model with Mental Health data: {e}")
                    
            self.loaded = True
            self.last_cache_update = datetime.datetime.now()
            logger.info("Bayesian models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Bayesian models: {e}")
            self.loaded = False
    
    def predict_intervention_effectiveness(self, emotion: str, intervention: str) -> float:
        """
        Predict the effectiveness of an intervention given an emotional state.
        
        Args:
            emotion: Current emotional state
            intervention: Proposed intervention
            
        Returns:
            Probability of effectiveness (0-1)
        """
        if not self.loaded:
            logger.warning("Bayesian models not loaded, returning default probability")
            return 0.5
        
        # Normalize emotion and intervention
        emotion = emotion.lower()
        intervention = intervention.lower()
        
        # Map intervention to known interventions
        intervention_mapping = {
            'social': 'social_connection',
            'social_connection': 'social_connection',
            'connect': 'social_connection',
            'talk': 'social_connection',
            
            'exercise': 'physical_activity',
            'physical': 'physical_activity',
            'physical_activity': 'physical_activity',
            'active': 'physical_activity',
            'workout': 'physical_activity',
            
            'mindfulness': 'mindfulness',
            'meditate': 'mindfulness',
            'meditation': 'mindfulness',
            'breathe': 'mindfulness',
            'breathing': 'mindfulness',
            
            'creative': 'creative_expression',
            'create': 'creative_expression',
            'art': 'creative_expression',
            'creative_expression': 'creative_expression',
            'write': 'creative_expression',
            
            'cognitive': 'cognitive_reframing',
            'reframe': 'cognitive_reframing',
            'cognitive_reframing': 'cognitive_reframing',
            'think': 'cognitive_reframing',
            'perspective': 'cognitive_reframing'
        }
        
        # Map intervention to known category
        intervention_category = intervention_mapping.get(intervention, None)
        
        # If intervention not recognized, return default probability
        if not intervention_category or intervention_category not in self.conditional_probs:
            return 0.5
        
        # Map emotion to known emotions
        emotion_mapping = {
            'happy': 'joy',
            'joy': 'joy',
            'excited': 'joy',
            
            'sad': 'sadness',
            'sadness': 'sadness',
            'depressed': 'sadness',
            
            'angry': 'anger',
            'anger': 'anger',
            'frustrated': 'anger',
            
            'afraid': 'fear',
            'fear': 'fear',
            'anxious': 'fear',
            'scared': 'fear',
            
            'surprised': 'surprise',
            'surprise': 'surprise',
            'shocked': 'surprise',
            
            'disgusted': 'disgust',
            'disgust': 'disgust',
            'repulsed': 'disgust',
            
            'neutral': 'neutral',
            'calm': 'neutral',
            'balanced': 'neutral'
        }
        
        # Map emotion to known category
        emotion_category = emotion_mapping.get(emotion, 'neutral')
        
        # Get conditional probability
        return self.conditional_probs[intervention_category].get(emotion_category, 0.5)
    
    def rank_interventions(self, emotion: str, interventions: List[str] = None) -> List[Dict[str, Any]]:
        """
        Rank interventions by effectiveness for a given emotion.
        
        Args:
            emotion: Current emotional state
            interventions: List of interventions to rank (optional, uses all if None)
            
        Returns:
            List of interventions with effectiveness scores, sorted by effectiveness
        """
        if not self.loaded:
            logger.warning("Bayesian models not loaded, returning default ranking")
            return [{'intervention': 'mindfulness', 'effectiveness': 0.5}]
        
        # If no interventions provided, use all known interventions
        if not interventions:
            interventions = list(self.conditional_probs.keys())
        
        # Calculate effectiveness for each intervention
        ranked_interventions = []
        for intervention in interventions:
            effectiveness = self.predict_intervention_effectiveness(emotion, intervention)
            intervention_name = intervention.replace('_', ' ').title()
            ranked_interventions.append({
                'intervention': intervention_name,
                'effectiveness': effectiveness
            })
        
        # Sort by effectiveness (descending)
        ranked_interventions.sort(key=lambda x: x['effectiveness'], reverse=True)
        
        return ranked_interventions


class MarkovModel:
    """
    Implements a sophisticated Markov model for predicting emotional state transitions.
    
    The MarkovModel uses data-driven transition probabilities derived from the IEMOCAP dataset
    and user history to model emotional state transitions over time. It features:
    
    1. Higher-order Markov chains for more accurate predictions using sequence history
    2. Time-dependent transitions that account for temporal patterns in emotional states
    3. Anomaly detection to identify unusual emotional transitions
    4. Integration with HDFS for model storage and retrieval
    5. Personalized models that adapt to individual users' emotional patterns
    """
    
    def __init__(self, user_email=None, models_path=None, order=2):
        """
        Initialize the Markov model.
        
        Args:
            user_email: User email for personalization
            models_path: Path to pre-trained models
            order: Order of the Markov chain (default: 2, meaning consider the last 2 emotions)
        """
        self.user_email = user_email
        self.models_path = models_path or os.environ.get(
            "MARKOV_MODELS_PATH", 
            "hdfs://namenode:9000/user/reflectly/models/markov"
        )
        self.order = min(max(1, order), 3)  # Restrict order to between 1 and 3
        
        # Initialize variables
        self.transition_matrix = {}        # First-order transitions (standard)
        self.second_order_matrix = {}      # Second-order transitions (based on last 2 emotions)
        self.third_order_matrix = {}       # Third-order transitions (based on last 3 emotions)
        self.time_transitions = {}         # Time-dependent transitions by hour of day
        self.weekday_transitions = {}      # Day-of-week dependent transitions
        self.anomaly_thresholds = {}       # Thresholds for identifying unusual transitions
        self.recent_transitions = []        # Cache of recent emotional transitions with timestamps
        self.cache_size = 20               # Size of recent transitions cache
        self.loaded = False
        self.last_update = datetime.datetime.now()
        
        # Integration with HDFS
        try:
            from ..services.hdfs_service import HDFSService
            self.hdfs_service = HDFSService()
        except ImportError:
            logger.warning("HDFS service not available, will use local storage for models")
            self.hdfs_service = None
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """
        Load Markov models from files or HDFS storage.
        
        This method first attempts to load user-specific models if a user_email is provided.
        If no user-specific model is found, it falls back to default models, then enhances them
        with dataset-derived probabilities from IEMOCAP dataset.
        """
        try:
            logger.info(f"Loading Markov models from {self.models_path}")
            
            # Try to load user-specific model if user_email is provided
            user_model_loaded = False
            if self.user_email and self.hdfs_service and self.hdfs_service.check_connection():
                user_model_path = f"{self.models_path}/{self.user_email}/markov_model.json"
                if self.hdfs_service.check_file_exists(user_model_path):
                    try:
                        model_json = self.hdfs_service.read_file(user_model_path)
                        user_model = json.loads(model_json)
                        
                        # Check if model is recent (less than a week old)
                        model_time = datetime.datetime.fromisoformat(user_model.get('timestamp', '2000-01-01T00:00:00'))
                        if (datetime.datetime.now() - model_time).total_seconds() < 604800:  # 7 days
                            self.transition_matrix = user_model.get('transition_matrix', {})
                            self.second_order_matrix = user_model.get('second_order_matrix', {})
                            self.third_order_matrix = user_model.get('third_order_matrix', {})
                            self.time_transitions = user_model.get('time_transitions', {})
                            self.weekday_transitions = user_model.get('weekday_transitions', {})
                            self.anomaly_thresholds = user_model.get('anomaly_thresholds', {})
                            user_model_loaded = True
                            logger.info(f"Loaded personalized Markov model for user {self.user_email}")
                    except Exception as e:
                        logger.warning(f"Failed to load user-specific Markov model: {e}")
            
            # Load default model if user model not loaded
            if not user_model_loaded:
                # Define first-order transition probabilities between emotions
                self.transition_matrix = {
                    'joy': {'joy': 0.6, 'sadness': 0.05, 'anger': 0.05, 'fear': 0.05, 'surprise': 0.15, 'disgust': 0.02, 'neutral': 0.08},
                    'sadness': {'joy': 0.1, 'sadness': 0.5, 'anger': 0.1, 'fear': 0.1, 'surprise': 0.05, 'disgust': 0.05, 'neutral': 0.1},
                    'anger': {'joy': 0.05, 'sadness': 0.15, 'anger': 0.5, 'fear': 0.1, 'surprise': 0.05, 'disgust': 0.1, 'neutral': 0.05},
                    'fear': {'joy': 0.05, 'sadness': 0.1, 'anger': 0.1, 'fear': 0.5, 'surprise': 0.15, 'disgust': 0.05, 'neutral': 0.05},
                    'surprise': {'joy': 0.3, 'sadness': 0.05, 'anger': 0.05, 'fear': 0.1, 'surprise': 0.3, 'disgust': 0.05, 'neutral': 0.15},
                    'disgust': {'joy': 0.05, 'sadness': 0.1, 'anger': 0.2, 'fear': 0.1, 'surprise': 0.05, 'disgust': 0.4, 'neutral': 0.1},
                    'neutral': {'joy': 0.15, 'sadness': 0.15, 'anger': 0.1, 'fear': 0.1, 'surprise': 0.15, 'disgust': 0.05, 'neutral': 0.3}
                }
                
                # Initialize second-order transition matrix with some reasonable defaults
                # Format: {(prev_emotion, current_emotion): {next_emotion: probability}}
                self.second_order_matrix = {
                    ('joy', 'joy'): {'joy': 0.7, 'sadness': 0.03, 'anger': 0.03, 'fear': 0.03, 'surprise': 0.12, 'disgust': 0.01, 'neutral': 0.08},
                    ('joy', 'sadness'): {'joy': 0.25, 'sadness': 0.4, 'anger': 0.05, 'fear': 0.05, 'surprise': 0.1, 'disgust': 0.05, 'neutral': 0.1},
                    ('sadness', 'joy'): {'joy': 0.5, 'sadness': 0.15, 'anger': 0.05, 'fear': 0.05, 'surprise': 0.15, 'disgust': 0.02, 'neutral': 0.08},
                    ('sadness', 'sadness'): {'joy': 0.05, 'sadness': 0.6, 'anger': 0.1, 'fear': 0.1, 'surprise': 0.03, 'disgust': 0.07, 'neutral': 0.05},
                    ('anger', 'anger'): {'joy': 0.02, 'sadness': 0.1, 'anger': 0.6, 'fear': 0.05, 'surprise': 0.03, 'disgust': 0.15, 'neutral': 0.05},
                    ('neutral', 'neutral'): {'joy': 0.15, 'sadness': 0.1, 'anger': 0.05, 'fear': 0.05, 'surprise': 0.1, 'disgust': 0.05, 'neutral': 0.5}
                }
                
                # Initialize time-dependent transitions (simplified version)
                # Different emotional patterns based on time of day
                self.time_transitions = {
                    # Morning (6-11 AM): More likely to transition to positive/neutral emotions
                    'morning': {
                        'joy': {'joy': 0.65, 'sadness': 0.05, 'anger': 0.05, 'fear': 0.03, 'surprise': 0.12, 'disgust': 0.02, 'neutral': 0.08},
                        'sadness': {'joy': 0.2, 'sadness': 0.4, 'anger': 0.05, 'fear': 0.05, 'surprise': 0.05, 'disgust': 0.05, 'neutral': 0.2},
                        'neutral': {'joy': 0.25, 'sadness': 0.10, 'anger': 0.05, 'fear': 0.05, 'surprise': 0.15, 'disgust': 0.05, 'neutral': 0.35}
                    },
                    # Afternoon (12-5 PM): Standard transitions
                    'afternoon': self.transition_matrix,
                    # Evening (6-10 PM): More reflection, higher neutral probability
                    'evening': {
                        'joy': {'joy': 0.5, 'sadness': 0.08, 'anger': 0.05, 'fear': 0.05, 'surprise': 0.1, 'disgust': 0.02, 'neutral': 0.2},
                        'sadness': {'joy': 0.12, 'sadness': 0.45, 'anger': 0.08, 'fear': 0.08, 'surprise': 0.05, 'disgust': 0.05, 'neutral': 0.17},
                        'neutral': {'joy': 0.15, 'sadness': 0.15, 'anger': 0.05, 'fear': 0.05, 'surprise': 0.1, 'disgust': 0.05, 'neutral': 0.45}
                    },
                    # Night (11 PM-5 AM): Higher probability for negative emotions
                    'night': {
                        'joy': {'joy': 0.4, 'sadness': 0.15, 'anger': 0.05, 'fear': 0.1, 'surprise': 0.05, 'disgust': 0.05, 'neutral': 0.2},
                        'sadness': {'joy': 0.05, 'sadness': 0.6, 'anger': 0.1, 'fear': 0.15, 'surprise': 0.02, 'disgust': 0.05, 'neutral': 0.03},
                        'fear': {'joy': 0.02, 'sadness': 0.15, 'anger': 0.1, 'fear': 0.6, 'surprise': 0.05, 'disgust': 0.05, 'neutral': 0.03}
                    }
                }
                
                # Initialize anomaly thresholds based on standard deviations from expected transitions
                # These values represent how many standard deviations away from the mean a transition
                # probability must be to be considered anomalous
                self.anomaly_thresholds = {
                    'joy': 2.0,      # Joy to another emotion
                    'sadness': 2.5,  # Sadness to another emotion
                    'anger': 2.5,    # Anger to another emotion
                    'fear': 2.5,     # Fear to another emotion
                    'surprise': 2.0, # Surprise to another emotion
                    'disgust': 2.5,  # Disgust to another emotion
                    'neutral': 2.0   # Neutral to another emotion
                }
            
            # If IEMOCAP data is available, enhance with dataset-derived probabilities
            if IEMOCAP_AVAILABLE:
                try:
                    iemocap = IemocapIntegration()
                    if iemocap.loaded:
                        # Update transition probabilities from IEMOCAP dataset
                        logger.info("Enhancing Markov model with IEMOCAP data")
                        
                        # For each emotion pair, update the transition probability with IEMOCAP data
                        for from_emotion in self.transition_matrix:
                            for to_emotion in self.transition_matrix[from_emotion]:
                                # Get transition probability from IEMOCAP
                                prob = iemocap.get_transition_probability(from_emotion, to_emotion)
                                
                                # Blend with existing probability (weighted average)
                                current_prob = self.transition_matrix[from_emotion][to_emotion]
                                self.transition_matrix[from_emotion][to_emotion] = 0.7 * prob + 0.3 * current_prob
                        
                        # If IEMOCAP provides second-order transitions, enhance those as well
                        if hasattr(iemocap, 'get_second_order_probability') and callable(getattr(iemocap, 'get_second_order_probability')):
                            for (prev, curr) in self.second_order_matrix:
                                for next_emotion in self.second_order_matrix[(prev, curr)]:
                                    prob = iemocap.get_second_order_probability(prev, curr, next_emotion)
                                    if prob is not None:
                                        current_prob = self.second_order_matrix[(prev, curr)][next_emotion]
                                        self.second_order_matrix[(prev, curr)][next_emotion] = 0.7 * prob + 0.3 * current_prob
                except Exception as e:
                    logger.warning(f"Failed to enhance Markov model with IEMOCAP data: {e}")
            
            self.loaded = True
            logger.info("Markov models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Markov models: {e}")
            self.loaded = False
    
    def predict_next_emotion(self, current_emotion: str, previous_emotion: str = None, 
                           timestamp: datetime.datetime = None) -> Tuple[str, float]:
        """
        Predict the next emotional state given the current state and optional previous state.
        
        This method uses higher-order Markov chains when available, and accounts for
        time-of-day effects on emotional transitions.
        
        Args:
            current_emotion: Current emotional state
            previous_emotion: Previous emotional state (for higher-order prediction)
            timestamp: Timestamp for time-dependent prediction
            
        Returns:
            A tuple of (predicted_emotion, confidence) where confidence is 0-1
        """
        if not self.loaded:
            logger.warning("Markov models not loaded, returning default prediction")
            return current_emotion, 0.5
        
        # Normalize emotion names
        current_emotion = current_emotion.lower()
        
        # Map to known emotions
        emotion_mapping = {
            'happy': 'joy',
            'joy': 'joy',
            'excited': 'joy',
            
            'sad': 'sadness',
            'sadness': 'sadness',
            'depressed': 'sadness',
            
            'angry': 'anger',
            'anger': 'anger',
            'frustrated': 'anger',
            
            'afraid': 'fear',
            'fear': 'fear',
            'anxious': 'fear',
            'scared': 'fear',
            
            'surprised': 'surprise',
            'surprise': 'surprise',
            'shocked': 'surprise',
            
            'disgusted': 'disgust',
            'disgust': 'disgust',
            'repulsed': 'disgust',
            
            'neutral': 'neutral',
            'calm': 'neutral',
            'balanced': 'neutral'
        }
        
        # Map to known emotion
        from_emotion = emotion_mapping.get(current_emotion, 'neutral')
        
        # Initialize variables
        confidence = 0.5  # Default confidence
        time_period = 'afternoon'  # Default time period
        
        # Determine time period if timestamp is provided
        if timestamp:
            hour = timestamp.hour
            if 6 <= hour < 12:
                time_period = 'morning'
            elif 12 <= hour < 18:
                time_period = 'afternoon'
            elif 18 <= hour < 23:
                time_period = 'evening'
            else:  # 23-5
                time_period = 'night'
        
        # Determine which order of Markov chain to use
        if self.order >= 2 and previous_emotion and self.second_order_matrix:
            # Use second-order Markov chain
            prev_emotion = emotion_mapping.get(previous_emotion.lower(), 'neutral')
            key = (prev_emotion, from_emotion)
            
            if key in self.second_order_matrix:
                # Use second-order transitions
                transitions = self.second_order_matrix[key]
                confidence = 0.75  # Higher confidence for second-order
            else:
                # Fall back to first-order
                transitions = self.transition_matrix.get(from_emotion, {})
                confidence = 0.6
        else:
            # First-order Markov chain
            if from_emotion in self.transition_matrix:
                transitions = self.transition_matrix[from_emotion]
                confidence = 0.6
            else:
                logger.warning(f"No transition probabilities for emotion {from_emotion}, using default")
                return from_emotion, 0.3  # Low confidence
        
        # Apply time-dependent effects if available
        if timestamp and time_period in self.time_transitions and from_emotion in self.time_transitions[time_period]:
            # Blend standard transitions with time-specific transitions
            time_transitions = self.time_transitions[time_period][from_emotion]
            
            # Create a combined transition dictionary
            combined_transitions = transitions.copy()
            
            # Update with time-specific probabilities (weighted blend)
            for emotion, prob in time_transitions.items():
                if emotion in combined_transitions:
                    # 60% standard + 40% time-specific
                    combined_transitions[emotion] = 0.6 * combined_transitions[emotion] + 0.4 * prob
                else:
                    combined_transitions[emotion] = prob
            
            transitions = combined_transitions
            confidence += 0.1  # Boost confidence with time data
        
        # Ensure we have valid transitions
        if not transitions:
            logger.warning(f"No valid transitions found for {from_emotion}, using default")
            return from_emotion, 0.3  # Low confidence
        
        # Get emotions and probabilities for weighted selection
        emotions = list(transitions.keys())
        probabilities = list(transitions.values())
        
        # Ensure probabilities sum to 1
        total_prob = sum(probabilities)
        if total_prob != 1.0:
            probabilities = [p/total_prob for p in probabilities]
        
        # Select next emotion using weighted random choice
        selected_emotion = np.random.choice(emotions, p=probabilities)
        
        # Add to recent transitions cache
        self.recent_transitions.append({
            'timestamp': timestamp or datetime.datetime.now(),
            'from_emotion': from_emotion,
            'to_emotion': selected_emotion,
            'probability': transitions.get(selected_emotion, 0)
        })
        
        # Keep only the most recent transitions
        if len(self.recent_transitions) > self.cache_size:
            self.recent_transitions = self.recent_transitions[-self.cache_size:]
        
        # Cap confidence at 0.95
        confidence = min(confidence, 0.95)
        
        return selected_emotion, confidence
    
    def predict_sequence(self, start_emotion: str, sequence_length: int = 5, 
                       include_confidence: bool = False, timestamp: datetime.datetime = None) -> List[Dict[str, Any]]:
        """
        Predict a sequence of emotional states starting from the given state.
        
        This enhanced method uses higher-order Markov chains and time-dependent transitions
        to generate more accurate predictions. It returns detailed information about each
        predicted state, including confidence scores.
        
        Args:
            start_emotion: Starting emotional state
            sequence_length: Length of the sequence to predict
            include_confidence: Whether to include confidence scores in the output
            timestamp: Optional starting timestamp for time-dependent predictions
            
        Returns:
            List of dictionaries containing predicted emotional states and metadata
        """
        if not self.loaded:
            logger.warning("Markov models not loaded, returning default sequence")
            if include_confidence:
                return [{'emotion': start_emotion, 'confidence': 0.3}] * sequence_length
            else:
                return [start_emotion] * sequence_length
        
        # Initialize sequence with start emotion
        current_emotion = start_emotion
        previous_emotion = None
        current_time = timestamp or datetime.datetime.now()
        sequence = []
        
        # Add starting emotion to sequence with high confidence
        if include_confidence:
            sequence.append({
                'emotion': current_emotion,
                'confidence': 0.95,  # High confidence for known starting point
                'timestamp': current_time.isoformat()
            })
        else:
            sequence.append(current_emotion)
        
        # Time increment for predictions (1-4 hours between emotional states)
        time_increments = [1, 2, 3, 4]  # hours
        
        # Predict next emotions
        for i in range(sequence_length - 1):
            # Update time for time-dependent predictions
            if timestamp:
                # Add a variable time increment to make predictions more realistic
                increment = np.random.choice(time_increments)
                current_time = current_time + datetime.timedelta(hours=increment)
            
            # Get next emotion prediction with confidence
            next_emotion, confidence = self.predict_next_emotion(
                current_emotion, 
                previous_emotion=previous_emotion, 
                timestamp=current_time
            )
            
            # Decrease confidence as we predict further into the future
            future_discount = max(0.5, 1.0 - (i * 0.1))  # Discount factor decreases with each step
            confidence = confidence * future_discount
            
            # Add prediction to sequence
            if include_confidence:
                sequence.append({
                    'emotion': next_emotion,
                    'confidence': confidence,
                    'timestamp': current_time.isoformat() if timestamp else None,
                    'likely_triggers': self._get_likely_triggers(current_emotion, next_emotion)
                })
            else:
                sequence.append(next_emotion)
            
            # Update for next iteration
            previous_emotion = current_emotion
            current_emotion = next_emotion
        
        return sequence
    
    def _get_likely_triggers(self, from_emotion: str, to_emotion: str) -> List[str]:
        """
        Get likely triggers for an emotional transition based on IEMOCAP data.
        
        Args:
            from_emotion: Starting emotional state
            to_emotion: Ending emotional state
            
        Returns:
            List of potential triggers for this emotional transition
        """
        # Define common triggers for emotional transitions
        triggers = {
            ('joy', 'sadness'): ['disappointment', 'loss', 'bad news'],
            ('joy', 'anger'): ['frustration', 'betrayal', 'unmet expectations'],
            ('joy', 'neutral'): ['return to baseline', 'time passing'],
            
            ('sadness', 'joy'): ['good news', 'support from others', 'perspective shift'],
            ('sadness', 'anger'): ['blame', 'injustice', 'repeated negative events'],
            ('sadness', 'fear'): ['uncertainty', 'anticipation of further loss'],
            
            ('anger', 'joy'): ['resolution', 'vindication', 'venting'],
            ('anger', 'sadness'): ['defeat', 'exhaustion', 'reflection'],
            ('anger', 'fear'): ['escalation', 'threat', 'consequences'],
            
            ('fear', 'joy'): ['relief', 'safety', 'overcoming challenge'],
            ('fear', 'sadness'): ['confirmed negative outcome', 'loss of hope'],
            ('fear', 'anger'): ['defensive response', 'frustration', 'feeling trapped'],
            
            ('neutral', 'joy'): ['positive event', 'pleasant surprise', 'accomplishment'],
            ('neutral', 'sadness'): ['negative news', 'remembering loss', 'disappointment'],
            ('neutral', 'anger'): ['provocation', 'unfairness', 'frustration'],
            ('neutral', 'fear'): ['threat', 'uncertainty', 'warning sign']
        }
        
        # Return triggers if we have them for this transition
        key = (from_emotion, to_emotion)
        if key in triggers:
            return triggers[key]
        else:
            # Generic triggers for unknown transitions
            return ['situational change', 'external event', 'internal reflection']
    
    def detect_anomalies(self, emotion_sequence: List[str], threshold_multiplier: float = 1.0) -> List[Dict[str, Any]]:
        """
        Detect anomalous transitions in a sequence of emotions.
        
        This method identifies unusual emotional transitions that deviate significantly
        from expected patterns. These anomalies could indicate important emotional events
        or potential issues that require attention.
        
        Args:
            emotion_sequence: Sequence of emotions to analyze
            threshold_multiplier: Adjustment factor for anomaly thresholds (higher = more sensitive)
            
        Returns:
            List of detected anomalies with metadata
        """
        if not self.loaded or len(emotion_sequence) < 2:
            logger.warning("Cannot detect anomalies: model not loaded or insufficient sequence")
            return []
        
        anomalies = []
        
        # Normalize and map emotions
        normalized_sequence = []
        emotion_mapping = {
            'happy': 'joy', 'joy': 'joy', 'excited': 'joy',
            'sad': 'sadness', 'sadness': 'sadness', 'depressed': 'sadness',
            'angry': 'anger', 'anger': 'anger', 'frustrated': 'anger',
            'afraid': 'fear', 'fear': 'fear', 'anxious': 'fear', 'scared': 'fear',
            'surprised': 'surprise', 'surprise': 'surprise', 'shocked': 'surprise',
            'disgusted': 'disgust', 'disgust': 'disgust', 'repulsed': 'disgust',
            'neutral': 'neutral', 'calm': 'neutral', 'balanced': 'neutral'
        }
        
        for emotion in emotion_sequence:
            normalized_sequence.append(emotion_mapping.get(emotion.lower(), 'neutral'))
        
        # Look for anomalous transitions
        for i in range(len(normalized_sequence) - 1):
            from_emotion = normalized_sequence[i]
            to_emotion = normalized_sequence[i+1]
            
            # Skip if we don't have transition data for this emotion
            if from_emotion not in self.transition_matrix:
                continue
                
            # Get transition probability
            probability = self.transition_matrix[from_emotion].get(to_emotion, 0)
            
            # Get anomaly threshold for this emotion
            threshold = self.anomaly_thresholds.get(from_emotion, 2.0) * threshold_multiplier
            
            # Calculate probabilities for all transitions from this emotion
            transition_probs = list(self.transition_matrix[from_emotion].values())
            mean_prob = sum(transition_probs) / len(transition_probs)
            std_dev = np.std(transition_probs)
            
            # Skip if standard deviation is too small to be meaningful
            if std_dev < 0.01:
                continue
                
            # Calculate z-score for this transition
            z_score = abs((probability - mean_prob) / std_dev)
            
            # If z-score exceeds threshold, mark as anomaly
            if z_score > threshold:
                anomalies.append({
                    'from_emotion': from_emotion,
                    'to_emotion': to_emotion,
                    'position': i,
                    'probability': probability,
                    'z_score': z_score,
                    'threshold': threshold,
                    'severity': 'high' if z_score > threshold * 1.5 else 'medium',
                    'potential_triggers': self._get_likely_triggers(from_emotion, to_emotion),
                    'explanation': f"Transition from {from_emotion} to {to_emotion} is unusual"
                })
        
        # Look for unusual patterns in the sequence (e.g., rapid oscillations)
        if len(normalized_sequence) >= 4:
            for i in range(len(normalized_sequence) - 3):
                subsequence = normalized_sequence[i:i+4]
                
                # Check for oscillation pattern (A-B-A-B)
                if subsequence[0] == subsequence[2] and subsequence[1] == subsequence[3] and subsequence[0] != subsequence[1]:
                    anomalies.append({
                        'pattern': 'oscillation',
                        'sequence': subsequence,
                        'position': i,
                        'severity': 'medium',
                        'explanation': f"Oscillation between {subsequence[0]} and {subsequence[1]}"
                    })
                
                # Check for stuck pattern (A-A-A-A)
                if subsequence.count(subsequence[0]) == 4 and subsequence[0] in ['sadness', 'anger', 'fear']:
                    anomalies.append({
                        'pattern': 'persistent_negative',
                        'emotion': subsequence[0],
                        'position': i,
                        'severity': 'high',
                        'explanation': f"Persistent {subsequence[0]} state"
                    })
        
        return anomalies
    
    def update_with_history(self, emotion_history: List[Dict[str, Any]]):
        """
        Update the Markov model with user's emotional history.
        
        This method learns from the user's emotional history to personalize the Markov model,
        updating transition probabilities for first-order, higher-order, and time-dependent
        transitions. It also adapts anomaly thresholds based on the user's emotional patterns.
        
        Args:
            emotion_history: List of emotional states with timestamps
        """
        if not self.loaded or not emotion_history or len(emotion_history) < 2:
            logger.warning("Cannot update Markov model: model not loaded or insufficient history")
            return
        
        # Sort history by timestamp
        sorted_history = sorted(emotion_history, key=lambda x: x.get('timestamp', datetime.datetime.min))
        
        # Normalize emotions in history
        emotion_mapping = {
            'happy': 'joy', 'joy': 'joy', 'excited': 'joy',
            'sad': 'sadness', 'sadness': 'sadness', 'depressed': 'sadness',
            'angry': 'anger', 'anger': 'anger', 'frustrated': 'anger',
            'afraid': 'fear', 'fear': 'fear', 'anxious': 'fear', 'scared': 'fear',
            'surprised': 'surprise', 'surprise': 'surprise', 'shocked': 'surprise',
            'disgusted': 'disgust', 'disgust': 'disgust', 'repulsed': 'disgust',
            'neutral': 'neutral', 'calm': 'neutral', 'balanced': 'neutral'
        }
        
        # Process history for updating model
        normalized_history = []
        for entry in sorted_history:
            emotion = entry.get('emotion', '').lower()
            if emotion:
                normalized_history.append({
                    'emotion': emotion_mapping.get(emotion, 'neutral'),
                    'timestamp': entry.get('timestamp', datetime.datetime.now())
                })
        
        # Skip if we don't have enough normalized history
        if len(normalized_history) < 2:
            logger.warning("Insufficient normalized history for updating model")
            return
        
        # Count first-order transitions in history
        first_order_counts = {}
        for i in range(len(normalized_history) - 1):
            from_emotion = normalized_history[i]['emotion']
            to_emotion = normalized_history[i+1]['emotion']
            
            if from_emotion not in first_order_counts:
                first_order_counts[from_emotion] = {}
            
            if to_emotion not in first_order_counts[from_emotion]:
                first_order_counts[from_emotion][to_emotion] = 0
                
            first_order_counts[from_emotion][to_emotion] += 1
        
        # Count second-order transitions if we have enough history
        second_order_counts = {}
        if len(normalized_history) >= 3 and self.order >= 2:
            for i in range(len(normalized_history) - 2):
                first_emotion = normalized_history[i]['emotion']
                second_emotion = normalized_history[i+1]['emotion']
                third_emotion = normalized_history[i+2]['emotion']
                
                key = (first_emotion, second_emotion)
                if key not in second_order_counts:
                    second_order_counts[key] = {}
                
                if third_emotion not in second_order_counts[key]:
                    second_order_counts[key][third_emotion] = 0
                    
                second_order_counts[key][third_emotion] += 1
        
        # Count third-order transitions if we have enough history
        third_order_counts = {}
        if len(normalized_history) >= 4 and self.order >= 3:
            for i in range(len(normalized_history) - 3):
                first_emotion = normalized_history[i]['emotion']
                second_emotion = normalized_history[i+1]['emotion']
                third_emotion = normalized_history[i+2]['emotion']
                fourth_emotion = normalized_history[i+3]['emotion']
                
                key = (first_emotion, second_emotion, third_emotion)
                if key not in third_order_counts:
                    third_order_counts[key] = {}
                
                if fourth_emotion not in third_order_counts[key]:
                    third_order_counts[key][fourth_emotion] = 0
                    
                third_order_counts[key][fourth_emotion] += 1
        
        # Count time-dependent transitions
        time_dependent_counts = {
            'morning': {}, # 6-12
            'afternoon': {}, # 12-18
            'evening': {}, # 18-23
            'night': {} # 23-6
        }
        
        for i in range(len(normalized_history) - 1):
            timestamp = normalized_history[i]['timestamp']
            from_emotion = normalized_history[i]['emotion']
            to_emotion = normalized_history[i+1]['emotion']
            
            # Determine time period
            hour = timestamp.hour if hasattr(timestamp, 'hour') else timestamp.hour() if hasattr(timestamp, 'hour') else 12
            
            if 6 <= hour < 12:
                time_period = 'morning'
            elif 12 <= hour < 18:
                time_period = 'afternoon'
            elif 18 <= hour < 23:
                time_period = 'evening'
            else: # 23-6
                time_period = 'night'
            
            # Initialize nested dictionaries if needed
            if from_emotion not in time_dependent_counts[time_period]:
                time_dependent_counts[time_period][from_emotion] = {}
            
            if to_emotion not in time_dependent_counts[time_period][from_emotion]:
                time_dependent_counts[time_period][from_emotion][to_emotion] = 0
                
            time_dependent_counts[time_period][from_emotion][to_emotion] += 1
        
        # Update first-order transition matrix
        self._update_transition_matrix(first_order_counts, self.transition_matrix, learning_rate=0.3)
        
        # Update second-order transition matrix if we're using higher-order chains
        if self.order >= 2 and second_order_counts:
            self._update_transition_matrix(second_order_counts, self.second_order_matrix, learning_rate=0.25)
        
        # Update third-order transition matrix if we're using higher-order chains
        if self.order >= 3 and third_order_counts:
            self._update_transition_matrix(third_order_counts, self.third_order_matrix, learning_rate=0.2)
        
        # Update time-dependent transitions
        for time_period, counts in time_dependent_counts.items():
            if counts:  # Only update if we have data
                if time_period not in self.time_transitions:
                    self.time_transitions[time_period] = {}
                    
                self._update_transition_matrix(counts, self.time_transitions[time_period], learning_rate=0.15)
        
        # Update anomaly thresholds based on history
        self._update_anomaly_thresholds(normalized_history)
        
        # Save updated model to HDFS if possible
        self._save_model()
    
    def _update_transition_matrix(self, counts, transition_matrix, learning_rate=0.2):
        """
        Update a transition matrix with new counts using a learning rate.
        
        Args:
            counts: Dictionary of transition counts
            transition_matrix: Transition matrix to update
            learning_rate: Rate at which to incorporate new data (0-1)
        """
        for from_state, to_states in counts.items():
            # Initialize if this state doesn't exist in the matrix
            if from_state not in transition_matrix:
                transition_matrix[from_state] = {}
            
            # Calculate total transitions from this state
            total_count = sum(to_states.values())
            
            # Update probabilities for each destination state
            for to_state, count in to_states.items():
                # Calculate new probability
                new_prob = count / total_count
                
                # If we already have a probability for this transition
                if to_state in transition_matrix[from_state]:
                    # Weighted average of old and new probability
                    old_prob = transition_matrix[from_state][to_state]
                    transition_matrix[from_state][to_state] = (1 - learning_rate) * old_prob + learning_rate * new_prob
                else:
                    # Initialize with new probability
                    transition_matrix[from_state][to_state] = new_prob
            
            # Normalize probabilities to ensure they sum to 1
            total_prob = sum(transition_matrix[from_state].values())
            if total_prob > 0:  # Avoid division by zero
                for to_state in transition_matrix[from_state]:
                    transition_matrix[from_state][to_state] /= total_prob
    
    def _update_anomaly_thresholds(self, history):
        """
        Update anomaly thresholds based on the user's emotional history.
        
        Args:
            history: List of emotional states with timestamps
        """
        # Calculate emotional variability for each emotion
        emotion_transitions = {}
        
        for i in range(len(history) - 1):
            from_emotion = history[i]['emotion']
            to_emotion = history[i+1]['emotion']
            
            if from_emotion not in emotion_transitions:
                emotion_transitions[from_emotion] = []
                
            emotion_transitions[from_emotion].append(to_emotion)
        
        # Update thresholds based on variability
        for emotion, transitions in emotion_transitions.items():
            if len(transitions) >= 3:
                # Count unique transitions
                unique_transitions = len(set(transitions))
                total_transitions = len(transitions)
                
                # Calculate variability ratio (0-1)
                variability = unique_transitions / total_transitions
                
                # Adjust threshold based on variability:
                # - High variability -> lower threshold (user has unpredictable patterns)
                # - Low variability -> higher threshold (user has predictable patterns)
                if variability > 0.7:  # High variability
                    self.anomaly_thresholds[emotion] = max(1.0, self.anomaly_thresholds.get(emotion, 2.0) * 0.9)
                elif variability < 0.3:  # Low variability
                    self.anomaly_thresholds[emotion] = min(3.0, self.anomaly_thresholds.get(emotion, 2.0) * 1.1)
    
    def _save_model(self):
        """
        Save the current model to HDFS for future use.
        """
        try:
            # Create serializable representation of the model
            model_data = {
                'version': '2.0',
                'user_id': self.user_id,
                'transition_matrix': self.transition_matrix,
                'second_order_matrix': self.second_order_matrix,
                'third_order_matrix': self.third_order_matrix,
                'time_transitions': self.time_transitions,
                'anomaly_thresholds': self.anomaly_thresholds,
                'updated_at': datetime.datetime.now().isoformat()
            }
            
            # Save to HDFS if connection is available
            if self.hdfs_client:
                model_path = f"/models/markov/{self.user_id}.json"
                with self.hdfs_client.write(model_path) as writer:
                    writer.write(json.dumps(model_data).encode('utf-8'))
                logger.info(f"Saved MarkovModel to HDFS for user {self.user_id}")
            else:
                logger.warning("HDFS client not available, model not saved")
                
        except Exception as e:
            logger.error(f"Error saving MarkovModel: {e}")
            
            # Map to known emotions
            emotion_mapping = {
                'happy': 'joy',
                'joy': 'joy',
                'excited': 'joy',
                
                'sad': 'sadness',
                'sadness': 'sadness',
                'depressed': 'sadness',
                
                'angry': 'anger',
                'anger': 'anger',
                'frustrated': 'anger',
                
                'afraid': 'fear',
                'fear': 'fear',
                'anxious': 'fear',
                'scared': 'fear',
                
                'surprised': 'surprise',
                'surprise': 'surprise',
                'shocked': 'surprise',
                
                'disgusted': 'disgust',
                'disgust': 'disgust',
                'repulsed': 'disgust',
                
                'neutral': 'neutral',
                'calm': 'neutral',
                'balanced': 'neutral'
            }
            
            from_emotion = emotion_mapping.get(from_emotion, 'neutral')
            to_emotion = emotion_mapping.get(to_emotion, 'neutral')
            
            if from_emotion not in transition_counts:
                transition_counts[from_emotion] = {}
            
            if to_emotion not in transition_counts[from_emotion]:
                transition_counts[from_emotion][to_emotion] = 0
            
            transition_counts[from_emotion][to_emotion] += 1
        
        # Update transition matrix with counts (using Bayesian update)
        for from_emotion in transition_counts:
            if from_emotion not in self.transition_matrix:
                self.transition_matrix[from_emotion] = {
                    'joy': 0.14,
                    'sadness': 0.14,
                    'anger': 0.14,
                    'fear': 0.14,
                    'surprise': 0.14,
                    'disgust': 0.14,
                    'neutral': 0.16
                }
            
            # Calculate total transitions from this emotion
            total = sum(transition_counts[from_emotion].values())
            
            # Update probabilities
            for to_emotion, count in transition_counts[from_emotion].items():
                # Calculate observed probability
                observed_prob = count / total
                
                # Update using weighted average (give more weight to user's history)
                if to_emotion in self.transition_matrix[from_emotion]:
                    current_prob = self.transition_matrix[from_emotion][to_emotion]
                    self.transition_matrix[from_emotion][to_emotion] = 0.7 * observed_prob + 0.3 * current_prob
                else:
                    self.transition_matrix[from_emotion][to_emotion] = observed_prob
            
            # Normalize probabilities to ensure they sum to 1
            total_prob = sum(self.transition_matrix[from_emotion].values())
            for to_emotion in self.transition_matrix[from_emotion]:
                self.transition_matrix[from_emotion][to_emotion] /= total_prob


class ProbabilisticReasoning:
    """
    Main class for probabilistic reasoning, combining Bayesian and Markov models.
    """
    
    def __init__(self, user_email=None, models_path=None):
        """
        Initialize ProbabilisticReasoning.
        
        Args:
            user_email: User email for personalization
            models_path: Path to pre-trained models
        """
        self.user_email = user_email
        self.models_path = models_path
        
        # Initialize Bayesian and Markov models
        self.bayesian_model = BayesianModel(user_email, models_path)
        self.markov_model = MarkovModel(user_email, models_path)
        
        # Integration with datasets
        self.using_iemocap = IEMOCAP_AVAILABLE
        self.using_mental_health = MENTAL_HEALTH_AVAILABLE
        
        if self.using_iemocap:
            try:
                self.iemocap = IemocapIntegration()
            except Exception as e:
                logger.warning(f"Failed to initialize IEMOCAP integration: {e}")
                self.using_iemocap = False
        
        if self.using_mental_health:
            try:
                self.mental_health = MentalHealthIntegration()
            except Exception as e:
                logger.warning(f"Failed to initialize Mental Health integration: {e}")
                self.using_mental_health = False
    
    def predict_intervention_effectiveness(self, emotion: str, intervention: str) -> float:
        """
        Predict the effectiveness of an intervention for a given emotion.
        
        Args:
            emotion: Current emotional state
            intervention: Proposed intervention
            
        Returns:
            Probability of effectiveness (0-1)
        """
        # Check Mental Health dataset first (it has more direct intervention data)
        if self.using_mental_health and self.mental_health.loaded:
            try:
                # Get interventions from Mental Health dataset
                interventions = self.mental_health.get_effective_interventions(emotion, limit=5)
                
                # Find matching intervention
                for item in interventions:
                    if intervention.lower() in item['intervention'].lower():
                        return item['effectiveness']
            except Exception as e:
                logger.warning(f"Error getting intervention data from Mental Health: {e}")
        
        # Fall back to Bayesian model
        return self.bayesian_model.predict_intervention_effectiveness(emotion, intervention)
    
    def predict_next_emotion(self, current_emotion: str, previous_emotion: str = None, 
                           timestamp: datetime.datetime = None) -> Dict[str, Any]:
        """
        Predict the next emotional state using enhanced Markov model capabilities.
        
        Args:
            current_emotion: Current emotional state
            previous_emotion: Previous emotional state (for higher-order predictions)
            timestamp: Timestamp for time-dependent predictions
            
        Returns:
            Dictionary with predicted emotion and confidence score
        """
        emotion, confidence = self.markov_model.predict_next_emotion(
            current_emotion, 
            previous_emotion=previous_emotion, 
            timestamp=timestamp
        )
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'timestamp': datetime.datetime.now().isoformat(),
            'likely_triggers': self.markov_model._get_likely_triggers(current_emotion, emotion)
        }
    
    def predict_emotional_sequence(self, start_emotion: str, sequence_length: int = 5, 
                               include_metadata: bool = False, 
                               timestamp: datetime.datetime = None) -> List[Any]:
        """
        Predict a sequence of emotional states with rich metadata.
        
        Args:
            start_emotion: Starting emotional state
            sequence_length: Length of the sequence to predict
            include_metadata: Whether to include detailed metadata
            timestamp: Optional starting timestamp
            
        Returns:
            List of predicted emotional states with optional metadata
        """
        return self.markov_model.predict_sequence(
            start_emotion, 
            sequence_length=sequence_length,
            include_confidence=include_metadata,
            timestamp=timestamp
        )
    
    def rank_interventions(self, emotion: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Rank interventions by effectiveness for a given emotion.
        
        Args:
            emotion: Current emotional state
            limit: Maximum number of interventions to return
            
        Returns:
            List of interventions with effectiveness scores
        """
        # Check Mental Health dataset first (it has more direct intervention data)
        if self.using_mental_health and self.mental_health.loaded:
            try:
                # Get interventions from Mental Health dataset
                return self.mental_health.get_effective_interventions(emotion, limit=limit)
            except Exception as e:
                logger.warning(f"Error getting interventions from Mental Health: {e}")
        
        # Fall back to Bayesian model
        return self.bayesian_model.rank_interventions(emotion)[:limit]
    
    def update_with_emotion_history(self, emotion_history: List[Dict[str, Any]]):
        """
        Update models with user's emotional history.
        
        Args:
            emotion_history: List of emotional states with timestamps
        """
        if emotion_history and len(emotion_history) >= 2:
            self.markov_model.update_with_history(emotion_history)
    
    def detect_emotional_anomalies(self, emotion_sequence: List[str], 
                                sensitivity: float = 1.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in an emotional sequence using the Markov model.
        
        Args:
            emotion_sequence: Sequence of emotions to analyze
            sensitivity: Adjustment factor for anomaly detection (higher = more sensitive)
            
        Returns:
            List of detected anomalies with metadata
        """
        return self.markov_model.detect_anomalies(emotion_sequence, threshold_multiplier=sensitivity)
    
    def analyze_emotional_journey(self, emotion_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform a comprehensive analysis of a user's emotional journey.
        
        This method combines Bayesian and Markov models to provide insights into:
        - Emotional patterns and transitions
        - Anomalies and potential issues
        - Effective interventions
        - Future emotional trajectories
        
        Args:
            emotion_history: List of emotional states with timestamps
            
        Returns:
            Comprehensive analysis results
        """
        if not emotion_history or len(emotion_history) < 2:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least two emotional states for analysis'
            }
        
        # Extract sequence of emotions for analysis
        emotion_sequence = [entry.get('emotion', 'neutral') for entry in emotion_history]
        current_emotion = emotion_sequence[-1] if emotion_sequence else 'neutral'
        
        # Detect anomalies
        anomalies = self.markov_model.detect_anomalies(emotion_sequence)
        
        # Get intervention recommendations
        interventions = self.rank_interventions(current_emotion, limit=3)
        
        # Predict future trajectory
        future_trajectory = self.markov_model.predict_sequence(
            current_emotion, 
            sequence_length=3,
            include_confidence=True
        )
        
        # Identify dominant emotions
        emotion_counts = {}
        for emotion in emotion_sequence:
            if emotion in emotion_counts:
                emotion_counts[emotion] += 1
            else:
                emotion_counts[emotion] = 1
                
        dominant_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Analyze emotional stability
        transitions = len(set(zip(emotion_sequence[:-1], emotion_sequence[1:])))  
        stability_score = 1.0 - (transitions / max(1, len(emotion_sequence) - 1))
        
        return {
            'status': 'success',
            'current_emotion': current_emotion,
            'dominant_emotions': [{'emotion': e, 'count': c} for e, c in dominant_emotions],
            'emotional_stability': stability_score,
            'anomalies': anomalies,
            'recommended_interventions': interventions,
            'future_trajectory': future_trajectory,
            'analysis_timestamp': datetime.datetime.now().isoformat()
        }
    
    def get_emotion_coordinates(self, emotion: str) -> Dict[str, float]:
        """
        Get coordinates for an emotion in 2D space.
        
        Args:
            emotion: Emotion to get coordinates for
            
        Returns:
            Dictionary with x and y coordinates
        """
        if self.using_iemocap and self.iemocap.loaded:
            try:
                return self.iemocap.get_emotion_coordinates(emotion)
            except Exception as e:
                logger.warning(f"Error getting emotion coordinates from IEMOCAP: {e}")
        
        # Fallback coordinates (valence-arousal space)
        coordinates = {
            'joy': {'x': 0.8, 'y': 0.6},
            'sadness': {'x': -0.7, 'y': -0.4},
            'anger': {'x': -0.6, 'y': 0.8},
            'fear': {'x': -0.8, 'y': 0.6},
            'surprise': {'x': 0.3, 'y': 0.8},
            'disgust': {'x': -0.7, 'y': 0.2},
            'neutral': {'x': 0.0, 'y': 0.0}
        }
        
        # Normalize emotion name
        emotion = emotion.lower()
        
        # Map to known emotions
        emotion_mapping = {
            'happy': 'joy',
            'excited': 'joy',
            'sad': 'sadness',
            'depressed': 'sadness',
            'angry': 'anger',
            'frustrated': 'anger',
            'afraid': 'fear',
            'anxious': 'fear',
            'scared': 'fear',
            'surprised': 'surprise',
            'shocked': 'surprise',
            'disgusted': 'disgust',
            'repulsed': 'disgust',
            'calm': 'neutral',
            'balanced': 'neutral'
        }
        
        base_emotion = emotion_mapping.get(emotion, emotion)
        
        return coordinates.get(base_emotion, {'x': 0.0, 'y': 0.0})
