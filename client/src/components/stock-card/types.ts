import { StockData } from "@/lib/stock-data";

// Valid timeframes for stock charts
export type TimeFrame = 
  | '1d'   // One day
  | '5d'   // Five days
  | '1mo'  // One month
  | '3mo'  // Three months
  | '6mo'  // Six months
  | '1y'   // One year
  | '5y'   // Five years
  | 'ytd'  // Year to date
  | 'max'; // Maximum available data

// Props for the StockCardHeader component
export interface StockCardHeaderProps {
  stock: StockData;
  formattedPrice?: string;
  changeValue?: string;
  changePercent?: string;
  isPositive?: boolean;
  onClose?: () => void;
}

// Props for the PriceChart component
export interface PriceChartProps {
  ticker: string;
  activeTimeframe: TimeFrame;
  isLoading?: boolean;
}

// Props for the TimeframeSelector component
export interface TimeframeSelectorProps {
  activeTimeframe?: TimeFrame;
  selectedTimeframe?: TimeFrame;
  timeframes?: TimeFrame[];
  timeframeLabel?: string;
  onTimeframeChange?: (timeframe: TimeFrame) => void;
  onSelect?: (timeframe: TimeFrame) => void;
}

// Props for the MetricsSection component
export interface MetricsSectionProps {
  stock: StockData;
  onMetricClick?: (metricName: string) => void;
}

// Props for the SynopsisSection component
export interface SynopsisSectionProps {
  stock: StockData;
}

// Props for the NewsSection component
export interface NewsSectionProps {
  stock: StockData;
}

// Props for the AnalystRatingsSection component
export interface AnalystRatingsSectionProps {
  stock: StockData;
}

// Props for the ComparativeAnalysisWrapper component
export interface ComparativeAnalysisWrapperProps {
  stock: StockData;
}

// Props for the HistoricalChartWrapper component
export interface HistoricalChartWrapperProps {
  stock: StockData;
}

// Interface for individual stock metrics
export interface StockMetric {
  name: string;
  value: number | string;
  icon?: React.ReactNode;
  color: 'green' | 'red' | 'yellow' | 'blue' | 'purple' | 'neutral';
  description?: string;
  detailLink?: string;
  categoryName?: string;
}

// Interface for chart data points
export interface ChartDataPoint {
  date: string;
  value: number;
  originalValue?: number; // For percentage calculations
}

// Interface for formatted chart data
export interface FormattedChartData {
  ticker: string;
  data: ChartDataPoint[];
  minValue: number;
  maxValue: number;
  startValue: number;
  endValue: number;
  percentChange: number;
  isPositive: boolean;
}