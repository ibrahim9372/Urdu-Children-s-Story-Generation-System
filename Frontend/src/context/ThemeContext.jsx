import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const ThemeContext = createContext(null);

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
};

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    try {
      return localStorage.getItem('chandni-theme') !== 'light';
    } catch {
      return true;
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle('light', !isDark);
    root.classList.toggle('dark', isDark);
    try {
      localStorage.setItem('chandni-theme', isDark ? 'dark' : 'light');
    } catch {
      /* noop */
    }
  }, [isDark]);

  const toggleTheme = useCallback(() => setIsDark((prev) => !prev), []);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
