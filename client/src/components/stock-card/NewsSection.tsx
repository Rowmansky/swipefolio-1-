import React from "react";
import { StockData, NewsItem } from "@/lib/stock-data";
import { Newspaper, ExternalLink } from "lucide-react";
import { NewsSectionProps } from "./types";

const NewsSection: React.FC<NewsSectionProps> = ({ stock }) => {
  // Check if news exists
  const hasNews = stock.news && Array.isArray(stock.news) && stock.news.length > 0;

  return (
    <div className="px-4 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Newspaper className="h-4 w-4 text-blue-500" />
        <h3 className="font-semibold text-slate-800 text-sm">Latest News</h3>
      </div>
      
      {hasNews ? (
        <div className="space-y-3">
          {stock.news?.slice(0, 3).map((newsItem: NewsItem, index: number) => (
            <a 
              key={index}
              href={newsItem.url || '#'} 
              target="_blank" 
              rel="noopener noreferrer"
              className="block p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1 pr-2">
                  <h4 className="font-medium text-sm text-slate-800 line-clamp-2">{newsItem.title}</h4>
                  <div className="flex items-center mt-1.5">
                    <span className="text-xs text-slate-500">{newsItem.publisher || 'News Source'}</span>
                    <span className="mx-1.5 text-slate-300">•</span>
                    <span className="text-xs text-slate-500">{newsItem.date || 'Recent'}</span>
                  </div>
                </div>
                <ExternalLink className="h-4 w-4 text-slate-400 mt-0.5 flex-shrink-0" />
              </div>
            </a>
          ))}
        </div>
      ) : (
        <div className="text-center py-6 border border-dashed border-slate-200 rounded-lg">
          <p className="text-sm text-slate-500">No recent news available</p>
        </div>
      )}
    </div>
  );
};

export default NewsSection;