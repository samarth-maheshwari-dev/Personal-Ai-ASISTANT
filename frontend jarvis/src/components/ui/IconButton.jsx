import React from 'react';
import { motion } from 'framer-motion';

const IconButton = ({ icon: Icon, className = '', size = 18, onClick, ...props }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.1, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`p-2 rounded-xl text-jarvis-muted hover:text-jarvis-text transition-colors flex items-center justify-center ${className}`}
      {...props}
    >
      <Icon size={size} />
    </motion.button>
  );
};

export default IconButton;
