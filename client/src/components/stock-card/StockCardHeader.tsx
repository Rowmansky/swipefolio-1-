import React from "react";
import { RefreshCw, TrendingUp, ChevronLeft } from "lucide-react";
import { StockData } from "@/lib/stock-data";
import { PriceInfo } from "./types";

interface StockCardHeaderProps {
  stock: StockData;
  priceInfo: PriceInfo;
  isRefreshing: boolean;
  onRefresh: () => void;
}

const StockCardHeader: React.FC<StockCardHeaderProps> = ({
  stock,
  priceInfo,
  isRefreshing,
  onRefresh
}) => {
  const { displayPrice, priceChange, dayRange, latestTradingDay } = priceInfo;
  const realTimeChange = priceChange.percent;

  return (
    <>
      {/* Stock Name & Ticker - Robinhood Style, moved down */}
      <div className="flex items-center justify-between px-5 pt-5 pb-1 mt-4">
        <div className="flex flex-col">
          <h1 className="sr-only">{stock.name} - {stock.ticker}</h1>
          <div aria-hidden="true">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium rounded-full bg-gray-100 px-2 py-0.5 text-gray-600">{stock.ticker}</span>
              <span className="text-base font-bold text-slate-900">{stock.name}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center">
          <button onClick={onRefresh} className="p-1.5 rounded-full hover:bg-slate-100 transition-colors" disabled={isRefreshing}>
            <RefreshCw size={14} className={`text-slate-400 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Price and Change - Larger, bolder, cleaner - with fixed height */}
      <div className="flex items-start px-5 pb-2 h-14"> {/* Added fixed height */}
        <span className="text-3xl font-bold text-slate-900">${displayPrice}</span>
        <div className="ml-2 flex items-center mt-1.5">
          <span className={`flex items-center text-sm px-3 py-1 rounded-full ${realTimeChange >= 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'}`}>
            {realTimeChange >= 0 ? <TrendingUp size={12} className="mr-1" /> : <ChevronLeft size={12} className="mr-1 rotate-90" />}
            {Math.abs(realTimeChange).toFixed(2)}%
          </span>
        </div>
      </div>

      {/* Day's Range - Only shown when Yahoo data is available - with fixed height */}
      <div className="h-6"> {/* Fixed height container */}
        {dayRange.low > 0 && dayRange.high > 0 && (
          <div className="px-5 flex items-center text-xs text-slate-500">
            <span className="mr-2">Day's Range:</span>
            <span className="font-medium">${dayRange.low.toFixed(2)} - ${dayRange.high.toFixed(2)}</span>
          </div>
        )}
      </div>
    </>
  );
};

export default StockCardHeader;