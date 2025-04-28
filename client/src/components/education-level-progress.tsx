import { motion } from 'framer-motion';
import { ChevronUp } from 'lucide-react';
import React from 'react';

interface EducationLevelProgressProps {
  level: number;
  progress: number; // 0-100 percentage
  onClick: () => void;
}

export default function EducationLevelProgress({ level, progress, onClick }: EducationLevelProgressProps) {
  return (
    <motion.div
      className="mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <h2 className="text-xl font-bold text-slate-800 mb-3">Level Progress</h2>
      
      <div 
        className="bg-white rounded-2xl overflow-hidden shadow-sm cursor-pointer"
        onClick={onClick}
      >
        <div className="px-4 py-4 flex items-center">
          <div className="h-10 w-10 rounded-full bg-green-500 flex items-center justify-center mr-3">
            <ChevronUp className="h-6 w-6 text-white" />
          </div>
          
          <div className="flex-1">
            <div className="flex items-start flex-col">
              <div className="flex items-center">
                <h3 className="text-slate-800 font-bold text-lg">{progress}% Win</h3>
              </div>
              <p className="text-sm text-slate-500">3h Loss</p>
            </div>
          </div>
          
          <div className="flex-shrink-0 w-20 h-20">
            <div className="relative w-full h-full flex items-center justify-center">
              <svg className="w-full h-full" viewBox="0 0 100 100">
                <circle 
                  cx="50" 
                  cy="50" 
                  r="40" 
                  fill="none" 
                  stroke="#f1f5f9" 
                  strokeWidth="8"
                />
                <circle 
                  cx="50" 
                  cy="50" 
                  r="40" 
                  fill="none" 
                  stroke="#22c55e" 
                  strokeWidth="8"
                  strokeDasharray={`${2 * Math.PI * 40}`}
                  strokeDashoffset={`${2 * Math.PI * 40 * (1 - progress/100)}`}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                />
                <text 
                  x="50" 
                  y="50" 
                  textAnchor="middle" 
                  dominantBaseline="middle" 
                  fontSize="16" 
                  fontWeight="bold" 
                  fill="#22c55e"
                >
                  {progress}%
                </text>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}