import React from 'react';
import { Link, useLocation } from 'wouter';
import { motion } from 'framer-motion';
import AppNavigation from '@/components/app-navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ChevronRight, DollarSign, BarChart3, User, Clock } from 'lucide-react';

export default function LearnPage() {
  const [location, navigate] = useLocation();

  return (
    <div className="min-h-screen bg-gray-50">
      <AppNavigation />
      
      <div className="container mx-auto px-4 py-6 pb-24">
        {/* Budget Beast Banner */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full bg-blue-600 rounded-xl p-5 text-white flex items-center justify-between mb-8"
        >
          <div>
            <span className="text-sm font-medium opacity-80">Fin</span>
            <h1 className="text-3xl font-bold mb-1">Meet the Budget Beast</h1>
            <Button 
              variant="secondary" 
              className="mt-2 font-semibold bg-yellow-400 hover:bg-yellow-500 text-black border-0"
              onClick={() => navigate('/learn/budget')}
            >
              Start Now
            </Button>
          </div>
          <div className="flex-shrink-0">
            <div className="relative">
              <div className="w-24 h-24 bg-green-500 rounded-lg flex items-center justify-center">
                <div className="w-16 h-16 bg-yellow-400 rounded-full flex items-center justify-center">
                  <span className="text-3xl">$</span>
                </div>
                <div className="absolute bottom-4 rounded-full w-8 h-2 bg-black"></div>
                <div className="absolute top-4 left-4 rounded-full w-4 h-4 bg-white"></div>
                <div className="absolute top-4 right-4 rounded-full w-4 h-4 bg-white"></div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Continue Your Journey */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <h2 className="text-2xl font-bold mb-4">Continue Your Journey</h2>
          
          <Card className="mb-6 border shadow-sm overflow-hidden">
            <div className="flex items-center p-4">
              <div className="bg-yellow-400 w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 mr-4">
                <DollarSign className="w-7 h-7 text-black" />
              </div>
              <div className="flex-grow">
                <h3 className="text-xl font-bold">Investing 101</h3>
                <p className="text-gray-600">Dollar-Cost Averaging</p>
                <div className="flex items-center mt-1 text-gray-500 text-sm">
                  <span className="mr-3">+12 XP</span>
                  <span className="flex items-center"><Clock className="w-3 h-3 mr-1" /> 6 min</span>
                </div>
              </div>
              <Button 
                className="ml-2 rounded-full px-6"
                onClick={() => navigate('/learn/investing-basics')}
              >
                Continue
              </Button>
            </div>
          </Card>
        </motion.div>

        {/* Mastery Map */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">Mastery Map</h2>
            <Link href="/games">
              <ChevronRight className="w-6 h-6 text-gray-400" />
            </Link>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            {/* Investing Circle */}
            <div className="flex flex-col items-center">
              <div className="relative mb-2">
                <div className="bg-green-100 w-20 h-20 rounded-full flex items-center justify-center">
                  <div className="bg-green-500 w-14 h-14 rounded-full flex items-center justify-center">
                    <BarChart3 className="w-8 h-8 text-white" />
                  </div>
                </div>
                <div className="absolute bottom-0 right-0 bg-gray-200 text-gray-800 text-xs font-bold rounded-full px-2 py-1">
                  20%
                </div>
              </div>
              <span className="text-sm font-medium">Investing</span>
            </div>
            
            {/* Budget Circle */}
            <div className="flex flex-col items-center">
              <div className="relative mb-2">
                <div className="w-20 h-20 rounded-full flex items-center justify-center">
                  <div className="w-20 h-20 bg-green-500 rounded-lg flex items-center justify-center">
                    <div className="w-12 h-12 bg-yellow-400 rounded-full flex items-center justify-center">
                      <span className="text-xl">$</span>
                    </div>
                    <div className="absolute top-5 left-5 rounded-full w-3 h-3 bg-white"></div>
                    <div className="absolute top-5 right-5 rounded-full w-3 h-3 bg-white"></div>
                    <div className="absolute bottom-5 rounded-full w-6 h-1 bg-black"></div>
                  </div>
                </div>
                <div className="absolute bottom-0 right-0 bg-gray-200 text-gray-800 text-xs font-bold rounded-full px-2 py-1">
                  20%
                </div>
              </div>
              <span className="text-sm font-medium">Budgeting</span>
            </div>
            
            {/* Credit Circle */}
            <div className="flex flex-col items-center">
              <div className="relative mb-2">
                <div className="bg-blue-100 w-20 h-20 rounded-full flex items-center justify-center">
                  <div className="bg-blue-500 w-14 h-14 rounded-full flex items-center justify-center">
                    <User className="w-8 h-8 text-white" />
                  </div>
                </div>
                <div className="absolute bottom-0 right-0 bg-blue-500 text-white text-xs font-bold rounded-full px-2 py-1">
                  Level 1
                </div>
              </div>
              <span className="text-sm font-medium">Credit</span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}