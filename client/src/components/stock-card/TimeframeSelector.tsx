import React from "react";
import { Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { TimeFrame, TimeframeSelectorProps } from "./types";

const DEFAULT_TIMEFRAMES: TimeFrame[] = ["1d", "5d", "1mo", "3mo", "1y", "max"];

const TimeframeSelector: React.FC<TimeframeSelectorProps> = ({
  selectedTimeframe = "1mo",
  timeframes = DEFAULT_TIMEFRAMES,
  timeframeLabel,
  onSelect,
  onTimeframeChange
}) => {
  // Use the appropriate callback function
  const handleTimeframeChange = (timeframe: TimeFrame) => {
    if (onSelect) {
      onSelect(timeframe);
    } else if (onTimeframeChange) {
      onTimeframeChange(timeframe);
    }
  };

  // Map display labels to timeframes 
  const timeFrameLabels: Record<TimeFrame, string> = {
    "1d": "1D",
    "5d": "1W",
    "1mo": "1M",
    "3mo": "3M",
    "6mo": "6M",
    "1y": "1Y",
    "5y": "5Y",
    "ytd": "YTD",
    "max": "MAX"
  };

  return (
    <>
      {/* Timeframe selector - Robinhood style below chart */}
      <div className="px-3 py-3 flex justify-center">
        <div className="grid grid-cols-6 gap-x-1 w-full max-w-xs bg-slate-100 rounded-full p-1">
          {timeframes.map((timeframe) => {
            const isActive = selectedTimeframe === timeframe;
            
            return (
              <button
                key={timeframe}
                onClick={() => handleTimeframeChange(timeframe)}
                className={cn(
                  "relative text-xs h-8 rounded-full flex items-center justify-center font-medium transition-all outline-none",
                  isActive
                    ? "bg-white text-slate-900 shadow-sm"
                    : "text-slate-600 hover:bg-white/50"
                )}
              >
                {timeFrameLabels[timeframe]}
              </button>
            );
          })}
        </div>
      </div>
      
      {/* Last Updated Info */}
      {timeframeLabel && (
        <div className="px-5 flex justify-center">
          <div className="flex items-center text-xs text-slate-400 mb-2">
            <Clock size={12} className="mr-1" />
            <span>Period: {timeframeLabel}</span>
          </div>
        </div>
      )}
    </>
  );
};

export default TimeframeSelector;