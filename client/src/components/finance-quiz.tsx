import React, { useState } from 'react';
import { useLocation } from 'wouter';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { X, ChevronLeft, CheckCircle2, XCircle } from 'lucide-react';
import AppNavigation from '@/components/app-navigation';

export interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctAnswer: number; // Index of the correct answer
  explanation?: string;
}

interface FinanceQuizProps {
  title: string;
  questions: QuizQuestion[];
  returnTo: string;
}

export default function FinanceQuiz({ title, questions, returnTo }: FinanceQuizProps) {
  const [location, navigate] = useLocation();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [isAnswerChecked, setIsAnswerChecked] = useState(false);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [isQuizComplete, setIsQuizComplete] = useState(false);
  
  const currentQuestion = questions[currentQuestionIndex];
  
  const checkAnswer = (optionIndex: number) => {
    setSelectedAnswer(optionIndex);
    setIsAnswerChecked(true);
    
    if (optionIndex === currentQuestion.correctAnswer) {
      setCorrectAnswers(correctAnswers + 1);
    }
  };
  
  const nextQuestion = () => {
    setSelectedAnswer(null);
    setIsAnswerChecked(false);
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      setIsQuizComplete(true);
    }
  };
  
  const restartQuiz = () => {
    setCurrentQuestionIndex(0);
    setSelectedAnswer(null);
    setIsAnswerChecked(false);
    setCorrectAnswers(0);
    setIsQuizComplete(false);
  };
  
  // Calculate progress
  const progress = ((currentQuestionIndex + (isAnswerChecked ? 1 : 0)) / questions.length) * 100;
  
  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <AppNavigation />
      
      <div className="container mx-auto px-4 py-6">
        {/* Header with Back Button */}
        <div className="mb-6 flex items-center">
          <button 
            onClick={() => navigate(returnTo)}
            className="mr-3 p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>
          <h1 className="text-xl font-bold">{title}</h1>
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 h-2 rounded-full mb-8">
          <div 
            className="bg-green-500 h-2 rounded-full transition-all duration-300" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        
        {!isQuizComplete ? (
          <div>
            {/* Question */}
            <Card className="mb-6 p-6">
              <h2 className="text-lg font-bold mb-4">{currentQuestion.question}</h2>
              
              {/* Options */}
              <div className="space-y-3">
                {currentQuestion.options.map((option, index) => (
                  <motion.button
                    key={index}
                    className={`w-full p-4 rounded-xl border text-left relative ${
                      selectedAnswer === index && isAnswerChecked
                        ? index === currentQuestion.correctAnswer
                          ? 'bg-green-50 border-green-500'
                          : 'bg-red-50 border-red-500'
                        : selectedAnswer === index
                        ? 'bg-blue-50 border-blue-500'
                        : 'border-gray-200 hover:border-blue-500'
                    } ${
                      isAnswerChecked && index !== selectedAnswer 
                      ? 'opacity-50' 
                      : 'opacity-100'
                    }`}
                    onClick={() => !isAnswerChecked && checkAnswer(index)}
                    disabled={isAnswerChecked}
                    whileHover={!isAnswerChecked ? { scale: 1.02 } : {}}
                    whileTap={!isAnswerChecked ? { scale: 0.98 } : {}}
                  >
                    <span>{option}</span>
                    
                    {isAnswerChecked && selectedAnswer === index && (
                      <span className="absolute right-4 top-1/2 transform -translate-y-1/2">
                        {index === currentQuestion.correctAnswer ? (
                          <CheckCircle2 className="w-6 h-6 text-green-500" />
                        ) : (
                          <XCircle className="w-6 h-6 text-red-500" />
                        )}
                      </span>
                    )}
                  </motion.button>
                ))}
              </div>
              
              {/* Explanation if answer is checked */}
              {isAnswerChecked && currentQuestion.explanation && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg text-blue-800">
                  <p className="font-medium">Explanation:</p>
                  <p>{currentQuestion.explanation}</p>
                </div>
              )}
            </Card>
            
            {/* Next Button */}
            {isAnswerChecked && (
              <Button 
                className="w-full py-6 text-lg font-medium"
                onClick={nextQuestion}
              >
                {currentQuestionIndex < questions.length - 1 ? 'Continue' : 'Finish Quiz'}
              </Button>
            )}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <h2 className="text-2xl font-bold mb-4">Quiz Complete!</h2>
            <p className="text-lg mb-6">
              You scored <span className="font-bold">{correctAnswers}</span> out of{" "}
              <span className="font-bold">{questions.length}</span> questions.
            </p>
            
            <div className="space-y-4">
              <Button
                className="w-full py-6 text-lg"
                onClick={() => navigate(returnTo)}
              >
                Return to Map
              </Button>
              
              <Button
                variant="outline"
                className="w-full py-6 text-lg"
                onClick={restartQuiz}
              >
                Try Again
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}