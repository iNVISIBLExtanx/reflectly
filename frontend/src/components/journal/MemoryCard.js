import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  useTheme
} from '@mui/material';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import BookmarkIcon from '@mui/icons-material/Bookmark';

/**
 * Component for displaying a memory card in the journal chat
 */
const MemoryCard = ({ memoryData, memoryType }) => {
  const theme = useTheme();
  
  // Different styling based on memory type
  const getCardStyle = () => {
    if (memoryType === 'encouragement') {
      return {
        backgroundColor: theme.palette.mode === 'dark' 
          ? 'rgba(129, 199, 132, 0.15)' 
          : 'rgba(129, 199, 132, 0.1)',
        borderLeft: `4px solid ${theme.palette.success.main}`
      };
    } else if (memoryType === 'reinforcement') {
      return {
        backgroundColor: theme.palette.mode === 'dark' 
          ? 'rgba(144, 202, 249, 0.15)' 
          : 'rgba(144, 202, 249, 0.1)',
        borderLeft: `4px solid ${theme.palette.primary.main}`
      };
    }
    return {};
  };
  
  if (!memoryData) return null;
  
  return (
    <Card 
      variant="outlined" 
      sx={{
        my: 1,
        mx: 0,
        width: '100%',
        borderRadius: 2,
        ...getCardStyle()
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <BookmarkIcon 
            color={memoryType === 'encouragement' ? 'success' : 'primary'} 
            fontSize="small" 
            sx={{ mr: 1 }} 
          />
          <Typography variant="subtitle2" color="textSecondary">
            Memory from your journal
          </Typography>
        </Box>
        
        <Typography variant="body1" sx={{ mb: 2 }}>
          {memoryData.summary}
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <CalendarTodayIcon fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
            <Typography variant="caption" color="textSecondary">
              {memoryData.date}
            </Typography>
          </Box>
          
          <Chip
            icon={<SentimentSatisfiedAltIcon fontSize="small" />}
            label={memoryData.emotion}
            size="small"
            color={memoryType === 'encouragement' ? 'success' : 'primary'}
            variant="outlined"
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default MemoryCard;
