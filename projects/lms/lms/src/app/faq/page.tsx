'use client';

import { useState } from 'react';
import { HiChevronDown, HiSearch } from 'react-icons/hi';
import { useGetPageQuery } from '@/store/api/endpoints/pages';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';

export default function FaqPage() {
  const { data: page, isLoading, error } = useGetPageQuery('faq');
  const [searchQuery, setSearchQuery] = useState('');
  const [openItems, setOpenItems] = useState<Record<string, boolean>>({});

  if (isLoading) return <LoadingSkeleton variant="detail" />;
  if (error || !page) return <ErrorState message="Unable to load FAQ content." />;

  const hero = page.blocks.find((block) => block.type === 'hero');
  const faqGroups = page.blocks.find((block) => block.type === 'faq_groups')?.groups || [];
  const cta = page.blocks.find((block) => block.type === 'cta');
  const filteredCategories = faqGroups
    .map((cat) => ({ ...cat, items: cat.items.filter((item) => item.question.toLowerCase().includes(searchQuery.toLowerCase()) || item.answer.toLowerCase().includes(searchQuery.toLowerCase())) }))
    .filter((cat) => cat.items.length > 0);

  const toggleItem = (categoryIdx: number, itemIdx: number) => {
    const key = `${categoryIdx}-${itemIdx}`;
    setOpenItems((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <section className="bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 text-white py-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">{hero?.heading || page.title}</h1>
          <p className="text-lg text-indigo-200 mb-8">{hero?.intro}</p>
          <div className="relative max-w-xl mx-auto"><HiSearch className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" /><input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search FAQs..." className="w-full pl-12 pr-4 py-3.5 rounded-xl text-gray-900 bg-white shadow-lg focus:ring-2 focus:ring-indigo-300 outline-none" /></div>
        </div>
      </section>
      <div className="max-w-3xl mx-auto px-4 py-16"><div className="space-y-8">{filteredCategories.map((category, catIdx) => (
        <section key={category.title} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden"><div className="px-6 py-4 bg-gray-50 border-b border-gray-100"><h2 className="text-lg font-semibold text-gray-900">{category.title}</h2></div><div className="divide-y divide-gray-100">{category.items.map((item, itemIdx) => { const key = `${catIdx}-${itemIdx}`; const isOpen = openItems[key]; return <div key={item.question}><button onClick={() => toggleItem(catIdx, itemIdx)} className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-gray-50 transition-colors"><span className="text-sm font-medium text-gray-900 pr-4">{item.question}</span><HiChevronDown className={`w-4 h-4 text-gray-400 flex-shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} /></button><div className={`px-6 overflow-hidden transition-all duration-300 ${isOpen ? 'pb-4 max-h-96' : 'max-h-0'}`}><p className="text-sm text-gray-600 leading-relaxed">{item.answer}</p></div></div>; })}</div></section>
      ))}</div>{cta && <div className="mt-12 text-center bg-indigo-50 rounded-2xl p-8"><h3 className="text-lg font-semibold text-gray-900 mb-2">{cta.heading}</h3><p className="text-gray-600 mb-6">{cta.intro}</p><a href={cta.ctas?.[0]?.href || '/contact'} className="btn-primary inline-flex">{cta.ctas?.[0]?.label || 'Contact Support'}</a></div>}</div>
    </div>
  );
}
