import type { Metadata } from 'next';
import React from 'react';
import Link from 'next/link';
import {
  Box,
  Button,
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
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';

export const metadata: Metadata = {
  title: 'Security, EU NIS2, EU AI Act & GDPR Art. 9 Compliance | SlainteTech',
  description:
    'Provable technical controls for EU NIS2, EU AI Act High-Risk Healthcare AI, GDPR Article 9 special-category PHI, OWASP API1:2023 BOLA, and HIQA standards.',
};

const COMPLIANCE_ROWS = [
  {
    framework: 'EU NIS2 Directive (2022/2555)',
    requirement: 'Art. 21 Cybersecurity Risk-Management, Supply-Chain & Incident Reporting',
    control: 'Continuous BOLA compartment red-teaming (SlainteShield-BOLA), exact == dependency pinning + SRI sha384 checks (SlainteShield-CVE), and HMAC-SHA256 SIEM webhooks.',
  },
  {
    framework: 'EU AI Act (High-Risk Annex III)',
    requirement: 'Art. 12 Record-Keeping, Art. 14 Human Oversight & Art. 15 Accuracy/Robustness',
    control: 'Append-only ai_exchange SQLite ledger with BEFORE UPDATE/DELETE abort triggers, mandatory clinician co-sign on Ambient Scribe drafts, and deterministic Python NEWS2/Rx-Guard math.',
  },
  {
    framework: 'EU GDPR Article 9 & 32',
    requirement: 'Special-Category Health Data Minimisation, Pseudonymisation & Vital Interests',
    control: 'Pre-inference PII stripping (names, telecom, addresses, GMS IDs), salted SHA-256 subject digests in logs, BAA cloud gate, and 60-minute Break-the-Glass emergency grants.',
  },
  {
    framework: 'OWASP API Security Top 10 (2023)',
    requirement: 'API1:2023 Broken Object Level Authorization & API2:2023 Broken Authentication',
    control: 'CompartmentDefinition/Patient dual-phase reflection probing, PBKDF2-HMAC-SHA256 / OIDC IdP auth, PKCE S256 SMART-on-FHIR v2, and SQLite multi-worker 5-strike lockouts.',
  },
  {
    framework: 'HIQA & Clinical Risk (DCB0129/0160)',
    requirement: 'Terminology Interoperability, Clinical Attribution & Medication Safety',
    control: 'SNOMED-CT, LOINC, UCUM & Irish GMS OID conformance with OASIS SARIF v2.1.0 export, IMC/PSI SHA-256 FHIR Provenance sign-off, and 3-Tier pharmacology interception.',
  },
];

export default function SecurityCompliancePage() {
  return (
    <Box>
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{
          bgcolor: '#0F172A',
          backgroundImage: 'linear-gradient(135deg, #0F172A 0%, #3B0D1E 100%)',
          color: '#FFFFFF',
          py: { xs: 6, md: 8 },
          borderBottom: '2px solid #EF4444',
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="overline" sx={{ color: '#FCA5A5', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
            Provable Engineering Controls — Not Paper Promises
          </Typography>
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            NIS2, EU AI Act, GDPR Art. 9 &amp; OWASP API Security
          </Typography>
          <Typography variant="body1" sx={{ color: '#E2E8F0', maxWidth: 760 }}>
            Every regulatory claim made by SlainteTech maps directly to an executable agent, database kernel trigger, or automated CI security gate inside our repository.
          </Typography>
        </Container>
      </Box>

      <Box component="section" aria-labelledby="matrix-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Typography component="h2" variant="h2" id="matrix-heading" sx={{ color: '#0F172A', mb: 3 }}>
            Regulatory-to-Code Verification Matrix
          </Typography>

          <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #CBD5E1', borderRadius: 2, bgcolor: '#FFFFFF' }}>
            <Table aria-label="Regulatory compliance verification matrix">
              <caption style={{ textAlign: 'left', padding: '12px 16px', color: '#334155', fontSize: '0.875rem' }}>
                Mapping between statutory European healthcare security regulations and live SlainteTech technical controls.
              </caption>
              <TableHead sx={{ bgcolor: '#F1F5F9' }}>
                <TableRow>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>Regulation / Standard</TableCell>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>Statutory Requirement</TableCell>
                  <TableCell scope="col" sx={{ fontWeight: 800, color: '#0F172A' }}>Live SlainteTech Technical Control</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {COMPLIANCE_ROWS.map((row) => (
                  <TableRow key={row.framework} hover>
                    <TableCell component="th" scope="row" sx={{ fontWeight: 800, color: '#0F172A', width: '24%' }}>
                      {row.framework}
                    </TableCell>
                    <TableCell sx={{ color: '#334155', width: '30%' }}>{row.requirement}</TableCell>
                    <TableCell sx={{ color: '#0F172A' }}>{row.control}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Paper elevation={0} sx={{ mt: 5, p: 3.5, bgcolor: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: 2.5 }}>
            <Typography component="h2" variant="h2" sx={{ color: '#0F172A', mb: 1 }}>
              Printable CISO Compliance Certificates &amp; SARIF Exports
            </Typography>
            <Typography variant="body2" sx={{ color: '#334155', mb: 2.5 }}>
              Hospital DPOs and CISOs can generate timestamped SHA-256 Compliance Attestation Certificates and OASIS SARIF v2.1.0 artefacts directly from the Governance Hub for HIQA, NIS2, and insurer audits.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
              <Button
                component={Link}
                href="/health-tech-agents/bola-authorization-red-team-agent/"
                variant="contained"
                color="primary"
                endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
              >
                Inspect BOLA Red-Team Agent
              </Button>
              <Button
                component={Link}
                href="/health-tech-agents/immutable-clinical-ai-audit-agent/"
                variant="outlined"
                color="primary"
              >
                Inspect Immutable Audit Agent
              </Button>
            </Stack>
          </Paper>
        </Container>
      </Box>
    </Box>
  );
}
