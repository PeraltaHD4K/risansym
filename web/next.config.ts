import type { NextConfig } from "next";

const isGithubActions = process.env.GITHUB_ACTIONS || false;
let repoName = '';

if (isGithubActions && process.env.GITHUB_REPOSITORY) {
  // GITHUB_REPOSITORY tiene el formato "usuario/repo"
  repoName = `/${process.env.GITHUB_REPOSITORY.split('/')[1]}`;
}

const nextConfig: NextConfig = {
  output: 'export',
  basePath: repoName,
};

export default nextConfig;
