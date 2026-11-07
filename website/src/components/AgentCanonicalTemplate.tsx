import React from 'react';
import Link from 'next/link';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
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
import VerifiedRoundedIcon from '@mui/icons-material/VerifiedRounded';
import HubRoundedIcon from '@mui/icons-material/HubRounded';
import { HEALTH_TECH_AGENTS, type AgentRecord } from '@/data/agentsData';
import { AgentIcon } from '@/components/AgentIcon';
import { AgentSchematicSvg } from '@/components/VisualSchematics';
import { AgentSolutionCard } from '@/components/AgentSolutionCard';

/**
 * Canonical, identical layout template shared across all 11 `/health-tech-agents/<agent-real-name>/` pages:
 * 1. Hero + Architecture Schematic
 * 2. 3-Column Deterministic Capabilities & Guardrails
 * 3. Full-Width Page Break featuring a verified real-world Vertical Use Case + direct Vertical link
 * 4. Technical Specification & HL7 FHIR R4 Binding Table
 * 5. End-of-page 3-Column Solution Grid showcasing the other 10 Health-Tech Agents
 */
export function AgentCanonicalTemplate({ agent }: { agent: AgentRecord }) {
  const otherAgents = HEALTH_TECH_AGENTS.filter((item) => item.slug !== agent.slug);

  return (
    <Box>
      {/* SECTION 1: CANONICAL AGENT HERO */}
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{
          bgcolor: '#0F172A',
          backgroundImage: 'linear-gradient(135deg, #0F172A 0%, #133B54 100%)',
          color: '#FFFFFF',
          py: { xs: 6, md: 9 },
          borderBottom: '1px solid #1E293B',
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
              sx={{ listStyle: 'none', p: 0, m: 0, fontSize: '0.875rem', color: '#CBD5E1' }}
            >
              <li>
                <Box component={Link} href="/" sx={{ color: '#BAE6FD', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
                  Home
                </Box>
              </li>
              <li aria-hidden="true">/</li>
              <li>
                <Box
                  component={Link}
                  href="/health-tech-agents/"
                  sx={{ color: '#BAE6FD', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
                >
                  Health-Tech Agents
                </Box>
              </li>
              <li aria-hidden="true">/</li>
              <li aria-current="page" style={{ color: '#FFFFFF', fontWeight: 700 }}>
                {agent.codeName}
              </li>
            </Stack>
          </Box>

          <Grid container spacing={{ xs: 4, md: 5 }} alignItems="center">
            <Grid size={{ xs: 12, md: 7 }}>
              <Stack direction="row" flexWrap="wrap" gap={1} alignItems="center" sx={{ mb: 2 }}>
                <Chip label={agent.squad} color={agent.squadColor} size="small" />
                <Chip
                  label={`Agent ID: ${agent.codeName}`}
                  size="small"
                  sx={{
                    bgcolor: '#1E293B',
                    color: '#F8FAFC',
                    border: '1px solid #475569',
                    fontFamily: 'monospace',
                  }}
                />
              </Stack>

              <Typography
                component="h1"
                variant="h1"
                id="page-heading"
                tabIndex={-1}
                sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
              >
                {agent.name}
              </Typography>

              <Typography variant="body1" sx={{ color: '#E2E8F0', fontSize: '1.08rem', mb: 3, maxWidth: 640 }}>
                {agent.heroSummary}
              </Typography>

              <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mb: 3.5 }}>
                {agent.fastMcpBadges.map((badge) => (
                  <Box
                    key={badge}
                    component="span"
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 0.75,
                      bgcolor: 'rgba(15, 23, 42, 0.72)',
                      color: '#E0F2FE',
                      border: '1px solid #38BDF8',
                      px: 1.4,
                      py: 0.6,
                      borderRadius: '6px',
                      fontSize: '0.82rem',
                      fontFamily: 'monospace',
                      fontWeight: 700,
                    }}
                  >
                    <VerifiedRoundedIcon sx={{ fontSize: 16, color: '#38BDF8' }} aria-hidden="true" />
                    {badge}
                  </Box>
                ))}
              </Stack>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
                <Button
                  component={Link}
                  href="/contact/"
                  variant="contained"
                  color="primary"
                  endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                  sx={{ border: '1px solid #7DD3FC' }}
                >
                  Deploy {agent.codeName} Pilot
                </Button>
                <Button
                  component={Link}
                  href={agent.verticalUseCase.verticalHref}
                  variant="outlined"
                  sx={{
                    color: '#FFFFFF',
                    borderColor: '#94A3B8',
                    '&:hover': { borderColor: '#FFFFFF', bgcolor: 'rgba(255,255,255,0.08)' },
                  }}
                >
                  {agent.verticalUseCase.verticalTitle}
                </Button>
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, md: 5 }}>
              <AgentSchematicSvg agent={agent} />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* SECTION 2: 3-COLUMN DETERMINISTIC CAPABILITIES */}
      <Box component="section" aria-labelledby="capabilities-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Box sx={{ mb: 4, maxWidth: 740 }}>
            <Typography
              variant="overline"
              sx={{ color: '#134E68', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}
            >
              Deterministic FastMCP Execution
            </Typography>
            <Typography component="h2" variant="h2" id="capabilities-heading" sx={{ color: '#0F172A', mb: 1 }}>
              How {agent.codeName} Enforces Clinical &amp; Security Safety
            </Typography>
            <Typography variant="body1" sx={{ color: '#334155' }}>
              Every SlainteTech agent separates probabilistic language generation from deterministic Python safety thresholds, schema rules, and cryptographic audit trails.
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {agent.capabilities.map((cap) => (
              <Grid key={cap.title} size={{ xs: 12, md: 4 }}>
                <Card
                  className="slainte-surface-panel"
                  sx={{ height: '100%', bgcolor: '#FFFFFF', display: 'flex', flexDirection: 'column' }}
                >
                  <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                      <Box
                        sx={{
                          width: 42,
                          height: 42,
                          borderRadius: '10px',
                          bgcolor: '#E0F2FE',
                          color: '#0C4A6E',
                          border: '1px solid #BAE6FD',
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <AgentIcon iconKey={cap.iconKey} sx={{ fontSize: 22 }} />
                      </Box>
                      <Box
                        component="span"
                        sx={{
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          fontFamily: 'monospace',
                          bgcolor: '#DCFCE7',
                          color: '#14532D',
                          border: '1px solid #86EFAC',
                          px: 1.1,
                          py: 0.4,
                          borderRadius: '6px',
                        }}
                      >
                        {cap.guardrailChip}
                      </Box>
                    </Stack>
                    <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 1.25 }}>
                      {cap.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#334155' }}>
                      {cap.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* SECTION 3: FULL-WIDTH PAGE BREAK — REAL EXAMPLE VERTICAL USE CASE */}
      <Box
        component="section"
        aria-labelledby="vertical-use-case-heading"
        sx={{
          bgcolor: '#0C2D48',
          backgroundImage: 'linear-gradient(120deg, #0F172A 0%, #134E68 60%, #0F3D3E 100%)',
          color: '#FFFFFF',
          py: { xs: 6, md: 7.5 },
          borderTop: '2px solid #38BDF8',
          borderBottom: '2px solid #38BDF8',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid size={{ xs: 12, md: 8 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
                <HubRoundedIcon sx={{ color: '#7DD3FC', fontSize: 20 }} aria-hidden="true" />
                <Typography
                  variant="overline"
                  sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em', lineHeight: 1.2 }}
                >
                  {agent.verticalUseCase.eyebrow}
                </Typography>
              </Stack>

              <Typography component="h2" variant="h2" id="vertical-use-case-heading" sx={{ color: '#FFFFFF', mb: 2 }}>
                {agent.verticalUseCase.headline}
              </Typography>

              <Typography variant="body1" sx={{ color: '#E2E8F0', mb: 2.5, maxWidth: 720 }}>
                {agent.verticalUseCase.scenario}
              </Typography>

              <Box
                sx={{
                  display: 'inline-block',
                  bgcolor: '#0F291E',
                  color: '#DCFCE7',
                  border: '1px solid #4ADE80',
                  px: 2,
                  py: 1,
                  borderRadius: '8px',
                  fontFamily: 'monospace',
                  fontSize: '0.88rem',
                  fontWeight: 700,
                }}
              >
                Verified Impact: {agent.verticalUseCase.outcomeMetric}
              </Box>
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  bgcolor: 'rgba(15, 23, 42, 0.84)',
                  color: '#FFFFFF',
                  border: '1px solid #7DD3FC',
                  borderRadius: 3,
                }}
              >
                <Typography component="p" variant="subtitle2" sx={{ color: '#BAE6FD', fontWeight: 800, mb: 1 }}>
                  DEPLOYED INDUSTRY VERTICAL
                </Typography>
                <Typography variant="body2" sx={{ color: '#E2E8F0', mb: 2.5 }}>
                  See how {agent.codeName} operates inside the live {agent.verticalUseCase.verticalTitle.replace(/^For /, '')} workflow across desktop and mobile clinical devices.
                </Typography>
                <Button
                  component={Link}
                  href={agent.verticalUseCase.verticalHref}
                  variant="contained"
                  color="primary"
                  fullWidth
                  endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                  sx={{ border: '1px solid #7DD3FC' }}
                >
                  {agent.verticalUseCase.verticalTitle}
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* SECTION 4: TECHNICAL SPECIFICATION & HL7 FHIR R4 BINDING TABLE */}
      <Box component="section" aria-labelledby="specs-heading" sx={{ py: { xs: 6, md: 8 }, bgcolor: '#FFFFFF', borderBottom: '1px solid #CBD5E1' }}>
        <Container maxWidth="lg">
          <Typography
            variant="overline"
            sx={{ color: '#134E68', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}
          >
            Engineering &amp; Regulatory Verification
          </Typography>
          <Typography component="h2" variant="h2" id="specs-heading" sx={{ color: '#0F172A', mb: 3 }}>
            HL7 FHIR R4 Bindings &amp; Standards Alignment
          </Typography>

          <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #CBD5E1', borderRadius: 2 }}>
            <Table aria-label={`${agent.name} technical specification`}>
              <caption style={{ textAlign: 'left', padding: '12px 16px', color: '#334155', fontSize: '0.875rem' }}>
                Verified implementation parameters for {agent.codeName} inside the SlainteTech FastMCP &amp; HL7 FHIR R4 runtime.
              </caption>
              <TableHead sx={{ bgcolor: '#F1F5F9' }}>
                <TableRow>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>
                    Control Surface
                  </TableCell>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>
                    Deterministic Mechanism
                  </TableCell>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>
                    HL7 FHIR R4 / Endpoint Binding
                  </TableCell>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>
                    Regulatory / Clinical Standard
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {agent.technicalSpecs.map((row) => (
                  <TableRow key={row.parameter} hover>
                    <TableCell component="th" scope="row" sx={{ fontWeight: 700, color: '#0F172A', whiteSpace: 'nowrap' }}>
                      {row.parameter}
                    </TableCell>
                    <TableCell sx={{ color: '#334155' }}>{row.deterministicMechanism}</TableCell>
                    <TableCell sx={{ color: '#0F172A', fontFamily: 'monospace', fontSize: '0.84rem' }}>
                      {row.fhirBinding}
                    </TableCell>
                    <TableCell sx={{ color: '#134E68', fontWeight: 700 }}>{row.standardAlignment}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Container>
      </Box>

      {/* SECTION 5: OTHER AUTONOMOUS AGENTS IN A 3-COLUMN SOLUTION GRID */}
      <Box component="section" aria-labelledby="other-agents-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Stack
            direction={{ xs: 'column', md: 'row' }}
            justifyContent="space-between"
            alignItems={{ xs: 'flex-start', md: 'flex-end' }}
            spacing={2}
            sx={{ mb: 4 }}
          >
            <Box>
              <Typography
                variant="overline"
                sx={{ color: '#134E68', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}
              >
                Unified 11-Agent Sovereign Fleet
              </Typography>
              <Typography component="h2" variant="h2" id="other-agents-heading" sx={{ color: '#0F172A' }}>
                Explore the Other 10 Health-Tech Agents
              </Typography>
            </Box>
            <Button component={Link} href="/health-tech-agents/" variant="outlined" color="primary">
              View All 11 Agents Directory
            </Button>
          </Stack>

          <Grid container spacing={3}>
            {otherAgents.map((other) => (
              <Grid key={other.slug} size={{ xs: 12, sm: 6, md: 4 }}>
                <AgentSolutionCard agent={other} headingLevel="h3" />
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}
