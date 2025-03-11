import React, { createContext, useState, useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../utils/axiosConfig';
import jwtDecode from 'jwt-decode';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();
  
  // Check if user is authenticated
  const checkAuth = useCallback(async () => {
    setLoading(true);
    try {
      console.log('checkAuth: Checking authentication status');
      const token = localStorage.getItem('token');
      console.log('checkAuth: Token exists:', !!token);
      
      if (!token) {
        console.log('checkAuth: No token found, user is not authenticated');
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }
      
      // Check if token is expired
      console.log('checkAuth: Decoding token');
      const decodedToken = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      console.log('checkAuth: Token expiration:', new Date(decodedToken.exp * 1000).toLocaleString());
      console.log('checkAuth: Current time:', new Date(currentTime * 1000).toLocaleString());
      
      if (decodedToken.exp < currentTime) {
        console.log('checkAuth: Token is expired');
        localStorage.removeItem('token');
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }
      
      // Set auth header
      console.log('checkAuth: Setting Authorization header');
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Get user data
      console.log('checkAuth: Fetching user data from API');
      const response = await axios.get('/api/auth/user');
      console.log('checkAuth: User data received:', response.data);
      setUser(response.data);
      setIsAuthenticated(true);
      console.log('checkAuth: User authenticated successfully');
    } catch (err) {
      console.error('checkAuth: Authentication error:', err);
      console.error('checkAuth: Error response:', err.response?.data);
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);
  
  // Register user
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/auth/register', userData);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await checkAuth();
      navigate('/journal');
      return true;
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  // Login user
  const login = async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Login attempt with credentials:', credentials);
      const response = await axios.post('/api/auth/login', credentials);
      console.log('Login API response:', response.data);
      const { access_token } = response.data;
      
      console.log('Storing token in localStorage');
      localStorage.setItem('token', access_token);
      console.log('Setting Authorization header');
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      console.log('Checking authentication status');
      await checkAuth();
      console.log('Authentication check completed, navigating to journal');
      navigate('/journal');
      return true;
    } catch (err) {
      console.error('Login error:', err);
      console.error('Error response:', err.response?.data);
      setError(err.response?.data?.message || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  // Logout user
  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setUser(null);
    navigate('/login');
  };
  
  // Clear error
  const clearError = () => {
    setError(null);
  };
  
  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    register,
    login,
    logout,
    checkAuth,
    clearError
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
