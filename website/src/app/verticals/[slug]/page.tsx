import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import React from 'react';
import { INDUSTRY_VERTICALS, getVerticalBySlug } from '@/data/verticalsData';
import { VerticalUniqueTemplate } from '@/components/VerticalUniqueTemplate';

export function generateStaticParams() {
  return INDUSTRY_VERTICALS.map((v) => ({ slug: v.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const vertical = getVerticalBySlug(slug);
  if (!vertical) {
    return { title: 'Vertical Not Found | SlainteTech' };
  }
  return {
    title: vertical.seoTitle,
    description: vertical.seoDescription,
  };
}

export default async function VerticalDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const vertical = getVerticalBySlug(slug);
  if (!vertical) {
    notFound();
  }
  return <VerticalUniqueTemplate vertical={vertical} />;
}
