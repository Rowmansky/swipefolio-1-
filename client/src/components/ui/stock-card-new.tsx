// File: client/src/components/ui/stock-card-new.tsx
import { useState, useRef, useCallback } from "react";
import { StockData } from "@/lib/stock-data";
import { motion, useAnimation, useMotionValue, PanInfo } from "framer-motion";
import { ChevronLeft, ChevronRight, RefreshCw } from "lucide-react";

// Import modularized components
import {
  StockCardHeader,
  PriceChart,
  TimeframeSelector,
  MetricsSection,
  SynopsisSection,
  NewsSection,
  AnalystRatingsSection,
  ComparativeAnalysisWrapper,
  HistoricalChartWrapper,
  TimeFrame
} from "@/components/stock-card";

interface StockCardProps {
  stock: StockData;
  onClose?: () => void;
  onSwipe?: (direction: "left" | "right") => void;
  onMetricClick?: (metricName: string) => void;
  showHeader?: boolean;
  showFooter?: boolean;
  isLoading?: boolean;
  cardIndex?: number;
  totalCards?: number;
  className?: string;
}

export default function StockCard({
  stock,
  onClose,
  onSwipe,
  onMetricClick = () => {},
  showHeader = true,
  showFooter = true,
  isLoading = false,
  cardIndex,
  totalCards,
  className = "",
}: StockCardProps) {
  // State management
  const [activeTimeframe, setActiveTimeframe] = useState<TimeFrame>("1mo");
  const [showAllSections, setShowAllSections] = useState(false);
  
  // Swipe interaction and animation controls
  const cardRef = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const controls = useAnimation();
  
  // Handle swipe gesture on mobile
  const handleDragEnd = useCallback((event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const threshold = 100; // Minimum drag distance to trigger swipe
    
    if (Math.abs(info.offset.x) > threshold && onSwipe) {
      if (info.offset.x > 0) {
        onSwipe("right");
      } else {
        onSwipe("left");
      }
    } else {
      // Return to center if swipe was not far enough
      controls.start({ x: 0, transition: { type: "spring", stiffness: 300, damping: 20 } });
    }
  }, [controls, onSwipe]);
  
  // Handle timeframe change
  const handleTimeframeChange = (timeframe: TimeFrame) => {
    setActiveTimeframe(timeframe);
  };
  
  // Toggle additional sections
  const toggleSections = () => {
    setShowAllSections(!showAllSections);
  };
  
  return (
    <motion.div
      ref={cardRef}
      className={`stock-card relative overflow-hidden bg-background rounded-2xl max-w-md mx-auto ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
      style={{ x }}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.1}
      onDragEnd={handleDragEnd}
    >
      {/* Navigation overlay - only shown when we have multiple cards */}
      {cardIndex !== undefined && totalCards && totalCards > 1 && (
        <div className="absolute top-1/2 -translate-y-1/2 w-full flex justify-between px-2 z-10 pointer-events-none">
          <button
            onClick={() => onSwipe && onSwipe("right")} 
            className="h-10 w-10 bg-white rounded-full flex items-center justify-center shadow pointer-events-auto"
            aria-label="Previous stock"
          >
            <ChevronLeft className="h-6 w-6 text-slate-600" />
          </button>
          <button
            onClick={() => onSwipe && onSwipe("left")}
            className="h-10 w-10 bg-white rounded-full flex items-center justify-center shadow pointer-events-auto"
            aria-label="Next stock"
          >
            <ChevronRight className="h-6 w-6 text-slate-600" />
          </button>
        </div>
      )}

      {/* Card Header */}
      {showHeader && (
        <StockCardHeader
          stock={stock}
          onClose={onClose}
        />
      )}

      {/* Price Chart */}
      <PriceChart
        ticker={stock.ticker}
        activeTimeframe={activeTimeframe}
        isLoading={isLoading}
      />

      {/* Timeframe Selector */}
      <TimeframeSelector
        selectedTimeframe={activeTimeframe}
        onSelect={handleTimeframeChange}
      />

      {/* Metrics Section */}
      <MetricsSection
        stock={stock}
        onMetricClick={onMetricClick}
      />

      {/* Synopsis Section */}
      <SynopsisSection stock={stock} />

      {/* Full Analysis Section - Conditionally shown */}
      {showAllSections && (
        <>
          <ComparativeAnalysisWrapper stock={stock} />
          <HistoricalChartWrapper stock={stock} />
          <AnalystRatingsSection stock={stock} />
          <NewsSection stock={stock} />
        </>
      )}

      {/* Card Footer with Expand/Collapse button */}
      {showFooter && (
        <div className="p-4 flex justify-center border-t border-slate-100">
          <button
            onClick={toggleSections}
            className="bg-slate-50 hover:bg-slate-100 text-slate-700 text-sm font-medium py-2 px-4 rounded-full flex items-center gap-2 transition-colors"
            aria-expanded={showAllSections}
          >
            <RefreshCw className="h-4 w-4" />
            {showAllSections ? "Show Less" : "Show More Analysis"}
          </button>
        </div>
      )}
    </motion.div>
  );
}