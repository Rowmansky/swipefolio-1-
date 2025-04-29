import React from 'react';
import FinanceQuiz, { QuizQuestion } from '@/components/finance-quiz';

const quizQuestions: QuizQuestion[] = [
  {
    id: 1,
    question: "What is a stock?",
    options: [
      "A loan you give to a company",
      "A partial ownership in a company",
      "A government-backed investment",
      "A type of savings account"
    ],
    correctAnswer: 1,
    explanation: "When you purchase a stock, you're buying a small piece of ownership (share) in a company. As a shareholder, you may benefit from the company's growth through price appreciation and dividends."
  },
  {
    id: 2,
    question: "What is diversification in investing?",
    options: [
      "Investing all your money in one promising company",
      "Buying only international stocks",
      "Spreading investments across different assets to reduce risk",
      "Changing your investment strategy frequently"
    ],
    correctAnswer: 2,
    explanation: "Diversification is the strategy of investing in a variety of assets to reduce risk. When your investments are spread across different asset classes, sectors, or geographical regions, losses in one area may be offset by gains in another."
  },
  {
    id: 3,
    question: "What is dollar-cost averaging?",
    options: [
      "Converting foreign currency into dollars for investing",
      "Investing a fixed amount regularly regardless of market price",
      "Waiting for the market to bottom out before investing",
      "Investing only in assets priced under one dollar"
    ],
    correctAnswer: 1,
    explanation: "Dollar-cost averaging is the practice of investing a fixed amount at regular intervals, regardless of market prices. This approach helps reduce the impact of market volatility and avoid the pitfalls of trying to time the market."
  },
  {
    id: 4,
    question: "Which of these is generally considered the highest risk investment?",
    options: [
      "Government bonds",
      "Certificate of deposit (CD)",
      "Blue-chip stocks",
      "Cryptocurrency"
    ],
    correctAnswer: 3,
    explanation: "Cryptocurrencies like Bitcoin are considered high-risk investments due to their significant price volatility, relatively short history, and lack of regulation compared to traditional investments like government bonds or established stocks."
  },
  {
    id: 5,
    question: "What is an index fund?",
    options: [
      "A fund that only invests in new companies",
      "A type of actively managed fund that tries to beat the market",
      "A passively managed fund that tracks a market index",
      "A government-run investment program"
    ],
    correctAnswer: 2,
    explanation: "An index fund is a type of mutual fund or ETF that aims to replicate the performance of a specific market index (like the S&P 500). They're typically passively managed, which often results in lower fees compared to actively managed funds."
  }
];

export default function InvestingBasicsQuiz() {
  return (
    <FinanceQuiz
      title="Investing 101 Quiz"
      questions={quizQuestions}
      returnTo="/budget/map"
    />
  );
}