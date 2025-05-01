import React from "react";
import ComparativeAnalysis from "@/components/comparative-analysis";
import { StockData } from "@/lib/stock-data";

interface ComparativeAnalysisWrapperProps {
  stock: StockData;
}

const ComparativeAnalysisWrapper: React.FC<ComparativeAnalysisWrapperProps> = ({ stock }) => {
  return (
    <div 
      className="bg-white border-t border-b border-slate-100 comparative-analysis-container mx-4 mb-4 rounded-xl shadow-md" 
      onClick={(e) => e.stopPropagation()}
    > 
      {/* Added margin and rounded corners */}
      <ComparativeAnalysis stock={stock} />
    </div>
  );
};

export default ComparativeAnalysisWrapper;