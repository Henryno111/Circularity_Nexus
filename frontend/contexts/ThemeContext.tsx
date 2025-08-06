'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  mounted: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    try {
      const root = document.documentElement;
      const body = document.body;
      
      // Check for saved theme preference or system preference
      const savedTheme = localStorage.getItem('theme') as Theme;
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      const initialTheme = savedTheme || systemTheme;
      
      console.log('Initial theme:', initialTheme);
      setTheme(initialTheme);
      
      // Apply theme immediately
      root.classList.remove('light', 'dark');
      root.classList.add(initialTheme);
      body.classList.remove('light', 'dark');
      body.classList.add(initialTheme);
      
      console.log('Applied theme classes:', root.classList.toString());
      setMounted(true);
    } catch (error) {
      console.error('Error initializing theme:', error);
      setMounted(true);
    }
  }, []);

  useEffect(() => {
    if (!mounted) return;
    
    try {
      const root = document.documentElement;
      const body = document.body;
      
      console.log('Changing theme to:', theme);
      
      root.classList.remove('light', 'dark');
      root.classList.add(theme);
      body.classList.remove('light', 'dark');
      body.classList.add(theme);
      
      console.log('Updated theme classes:', root.classList.toString());
      localStorage.setItem('theme', theme);
    } catch (error) {
      console.error('Error updating theme:', error);
    }
  }, [theme, mounted]);

  const toggleTheme = () => {
    try {
      const newTheme = theme === 'light' ? 'dark' : 'light';
      console.log('Toggling theme from', theme, 'to', newTheme);
      setTheme(newTheme);
    } catch (error) {
      console.error('Error toggling theme:', error);
    }
  };

  const contextValue: ThemeContextType = {
    theme,
    toggleTheme,
    mounted
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}