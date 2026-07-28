'use client';

import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import { useGetInstructorCoursesQuery, useDeleteInstructorCourseMutation } from '@/store/api/endpoints/instructors';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiPlus, HiPencil, HiTrash, HiBookOpen, HiEye } from 'react-icons/hi';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function DashboardCoursesPage() {
  const { data: profile } = useGetProfileQuery();
  const { data: courses, isLoading } = useGetInstructorCoursesQuery(profile?.id ?? 0, { skip: !profile?.id });
  const [deleteCourse] = useDeleteInstructorCourseMutation();

  if (profile?.role !== 'instructor') {
    return <ErrorState fullPage message="This page is only available for instructors." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Courses</h1>
          <p className="text-gray-500 mt-1">Manage your course catalog</p>
        </div>
        <Link href="/dashboard/courses/new" className="btn-primary flex items-center gap-2">
          <HiPlus className="w-4 h-4" /> New Course
        </Link>
      </div>

      {isLoading ? (
        <LoadingSkeleton variant="list" count={3} />
      ) : courses && courses.length > 0 ? (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm min-w-[500px]">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-6 py-3 font-medium text-gray-500">Course</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Students</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Rating</th>
                <th className="text-center px-6 py-3 font-medium text-gray-500">Status</th>
                <th className="text-right px-6 py-3 font-medium text-gray-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {courses?.map((course) => (
                <tr key={course.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 card-gradient rounded flex items-center justify-center">
                        <HiBookOpen className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{course.title}</p>
                        <p className="text-xs text-gray-500">${course.price}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center text-gray-500">{course.students_count}</td>
                  <td className="px-6 py-4 text-center text-gray-500">{course.rating}</td>
                  <td className="px-6 py-4 text-center">
                    <span className={`badge ${course.is_published ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {course.is_published ? 'Published' : 'Draft'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link href={`/course-details/${course.id}` as any} className="p-2 text-gray-400 hover:text-[rgb(var(--fu-primary))] transition-colors"><HiEye className="w-4 h-4" /></Link>
                      <Link href={`/dashboard/courses/${course.id}/edit` as any} className="p-2 text-gray-400 hover:text-[rgb(var(--fu-primary))] transition-colors"><HiPencil className="w-4 h-4" /></Link>
                      <button onClick={() => deleteCourse(course.id)} className="p-2 text-gray-400 hover:text-red-600 transition-colors"><HiTrash className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState icon="courses" title="No courses yet" description="Create your first course to start teaching." actionLabel="Create Course" actionHref="/dashboard/courses/new" />
      )}
    </div>
  );
}
