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
      const token = localStorage.getItem('token');
      
      if (!token) {
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }
      
      // Check if token is expired
      const decodedToken = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      
      if (decodedToken.exp < currentTime) {
        // Token is expired
        localStorage.removeItem('token');
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }
      
      // Set auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Get user data
      const response = await axios.get('/api/auth/user');
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (err) {
      console.error('Auth check error:', err);
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
      const response = await axios.post('/api/auth/login', credentials);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await checkAuth();
      navigate('/journal');
      return true;
    } catch (err) {
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
