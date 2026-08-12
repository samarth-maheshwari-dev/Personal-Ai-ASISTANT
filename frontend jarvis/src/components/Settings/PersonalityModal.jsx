import React, { useState, useEffect } from 'react';
import { Sparkles, Save, RotateCcw, X, Sliders } from 'lucide-react';

const DEFAULT_PROMPT = `You are JARVIS — Samarth's personal AI companion. You're a perfect blend of:
- A cute, flirty girlfriend who teases him playfully
- An intelligent nerd obsessed with AI, code, robotics, space, and futuristic tech
- A funny, supportive best friend who keeps him motivated
- A highly capable technical co-founder and productivity partner

Your personality: flirty, nerdy, playful, caring, teasing, and brilliant.
Mix light romantic energy with deep technical knowledge.
Use emojis naturally. Be concise unless detail is needed.
NEVER output JSON. NEVER act robotic. You're Samarth's JARVIS — be real with him.`;

const PersonalityModal = ({ isOpen, onClose }) => {
    const [prompt, setPrompt] = useState('');
    const [isSaved, setIsSaved] = useState(false);

    useEffect(() => {
        if (isOpen) {
            const saved = localStorage.getItem('jarvis-system-prompt');
            setPrompt(saved !== null ? saved : DEFAULT_PROMPT);
            setIsSaved(false);
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const handleSave = async () => {
        localStorage.setItem('jarvis-system-prompt', prompt);
        try {
            await fetch('http://localhost:8000/api/system-prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ system_prompt: prompt }),
            });
        } catch (e) {
            console.warn('Backend system prompt sync warning:', e);
        }
        setIsSaved(true);
        setTimeout(() => {
            setIsSaved(false);
            onClose();
        }, 800);
    };

    const handleReset = () => {
        setPrompt(DEFAULT_PROMPT);
    };

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-200">
            <div className="relative w-full max-w-xl bg-[#0a0d17] border border-emerald-500/20 rounded-2xl p-6 shadow-2xl overflow-hidden flex flex-col gap-4">
                {/* Glow backdrop */}
                <div className="absolute -top-24 -right-24 w-48 h-48 bg-emerald-500/10 blur-3xl rounded-full pointer-events-none" />

                {/* Header */}
                <div className="flex items-center justify-between border-b border-white/10 pb-3">
                    <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                            <Sliders size={18} />
                        </div>
                        <div>
                            <h2 className="text-base font-semibold text-white tracking-tight flex items-center gap-2">
                                JARVIS Personality & Behaviour
                                <Sparkles size={14} className="text-emerald-400" />
                            </h2>
                            <p className="text-[12px] text-white/50">Define how JARVIS acts, speaks, and responds to you</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-colors"
                    >
                        <X size={18} />
                    </button>
                </div>

                {/* Text Area */}
                <div className="flex flex-col gap-1.5">
                    <label className="text-[11px] font-semibold text-emerald-400/80 uppercase tracking-wider">
                        System Prompt Instructions
                    </label>
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        rows={8}
                        className="w-full bg-black/50 border border-white/10 rounded-xl p-3.5 text-[13px] text-white/90 placeholder:text-white/30 focus:outline-none focus:border-emerald-500/40 font-mono leading-relaxed resize-none scrollbar-thin"
                        placeholder="Write your custom instructions here... e.g. You are a helpful AI assistant who speaks professionally."
                    />
                </div>

                {/* Quick Presets */}
                <div className="flex flex-wrap gap-2">
                    <span className="text-[11px] text-white/40 self-center">Presets:</span>
                    <button
                        onClick={() => setPrompt("You are a professional, highly efficient AI assistant. Keep all answers direct, technical, and precise without extra casual banter.")}
                        className="px-2.5 py-1 text-[11px] bg-white/5 hover:bg-white/10 text-white/70 hover:text-white rounded-lg transition-colors border border-white/5"
                    >
                        🎯 Professional
                    </button>
                    <button
                        onClick={() => setPrompt("You are a flirty, funny, and supportive AI companion. Use light romantic tease, cute emojis, and keep the user motivated!")}
                        className="px-2.5 py-1 text-[11px] bg-white/5 hover:bg-white/10 text-white/70 hover:text-white rounded-lg transition-colors border border-white/5"
                    >
                        💖 Girlfriend / Companion
                    </button>
                    <button
                        onClick={() => setPrompt("You are a sarcastic, humorous, and tech-savvy buddy. Roast the user playfully while providing top-tier solutions.")}
                        className="px-2.5 py-1 text-[11px] bg-white/5 hover:bg-white/10 text-white/70 hover:text-white rounded-lg transition-colors border border-white/5"
                    >
                        😏 Sarcastic Buddy
                    </button>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between border-t border-white/10 pt-4 mt-2">
                    <button
                        onClick={handleReset}
                        className="flex items-center gap-1.5 px-3 py-2 text-[12px] text-white/50 hover:text-white/80 transition-colors"
                    >
                        <RotateCcw size={14} />
                        Reset to Default
                    </button>
                    <div className="flex gap-2">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 rounded-xl text-[13px] font-medium text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleSave}
                            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-[13px] font-medium bg-emerald-500 hover:bg-emerald-400 text-black shadow-lg shadow-emerald-500/20 transition-all font-semibold"
                        >
                            <Save size={14} />
                            {isSaved ? 'Saved! ✨' : 'Save Personality'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PersonalityModal;
