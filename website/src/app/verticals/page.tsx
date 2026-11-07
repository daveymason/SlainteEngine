import type { Metadata } from 'next';
import React from 'react';
import Link from 'next/link';
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Container,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';
import { INDUSTRY_VERTICALS } from '@/data/verticalsData';

export const metadata: Metadata = {
  title: '8 Healthcare Industry Verticals | SlainteTech AI Security Labs',
  description:
    'Explore all 8 SlainteTech clinical verticals: Emergency Departments, General Practice & Community Nursing, Psychiatry, Dentistry, Pharmacy, Ambulance ePCR, Sports Medicine, and Aerospace.',
};

export default function VerticalsHubPage() {
  return (
    <Box>
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{
          bgcolor: '#0F172A',
          backgroundImage: 'linear-gradient(135deg, #0F172A 0%, #133B54 100%)',
          color: '#FFFFFF',
          py: { xs: 6, md: 8 },
          borderBottom: '2px solid #38BDF8',
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="overline" sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
            One Sovereign Engine • 8 Tailored Verticals
          </Typography>
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            Clinical Verticals Engineered for Every Care Setting
          </Typography>
          <Typography variant="body1" sx={{ color: '#E2E8F0', maxWidth: 760 }}>
            Every vertical runs natively inside the SlainteTech core application (&ldquo;Sign in as...&rdquo;) with role-specific FHIR R4 workflows, pre-assigned autonomous safety agents, and responsive desktop, tablet, and smartphone layouts.
          </Typography>
        </Container>
      </Box>

      {/* 8 VERTICAL CARDS */}
      <Box component="section" aria-labelledby="vertical-cards-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Typography component="h2" variant="h2" id="vertical-cards-heading" sx={{ color: '#0F172A', mb: 4 }}>
            Select Your Clinical or Operational Vertical
          </Typography>

          <Grid container spacing={3}>
            {INDUSTRY_VERTICALS.map((v) => (
              <Grid key={v.slug} size={{ xs: 12, sm: 6, md: 6 }}>
                <Card
                  className="slainte-interactive-card"
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    bgcolor: '#FFFFFF',
                    borderTop: `5px solid ${v.palette.accentMain}`,
                  }}
                >
                  <CardContent sx={{ p: 3.5 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
                      <Box
                        component="span"
                        sx={{
                          bgcolor: v.palette.badgeBg,
                          color: v.palette.badgeText,
                          px: 1.4,
                          py: 0.45,
                          borderRadius: '6px',
                          fontSize: '0.78rem',
                          fontWeight: 800,
                        }}
                      >
                        {v.brand}
                      </Box>
                      <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700 }}>
                        {v.assignedAgentSlugs.length} Active Agents
                      </Typography>
                    </Stack>

                    <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 1 }}>
                      {v.forLabel}
                    </Typography>

                    <Typography variant="body2" sx={{ color: '#334155', mb: 2 }}>
                      {v.heroLead}
                    </Typography>

                    <Stack direction="row" flexWrap="wrap" gap={1}>
                      {v.kpis.map((k) => (
                        <Box
                          key={k.label}
                          component="span"
                          sx={{
                            fontSize: '0.76rem',
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            bgcolor: '#F1F5F9',
                            color: '#0F172A',
                            border: '1px solid #CBD5E1',
                            px: 1.1,
                            py: 0.35,
                            borderRadius: '6px',
                          }}
                        >
                          {k.label}: {k.value}
                        </Box>
                      ))}
                    </Stack>
                  </CardContent>

                  <CardActions sx={{ px: 3.5, pb: 3, pt: 0 }}>
                    <Button
                      component={Link}
                      href={`/verticals/${v.slug}/`}
                      variant="contained"
                      fullWidth
                      endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                      sx={{
                        bgcolor: v.palette.accentMain,
                        color: '#FFFFFF',
                        justifyContent: 'space-between',
                        '&:hover': { bgcolor: '#0F172A' },
                      }}
                    >
                      Open {v.forLabel} Page
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* COMPARISON MATRIX */}
      <Box component="section" aria-labelledby="comparison-heading" sx={{ py: { xs: 6, md: 8 }, bgcolor: '#FFFFFF', borderTop: '1px solid #CBD5E1' }}>
        <Container maxWidth="lg">
          <Typography component="h2" variant="h2" id="comparison-heading" sx={{ color: '#0F172A', mb: 3 }}>
            8-Vertical Capability &amp; Device Matrix
          </Typography>

          <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #CBD5E1', borderRadius: 2 }}>
            <Table aria-label="Industry verticals capability comparison">
              <caption style={{ textAlign: 'left', padding: '12px 16px', color: '#334155', fontSize: '0.875rem' }}>
                Overview of primary clinical users, deterministic safety anchors, and responsive field form-factors per vertical.
              </caption>
              <TableHead sx={{ bgcolor: '#F1F5F9' }}>
                <TableRow>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>Vertical</TableCell>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>Primary Clinical Users</TableCell>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>Signature Clinical Capability</TableCell>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>Device Form-Factors</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {INDUSTRY_VERTICALS.map((v) => (
                  <TableRow key={v.slug} hover>
                    <TableCell component="th" scope="row" sx={{ fontWeight: 800 }}>
                      <Box component={Link} href={`/verticals/${v.slug}/`} sx={{ color: '#134E68', textDecoration: 'underline' }}>
                        {v.brand} ({v.forLabel})
                      </Box>
                    </TableCell>
                    <TableCell sx={{ color: '#334155' }}>{v.roleLabel}</TableCell>
                    <TableCell sx={{ color: '#0F172A', fontWeight: 600 }}>
                      {v.kpis[0].value} + {v.kpis[1].value}
                    </TableCell>
                    <TableCell sx={{ color: '#334155' }}>{v.mobileReadyNote}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Container>
      </Box>
    </Box>
  );
}
