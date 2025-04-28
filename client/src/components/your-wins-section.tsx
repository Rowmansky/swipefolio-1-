import { motion } from 'framer-motion';
import { Trophy, TrendingUp, Sparkles } from 'lucide-react';

interface WinBubbleProps {
  icon: React.ReactNode;
  value: string;
  label: string;
  color: string;
}

const WinBubble = ({ icon, value, label, color }: WinBubbleProps) => (
  <motion.div
    whileHover={{ y: -5, scale: 1.03 }}
    className="flex flex-col items-center"
  >
    <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-2 ${color}`}>
      {icon}
    </div>
    <div className="text-lg font-bold text-slate-800">{value}</div>
    <div className="text-xs text-slate-500">{label}</div>
  </motion.div>
);

export default function YourWinsSection() {
  // Sample win data
  const winData = [
    {
      id: 1,
      icon: <Trophy className="w-8 h-8 text-white" />,
      value: '3',
      label: 'Badges Earned',
      color: 'bg-gradient-to-br from-amber-400 to-amber-500'
    },
    {
      id: 2,
      icon: <TrendingUp className="w-8 h-8 text-white" />,
      value: '12%',
      label: 'Portfolio Growth',
      color: 'bg-gradient-to-br from-green-400 to-green-500'
    },
    {
      id: 3,
      icon: <Sparkles className="w-8 h-8 text-white" />,
      value: '7',
      label: 'Lessons Completed',
      color: 'bg-gradient-to-br from-blue-400 to-indigo-500'
    }
  ];

  return (
    <div className="mb-6">
      <h2 className="text-xl font-semibold text-slate-800 mb-4">Your Wins</h2>
      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
        <div className="flex justify-around">
          {winData.map((win) => (
            <WinBubble
              key={win.id}
              icon={win.icon}
              value={win.value}
              label={win.label}
              color={win.color}
            />
          ))}
        </div>
      </div>
    </div>
  );
}