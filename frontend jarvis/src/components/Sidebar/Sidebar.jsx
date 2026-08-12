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
  const [threads, setThreads] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [isOpenMobile, setIsOpenMobile] = useState(false);
  const sidebarRef = useRef(null);

  useEffect(() => {
    const handleToggleMobile = () => setIsOpenMobile(prev => !prev);
    window.addEventListener('toggle-mobile-sidebar', handleToggleMobile);
    return () => window.removeEventListener('toggle-mobile-sidebar', handleToggleMobile);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing || isOpenMobile) return;
      const newWidth = e.clientX - sidebarRef.current.getBoundingClientRect().left;
      if (newWidth >= 200 && newWidth <= 500) {
        setWidth(newWidth);
      }
    };

    const loadThreads = () => {
      const stored = JSON.parse(localStorage.getItem('jarvis-threads') || '[]');
      setThreads(stored);
    };

    loadThreads();

    const handleMouseUp = () => setIsResizing(false);
    const handleThreadsUpdated = () => loadThreads();
    const handleSetThread = (e) => {
      setActiveId(e.detail?.id || null);
      if (window.innerWidth < 768) setIsOpenMobile(false);
    };

    // When a message is sent in empty state, CommandBar creates a thread
    const handleThreadCreated = (e) => {
      setActiveId(e.detail.id);
      loadThreads();
    };

    window.addEventListener('threads-updated', handleThreadsUpdated);
    window.addEventListener('set-thread', handleSetThread);
    window.addEventListener('thread-created', handleThreadCreated);

    if (isResizing && !isOpenMobile) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('threads-updated', handleThreadsUpdated);
      window.removeEventListener('set-thread', handleSetThread);
      window.removeEventListener('thread-created', handleThreadCreated);
    };
  }, [isResizing, isOpenMobile]);

  const handleDelete = (id) => {
    const next = threads.filter(t => t.id !== id);
    localStorage.setItem('jarvis-threads', JSON.stringify(next));
    setThreads(next);
    if (activeId === id) {
      window.dispatchEvent(new CustomEvent('set-thread', { detail: { id: null } }));
    }
  };

  const handleRename = (id, currentTitle) => {
    const newTitle = window.prompt("Rename chat:", currentTitle);
    if (!newTitle || newTitle.trim() === '') return;
    const next = threads.map(t => t.id === id ? { ...t, title: newTitle.trim() } : t);
    localStorage.setItem('jarvis-threads', JSON.stringify(next));
    setThreads(next);
  };

  const handlePin = (id) => {
    const next = threads.map(t => t.id === id ? { ...t, isPinned: !t.isPinned } : t);
    localStorage.setItem('jarvis-threads', JSON.stringify(next));
    setThreads(next);
  };

  const handleSelect = (id) => {
    window.dispatchEvent(new CustomEvent('set-thread', { detail: { id } }));
  };

  const handleNewThread = () => {
    window.dispatchEvent(new CustomEvent('set-thread', { detail: { id: null } }));
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpenMobile && (
        <div
          className="md:hidden fixed inset-0 bg-black/60 z-[90] backdrop-blur-sm"
          onClick={() => setIsOpenMobile(false)}
        />
      )}

      <div
        ref={sidebarRef}
        style={{ width: isOpenMobile ? '280px' : `${width}px` }}
        className={`h-full flex flex-col border-r border-jarvis-border bg-[#0a0d17]/80 md:bg-[#0a0d17]/40 backdrop-blur-3xl shrink-0 group/sidebar
          ${isOpenMobile ? 'fixed inset-y-0 left-0 z-[100] transition-transform translate-x-0' : 'hidden md:relative md:flex'}`}
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
            <div onClick={handleNewThread}>
              <NavItem icon={PlusCircle} label="New thread" isActive={!activeId} />
            </div>
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
            <div className="px-3 py-1 mb-1 text-[10px] font-semibold text-emerald-500/80 tracking-wider">
              Threads
            </div>
            {threads.length === 0 && (
              <div className="px-3 py-2 text-[11px] text-white/30 italic">No previous chats</div>
            )}
            {threads.sort((a, b) => (b.isPinned ? 1 : 0) - (a.isPinned ? 1 : 0)).map(t => (
              <ThreadItem
                key={t.id}
                title={t.title}
                time={t.time || "recent"}
                isActive={activeId === t.id}
                isPinned={t.isPinned}
                onClick={() => handleSelect(t.id)}
                onDelete={() => handleDelete(t.id)}
                onRename={() => handleRename(t.id, t.title)}
                onPin={() => handlePin(t.id)}
              />
            ))}
          </SidebarSection>

        </div>

        {/* Bottom Section */}
        <div className="mt-auto border-t border-jarvis-white/5 bg-[#0a0d17]/60 p-2">
          <div onClick={() => window.dispatchEvent(new CustomEvent('open-personality'))}>
            <NavItem icon={Settings} label="Personality & Prompt" />
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
