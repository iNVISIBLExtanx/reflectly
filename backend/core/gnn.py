"""
GNN-Based Dynamic Graph Weight Calculator
Uses Graph Neural Networks to learn optimal edge weights for emotion transitions
Based on success rates, temporal features, and user patterns
"""

import logging
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_geometric.nn import GATConv, global_mean_pool
    from torch_geometric.data import Data
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch/PyG not installed. GNN features will be disabled.")

from config import GNNConfig, EMOTION_HIERARCHY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmotionGNN(nn.Module):
    """
    Graph Attention Network for learning emotion transition weights
    Uses attention mechanism to focus on important transitions
    """
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, num_heads: int = 4):
        super(EmotionGNN, self).__init__()
        
        # Graph Attention layers
        self.conv1 = GATConv(input_dim, hidden_dim, heads=num_heads, dropout=GNNConfig.DROPOUT)
        self.conv2 = GATConv(hidden_dim * num_heads, output_dim, heads=1, dropout=GNNConfig.DROPOUT)
        
        # Edge weight prediction layer
        self.edge_predictor = nn.Sequential(
            nn.Linear(output_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(GNNConfig.DROPOUT),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()  # Output between 0 and 1
        )
    
    def forward(self, x, edge_index):
        """
        Forward pass through the GNN
        
        Args:
            x: Node features [num_nodes, input_dim]
            edge_index: Edge indices [2, num_edges]
            
        Returns:
            Node embeddings and edge weights
        """
        # Graph convolution layers with attention
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=GNNConfig.DROPOUT, training=self.training)
        x = self.conv2(x, edge_index)
        
        return x
    
    def predict_edge_weight(self, node_embeddings, edge_index):
        """
        Predict weight for each edge based on node embeddings
        
        Args:
            node_embeddings: Learned node representations
            edge_index: Edge connections
            
        Returns:
            Predicted edge weights
        """
        # Get source and target node embeddings for each edge
        src_embeddings = node_embeddings[edge_index[0]]
        dst_embeddings = node_embeddings[edge_index[1]]
        
        # Concatenate source and target embeddings
        edge_features = torch.cat([src_embeddings, dst_embeddings], dim=1)
        
        # Predict weights
        weights = self.edge_predictor(edge_features)
        
        # Scale to desired range
        weights = GNNConfig.MIN_EDGE_WEIGHT + weights.squeeze() * (
            GNNConfig.MAX_EDGE_WEIGHT - GNNConfig.MIN_EDGE_WEIGHT
        )
        
        return weights


