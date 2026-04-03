import React from 'react';
import { Minus, Square, X } from 'lucide-react';

const TitleBar = () => {
  return (
    <div className="h-9 w-full flex items-center justify-between px-4 border-b border-jarvis-border bg-[#0a0d17]/80 backdrop-blur-md z-50 rounded-t-3xl">
      {/* macOS Controls */}
      <div className="flex items-center space-x-2 w-24">
        <div className="group w-3 h-3 rounded-full bg-[#ff5f57] flex items-center justify-center cursor-pointer overflow-hidden">
          <X size={8} className="opacity-0 group-hover:opacity-100 text-black/40" />
        </div>
        <div className="group w-3 h-3 rounded-full bg-[#febc2e] flex items-center justify-center cursor-pointer overflow-hidden">
          <Minus size={8} className="opacity-0 group-hover:opacity-100 text-black/40" />
        </div>
        <div className="group w-3 h-3 rounded-full bg-[#28c840] flex items-center justify-center cursor-pointer overflow-hidden">
          <Square size={6} className="opacity-0 group-hover:opacity-100 text-black/40" />
        </div>
      </div>

      {/* Title */}
      <div className="text-[13px] font-medium text-jarvis-muted/80 tracking-tight">
        Jarvis
      </div>

      {/* Right Status */}
      <div className="flex items-center space-x-3 w-24 justify-end">
        <div className="flex items-center space-x-1">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]"></div>
          <span className="text-[11px] text-jarvis-muted/60 font-medium tracking-wide">Online</span>
        </div>
      </div>
    </div>
  );
};

export default TitleBar;
