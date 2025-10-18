"""
Configuration file for Reflectly Enhanced System
Centralizes all settings for LLM, GNN, and memory management
"""

import os

# ============================================================================
# LLM Configuration
# ============================================================================

class LLMConfig:
    """Configuration for Local LLM (Ollama) Integration"""
    
    # Ollama settings
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    
    # Primary model (most accurate for emotion analysis based on research)
    PRIMARY_MODEL = os.getenv('LLM_MODEL', 'mistral:7b')
    
    # Fallback models if primary fails
    FALLBACK_MODELS = ['llama3.2:3b', 'llama2:7b']
    
    # LLM parameters
    TEMPERATURE = 0.3  # Lower for more consistent emotion analysis
    TOP_P = 0.9
    MAX_TOKENS = 150
    
    # Performance settings
    REQUEST_TIMEOUT = 30  # seconds
    MAX_RETRIES = 2
    
    # Enable/disable LLM (fallback to regex if disabled)
    LLM_ENABLED = os.getenv('LLM_ENABLED', 'true').lower() == 'true'
    
    # Emotion analysis prompt template
    EMOTION_PROMPT_TEMPLATE = """Analyze the emotional content of the following text.
Identify the primary emotion from these categories: happy, sad, anxious, angry, confused, tired, neutral.
Also rate the confidence (0.0 to 1.0) and classify as positive, negative, or neutral.

Text: {text}

Respond ONLY with this exact JSON format:
{{"primary_emotion": "emotion_name", "confidence": 0.95, "emotion_type": "positive/negative/neutral"}}"""

# ============================================================================
# GNN Configuration  
# ============================================================================

class GNNConfig:
    """Configuration for Graph Neural Network"""
    
    # Model architecture
    HIDDEN_DIM = 64
    OUTPUT_DIM = 32
    NUM_LAYERS = 2
    DROPOUT = 0.1
    
    # Attention mechanism
    ATTENTION_HEADS = 4
    USE_ATTENTION = True
    
    # Training parameters
    LEARNING_RATE = 0.001
    WEIGHT_DECAY = 1e-5
    NUM_EPOCHS = 50
    BATCH_SIZE = 32
    
    # Temporal decay for older transitions
    TEMPORAL_DECAY_RATE = 0.95  # Per day
    MAX_AGE_DAYS = 90  # After this, weight approaches minimum
    
    # Minimum edge weight
    MIN_EDGE_WEIGHT = 0.1
    MAX_EDGE_WEIGHT = 10.0
    
    # GNN training trigger
    MIN_TRANSITIONS_FOR_TRAINING = 10  # Start GNN after this many transitions
    RETRAIN_INTERVAL = 20  # Retrain after every N new transitions
    
    # Enable/disable GNN (fallback to hardcoded weights if disabled)
    GNN_ENABLED = os.getenv('GNN_ENABLED', 'true').lower() == 'true'

# ============================================================================
# Memory Configuration
# ============================================================================

class MemoryConfig:
    """Configuration for Memory Logger and Data Persistence"""
    
    # Data directory
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    
    # File paths
    MEMORY_FILE = os.path.join(DATA_DIR, 'memory_map.json')
    TRANSITIONS_FILE = os.path.join(DATA_DIR, 'transitions.json')
    GNN_MODEL_FILE = os.path.join(DATA_DIR, 'gnn_model.pt')
    
    # Memory retention
    MAX_EXPERIENCES = 10000  # Maximum experiences to keep in memory
    MAX_TRANSITION_AGE_DAYS = 90  # Remove transitions older than this
    
    # Auto-save settings
    AUTO_SAVE = True
    SAVE_INTERVAL_SECONDS = 300  # Save every 5 minutes
    
    # Statistics tracking
    TRACK_PERFORMANCE = True
    PERFORMANCE_LOG_FILE = os.path.join(DATA_DIR, 'performance_log.json')

# ============================================================================
# Application Configuration
# ============================================================================

class AppConfig:
    """General application settings"""
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Feature flags
    ENABLE_ALGORITHM_COMPARISON = True  # Keep existing algorithm comparison
    ENABLE_ENHANCED_LEARNING = True     # Enable LLM + GNN enhancements

# ============================================================================
# Emotion Hierarchy (for fallback heuristics)
# ============================================================================

EMOTION_HIERARCHY = {
    'happy': 1,
    'neutral': 2,
    'confused': 3,
    'tired': 4,
    'sad': 5,
    'anxious': 5,
    'angry': 6
}

# ============================================================================
# Default Suggestions (fallback when no learned data)
# ============================================================================

DEFAULT_SUGGESTIONS = {
    'sad': [
        "Listen to uplifting music",
        "Call or text a friend",
        "Take a warm bath or shower"
    ],
    'anxious': [
        "Practice deep breathing for 5 minutes",
        "Try progressive muscle relaxation",
        "Go for a short walk outside"
    ],
    'angry': [
        "Count to 10 slowly",
        "Write down your feelings",
        "Do some physical exercise"
    ],
    'confused': [
        "Break down the problem into smaller steps",
        "Talk to someone about it",
        "Take time to reflect and organize your thoughts"
    ],
    'tired': [
        "Take a 20-minute power nap",
        "Drink a glass of water",
        "Get some fresh air"
    ],
    'neutral': [
        "Try something you enjoy",
        "Take a walk and notice your surroundings",
        "Practice gratitude - list 3 things you're thankful for"
    ]
}

# ============================================================================
# Utility Functions
# ============================================================================

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    os.makedirs(MemoryConfig.DATA_DIR, exist_ok=True)

def get_config_summary():
    """Get summary of current configuration"""
    return {
        'llm_enabled': LLMConfig.LLM_ENABLED,
        'llm_model': LLMConfig.PRIMARY_MODEL,
        'gnn_enabled': GNNConfig.GNN_ENABLED,
        'data_dir': MemoryConfig.DATA_DIR,
        'debug': AppConfig.DEBUG,
        'port': AppConfig.PORT
    }
