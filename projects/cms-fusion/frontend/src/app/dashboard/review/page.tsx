'use client';

import { useState } from 'react';
import { HiStar, HiThumbUp, HiFlag, HiChat, HiSearch } from 'react-icons/hi';
import EmptyState from '@/components/ui/EmptyState';
import ErrorState from '@/components/ui/ErrorState';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';

const mockReviews = [
  { id: 'r1', student: 'Alex M.', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50', course: 'Advanced React Development', rating: 5, text: 'Excellent course! The projects were very practical and the instructor explained complex concepts clearly. Highly recommended for anyone looking to level up their React skills.', date: '2 days ago', helpful: 12, replied: false },
  { id: 'r2', student: 'Jessica L.', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=50', course: 'Full-Stack TypeScript', rating: 4, text: 'Great content overall. Would love to see more real-world project examples. The section on generics was particularly helpful.', date: '1 week ago', helpful: 8, replied: true },
  { id: 'r3', student: 'David R.', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=50', course: 'Advanced React Development', rating: 5, text: 'One of the best React courses I have taken. The instructor provides clear explanations and great code examples.', date: '2 weeks ago', helpful: 15, replied: false },
  { id: 'r4', student: 'Sarah K.', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=50', course: 'Python for Data Science', rating: 3, text: 'Good course but some sections felt rushed. The pandas section could use more detailed explanations.', date: '3 weeks ago', helpful: 5, replied: false },
  { id: 'r5', student: 'Michael B.', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=50', course: 'Advanced React Development', rating: 5, text: 'Absolutely worth every penny. The instructor engagement in the Q&A section was outstanding.', date: '1 month ago', helpful: 20, replied: true },
];

export default function DashboardReviewPage() {
  const { data: profile } = useGetProfileQuery();
  const [searchQuery, setSearchQuery] = useState('');
  const [ratingFilter, setRatingFilter] = useState<number | null>(null);

  if (profile?.role !== 'instructor') {
    return <ErrorState fullPage message="This page is only available for instructors." />;
  }

  const filtered = mockReviews.filter((r) => {
    const matchesSearch = r.student.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.course.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.text.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRating = ratingFilter ? r.rating === ratingFilter : true;
    return matchesSearch && matchesRating;
  });

  const avgRating = (mockReviews.reduce((sum, r) => sum + r.rating, 0) / mockReviews.length).toFixed(1);
  const ratingCounts = [0, 0, 0, 0, 0];
  mockReviews.forEach((r) => ratingCounts[r.rating - 1]++);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Reviews</h1>
          <p className="text-sm text-gray-500 mt-1">Manage feedback from your students</p>
        </div>

        {/* Rating Summary */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6">
          <div className="flex items-center gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-gray-900">{avgRating}</div>
              <div className="flex items-center gap-0.5 mt-1">
                {[...Array(5)].map((_, i) => (
                  <HiStar key={i} className={`w-4 h-4 ${i < Math.round(Number(avgRating)) ? 'text-yellow-400' : 'text-gray-200'}`} />
                ))}
              </div>
              <div className="text-xs text-gray-500 mt-1">{mockReviews.length} reviews</div>
            </div>
            <div className="flex-1 space-y-1">
              {[5, 4, 3, 2, 1].map((star) => (
                <div key={star} className="flex items-center gap-2 text-sm">
                  <span className="w-6 text-right text-gray-600">{star}</span>
                  <HiStar className="w-3.5 h-3.5 text-yellow-400" />
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-yellow-400 rounded-full" style={{ width: `${(ratingCounts[star - 1] / mockReviews.length) * 100}%` }} />
                  </div>
                  <span className="w-6 text-right text-gray-500">{ratingCounts[star - 1]}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Search & Filter */}
        <div className="flex items-center gap-3 mb-6">
          <div className="relative flex-1">
            <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search reviews..."
              className="w-full pl-9 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-[rgb(var(--ctc-primary))] focus:border-transparent outline-none text-sm" />
          </div>
          <div className="flex gap-1">
            {[null, 5, 4, 3, 2, 1].map((r) => (
              <button key={r === null ? 'all' : r} onClick={() => setRatingFilter(r)}
                className={`px-3 py-2 text-sm rounded-lg transition-all ${ratingFilter === r ? 'bg-[rgb(var(--ctc-primary))] text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
                {r === null ? 'All' : r + '★'}
              </button>
            ))}
          </div>
        </div>

        {/* Reviews List */}
        <div className="space-y-3">
          {filtered.length === 0 ? (
            <EmptyState icon="messages" title="No reviews found" description={searchQuery ? 'No reviews match your search.' : 'No reviews yet for your courses.'} />
          ) : filtered.map((review) => (
            <div key={review.id} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <img src={review.avatar} alt="" className="w-10 h-10 rounded-full object-cover flex-shrink-0" />
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <div>
                      <span className="font-medium text-gray-900 text-sm">{review.student}</span>
                      <span className="text-gray-300 mx-2">·</span>
                      <span className="text-xs text-gray-500">{review.course}</span>
                    </div>
                    <span className="text-xs text-gray-400">{review.date}</span>
                  </div>
                  <div className="flex items-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => <HiStar key={i} className={`w-3.5 h-3.5 ${i < review.rating ? 'text-yellow-400' : 'text-gray-200'}`} />)}
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed">{review.text}</p>
                  <div className="flex items-center gap-4 mt-3">
                    <button className="flex items-center gap-1 text-xs text-gray-400 hover:text-[rgb(var(--ctc-primary))] transition-colors"><HiThumbUp className="w-3.5 h-3.5" /> Helpful ({review.helpful})</button>
                    <button className="flex items-center gap-1 text-xs text-gray-400 hover:text-[rgb(var(--ctc-primary))] transition-colors"><HiFlag className="w-3.5 h-3.5" /> Report</button>
                    <button className={`flex items-center gap-1 text-xs transition-colors ${review.replied ? 'text-green-600' : 'text-gray-400 hover:text-[rgb(var(--ctc-primary))]'}`}>
                      <HiChat className="w-3.5 h-3.5" /> {review.replied ? 'Replied' : 'Reply'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
