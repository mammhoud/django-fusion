/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', '127.0.0.1'],
  },
  experimental: {
    // typedRoutes disabled: the app uses dynamic string hrefs across multiple
    // components, so strict typed routes create more friction than value.
    typedRoutes: false,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5075/api',
    NEXT_PUBLIC_FUSION_SITE_NAME: process.env.NEXT_PUBLIC_FUSION_SITE_NAME || 'Fusion CMS',
  },
};

module.exports = nextConfig;
