import { motion } from 'framer-motion';

interface MissionItemProps {
  icon: React.ReactNode;
  title: string;
  customTitle?: React.ReactNode;
  xpValue: number;
  iconBg: string;
  iconColor: string;
  onClick?: () => void;
}

// Creating custom SVG icons that exactly match the iOS reference
// Using filled variants for more vibrant, noticeable appearance
const SwordIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M14.5 12.5L19 8M8.5 18.5L5 22M8.5 8.5L5 5M17.5 17.5L22 22M8.5 8.5L12.5 12.5M12.5 12.5L8.5 18.5M12.5 12.5L17.5 17.5" 
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const PercentIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M19 5L5 19M9 7C9 8.10457 8.10457 9 7 9C5.89543 9 5 8.10457 5 7C5 5.89543 5.89543 5 7 5C8.10457 5 9 5.89543 9 7ZM19 17C19 18.1046 18.1046 19 17 19C15.8954 19 15 18.1046 15 17C15 15.8954 15.8954 15 17 15C18.1046 15 19 15.8954 19 17Z" 
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const ListIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M8 6H19M8 12H19M8 18H19M4 6H4.01M4 12H4.01M4 18H4.01" 
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const FlameIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2C8.5 7 6 9 6 14C6 19 8.5 21 12 21C15.5 21 18 19 18 14C18 9 15.5 7 12 2Z" 
      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const MissionItem = ({ icon, title, customTitle, xpValue, iconBg, iconColor, onClick }: MissionItemProps) => (
  <motion.div
    whileHover={{ y: -1 }}
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className="bg-white rounded-xl p-3 flex flex-col justify-between cursor-pointer"
    style={{ 
      height: '100%',
      boxShadow: '0 1px 1px rgba(0,0,0,0.02)'
    }}
  >
    <div className="flex items-center space-x-3 mb-3">
      <div className="rounded-lg flex-shrink-0 flex items-center justify-center" 
        style={{ 
          backgroundColor: iconBg,
          width: '32px',
          height: '32px',
          padding: '4px'
        }}>
        <div style={{ color: iconColor }}>
          {icon}
        </div>
      </div>
      <div className="flex-1 -mt-0.5">
        {customTitle ? (
          customTitle
        ) : (
          <h3 className="text-black font-semibold text-[15px] leading-tight">{title}</h3>
        )}
      </div>
    </div>
    <div className="flex" style={{ 
        justifyContent: xpValue === 5 ? "flex-end" : (xpValue === 10 ? "flex-start" : "flex-end")
      }}>
      <span className="inline-flex items-center px-2 py-[2px] rounded-full text-white text-xs font-semibold"
        style={{ 
          backgroundColor: '#4863FF',
          fontSize: '11px'
        }}>
        + {xpValue} XP
      </span>
    </div>
  </motion.div>
);

export default function DailyMissionsGrid() {
  // Missions data with exact iOS match from the reference image with more vibrant colors
  const missions = [
    {
      id: 1,
      title: 'Win a Duel',
      icon: <SwordIcon />,
      xpValue: 25,
      iconBg: '#DBE1FF',
      iconColor: '#5271FF'
    },
    {
      id: 2,
      title: 'Make a Trade',
      customTitle: (
        <div>
          <span className="text-black font-semibold text-[15px] leading-tight">Make a</span>
          <span className="text-black font-semibold text-[15px] leading-tight block">Trade</span>
        </div>
      ),
      icon: <PercentIcon />,
      xpValue: 5,
      iconBg: '#DBE1FF',
      iconColor: '#5271FF'
    },
    {
      id: 3,
      title: 'Review Your Moves',
      customTitle: (
        <div>
          <span className="text-black font-semibold text-[15px] leading-tight">Review</span>
          <span className="text-black font-semibold text-[15px] leading-tight block">Your Moves</span>
        </div>
      ),
      icon: <ListIcon />,
      xpValue: 10,
      iconBg: '#DBE1FF',
      iconColor: '#5271FF'
    },
    {
      id: 4,
      title: '2-Day Streak',
      customTitle: (
        <div>
          <span className="text-black font-semibold text-[15px] leading-tight">2-Day</span>
          <span className="text-black font-semibold text-[15px] leading-tight block">Streak</span>
        </div>
      ),
      icon: <FlameIcon />,
      xpValue: 25,
      iconBg: '#EADFFF',
      iconColor: '#9167FF'
    }
  ];

  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold text-black mb-2.5">Daily Missions</h2>
      <div className="grid grid-cols-2 gap-2.5">
        {missions.map((mission) => (
          <MissionItem
            key={mission.id}
            icon={mission.icon}
            title={mission.title}
            customTitle={mission.customTitle}
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