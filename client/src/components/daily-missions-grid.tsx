import { motion } from 'framer-motion';
import { 
  FileCheck, 
  PercentCircle, 
  Flame, 
  Zap,
  Swords
} from 'lucide-react';
import React from 'react';

// Single mission card component
interface MissionCardProps {
  icon: React.ReactNode;
  title: string;
  xpReward: number;
  onClick: () => void;
}

const MissionCard = ({ icon, title, xpReward, onClick }: MissionCardProps) => {
  return (
    <motion.div
      className="bg-white rounded-2xl shadow-sm p-4 flex flex-col justify-between h-full"
      whileHover={{ y: -2, boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.05)' }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      <div className="flex flex-col h-full">
        <div className="mb-2">
          <div className="bg-blue-100 w-12 h-12 rounded-xl flex items-center justify-center">
            {icon}
          </div>
        </div>
        
        <h3 className="text-lg font-semibold text-slate-800 mb-auto">{title}</h3>
        
        <div className="self-end mt-2">
          <div className="flex items-center bg-blue-500 text-white text-xs font-medium rounded-full px-3 py-1.5">
            <span>+ {xpReward} XP</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

interface DailyMissionsGridProps {
  onMissionClick: (missionId: string) => void;
}

export default function DailyMissionsGrid({ onMissionClick }: DailyMissionsGridProps) {
  // Missions data
  const missions = [
    {
      id: 'win-duel',
      title: 'Win a Duel',
      icon: <Swords className="h-6 w-6 text-blue-600" />,
      xpReward: 25
    },
    {
      id: 'make-trade',
      title: 'Make a Trade',
      icon: <PercentCircle className="h-6 w-6 text-blue-600" />,
      xpReward: 5
    },
    {
      id: 'review-moves',
      title: 'Review Your Moves',
      icon: <FileCheck className="h-6 w-6 text-blue-600" />,
      xpReward: 10
    },
    {
      id: 'maintain-streak',
      title: '2-Day Streak',
      icon: <Flame className="h-6 w-6 text-purple-600" />,
      xpReward: 25
    }
  ];

  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold text-slate-800 mb-3">Daily Missions</h2>
      <div className="grid grid-cols-2 gap-3">
        {missions.map(mission => (
          <MissionCard
            key={mission.id}
            icon={mission.icon}
            title={mission.title}
            xpReward={mission.xpReward}
            onClick={() => onMissionClick(mission.id)}
          />
        ))}
      </div>
    </div>
  );
}