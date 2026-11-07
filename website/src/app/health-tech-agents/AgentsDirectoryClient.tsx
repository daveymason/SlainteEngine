'use client';

import React, { useState } from 'react';
import { Box, Button, Stack, Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import { HEALTH_TECH_AGENTS, type AgentSquad } from '@/data/agentsData';
import { AgentSolutionCard } from '@/components/AgentSolutionCard';

const SQUAD_FILTERS: Array<{ label: string; value: 'ALL' | AgentSquad }> = [
  { label: 'All 11 Agents', value: 'ALL' },
  { label: 'SlainteShield Security (3)', value: 'SlainteShield Security' },
  { label: 'SlainteGov Governance & Coding (3)', value: 'SlainteGov Governance' },
  { label: 'SlainteClinical Care (5)', value: 'SlainteClinical Care' },
];

export function AgentsDirectoryClient() {
  const [selectedSquad, setSelectedSquad] = useState<'ALL' | AgentSquad>('ALL');

  const visibleAgents =
    selectedSquad === 'ALL'
      ? HEALTH_TECH_AGENTS
      : HEALTH_TECH_AGENTS.filter((a) => a.squad === selectedSquad);

  return (
    <Box>
      <Stack
        direction="row"
        flexWrap="wrap"
        gap={1}
        role="group"
        aria-label="Filter autonomous agents by squad"
        sx={{ mb: 4 }}
      >
        {SQUAD_FILTERS.map((filter) => {
          const active = selectedSquad === filter.value;
          return (
            <Button
              key={filter.value}
              variant={active ? 'contained' : 'outlined'}
              color="primary"
              aria-pressed={active}
              onClick={() => setSelectedSquad(filter.value)}
            >
              {filter.label}
            </Button>
          );
        })}
      </Stack>

      <Typography variant="body2" sx={{ color: '#334155', mb: 2.5, fontWeight: 700 }} aria-live="polite">
        Showing {visibleAgents.length} of {HEALTH_TECH_AGENTS.length} verified health-tech agents
      </Typography>

      <Grid container spacing={3}>
        {visibleAgents.map((agent) => (
          <Grid key={agent.slug} size={{ xs: 12, sm: 6, md: 4 }}>
            <AgentSolutionCard agent={agent} headingLevel="h2" />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
