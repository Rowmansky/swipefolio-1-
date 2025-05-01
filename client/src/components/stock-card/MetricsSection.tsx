import React from "react";
import { TrendingUp, Shield, DollarSign, Zap } from "lucide-react";
import { StockData } from "@/lib/stock-data";

interface MetricsSectionProps {
  stock: StockData;
  onMetricClick: (metricName: string) => void;
}

const MetricsSection: React.FC<MetricsSectionProps> = ({ stock, onMetricClick }) => {
  // Define metrics with their properties
  const metrics = [
    {
      id: "performance",
      name: "Performance",
      icon: <TrendingUp className="w-4 h-4" />,
      iconColor: "text-green-500",
      value: stock.metrics?.performance?.value || 0,
      color: stock.metrics?.performance?.color || "yellow",
    },
    {
      id: "stability",
      name: "Stability",
      icon: <Shield className="w-4 h-4" />,
      iconColor: "text-blue-500",
      value: stock.metrics?.stability?.value || 0,
      color: stock.metrics?.stability?.color || "yellow",
    },
    {
      id: "value",
      name: "Value",
      icon: <DollarSign className="w-4 h-4" />,
      iconColor: "text-purple-500",
      value: stock.metrics?.value?.value || 0,
      color: stock.metrics?.value?.color || "yellow",
    },
    {
      id: "momentum",
      name: "Momentum",
      icon: <Zap className="w-4 h-4" />,
      iconColor: "text-amber-500",
      value: stock.metrics?.momentum?.value || 0,
      color: stock.metrics?.momentum?.color || "yellow",
    },
  ];

  return (
    <div className="px-4 pb-4 grid grid-cols-4 gap-2 mt-2">
      {metrics.map((metric) => (
        <div
          key={metric.id}
          className="relative overflow-hidden cursor-pointer active:scale-[0.98] transition-transform"
          onClick={() => onMetricClick(metric.name)}
        >
          {/* Enhanced Hover Glow Effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-white to-slate-200 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
          
          {/* Main Metric Box with enhanced styling */}
          <div
            className="bg-white border border-slate-200 rounded-xl shadow-sm p-2 relative overflow-hidden hover:shadow-md transition-shadow"
          >
            {/* Enhanced Top Color Bar */}
            <div 
              className={`absolute top-0 left-0 right-0 h-1 ${
                metric.color === 'green' 
                  ? 'bg-green-500' 
                  : metric.color === 'red' 
                    ? 'bg-red-500' 
                    : 'bg-amber-400'
              }`}
            ></div>
            
            {/* Icon and Info with enhanced styling */}
            <div className="flex flex-col items-center pt-1">
              <div className={`${metric.iconColor} p-2 rounded-full bg-slate-50`}>
                {metric.icon}
              </div>
              
              {/* Rating Star Display - Enhanced with shadow */}
              <div className="flex items-center mt-1.5 mb-1 justify-center">
                {[...Array(5)].map((_, i) => (
                  <div 
                    key={i}
                    className={`w-1.5 h-1.5 mx-0.5 rounded-full ${
                      i < metric.value 
                        ? metric.color === 'green' 
                          ? 'bg-green-500' 
                          : metric.color === 'red' 
                            ? 'bg-red-500' 
                            : 'bg-amber-400'
                        : 'bg-slate-200'
                    }`}
                  ></div>
                ))}
              </div>
              
              {/* Value and Name with enhanced styling */}
              <div className="text-center">
                <p className="text-xs font-medium text-slate-800 whitespace-nowrap">{metric.name}</p>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MetricsSection;