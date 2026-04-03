import React from 'react';
import { ShieldCheck, HardDrive, Mic } from 'lucide-react';

const StatusStrip = () => {
  return (
    <div className="w-full flex items-center justify-between px-6 pt-2 pb-4">
      <div className="flex items-center space-x-3">
        <button className="flex items-center space-x-2 bg-white/[0.03] hover:bg-white/[0.08] border border-white/5 hover:border-white/20 px-3 py-1.5 rounded-full transition-all duration-300 group cursor-pointer shadow-lg hover:shadow-[0_0_15px_rgba(255,255,255,0.05)]">
          <div className="relative flex items-center justify-center">
            <div className="absolute inset-0 bg-emerald-500/20 blur-md rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <HardDrive size={12} strokeWidth={2} className="text-emerald-500/70 group-hover:text-emerald-400 relative z-10 transition-colors" />
          </div>
          <span className="text-[10px] font-bold tracking-[0.1em] text-white/50 group-hover:text-white/90 uppercase transition-colors">Local</span>
        </button>

        <button className="flex items-center space-x-2 bg-[#402fb5]/10 hover:bg-[#402fb5]/20 border border-[#402fb5]/20 hover:border-[#402fb5]/40 px-3 py-1.5 rounded-full transition-all duration-300 group cursor-pointer shadow-lg hover:shadow-[0_0_15px_rgba(64,47,181,0.3)]">
          <div className="relative flex items-center justify-center">
            <div className="absolute inset-0 bg-[#402fb5]/40 blur-md rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <ShieldCheck size={12} strokeWidth={2} className="text-[#a099d8] group-hover:text-white relative z-10 transition-colors" />
          </div>
          <span className="text-[10px] font-bold tracking-[0.1em] text-[#a099d8]/70 group-hover:text-white/90 uppercase transition-colors">Full access</span>
        </button>
      </div>
      
      <div className="flex items-center space-x-1.5 text-white/40 grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all cursor-pointer group">
        <Mic size={11} strokeWidth={2.5} className="group-hover:text-red-500 transition-colors" />
        <span className="text-[10px] font-bold tracking-[0.1em] uppercase">Hey Jarvis</span>
      </div>
    </div>
  );
};

export default StatusStrip;
