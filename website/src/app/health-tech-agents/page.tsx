import type { Metadata } from 'next';
import React from 'react';
import { Box, Container, Typography } from '@mui/material';
import { AgentsDirectoryClient } from './AgentsDirectoryClient';

export const metadata: Metadata = {
  title: '11 Autonomous Health-Tech Agents | SlainteTech AI Security Labs',
  description:
    'Explore all 11 deterministic health-tech security, governance, and clinical agents built on HL7 FHIR R4 and Python FastMCP.',
};

export default function HealthTechAgentsIndexPage() {
  return (
    <Box>
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{
          bgcolor: '#0F172A',
          backgroundImage: 'linear-gradient(135deg, #0F172A 0%, #134E68 100%)',
          color: '#FFFFFF',
          py: { xs: 6, md: 8 },
          borderBottom: '2px solid #38BDF8',
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="overline" sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
            Autonomous Health-Tech Agent Fleet
          </Typography>
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            11 Specialized Agents. Zero Hallucinated Clinical Math.
          </Typography>
          <Typography variant="body1" sx={{ color: '#E2E8F0', maxWidth: 740 }}>
            Every SlainteTech agent operates against structured HL7 FHIR R4 compartments, enforces deterministic Python FastMCP guardrails, and writes immutable SHA-256 audit records. Select any agent below to inspect its architecture, vertical use case, and technical specification.
          </Typography>
        </Container>
      </Box>

      <Box component="section" aria-label="Agent directory" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <AgentsDirectoryClient />
        </Container>
      </Box>
    </Box>
  );
}
