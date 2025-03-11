import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Divider,
  CircularProgress,
  Chip,
  Avatar,
  Tooltip,
  Fade,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral';
import axios from '../utils/axiosConfig';
import { format } from 'date-fns';
import { useAuth } from '../context/AuthContext';

const Journal = () => {
  const [entries, setEntries] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [speechRecognition, setSpeechRecognition] = useState(null);
  const [error, setError] = useState(null);
  
  const messagesEndRef = useRef(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user } = useAuth();
  
  // Initialize speech recognition if available
  useEffect(() => {
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0])
          .map(result => result.transcript)
          .join('');
        
        setCurrentMessage(transcript);
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsRecording(false);
      };
      
      setSpeechRecognition(recognition);
    }
  }, []);
  
  // Fetch journal entries on component mount
  useEffect(() => {
    fetchEntries();
  }, []);
  
  // Scroll to bottom of messages when entries change
  useEffect(() => {
    scrollToBottom();
  }, [entries]);
  
  const fetchEntries = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get('/api/journal/entries');
      setEntries(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching journal entries:', err);
      setError('Failed to load journal entries. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!currentMessage.trim()) return;
    
    // Generate a temporary ID that we can reference later
    const tempId = `temp-${Date.now()}`;
    
    try {
      setIsLoading(true);
      
      // Optimistically add user message to UI
      const userEntry = {
        _id: tempId,
        content: currentMessage,
        user_email: user.email,
        created_at: new Date().toISOString(),
        isUserMessage: true
      };
      
      setEntries(prev => [...prev, userEntry]);
      setCurrentMessage('');
      
      // Send to API
      console.log('Sending journal entry to API:', userEntry.content);
      const response = await axios.post('/api/journal/entries', {
        content: userEntry.content
      });
      console.log('API response:', response.data);
      
      // Add AI response
      const aiResponse = {
        _id: response.data.entry_id,
        content: response.data.response,
        emotion: response.data.emotion,
        created_at: new Date().toISOString(),
        isUserMessage: false
      };
      
      // Replace temporary user message with actual entry and add AI response
      setEntries(prev => 
        prev.map(entry => 
          entry._id === tempId 
            ? { ...entry, _id: response.data.entry_id } 
            : entry
        ).concat(aiResponse)
      );
      
      setError(null);
    } catch (err) {
      console.error('Error creating journal entry:', err);
      setError('Failed to send your message. Please try again.');
      
      // Remove the optimistic entry using the stored tempId
      setEntries(prev => prev.filter(entry => entry._id !== tempId));
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleInputChange = (e) => {
    setCurrentMessage(e.target.value);
  };
  
  const toggleRecording = () => {
    if (!speechRecognition) return;
    
    if (isRecording) {
      speechRecognition.stop();
      setIsRecording(false);
    } else {
      speechRecognition.start();
      setIsRecording(true);
    }
  };
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const getEmotionIcon = (emotion) => {
    if (!emotion) return null;
    
    switch (emotion.primary_emotion) {
      case 'joy':
      case 'surprise':
        return <SentimentSatisfiedAltIcon color="success" />;
      case 'anger':
      case 'disgust':
      case 'fear':
      case 'sadness':
        return <SentimentDissatisfiedIcon color="error" />;
      default:
        return <SentimentNeutralIcon color="action" />;
    }
  };
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return format(date, 'MMM d, yyyy h:mm a');
  };
  
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper 
        elevation={3} 
        sx={{ 
          height: 'calc(100vh - 160px)', 
          display: 'flex', 
          flexDirection: 'column',
          borderRadius: 2,
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <Box 
          sx={{ 
            p: 2, 
            backgroundColor: theme.palette.primary.main, 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <Typography variant="h6">Journal</Typography>
          <Chip 
            icon={<CalendarTodayIcon />} 
            label={format(new Date(), 'EEEE, MMMM d')} 
            sx={{ 
              color: 'white', 
              '& .MuiChip-icon': { color: 'white' } 
            }} 
            variant="outlined" 
          />
        </Box>
        
        {/* Messages area */}
        <Box 
          sx={{ 
            flexGrow: 1, 
            p: 2, 
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          {isLoading && entries.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress />
            </Box>
          ) : entries.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', textAlign: 'center' }}>
              <Box>
                <Typography variant="h6" gutterBottom>Welcome to your journal!</Typography>
                <Typography variant="body1" color="text.secondary">
                  Start by typing a message below to begin your reflection journey.
                </Typography>
              </Box>
            </Box>
          ) : (
            <>
              {entries.map((entry, index) => (
                <Fade in={true} key={entry._id} timeout={500}>
                  <Box sx={{ mb: 2 }}>
                    {/* Date divider if it's a new day */}
                    {index === 0 || 
                      format(new Date(entry.created_at), 'yyyy-MM-dd') !== 
                      format(new Date(entries[index - 1].created_at), 'yyyy-MM-dd') ? (
                      <Box 
                        sx={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          my: 3
                        }}
                      >
                        <Divider sx={{ flexGrow: 1 }} />
                        <Chip 
                          label={format(new Date(entry.created_at), 'EEEE, MMMM d')} 
                          size="small" 
                          sx={{ mx: 2 }} 
                        />
                        <Divider sx={{ flexGrow: 1 }} />
                      </Box>
                    ) : null}
                    
                    {/* Message bubble */}
                    <Box 
                      sx={{ 
                        display: 'flex',
                        flexDirection: entry.isUserMessage ? 'row-reverse' : 'row',
                        alignItems: 'flex-start',
                        mb: 1
                      }}
                    >
                      <Avatar 
                        sx={{ 
                          bgcolor: entry.isUserMessage ? 'primary.main' : 'secondary.main',
                          width: 36,
                          height: 36,
                          mr: entry.isUserMessage ? 0 : 1,
                          ml: entry.isUserMessage ? 1 : 0
                        }}
                      >
                        {entry.isUserMessage ? user?.name?.charAt(0) || 'U' : 'R'}
                      </Avatar>
                      
                      <Box>
                        <Box 
                          className={`chat-bubble ${entry.isUserMessage ? 'user-bubble' : 'ai-bubble'}`}
                          sx={{
                            backgroundColor: entry.isUserMessage 
                              ? 'primary.light' 
                              : theme.palette.mode === 'dark' 
                                ? 'grey.800' 
                                : 'grey.100',
                            color: entry.isUserMessage 
                              ? 'white' 
                              : 'text.primary',
                          }}
                        >
                          <Typography variant="body1">{entry.content}</Typography>
                        </Box>
                        
                        <Box 
                          sx={{ 
                            display: 'flex', 
                            alignItems: 'center',
                            justifyContent: entry.isUserMessage ? 'flex-end' : 'flex-start',
                            mt: 0.5,
                            ml: entry.isUserMessage ? 0 : 1,
                            mr: entry.isUserMessage ? 1 : 0
                          }}
                        >
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                            {formatDate(entry.created_at)}
                          </Typography>
                          
                          {!entry.isUserMessage && entry.emotion && (
                            <Tooltip title={`Emotion: ${entry.emotion.primary_emotion}`}>
                              <Box component="span" sx={{ display: 'inline-flex', ml: 1 }}>
                                {getEmotionIcon(entry.emotion)}
                              </Box>
                            </Tooltip>
                          )}
                        </Box>
                      </Box>
                    </Box>
                  </Box>
                </Fade>
              ))}
              
              {/* Error message */}
              {error && (
                <Box 
                  sx={{ 
                    p: 2, 
                    backgroundColor: theme.palette.error.light,
                    color: theme.palette.error.contrastText,
                    borderRadius: 1,
                    mb: 2
                  }}
                >
                  <Typography variant="body2">{error}</Typography>
                </Box>
              )}
              
              {/* Scroll anchor */}
              <div ref={messagesEndRef} />
            </>
          )}
        </Box>
        
        {/* Input area */}
        <Box 
          component="form" 
          onSubmit={handleSubmit}
          sx={{ 
            p: 2, 
            borderTop: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.background.paper
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              fullWidth
              placeholder="Type your thoughts here..."
              variant="outlined"
              value={currentMessage}
              onChange={handleInputChange}
              disabled={isLoading}
              multiline
              maxRows={4}
              sx={{ mr: 1 }}
            />
            
            {speechRecognition && (
              <Tooltip title={isRecording ? "Stop recording" : "Start voice input"}>
                <IconButton 
                  color={isRecording ? "error" : "primary"} 
                  onClick={toggleRecording}
                  disabled={isLoading}
                >
                  {isRecording ? <MicOffIcon /> : <MicIcon />}
                </IconButton>
              </Tooltip>
            )}
            
            <Button
              variant="contained"
              color="primary"
              endIcon={<SendIcon />}
              type="submit"
              disabled={!currentMessage.trim() || isLoading}
              sx={{ ml: 1, height: 56, px: isMobile ? 2 : 3 }}
            >
              {isLoading ? <CircularProgress size={24} /> : isMobile ? null : "Send"}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Journal;
