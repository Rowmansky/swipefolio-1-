import { motion } from 'framer-motion';
import { Percent, BarChart3, RotateCw, Zap } from 'lucide-react';

interface MissionItemProps {
  icon: React.ReactNode;
  title: string;
  xpValue: number;
  iconBg: string;
  iconColor: string;
  onClick?: () => void;
}

const MissionItem = ({ icon, title, xpValue, iconBg, iconColor, onClick }: MissionItemProps) => (
  <motion.div
    whileHover={{ y: -3, boxShadow: '0 6px 15px -3px rgba(0,0,0,0.1)' }}
    whileTap={{ scale: 0.97 }}
    onClick={onClick}
    className="bg-white rounded-xl p-3 shadow-sm border border-slate-100 flex flex-col justify-between cursor-pointer"
    style={{ boxShadow: '0 3px 10px -2px rgba(0,0,0,0.05)' }}
  >
    <div className="flex justify-between items-start mb-2">
      <div className="p-2 rounded-lg" style={{ backgroundColor: iconBg, color: iconColor }}>
        {icon}
      </div>
    </div>
    <div>
      <h3 className="text-slate-900 font-bold text-base mb-1 leading-tight">{title}</h3>
      <div className="flex justify-end">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-white text-xs font-medium"
          style={{ 
            backgroundColor: '#3B82F6',
            boxShadow: '0 2px 4px rgba(59, 130, 246, 0.3)'
          }}>
          + {xpValue} XP
        </span>
      </div>
    </div>
  </motion.div>
);

export default function DailyMissionsGrid() {
  // Sample mission data with enhanced colors to match design
  const missions = [
    {
      id: 1,
      title: 'Complete a Lesson',
      icon: <BarChart3 className="w-5 h-5" />,
      xpValue: 25,
      iconBg: '#E0E7FF',
      iconColor: '#4F46E5'
    },
    {
      id: 2,
      title: 'Make a Trade',
      icon: <Percent className="w-5 h-5" />,
      xpValue: 5,
      iconBg: '#DBEAFE',
      iconColor: '#3B82F6'
    },
    {
      id: 3,
      title: 'Review Your Moves',
      icon: <RotateCw className="w-5 h-5" />,
      xpValue: 10,
      iconBg: '#DBEAFE',
      iconColor: '#3B82F6'
    },
    {
      id: 4,
      title: '2-Day Streak',
      icon: <Zap className="w-5 h-5" />,
      xpValue: 25,
      iconBg: '#EDE9FE',
      iconColor: '#8B5CF6'
    }
  ];

  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold text-slate-900 mb-3">Daily Missions</h2>
      <div className="grid grid-cols-2 gap-2.5">
        {missions.map((mission) => (
          <MissionItem
            key={mission.id}
            icon={mission.icon}
            title={mission.title}
            xpValue={mission.xpValue}
            iconBg={mission.iconBg}
            iconColor={mission.iconColor}
            onClick={() => console.log(`Mission ${mission.id} clicked`)}
          />
        ))}
      </div>
    </div>
  );
}