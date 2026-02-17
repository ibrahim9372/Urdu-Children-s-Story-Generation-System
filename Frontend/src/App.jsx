import React from 'react';
import StarField from './components/StarField';
import Header from './components/Header';
import ChatInterface from './components/ChatInterface';
import { ThemeProvider, useTheme } from './context/ThemeContext';

function AppContent() {
  const { isDark } = useTheme();
  return (
    <div
      className={`flex flex-col h-screen overflow-hidden transition-colors duration-500
        ${isDark ? 'bg-palace-night' : 'bg-[#FFFDF5]'}`}
    >
      <StarField />
      <Header />
      <div className="flex-1 flex flex-col relative z-10 overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
