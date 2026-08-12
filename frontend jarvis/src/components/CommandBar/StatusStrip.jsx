import React, { useState, useEffect } from 'react';
import { RotateCw, Power, CheckCircle2, AlertTriangle } from 'lucide-react';

const API_URL = 'http://localhost:8000';

const StatusStrip = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [serverStatus, setServerStatus] = useState('checking'); // 'online', 'offline', 'restarting'
  const [statusMsg, setStatusMsg] = useState('ONLINE');

  const checkHealth = async () => {
    try {
      const res = await fetch(API_URL + '/api/health', { signal: AbortSignal.timeout(2500) });
      if (res.ok) {
        setServerStatus('online');
        setStatusMsg('ONLINE');
      } else {
        setServerStatus('offline');
        setStatusMsg('OFFLINE');
      }
    } catch {
      setServerStatus('offline');
      setStatusMsg('OFFLINE');
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleRestartServer = async () => {
    if (isRefreshing) return;
    setIsRefreshing(true);
    setServerStatus('restarting');
    setStatusMsg('RESTARTING...');

    try {
      await fetch(API_URL + '/api/restart', { method: 'POST' });
      setTimeout(async () => {
        await checkHealth();
        setIsRefreshing(false);
      }, 1200);
    } catch (err) {
      console.error("Restart error:", err);
      setServerStatus('offline');
      setStatusMsg('ERROR');
      setIsRefreshing(false);
    }
  };

  return (
    <div className="w-full flex items-center justify-between px-6 pt-4 pb-2 select-none">
      {/* Left status indicators */}
      <div className="flex items-center space-x-4 opacity-80">
        <div className="flex items-center space-x-1.5">
          <div
            className={`w-2 h-2 rounded-full transition-all ${serverStatus === 'online'
                ? 'bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]'
                : serverStatus === 'restarting'
                  ? 'bg-amber-400 animate-ping'
                  : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]'
              }`}
          />
          <span
            className={`text-[10px] font-bold tracking-[0.1em] uppercase ${serverStatus === 'online'
                ? 'text-emerald-400'
                : serverStatus === 'restarting'
                  ? 'text-amber-400'
                  : 'text-red-400'
              }`}
          >
            {statusMsg}
          </span>
        </div>

        <span className="text-[10px] font-mono tracking-wide text-white/40">Engine: Python 3.11</span>
        <span className="text-[10px] font-mono tracking-wide text-white/40">Ollama: Active</span>
      </div>

      {/* Right Server Restart / Power Actions */}
      <div className="flex items-center space-x-2">
        <button
          onClick={handleRestartServer}
          disabled={isRefreshing}
          title="Restart JARVIS Backend Engine"
          className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 text-emerald-400 hover:text-emerald-300 transition-all text-[10px] font-semibold tracking-wider active:scale-95 disabled:opacity-50"
        >
          <RotateCw size={11} className={isRefreshing ? "animate-spin" : ""} />
          <span>{isRefreshing ? "RESETTING..." : "RESTART ENGINE"}</span>
        </button>
      </div>
    </div>
  );
};

export default StatusStrip;
