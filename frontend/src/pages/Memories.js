import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  InputAdornment,
  Snackbar,
  Alert,
  Tooltip,
  Menu,
  MenuItem,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import FilterListIcon from '@mui/icons-material/FilterList';
import SortIcon from '@mui/icons-material/Sort';
import { format } from 'date-fns';
import axios from '../utils/axiosConfig';
import { useAuth } from '../context/AuthContext';

const Memories = () => {
  const [memories, setMemories] = useState([]);
  const [filteredMemories, setFilteredMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingMemory, setEditingMemory] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    tags: ''
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });
  const [anchorElFilter, setAnchorElFilter] = useState(null);
  const [anchorElSort, setAnchorElSort] = useState(null);
  const [selectedTags, setSelectedTags] = useState([]);
  const [sortOption, setSortOption] = useState('newest');
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [activeMemoryId, setActiveMemoryId] = useState(null);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user } = useAuth();
  
  // Fetch memories on component mount
  useEffect(() => {
    fetchMemories();
  }, []);
  
  // Filter memories when search query or selected tags change
  useEffect(() => {
    filterMemories();
  }, [memories, searchQuery, selectedTags, sortOption]);
  
  const fetchMemories = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/memories');
      setMemories(response.data);
    } catch (err) {
      console.error('Error fetching memories:', err);
      setSnackbar({
        open: true,
        message: 'Failed to load memories. Please try again later.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const filterMemories = () => {
    let filtered = [...memories];
    
    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(memory => 
        memory.title.toLowerCase().includes(query) || 
        memory.content.toLowerCase().includes(query) ||
        memory.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }
    
    // Filter by selected tags
    if (selectedTags.length > 0) {
      filtered = filtered.filter(memory => 
        selectedTags.every(tag => memory.tags.includes(tag))
      );
    }
    
    // Sort memories
    switch (sortOption) {
      case 'newest':
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        break;
      case 'alphabetical':
        filtered.sort((a, b) => a.title.localeCompare(b.title));
        break;
      case 'favorite':
        filtered.sort((a, b) => (b.is_favorite ? 1 : 0) - (a.is_favorite ? 1 : 0));
        break;
      default:
        break;
    }
    
    setFilteredMemories(filtered);
  };
  
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };
  
  const handleOpenDialog = (memory = null) => {
    if (memory) {
      // Edit existing memory
      setEditingMemory(memory);
      setFormData({
        title: memory.title,
        content: memory.content,
        tags: memory.tags.join(', ')
      });
    } else {
      // Create new memory
      setEditingMemory(null);
      setFormData({
        title: '',
        content: '',
        tags: ''
      });
    }
    setOpenDialog(true);
  };
  
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingMemory(null);
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };
  
  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const tags = formData.tags
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
      
      const memoryData = {
        title: formData.title,
        content: formData.content,
        tags
      };
      
      if (editingMemory) {
        // Update existing memory
        await axios.put(`/api/memories/${editingMemory._id}`, memoryData);
        
        // Update local state
        setMemories(memories.map(memory => 
          memory._id === editingMemory._id 
            ? { ...memory, ...memoryData } 
            : memory
        ));
        
        setSnackbar({
          open: true,
          message: 'Memory updated successfully!',
          severity: 'success'
        });
      } else {
        // Create new memory
        const response = await axios.post('/api/memories', memoryData);
        
        // Update local state
        setMemories([...memories, response.data]);
        
        setSnackbar({
          open: true,
          message: 'Memory created successfully!',
          severity: 'success'
        });
      }
      
      handleCloseDialog();
    } catch (err) {
      console.error('Error saving memory:', err);
      setSnackbar({
        open: true,
        message: 'Failed to save memory. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleDeleteMemory = async (memoryId) => {
    if (!window.confirm('Are you sure you want to delete this memory?')) {
      return;
    }
    
    try {
      setLoading(true);
      await axios.delete(`/api/memories/${memoryId}`);
      
      // Update local state
      setMemories(memories.filter(memory => memory._id !== memoryId));
      
      setSnackbar({
        open: true,
        message: 'Memory deleted successfully!',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error deleting memory:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete memory. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleToggleFavorite = async (memory) => {
    try {
      const updatedMemory = { ...memory, is_favorite: !memory.is_favorite };
      
      await axios.put(`/api/memories/${memory._id}/favorite`, {
        is_favorite: updatedMemory.is_favorite
      });
      
      // Update local state
      setMemories(memories.map(m => 
        m._id === memory._id ? updatedMemory : m
      ));
      
      setSnackbar({
        open: true,
        message: updatedMemory.is_favorite 
          ? 'Added to favorites!' 
          : 'Removed from favorites!',
        severity: 'success'
      });
    } catch (err) {
      console.error('Error updating favorite status:', err);
      setSnackbar({
        open: true,
        message: 'Failed to update favorite status. Please try again.',
        severity: 'error'
      });
    }
  };
  
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };
  
  const handleOpenFilterMenu = (event) => {
    setAnchorElFilter(event.currentTarget);
  };
  
  const handleCloseFilterMenu = () => {
    setAnchorElFilter(null);
  };
  
  const handleOpenSortMenu = (event) => {
    setAnchorElSort(event.currentTarget);
  };
  
  const handleCloseSortMenu = () => {
    setAnchorElSort(null);
  };
  
  const handleTagSelect = (tag) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };
  
  const handleSortSelect = (option) => {
    setSortOption(option);
    handleCloseSortMenu();
  };
  
  const handleOpenMenu = (event, memoryId) => {
    setMenuAnchorEl(event.currentTarget);
    setActiveMemoryId(memoryId);
  };
  
  const handleCloseMenu = () => {
    setMenuAnchorEl(null);
    setActiveMemoryId(null);
  };
  
  // Get all unique tags from memories
  const getAllTags = () => {
    const tagSet = new Set();
    memories.forEach(memory => {
      memory.tags.forEach(tag => tagSet.add(tag));
    });
    return Array.from(tagSet);
  };
  
  const allTags = getAllTags();
  
  const formatDate = (dateString) => {
    return format(new Date(dateString), 'MMM d, yyyy');
  };
  
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
        <Typography variant="h4" component="h1" sx={{ mb: { xs: 2, sm: 0 } }}>
          Your Memories
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Memory
        </Button>
      </Box>
      
      {/* Search and Filter Bar */}
      <Paper 
        elevation={2} 
        sx={{ 
          p: 2, 
          mb: 4, 
          display: 'flex', 
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 2
        }}
      >
        <TextField
          placeholder="Search memories..."
          variant="outlined"
          size="small"
          fullWidth={isMobile}
          sx={{ flexGrow: 1, maxWidth: { sm: '50%' } }}
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            )
          }}
        />
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<FilterListIcon />}
            onClick={handleOpenFilterMenu}
            color={selectedTags.length > 0 ? "primary" : "inherit"}
          >
            {selectedTags.length > 0 ? `Filters (${selectedTags.length})` : "Filter"}
          </Button>
          
          <Button
            variant="outlined"
            size="small"
            startIcon={<SortIcon />}
            onClick={handleOpenSortMenu}
          >
            Sort
          </Button>
        </Box>
        
        {/* Filter Menu */}
        <Menu
          anchorEl={anchorElFilter}
          open={Boolean(anchorElFilter)}
          onClose={handleCloseFilterMenu}
          PaperProps={{
            style: {
              maxHeight: 300,
              width: 250
            }
          }}
        >
          <MenuItem disabled>
            <Typography variant="subtitle2">Filter by Tags</Typography>
          </MenuItem>
          <Divider />
          {allTags.length === 0 ? (
            <MenuItem disabled>
              <Typography variant="body2">No tags available</Typography>
            </MenuItem>
          ) : (
            allTags.map(tag => (
              <MenuItem 
                key={tag} 
                onClick={() => handleTagSelect(tag)}
                selected={selectedTags.includes(tag)}
              >
                {tag}
              </MenuItem>
            ))
          )}
          {selectedTags.length > 0 && (
            <>
              <Divider />
              <MenuItem onClick={() => setSelectedTags([])}>
                <Typography color="error">Clear Filters</Typography>
              </MenuItem>
            </>
          )}
        </Menu>
        
        {/* Sort Menu */}
        <Menu
          anchorEl={anchorElSort}
          open={Boolean(anchorElSort)}
          onClose={handleCloseSortMenu}
        >
          <MenuItem 
            onClick={() => handleSortSelect('newest')}
            selected={sortOption === 'newest'}
          >
            Newest First
          </MenuItem>
          <MenuItem 
            onClick={() => handleSortSelect('oldest')}
            selected={sortOption === 'oldest'}
          >
            Oldest First
          </MenuItem>
          <MenuItem 
            onClick={() => handleSortSelect('alphabetical')}
            selected={sortOption === 'alphabetical'}
          >
            Alphabetical
          </MenuItem>
          <MenuItem 
            onClick={() => handleSortSelect('favorite')}
            selected={sortOption === 'favorite'}
          >
            Favorites First
          </MenuItem>
        </Menu>
      </Paper>
      
      {/* Selected Filters */}
      {selectedTags.length > 0 && (
        <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {selectedTags.map(tag => (
            <Chip
              key={tag}
              label={tag}
              onDelete={() => handleTagSelect(tag)}
              color="primary"
              variant="outlined"
              size="small"
            />
          ))}
          <Chip
            label="Clear All"
            onClick={() => setSelectedTags([])}
            color="error"
            size="small"
          />
        </Box>
      )}
      
      {/* Memories Grid */}
      {loading && memories.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : filteredMemories.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          {memories.length === 0 ? (
            <>
              <Typography variant="h6" gutterBottom>
                You don't have any memories yet
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Start creating memories to preserve your important moments
              </Typography>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={() => handleOpenDialog()}
              >
                Create Your First Memory
              </Button>
            </>
          ) : (
            <>
              <Typography variant="h6" gutterBottom>
                No memories match your search
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Try adjusting your search terms or filters
              </Typography>
              <Button
                variant="outlined"
                onClick={() => {
                  setSearchQuery('');
                  setSelectedTags([]);
                }}
              >
                Clear Search & Filters
              </Button>
            </>
          )}
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredMemories.map(memory => (
            <Grid item xs={12} sm={6} md={4} key={memory._id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  position: 'relative',
                  transition: 'transform 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                  }
                }}
              >
                {memory.is_favorite && (
                  <Box 
                    sx={{ 
                      position: 'absolute', 
                      top: 8, 
                      right: 8, 
                      zIndex: 1,
                      bgcolor: 'error.main',
                      color: 'white',
                      borderRadius: '50%',
                      width: 32,
                      height: 32,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <FavoriteIcon fontSize="small" />
                  </Box>
                )}
                
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography variant="h6" component="h3" gutterBottom>
                      {memory.title}
                    </Typography>
                    <IconButton 
                      size="small" 
                      onClick={(e) => handleOpenMenu(e, memory._id)}
                      aria-label="memory options"
                    >
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {formatDate(memory.created_at)}
                  </Typography>
                  
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      mb: 2,
                      display: '-webkit-box',
                      WebkitLineClamp: 4,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    }}
                  >
                    {memory.content}
                  </Typography>
                  
                  {memory.tags.length > 0 && (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 'auto' }}>
                      {memory.tags.map(tag => (
                        <Chip 
                          key={tag} 
                          label={tag} 
                          size="small" 
                          onClick={() => {
                            if (!selectedTags.includes(tag)) {
                              setSelectedTags([...selectedTags, tag]);
                            }
                          }}
                          sx={{ cursor: 'pointer' }}
                        />
                      ))}
                    </Box>
                  )}
                </CardContent>
                
                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={memory.is_favorite ? <FavoriteIcon /> : <FavoriteBorderIcon />}
                    onClick={() => handleToggleFavorite(memory)}
                    color={memory.is_favorite ? "error" : "default"}
                  >
                    {memory.is_favorite ? "Favorited" : "Favorite"}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Memory Options Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleCloseMenu}
      >
        <MenuItem 
          onClick={() => {
            const memory = memories.find(m => m._id === activeMemoryId);
            handleOpenDialog(memory);
            handleCloseMenu();
          }}
        >
          <EditIcon fontSize="small" sx={{ mr: 1 }} />
          Edit
        </MenuItem>
        <MenuItem 
          onClick={() => {
            handleDeleteMemory(activeMemoryId);
            handleCloseMenu();
          }}
          sx={{ color: 'error.main' }}
        >
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Delete
        </MenuItem>
      </Menu>
      
      {/* Create/Edit Memory Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingMemory ? 'Edit Memory' : 'Create New Memory'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Memory Title"
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
            name="content"
            label="Memory Content"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.content}
            onChange={handleInputChange}
            multiline
            rows={6}
            sx={{ mb: 2 }}
          />
          
          <TextField
            margin="dense"
            name="tags"
            label="Tags (comma separated)"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.tags}
            onChange={handleInputChange}
            helperText="Example: personal, important, work"
            sx={{ mb: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={!formData.title.trim() || !formData.content.trim() || loading}
          >
            {loading ? <CircularProgress size={24} /> : editingMemory ? 'Update' : 'Create'}
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

export default Memories;
