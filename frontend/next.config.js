/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  rewrites: async () => [
    {
      source: '/graphql',
      destination: 'http://localhost:8080/graphql',
    },
  ],
};

export default nextConfig;
