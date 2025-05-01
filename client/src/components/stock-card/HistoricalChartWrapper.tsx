import React from "react";
import { LineChart, Info } from "lucide-react";
import { StockData, HistoricalReturn } from "@/lib/stock-data";
import { HistoricalChartWrapperProps } from "./types";

const HistoricalChartWrapper: React.FC<HistoricalChartWrapperProps> = ({ stock }) => {
  // Check if historical data exists
  const hasHistoricalData = stock.historicalData && 
    Array.isArray(stock.historicalData.prices) && 
    stock.historicalData.prices.length > 0;

  return (
    <div className="px-4 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <LineChart className="h-4 w-4 text-emerald-500" />
        <h3 className="font-semibold text-slate-800 text-sm">Historical Performance</h3>
      </div>
      
      {hasHistoricalData ? (
        <div className="rounded-lg border border-slate-200 p-3">
          <div className="mb-3">
            <p className="text-sm text-slate-600">
              {stock.historicalData?.description || 
                `Long-term performance analysis of ${stock.name} showing key trends and growth metrics.`}
            </p>
          </div>
          
          <div className="aspect-[3/2] bg-slate-50 rounded-md overflow-hidden relative mb-2">
            {/* Historical Chart Placeholder - In a real implementation, we would use a chart library here */}
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-sm text-slate-400">Historical chart visualization</p>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-2 text-center">
            {['1Y Return', '3Y Return', '5Y Return'].map((label: string, index: number) => {
              const value = stock.historicalData?.returns?.[index]?.value || 0;
              const isPositive = value >= 0;
              
              return (
                <div key={label} className="bg-slate-50 rounded-md p-2">
                  <p className="text-xs text-slate-600 mb-1">{label}</p>
                  <p className={`text-sm font-semibold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                    {isPositive ? '+' : ''}{value}%
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center py-6 border border-dashed border-slate-200 rounded-lg">
          <div className="flex items-center gap-2 text-slate-500">
            <Info className="h-4 w-4" />
            <p className="text-sm">Historical data unavailable</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoricalChartWrapper;