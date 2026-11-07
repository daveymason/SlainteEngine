import type { Metadata } from 'next';
import React from 'react';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v15-appRouter';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { slainteTheme } from '@/theme/slainteTheme';
import { SiteChrome } from '@/components/SiteChrome';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'SlainteTech AI Security Labs | Sovereign Clinical AI & HL7 FHIR R4 Verticals',
  description:
    '11 autonomous healthcare security, governance, and clinical agents bound by deterministic Python FastMCP guardrails across 8 HL7 FHIR R4 industry verticals.',
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
