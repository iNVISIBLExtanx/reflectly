import axios from 'axios';

/**
 * Service for interacting with AI-related API endpoints
 */
const aiService = {
  /**
   * Find an emotional path from current to target emotion
   * @param {string} currentEmotion - The user's current emotional state
   * @param {string} targetEmotion - The target emotional state
   * @returns {Promise} - The API response with path and actions
   */
  findEmotionalPath: async (currentEmotion, targetEmotion) => {
    try {
      const response = await axios.post('/api/emotional-path', {
        current_emotion: currentEmotion,
        target_emotion: targetEmotion
      });
      return response.data;
    } catch (error) {
      console.error('Error finding emotional path:', error);
      throw error;
    }
  },

  /**
   * Predict the next emotional state
   * @param {string} currentEmotion - The user's current emotional state
   * @param {string} modelType - The type of model to use (markov or bayesian)
   * @returns {Promise} - The API response with predicted emotion and probability
   */
  predictNextEmotion: async (currentEmotion, modelType = 'markov') => {
    try {
      const response = await axios.post('/api/predict/emotion', {
        current_emotion: currentEmotion,
        model_type: modelType
      });
      return response.data;
    } catch (error) {
      console.error('Error predicting next emotion:', error);
      throw error;
    }
  },

  /**
   * Predict a sequence of emotional states
   * @param {string} currentEmotion - The user's current emotional state
   * @param {number} sequenceLength - The length of the sequence to predict
   * @param {string} modelType - The type of model to use (markov or bayesian)
   * @returns {Promise} - The API response with sequence and probabilities
   */
  predictEmotionalSequence: async (currentEmotion, sequenceLength = 3, modelType = 'markov') => {
    try {
      const response = await axios.post('/api/predict/emotional-sequence', {
        current_emotion: currentEmotion,
        sequence_length: sequenceLength,
        model_type: modelType
      });
      return response.data;
    } catch (error) {
      console.error('Error predicting emotional sequence:', error);
      throw error;
    }
  },

  /**
   * Get the current agent state
   * @returns {Promise} - The API response with agent state
   */
  getAgentState: async () => {
    try {
      const response = await axios.get('/api/agent/state');
      return response.data;
    } catch (error) {
      console.error('Error getting agent state:', error);
      throw error;
    }
  },

  /**
   * Create an action plan for the agent
   * @param {string} currentEmotion - The user's current emotional state
   * @param {string} targetEmotion - The target emotional state
   * @returns {Promise} - The API response with action plan
   */
  createActionPlan: async (currentEmotion, targetEmotion) => {
    try {
      const response = await axios.post('/api/agent/plan', {
        current_emotion: currentEmotion,
        target_emotion: targetEmotion
      });
      return response.data;
    } catch (error) {
      console.error('Error creating action plan:', error);
      throw error;
    }
  },

  /**
   * Execute an action in the agent's plan
   * @param {string} actionId - The ID of the action to execute
   * @param {Object} feedback - Optional feedback about the action
   * @returns {Promise} - The API response with updated agent state
   */
  executeAction: async (actionId, feedback = null) => {
    try {
      const payload = { action_id: actionId };
      if (feedback) {
        payload.feedback = feedback;
      }
      
      const response = await axios.post('/api/agent/execute', payload);
      return response.data;
    } catch (error) {
      console.error('Error executing action:', error);
      throw error;
    }
  },

  /**
   * Analyze a decision with multiple options
   * @param {string} currentEmotion - The user's current emotional state
   * @param {string} decision - The decision to be made
   * @param {Array} options - The options to analyze
   * @returns {Promise} - The API response with analysis results
   */
  analyzeDecision: async (currentEmotion, decision, options) => {
    try {
      const response = await axios.post('/api/agent/analyze-decision', {
        current_emotion: currentEmotion,
        decision: decision,
        options: options
      });
      return response.data;
    } catch (error) {
      console.error('Error analyzing decision:', error);
      throw error;
    }
  },
  
  /**
   * Get the emotional graph with transition probabilities
   * @returns {Promise} - The API response with emotional graph data
   */
  getEmotionalGraph: async () => {
    try {
      const response = await axios.get('/api/probabilistic/emotional-graph');
      return response.data.graph;
    } catch (error) {
      console.error('Error getting emotional graph:', error);
      throw error;
    }
  }
};

export default aiService;
