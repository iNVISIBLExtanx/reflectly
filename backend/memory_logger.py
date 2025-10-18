"""
Enhanced Memory Logger with Temporal Features
Persistent storage of experiences, transitions, and temporal features
for better learning and GNN training
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import threading
import time

from config import MemoryConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryLogger:
    """
    Enhanced memory logger with persistence and temporal features
    Logs transition success rates, temporal patterns, and user behavior
    """
    
    def __init__(self):
        """Initialize memory logger"""
        MemoryConfig.ensure_data_directory()
        
        # In-memory storage
        self.memory_map = {
            'emotional_states': {},
            'transitions': {},
            'user_experiences': [],
            'graph_connections': defaultdict(list),
            'algorithm_comparisons': []
        }
        
        # Temporal features tracking
        self.temporal_features = {
            'transition_patterns': {},  # Time-of-day patterns
            'success_rates_over_time': {},  # How success rates change
            'user_activity_patterns': {}  # When user is most active
        }
        
        # Statistics
        self.stats = {
            'total_experiences': 0,
            'total_transitions': 0,
            'last_save_time': None,
            'last_cleanup_time': None
        }
        
        # Load existing data
        self._load_memory()
        
        # Auto-save thread
        if MemoryConfig.AUTO_SAVE:
            self._start_autosave_thread()
        
        logger.info("Memory Logger initialized")
    
    def log_experience(self, experience: Dict) -> str:
        """
        Log a user experience
        
        Args:
            experience: Experience dictionary with emotion, text, etc.
            
        Returns:
            Experience ID
        """
        # Add timestamp if not present
        if 'timestamp' not in experience:
            experience['timestamp'] = datetime.now().isoformat()
        
        # Store in memory
        self.memory_map['user_experiences'].append(experience)
        
        # Update emotional states
        emotion = experience.get('emotion', 'neutral')
        if emotion not in self.memory_map['emotional_states']:
            self.memory_map['emotional_states'][emotion] = []
        self.memory_map['emotional_states'][emotion].append(experience)
        
        # Update statistics
        self.stats['total_experiences'] += 1
        
        # Track temporal patterns
        self._update_activity_patterns(experience)
        
        logger.debug(f"Logged experience: {experience['id']}, emotion: {emotion}")
        
        return experience['id']
    
    def log_transition(self, from_emotion: str, to_emotion: str, 
                      actions: List[str], experience_id: str,
                      success_count: int = 1) -> None:
        """
        Log an emotional transition with actions
        
        Args:
            from_emotion: Starting emotion
            to_emotion: Target emotion
            actions: List of actions taken
            experience_id: Associated experience ID
            success_count: Initial success count (default 1)
        """
        transition_key = (from_emotion, to_emotion)
        
        if transition_key not in self.memory_map['transitions']:
            self.memory_map['transitions'][transition_key] = []
        
        timestamp = datetime.now().isoformat()
        
        for action in actions:
            # Check if action already exists
            existing_action = None
            for act in self.memory_map['transitions'][transition_key]:
                if act['action'] == action:
                    existing_action = act
                    break
            
            if existing_action:
                # Update existing action
                existing_action['success_count'] += success_count
                existing_action['last_used'] = timestamp
                existing_action['use_count'] = existing_action.get('use_count', 1) + 1
            else:
                # Add new action
                action_record = {
                    'action': action,
                    'success_count': success_count,
                    'timestamp': timestamp,
                    'last_used': timestamp,
                    'use_count': 1,
                    'experience_id': experience_id
                }
                self.memory_map['transitions'][transition_key].append(action_record)
        
        # Update graph connections
        if to_emotion not in self.memory_map['graph_connections'][from_emotion]:
            self.memory_map['graph_connections'][from_emotion].append(to_emotion)
        
        # Update statistics
        self.stats['total_transitions'] += 1
        
        # Track temporal transition patterns
        self._update_transition_patterns(from_emotion, to_emotion, timestamp)
        
        logger.debug(f"Logged transition: {from_emotion} -> {to_emotion}")
    
    def update_transition_success(self, from_emotion: str, to_emotion: str,
                                 action: str, success: bool = True) -> None:
        """
        Update success rate for a specific transition action
        
        Args:
            from_emotion: Starting emotion
            to_emotion: Target emotion
            action: The action taken
            success: Whether the action was successful
        """
        transition_key = (from_emotion, to_emotion)
        
        if transition_key not in self.memory_map['transitions']:
            logger.warning(f"Transition {transition_key} not found")
            return
        
        # Find and update the action
        for act in self.memory_map['transitions'][transition_key]:
            if act['action'] == action:
                if success:
                    act['success_count'] += 1
                else:
                    # Decrease success count (but keep minimum of 1)
                    act['success_count'] = max(1, act['success_count'] - 1)
                
                act['last_used'] = datetime.now().isoformat()
                act['use_count'] = act.get('use_count', 1) + 1
                
                logger.debug(f"Updated success for {action}: {act['success_count']}")
                break
    
    def get_transition_features(self, from_emotion: str, to_emotion: str) -> Dict:
        """
        Get detailed features for a transition (for GNN training)
        
        Args:
            from_emotion: Starting emotion
            to_emotion: Target emotion
            
        Returns:
            Dictionary of transition features
        """
        transition_key = (from_emotion, to_emotion)
        actions = self.memory_map['transitions'].get(transition_key, [])
        
        if not actions:
            return {
                'has_data': False,
                'num_actions': 0,
                'avg_success_rate': 0,
                'total_uses': 0,
                'temporal_score': 0
            }
        
        # Calculate features
        success_rates = [act['success_count'] for act in actions]
        use_counts = [act.get('use_count', 1) for act in actions]
        
        # Temporal features
        timestamps = [act.get('last_used', act['timestamp']) for act in actions]
        temporal_score = self._calculate_temporal_score(timestamps)
        
        return {
            'has_data': True,
            'num_actions': len(actions),
            'avg_success_rate': sum(success_rates) / len(success_rates),
            'max_success_rate': max(success_rates),
            'total_uses': sum(use_counts),
            'temporal_score': temporal_score,
            'recency_days': self._calculate_recency_days(timestamps)
        }
    
    def _calculate_temporal_score(self, timestamps: List[str]) -> float:
        """
        Calculate temporal score based on recency
        
        Args:
            timestamps: List of timestamp strings
            
        Returns:
            Score between 0 and 1 (1 = very recent)
        """
        if not timestamps:
            return 0.0
        
        current_time = datetime.now()
        scores = []
        
        for ts_str in timestamps:
            try:
                ts = datetime.fromisoformat(ts_str)
                days_old = (current_time - ts).days
                score = 0.95 ** days_old  # Exponential decay
                scores.append(score)
            except:
                pass
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _calculate_recency_days(self, timestamps: List[str]) -> int:
        """
        Calculate days since most recent use
        
        Args:
            timestamps: List of timestamp strings
            
        Returns:
            Days since most recent timestamp
        """
        if not timestamps:
            return 999
        
        current_time = datetime.now()
        min_days = 999
        
        for ts_str in timestamps:
            try:
                ts = datetime.fromisoformat(ts_str)
                days = (current_time - ts).days
                min_days = min(min_days, days)
            except:
                pass
        
        return min_days
    
    def _update_activity_patterns(self, experience: Dict) -> None:
        """
        Track user activity patterns (time of day, day of week)
        
        Args:
            experience: Experience dictionary
        """
        try:
            timestamp = datetime.fromisoformat(experience['timestamp'])
            hour = timestamp.hour
            day_of_week = timestamp.strftime('%A')
            
            user_id = experience.get('user_id', 'default_user')
            
            if user_id not in self.temporal_features['user_activity_patterns']:
                self.temporal_features['user_activity_patterns'][user_id] = {
                    'hours': defaultdict(int),
                    'days': defaultdict(int)
                }
            
            self.temporal_features['user_activity_patterns'][user_id]['hours'][hour] += 1
            self.temporal_features['user_activity_patterns'][user_id]['days'][day_of_week] += 1
            
        except Exception as e:
            logger.debug(f"Failed to update activity patterns: {e}")
    
    def _update_transition_patterns(self, from_emotion: str, to_emotion: str, 
                                   timestamp: str) -> None:
        """
        Track when transitions typically happen
        
        Args:
            from_emotion: Starting emotion
            to_emotion: Target emotion
            timestamp: ISO format timestamp
        """
        try:
            dt = datetime.fromisoformat(timestamp)
            hour = dt.hour
            
            transition_key = f"{from_emotion}->{to_emotion}"
            
            if transition_key not in self.temporal_features['transition_patterns']:
                self.temporal_features['transition_patterns'][transition_key] = {
                    'hours': defaultdict(int),
                    'total_count': 0
                }
            
            self.temporal_features['transition_patterns'][transition_key]['hours'][hour] += 1
            self.temporal_features['transition_patterns'][transition_key]['total_count'] += 1
            
        except Exception as e:
            logger.debug(f"Failed to update transition patterns: {e}")
    
    def cleanup_old_data(self) -> None:
        """
        Remove experiences and transitions older than MAX_TRANSITION_AGE_DAYS
        """
        current_time = datetime.now()
        max_age = timedelta(days=MemoryConfig.MAX_TRANSITION_AGE_DAYS)
        
        # Clean experiences
        original_count = len(self.memory_map['user_experiences'])
        self.memory_map['user_experiences'] = [
            exp for exp in self.memory_map['user_experiences']
            if (current_time - datetime.fromisoformat(exp['timestamp'])) < max_age
        ]
        removed_exp = original_count - len(self.memory_map['user_experiences'])
        
        # Clean transitions
        removed_transitions = 0
        for transition_key, actions in list(self.memory_map['transitions'].items()):
            original_action_count = len(actions)
            self.memory_map['transitions'][transition_key] = [
                act for act in actions
                if (current_time - datetime.fromisoformat(act['timestamp'])) < max_age
            ]
            
            # Remove empty transitions
            if not self.memory_map['transitions'][transition_key]:
                del self.memory_map['transitions'][transition_key]
                removed_transitions += 1
            else:
                removed_transitions += original_action_count - len(self.memory_map['transitions'][transition_key])
        
        self.stats['last_cleanup_time'] = current_time.isoformat()
        
        if removed_exp > 0 or removed_transitions > 0:
            logger.info(f"Cleanup: Removed {removed_exp} experiences and {removed_transitions} transition actions")
    
    def get_memory_map(self) -> Dict:
        """
        Get current memory map
        
        Returns:
            Copy of current memory map
        """
        return dict(self.memory_map)
    
    def get_stats(self) -> Dict:
        """
        Get memory statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            'emotional_states_count': len(self.memory_map['emotional_states']),
            'transitions_count': len(self.memory_map['transitions']),
            'graph_connections_count': len(self.memory_map['graph_connections'])
        }
    
    def save_memory(self) -> None:
        """
        Save memory map to disk
        """
        try:
            # Save main memory map
            with open(MemoryConfig.MEMORY_FILE, 'w') as f:
                # Convert defaultdict to regular dict for JSON serialization
                serializable_map = {
                    'emotional_states': self.memory_map['emotional_states'],
                    'transitions': {
                        f"{k[0]}->{k[1]}": v 
                        for k, v in self.memory_map['transitions'].items()
                    },
                    'user_experiences': self.memory_map['user_experiences'],
                    'graph_connections': dict(self.memory_map['graph_connections']),
                    'algorithm_comparisons': self.memory_map['algorithm_comparisons']
                }
                json.dump(serializable_map, f, indent=2)
            
            # Save temporal features
            temporal_file = MemoryConfig.MEMORY_FILE.replace('memory_map', 'temporal_features')
            with open(temporal_file, 'w') as f:
                serializable_temporal = {
                    k: dict(v) if isinstance(v, defaultdict) else v
                    for k, v in self.temporal_features.items()
                }
                json.dump(serializable_temporal, f, indent=2)
            
            self.stats['last_save_time'] = datetime.now().isoformat()
            logger.info(f"Memory saved to {MemoryConfig.MEMORY_FILE}")
            
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def _load_memory(self) -> None:
        """
        Load memory map from disk if available
        """
        try:
            if os.path.exists(MemoryConfig.MEMORY_FILE):
                with open(MemoryConfig.MEMORY_FILE, 'r') as f:
                    data = json.load(f)
                    
                    # Restore memory map
                    self.memory_map['emotional_states'] = data.get('emotional_states', {})
                    self.memory_map['user_experiences'] = data.get('user_experiences', [])
                    self.memory_map['algorithm_comparisons'] = data.get('algorithm_comparisons', [])
                    
                    # Restore transitions (convert back to tuple keys)
                    transitions = data.get('transitions', {})
                    for key_str, value in transitions.items():
                        from_e, to_e = key_str.split('->')
                        self.memory_map['transitions'][(from_e, to_e)] = value
                    
                    # Restore graph connections
                    connections = data.get('graph_connections', {})
                    self.memory_map['graph_connections'] = defaultdict(list, connections)
                    
                    # Update stats
                    self.stats['total_experiences'] = len(self.memory_map['user_experiences'])
                    self.stats['total_transitions'] = len(self.memory_map['transitions'])
                    
                    logger.info(f"Memory loaded: {self.stats['total_experiences']} experiences, "
                              f"{self.stats['total_transitions']} transitions")
            
            # Load temporal features
            temporal_file = MemoryConfig.MEMORY_FILE.replace('memory_map', 'temporal_features')
            if os.path.exists(temporal_file):
                with open(temporal_file, 'r') as f:
                    self.temporal_features = json.load(f)
                    logger.info("Temporal features loaded")
                    
        except Exception as e:
            logger.warning(f"Failed to load memory: {e}")
    
    def _start_autosave_thread(self) -> None:
        """
        Start background thread for auto-saving
        """
        def autosave_loop():
            while True:
                time.sleep(MemoryConfig.SAVE_INTERVAL_SECONDS)
                self.save_memory()
                
                # Also cleanup old data periodically
                if self.stats['last_cleanup_time'] is None or \
                   (datetime.now() - datetime.fromisoformat(self.stats['last_cleanup_time'])).days >= 7:
                    self.cleanup_old_data()
        
        thread = threading.Thread(target=autosave_loop, daemon=True)
        thread.start()
        logger.info("Auto-save thread started")
    
    def reset_memory(self) -> None:
        """
        Reset all memory data
        """
        self.memory_map = {
            'emotional_states': {},
            'transitions': {},
            'user_experiences': [],
            'graph_connections': defaultdict(list),
            'algorithm_comparisons': []
        }
        self.temporal_features = {
            'transition_patterns': {},
            'success_rates_over_time': {},
            'user_activity_patterns': {}
        }
        self.stats = {
            'total_experiences': 0,
            'total_transitions': 0,
            'last_save_time': None,
            'last_cleanup_time': None
        }
        self.save_memory()
        logger.info("Memory reset")


# Singleton instance
_memory_logger_instance = None

def get_memory_logger() -> MemoryLogger:
    """Get singleton memory logger instance"""
    global _memory_logger_instance
    if _memory_logger_instance is None:
        _memory_logger_instance = MemoryLogger()
    return _memory_logger_instance


if __name__ == "__main__":
    # Test the memory logger
    logger = get_memory_logger()
    
    # Test experience logging
    exp = {
        'id': '123',
        'text': 'I feel happy',
        'emotion': 'happy',
        'confidence': 0.9,
        'user_id': 'test_user'
    }
    logger.log_experience(exp)
    
    # Test transition logging
    logger.log_transition('sad', 'happy', ['exercise', 'meditation'], '123')
    
    print("\nStats:")
    print(json.dumps(logger.get_stats(), indent=2))
    
    print("\nTransition Features:")
    features = logger.get_transition_features('sad', 'happy')
    print(json.dumps(features, indent=2))
