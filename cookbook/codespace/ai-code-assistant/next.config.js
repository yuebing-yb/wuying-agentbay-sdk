/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  webpack: (config, { isServer }) => {
    // Exclude playwright and other server-only dependencies from client bundle
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
        child_process: false,
        'playwright-core': false,
        'chromium-bidi': false,
      };
    }

    // Externalize playwright for server-side
    if (isServer) {
      config.externals = [...(config.externals || []), 'playwright-core', 'playwright'];
    }

    return config;
  },
};

module.exports = nextConfig;
