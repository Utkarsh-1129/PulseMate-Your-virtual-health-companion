import React from 'react';
import ChatBox from './components/ChatBox';
import Header from './components/Header.jsx';
import Footer from './components/Footer';
import './styles/App.css';

function App() {
  return (
    
    <div className="app">
        <div>
        
        <main className="main-content">
          <ChatBox />
        </main>
      
      </div>
    </div>
  );
}

export default App;