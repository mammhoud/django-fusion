import Link from 'next/link';
import { HiAcademicCap } from 'react-icons/hi';

const footerLinks = {
  'Platform': [
    { href: '/courses', label: 'All Courses' },
    { href: '/instructors', label: 'Instructors' },
    { href: '/blog', label: 'Blog' },
    { href: '/events', label: 'Events' },
  ],
  'Support': [
    { href: '/contact', label: 'Contact Us' },
    { href: '/about-us', label: 'About Us' },
    { href: '/faq', label: 'FAQ' },
    { href: '/privacy', label: 'Privacy Policy' },
  ],
  'Community': [
    { href: '/instructor-dashboard', label: 'Teach on LMS' },
    { href: '/student-dashboard', label: 'Student Dashboard' },
    { href: '/shop', label: 'Merch Shop' },
  ],
};

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <Link href="/" className="flex items-center gap-2 text-white font-bold text-lg mb-4">
              <HiAcademicCap className="w-7 h-7 text-[rgb(var(--ctc-primary))]" />
              <span>LMS</span>
            </Link>
            <p className="text-sm text-gray-400 leading-relaxed">
              Empowering learners worldwide with quality education and expert instructors.
            </p>
          </div>

          {/* Link Groups */}
          {Object.entries(footerLinks).map(([title, links]) => (
            <div key={title}>
              <h3 className="text-white font-semibold mb-4">{title}</h3>
              <ul className="space-y-2">
                {links.map((link) => (
                  <li key={link.href}>
                    <Link href={link.href as any} className="text-sm text-gray-400 hover:text-white transition-colors duration-200">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 pt-8 border-t border-gray-800 text-center text-sm text-gray-500">
          <p>&copy; {new Date().getFullYear()} LMS Platform. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
