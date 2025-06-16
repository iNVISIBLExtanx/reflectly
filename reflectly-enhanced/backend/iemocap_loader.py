"""
IEMOCAP Dataset Loader and Processor
====================================

This module handles loading and processing the IEMOCAP Emotional Speech Dataset
for validating emotion recognition and pathfinding algorithms.

Requirements:
- pandas
- numpy
- scipy
- librosa (for audio processing)
- scikit-learn
- nltk

Install: pip install pandas numpy scipy librosa scikit-learn nltk
"""

import os
import pandas as pd
import numpy as np
import json
import re
from collections import defaultdict, Counter
from datetime import datetime
import librosa
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    print("NLTK download failed, some features may not work")

class IEMOCAPDatasetLoader:
    """
    Loads and processes IEMOCAP dataset for emotion recognition validation
    """
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.data = None
        self.processed_data = None
        self.emotion_mapping = {
            'ang': 'angry',
            'hap': 'happy', 
            'sad': 'sad',
            'neu': 'neutral',
            'exc': 'happy',  # excitement mapped to happy
            'fru': 'angry',  # frustration mapped to angry
            'fea': 'anxious', # fear mapped to anxious
            'sur': 'confused', # surprise mapped to confused
            'dis': 'angry',   # disgust mapped to angry
            'oth': 'neutral'  # other mapped to neutral
        }
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def load_dataset(self):
        """
        Load IEMOCAP dataset from CSV or directory structure
        """
        try:
            # Check for iemocap_full_dataset.csv
            csv_path = os.path.join(self.dataset_path, 'iemocap_full_dataset.csv')
            if os.path.exists(csv_path):
                raw_data = pd.read_csv(csv_path)
                print(f"Loaded {len(raw_data)} samples from CSV at {csv_path}")
                
                # Transform into expected format
                self.data = pd.DataFrame()
                self.data['filename'] = raw_data['path'].apply(lambda x: os.path.basename(x) if isinstance(x, str) else '')
                self.data['text'] = ''  # Initialize empty text column, will be populated if possible
                self.data['emotion'] = raw_data['emotion']
                self.data['session'] = raw_data['session']
                self.data['speaker'] = raw_data['gender']
                
                # Look for transcription files if available
                for i, row in self.data.iterrows():
                    wav_path = row['filename']
                    try:
                        # Try to find matching transcript file
                        transcript_path = os.path.join(self.dataset_path, 'transcripts',
                                                     f"{os.path.splitext(wav_path)[0]}.txt")
                        if os.path.exists(transcript_path):
                            with open(transcript_path, 'r', encoding='utf-8') as f:
                                self.data.at[i, 'text'] = f.read().strip()
                    except Exception as e:
                        # If transcript not found, leave the text field empty
                        pass
            else:
                # Legacy loading from directory structure
                self.data = self._load_from_directory()
                print(f"Loaded {len(self.data)} samples from directory")
                
            # Filter out rows with 'xxx' emotion (unclassified)
            self.data = self.data[self.data['emotion'] != 'xxx']
                
            # Standardize emotion labels
            self.data['emotion_mapped'] = self.data['emotion'].map(
                lambda x: self.emotion_mapping.get(x.lower()[:3], 'neutral') if isinstance(x, str) else 'neutral'
            )
            
            return len(self.data) > 0
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return False
    
    def _load_from_directory(self):
        """
        Load dataset from IEMOCAP directory structure
        This is a simplified version - adjust based on actual dataset structure
        """
        data_records = []
        
        # Walk through dataset directory
        for root, dirs, files in os.walk(self.dataset_path):
            for file in files:
                if file.endswith('.txt'):  # Transcription files
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            
                        # Extract emotion from filename or directory
                        emotion = self._extract_emotion_from_path(file_path)
                        session = self._extract_session_from_path(file_path)
                        speaker = self._extract_speaker_from_path(file_path)
                        
                        data_records.append({
                            'filename': file,
                            'text': content,
                            'emotion': emotion,
                            'session': session,
                            'speaker': speaker
                        })
                        
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        continue
        
        return pd.DataFrame(data_records)
    
    def _extract_emotion_from_path(self, file_path):
        """Extract emotion label from file path"""
        # This would be customized based on actual IEMOCAP structure
        # For now, using a simple pattern
        emotions = ['ang', 'hap', 'sad', 'neu', 'exc', 'fru', 'fea', 'sur', 'dis']
        for emotion in emotions:
            if emotion in file_path.lower():
                return emotion
        return 'neu'
    
    def _extract_session_from_path(self, file_path):
        """Extract session info from file path"""
        match = re.search(r'Session(\d+)', file_path)
        return match.group(1) if match else 'unknown'
    
    def _extract_speaker_from_path(self, file_path):
        """Extract speaker info from file path"""
        match = re.search(r'[MF]\d+', file_path)
        return match.group(0) if match else 'unknown'
    
    def preprocess_data(self):
        """
        Preprocess the loaded data for emotion recognition and action extraction
        """
        if self.data is None or len(self.data) == 0:
            print("No data loaded. Call load_dataset() first.")
            return False
        
        print("Preprocessing dataset...")
        
        try:
            # Clean and process text
            self.data['text_cleaned'] = self.data['text'].fillna('').apply(self._clean_text)
            
            # Extract potential actions from text
            self.data['extracted_actions'] = self.data['text_cleaned'].apply(
                self._extract_actions_ml
            )
            
            # Calculate text features
            self.data['text_length'] = self.data['text'].fillna('').str.len()
            self.data['word_count'] = self.data['text_cleaned'].str.split().str.len()
            
            # If there's no text, generate synthetic data for testing purposes
            if self.data['text_length'].sum() == 0:
                print("Warning: No text data found. Generating placeholder actions for testing.")
                # Assign random actions based on emotion
                action_map = {
                    'angry': ['argue', 'shout', 'complain', 'criticize'],
                    'happy': ['smile', 'laugh', 'celebrate', 'praise'],
                    'sad': ['cry', 'sigh', 'withdraw', 'mourn'],
                    'neutral': ['talk', 'discuss', 'consider', 'observe'],
                    'anxious': ['worry', 'fidget', 'panic', 'hesitate'],
                    'confused': ['question', 'wonder', 'examine', 'ponder']
                }
                
                # Assign synthetic actions
                def assign_actions(emotion):
                    import random
                    emotion_key = emotion if emotion in action_map else 'neutral'
                    actions = action_map.get(emotion_key, [])
                    num_actions = random.randint(1, 3) if actions else 0
                    return random.sample(actions, min(num_actions, len(actions)))
                
                self.data['extracted_actions'] = self.data['emotion_mapped'].apply(assign_actions)
            
            # Group by emotion for analysis
            emotion_groups = self.data.groupby('emotion_mapped')
            
            self.processed_data = {
                'emotion_distribution': emotion_groups.size().to_dict(),
                'avg_text_length': emotion_groups['text_length'].mean().to_dict(),
                'common_actions': self._extract_common_actions(),
                'emotion_transitions': self._build_emotion_transitions(),
                'dataset_stats': {
                    'total_samples': len(self.data),
                    'unique_emotions': self.data['emotion_mapped'].nunique(),
                    'sessions': self.data['session'].nunique(),
                    'speakers': self.data['speaker'].nunique()
                }
            }
            
            print("Preprocessing completed!")
            return True
            
        except Exception as e:
            print(f"Error during preprocessing: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        if pd.isna(text) or text == '':
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s\.\,\!\?]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_actions_ml(self, text):
        """
        Extract potential actions using ML-based approach
        """
        actions = []
        
        # Return empty list if no text content
        if not text or text == "":
            return actions
        
        # Tokenize sentences
        try:
            sentences = sent_tokenize(text)
        except:
            return actions  # Return empty if tokenization fails
        
        for sentence in sentences:
            try:
                words = word_tokenize(sentence.lower())
                
                # Look for action patterns
                action_patterns = [
                    r'\b(i|we|he|she|they)\s+(am|is|are|was|were|will|would|should|could|might)\s+(\w+ing)\b',
                    r'\b(i|we|he|she|they)\s+(go|went|come|came|run|ran|walk|walked|talk|talked|think|thought)\b',
                    r'\b(i|we|he|she|they)\s+(feel|felt|seem|seemed|look|looked|sound|sounded)\s+(\w+)\b',
                    r'\b(let\'s|should|could|might|would)\s+(\w+)\b',
                    r'\b(try|tried|attempt|attempted|decide|decided|choose|chose)\s+to\s+(\w+)\b'
                ]
                
                for pattern in action_patterns:
                    matches = re.findall(pattern, sentence)
                    for match in matches:
                        if isinstance(match, tuple):
                            # Extract the action verb from the match
                            action = match[-1] if match else ""
                        else:
                            action = match
                        
                        if action and action not in self.stop_words and len(action) > 2:
                            actions.append(self.lemmatizer.lemmatize(action, 'v'))
            except Exception as e:
                continue  # Skip this sentence if processing fails
        
        return list(set(actions))  # Remove duplicates
    
    def _extract_common_actions(self):
        """Extract most common actions for each emotion"""
        emotion_actions = defaultdict(list)
        
        for _, row in self.data.iterrows():
            emotion = row['emotion_mapped']
            actions = row['extracted_actions']
            if actions:
                emotion_actions[emotion].extend(actions)
        
        # Get top actions for each emotion
        common_actions = {}
        for emotion, actions in emotion_actions.items():
            action_counts = Counter(actions)
            common_actions[emotion] = action_counts.most_common(10)
        
        return common_actions
    
    def _build_emotion_transitions(self):
        """
        Build emotion transitions based on session data
        """
        transitions = defaultdict(int)
        
        # Group by session and speaker
        session_groups = self.data.groupby(['session', 'speaker'])
        
        for (session, speaker), group in session_groups:
            # Sort by filename (assuming chronological order)
            group_sorted = group.sort_values('filename')
            emotions = group_sorted['emotion_mapped'].tolist()
            
            # Count transitions
            for i in range(len(emotions) - 1):
                from_emotion = emotions[i]
                to_emotion = emotions[i + 1]
                if from_emotion != to_emotion:  # Only count actual transitions
                    # Use string representation of tuple as key instead of tuple itself
                    transitions[f"{from_emotion}_to_{to_emotion}"] += 1
        
        return dict(transitions)
    
    def generate_emotional_map(self):
        """
        Generate comprehensive emotional map for algorithm testing
        """
        if self.processed_data is None:
            print("Data not preprocessed. Call preprocess_data() first.")
            return None
        
        emotional_map = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "dataset": "IEMOCAP",
                "total_samples": self.processed_data['dataset_stats']['total_samples'],
                "processing_date": datetime.now().isoformat()
            }
        }
        
        # Create nodes for each emotion
        for emotion, count in self.processed_data['emotion_distribution'].items():
            emotional_map["nodes"].append({
                "id": emotion,
                "label": emotion.title(),
                "count": int(count),
                "avg_text_length": self.processed_data['avg_text_length'].get(emotion, 0),
                "common_actions": [action for action, _ in 
                                 self.processed_data['common_actions'].get(emotion, [])[:5]]
            })
        
        # Create edges for transitions
        for key, count in self.processed_data['emotion_transitions'].items():
            # Parse from and to emotions from the key string format "from_to_to"
            parts = key.split('_to_')
            if len(parts) == 2:
                from_emotion, to_emotion = parts
                if count > 0:  # Only include transitions that occurred
                    emotional_map["edges"].append({
                        "from": from_emotion,
                        "to": to_emotion,
                        "weight": int(count),
                        "actions": [action for action, _ in 
                                   self.processed_data['common_actions'].get(from_emotion, [])[:3]]
                    })
        
        return emotional_map
    
    def export_for_validation(self, output_path: str):
        """
        Export processed data for algorithm validation
        """
        if self.processed_data is None:
            print("No processed data to export")
            return False
        
        try:
            # Create validation dataset
            validation_data = {
                "conversations": [],
                "emotional_map": self.generate_emotional_map(),
                "statistics": self.processed_data
            }
            
            # Sample conversations for testing
            session_groups = self.data.groupby('session')
            for session_id, group in list(session_groups)[:10]:  # Take first 10 sessions
                group_sorted = group.sort_values('filename')
                
                conversation = {
                    "session_id": session_id,
                    "turns": []
                }
                
                for _, row in group_sorted.iterrows():
                    conversation["turns"].append({
                        "text": row['text'],
                        "emotion": row['emotion_mapped'],
                        "actions": row['extracted_actions'],
                        "speaker": row['speaker']
                    })
                
                validation_data["conversations"].append(conversation)
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(validation_data, f, indent=2, ensure_ascii=False)
            
            print(f"Validation data exported to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def get_dataset_summary(self):
        """Get summary statistics of the dataset"""
        if self.data is None:
            return "No data loaded"
        
        summary = {
            "total_samples": len(self.data),
            "emotion_distribution": self.data['emotion_mapped'].value_counts().to_dict(),
            "average_text_length": self.data['text'].str.len().mean(),
            "sessions": self.data['session'].nunique(),
            "speakers": self.data['speaker'].nunique()
        }
        
        return summary

# Usage Example:
if __name__ == "__main__":
    # Initialize loader
    loader = IEMOCAPDatasetLoader("/path/to/iemocap/dataset")
    
    # Load and process dataset
    if loader.load_dataset():
        loader.preprocess_data()
        
        # Generate emotional map
        emotional_map = loader.generate_emotional_map()
        print("Generated emotional map with", len(emotional_map["nodes"]), "emotions")
        
        # Export for validation
        loader.export_for_validation("iemocap_validation_data.json")
        
        # Print summary
        summary = loader.get_dataset_summary()
        print("Dataset Summary:", summary)