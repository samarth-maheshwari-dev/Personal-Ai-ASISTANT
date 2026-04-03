import React from 'react';
import { motion } from 'framer-motion';
import { Terminal, Search, Brain, X, Info } from 'lucide-react';
import GlassPanel from '../ui/GlassPanel';

const SuggestionCard = ({ icon: Icon, title, description }) => {
  return (
    <motion.div
      whileHover={{ y: -4, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
      whileTap={{ scale: 0.98 }}
      className="group cursor-pointer"
    >
      <div className="glass-panel p-4 h-[110px] w-[200px] rounded-2xl flex flex-col justify-between transition-all duration-300 border border-white/5 hover:border-white/10">
        <div className="p-1.5 w-fit rounded-lg bg-white/5 text-jarvis-accent group-hover:bg-jarvis-accent group-hover:text-white transition-colors duration-300">
          <Icon size={14} />
        </div>
        <div>
          <h3 className="text-[12px] font-semibold text-white/90 truncate">
            {title}
          </h3>
          <p className="text-[10px] text-white/40 leading-tight line-clamp-2 mt-0.5">
            {description}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

const SuggestionCards = () => {
  return (
    <div className="mt-12 flex items-center justify-center space-x-4 z-10">
      <SuggestionCard 
        icon={Search} 
        title="Search Files" 
        description="Find files locally." 
      />
      <SuggestionCard 
        icon={Brain} 
        title="Remember" 
        description="Save to memory." 
      />
    </div>
  );
};

export default SuggestionCards;
