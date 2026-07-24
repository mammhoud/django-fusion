'use client';

import Link from 'next/link';
import { FusionPage } from '@/components/FusionPage';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import type { CmsPage } from '@/store/api/endpoints/pages';

function PrivacyContent({ page, isLoading, error }: {
  page?: CmsPage;
  isLoading: boolean;
  error?: any;
}) {
  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16">
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  if (error || !page) {
    return <ErrorState message="Unable to load privacy content." />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">{page.title}</h1>
          {page.last_updated && <p className="text-gray-500">Last updated: {page.last_updated}</p>}
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 md:p-12 space-y-8">
          {page.blocks.map((block) => (
            <section key={block.heading}>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">{block.heading}</h2>
              <div className="text-gray-600 leading-relaxed space-y-3" dangerouslySetInnerHTML={{ __html: block.html || '' }} />
            </section>
          ))}
        </div>
        <div className="mt-8 text-center"><Link href="/" className="text-indigo-600 hover:text-indigo-700 font-medium">Back to Home</Link></div>
      </div>
    </div>
  );
}

export default function PrivacyPage() {
  return (
    <FusionPage slug="privacy">
      {(page, { isLoading, error }) => (
        <PrivacyContent page={page} isLoading={isLoading} error={error} />
      )}
    </FusionPage>
  );
}
