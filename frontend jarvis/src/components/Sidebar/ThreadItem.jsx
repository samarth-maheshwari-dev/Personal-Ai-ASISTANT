import React from 'react';
import { Edit2, Trash2, Pin, PinOff } from 'lucide-react';

const ThreadItem = ({ title, time, isActive = false, isPinned = false, onClick, onDelete, onRename, onPin }) => {
  return (
    <div
      onClick={onClick}
      className={`
        relative group mx-2 px-3 py-2.5 rounded-lg cursor-pointer transition-all border-l-2
        ${isActive
          ? 'bg-white/10 border-white/20 text-white'
          : 'border-transparent text-white/50 hover:bg-white/5 hover:text-white/90'}
      `}
    >
      <div className="flex justify-between items-center w-full">
        <span className="text-[14px] font-medium truncate pr-6 tracking-tight">
          {title}
        </span>
      </div>

      {/* Actions (visible on hover) */}
      <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity bg-gradient-to-l from-[#0a0d17] via-[#0a0d17] to-transparent pl-6 py-1">
        <Edit2 size={13} className="text-white/40 hover:text-white/90 cursor-pointer" onClick={(e) => { e.stopPropagation(); onRename && onRename(); }} />
        <Trash2 size={13} className="text-white/40 hover:text-red-400 cursor-pointer" onClick={(e) => { e.stopPropagation(); onDelete && onDelete(); }} />
        {isPinned ? (
          <PinOff size={13} className="text-emerald-400 hover:text-emerald-500 cursor-pointer" onClick={(e) => { e.stopPropagation(); onPin && onPin(); }} />
        ) : (
          <Pin size={13} className="text-white/40 hover:text-emerald-400 cursor-pointer" onClick={(e) => { e.stopPropagation(); onPin && onPin(); }} />
        )}
      </div>
    </div>
  );
};

export default ThreadItem;
