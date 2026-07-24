'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { HiClock, HiCheck, HiX, HiArrowLeft, HiFlag } from 'react-icons/hi';

interface Question {
  id: number;
  question: string;
  options: string[];
  correct: number;
}

const mockQuiz: {
  title: string;
  course: string;
  timeLimit: number;
  passingScore: number;
  questions: Question[];
} = {
  title: 'React Fundamentals Quiz',
  course: 'Advanced React Development',
  timeLimit: 15,
  passingScore: 70,
  questions: [
    { id: 1, question: 'What hook is used for side effects in React?', options: ['useState', 'useEffect', 'useContext', 'useReducer'], correct: 1 },
    { id: 2, question: 'What does JSX stand for?', options: ['JavaScript XML', 'Java Syntax Extension', 'JSON XML', 'None of the above'], correct: 0 },
    { id: 3, question: 'Which method is used to create a React app?', options: ['create-react-app', 'init-react', 'new-react', 'react-start'], correct: 0 },
    { id: 4, question: 'What is the virtual DOM?', options: ['A direct copy of the real DOM', 'A lightweight representation of the DOM', 'A browser API', 'A JavaScript library'], correct: 1 },
    { id: 5, question: 'Which hook is used for state management?', options: ['useEffect', 'useState', 'useCallback', 'useMemo'], correct: 1 },
    { id: 6, question: 'What is a React component?', options: ['A function that returns HTML', 'A class that returns JSX', 'A reusable piece of UI', 'All of the above'], correct: 3 },
    { id: 7, question: 'What does the key prop do in lists?', options: ['Adds styling', 'Helps React identify items', 'Sets the item order', 'None of the above'], correct: 1 },
    { id: 8, question: 'What is the purpose of useMemo?', options: ['Memoize values', 'Memoize functions', 'Handle side effects', 'Manage state'], correct: 0 },
    { id: 9, question: 'What is React.StrictMode?', options: ['A production mode', 'A development tool for highlighting problems', 'A build tool', 'A testing framework'], correct: 1 },
    { id: 10, question: 'Which of the following is NOT a React lifecycle method?', options: ['componentDidMount', 'componentWillUnmount', 'componentShouldUpdate', 'componentDidUpdate'], correct: 2 },
  ],
};

type QuizState = 'not_started' | 'in_progress' | 'completed';

