import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import type { Stack } from '@shared/schema';
import StackCard from './ui/stack-card';

// Enhanced Stack type with imageUrl
interface EnhancedStack extends Stack {
  imageUrl?: string;
}

interface HorizontalStacksSliderProps {
  stacks: Stack[];
  onStackClick: (stackId: number) => void;
}

export default function HorizontalStacksSlider({ stacks, onStackClick }: HorizontalStacksSliderProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  // Industry names and images with vibrant mobile-friendly imagery
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
    "Energy": { 
      name: "Energy Innovators", 
      image: "https://images.unsplash.com/photo-1591964006776-90d33e597522?q=80&w=580&auto=format&fit=crop" 
    },
    "Automotive": { 
      name: "Mobility Disruptors", 
      image: "https://images.unsplash.com/photo-1533106418989-88406c7cc8ca?q=80&w=580&auto=format&fit=crop" 
    },
    "Fintech": { 
      name: "Banking Disruptors", 
      image: "https://images.unsplash.com/photo-1563013544-824ae1b704d3?q=80&w=580&auto=format&fit=crop" 
    },
    "ESG": { 
      name: "Green Giants", 
      image: "Profiles/green.png" 
    },
    "Industrials": { 
      name: "Industrial Leaders", 
      image: "https://images.unsplash.com/photo-1516937941344-00b4e0337589?q=80&w=580&auto=format&fit=crop" 
    },
    "Communication": { 
      name: "Media Movers", 
      image: "https://images.unsplash.com/photo-1516321497487-e288fb19713f?q=80&w=580&auto=format&fit=crop" 
    },
    "Technology": {
      name: "Tech Titans",
      image: "Profiles/Industry_Tech.png"
    },
    "Investing": {
      name: "Investment Essentials",
      image: "https://images.unsplash.com/photo-1621951753163-ee63e7fc0743?q=80&w=580&auto=format&fit=crop"
    },
    "Cryptocurrency": {
      name: "Crypto Explorer",
      image: "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?q=80&w=580&auto=format&fit=crop"
    }
  };

  // Get details for a given industry
  const getIndustryDetails = (industry: string) => {
    return industryDetails[industry] || { 
      name: industry, 
      image: "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?q=80&w=580&auto=format&fit=crop" 
    };
  };

  // Enhance stack data with industry details
  const enhancedStacks: EnhancedStack[] = stacks.map(stack => {
    const details = getIndustryDetails(stack.industry);
    return {
      ...stack,
      imageUrl: details.image
    };
  });

  // Handle scroll shadows
  const handleScroll = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setShowLeftArrow(scrollLeft > 10);
      setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;
    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
      return () => scrollContainer.removeEventListener('scroll', handleScroll);
    }
  }, []);

  // Scroll functions
  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: -300, behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: 300, behavior: 'smooth' });
    }
  };

  // Ensure there are enough stacks for our scrolling interface
  const displayStacks = enhancedStacks.length >= 3 ? enhancedStacks : [...enhancedStacks, ...enhancedStacks];

  // Add a global style to hide scrollbars but keep functionality
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      .hide-scrollbar::-webkit-scrollbar {
        display: none;
      }
      .hide-scrollbar {
        -ms-overflow-style: none;
        scrollbar-width: none;
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  return (
    <div className="mb-6 relative">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xl font-bold text-slate-800">Explore Topics</h2>
        <div className="flex space-x-2">
          {showLeftArrow && (
            <motion.button
              onClick={scrollLeft}
              className="w-8 h-8 rounded-full bg-white border border-slate-200 shadow-sm flex items-center justify-center"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ChevronLeft className="h-4 w-4 text-slate-600" />
            </motion.button>
          )}
          {showRightArrow && (
            <motion.button
              onClick={scrollRight}
              className="w-8 h-8 rounded-full bg-white border border-slate-200 shadow-sm flex items-center justify-center"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ChevronRight className="h-4 w-4 text-slate-600" />
            </motion.button>
          )}
        </div>
      </div>

      {/* Background stripe */}
      <div className="absolute left-0 right-0 h-[120px] bg-slate-100/70 top-1/2 -translate-y-1/2 -z-10 rounded-xl"></div>
      
      {/* Scrollable container */}
      <div 
        ref={scrollContainerRef}
        className="flex overflow-x-auto pb-4 pt-2 px-1 -mx-1 hide-scrollbar"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        <div className="flex space-x-4 px-1">
          {displayStacks.map((stack) => (
            <div key={stack.id} className="flex-shrink-0 w-72">
              <StackCard
                stack={stack}
                onClick={onStackClick}
                imageUrl={stack.imageUrl}
                category={stack.industry}
              />
            </div>
          ))}
        </div>
      </div>
      
      {/* Shadow indicators */}
      {showLeftArrow && (
        <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-white to-transparent pointer-events-none" />
      )}
      {showRightArrow && (
        <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-white to-transparent pointer-events-none" />
      )}
    </div>
  );
}