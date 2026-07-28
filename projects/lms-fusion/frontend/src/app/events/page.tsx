'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiCalendar, HiLocationMarker, HiUserGroup, HiArrowRight, HiStar } from 'react-icons/hi';
import { useGetEventsQuery } from '@/store/api/endpoints/events';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Carousel from '@/components/ui/Carousel';
import type { CarouselSlide } from '@/components/ui/Carousel';
import { useToast } from '@/components/ui/Toast';

export default function EventsPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useGetEventsQuery({ page });
  const toast = useToast();

  useEffect(() => {
    const timer = setTimeout(() => {
      toast.info('Upcoming Events', 'Discover workshops, webinars, and community meetups.', 4000);
    }, 1500);
    return () => clearTimeout(timer);
  }, [toast]);

  // Build carousel slides from upcoming events
  const eventSlides: CarouselSlide[] = (data?.results ?? []).slice(0, 5).map((event) => ({
    id: event.id,
    content: (
      <Link href={`/events/${event.id}`} className="card block overflow-hidden group h-full mx-1">
        <div className="bg-gradient-to-br card-gradient h-28 flex items-center justify-center">
          <HiCalendar className="w-10 h-10 text-white/60" />
        </div>
        <div className="p-4">
          <div className="flex items-center gap-2 mb-1">
            <span className={`badge text-xs ${event.is_free ? 'bg-green-100 text-green-700' : 'bg-[rgb(var(--ctc-primary))]/10 text-[rgb(var(--ctc-primary-dark))]'}`}>
              {event.is_free ? 'Free' : `$${event.price}`}
            </span>
          </div>
          <h3 className="font-semibold text-gray-900 text-sm group-hover:text-[rgb(var(--ctc-primary))] transition-colors line-clamp-1">{event.title}</h3>
          <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
            <HiCalendar className="w-3 h-3" />
            <span>{new Date(event.start_date).toLocaleDateString()}</span>
          </div>
        </div>
      </Link>
    ),
  }));

  return (
    <ScrollReveal animation="fadeUp" duration={0.5}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Events</h1>
          <p className="text-gray-500 mt-2">Workshops, webinars, and community meetups</p>
        </div>

        {/* Upcoming Events Carousel */}
        {!isLoading && eventSlides.length > 0 && (
          <ScrollReveal animation="fadeUp" duration={0.4}>
            <section className="mb-10">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <HiStar className="w-5 h-5 text-[rgb(var(--ctc-primary))]" />
                Upcoming Events
              </h2>
              <Carousel
                slides={eventSlides}
                slidesPerView={{ xs: 1, sm: 2, md: 3, lg: 4 }}
                showArrows={eventSlides.length > 3}
                showDots={false}
                autoplay={5000}
                loop
                animation="slide"
                gap={16}
                className="pb-2"
              />
            </section>
          </ScrollReveal>
        )}

        {isLoading ? (
          <LoadingSkeleton variant="card" count={3} />
        ) : data && data.results.length > 0 ? (
          <ScrollReveal animation="fadeUp" duration={0.4} threshold={0.02}>
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-4">All Events</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {data?.results.map((event, idx) => (
                  <motion.div key={event.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.03 }}
                    className="card overflow-hidden">
                    <div className="bg-gradient-to-br card-gradient h-32 flex items-center justify-center">
                      <HiCalendar className="w-12 h-12 text-white/60" />
                    </div>
                    <div className="p-5">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`badge text-xs ${event.is_free ? 'bg-green-100 text-green-700' : 'bg-[rgb(var(--ctc-primary))]/10 text-[rgb(var(--ctc-primary-dark))]'}`}>
                          {event.is_free ? 'Free' : `$${event.price}`}
                        </span>
                        <span className="badge bg-gray-100 text-gray-600 text-xs">{event.status}</span>
                      </div>
                      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-1">{event.title}</h3>
                      <p className="text-sm text-gray-500 line-clamp-2 mb-3">{event.short_description}</p>
                      <div className="space-y-1 text-xs text-gray-500">
                        <p className="flex items-center gap-1"><HiCalendar className="w-3 h-3" /> {new Date(event.start_date).toLocaleDateString()} - {new Date(event.end_date).toLocaleDateString()}</p>
                        <p className="flex items-center gap-1"><HiLocationMarker className="w-3 h-3" /> {event.is_online ? 'Online' : event.location}</p>
                        <p className="flex items-center gap-1"><HiUserGroup className="w-3 h-3" /> {event.registered_count}/{event.capacity} registered</p>
                      </div>
                      <Link href={`/events/${event.id}`} className="mt-4 text-[rgb(var(--ctc-primary))] text-sm font-medium flex items-center gap-1 hover:text-[rgb(var(--ctc-primary-dark))]">
                        View Details <HiArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </motion.div>
                ))}
              </div>

              {data && Math.ceil(data.count / 10) > 1 && (
                <div className="flex justify-center gap-2 mt-10">
                  {Array.from({ length: Math.ceil(data.count / 10) }, (_, i) => i + 1).map(p => (
                    <button key={p} onClick={() => setPage(p)}
                      className={`w-10 h-10 rounded-lg font-medium transition-colors ${p === page ? 'bg-[rgb(var(--ctc-primary))] text-white' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'}`}>{p}</button>
                  ))}
                </div>
              )}
            </div>
          </ScrollReveal>
        ) : (
          <EmptyState icon="events" />
        )}
      </div>
    </ScrollReveal>
  );
}