export default function QuizPage() {
  const [quizState, setQuizState] = useState<QuizState>('not_started');
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [timeLeft, setTimeLeft] = useState(mockQuiz.timeLimit * 60);
  const [flaggedQuestions, setFlaggedQuestions] = useState<number[]>([]);

  const score = Object.entries(answers).reduce((acc, [qId, answer]) =>
    acc + (mockQuiz.questions[Number(qId)]?.correct === answer ? 1 : 0), 0);
  const percentage = Math.round((score / mockQuiz.questions.length) * 100);
  const passed = percentage >= mockQuiz.passingScore;

  // Timer
  useEffect(() => {
    if (quizState !== 'in_progress') return;
    if (timeLeft <= 0) { setQuizState('completed'); return; }
    const timer = setInterval(() => setTimeLeft((t) => t - 1), 1000);
    return () => clearInterval(timer);
  }, [quizState, timeLeft]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const handleAnswer = (optionIndex: number) => {
    setAnswers({ ...answers, [currentQuestion]: optionIndex });
  };

  const toggleFlag = () => {
    setFlaggedQuestions((prev) =>
      prev.includes(currentQuestion)
        ? prev.filter((q) => q !== currentQuestion)
        : [...prev, currentQuestion]
    );
  };

  const questions = mockQuiz.questions;

  return (
    <div className="min-h-screen bg-gray-50">
      {quizState === 'not_started' && (
        <div className="max-w-2xl mx-auto px-4 py-16">
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 text-center">
            <div className="w-16 h-16 bg-[rgb(var(--ctc-primary))]/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <HiClock className="w-8 h-8 text-[rgb(var(--ctc-primary))]" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{mockQuiz.title}</h1>
            <p className="text-gray-500 mb-2">Course: {mockQuiz.course}</p>
            <div className="flex justify-center gap-6 mt-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{questions.length}</div>
                <div className="text-xs text-gray-500">Questions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{mockQuiz.timeLimit}min</div>
                <div className="text-xs text-gray-500">Time Limit</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{mockQuiz.passingScore}%</div>
                <div className="text-xs text-gray-500">Pass Score</div>
              </div>
            </div>
            <button onClick={() => setQuizState('in_progress')} className="btn-primary">
              Start Quiz
            </button>
          </div>
        </div>
      )}

      {quizState === 'in_progress' && (
        <div className="max-w-3xl mx-auto px-4 py-6">
          {/* Top Bar */}
          <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link href="/student-dashboard" className="text-gray-400 hover:text-gray-600">
                <HiArrowLeft className="w-5 h-5" />
              </Link>
              <span className="text-sm font-medium text-gray-900">
                Question {currentQuestion + 1} of {questions.length}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={toggleFlag}
                className={`flex items-center gap-1 text-sm transition-colors ${flaggedQuestions.includes(currentQuestion) ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'}`}
              >
                <HiFlag className="w-4 h-4" />
                Flag
              </button>
              <div className={`flex items-center gap-1 text-sm font-medium ${timeLeft < 60 ? 'text-red-600' : 'text-gray-700'}`}>
                <HiClock className="w-4 h-4" />
                {formatTime(timeLeft)}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Question Navigation */}
            <div className="lg:col-span-1 order-2 lg:order-1">
              <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 sticky top-24">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Questions</h3>
                <div className="grid grid-cols-5 gap-2">
                  {questions.map((_, i) => (
                    <button
                      key={i}
                      onClick={() => setCurrentQuestion(i)}
                      className={`w-9 h-9 rounded-lg text-xs font-medium transition-all ${
                        i === currentQuestion
                          ? 'bg-[rgb(var(--ctc-primary))] text-white'
                          : answers[i] !== undefined
                          ? 'bg-green-100 text-green-700'
                          : flaggedQuestions.includes(i)
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {i + 1}
                    </button>
                  ))}
                </div>
                <div className="mt-4 space-y-1">
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span className="w-3 h-3 rounded bg-green-100" /> Answered
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span className="w-3 h-3 rounded bg-yellow-100" /> Flagged
                  </div>
                </div>
              </div>
            </div>

            {/* Question */}
            <div className="lg:col-span-3 order-1 lg:order-2">
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <p className="text-xs text-gray-500 mb-2">Question {currentQuestion + 1} of {questions.length}</p>
                <h2 className="text-lg font-semibold text-gray-900 mb-6">{questions[currentQuestion].question}</h2>

                <div className="space-y-3">
                  {questions[currentQuestion].options.map((option, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleAnswer(idx)}
                      className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                        answers[currentQuestion] === idx
                          ? 'border-[rgb(var(--ctc-primary))] bg-[rgb(var(--ctc-primary))]/5 text-[rgb(var(--ctc-primary-dark))]'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <span className="font-medium">{String.fromCharCode(65 + idx)}.</span> {option}
                    </button>
                  ))}
                </div>

                <div className="flex justify-between mt-8">
                  <button
                    onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                    disabled={currentQuestion === 0}
                    className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  {currentQuestion < questions.length - 1 ? (
                    <button
                      onClick={() => setCurrentQuestion(currentQuestion + 1)}
                      className="btn-primary"
                    >
                      Next
                    </button>
                  ) : (
                    <button
                      onClick={() => setQuizState('completed')}
                      className="btn-primary"
                    >
                      Submit Quiz
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {quizState === 'completed' && (
        <div className="max-w-2xl mx-auto px-4 py-16">
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 text-center">
            <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 ${
              passed ? 'bg-green-100' : 'bg-red-100'
            }`}>
              {passed ? (
                <HiCheck className="w-10 h-10 text-green-600" />
              ) : (
                <HiX className="w-10 h-10 text-red-600" />
              )}
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {passed ? 'Congratulations!' : 'Keep Practicing!'}
            </h2>
            <p className="text-gray-500 mb-6">
              {passed
                ? 'You passed the quiz! You\'re making great progress.'
                : `You scored ${percentage}%, but don't give up! Review the material and try again.`}
            </p>

            {/* Score Circle */}
            <div className="relative w-32 h-32 mx-auto mb-6">
              <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 128 128">
                <circle cx="64" cy="64" r="54" fill="none" stroke="#e5e7eb" strokeWidth="8" />
                <circle
                  cx="64" cy="64" r="54" fill="none"
                  stroke={passed ? '#22c55e' : '#ef4444'}
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={`${(percentage / 100) * 339.292} 339.292`}
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div>
                  <div className="text-3xl font-bold text-gray-900">{percentage}%</div>
                  <div className="text-xs text-gray-500">Score</div>
                </div>
              </div>
            </div>

            <div className="flex justify-center gap-6 mb-8">
              <div className="text-center">
                <div className="text-lg font-bold text-green-600">{score}</div>
                <div className="text-xs text-gray-500">Correct</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-red-600">{questions.length - score}</div>
                <div className="text-xs text-gray-500">Incorrect</div>
              </div>
            </div>

            {/* Review */}
            <div className="text-left space-y-3 mb-8">
              {questions.map((q, i) => (
                <div key={i} className={`p-3 rounded-xl border ${
                  answers[i] === q.correct
                    ? 'border-green-200 bg-green-50'
                    : 'border-red-200 bg-red-50'
                }`}>
                  <div className="flex items-start gap-2">
                    {answers[i] === q.correct ? (
                      <HiCheck className="w-4 h-4 text-green-600 mt-0.5" />
                    ) : (
                      <HiX className="w-4 h-4 text-red-600 mt-0.5" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-gray-900">{q.question}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Correct answer: {q.options[q.correct]}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-3 justify-center">
              <button onClick={() => {
                setQuizState('not_started');
                setCurrentQuestion(0);
                setAnswers({});
                setTimeLeft(mockQuiz.timeLimit * 60);
                setFlaggedQuestions([]);
              }} className="btn-secondary">
                Retry Quiz
              </button>
              <Link href="/student-dashboard" className="btn-primary">
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
