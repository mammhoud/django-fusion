'use client';

import { useEffect } from 'react';
import FusionProxy from '@/components/FusionProxy';
import ScrollReveal from '@/components/ui/ScrollReveal';
import { useToast } from '@/components/ui/Toast';

export default function HomePage() {
  const toast = useToast();

  useEffect(() => {
    // Small delay so the page can render before the toast appears
    const timer = setTimeout(() => {
      toast.info(
        'Welcome to Fusion LMS',
        'Explore our courses and start learning today.',
        4000,
      );
    }, 1500);
    return () => clearTimeout(timer);
  }, [toast]);

  return (
    <div className="min-h-screen">
      <ScrollReveal animation="fadeUp" duration={0.6}>
        <FusionProxy slug="home" />
      </ScrollReveal>
    </div>
  );
}
