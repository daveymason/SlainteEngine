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
import { CopyCodeBlock } from '@/components/CopyCodeBlock';

export const metadata: Metadata = {
  title: 'Platform & FastMCP Architecture | SlainteTech AI Security Labs',
  description:
    'Explore the 4-layer SlainteTech architecture: Responsive Clinical Verticals, 16 Autonomous Agents, Python FastMCP Safety Guardrails, and Sovereign HL7 FHIR R4.',
};

const DOCKER_SNIPPET = `# Air-gapped or on-premise hospital deployment (under 5 minutes)
git clone https://github.com/daveymason/slainte-engine.git
cd slainte-engine
cp .env.example .env
docker compose up -d --build

# Services exposed on isolated internal network:
# - Clinical Verticals & Agents UI -> http://127.0.0.1:8000
# - FastMCP Safety Tool Server     -> http://127.0.0.1:8081
# - SlainteFHIR R4 Micro-Server    -> http://127.0.0.1:8082/fhir/r4`;

export default function PlatformPage() {
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
            Deterministic Clinical &amp; Security Architecture
          </Typography>
          <Typography
            component="h1"
            variant="h1"
            id="page-heading"
            tabIndex={-1}
            sx={{ color: '#FFFFFF', mb: 2, outline: 'none' }}
          >
            Why SlainteTech Separates Language Models From Clinical Math
          </Typography>
          <Typography variant="body1" sx={{ color: '#E2E8F0', maxWidth: 760 }}>
            Generic healthcare AI wrappers send raw patient charts to external LLMs and hope probabilistic weights calculate triage scores and drug interactions accurately. SlainteTech enforces a strict architectural boundary: LLMs draft and summarise; deterministic Python FastMCP tools compute scores, block unsafe drugs, and sign audit records.
          </Typography>
        </Container>
      </Box>

      <Box component="section" aria-labelledby="layers-heading" sx={{ py: { xs: 6, md: 8 } }}>
        <Container maxWidth="lg">
          <Typography component="h2" variant="h2" id="layers-heading" sx={{ color: '#0F172A', mb: 4 }}>
            Four Sovereign Architectural Layers
          </Typography>

          <Grid container spacing={3}>
            {[
              {
                step: 'LAYER 01',
                title: 'Responsive Multi-Vertical Clinical UI & SMART-on-FHIR v2',
                desc: 'Eight role-based verticals (ED, GP & Community Nursing, Psychiatry, Dentistry, Pharmacy, Ambulance ePCR, Sports Medicine, Aerospace) served with sub-50ms HTMX updates, coarse-pointer 44px touch controls, and PKCE SMART-on-FHIR v2 launch.',
              },
              {
                step: 'LAYER 02',
                title: '16 Autonomous Health-Tech Agents',
                desc: 'Three coordinated squads — SlainteShield Security (3), SlainteGov Governance & Coding (5), and SlainteClinical Care (8).',
              },
              {
                step: 'LAYER 03',
                title: 'Python FastMCP Deterministic Safety Server (:8081)',
                desc: 'Executes Royal College of Physicians NEWS2, Manchester Triage Cat 1–5, 3-Tier pharmacology (cross-reactivity, ISMP high-alert DDI, LOINC eGFR/Potassium), and RFC 1918 red-team locks with 0% LLM arithmetic.',
              },
              {
                step: 'LAYER 04',
                title: 'SlainteFHIR R4 Store & Append-Only Audit Kernel (:8082)',
                desc: 'Lightweight HL7 FHIR R4 micro-EHR and HL7v2 pipe-hat bridge backed by SQLite BEFORE UPDATE/DELETE tamper-rejection triggers, SHA-256 FHIR Provenance, and HMAC-SHA256 SIEM webhooks.',
              },
            ].map((item) => (
              <Grid key={item.step} size={{ xs: 12, md: 6 }}>
                <Card className="slainte-surface-panel" sx={{ height: '100%', bgcolor: '#FFFFFF' }}>
                  <CardContent sx={{ p: 3.5 }}>
                    <Typography variant="caption" sx={{ fontFamily: 'monospace', fontWeight: 800, color: '#134E68' }}>
                      {item.step}
                    </Typography>
                    <Typography component="h3" variant="h3" sx={{ color: '#0F172A', mt: 0.5, mb: 1.25 }}>
                      {item.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#334155' }}>
                      {item.desc}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Paper elevation={0} sx={{ mt: 5, p: { xs: 3, md: 4 }, bgcolor: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: 3 }}>
            <Typography component="h2" variant="h2" sx={{ color: '#0F172A', mb: 1.5 }}>
              5-Minute Sovereign Appliance Deployment
            </Typography>
            <Typography variant="body2" sx={{ color: '#334155', mb: 3 }}>
              Run the entire stack inside a hospital VPC, private clinic server, or air-gapped field workstation using Docker Compose — or attach solely as a read-only SMART-on-FHIR v2 sidecar to Epic, Oracle Cerner, MEDITECH, or HAPI FHIR.
            </Typography>
            <CopyCodeBlock caption="docker-compose sovereign appliance quickstart" code={DOCKER_SNIPPET} />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ mt: 3 }}>
              <Button
                component={Link}
                href="/docs/"
                variant="contained"
                color="primary"
                endIcon={<ArrowForwardRoundedIcon aria-hidden="true" />}
              >
                Read Developer &amp; API Documentation
              </Button>
              <Button component={Link} href="/health-tech-agents/" variant="outlined" color="primary">
                Inspect All 16 Agents
              </Button>
            </Stack>
          </Paper>
        </Container>
      </Box>
    </Box>
  );
}
