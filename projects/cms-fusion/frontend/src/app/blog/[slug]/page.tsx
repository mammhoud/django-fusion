'use client';

import React from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5075/apis';

interface BlogPostDetail {
  id: number; title: string; slug: string; content: string; excerpt: string;
  author: { name: string; id: number | null };
  published_date: string | null;
  featured_image_url: string | null;
  categories: { slug: string; name: string }[];
  tags: { slug: string; name: string }[];
  reading_time: number; likes_count: number;
  meta_description: string;
  related_posts: { title: string; slug: string; excerpt: string; featured_image_url: string | null }[];
}

export default function BlogPostPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [post, setPost] = React.useState<BlogPostDetail | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5075/apis'}/blog/${slug}`);
        if (!res.ok) throw new Error(`Post not found (${res.status})`);
        const data = await res.json();
        setPost(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load post');
      } finally {
        setLoading(false);
      }
    })();
  }, [slug]);

  if (loading) return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-4 py-16 space-y-6">
        <div className="fusion-skeleton h-8 w-1/4" />
        <div className="fusion-skeleton h-12 w-3/4" />
        <div className="fusion-skeleton h-64 w-full rounded-xl" />
        <div className="space-y-3">
          <div className="fusion-skeleton h-4 w-full" />
          <div className="fusion-skeleton h-4 w-5/6" />
          <div className="fusion-skeleton h-4 w-4/6" />
        </div>
      </div>
    </div>
  );

  if (error || !post) return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Post Not Found</h2>
        <p className="text-gray-500 mb-4">{error || 'This post does not exist.'}</p>
        <Link href="/blog" className="text-purple-600 hover:text-purple-800 font-medium">← Back to Blog</Link>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-white">
      {/* Featured Image */}
      {post.featured_image_url && (
        <div className="w-full h-64 md:h-96 overflow-hidden">
          <img src={post.featured_image_url} alt={post.title} className="w-full h-full object-cover" />
        </div>
      )}

      <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-gray-500 mb-6">
          <Link href="/blog" className="hover:text-purple-700">Blog</Link>
          <span>/</span>
          {post.categories?.[0] && (
            <>
              <Link href={`/blog?category=${post.categories[0].slug}`} className="hover:text-purple-700">{post.categories[0].name}</Link>
              <span>/</span>
            </>
          )}
          <span className="text-gray-900 truncate">{post.title}</span>
        </nav>

        {/* Meta */}
        <div className="flex flex-wrap items-center gap-3 mb-4">
          {post.categories.map((cat) => (
            <Link key={cat.slug} href={`/blog?category=${cat.slug}`}
              className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium hover:bg-purple-200">
              {cat.name}
            </Link>
          ))}
          <span className="text-sm text-gray-400">{post.reading_time} min read</span>
        </div>

        {/* Title */}
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">{post.title}</h1>

        {/* Author & Date */}
        <div className="flex items-center gap-3 mb-8 text-sm text-gray-500">
          <span className="font-medium text-gray-700">{post.author.name}</span>
          <span>·</span>
          <span>{post.published_date ? new Date(post.published_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : ''}</span>
        </div>

        {/* Content */}
        <div className="prose prose-lg max-w-none prose-headings:text-gray-900 prose-a:text-purple-600 prose-img:rounded-xl" dangerouslySetInnerHTML={{ __html: post.content }} />

        {/* Tags */}
        {post.tags.length > 0 && (
          <div className="mt-10 pt-8 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {post.tags.map((tag) => (
                <Link key={tag.slug} href={`/blog?tag=${tag.slug}`}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs hover:bg-gray-200 transition-colors">
                  #{tag.name}
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Related Posts */}
        {post.related_posts.length > 0 && (
          <div className="mt-12 pt-8 border-t border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Posts</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {post.related_posts.map((rp) => (
                <Link key={rp.slug} href={`/blog/${rp.slug}`} className="group block bg-gray-50 rounded-xl overflow-hidden hover:bg-gray-100 transition-colors">
                  {rp.featured_image_url && (
                    <div className="h-40 overflow-hidden">
                      <img src={rp.featured_image_url} alt={rp.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                    </div>
                  )}
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 group-hover:text-purple-700 transition-colors line-clamp-2">{rp.title}</h3>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">{rp.excerpt}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <Link href="/blog" className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-800 font-medium">
            ← Back to Blog
          </Link>
        </div>
      </article>
    </div>
  );
}
