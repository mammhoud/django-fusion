'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiSearch, HiStar, HiBookOpen, HiFilter } from 'react-icons/hi';
import { useGetCoursesQuery, useGetCategoriesQuery } from '@/store/api/endpoints/courses';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function CoursesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [level, setLevel] = useState('');

  const { data, isLoading, error } = useGetCoursesQuery({ page, search, category, level });
  const { data: categories } = useGetCategoriesQuery();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Explore Courses</h1>
        <p className="text-gray-500 mt-2">Discover courses from expert instructors</p>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="flex-1 relative">
          <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search courses..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="input-field pl-10"
          />
        </div>
        <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}
                className="input-field md:w-48">
          <option value="">All Categories</option>
          {categories?.map((cat) => (
            <option key={cat.id} value={cat.slug}>{cat.name}</option>
          ))}
        </select>
        <select value={level} onChange={(e) => { setLevel(e.target.value); setPage(1); }}
                className="input-field md:w-40">
          <option value="">All Levels</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      {/* Course Grid */}
      {isLoading ? (
        <LoadingSkeleton variant="card" count={6} />
      ) : error ? (
        <ErrorState message="Failed to load courses. Please try again." onRetry={() => window.location.reload()} />
      ) : data && data.results.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {data?.results.map((course, idx) => (
              <motion.div
                key={course.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.03 }}
              >
                <Link href={`/course-details/${course.id}`} className="card block overflow-hidden group h-full">
                  <div className="bg-gradient-to-br card-gradient h-40 flex items-center justify-center">
                    <HiBookOpen className="w-12 h-12 text-white/60" />
                  </div>
                  <div className="p-5">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="badge-primary text-xs">{course.category_name}</span>
                      <span className="badge bg-gray-100 text-gray-600 text-xs">{course.level}</span>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-[rgb(var(--ctc-primary))] transition-colors line-clamp-2">
                      {course.title}
                    </h3>
                    <p className="text-sm text-gray-500 mb-3 line-clamp-2">{course.short_description}</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">{course.instructor_name}</span>
                      <span className="font-bold text-[rgb(var(--ctc-primary))]">${course.discounted_price || course.price}</span>
                    </div>
                    <div className="flex items-center gap-3 mt-3 text-sm text-gray-500">
                      <span>{course.duration}</span>
                      <span>·</span>
                      <span className="flex items-center gap-1">
                        <HiStar className="w-4 h-4 text-yellow-400" />
                        {course.rating} ({course.reviews_count})
                      </span>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>

          {/* Pagination */}
          {data && Math.ceil(data.count / 10) > 1 && (
            <div className="flex justify-center gap-2 mt-10">
              {Array.from({ length: Math.ceil(data.count / 10) }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                    p === page ? 'bg-[rgb(var(--ctc-primary))] text-white' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </>
      ) : (
        <EmptyState icon="courses" title="No courses found" description="No courses match your current filters. Try adjusting your search criteria." />
      )}
    </div>
  );
}
