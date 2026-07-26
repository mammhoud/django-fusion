import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
// Single source of truth for design tokens (shared with Django)
import '../styles/theme/fusion-theme.scss';
import './globals.css';
import Providers from '../components/Providers';
import ErrorBoundary from '../components/ErrorBoundary';
import Header from '../components/Header';
import Footer from '../components/Footer';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Fusion LMS — Learning Management System',
  description: 'Modern learning management platform powered by django-fusion and django-bolt.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <ErrorBoundary>
            <div className="flex flex-col min-h-screen">
              <Header />
              <main className="flex-1">
                {children}
              </main>
              <Footer />
            </div>
          </ErrorBoundary>
        </Providers>
      </body>
    </html>
  );
}
