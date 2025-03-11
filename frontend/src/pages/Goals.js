import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Paper,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  LinearProgress,
  Chip,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Divider,
  Alert,
  Snackbar,
  Tooltip,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import DateRangeIcon from '@mui/icons-material/DateRange';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { format, isAfter, differenceInDays } from 'date-fns';
import axios from '../utils/axiosConfig';

const Goals = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingGoal, setEditingGoal] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    target_date: null,
    progress: 0
  });
  const [progressDialogOpen, setProgressDialogOpen] = useState(false);
  const [currentGoalId, setCurrentGoalId] = useState(null);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  // Fetch goals on component mount
  useEffect(() => {
    fetchGoals();
  }, []);
  
  const fetchGoals = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/goals');
      setGoals(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching goals:', err);
      setError('Failed to load goals. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleOpenDialog = (goal = null) => {
    if (goal) {
      // Edit existing goal
      setEditingGoal(goal);
      setFormData({
        title: goal.title,
        description: goal.description || '',
        target_date: goal.target_date ? new Date(goal.target_date) : null,
        progress: goal.progress || 0
      });
    } else {
      // Create new goal
      setEditingGoal(null);
      setFormData({
        title: '',
        description: '',
        target_date: null,
        progress: 0
      });
    }
    setOpenDialog(true);
  };
  
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingGoal(null);
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  
  const handleDateChange = (date) => {
    setFormData({ ...formData, target_date: date });
  };
  
  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      if (editingGoal) {
        // Update existing goal
        await axios.put(`/api/goals/${editingGoal._id}`, formData);
        setSnackbar({
          open: true,
          message: 'Goal updated successfully!',
          severity: 'success'
        });
      } else {
        // Create new goal
        await axios.post('/api/goals', formData);
        setSnackbar({
          open: true,
          message: 'Goal created successfully!',
          severity: 'success'
        });
      }
      
      // Refresh goals
      fetchGoals();
      handleCloseDialog();
    } catch (err) {
      console.error('Error saving goal:', err);
      setSnackbar({
        open: true,
        message: 'Failed to save goal. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleDeleteGoal = async (goalId) => {
    if (!window.confirm('Are you sure you want to delete this goal?')) {
      return;
    }
    
    try {
      setLoading(true);
      await axios.delete(`/api/goals/${goalId}`);
      
      // Update local state
      setGoals(goals.filter(goal => goal._id !== goalId));
      
      setSnackbar({
        open: true,
        message: 'Goal deleted successfully!',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error deleting goal:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete goal. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleOpenProgressDialog = (goalId, currentProgress) => {
    setCurrentGoalId(goalId);
    setCurrentProgress(currentProgress);
    setProgressDialogOpen(true);
  };
  
  const handleCloseProgressDialog = () => {
    setProgressDialogOpen(false);
    setCurrentGoalId(null);
  };
  
  const handleProgressChange = (e) => {
    setCurrentProgress(Number(e.target.value));
  };
  
  const handleUpdateProgress = async () => {
    try {
      setLoading(true);
      await axios.put(`/api/goals/${currentGoalId}/progress`, {
        progress: currentProgress
      });
      
      // Update local state
      setGoals(goals.map(goal => 
        goal._id === currentGoalId 
          ? { ...goal, progress: currentProgress } 
          : goal
      ));
      
      setSnackbar({
        open: true,
        message: currentProgress >= 100 
          ? 'Congratulations! Goal completed!' 
          : 'Progress updated successfully!',
        severity: 'success'
      });
      
      handleCloseProgressDialog();
    } catch (err) {
      console.error('Error updating progress:', err);
      setSnackbar({
        open: true,
        message: 'Failed to update progress. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };
  
  const getGoalStatusColor = (goal) => {
    if (goal.progress >= 100) {
      return theme.palette.success.main;
    }
    
    if (goal.target_date) {
      const targetDate = new Date(goal.target_date);
      const today = new Date();
      
      if (isAfter(today, targetDate)) {
        return theme.palette.error.main; // Overdue
      }
      
      const daysRemaining = differenceInDays(targetDate, today);
      if (daysRemaining <= 7) {
        return theme.palette.warning.main; // Due soon
      }
    }
    
    return theme.palette.info.main; // In progress
  };
  
  const getGoalStatusText = (goal) => {
    if (goal.progress >= 100) {
      return 'Completed';
    }
    
    if (goal.target_date) {
      const targetDate = new Date(goal.target_date);
      const today = new Date();
      
      if (isAfter(today, targetDate)) {
        return 'Overdue';
      }
      
      const daysRemaining = differenceInDays(targetDate, today);
      if (daysRemaining <= 7) {
        return `Due soon (${daysRemaining} days)`;
      }
      
      return `${daysRemaining} days remaining`;
    }
    
    return 'In progress';
  };
  
  // Group goals by status
  const groupedGoals = {
    completed: goals.filter(goal => goal.progress >= 100),
    active: goals.filter(goal => goal.progress < 100)
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Your Goals
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Goal
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      {loading && goals.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : goals.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            You don't have any goals yet
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Set your first goal to start tracking your progress
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Create Your First Goal
          </Button>
        </Paper>
      ) : (
        <>
          {/* Active Goals */}
          <Typography variant="h5" component="h2" sx={{ mb: 2, mt: 4 }}>
            Active Goals
          </Typography>
          
          {groupedGoals.active.length === 0 ? (
            <Paper sx={{ p: 3, mb: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                You don't have any active goals. All your goals are completed!
              </Typography>
            </Paper>
          ) : (
            <Grid container spacing={3} sx={{ mb: 4 }}>
              {groupedGoals.active.map(goal => (
                <Grid item xs={12} sm={6} md={4} key={goal._id}>
                  <Card 
                    sx={{ 
                      height: '100%', 
                      display: 'flex', 
                      flexDirection: 'column',
                      position: 'relative',
                      overflow: 'visible'
                    }}
                  >
                    {/* Progress indicator */}
                    <Box 
                      sx={{ 
                        position: 'absolute', 
                        top: -8, 
                        left: 16, 
                        right: 16, 
                        zIndex: 1 
                      }}
                    >
                      <LinearProgress 
                        variant="determinate" 
                        value={goal.progress} 
                        sx={{ 
                          height: 8, 
                          borderRadius: 4,
                          backgroundColor: theme.palette.grey[300],
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getGoalStatusColor(goal)
                          }
                        }} 
                      />
                    </Box>
                    
                    <CardContent sx={{ pt: 3, flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="h6" component="h3" gutterBottom>
                          {goal.title}
                        </Typography>
                        <Chip 
                          label={`${goal.progress}%`} 
                          size="small" 
                          color={goal.progress >= 100 ? "success" : "primary"} 
                        />
                      </Box>
                      
                      {goal.description && (
                        <Typography variant="body2" color="text.secondary" paragraph>
                          {goal.description}
                        </Typography>
                      )}
                      
                      {goal.target_date && (
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <DateRangeIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            Due: {format(new Date(goal.target_date), 'MMM d, yyyy')}
                          </Typography>
                        </Box>
                      )}
                      
                      <Chip 
                        label={getGoalStatusText(goal)} 
                        size="small" 
                        sx={{ 
                          backgroundColor: getGoalStatusColor(goal),
                          color: '#fff',
                          mt: 1
                        }} 
                      />
                    </CardContent>
                    
                    <Divider />
                    
                    <CardActions>
                      <Button 
                        size="small" 
                        startIcon={<TrendingUpIcon />}
                        onClick={() => handleOpenProgressDialog(goal._id, goal.progress)}
                      >
                        Update Progress
                      </Button>
                      <Box sx={{ flexGrow: 1 }} />
                      <Tooltip title="Edit">
                        <IconButton 
                          size="small" 
                          onClick={() => handleOpenDialog(goal)}
                          aria-label="edit"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteGoal(goal._id)}
                          aria-label="delete"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
          
          {/* Completed Goals */}
          {groupedGoals.completed.length > 0 && (
            <>
              <Typography variant="h5" component="h2" sx={{ mb: 2, mt: 4, display: 'flex', alignItems: 'center' }}>
                <CheckCircleIcon sx={{ mr: 1, color: 'success.main' }} />
                Completed Goals
              </Typography>
              
              <Grid container spacing={3}>
                {groupedGoals.completed.map(goal => (
                  <Grid item xs={12} sm={6} md={4} key={goal._id}>
                    <Card 
                      sx={{ 
                        height: '100%', 
                        display: 'flex', 
                        flexDirection: 'column',
                        opacity: 0.8
                      }}
                    >
                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                          <Typography variant="h6" component="h3" gutterBottom>
                            {goal.title}
                          </Typography>
                          <Chip 
                            label="100%" 
                            size="small" 
                            color="success" 
                          />
                        </Box>
                        
                        {goal.description && (
                          <Typography variant="body2" color="text.secondary" paragraph>
                            {goal.description}
                          </Typography>
                        )}
                        
                        {goal.target_date && (
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <DateRangeIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                            <Typography variant="body2" color="text.secondary">
                              Completed: {format(new Date(goal.updated_at || goal.target_date), 'MMM d, yyyy')}
                            </Typography>
                          </Box>
                        )}
                      </CardContent>
                      
                      <Divider />
                      
                      <CardActions>
                        <Tooltip title="Delete">
                          <IconButton 
                            size="small" 
                            onClick={() => handleDeleteGoal(goal._id)}
                            aria-label="delete"
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </>
          )}
        </>
      )}
      
      {/* Create/Edit Goal Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingGoal ? 'Edit Goal' : 'Create New Goal'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Goal Title"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.title}
            onChange={handleInputChange}
            required
            sx={{ mb: 2, mt: 1 }}
          />
          
          <TextField
            margin="dense"
            name="description"
            label="Description (Optional)"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.description}
            onChange={handleInputChange}
            multiline
            rows={3}
            sx={{ mb: 2 }}
          />
          
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="Target Date (Optional)"
              value={formData.target_date}
              onChange={handleDateChange}
              renderInput={(params) => (
                <TextField 
                  {...params} 
                  fullWidth 
                  margin="dense"
                  sx={{ mb: 2 }}
                />
              )}
              minDate={new Date()}
            />
          </LocalizationProvider>
          
          {editingGoal && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Current Progress: {formData.progress}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={formData.progress} 
                sx={{ height: 10, borderRadius: 5 }} 
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={!formData.title.trim() || loading}
          >
            {loading ? <CircularProgress size={24} /> : editingGoal ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Update Progress Dialog */}
      <Dialog open={progressDialogOpen} onClose={handleCloseProgressDialog} maxWidth="xs" fullWidth>
        <DialogTitle>Update Progress</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>
              Current Progress: {currentProgress}%
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={currentProgress} 
              sx={{ 
                height: 10, 
                borderRadius: 5,
                mb: 3
              }} 
            />
            
            <TextField
              type="number"
              label="Progress Percentage"
              value={currentProgress}
              onChange={handleProgressChange}
              inputProps={{ min: 0, max: 100 }}
              fullWidth
              variant="outlined"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseProgressDialog}>Cancel</Button>
          <Button 
            onClick={handleUpdateProgress} 
            variant="contained" 
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
      
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

export default Goals;
