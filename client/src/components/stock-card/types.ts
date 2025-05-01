import { AnimationControls, useMotionValue } from "framer-motion";
import { StockData } from "@/lib/stock-data";
import { YahooChartResponse } from "@/lib/yahoo-finance-client";

// Define Metric structure used in handleMetricClick callback
export interface MetricClickData {
  name: string;
  color: "green" | "yellow" | "red";
  data: any; // Keep the detailed data structure needed by the modal
}

export interface StockCardProps {
  stock: StockData;
  onNext?: () => void;
  onPrevious?: () => void;
  onInvest?: () => void;
  onMetricClick?: (metricData: MetricClickData) => void; // Callback for parent
  onOpenCalculator?: () => void; // Callback for parent
  currentIndex: number;
  totalCount: number;
  displayMode?: 'simple' | 'realtime'; // Keep displayMode if needed elsewhere
  cardControls?: AnimationControls; // Optional controls from parent
  x?: ReturnType<typeof useMotionValue<number>>; // Optional motion value from parent
}

// Define TimeFrame type locally if not imported
export type TimeFrame = "1D" | "5D" | "1M" | "3M" | "6M" | "YTD" | "1Y" | "5Y" | "MAX";

// Common price information shared between components
export interface PriceInfo {
  currentPrice: number;
  displayPrice: string;
  priceChange: {
    value: number;
    percent: number;
  };
  dayRange: {
    low: number;
    high: number;
  };
  latestTradingDay: string | null;
}

// Chart data interfaces
export interface ChartData {
  chartPrices: number[];
  timeScaleLabels: string[];
  minValue: number;
  maxValue: number;
  priceRangeMin: number;
  priceRangeMax: number;
  yahooChartData: YahooChartResponse | undefined;
  isLoadingYahooData: boolean;
  yahooError: unknown;
}