import React from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const Message = ({ message = {} }) => {
  const { text = '', sender = '', timestamp = new Date() } = message;

  // Convert markdown to sanitized HTML
  const createMarkup = (markdownText) => {
    const rawHtml = marked(markdownText);
    const cleanHtml = DOMPurify.sanitize(rawHtml);
    return { __html: cleanHtml };
  };

  return (
    <div className={`message ${sender === 'user' ? 'user-message' : 'bot-message'}`}>
      <div className="message-content">
        <div dangerouslySetInnerHTML={createMarkup(text)} />
        <span className="message-time">
          {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
};

export default Message;
