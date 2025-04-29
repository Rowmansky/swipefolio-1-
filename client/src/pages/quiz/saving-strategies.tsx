import React from 'react';
import FinanceQuiz, { QuizQuestion } from '@/components/finance-quiz';

const quizQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: "What is the recommended minimum amount for an emergency fund?",
    options: [
      "$100",
      "One month's expenses",
      "Three to six months' expenses",
      "One year's salary"
    ],
    correctAnswer: 2,
    explanation: "Financial experts typically recommend having three to six months' worth of living expenses saved in an emergency fund to cover unexpected events like job loss or medical emergencies."
  },
  {
    id: 2,
    question: "Which saving strategy involves automatically transferring money to savings when you get paid?",
    options: [
      "Impulse saving",
      "Pay yourself first",
      "Zero-based budgeting",
      "The envelope method"
    ],
    correctAnswer: 1,
    explanation: "'Pay yourself first' means prioritizing savings by automatically setting aside a portion of your income for savings before spending on other expenses."
  },
  {
    id: 3,
    question: "What is the 50/30/20 rule in budgeting?",
    options: [
      "50% on housing, 30% on transportation, 20% on food",
      "50% on needs, 30% on wants, 20% on savings",
      "50% on debt repayment, 30% on living expenses, 20% on entertainment",
      "50% saved, 30% invested, 20% spent"
    ],
    correctAnswer: 1,
    explanation: "The 50/30/20 rule suggests allocating 50% of your income to needs (housing, utilities, groceries), 30% to wants (entertainment, dining out), and 20% to savings and debt repayment."
  },
  {
    id: 4,
    question: "Which type of account typically offers the highest interest rate for savings?",
    options: [
      "Regular checking account",
      "Regular savings account",
      "Money market account",
      "Certificate of deposit (CD)"
    ],
    correctAnswer: 3,
    explanation: "Certificates of deposit (CDs) generally offer higher interest rates than regular savings or checking accounts because you commit to leaving your money untouched for a specific period."
  },
  {
    id: 5,
    question: "What is the main benefit of automating your savings?",
    options: [
      "It guarantees a high return on investment",
      "It removes the temptation to spend the money instead",
      "It eliminates all banking fees",
      "It protects your money from inflation"
    ],
    correctAnswer: 1,
    explanation: "Automating savings helps build the habit by removing the decision-making process each time. The money is transferred before you have a chance to spend it, making saving consistent and effortless."
  }
];

export default function SavingStrategiesQuiz() {
  return (
    <FinanceQuiz
      title="Saving Strategies Quiz"
      questions={quizQuestions}
      returnTo="/budget/map"
    />
  );
}