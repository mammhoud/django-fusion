/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', '127.0.0.1'],
  },
  experimental: {
    typedRoutes: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5074/api',
    NEXT_PUBLIC_FUSION_SITE_NAME: process.env.NEXT_PUBLIC_FUSION_SITE_NAME || 'Fusion LMS',
  },
};

module.exports = nextConfig;
