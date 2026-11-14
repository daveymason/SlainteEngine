import type { Metadata } from 'next';
import React from 'react';
import Link from 'next/link';
import { Box, Button, Container, Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';
import { HEALTH_TECH_AGENTS } from '@/data/agentsData';
import { AgentSolutionCard } from '@/components/AgentSolutionCard';

export const metadata: Metadata = {
  title: 'Autonomous Agents Directory | SlainteTech AI Security Labs',
  description: 'Direct index to all 16 SlainteTech autonomous health-tech agents at /health-tech-agents/.',
};

export default function AgentsAliasPage() {
  return (
    <Box>
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{ bgcolor: '#0F172A', color: '#FFFFFF', py: { xs: 6, md: 8 }, borderBottom: '2px solid #38BDF8' }}
      >
        <Container maxWidth="lg">
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            SlainteTech Autonomous Health-Tech Agents
          </Typography>
          <Typography variant="body1" sx={{ color: '#CBD5E1', mb: 3, maxWidth: 680 }}>
            Each of our 16 autonomous clinical, governance, and security agents has a dedicated technical page under <code>/health-tech-agents/</code>.
          </Typography>
          <Button
            component={Link}
            href="/health-tech-agents/"
            variant="contained"
            color="primary"
            endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
          >
            Open Interactive Squad Directory
          </Button>
        </Container>
      </Box>

      <Box component="section" aria-label="All 16 agents" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Grid container spacing={3}>
            {HEALTH_TECH_AGENTS.map((agent) => (
              <Grid key={agent.slug} size={{ xs: 12, sm: 6, md: 4 }}>
                <AgentSolutionCard agent={agent} headingLevel="h2" />
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}
