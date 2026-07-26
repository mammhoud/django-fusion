'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiCalendar, HiUser, HiArrowLeft, HiTag } from 'react-icons/hi';

function BlogDetailsContent() {
  const searchParams = useSearchParams();
  const postId = searchParams.get('id');

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <Link href="/blog" className="inline-flex items-center gap-2 text-gray-500 hover:text-[rgb(var(--ctc-primary))] mb-8 transition-colors">
        <HiArrowLeft className="w-4 h-4" /> Back to Blog
      </Link>

      <motion.article initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="bg-gradient-to-br card-gradient h-64 rounded-xl flex items-center justify-center mb-8">
          <HiTag className="w-20 h-20 text-white/40" />
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
          <span className="badge-primary">Category</span>
          <span className="flex items-center gap-1"><HiCalendar className="w-4 h-4" /> June 15, 2026</span>
          <span className="flex items-center gap-1"><HiUser className="w-4 h-4" /> Author Name</span>
        </div>

        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">Blog Post Title</h1>

        <div className="prose prose-lg max-w-none text-gray-600 leading-relaxed">
          <p className="lead">This is the blog post content. In a fully integrated version, this would be fetched from the API using <code>useGetBlogPostQuery(postId)</code> and rendered with proper formatting.</p>
          <p>The post content would include rich text, images, code snippets, and more. The RTK Query hook would handle loading states, caching, and revalidation automatically.</p>
        </div>
      </motion.article>
    </div>
  );
}

export default function BlogDetailsPage() {
  return (
    <Suspense fallback={<div className="max-w-4xl mx-auto px-4 py-10"><div className="w-12 h-12 border-4 border-[rgb(var(--ctc-primary))] border-t-transparent rounded-full animate-spin mx-auto" /></div>}>
      <BlogDetailsContent />
    </Suspense>
  );
}
