import React from 'react';
import { ShieldCheck, HardDrive, Mic } from 'lucide-react';

const StatusStrip = () => {
  return (
    <div className="w-full flex items-center justify-between px-6 pt-4 pb-2">
      <div className="flex items-center space-x-4 opacity-70">
        <div className="flex items-center space-x-1.5">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
          <span className="text-[10px] font-bold tracking-[0.1em] text-emerald-400 uppercase">ONLINE</span>
        </div>

        <span className="text-[10px] font-mono tracking-wide text-white/50">Qwen2.5:3B</span>
        <span className="text-[10px] font-mono tracking-wide text-white/50">2.1 GB RAM</span>
        <span className="text-[10px] font-mono tracking-wide text-white/50">Memory: <span className="text-emerald-400/80">ON</span></span>
      </div>

      <div className="flex items-center space-x-1.5 text-white/30 hover:text-white/80 transition-all cursor-pointer group">
        <Mic size={11} strokeWidth={2.5} className="group-hover:text-red-500 transition-colors" />
        <span className="text-[10px] font-bold tracking-[0.1em] uppercase">MUTE</span>
      </div>
    </div>
  );
};

export default StatusStrip;
