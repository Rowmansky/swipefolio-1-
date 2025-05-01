import React from "react";
import { Building, TrendingUp, Layers } from "lucide-react";
import { StockData } from "@/lib/stock-data";

interface SynopsisSectionProps {
  stock: StockData;
}

// Define a type guard to check for priceTrend properties
function hasPriceTrend(obj: any): obj is { priceTrend: { title: string, description: string } } {
  return obj && typeof obj === 'object' && obj.priceTrend && 
    typeof obj.priceTrend === 'object' && 
    typeof obj.priceTrend.title === 'string' && 
    typeof obj.priceTrend.description === 'string';
}

// Define a type guard to check for overview properties
function hasOverview(obj: any): obj is { overview: { title: string, description: string } } {
  return obj && typeof obj === 'object' && obj.overview && 
    typeof obj.overview === 'object' && 
    typeof obj.overview.title === 'string' && 
    typeof obj.overview.description === 'string';
}

// Define a type guard to check for portfolioRole properties
function hasPortfolioRole(obj: any): obj is { portfolioRole: { title: string, description: string } } {
  return obj && typeof obj === 'object' && obj.portfolioRole && 
    typeof obj.portfolioRole === 'object' && 
    typeof obj.portfolioRole.title === 'string' && 
    typeof obj.portfolioRole.description === 'string';
}

// Define a type guard to check for simple properties
function hasSimpleProps(obj: any): obj is { price: string, company: string, role: string } {
  return obj && typeof obj === 'object' && 
    typeof obj.price === 'string' && 
    typeof obj.company === 'string' && 
    typeof obj.role === 'string';
}

const SynopsisSection: React.FC<SynopsisSectionProps> = ({ stock }) => {
  // Use fallback data if synopsis doesn't exist
  const synopsis = stock.synopsis || {};
  
  // Default values
  let priceTrendTitle = "Price Trend";
  let priceTrendDesc = "Analysis of the stock's recent price movement and trading patterns.";
  let overviewTitle = "Company Overview";
  let overviewDesc = "Key information about the company's business model, market position, and competitive advantages.";
  let portfolioRoleTitle = "Portfolio Role";
  let portfolioRoleDesc = "How this stock might fit into a diversified investment portfolio.";
  
  // Check for detailed structure first
  if (hasPriceTrend(synopsis)) {
    priceTrendTitle = synopsis.priceTrend.title;
    priceTrendDesc = synopsis.priceTrend.description;
  }
  
  if (hasOverview(synopsis)) {
    overviewTitle = synopsis.overview.title;
    overviewDesc = synopsis.overview.description;
  }
  
  if (hasPortfolioRole(synopsis)) {
    portfolioRoleTitle = synopsis.portfolioRole.title;
    portfolioRoleDesc = synopsis.portfolioRole.description;
  }
  
  // Check for simple structure as fallback
  if (hasSimpleProps(synopsis)) {
    if (!hasPriceTrend(synopsis)) priceTrendTitle = synopsis.price;
    if (!hasOverview(synopsis)) overviewTitle = synopsis.company;
    if (!hasPortfolioRole(synopsis)) portfolioRoleTitle = synopsis.role;
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-md overflow-hidden my-4 mx-4"> {/* Added mx-4 for horizontal margin */}
      {/* Price Trend */}
      <div className="flex items-center p-4 border-b border-slate-100">
        <div className="bg-blue-50 p-2 rounded-md mr-3">
          <TrendingUp className="w-4 h-4 text-blue-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-slate-800">{priceTrendTitle}</h3>
          <p className="text-xs text-slate-600 mt-0.5 line-clamp-2">{priceTrendDesc}</p>
        </div>
      </div>
      
      {/* Company Overview */}
      <div className="flex items-center p-4 border-b border-slate-100">
        <div className="bg-violet-50 p-2 rounded-md mr-3">
          <Building className="w-4 h-4 text-violet-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-slate-800">{overviewTitle}</h3>
          <p className="text-xs text-slate-600 mt-0.5 line-clamp-2">{overviewDesc}</p>
        </div>
      </div>
      
      {/* Portfolio Role */}
      <div className="flex items-center p-4">
        <div className="bg-emerald-50 p-2 rounded-md mr-3">
          <Layers className="w-4 h-4 text-emerald-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-slate-800">{portfolioRoleTitle}</h3>
          <p className="text-xs text-slate-600 mt-0.5 line-clamp-2">{portfolioRoleDesc}</p>
        </div>
      </div>
    </div>
  );
};

export default SynopsisSection;