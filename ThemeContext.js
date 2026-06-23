import React, { createContext, useState, useContext } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleTheme = () => setIsDarkMode(prev => !prev);

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