# Data and Methods

## 1. Datasets and Preprocessing

The Reflectly project utilizes two primary datasets to train and refine its emotional analysis capabilities:

### 1.1 IEMOCAP Dataset

The Interactive Emotional Dyadic Motion Capture (IEMOCAP) dataset serves as the foundation for our emotional state transition modeling. This dataset consists of approximately 12 hours of audiovisual data from dyadic sessions, where actors perform improvised or scripted scenarios designed to elicit specific emotional responses.

**Dataset Characteristics:**
- 10 actors (5 male, 5 female) in dyadic interactions
- Multimodal data: audio, video, motion capture, and transcripts
- Discrete emotion annotations: anger, happiness, sadness, neutrality, excitement, frustration, fear, surprise, and disgust
- Dimensional annotations: valence, activation, and dominance

**Preprocessing Steps:**
1. **Text Normalization:**
   - Conversion to lowercase
   - Removal of punctuation and special characters
   - Tokenization and lemmatization of utterances

2. **Emotional Label Mapping:**
   - Standardization of emotion labels to match Reflectly's emotion model:
     ```python
     emotion_mapping = {
         "happiness": "joy",
         "excited": "joy",
         "sadness": "sadness",
         "anger": "anger",
         "frustrated": "anger",
         "fear": "fear",
         "disgust": "disgust",
         "neutral": "neutral",
         "surprise": "joy"  # Mapping surprise to joy as a simplification
     }
     ```

3. **Feature Extraction:**
   - Extraction of emotional transitions between utterances
   - Calculation of transition probabilities between emotional states
   - Identification of linguistic patterns associated with emotional shifts

4. **Data Partitioning:**
   - 80% for model training
   - 10% for validation
   - 10% for testing

### 1.2 Mental Health Dataset

In addition to IEMOCAP, we utilize an anonymized mental health dataset containing journal entries, emotion logs, and intervention outcomes. This dataset provides real-world context for emotional state transitions and effective interventions.

**Dataset Characteristics:**
- Anonymized journal entries with emotional state annotations
- Intervention records with effectiveness ratings
- Temporal sequences of emotional states
- Demographic information (age, gender, location)

**Preprocessing Steps:**
1. **Privacy Protection:**
   - Complete anonymization of all personal identifiers
   - Removal of specific contextual details that could enable re-identification

2. **Text Processing:**
   - Removal of irrelevant content (URLs, numbers, special characters)
   - Tokenization and stemming
   - Named entity recognition and redaction

3. **Emotional Annotation:**
   - Standardization of emotional labels
   - Extraction of emotional intensity metrics
   - Identification of emotional triggers and patterns

4. **Intervention Classification:**
   - Categorization of interventions (cognitive, behavioral, physiological)
   - Standardization of effectiveness ratings
   - Temporal alignment with emotional state changes

5. **Data Integration:**
   - Mapping of intervention types to emotional state transitions
   - Creation of emotional transition graphs with associated interventions
   - Correlation analysis between intervention types and transition success rates

## 2. Methodology and Model Architectures

The Reflectly system employs a multi-faceted approach to emotional analysis and guidance, combining several AI techniques within a robust big data architecture.

### 2.1 Emotional Graph Model

The foundation of Reflectly's emotional analysis is the EmotionalGraph model, which represents emotional states as nodes in a graph structure, with transitions between states as weighted edges.

**Key Components:**
- **Node Structure:** Each node represents a discrete emotional state (e.g., joy, sadness, anger)
- **Edge Weighting:** Transitions between states are weighted based on:
  - Historical transition frequencies
  - Transition difficulty derived from psychological research
  - User-specific transition patterns
- **Metadata Integration:** Nodes and edges contain metadata about:
  - Associated interventions
  - Success rates
  - Contextual triggers

