import { motion } from "framer-motion";
import { Swords, Percent, List, Flame } from "lucide-react";

interface MissionItemProps {
  icon: React.ReactNode;
  title: string;
  customTitle?: React.ReactNode;
  xpValue: number;
  iconBg: string;
  iconColor: string;
  onClick?: () => void;
}

const MissionItem = ({
  icon,
  title,
  customTitle,
  xpValue,
  iconBg,
  iconColor,
  onClick,
}: MissionItemProps) => (
  <motion.div
    whileHover={{ y: -1 }}
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className="bg-white rounded-xl p-4 flex flex-col justify-between cursor-pointer"
    style={{
      height: "100%",
      boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
      border: "1px solid rgba(0,0,0,0.03)",
    }}
  >
    <div className="flex items-center space-x-3 mb-3">
      <div
        className="rounded-lg flex-shrink-0 flex items-center justify-center"
        style={{
          backgroundColor: iconBg,
          width: "42px",
          height: "42px",
          padding: "8px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        }}
      >
        <div style={{ color: iconColor }}>{icon}</div>
      </div>
      <div className="flex-1 -mt-0.5">
        {customTitle ? (
          customTitle
        ) : (
          <h3 className="text-black font-bold text-[22px] leading-tight">
            {title}
          </h3>
        )}
      </div>
    </div>
    <div
      className="flex"
      style={{
        justifyContent:
          xpValue === 5 ? "flex-end" : xpValue === 10 ? "flex-end" : "flex-end",
      }}
    >
      <span
        className="inline-flex items-center px-3 py-1.5 rounded-full text-white font-semibold"
        style={{
          backgroundColor: "#4863FF",
          fontSize: "13px",
          boxShadow: "0 2px 4px rgba(72, 99, 255, 0.25)",
        }}
      >
        + {xpValue} XP
      </span>
    </div>
  </motion.div>
);

export default function DailyMissionsGrid() {
  // Missions data with deeper, more vibrant colors matching the screenshot
  const missions = [
    {
      id: 1,
      title: "Win a Duel",
      icon: <Swords size={24} />,
      xpValue: 25,
      iconBg: "#4361FF",
      iconColor: "#FFFFFF",
    },
    {
      id: 2,
      title: "Make a Trade",
      customTitle: (
        <div>
          <span className="text-black font-bold text-[22px] leading-tight">
            Make a
          </span>
          <span className="text-black font-bold text-[22px] leading-tight block">
            Trade
          </span>
        </div>
      ),
      icon: <Percent size={24} />,
      xpValue: 5,
      iconBg: "#4361FF",
      iconColor: "#FFFFFF",
    },
    {
      id: 3,
      title: "Review Your Moves",
      customTitle: (
        <div>
          <span className="text-black font-bold text-[22px] leading-tight">
            Review
          </span>
          <span className="text-black font-bold text-[22px] leading-tight block">
            Your Moves
          </span>
        </div>
      ),
      icon: <List size={24} />,
      xpValue: 10,
      iconBg: "#4361FF",
      iconColor: "#FFFFFF",
    },
    {
      id: 4,
      title: "2-Day Streak",
      customTitle: (
        <div>
          <span className="text-black font-bold text-[22px] leading-tight">
            2-Day
          </span>
          <span className="text-black font-bold text-[22px] leading-tight block">
            Streak
          </span>
        </div>
      ),
      icon: <Flame size={24} />,
      xpValue: 25,
      iconBg: "#9259FF",
      iconColor: "#FFFFFF",
    },
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