import React from 'react';

const LoadingIndicator = () => {
  return (
    <div className="loading-indicator">
      <div className="loading-bubble">
        <div className="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};
export default LoadingIndicator;
