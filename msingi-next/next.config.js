/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [];
  },

 // Ignore ESLint errors
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Ignore TypeScript errors
  typescript: {
    ignoreBuildErrors: true,
  },

  // Optional: reduce strict warnings
  reactStrictMode: false,
};

module.exports = nextConfig;
