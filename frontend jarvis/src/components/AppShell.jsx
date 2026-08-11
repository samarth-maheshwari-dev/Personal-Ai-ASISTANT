import React, { useState, useEffect } from 'react';
import TitleBar from './TitleBar';
import Sidebar from './Sidebar/Sidebar';
import CommandBar from './CommandBar/CommandBar';
import MainHero from './Main/MainHero';
import StatusStrip from './CommandBar/StatusStrip';
import SuggestionCards from './Main/SuggestionCards';
import { DottedSurface } from './ui/dotted-surface';

const AppShell = () => {
  const [chatStarted, setChatStarted] = useState(false);

  useEffect(() => {
    const handleStart = () => setChatStarted(true);
    const handleClear = () => setChatStarted(false);
    window.addEventListener('chat-started', handleStart);
    window.addEventListener('chat-cleared', handleClear);
    return () => {
      window.removeEventListener('chat-started', handleStart);
      window.removeEventListener('chat-cleared', handleClear);
    };
  }, []);

  return (
    <div className="relative w-screen h-screen flex items-center justify-center bg-[#05070a] overflow-hidden mesh-bg noise">
      {/* Background gradients for depth */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#0a0d17]/90 via-[#0a0d17]/50 to-transparent pointer-events-none z-0" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-emerald-500/5 blur-[120px] rounded-full pointer-events-none z-0" />

      <DottedSurface />

      {/* App Window Container */}
      <div className="relative w-full h-full flex flex-col glass-panel overflow-hidden animate-in fade-in zoom-in duration-700 border-none z-10">
        <TitleBar />

        <div className="flex-1 flex overflow-hidden">
          <Sidebar />

          <main className="flex-1 flex flex-col relative px-4 text-left">
            {/* Top/Center Area */}
            <div className={`w-full flex-col items-center justify-center transition-all duration-700 flex ${chatStarted ? 'py-4 shrink-0' : 'flex-1 pt-16'}`}>
              <MainHero chatStarted={chatStarted} />
            </div>

            <div className="w-full flex-1 flex flex-col items-center justify-end overflow-hidden pb-4">
              <CommandBar />
            </div>

            <div className="w-full mt-auto">
              <StatusStrip />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default AppShell;