**Implementation Details:**
```python
class EmotionalGraph:
    def __init__(self, db):
        self.db = db
        self.emotions_collection = db.emotional_states
        self.transitions_collection = db.emotional_transitions
        
        # Define positive and negative emotions
        self.positive_emotions = ['joy', 'surprise', 'happy', 'excited', 'content', 'calm']
        self.negative_emotions = ['sadness', 'anger', 'fear', 'disgust', 'sad', 'anxious', 'frustrated', 'stressed']
        self.neutral_emotions = ['neutral']
```

The EmotionalGraphBigData class extends this model with big data capabilities:
- Kafka integration for real-time event streaming
- HDFS for distributed storage of emotional data
- Spark for distributed processing of emotional patterns

### 2.2 A* Search Algorithm for Emotional Pathfinding

To identify optimal paths between emotional states, we implement a customized A* search algorithm that navigates the emotional state graph to find the most effective transitions.

**Algorithm Characteristics:**
- **Heuristic Function:** Estimates the "emotional distance" between states
- **Cost Function:** Combines transition difficulty, time required, and user-specific factors
- **Path Optimization:** Balances path length with psychological appropriateness

**Implementation Details:**
```python
def heuristic(self, current_emotion, target_emotion, user_email=None):
    """
    Heuristic function for A* search
    Estimates the cost to reach the target emotion from the current emotion
    """
    # Define base costs between emotion categories
    # Lower cost means emotions are closer/easier to transition between
    base_costs = {
        ('joy', 'joy'): 0.1,
        ('joy', 'neutral'): 0.5,
        ('joy', 'sadness'): 1.5,
        # Additional mappings omitted for brevity
    }
    
    # Get base cost or use default
    emotion_pair = (current_emotion, target_emotion)
    base_cost = base_costs.get(emotion_pair, 1.0)
    
    # Apply logarithmic transformation to costs
    # This ensures the heuristic never overestimates the true cost
    log_cost = np.log(1 + base_cost)
    
    # If user email is provided, personalize the heuristic
    if user_email:
        # Get user history from emotional graph
        user_history = self.emotional_graph.get_user_history(user_email)
        
        # Check if this transition exists in user history
        if current_emotion in user_history and target_emotion in user_history[current_emotion]:
            # Calculate personalized cost based on historical effectiveness
            effectiveness = user_history[current_emotion][target_emotion]
            personalized_cost = log_cost * (1.0 - effectiveness)
            return personalized_cost
    
    return log_cost
```

The A* implementation includes optimizations for:
- Memory efficiency to handle large emotional graphs
- Personalization based on user history
- Dynamic cost updates as new data becomes available

### 2.3 Probabilistic Models

Reflectly employs two primary probabilistic models to reason about emotional state transitions:

#### 2.3.1 Markov Model

The MarkovModel class implements a first-order Markov chain to model temporal dependencies in emotional state sequences.

**Model Characteristics:**
- **State Space:** Discrete emotional states
- **Transition Matrix:** Probability distribution of transitions between states
- **Order:** First-order (transition depends only on current state)
- **Learning:** Incremental updates based on observed emotional sequences

**Implementation Details:**
```python
class MarkovModel:
    def __init__(self, states: List[str], transition_matrix: Optional[np.ndarray] = None):
        """
        Initialize a Markov model.
        
        Args:
            states: List of possible states
            transition_matrix: Optional transition matrix (will be initialized to uniform if not provided)
        """
        self.states = states
        self.state_to_idx = {state: i for i, state in enumerate(states)}
        
        # Initialize transition matrix
        if transition_matrix is not None:
            if transition_matrix.shape != (len(states), len(states)):
                raise ValueError(f"Transition matrix shape {transition_matrix.shape} does not match number of states {len(states)}")
            self.transition_matrix = transition_matrix
        else:
            # Initialize with uniform transitions
            self.transition_matrix = np.ones((len(states), len(states))) / len(states)
```

