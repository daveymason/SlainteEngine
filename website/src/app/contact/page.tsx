import type { Metadata } from 'next';
import React from 'react';
import { Box, Container, Paper, Stack, Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import { ContactFormClient } from './ContactFormClient';

export const metadata: Metadata = {
  title: 'Contact, Hospital Pilots & Investor Data Room | SlainteTech',
  description:
    'Book a 30-day hospital SMART-on-FHIR pilot, clinic vertical deployment, or institutional investor data room walkthrough.',
};

export default function ContactPage() {
  return (
    <Box>
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{ bgcolor: '#0F172A', color: '#FFFFFF', py: { xs: 6, md: 8 }, borderBottom: '2px solid #38BDF8' }}
      >
        <Container maxWidth="lg">
          <Typography variant="overline" sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
            Pilots • CISO Security Audits • Investor Data Room
          </Typography>
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            Start With a Zero-Disruption Pilot
          </Typography>
          <Typography variant="body1" sx={{ color: '#E2E8F0', maxWidth: 720 }}>
            Deploy SlainteTech inside your staging or clinical environment in under 15 minutes via Docker Compose or SMART-on-FHIR v2.
          </Typography>
        </Container>
      </Box>

      <Box component="section" aria-label="Contact and pilot booking" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid size={{ xs: 12, md: 7 }}>
              <ContactFormClient />
            </Grid>
            <Grid size={{ xs: 12, md: 5 }}>
              <Stack spacing={2.5}>
                <Paper elevation={0} sx={{ p: 3, bgcolor: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: 2.5 }}>
                  <Typography component="h2" variant="h3" sx={{ color: '#0F172A', mb: 1 }}>
                    What Happens in a 30-Day Hospital Pilot?
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#334155' }}>
                    Week 1: Deploy read-only SMART-on-FHIR v2 or synthetic/staging HL7v2 mirror. Week 2: Run SlainteShield BOLA + FHIR SARIF conformance + SlainteRev-Coding HIPE gap audit. Week 3–4: Deliver executive CISO Compliance Certificate and quantified DRG uplift report.
                  </Typography>
                </Paper>
                <Paper elevation={0} sx={{ p: 3, bgcolor: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: 2.5 }}>
                  <Typography component="h2" variant="h3" sx={{ color: '#0F172A', mb: 1 }}>
                    Direct Engineering &amp; Investor Contact
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#334155', mb: 1 }}>
                    Clinical Pilots: <strong>pilots@slaintetech.ie</strong>
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#334155', mb: 1 }}>
                    CISO &amp; Security Disclosure: <strong>security@slaintetech.ie</strong>
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#334155' }}>
                    Investor Relations: <strong>investors@slaintetech.ie</strong>
                  </Typography>
                </Paper>
              </Stack>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}
