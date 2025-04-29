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
    whileHover={{ y: -3, scale: 1.02 }}
    className="flex flex-col items-center"
  >
    <div 
      className="rounded-full flex items-center justify-center mb-2 shadow-sm"
      style={{ 
        background: `linear-gradient(135deg, ${gradientFrom}, ${gradientTo})`,
        width: '3.75rem',
        height: '3.75rem',
        boxShadow: `0 4px 10px -2px ${gradientTo}40`
      }}
    >
      {icon}
    </div>
    <div className="text-lg font-bold text-black mt-1">{value}</div>
    <div className="text-xs text-gray-600 font-medium">{label}</div>
  </motion.div>
);

export default function YourWinsSection() {
  // Sample win data with colors matching the app theme
  const winData = [
    {
      id: 1,
      icon: <Trophy className="w-7 h-7 text-white" />,
      value: '3',
      label: 'Badges Earned',
      gradientFrom: '#4361FF',
      gradientTo: '#3A56E6'
    },
    {
      id: 2,
      icon: <TrendingUp className="w-7 h-7 text-white" />,
      value: '12%',
      label: 'Portfolio Growth',
      gradientFrom: '#4361FF',
      gradientTo: '#3A56E6'
    },
    {
      id: 3,
      icon: <Sparkles className="w-7 h-7 text-white" />,
      value: '7',
      label: 'Lessons Completed',
      gradientFrom: '#9259FF',
      gradientTo: '#7C4AE0'
    }
  ];

  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold text-black mb-2.5">Your Wins</h2>
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100"
        style={{ boxShadow: '0 2px 6px rgba(0,0,0,0.05)' }}>
        <div className="flex justify-between px-4 py-2">
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