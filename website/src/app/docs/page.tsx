import type { Metadata } from 'next';
import React from 'react';
import Link from 'next/link';
import { Box, Button, Container, Paper, Stack, Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import { CopyCodeBlock } from '@/components/CopyCodeBlock';

export const metadata: Metadata = {
  title: 'Developer, SMART-on-FHIR v2 & HL7v2 Docs | SlainteTech',
  description:
    'Technical integration documentation for SMART-on-FHIR v2 PKCE sidecar launch, HL7v2 pipe-hat ingestion, OIDC SSO, and FastMCP safety endpoints.',
};

const SMART_CONFIG_JSON = `GET /.well-known/smart-configuration HTTP/1.1
Host: slainte-appliance.internal

{
  "authorization_endpoint": "https://slainte-appliance.internal/smart/authorize",
  "token_endpoint": "https://slainte-appliance.internal/smart/token",
  "code_challenge_methods_supported": ["S256"],
  "grant_types_supported": ["authorization_code"],
  "scopes_supported": [
    "openid", "fhirUser", "launch", "launch/patient",
    "patient/*.read", "user/*.cruds"
  ]
}`;

const HL7V2_CURL = `curl -X POST http://127.0.0.1:8000/enterprise/hl7v2/ingest \\
  -H "Content-Type: text/plain" \\
  --data-binary $'MSH|^~\\\\&|PAS|HSE_HOSP|SLAINTE|R4|202611071200||ADT^A01|MSG001|P|2.5\\rPID|1||GMS992811^^^HSE_GMS||MURPHY^SIOBHAN||19680412|F\\rAL1|1|DA|91936005^Penicillin^SCT|SV|Anaphylaxis\\rOBX|1|NM|33914-3^eGFR^LN||28|mL/min/1.73m2'`;

export default function DocsPage() {
  return (
    <Box>
      <Box
        component="section"
        aria-labelledby="page-heading"
        sx={{ bgcolor: '#0F172A', color: '#FFFFFF', py: { xs: 6, md: 8 }, borderBottom: '2px solid #38BDF8' }}
      >
        <Container maxWidth="lg">
          <Typography variant="overline" sx={{ color: '#BAE6FD', fontWeight: 800, letterSpacing: '0.08em', display: 'block' }}>
            Hospital IT &amp; Interoperability Reference
          </Typography>
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            SMART-on-FHIR v2, HL7v2 Bridge &amp; FastMCP Integration
          </Typography>
          <Typography variant="body1" sx={{ color: '#CBD5E1', maxWidth: 760 }}>
            Integrate SlainteTech alongside any HL7 FHIR R4 server (Epic, Oracle Cerner, HAPI FHIR, Azure Health Data Services) or legacy HL7v2 v2.3–v2.5 hospital interface engine.
          </Typography>
        </Container>
      </Box>

      <Box component="section" aria-labelledby="integration-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Typography component="h2" variant="h2" id="integration-heading" sx={{ color: '#0F172A', mb: 3 }}>
            1. SMART-on-FHIR v2 Discovery &amp; S256 PKCE Launch
          </Typography>
          <Typography variant="body2" sx={{ color: '#334155', mb: 2.5 }}>
            SlainteTech exposes a native RFC 7636 S256 PKCE authorization flow and EHR launch receiver at <code>/.well-known/smart-configuration</code> and <code>/smart/launch</code>.
          </Typography>
          <CopyCodeBlock caption="SMART-on-FHIR v2 Discovery Endpoint" code={SMART_CONFIG_JSON} />

          <Typography component="h2" variant="h2" sx={{ color: '#0F172A', mt: 6, mb: 3 }}>
            2. Legacy Hospital HL7v2 Pipe-Hat Ingestion Bridge
          </Typography>
          <Typography variant="body2" sx={{ color: '#334155', mb: 2.5 }}>
            Translate legacy <code>ADT^A01</code>, <code>ORU^R01</code>, and <code>RDE^O11</code> messages directly into deduplicated HL7 FHIR R4 Patient, AllergyIntolerance, Condition, Observation, and MedicationRequest bundles.
          </Typography>
          <CopyCodeBlock caption="POST /enterprise/hl7v2/ingest (MSH / PID / AL1 / OBX)" code={HL7V2_CURL} />

          <Grid container spacing={3} sx={{ mt: 4 }}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Paper elevation={0} sx={{ p: 3, bgcolor: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: 2.5, height: '100%' }}>
                <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 1 }}>
                  Enterprise OIDC &amp; Granular Clinical RBAC
                </Typography>
                <Typography variant="body2" sx={{ color: '#334155' }}>
                  Connect Keycloak, Microsoft Entra ID, or Okta via <code>OIDC_DISCOVERY_URL</code> to map institutional claims straight into <code>consultant</code>, <code>gp</code>, <code>pharmacist</code>, <code>triage_nurse</code>, and <code>admin</code> roles.
                </Typography>
              </Paper>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <Paper elevation={0} sx={{ p: 3, bgcolor: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: 2.5, height: '100%' }}>
                <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mb: 1 }}>
                  GEO &amp; Machine-Readable Manifest
                </Typography>
                <Typography variant="body2" sx={{ color: '#334155', mb: 2 }}>
                  Inspect our structured <code>/llms.txt</code> manifest indexing all 11 <code>/health-tech-agents/</code> and 8 <code>/verticals/</code> endpoints.
                </Typography>
                <Stack direction="row" spacing={1.5}>
                  <Button component={Link} href="/llms.txt" variant="outlined" color="primary" size="small">
                    View /llms.txt
                  </Button>
                  <Button component={Link} href="/health-tech-agents/" variant="contained" color="primary" size="small">
                    Browse All 11 Agents
                  </Button>
                </Stack>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}
