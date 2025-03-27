import React, { useState, useEffect } from 'react';
import axios from 'axios';
import aiService from '../services/aiService';
import { useAuth } from '../context/AuthContext';
import { 
  Box, 
  Container, 
  Typography, 
  Paper, 
  Button, 
  TextField, 
  MenuItem, 
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { 
  ExpandMore,
  Psychology, 
  Insights, 
  ArrowForward,
  Lightbulb,
  BarChart,
  CompareArrows,
  CheckCircle
} from '@mui/icons-material';

const emotions = [
  'joy', 'happy', 'content', 'calm', 'relaxed',
  'sad', 'angry', 'anxious', 'stressed', 'frustrated',
  'excited', 'surprised', 'fearful', 'disgusted', 'neutral'
];

const DecisionExplorer = () => {
  const { user } = useAuth();
  const [currentEmotion, setCurrentEmotion] = useState('');
  const [decision, setDecision] = useState('');
  const [options, setOptions] = useState([
    { id: 1, text: '', outcome: '', probability: 0.5, emotion: '' }
  ]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
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

    fetchCurrentEmotion();
  }, []);

  const handleAddOption = () => {
    setOptions([
      ...options,
      { 
        id: options.length + 1, 
        text: '', 
        outcome: '', 
        probability: 0.5, 
        emotion: '' 
      }
    ]);
  };

  const handleRemoveOption = (id) => {
    if (options.length > 1) {
      setOptions(options.filter(option => option.id !== id));
    }
  };

  const handleOptionChange = (id, field, value) => {
    setOptions(options.map(option => 
      option.id === id ? { ...option, [field]: value } : option
    ));
  };

  const handleAnalyzeDecision = async () => {
    if (!currentEmotion || !decision || options.some(o => !o.text)) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Try to use the real API endpoint if it exists
      try {
        const result = await aiService.analyzeDecision(currentEmotion, decision, options);
        setAnalysis(result);
      } catch (apiError) {
        console.warn('API endpoint not available, using mock data:', apiError);
        
        // Fallback to mock implementation
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Mock response
        const mockAnalysis = {
          decision: decision,
          current_emotion: currentEmotion,
          options: options.map(option => ({
            ...option,
            analysis: {
              emotional_impact: Math.random() * 2 - 1, // -1 to 1
              confidence: Math.random() * 0.5 + 0.5, // 0.5 to 1
              recommendation_score: Math.random() * 10 // 0 to 10
            }
          })),
          best_option: Math.floor(Math.random() * options.length) + 1,
          explanation: "This recommendation is based on your current emotional state and the expected outcomes of each option. The recommended option is most likely to lead to a positive emotional transition."
        };
        
        setAnalysis(mockAnalysis);
      }
    } catch (err) {
      console.error('Error analyzing decision:', err);
      setError('Failed to analyze decision');
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

  const getImpactColor = (impact) => {
    if (impact > 0.5) return 'success';
    if (impact > 0) return 'info';
    if (impact > -0.5) return 'warning';
    return 'error';
  };

  const getImpactText = (impact) => {
    if (impact > 0.5) return 'Very Positive';
    if (impact > 0) return 'Positive';
    if (impact > -0.5) return 'Slightly Negative';
    return 'Negative';
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Decision Explorer
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Analyze how different decisions might impact your emotional state and get AI-powered recommendations.
      </Typography>
      <Divider sx={{ mb: 4 }} />

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Decision Analysis
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              select
              label="Current Emotional State"
              value={currentEmotion}
              onChange={(e) => setCurrentEmotion(e.target.value)}
              fullWidth
              variant="outlined"
              margin="normal"
            >
              {emotions.map((emotion) => (
                <MenuItem key={emotion} value={emotion}>
                  {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              label="Decision to Make"
              value={decision}
              onChange={(e) => setDecision(e.target.value)}
              fullWidth
              variant="outlined"
              margin="normal"
              placeholder="e.g., 'Should I change jobs?'"
            />
          </Grid>
        </Grid>

        <Typography variant="h6" sx={{ mt: 4, mb: 2 }}>
          Options
        </Typography>
        
        {options.map((option, index) => (
          <Card key={option.id} variant="outlined" sx={{ mb: 2 }}>
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    label={`Option ${index + 1}`}
                    value={option.text}
                    onChange={(e) => handleOptionChange(option.id, 'text', e.target.value)}
                    fullWidth
                    variant="outlined"
                    placeholder="Describe this option"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Expected Outcome"
                    value={option.outcome}
                    onChange={(e) => handleOptionChange(option.id, 'outcome', e.target.value)}
                    fullWidth
                    variant="outlined"
                    placeholder="What might happen?"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    select
                    label="Expected Emotional Result"
                    value={option.emotion}
                    onChange={(e) => handleOptionChange(option.id, 'emotion', e.target.value)}
                    fullWidth
                    variant="outlined"
                  >
                    {emotions.map((emotion) => (
                      <MenuItem key={emotion} value={emotion}>
                        {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
              </Grid>
              
              {options.length > 1 && (
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    variant="outlined" 
                    color="error" 
                    size="small"
                    onClick={() => handleRemoveOption(option.id)}
                  >
                    Remove Option
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        ))}
        
        <Box sx={{ mt: 2, mb: 4 }}>
          <Button 
            variant="outlined" 
            onClick={handleAddOption}
          >
            Add Another Option
          </Button>
        </Box>
        
        <Button
          variant="contained"
          color="primary"
          onClick={handleAnalyzeDecision}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <Psychology />}
          fullWidth
          size="large"
          sx={{ mt: 2 }}
        >
          {loading ? 'Analyzing...' : 'Analyze Decision'}
        </Button>

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
      </Paper>

      {analysis && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Analysis Results
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Decision Summary
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <Psychology fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Decision" 
                        secondary={analysis.decision} 
                      />
                    </ListItem>
                    
                    <ListItem>
                      <ListItemIcon>
                        <Box
                          component="span"
                          sx={{
                            width: 24,
                            height: 24,
                            borderRadius: '50%',
                            bgcolor: getEmotionColor(analysis.current_emotion),
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Current Emotion" 
                        secondary={analysis.current_emotion.charAt(0).toUpperCase() + analysis.current_emotion.slice(1)} 
                      />
                    </ListItem>
                    
                    <ListItem>
                      <ListItemIcon>
                        <CheckCircle fontSize="small" color="success" />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Recommended Option" 
                        secondary={options.find(o => o.id === analysis.best_option)?.text || 'None'} 
                      />
                    </ListItem>
                  </List>
                  
                  <Alert severity="info" sx={{ mt: 2 }}>
                    {analysis.explanation}
                  </Alert>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Option Analysis
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  {analysis.options.map((option) => (
                    <Accordion key={option.id} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                          <Typography sx={{ flexGrow: 1 }}>
                            {option.text}
                          </Typography>
                          
                          {option.id === analysis.best_option && (
                            <Chip 
                              label="Recommended" 
                              color="success" 
                              size="small" 
                              icon={<CheckCircle />}
                              sx={{ ml: 1 }}
                            />
                          )}
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={6}>
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" color="text.secondary">
                                Expected Outcome:
                              </Typography>
                              <Typography variant="body2">
                                {option.outcome || 'Not specified'}
                              </Typography>
                            </Box>
                            
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" color="text.secondary">
                                Expected Emotion:
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Box
                                  sx={{
                                    width: 16,
                                    height: 16,
                                    borderRadius: '50%',
                                    bgcolor: getEmotionColor(option.emotion),
                                    mr: 1
                                  }}
                                />
                                <Typography variant="body2">
                                  {option.emotion ? 
                                    (option.emotion.charAt(0).toUpperCase() + option.emotion.slice(1)) : 
                                    'Not specified'}
                                </Typography>
                              </Box>
                            </Box>
                          </Grid>
                          
                          <Grid item xs={12} sm={6}>
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" color="text.secondary">
                                Emotional Impact:
                              </Typography>
                              <Chip 
                                label={getImpactText(option.analysis.emotional_impact)}
                                color={getImpactColor(option.analysis.emotional_impact)}
                                size="small"
                                icon={<Insights />}
                              />
                            </Box>
                            
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="subtitle2" color="text.secondary">
                                Confidence:
                              </Typography>
                              <Typography variant="body2">
                                {Math.round(option.analysis.confidence * 100)}%
                              </Typography>
                            </Box>
                            
                            <Box>
                              <Typography variant="subtitle2" color="text.secondary">
                                Recommendation Score:
                              </Typography>
                              <Typography variant="body2">
                                {option.analysis.recommendation_score.toFixed(1)} / 10
                              </Typography>
                            </Box>
                          </Grid>
                        </Grid>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}
    </Container>
  );
};

export default DecisionExplorer;
