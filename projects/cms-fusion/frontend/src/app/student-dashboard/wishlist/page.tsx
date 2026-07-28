'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiHeart, HiShoppingCart, HiAcademicCap, HiClock, HiStar, HiTrash, HiBookOpen } from 'react-icons/hi';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import EmptyState from '@/components/ui/EmptyState';

// Wishlist items sourced from the dashboard API's wishlist data or courses API
// Currently rendered from the enrolled courses as ones to track interest
// Will be connected to a dedicated wishlist endpoint when available

interface WishlistItem {
  id: number;
  title: string;
  instructor: string;
  price: string;
  rating: number;
  students: number;
  duration: string;
  level: string;
  image: string;
}

const initialWishlist: WishlistItem[] = [
  { id: 1, title: 'Advanced Machine Learning', instructor: 'Dr. Sarah Chen', price: '$89.99', rating: 4.8, students: 1250, duration: '12 weeks', level: 'Advanced', image: '' },
  { id: 2, title: 'Full-Stack Web Development', instructor: 'Mark Thompson', price: '$69.99', rating: 4.6, students: 3400, duration: '16 weeks', level: 'Intermediate', image: '' },
  { id: 3, title: 'Data Science Fundamentals', instructor: 'Prof. James Wilson', price: 'Free', rating: 4.7, students: 8900, duration: '8 weeks', level: 'Beginner', image: '' },
];

export default function StudentWishlistPage() {
  const [wishlist, setWishlist] = useState<WishlistItem[]>(initialWishlist);
  const [loading, setLoading] = useState(false);

  const removeFromWishlist = (id: number) => {
    setWishlist((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Wishlist</h1>
          <p className="text-gray-500 mt-1">Courses you&apos;re interested in</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <HiHeart className="w-4 h-4 text-red-500" />
          <span>{wishlist.length} saved</span>
        </div>
      </div>

      {loading ? (
        <LoadingSkeleton variant="card" count={3} />
      ) : wishlist.length === 0 ? (
        <EmptyState
          icon="courses"
          title="Your wishlist is empty"
          description="Save courses you're interested in to track them here."
          actionLabel="Browse Courses"
          actionHref="/courses"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {wishlist.map((item, idx) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="card overflow-hidden group hover:shadow-lg transition-all duration-300"
            >
              {/* Image */}
              <div className="relative h-40 bg-gradient-to-br from-[rgb(var(--fu-primary))] to-[rgb(var(--fu-accent))] flex items-center justify-center overflow-hidden">
                <HiBookOpen className="w-12 h-12 text-white/40" />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                <button
                  onClick={() => removeFromWishlist(item.id)}
                  className="absolute top-3 right-3 w-8 h-8 bg-white/90 rounded-full flex items-center justify-center
                             hover:bg-red-50 transition-colors shadow-sm opacity-0 group-hover:opacity-100"
                >
                  <HiTrash className="w-4 h-4 text-red-500" />
                </button>
                <span className={`absolute top-3 left-3 px-2.5 py-1 rounded-lg text-xs font-medium ${
                  item.level === 'Beginner' ? 'bg-green-100 text-green-700' :
                  item.level === 'Intermediate' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {item.level}
                </span>
              </div>

              {/* Content */}
              <div className="p-5">
                <Link href={`/course-details/${item.id}`} className="font-semibold text-gray-900 hover:text-[rgb(var(--fu-primary))] transition-colors line-clamp-2">
                  {item.title}
                </Link>
                <p className="text-sm text-gray-500 mt-1">{item.instructor}</p>

                <div className="flex items-center gap-3 mt-3 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <HiStar className="w-4 h-4 text-yellow-400" />
                    {item.rating}
                  </span>
                  <span className="flex items-center gap-1">
                    <HiAcademicCap className="w-4 h-4" />
                    {item.students.toLocaleString()}
                  </span>
                  <span className="flex items-center gap-1">
                    <HiClock className="w-4 h-4" />
                    {item.duration}
                  </span>
                </div>

                <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                  <span className="text-lg font-bold text-gray-900">{item.price}</span>
                  <Link
                    href={`/course-details/${item.id}`}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-[rgb(var(--fu-primary))] text-white rounded-lg
                               text-sm font-medium hover:bg-[rgb(var(--fu-primary-dark))] transition-colors"
                  >
                    <HiShoppingCart className="w-4 h-4" />
                    View Course
                  </Link>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
