import type { Metadata } from 'next';
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

export const metadata: Metadata = {
  title: 'Investor Thesis & Defensibility | SlainteTech AI Security Labs',
  description:
    'Why SlainteTech wins European and global healthcare AI: statutory NIS2 + EU AI Act regulatory tailwinds, deterministic FastMCP safety moat, and 8 verticals on 1 codebase.',
};

export default function InvestorsPage() {
  return (
    <Box>
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{
          bgcolor: '#0F172A',
          backgroundImage: 'linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%)',
          color: '#FFFFFF',
          py: { xs: 6, md: 8 },
          borderBottom: '2px solid #38BDF8',
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="overline" sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
            Institutional Investor &amp; Strategic Acquirer Brief
          </Typography>
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            The Deterministic Safety Layer for Regulated Healthcare AI
          </Typography>
          <Typography variant="body1" sx={{ color: '#E2E8F0', maxWidth: 760 }}>
            Healthcare providers face simultaneous statutory enforcement of the EU NIS2 Directive and the EU AI Act while clinicians suffer historic burnout. SlainteTech solves both problems in a single sovereign HL7 FHIR R4 + FastMCP platform.
          </Typography>
        </Container>
      </Box>

      <Box component="section" aria-labelledby="moats-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Typography component="h2" variant="h2" id="moats-heading" sx={{ color: '#0F172A', mb: 4 }}>
            Four Structural Moats
          </Typography>

          <Grid container spacing={3}>
            {[
              {
                title: '1. Zero-Hallucination FastMCP Clinical Math',
                body: 'Competitors wrapping raw LLMs cannot pass hospital Clinical Safety Case (DCB0129/0160) review because LLM weights hallucinate doses and triage scores. SlainteTech executes RCP NEWS2, MTS Cat 1–5, and 3-Tier Rx-Guard in deterministic Python.',
              },
              {
                title: '2. 15-Minute SMART-on-FHIR v2 "Wedge" Distribution',
                body: 'Instead of battling 24-month EHR replacement tenders, SlainteTech lands in 15 minutes as a read-only BOLA security & HIPE DRG coding sidecar that pays for itself in recovered uncoded hospital comorbidities.',
              },
              {
                title: '3. 1 Codebase Powering 8 Distinct Verticals',
                body: 'Emergency Medicine, GP & Mobile Home Nursing, Psychiatry, Dentistry, Pharmacy, Ambulance Tablet ePCR, Elite Sports, and Air-Gapped Aerospace all share one HL7 FHIR R4 + 11-Agent core — multiplying TAM with near-zero marginal R&D.',
              },
              {
                title: '4. Sovereign Air-Gap & Local 3B Readiness',
                body: 'Runs seamlessly on local quantized 3B models inside hospital VPCs, submarines, or spacecraft with zero external cloud PHI leakage — eliminating GDPR Article 9 cross-border transfer blockers.',
              },
            ].map((item) => (
              <Grid key={item.title} size={{ xs: 12, md: 6 }}>
                <Card className="slainte-surface-panel" sx={{ height: '100%', bgcolor: '#FFFFFF' }}>
                  <CardContent sx={{ p: 3.5 }}>
                    <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 1.25 }}>
                      {item.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#334155' }}>
                      {item.body}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Paper elevation={0} sx={{ mt: 5, p: 4, bgcolor: '#0F172A', color: '#FFFFFF', borderRadius: 3, border: '1px solid #38BDF8' }}>
            <Typography component="h2" variant="h2" sx={{ color: '#FFFFFF', mb: 1.5 }}>
              Due-Diligence Ready Today
            </Typography>
            <Typography variant="body1" sx={{ color: '#CBD5E1', mb: 3, maxWidth: 740 }}>
              Technical due diligence requires working code, not slideware. Our repository ships with 330+ automated security/clinical tests, reproducible Docker Compose appliance builds, OASIS SARIF v2.1.0 outputs, and live interactive workspaces for all 8 verticals and 11 agents.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
              <Button
                component={Link}
                href="/contact/"
                variant="contained"
                color="primary"
                endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                sx={{ border: '1px solid #7DD3FC' }}
              >
                Request Investor Data Room &amp; Live Demo
              </Button>
              <Button
                component={Link}
                href="/verticals/"
                variant="outlined"
                sx={{ color: '#FFFFFF', borderColor: '#94A3B8', '&:hover': { borderColor: '#FFFFFF' } }}
              >
                Review All 8 Verticals
              </Button>
            </Stack>
          </Paper>
        </Container>
      </Box>
    </Box>
  );
}
