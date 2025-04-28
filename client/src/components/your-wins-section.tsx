import { motion } from 'framer-motion';
import { Trophy, TrendingUp, Sparkles } from 'lucide-react';

interface WinBubbleProps {
  icon: React.ReactNode;
  value: string;
  label: string;
  gradientFrom: string;
  gradientTo: string;
}

const WinBubble = ({ icon, value, label, gradientFrom, gradientTo }: WinBubbleProps) => (
  <motion.div
    whileHover={{ y: -5, scale: 1.03 }}
    className="flex flex-col items-center"
  >
    <div 
      className="w-18 h-18 rounded-full flex items-center justify-center mb-2 shadow-sm"
      style={{ 
        background: `linear-gradient(135deg, ${gradientFrom}, ${gradientTo})`,
        width: '4.25rem',
        height: '4.25rem',
        boxShadow: `0 6px 12px -3px ${gradientTo}30`
      }}
    >
      {icon}
    </div>
    <div className="text-lg font-bold text-slate-900">{value}</div>
    <div className="text-xs text-slate-500 font-medium">{label}</div>
  </motion.div>
);

export default function YourWinsSection() {
  // Sample win data with enhanced colors
  const winData = [
    {
      id: 1,
      icon: <Trophy className="w-7 h-7 text-white" />,
      value: '3',
      label: 'Badges Earned',
      gradientFrom: '#F59E0B',
      gradientTo: '#D97706'
    },
    {
      id: 2,
      icon: <TrendingUp className="w-7 h-7 text-white" />,
      value: '12%',
      label: 'Portfolio Growth',
      gradientFrom: '#10B981',
      gradientTo: '#059669'
    },
    {
      id: 3,
      icon: <Sparkles className="w-7 h-7 text-white" />,
      value: '7',
      label: 'Lessons Completed',
      gradientFrom: '#4F46E5',
      gradientTo: '#4338CA'
    }
  ];

  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold text-slate-900 mb-3">Your Wins</h2>
      <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-100"
        style={{ boxShadow: '0 4px 12px -2px rgba(0,0,0,0.05)' }}>
        <div className="flex justify-around">
          {winData.map((win) => (
            <WinBubble
              key={win.id}
              icon={win.icon}
              value={win.value}
              label={win.label}
              gradientFrom={win.gradientFrom}
              gradientTo={win.gradientTo}
            />
          ))}
        </div>
      </div>
    </div>
  );
}