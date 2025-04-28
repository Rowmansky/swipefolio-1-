import { motion } from 'framer-motion';
import React from 'react';

interface WinItem {
  id: string;
  symbol: string;
  price: string;
  iconType: 'trophy' | 'chart' | 'custom';
  customIcon?: React.ReactNode;
}

interface YourWinsSectionProps {
  wins: WinItem[];
}

export default function YourWinsSection({ wins }: YourWinsSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="mb-6"
    >
      <h2 className="text-xl font-bold text-slate-800 mb-3">Portfolio</h2>
      
      <div className="grid grid-cols-3 gap-3">
        {wins.map((win) => (
          <motion.div
            key={win.id}
            className="bg-white rounded-2xl overflow-hidden shadow-sm p-3 flex flex-col"
            whileHover={{ y: -2, boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.05)' }}
          >
            <div className="flex flex-col">
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-bold text-slate-800">{win.symbol}</h3>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 17L9 11L13 15L21 7" stroke="#4F46E5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M17 7H21V11" stroke="#4F46E5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <p className="text-sm text-slate-600">{win.price}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}