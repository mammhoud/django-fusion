'use client';

import { motion } from 'framer-motion';
import { HiAcademicCap, HiUserGroup, HiBookOpen, HiGlobe, HiStar } from 'react-icons/hi';
import Link from 'next/link';
import type { Route } from 'next';
import { useGetInstructorsQuery } from '@/store/api/endpoints/instructors';
import { useGetCoursesQuery } from '@/store/api/endpoints/courses';
import { FusionPage } from '@/components/FusionPage';
import StatSkeleton from '@/components/ui/StatSkeleton';
import type { CmsPage } from '@/store/api/endpoints/pages';

export default function AboutPage() {
  return (
    <FusionPage slug="about-us">
      {(page, _fallback) => <AboutPageContent page={page} />}
    </FusionPage>
  );
}

function AboutPageContent({ page }: { page: CmsPage | undefined }) {
  const { data: instructorsData, isLoading: instrLoading } = useGetInstructorsQuery({ page: 1 });
  const { data: coursesData, isLoading: coursesLoading } = useGetCoursesQuery({ page: 1 });

  const highlights = [
    { icon: HiBookOpen, label: 'Courses', value: coursesData?.count ?? 0, apiLoading: coursesLoading, desc: 'Expert-crafted courses' },
    { icon: HiUserGroup, label: 'Instructors', value: instructorsData?.count ?? 0, apiLoading: instrLoading, desc: 'Industry professionals' },
    { icon: HiAcademicCap, label: 'Students', value: '5K+', desc: 'Active learners worldwide' },
    { icon: HiGlobe, label: 'Countries', value: '50+', desc: 'Global reach' },
  ];

  const hero = page?.blocks.find((block) => block.type === 'hero');
  const mission = page?.blocks.find((block) => block.type === 'rich_section');
  const cta = page?.blocks.find((block) => block.type === 'cta');

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-[rgb(var(--fu-primary))] to-[rgb(var(--fu-primary-dark))] text-white py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-5xl font-bold mb-6">
            {hero?.heading || page?.title || 'About Us'}
          </motion.h1>
          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="text-xl text-white/70 leading-relaxed">
            {hero?.intro}
          </motion.p>
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-7xl mx-auto px-4 -mt-10 relative z-10">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {highlights.map((h, i) => (
            <motion.div key={h.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              className="card p-6 text-center bg-white">
              <h.icon className="w-8 h-8 text-[rgb(var(--fu-primary))] mx-auto mb-3" />
              {h.apiLoading ? (
                <StatSkeleton size="lg" center />
              ) : (
                <div className="text-3xl font-bold text-gray-900">{h.value}</div>
              )}
              <div className="text-sm text-gray-500 mt-1">{h.label}</div>
              <p className="text-xs text-gray-400 mt-1">{h.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Mission */}
      <section className="max-w-4xl mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">{mission?.heading}</h2>
          <div className="text-lg text-gray-600 leading-relaxed" dangerouslySetInnerHTML={{ __html: mission?.html || '' }} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {(mission?.items || []).map((item, i) => (
            <motion.div key={item.heading} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}
              className="text-center p-6">
              <div className="w-12 h-12 bg-[rgb(var(--fu-primary))]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <HiStar className="w-6 h-6 text-[rgb(var(--fu-primary))]" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{item.heading}</h3>
              <p className="text-sm text-gray-500">{item.text}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">{cta?.heading}</h2>
          <p className="text-gray-500 mb-8">{cta?.intro}</p>
          <Link href={(cta?.ctas?.[0]?.href || '/registration') as Route} className="btn-primary text-lg px-10 py-3">{cta?.ctas?.[0]?.label || 'Create Free Account'}</Link>
        </div>
      </section>
    </div>
  );
}
