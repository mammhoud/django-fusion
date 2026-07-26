'use client';

import { useParams } from 'next/navigation';
import FusionProxy from '@/components/FusionProxy';

export default function DynamicPage() {
  const params = useParams();
  const slug = params.slug as string;

  return (
    <div className="min-h-screen">
      <FusionProxy slug={slug} />
    </div>
  );
}
