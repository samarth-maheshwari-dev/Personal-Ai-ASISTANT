import React, { useState, useRef, useEffect } from 'react';
import { Plus, Mic, ArrowUp, Loader2, Terminal, User, Cpu } from 'lucide-react';

const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

const CommandBar = () => {
  const [isFocused, setIsFocused] = useState(false);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [logs, setLogs] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [showTerminal, setShowTerminal] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [chatStarted, setChatStarted] = useState(false);
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const logsEndRef = useRef(null);
  const wsRef = useRef(null);

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

  // ── WebSocket connection for live logs ──
  useEffect(() => {
    let reconnectTimer = null;
    let ws = null;

    const connect = () => {
      try {
        ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
          setLogs(prev => [...prev, { content: '[JARVIS] WebSocket connected.', ts: new Date().toISOString() }]);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'log' && data.content) {
              setLogs(prev => [...prev, { content: data.content, ts: data.timestamp || new Date().toISOString() }]);
            }
          } catch (e) {
            // ignore non-JSON
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          setLogs(prev => [...prev, { content: '[JARVIS] WebSocket disconnected. Reconnecting...', ts: new Date().toISOString() }]);
          if (!reconnectTimer) {
            reconnectTimer = setTimeout(() => {
              reconnectTimer = null;
              connect();
            }, 3000);
          }
        };

        ws.onerror = () => {
          ws.close();
        };
      } catch (e) {
        console.error('WS error', e);
      }
    };

    connect();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

  // Heartbeat ping to keep connection alive
  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, 25000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  useEffect(() => {
    const handler = (e) => setIsListening(e.detail.isListening);
    window.addEventListener('toggle-mic', handler);
    return () => window.removeEventListener('toggle-mic', handler);
  }, []);

  useEffect(() => {
    const handleKeyDownGlobally = (e) => {
      if (e.key === '`' && e.ctrlKey) {
        e.preventDefault();
        setShowTerminal(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDownGlobally);
    return () => window.removeEventListener('keydown', handleKeyDownGlobally);
  }, []);

  useEffect(() => {
    const handleSetThread = (e) => {
      const tid = e.detail?.id;
      setCurrentThreadId(tid);
      if (!tid) {
        setMessages([]);
        window.dispatchEvent(new CustomEvent('chat-cleared'));
      } else {
        const all = JSON.parse(localStorage.getItem('jarvis-threads') || '[]');
        const t = all.find(x => x.id === tid);
        if (t) {
          setMessages(t.messages || []);
          window.dispatchEvent(new CustomEvent('chat-started'));
        }
      }
    };
    window.addEventListener('set-thread', handleSetThread);
    return () => window.removeEventListener('set-thread', handleSetThread);
  }, []);

  const saveMessagesToThread = (id, msgs, title) => {
    const all = JSON.parse(localStorage.getItem('jarvis-threads') || '[]');
    const idx = all.findIndex(x => x.id === id);
    if (idx >= 0) {
      all[idx].messages = msgs;
    } else {
      all.unshift({ id, title: title || msgs[0]?.content || "New Chat", messages: msgs });
    }
    localStorage.setItem('jarvis-threads', JSON.stringify(all));
    window.dispatchEvent(new CustomEvent('threads-updated'));
  };

  const handleSubmit = async () => {
    if (isListening) {
      if (window.activeRecognition) window.activeRecognition.stop();
      if (window.micCleanup) window.micCleanup();
      setIsListening(false);
      window.dispatchEvent(new CustomEvent('toggle-mic', { detail: { isListening: false } }));
    }

    const cmd = input.trim();
    if (!cmd || isLoading) return;

    let tid = currentThreadId;
    if (!tid) {
      tid = Date.now().toString();
      setCurrentThreadId(tid);
      window.dispatchEvent(new CustomEvent('thread-created', { detail: { id: tid, title: cmd } }));
    }

    window.dispatchEvent(new CustomEvent('chat-started'));

    const newMsgs = [...messages, { role: 'user', content: cmd, timestamp: new Date().toISOString() }];
    setMessages(newMsgs);
    setInput('');
    setIsLoading(true);

    saveMessagesToThread(tid, newMsgs, cmd);

    try {
      const res = await fetch(API_URL + '/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: cmd }),
      });
      if (!res.ok) throw new Error('Server error: ' + res.status);
      const data = await res.json();

      let content = data.message || 'No response';

      if (data.action && data.message.trim().toLowerCase() === cmd.toLowerCase()) {
        content = typeof data.target === 'string' && data.target.trim().length > 0
          ? `Opening ${data.target} for you sir ✨`
          : `Executing command sir ✨`;
      }

      const finalMsgs = [...newMsgs, {
        role: 'assistant', type: data.type || 'chat', content,
        action: data.action, target: data.target, model_used: data.model_used,
        success: data.success, timestamp: data.timestamp,
      }];
      setMessages(finalMsgs);
      saveMessagesToThread(tid, finalMsgs);

      // -- TTS Speak --
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
        // Remove markdown asterisks and any emojis so TTS doesn't say "sparkles"
        const cleanContent = content
          .replace(/\*/g, '')
          .replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, '')
          .trim();
        const utterance = new SpeechSynthesisUtterance(cleanContent);
        // Slightly higher pitch and standard rate for a more pleasing tone
        utterance.pitch = 1.05;
        utterance.rate = 1;

        const voices = window.speechSynthesis.getVoices();
        // Priority for pleasing female voices across different platforms (Windows, macOS, Chrome)
        const preferred = voices.find(v =>
          /google (uk|us) english female/i.test(v.name) ||
          /samantha|zira|hazel|victoria|susan|karen|veena/i.test(v.name) ||
          /female|woman/i.test(v.name)
        ) || voices.find(v => v.lang.startsWith('en') && v.name.includes('Google')) || voices.find(v => v.lang.startsWith('en'));

        if (preferred) utterance.voice = preferred;
        window.speechSynthesis.speak(utterance);
      }
    } catch (err) {
      const errMsgs = [...newMsgs, {
        role: 'assistant', type: 'error',
        content: 'Connection error: ' + err.message + '. Make sure the API server is running.',
        success: false, timestamp: new Date().toISOString(),
      }];
      setMessages(errMsgs);
      saveMessagesToThread(tid, errMsgs);
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

  const handleMicToggle = async () => {
    const newState = !isListening;
    setIsListening(newState);

    if (newState) {
      window.dispatchEvent(new CustomEvent('chat-cleared')); // Show globe instantly!
      // 1. Setup speech recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onresult = (e) => {
          let finalTranscript = '';
          for (let i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) finalTranscript += e.results[i][0].transcript;
          }
          if (finalTranscript) {
            setInput(prev => (prev ? prev + ' ' : '') + finalTranscript);
          }
        };

        recognition.onend = () => {
          setIsListening(false);
          window.dispatchEvent(new CustomEvent('toggle-mic', { detail: { isListening: false } }));
          if (window.micCleanup) window.micCleanup();
        };

        window.activeRecognition = recognition;
        recognition.start();
      }

      // 2. Setup frequency analyzer
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const analyzer = audioCtx.createAnalyser();
        analyzer.fftSize = 256;
        const source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyzer);
        const dataArr = new Uint8Array(analyzer.frequencyBinCount);

        const updateFreq = () => {
          analyzer.getByteFrequencyData(dataArr);
          let sum = 0;
          for (let i = 0; i < dataArr.length; i++) sum += dataArr[i];
          const avg = sum / dataArr.length;
          // avg is typically 0 to 255
          window.dispatchEvent(new CustomEvent('mic-frequency', { detail: { volume: avg } }));
          window.micAnimFrame = requestAnimationFrame(updateFreq);
        };
        updateFreq();

        window.micCleanup = () => {
          if (window.micAnimFrame) cancelAnimationFrame(window.micAnimFrame);
          stream.getTracks().forEach(t => t.stop());
          if (audioCtx.state !== 'closed') audioCtx.close();
          window.dispatchEvent(new CustomEvent('mic-frequency', { detail: { volume: 0 } }));
        };
      } catch (err) {
        console.error("Mic access denied or err", err);
      }
    } else {
      if (window.activeRecognition) {
        window.activeRecognition.stop();
      }
      if (window.micCleanup) {
        window.micCleanup();
      }
    }

    window.isMicActive = newState;
    window.dispatchEvent(new CustomEvent('toggle-mic', { detail: { isListening: newState } }));
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const renderMessageContent = (content) => {
    if (typeof content !== 'string') return content;
    const parts = content.split(/(\*\*.*?\*\*|\*[^*]+\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*')) {
        return <em key={i} className="text-white/80 italic">{part.slice(1, -1)}</em>;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="w-full h-full flex flex-col gap-3 px-4 md:px-8 mx-auto max-w-4xl">
      {/* Live terminal logs (Dev Mode) */}
      {showTerminal && logs.length > 0 && (
        <div className="w-full rounded-2xl border border-emerald-500/20 bg-black/60 backdrop-blur-xl overflow-hidden animate-in slide-in-from-top-2 fade-in duration-200">
          <div className="flex items-center justify-between px-4 py-2 border-b border-emerald-500/10 bg-emerald-500/5">
            <div className="flex items-center gap-2">
              <Terminal size={13} className="text-emerald-400" />
              <span className="text-[10px] font-bold tracking-[0.15em] text-emerald-400/80 uppercase">Jarvis Developer Terminal</span>
              <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full ${isConnected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                {isConnected ? 'LIVE' : 'OFFLINE'}
              </span>
            </div>
            <button onClick={clearLogs} className="text-[10px] text-white/30 hover:text-white/70 transition-colors">
              Clear
            </button>
          </div>
          <div className="max-h-[220px] overflow-y-auto scrollbar-thin p-3 space-y-0.5 font-mono text-[12px] leading-relaxed">
            {logs.map((log, idx) => (
              <div key={idx} className="text-emerald-400/90 whitespace-pre-wrap break-words">
                {log.content}
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </div>
      )}

      {/* Chat messages container */}
      <div className={`flex-1 w-full flex flex-col overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent ${!chatStarted ? 'hidden' : ''}`}>
        {messages.length > 0 && (
          <div className="space-y-8 px-4 py-6 w-full flex flex-col mt-auto">
            {messages.map((msg, idx) => {
              if (msg.role === 'user') {
                return (
                  <div key={idx} className="flex justify-end w-full group mb-2">
                    <div className="max-w-[80%] md:max-w-[70%] px-5 py-3 rounded-2xl md:rounded-3xl bg-[#2f2f2f] text-white/95 text-[15px] leading-relaxed shadow-sm">
                      <p className="whitespace-pre-wrap break-words">{renderMessageContent(msg.content)}</p>
                    </div>
                  </div>
                );
              }
              return (
                <div key={idx} className="flex gap-4 w-full group justify-start mb-2">
                  <div className="shrink-0 flex items-center justify-center w-8 h-8 rounded-full border border-white/10 bg-[#0a0d17] shadow-sm">
                    <Cpu size={15} className={msg.type === 'error' ? "text-red-400" : "text-emerald-400"} />
                  </div>
                  <div className="flex-1 flex flex-col pt-1 w-full max-w-full overflow-hidden">
                    <h3 className="text-[13px] font-semibold text-white/80 mb-1">Jarvis</h3>
                    <div className={"w-full text-[15px] leading-relaxed " +
                      (msg.type === 'error'
                        ? "text-red-400"
                        : "text-white/90")}>
                      <p className="whitespace-pre-wrap break-words">{renderMessageContent(msg.content)}</p>
                    </div>
                  </div>
                </div>
              );
            })}
            {isLoading && (
              <div className="flex gap-4 w-full animate-pulse justify-start mb-2">
                <div className="shrink-0 flex items-center justify-center w-8 h-8 rounded-full border border-white/10 bg-[#0a0d17]">
                  <Cpu size={15} className="text-emerald-400/50" />
                </div>
                <div className="flex-1 flex flex-col pt-1.5">
                  <h3 className="text-[13px] font-semibold text-white/60 mb-1">Jarvis</h3>
                  <div className="flex items-center gap-1 mt-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} className="h-4" />
          </div>
        )}
      </div>

      <div className="relative w-full z-[60] mx-auto group shrink-0 mt-auto">
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
        </div>
      </div>
    </div>
  );
};

export default CommandBar;
