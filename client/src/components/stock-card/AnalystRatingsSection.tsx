import React from "react";
import { AnalystRatingsRedesign } from "@/components/stock-detail/analyst-ratings-redesign";
import { StockData } from "@/lib/stock-data";

interface AnalystRatingsSectionProps {
  stock: StockData;
}

const AnalystRatingsSection: React.FC<AnalystRatingsSectionProps> = ({ stock }) => {
  return (
    <div className="px-4 mb-4 rounded-xl shadow-md bg-white mx-4 overflow-hidden">
      <AnalystRatingsRedesign symbol={stock.ticker} />
    </div>
  );
};

export default AnalystRatingsSection;