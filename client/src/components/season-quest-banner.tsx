import { motion } from 'framer-motion';
import React from 'react';

interface SeasonQuestBannerProps {
  title: string;
  description: string;
  daysLeft: number;
  onClick: () => void;
}

export default function SeasonQuestBanner({ 
  title, 
  description, 
  daysLeft, 
  onClick 
}: SeasonQuestBannerProps) {
  return (
    <motion.div
      className="relative bg-purple-600 text-white rounded-full p-4 mb-6 overflow-hidden flex items-center justify-between"
      whileHover={{ y: -2, boxShadow: '0 10px 25px -5px rgba(124, 58, 237, 0.5)' }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      <div className="flex items-center z-10">
        <div className="mr-3 text-yellow-300">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 6V8M12 6C9.8 6 8 7.8 8 10H16C16 7.8 14.2 6 12 6ZM12 6C11.2 6 10.5 5.3 10.5 4.5C10.5 3.7 11.2 3 12 3C12.8 3 13.5 3.7 13.5 4.5C13.5 5.3 12.8 6 12 6ZM8 10V12C8 14.2 9.8 16 12 16C14.2 16 16 14.2 16 12V10H8ZM5 8V10H8C8 8.9 8.4 7.9 9 7C8.2 7.3 7.4 7.8 6.9 8.5C6.6 8.2 6.3 8 6 8H5ZM19 8V10H16C16 8.9 15.6 7.9 15 7C15.8 7.3 16.6 7.8 17.1 8.5C17.4 8.2 17.7 8 18 8H19ZM16 12V13.5H19V12H16ZM8 12V13.5H5V12H8ZM12 16V21H7V18H5V21H2V18C2 16.9 2.9 16 4 16H12ZM12 16V21H17V18H19V21H22V18C22 16.9 21.1 16 20 16H12Z" fill="#FFDC34" stroke="#FFDC34" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        
        <div>
          <h2 className="text-xl font-bold">{title}</h2>
          <p className="text-purple-100">{description}</p>
        </div>
      </div>
      
      <div className="bg-purple-500/80 backdrop-blur-sm px-4 py-2 rounded-full text-white font-medium z-10">
        {daysLeft} days left
      </div>
    </motion.div>
  );
}