The model supports:
- Prediction of likely emotional sequences
- Calculation of stationary distributions
- Estimation of expected time to reach positive emotional states
- Personalization based on individual emotion histories

#### 2.3.2 Bayesian Network

The BayesianNetwork class implements a directed graphical model to represent the causal relationships between emotional states, actions, and contextual factors.

**Model Characteristics:**
- **Node Types:** Emotional states, actions, and contextual factors
- **Conditional Probability Tables (CPTs):** Quantify the relationship between variables
- **Structure:** Directed acyclic graph (DAG) encoding causal relationships
- **Inference:** Support for various inference queries (prediction, intervention, counterfactuals)

**Implementation Details:**
```python
class BayesianNetwork:
    def __init__(self):
        """Initialize an empty Bayesian network."""
        self.nodes = {}  # Maps node names to Node objects
    
    @classmethod
    def create_emotional_network(cls, emotions: List[str], actions: List[str]) -> 'BayesianNetwork':
        """
        Create a Bayesian network for emotional transitions.
        """
        network = cls()
        
        # Add nodes
        network.add_node('current_emotion', emotions)
        network.add_node('action', actions)
        network.add_node('next_emotion', emotions)
        
        # Add edges
        network.add_edge('current_emotion', 'next_emotion')
        network.add_edge('action', 'next_emotion')
        
        # Set CPTs (would be learned from data in a real implementation)
        # For now, use placeholder uniform distributions
        
        # Implementation details omitted for brevity
        
        return network
```

The Bayesian network is used for:
- Predicting emotional responses to specific interventions
- Identifying optimal actions to facilitate desired emotional transitions
- Reasoning about the impact of contextual factors on emotional states
- Personalizing recommendations based on individual response patterns

### 2.4 Intelligent Agent Architecture

The intelligent agent in Reflectly manages the user's emotional journey using a sophisticated state management system. The agent observes the user's emotional states, plans interventions, and learns from feedback.

**Agent Components:**
- **State Management:** Tracks current emotion, target emotion, and action plan
- **Planning System:** Generates action plans to guide emotional transitions
- **Learning Module:** Updates models based on feedback and outcomes
- **Recommendation Engine:** Suggests personalized interventions

**Implementation Details:**
```python
class AgentState:
    def __init__(self, user_id: str, user_email=None, current_emotion=None, target_emotion=None, action_plan=None, current_action_index=0, feedback_history=None):
        """
        Initialize agent state.
        """
        self.user_id = user_id
        self.user_email = user_email
        self.current_emotion = current_emotion
        self.target_emotion = target_emotion
        self.history = []
        self.last_updated = time.time()
        self.context = {}
        self.actions = action_plan if action_plan is not None else []
        self.current_action_index = current_action_index
        self.feedback = feedback_history if feedback_history is not None else []
```

The agent architecture follows a modified BDI (Belief-Desire-Intention) framework:
- **Beliefs:** Current emotional state and contextual factors
- **Desires:** Target emotional states and well-being goals
- **Intentions:** Action plans to achieve desired emotional transitions

### 2.5 Big Data Infrastructure

The Reflectly system leverages a robust big data infrastructure to process and analyze emotional data at scale.

**Components:**
- **Kafka:** Real-time streaming of emotional events and transitions
- **HDFS:** Distributed storage of historical emotional data
- **Spark:** Distributed processing of emotional patterns and model training
- **MongoDB:** Operational data storage for quick access to user profiles and current states

**Implementation Details:**
The infrastructure supports several key processing flows:
1. **Real-time Emotion Processing:**
   - User journal entries → Kafka → Emotion Analysis → HDFS
   - User feedback → Kafka → Model Updates → HDFS

2. **Batch Processing:**
   - Nightly Spark jobs for model training and pattern discovery
   - Weekly aggregation of emotional trends and insights

3. **Hybrid Processing:**
   - Streaming analytics for immediate personalization
   - Batch integration for comprehensive model updates

