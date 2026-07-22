'use client';

import { useState } from 'react';
import { HiChevronDown, HiSearch } from 'react-icons/hi';

const faqCategories = [
  {
    title: 'Getting Started',
    items: [
      { q: 'How do I create an account?', a: 'Click the "Sign Up" button in the top right corner. Fill in your details including name, email, and password. You can choose to register as a student or instructor. Verify your email address to activate your account.' },
      { q: 'Is there a free trial?', a: 'Yes! We offer a 7-day free trial for all new students. During this period, you have full access to all course materials. No credit card is required to start.' },
      { q: 'How do I enroll in a course?', a: 'Browse our course catalog, select a course you\'re interested in, and click the "Enroll Now" button. If it\'s a paid course, you\'ll be guided through the checkout process.' },
      { q: 'Can I access courses on mobile?', a: 'Absolutely! Our platform is fully responsive and works on all devices. You can learn on your phone, tablet, or desktop - anytime, anywhere.' },
    ],
  },
  {
    title: 'Account & Billing',
    items: [
      { q: 'What payment methods do you accept?', a: 'We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and in select regions, local payment methods.' },
      { q: 'Can I get a refund?', a: 'Yes, we offer a 30-day money-back guarantee. If you\'re not satisfied with a course, you can request a full refund within 30 days of purchase.' },
      { q: 'How do I update my billing information?', a: 'Go to your account settings, navigate to the "Billing" section, and you can update your payment method and billing address there.' },
      { q: 'Do you offer student discounts?', a: 'Yes! Verified students with a valid .edu email address receive a 20% discount on all courses. Contact our support team to verify your student status.' },
    ],
  },
  {
    title: 'Learning Experience',
    items: [
      { q: 'How are courses structured?', a: 'Courses are divided into modules and lessons. Each lesson includes video content, reading materials, and practical exercises. Many courses also include quizzes and projects.' },
      { q: 'Can I download course materials?', a: 'Yes, most course materials including videos, PDFs, and exercise files can be downloaded for offline access through our mobile app.' },
      { q: 'How do I track my progress?', a: 'Your student dashboard shows your progress for each course, including completed lessons, quiz scores, and overall completion percentage.' },
      { q: 'Do I get a certificate?', a: 'Yes! Upon completing a course, you\'ll receive a verifiable certificate of completion that you can share on LinkedIn or your resume.' },
    ],
  },
  {
    title: 'For Instructors',
    items: [
      { q: 'How do I become an instructor?', a: 'Register as an instructor, complete your profile, and submit your first course for review. Our team will review it within 5 business days.' },
      { q: 'What are the revenue shares?', a: 'Instructors earn up to 80% revenue share for courses sold through our platform. Higher rates apply for instructor-driven sales.' },
      { q: 'How do I get paid?', a: 'Payments are processed monthly via PayPal or bank transfer. You need a minimum balance of $50 to receive a payout.' },
      { q: 'Can I update my course after publishing?', a: 'Yes, you can update your course content anytime. Students will be notified of new or updated content.' },
    ],
  },
  {
    title: 'Technical Support',
    items: [
      { q: 'What browsers are supported?', a: 'We support the latest versions of Chrome, Firefox, Safari, and Edge. For the best experience, we recommend using Chrome.' },
      { q: 'Why is my video not playing?', a: 'Try refreshing the page, checking your internet connection, or clearing your browser cache. If the issue persists, contact our support team.' },
      { q: 'How do I reset my password?', a: 'Click "Forgot Password" on the login page. Enter your email address, and we\'ll send you a password reset link.' },
    ],
  },
];

export default function FaqPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [openItems, setOpenItems] = useState<Record<string, boolean>>({});

  const toggleItem = (categoryIdx: number, itemIdx: number) => {
    const key = `${categoryIdx}-${itemIdx}`;
    setOpenItems((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const filteredCategories = faqCategories
    .map((cat) => ({
      ...cat,
      items: cat.items.filter(
        (item) =>
          item.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.a.toLowerCase().includes(searchQuery.toLowerCase())
      ),
    }))
    .filter((cat) => cat.items.length > 0);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero */}
      <section className="bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 text-white py-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Frequently Asked Questions</h1>
          <p className="text-lg text-indigo-200 mb-8">Find answers to common questions about our platform</p>
          <div className="relative max-w-xl mx-auto">
            <HiSearch className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search FAQs..."
              className="w-full pl-12 pr-4 py-3.5 rounded-xl text-gray-900 bg-white shadow-lg focus:ring-2 focus:ring-indigo-300 outline-none"
            />
          </div>
        </div>
      </section>

      {/* FAQ Content */}
      <div className="max-w-3xl mx-auto px-4 py-16">
        <div className="space-y-8">
          {filteredCategories.map((category, catIdx) => (
            <section key={catIdx} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">{category.title}</h2>
              </div>
              <div className="divide-y divide-gray-100">
                {category.items.map((item, itemIdx) => {
                  const key = `${catIdx}-${itemIdx}`;
                  const isOpen = openItems[key];
                  return (
                    <div key={itemIdx}>
                      <button
                        onClick={() => toggleItem(catIdx, itemIdx)}
                        className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-gray-50 transition-colors"
                      >
                        <span className="text-sm font-medium text-gray-900 pr-4">{item.q}</span>
                        <HiChevronDown
                          className={`w-4 h-4 text-gray-400 flex-shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                        />
                      </button>
                      <div
                        className={`px-6 overflow-hidden transition-all duration-300 ${
                          isOpen ? 'pb-4 max-h-96' : 'max-h-0'
                        }`}
                      >
                        <p className="text-sm text-gray-600 leading-relaxed">{item.a}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          ))}
        </div>

        {/* Still need help */}
        <div className="mt-12 text-center bg-indigo-50 rounded-2xl p-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Still have questions?</h3>
          <p className="text-gray-600 mb-6">Can&apos;t find the answer you&apos;re looking for? We&apos;re here to help.</p>
          <a href="/contact" className="btn-primary inline-flex">Contact Support</a>
        </div>
      </div>
    </div>
  );
}
