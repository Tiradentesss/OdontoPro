import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ThemeContext = createContext();
const THEME_STORAGE_KEY = '@odontopro:isDarkMode';

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const loadTheme = async () => {
      try {
        const storedTheme = await AsyncStorage.getItem(THEME_STORAGE_KEY);
        if (storedTheme !== null) {
          setIsDarkMode(storedTheme === 'true');
        }
      } catch (error) {
        console.warn('Could not load saved theme:', error);
      }
    };

    loadTheme();
  }, []);

  const toggleTheme = () => {
    setIsDarkMode((previousValue) => {
      const nextValue = !previousValue;
      AsyncStorage.setItem(THEME_STORAGE_KEY, String(nextValue)).catch((error) => {
        console.warn('Could not save theme:', error);
      });
      return nextValue;
    });
  };

  // Centraliza as paletas de cores de todo o ecossistema OdontoPro
  const theme = {
    isDarkMode,
    toggleTheme,
    colors: {
      container: isDarkMode ? '#0F172A' : '#F4F7FA',
      card: isDarkMode ? '#1E293B' : '#FFFFFF',
      text: isDarkMode ? '#F8FAFC' : '#0F1E36',
      border: isDarkMode ? '#334155' : '#E2E8F0',
      backButtonBg: isDarkMode ? '#334155' : '#EEF2F6',
      mutedText: '#64748B',
      brandBlue: isDarkMode ? '#38BDF8' : '#153A90', // Azul se adapta no dark para dar contraste
      filterActiveBg: isDarkMode ? '#38BDF8' : '#153A90',
      filterInactiveBg: isDarkMode ? '#1E293B' : '#F4F7FC',
    }
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};

// Hook personalizado para facilitar o uso nas telas
export const useTheme = () => useContext(ThemeContext);