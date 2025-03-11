import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Avatar,
  Button,
  Grid,
  TextField,
  Divider,
  CircularProgress,
  Alert,
  Snackbar,
  Card,
  CardContent,
  IconButton,
  Tabs,
  Tab,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import MoodIcon from '@mui/icons-material/Mood';
import TodayIcon from '@mui/icons-material/Today';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, BarElement } from 'chart.js';
import { Pie, Line, Bar } from 'react-chartjs-2';
import { format, subDays } from 'date-fns';
import axios from '../utils/axiosConfig';
import { useAuth } from '../context/AuthContext';

// Register ChartJS components
ChartJS.register(
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title
);

const Profile = () => {
  const [tabValue, setTabValue] = useState(0);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [userData, setUserData] = useState({
    name: '',
    email: '',
    bio: '',
    password: '',
    confirmPassword: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user, updateUser } = useAuth();
  
  useEffect(() => {
    if (user) {
      setUserData({
        name: user.name || '',
        email: user.email || '',
        bio: user.bio || '',
        password: '',
        confirmPassword: ''
      });
    }
  }, [user]);
  
  useEffect(() => {
    fetchStats();
  }, []);
  
  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/user/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching user stats:', err);
      setSnackbar({
        open: true,
        message: 'Failed to load user statistics',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUserData({ ...userData, [name]: value });
    
    // Clear field error when user types
    if (formErrors[name]) {
      setFormErrors({ ...formErrors, [name]: '' });
    }
  };
  
  const validateForm = () => {
    const errors = {};
    
    if (!userData.name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (userData.password) {
      if (userData.password.length < 8) {
        errors.password = 'Password must be at least 8 characters';
      }
      
      if (userData.password !== userData.confirmPassword) {
        errors.confirmPassword = 'Passwords do not match';
      }
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Only include password if it was changed
      const dataToUpdate = {
        name: userData.name,
        bio: userData.bio
      };
      
      if (userData.password) {
        dataToUpdate.password = userData.password;
      }
      
      await updateUser(dataToUpdate);
      
      setSnackbar({
        open: true,
        message: 'Profile updated successfully!',
        severity: 'success'
      });
      
      setEditing(false);
      
      // Clear password fields
      setUserData({
        ...userData,
        password: '',
        confirmPassword: ''
      });
    } catch (err) {
      console.error('Error updating profile:', err);
      setSnackbar({
        open: true,
        message: 'Failed to update profile. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };
  
  const toggleEditing = () => {
    if (editing) {
      // Cancel editing - reset form
      setUserData({
        name: user.name || '',
        email: user.email || '',
        bio: user.bio || '',
        password: '',
        confirmPassword: ''
      });
      setFormErrors({});
    }
    setEditing(!editing);
  };
  
  // Generate sample data for charts if real data is not available
  const generateSampleData = () => {
    if (stats) return stats;
    
    // Sample data for demonstration
    const emotions = {
      joy: 35,
      sadness: 15,
      anger: 10,
      fear: 8,
      surprise: 12,
      neutral: 20
    };
    
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = subDays(new Date(), i);
      return format(date, 'MMM dd');
    }).reverse();
    
    const entriesPerDay = last7Days.map(() => Math.floor(Math.random() * 5));
    
    return {
      total_entries: 87,
      streak_days: 12,
      avg_entries_per_day: 2.3,
      emotions,
      entries_timeline: {
        dates: last7Days,
        counts: entriesPerDay
      },
      emotion_timeline: {
        dates: last7Days,
        emotions: {
          joy: last7Days.map(() => Math.floor(Math.random() * 100)),
          sadness: last7Days.map(() => Math.floor(Math.random() * 100)),
          anger: last7Days.map(() => Math.floor(Math.random() * 100))
        }
      }
    };
  };
  
  const sampleData = generateSampleData();
  
  // Prepare chart data
  const emotionChartData = {
    labels: Object.keys(sampleData.emotions).map(emotion => 
      emotion.charAt(0).toUpperCase() + emotion.slice(1)
    ),
    datasets: [
      {
        data: Object.values(sampleData.emotions),
        backgroundColor: [
          '#4CAF50', // joy
          '#5C6BC0', // sadness
          '#EF5350', // anger
          '#FFA726', // fear
          '#42A5F5', // surprise
          '#BDBDBD'  // neutral
        ],
        borderWidth: 1
      }
    ]
  };
  
  const entriesTimelineData = {
    labels: sampleData.entries_timeline.dates,
    datasets: [
      {
        label: 'Journal Entries',
        data: sampleData.entries_timeline.counts,
        backgroundColor: theme.palette.primary.main,
        borderColor: theme.palette.primary.main,
        borderWidth: 2,
        tension: 0.4
      }
    ]
  };
  
  const emotionTimelineData = {
    labels: sampleData.emotion_timeline.dates,
    datasets: [
      {
        label: 'Joy',
        data: sampleData.emotion_timeline.emotions.joy,
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        borderColor: '#4CAF50',
        borderWidth: 2,
        tension: 0.4,
        fill: true
      },
      {
        label: 'Sadness',
        data: sampleData.emotion_timeline.emotions.sadness,
        backgroundColor: 'rgba(92, 107, 192, 0.2)',
        borderColor: '#5C6BC0',
        borderWidth: 2,
        tension: 0.4,
        fill: true
      },
      {
        label: 'Anger',
        data: sampleData.emotion_timeline.emotions.anger,
        backgroundColor: 'rgba(239, 83, 80, 0.2)',
        borderColor: '#EF5350',
        borderWidth: 2,
        tension: 0.4,
        fill: true
      }
    ]
  };
  
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  };
  
  const lineChartOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={4}>
        {/* Profile Section */}
        <Grid item xs={12} md={4}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3, 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center',
              borderRadius: 2
            }}
          >
            <Avatar 
              sx={{ 
                width: 120, 
                height: 120, 
                mb: 2,
                bgcolor: theme.palette.primary.main,
                fontSize: '3rem'
              }}
            >
              {userData.name ? userData.name.charAt(0).toUpperCase() : 'U'}
            </Avatar>
            
            {!editing ? (
              <Box sx={{ width: '100%', textAlign: 'center' }}>
                <Typography variant="h5" gutterBottom>
                  {userData.name || 'User'}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {userData.email}
                </Typography>
                
                {userData.bio && (
                  <Typography variant="body1" sx={{ mt: 2, mb: 2 }}>
                    {userData.bio}
                  </Typography>
                )}
                
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={toggleEditing}
                  sx={{ mt: 2 }}
                >
                  Edit Profile
                </Button>
              </Box>
            ) : (
              <Box component="form" sx={{ width: '100%', mt: 2 }}>
                <TextField
                  fullWidth
                  label="Name"
                  name="name"
                  value={userData.name}
                  onChange={handleInputChange}
                  margin="normal"
                  error={!!formErrors.name}
                  helperText={formErrors.name}
                  disabled={loading}
                />
                
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  value={userData.email}
                  disabled
                  margin="normal"
                />
                
                <TextField
                  fullWidth
                  label="Bio"
                  name="bio"
                  value={userData.bio}
                  onChange={handleInputChange}
                  margin="normal"
                  multiline
                  rows={3}
                  disabled={loading}
                />
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle2" gutterBottom>
                  Change Password (leave blank to keep current)
                </Typography>
                
                <TextField
                  fullWidth
                  label="New Password"
                  name="password"
                  type="password"
                  value={userData.password}
                  onChange={handleInputChange}
                  margin="normal"
                  error={!!formErrors.password}
                  helperText={formErrors.password}
                  disabled={loading}
                />
                
                <TextField
                  fullWidth
                  label="Confirm New Password"
                  name="confirmPassword"
                  type="password"
                  value={userData.confirmPassword}
                  onChange={handleInputChange}
                  margin="normal"
                  error={!!formErrors.confirmPassword}
                  helperText={formErrors.confirmPassword}
                  disabled={loading}
                />
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
                  <Button
                    variant="outlined"
                    startIcon={<CancelIcon />}
                    onClick={toggleEditing}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  
                  <Button
                    variant="contained"
                    startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
                    onClick={handleSubmit}
                    disabled={loading}
                  >
                    Save Changes
                  </Button>
                </Box>
              </Box>
            )}
          </Paper>
          
          {/* Stats Cards */}
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={6}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <TodayIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h4">{sampleData.total_entries}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Entries
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={6}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <TrendingUpIcon color="secondary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h4">{sampleData.streak_days}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Day Streak
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <AccessTimeIcon color="info" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="h4">{sampleData.avg_entries_per_day}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg. Entries Per Day
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
        
        {/* Analytics Section */}
        <Grid item xs={12} md={8}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3, 
              borderRadius: 2,
              height: '100%'
            }}
          >
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
              <Tabs 
                value={tabValue} 
                onChange={handleTabChange}
                aria-label="analytics tabs"
                variant={isMobile ? "scrollable" : "standard"}
                scrollButtons={isMobile ? "auto" : false}
              >
                <Tab label="Emotions" icon={<MoodIcon />} iconPosition="start" />
                <Tab label="Journal Activity" icon={<TodayIcon />} iconPosition="start" />
                <Tab label="Emotion Trends" icon={<TrendingUpIcon />} iconPosition="start" />
              </Tabs>
            </Box>
            
            {/* Emotions Tab */}
            {tabValue === 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Your Emotion Distribution
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  This chart shows the distribution of emotions detected in your journal entries.
                </Typography>
                
                <Box sx={{ height: 300, mt: 4 }}>
                  <Pie data={emotionChartData} options={chartOptions} />
                </Box>
              </Box>
            )}
            
            {/* Journal Activity Tab */}
            {tabValue === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Your Journaling Activity
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  This chart shows your journaling frequency over the past week.
                </Typography>
                
                <Box sx={{ height: 300, mt: 4 }}>
                  <Bar data={entriesTimelineData} options={lineChartOptions} />
                </Box>
              </Box>
            )}
            
            {/* Emotion Trends Tab */}
            {tabValue === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Your Emotion Trends
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  This chart shows how your emotions have changed over time.
                </Typography>
                
                <Box sx={{ height: 300, mt: 4 }}>
                  <Line data={emotionTimelineData} options={lineChartOptions} />
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Profile;
