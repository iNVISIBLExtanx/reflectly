import axios from 'axios';

// Configure axios to use our backend API running on port 5002
axios.defaults.baseURL = 'http://localhost:5002';

export default axios;
