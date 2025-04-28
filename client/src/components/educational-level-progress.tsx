import { motion } from 'framer-motion';
import { ChevronUp, ArrowUp } from 'lucide-react';

export default function EducationalLevelProgress() {
  // Sample data to exactly match the reference image
  const duelsInProgress = 1;
  const completionPercentage = 67;
  
  // Define exact green color from iOS screenshot - updated to more vibrant green
  const greenColor = '#22C55E';

  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold text-black mb-2.5">Duels Progress</h2>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="bg-white rounded-xl p-4"
        style={{ 
          border: '1px solid rgba(0,0,0,0.03)',
          boxShadow: '0 2px 6px rgba(0,0,0,0.05)'
        }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="h-10 w-10 rounded-full flex items-center justify-center mr-3"
                style={{ backgroundColor: greenColor }}>
              <ChevronUp className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="text-sm text-slate-500 mb-0.5">
                {duelsInProgress} duel in progress
              </div>
              <div className="flex items-center">
                <div className="text-2xl font-bold text-black">{completionPercentage}% Win</div>
                <div className="ml-2 font-medium flex items-center text-sm" style={{ color: greenColor }}>
                  <ArrowUp className="h-3.5 w-3.5 mr-0.5" />
                  3h Loss
                </div>
              </div>
            </div>
          </div>

          <div className="w-20 h-20 relative">
            <svg className="w-full h-full" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="#E5E7EB"
                strokeWidth="8"
              />
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke={greenColor}
                strokeWidth="8"
                strokeDasharray={`${completionPercentage * 2.51} ${251 - completionPercentage * 2.51}`}
                strokeDashoffset="62.5"
                transform="rotate(-90 50 50)"
                strokeLinecap="round"
              />
              <text
                x="50"
                y="50"
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="20"
                fontWeight="bold"
                fill={greenColor}
              >
                {completionPercentage}%
              </text>
              <text
                x="50"
                y="70"
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="12"
                fontWeight="bold"
                fill={greenColor}
              >
                Win
              </text>
            </svg>
          </div>
        </div>
      </motion.div>
    </div>
  );
}