import React, { useRef, useState, useEffect } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { TimeFrame, PriceChartProps } from "./types";

const PriceChart: React.FC<PriceChartProps> = ({ 
  ticker,
  activeTimeframe,
  isLoading = false
}) => {
  // Sample chart data - in a real app this would be loaded from an API
  const [chartPrices, setChartPrices] = useState<number[]>([]);
  const [timeScaleLabels, setTimeScaleLabels] = useState<string[]>([]);
  const [minValue, setMinValue] = useState(0);
  const [maxValue, setMaxValue] = useState(100);

  const [hoveredPrice, setHoveredPrice] = useState<number | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [isChartHovered, setIsChartHovered] = useState(false);
  const chartContainerRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<SVGRectElement>) => {
    if (!chartPrices.length || !chartContainerRef.current) return;
    
    const svgRect = chartContainerRef.current.getBoundingClientRect();
    const xPercent = (e.clientX - svgRect.left) / svgRect.width * 100;
    const indexFloat = (xPercent / 100) * (chartPrices.length - 1);
    const indexLower = Math.floor(indexFloat);
    const indexUpper = Math.ceil(indexFloat);
    const fraction = indexFloat - indexLower;
    
    // Linear interpolation between two points for smoother hovering
    let price;
    if (indexLower === indexUpper) {
      price = chartPrices[indexLower];
    } else {
      price = chartPrices[indexLower] * (1 - fraction) + chartPrices[indexUpper] * fraction;
    }
    
    setHoveredPrice(price);
    setHoveredIndex(indexFloat);
    setIsChartHovered(true);
  };

  const handleTouchMove = (e: React.TouchEvent<SVGRectElement>) => {
    if (!chartPrices.length || !chartContainerRef.current) return;
    
    const svgRect = chartContainerRef.current.getBoundingClientRect();
    const xPercent = (e.touches[0].clientX - svgRect.left) / svgRect.width * 100;
    const indexFloat = (xPercent / 100) * (chartPrices.length - 1);
    const indexLower = Math.floor(indexFloat);
    const indexUpper = Math.ceil(indexFloat);
    const fraction = indexFloat - indexLower;
    
    // Linear interpolation between two points for smoother hovering
    let price;
    if (indexLower === indexUpper) {
      price = chartPrices[indexLower];
    } else {
      price = chartPrices[indexLower] * (1 - fraction) + chartPrices[indexUpper] * fraction;
    }
    
    setHoveredPrice(price);
    setHoveredIndex(indexFloat);
    setIsChartHovered(true);
  };

  const handleMouseLeave = () => {
    setIsChartHovered(false);
    setHoveredPrice(null);
    setHoveredIndex(null);
  };

  // Create the chart path from price data
  const createChartPath = () => {
    if (!chartPrices.length) return "";
    
    const height = 240; // SVG viewport height - matches div
    const width = 400;  // SVG viewport width
    
    const xStep = width / (chartPrices.length - 1);
    const yScale = height / (maxValue - minValue || 1);  // Avoid division by zero
    
    return chartPrices.map((price, i) => {
      const x = i * xStep;
      const y = height - ((price - minValue) * yScale);
      return `${i === 0 ? 'M' : 'L'} ${x},${y}`;
    }).join(' ');
  };

  // Generate some sample data on timeframe change
  useEffect(() => {
    if (ticker) {
      // Demo data - in a real app, we would fetch this from an API
      const generateDemoData = () => {
        const numPoints = activeTimeframe === "1d" ? 24 : 
                        activeTimeframe === "5d" ? 5 : 
                        activeTimeframe === "1mo" ? 30 : 
                        activeTimeframe === "3mo" ? 90 : 
                        activeTimeframe === "1y" ? 365 : 100;
        
        const basePrice = 150 + Math.random() * 50;
        const volatility = 0.1;
        
        const prices: number[] = [];
        for (let i = 0; i < numPoints; i++) {
          const change = (Math.random() - 0.5) * volatility * basePrice;
          const newPrice = i === 0 ? basePrice : prices[i-1] + change;
          prices.push(Math.max(newPrice, 1)); // Ensure price is always positive
        }
        
        // Set the data
        setChartPrices(prices);
        setMinValue(Math.min(...prices) * 0.95);
        setMaxValue(Math.max(...prices) * 1.05);
        
        // Generate time labels based on timeframe
        const labels = [];
        if (activeTimeframe === "1d") {
          labels.push("9:30 AM", "12 PM", "4 PM");
        } else if (activeTimeframe === "5d" || activeTimeframe === "1mo") {
          labels.push("Week 1", "Week 2", "Week 3", "Week 4");
        } else {
          labels.push("Jan", "Apr", "Jul", "Oct", "Dec");
        }
        setTimeScaleLabels(labels);
      };
      
      generateDemoData();
    }
  }, [ticker, activeTimeframe]);

  return (
    <div className="relative h-64 w-full -mx-1 mt-3">
      {isLoading ? (
        <div className="absolute inset-0 flex items-center justify-center bg-white">
          <Skeleton className="h-40 w-full mx-auto rounded" />
        </div>
      ) : (
        <>
          {chartPrices.length > 0 ? (
            <div 
              ref={chartContainerRef}
              className="absolute inset-0 touch-manipulation">
              <svg viewBox="0 0 400 240" className="w-full h-full overflow-visible">
                <defs>
                  {/* Subtle glow effect for the line */}
                  <filter id="glow" height="300%" width="300%" x="-100%" y="-100%">
                    <feGaussianBlur stdDeviation="1.5" result="coloredBlur" />
                    <feComposite in="SourceGraphic" in2="coloredBlur" operator="over" />
                  </filter>
                </defs>
                
                {/* Horizontal dotted grid lines */}
                {[0, 1, 2, 3].map(i => (
                  <line key={i} x1="0" y1={60 * i} x2="400" y2={60 * i} stroke="#f1f5f9" strokeWidth="1" strokeDasharray="1,3" />
                ))}
                
                {/* Chart Line */}
                <path
                  d={createChartPath()}
                  fill="none"
                  stroke="#3b82f6"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  filter="url(#glow)"
                />
                
                {/* Interactive Price Tracker */}
                <g className="price-tracker-group">
                  {/* Invisible overlay for interaction */}
                  <rect
                    x="0"
                    y="0"
                    width="400"
                    height="240"
                    fill="transparent"
                    onMouseMove={handleMouseMove}
                    onMouseLeave={handleMouseLeave}
                    onTouchMove={handleTouchMove}
                    onTouchEnd={handleMouseLeave}
                    className="touch-manipulation"
                  />
                  
                  {/* Interactive elements only shown when hovering */}
                  {isChartHovered && hoveredIndex !== null && hoveredPrice !== null && (
                    <>
                      {/* Vertical cursor line */}
                      <line
                        x1={hoveredIndex / (chartPrices.length - 1) * 400}
                        y1="0"
                        x2={hoveredIndex / (chartPrices.length - 1) * 400}
                        y2="240"
                        stroke="#6b7280"
                        strokeWidth="0.8"
                        strokeDasharray="2,2"
                      />
                      
                      {/* Price point */}
                      <circle
                        cx={hoveredIndex / (chartPrices.length - 1) * 400}
                        cy={240 - ((hoveredPrice - minValue) / (maxValue - minValue || 1) * 240)}
                        r="3.5"
                        fill="white"
                        stroke="#3b82f6"
                        strokeWidth="1.5"
                      />
                      
                      {/* Price label */}
                      <g transform={`translate(${Math.min(Math.max(hoveredIndex / (chartPrices.length - 1) * 400, 30), 370)}, 15)`}>
                        <rect
                          x="-25"
                          y="-12"
                          width="50"
                          height="22"
                          rx="4"
                          fill="rgba(30, 41, 59, 0.85)"
                        />
                        <text
                          x="0"
                          y="2"
                          textAnchor="middle"
                          fontSize="11"
                          fontWeight="bold"
                          fill="white"
                          fontFamily="system-ui, -apple-system, sans-serif"
                        >
                          ${hoveredPrice.toFixed(2)}
                        </text>
                      </g>
                    </>
                  )}
                </g>
              </svg>
              
              {/* X Axis Labels */}
              <div className="flex justify-between text-[10px] text-slate-400 px-3 mt-1 font-medium">
                {timeScaleLabels.map((label, i) => (
                  <div key={i}>{label}</div>
                ))}
              </div>
            </div>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-slate-400 text-sm font-medium">No chart data available</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default PriceChart;