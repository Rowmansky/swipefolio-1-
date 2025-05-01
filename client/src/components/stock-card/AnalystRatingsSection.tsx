import React from "react";
import { BarChart3 } from "lucide-react";
import { StockData } from "@/lib/stock-data";
import { AnalystRatingsSectionProps } from "./types";

const AnalystRatingsSection: React.FC<AnalystRatingsSectionProps> = ({ stock }) => {
  // Mock data structure for analyst ratings (typically from an API or other data source)
  const ratings = {
    buy: 65,      // percentage of analysts recommending "buy"
    hold: 25,     // percentage of analysts recommending "hold" 
    sell: 10,     // percentage of analysts recommending "sell"
    targetPrice: stock.predictedPrice || "N/A",
    currentPrice: `$${stock.price.toFixed(2)}`,
    upside: stock.predictedPrice ? 
      ((parseFloat(stock.predictedPrice.replace('$', '')) / stock.price - 1) * 100).toFixed(1) + '%' : 
      "N/A"
  };

  return (
    <div className="px-4 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <BarChart3 className="h-4 w-4 text-indigo-500" />
        <h3 className="font-semibold text-slate-800 text-sm">Analyst Recommendations</h3>
      </div>
      
      <div className="rounded-lg border border-slate-200 p-3">
        {/* Recommendation Bars */}
        <div className="space-y-2 mb-4">
          {/* Buy Rating */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="font-medium text-slate-700">Buy</span>
              <span className="text-slate-500">{ratings.buy}%</span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-green-500 rounded-full" 
                style={{ width: `${ratings.buy}%` }}
              ></div>
            </div>
          </div>
          
          {/* Hold Rating */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="font-medium text-slate-700">Hold</span>
              <span className="text-slate-500">{ratings.hold}%</span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-amber-500 rounded-full" 
                style={{ width: `${ratings.hold}%` }}
              ></div>
            </div>
          </div>
          
          {/* Sell Rating */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="font-medium text-slate-700">Sell</span>
              <span className="text-slate-500">{ratings.sell}%</span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-red-500 rounded-full" 
                style={{ width: `${ratings.sell}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        {/* Price Target */}
        <div className="border-t border-slate-100 pt-3 mt-3">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-xs text-slate-500 mb-1">Current Price</p>
              <p className="text-sm font-medium text-slate-800">{ratings.currentPrice}</p>
            </div>
            <div className="text-center px-3">
              <p className="text-xs text-slate-500 mb-1">Upside</p>
              <p className={`text-sm font-medium ${
                ratings.upside !== "N/A" && parseFloat(ratings.upside) > 0 ? 
                  'text-green-600' : 'text-red-600'
              }`}>
                {ratings.upside !== "N/A" && parseFloat(ratings.upside) > 0 ? '+' : ''}
                {ratings.upside}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500 mb-1">Price Target</p>
              <p className="text-sm font-medium text-slate-800">{ratings.targetPrice}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalystRatingsSection;