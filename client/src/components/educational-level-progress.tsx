import { motion } from 'framer-motion';
import { GraduationCap, ArrowUp, ChevronUp } from 'lucide-react';

export default function EducationalLevelProgress() {
  // Sample data for educational progress, exactly matching the reference image
  const levelInProgress = 1;
  const completionPercentage = 67;
  
  // Define sharper green color
  const greenColor = '#22C55E';

  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold text-slate-900 mb-3">Level Progress</h2>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="bg-white rounded-xl p-3.5 shadow-sm border border-slate-100"
        style={{ boxShadow: '0 4px 12px -2px rgba(0,0,0,0.05)' }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="h-10 w-10 rounded-full flex items-center justify-center mr-3"
                style={{ backgroundColor: greenColor }}>
              <ChevronUp className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="text-sm text-slate-500">
                {levelInProgress} {levelInProgress === 1 ? 'level' : 'levels'} in progress
              </div>
              <div className="flex items-center">
                <div className="text-2xl font-bold text-slate-900">{completionPercentage}% Win</div>
                <div className="ml-2 font-medium flex items-center" style={{ color: greenColor }}>
                  <ArrowUp className="h-4 w-4 mr-0.5" />
                  3h Loss
                </div>
              </div>
            </div>
          </div>

          <div className="w-16 h-16 relative">
            <svg className="w-full h-full" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="#E5E7EB"
                strokeWidth="10"
              />
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke={greenColor}
                strokeWidth="10"
                strokeDasharray={`${completionPercentage * 2.51} ${251 - completionPercentage * 2.51}`}
                strokeDashoffset="62.5"
                transform="rotate(-90 50 50)"
              />
              <text
                x="50"
                y="50"
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="16"
                fontWeight="bold"
                fill={greenColor}
              >
                {completionPercentage}%
              </text>
              <text
                x="50"
                y="66"
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="10"
                fontWeight="medium"
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