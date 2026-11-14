import type { Metadata } from 'next';
import React from 'react';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v15-appRouter';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { slainteTheme } from '@/theme/slainteTheme';
import { SiteChrome } from '@/components/SiteChrome';
import '@/styles/globals.css';

export const metadata: Metadata = {
  metadataBase: new URL('https://slainte-tech.com'),
  title: 'SlainteTech AI Security Labs | Sovereign Clinical AI & HL7 FHIR R4 Verticals',
  description:
    '16 autonomous healthcare security, governance, and clinical agents bound by deterministic Python FastMCP guardrails across 8 HL7 FHIR R4 industry verticals.',
  alternates: {
    canonical: './',
  },
  openGraph: {
    title: 'SlainteTech AI Security Labs | Sovereign Clinical AI & HL7 FHIR R4 Verticals',
    description:
      '16 autonomous healthcare security, governance, and clinical agents bound by deterministic Python FastMCP guardrails across 8 HL7 FHIR R4 industry verticals.',
    url: 'https://slainte-tech.com',
    siteName: 'SlainteTech AI Security Labs',
    type: 'website',
    images: [
      {
        url: '/images/hero-clinicians.jpg',
        alt: 'SlainteTech AI Security Labs — Sovereign Healthcare AI & HL7 FHIR R4 Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SlainteTech AI Security Labs | Sovereign Clinical AI & HL7 FHIR R4 Verticals',
    description:
      '16 autonomous healthcare security, governance, and clinical agents bound by deterministic Python FastMCP guardrails across 8 HL7 FHIR R4 industry verticals.',
    images: ['/images/hero-clinicians.jpg'],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>
          <ThemeProvider theme={slainteTheme}>
            <CssBaseline />
            <SiteChrome>{children}</SiteChrome>
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
