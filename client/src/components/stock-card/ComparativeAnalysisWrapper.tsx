import React from "react";
import { BarChart2, Info } from "lucide-react";
import { StockData, ComparativeMetric } from "@/lib/stock-data";
import { ComparativeAnalysisWrapperProps } from "./types";

const ComparativeAnalysisWrapper: React.FC<ComparativeAnalysisWrapperProps> = ({ stock }) => {
  // Check if comparative data exists
  const hasComparativeData = stock.comparativeData && 
    Array.isArray(stock.comparativeData.metrics) && 
    stock.comparativeData.metrics.length > 0;

  return (
    <div className="px-4 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <BarChart2 className="h-4 w-4 text-purple-500" />
        <h3 className="font-semibold text-slate-800 text-sm">Comparative Analysis</h3>
      </div>

      {hasComparativeData ? (
        <div className="rounded-lg border border-slate-200 p-3">
          <div className="mb-3">
            <p className="text-sm text-slate-600">
              {stock.comparativeData?.description || 
                `Comparison of ${stock.name} against industry averages and key competitors.`}
            </p>
          </div>

          <div className="space-y-2.5">
            {stock.comparativeData?.metrics.slice(0, 3).map((metric: ComparativeMetric, index: number) => (
              <div key={index} className="relative">
                <div className="flex justify-between mb-1 items-center">
                  <div className="text-xs font-medium text-slate-700">{metric.name}</div>
                  <div className="text-xs text-slate-500">
                    {metric.value}
                    {metric.unit ? ` ${metric.unit}` : ''}
                  </div>
                </div>
                
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      metric.performance === 'good' ? 'bg-green-500' : 
                      metric.performance === 'average' ? 'bg-amber-500' : 
                      'bg-red-500'
                    }`}
                    style={{ width: `${Math.min(Math.max(metric.percentile || 50, 0), 100)}%` }}
                  ></div>
                </div>
                
                <div className="flex justify-between mt-1">
                  <span className="text-[10px] text-slate-400">Industry Min</span>
                  <span className="text-[10px] text-slate-400">Industry Max</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center py-6 border border-dashed border-slate-200 rounded-lg">
          <div className="flex items-center gap-2 text-slate-500">
            <Info className="h-4 w-4" />
            <p className="text-sm">Comparative data unavailable</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComparativeAnalysisWrapper;