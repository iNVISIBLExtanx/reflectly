#!/usr/bin/env python3

import os
import sys

def fix_unknown_emotions():
    # Path to the search algorithm file
    search_algorithm_path = os.path.join("models", "search_algorithm.py")
    agent_service_path = os.path.join("services", "agent_service.py")
    
    # Update the search algorithm to handle unknown emotions
    if os.path.exists(search_algorithm_path):
        with open(search_algorithm_path, "r") as f:
            content = f.read()
        
        # Add emotion mapping to the get_default_action method
        if "emotion_mapping" not in content:
            content = content.replace("def get_default_action(self, from_emotion, to_emotion):", 
                                    "def get_default_action(self, from_emotion, to_emotion):\n        # Map unknown emotions to standard emotions\n        emotion_mapping = {\n            # Positive emotions\n            \"happy\": \"joy\",\n            \"excited\": \"joy\",\n            \"content\": \"joy\",\n            \"calm\": \"neutral\",\n            # Negative emotions\n            \"stressed\": \"fear\",\n            \"anxious\": \"fear\",\n            \"worried\": \"fear\",\n            \"depressed\": \"sadness\",\n            \"frustrated\": \"anger\",\n            \"annoyed\": \"anger\",\n            \"disgusted\": \"disgust\"\n        }\n        \n        # Map emotions if they are in the mapping\n        mapped_from = emotion_mapping.get(from_emotion, from_emotion)\n        mapped_to = emotion_mapping.get(to_emotion, to_emotion)")
            
            # Update references to from_emotion and to_emotion
            content = content.replace("default_actions.get((from_emotion, to_emotion))", 
                                    "default_actions.get((mapped_from, mapped_to))")
            
            with open(search_algorithm_path, "w") as f:
                f.write(content)
            print(f"Updated SearchAlgorithm.get_default_action to handle unknown emotions at {search_algorithm_path}")
    
    # Update the agent service to handle unknown emotions
    if os.path.exists(agent_service_path):
        with open(agent_service_path, "r") as f:
            content = f.read()
        
        # Add emotion mapping to the create_action_plan method
        if "emotion_mapping" not in content:
            content = content.replace("def create_action_plan(self, user_email, current_emotion, target_emotion):", 
                                    "def create_action_plan(self, user_email, current_emotion, target_emotion):\n        # Map unknown emotions to standard emotions\n        emotion_mapping = {\n            # Positive emotions\n            \"happy\": \"joy\",\n            \"excited\": \"joy\",\n            \"content\": \"joy\",\n            \"calm\": \"neutral\",\n            # Negative emotions\n            \"stressed\": \"fear\",\n            \"anxious\": \"fear\",\n            \"worried\": \"fear\",\n            \"depressed\": \"sadness\",\n            \"frustrated\": \"anger\",\n            \"annoyed\": \"anger\",\n            \"disgusted\": \"disgust\"\n        }\n        \n        # Map emotions if they are in the mapping\n        mapped_current = emotion_mapping.get(current_emotion, current_emotion)\n        mapped_target = emotion_mapping.get(target_emotion, target_emotion)")
            
            # Update references to current_emotion and target_emotion
            content = content.replace("action_plan = self.planner.create_plan(user_email, current_emotion, target_emotion)", 
                                    "action_plan = self.planner.create_plan(user_email, mapped_current, mapped_target)")
            
            with open(agent_service_path, "w") as f:
                f.write(content)
            print(f"Updated AgentService.create_action_plan to handle unknown emotions at {agent_service_path}")
    
    print("Unknown emotions fixes applied")

if __name__ == "__main__":
    fix_unknown_emotions()
