import { motion } from 'framer-motion';
import { AiLoader } from '../ui/ai-loader';

const MainHero = ({ chatStarted = false }) => {
  return (
    <div className="flex flex-col items-center text-center max-w-2xl px-6">
      <motion.div
        animate={{
          scale: chatStarted ? 0 : 1,
          opacity: chatStarted ? 0 : 1,
          height: chatStarted ? 0 : 'auto',
          marginBottom: chatStarted ? 0 : 16
        }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="origin-bottom relative z-10"
      >
        <AiLoader size={200} text="Jarvis" />
      </motion.div>

      <motion.div
        animate={{
          opacity: chatStarted ? 0 : 1,
          height: chatStarted ? 0 : 'auto',
          marginTop: chatStarted ? 0 : 24
        }}
        transition={{ duration: 0.5 }}
        className="overflow-hidden"
      >
        <h1 className="text-4xl font-bold tracking-tight text-white mb-2">
          Hey Samarth ✨
        </h1>
        <p className="text-[15px] text-white/40 font-medium tracking-wide">
          What are we building today?
        </p>
      </motion.div>
    </div>
  );
};

export default MainHero;
