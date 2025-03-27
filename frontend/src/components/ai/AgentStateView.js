import React, { useState, useEffect } from 'react';
import aiService from '../../services/aiService';
import { useAuth } from '../../context/AuthContext';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  TextField, 
  MenuItem, 
  CircularProgress,
  Card,
  CardContent,
  CardActions,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Rating,
  Grid,
  Chip,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  SmartToy, 
  EmojiEmotions, 
  PlayArrow, 
  Refresh,
  CheckCircle,
  Info,
  ThumbUp,
  ThumbDown
} from '@mui/icons-material';

const emotions = [
  'joy', 'happy', 'content', 'calm', 'relaxed',
  'sad', 'angry', 'anxious', 'stressed', 'frustrated',
  'excited', 'surprised', 'fearful', 'disgusted', 'neutral'
];

const AgentStateView = () => {
  const { user } = useAuth();
  const [agentState, setAgentState] = useState(null);
  const [currentEmotion, setCurrentEmotion] = useState('');
  const [targetEmotion, setTargetEmotion] = useState('');
  const [loading, setLoading] = useState(false);
  const [planLoading, setPlanLoading] = useState(false);
  const [executeLoading, setExecuteLoading] = useState(false);
  const [error, setError] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [actionRating, setActionRating] = useState(0);

  useEffect(() => {
    fetchAgentState();
  }, []);

  const fetchAgentState = async () => {
    setLoading(true);
    try {
      const result = await aiService.getAgentState();
      setAgentState(result);
      
      if (result.current_emotion) {
        setCurrentEmotion(result.current_emotion);
      }
      
      if (result.target_emotion) {
        setTargetEmotion(result.target_emotion);
      }
    } catch (err) {
      console.error('Error fetching agent state:', err);
      setError('Failed to fetch agent state');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async () => {
    if (!currentEmotion || !targetEmotion) {
      setError('Please select both current and target emotions');
      return;
    }

    setPlanLoading(true);
    setError('');
    
    try {
      const result = await aiService.createActionPlan(currentEmotion, targetEmotion);
      
      setAgentState(result);
    } catch (err) {
      console.error('Error creating action plan:', err);
      setError(err.response?.data?.message || 'Failed to create action plan');
    } finally {
      setPlanLoading(false);
    }
  };

  const handleExecuteAction = async (actionId) => {
    setExecuteLoading(true);
    setError('');
    
    try {
      // Include feedback if available
      let feedbackData = null;
      if (feedback) {
        feedbackData = {
          rating: actionRating,
          comment: feedback
        };
      }
      
      const result = await aiService.executeAction(actionId, feedbackData);
      setAgentState(result);
      
      // Reset feedback
      setFeedback(null);
      setActionRating(0);
    } catch (err) {
      console.error('Error executing action:', err);
      setError(err.response?.data?.message || 'Failed to execute action');
    } finally {
      setExecuteLoading(false);
    }
  };

  const getEmotionColor = (emotion) => {
    const emotionColors = {
      'joy': '#FFD700',
      'happy': '#FFA500',
      'content': '#98FB98',
      'calm': '#87CEEB',
      'relaxed': '#ADD8E6',
      'sad': '#6495ED',
      'angry': '#FF6347',
      'anxious': '#BA55D3',
      'stressed': '#FF69B4',
      'frustrated': '#CD5C5C',
      'excited': '#FF4500',
      'surprised': '#00FFFF',
      'fearful': '#9370DB',
      'disgusted': '#8FBC8F',
      'neutral': '#DCDCDC'
    };
    
    return emotionColors[emotion] || '#DCDCDC';
  };

  const getCurrentAction = () => {
    if (!agentState || !agentState.action_plan || agentState.action_plan.length === 0) {
      return null;
    }
    
    const currentIndex = agentState.current_action_index || 0;
    if (currentIndex >= agentState.action_plan.length) {
      return null;
    }
    
    return agentState.action_plan[currentIndex];
  };

  const currentAction = getCurrentAction();

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Emotional Intelligence Agent
      </Typography>
      <Typography variant="body1" paragraph>
        Your personal AI assistant for emotional well-being and growth.
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2, mb: 3 }}>
          <TextField
            select
            label="Current Emotional State"
            value={currentEmotion}
            onChange={(e) => setCurrentEmotion(e.target.value)}
            fullWidth
            variant="outlined"
          >
            {emotions.map((emotion) => (
              <MenuItem key={emotion} value={emotion}>
                {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Target Emotional State"
            value={targetEmotion}
            onChange={(e) => setTargetEmotion(e.target.value)}
            fullWidth
            variant="outlined"
          >
            {emotions.map((emotion) => (
              <MenuItem key={emotion} value={emotion}>
                {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
              </MenuItem>
            ))}
          </TextField>
        </Box>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleCreatePlan}
            disabled={planLoading}
            startIcon={planLoading ? <CircularProgress size={20} /> : <SmartToy />}
            fullWidth
          >
            {planLoading ? 'Creating Plan...' : 'Create Action Plan'}
          </Button>
          
          <Button
            variant="outlined"
            color="secondary"
            onClick={fetchAgentState}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <Refresh />}
          >
            Refresh
          </Button>
        </Box>

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
      </Paper>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : agentState ? (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Agent State
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Current Emotion:
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        bgcolor: getEmotionColor(agentState.current_emotion || 'neutral'),
                        mr: 1
                      }}
                    />
                    <Typography>
                      {agentState.current_emotion ? 
                        (agentState.current_emotion.charAt(0).toUpperCase() + agentState.current_emotion.slice(1)) : 
                        'Not set'}
                    </Typography>
                  </Box>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Target Emotion:
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        bgcolor: getEmotionColor(agentState.target_emotion || 'neutral'),
                        mr: 1
                      }}
                    />
                    <Typography>
                      {agentState.target_emotion ? 
                        (agentState.target_emotion.charAt(0).toUpperCase() + agentState.target_emotion.slice(1)) : 
                        'Not set'}
                    </Typography>
                  </Box>
                </Box>
                
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Progress:
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    {agentState.action_plan && agentState.action_plan.length > 0 ? (
                      <Chip 
                        label={`Step ${(agentState.current_action_index || 0) + 1} of ${agentState.action_plan.length}`}
                        color="primary"
                        variant="outlined"
                      />
                    ) : (
                      <Chip 
                        label="No active plan"
                        color="default"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={8}>
            {currentAction ? (
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Current Action
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body1" fontWeight="medium">
                      {currentAction.description || 'Take the recommended action to progress toward your target emotional state.'}
                    </Typography>
                  </Alert>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Expected Outcome:
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <Box
                        sx={{
                          width: 24,
                          height: 24,
                          borderRadius: '50%',
                          bgcolor: getEmotionColor(currentAction.expected_emotion || 'neutral'),
                          mr: 1
                        }}
                      />
                      <Typography>
                        {currentAction.expected_emotion ? 
                          (currentAction.expected_emotion.charAt(0).toUpperCase() + currentAction.expected_emotion.slice(1)) : 
                          'Unknown'}
                      </Typography>
                      
                      {currentAction.confidence && (
                        <Chip 
                          label={`${Math.round(currentAction.confidence * 100)}% confidence`}
                          color={currentAction.confidence > 0.7 ? 'success' : 'warning'}
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      How did this action work for you?
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Rating
                        value={actionRating}
                        onChange={(event, newValue) => {
                          setActionRating(newValue);
                        }}
                        max={5}
                      />
                      <TextField
                        placeholder="Optional feedback"
                        variant="outlined"
                        size="small"
                        value={feedback || ''}
                        onChange={(e) => setFeedback(e.target.value)}
                        sx={{ ml: 2, flexGrow: 1 }}
                      />
                    </Box>
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleExecuteAction(currentAction.action_id)}
                    disabled={executeLoading}
                    startIcon={executeLoading ? <CircularProgress size={20} /> : <PlayArrow />}
                    fullWidth
                  >
                    {executeLoading ? 'Processing...' : 'Complete & Continue'}
                  </Button>
                </CardActions>
              </Card>
            ) : agentState.action_plan && agentState.action_plan.length > 0 ? (
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CheckCircle color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6">
                      Plan Complete
                    </Typography>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Alert severity="success" sx={{ mb: 3 }}>
                    You have completed all actions in your current plan.
                  </Alert>
                  
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleCreatePlan}
                    startIcon={<Refresh />}
                    fullWidth
                  >
                    Create New Plan
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    No Active Plan
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Alert severity="info" sx={{ mb: 3 }}>
                    Create an action plan to get personalized guidance for transitioning from your current emotional state to your desired target state.
                  </Alert>
                  
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleCreatePlan}
                    startIcon={<SmartToy />}
                    fullWidth
                  >
                    Create Action Plan
                  </Button>
                </CardContent>
              </Card>
            )}
            
            {agentState.action_plan && agentState.action_plan.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Action Plan Overview
                </Typography>
                <Stepper 
                  activeStep={agentState.current_action_index || 0} 
                  orientation="vertical"
                >
                  {agentState.action_plan.map((action, index) => (
                    <Step key={index} completed={index < (agentState.current_action_index || 0)}>
                      <StepLabel>
                        <Typography variant="subtitle1">
                          {action.description || `Step ${index + 1}`}
                        </Typography>
                      </StepLabel>
                      <StepContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                            Expected outcome:
                          </Typography>
                          <Box
                            sx={{
                              width: 16,
                              height: 16,
                              borderRadius: '50%',
                              bgcolor: getEmotionColor(action.expected_emotion || 'neutral'),
                              mr: 0.5
                            }}
                          />
                          <Typography variant="body2">
                            {action.expected_emotion || 'Unknown'}
                          </Typography>
                        </Box>
                        
                        {index === (agentState.current_action_index || 0) && (
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleExecuteAction(action.action_id)}
                            disabled={executeLoading}
                            startIcon={<PlayArrow />}
                            sx={{ mt: 1 }}
                          >
                            Complete
                          </Button>
                        )}
                      </StepContent>
                    </Step>
                  ))}
                </Stepper>
              </Box>
            )}
          </Grid>
        </Grid>
      ) : (
        <Alert severity="info">
          No agent state available. Create an action plan to get started.
        </Alert>
      )}
    </Box>
  );
};

export default AgentStateView;
