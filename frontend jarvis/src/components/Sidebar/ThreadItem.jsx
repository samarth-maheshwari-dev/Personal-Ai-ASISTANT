import React from 'react';

const ThreadItem = ({ title, time, isActive = false }) => {
  return (
    <div 
      className={`
        mx-2 px-3 py-1.5 rounded-lg cursor-pointer transition-all border-l-2
        ${isActive 
          ? 'bg-jarvis-active/40 border-jarvis-accent text-jarvis-text' 
          : 'border-transparent text-jarvis-muted hover:bg-white/5 hover:text-jarvis-text'}
      `}
    >
      <div className="flex justify-between items-center w-full">
        <span className="text-[12.5px] font-medium truncate pr-2 tracking-tight">
          {title}
        </span>
        <span className="text-[10px] text-jarvis-muted/50 font-normal shrink-0">
          {time}
        </span>
      </div>
      <div className="text-[10.5px] opacity-40 truncate leading-tight mt-0.5">
        Click to open this conversation
      </div>
    </div>
  );
};

export default ThreadItem;
