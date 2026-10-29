import type { NextConfig } from 'next';

// Backend URL:
//   - Local dev:  http://127.0.0.1:8000  (default)
//   - Production: set BACKEND_URL env var to your deployed backend URL
//     e.g.  https://gearbox-studio-backend.onrender.com
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
