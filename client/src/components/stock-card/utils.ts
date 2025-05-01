import { StockData } from "@/lib/stock-data";
import { getIndustryAverages } from "@/lib/industry-data";

// Helper function to get industry average data 
export const getIndustryAverageData = (stock: StockData, metricType: string) => {
    const industryAvgs = getIndustryAverages(stock.industry);
    if (!industryAvgs) return [];

    if (metricType === 'performance') {
        return [
            { label: "Revenue Growth", value: `${industryAvgs.performance.revenueGrowth}` },
            { label: "Profit Margin", value: `${industryAvgs.performance.profitMargin}` },
            { label: "Return on Capital", value: `${industryAvgs.performance.returnOnCapital}` }
        ];
    } else if (metricType === 'stability') {
        return [
            { label: "Volatility", value: `${industryAvgs.stability.volatility}` },
            { label: "Beta", value: `${industryAvgs.stability.beta}` },
            { label: "Dividend Consistency", value: `${industryAvgs.stability.dividendConsistency}` }
        ];
    } else if (metricType === 'value') {
        return [
            { label: "P/E Ratio", value: `${industryAvgs.value.peRatio}` },
            { label: "P/B Ratio", value: `${industryAvgs.value.pbRatio}` },
            { label: "Dividend Yield", value: `${industryAvgs.value.dividendYield}` }
        ];
    } else if (metricType === 'momentum') {
        return [
            { label: "3-Month Return", value: `${industryAvgs.momentum.threeMonthReturn}` },
            { label: "Relative Performance", value: `${industryAvgs.momentum.relativePerformance}` },
            { label: "RSI", value: `${industryAvgs.momentum.rsi}` }
        ];
    }
    return [];
};