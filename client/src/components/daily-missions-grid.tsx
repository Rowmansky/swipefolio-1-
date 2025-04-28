import { motion } from 'framer-motion';
import { Sword, Percent, List, Flame } from 'lucide-react';

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
    whileHover={{ y: -2 }}
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className="bg-white rounded-xl p-2.5 flex flex-col justify-between cursor-pointer"
    style={{ border: '1px solid rgba(0,0,0,0.03)' }}
  >
    <div className="flex justify-between items-start mb-2">
      <div className="p-1.5 rounded-lg" style={{ backgroundColor: iconBg, color: iconColor }}>
        {icon}
      </div>
    </div>
    <div>
      <h3 className="text-slate-900 font-bold text-[15px] mb-1 leading-tight">{title}</h3>
      <div className="flex justify-end">
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-white text-xs font-medium"
          style={{ 
            backgroundColor: '#3B82F6'
          }}>
          + {xpValue} XP
        </span>
      </div>
    </div>
  </motion.div>
);

export default function DailyMissionsGrid() {
  // Missions data with exact iOS match
  const missions = [
    {
      id: 1,
      title: 'Win a Duel',
      icon: <Sword className="w-5 h-5" />,
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
      icon: <List className="w-5 h-5" />,
      xpValue: 10,
      iconBg: '#DBEAFE',
      iconColor: '#3B82F6'
    },
    {
      id: 4,
      title: '2-Day Streak',
      icon: <Flame className="w-5 h-5" />,
      xpValue: 25,
      iconBg: '#EDE9FE',
      iconColor: '#8B5CF6'
    }
  ];

  return (
    <div className="mb-3">
      <h2 className="text-xl font-bold text-black mb-2.5">Daily Missions</h2>
      <div className="grid grid-cols-2 gap-2">
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