import React from 'react';
import { useLocation } from 'wouter';
import { motion } from 'framer-motion';
import AppNavigation from '@/components/app-navigation';
import { Button } from '@/components/ui/button';
import { 
  DollarSign, 
  Star, 
  Download, 
  Calculator,
  ChevronLeft
} from 'lucide-react';

export default function BudgetMapPage() {
  const [location, navigate] = useLocation();

  // The levels in the map
  const levels = [
    {
      id: 1,
      icon: <Star className="w-6 h-6 text-white" />,
      color: "bg-yellow-400",
      unlocked: true,
      completed: true,
      name: "Money Basics",
      route: "/quiz/money-basics"
    },
    {
      id: 2,
      icon: <DollarSign className="w-6 h-6 text-white" />,
      color: "bg-green-500",
      unlocked: true,
      completed: false,
      name: "Saving Strategies",
      route: "/quiz/saving-strategies"
    },
    {
      id: 3,
      icon: <Download className="w-6 h-6 text-white" />,
      color: "bg-green-500",
      unlocked: true,
      completed: false,
      name: "Investing 101",
      route: "/quiz/investing-basics"
    },
    {
      id: 4,
      icon: <Calculator className="w-6 h-6 text-white" />,
      color: "bg-green-500",
      unlocked: false,
      completed: false,
      name: "Advanced Budget",
      route: "/quiz/advanced-budget"
    },
    {
      id: 5,
      icon: <DollarSign className="w-6 h-6 text-white" />,
      color: "bg-green-500",
      unlocked: false,
      completed: false,
      name: "Final Challenge",
      route: "/quiz/final-challenge"
    },
  ];

  return (
    <div className="min-h-screen bg-blue-500">
      <AppNavigation />
      
      <div className="container mx-auto px-4 py-6 pb-24">
        {/* Header */}
        <div className="mb-6 flex items-center">
          <button 
            onClick={() => navigate('/learn')}
            className="mr-3 p-2 rounded-full bg-blue-400 hover:bg-blue-600 transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-white" />
          </button>
          <div className="text-white">
            <h2 className="text-sm font-medium opacity-80">SECTION 1, UNIT 1</h2>
            <h1 className="text-3xl font-bold">Understanding money</h1>
          </div>
        </div>
        
        {/* Map content */}
        <div className="relative pb-20">
          {/* Vertical line connecting levels */}
          <div className="absolute left-1/2 top-0 h-full w-1 bg-blue-400 transform -translate-x-1/2 z-0"></div>
          
          {/* Levels */}
          <div className="flex flex-col items-center">
            {levels.map((level, index) => (
              <div 
                key={level.id} 
                className="relative z-10 mb-20 flex flex-col items-center"
              >
                <motion.button 
                  whileHover={level.unlocked ? { scale: 1.1 } : {}}
                  whileTap={level.unlocked ? { scale: 0.95 } : {}}
                  onClick={() => level.unlocked && navigate(level.route)}
                  className={`w-16 h-16 rounded-full ${level.color} ${!level.unlocked && 'opacity-50'} flex items-center justify-center mb-2 relative`}
                  disabled={!level.unlocked}
                >
                  {level.icon}
                  {level.completed && (
                    <div className="absolute top-0 right-0 transform translate-x-1/3 -translate-y-1/3 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                      <Star className="w-4 h-4 text-white" />
                    </div>
                  )}
                  {level.id === 5 && (
                    <div className="absolute -bottom-10 w-12 h-8 bg-yellow-700 rounded-md flex items-center justify-center">
                      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-yellow-700"></div>
                      <div className="w-6 h-3 bg-yellow-500 rounded"></div>
                    </div>
                  )}
                </motion.button>
                {level.id !== 5 && index !== levels.length - 1 && (
                  <div className="text-sm font-medium text-white my-1">{level.name}</div>
                )}
                {level.id === 1 && (
                  <div className="absolute right-1/4 top-0">
                    <img 
                      src="/budget-beast.svg" 
                      alt="Budget Beast character" 
                      className="w-20 h-20"
                    />
                    <div className="flex mt-2 justify-center">
                      <Star className="w-4 h-4 text-yellow-400" />
                      <Star className="w-4 h-4 text-gray-300" />
                      <Star className="w-4 h-4 text-gray-300" />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}