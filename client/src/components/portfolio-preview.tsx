import { motion } from 'framer-motion';
import { useContext } from 'react';
import { PortfolioContext } from '@/contexts/portfolio-context';

export default function PortfolioPreview() {
  // Sample data for illustration
  const sampleStocks = [
    {
      symbol: 'AAPL',
      price: 172.14,
      change: 0.5,
      isPositive: true
    },
    {
      symbol: 'TSLA',
      price: 163.52,
      change: 1.2,
      isPositive: true
    },
    {
      symbol: 'SPY',
      price: 504.18,
      change: 0.3,
      isPositive: true
    }
  ];

  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold text-black mb-2.5">Portfolio</h2>
      <div className="grid grid-cols-3 gap-2.5">
        {sampleStocks.map((stock) => (
          <motion.div
            key={stock.symbol}
            whileHover={{ y: -1 }}
            whileTap={{ scale: 0.98 }}
            className="bg-white rounded-xl p-3 cursor-pointer"
            style={{ 
              boxShadow: '0 2px 6px rgba(0,0,0,0.05)',
              border: '1px solid rgba(0,0,0,0.03)'
            }}
          >
            <div className="flex justify-between items-center mb-1">
              <span className="font-bold text-black">{stock.symbol}</span>
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke={stock.isPositive ? '#22C55E' : '#EF4444'} strokeWidth="2">
                <path d="M3 8L7 4M7 4L11 8M7 4V20M13 16L17 20M17 20L21 16M17 20V4" />
              </svg>
            </div>
            <div className="text-black font-medium">${stock.price.toLocaleString()}</div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}