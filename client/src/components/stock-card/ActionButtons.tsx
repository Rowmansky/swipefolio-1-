import React from "react";
import { X, Check } from "lucide-react";

interface ActionButtonsProps {
  onSkip: () => void;
  onInvest: () => void;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({ onSkip, onInvest }) => {
  return (
    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-white via-white to-transparent pt-12 pb-5">
      {/* Shadow/gradient edge */}
      <div className="h-px w-full bg-slate-100 mb-4"></div>
      
      <div className="px-6 flex justify-between">
        <button
          onClick={onSkip}
          className="w-[46%] py-3 rounded-xl bg-slate-100 text-slate-700 font-medium text-sm flex items-center justify-center shadow-sm hover:bg-slate-200 active:bg-slate-300 active:scale-[0.98] transition-all focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2"
        >
          <X className="mr-2" size={18} /> {/* Using X instead of ChevronLeft for skip */}
          Skip
        </button>
        
        <button
          onClick={onInvest}
          className="w-[46%] py-3 rounded-xl bg-blue-500 text-white font-medium text-sm flex items-center justify-center shadow-sm hover:bg-blue-600 active:bg-blue-700 active:scale-[0.98] transition-all focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
        >
          <Check className="mr-2" size={18} /> {/* Using Check instead of DollarSign for buy */}
          Invest
        </button>
      </div>
    </div>
  );
};

export default ActionButtons;