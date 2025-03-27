import random
import logging

# Import dataset integrations
try:
    from .dataset.mental_health_integration import MentalHealthIntegration
    MENTAL_HEALTH_AVAILABLE = True
except ImportError:
    MENTAL_HEALTH_AVAILABLE = False
    logging.warning("Mental Health integration not available")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Class for generating responses based on user input and emotion analysis.
    Enhanced with Mental Health dataset insights for better response personalization.
    """
    
    def __init__(self, use_mental_health=True):
        # Track previously used templates to avoid repetition
        self.last_used_templates = {}
        self.template_history = {}
        
        # Initialize Mental Health integration if requested
        self.use_mental_health = use_mental_health and MENTAL_HEALTH_AVAILABLE
        self.using_mental_health = False
        
        if self.use_mental_health:
            try:
                logger.info("Loading Mental Health dataset integration...")
                self.mental_health = MentalHealthIntegration()
                if self.mental_health.loaded:
                    self.using_mental_health = True
                    logger.info("Mental Health dataset integration loaded successfully")
                else:
                    logger.warning("Mental Health dataset models not loaded. Some features will be limited.")
            except Exception as e:
                logger.warning(f"Failed to initialize Mental Health integration: {str(e)}")
                self.using_mental_health = False
        # Define response templates for different emotions
        self.positive_templates = [
            "That's wonderful! I'm glad to hear you're feeling {emotion}. What made you feel this way?",
            "It's great that you're experiencing {emotion}! Would you like to share more about it?",
            "I'm happy to see you're feeling {emotion}. How can you maintain this positive energy?",
            "That sounds really positive! How does this {emotion} compare to how you felt yesterday?",
            "It's always nice to feel {emotion}. What's one thing you're grateful for right now?"
        ]
        
        self.negative_templates = [
            "I'm sorry to hear you're feeling {emotion}. What specific events or situations led to this feeling?",
            "It sounds like you're going through a difficult time. What are the main factors contributing to your {emotion}?",
            "I notice you're feeling {emotion}. What happened today that might have triggered this emotion?",
            "When you feel {emotion}, it can be helpful to identify the root causes. What do you think is behind this feeling?",
            "I'm here for you during this {emotion}. Can you share what activities or interactions made you feel this way?"
        ]
        
        # Special templates for stressed state
        self.stressed_templates = [
            "I understand you're feeling stressed. What specific pressures or responsibilities are weighing on you right now?",
            "Being stressed can be overwhelming. What particular situations are causing you to feel this way?",
            "I notice you're feeling stressed. What are the main sources of pressure in your life currently?",
            "Stress often comes from specific triggers. What events or deadlines are contributing to your stress?",
            "I'm here to help with your stress. What aspects of your daily routine might be adding to this feeling?"
        ]
        
        self.neutral_templates = [
            "Thanks for sharing that. How do you feel about it?",
            "I appreciate you writing this down. Is there anything specific you'd like to reflect on?",
            "That's interesting. How does this relate to your goals?",
            "Thank you for your entry. Is there anything else on your mind?",
            "I see. Would you like to explore this topic further?"
        ]
        
        # Define follow-up questions for deeper reflection
        self.follow_up_questions = [
            "How did this experience affect your perspective?",
            "What did you learn from this situation?",
            "How might this connect to your long-term goals?",
            "What patterns do you notice in how you respond to similar situations?",
            "If you could change one thing about this experience, what would it be?"
        ]
        
        # Define suggested actions for different emotions
        self.suggested_actions = {
            'sadness': [
                "Reach out to a friend or family member",
                "Practice self-care activities",
                "Listen to uplifting music",
                "Take a short walk outside",
                "Write down three things you're grateful for"
            ],
            'anger': [
                "Take deep breaths for a few minutes",
                "Write down your thoughts",
                "Engage in physical activity",
                "Practice mindfulness meditation",
                "Step away from the situation temporarily"
            ],
            'fear': [
                "Focus on your breathing",
                "Challenge negative thoughts",
                "Talk to someone you trust",
                "Create a plan to address your concerns",
                "Practice progressive muscle relaxation"
            ],
            'stressed': [
                "Try the 4-7-8 breathing technique (inhale for 4, hold for 7, exhale for 8)",
                "Take a 10-minute break from your current task",
                "Go for a short walk outside",
                "Practice mindfulness meditation for 5 minutes",
                "Write down your top 3 priorities to gain clarity",
                "Stretch or do gentle yoga poses",
                "Listen to calming music"
            ],
            'disgust': [
                "Redirect your attention to something positive",
                "Practice acceptance",
                "Engage in a pleasant activity",
                "Connect with supportive people",
                "Focus on things you appreciate"
            ],
            'neutral': [
                "Set a goal for today",
                "Practice gratitude",
                "Learn something new",
                "Connect with nature",
                "Reflect on your recent achievements"
            ],
            'joy': [
                "Share your positive experience with others",
                "Practice gratitude",
                "Savor the moment",
                "Set new goals",
                "Pay it forward with a kind act"
            ],
            'surprise': [
                "Reflect on what surprised you",
                "Consider what you can learn from this experience",
                "Share your experience with others",
                "Use this energy for creative activities",
                "Journal about your unexpected insights"
            ]
        }
    
    def generate(self, text, emotion_data):
        """
        Generate a response based on the user's input and emotion analysis.
        
        Args:
            text (str): The user's input text
            emotion_data (dict): Emotion analysis data
            
        Returns:
            str: A generated response
        """
        # Ensure emotion_data has all required fields
        if not emotion_data or not isinstance(emotion_data, dict):
            # Default to neutral if no emotion data
            emotion_data = {
                'primary_emotion': 'neutral',
                'is_positive': False,
                'emotion_scores': {}
            }
        
        # Ensure all required keys exist
        if 'primary_emotion' not in emotion_data:
            emotion_data['primary_emotion'] = 'neutral'
        if 'is_positive' not in emotion_data:
            emotion_data['is_positive'] = False
        if 'emotion_scores' not in emotion_data:
            emotion_data['emotion_scores'] = {}
            
        primary_emotion = emotion_data['primary_emotion']
        is_positive = emotion_data['is_positive']
        
        # Select appropriate template based on emotion
        if primary_emotion in ['joy', 'surprise']:
            template = random.choice(self.positive_templates)
        elif primary_emotion in ['anger', 'disgust', 'fear', 'sadness']:
            template = random.choice(self.negative_templates)
        else:
            template = random.choice(self.neutral_templates)
        
        # Format the template with the emotion
        response = template.format(emotion=primary_emotion)
        
        # Add a follow-up question 50% of the time
        if random.random() > 0.5:
            response += " " + random.choice(self.follow_up_questions)
        
        return response
        
    def generate_with_memory(self, text, emotion_data, memories=None, suggested_actions=None, emotion_history=None, **kwargs):
        """
        Generate a personalized response incorporating emotional history and suggested actions.
        Enhanced with Mental Health dataset insights for better personalization.
        
        Args:
            text (str): The user's input text
            emotion_data (dict): Emotion analysis data
            memories (list): Optional memory data for context
            suggested_actions (list): Optional suggested actions from emotional graph
            emotion_history (list): Optional emotional state history
            **kwargs: Additional context parameters
            
        Returns:
            dict: A response object with text and suggested actions
        """
        # Log for debugging
        logger.info(f"generate_with_memory called with emotion: {emotion_data.get('primary_emotion')}")
        if emotion_history:
            logger.info(f"Emotion history has {len(emotion_history)} entries")
            for i, entry in enumerate(emotion_history[:3]):
                logger.info(f"History entry {i}: {entry.get('primary_emotion')}")
                
        # Prepare user context for personalization
        user_context = {
            'text': text,
            'current_emotion': emotion_data.get('primary_emotion', 'neutral'),
            'is_positive': emotion_data.get('is_positive', False),
            'emotion_history': emotion_history,
            'memories': memories,
            'additional_context': kwargs
        }
        
        # Ensure emotion_data has all required fields
        if not emotion_data or not isinstance(emotion_data, dict):
            # Default to neutral if no emotion data
            emotion_data = {
                'primary_emotion': 'neutral',
                'is_positive': False,
                'emotion_scores': {}
            }
            
        # Ensure all required keys exist
        if 'primary_emotion' not in emotion_data:
            emotion_data['primary_emotion'] = 'neutral'
        if 'is_positive' not in emotion_data:
            emotion_data['is_positive'] = False
        if 'emotion_scores' not in emotion_data:
            emotion_data['emotion_scores'] = {}
        
        primary_emotion = emotion_data['primary_emotion']
        is_positive = emotion_data['is_positive']
        
        # Generate a personalized response based on emotional context
        personalized_response = self._generate_personalized_response(text, emotion_data, emotion_history)
        
        # Check if we have an override emotion (like 'stressed')
        emotion_to_use = emotion_data.get('override_emotion', primary_emotion)
        
        # Use provided suggested actions if available, otherwise generate generic ones
        if not suggested_actions:
            suggested_actions = self._get_suggested_actions(emotion_to_use)
        
        # Check for emotional state changes
        emotion_changed = False
        previous_emotion = None
        if emotion_history and len(emotion_history) > 0:
            # The first entry in emotion_history is the most recent previous emotion
            previous_emotion = emotion_history[0].get('primary_emotion')
            print(f"Previous emotion from history: {previous_emotion}")
            print(f"Current emotion: {primary_emotion}")
            
            # Check if current emotion is different from the previous one
            if previous_emotion and previous_emotion != primary_emotion:
                emotion_changed = True
                print(f"Emotion changed from {previous_emotion} to {primary_emotion}")
                print(f"Previous emotion details: {emotion_history[0]}")
            else:
                print("No emotion change detected or previous emotion is None")
        
        # Try to use Mental Health dataset for more personalized responses
        if self.using_mental_health and emotion_history and len(emotion_history) >= 2:
            try:
                # If emotion has changed, use transition-specific response
                if emotion_changed and previous_emotion:
                    # Get transition-specific response
                    transition_response = self.mental_health.generate_transition_response(
                        previous_emotion, primary_emotion, user_context
                    )
                    
                    if transition_response:
                        logger.info(f"Using mental health transition response for {previous_emotion} to {primary_emotion}")
                        return transition_response
                
                # If we have enough emotion history, use sequence-specific response
                if len(emotion_history) >= 3:
                    emotion_sequence = [primary_emotion] + [entry.get('primary_emotion') for entry in emotion_history[:4]]
                    sequence_response = self.mental_health.generate_emotion_sequence_response(
                        emotion_sequence, user_context
                    )
                    
                    if sequence_response:
                        logger.info(f"Using mental health sequence response")
                        return sequence_response
            except Exception as e:
                logger.error(f"Error using Mental Health dataset for response generation: {str(e)}")
                
        # Create a more personalized response by adding context about emotional journey
        if emotion_history and not is_positive:
            # Add encouragement based on past positive emotions if current emotion is negative
            positive_history = [state for state in emotion_history if state.get('is_positive', False)]
            if positive_history:
                # Add a reminder of past positive experiences
                personalized_response += f" Remember that you've felt positive emotions before, and you can get there again."
        
        # If emotion has changed, ask what led to the change
        if emotion_changed:
            print(f"Generating response for emotional change from {previous_emotion} to {primary_emotion}")
            
            # Positive to negative transition
            if not is_positive and previous_emotion in ['joy', 'surprise', 'trust', 'anticipation', 'happy', 'excited']:
                change_responses = [
                    f" I notice your emotion has changed from {previous_emotion} to {primary_emotion}. What happened that led to this change?",
                    f" It seems your mood has shifted from {previous_emotion} to {primary_emotion}. Would you like to share what contributed to this?",
                    f" I see that you're feeling {primary_emotion} now, whereas before you were feeling {previous_emotion}. What events led to this change?"
                ]
                personalized_response += random.choice(change_responses)
            
            # Negative to positive transition
            elif is_positive and previous_emotion in ['anger', 'fear', 'sadness', 'disgust', 'stressed', 'anxious']:
                change_responses = [
                    f" I notice your emotion has shifted from {previous_emotion} to {primary_emotion}. What did you do that helped you reach this more positive state?",
                    f" That's wonderful! Your mood has improved from {previous_emotion} to {primary_emotion}. What actions or thoughts helped with this positive change?",
                    f" It's great to see your emotional state improve from {previous_emotion} to {primary_emotion}. What strategies worked for you?"
                ]
                personalized_response += random.choice(change_responses)
            
            # Other transitions
            else:
                change_responses = [
                    f" I notice your emotional state has changed from {previous_emotion} to {primary_emotion}. What do you think contributed to this shift?",
                    f" Your feelings have shifted from {previous_emotion} to {primary_emotion}. What factors do you think influenced this change?",
                    f" I see that your emotion has transitioned from {previous_emotion} to {primary_emotion}. What insights do you have about this change?"
                ]
                personalized_response += random.choice(change_responses)
        
        # Add stress-specific insights if available
        stress_context = kwargs.get('stress_context', {})
        if stress_context and emotion_to_use == 'stressed':
            # Add insights about stress patterns
            stress_frequency = stress_context.get('stress_frequency', 0)
            stress_triggers = stress_context.get('stress_triggers', [])
            stress_recommendations = stress_context.get('stress_recommendations', [])
            
            # Add stress pattern insights
            if stress_frequency > 0.3:  # If stress is frequent (more than 30% of days)
                personalized_response += f" I've noticed that you've been experiencing stress frequently lately."
                
                # Add information about triggers if available
                if stress_triggers:
                    personalized_response += f" Common triggers for your stress appear to be: {', '.join(stress_triggers[:2])}."
                
                # Add a targeted recommendation
                if stress_recommendations:
                    personalized_response += f" {stress_recommendations[0]}"
        
        response_obj = {
            'text': personalized_response,
            'suggested_actions': suggested_actions,
            'emotion_changed': emotion_changed if emotion_changed else False,
            'previous_emotion': previous_emotion if previous_emotion else None,
            'current_emotion': primary_emotion
        }
        
        return response_obj
        
    def _generate_personalized_response(self, text, emotion_data, emotion_history=None):
        """
        Generate a personalized response based on the user's emotional context and history.
        
        Args:
            text (str): The user's input text
            emotion_data (dict): Emotion analysis data
            emotion_history (list): Optional emotional state history
            
        Returns:
            str: A personalized response
        """
        primary_emotion = emotion_data['primary_emotion']
        is_positive = emotion_data['is_positive']
        
        # Log for debugging
        print(f"Generating personalized response for emotion: {primary_emotion}, positive: {is_positive}")
        if emotion_history:
            print(f"Emotion history available with {len(emotion_history)} entries")
            for i, entry in enumerate(emotion_history[:3]):
                print(f"History entry {i}: {entry.get('primary_emotion')}")
        
        # Check if this is specifically about stress
        is_stressed = ('stress' in text.lower() or 'anxious' in text.lower() or 'worried' in text.lower()) and primary_emotion in ['fear', 'sadness']
        
        # Using template-based response generation
        print("Using template-based response generation")
        
        # Generate appropriate response based on emotion using templates
        # Avoid repeating the same template for the same emotion
        if is_stressed:
            # Use stressed templates for stress-specific responses
            available_templates = [t for t in self.stressed_templates if t not in self.last_used_templates.get('stressed', [])]
            if not available_templates:  # If all templates have been used recently
                available_templates = self.stressed_templates
                
            template = random.choice(available_templates)
            print(f"Selected stressed template: {template}")
            
            # Track this template to avoid repetition
            if 'stressed' not in self.last_used_templates:
                self.last_used_templates['stressed'] = []
            self.last_used_templates['stressed'] = [template] + self.last_used_templates['stressed'][:2]
            
            response = template.format(emotion='stressed')
            # Override primary emotion for suggested actions
            emotion_data['override_emotion'] = 'stressed'
        else:
            # Use standard templates for other emotions
            if primary_emotion in ['joy', 'surprise']:
                available_templates = [t for t in self.positive_templates if t not in self.last_used_templates.get(primary_emotion, [])]
                if not available_templates:  # If all templates have been used recently
                    available_templates = self.positive_templates
                    
                template = random.choice(available_templates)
                print(f"Selected positive template: {template}")
            elif primary_emotion in ['anger', 'disgust', 'fear', 'sadness']:
                available_templates = [t for t in self.negative_templates if t not in self.last_used_templates.get(primary_emotion, [])]
                if not available_templates:  # If all templates have been used recently
                    available_templates = self.negative_templates
                    
                template = random.choice(available_templates)
                print(f"Selected negative template: {template}")
            else:
                available_templates = [t for t in self.neutral_templates if t not in self.last_used_templates.get(primary_emotion, [])]
                if not available_templates:  # If all templates have been used recently
                    available_templates = self.neutral_templates
                    
                template = random.choice(available_templates)
                print(f"Selected neutral template: {template}")
            
            # Track this template to avoid repetition
            if primary_emotion not in self.last_used_templates:
                self.last_used_templates[primary_emotion] = []
            self.last_used_templates[primary_emotion] = [template] + self.last_used_templates[primary_emotion][:2]
            
            response = template.format(emotion=primary_emotion)
            
            # Add to template history for debugging
            self.template_history.append({
                'emotion': primary_emotion,
                'template': template,
                'formatted_response': response
            })
            print(f"Template history length: {len(self.template_history)}")
            
        # Add a follow-up question 50% of the time
        if random.random() > 0.5:
            response += " " + random.choice(self.follow_up_questions)
        
        # If we have emotional history, enhance the response with personalized insights
        if emotion_history and len(emotion_history) > 1:
            # Check for patterns in emotional states
            recent_emotions = [state.get('primary_emotion') for state in emotion_history[:5]]
            
            # If there's a pattern of negative emotions
            if all(emotion in ['sadness', 'anger', 'fear', 'disgust'] for emotion in recent_emotions[:3]):
                response += " I've noticed you've been experiencing challenging emotions lately. Let's work together to find ways to improve how you're feeling."
            
            # If there's improvement in emotional state
            if not is_positive and any(state.get('is_positive', False) for state in emotion_history[1:3]):
                response += " It seems your emotions have shifted recently. What do you think contributed to this change?"
            
            # If there's a consistent positive trend
            if is_positive and all(state.get('is_positive', False) for state in emotion_history[:3]):
                response += " You've been maintaining positive emotions consistently. That's wonderful progress!"
        
        return response
        

        
    def _get_suggested_actions(self, emotion, count=3, user_context=None):
        """
        Get suggested actions for the given emotion, enhanced with Mental Health dataset insights.
        
        Args:
            emotion (str): The emotion to get suggestions for
            count (int): Number of suggestions to return
            user_context (dict): Optional user context data for personalization
            
        Returns:
            list: List of suggested actions
        """
        # Try to get personalized suggestions from Mental Health dataset first
        if self.using_mental_health and user_context:
            try:
                # Get personalized suggestions from Mental Health dataset
                personalized_suggestions = self.mental_health.get_personalized_interventions(
                    emotion, user_context
                )
                
                if personalized_suggestions and len(personalized_suggestions) >= count:
                    # Return data-driven personalized suggestions
                    logger.info(f"Using personalized suggestions for {emotion} from Mental Health dataset")
                    return personalized_suggestions[:count]
            except Exception as e:
                logger.error(f"Error getting personalized suggestions from Mental Health dataset: {str(e)}")
        
        # Fallback to standard suggestions if the above doesn't work
        all_suggestions = self.suggested_actions.get(emotion, self.suggested_actions['neutral'])
        
        # Randomly select a subset of suggestions
        if len(all_suggestions) <= count:
            return all_suggestions
        else:
            return random.sample(all_suggestions, count)
            
    def get_transition_response(self, from_emotion, to_emotion, user_context=None):
        """
        Generate a response that addresses the transition between two emotions,
        using insights from the Mental Health dataset.
        
        Args:
            from_emotion (str): The starting emotion
            to_emotion (str): The target emotion
            user_context (dict): Optional user context for personalization
            
        Returns:
            dict: A response object with text and suggested actions
        """
        if self.using_mental_health:
            try:
                # Get transition-specific response from Mental Health dataset
                transition_response = self.mental_health.generate_transition_response(
                    from_emotion, to_emotion, user_context
                )
                
                if transition_response:
                    logger.info(f"Using mental health transition response for {from_emotion} to {to_emotion}")
                    return transition_response
            except Exception as e:
                logger.error(f"Error getting transition response from Mental Health dataset: {str(e)}")
        
        # Fallback to basic transition response
        return self._get_fallback_transition_response(from_emotion, to_emotion, user_context)
    
    def _get_fallback_transition_response(self, from_emotion, to_emotion, user_context=None):
        """
        Generate a fallback transition response if Mental Health dataset is not available.
        """
        # Categorize emotions
        positive_emotions = ['joy', 'surprise', 'trust', 'anticipation', 'happy', 'excited']
        negative_emotions = ['anger', 'disgust', 'fear', 'sadness', 'stressed', 'anxious']
        
        # Build basic response
        response_text = ""
        suggested_actions = []
        
        # Positive to negative transition
        if from_emotion in positive_emotions and to_emotion in negative_emotions:
            responses = [
                f"I notice your emotion has changed from {from_emotion} to {to_emotion}. It's natural for our feelings to fluctuate. What happened that led to this change?",
                f"Your mood seems to have shifted from {from_emotion} to {to_emotion}. Would you like to share what contributed to this?",
                f"It seems you're feeling {to_emotion} now, whereas before you were feeling {from_emotion}. What events led to this change?"
            ]
            response_text = random.choice(responses)
            suggested_actions = self._get_suggested_actions(to_emotion)
            
        # Negative to positive transition
        elif from_emotion in negative_emotions and to_emotion in positive_emotions:
            responses = [
                f"I notice your emotion has shifted from {from_emotion} to {to_emotion}. That's great! What did you do that helped you reach this more positive state?",
                f"That's wonderful! Your mood has improved from {from_emotion} to {to_emotion}. What actions or thoughts helped with this positive change?",
                f"It's great to see your emotional state improve from {from_emotion} to {to_emotion}. What strategies worked for you?"
            ]
            response_text = random.choice(responses)
            suggested_actions = self._get_suggested_actions(to_emotion)
            
        # Other transitions
        else:
            responses = [
                f"I notice your emotional state has changed from {from_emotion} to {to_emotion}. What do you think contributed to this shift?",
                f"Your feelings have shifted from {from_emotion} to {to_emotion}. What factors do you think influenced this change?",
                f"I see that your emotion has transitioned from {from_emotion} to {to_emotion}. What insights do you have about this change?"
            ]
            response_text = random.choice(responses)
            suggested_actions = self._get_suggested_actions(to_emotion)
        
        return {
            'text': response_text,
            'suggested_actions': suggested_actions,
            'emotion_changed': True,
            'from_emotion': from_emotion,
            'to_emotion': to_emotion,
            'source': 'fallback'
        }
    
    def get_emotion_sequence_response(self, emotion_sequence, user_context=None):
        """
        Generate a response that addresses a sequence of emotions over time,
        using insights from the Mental Health dataset.
        
        Args:
            emotion_sequence (list): List of emotions in chronological order
            user_context (dict): Optional user context for personalization
            
        Returns:
            dict: A response object with text, insights, and suggested actions
        """
        if not emotion_sequence or len(emotion_sequence) < 2:
            return {
                'text': "I don't have enough information about your emotional journey yet. Keep sharing how you feel.",
                'suggested_actions': self._get_suggested_actions('neutral'),
                'insights': [],
                'patterns': [],
                'source': 'insufficient_data'
            }
        
        if self.using_mental_health:
            try:
                # Get sequence-specific response from Mental Health dataset
                sequence_response = self.mental_health.generate_emotion_sequence_response(
                    emotion_sequence, user_context
                )
                
                if sequence_response:
                    logger.info(f"Using mental health sequence response for a sequence of {len(emotion_sequence)} emotions")
                    return sequence_response
            except Exception as e:
                logger.error(f"Error getting sequence response from Mental Health dataset: {str(e)}")
        
        # Fallback to basic sequence analysis response
        return self._get_fallback_sequence_response(emotion_sequence, user_context)
    
    def _get_fallback_sequence_response(self, emotion_sequence, user_context=None):
        """
        Generate a fallback sequence response if Mental Health dataset is not available.
        """
        # Categorize emotions
        positive_emotions = ['joy', 'surprise', 'trust', 'anticipation', 'happy', 'excited']
        negative_emotions = ['anger', 'disgust', 'fear', 'sadness', 'stressed', 'anxious']
        neutral_emotions = ['neutral']
        
        # Simple analysis
        current_emotion = emotion_sequence[-1]
        positive_count = sum(1 for e in emotion_sequence if e in positive_emotions)
        negative_count = sum(1 for e in emotion_sequence if e in negative_emotions)
        
        # Check for patterns
        patterns = []
        insights = []
        
        # Consistent negativity
        if negative_count >= len(emotion_sequence) * 0.7:
            patterns.append('persistent_negative')
            insights.append("You've been experiencing predominantly negative emotions lately.")
        
        # Consistent positivity
        if positive_count >= len(emotion_sequence) * 0.7:
            patterns.append('persistent_positive')
            insights.append("You've been maintaining predominantly positive emotions lately.")
        
        # Volatility (frequent changes)
        changes = sum(1 for i in range(len(emotion_sequence)-1) if emotion_sequence[i] != emotion_sequence[i+1])
        if changes >= len(emotion_sequence) * 0.6:
            patterns.append('emotional_volatility')
            insights.append("Your emotions have been changing frequently.")
        
        # Improvement trend (from negative to positive)
        if len(emotion_sequence) >= 3 and all(e in negative_emotions for e in emotion_sequence[:2]) and any(e in positive_emotions for e in emotion_sequence[-2:]):
            patterns.append('improvement_trend')
            insights.append("There seems to be a positive trend in your emotional journey.")
        
        # Deterioration trend (from positive to negative)
        if len(emotion_sequence) >= 3 and all(e in positive_emotions for e in emotion_sequence[:2]) and any(e in negative_emotions for e in emotion_sequence[-2:]):
            patterns.append('deterioration_trend')
            insights.append("There appears to be a shift toward more challenging emotions recently.")
        
        # Build response based on patterns
        response_text = f"Based on your recent emotional journey, "
        
        if 'persistent_negative' in patterns:
            response_text += "you've been experiencing consistent challenging emotions. It's important to acknowledge these feelings and consider reaching out for support if needed. "
            suggested_actions = self._get_suggested_actions('sadness')
        elif 'persistent_positive' in patterns:
            response_text += "you've been maintaining a positive emotional state. That's wonderful! What activities or practices do you think are contributing to this?"
            suggested_actions = self._get_suggested_actions('joy')
        elif 'improvement_trend' in patterns:
            response_text += "I notice an improvement in your emotional state. What changes or strategies do you think helped with this positive shift?"
            suggested_actions = self._get_suggested_actions(current_emotion)
        elif 'deterioration_trend' in patterns:
            response_text += "I notice your emotions have become more challenging recently. What factors might be contributing to this change?"
            suggested_actions = self._get_suggested_actions(current_emotion)
        elif 'emotional_volatility' in patterns:
            response_text += "your emotions have been fluctuating frequently. This kind of emotional volatility can sometimes be challenging. Would developing emotional regulation strategies be helpful for you?"
            suggested_actions = ["Practice mindfulness meditation", "Maintain a regular sleep schedule", "Identify emotion triggers in your journal"]
        else:
            response_text += "I notice a mix of different emotions in your journey. Reflecting on these patterns might provide valuable insights about your wellbeing."
            suggested_actions = self._get_suggested_actions(current_emotion)
        
        return {
            'text': response_text,
            'suggested_actions': suggested_actions,
            'insights': insights,
            'patterns': patterns,
            'source': 'fallback'
        }
        
    def get_intervention_effectiveness(self, emotion, intervention, user_context=None):
        """
        Get the effectiveness data for a specific intervention for a given emotion,
        using insights from the Mental Health dataset.
        
        Args:
            emotion (str): The target emotion
            intervention (str): The intervention to evaluate
            user_context (dict): Optional user context for personalization
            
        Returns:
            dict: Effectiveness data including score and supporting evidence
        """
        if self.using_mental_health:
            try:
                # Get intervention effectiveness from Mental Health dataset
                effectiveness_data = self.mental_health.get_intervention_effectiveness(
                    emotion, intervention, user_context
                )
                
                if effectiveness_data:
                    logger.info(f"Using mental health effectiveness data for {intervention} on {emotion}")
                    return effectiveness_data
            except Exception as e:
                logger.error(f"Error getting intervention effectiveness from Mental Health dataset: {str(e)}")
        
        # Fallback to basic effectiveness estimation
        return self._get_fallback_intervention_effectiveness(emotion, intervention)
    
    def _get_fallback_intervention_effectiveness(self, emotion, intervention):
        """
        Generate fallback intervention effectiveness if Mental Health dataset is not available.
        """
        # Map of common interventions to their general effectiveness for different emotions
        effectiveness_map = {
            'meditation': {
                'anger': 0.7,
                'anxiety': 0.8,
                'sadness': 0.6,
                'stress': 0.75,
                'default': 0.65
            },
            'exercise': {
                'sadness': 0.8,
                'anxiety': 0.75,
                'stress': 0.85,
                'anger': 0.7,
                'default': 0.7
            },
            'social': {
                'sadness': 0.85,
                'loneliness': 0.9,
                'anxiety': 0.6,
                'default': 0.65
            },
            'nature': {
                'stress': 0.8,
                'anxiety': 0.7,
                'sadness': 0.65,
                'default': 0.7
            },
            'creative': {
                'sadness': 0.7,
                'stress': 0.65,
                'anger': 0.6,
                'default': 0.6
            },
            'default': 0.5
        }
        
        # Determine intervention category
        intervention_category = 'default'
        intervention_lower = intervention.lower()
        
        if any(word in intervention_lower for word in ['meditate', 'mindful', 'breathing', 'relax', 'calm']):
            intervention_category = 'meditation'
        elif any(word in intervention_lower for word in ['exercise', 'walk', 'run', 'gym', 'physical', 'yoga']):
            intervention_category = 'exercise'
        elif any(word in intervention_lower for word in ['friend', 'family', 'social', 'connect', 'talk', 'share']):
            intervention_category = 'social'
        elif any(word in intervention_lower for word in ['nature', 'outside', 'outdoor', 'park', 'garden']):
            intervention_category = 'nature'
        elif any(word in intervention_lower for word in ['art', 'music', 'write', 'create', 'draw', 'paint', 'play']):
            intervention_category = 'creative'
        
        # Get effectiveness score
        if intervention_category in effectiveness_map:
            category_map = effectiveness_map[intervention_category]
            effectiveness = category_map.get(emotion, category_map.get('default', 0.5))
        else:
            effectiveness = effectiveness_map['default']
        
        # Generate supporting evidence
        evidence = []
        
        if effectiveness >= 0.8:
            evidence.append("Research suggests this is highly effective for many people")
        elif effectiveness >= 0.65:
            evidence.append("Studies indicate this can be moderately effective")
        else:
            evidence.append("This may help some individuals, though effects vary")
        
        # Add emotion-specific evidence
        if intervention_category == 'meditation' and emotion in ['anxiety', 'stress']:
            evidence.append("Mindfulness practices have been shown to reduce stress and anxiety symptoms")
        elif intervention_category == 'exercise' and emotion in ['sadness', 'depression']:
            evidence.append("Physical activity can help release endorphins that improve mood")
        elif intervention_category == 'social' and emotion in ['sadness', 'loneliness']:
            evidence.append("Social connection is linked to reduced depression symptoms")
        
        return {
            'effectiveness_score': effectiveness,
            'supporting_evidence': evidence,
            'confidence': 'medium',
            'source': 'fallback'
        }
