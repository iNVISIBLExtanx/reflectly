import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import { 
  ArrowForward, 
  Route, 
  EmojiEmotions, 
  DirectionsRun,
  CheckCircle
} from '@mui/icons-material';

const emotions = [
  'joy', 'happy', 'content', 'calm', 'relaxed',
  'sad', 'angry', 'anxious', 'stressed', 'frustrated',
  'excited', 'surprised', 'fearful', 'disgusted', 'neutral'
];

const EmotionalPathView = () => {
  const { user } = useAuth();
  const [currentEmotion, setCurrentEmotion] = useState('');
  const [targetEmotion, setTargetEmotion] = useState('');
  const [path, setPath] = useState([]);
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Get user's current emotion from the latest journal entry
    const fetchCurrentEmotion = async () => {
      try {
        const response = await axios.get('/api/journal');
        if (response.data.entries && response.data.entries.length > 0) {
          const latestEntry = response.data.entries[0];
          if (latestEntry.emotion && latestEntry.emotion.primary_emotion) {
            setCurrentEmotion(latestEntry.emotion.primary_emotion);
          }
        }
      } catch (err) {
        console.error('Error fetching current emotion:', err);
      }
    };

    fetchCurrentEmotion();
  }, []);

  const handleFindPath = async () => {
    if (!currentEmotion || !targetEmotion) {
      setError('Please select both current and target emotions');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess(false);
    
    try {
      const result = await aiService.findEmotionalPath(currentEmotion, targetEmotion);
      
      setPath(result.path || []);
      setActions(result.actions || []);
      setSuccess(true);
    } catch (err) {
      console.error('Error finding emotional path:', err);
      setError(err.response?.data?.message || 'Failed to find emotional path');
    } finally {
      setLoading(false);
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

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Emotional Path Finder
      </Typography>
      <Typography variant="body1" paragraph>
        Find the optimal path from your current emotional state to a desired emotional state.
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

        <Button
          variant="contained"
          color="primary"
          onClick={handleFindPath}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <Route />}
          fullWidth
        >
          {loading ? 'Finding Path...' : 'Find Emotional Path'}
        </Button>

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
      </Paper>

      {success && path.length > 0 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Your Emotional Journey
          </Typography>
          
          <Stepper orientation="vertical" sx={{ mb: 4 }}>
            {path.map((emotion, index) => (
              <Step key={index} active={true} completed={index < path.length - 1}>
                <StepLabel 
                  icon={
                    <EmojiEmotions 
                      sx={{ 
                        color: getEmotionColor(emotion),
                        bgcolor: 'white',
                        borderRadius: '50%',
                        p: 0.5
                      }} 
                    />
                  }
                >
                  <Typography variant="subtitle1" fontWeight="bold">
                    {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                  </Typography>
                </StepLabel>
                <StepContent>
                  {index < actions.length && (
                    <Card variant="outlined" sx={{ mb: 2, mt: 1 }}>
                      <CardContent>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          Suggested Actions:
                        </Typography>
                        <List dense>
                          {actions[index]?.actions?.map((action, actionIndex) => (
                            <ListItem key={actionIndex}>
                              <ListItemIcon>
                                <DirectionsRun fontSize="small" />
                              </ListItemIcon>
                              <ListItemText 
                                primary={typeof action === 'string' ? action : action.action} 
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  )}
                  
                  {index < path.length - 1 && (
                    <Box sx={{ display: 'flex', alignItems: 'center', my: 1 }}>
                      <ArrowForward color="action" />
                      <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                        Next step: {path[index + 1]}
                      </Typography>
                    </Box>
                  )}
                </StepContent>
              </Step>
            ))}
          </Stepper>
          
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Chip 
              icon={<CheckCircle />} 
              label="Journey Complete" 
              color="success" 
              variant="outlined" 
            />
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default EmotionalPathView;
