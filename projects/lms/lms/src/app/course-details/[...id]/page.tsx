'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiStar, HiClock, HiUser, HiAcademicCap, HiPlay, HiCheckCircle, HiArrowLeft } from 'react-icons/hi';
import { useGetCourseQuery } from '@/store/api/endpoints/courses';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

export default function CourseDetailsPage() {
  const params = useParams();
  const courseId = Number(params?.id?.[0] ?? 0);
  const { data: course, isLoading } = useGetCourseQuery(courseId, { skip: !courseId });

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-10">
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  if (!course) {
    return (
      <ErrorState fullPage message="Course not found. It may have been removed or is no longer available." />
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <Link href="/courses" className="inline-flex items-center gap-2 text-gray-500 hover:text-[rgb(var(--ctc-primary))] mb-6 transition-colors">
        <HiArrowLeft className="w-4 h-4" /> Back to Courses
      </Link>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="bg-gradient-to-br from-[rgb(var(--ctc-primary))] to-[rgb(var(--ctc-primary-dark))] rounded-xl p-8 text-white mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="badge bg-white/20 text-white">{course.category_name}</span>
            <span className="badge bg-white/20 text-white">{course.level}</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3">{course.title}</h1>
          <p className="text-white/70 text-lg mb-6">{course.short_description}</p>
          <div className="flex flex-wrap items-center gap-6 text-sm text-white/70">
            <span className="flex items-center gap-1"><HiUser className="w-4 h-4" /> {course.instructor_name}</span>
            <span className="flex items-center gap-1"><HiClock className="w-4 h-4" /> {course.duration}</span>
            <span className="flex items-center gap-1"><HiStar className="w-4 h-4 text-yellow-400" /> {course.rating} ({course.reviews_count})</span>
            <span className="flex items-center gap-1"><HiAcademicCap className="w-4 h-4" /> {course.students_count} students</span>
          </div>
          <div className="mt-6">
            <span className="text-3xl font-bold">${course.discounted_price || course.price}</span>
            {course.discounted_price && <span className="text-lg line-through text-white/40 ml-2">${course.price}</span>}
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-8">
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4">About This Course</h2>
              <p className="text-gray-600 leading-relaxed">{course.description}</p>
            </section>

            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Course Curriculum</h2>
              <div className="space-y-2">
                {course.curriculum?.map((lesson, idx) => (
                  <div key={lesson.id} className="card p-4 flex items-center gap-3">
                    <div className="w-10 h-10 bg-[rgb(var(--ctc-primary))]/10 rounded-full flex items-center justify-center flex-shrink-0">
                      {lesson.is_free ? <HiPlay className="w-5 h-5 text-[rgb(var(--ctc-primary))]" /> : <HiCheckCircle className="w-5 h-5 text-[rgb(var(--ctc-primary))]" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900">{idx + 1}. {lesson.title}</p>
                      <p className="text-sm text-gray-500">{lesson.duration} {lesson.is_free && <span className="text-green-600 font-medium ml-2">Free</span>}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="card p-6 h-fit lg:sticky lg:top-24">
            <Link href={`/lesson`} className="btn-primary w-full text-center block mb-4">
              Start Learning
            </Link>
            <div className="space-y-3 text-sm text-gray-500">
              <div className="flex justify-between"><span>Duration</span><span className="text-gray-700 font-medium">{course.duration}</span></div>
              <div className="flex justify-between"><span>Level</span><span className="text-gray-700 font-medium capitalize">{course.level}</span></div>
              <div className="flex justify-between"><span>Language</span><span className="text-gray-700 font-medium">{course.language}</span></div>
              <div className="flex justify-between"><span>Students</span><span className="text-gray-700 font-medium">{course.students_count}</span></div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
