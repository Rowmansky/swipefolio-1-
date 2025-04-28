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
      className="bg-gradient-to-r from-purple-600 to-purple-500 rounded-xl p-4 text-white flex items-center justify-between mb-6 shadow-md"
    >
      <div className="flex items-center">
        <Trophy className="h-8 w-8 mr-3 text-yellow-300" />
        <div>
          <h2 className="text-xl font-bold mb-0.5">Season Quest</h2>
          <p className="text-white/90">{questTitle}</p>
        </div>
      </div>
      <div className="bg-purple-400/30 rounded-full px-4 py-2 backdrop-blur-sm">
        <span className="font-semibold">{daysLeft} days left</span>
      </div>
    </motion.div>
  );
}