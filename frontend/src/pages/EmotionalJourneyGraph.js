import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, CircularProgress, Button } from '@mui/material';
import axios from '../utils/axiosConfig';

const EmotionalJourneyGraph = () => {
  const [loading, setLoading] = useState(true);
  const [graphData, setGraphData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEmotionalJourneyData = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/emotional-journey');
        setGraphData(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching emotional journey data:', err);
        setError('Failed to load emotional journey data. Please try again later.');
        setLoading(false);
      }
    };

    fetchEmotionalJourneyData();
  }, []);

  const renderGraph = () => {
    if (!graphData || !graphData.nodes || !graphData.edges) {
      return (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <Typography variant="body1" color="text.secondary">
            No emotional journey data available. Start journaling to see your emotional path.
          </Typography>
        </Box>
      );
    }

    // This is a simplified visualization - in a real implementation,
    // you would use a graph visualization library like D3.js or react-force-graph
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Your Emotional States
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, my: 2 }}>
          {graphData.nodes.map((node) => (
            <Paper
              key={node.id}
              elevation={3}
              sx={{
                p: 2,
                borderRadius: 2,
                bgcolor: getEmotionColor(node.emotion),
                color: '#fff',
                minWidth: 100,
                textAlign: 'center'
              }}
            >
              <Typography variant="subtitle1">{node.emotion}</Typography>
              <Typography variant="caption">
                {new Date(node.timestamp).toLocaleDateString()}
              </Typography>
            </Paper>
          ))}
        </Box>

        <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
          Recommended Path to Positive Emotions
        </Typography>
        {graphData.optimalPath && graphData.optimalPath.length > 0 ? (
          <Box sx={{ display: 'flex', alignItems: 'center', overflowX: 'auto', py: 2 }}>
            {graphData.optimalPath.map((state, index) => (
              <React.Fragment key={index}>
                <Paper
                  elevation={3}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    bgcolor: getEmotionColor(state),
                    color: '#fff',
                    minWidth: 100,
                    textAlign: 'center'
                  }}
                >
                  <Typography variant="subtitle1">{state}</Typography>
                </Paper>
                {index < graphData.optimalPath.length - 1 && (
                  <Box sx={{ mx: 1, color: 'text.secondary' }}>→</Box>
                )}
              </React.Fragment>
            ))}
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No optimal path available yet.
          </Typography>
        )}
      </Box>
    );
  };

  // Helper function to get color based on emotion
  const getEmotionColor = (emotion) => {
    const emotionColors = {
      happy: '#4CAF50',
      sad: '#2196F3',
      angry: '#F44336',
      anxious: '#FF9800',
      neutral: '#9E9E9E',
      excited: '#8BC34A',
      calm: '#03A9F4',
      frustrated: '#E91E63',
      content: '#009688',
      worried: '#FFC107'
    };

    return emotionColors[emotion.toLowerCase()] || '#9E9E9E';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ textAlign: 'center', my: 4 }}>
        <Typography variant="body1" color="error" gutterBottom>
          {error}
        </Typography>
        <Button
          variant="contained"
          onClick={() => window.location.reload()}
          sx={{ mt: 2 }}
        >
          Try Again
        </Button>
      </Box>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h5" gutterBottom>
        Your Emotional Journey
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        This graph visualizes your emotional states over time and shows the optimal path to reach positive emotions based on your personal history.
      </Typography>
      {renderGraph()}
    </Paper>
  );
};

export default EmotionalJourneyGraph;
