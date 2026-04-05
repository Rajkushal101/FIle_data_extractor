/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    API_URL:
      process.env.NEXT_PUBLIC_API_BASE_URL ||
      'https://file-data-extractor.onrender.com',
  },
}

module.exports = nextConfig