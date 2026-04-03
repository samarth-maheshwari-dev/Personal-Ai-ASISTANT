import * as React from "react";

export const AiLoader = ({ size = 180, text = "Generating" }) => {
  const letters = text.split("");
  const [isListening, setIsListening] = React.useState(false);

  React.useEffect(() => {
    const handleToggleMic = (e) => setIsListening(e.detail.isListening);
    window.addEventListener('toggle-mic', handleToggleMic);
    return () => window.removeEventListener('toggle-mic', handleToggleMic);
  }, []);

  return (
    <div className="flex items-center justify-center">
      <div
        className="relative flex items-center justify-center font-inter select-none transition-all duration-700 ease-in-out"
        style={{ 
          width: size, 
          height: size,
          transform: isListening ? 'scale(1.15)' : 'scale(1)'
        }}
      >
        <div className="flex space-x-0.5">
          {letters.map((letter, index) => (
            <span
              key={index}
              className="inline-block text-white dark:text-gray-800 opacity-40 animate-loader-letter"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {letter}
            </span>
          ))}
        </div>

        <div
          className={`absolute inset-0 rounded-full animate-loader-circle transition-all duration-700 ${
            isListening 
              ? 'shadow-[0_0_80px_20px_rgba(59,130,246,0.6),inset_0_0_40px_10px_rgba(59,130,246,0.4)] border-blue-400/50' 
              : ''
          }`}
        ></div>
        
        {/* Extra ripple rings when listening */}
        {isListening && (
          <>
            <div className="absolute inset-0 rounded-full border border-blue-500/30 animate-ping opacity-50" style={{ animationDuration: '2s' }}></div>
            <div className="absolute inset-[-20px] rounded-full border border-blue-400/20 animate-ping opacity-30" style={{ animationDuration: '2.5s', animationDelay: '0.5s' }}></div>
          </>
        )}
      </div>
    </div>
  );
};
