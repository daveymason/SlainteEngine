import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import React from 'react';
import { HEALTH_TECH_AGENTS, getAgentBySlug } from '@/data/agentsData';
import { AgentCanonicalTemplate } from '@/components/AgentCanonicalTemplate';

export function generateStaticParams() {
  return HEALTH_TECH_AGENTS.map((agent) => ({ slug: agent.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const agent = getAgentBySlug(slug);
  if (!agent) {
    return { title: 'Agent Not Found | SlainteTech' };
  }
  return {
    title: agent.seoTitle,
    description: agent.seoDescription,
  };
}

export default async function HealthTechAgentDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const agent = getAgentBySlug(slug);
  if (!agent) {
    notFound();
  }
  return <AgentCanonicalTemplate agent={agent} />;
}
