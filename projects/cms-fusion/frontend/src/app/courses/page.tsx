'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiSearch, HiStar, HiBookOpen, HiFilter } from 'react-icons/hi';
import { useGetCoursesQuery, useGetCategoriesQuery } from '@/store/api/endpoints/courses';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Carousel from '@/components/ui/Carousel';
import type { CarouselSlide } from '@/components/ui/Carousel';
import { useToast } from '@/components/ui/Toast';

export default function CoursesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [level, setLevel] = useState('');
  const { info: toastInfo } = useToast();

  const { data, isLoading, error } = useGetCoursesQuery({ page, search, category, level });
  const { data: categories } = useGetCategoriesQuery();

  useEffect(() => {
    const timer = setTimeout(() => {
      toastInfo('Explore Courses', 'Discover courses from expert instructors.', 4000);
    }, 1500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Build carousel slides from top courses
  const courseSlides: CarouselSlide[] = (data?.results ?? []).slice(0, 6).map((course) => ({
    id: course.id,
    content: (
      <Link href={`/course-details/${course.id}`} className="card block overflow-hidden group h-full mx-1">
        <div className="bg-gradient-to-br card-gradient h-32 flex items-center justify-center">
          <HiBookOpen className="w-10 h-10 text-white/60" />
        </div>
        <div className="p-4">
          <span className="badge-primary text-xs mb-2 inline-block">{course.category_name}</span>
          <h3 className="font-semibold text-gray-900 text-sm group-hover:text-[rgb(var(--fu-primary))] transition-colors line-clamp-1">{course.title}</h3>
          <div className="flex items-center justify-between mt-3">
            <span className="font-bold text-sm text-[rgb(var(--fu-primary))]">${course.discounted_price || course.price}</span>
            <span className="flex items-center gap-1 text-xs">
              <HiStar className="w-3 h-3 text-yellow-400" />
              <span className="text-gray-500">{course.rating}</span>
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">{course.instructor_name}</p>
        </div>
      </Link>
    ),
  }));

  return (
    <ScrollReveal animation="fadeUp" duration={0.5}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Explore Courses</h1>
          <p className="text-gray-500 mt-2">Discover courses from expert instructors</p>
        </div>

        {/* Search & Filters */}
        <ScrollReveal animation="fadeUp" delay={0.05} duration={0.4}>
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
        </ScrollReveal>

        {/* Courses Carousel */}
        {!isLoading && courseSlides.length > 0 && (
          <ScrollReveal animation="fadeUp" delay={0.1} duration={0.4}>
            <section className="mb-10">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <HiStar className="w-5 h-5 text-[rgb(var(--fu-primary))]" />
                Top Courses
              </h2>
              <Carousel
                slides={courseSlides}
                slidesPerView={{ xs: 1, sm: 2, md: 3, lg: 4 }}
                showArrows={courseSlides.length > 3}
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

        {/* Course Grid */}
        {isLoading ? (
          <LoadingSkeleton variant="card" count={6} />
        ) : error ? (
          <ErrorState message="Failed to load courses. Please try again." onRetry={() => window.location.reload()} />
        ) : data && data.results.length > 0 ? (
          <ScrollReveal animation="fadeUp" duration={0.4} threshold={0.02}>
            <div>
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
                        <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-[rgb(var(--fu-primary))] transition-colors line-clamp-2">
                          {course.title}
                        </h3>
                        <p className="text-sm text-gray-500 mb-3 line-clamp-2">{course.short_description}</p>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-500">{course.instructor_name}</span>
                          <span className="font-bold text-[rgb(var(--fu-primary))]">${course.discounted_price || course.price}</span>
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
                        p === page ? 'bg-[rgb(var(--fu-primary))] text-white' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </ScrollReveal>
        ) : (
          <EmptyState icon="courses" title="No courses found" description="No courses match your current filters. Try adjusting your search criteria." />
        )}
      </div>
    </ScrollReveal>
  );
}
