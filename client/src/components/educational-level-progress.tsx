import { motion } from 'framer-motion';
import { GraduationCap, ArrowUp } from 'lucide-react';

export default function EducationalLevelProgress() {
  // Sample data for educational progress
  const levelInProgress = 1;
  const completionPercentage = 67;

  return (
    <div className="mb-6">
      <h2 className="text-xl font-semibold text-slate-800 mb-4">Level Progress</h2>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="bg-white rounded-xl p-4 shadow-sm border border-slate-200"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="h-10 w-10 rounded-full bg-green-500 flex items-center justify-center mr-3">
              <GraduationCap className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="text-sm text-slate-500">
                {levelInProgress} {levelInProgress === 1 ? 'level' : 'levels'} in progress
              </div>
              <div className="flex items-center">
                <div className="text-2xl font-bold text-slate-800">{completionPercentage}%</div>
                <div className="ml-2 text-green-500 font-medium flex items-center">
                  <ArrowUp className="h-4 w-4 mr-0.5" />
                  Complete
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
                stroke="#22C55E"
                strokeWidth="10"
                strokeDasharray={`${completionPercentage * 2.51} ${251 - completionPercentage * 2.51}`}
                strokeDashoffset="62.5"
                transform="rotate(-90 50 50)"
              />
              <text
                x="50"
                y="55"
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="18"
                fontWeight="bold"
                fill="#22C55E"
              >
                {completionPercentage}%
              </text>
            </svg>
          </div>
        </div>
      </motion.div>
    </div>
  );
}