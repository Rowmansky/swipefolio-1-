import React from "react";
import { X, TrendingUp, ChevronLeft } from "lucide-react";
import { StockData } from "@/lib/stock-data";
import { StockCardHeaderProps } from "./types";

const StockCardHeader: React.FC<StockCardHeaderProps> = ({
  stock,
  formattedPrice,
  changeValue,
  changePercent,
  isPositive,
  onClose
}) => {
  // Default values if not provided through props
  const displayPrice = formattedPrice || `$${stock.price.toFixed(2)}`;
  const percentChange = Math.abs(stock.change * 100 / stock.price).toFixed(2);
  const changePercDisplay = changePercent || (stock.change >= 0 ? '+' : '-') + `${percentChange}%`;
  const isChangePositive = isPositive !== undefined ? isPositive : stock.change >= 0;

  return (
    <>
      {/* Stock Name & Ticker */}
      <div className="flex items-center justify-between px-5 pt-5 pb-1 mt-4">
        <div className="flex flex-col">
          <h1 className="sr-only">{stock.name} - {stock.ticker}</h1>
          <div aria-hidden="true">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium rounded-full bg-gray-100 px-2 py-0.5 text-gray-600">{stock.ticker}</span>
              <span className="text-base font-bold text-slate-900">{stock.name}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center">
          {onClose && (
            <button onClick={onClose} className="p-1.5 rounded-full hover:bg-slate-100 transition-colors">
              <X size={14} className="text-slate-400" />
            </button>
          )}
        </div>
      </div>

      {/* Price and Change - Larger, bolder, cleaner - with fixed height */}
      <div className="flex items-start px-5 pb-2 h-14">
        <span className="text-3xl font-bold text-slate-900">{displayPrice}</span>
        <div className="ml-2 flex items-center mt-1.5">
          <span className={`flex items-center text-sm px-3 py-1 rounded-full ${isChangePositive ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'}`}>
            {isChangePositive ? <TrendingUp size={12} className="mr-1" /> : <ChevronLeft size={12} className="mr-1 rotate-90" />}
            {changePercDisplay}
          </span>
        </div>
      </div>

      {/* Additional data placeholder with fixed height */}
      <div className="h-6">
        {/* Placeholder for additional data */}
      </div>
    </>
  );
};

export default StockCardHeader;

// Also export the type
export type { StockCardHeaderProps };