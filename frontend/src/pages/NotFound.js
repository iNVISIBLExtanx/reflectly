import React from 'react';
import { Box, Container, Typography, Button, Paper } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';

const NotFound = () => {
  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Paper 
        elevation={3} 
        sx={{ 
          p: 5, 
          textAlign: 'center',
          borderRadius: 2
        }}
      >
        <SentimentDissatisfiedIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
        
        <Typography variant="h3" component="h1" gutterBottom>
          404 - Page Not Found
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph sx={{ mb: 4 }}>
          The page you are looking for doesn't exist or has been moved.
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button 
            variant="contained" 
            component={RouterLink} 
            to="/"
            size="large"
          >
            Go to Home
          </Button>
          
          <Button 
            variant="outlined" 
            component={RouterLink} 
            to="/journal"
            size="large"
          >
            Go to Journal
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NotFound;
