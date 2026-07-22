'use client';

import { motion } from 'framer-motion';
import { HiAcademicCap, HiUserGroup, HiBookOpen, HiGlobe, HiStar } from 'react-icons/hi';
import Link from 'next/link';
import { useGetInstructorsQuery } from '@/store/api/endpoints/instructors';
import { useGetCoursesQuery } from '@/store/api/endpoints/courses';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

export default function AboutPage() {
  const { data: instructorsData, isLoading: instrLoading } = useGetInstructorsQuery({ page: 1 });
  const { data: coursesData, isLoading: coursesLoading } = useGetCoursesQuery({ page: 1 });

  const highlights = [
    { icon: HiBookOpen, label: 'Courses', value: coursesData?.count ?? 0, desc: 'Expert-crafted courses' },
    { icon: HiUserGroup, label: 'Instructors', value: instructorsData?.count ?? 0, desc: 'Industry professionals' },
    { icon: HiAcademicCap, label: 'Students', value: '5K+', desc: 'Active learners worldwide' },
    { icon: HiGlobe, label: 'Countries', value: '50+', desc: 'Global reach' },
  ];

  if (coursesLoading || instrLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-10">
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-indigo-600 to-purple-700 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-5xl font-bold mb-6">
            About LMS Platform
          </motion.h1>
          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="text-xl text-indigo-200 leading-relaxed">
            Empowering learners worldwide with quality education and expert-led courses.
          </motion.p>
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-7xl mx-auto px-4 -mt-10 relative z-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {highlights.map((h, i) => (
            <motion.div key={h.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              className="card p-6 text-center bg-white">
              <h.icon className="w-8 h-8 text-indigo-600 mx-auto mb-3" />
              <div className="text-3xl font-bold text-gray-900">{h.value}</div>
              <div className="text-sm text-gray-500 mt-1">{h.label}</div>
              <p className="text-xs text-gray-400 mt-1">{h.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Mission */}
      <section className="max-w-4xl mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Mission</h2>
          <p className="text-lg text-gray-600 leading-relaxed">
            We believe quality education should be accessible to everyone. Our platform connects
            passionate instructors with eager learners, creating a community where knowledge
            knows no boundaries.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { title: 'Quality Content', desc: 'Courses crafted by industry experts with real-world experience' },
            { title: 'Flexible Learning', desc: 'Learn at your own pace with lifetime access to all materials' },
            { title: 'Community Driven', desc: 'Join a global community of learners and instructors' },
          ].map((item, i) => (
            <motion.div key={item.title} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              className="text-center p-6">
              <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <HiStar className="w-6 h-6 text-indigo-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
              <p className="text-sm text-gray-500">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Get Started?</h2>
          <p className="text-gray-500 mb-8">Join our community and start learning today.</p>
          <Link href="/registration" className="btn-primary text-lg px-10 py-3">Create Free Account</Link>
        </div>
      </section>
    </div>
  );
}
