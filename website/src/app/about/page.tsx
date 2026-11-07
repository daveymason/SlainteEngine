import type { Metadata } from 'next';
import React from 'react';
import Link from 'next/link';
import { Box, Button, Card, CardContent, Container, Stack, Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';

export const metadata: Metadata = {
  title: 'About SlainteTech AI Security Labs | Sovereign Digital Health',
  description:
    'SlainteTech AI Security Labs builds deterministic clinical safety, HL7 FHIR R4 interoperability, and autonomous healthcare cybersecurity agents in Ireland.',
};

export default function AboutPage() {
  return (
    <Box>
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{ bgcolor: '#0F172A', color: '#FFFFFF', py: { xs: 6, md: 8 }, borderBottom: '2px solid #38BDF8' }}
      >
        <Container maxWidth="lg">
          <Typography variant="overline" sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
            Mission &amp; Engineering Philosophy
          </Typography>
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            Making Autonomous Clinical AI Provably Safe, Auditable &amp; Sovereign
          </Typography>
          <Typography variant="body1" sx={{ color: '#E2E8F0', maxWidth: 740 }}>
            Born from Irish healthcare interoperability and offensive API security research, SlainteTech AI Security Labs was founded on a simple rule: no language model should ever guess a vital-sign deterioration score, invent a drug interaction result, or silently leak special-category patient records.
          </Typography>
        </Container>
      </Box>

      <Box component="section" aria-labelledby="principles-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Typography component="h2" variant="h2" id="principles-heading" sx={{ color: '#0F172A', mb: 4 }}>
            Our Three Non-Negotiable Engineering Rules
          </Typography>

          <Grid container spacing={3}>
            {[
              {
                title: 'Deterministic Guardrails Over Probabilistic Hope',
                text: 'Every physiological score (RCP NEWS2, Manchester Triage) and pharmacology check (Allergy cross-reactivity, ISMP DDI, LOINC eGFR) is executed by deterministic Python FastMCP code covered by automated regression tests.',
              },
              {
                title: 'Continuous Offensive Security Inside the Clinic',
                text: 'Healthcare APIs are prime ransomware and BOLA targets. Our SlainteShield squad continuously verifies patient compartment isolation, dependency pins, and Subresource Integrity hashes.',
              },
              {
                title: 'Built for Real Frontline Conditions',
                text: 'Whether used by an Emergency Consultant at a workstation, a Care-at-Home Nurse on a phone, a Paramedic on a rugged tablet, or a Crew Medical Officer in an offline habitat, the UI stays fast, accessible (WCAG 2.2 AA), and calm.',
              },
            ].map((p) => (
              <Grid key={p.title} size={{ xs: 12, md: 4 }}>
                <Card className="slainte-surface-panel" sx={{ height: '100%', bgcolor: '#FFFFFF' }}>
                  <CardContent sx={{ p: 3.5 }}>
                    <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 1.25 }}>
                      {p.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#334155' }}>
                      {p.text}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ mt: 5 }}>
            <Button
              component={Link}
              href="/contact/"
              variant="contained"
              color="primary"
              endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
            >
              Get in Touch With Engineering
            </Button>
            <Button component={Link} href="/verticals/" variant="outlined" color="primary">
              Explore Our 8 Verticals
            </Button>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
}
