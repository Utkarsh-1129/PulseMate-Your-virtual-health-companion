import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import LoadingIndicator from './LoadingIndicator';
import Header from './Header';
import Footer from './Footer';
import { sendMessage } from '../services/api';
import '../styles/ChatBox.css';

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const [userId] = useState(() => {
    const savedId = localStorage.getItem('healthAssistantUserId');
    if (savedId) return savedId;

    const newId = `user_${Math.random().toString(36).substring(2, 9)}`;
    localStorage.setItem('healthAssistantUserId', newId);
    return newId;
  });

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          text: "👋 Hello! I'm your health assistant. I can help you understand symptoms, find healthcare facilities, and provide reliable health information. How can I assist you today?",
          sender: 'bot',
          timestamp: new Date()
        }
      ]);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      id: `msg_${Date.now()}`,
      text: input,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendMessage(input, userId);

      const botMessage = {
        id: `msg_${Date.now() + 1}`,
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage = {
        id: `msg_${Date.now() + 2}`,
        text: "⚠️ Sorry, I couldn't process that. Please try again later.",
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
    <Header />
    <div className="chat-messages">
      {messages.map((msg) => (
        <Message key={msg.id} message={msg} />
      ))}
      <div ref={messagesEndRef} />
    </div>
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        className="chat-input"
        placeholder="Type your message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button type="submit" className="send-button">Send</button>
      {loading && <LoadingIndicator />}
    </form>
    <Footer />
  </div>
  
  );
};

export default ChatBox;
