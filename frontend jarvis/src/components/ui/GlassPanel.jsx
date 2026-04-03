import React from 'react';

const GlassPanel = ({ children, className = '', ...props }) => {
  return (
    <div 
      className={`bg-jarvis-panel border border-jarvis-border backdrop-blur-xl rounded-2xl ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default GlassPanel;
