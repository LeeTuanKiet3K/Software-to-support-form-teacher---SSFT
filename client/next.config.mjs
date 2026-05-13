/** @type {import('next').NextConfig} */
const nextConfig = {
  // Cho phép gọi API backend Python
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
    ];
  },
};

export default nextConfig;
