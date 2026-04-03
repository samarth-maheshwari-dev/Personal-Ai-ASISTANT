import React from 'react';
import { motion } from 'framer-motion';

const OrbVisual = () => {
  return (
    <div className="relative w-28 h-28 flex items-center justify-center">
      {/* Outer Glow (CSS Orb Glow) */}
      <motion.div
        animate={{ 
          scale: [1, 1.05, 1],
          opacity: [0.6, 0.8, 0.6]
        }}
        transition={{ 
          duration: 4, 
          repeat: Infinity, 
          ease: "easeInOut" 
        }}
        className="absolute inset-0 rounded-full bg-jarvis-accent/40 blur-[40px]"
      />
      
      {/* Middle Atmosphere */}
      <motion.div
        animate={{ 
          rotate: 360,
          scale: [1, 1.02, 1]
        }}
        transition={{ 
          duration: 10, 
          repeat: Infinity, 
          ease: "linear"
        }}
        className="absolute inset-2 rounded-full border border-white/10 shadow-[inset_0_0_20px_rgba(255,255,255,0.1)] backdrop-blur-sm"
      />

      {/* Surface Details */}
      <div className="absolute inset-4 overflow-hidden rounded-full opacity-20 pointer-events-none">
        <div className="w-full h-full bg-[radial-gradient(circle_at_30%_30%,_white_0%,_transparent_60%)]" />
      </div>

      {/* Core Orb */}
      <motion.div
        animate={{ 
          y: [-4, 4, -4],
          scale: [1, 1.02, 1]
        }}
        transition={{ 
          duration: 6, 
          repeat: Infinity, 
          ease: "easeInOut" 
        }}
        className="relative w-16 h-16 rounded-full glass-panel flex items-center justify-center overflow-hidden border border-white/20 shadow-2xl"
      >
        {/* Internal Glows Layered */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_#6289ff_0%,_#3d6bfa_60%,_#080b14_100%)] opacity-80" />
        <div className="absolute inset-0 bg-[linear-gradient(135deg,_transparent_30%,_rgba(255,255,255,0.1)_50%,_transparent_70%)] animate-pulse" />
        
        {/* Core highlight */}
        <div className="w-2 h-2 rounded-full bg-white opacity-40 blur-[4px] absolute top-2 right-4 shadow-white shadow-lg" />
        
        {/* Atmospheric noise/particles simplified (CSS only) */}
        <div className="absolute inset-0 w-full h-full opacity-10 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] scale-150 rotate-45" />
      </motion.div>
    </div>
  );
};

export default OrbVisual;
