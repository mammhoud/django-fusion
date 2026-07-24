'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { HiCalendar, HiClock, HiLocationMarker, HiUserGroup, HiShare, HiArrowLeft } from 'react-icons/hi';
import { useGetEventQuery } from '@/store/api/endpoints/events';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

export default function EventDetailsPage() {
  const params = useParams();
  const eventId = Number(params?.id?.[0]) || 0;
  const { data: event, isLoading, error } = useGetEventQuery(eventId, { skip: !eventId });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  if (error || !event) {
    return <ErrorState fullPage message="Event not found." />;
  }

  const spotsRemaining = Math.max(0, (event.capacity || 0) - (event.registered_count || 0));
  const registrationProgress = event.capacity > 0
    ? ((event.registered_count || 0) / event.capacity) * 100
    : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero */}
      <div className="relative h-56 sm:h-72 md:h-96 overflow-hidden bg-gradient-to-br from-[rgb(var(--ctc-primary))] to-[rgb(var(--ctc-primary-dark))]">
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10">
          <div className="max-w-5xl mx-auto">
            <Link href="/events" className="inline-flex items-center gap-1 text-white/80 hover:text-white mb-3 transition-colors">
              <HiArrowLeft className="w-4 h-4" />
              Back to Events
            </Link>
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">{event.title}</h1>
            <div className="flex flex-wrap items-center gap-4 text-sm text-white/80">
              <span className="flex items-center gap-1"><HiCalendar className="w-4 h-4" /> {new Date(event.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
              <span className="flex items-center gap-1"><HiClock className="w-4 h-4" /> {new Date(event.start_date).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</span>
              <span className="flex items-center gap-1"><HiLocationMarker className="w-4 h-4" /> {event.location}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Description */}
            <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-3">About This Event</h2>
              <p className="text-gray-600 leading-relaxed">{event.description || event.short_description}</p>
            </section>

            {/* Organizer */}
            {event.organizer && (
              <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Organizer</h2>
                <p className="text-gray-700">{event.organizer}</p>
              </section>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 lg:sticky lg:top-24">
              <div className="text-center mb-6">
                <div className="text-3xl font-bold text-gray-900">
                  {event.is_free ? 'Free' : `$${event.price}`}
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  {spotsRemaining} of {event.capacity || 0} spots remaining
                </p>
                <div className="mt-3 progress-track">
                  <div
                    className="progress-fill"
                    style={{ width: `${Math.min(100, registrationProgress)}%` }}
                  />
                </div>
              </div>

              <button className="btn-primary w-full mb-3">Register Now</button>

              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-center gap-3">
                  <HiCalendar className="w-4 h-4 text-gray-400" />
                  <span>{new Date(event.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                </div>
                <div className="flex items-center gap-3">
                  <HiClock className="w-4 h-4 text-gray-400" />
                  <span>{new Date(event.start_date).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</span>
                </div>
                <div className="flex items-center gap-3">
                  <HiLocationMarker className="w-4 h-4 text-gray-400" />
                  <span>{event.is_online ? 'Online' : event.location}</span>
                </div>
                <div className="flex items-center gap-3">
                  <HiUserGroup className="w-4 h-4 text-gray-400" />
                  <span>{spotsRemaining} spots left</span>
                </div>
              </div>

              <hr className="my-4" />

              <button className="w-full flex items-center justify-center gap-2 py-2 text-sm text-gray-600 hover:text-[rgb(var(--ctc-primary))] hover:bg-[rgb(var(--ctc-primary))]/5 rounded-lg transition-colors">
                <HiShare className="w-4 h-4" />
                Share Event
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
