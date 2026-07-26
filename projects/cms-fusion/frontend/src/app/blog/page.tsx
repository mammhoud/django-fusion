'use client';

import React from 'react';
import Link from 'next/link';
import { fusionApi } from '@/lib/api-client';
import { fusionDecoder } from '@/lib/fusion-decoder';

interface BlogPost {
  id: number; title: string; slug: string; excerpt: string;
  author: string; published_date: string | null;
  featured_image_url: string | null;
  categories: { slug: string; name: string }[];
  tags: { slug: string; name: string }[];
  reading_time: number;
}

export default function BlogPage() {
  const [posts, setPosts] = React.useState<BlogPost[]>([]);
  const [pagination, setPagination] = React.useState({ page: 1, total: 0, total_pages: 0 });
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  const fetchPosts = async (page = 1) => {
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5075/api'}/blog?page=${page}&per_page=9`);
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const json = await res.json();
      const data = fusionDecoder.unwrap<{ data: BlogPost[]; pagination: { page: number; total: number; total_pages: number } }>(json.data ? json : { status: 200, message: 'OK', data: json });
      setPosts(data.data || []);
      setPagination(data.pagination || { page: 1, total: 0, total_pages: 0 });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load posts');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => { fetchPosts(); }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero */}
      <section className="bg-gradient-to-r from-purple-700 to-violet-800 text-white py-16" style={{ background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Blog</h1>
          <p className="text-lg text-purple-200 max-w-2xl mx-auto">
            Insights, tutorials, and updates from the Fusion CMS team
          </p>
        </div>
      </section>

      {/* Posts Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-white rounded-xl shadow-sm overflow-hidden">
                <div className="fusion-skeleton h-48 w-full" />
                <div className="p-6 space-y-3">
                  <div className="fusion-skeleton h-4 w-1/4" />
                  <div className="fusion-skeleton h-6 w-3/4" />
                  <div className="fusion-skeleton h-4 w-full" />
                  <div className="fusion-skeleton h-4 w-2/3" />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-16">
            <p className="text-red-500 mb-4">{error}</p>
            <button onClick={() => fetchPosts()} className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">Retry</button>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <p className="text-xl">No blog posts yet</p>
            <p className="mt-2">Check back soon for new content.</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {posts.map((post) => (
                <Link key={post.id} href={`/blog/${post.slug}`} className="group block bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                  <div className="h-48 bg-gray-200 overflow-hidden">
                    {post.featured_image_url ? (
                      <img src={post.featured_image_url} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-100 to-violet-200">
                        <span className="text-purple-400 text-4xl">📝</span>
                      </div>
                    )}
                  </div>
                  <div className="p-6">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                      {post.categories?.[0] && (
                        <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full">{post.categories[0].name}</span>
                      )}
                      <span>{post.reading_time} min read</span>
                    </div>
                    <h2 className="text-lg font-semibold text-gray-900 group-hover:text-purple-700 transition-colors line-clamp-2 mb-2">
                      {post.title}
                    </h2>
                    <p className="text-sm text-gray-600 line-clamp-2">{post.excerpt}</p>
                    <div className="flex items-center gap-2 mt-4 text-xs text-gray-400">
                      <span>{post.author}</span>
                      <span>·</span>
                      <span>{post.published_date ? new Date(post.published_date).toLocaleDateString() : ''}</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {pagination.total_pages > 1 && (
              <div className="flex justify-center gap-2 mt-12">
                {Array.from({ length: pagination.total_pages }).map((_, i) => (
                  <button
                    key={i}
                    onClick={() => fetchPosts(i + 1)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      pagination.page === i + 1
                        ? 'bg-purple-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-purple-50 border border-gray-200'
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}
