'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence, type PanInfo } from 'framer-motion';
import {
  HiChevronLeft,
  HiChevronRight,
  HiPlay,
  HiPause,
} from 'react-icons/hi';

// ── Types ──

export interface CarouselSlide {
  id: string | number;
  content: React.ReactNode;
  /** Optional background image URL - applied as inline style background */
  bgImage?: string;
  /** Optional background color fallback */
  bgColor?: string;
}

interface CarouselProps {
  slides: CarouselSlide[];
  /** Visible items per breakpoint */
  slidesPerView?: number | { xs?: number; sm?: number; md?: number; lg?: number; xl?: number };
  /** Show prev/next arrows */
  showArrows?: boolean;
  /** Show dot indicators */
  showDots?: boolean;
  /** Autoplay interval in ms (0 to disable) */
  autoplay?: number;
  /** Loop back to start */
  loop?: boolean;
  /** Animation variant */
  animation?: 'slide' | 'fade' | 'zoom';
  /** Gap between slides in px */
  gap?: number;
  /** Height of carousel */
  height?: string;
  /** Additional CSS classes */
  className?: string;
  /** Called when active slide changes */
  onSlideChange?: (index: number) => void;
  /** Hero mode - full-width with animated captions */
  hero?: boolean;
  /** Initial active index */
  initialIndex?: number;
}

// ── Responsive helper ──

function getSlidesPerView(
  config: CarouselProps['slidesPerView'],
): number {
  if (typeof config === 'number') return config;
  const bp = config ?? {};
  if (typeof window === 'undefined') return bp.lg ?? 1;
  const w = window.innerWidth;
  if (w >= 1280) return bp.xl ?? bp.lg ?? 4;
  if (w >= 1024) return bp.lg ?? 3;
  if (w >= 768) return bp.md ?? 2;
  if (w >= 640) return bp.sm ?? bp.md ?? 1;
  return bp.xs ?? 1;
}

// ── Variants ──

const variants: Record<string, { enter: object; center: object; exit: object }> = {
  slide: {
    enter: (dir: number) => ({ x: dir > 0 ? 300 : -300, opacity: 0 }),
    center: { x: 0, opacity: 1 },
    exit: (dir: number) => ({ x: dir < 0 ? 300 : -300, opacity: 0 }),
  },
  fade: {
    enter: { opacity: 0 },
    center: { opacity: 1 },
    exit: { opacity: 0 },
  },
  zoom: {
    enter: { scale: 0.85, opacity: 0 },
    center: { scale: 1, opacity: 1 },
    exit: { scale: 1.05, opacity: 0 },
  },
};

// ── Component ──

