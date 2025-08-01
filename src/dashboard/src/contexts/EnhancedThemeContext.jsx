/**
 * Enhanced Theme Context with Dark Mode Support
 */
import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check localStorage and system preference
    const stored = localStorage.getItem('darkMode');
    if (stored !== null) {
      return JSON.parse(stored);
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const [accentColor, setAccentColor] = useState(() => {
    return localStorage.getItem('accentColor') || 'blue';
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  useEffect(() => {
    localStorage.setItem('accentColor', accentColor);
  }, [accentColor]);

  const theme = {
    isDarkMode,
    accentColor,
    toggleDarkMode: () => setIsDarkMode(prev => !prev),
    setAccentColor,
    colors: {
      primary: accentColor === 'blue' ? '#3B82F6' : 
               accentColor === 'green' ? '#10B981' :
               accentColor === 'purple' ? '#8B5CF6' :
               accentColor === 'orange' ? '#F59E0B' : '#3B82F6',
      background: isDarkMode ? '#0F172A' : '#F8FAFC',
      surface: isDarkMode ? '#1E293B' : '#FFFFFF',
      text: isDarkMode ? '#F1F5F9' : '#1E293B',
      textSecondary: isDarkMode ? '#94A3B8' : '#64748B',
      border: isDarkMode ? '#334155' : '#E2E8F0',
    }
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
