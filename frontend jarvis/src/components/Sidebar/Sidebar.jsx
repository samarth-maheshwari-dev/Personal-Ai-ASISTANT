import React, { useState, useEffect, useRef } from 'react';
import { 
  PlusCircle, 
  Zap, 
  Cpu, 
  MessageSquare, 
  Folder, 
  Inbox, 
  Database, 
  Wrench, 
  MoreHorizontal, 
  Settings, 
  Search, 
  Filter,
  CheckCircle2,
  Workflow,
  Mail,
  LayoutDashboard,
  Activity,
  Calendar,
  RotateCw,
  ChevronRight,
  ChevronLeft
} from 'lucide-react';
import NavItem from './NavItem';
import SidebarSection from './SidebarSection';
import ThreadItem from './ThreadItem';

const Sidebar = () => {
  const [width, setWidth] = useState(230);
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef(null);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      const newWidth = e.clientX - sidebarRef.current.getBoundingClientRect().left;
      if (newWidth >= 200 && newWidth <= 500) {
        setWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  return (
    <div 
      ref={sidebarRef}
      style={{ width: `${width}px` }}
      className="relative h-full flex flex-col border-r border-jarvis-border bg-[#0a0d17]/40 backdrop-blur-3xl shrink-0 group/sidebar"
    >
      {/* Resizer Handle */}
      <div 
        className="absolute top-0 right-0 w-1.5 h-full cursor-col-resize z-50 hover:bg-white/10 transition-colors"
        onMouseDown={(e) => {
          e.preventDefault();
          setIsResizing(true);
        }}
      >
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-8 bg-[#181a24] border border-white/10 rounded-full flex items-center justify-center opacity-0 group-hover/sidebar:opacity-100 transition-opacity">
          <ChevronRight size={10} className="text-white/40" />
        </div>
      </div>
      {/* Top Section */}
      <div className="p-4 flex items-center justify-between mb-2">
        <div className="flex space-x-1.5 opacity-40">
          <div className="w-1.5 h-1.5 rounded-full bg-white/20"></div>
          <div className="w-1.5 h-1.5 rounded-full bg-white/20"></div>
          <div className="w-1.5 h-1.5 rounded-full bg-white/20"></div>
        </div>
        <LayoutDashboard size={14} className="text-jarvis-muted/40 cursor-pointer hover:text-jarvis-text transition-colors" />
      </div>

      <div className="flex-1 overflow-y-auto px-1 group-scrollbar custom-scrollbar pb-10">
        {/* Main Actions */}
        <div className="px-1 space-y-0.5 mb-6">
          <NavItem icon={PlusCircle} label="New thread" isActive={false} />
          <NavItem icon={Zap} label="Automations" />
          <NavItem icon={Cpu} label="Skills" />
        </div>

        {/* Threads Section */}
        <SidebarSection 
          title="Threads" 
          actions={
            <div className="flex space-x-2">
              <Search size={12} className="text-jarvis-muted hover:text-jarvis-text cursor-pointer transition-colors" />
              <Filter size={12} className="text-jarvis-muted hover:text-jarvis-text cursor-pointer transition-colors" />
            </div>
          }
        >
          <div className="px-3 py-1 mb-1 first:mt-0 text-[10px] font-semibold text-jarvis-muted/40 tracking-wider">
            Today
          </div>
          <ThreadItem title="You have your ow..." time="31m" isActive={true} />
          <ThreadItem title="Dutch Guy Needs..." time="37m" />
          <ThreadItem title="What's Up with Yo..." time="10h" />
          <ThreadItem title="Weather in São Pa..." time="13h" />
          <ThreadItem title="Send Test Email to..." time="14h" />
          <div className="px-3 py-1 mt-4 mb-1 text-[10px] font-semibold text-jarvis-muted/40 tracking-wider">
            Yesterday
          </div>
          <ThreadItem title="Project Beta Recap" time="24h" />
          <ThreadItem title="Deployment Pipeline" time="26h" />
        </SidebarSection>

      </div>

      {/* Bottom Section */}
      <div className="mt-auto border-t border-jarvis-white/5 bg-[#0a0d17]/60 p-2">
        <NavItem icon={Settings} label="Settings" />
      </div>
    </div>
  );
};

export default Sidebar;
