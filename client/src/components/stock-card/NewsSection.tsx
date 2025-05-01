import React from "react";
import StockNewsSection from "@/components/stock-news/StockNewsSection";
import { StockData } from "@/lib/stock-data";

interface NewsSectionProps {
  stock: StockData;
}

const NewsSection: React.FC<NewsSectionProps> = ({ stock }) => {
  return (
    <div className="bg-white border-t border-slate-100 mb-4 mx-4 rounded-xl shadow-md overflow-hidden"> 
      {/* Added margin and rounded corners */}
      <StockNewsSection ticker={stock.ticker} />
    </div>
  );
};

export default NewsSection;