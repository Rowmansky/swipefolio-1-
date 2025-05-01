import React from "react";
import AskAI from "@/components/ui/ask-ai";
import { StockData } from "@/lib/stock-data";

interface AskAISectionProps {
  stock: StockData;
}

const AskAISection: React.FC<AskAISectionProps> = ({ stock }) => {
  return (
    <div className="bg-white border-t border-slate-100 mx-4 mb-4 rounded-xl shadow-md"> 
      {/* Added margin and rounded corners */}
      <AskAI stock={stock} />
    </div>
  );
};

export default AskAISection;