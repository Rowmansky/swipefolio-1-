import { motion } from 'framer-motion';
import { Percent, BarChart3, RotateCw, Zap } from 'lucide-react';

interface MissionItemProps {
  icon: React.ReactNode;
  title: string;
  xpValue: number;
  onClick?: () => void;
}

const MissionItem = ({ icon, title, xpValue, onClick }: MissionItemProps) => (
  <motion.div
    whileHover={{ y: -3, backgroundColor: 'rgba(255, 255, 255, 0.8)' }}
    whileTap={{ scale: 0.97 }}
    onClick={onClick}
    className="bg-white rounded-xl p-4 shadow-sm border border-slate-100 flex flex-col justify-between cursor-pointer"
  >
    <div className="flex justify-between items-start mb-4">
      <div className="text-blue-500 p-2 bg-blue-100 rounded-lg">
        {icon}
      </div>
    </div>
    <div>
      <h3 className="text-slate-800 font-semibold mb-1">{title}</h3>
      <div className="flex justify-end">
        <span className="inline-flex items-center px-2 py-1 rounded-full bg-blue-500 text-white text-xs font-medium">
          + {xpValue} XP
        </span>
      </div>
    </div>
  </motion.div>
);

export default function DailyMissionsGrid() {
  // Sample mission data
  const missions = [
    {
      id: 1,
      title: 'Complete a Lesson',
      icon: <BarChart3 className="w-5 h-5" />,
      xpValue: 25
    },
    {
      id: 2,
      title: 'Make a Trade',
      icon: <Percent className="w-5 h-5" />,
      xpValue: 5
    },
    {
      id: 3,
      title: 'Review Your Progress',
      icon: <RotateCw className="w-5 h-5" />,
      xpValue: 10
    },
    {
      id: 4,
      title: '2-Day Streak',
      icon: <Zap className="w-5 h-5" style={{ color: '#8b5cf6' }} />,
      xpValue: 25
    }
  ];

  return (
    <div className="mb-6">
      <h2 className="text-xl font-semibold text-slate-800 mb-4">Daily Missions</h2>
      <div className="grid grid-cols-2 gap-3">
        {missions.map((mission) => (
          <MissionItem
            key={mission.id}
            icon={mission.icon}
            title={mission.title}
            xpValue={mission.xpValue}
            onClick={() => console.log(`Mission ${mission.id} clicked`)}
          />
        ))}
      </div>
    </div>
  );
}