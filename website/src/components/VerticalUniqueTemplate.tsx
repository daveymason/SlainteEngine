import React from 'react';
import Link from 'next/link';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';
import DevicesRoundedIcon from '@mui/icons-material/DevicesRounded';
import CheckCircleRoundedIcon from '@mui/icons-material/CheckCircleRounded';
import WarningAmberRoundedIcon from '@mui/icons-material/WarningAmberRounded';
import VerifiedUserRoundedIcon from '@mui/icons-material/VerifiedUserRounded';
import { HEALTH_TECH_AGENTS } from '@/data/agentsData';
import { INDUSTRY_VERTICALS, type VerticalRecord } from '@/data/verticalsData';
import { VerticalUniqueGraphic } from '@/components/VisualSchematics';
import { AgentSolutionCard } from '@/components/AgentSolutionCard';

/**
 * Unlike the canonical identical Agent pages, each of the 8 Vertical pages has:
 * - Its own WCAG-AA verified bespoke palette (`vertical.palette`)
 * - Its own unique custom SVG illustration (`<VerticalUniqueGraphic variant={vertical.layoutVariant} />`)
 * - Distinct section composition & visual framing keyed to `vertical.layoutVariant`
 */
export function VerticalUniqueTemplate({ vertical }: { vertical: VerticalRecord }) {
  const { palette } = vertical;
  const assignedAgents = vertical.assignedAgentSlugs
    .map((slug) => HEALTH_TECH_AGENTS.find((a) => a.slug === slug))
    .filter((a): a is NonNullable<typeof a> => Boolean(a));

  const otherVerticals = INDUSTRY_VERTICALS.filter((v) => v.slug !== vertical.slug);

  // Alternate visual hero alignment & KPI strip architecture per vertical variant so each industry feels bespoke
  const reverseHeroColumns =
    vertical.layoutVariant === 'longitudinal-care' ||
    vertical.layoutVariant === 'precision-odontogram' ||
    vertical.layoutVariant === 'rugged-field-tablet' ||
    vertical.layoutVariant === 'orbital-airgap';

  const timelineWorkflowStyle =
    vertical.layoutVariant === 'resuscitation-command' ||
    vertical.layoutVariant === 'rugged-field-tablet' ||
    vertical.layoutVariant === 'athletic-telemetry' ||
    vertical.layoutVariant === 'orbital-airgap';

  return (
    <Box>
      {/* BESPOKE VERTICAL HERO */}
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{
          bgcolor: palette.heroBg,
          backgroundImage: palette.heroGradient,
          color: palette.heroText,
          py: { xs: 6, md: 9 },
          borderBottom: `3px solid ${palette.accentMain}`,
        }}
      >
        <Container maxWidth="lg">
          <Box component="nav" aria-label="Breadcrumb" sx={{ mb: 2.5 }}>
            <Stack
              component="ol"
              direction="row"
              flexWrap="wrap"
              spacing={1}
              alignItems="center"
              sx={{ listStyle: 'none', p: 0, m: 0, fontSize: '0.875rem', color: palette.heroMuted }}
            >
              <li>
                <Box component={Link} href="/" sx={{ color: '#FFFFFF', textDecoration: 'underline' }}>
                  Home
                </Box>
              </li>
              <li aria-hidden="true">/</li>
              <li>
                <Box component={Link} href="/verticals/" sx={{ color: '#FFFFFF', textDecoration: 'underline' }}>
                  Industry Verticals
                </Box>
              </li>
              <li aria-hidden="true">/</li>
              <li aria-current="page" style={{ fontWeight: 800 }}>
                {vertical.brand}
              </li>
            </Stack>
          </Box>

          <Grid
            container
            spacing={{ xs: 4, md: 5 }}
            alignItems="center"
            direction={reverseHeroColumns ? { xs: 'column', md: 'row-reverse' } : 'row'}
          >
            <Grid size={{ xs: 12, md: 7 }}>
              <Stack direction="row" flexWrap="wrap" gap={1} alignItems="center" sx={{ mb: 2 }}>
                <Box
                  component="span"
                  sx={{
                    bgcolor: palette.badgeBg,
                    color: palette.badgeText,
                    px: 1.5,
                    py: 0.5,
                    borderRadius: '6px',
                    fontWeight: 800,
                    fontSize: '0.8rem',
                    letterSpacing: '0.03em',
                  }}
                >
                  {vertical.forLabel}
                </Box>
                <Box
                  component="span"
                  sx={{
                    bgcolor: 'rgba(15, 23, 42, 0.68)',
                    color: '#FFFFFF',
                    border: '1px solid rgba(255,255,255,0.35)',
                    px: 1.4,
                    py: 0.5,
                    borderRadius: '6px',
                    fontFamily: 'monospace',
                    fontWeight: 700,
                    fontSize: '0.8rem',
                  }}
                >
                  In-App Vertical: {vertical.brand}
                </Box>
              </Stack>

              <Typography
                component="h1"
                variant="h1"
                id="page-heading"
                tabIndex={-1}
                sx={{ color: palette.heroText, mb: 2, outline: 'none' }}
              >
                {vertical.heroHeadline}
              </Typography>

              <Typography variant="body1" sx={{ color: palette.heroMuted, fontSize: '1.06rem', mb: 2.5 }}>
                {vertical.heroLead}
              </Typography>

              {/* Responsive Mobile / Tablet Field Readiness Callout */}
              <Paper
                elevation={0}
                sx={{
                  p: 1.75,
                  mb: 3,
                  bgcolor: 'rgba(15, 23, 42, 0.72)',
                  color: '#FFFFFF',
                  border: '1px solid rgba(255,255,255,0.28)',
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 1.5,
                }}
              >
                <DevicesRoundedIcon sx={{ color: '#7DD3FC', mt: 0.25, flexShrink: 0 }} aria-hidden="true" />
                <Typography variant="body2" sx={{ color: '#F8FAFC' }}>
                  <strong>Responsive Desktop, Tablet &amp; Mobile UX:</strong> {vertical.mobileReadyNote}
                </Typography>
              </Paper>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
                <Button
                  component={Link}
                  href="/contact/"
                  variant="contained"
                  endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                  sx={{
                    bgcolor: '#FFFFFF',
                    color: '#0F172A',
                    '&:hover': { bgcolor: '#F1F5F9' },
                  }}
                >
                  Request {vertical.brand} Live Demo
                </Button>
                <Button
                  component={Link}
                  href="/pricing/"
                  variant="outlined"
                  sx={{
                    color: '#FFFFFF',
                    borderColor: 'rgba(255,255,255,0.6)',
                    '&:hover': { borderColor: '#FFFFFF', bgcolor: 'rgba(255,255,255,0.1)' },
                  }}
                >
                  View Vertical Licensing
                </Button>
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, md: 5 }}>
              <VerticalUniqueGraphic variant={vertical.layoutVariant} brand={vertical.brand} />
            </Grid>
          </Grid>

          {/* BESPOKE KPI STRIP */}
          <Grid container spacing={2.5} sx={{ mt: { xs: 3, md: 5 } }}>
            {vertical.kpis.map((kpi) => (
              <Grid key={kpi.label} size={{ xs: 12, md: 4 }}>
                <Box
                  sx={{
                    p: 2.5,
                    borderRadius: 2.5,
                    bgcolor: 'rgba(15, 23, 42, 0.78)',
                    border: '1px solid rgba(255, 255, 255, 0.24)',
                    height: '100%',
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{ color: palette.heroMuted, fontFamily: 'monospace', fontWeight: 700, textTransform: 'uppercase' }}
                  >
                    {kpi.label}
                  </Typography>
                  <Typography sx={{ fontSize: '1.65rem', fontWeight: 800, color: '#FFFFFF', my: 0.5 }}>
                    {kpi.value}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#E2E8F0' }}>
                    {kpi.detail}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* PAIN POINTS VS. DETERMINISTIC SLAINTETECH FIX */}
      <Box
        component="section"
        aria-labelledby="clinical-challenges-heading"
        sx={{ py: { xs: 6, md: 8 }, bgcolor: palette.surfaceTint, borderBottom: `1px solid ${palette.borderTint}` }}
      >
        <Container maxWidth="lg">
          <Box sx={{ mb: 4, maxWidth: 760 }}>
            <Typography
              variant="overline"
              sx={{ color: palette.accentMain, fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}
            >
              Built Specifically for {vertical.roleLabel}
            </Typography>
            <Typography component="h2" variant="h2" id="clinical-challenges-heading" sx={{ color: '#0F172A' }}>
              Replacing Legacy Clinical Friction With Deterministic Safety
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {vertical.painPointsSolved.map((item, idx) => (
              <Grid key={idx} size={{ xs: 12, md: 4 }}>
                <Card
                  className="slainte-surface-panel"
                  sx={{
                    height: '100%',
                    bgcolor: '#FFFFFF',
                    borderTop: `4px solid ${palette.accentMain}`,
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Stack direction="row" spacing={1} alignItems="flex-start" sx={{ mb: 2 }}>
                      <WarningAmberRoundedIcon sx={{ color: '#B45309', mt: 0.25, flexShrink: 0 }} aria-hidden="true" />
                      <Box>
                        <Typography variant="caption" sx={{ fontWeight: 800, color: '#B45309', textTransform: 'uppercase' }}>
                          Legacy Risk #{idx + 1}
                        </Typography>
                        <Typography component="h3" variant="h3" sx={{ fontSize: '1.05rem', color: '#0F172A', mt: 0.25 }}>
                          {item.pain}
                        </Typography>
                      </Box>
                    </Stack>

                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 2,
                        bgcolor: palette.surfaceTint,
                        border: `1px solid ${palette.borderTint}`,
                      }}
                    >
                      <Stack direction="row" spacing={1} alignItems="flex-start">
                        <CheckCircleRoundedIcon sx={{ color: '#15803D', mt: 0.25, flexShrink: 0 }} aria-hidden="true" />
                        <Typography variant="body2" sx={{ color: '#0F172A', fontWeight: 500 }}>
                          <strong>{vertical.brand} Guardrail:</strong> {item.deterministicFix}
                        </Typography>
                      </Stack>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* OPERATIONAL WORKFLOW & EXECUTIVE BUYER / INVESTOR ROI */}
      <Box component="section" aria-labelledby="workflow-roi-heading" sx={{ py: { xs: 6, md: 8 }, bgcolor: '#FFFFFF', borderBottom: '1px solid #CBD5E1' }}>
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="stretch">
            <Grid size={{ xs: 12, md: 7 }}>
              <Typography
                variant="overline"
                sx={{ color: palette.accentMain, fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}
              >
                Live In-App Workflow (&ldquo;Sign in as {vertical.brand}&rdquo;)
              </Typography>
              <Typography component="h2" variant="h2" id="workflow-roi-heading" sx={{ color: '#0F172A', mb: 3 }}>
                3-Step Operational Execution
              </Typography>

              <Stack spacing={2}>
                {vertical.workflowSteps.map((ws) => (
                  <Paper
                    key={ws.step}
                    elevation={0}
                    sx={{
                      p: 2.5,
                      borderRadius: 2.5,
                      border: '1px solid #CBD5E1',
                      borderLeft: timelineWorkflowStyle ? `5px solid ${palette.accentMain}` : '1px solid #CBD5E1',
                      bgcolor: timelineWorkflowStyle ? '#F8FAFC' : '#FFFFFF',
                      display: 'flex',
                      gap: 2,
                      alignItems: 'flex-start',
                    }}
                  >
                    <Box
                      sx={{
                        minWidth: 42,
                        height: 42,
                        borderRadius: '10px',
                        bgcolor: palette.badgeBg,
                        color: palette.badgeText,
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontFamily: 'monospace',
                        fontWeight: 800,
                      }}
                    >
                      {ws.step}
                    </Box>
                    <Box>
                      <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 0.5 }}>
                        {ws.title}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#334155' }}>
                        {ws.detail}
                      </Typography>
                    </Box>
                  </Paper>
                ))}
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, md: 5 }}>
              <Paper
                elevation={0}
                sx={{
                  height: '100%',
                  p: { xs: 3, md: 3.5 },
                  borderRadius: 3,
                  bgcolor: '#0F172A',
                  color: '#FFFFFF',
                  border: `2px solid ${palette.accentMain}`,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <Box>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                    <VerifiedUserRoundedIcon sx={{ color: '#7DD3FC' }} aria-hidden="true" />
                    <Typography variant="overline" sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em' }}>
                      Decision-Maker &amp; Buyer Brief
                    </Typography>
                  </Stack>

                  <Typography component="h3" variant="h3" sx={{ color: '#FFFFFF', mb: 2.5 }}>
                    Commercial &amp; Governance Case for {vertical.brand}
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#94A3B8', fontWeight: 800, textTransform: 'uppercase' }}>
                      Primary Clinical &amp; Executive Buyers
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#F8FAFC', mt: 0.5 }}>
                      {vertical.buyerRoi.clinicalBuyer}
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: '#94A3B8', fontWeight: 800, textTransform: 'uppercase' }}>
                      Measurable Operational &amp; Financial ROI
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#F8FAFC', mt: 0.5 }}>
                      {vertical.buyerRoi.economicImpact}
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="caption" sx={{ color: '#94A3B8', fontWeight: 800, textTransform: 'uppercase' }}>
                      Regulatory &amp; Medico-Legal Guarantee
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#DCFCE7', mt: 0.5 }}>
                      {vertical.buyerRoi.complianceGuarantee}
                    </Typography>
                  </Box>
                </Box>

                <Button
                  component={Link}
                  href="/contact/"
                  variant="contained"
                  color="primary"
                  fullWidth
                  endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                  sx={{ border: '1px solid #7DD3FC' }}
                >
                  Schedule {vertical.brand} Pilot Review
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* ASSIGNED AUTONOMOUS AGENTS FOR THIS VERTICAL */}
      <Box component="section" aria-labelledby="assigned-agents-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="overline"
              sx={{ color: palette.accentMain, fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}
            >
              Autonomous Health-Tech Agents Active in {vertical.brand}
            </Typography>
            <Typography component="h2" variant="h2" id="assigned-agents-heading" sx={{ color: '#0F172A', mb: 1 }}>
              Pre-Configured Agent Fleet for {vertical.forLabel.replace(/^For /, '')}
            </Typography>
            <Typography variant="body2" sx={{ color: '#334155' }}>
              Each agent below runs natively inside the {vertical.brand} vertical with dedicated telemetry and audit trails.
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {assignedAgents.map((agent) => (
              <Grid key={agent.slug} size={{ xs: 12, sm: 6, md: 4 }}>
                <AgentSolutionCard agent={agent} headingLevel="h3" />
              </Grid>
            ))}
          </Grid>

          {/* Cross-vertical switcher pills */}
          <Paper elevation={0} sx={{ mt: 6, p: 3, bgcolor: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: 2.5 }}>
            <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 1.5 }}>
              Explore Other SlainteTech Industry Verticals
            </Typography>
            <Stack direction="row" flexWrap="wrap" gap={1}>
              {otherVerticals.map((ov) => (
                <Button
                  key={ov.slug}
                  component={Link}
                  href={`/verticals/${ov.slug}/`}
                  variant="outlined"
                  size="small"
                  sx={{
                    color: '#0F172A',
                    borderColor: '#94A3B8',
                    '&:hover': { borderColor: '#1B6B8D', bgcolor: '#F0F9FF' },
                  }}
                >
                  {ov.forLabel}
                </Button>
              ))}
            </Stack>
          </Paper>
        </Container>
      </Box>
    </Box>
  );
}
