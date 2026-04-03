import React from 'react';

const SidebarSection = ({ title, children, actions = null }) => {
  return (
    <div className="mb-4 mt-2">
      <div className="flex items-center justify-between px-4 mb-2">
        <h4 className="text-[10px] font-bold text-jarvis-muted uppercase tracking-[0.1em] opacity-60">
          {title}
        </h4>
        {actions}
      </div>
      <div className="space-y-0.5">
        {children}
      </div>
    </div>
  );
};

export default SidebarSection;