export default function Carousel({
  slides,
  slidesPerView = 1,
  showArrows = true,
  showDots = true,
  autoplay = 0,
  loop = true,
  animation = 'slide',
  gap = 16,
  height,
  className = '',
  onSlideChange,
  hero = false,
  initialIndex = 0,
}: CarouselProps) {
  const [[activeIndex, direction], setActiveState] = useState([initialIndex, 0]);
  const [isPaused, setIsPaused] = useState(false);
  const [spv, setSpv] = useState(() =>
    typeof slidesPerView === 'number' ? slidesPerView : 1,
  );
  const containerRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const maxIndex = Math.max(0, slides.length - spv);

  // Responsive slidesPerView
  useEffect(() => {
    if (typeof slidesPerView === 'number') return;
    const calc = () => setSpv(getSlidesPerView(slidesPerView));
    calc();
    window.addEventListener('resize', calc);
    return () => window.removeEventListener('resize', calc);
  }, [slidesPerView]);

  // Clamp active index
  useEffect(() => {
    setActiveState(([idx, dir]) => [Math.min(idx, maxIndex), dir]);
  }, [maxIndex]);

  // Autoplay
  useEffect(() => {
    if (!autoplay || isPaused) {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }
    timerRef.current = setInterval(() => {
      setActiveState(([idx]) => {
        const next = idx + 1;
        if (next > maxIndex) {
          if (loop) return [0, 1];
          return [idx, 0];
        }
        return [next, 1];
      });
    }, autoplay);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [autoplay, isPaused, maxIndex, loop]);

  const goTo = useCallback(
    (index: number) => {
      const clamped = Math.max(0, Math.min(index, maxIndex));
      const dir = clamped > activeIndex ? 1 : -1;
      setActiveState([clamped, dir]);
      onSlideChange?.(clamped);
    },
    [activeIndex, maxIndex, onSlideChange],
  );

  const goNext = useCallback(() => {
    if (activeIndex >= maxIndex) {
      if (loop) goTo(0);
      return;
    }
    goTo(activeIndex + 1);
  }, [activeIndex, maxIndex, loop, goTo]);

  const goPrev = useCallback(() => {
    if (activeIndex <= 0) {
      if (loop) goTo(maxIndex);
      return;
    }
    goTo(activeIndex - 1);
  }, [activeIndex, maxIndex, loop, goTo]);

  const handleDragEnd = (_: any, info: PanInfo) => {
    const threshold = 50;
    if (info.offset.x < -threshold) goNext();
    else if (info.offset.x > threshold) goPrev();
  };

  const hasPrev = loop || activeIndex > 0;
  const hasNext = loop || activeIndex < maxIndex;

  if (!slides.length) return null;

  // ── Slide Indicator ──
  const slideCount = maxIndex + 1;

  // ── Render ──

  return (
    <div
      ref={containerRef}
      className={`relative overflow-hidden select-none ${className}`}
      style={{ height }}
      onMouseEnter={() => autoplay && setIsPaused(true)}
      onMouseLeave={() => autoplay && setIsPaused(false)}
      role="region"
      aria-roledescription="carousel"
      aria-label="Image carousel"
    >
      {/* Slides */}
      <div className="relative w-full h-full" style={{ margin: `0 -${gap / 2}px` }}>
        <AnimatePresence initial={false} custom={direction} mode="popLayout">
          <motion.div
            key={activeIndex}
            custom={direction}
            variants={variants[animation] as any}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            dragElastic={0.2}
            onDragEnd={handleDragEnd}
            className="flex"
            style={{ gap, padding: `0 ${gap / 2}px` }}
            aria-live="polite"
          >
            {Array.from({ length: spv }).map((_, offset) => {
              const idx = activeIndex + offset;
              const slide = slides[idx];
              if (!slide) return null;
              return (
                <div
                  key={`${slide.id}-${offset}`}
                  className={`flex-shrink-0 ${hero ? 'w-full' : ''}`}
                  style={{
                    flex: hero ? '0 0 100%' : `0 0 calc(${100 / spv}% - ${gap}px)`,
                  }}
                  role="group"
                  aria-roledescription="slide"
                  aria-label={`Slide ${idx + 1} of ${slides.length}`}
                >
                  {hero ? (
                    <div
                      className="relative w-full h-full min-h-[60vh] flex items-center justify-center bg-cover bg-center"
                      style={{
                        backgroundImage: slide.bgImage ? `url(${slide.bgImage})` : undefined,
                        backgroundColor: slide.bgColor ?? '#1a1a2e',
                      }}
                    >
                      <div className="absolute inset-0 bg-black/40" />
                      <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2, duration: 0.6 }}
                        className="relative z-10 text-white text-center px-6 max-w-4xl"
                      >
                        {slide.content}
                      </motion.div>
                    </div>
                  ) : (
                    slide.content
                  )}
                </div>
              );
            })}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Arrows */}
      {showArrows && (hasPrev || hasNext) && (
        <>
          <button
            onClick={goPrev}
            disabled={!hasPrev}
            className={`absolute left-3 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full 
              bg-white/90 hover:bg-white shadow-lg flex items-center justify-center
              transition-all duration-200 
              ${!hasPrev ? 'opacity-30 cursor-not-allowed' : 'opacity-80 hover:opacity-100'}
              ${hero ? 'text-white bg-black/30 hover:bg-black/50' : 'text-gray-800'}`}
            aria-label="Previous slide"
          >
            <HiChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={goNext}
            disabled={!hasNext}
            className={`absolute right-3 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full 
              bg-white/90 hover:bg-white shadow-lg flex items-center justify-center
              transition-all duration-200
              ${!hasNext ? 'opacity-30 cursor-not-allowed' : 'opacity-80 hover:opacity-100'}
              ${hero ? 'text-white bg-black/30 hover:bg-black/50' : 'text-gray-800'}`}
            aria-label="Next slide"
          >
            <HiChevronRight className="w-5 h-5" />
          </button>
        </>
      )}

      {/* Dots */}
      {showDots && slides.length > 1 && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2">
          {Array.from({ length: slideCount }).map((_, i) => (
            <button
              key={i}
              onClick={() => goTo(i)}
              className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
                i === activeIndex
                  ? hero
                    ? 'bg-white w-6'
                    : 'bg-[rgb(var(--fu-primary))] w-6'
                  : hero
                    ? 'bg-white/50 hover:bg-white/80'
                    : 'bg-gray-300 hover:bg-gray-400'
              }`}
              aria-label={`Go to slide ${i + 1}`}
            />
          ))}
          {/* Play/Pause button */autoplay > 0 && (
            <button
              onClick={() => setIsPaused(!isPaused)}
              className={`ml-3 w-7 h-7 rounded-full flex items-center justify-center transition-colors ${
                hero ? 'bg-white/20 hover:bg-white/30 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-600'
              }`}
              aria-label={isPaused ? 'Resume autoplay' : 'Pause autoplay'}
            >
              {isPaused ? <HiPlay className="w-3.5 h-3.5" /> : <HiPause className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
