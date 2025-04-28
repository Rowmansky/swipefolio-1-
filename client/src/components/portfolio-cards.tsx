import { motion } from 'framer-motion';

interface PortfolioCardProps {
  ticker: string;
  price: string;
  // In a production app, this would be actual chart data
  // For now, we'll use a static image or a stub
}

const PortfolioCard = ({ ticker, price }: PortfolioCardProps) => (
  <motion.div
    whileHover={{ y: -2 }}
    whileTap={{ scale: 0.98 }}
    className="bg-white rounded-xl p-3 flex flex-col items-start"
    style={{ 
      border: '1px solid rgba(0,0,0,0.03)',
      minWidth: '100px'
    }}
  >
    <div className="font-bold text-black text-lg mb-0.5">{ticker}</div>
    <div className="text-slate-700 text-base mb-2">${price}</div>
    <div className="w-full h-8">
      {/* Simple static sparkline representation */}
      <svg width="100%" height="100%" viewBox="0 0 100 30" preserveAspectRatio="none">
        <path 
          d={ticker === 'AAPL' ? 
              "M0,20 L10,18 L20,22 L30,15 L40,16 L50,10 L60,8 L70,5 L80,7 L90,3 L100,5" : 
              ticker === 'TSLA' ? 
              "M0,15 L10,17 L20,14 L30,16 L40,12 L50,10 L60,8 L70,7 L80,5 L90,3 L100,2" : 
              "M0,20 L10,18 L20,19 L30,17 L40,15 L50,16 L60,14 L70,12 L80,10 L90,8 L100,5"
          }
          fill="none"
          stroke="#4F46E5"
          strokeWidth="2"
        />
      </svg>
    </div>
  </motion.div>
);

export default function PortfolioCards() {
  const portfolioItems = [
    {
      ticker: 'AAPL',
      price: '172.14'
    },
    {
      ticker: 'TSLA',
      price: '163.52'
    },
    {
      ticker: 'SPY',
      price: '504.18'
    }
  ];

  return (
    <div className="mb-4">
      <h2 className="text-xl font-bold text-black mb-2.5">Portfolio</h2>
      <div className="flex space-x-2 overflow-x-auto pb-1">
        {portfolioItems.map((item) => (
          <PortfolioCard
            key={item.ticker}
            ticker={item.ticker}
            price={item.price}
          />
        ))}
      </div>
    </div>
  );
}