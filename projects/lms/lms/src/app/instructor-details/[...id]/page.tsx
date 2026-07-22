'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { HiStar, HiAcademicCap, HiUserGroup, HiPlay, HiGlobe, HiBookOpen, HiArrowLeft } from 'react-icons/hi';
import { useGetInstructorQuery } from '@/store/api/endpoints/instructors';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

const mockInstructor = {
  id: '1',
  name: 'Dr. Sarah Chen',
  role: 'Senior Software Engineer',
  avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300',
  cover: 'https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=1200',
  bio: 'With over 15 years of experience in software development and a PhD in Computer Science, Dr. Chen has taught over 50,000 students worldwide. Her teaching philosophy emphasizes practical, project-based learning.',
  rating: 4.8,
  studentsCount: 52341,
  coursesCount: 12,
  reviewsCount: 3421,
  social: {
    website: 'https://sarahchen.dev',
    twitter: '@sarahchen_dev',
    github: 'sarahchen',
  },
  skills: ['React', 'TypeScript', 'Python', 'Machine Learning', 'System Design', 'Cloud Architecture'],
  courses: [
    { id: 'c1', title: 'Advanced React Development', students: 12340, rating: 4.9, price: 89.99, image: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=400' },
    { id: 'c2', title: 'Full-Stack TypeScript', students: 8940, rating: 4.8, price: 79.99, image: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400' },
    { id: 'c3', title: 'Python for Data Science', students: 15230, rating: 4.7, price: 69.99, image: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400' },
  ],
};

const mockReviews = [
  { id: 'r1', student: 'Alex M.', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50', rating: 5, text: 'Excellent instructor! The course was well-structured and the projects were very practical.', date: '2 weeks ago' },
  { id: 'r2', student: 'Jessica L.', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=50', rating: 5, text: 'Dr. Chen explains complex concepts in a way that\'s easy to understand. Highly recommended!', date: '1 month ago' },
  { id: 'r3', student: 'David R.', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=50', rating: 4, text: 'Great content and amazing support. Would love to see more advanced topics covered.', date: '2 months ago' },
];

export default function InstructorDetailsPage() {
  const params = useParams();
  const instructorId = Number(params?.id?.[0]) || 1;
  const { data: instructor, isLoading } = useGetInstructorQuery(instructorId);

  const display = (instructor || mockInstructor) as any;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 py-10">
          <LoadingSkeleton variant="detail" />
        </div>
      </div>
    );
  }

  if (!instructor && !mockInstructor) {
    return <ErrorState fullPage message="Instructor not found." />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Cover & Profile */}
      <div className="relative">
        <div className="h-48 sm:h-56 md:h-72 overflow-hidden">
          <img src={display.cover || mockInstructor.cover} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
        </div>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 -mt-20 relative z-10">
          <div className="flex flex-col md:flex-row items-start md:items-end gap-6">
            <img src={display.avatar || mockInstructor.avatar} alt={display.name} className="w-32 h-32 rounded-2xl border-4 border-white shadow-lg object-cover" />
            <div className="flex-1 pb-4">
              <Link href="/instructors" className="inline-flex items-center gap-1 text-sm text-white/80 hover:text-white mb-2 transition-colors">
                <HiArrowLeft className="w-4 h-4" />
                All Instructors
              </Link>
              <h1 className="text-3xl font-bold text-white">{display.name}</h1>
              <p className="text-white/80 mt-1">{display.role || mockInstructor.role}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Bio */}
            <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-3">About Me</h2>
              <p className="text-gray-600 leading-relaxed">{display.bio || mockInstructor.bio}</p>
            </section>

            {/* Skills */}
            <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Expertise</h2>
              <div className="flex flex-wrap gap-2">
                {(display.skills || mockInstructor.skills).map((skill: string) => (
                  <span key={skill} className="px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-lg text-sm font-medium">
                    {skill}
                  </span>
                ))}
              </div>
            </section>

            {/* Courses */}
            <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <HiBookOpen className="w-5 h-5 text-indigo-600" />
                Courses ({display.coursesCount || mockInstructor.coursesCount})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(display.courses || mockInstructor.courses).map((course: { id: string; title: string; students: number; rating: number; price: number; image: string }) => (
                  <Link key={course.id} href={`/course-details/${course.id}`} className="group">
                    <div className="bg-gray-50 rounded-xl overflow-hidden hover:shadow-md transition-all">
                      <div className="aspect-video bg-gray-200 overflow-hidden">
                        <img src={course.image} alt={course.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">{course.title}</h3>
                        <div className="flex items-center justify-between mt-2 text-sm">
                          <div className="flex items-center gap-2 text-gray-500">
                            <HiUserGroup className="w-4 h-4" />
                            <span>{course.students?.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <HiStar className="w-4 h-4 text-yellow-400" />
                            <span className="font-medium">{course.rating}</span>
                          </div>
                        </div>
                        <div className="text-lg font-bold text-gray-900 mt-2">${course.price}</div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </section>

            {/* Reviews */}
            <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Student Reviews</h2>
              <div className="space-y-4">
                {mockReviews.map((review) => (
                  <div key={review.id} className="border-b border-gray-100 last:border-0 pb-4 last:pb-0">
                    <div className="flex items-center gap-3 mb-2">
                      <img src={review.avatar} alt={review.student} className="w-8 h-8 rounded-full object-cover" />
                      <div>
                        <span className="font-medium text-sm text-gray-900">{review.student}</span>
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <HiStar key={i} className={`w-3 h-3 ${i < review.rating ? 'text-yellow-400' : 'text-gray-200'}`} />
                          ))}
                        </div>
                      </div>
                      <span className="text-xs text-gray-400 ml-auto">{review.date}</span>
                    </div>
                    <p className="text-sm text-gray-600 ml-11">{review.text}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>

          {/* Sidebar Stats */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 lg:sticky lg:top-24">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-indigo-50 rounded-xl">
                  <HiStar className="w-6 h-6 text-yellow-500 mx-auto mb-1" />
                  <div className="text-2xl font-bold text-gray-900">{display.rating || mockInstructor.rating}</div>
                  <div className="text-xs text-gray-500">Rating</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-xl">
                  <HiUserGroup className="w-6 h-6 text-green-500 mx-auto mb-1" />
                  <div className="text-2xl font-bold text-gray-900">{(display.studentsCount || mockInstructor.studentsCount) >= 1000 ? `${(display.studentsCount / 1000).toFixed(1)}k` : display.studentsCount}</div>
                  <div className="text-xs text-gray-500">Students</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-xl">
                  <HiPlay className="w-6 h-6 text-purple-500 mx-auto mb-1" />
                  <div className="text-2xl font-bold text-gray-900">{display.coursesCount || mockInstructor.coursesCount}</div>
                  <div className="text-xs text-gray-500">Courses</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-xl">
                  <HiBookOpen className="w-6 h-6 text-orange-500 mx-auto mb-1" />
                  <div className="text-2xl font-bold text-gray-900">{(display.reviewsCount || mockInstructor.reviewsCount) >= 1000 ? `${(display.reviewsCount / 1000).toFixed(1)}k` : display.reviewsCount}</div>
                  <div className="text-xs text-gray-500">Reviews</div>
                </div>
              </div>

              <hr className="my-6" />

              <div className="space-y-3">
                {(() => {
                  const social = display.social || mockInstructor.social;
                  const website = social?.website || '';
                  const twitter = social?.twitter || '';
                  return (
                    <>
                      {website && (
                        <a href={website} target="_blank" rel="noopener noreferrer"
                           className="flex items-center gap-2 text-sm text-gray-600 hover:text-indigo-600 transition-colors">
                          <HiGlobe className="w-4 h-4" />
                          Website
                        </a>
                      )}
                      {twitter && (
                        <a href={`https://twitter.com/${twitter.replace('@', '')}`} target="_blank" rel="noopener noreferrer"
                           className="flex items-center gap-2 text-sm text-gray-600 hover:text-indigo-600 transition-colors">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                          {twitter}
                        </a>
                      )}
                    </>
                  );
                })()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
