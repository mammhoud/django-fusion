'use client';

import { useState, Suspense, useRef, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  HiPlay, HiCheck, HiLockClosed, HiMenu, HiX,
  HiChevronLeft, HiChevronRight, HiBookOpen, HiClock,
  HiDocumentText, HiChat, HiStar, HiVolumeUp, HiFilm,
} from 'react-icons/hi';

interface Lesson {
  id: string;
  title: string;
  duration: string;
  completed: boolean;
  locked: boolean;
  video_id?: number | null;
  video_file_url?: string;
  video_url?: string;
  has_video?: boolean;
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
      { id: 'l1', title: 'Course Introduction', duration: '4:30', completed: true, locked: false, has_video: true, video_file_url: '' },
      { id: 'l2', title: 'Setting Up Your Environment', duration: '12:15', completed: true, locked: false, has_video: true },
      { id: 'l3', title: 'Core Concepts Overview', duration: '8:45', completed: false, locked: false, has_video: true },
    ],
  },
  {
    id: 'm2',
    title: 'Foundation Topics',
    lessons: [
      { id: 'l4', title: 'Understanding the Basics', duration: '15:20', completed: false, locked: false, has_video: true },
      { id: 'l5', title: 'Advanced Techniques', duration: '22:10', completed: false, locked: false, has_video: true },
      { id: 'l6', title: 'Practical Applications', duration: '18:30', completed: false, locked: true, has_video: false },
    ],
  },
  {
    id: 'm3',
    title: 'Advanced Module',
    lessons: [
      { id: 'l7', title: 'Expert Patterns', duration: '25:00', completed: false, locked: true, has_video: true },
      { id: 'l8', title: 'Real-World Project', duration: '45:00', completed: false, locked: true, has_video: true },
    ],
  },
];

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
                      <HiPlay className="w-4 h-4 text-[rgb(var(--ctc-primary))]" />
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

        {/* Video Player — Real HTML5 player */}
        <VideoPlayer
          lesson={currentLesson}
          onProgress={(pct) => {
            // In production, send progress to the server
            console.log(`Video progress: ${pct}%`);
          }}
        />

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

// ══════════════════════════════════════════════════════════════════════
// VideoPlayer component — real HTML5 video with range-request support
// ══════════════════════════════════════════════════════════════════════

interface VideoPlayerProps {
  lesson: Lesson | undefined;
  onProgress?: (progressPercent: number) => void;
}

function VideoPlayer({ lesson, onProgress }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Determine the video source
  const hasVideo = lesson?.has_video && (lesson?.video_file_url || lesson?.video_url);
  const videoSource = lesson?.video_file_url || lesson?.video_url || '';
  const isExternalVideo = !lesson?.video_file_url && !!lesson?.video_url;

  const handleTimeUpdate = useCallback(() => {
    if (videoRef.current) {
      const ct = videoRef.current.currentTime;
      setCurrentTime(ct);
      if (duration > 0) {
        const pct = Math.round((ct / duration) * 100);
        onProgress?.(pct);
      }
    }
  }, [duration, onProgress]);

  const handleLoadedMetadata = useCallback(() => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  }, []);

  const togglePlay = useCallback(() => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play().catch(() => {});
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  const handleVolumeChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const v = parseFloat(e.target.value);
    setVolume(v);
    setIsMuted(v === 0);
    if (videoRef.current) {
      videoRef.current.volume = v;
    }
  }, []);

  const toggleMute = useCallback(() => {
    if (!videoRef.current) return;
    const newMuted = !isMuted;
    videoRef.current.muted = newMuted;
    setIsMuted(newMuted);
  }, [isMuted]);

  const toggleFullscreen = useCallback(() => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch(() => {});
      setIsFullscreen(true);
    } else {
      document.exitFullscreen().catch(() => {});
      setIsFullscreen(false);
    }
  }, []);

  const formatTime = (seconds: number): string => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  const seekTo = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!videoRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const pct = x / rect.width;
    videoRef.current.currentTime = pct * duration;
  }, [duration]);

  if (!hasVideo) {
    return (
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 aspect-video flex items-center justify-center">
        <div className="text-center">
          <HiFilm className="w-12 h-12 text-white/30 mx-auto mb-3" />
          <p className="text-white/50 text-sm">No video available for this lesson</p>
          <p className="text-white/30 text-xs mt-1">{lesson?.duration || ''} reading content</p>
        </div>
      </div>
    );
  }

  if (isExternalVideo) {
    return (
      <div className="bg-black aspect-video flex items-center justify-center">
        <iframe
          src={videoSource.replace('watch?v=', 'embed/').replace('youtu.be/', 'youtube.com/embed/')}
          className="w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          title={lesson?.title || 'Lesson video'}
        />
      </div>
    );
  }

  // Self-hosted video with HTML5 player
  return (
    <div ref={containerRef} className="bg-black relative group">
      <video
        ref={videoRef}
        className="w-full aspect-video object-contain cursor-pointer"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        onClick={togglePlay}
        preload="metadata"
        playsInline
      >
        <source src={videoSource} type='video/mp4' />
        Your browser does not support the video tag.
      </video>

      {/* Play/Pause overlay (shown when paused) */}
      {!isPlaying && (
        <div
          className="absolute inset-0 flex items-center justify-center bg-black/20 cursor-pointer"
          onClick={togglePlay}
        >
          <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center
            hover:bg-white/30 transition-all hover:scale-110">
            <HiPlay className="w-8 h-8 text-white ml-0.5" />
          </div>
        </div>
      )}

      {/* Controls bar */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent px-4 pt-8 pb-3
        opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        {/* Progress bar */}
        <div
          className="w-full h-1 bg-white/30 rounded-full mb-3 cursor-pointer group/progress"
          onClick={seekTo}
        >
          <div
            className="h-full bg-[rgb(var(--ctc-primary))] rounded-full relative transition-all duration-100"
            style={{ width: `${progressPercent}%` }}
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full
              opacity-0 group-hover/progress:opacity-100 transition-opacity shadow" />
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between text-white">
          <div className="flex items-center gap-3">
            {/* Play/Pause */}
            <button onClick={togglePlay} className="p-1 hover:text-[rgb(var(--ctc-primary))] transition-colors">
              {isPlaying ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/></svg>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
              )}
            </button>

            {/* Time */}
            <span className="text-xs text-white/70 font-mono">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Volume */}
            <div className="flex items-center gap-1.5 group/vol">
              <button onClick={toggleMute} className="p-1 hover:text-[rgb(var(--ctc-primary))] transition-colors">
                {isMuted || volume === 0 ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51A8.796 8.796 0 0021 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06a8.99 8.99 0 003.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
                ) : (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
                )}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-0 group-hover/vol:w-20 transition-all duration-300 accent-[rgb(var(--ctc-primary))]"
              />
            </div>

            {/* Fullscreen */}
            <button onClick={toggleFullscreen} className="p-1 hover:text-[rgb(var(--ctc-primary))] transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                {isFullscreen ? (
                  <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
                ) : (
                  <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════
// Page export
// ══════════════════════════════════════════════════════════════════════

export default function LessonPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="w-12 h-12 border-4 border-[rgb(var(--ctc-primary))] border-t-transparent rounded-full animate-spin" /></div>}>
      <LessonContent />
    </Suspense>
  );
}
