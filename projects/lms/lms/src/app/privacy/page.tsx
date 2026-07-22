'use client';

'use client';

import Link from 'next/link';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
          <p className="text-gray-500">Last updated: January 1, 2026</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 md:p-12 space-y-8">
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Introduction</h2>
            <p className="text-gray-600 leading-relaxed">
              Welcome to LMS Platform. We respect your privacy and are committed to protecting your personal data. This
              privacy policy explains how we collect, use, disclose, and safeguard your information when you visit our
              platform.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Information We Collect</h2>
            <div className="space-y-3 text-gray-600 leading-relaxed">
              <p>We may collect the following types of information:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Personal Identification Information:</strong> Name, email address, phone number, billing address</li>
                <li><strong>Account Credentials:</strong> Username, password, and authentication data</li>
                <li><strong>Profile Information:</strong> Profile picture, bio, educational background, professional experience</li>
                <li><strong>Learning Data:</strong> Courses enrolled, progress, quiz results, certificates earned</li>
                <li><strong>Payment Information:</strong> Payment method details (processed securely by third-party payment processors)</li>
                <li><strong>Technical Data:</strong> IP address, browser type, device information, cookies</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">3. How We Use Your Information</h2>
            <div className="space-y-3 text-gray-600 leading-relaxed">
              <p>We use your information for the following purposes:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>To provide, maintain, and improve our educational platform</li>
                <li>To process your enrollment and payments</li>
                <li>To personalize your learning experience</li>
                <li>To communicate with you about courses, updates, and support</li>
                <li>To issue certificates of completion</li>
                <li>To detect and prevent fraud or abuse</li>
                <li>To comply with legal obligations</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Data Sharing and Disclosure</h2>
            <p className="text-gray-600 leading-relaxed">
              We do not sell your personal information to third parties. We may share your data with:
            </p>
            <ul className="list-disc pl-6 mt-3 space-y-2 text-gray-600">
              <li><strong>Service Providers:</strong> Payment processors, cloud hosting, analytics providers</li>
              <li><strong>Course Instructors:</strong> Basic profile information and learning progress for courses you take</li>
              <li><strong>Legal Authorities:</strong> When required by law or to protect our rights</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Data Security</h2>
            <p className="text-gray-600 leading-relaxed">
              We implement appropriate technical and organizational measures to protect your personal data, including
              encryption in transit and at rest, secure data centers, and access controls. However, no method of
              transmission over the Internet is 100% secure.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Your Rights</h2>
            <p className="text-gray-600 leading-relaxed mb-3">You have the following rights regarding your data:</p>
            <ul className="list-disc pl-6 space-y-2 text-gray-600">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Rectification:</strong> Request correction of inaccurate data</li>
              <li><strong>Erasure:</strong> Request deletion of your data (subject to legal requirements)</li>
              <li><strong>Portability:</strong> Request transfer of your data to another service</li>
              <li><strong>Objection:</strong> Object to processing of your data for marketing purposes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Cookies</h2>
            <p className="text-gray-600 leading-relaxed">
              We use cookies and similar tracking technologies to enhance your browsing experience, analyze site traffic,
              and understand where our users come from. You can control cookie preferences through your browser settings.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Third-Party Links</h2>
            <p className="text-gray-600 leading-relaxed">
              Our platform may contain links to third-party websites. We are not responsible for the privacy practices
              of these external sites. We encourage you to review their privacy policies before providing any personal
              information.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Changes to This Policy</h2>
            <p className="text-gray-600 leading-relaxed">
              We may update this privacy policy from time to time. We will notify you of any changes by posting the new
              policy on this page and updating the &ldquo;Last updated&rdquo; date.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Contact Us</h2>
            <p className="text-gray-600 leading-relaxed">
              If you have any questions about this privacy policy or our data practices, please contact us at
              <a href="mailto:privacy@lmsplatform.com" className="text-indigo-600 hover:text-indigo-700 ml-1">privacy@lmsplatform.com</a>.
            </p>
          </section>
        </div>

        <div className="mt-8 text-center">
          <Link href="/" className="text-indigo-600 hover:text-indigo-700 font-medium">
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
