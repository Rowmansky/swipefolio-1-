import { TimeFrame } from './types';

/**
 * Formats a price number with proper currency formatting
 */
export function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price);
}

/**
 * Determines change value, change percentage, and if it's positive
 */
export function determineChange(change: number, changePercent: number) {
  const isPositive = change >= 0;
  
  // Format change value with sign
  const changeValue = formatPrice(Math.abs(change));
  
  // Format change percentage
  const changePercStr = Math.abs(changePercent).toFixed(2) + '%';
  
  return {
    changeValue: (isPositive ? '+' : '-') + changeValue,
    changePercent: (isPositive ? '+' : '-') + changePercStr,
    isPositive
  };
}

/**
 * Converts a TimeFrame into a human-readable label
 */
export function getTimeframeLabel(timeframe: TimeFrame): string {
  switch (timeframe) {
    case '1d':
      return 'Today';
    case '5d':
      return '5 Days';
    case '1mo':
      return 'Month';
    case '3mo':
      return '3 Months';
    case '6mo':
      return '6 Months';
    case '1y':
      return '1 Year';
    case '5y':
      return '5 Years';
    case 'ytd':
      return 'Year to Date';
    case 'max':
      return 'Max';
    default:
      return timeframe;
  }
}

/**
 * Formats a large number into a more readable format with suffixes (k, M, B)
 */
export function formatLargeNumber(num: number): string {
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(1) + 'B';
  }
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k';
  }
  return num.toString();
}

/**
 * Formats a date in a user-friendly way
 */
export function formatDate(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

/**
 * Truncates a string to a certain length and adds ellipsis if needed
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}