import React from 'react';
import TitleBar from './TitleBar';
import Sidebar from './Sidebar/Sidebar';
import CommandBar from './CommandBar/CommandBar';
import MainHero from './Main/MainHero';
import StatusStrip from './CommandBar/StatusStrip';
import SuggestionCards from './Main/SuggestionCards';

import { DottedSurface } from './ui/dotted-surface';

const AppShell = () => {
  return (
    <div className="relative w-screen h-screen flex items-center justify-center bg-[#05070a] overflow-hidden mesh-bg noise">
      <DottedSurface />
      
      {/* App Window Container */}
      <div className="relative w-full h-full flex flex-col glass-panel overflow-hidden animate-in fade-in zoom-in duration-700 border-none">
        <TitleBar />
        
        <div className="flex-1 flex overflow-hidden">
          <Sidebar />
          
          <main className="flex-1 flex flex-col relative px-4 text-center">
            <div className="flex-1 flex flex-col items-center justify-center overflow-y-auto scrollbar-hide pt-16">
              <MainHero />
              <SuggestionCards />
            </div>
            
            <div className="mt-auto w-full pt-8 pb-6 flex flex-col items-center">
              <CommandBar />
              <StatusStrip />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default AppShell;