## 3. Evaluation Metrics

The Reflectly system's performance is evaluated using a comprehensive set of metrics across several dimensions.

### 3.1 Emotional State Recognition Accuracy

**Metrics:**
- **Precision:** Correctly identified emotions / Total identified emotions for each category
- **Recall:** Correctly identified emotions / Total actual emotions for each category
- **F1-Score:** Harmonic mean of precision and recall
- **Confusion Matrix:** Visualization of classification performance across emotional categories

**Implementation:**
```python
def evaluate_emotion_recognition(predictions, ground_truth):
    """
    Evaluate emotion recognition performance.
    
    Args:
        predictions: List of predicted emotions
        ground_truth: List of ground truth emotions
        
    Returns:
        Dictionary of evaluation metrics
    """
    # Calculate precision, recall, and F1-score for each emotion
    precision = {}
    recall = {}
    f1_score = {}
    
    for emotion in set(ground_truth):
        # True positives
        tp = sum(1 for p, g in zip(predictions, ground_truth) if p == emotion and g == emotion)
        
        # False positives
        fp = sum(1 for p, g in zip(predictions, ground_truth) if p == emotion and g != emotion)
        
        # False negatives
        fn = sum(1 for p, g in zip(predictions, ground_truth) if p != emotion and g == emotion)
        
        # Calculate metrics
        precision[emotion] = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall[emotion] = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score[emotion] = 2 * (precision[emotion] * recall[emotion]) / (precision[emotion] + recall[emotion]) if (precision[emotion] + recall[emotion]) > 0 else 0
    
    # Calculate overall accuracy
    accuracy = sum(1 for p, g in zip(predictions, ground_truth) if p == g) / len(ground_truth)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'accuracy': accuracy
    }
```

### 3.2 Emotional Path Optimization

**Metrics:**
- **Path Optimality:** Ratio of A* path cost to shortest possible path cost
- **Transition Success Rate:** Percentage of users who successfully follow the recommended path
- **Time to Positive State:** Average time to transition from negative to positive emotional states
- **Path Personalization Accuracy:** Correlation between predicted optimal paths and actual user transitions

**Implementation:**
```python
def evaluate_path_optimization(recommended_paths, actual_paths):
    """
    Evaluate emotional path optimization performance.
    
    Args:
        recommended_paths: List of recommended emotional paths
        actual_paths: List of actual emotional paths taken by users
        
    Returns:
        Dictionary of evaluation metrics
    """
    # Calculate path similarity
    path_similarities = []
    for rec_path, act_path in zip(recommended_paths, actual_paths):
        # Calculate Levenshtein distance between paths
        distance = levenshtein_distance(rec_path, act_path)
        max_length = max(len(rec_path), len(act_path))
        similarity = 1 - (distance / max_length) if max_length > 0 else 1
        path_similarities.append(similarity)
    
    # Calculate transition success rate
    success_count = 0
    for rec_path, act_path in zip(recommended_paths, actual_paths):
        if rec_path[-1] == act_path[-1]:  # End at the same emotional state
            success_count += 1
    
    transition_success_rate = success_count / len(recommended_paths) if len(recommended_paths) > 0 else 0
    
    # Calculate average time to positive state
    times_to_positive = []
    for path in actual_paths:
        # Extract timestamps from path
        timestamps = [node['timestamp'] for node in path]
        
        # Find first positive emotion
        for i, node in enumerate(path):
            if node['emotion'] in positive_emotions:
                time_to_positive = timestamps[i] - timestamps[0]
                times_to_positive.append(time_to_positive)
                break
    
    avg_time_to_positive = sum(times_to_positive) / len(times_to_positive) if times_to_positive else float('inf')
    
    return {
        'path_similarity': sum(path_similarities) / len(path_similarities) if path_similarities else 0,
        'transition_success_rate': transition_success_rate,
        'avg_time_to_positive': avg_time_to_positive
    }
```

