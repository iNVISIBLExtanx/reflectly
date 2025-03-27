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
  Card,
  CardContent,
  Divider,
  Slider,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Chip,
  Grid
} from '@mui/material';
import { 
  Timeline,
  Insights, 
  TrendingUp, 
  Psychology
} from '@mui/icons-material';

const emotions = [
  'joy', 'happy', 'content', 'calm', 'relaxed',
  'sad', 'angry', 'anxious', 'stressed', 'frustrated',
  'excited', 'surprised', 'fearful', 'disgusted', 'neutral'
];

const ProbabilityGraph = () => {
  const { user } = useAuth();
  const [currentEmotion, setCurrentEmotion] = useState('');
  const [sequenceLength, setSequenceLength] = useState(3);
  const [modelType, setModelType] = useState('markov');
  const [nextEmotion, setNextEmotion] = useState(null);
  const [sequence, setSequence] = useState([]);
  const [probabilities, setProbabilities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [sequenceLoading, setSequenceLoading] = useState(false);
  const [graphLoading, setGraphLoading] = useState(false);
  const [emotionalGraph, setEmotionalGraph] = useState(null);
  const [error, setError] = useState('');

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

    // Fetch the emotional graph data
    const fetchEmotionalGraph = async () => {
      try {
        setGraphLoading(true);
        const result = await aiService.getEmotionalGraph();
        setEmotionalGraph(result);
      } catch (err) {
        console.error('Error fetching emotional graph:', err);
      } finally {
        setGraphLoading(false);
      }
    };

    fetchCurrentEmotion();
    fetchEmotionalGraph();
  }, []);

  const handlePredictNextEmotion = async () => {
    if (!currentEmotion) {
      setError('Please select a current emotion');
      return;
    }

    setPredictionLoading(true);
    setError('');
    
    try {
      const result = await aiService.predictNextEmotion(currentEmotion, modelType);
      
      setNextEmotion({
        emotion: result.predicted_emotion,
        probability: result.probability
      });
    } catch (err) {
      console.error('Error predicting next emotion:', err);
      setError(err.response?.data?.message || 'Failed to predict next emotion');
    } finally {
      setPredictionLoading(false);
    }
  };

  const handlePredictSequence = async () => {
    if (!currentEmotion) {
      setError('Please select a current emotion');
      return;
    }

    setSequenceLoading(true);
    setError('');
    
    try {
      const result = await aiService.predictEmotionalSequence(currentEmotion, sequenceLength, modelType);
      
      setSequence(result.sequence || []);
      setProbabilities(result.probabilities || []);
    } catch (err) {
      console.error('Error predicting emotional sequence:', err);
      setError(err.response?.data?.message || 'Failed to predict emotional sequence');
    } finally {
      setSequenceLoading(false);
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

  const getProbabilityColor = (probability) => {
    if (probability >= 0.7) return 'success';
    if (probability >= 0.4) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Emotional Probability Analysis
      </Typography>
      <Typography variant="body1" paragraph>
        Predict your future emotional states using probabilistic reasoning.
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ mb: 3 }}>
          <TextField
            select
            label="Current Emotional State"
            value={currentEmotion}
            onChange={(e) => setCurrentEmotion(e.target.value)}
            fullWidth
            variant="outlined"
            sx={{ mb: 2 }}
          >
            {emotions.map((emotion) => (
              <MenuItem key={emotion} value={emotion}>
                {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
              </MenuItem>
            ))}
          </TextField>

          <FormControl component="fieldset" sx={{ mb: 2 }}>
            <FormLabel component="legend">Prediction Model</FormLabel>
            <RadioGroup
              row
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
            >
              <FormControlLabel value="markov" control={<Radio />} label="Markov Chain" />
              <FormControlLabel value="bayesian" control={<Radio />} label="Bayesian Network" />
            </RadioGroup>
          </FormControl>

          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>Sequence Length</Typography>
            <Slider
              value={sequenceLength}
              onChange={(e, newValue) => setSequenceLength(newValue)}
              valueLabelDisplay="auto"
              step={1}
              marks
              min={1}
              max={10}
              disabled={sequenceLoading}
            />
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Button
                variant="contained"
                color="primary"
                onClick={handlePredictNextEmotion}
                disabled={predictionLoading}
                startIcon={predictionLoading ? <CircularProgress size={20} /> : <Psychology />}
                fullWidth
                sx={{ mb: { xs: 2, sm: 0 } }}
              >
                {predictionLoading ? 'Predicting...' : 'Predict Next Emotion'}
              </Button>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Button
                variant="contained"
                color="secondary"
                onClick={handlePredictSequence}
                disabled={sequenceLoading}
                startIcon={sequenceLoading ? <CircularProgress size={20} /> : <Timeline />}
                fullWidth
              >
                {sequenceLoading ? 'Predicting...' : 'Predict Sequence'}
              </Button>
            </Grid>
          </Grid>

          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
        </Box>
      </Paper>

      {emotionalGraph && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Emotional Transition Graph
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <Typography variant="body2" paragraph>
            This graph shows the probability of transitioning from one emotional state to another based on your emotional history.
          </Typography>
          
          <Box sx={{ overflowX: 'auto', mb: 2 }}>
            <Box sx={{ minWidth: 600, p: 2 }}>
              {Object.keys(emotionalGraph).map(fromEmotion => (
                <Box key={fromEmotion} sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
                    From: {fromEmotion.charAt(0).toUpperCase() + fromEmotion.slice(1)}
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {Object.entries(emotionalGraph[fromEmotion]).map(([toEmotion, probability]) => (
                      <Chip
                        key={toEmotion}
                        label={`${toEmotion}: ${Math.round(probability * 100)}%`}
                        sx={{
                          bgcolor: getEmotionColor(toEmotion),
                          color: '#000',
                          fontWeight: probability > 0.3 ? 'bold' : 'normal',
                          opacity: 0.3 + probability * 0.7
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              ))}
            </Box>
          </Box>
        </Paper>
      )}
      
      <Grid container spacing={3}>
        {nextEmotion && (
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Next Emotion Prediction
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      bgcolor: getEmotionColor(nextEmotion.emotion),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2
                    }}
                  >
                    <Typography variant="body2" fontWeight="bold">
                      {nextEmotion.emotion.slice(0, 1).toUpperCase()}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="h5">
                      {nextEmotion.emotion.charAt(0).toUpperCase() + nextEmotion.emotion.slice(1)}
                    </Typography>
                    <Chip 
                      label={`${Math.round(nextEmotion.probability * 100)}% probability`}
                      color={getProbabilityColor(nextEmotion.probability)}
                      size="small"
                    />
                  </Box>
                </Box>
                
                <Typography variant="body2" color="text.secondary">
                  Based on your emotional history and current state, our {modelType === 'markov' ? 'Markov chain' : 'Bayesian network'} model 
                  predicts that your next emotional state is likely to be {nextEmotion.emotion}.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        {sequence.length > 0 && (
          <Grid item xs={12} md={nextEmotion ? 6 : 12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Emotional Sequence Prediction
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Box sx={{ display: 'flex', alignItems: 'center', overflowX: 'auto', pb: 1 }}>
                  {sequence.map((emotion, index) => (
                    <React.Fragment key={index}>
                      {index > 0 && (
                        <TrendingUp sx={{ mx: 1, color: 'text.secondary' }} />
                      )}
                      <Box sx={{ textAlign: 'center', minWidth: 80 }}>
                        <Box
                          sx={{
                            width: 40,
                            height: 40,
                            borderRadius: '50%',
                            bgcolor: getEmotionColor(emotion),
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            mx: 'auto',
                            mb: 1
                          }}
                        >
                          <Typography variant="body2" fontWeight="bold">
                            {emotion.slice(0, 1).toUpperCase()}
                          </Typography>
                        </Box>
                        <Typography variant="body2" noWrap>
                          {emotion}
                        </Typography>
                        <Chip 
                          label={`${Math.round((probabilities[index] || 0) * 100)}%`}
                          color={getProbabilityColor(probabilities[index] || 0)}
                          size="small"
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                    </React.Fragment>
                  ))}
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  This sequence represents the most likely path your emotional state will take 
                  over the next {sequence.length} transitions, according to our {modelType === 'markov' ? 'Markov chain' : 'Bayesian network'} model.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default ProbabilityGraph;
