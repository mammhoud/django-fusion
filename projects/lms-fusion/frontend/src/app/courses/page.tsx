'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Carousel from '@/components/ui/Carousel';
import type { CarouselSlide } from '@/components/ui/Carousel';
import { useToast } from '@/components/ui/Toast';
import { HiAcademicCap, HiStar } from 'react-icons/hi';

interface Course {
  id: number; title: string; slug: string; short_description: string;
  image_url: string | null; instructor: string;
  price: number; original_price: number | null;
  difficulty: string; language: string; duration: number;
  rating: number; reviews_count: number;
  is_featured: boolean; has_certificate: boolean;
}

interface Filters {
  languages: string[]; difficulties: string[];
}

export default function CoursesPage() {
  const [courses, setCourses] = React.useState<Course[]>([]);
  const [pagination, setPagination] = React.useState({ page: 1, total: 0, total_pages: 0 });
  const [filters, setFilters] = React.useState<Filters>({ languages: [], difficulties: [] });
  const [activeFilters, setActiveFilters] = React.useState<{ language?: string; difficulty?: string; q?: string }>({});
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [search, setSearch] = React.useState('');
  const toast = useToast();

  const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5076/api';

  const fetchCourses = async (page = 1) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: String(page), per_page: '12' });
      if (activeFilters.language) params.set('language', activeFilters.language);
      if (activeFilters.difficulty) params.set('difficulty', activeFilters.difficulty);
      if (activeFilters.q) params.set('q', activeFilters.q);

      const res = await fetch(`${API}/courses?${params}`);
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const json = await res.json();
      const data = json.data ? json : { data: json };
      setCourses(data.data || []);
      setPagination(data.pagination || { page: 1, total: 0, total_pages: 0 });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch(`${API}/courses/filters`).then(r => r.json()).then(setFilters).catch(() => {});
  }, []);

  useEffect(() => { fetchCourses(); }, [activeFilters]);

  useEffect(() => {
    const timer = setTimeout(() => {
      toast.info('Explore Courses', 'Discover new skills and advance your career.', 4000);
    }, 1500);
    return () => clearTimeout(timer);
  }, [toast]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setActiveFilters(prev => ({ ...prev, q: search || undefined }));
  };

  // Build featured courses carousel slides
  const featuredCourses = courses.filter(c => c.is_featured);
  const featuredSlides: CarouselSlide[] = featuredCourses.slice(0, 6).map((course) => ({
    id: course.id,
    content: (
      <Link href={`/courses/${course.slug}`} className="card block overflow-hidden group h-full mx-1">
        <div className="h-36 bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center relative">
          {course.image_url ? (
            <img src={course.image_url} alt={course.title} className="w-full h-full object-cover" />
          ) : (
            <HiAcademicCap className="w-10 h-10 text-white/60" />
          )}
          <span className="absolute top-2 right-2 px-2 py-0.5 bg-yellow-400 text-yellow-900 text-xs font-semibold rounded">Featured</span>
        </div>
        <div className="p-4">
          <h3 className="font-semibold text-gray-900 text-sm group-hover:text-teal-700 transition-colors line-clamp-1">{course.title}</h3>
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{course.short_description}</p>
          <div className="flex items-center justify-between mt-3">
            <span className="font-bold text-sm text-gray-900">${course.price.toFixed(2)}</span>
            <span className="flex items-center gap-1 text-xs text-yellow-500">
              <HiStar className="w-3 h-3" />
              <span className="text-gray-600">{course.rating.toFixed(1)}</span>
            </span>
          </div>
        </div>
      </Link>
    ),
  }));

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero */}
      <ScrollReveal animation="fadeUp" duration={0.6}>
        <section className="bg-gradient-to-r from-teal-600 to-cyan-700 text-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">Courses</h1>
            <p className="text-lg text-teal-100 max-w-2xl mx-auto mb-8">
              Expand your knowledge with our comprehensive course catalog
            </p>
            <form onSubmit={handleSearch} className="max-w-xl mx-auto">
              <div className="flex gap-2">
                <input
                  type="text" value={search} onChange={e => setSearch(e.target.value)}
                  placeholder="Search courses..."
                  className="flex-1 px-4 py-3 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-teal-300"
                />
                <button type="submit" className="px-6 py-3 bg-white text-teal-700 font-medium rounded-lg hover:bg-teal-50 transition-colors">
                  Search
                </button>
              </div>
            </form>
          </div>
        </section>
      </ScrollReveal>

      {/* Featured Courses Carousel — only after the API response is in */}
      {!loading && featuredSlides.length > 0 && (
        <ScrollReveal animation="fadeUp" duration={0.5}>
          <section className="bg-white border-b border-gray-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Featured Courses</h2>
              <Carousel
                slides={featuredSlides}
                slidesPerView={{ xs: 1, sm: 2, md: 3, lg: 4 }}
                showArrows={featuredSlides.length > 3}
                showDots={false}
                autoplay={5000}
                loop
                animation="slide"
                gap={16}
                className="pb-2"
              />
            </div>
          </section>
        </ScrollReveal>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <ScrollReveal animation="fadeLeft" duration={0.4}>
            <aside className="lg:w-64 flex-shrink-0">
              <div className="bg-white rounded-xl shadow-sm p-6 space-y-6 sticky top-24">
                <h3 className="font-semibold text-gray-900">Filters</h3>

                {filters.languages.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Language</h4>
                    <div className="space-y-1">
                      <button onClick={() => setActiveFilters(p => ({ ...p, language: undefined }))}
                        className={`block w-full text-left text-sm px-2 py-1 rounded ${!activeFilters.language ? 'bg-teal-100 text-teal-700 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}>
                        All
                      </button>
                      {filters.languages.map(l => (
                        <button key={l} onClick={() => setActiveFilters(p => ({ ...p, language: l }))}
                          className={`block w-full text-left text-sm px-2 py-1 rounded ${activeFilters.language === l ? 'bg-teal-100 text-teal-700 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}>
                          {l}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {filters.difficulties.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Difficulty</h4>
                    <div className="space-y-1">
                      <button onClick={() => setActiveFilters(p => ({ ...p, difficulty: undefined }))}
                        className={`block w-full text-left text-sm px-2 py-1 rounded ${!activeFilters.difficulty ? 'bg-teal-100 text-teal-700 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}>
                        All
                      </button>
                      {filters.difficulties.map(d => (
                        <button key={d} onClick={() => setActiveFilters(p => ({ ...p, difficulty: d }))}
                          className={`block w-full text-left text-sm px-2 py-1 rounded capitalize ${activeFilters.difficulty === d ? 'bg-teal-100 text-teal-700 font-medium' : 'text-gray-600 hover:bg-gray-50'}`}>
                          {d}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {(activeFilters.language || activeFilters.difficulty || activeFilters.q) && (
                  <button onClick={() => { setActiveFilters({}); setSearch(''); }}
                    className="text-sm text-red-600 hover:text-red-800 font-medium">
                    Clear all filters
                  </button>
                )}
              </div>
            </aside>
          </ScrollReveal>

          {/* Course Grid */}
          <main className="flex-1">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="bg-white rounded-xl shadow-sm overflow-hidden">
                    <div className="bg-gray-200 h-48 w-full animate-pulse" />
                    <div className="p-5 space-y-3">
                      <div className="bg-gray-200 h-4 w-1/3 rounded animate-pulse" />
                      <div className="bg-gray-200 h-5 w-3/4 rounded animate-pulse" />
                      <div className="bg-gray-200 h-4 w-full rounded animate-pulse" />
                    </div>
                  </div>
                ))}
              </div>
            ) : error ? (
              <div className="text-center py-16">
                <p className="text-red-500 mb-4">{error}</p>
                <button onClick={() => fetchCourses()} className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700">Retry</button>
              </div>
            ) : courses.length === 0 ? (
              <div className="text-center py-16 text-gray-500">
                <p className="text-xl">No courses found</p>
                <p className="mt-2">Try adjusting your filters or search terms.</p>
              </div>
            ) : (
              <ScrollReveal animation="fadeUp" duration={0.4} threshold={0.02}>
                <div>
                  <p className="text-sm text-gray-500 mb-4">{pagination.total} course{pagination.total !== 1 ? 's' : ''} found</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {courses.map(course => (
                      <Link key={course.id} href={`/courses/${course.slug}`} className="group block bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                        <div className="h-48 bg-gray-200 overflow-hidden relative">
                          {course.image_url ? (
                            <img src={course.image_url} alt={course.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-teal-50 to-cyan-100">
                              <span className="text-teal-400 text-4xl">📚</span>
                            </div>
                          )}
                          {course.is_featured && (
                            <span className="absolute top-3 left-3 px-2 py-1 bg-yellow-400 text-yellow-900 text-xs font-semibold rounded">Featured</span>
                          )}
                        </div>
                        <div className="p-5">
                          <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                            <span className="capitalize">{course.difficulty}</span>
                            <span>·</span>
                            <span>{course.duration}h</span>
                            {course.has_certificate && <span className="text-green-600">· Certificate</span>}
                          </div>
                          <h3 className="font-semibold text-gray-900 group-hover:text-teal-700 transition-colors line-clamp-2 mb-1">{course.title}</h3>
                          <p className="text-sm text-gray-600 line-clamp-2 mb-3">{course.short_description}</p>
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="text-lg font-bold text-gray-900">${course.price.toFixed(2)}</span>
                              {course.original_price && course.original_price > course.price && (
                                <span className="text-sm text-gray-400 line-through ml-2">${course.original_price.toFixed(2)}</span>
                              )}
                            </div>
                            <div className="flex items-center gap-1 text-sm text-yellow-500">
                              <span>★</span>
                              <span className="text-gray-600">{course.rating.toFixed(1)}</span>
                              <span className="text-gray-400">({course.reviews_count})</span>
                            </div>
                          </div>
                          <p className="text-xs text-gray-400 mt-2">by {course.instructor}</p>
                        </div>
                      </Link>
                    ))}
                  </div>

                  {pagination.total_pages > 1 && (
                    <div className="flex justify-center gap-2 mt-10">
                      {Array.from({ length: pagination.total_pages }).map((_, i) => (
                        <button key={i} onClick={() => fetchCourses(i + 1)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            pagination.page === i + 1 ? 'bg-teal-600 text-white' : 'bg-white text-gray-700 hover:bg-teal-50 border border-gray-200'
                          }`}>
                          {i + 1}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </ScrollReveal>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
