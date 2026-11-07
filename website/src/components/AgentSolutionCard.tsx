import React from 'react';
import Link from 'next/link';
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Stack,
  Typography,
} from '@mui/material';
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';
import type { AgentRecord } from '@/data/agentsData';
import { AgentIcon } from '@/components/AgentIcon';

export function AgentSolutionCard({
  agent,
  headingLevel = 'h3',
}: {
  agent: AgentRecord;
  headingLevel?: 'h2' | 'h3';
}) {
  const iconSurface =
    agent.squadColor === 'error'
      ? { bg: '#FEE2E2', fg: '#991B1B', border: '#FECACA' }
      : agent.squadColor === 'warning'
      ? { bg: '#FEF3C7', fg: '#92400E', border: '#FDE68A' }
      : { bg: '#E0F2FE', fg: '#0C4A6E', border: '#BAE6FD' };

  return (
    <Card
      className="slainte-interactive-card"
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        bgcolor: '#FFFFFF',
      }}
    >
      <CardContent sx={{ p: 3, pb: 1.5 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1.5} sx={{ mb: 2 }}>
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: '10px',
              bgcolor: iconSurface.bg,
              color: iconSurface.fg,
              border: `1px solid ${iconSurface.border}`,
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <AgentIcon iconKey={agent.iconKey} sx={{ fontSize: 24 }} />
          </Box>
          <Chip
            size="small"
            label={agent.squad}
            color={agent.squadColor}
            sx={{ fontSize: '0.74rem' }}
          />
        </Stack>

        <Typography
          variant="caption"
          sx={{
            fontFamily: 'monospace',
            fontWeight: 700,
            color: '#334155',
            display: 'block',
            mb: 0.5,
          }}
        >
          {agent.codeName}
        </Typography>

        <Typography component={headingLevel} variant="h3" sx={{ color: '#0F172A', mb: 1.25 }}>
          {agent.name}
        </Typography>

        <Typography variant="body2" sx={{ color: '#334155', mb: 2 }}>
          {agent.heroSummary}
        </Typography>

        <Stack direction="row" flexWrap="wrap" gap={0.75}>
          {agent.fastMcpBadges.slice(0, 2).map((badge) => (
            <Box
              key={badge}
              component="span"
              sx={{
                fontSize: '0.75rem',
                fontWeight: 700,
                fontFamily: 'monospace',
                bgcolor: '#F1F5F9',
                color: '#0F172A',
                border: '1px solid #CBD5E1',
                px: 1,
                py: 0.35,
                borderRadius: '6px',
              }}
            >
              {badge}
            </Box>
          ))}
        </Stack>
      </CardContent>

      <CardActions sx={{ px: 3, pb: 2.5, pt: 1 }}>
        <Button
          component={Link}
          href={`/health-tech-agents/${agent.slug}/`}
          variant="outlined"
          color="primary"
          fullWidth
          endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
          sx={{ justifyContent: 'space-between', borderWidth: '1.5px', '&:hover': { borderWidth: '1.5px' } }}
        >
          Inspect {agent.codeName}
        </Button>
      </CardActions>
    </Card>
  );
}
