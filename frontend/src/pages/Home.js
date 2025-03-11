import React from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Import icons
import ChatIcon from '@mui/icons-material/Chat';
import EmojiEmotionsIcon from '@mui/icons-material/EmojiEmotions';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import MemoryIcon from '@mui/icons-material/Memory';

const Home = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isAuthenticated } = useAuth();

  const features = [
    {
      title: 'Conversational Journaling',
      description: 'Chat with yourself in a familiar interface. Document your daily experiences, emotions, and goals with ease.',
      icon: <ChatIcon fontSize="large" color="primary" />
    },
    {
      title: 'Emotion Tracking',
      description: 'Our AI analyzes your emotions and provides support when you need it most, celebrating your happiness and helping during tough times.',
      icon: <EmojiEmotionsIcon fontSize="large" color="primary" />
    },
    {
      title: 'Goal Setting',
      description: 'Set personal goals and track your progress. Receive encouragement and celebrate milestones along the way.',
      icon: <TrackChangesIcon fontSize="large" color="primary" />
    },
    {
      title: 'Memory Management',
      description: 'Intelligent retrieval of past positive experiences when you need them most, helping you remember the good times.',
      icon: <MemoryIcon fontSize="large" color="primary" />
    }
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box 
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: { xs: 8, md: 12 },
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography 
                variant="h2" 
                component="h1" 
                gutterBottom
                sx={{ 
                  fontWeight: 700,
                  fontSize: { xs: '2.5rem', md: '3.5rem' }
                }}
              >
                Reflect on Your Journey
              </Typography>
              <Typography 
                variant="h5" 
                component="p" 
                gutterBottom
                sx={{ mb: 4, opacity: 0.9 }}
              >
                A personal journaling app designed to help you engage in meaningful self-reflection through a conversational interface.
              </Typography>
              <Box sx={{ mt: 4 }}>
                <Button
                  component={RouterLink}
                  to={isAuthenticated ? "/journal" : "/register"}
                  variant="contained"
                  size="large"
                  color="secondary"
                  sx={{ 
                    mr: 2, 
                    px: 4, 
                    py: 1.5,
                    fontSize: '1.1rem'
                  }}
                >
                  {isAuthenticated ? "Start Journaling" : "Get Started"}
                </Button>
                {!isAuthenticated && (
                  <Button
                    component={RouterLink}
                    to="/login"
                    variant="outlined"
                    size="large"
                    sx={{ 
                      px: 4, 
                      py: 1.5,
                      fontSize: '1.1rem',
                      color: 'white',
                      borderColor: 'white',
                      '&:hover': {
                        borderColor: 'white',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)'
                      }
                    }}
                  >
                    Login
                  </Button>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={6} sx={{ display: { xs: 'none', md: 'block' } }}>
              <Box 
                component="img"
                src="/hero-image.png" 
                alt="Reflectly App"
                sx={{
                  width: '100%',
                  maxWidth: 500,
                  height: 'auto',
                  display: 'block',
                  margin: '0 auto',
                  filter: 'drop-shadow(0 10px 20px rgba(0,0,0,0.2))',
                  transform: 'translateY(20px)'
                }}
              />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography 
          variant="h3" 
          component="h2" 
          align="center" 
          gutterBottom
          sx={{ mb: 6 }}
        >
          Key Features
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 20px rgba(0,0,0,0.1)'
                  }
                }}
                elevation={2}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
                  <Box sx={{ mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography gutterBottom variant="h5" component="h3">
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* How It Works Section */}
      <Box sx={{ bgcolor: theme.palette.grey[50], py: 8 }}>
        <Container maxWidth="lg">
          <Typography 
            variant="h3" 
            component="h2" 
            align="center" 
            gutterBottom
            sx={{ mb: 6 }}
          >
            How It Works
          </Typography>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box 
                component="img"
                src="/app-screenshot.png" 
                alt="Reflectly App Screenshot"
                sx={{
                  width: '100%',
                  height: 'auto',
                  borderRadius: 2,
                  boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box>
                <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600 }}>
                  1. Start a Conversation
                </Typography>
                <Typography variant="body1" paragraph>
                  Begin by typing or speaking your thoughts in our chat-like interface. Share your day, express your feelings, or document your achievements.
                </Typography>

                <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600, mt: 3 }}>
                  2. Receive Intelligent Responses
                </Typography>
                <Typography variant="body1" paragraph>
                  Our AI analyzes your emotions and provides thoughtful responses to help you reflect deeper and gain insights about yourself.
                </Typography>

                <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600, mt: 3 }}>
                  3. Track Your Progress
                </Typography>
                <Typography variant="body1" paragraph>
                  Set personal goals and monitor your progress over time. Celebrate achievements and learn from setbacks with our visual tracking tools.
                </Typography>

                <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 600, mt: 3 }}>
                  4. Reflect on Your Journey
                </Typography>
                <Typography variant="body1" paragraph>
                  Access your past entries and see how you've grown. Our memory system highlights positive experiences when you need encouragement.
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Call to Action */}
      <Box 
        sx={{ 
          bgcolor: 'secondary.main', 
          color: 'white', 
          py: 8, 
          textAlign: 'center' 
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h3" component="h2" gutterBottom>
            Start Your Reflection Journey Today
          </Typography>
          <Typography variant="h6" component="p" sx={{ mb: 4, opacity: 0.9 }}>
            Join thousands of users who are discovering themselves through meaningful journaling.
          </Typography>
          <Button
            component={RouterLink}
            to={isAuthenticated ? "/journal" : "/register"}
            variant="contained"
            size="large"
            color="primary"
            sx={{ 
              px: 4, 
              py: 1.5,
              fontSize: '1.1rem'
            }}
          >
            {isAuthenticated ? "Go to Journal" : "Sign Up Now"}
          </Button>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;
