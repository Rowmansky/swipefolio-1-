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
      className="bg-gradient-to-r from-purple-600 to-purple-500 rounded-xl p-4 text-white flex items-center justify-between mb-5 shadow-md"
      style={{ 
        background: 'linear-gradient(to right, #8B5CF6, #7C3AED)',
        boxShadow: '0 4px 10px rgba(124, 58, 237, 0.2)'
      }}
    >
      <div className="flex items-center">
        <Trophy className="h-8 w-8 mr-3 text-yellow-300" 
          style={{ color: '#FCD34D' }} />
        <div>
          <h2 className="text-xl font-bold mb-0.5 tracking-tight">Season Quest</h2>
          <p className="text-white text-sm font-medium">{questTitle}</p>
        </div>
      </div>
      <div className="bg-purple-400/30 rounded-full px-4 py-1.5 backdrop-blur-sm"
        style={{ backgroundColor: 'rgba(139, 92, 246, 0.5)' }}>
        <span className="font-semibold text-sm">{daysLeft} days left</span>
      </div>
    </motion.div>
  );
}