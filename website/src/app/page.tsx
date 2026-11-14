import React from 'react';
import Link from 'next/link';
import {
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Container,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';
import ShieldRoundedIcon from '@mui/icons-material/ShieldRounded';
import DevicesRoundedIcon from '@mui/icons-material/DevicesRounded';
import VerifiedRoundedIcon from '@mui/icons-material/VerifiedRounded';
import LockRoundedIcon from '@mui/icons-material/LockRounded';
import { HEALTH_TECH_AGENTS } from '@/data/agentsData';
import { INDUSTRY_VERTICALS } from '@/data/verticalsData';
import { AgentSolutionCard } from '@/components/AgentSolutionCard';

export default function HomePage() {
  return (
    <Box>
      {/* HERO */}
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{
          bgcolor: '#0F172A',
          backgroundImage: 'linear-gradient(135deg, #0F172A 0%, #133B54 65%, #0F291E 100%)',
          color: '#FFFFFF',
          py: { xs: 7, md: 10 },
          borderBottom: '2px solid #38BDF8',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={{ xs: 4, md: 6 }} alignItems="center">
            <Grid size={{ xs: 12, md: 7 }}>
              <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mb: 2.5 }}>
                <Chip
                  label="16 Autonomous Health-Tech Agents"
                  color="primary"
                  size="small"
                  sx={{ border: '1px solid #7DD3FC' }}
                />
                <Chip
                  label="8 Specialized Clinical Verticals"
                  size="small"
                  sx={{ bgcolor: '#1E293B', color: '#F8FAFC', border: '1px solid #475569' }}
                />
                <Chip
                  label="Desktop • Tablet • Mobile Home Care"
                  size="small"
                  sx={{ bgcolor: '#0F291E', color: '#DCFCE7', border: '1px solid #4ADE80' }}
                />
              </Stack>

              <Typography
                component="h1"
                variant="h1"
                id="page-heading"
                tabIndex={-1}
                sx={{ color: '#FFFFFF', mb: 2.5, outline: 'none' }}
              >
                Autonomous Clinical &amp; Security Agents That Never Guess With Patient Safety.
              </Typography>

              <Typography variant="body1" sx={{ color: '#E2E8F0', fontSize: '1.1rem', mb: 3.5, maxWidth: 650 }}>
                SlainteTech pairs sovereign HL7 FHIR R4 infrastructure with 16 specialized agents governed by deterministic Python FastMCP guardrails — delivering zero-hallucination triage, 3-Tier pharmacology, ambient scribing, and OWASP/NIS2 security across 8 healthcare verticals.
              </Typography>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ mb: 4 }}>
                <Button
                  component={Link}
                  href="/verticals/"
                  variant="contained"
                  color="primary"
                  endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                  sx={{ border: '1px solid #7DD3FC' }}
                >
                  Explore Industry Verticals
                </Button>
                <Button
                  component={Link}
                  href="/health-tech-agents/"
                  variant="outlined"
                  sx={{
                    color: '#FFFFFF',
                    borderColor: '#94A3B8',
                    '&:hover': { borderColor: '#FFFFFF', bgcolor: 'rgba(255,255,255,0.08)' },
                  }}
                >
                  Inspect All 16 Agents
                </Button>
                <Button
                  component={Link}
                  href="/investors/"
                  variant="outlined"
                  sx={{
                    color: '#BAE6FD',
                    borderColor: '#38BDF8',
                    '&:hover': { borderColor: '#7DD3FC', bgcolor: 'rgba(56,189,248,0.12)' },
                  }}
                >
                  Investor Thesis
                </Button>
              </Stack>

              <Grid container spacing={2}>
                {[
                  { stat: '0% LLM Math', detail: 'RCP NEWS2, MTS Cat 1–5 & 3-Tier Rx-Guard run in deterministic Python' },
                  { stat: '330+ Automated Tests', detail: 'Continuous CI verification across security, RBAC, and FHIR R4 schemas' },
                  { stat: '100% Air-Gap Capable', detail: 'Runs on local 3B Ollama models or BAA-gated cloud frontier APIs' },
                ].map((item) => (
                  <Grid key={item.stat} size={{ xs: 12, sm: 4 }}>
                    <Box sx={{ p: 1.75, borderRadius: 2, bgcolor: 'rgba(15, 23, 42, 0.72)', border: '1px solid #334155', height: '100%' }}>
                      <Typography sx={{ fontWeight: 800, color: '#7DD3FC', fontSize: '1.05rem', mb: 0.4 }}>
                        {item.stat}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#CBD5E1', display: 'block', lineHeight: 1.45 }}>
                        {item.detail}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Grid>

            <Grid size={{ xs: 12, md: 5 }}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 3,
                  bgcolor: '#0B192C',
                  border: '1px solid #38BDF8',
                  color: '#FFFFFF',
                }}
              >
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                  <Typography variant="caption" sx={{ fontFamily: 'monospace', color: '#7DD3FC', fontWeight: 800 }}>
                    LIVE PLATFORM ARCHITECTURE
                  </Typography>
                  <Box
                    component="span"
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 0.75,
                      fontSize: '0.75rem',
                      fontFamily: 'monospace',
                      color: '#86EFAC',
                    }}
                  >
                    <Box
                      component="span"
                      className="telemetry-pulse"
                      sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#22C55E', display: 'inline-block' }}
                    />
                    VERIFIED R4
                  </Box>
                </Stack>

                <Stack spacing={1.5}>
                  {[
                    {
                      layer: 'Layer 1 • Responsive Clinical & Field Verticals',
                      desc: '8 role-specific workspaces (ED, GP & Home Nursing, Psychiatry, Dentistry, Pharmacy, Ambulance Tablet ePCR, Elite Sport, Aerospace).',
                    },
                    {
                      layer: 'Layer 2 • 16 Autonomous Health-Tech Agents',
                      desc: '3 specialized squads: SlainteShield Security (3), SlainteGov Governance (5), and SlainteClinical Care (8).',
                    },
                    {
                      layer: 'Layer 3 • FastMCP Deterministic Safety Kernel (:8081)',
                      desc: 'Hard-coded Python clinical calculators, 3-Tier pharmacology cross-reactivity/DDI/eGFR gates, and RFC 1918 red-team locks.',
                    },
                    {
                      layer: 'Layer 4 • Sovereign HL7 FHIR R4 & Append-Only Audit (:8082)',
                      desc: 'Micro-EHR compartment store, SMART-on-FHIR v2 PKCE sidecar, SHA-256 Provenance signatures, and SQLite tamper-rejection triggers.',
                    },
                  ].map((box) => (
                    <Box
                      key={box.layer}
                      sx={{
                        p: 1.75,
                        borderRadius: 2,
                        bgcolor: '#13263E',
                        border: '1px solid #294364',
                      }}
                    >
                      <Typography sx={{ fontWeight: 800, fontSize: '0.88rem', color: '#F8FAFC', mb: 0.4 }}>
                        {box.layer}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#CBD5E1', display: 'block', lineHeight: 1.45 }}>
                        {box.desc}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* "FOR..." INDUSTRY VERTICALS SECTION */}
      <Box component="section" aria-labelledby="for-verticals-heading" sx={{ py: { xs: 7, md: 9 } }}>
        <Container maxWidth="lg">
          <Stack
            direction={{ xs: 'column', md: 'row' }}
            justifyContent="space-between"
            alignItems={{ xs: 'flex-start', md: 'flex-end' }}
            spacing={2}
            sx={{ mb: 4.5 }}
          >
            <Box sx={{ maxWidth: 720 }}>
              <Typography variant="overline" sx={{ color: '#134E68', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
                8 Purpose-Built Clinical Verticals
              </Typography>
              <Typography component="h2" variant="h2" id="for-verticals-heading" sx={{ color: '#0F172A', mb: 1 }}>
                Built For Every Frontline Care Setting
              </Typography>
              <Typography variant="body1" sx={{ color: '#334155' }}>
                One underlying HL7 FHIR R4 + FastMCP engine tailored into 8 distinct operational verticals — each with its own clinical workflows, bespoke interface, and responsive mobile/tablet ergonomics.
              </Typography>
            </Box>
            <Button component={Link} href="/verticals/" variant="outlined" color="primary">
              Compare All 8 Verticals
            </Button>
          </Stack>

          <Grid container spacing={3}>
            {INDUSTRY_VERTICALS.map((v) => (
              <Grid key={v.slug} size={{ xs: 12, sm: 6, md: 3 }}>
                <Card
                  className="slainte-interactive-card"
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    bgcolor: '#FFFFFF',
                    borderTop: `4px solid ${v.palette.accentMain}`,
                  }}
                >
                  <CardContent sx={{ p: 2.75 }}>
                    <Box
                      component="span"
                      sx={{
                        display: 'inline-block',
                        bgcolor: v.palette.badgeBg,
                        color: v.palette.badgeText,
                        px: 1.2,
                        py: 0.4,
                        borderRadius: '6px',
                        fontSize: '0.74rem',
                        fontWeight: 800,
                        mb: 1.5,
                      }}
                    >
                      {v.brand}
                    </Box>
                    <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 1, fontSize: '1.1rem' }}>
                      {v.forLabel}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#334155', fontSize: '0.88rem', mb: 1.5 }}>
                      {v.heroHeadline}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#134E68', fontWeight: 700, display: 'block' }}>
                      {v.kpis[0].value} • {v.kpis[1].value}
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ px: 2.75, pb: 2.5, pt: 0 }}>
                    <Button
                      component={Link}
                      href={`/verticals/${v.slug}/`}
                      size="small"
                      variant="outlined"
                      fullWidth
                      endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                      sx={{
                        color: v.palette.accentMain,
                        borderColor: v.palette.accentMain,
                        justifyContent: 'space-between',
                      }}
                    >
                      Explore {v.brand}
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* RESPONSIVE CARE-AT-HOME & AMBULANCE TABLET CALLOUT */}
      <Box
        component="section"
        aria-labelledby="responsive-field-heading"
        sx={{
          py: { xs: 6, md: 7.5 },
          bgcolor: '#FFFFFF',
          borderTop: '1px solid #CBD5E1',
          borderBottom: '1px solid #CBD5E1',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid size={{ xs: 12, md: 7 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <DevicesRoundedIcon sx={{ color: '#1B6B8D' }} aria-hidden="true" />
                <Typography variant="overline" sx={{ color: '#134E68', fontWeight: 800, letterSpacing: '0.08em' }}>
                  Responsive Desktop, Rugged Tablet &amp; Smartphone Clinical UX
                </Typography>
              </Stack>
              <Typography component="h2" variant="h2" id="responsive-field-heading" sx={{ color: '#0F172A', mb: 1.5 }}>
                Engineered for Care-at-Home Nurses, Community Teams &amp; Moving Ambulances
              </Typography>
              <Typography variant="body1" sx={{ color: '#334155', mb: 2.5 }}>
                Healthcare no longer stays behind a hospital desk. Both the SlainteTech clinical platform and vertical workspaces adapt automatically to smartphones and ruggedised ambulance tablets with off-canvas touch drawers, sticky 1-thumb quick docks, 44px coarse-pointer targets, and WCAG 2.2 AA contrast.
              </Typography>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
                <Button component={Link} href="/verticals/general-practice/" variant="contained" color="primary">
                  Community &amp; Home Nursing UX
                </Button>
                <Button component={Link} href="/verticals/ambulance-ems/" variant="outlined" color="primary">
                  Ambulance Tablet ePCR UX
                </Button>
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, md: 5 }}>
              <Stack spacing={1.5}>
                {[
                  {
                    icon: <DevicesRoundedIcon sx={{ color: '#1B6B8D' }} aria-hidden="true" />,
                    title: '44px Glove & Thumb Touch Targets',
                    text: 'Coarse-pointer media queries enlarge bedside inputs, odontogram teeth, and triage actions automatically.',
                  },
                  {
                    icon: <ShieldRoundedIcon sx={{ color: '#15803D' }} aria-hidden="true" />,
                    title: 'Sticky Field Bottom Quick-Dock',
                    text: 'Instant 1-tap switching across Triage, Patients, Vertical Workspace, and Autonomous Agents on phones and iPads.',
                  },
                  {
                    icon: <LockRoundedIcon sx={{ color: '#B91C1C' }} aria-hidden="true" />,
                    title: 'WCAG 2.2 AA & High-Contrast Ready',
                    text: 'Readable under bright ambulance bay glare or dimmed night-shift wards with zero rainbow visual noise.',
                  },
                ].map((feat) => (
                  <Paper key={feat.title} elevation={0} sx={{ p: 2, border: '1px solid #CBD5E1', borderRadius: 2, bgcolor: '#F8FAFC' }}>
                    <Stack direction="row" spacing={1.5} alignItems="flex-start">
                      <Box sx={{ mt: 0.25 }}>{feat.icon}</Box>
                      <Box>
                        <Typography component="h3" variant="h3" sx={{ fontSize: '1rem', color: '#0F172A', mb: 0.25 }}>
                          {feat.title}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#334155', fontSize: '0.88rem' }}>
                          {feat.text}
                        </Typography>
                      </Box>
                    </Stack>
                  </Paper>
                ))}
              </Stack>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* ALL 16 AUTONOMOUS HEALTH-TECH AGENTS GRID */}
      <Box component="section" aria-labelledby="agents-fleet-heading" sx={{ py: { xs: 7, md: 9 } }}>
        <Container maxWidth="lg">
          <Stack
            direction={{ xs: 'column', md: 'row' }}
            justifyContent="space-between"
            alignItems={{ xs: 'flex-start', md: 'flex-end' }}
            spacing={2}
            sx={{ mb: 4.5 }}
          >
            <Box sx={{ maxWidth: 740 }}>
              <Typography variant="overline" sx={{ color: '#134E68', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
                3 Specialized Squads • 16 Verified Agents
              </Typography>
              <Typography component="h2" variant="h2" id="agents-fleet-heading" sx={{ color: '#0F172A', mb: 1 }}>
                Autonomous Health-Tech Agents
              </Typography>
              <Typography variant="body1" sx={{ color: '#334155' }}>
                Every agent has its own dedicated dashboard, FastMCP safety gate, HL7 FHIR R4 resource binding, and immutable SQLite audit trail.
              </Typography>
            </Box>
            <Button component={Link} href="/health-tech-agents/" variant="contained" color="primary">
              Filter Agents by Squad
            </Button>
          </Stack>

          <Grid container spacing={3}>
            {HEALTH_TECH_AGENTS.map((agent) => (
              <Grid key={agent.slug} size={{ xs: 12, sm: 6, md: 4 }}>
                <AgentSolutionCard agent={agent} headingLevel="h3" />
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* REAL-WORLD HEALTHCARE DELIVERY & CLINICAL PHOTOGRAPHY */}
      <Box
        component="section"
        aria-labelledby="clinical-delivery-heading"
        sx={{
          py: { xs: 7, md: 9 },
          bgcolor: '#FFFFFF',
          borderTop: '1px solid #E2E8F0',
          borderBottom: '1px solid #E2E8F0',
        }}
      >
        <Container maxWidth="lg">
          <Stack spacing={2} sx={{ mb: 4.5, maxWidth: 780 }}>
            <Typography variant="overline" sx={{ color: '#134E68', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
              Real-World Clinical Environments
            </Typography>
            <Typography component="h2" variant="h2" id="clinical-delivery-heading" sx={{ color: '#0F172A' }}>
              Built for Frontline Clinicians, Hospital Trusts &amp; Community Care Teams
            </Typography>
            <Typography variant="body1" sx={{ color: '#334155' }}>
              Like leading healthcare technology platforms, SlainteTech is designed for real clinical workflows — from high-acuity resuscitation bays and multi-disciplinary inpatient rounds to community nursing and enterprise cybersecurity command centres.
            </Typography>
          </Stack>

          <Grid container spacing={3}>
            {[
              {
                img: '/images/hero-clinicians.jpg',
                title: 'Multi-Disciplinary Clinical Rounds',
                subtitle: 'Hospital Inpatient & Specialist Wards',
                desc: 'Physicians and charge nurses review live vital trajectories, NEWS2 early warnings, and cited AI bedside briefings on mobile tablets.',
              },
              {
                img: '/images/bedside-doctor.jpg',
                title: 'Point-of-Care Bedside Review',
                subtitle: 'General Practice & Ambulatory Care',
                desc: 'Ambient voice scribing drafts structured SOAP notes and pre-screened orders while clinicians maintain unbroken eye contact with patients.',
              },
              {
                img: '/images/emergency-team.jpg',
                title: 'Acute Emergency Resuscitation',
                subtitle: 'Emergency Departments & Trauma Bays',
                desc: 'Manchester Triage Cat 1–5 urgency calculation and automated ambulance pre-alert telemetry prepared before the patient arrives.',
              },
              {
                img: '/images/telehealth-nurse.jpg',
                title: 'Chronic Disease Surveillance',
                subtitle: 'Primary Care & Care-at-Home Nursing',
                desc: 'Continuous surveillance of diabetic and hypertensive panels to surface overdue surveillance markers and proactive recall interventions.',
              },
              {
                img: '/images/security-soc.jpg',
                title: 'CISO Cybersecurity Command',
                subtitle: 'EU NIS2 & SIEM Webhook Telemetry',
                desc: 'Continuous Article 21 technical safeguards verification with live HMAC-signed security alerts dispatched to Sentinel, Splunk, and PagerDuty.',
              },
            ].map((card, idx) => (
              <Grid key={card.title} size={{ xs: 12, sm: 6, md: idx === 0 ? 8 : idx === 1 ? 4 : 4 }}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    borderRadius: 2,
                    border: '1px solid #CBD5E1',
                    overflow: 'hidden',
                    boxShadow: '0 2px 8px rgba(15, 23, 42, 0.06)',
                    transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 18px rgba(15, 23, 42, 0.12)',
                    },
                  }}
                >
                  <Box
                    component="img"
                    src={card.img}
                    alt={card.title}
                    sx={{
                      width: '100%',
                      height: idx === 0 ? 240 : 190,
                      objectFit: 'cover',
                      display: 'block',
                      bgcolor: '#0F172A',
                    }}
                  />
                  <CardContent sx={{ p: 2.5, flexGrow: 1 }}>
                    <Typography variant="overline" sx={{ color: '#1B6B8D', fontWeight: 800, fontSize: '0.72rem' }}>
                      {card.subtitle}
                    </Typography>
                    <Typography component="h3" variant="h3" sx={{ fontSize: '1.05rem', color: '#0F172A', mb: 0.75 }}>
                      {card.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#475569', fontSize: '0.86rem', lineHeight: 1.5 }}>
                      {card.desc}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* DECISION-MAKER & INVESTOR FOOTER CTA */}
      <Box
        component="section"
        aria-labelledby="decision-makers-heading"
        sx={{
          py: { xs: 6, md: 8 },
          bgcolor: '#0F172A',
          color: '#FFFFFF',
          borderTop: '2px solid #1B6B8D',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid size={{ xs: 12, md: 7 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <VerifiedRoundedIcon sx={{ color: '#38BDF8' }} aria-hidden="true" />
                <Typography variant="overline" sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em' }}>
                  For Hospital CISOs, Clinical Directors &amp; Institutional Investors
                </Typography>
              </Stack>
              <Typography component="h2" variant="h2" id="decision-makers-heading" sx={{ color: '#FFFFFF', mb: 1.5 }}>
                Land With Zero-Disruption Security. Expand Into Full Clinical Verticals.
              </Typography>
              <Typography variant="body1" sx={{ color: '#CBD5E1' }}>
                Deploy as a 15-minute read-only SMART-on-FHIR v2 security &amp; HIPE coding sidecar alongside Epic, Cerner, or MEDITECH — or launch standalone sovereign verticals for clinics, pharmacies, ambulances, and aerospace missions.
              </Typography>
            </Grid>
            <Grid size={{ xs: 12, md: 5 }}>
              <Stack spacing={1.5}>
                <Button
                  component={Link}
                  href="/contact/"
                  variant="contained"
                  color="primary"
                  size="large"
                  endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                  sx={{ border: '1px solid #7DD3FC' }}
                >
                  Book a 30-Minute Live Architecture Demo
                </Button>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
                  <Button
                    component={Link}
                    href="/pricing/"
                    variant="outlined"
                    fullWidth
                    sx={{ color: '#FFFFFF', borderColor: '#64748B', '&:hover': { borderColor: '#FFFFFF' } }}
                  >
                    View Commercial Tiers
                  </Button>
                  <Button
                    component={Link}
                    href="/security-compliance/"
                    variant="outlined"
                    fullWidth
                    sx={{ color: '#FFFFFF', borderColor: '#64748B', '&:hover': { borderColor: '#FFFFFF' } }}
                  >
                    NIS2 &amp; EU AI Act Matrix
                  </Button>
                </Stack>
              </Stack>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}
