'use client';

import React from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

interface CourseDetail {
  id: number; title: string; slug: string;
  description: string; short_description: string; overview: string;
  image_url: string | null; preview_video_url: string;
  instructor: { name: string; bio: string };
  price: number; original_price: number | null; discount_percentage: number;
  difficulty: string; language: string; duration: number;
  rating: number; reviews_count: number; enrollment_count: number;
  is_featured: boolean; has_certificate: boolean;
  modules: { id: number; title: string; description: string; lessons: { id: number; title: string; is_preview: boolean; duration: number }[] }[];
  requirements: string[];
}

export default function CourseDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [course, setCourse] = React.useState<CourseDetail | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5075/api'}/courses/${slug}`);
        if (!res.ok) throw new Error(`Course not found (${res.status})`);
        const data = await res.json();
        setCourse(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load course');
      } finally {
        setLoading(false);
      }
    })();
  }, [slug]);

  if (loading) return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-4 py-16 space-y-6">
        <div className="fusion-skeleton h-8 w-1/4" />
        <div className="fusion-skeleton h-12 w-1/2" />
        <div className="fusion-skeleton h-96 w-full rounded-xl" />
      </div>
    </div>
  );

  if (error || !course) return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Course Not Found</h2>
        <p className="text-gray-500 mb-4">{error || 'This course does not exist.'}</p>
        <Link href="/courses" className="text-purple-600 hover:text-purple-800 font-medium">← Back to Courses</Link>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-white">
      {/* Hero */}
      <section className="bg-gray-900 text-white py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex items-center gap-2 text-sm text-gray-400 mb-4">
            <Link href="/courses" className="hover:text-white">Courses</Link>
            <span>/</span>
            <span className="text-white">{course.title}</span>
          </nav>
          <div className="flex flex-col lg:flex-row gap-8 items-start">
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-3">
                {course.is_featured && <span className="px-2 py-1 bg-yellow-500 text-yellow-900 text-xs font-semibold rounded">Featured</span>}
                {course.has_certificate && <span className="px-2 py-1 bg-green-500 text-white text-xs font-semibold rounded">Certificate</span>}
              </div>
              <h1 className="text-3xl md:text-4xl font-bold mb-3">{course.title}</h1>
              <p className="text-gray-300 text-lg mb-4">{course.short_description}</p>
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400">
                <span className="flex items-center gap-1">★ <span className="text-yellow-400 font-medium">{course.rating.toFixed(1)}</span> ({course.reviews_count} reviews)</span>
                <span>{course.enrollment_count} enrolled</span>
                <span className="capitalize">{course.difficulty}</span>
                <span>{course.language}</span>
                <span>{course.duration}h</span>
              </div>
              <p className="text-sm text-gray-400 mt-2">by {course.instructor.name}</p>
            </div>
            {/* Pricing Card */}
            <div className="lg:w-80 bg-white text-gray-900 rounded-xl p-6 shadow-lg">
              {course.image_url && (
                <img src={course.image_url} alt={course.title} className="w-full h-40 object-cover rounded-lg mb-4" />
              )}
              <div className="mb-4">
                <span className="text-3xl font-bold">${course.price.toFixed(2)}</span>
                {course.original_price && course.original_price > course.price && (
                  <>
                    <span className="text-lg text-gray-400 line-through ml-2">${course.original_price.toFixed(2)}</span>
                    <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded">{course.discount_percentage}% off</span>
                  </>
                )}
              </div>
              <button className="w-full py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors mb-3">
                Enroll Now
              </button>
              <button className="w-full py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors">
                Add to Wishlist
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col lg:flex-row gap-12">
          {/* Main Content */}
          <div className="flex-1">
            {/* Description */}
            {course.description && (
              <section className="mb-10">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">About This Course</h2>
                <div className="prose max-w-none text-gray-700" dangerouslySetInnerHTML={{ __html: course.description }} />
              </section>
            )}

            {/* Requirements */}
            {course.requirements.length > 0 && (
              <section className="mb-10">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Requirements</h2>
                <ul className="list-disc list-inside space-y-1 text-gray-700">
                  {course.requirements.map((req, i) => <li key={i}>{req}</li>)}
                </ul>
              </section>
            )}

            {/* Curriculum */}
            {course.modules.length > 0 && (
              <section>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Curriculum</h2>
                <div className="space-y-3">
                  {course.modules.map((mod, mi) => (
                    <details key={mod.id} className="bg-gray-50 rounded-xl overflow-hidden" open={mi === 0}>
                      <summary className="px-6 py-4 cursor-pointer hover:bg-gray-100 font-medium text-gray-900 flex items-center justify-between">
                        <span>{mod.title}</span>
                        <span className="text-sm text-gray-500">{mod.lessons.length} lessons</span>
                      </summary>
                      <div className="px-6 pb-4 space-y-2">
                        {mod.description && <p className="text-sm text-gray-500 mb-2">{mod.description}</p>}
                        {mod.lessons.map(lesson => (
                          <div key={lesson.id} className="flex items-center justify-between py-2 px-3 bg-white rounded-lg text-sm">
                            <div className="flex items-center gap-2">
                              <span className="text-gray-400">{lesson.is_preview ? '👁' : '🔒'}</span>
                              <span className="text-gray-700">{lesson.title}</span>
                              {lesson.is_preview && <span className="text-xs text-purple-600 font-medium">Preview</span>}
                            </div>
                            <span className="text-gray-400 text-xs">{lesson.duration} min</span>
                          </div>
                        ))}
                      </div>
                    </details>
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* Sidebar */}
          <aside className="lg:w-72 flex-shrink-0">
            {/* Instructor */}
            <div className="bg-gray-50 rounded-xl p-6 mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Instructor</h3>
              <p className="font-medium text-gray-800">{course.instructor.name}</p>
              {course.instructor.bio && <p className="text-sm text-gray-600 mt-2">{course.instructor.bio}</p>}
            </div>

            {/* Quick Info */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Course Info</h3>
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between"><dt className="text-gray-500">Difficulty</dt><dd className="text-gray-900 capitalize">{course.difficulty}</dd></div>
                <div className="flex justify-between"><dt className="text-gray-500">Language</dt><dd className="text-gray-900">{course.language}</dd></div>
                <div className="flex justify-between"><dt className="text-gray-500">Duration</dt><dd className="text-gray-900">{course.duration}h</dd></div>
                <div className="flex justify-between"><dt className="text-gray-500">Certificate</dt><dd className="text-gray-900">{course.has_certificate ? 'Yes' : 'No'}</dd></div>
                <div className="flex justify-between"><dt className="text-gray-500">Enrolled</dt><dd className="text-gray-900">{course.enrollment_count}</dd></div>
              </dl>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
