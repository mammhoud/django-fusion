/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', '127.0.0.1'],
  },
  experimental: {
    typedRoutes: true,
  },
};

module.exports = nextConfig;
