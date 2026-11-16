import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    const backendTarget =
      process.env.BACKEND_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === "production" ? "" : "http://localhost:8000");

    if (!backendTarget) return [];

    // Strip trailing /api/v1 or /api to avoid duplicated path prefix
    const cleanTarget = backendTarget.replace(/\/api(\/v1)?\/?$/, "").replace(/\/+$/, "");

    return [
      {
        source: "/api/v1/:path*",
        destination: `${cleanTarget}/api/v1/:path*`,
      },
      {
        source: "/api/:path*",
        destination: `${cleanTarget}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
