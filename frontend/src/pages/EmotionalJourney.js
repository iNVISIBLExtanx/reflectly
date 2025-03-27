import React, { useState, useEffect } from 'react';
import aiService from '../services/aiService';
import { 
  Box, 
  Container, 
  Typography, 
  Tabs, 
  Tab, 
  Paper,
  Divider
} from '@mui/material';
import { 
  Route, 
  Psychology, 
  SmartToy
} from '@mui/icons-material';
import EmotionalPathView from '../components/ai/EmotionalPathView';
import ProbabilityGraph from '../components/ai/ProbabilityGraph';
import AgentStateView from '../components/ai/AgentStateView';

const EmotionalJourney = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Emotional Journey
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Explore your emotional landscape with advanced AI tools to understand, predict, and navigate your emotional states.
      </Typography>
      <Divider sx={{ mb: 4 }} />

      <Paper sx={{ mb: 4 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          indicatorColor="primary"
          textColor="primary"
          aria-label="emotional journey tabs"
        >
          <Tab 
            icon={<Route />} 
            label="Emotional Path" 
            iconPosition="start"
          />
          <Tab 
            icon={<Psychology />} 
            label="Probability Analysis" 
            iconPosition="start"
          />
          <Tab 
            icon={<SmartToy />} 
            label="Intelligent Agent" 
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      <Box sx={{ mb: 4 }}>
        {activeTab === 0 && <EmotionalPathView />}
        {activeTab === 1 && <ProbabilityGraph />}
        {activeTab === 2 && <AgentStateView />}
      </Box>
    </Container>
  );
};

export default EmotionalJourney;
