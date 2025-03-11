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
        
    def generate_with_memory(self, text, emotion_data, memories):
        """
        Generate a response that incorporates past memories.
        
        Args:
            text (str): The user's input text
            emotion_data (dict): Emotion analysis data
            memories (list): List of relevant memories
            
        Returns:
            dict: A response object with text and memory data
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
            
        # Get base response
        base_response = self.generate(text, emotion_data)
        response_obj = {
            'text': base_response,
            'memory': None
        }
        
        # If there are memories, determine how to use them based on emotional state
        if memories and len(memories) > 0:
            try:
                # For negative emotions, provide encouraging memories
                if not emotion_data['is_positive']:
                    memory = random.choice(memories)
                    memory_reference = f"I remember that on {memory.get('date', 'a previous day')}, you wrote about feeling {memory.get('emotion', 'good')} when {memory.get('summary', 'something positive happened')}. Perhaps reflecting on that positive experience might help now."
                    
                    # Add memory data to response object
                    response_obj['memory'] = {
                        'type': 'encouragement',
                        'data': memory,
                        'message': memory_reference
                    }
                
                # For positive emotions, sometimes reinforce with similar positive memories
                elif emotion_data['is_positive'] and random.random() > 0.7:  # 30% chance
                    memory = random.choice(memories)
                    memory_reference = f"It's great to see you feeling {emotion_data['primary_emotion']}! This reminds me of {memory.get('date', 'a previous day')} when you also felt {memory.get('emotion', 'good')} about {memory.get('summary', 'something positive')}."
                    
                    # Add memory data to response object
                    response_obj['memory'] = {
                        'type': 'reinforcement',
                        'data': memory,
                        'message': memory_reference
                    }
            except Exception as e:
                print(f"Error processing memories: {str(e)}")
                # Continue without memory if there's an error
        
        return response_obj
