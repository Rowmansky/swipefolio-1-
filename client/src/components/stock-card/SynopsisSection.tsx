import React from "react";
import { Building, TrendingUp, Layers } from "lucide-react";
import { StockData } from "@/lib/stock-data";

interface SynopsisSectionProps {
  stock: StockData;
}

const SynopsisSection: React.FC<SynopsisSectionProps> = ({ stock }) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-md overflow-hidden my-4 mx-4"> {/* Added mx-4 for horizontal margin */}
      {/* Price Trend */}
      <div className="flex items-center p-4 border-b border-slate-100">
        <div className="bg-blue-50 p-2 rounded-md mr-3">
          <TrendingUp className="w-4 h-4 text-blue-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-slate-800">{stock.synopsis.priceTrend.title}</h3>
          <p className="text-xs text-slate-600 mt-0.5 line-clamp-2">{stock.synopsis.priceTrend.description}</p>
        </div>
      </div>
      
      {/* Company Overview */}
      <div className="flex items-center p-4 border-b border-slate-100">
        <div className="bg-violet-50 p-2 rounded-md mr-3">
          <Building className="w-4 h-4 text-violet-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-slate-800">{stock.synopsis.overview.title}</h3>
          <p className="text-xs text-slate-600 mt-0.5 line-clamp-2">{stock.synopsis.overview.description}</p>
        </div>
      </div>
      
      {/* Portfolio Role */}
      <div className="flex items-center p-4">
        <div className="bg-emerald-50 p-2 rounded-md mr-3">
          <Layers className="w-4 h-4 text-emerald-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-slate-800">{stock.synopsis.portfolioRole.title}</h3>
          <p className="text-xs text-slate-600 mt-0.5 line-clamp-2">{stock.synopsis.portfolioRole.description}</p>
        </div>
      </div>
    </div>
  );
};

export default SynopsisSection;