import React from 'react';
import FinanceQuiz, { QuizQuestion } from '@/components/finance-quiz';

const quizQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: "What is the main purpose of a budget?",
    options: [
      "To restrict your spending completely",
      "To track and plan your income and expenses",
      "To eliminate all debt immediately",
      "To invest all your money"
    ],
    correctAnswer: 1,
    explanation: "A budget is a financial planning tool that helps you track your income and plan your expenses to meet your financial goals."
  },
  {
    id: 2,
    question: "Which of these is a liquid asset?",
    options: [
      "A house",
      "A car",
      "A savings account",
      "Jewelry"
    ],
    correctAnswer: 2,
    explanation: "Liquid assets can be quickly converted to cash with minimal loss of value. Savings accounts are highly liquid, while houses, cars, and jewelry typically take time to sell."
  },
  {
    id: 3,
    question: "What does the term 'net worth' mean?",
    options: [
      "Your annual salary",
      "Your total assets minus your total liabilities",
      "The total amount in your checking account",
      "The value of your investments"
    ],
    correctAnswer: 1,
    explanation: "Net worth is calculated by subtracting all your liabilities (debts) from your total assets. It provides a snapshot of your financial health."
  },
  {
    id: 4,
    question: "Which of these is NOT typically a fixed expense?",
    options: [
      "Mortgage payment",
      "Car insurance",
      "Grocery spending",
      "Internet bill"
    ],
    correctAnswer: 2,
    explanation: "Fixed expenses remain the same each month, like mortgage, insurance, and subscriptions. Grocery spending typically varies month to month, making it a variable expense."
  },
  {
    id: 5,
    question: "What is compound interest?",
    options: [
      "Interest you pay on loans",
      "Interest earned only on your principal investment",
      "Interest earned on both principal and accumulated interest",
      "The interest rate set by the Federal Reserve"
    ],
    correctAnswer: 2,
    explanation: "Compound interest is when you earn interest not just on your initial investment (principal), but also on any interest previously accumulated. It's often described as 'interest on interest.'"
  }
];

export default function MoneyBasicsQuiz() {
  return (
    <FinanceQuiz
      title="Money Basics Quiz"
      questions={quizQuestions}
      returnTo="/budget/map"
    />
  );
}