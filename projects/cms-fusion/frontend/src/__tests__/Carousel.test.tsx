/**
 * Unit tests for the Carousel component.
 *
 * Covers:
 * - Rendering slides, arrows, dots
 * - Empty state (no slides → null)
 * - Arrow navigation (prev/next)
 * - Dot navigation
 * - onSlideChange callback
 * - Autoplay with pause on hover
 * - Hero mode with animated captions
 * - Custom initialIndex
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import Carousel from '@/components/ui/Carousel';
import type { CarouselSlide } from '@/components/ui/Carousel';

const sampleSlides: CarouselSlide[] = [
  { id: 1, content: <div>Slide 1</div> },
  { id: 2, content: <div>Slide 2</div> },
  { id: 3, content: <div>Slide 3</div> },
];

describe('Carousel', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders all slides', () => {
    render(<Carousel slides={sampleSlides} showArrows={false} showDots={false} />);
    expect(screen.getByText('Slide 1')).toBeInTheDocument();
  });

  it('returns null when slides array is empty', () => {
    const { container } = render(<Carousel slides={[]} />);
    expect(container.innerHTML).toBe('');
  });

  it('renders next/prev arrow buttons by default', () => {
    render(<Carousel slides={sampleSlides} />);
    expect(screen.getByLabelText('Previous slide')).toBeInTheDocument();
    expect(screen.getByLabelText('Next slide')).toBeInTheDocument();
  });

  it('hides arrows when showArrows is false', () => {
    render(<Carousel slides={sampleSlides} showArrows={false} />);
    expect(screen.queryByLabelText('Previous slide')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Next slide')).not.toBeInTheDocument();
  });

  it('shows dot indicators', () => {
    render(<Carousel slides={sampleSlides} showArrows={false} />);
    expect(screen.getByLabelText('Go to slide 1')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to slide 2')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to slide 3')).toBeInTheDocument();
  });

  it('hides dots when showDots is false', () => {
    render(<Carousel slides={sampleSlides} showArrows={false} showDots={false} />);
    expect(screen.queryByLabelText('Go to slide 1')).not.toBeInTheDocument();
  });

  it('navigates to next slide via arrow button', async () => {
    render(<Carousel slides={sampleSlides} showDots />);
    const nextBtn = screen.getByLabelText('Next slide');
    fireEvent.click(nextBtn);
    // The active dot should now be slide 2
    await vi.waitFor(() => {
      const dot2 = screen.getByLabelText('Go to slide 2');
      expect(dot2.className).toContain('w-6');
    });
  });

  it('navigates to previous slide via arrow button', async () => {
    render(<Carousel slides={sampleSlides} initialIndex={1} showDots />);
    const prevBtn = screen.getByLabelText('Previous slide');
    fireEvent.click(prevBtn);
    await vi.waitFor(() => {
      const dot1 = screen.getByLabelText('Go to slide 1');
      expect(dot1.className).toContain('w-6');
    });
  });

  it('navigates to a specific slide via dot button', () => {
    const onSlideChange = vi.fn();
    render(
      <Carousel
        slides={sampleSlides}
        showArrows={false}
        onSlideChange={onSlideChange}
      />,
    );
    fireEvent.click(screen.getByLabelText('Go to slide 3'));
    expect(onSlideChange).toHaveBeenCalledWith(2);
  });

  it('calls onSlideChange when navigating', () => {
    const onSlideChange = vi.fn();
    render(<Carousel slides={sampleSlides} onSlideChange={onSlideChange} />);
    fireEvent.click(screen.getByLabelText('Next slide'));
    expect(onSlideChange).toHaveBeenCalledWith(1);
  });

  it('autoplay advances slides automatically', async () => {
    render(
      <Carousel
        slides={sampleSlides}
        autoplay={1000}
        showDots
        showArrows={false}
      />,
    );
    // Initially slide 1 is active
    const dot1 = screen.getByLabelText('Go to slide 1');
    expect(dot1.className).toContain('w-6');

    // Advance autoplay timer
    vi.advanceTimersByTime(1000);

    // Slide 2 should now be active
    await vi.waitFor(() => {
      const dot2 = screen.getByLabelText('Go to slide 2');
      expect(dot2.className).toContain('w-6');
    });
  });

  it('pauses autoplay on mouse enter and resumes on mouse leave', async () => {
    render(
      <Carousel
        slides={sampleSlides}
        autoplay={1000}
        showDots
        showArrows={false}
      />,
    );

    // Hover over carousel
    const carousel = screen.getByRole('region');
    fireEvent.mouseEnter(carousel);

    // Advance timer — should NOT advance since paused
    vi.advanceTimersByTime(1000);
    const dot1 = screen.getByLabelText('Go to slide 1');
    expect(dot1.className).toContain('w-6');

    // Mouse leave — should resume
    fireEvent.mouseLeave(carousel);
    vi.advanceTimersByTime(1000);
    await vi.waitFor(() => {
      const dot2 = screen.getByLabelText('Go to slide 2');
      expect(dot2.className).toContain('w-6');
    });
  });

  it('renders hero mode with background and animated content', () => {
    const heroSlides: CarouselSlide[] = [
      { id: 1, content: <div>Hero Slide</div>, bgImage: 'https://example.com/bg.jpg', bgColor: '#123456' },
    ];
    render(<Carousel slides={heroSlides} hero showArrows={false} showDots={false} />);
    expect(screen.getByText('Hero Slide')).toBeInTheDocument();
  });

  it('respects initialIndex', () => {
    render(
      <Carousel
        slides={sampleSlides}
        initialIndex={2}
        showDots
        showArrows={false}
      />,
    );
    const dot3 = screen.getByLabelText('Go to slide 3');
    expect(dot3.className).toContain('w-6');
  });

  it('renders slides with custom className', () => {
    const { container } = render(
      <Carousel slides={sampleSlides} showArrows={false} showDots={false} className="my-carousel" />,
    );
    const region = container.querySelector('[role="region"]');
    expect(region?.className).toContain('my-carousel');
  });

  it('renders play/pause button when autoplay is enabled', () => {
    render(
      <Carousel slides={sampleSlides} autoplay={3000} showArrows={false} showDots />,
    );
    expect(screen.getByLabelText('Pause autoplay')).toBeInTheDocument();
  });

  it('shows slide count in aria-label', () => {
    render(<Carousel slides={sampleSlides} showArrows={false} showDots={false} />);
    const slideGroup = screen.getByLabelText('Slide 1 of 3');
    expect(slideGroup).toBeInTheDocument();
  });

  it('does not disable prev button when loop is true', () => {
    render(<Carousel slides={sampleSlides} loop showDots />);
    const prevBtn = screen.getByLabelText('Previous slide');
    expect(prevBtn).not.toBeDisabled();
  });

  it('disables prev button at start when loop is false', () => {
    render(<Carousel slides={sampleSlides} loop={false} showDots />);
    const prevBtn = screen.getByLabelText('Previous slide');
    expect(prevBtn).toBeDisabled();
  });
});
