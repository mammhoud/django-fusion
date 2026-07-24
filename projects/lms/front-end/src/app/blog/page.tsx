'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiCalendar, HiUser, HiTag, HiArrowRight } from 'react-icons/hi';
import { useGetBlogPostsQuery, useGetBlogCategoriesQuery } from '@/store/api/endpoints/blog';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function BlogPage() {
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');

  const { data, isLoading } = useGetBlogPostsQuery({ page, category, search });
  const { data: categories } = useGetBlogCategoriesQuery();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Blog</h1>
        <p className="text-gray-500 mt-2">Insights, tutorials, and updates from our community</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <input type="text" placeholder="Search posts..." value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="input-field flex-1" />
        <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}
          className="input-field md:w-48">
          <option value="">All Categories</option>
          {categories?.map((cat) => (
            <option key={cat.id} value={cat.slug}>{cat.name} ({cat.post_count})</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <LoadingSkeleton variant="card" count={6} />
      ) : data && data.results.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {data?.results.map((post, idx) => (
              <motion.div key={post.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.03 }}>
                <Link href={`/blog-details`} className="card block overflow-hidden group h-full">
                  <div className="bg-gradient-to-br from-indigo-500 to-purple-600 h-40 flex items-center justify-center">
                    <HiTag className="w-12 h-12 text-white/60" />
                  </div>
                  <div className="p-5">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                      <span className="badge-primary">{post.category_name}</span>
                      <span className="flex items-center gap-1"><HiCalendar className="w-3 h-3" />{new Date(post.created_at).toLocaleDateString()}</span>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors line-clamp-2">{post.title}</h3>
                    <p className="text-sm text-gray-500 line-clamp-2 mb-3">{post.excerpt}</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-1 text-gray-500"><HiUser className="w-3 h-3" />{post.author_name}</span>
                      <span className="text-indigo-600 font-medium flex items-center gap-1">Read More <HiArrowRight className="w-3 h-3" /></span>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>

          {data && Math.ceil(data.count / 10) > 1 && (
            <div className="flex justify-center gap-2 mt-10">
              {Array.from({ length: Math.ceil(data.count / 10) }, (_, i) => i + 1).map(p => (
                <button key={p} onClick={() => setPage(p)}
                  className={`w-10 h-10 rounded-lg font-medium transition-colors ${p === page ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'}`}>{p}</button>
              ))}
            </div>
          )}
        </>
      ) : (
        <EmptyState icon="blog" title="No posts found" description="No blog posts match your current filters." />
      )}
    </div>
  );
}