class GNNGraphWeightCalculator:
    """
    Main class for managing GNN-based graph weight calculation
    Handles training, prediction, and fallback to hardcoded weights
    """
    
    def __init__(self):
        """Initialize GNN calculator"""
        self.gnn_enabled = GNNConfig.GNN_ENABLED and TORCH_AVAILABLE
        
        if not self.gnn_enabled:
            logger.info("GNN disabled or unavailable. Using hardcoded weights.")
            return
        
        # Emotion to index mapping
        self.emotions = list(EMOTION_HIERARCHY.keys())
        self.emotion_to_idx = {emotion: idx for idx, emotion in enumerate(self.emotions)}
        self.num_emotions = len(self.emotions)
        
        # Initialize model
        input_dim = 10  # Node feature dimension
        self.model = EmotionGNN(
            input_dim=input_dim,
            hidden_dim=GNNConfig.HIDDEN_DIM,
            output_dim=GNNConfig.OUTPUT_DIM,
            num_heads=GNNConfig.ATTENTION_HEADS
        )
        
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=GNNConfig.LEARNING_RATE,
            weight_decay=GNNConfig.WEIGHT_DECAY
        )
        
        # Training state
        self.is_trained = False
        self.transition_count = 0
        
        # Try to load existing model
        self._load_model()
        
        logger.info("GNN Graph Weight Calculator initialized")
    
    def calculate_weights(self, memory_map: Dict) -> Dict[Tuple[str, str], float]:
        """
        Calculate edge weights for all transitions in the memory map
        
        Args:
            memory_map: Current memory map with transitions
            
        Returns:
            Dictionary mapping (from_emotion, to_emotion) to weight
        """
        if not self.gnn_enabled:
            return self._hardcoded_weights(memory_map)
        
        # Check if we have enough data to train
        num_transitions = len(memory_map.get('transitions', {}))
        
        if num_transitions < GNNConfig.MIN_TRANSITIONS_FOR_TRAINING:
            logger.info(f"Not enough transitions ({num_transitions}) for GNN training. Using hardcoded weights.")
            return self._hardcoded_weights(memory_map)
        
        # Check if we need to retrain
        if not self.is_trained or (num_transitions - self.transition_count) >= GNNConfig.RETRAIN_INTERVAL:
            logger.info("Retraining GNN with new data...")
            self._train(memory_map)
            self.transition_count = num_transitions
        
        # Predict weights using trained model
        return self._predict_weights(memory_map)
    
    def _prepare_graph_data(self, memory_map: Dict) -> Optional[Data]:
        """
        Prepare PyTorch Geometric Data object from memory map
        
        Args:
            memory_map: Current memory map
            
        Returns:
            PyTorch Geometric Data object or None if failed
        """
        try:
            # Create node features (one for each emotion)
            node_features = []
            
            for emotion in self.emotions:
                # Features: [hierarchy_level, num_experiences, avg_confidence, 
                #            positive_rate, negative_incoming, positive_outgoing, 
                #            avg_success_rate, temporal_score, degree, betweenness]
                
                experiences = memory_map.get('emotional_states', {}).get(emotion, [])
                num_exp = len(experiences)
                avg_conf = np.mean([exp.get('confidence', 0.5) for exp in experiences]) if experiences else 0.5
                
                hierarchy_level = EMOTION_HIERARCHY.get(emotion, 3) / 6  # Normalize
                
                # Count incoming/outgoing transitions
                positive_out = sum(
                    1 for (from_e, to_e) in memory_map.get('transitions', {}).keys()
                    if from_e == emotion and EMOTION_HIERARCHY.get(to_e, 3) < EMOTION_HIERARCHY.get(from_e, 3)
                )
                negative_in = sum(
                    1 for (from_e, to_e) in memory_map.get('transitions', {}).keys()
                    if to_e == emotion and EMOTION_HIERARCHY.get(from_e, 3) > EMOTION_HIERARCHY.get(to_e, 3)
                )
                
                # Calculate average success rate for transitions from this emotion
                success_rates = []
                for (from_e, to_e), actions in memory_map.get('transitions', {}).items():
                    if from_e == emotion:
                        for action in actions:
                            success_rates.append(action.get('success_count', 1))
                avg_success = np.mean(success_rates) if success_rates else 1.0
                
                # Temporal score (recency of experiences)
                temporal_score = self._calculate_temporal_score(experiences)
                
                # Graph metrics (simplified)
                degree = positive_out + negative_in
                betweenness = 0.5  # Simplified
                
                features = [
                    hierarchy_level,
                    min(num_exp / 100, 1.0),  # Normalized
                    avg_conf,
                    min(positive_out / 10, 1.0),  # Normalized
                    min(negative_in / 10, 1.0),  # Normalized
                    min(positive_out / 5, 1.0),  # Normalized
                    min(avg_success / 10, 1.0),  # Normalized
                    temporal_score,
                    min(degree / 10, 1.0),  # Normalized
                    betweenness
                ]
                
                node_features.append(features)
            
            x = torch.tensor(node_features, dtype=torch.float)
            
            # Create edges and edge labels (true weights based on success)
            edge_list = []
            edge_weights = []
            
            for (from_emotion, to_emotion), actions in memory_map.get('transitions', {}).items():
                if from_emotion in self.emotion_to_idx and to_emotion in self.emotion_to_idx:
                    from_idx = self.emotion_to_idx[from_emotion]
                    to_idx = self.emotion_to_idx[to_emotion]
                    
                    edge_list.append([from_idx, to_idx])
                    
                    # Calculate true weight based on success rates and temporal decay
                    weight = self._calculate_true_edge_weight(actions)
                    edge_weights.append(weight)
            
            if not edge_list:
                logger.warning("No valid edges found in memory map")
                return None
            
            edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()
            y = torch.tensor(edge_weights, dtype=torch.float)
            
            return Data(x=x, edge_index=edge_index, y=y)
            
        except Exception as e:
            logger.error(f"Failed to prepare graph data: {e}")
            return None
    
    def _calculate_true_edge_weight(self, actions: List[Dict]) -> float:
        """
        Calculate true edge weight based on action success rates and temporal decay
        
        Args:
            actions: List of actions for this transition
            
        Returns:
            Calculated weight
        """
        if not actions:
            return GNNConfig.MIN_EDGE_WEIGHT
        
        weights = []
        current_time = datetime.now()
        
        for action in actions:
            success_count = action.get('success_count', 1)
            timestamp_str = action.get('timestamp', '')
            
            # Calculate temporal decay
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    days_old = (current_time - timestamp).days
                    decay = GNNConfig.TEMPORAL_DECAY_RATE ** days_old
                except:
                    decay = 1.0
            else:
                decay = 1.0
            
            weight = success_count * decay
            weights.append(weight)
        
        avg_weight = np.mean(weights)
        
        # Scale to desired range
        scaled_weight = GNNConfig.MIN_EDGE_WEIGHT + min(avg_weight / 10, 1.0) * (
            GNNConfig.MAX_EDGE_WEIGHT - GNNConfig.MIN_EDGE_WEIGHT
        )
        
        return scaled_weight
    
    def _calculate_temporal_score(self, experiences: List[Dict]) -> float:
        """
        Calculate temporal score based on recency of experiences
        
        Args:
            experiences: List of experiences
            
        Returns:
            Temporal score between 0 and 1
        """
        if not experiences:
            return 0.0
        
        current_time = datetime.now()
        recency_scores = []
        
        for exp in experiences[-10:]:  # Only consider last 10
            timestamp_str = exp.get('timestamp', '')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    days_old = (current_time - timestamp).days
                    score = GNNConfig.TEMPORAL_DECAY_RATE ** days_old
                    recency_scores.append(score)
                except:
                    pass
        
        return np.mean(recency_scores) if recency_scores else 0.5
    
    def _train(self, memory_map: Dict):
        """
        Train the GNN model on current memory map data
        
        Args:
            memory_map: Current memory map
        """
        data = self._prepare_graph_data(memory_map)
        if data is None:
            logger.warning("Failed to prepare training data")
            return
        
        self.model.train()
        
        best_loss = float('inf')
        patience = 10
        patience_counter = 0
        
        for epoch in range(GNNConfig.NUM_EPOCHS):
            self.optimizer.zero_grad()
            
            # Forward pass
            node_embeddings = self.model(data.x, data.edge_index)
            predicted_weights = self.model.predict_edge_weight(node_embeddings, data.edge_index)
            
            # Loss: MSE between predicted and true weights
            loss = F.mse_loss(predicted_weights, data.y)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Early stopping
            if loss.item() < best_loss:
                best_loss = loss.item()
                patience_counter = 0
                self._save_model()
            else:
                patience_counter += 1
            
            if patience_counter >= patience:
                logger.info(f"Early stopping at epoch {epoch + 1}")
                break
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch + 1}/{GNNConfig.NUM_EPOCHS}, Loss: {loss.item():.4f}")
        
        self.is_trained = True
        logger.info(f"GNN training completed. Final loss: {best_loss:.4f}")
    
    def _predict_weights(self, memory_map: Dict) -> Dict[Tuple[str, str], float]:
        """
        Predict edge weights using trained GNN model
        
        Args:
            memory_map: Current memory map
            
        Returns:
            Dictionary of predicted weights
        """
        data = self._prepare_graph_data(memory_map)
        if data is None:
            return self._hardcoded_weights(memory_map)
        
        self.model.eval()
        
        with torch.no_grad():
            node_embeddings = self.model(data.x, data.edge_index)
            predicted_weights = self.model.predict_edge_weight(node_embeddings, data.edge_index)
        
        # Convert to dictionary
        weights_dict = {}
        edge_list = data.edge_index.t().tolist()
        
        for i, (from_idx, to_idx) in enumerate(edge_list):
            from_emotion = self.emotions[from_idx]
            to_emotion = self.emotions[to_idx]
            weight = predicted_weights[i].item()
            weights_dict[(from_emotion, to_emotion)] = weight
        
        return weights_dict
    
    def _hardcoded_weights(self, memory_map: Dict) -> Dict[Tuple[str, str], float]:
        """
        Fallback to hardcoded weights based on success counts
        
        Args:
            memory_map: Current memory map
            
        Returns:
            Dictionary of hardcoded weights
        """
        weights = {}
        
        for (from_emotion, to_emotion), actions in memory_map.get('transitions', {}).items():
            if actions:
                # Simple average of success counts
                avg_success = np.mean([action.get('success_count', 1) for action in actions])
                # Inverse for cost (higher success = lower cost)
                weight = 1.0 / max(0.1, avg_success)
            else:
                # Default weight based on emotion hierarchy
                from_level = EMOTION_HIERARCHY.get(from_emotion, 3)
                to_level = EMOTION_HIERARCHY.get(to_emotion, 3)
                weight = abs(from_level - to_level)
            
            weights[(from_emotion, to_emotion)] = weight
        
        return weights
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            from config import MemoryConfig
            MemoryConfig.ensure_data_directory()
            
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'is_trained': self.is_trained,
                'transition_count': self.transition_count
            }, GNNConfig.GNN_MODEL_FILE)
            
            logger.info(f"GNN model saved to {GNNConfig.GNN_MODEL_FILE}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def _load_model(self):
        """Load trained model from disk if available"""
        try:
            if os.path.exists(GNNConfig.GNN_MODEL_FILE):
                checkpoint = torch.load(GNNConfig.GNN_MODEL_FILE)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                self.is_trained = checkpoint.get('is_trained', False)
                self.transition_count = checkpoint.get('transition_count', 0)
                logger.info(f"GNN model loaded from {GNNConfig.GNN_MODEL_FILE}")
        except Exception as e:
            logger.warning(f"Failed to load model: {e}")


# Utility function
def create_gnn_calculator() -> GNNGraphWeightCalculator:
    """Factory function to create GNN calculator"""
    return GNNGraphWeightCalculator()


if __name__ == "__main__":
    # Test the GNN calculator
    print("\n=== GNN Graph Weight Calculator Test ===")
    
    # Create mock memory map
    mock_memory = {
        'emotional_states': {
            'sad': [{'confidence': 0.8, 'timestamp': datetime.now().isoformat()}],
            'happy': [{'confidence': 0.9, 'timestamp': datetime.now().isoformat()}],
            'anxious': [{'confidence': 0.7, 'timestamp': datetime.now().isoformat()}]
        },
        'transitions': {
            ('sad', 'neutral'): [{'success_count': 3, 'timestamp': datetime.now().isoformat()}],
            ('neutral', 'happy'): [{'success_count': 5, 'timestamp': datetime.now().isoformat()}],
            ('anxious', 'neutral'): [{'success_count': 2, 'timestamp': datetime.now().isoformat()}]
        }
    }
    
    calculator = create_gnn_calculator()
    weights = calculator.calculate_weights(mock_memory)
    
    print("\nCalculated Weights:")
    for transition, weight in weights.items():
        print(f"{transition[0]} -> {transition[1]}: {weight:.3f}")
