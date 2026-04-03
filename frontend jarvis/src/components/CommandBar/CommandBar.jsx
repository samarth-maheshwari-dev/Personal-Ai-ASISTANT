import React, { useState } from 'react';
import { Plus, Mic, ArrowUp } from 'lucide-react';

const CommandBar = () => {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="relative w-full max-w-[900px] z-[60] mx-auto group">
      {/* Animated Glowing Borders */}
      <div className="absolute z-[-1] overflow-hidden h-full w-full rounded-2xl blur-[3px] 
                      before:absolute before:content-[''] before:z-[-2] before:w-[2000px] before:h-[2000px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-60
                      before:bg-[conic-gradient(#000,#402fb5_5%,#000_38%,#000_50%,#cf30aa_60%,#000_87%)] before:transition-all before:duration-2000
                      group-hover:before:rotate-[-120deg] group-focus-within:before:rotate-[420deg] group-focus-within:before:duration-[4000ms]">
      </div>
      <div className="absolute z-[-1] overflow-hidden h-full w-full rounded-2xl blur-[3px] 
                      before:absolute before:content-[''] before:z-[-2] before:w-[2000px] before:h-[2000px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-[82deg]
                      before:bg-[conic-gradient(rgba(0,0,0,0),#18116a,rgba(0,0,0,0)_10%,rgba(0,0,0,0)_50%,#6e1b60,rgba(0,0,0,0)_60%)] before:transition-all before:duration-2000
                      group-hover:before:rotate-[-98deg] group-focus-within:before:rotate-[442deg] group-focus-within:before:duration-[4000ms]">
      </div>
      <div className="absolute z-[-1] overflow-hidden h-full w-full rounded-2xl blur-[2px] 
                      before:absolute before:content-[''] before:z-[-2] before:w-[2000px] before:h-[2000px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-[83deg]
                      before:bg-[conic-gradient(rgba(0,0,0,0)_0%,#a099d8,rgba(0,0,0,0)_8%,rgba(0,0,0,0)_50%,#dfa2da,rgba(0,0,0,0)_58%)] before:brightness-140
                      before:transition-all before:duration-2000 group-hover:before:rotate-[-97deg] group-focus-within:before:rotate-[443deg] group-focus-within:before:duration-[4000ms]">
      </div>
      <div className="absolute z-[-1] overflow-hidden h-full w-full rounded-2xl blur-[0.5px] 
                      before:absolute before:content-[''] before:z-[-2] before:w-[2000px] before:h-[2000px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-70
                      before:bg-[conic-gradient(#1c191c,#402fb5_5%,#1c191c_14%,#1c191c_50%,#cf30aa_60%,#1c191c_64%)] before:brightness-130
                      before:transition-all before:duration-2000 group-hover:before:rotate-[-110deg] group-focus-within:before:rotate-[430deg] group-focus-within:before:duration-[4000ms]">
      </div>

      <div className="relative bg-[#080b12]/95 backdrop-blur-2xl border border-white/5 rounded-2xl p-1.5 transition-all shadow-2xl overflow-hidden group/bar">
        <div className="flex flex-col">
          {/* Input Area */}
          <div className="flex items-center px-2 py-1 gap-1">
            <button className="p-2.5 rounded-xl hover:bg-white/5 text-white/30 hover:text-white transition-all shrink-0">
              <Plus size={18} strokeWidth={2.5} />
            </button>
            
            <input 
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              className="w-full bg-transparent border-none outline-none text-[15px] font-medium text-white placeholder:text-white/40 py-2.5 tracking-tight group-hover:placeholder:text-white/60 transition-colors"
              placeholder="Ask Jarvis anything, + to add files, / for commands"
            />

            <div className="flex items-center gap-1.5 shrink-0 ml-auto pr-1">
              <button 
                onClick={() => {
                  const newState = !window.isMicActive; // use global to toggle smoothly
                  window.isMicActive = newState;
                  window.dispatchEvent(new CustomEvent('toggle-mic', { detail: { isListening: newState }}));
                  // trigger small re-render purely for the button text-white class
                  setIsFocused((prev) => prev);
                }}
                className={`p-2.5 rounded-xl transition-all ${window.isMicActive ? 'text-blue-400 bg-blue-500/10' : 'text-white/20 hover:text-white'}`}
              >
                <Mic size={18} />
              </button>
              <div className="w-[1px] h-6 bg-white/5 mx-1" />
              <button 
                className={`
                  relative overflow-hidden p-2.5 rounded-xl transition-all flex items-center justify-center
                  ${isFocused ? 'text-white' : 'bg-white/5 text-white/20'}
                `}
              >
                {/* Animated Submit Button Background (Visible on Focus) */}
                {isFocused && (
                  <>
                    <div className="absolute inset-[-10px] overflow-hidden rounded-lg
                                  before:absolute before:content-[''] before:w-[150px] before:h-[150px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-90
                                  before:bg-[conic-gradient(rgba(0,0,0,0),#3d3a4f,rgba(0,0,0,0)_50%,rgba(0,0,0,0)_50%,#3d3a4f,rgba(0,0,0,0)_100%)]
                                  before:brightness-135 before:animate-spin-slow">
                    </div>
                    <div className="absolute inset-[1px] bg-black rounded-xl"></div>
                  </>
                )}
                <ArrowUp size={18} strokeWidth={3} className="relative z-10" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommandBar;
