'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiStar, HiTrash, HiPencil, HiAcademicCap, HiClock } from 'react-icons/hi';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetStudentEnrollmentsQuery } from '@/store/api/endpoints/students';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import EmptyState from '@/components/ui/EmptyState';

export default function StudentReviewsPage() {
  const { data: profile } = useGetProfileQuery();
  const { data: enrollments, isLoading } = useGetStudentEnrollmentsQuery(profile?.id ?? 0, {
    skip: !profile?.id,
  });

  // Filter to only completed courses (those that can be reviewed)
  const reviewableCourses = (enrollments || []).filter((e) => e.is_completed || e.progress > 50);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Reviews</h1>
        <p className="text-gray-500 mt-1">Rate and review courses you&apos;ve taken</p>
      </div>

      {isLoading ? (
        <LoadingSkeleton variant="card" count={3} />
      ) : reviewableCourses.length === 0 ? (
        <EmptyState
          icon="courses"
          title="No courses to review yet"
          description="Complete more course content to leave reviews."
          actionLabel="Browse Courses"
          actionHref="/courses"
        />
      ) : (
        <div className="space-y-4">
          {reviewableCourses.map((enrollment, idx) => (
            <ReviewCard key={enrollment.id} enrollment={enrollment} index={idx} />
          ))}
        </div>
      )}
    </div>
  );
}

function ReviewCard({ enrollment, index }: { enrollment: any; index: number }) {
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) return;
    // Placeholder: would connect to a POST /apis/reviews endpoint
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="card p-6"
    >
      <div className="flex items-start gap-4">
        {/* Course Thumbnail */}
        <div className="w-20 h-20 bg-gradient-to-br from-[rgb(var(--fu-primary))] to-[rgb(var(--fu-accent))] rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden">
          {enrollment.course_thumbnail ? (
            <img src={enrollment.course_thumbnail} alt="" className="w-full h-full object-cover" />
          ) : (
            <HiAcademicCap className="w-8 h-8 text-white/60" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <Link
            href={`/course-details/${enrollment.course}`}
            className="font-semibold text-gray-900 hover:text-[rgb(var(--fu-primary))] transition-colors"
          >
            {enrollment.course_title}
          </Link>
          <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <HiClock className="w-4 h-4" />
              Progress: {Math.round(enrollment.progress)}%
            </span>
            <span className="flex items-center gap-1">
              <HiAcademicCap className="w-4 h-4" />
              {enrollment.instructor_name || 'Instructor'}
            </span>
          </div>

          {submitted ? (
            <div className="mt-4 flex items-center gap-2 text-green-600 bg-green-50 px-4 py-3 rounded-xl">
              <HiStar className="w-5 h-5" />
              <span className="text-sm font-medium">Review submitted! Thank you for your feedback.</span>
            </div>
          ) : (
            <div className="mt-4">
              {/* Star Rating */}
              <div className="flex items-center gap-1 mb-3">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoveredStar(star)}
                    onMouseLeave={() => setHoveredStar(0)}
                    className="transition-transform hover:scale-110"
                  >
                    <HiStar
                      className={`w-6 h-6 ${
                        star <= (hoveredStar || rating)
                          ? 'text-yellow-400 fill-current'
                          : 'text-gray-300'
                      }`}
                    />
                  </button>
                ))}
                <span className="text-sm text-gray-500 ml-2">
                  {rating > 0 ? `${rating}/5` : 'Click to rate'}
                </span>
              </div>

              {/* Comment */}
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Share your experience with this course..."
                rows={3}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm resize-none
                           focus:ring-2 focus:ring-[rgb(var(--fu-primary))] focus:border-transparent outline-none
                           placeholder:text-gray-400"
              />

              {/* Submit */}
              <div className="flex justify-end mt-3">
                <button
                  onClick={handleSubmit}
                  disabled={rating === 0}
                  className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${
                    rating > 0
                      ? 'bg-[rgb(var(--fu-primary))] text-white hover:bg-[rgb(var(--fu-primary-dark))]'
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  Submit Review
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
