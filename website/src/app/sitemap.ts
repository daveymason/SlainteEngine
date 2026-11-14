import type { MetadataRoute } from 'next';
import { HEALTH_TECH_AGENTS } from '@/data/agentsData';
import { INDUSTRY_VERTICALS } from '@/data/verticalsData';

export const dynamic = 'force-static';

const BASE_URL = 'https://slainte-tech.com';

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date('2026-11-13T00:00:00.000Z');

  const staticRoutes = [
    '/',
    '/platform/',
    '/health-tech-agents/',
    '/agents/',
    '/verticals/',
    '/security-compliance/',
    '/pricing/',
    '/investors/',
    '/docs/',
    '/about/',
    '/contact/',
  ].map((route) => ({
    url: `${BASE_URL}${route}`,
    lastModified,
    changeFrequency: 'weekly' as const,
    priority: route === '/' ? 1.0 : 0.85,
  }));

  const agentRoutes = HEALTH_TECH_AGENTS.map((agent) => ({
    url: `${BASE_URL}/health-tech-agents/${agent.slug}/`,
    lastModified,
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));

  const verticalRoutes = INDUSTRY_VERTICALS.map((vertical) => ({
    url: `${BASE_URL}/verticals/${vertical.slug}/`,
    lastModified,
    changeFrequency: 'weekly' as const,
    priority: 0.85,
  }));

  return [...staticRoutes, ...verticalRoutes, ...agentRoutes];
}
