import type { Metadata } from 'next';
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
  Stack,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import CheckCircleRoundedIcon from '@mui/icons-material/CheckCircleRounded';
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';

export const metadata: Metadata = {
  title: 'Commercial Pricing & Licensing | SlainteTech AI Security Labs',
  description:
    'Transparent Land-and-Expand licensing for hospital CISOs, GP/Dental/Pharmacy clinics, ambulance fleets, and sovereign air-gapped appliances.',
};

const TIERS = [
  {
    name: 'Tier 1 • Clinic & Practice Vertical',
    badge: 'GP, Dental, Psych & Pharmacy',
    price: '€199 – €499',
    unit: 'per clinician / site / month',
    summary:
      'Turnkey sovereign clinical vertical for independent practices, DSOs, community nursing teams, and pharmacies.',
    features: [
      'Choice of Vertical (SlainteGP, SlainteDent, SlaintePsych, SlaintePharm)',
      'Ambient Clinical Voice Scribe (SOAP + pre-screened FHIR draft orders)',
      '3-Tier SlainteRx-Guard (Allergy, ISMP High-Alert DDI & LOINC eGFR)',
      'Responsive smartphone & tablet home-visit / chairside UX',
      'HSE PCRS monthly GMS batch CSV export & GDPR Art. 9 PII redaction',
    ],
  },
  {
    name: 'Tier 2 • Hospital Security & Coding Sidecar',
    badge: 'Recommended Enterprise Land',
    price: '€48,000 – €95,000',
    unit: 'annual site license',
    summary:
      'Zero-disruption 15-minute SMART-on-FHIR v2 sidecar alongside Epic, Cerner, or MEDITECH — no EHR rip-and-replace.',
    features: [
      'SlainteShield Squad (BOLA Red-Team, FHIR Conformance SARIF, CVE Audit)',
      'SlainteRev-Coding Autonomous HIPE / ICD-10-AM DRG Uplift Scanner',
      'SlainteGov-Audit Append-Only AI Ledger & Printable CISO Certificates',
      'Enterprise OIDC SSO (Keycloak / Entra ID / Okta) + HMAC SIEM Webhooks',
      'Typical payback < 90 days from recovered uncoded DRG complexity alone',
    ],
    highlighted: true,
  },
  {
    name: 'Tier 3 • Sovereign Air-Gapped Appliance',
    badge: 'Acute Trusts, EMS, Defence & Space',
    price: 'Custom Enterprise',
    unit: 'dedicated VPC or air-gapped hardware',
    summary:
      'Full 8-vertical, 11-agent sovereign deployment with local 3B Ollama models, HL7v2 bridge, and zero external network dependency.',
    features: [
      'All 8 Clinical Verticals (incl. Emergency Dept, Ambulance ePCR & Aerospace)',
      'All 11 Autonomous Health-Tech Agents + FastMCP :8081 + SlainteFHIR :8082',
      'Native HL7v2 Pipe-Hat (ADT, ORU, RDE) Legacy PAS/LIS Hospital Bridge',
      '100% Air-Gapped Local 3B Inference (0 bytes transmitted off-premise)',
      'Dedicated clinical safety engineering (DCB0129/0160) onboarding',
    ],
  },
];

export default function PricingPage() {
  return (
    <Box>
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{
          bgcolor: '#0F172A',
          backgroundImage: 'linear-gradient(135deg, #0F172A 0%, #134E68 100%)',
          color: '#FFFFFF',
          py: { xs: 6, md: 8 },
          borderBottom: '2px solid #38BDF8',
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="overline" sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
            Frictionless Procurement &amp; Immediate CFO Payback
          </Typography>
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            Land With a 15-Minute Sidecar. Expand Across Every Vertical.
          </Typography>
          <Typography variant="body1" sx={{ color: '#E2E8F0', maxWidth: 740 }}>
            Hospitals do not need a 3-year EHR replacement to adopt safe autonomous AI. Start with read-only NIS2 BOLA verification and HIPE DRG revenue recovery, or launch full clinical verticals immediately.
          </Typography>
        </Container>
      </Box>

      <Box component="section" aria-labelledby="tiers-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Typography component="h2" variant="h2" id="tiers-heading" sx={{ color: '#0F172A', mb: 4 }}>
            Commercial Licensing Tiers
          </Typography>

          <Grid container spacing={3} alignItems="stretch">
            {TIERS.map((tier) => (
              <Grid key={tier.name} size={{ xs: 12, md: 4 }}>
                <Card
                  className="slainte-interactive-card"
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    bgcolor: '#FFFFFF',
                    border: tier.highlighted ? '2px solid #1B6B8D' : '1px solid #CBD5E1',
                  }}
                >
                  <CardContent sx={{ p: 3.5 }}>
                    <Chip
                      label={tier.badge}
                      color={tier.highlighted ? 'primary' : 'default'}
                      size="small"
                      sx={{ mb: 2 }}
                    />
                    <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 1 }}>
                      {tier.name}
                    </Typography>
                    <Typography sx={{ fontSize: '1.85rem', fontWeight: 800, color: '#134E68' }}>
                      {tier.price}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#334155', display: 'block', mb: 2, fontWeight: 700 }}>
                      {tier.unit}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#334155', mb: 2.5 }}>
                      {tier.summary}
                    </Typography>

                    <Stack component="ul" role="list" spacing={1.25} sx={{ listStyle: 'none', p: 0, m: 0 }}>
                      {tier.features.map((feat) => (
                        <Stack component="li" key={feat} direction="row" spacing={1} alignItems="flex-start">
                          <CheckCircleRoundedIcon sx={{ color: '#15803D', fontSize: 19, mt: 0.25, flexShrink: 0 }} aria-hidden="true" />
                          <Typography variant="body2" sx={{ color: '#0F172A', fontSize: '0.88rem' }}>
                            {feat}
                          </Typography>
                        </Stack>
                      ))}
                    </Stack>
                  </CardContent>

                  <CardActions sx={{ px: 3.5, pb: 3.5, pt: 1 }}>
                    <Button
                      component={Link}
                      href="/contact/"
                      variant={tier.highlighted ? 'contained' : 'outlined'}
                      color="primary"
                      fullWidth
                      endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
                    >
                      Request Pilot Proposal
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}
