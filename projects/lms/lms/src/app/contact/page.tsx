'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { HiMail, HiPhone, HiLocationMarker, HiClock } from 'react-icons/hi';
import { useSubmitContactMutation } from '@/store/api/endpoints/contact';

export default function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [submit, { isLoading, isSuccess, error }] = useSubmitContactMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await submit(form).unwrap();
      setForm({ name: '', email: '', subject: '', message: '' });
    } catch { /* error handled by RTK */ }
  };

  const contactInfo = [
    { icon: HiMail, label: 'Email', value: 'support@lmsplatform.com', href: 'mailto:support@lmsplatform.com' },
    { icon: HiPhone, label: 'Phone', value: '+1 (555) 123-4567', href: 'tel:+15551234567' },
    { icon: HiLocationMarker, label: 'Address', value: '123 Learning St, Education City, EC 10001' },
    { icon: HiClock, label: 'Hours', value: 'Mon-Fri 9:00 AM - 6:00 PM EST' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-bold text-gray-900">Contact Us</h1>
        <p className="text-gray-500 mt-2">We&apos;d love to hear from you</p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {/* Contact Info */}
        <div className="space-y-6">
          {contactInfo.map((info) => (
            <motion.div key={info.label} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
              className="card p-5">
              <info.icon className="w-6 h-6 text-indigo-600 mb-3" />
              <h3 className="font-medium text-gray-900">{info.label}</h3>
              {info.href ? (
                <a href={info.href} className="text-sm text-gray-500 hover:text-indigo-600 transition-colors">{info.value}</a>
              ) : (
                <p className="text-sm text-gray-500">{info.value}</p>
              )}
            </motion.div>
          ))}
        </div>

        {/* Contact Form */}
        <div className="md:col-span-2">
          <form onSubmit={handleSubmit} className="card p-8 space-y-5">
            {isSuccess && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
                Message sent successfully! We&apos;ll get back to you soon.
              </div>
            )}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                Failed to send message. Please try again.
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="input-field" placeholder="Your name" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="input-field" placeholder="your@email.com" required />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <input type="text" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })}
                className="input-field" placeholder="How can we help?" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea rows={5} value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })}
                className="input-field" placeholder="Tell us more about your inquiry..." required />
            </div>
            <button type="submit" disabled={isLoading} className="btn-primary w-full flex items-center justify-center gap-2">
              {isLoading ? (
                <><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Sending...</>
              ) : 'Send Message'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
