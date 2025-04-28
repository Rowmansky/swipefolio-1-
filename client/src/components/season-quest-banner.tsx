import { motion } from 'framer-motion';
import { Trophy } from 'lucide-react';

export default function SeasonQuestBanner() {
  // Sample data for season quest
  const questTitle = "Invest in Tech Titans stocks";
  const daysLeft = 13;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="rounded-2xl p-5 text-white flex items-center justify-between mb-5"
      style={{ 
        background: 'linear-gradient(to right, #7747FF, #7551FF)',
        boxShadow: '0 4px 12px rgba(119, 71, 255, 0.2)'
      }}
    >
      <div className="flex items-center">
        <div className="h-10 w-10 mr-4 flex items-center justify-center">
          <Trophy className="h-9 w-9 text-yellow-300" 
            style={{ color: '#FFC700' }} />
        </div>
        <div>
          <h2 className="text-2xl font-bold mb-0.5 tracking-tight">Season Quest</h2>
          <p className="text-white text-base font-medium">{questTitle}</p>
        </div>
      </div>
      <div className="bg-white/20 rounded-full px-4 py-1.5 backdrop-blur-sm">
        <span className="font-semibold text-sm">{daysLeft} days left</span>
      </div>
    </motion.div>
  );
}