### 3.3 Probabilistic Prediction Accuracy

**Metrics:**
- **Log-Likelihood:** Measure of how well the probabilistic models fit the observed data
- **Perplexity:** Exponentiated average negative log-likelihood per prediction
- **Prediction Accuracy:** Percentage of correctly predicted next emotional states
- **Mean Reciprocal Rank (MRR):** Average of the reciprocal ranks of the correct emotion in the predicted distribution

**Implementation:**
```python
def evaluate_probabilistic_prediction(model, test_sequences):
    """
    Evaluate probabilistic prediction performance.
    
    Args:
        model: Markov model or Bayesian network
        test_sequences: List of emotional sequences for testing
        
    Returns:
        Dictionary of evaluation metrics
    """
    log_likelihoods = []
    correct_predictions = 0
    total_predictions = 0
    reciprocal_ranks = []
    
    for sequence in test_sequences:
        for i in range(len(sequence) - 1):
            # Current and next emotion
            current = sequence[i]
            next_actual = sequence[i + 1]
            
            # Get prediction
            prediction = model.predict_next(current)
            
            # Calculate log-likelihood
            prob = prediction.get(next_actual, 0)
            log_likelihood = np.log(prob) if prob > 0 else -np.inf
            log_likelihoods.append(log_likelihood)
            
            # Check if prediction is correct
            predicted_emotion = max(prediction.items(), key=lambda x: x[1])[0]
            if predicted_emotion == next_actual:
                correct_predictions += 1
            
            # Calculate reciprocal rank
            sorted_predictions = sorted(prediction.items(), key=lambda x: x[1], reverse=True)
            for rank, (emotion, _) in enumerate(sorted_predictions, 1):
                if emotion == next_actual:
                    reciprocal_ranks.append(1 / rank)
                    break
            
            total_predictions += 1
    
    # Calculate evaluation metrics
    avg_log_likelihood = sum(ll for ll in log_likelihoods if ll != -np.inf) / len(log_likelihoods) if log_likelihoods else -np.inf
    perplexity = np.exp(-avg_log_likelihood)
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0
    
    return {
        'avg_log_likelihood': avg_log_likelihood,
        'perplexity': perplexity,
        'accuracy': accuracy,
        'mrr': mrr
    }
```

### 3.4 Agent Effectiveness

**Metrics:**
- **Goal Achievement Rate:** Percentage of users who reach their target emotional states
- **User Satisfaction:** Self-reported satisfaction with agent recommendations
- **Engagement:** Frequency and duration of user interactions with the agent
- **Learning Rate:** Improvement in recommendation accuracy over time

**Implementation:**
```python
def evaluate_agent_effectiveness(agent_interactions):
    """
    Evaluate agent effectiveness.
    
    Args:
        agent_interactions: List of agent interactions with users
        
    Returns:
        Dictionary of evaluation metrics
    """
    # Calculate goal achievement rate
    achieved_goals = sum(1 for interaction in agent_interactions if interaction['goal_achieved'])
    goal_achievement_rate = achieved_goals / len(agent_interactions) if agent_interactions else 0
    
    # Calculate average user satisfaction
    avg_satisfaction = sum(interaction['satisfaction_rating'] for interaction in agent_interactions if 'satisfaction_rating' in interaction) / sum(1 for interaction in agent_interactions if 'satisfaction_rating' in interaction)
    
    # Calculate average engagement
    avg_interactions_per_day = sum(interaction['interactions_per_day'] for interaction in agent_interactions) / len(agent_interactions) if agent_interactions else 0
    
    # Calculate learning rate
    initial_accuracy = sum(interaction['initial_recommendation_accuracy'] for interaction in agent_interactions) / len(agent_interactions) if agent_interactions else 0
    final_accuracy = sum(interaction['final_recommendation_accuracy'] for interaction in agent_interactions) / len(agent_interactions) if agent_interactions else 0
    learning_rate = (final_accuracy - initial_accuracy) / initial_accuracy if initial_accuracy > 0 else 0
    
    return {
        'goal_achievement_rate': goal_achievement_rate,
        'avg_satisfaction': avg_satisfaction,
        'avg_interactions_per_day': avg_interactions_per_day,
        'learning_rate': learning_rate
    }
```

