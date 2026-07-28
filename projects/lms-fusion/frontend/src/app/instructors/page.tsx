'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiStar, HiAcademicCap, HiUserGroup } from 'react-icons/hi';
import { useGetInstructorsQuery } from '@/store/api/endpoints/instructors';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function InstructorsPage() {
  const { data, isLoading } = useGetInstructorsQuery({ page: 1 });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Our Instructors</h1>
        <p className="text-gray-500 mt-2">Learn from industry experts and experienced educators</p>
      </div>

      {isLoading ? (
        <LoadingSkeleton variant="card" count={4} />
      ) : data && data.results.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {data?.results.map((instructor, idx) => (
            <motion.div key={instructor.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }}
              className="card p-6 text-center hover:shadow-lg transition-shadow">
              <div className="w-20 h-20 bg-gradient-to-br from-[rgb(var(--fu-primary))] to-[rgb(var(--fu-accent))] rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-bold">
                {instructor.first_name?.[0]}{instructor.last_name?.[0]}
              </div>
              <h3 className="font-semibold text-gray-900">{instructor.first_name} {instructor.last_name}</h3>
              <p className="text-sm text-gray-500 mt-1">{instructor.title}</p>
              <p className="text-xs text-gray-400 mt-1 line-clamp-2">{instructor.bio}</p>
              <div className="flex items-center justify-center gap-3 mt-4 text-sm text-gray-500">
                <span className="flex items-center gap-1"><HiAcademicCap className="w-4 h-4" /> {instructor.courses_count}</span>
                <span className="flex items-center gap-1"><HiUserGroup className="w-4 h-4" /> {instructor.students_count}</span>
                <span className="flex items-center gap-1"><HiStar className="w-4 h-4 text-yellow-400" /> {instructor.average_rating}</span>
              </div>
              <Link href={`/instructor-details/${instructor.id}` as any} className="mt-4 text-sm text-[rgb(var(--fu-primary))] font-medium hover:text-[rgb(var(--fu-primary-dark))] inline-block">
                View Profile
              </Link>
            </motion.div>
          ))}
        </div>
      ) : (
        <EmptyState icon="instructors" />
      )}
    </div>
  );
}
