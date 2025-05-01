import React from "react";
import HistoricalPerformanceChart from "@/components/stock-detail/historical-performance-chart";
import { StockData } from "@/lib/stock-data";

interface HistoricalChartWrapperProps {
  stock: StockData;
}

const HistoricalChartWrapper: React.FC<HistoricalChartWrapperProps> = ({ stock }) => {
  return (
    <div className="px-4 mb-4 rounded-xl shadow-md bg-white mx-4 overflow-hidden">
      <HistoricalPerformanceChart ticker={stock.ticker} />
    </div>
  );
};

export default HistoricalChartWrapper;