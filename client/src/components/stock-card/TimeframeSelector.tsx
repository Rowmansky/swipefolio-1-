import React from "react";
import { Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { TimeFrame } from "./types";

interface TimeframeSelectorProps {
  timeFrame: TimeFrame;
  visitedTimeframes: Record<TimeFrame, boolean>;
  onTimeFrameChange: (newTimeFrame: TimeFrame) => void;
  latestTradingDay: string | null;
}

const TimeframeSelector: React.FC<TimeframeSelectorProps> = ({
  timeFrame,
  visitedTimeframes,
  onTimeFrameChange,
  latestTradingDay
}) => {
  // Define available timeframes for the selector
  const timeFrames: {period: string; label: string}[] = [
    { period: "1D", label: "1D" },
    { period: "1W", label: "1W" }, // Actually uses 5D in the API
    { period: "1M", label: "1M" },
    { period: "3M", label: "3M" },
    { period: "1Y", label: "1Y" },
    { period: "MAX", label: "MAX" }
  ];

  return (
    <>
      {/* --- Time frame selector (Robinhood style below chart) - Moved up slightly --- */}
      <div className="px-3 py-3 flex justify-center">
        <div className="grid grid-cols-6 gap-x-1 w-full max-w-xs bg-slate-100 rounded-full p-1">
          {timeFrames.map((item) => {
            const isActive = timeFrame === (item.period === "1W" ? "5D" : item.period);
            const actualTimeframe = (item.period === "1W" ? "5D" : item.period) as TimeFrame;
            const hasBeenVisited = visitedTimeframes[actualTimeframe];
            
            return (
              <button
                key={item.period}
                onClick={() => onTimeFrameChange(actualTimeframe)}
                className={cn(
                  "relative text-xs h-8 rounded-full flex items-center justify-center font-medium transition-all outline-none",
                  isActive
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-slate-600 hover:bg-white/50"
                )}
              >
                {item.label}
                {!hasBeenVisited && (
                  <div className="absolute -top-0.5 -right-0.5">
                    {/* Show loading indicator only for first visit */}
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>
      
      {/* Last Updated Info - Only shown when Yahoo data provides a trading date */}
      {latestTradingDay && (
        <div className="px-5 flex justify-center">
          <div className="flex items-center text-xs text-slate-400 mb-2">
            <Clock size={12} className="mr-1" />
            <span>Last updated: {latestTradingDay}</span>
          </div>
        </div>
      )}
    </>
  );
};

export default TimeframeSelector;