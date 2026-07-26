'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { HiCalendar, HiClock, HiLocationMarker, HiUserGroup, HiShare, HiArrowLeft } from 'react-icons/hi';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

const mockEvents: Record<string, {
  id: string; title: string; date: string; time: string; location: string;
  category: string; image: string; price: string; spots: number; totalSpots: number;
  description: string; agenda: { time: string; title: string; description: string }[];
  speaker: { name: string; role: string; avatar: string };
}> = {
  '1': {
    id: '1', title: 'Web Development Bootcamp 2026', date: 'Mar 15, 2026', time: '9:00 AM - 5:00 PM',
    location: 'San Francisco Convention Center', category: 'Workshop',
    image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800',
    price: '$149', spots: 23, totalSpots: 50,
    description: 'Join us for an intensive one-day bootcamp covering the latest in web development. From modern frameworks to deployment strategies, this workshop has everything you need to level up your skills.',
    agenda: [
      { time: '9:00 AM', title: 'Registration & Welcome Coffee', description: 'Check-in and networking' },
      { time: '10:00 AM', title: 'Modern Frontend Architecture', description: 'Deep dive into component-based architecture' },
      { time: '12:00 PM', title: 'Lunch Break', description: 'Networking lunch provided' },
      { time: '1:30 PM', title: 'Backend Best Practices', description: 'API design and database optimization' },
      { time: '3:30 PM', title: 'Deployment & DevOps', description: 'CI/CD pipelines and cloud deployment' },
      { time: '4:30 PM', title: 'Q&A and Closing', description: 'Open forum and networking' },
    ],
    speaker: { name: 'Dr. Sarah Chen', role: 'Senior Engineer at TechCorp', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100' },
  },
  '2': {
    id: '2', title: 'AI in Education Summit', date: 'Apr 20, 2026', time: '10:00 AM - 4:00 PM',
    location: 'Online (Zoom)', category: 'Conference',
    image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800',
    price: 'Free', spots: 145, totalSpots: 500,
    description: 'Explore how artificial intelligence is transforming education. Hear from industry leaders about AI-powered learning tools, personalized education paths, and the future of teaching.',
    agenda: [
      { time: '10:00 AM', title: 'Keynote: The Future of Learning', description: 'AI-driven personalized education' },
      { time: '11:00 AM', title: 'Panel Discussion', description: 'Ethics and AI in education' },
      { time: '12:00 PM', title: 'Break', description: 'Virtual networking' },
      { time: '1:00 PM', title: 'Workshop: Building AI Tutors', description: 'Hands-on session' },
      { time: '3:00 PM', title: 'Closing Remarks', description: 'Key takeaways and next steps' },
    ],
    speaker: { name: 'Prof. James Wilson', role: 'AI Research Lead at EduTech', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100' },
  },
};

export default function EventDetailsPage() {
  const params = useParams();
  const eventId = params?.id?.[0] || '1';
  const event = mockEvents[eventId] || Object.values(mockEvents)[0];

  if (!event) {
    return <ErrorState fullPage message="Event not found." />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero */}
      <div className="relative h-56 sm:h-72 md:h-96 overflow-hidden">
        <img src={event.image} alt={event.title} className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10">
          <div className="max-w-5xl mx-auto">
            <Link href="/events" className="inline-flex items-center gap-1 text-white/80 hover:text-white mb-3 transition-colors">
              <HiArrowLeft className="w-4 h-4" />
              Back to Events
            </Link>
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">{event.title}</h1>
            <div className="flex flex-wrap items-center gap-4 text-sm text-white/80">
              <span className="flex items-center gap-1"><HiCalendar className="w-4 h-4" /> {event.date}</span>
              <span className="flex items-center gap-1"><HiClock className="w-4 h-4" /> {event.time}</span>
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
              <p className="text-gray-600 leading-relaxed">{event.description}</p>
            </section>

            {/* Agenda */}
            <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Agenda</h2>
              <div className="space-y-0">
                {event.agenda.map((item, i) => (
                  <div key={i} className="flex gap-4 pb-4 last:pb-0 relative">
                    <div className="flex flex-col items-center">
                      <div className="w-3 h-3 rounded-full bg-[rgb(var(--ctc-primary))] mt-1.5" />
                      {i < event.agenda.length - 1 && (
                        <div className="w-0.5 flex-1 bg-[rgb(var(--ctc-primary))]/20 mt-1" />
                      )}
                    </div>
                    <div>
                      <span className="text-xs font-medium text-[rgb(var(--ctc-primary))]">{item.time}</span>
                      <h4 className="font-medium text-gray-900 mt-0.5">{item.title}</h4>
                      <p className="text-sm text-gray-500 mt-0.5">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Speaker */}
            <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Speaker</h2>
              <div className="flex items-center gap-4">
                <img src={event.speaker.avatar} alt={event.speaker.name} className="w-16 h-16 rounded-full object-cover" />
                <div>
                  <h3 className="font-semibold text-gray-900">{event.speaker.name}</h3>
                  <p className="text-sm text-gray-500">{event.speaker.role}</p>
                </div>
              </div>
            </section>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 lg:sticky lg:top-24">
              <div className="text-center mb-6">
                <div className="text-3xl font-bold text-gray-900">{event.price}</div>
                <p className="text-sm text-gray-500 mt-1">
                  {event.spots} of {event.totalSpots} spots remaining
                </p>
                <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-[rgb(var(--ctc-primary))] h-2 rounded-full transition-all"
                    style={{ width: `${((event.totalSpots - event.spots) / event.totalSpots) * 100}%` }}
                  />
                </div>
              </div>

              <button className="btn-primary w-full mb-3">Register Now</button>

              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-center gap-3">
                  <HiCalendar className="w-4 h-4 text-gray-400" />
                  <span>{event.date}</span>
                </div>
                <div className="flex items-center gap-3">
                  <HiClock className="w-4 h-4 text-gray-400" />
                  <span>{event.time}</span>
                </div>
                <div className="flex items-center gap-3">
                  <HiLocationMarker className="w-4 h-4 text-gray-400" />
                  <span>{event.location}</span>
                </div>
                <div className="flex items-center gap-3">
                  <HiUserGroup className="w-4 h-4 text-gray-400" />
                  <span>{event.spots} spots left</span>
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
