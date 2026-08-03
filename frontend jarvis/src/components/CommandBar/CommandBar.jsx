import React, { useState, useRef, useEffect } from 'react';
import { Plus, Mic, ArrowUp, Loader2 } from 'lucide-react';

const API_URL = 'http://localhost:8000';

const CommandBar = () => {
  const [isFocused, setIsFocused] = useState(false);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const handler = (e) => setIsListening(e.detail.isListening);
    window.addEventListener('toggle-mic', handler);
    return () => window.removeEventListener('toggle-mic', handler);
  }, []);

  const handleSubmit = async () => {
    const cmd = input.trim();
    if (!cmd || isLoading) return;
    setMessages(prev => [...prev, { role: 'user', content: cmd, timestamp: new Date().toISOString() }]);
    setInput('');
    setIsLoading(true);
    try {
      const res = await fetch(API_URL + '/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: cmd }),
      });
      if (!res.ok) throw new Error('Server error: ' + res.status);
      const data = await res.json();
      setMessages(prev => [...prev, {
        role: 'assistant', type: data.type || 'chat', content: data.message || 'No response',
        action: data.action, target: data.target, model_used: data.model_used,
        success: data.success, timestamp: data.timestamp,
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant', type: 'error',
        content: 'Connection error: ' + err.message + '. Make sure the API server is running.',
        success: false, timestamp: new Date().toISOString(),
      }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleMicToggle = () => {
    const newState = !isListening;
    setIsListening(newState);
    window.isMicActive = newState;
    window.dispatchEvent(new CustomEvent('toggle-mic', { detail: { isListening: newState } }));
  };

  return (
    <div className="w-full max-w-[900px] mx-auto flex flex-col gap-3">
      {messages.length > 0 && (
        <div className="max-h-[300px] overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent space-y-2 px-1">
          {messages.map((msg, idx) => {
            return (
              <div key={idx} className={"flex gap-2.5 text-sm " + (msg.role === 'user' ? "justify-end" : "")}>
                <div className={"max-w-[85%] rounded-2xl px-4 py-2.5 " + (msg.role === 'user' ? "bg-white/5 text-white/90 border border-white/5" : msg.type === 'error' ? "bg-red-500/10 border border-red-500/20 text-red-300" : "bg-[#0c0f18] border border-white/5 text-white/85")}>
                  <p className="leading-relaxed whitespace-pre-wrap break-words">{msg.content}</p>
                </div>
                );
          })}
                <div ref={messagesEndRef} />
              </div>
            )
          }

      <div className="relative w-full z-[60] mx-auto group">
              <div className="absolute z-[-1] overflow-hidden h-full w-full rounded-2xl blur-[3px] before:absolute before:content-[''] before:z-[-2] before:w-[2000px] before:h-[2000px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-60 before:bg-[conic-gradient(#000,#402fb5_5%,#000_38%,#000_50%,#cf30aa_60%,#000_87%)] before:transition-all before:duration-2000 group-hover:before:rotate-[-120deg] group-focus-within:before:rotate-[420deg] group-focus-within:before:duration-[4000ms]"></div>
              <div className="absolute z-[-1] overflow-hidden h-full w-full rounded-2xl blur-[3px] before:absolute before:content-[''] before:z-[-2] before:w-[2000px] before:h-[2000px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-[82deg] before:bg-[conic-gradient(rgba(0,0,0,0),#18116a,rgba(0,0,0,0)_10%,rgba(0,0,0,0)_50%,#6e1b60,rgba(0,0,0,0)_60%)] before:transition-all before:duration-2000 group-hover:before:rotate-[-98deg] group-focus-within:before:rotate-[442deg] group-focus-within:before:duration-[4000ms]"></div>
              <div className="absolute z-[-1] overflow-hidden h-full w-full rounded-2xl blur-[2px] before:absolute before:content-[''] before:z-[-2] before:w-[2000px] before:h-[2000px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-[83deg] before:bg-[conic-gradient(rgba(0,0,0,0)_0%,#a099d8,rgba(0,0,0,0)_8%,rgba(0,0,0,0)_50%,#dfa2da,rgba(0,0,0,0)_58%)] before:brightness-140 before:transition-all before:duration-2000 group-hover:before:rotate-[-97deg] group-focus-within:before:rotate-[443deg] group-focus-within:before:duration-[4000ms]"></div>
              <div className="absolute z-[-1] overflow-hidden h-full w-full rounded-2xl blur-[0.5px] before:absolute before:content-[''] before:z-[-2] before:w-[2000px] before:h-[2000px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-70 before:bg-[conic-gradient(#1c191c,#402fb5_5%,#1c191c_14%,#1c191c_50%,#cf30aa_60%,#1c191c_64%)] before:brightness-130 before:transition-all before:duration-2000 group-hover:before:rotate-[-110deg] group-focus-within:before:rotate-[430deg] group-focus-within:before:duration-[4000ms]"></div>

              <div className="relative bg-[#080b12]/95 backdrop-blur-2xl border border-white/5 rounded-2xl p-1.5 transition-all shadow-2xl overflow-hidden group/bar">
                <div className="flex flex-col">
                  <div className="flex items-center px-2 py-1 gap-1">
                    <button className="p-2.5 rounded-xl hover:bg-white/5 text-white/30 hover:text-white transition-all shrink-0">
                      <Plus size={18} strokeWidth={2.5} />
                    </button>

                    <input
                      ref={inputRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onFocus={() => setIsFocused(true)}
                      onBlur={() => setIsFocused(false)}
                      onKeyDown={handleKeyDown}
                      disabled={isLoading}
                      className="w-full bg-transparent border-none outline-none text-[15px] font-medium text-white placeholder:text-white/40 py-2.5 tracking-tight group-hover:placeholder:text-white/60 transition-colors disabled:opacity-50"
                      placeholder="Ask Jarvis anything, + to add files, / for commands"
                    />

                    <div className="flex items-center gap-1.5 shrink-0 ml-auto pr-1">
                      <button
                        onClick={handleMicToggle}
                        className={"p-2.5 rounded-xl transition-all " + (isListening ? "text-blue-400 bg-blue-500/10" : "text-white/20 hover:text-white")}
                      >
                        <Mic size={18} />
                      </button>
                      <div className="w-[1px] h-6 bg-white/5 mx-1" />
                      <button
                        onClick={handleSubmit}
                        disabled={isLoading || !input.trim()}
                        className={"relative overflow-hidden p-2.5 rounded-xl transition-all flex items-center justify-center " + (isFocused && input.trim() ? "text-white" : "bg-white/5 text-white/20") + " disabled:opacity-40 disabled:cursor-not-allowed"}
                      >
                        {isFocused && input.trim() && (
                          <>
                            <div className="absolute inset-[-10px] overflow-hidden rounded-lg before:absolute before:content-[''] before:w-[150px] before:h-[150px] before:bg-no-repeat before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-90 before:bg-[conic-gradient(rgba(0,0,0,0),#3d3a4f,rgba(0,0,0,0)_50%,rgba(0,0,0,0)_50%,#3d3a4f,rgba(0,0,0,0)_100%)] before:brightness-135 before:animate-spin-slow"></div>
                            <div className="absolute inset-[1px] bg-black rounded-xl"></div>
                          </>
                        )}
                        {isLoading ? <Loader2 size={18} strokeWidth={3} className="relative z-10 animate-spin" /> : <ArrowUp size={18} strokeWidth={3} className="relative z-10" />}
                      </button>
                    </div>
                  </div>
                </div>
                );
};

                export default CommandBar;
