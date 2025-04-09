import React from 'react';

const Message = ({ message = {} }) => {
  const { text = '', sender = '', timestamp = new Date() } = message;

  return (
    <div className={`message ${sender === 'user' ? 'user-message' : 'bot-message'}`}>
      <div className="message-content">
        <p>{text}</p>
        <span className="message-time">
          {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
};

export default Message;
