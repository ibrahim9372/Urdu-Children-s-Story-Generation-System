
import React from 'react';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="flex h-screen bg-[#000000]">
      <div className="flex-1 flex flex-col h-full relative">
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;