### 3.5 System Performance

**Metrics:**
- **Latency:** Response time for various API endpoints
- **Throughput:** Number of requests processed per second
- **Resource Utilization:** CPU, memory, and network usage across the big data infrastructure
- **Scalability:** Performance under increasing load

**Implementation:**
```python
def evaluate_system_performance(performance_logs):
    """
    Evaluate system performance.
    
    Args:
        performance_logs: System performance logs
        
    Returns:
        Dictionary of evaluation metrics
    """
    # Calculate average API latency
    api_latencies = {}
    for endpoint, latencies in performance_logs['api_latencies'].items():
        api_latencies[endpoint] = sum(latencies) / len(latencies) if latencies else 0
    
    # Calculate average throughput
    avg_throughput = sum(performance_logs['requests_per_second']) / len(performance_logs['requests_per_second']) if performance_logs['requests_per_second'] else 0
    
    # Calculate average resource utilization
    avg_cpu_usage = sum(performance_logs['cpu_usage']) / len(performance_logs['cpu_usage']) if performance_logs['cpu_usage'] else 0
    avg_memory_usage = sum(performance_logs['memory_usage']) / len(performance_logs['memory_usage']) if performance_logs['memory_usage'] else 0
    
    # Calculate scalability factor
    scalability_factor = performance_logs['throughput_at_peak'] / performance_logs['throughput_baseline'] if performance_logs['throughput_baseline'] > 0 else 0
    
    return {
        'api_latencies': api_latencies,
        'avg_throughput': avg_throughput,
        'avg_cpu_usage': avg_cpu_usage,
        'avg_memory_usage': avg_memory_usage,
        'scalability_factor': scalability_factor
    }
```

## 4. Experimental Setup

The evaluation of the Reflectly system was conducted using a multi-phase experimental setup.

### 4.1 Offline Evaluation

The initial phase involved offline evaluation using historical data:

1. **Dataset Splitting:**
   - Training set (80%): Used for model development and parameter tuning
   - Validation set (10%): Used for hyperparameter optimization
   - Test set (10%): Used for final evaluation

2. **Cross-Validation:**
   - 5-fold cross-validation for robust performance estimation
   - Stratification by emotion category to ensure balanced representation

3. **Model Comparison:**
   - Baseline models: Rule-based systems, simple statistical models
   - Advanced models: A* search, Markov models, Bayesian networks
   - Hybrid approaches: Combinations of probabilistic and search-based methods

### 4.2 Online Evaluation

The second phase involved online evaluation with real users:

1. **A/B Testing:**
   - Control group: Basic emotional journaling without advanced recommendations
   - Test group: Full Reflectly system with A* search and probabilistic reasoning

2. **User Feedback Collection:**
   - Daily mood tracking
   - Weekly satisfaction surveys
   - Qualitative feedback on recommendation quality

3. **Longitudinal Analysis:**
   - Tracking of emotional trajectories over a 12-week period
   - Comparison of emotional well-being metrics between control and test groups

### 4.3 Technical Evaluation

The final phase focused on technical performance and scalability:

1. **Load Testing:**
   - Simulation of various user loads (100, 1,000, 10,000 concurrent users)
   - Measurement of system response times and resource utilization

2. **Fault Tolerance:**
   - Induced failure of system components
   - Evaluation of failover mechanisms and data consistency

3. **Scalability Testing:**
   - Horizontal scaling of Kafka, Spark, and MongoDB components
   - Measurement of throughput and latency with increasing data volumes
