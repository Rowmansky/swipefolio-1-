import React from 'react';
import { useLocation } from 'wouter';
import { motion } from 'framer-motion';
import { ChevronLeft, DollarSign, PiggyBank, BarChart3, Shield, Wallet, CreditCard } from 'lucide-react';
import AppNavigation from '@/components/app-navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export default function BudgetMapPage() {
  const [_, navigate] = useLocation();
  
  // Define the mini-games
  const miniGames = [
    {
      id: 'money-basics',
      title: 'Money Basics',
      description: 'Learn essential financial terminology and concepts',
      icon: <DollarSign className="w-8 h-8 text-white" />,
      color: 'bg-green-500',
      route: '/quiz/money-basics',
      available: true,
    },
    {
      id: 'saving-strategies',
      title: 'Saving Strategies',
      description: 'Master techniques to grow your savings',
      icon: <PiggyBank className="w-8 h-8 text-white" />,
      color: 'bg-blue-500',
      route: '/quiz/saving-strategies',
      available: true,
    },
    {
      id: 'investing-basics',
      title: 'Investing 101',
      description: 'Understand basic investment principles',
      icon: <BarChart3 className="w-8 h-8 text-white" />,
      color: 'bg-purple-500',
      route: '/quiz/investing-basics',
      available: true,
    },
    {
      id: 'risk-management',
      title: 'Risk Management',
      description: 'Learn to protect your financial future',
      icon: <Shield className="w-8 h-8 text-white" />,
      color: 'bg-red-500',
      route: '/quiz/risk-management',
      available: false,
    },
    {
      id: 'budgeting-tools',
      title: 'Budgeting Tools',
      description: 'Explore apps and methods for tracking finances',
      icon: <Wallet className="w-8 h-8 text-white" />,
      color: 'bg-yellow-500',
      route: '/quiz/budgeting-tools',
      available: false,
    },
    {
      id: 'credit-mastery',
      title: 'Credit Mastery',
      description: 'Build and maintain good credit',
      icon: <CreditCard className="w-8 h-8 text-white" />,
      color: 'bg-indigo-500',
      route: '/quiz/credit-mastery',
      available: false,
    },
  ];
  
  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <AppNavigation />
      
      <div className="container mx-auto px-4 py-6">
        {/* Header with Back Button */}
        <div className="mb-6 flex items-center">
          <button 
            onClick={() => navigate('/learn')}
            className="mr-3 p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>
          <h1 className="text-xl font-bold">Budget Beast Mastery Map</h1>
        </div>
        
        {/* Character Banner */}
        <Card className="mb-6 p-4 bg-gradient-to-r from-yellow-400 to-yellow-300 border-none">
          <div className="flex items-center">
            <img 
              src="/budget-beast.svg" 
              alt="Budget Beast character" 
              className="w-24 h-24 mr-4"
            />
            <div>
              <h2 className="text-lg font-bold text-black">Welcome to the Map!</h2>
              <p className="text-black/80">Complete quizzes to master your financial skills</p>
            </div>
          </div>
        </Card>
        
        {/* Game Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          {miniGames.map((game, index) => (
            <motion.div
              key={game.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card 
                className={`p-6 border ${!game.available ? 'opacity-70' : ''}`}
              >
                <div className="flex items-start">
                  <div className={`${game.color} w-12 h-12 rounded-lg flex items-center justify-center mr-4 flex-shrink-0`}>
                    {game.icon}
                  </div>
                  <div className="flex-grow">
                    <h3 className="text-lg font-bold mb-1">{game.title}</h3>
                    <p className="text-sm text-gray-600 mb-3">{game.description}</p>
                    <Button
                      variant={game.available ? "default" : "outline"}
                      className={game.available ? "" : "opacity-50 cursor-not-allowed"}
                      onClick={() => game.available && navigate(game.route)}
                      disabled={!game.available}
                    >
                      {game.available ? 'Start Quiz' : 'Coming Soon'}
                    </Button>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
        
        {/* Progress Overview */}
        <Card className="mb-4 p-4 border">
          <h3 className="text-lg font-bold mb-3">Your Progress</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Money Basics</span>
                <span className="font-medium">0/5 completed</span>
              </div>
              <div className="w-full bg-gray-200 h-2 rounded-full">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '0%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Saving Strategies</span>
                <span className="font-medium">0/5 completed</span>
              </div>
              <div className="w-full bg-gray-200 h-2 rounded-full">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '0%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Investing 101</span>
                <span className="font-medium">0/5 completed</span>
              </div>
              <div className="w-full bg-gray-200 h-2 rounded-full">
                <div className="bg-purple-500 h-2 rounded-full" style={{ width: '0%' }}></div>
              </div>
            </div>
          </div>
        </Card>
        
        {/* Return to Main Learning Page */}
        <Button
          variant="outline"
          className="w-full"
          onClick={() => navigate('/learn')}
        >
          Return to Learning Hub
        </Button>
      </div>
    </div>
  );
}