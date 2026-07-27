'use client';

import { useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  HiPlay, HiCheck, HiLockClosed, HiMenu, HiX,
  HiChevronLeft, HiChevronRight, HiBookOpen, HiClock,
  HiDocumentText, HiChat, HiStar,
} from 'react-icons/hi';

interface Lesson {
  id: string;
  title: string;
  duration: string;
  completed: boolean;
  locked: boolean;
}

interface Module {
  id: string;
  title: string;
  lessons: Lesson[];
}

const mockModules: Module[] = [
  {
    id: 'm1',
    title: 'Getting Started',
    lessons: [
      { id: 'l1', title: 'Course Introduction', duration: '4:30', completed: true, locked: false },
      { id: 'l2', title: 'Setting Up Your Environment', duration: '12:15', completed: true, locked: false },
      { id: 'l3', title: 'Core Concepts Overview', duration: '8:45', completed: false, locked: false },
    ],
  },
  {
    id: 'm2',
    title: 'Foundation Topics',
    lessons: [
      { id: 'l4', title: 'Understanding the Basics', duration: '15:20', completed: false, locked: false },
      { id: 'l5', title: 'Advanced Techniques', duration: '22:10', completed: false, locked: false },
      { id: 'l6', title: 'Practical Applications', duration: '18:30', completed: false, locked: true },
    ],
  },
  {
    id: 'm3',
    title: 'Advanced Module',
    lessons: [
      { id: 'l7', title: 'Expert Patterns', duration: '25:00', completed: false, locked: true },
      { id: 'l8', title: 'Real-World Project', duration: '45:00', completed: false, locked: true },
    ],
  },]
;

function LessonContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const courseId = searchParams.get('course');
  const lessonId = searchParams.get('lesson') || 'l3';

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'notes' | 'qa'>('overview');

  const currentLesson = mockModules
    .flatMap((m) => m.lessons)
    .find((l) => l.id === lessonId);

  const allLessons = mockModules.flatMap((m) => m.lessons);
  const currentIndex = allLessons.findIndex((l) => l.id === lessonId);
  const prevLesson = currentIndex > 0 ? allLessons[currentIndex - 1] : null;
  const nextLesson = currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : null;

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-40 w-80 bg-white border-r border-gray-200
          transform transition-transform duration-300 ease-in-out overflow-y-auto
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0 lg:w-0 lg:overflow-hidden'}`}
      >
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Course Content</h2>
            <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-gray-400 hover:text-gray-600">
              <HiX className="w-5 h-5" />
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-1">{allLessons.filter((l) => l.completed).length} of {allLessons.length} completed</p>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
            <div
              className="bg-[rgb(var(--ctc-primary))] h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${(allLessons.filter((l) => l.completed).length / allLessons.length) * 100}%` }}
            />
          </div>
        </div>

        <nav className="p-2">
          {mockModules.map((module) => (
            <div key={module.id} className="mb-2">
              <h3 className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                {module.title}
              </h3>
              {module.lessons.map((lesson) => (
                <Link
                  key={lesson.id}
                  href={`/lesson?course=${courseId}&lesson=${lesson.id}`}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors
                    ${lesson.id === lessonId
                      ? 'bg-[rgb(var(--ctc-primary))]/5 text-[rgb(var(--ctc-primary-dark))] font-medium'
                      : lesson.locked
                      ? 'text-gray-400 cursor-not-allowed'
                      : 'text-gray-700 hover:bg-gray-50'}`}
                >
                  <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
                    {lesson.completed ? (
                      <HiCheck className="w-4 h-4 text-green-500" />
                    ) : lesson.locked ? (
                      <HiLockClosed className="w-3.5 h-3.5 text-gray-300" />
                    ) : (
                      <HiPlay className="w-4 h-4 text-[rgb(var(--ctc-primary-dark))]" />
                    )}
                  </span>
                  <span className="flex-1 truncate">{lesson.title}</span>
                  <span className="text-xs text-gray-400 flex-shrink-0">{lesson.duration}</span>
                </Link>
              ))}
            </div>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 min-w-0">
        {/* Top Bar */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <HiMenu className="w-5 h-5" />
          </button>

          <Link href={`/course-details/${courseId}`} className="text-sm text-gray-500 hover:text-[rgb(var(--ctc-primary))] transition-colors">
            <HiChevronLeft className="w-4 h-4 inline mr-1" />
            Back to Course
          </Link>

          <div className="flex-1" />

          <div className="flex items-center gap-2">
            {prevLesson && (
              <Link
                href={`/lesson?course=${courseId}&lesson=${prevLesson.id}`}
                className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-[rgb(var(--ctc-primary))] hover:bg-gray-50 rounded-lg transition-colors"
              >
                <HiChevronLeft className="w-4 h-4" />
                Previous
              </Link>
            )}
            {nextLesson && (
              <Link
                href={`/lesson?course=${courseId}&lesson=${nextLesson.id}`}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-[rgb(var(--ctc-primary))] text-white hover:bg-[rgb(var(--ctc-primary-dark))] rounded-lg transition-colors"
              >
                Next
                <HiChevronRight className="w-4 h-4" />
              </Link>
            )}
          </div>
        </div>

        {/* Video Player */}
        <div className="bg-black aspect-video flex items-center justify-center relative group">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mx-auto mb-4
                group-hover:bg-white/30 transition-colors cursor-pointer">
                <HiPlay className="w-8 h-8 text-white ml-0.5" />
              </div>
              <p className="text-white/60 text-sm">{currentLesson?.duration || '0:00'}</p>
            </div>
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-800">
            <div className="h-full bg-[rgb(var(--ctc-primary))]/50 w-1/3 transition-all" />
          </div>
        </div>

        {/* Lesson Content */}
        <div className="max-w-4xl mx-auto px-4 py-6">
          {/* Tabs */}
          <div className="flex gap-1 border-b border-gray-200 mb-6">
            {[
              { id: 'overview' as const, label: 'Overview', icon: HiBookOpen },
              { id: 'notes' as const, label: 'Notes', icon: HiDocumentText },
              { id: 'qa' as const, label: 'Q&A', icon: HiChat },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors
                  ${activeTab === tab.id
                    ? 'border-[rgb(var(--ctc-primary))] text-[rgb(var(--ctc-primary))]'
                    : 'border-transparent text-gray-500 hover:text-gray-700'}`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">{currentLesson?.title || 'Lesson'}</h1>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1"><HiClock className="w-4 h-4" /> {currentLesson?.duration || '0:00'}</span>
                  <span className="flex items-center gap-1">
                    <HiCheck className="w-4 h-4" />
                    {currentLesson?.completed ? 'Completed' : 'Not completed'}
                  </span>
                </div>
              </div>

              <div className="prose prose-gray max-w-none">
                <h2>Lesson Overview</h2>
                <p>
                  In this lesson, you will learn the fundamental concepts and practical techniques
                  needed to master this topic. We will cover key theories, real-world examples,
                  and hands-on exercises to reinforce your understanding.
                </p>
                <h3>Key Takeaways</h3>
                <ul>
                  <li>Understand the core principles and best practices</li>
                  <li>Apply learned concepts through practical exercises</li>
                  <li>Build confidence with real-world project scenarios</li>
                  <li>Identify common pitfalls and how to avoid them</li>
                </ul>
                <h3>Prerequisites</h3>
                <ul>
                  <li>Basic understanding of the subject matter</li>
                  <li>Required tools and software installed</li>
                  <li>Completion of previous lessons in this module</li>
                </ul>
              </div>

              {/* Resources */}
              <div className="bg-[rgb(var(--ctc-primary))]/5 rounded-xl p-6">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <HiDocumentText className="w-5 h-5 text-[rgb(var(--ctc-primary))]" />
                  Resources & Materials
                </h3>
                <div className="space-y-2">
                  {['Lesson Notes PDF', 'Exercise Files', 'Cheat Sheet'].map((resource) => (
                    <div key={resource} className="flex items-center gap-3 p-3 bg-white rounded-lg hover:shadow-sm transition-shadow cursor-pointer">
                      <div className="w-8 h-8 bg-[rgb(var(--ctc-primary))]/10 rounded-lg flex items-center justify-center">
                        <HiDocumentText className="w-4 h-4 text-[rgb(var(--ctc-primary))]" />
                      </div>
                      <span className="text-sm font-medium text-gray-700">{resource}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notes' && (
            <div>
              <textarea
                className="w-full h-64 p-4 border border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-[rgb(var(--ctc-primary))] focus:border-transparent outline-none text-sm"
                placeholder="Write your notes here... Markdown is supported.

# Heading
- Bullet points
**Bold text**"
              />
              <div className="flex justify-end mt-3">
                <button className="btn-primary text-sm !px-6">Save Notes</button>
              </div>
            </div>
          )}

          {activeTab === 'qa' && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <input
                  type="text"
                  placeholder="Ask a question about this lesson..."
                  className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[rgb(var(--ctc-primary))] focus:border-transparent outline-none text-sm"
                />
                <button className="btn-primary text-sm !px-6">Ask</button>
              </div>

              {[
                { author: 'Sarah M.', question: 'What is the difference between this and the previous approach?', answers: 3, time: '2h ago' },
                { author: 'John D.', question: 'Can you provide more examples of real-world applications?', answers: 1, time: '5h ago' },
              ].map((qa, i) => (
                <div key={i} className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-sm transition-shadow">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">{qa.question}</h4>
                      <p className="text-sm text-gray-500 mt-1">by {qa.author} · {qa.time}</p>
                    </div>
                    <span className="text-xs text-gray-400 flex items-center gap-1">
                      <HiChat className="w-3.5 h-3.5" />
                      {qa.answers}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default function LessonPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="w-12 h-12 border-4 border-[rgb(var(--ctc-primary))] border-t-transparent rounded-full animate-spin" /></div>}>
      <LessonContent />
    </Suspense>
  );
}
