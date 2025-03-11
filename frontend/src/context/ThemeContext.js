import React, { createContext, useState, useContext, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles';

const ThemeContext = createContext();

export const useThemeContext = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
  const [mode, setMode] = useState(() => {
    const savedMode = localStorage.getItem('themeMode');
    return savedMode || 'light';
  });

  const toggleTheme = () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    setMode(newMode);
    localStorage.setItem('themeMode', newMode);
  };

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: {
            main: '#4dabf5',
            light: '#80d8ff',
            dark: '#0077c2',
            contrastText: '#fff',
          },
          secondary: {
            main: '#66bb6a',
            light: '#98ee99',
            dark: '#338a3e',
            contrastText: '#fff',
          },
          background: {
            default: mode === 'light' ? '#f5f5f5' : '#121212',
            paper: mode === 'light' ? '#fff' : '#1e1e1e',
          },
        },
        typography: {
          fontFamily: [
            'Roboto',
            '"Helvetica Neue"',
            'Arial',
            'sans-serif',
          ].join(','),
          h1: {
            fontSize: '2.5rem',
            fontWeight: 500,
          },
          h2: {
            fontSize: '2rem',
            fontWeight: 500,
          },
          h3: {
            fontSize: '1.75rem',
            fontWeight: 500,
          },
          h4: {
            fontSize: '1.5rem',
            fontWeight: 500,
          },
          h5: {
            fontSize: '1.25rem',
            fontWeight: 500,
          },
          h6: {
            fontSize: '1rem',
            fontWeight: 500,
          },
        },
        shape: {
          borderRadius: 8,
        },
        components: {
          MuiButton: {
            styleOverrides: {
              root: {
                textTransform: 'none',
                borderRadius: 8,
                padding: '8px 16px',
              },
            },
          },
          MuiCard: {
            styleOverrides: {
              root: {
                borderRadius: 12,
                boxShadow: mode === 'light' 
                  ? '0 4px 12px rgba(0,0,0,0.05)' 
                  : '0 4px 12px rgba(0,0,0,0.2)',
              },
            },
          },
          MuiTextField: {
            styleOverrides: {
              root: {
                marginBottom: 16,
              },
            },
          },
        },
      }),
    [mode],
  );

  const value = {
    mode,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={theme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
