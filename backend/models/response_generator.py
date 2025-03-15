import random

class ResponseGenerator:
    """
    Class for generating responses based on user input and emotion analysis.
    In a production environment, this would use GPT or a similar model.
    """
    
    def __init__(self):
        # Define response templates for different emotions
        self.positive_templates = [
            "That's wonderful! I'm glad to hear you're feeling {emotion}. What made you feel this way?",
            "It's great that you're experiencing {emotion}! Would you like to share more about it?",
            "I'm happy to see you're feeling {emotion}. How can you maintain this positive energy?",
            "That sounds really positive! How does this {emotion} compare to how you felt yesterday?",
            "It's always nice to feel {emotion}. What's one thing you're grateful for right now?"
        ]
        
        self.negative_templates = [
            "I'm sorry to hear you're feeling {emotion}. Would you like to talk more about what's bothering you?",
            "It sounds like you're going through a difficult time. Remember that it's okay to feel {emotion} sometimes.",
            "I notice you're feeling {emotion}. What's one small thing that might help you feel better?",
            "When you feel {emotion}, it can be helpful to remember past times when you overcame similar feelings.",
            "I'm here for you during this {emotion}. What support do you need right now?"
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
        
    def generate_with_memory(self, text, emotion_data, memories=None, suggested_actions=None, emotion_history=None):
        """
        Generate a personalized response incorporating emotional history and suggested actions.
        
        Args:
            text (str): The user's input text
            emotion_data (dict): Emotion analysis data
            memories (list): Optional memory data for context
            suggested_actions (list): Optional suggested actions from emotional graph
            emotion_history (list): Optional emotional state history
            
        Returns:
            dict: A response object with text and suggested actions
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
        
        # Generate a personalized response based on emotional context
        personalized_response = self._generate_personalized_response(text, emotion_data, emotion_history)
        
        # Use provided suggested actions if available, otherwise generate generic ones
        if not suggested_actions:
            suggested_actions = self._get_suggested_actions(primary_emotion)
        
        # Create a more personalized response by adding context about emotional journey
        if emotion_history and not is_positive:
            # Add encouragement based on past positive emotions if current emotion is negative
            positive_history = [state for state in emotion_history if state.get('is_positive', False)]
            if positive_history:
                # Add a reminder of past positive experiences
                personalized_response += f" Remember that you've felt positive emotions before, and you can get there again."
        
        response_obj = {
            'text': personalized_response,
            'suggested_actions': suggested_actions
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
        
        # Start with a base response
        base_response = self.generate(text, emotion_data)
        
        # If we have emotional history, enhance the response with personalized insights
        if emotion_history and len(emotion_history) > 1:
            # Check for patterns in emotional states
            recent_emotions = [state.get('primary_emotion') for state in emotion_history[:5]]
            
            # If there's a pattern of negative emotions
            if all(emotion in ['sadness', 'anger', 'fear', 'disgust'] for emotion in recent_emotions[:3]):
                base_response += " I've noticed you've been experiencing challenging emotions lately. Let's work together to find ways to improve how you're feeling."
            
            # If there's improvement in emotional state
            if not is_positive and any(state.get('is_positive', False) for state in emotion_history[1:3]):
                base_response += " It seems your emotions have shifted recently. What do you think contributed to this change?"
            
            # If there's a consistent positive trend
            if is_positive and all(state.get('is_positive', False) for state in emotion_history[:3]):
                base_response += " You've been maintaining positive emotions consistently. That's wonderful progress!"
        
        return base_response
        
    def _get_suggested_actions(self, emotion, count=3):
        """
        Get suggested actions for the given emotion.
        
        Args:
            emotion (str): The emotion to get suggestions for
            count (int): Number of suggestions to return
            
        Returns:
            list: List of suggested actions
        """
        # Get suggestions for the emotion, or default to neutral
        all_suggestions = self.suggested_actions.get(emotion, self.suggested_actions['neutral'])
        
        # Randomly select a subset of suggestions
        if len(all_suggestions) <= count:
            return all_suggestions
        else:
            return random.sample(all_suggestions, count)
