import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useLocation } from 'wouter';
import { ChevronRight, ChevronLeft } from 'lucide-react';
import type { Stack } from '@shared/schema';
import { useQueryClient } from '@tanstack/react-query';
import { fetchStockChartData, timeFrameToRange } from '@/lib/yahoo-finance-client';
import { getIndustryStocks } from '@/lib/stock-data';

// Extended Stack type with imageUrl
interface ExtendedStack extends Stack {
  imageUrl?: string;
}

interface StackCardProps {
  stack: ExtendedStack;
  onClick: (id: number) => void;
}

// Individual stack card component - iOS style
const StackCard = ({ stack, onClick }: StackCardProps) => (
  <motion.div
    whileHover={{ y: -5, scale: 1.02, boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)' }}
    whileTap={{ scale: 0.98 }}
    onClick={() => onClick(stack.id)}
    className="flex-shrink-0 w-56 bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden mr-2.5"
    style={{ boxShadow: '0 4px 12px -2px rgba(0,0,0,0.05)' }}
  >
    <div className="h-20 flex items-center justify-center relative overflow-hidden"
      style={{ 
        background: 'linear-gradient(135deg, #4F46E5, #4338CA)',
      }}
    >
      {stack.imageUrl && (
        <img 
          src={stack.imageUrl} 
          alt={stack.title} 
          className="absolute inset-0 w-full h-full object-cover opacity-25 mix-blend-overlay"
        />
      )}
      <h3 className="text-white font-bold text-lg z-10 px-4 text-center leading-snug tracking-tight">{stack.title}</h3>
    </div>
    <div className="p-3">
      <p className="text-slate-600 text-xs mb-2 line-clamp-2 leading-snug">{stack.description}</p>
      <div className="flex justify-between items-center">
        <span className="text-xs text-slate-500 font-medium">{stack.cardCount} cards</span>
        <span className="text-xs font-medium px-2 py-0.5 rounded-full"
          style={{ backgroundColor: 'rgba(79, 70, 229, 0.1)', color: '#4F46E5' }}>{stack.industry}</span>
      </div>
    </div>
  </motion.div>
);

interface SwipeableStacksProps {
  stacks: Stack[];
}

export default function SwipeableStacks({ stacks }: SwipeableStacksProps) {
  // Industry details with images
  const industryDetails: Record<string, { name: string, image: string }> = {
    "Tech": { 
      name: "Tech Titans", 
      image: "Profiles/Industry_Tech.png" 
    },
    "Healthcare": { 
      name: "Med-Tech Innovators", 
      image: "Profiles/savelives.png"
    },
    "Consumer": { 
      name: "Retail Champions", 
      image: "Profiles/Industry_Retail.png"
    },
    "Retail": { 
      name: "Retail Champions", 
      image: "Profiles/Industry_Retail.png"
    },
    "Real Estate": { 
      name: "Property Players", 
      image: "Profiles/Industry_RealEstate.png" 
    },
    "ESG": { 
      name: "Green Giants", 
      image: "Profiles/green.png" 
    }
  };

  // Add imageUrl to stacks
  const enhancedStacks = stacks.map(stack => {
    const details = industryDetails[stack.industry] || { 
      name: stack.industry, 
      image: "Profiles/Industry_Tech.png" // default image
    };
    
    return {
      ...stack,
      imageUrl: details.image
    } as ExtendedStack;
  });
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [_, setLocation] = useLocation();
  const queryClient = useQueryClient();
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  // Function to check scroll position and update arrows
  const checkScrollPosition = () => {
    const container = scrollContainerRef.current;
    if (container) {
      setShowLeftArrow(container.scrollLeft > 20);
      setShowRightArrow(container.scrollLeft < container.scrollWidth - container.clientWidth - 20);
    }
  };

  // Add scroll listener
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (container) {
      container.addEventListener('scroll', checkScrollPosition);
      return () => container.removeEventListener('scroll', checkScrollPosition);
    }
  }, []);

  // Handle scroll buttons
  const handleScroll = (direction: 'left' | 'right') => {
    const container = scrollContainerRef.current;
    if (container) {
      const scrollAmount = 300; // Adjust scroll amount as needed
      const targetPosition = container.scrollLeft + (direction === 'left' ? -scrollAmount : scrollAmount);
      container.scrollTo({
        left: targetPosition,
        behavior: 'smooth'
      });
    }
  };

  // This function preloads the chart data for the first stock in the stack
  const preloadStackData = async (industry: string) => {
    try {
      // Get the stocks for this industry
      const stocks = getIndustryStocks(industry);
      
      // If we have stocks, preload the data for the first few stocks
      if (stocks && stocks.length > 0) {
        // Preload first stock (the one that will be shown immediately)
        const firstStock = stocks[0];
        const firstSymbol = firstStock.ticker;
        
        // Get range for default timeframe (1Y is most commonly viewed)
        const defaultTimeframes = ["1Y", "1D"]; // Preload both 1Y and 1D data
        
        for (const timeframe of defaultTimeframes) {
          const range = timeFrameToRange[timeframe];
          
          // Prefetch first stock data and store in cache with higher priority
          const queryKey = ['/api/yahoo-finance/chart', firstSymbol, range];
          await queryClient.prefetchQuery({
            queryKey,
            queryFn: async () => fetchStockChartData(firstSymbol, range),
            staleTime: 5 * 60 * 1000, // 5 minutes
          });
        }
      }
    } catch (error) {
      console.error(`Error preloading chart data:`, error);
    }
  };

  const handleStackClick = (stackId: number) => {
    // Find the stack that was clicked
    const clickedStack = stacks.find(stack => stack.id === stackId);
    
    if (clickedStack?.industry) {
      // Start preloading the chart data for the first stock in this industry
      preloadStackData(clickedStack.industry);
    }
    
    // Navigate to the stack detail page
    setLocation(`/stock/${stackId}`);
  };

  return (
    <div className="mb-4 relative">
      <h2 className="text-xl font-bold text-slate-900 mb-3">Learning Stacks</h2>
      
      <div className="bg-slate-100 rounded-xl p-3.5 relative"
        style={{ backgroundColor: '#F1F5F9' }}>
        {/* Left scroll button */}
        {showLeftArrow && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute left-2 top-1/2 -translate-y-1/2 z-10 bg-white w-8 h-8 rounded-full shadow-md flex items-center justify-center"
            style={{ boxShadow: '0 4px 10px rgba(0,0,0,0.1)' }}
            onClick={() => handleScroll('left')}
          >
            <ChevronLeft className="w-5 h-5 text-slate-700" />
          </motion.button>
        )}
        
        {/* Scrollable container */}
        <div 
          ref={scrollContainerRef}
          className="flex overflow-x-auto py-2 scrollbar-hide gap-2.5"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {enhancedStacks.map(stack => (
            <StackCard 
              key={stack.id} 
              stack={stack} 
              onClick={handleStackClick} 
            />
          ))}
        </div>
        
        {/* Right scroll button */}
        {showRightArrow && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute right-2 top-1/2 -translate-y-1/2 z-10 bg-white w-8 h-8 rounded-full shadow-md flex items-center justify-center"
            style={{ boxShadow: '0 4px 10px rgba(0,0,0,0.1)' }}
            onClick={() => handleScroll('right')}
          >
            <ChevronRight className="w-5 h-5 text-slate-700" />
          </motion.button>
        )}
      </div>
    </div>
  );
}