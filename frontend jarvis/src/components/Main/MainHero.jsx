import { motion } from 'framer-motion';
import { AiLoader } from '../ui/ai-loader';

const MainHero = () => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="flex flex-col items-center text-center max-w-2xl px-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
      >
        <AiLoader size={200} text="Jarvis" />
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="mt-6"
      >
        <h1 className="text-4xl font-bold tracking-tight text-white mb-2">
          {getGreeting()}
        </h1>
        <p className="text-[15px] text-white/40 font-medium tracking-wide">
          I'm Jarvis. Ask me anything, or try one of these:
        </p>
      </motion.div>
    </div>
  );
};

export default MainHero;
