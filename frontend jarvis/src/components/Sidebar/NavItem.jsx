import React from 'react';
import { motion } from 'framer-motion';

const NavItem = ({ icon: Icon, label, isActive = false, activeStyle = 'pill' }) => {
  return (
    <motion.div
      whileHover={{ x: 2 }}
      className={`
        relative flex items-center px-3 py-1.5 mx-1 rounded-lg cursor-pointer transition-colors group
        ${isActive ? 'bg-jarvis-active text-jarvis-text shadow-sm' : 'text-jarvis-muted hover:text-jarvis-text hover:bg-white/5'}
      `}
    >
      {isActive && activeStyle === 'line' && (
        <motion.div 
          layoutId="active-nav-line"
          className="absolute left-0 w-1 h-4 bg-jarvis-accent rounded-full"
        />
      )}
      
      <Icon size={16} strokeWidth={isActive ? 2 : 1.5} className={`${isActive ? 'text-jarvis-accent' : 'text-current'} mr-3 transition-transform group-hover:scale-110`} />
      <span className="text-[13px] font-medium tracking-tight whitespace-nowrap">
        {label}
      </span>
    </motion.div>
  );
};

export default NavItem;
