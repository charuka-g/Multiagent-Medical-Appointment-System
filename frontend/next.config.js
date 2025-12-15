/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // output: 'export', // Required for static export to S3
  images: {
    unoptimized: true, // Required for static export
  },
  // Removed rewrites - they don't work with static export
  // Use NEXT_PUBLIC_BACKEND_URL environment variable instead
}

module.exports = nextConfig

