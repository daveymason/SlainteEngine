'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  AppBar,
  Box,
  Button,
  Container,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import MenuRoundedIcon from '@mui/icons-material/MenuRounded';
import CloseRoundedIcon from '@mui/icons-material/CloseRounded';
import ShieldRoundedIcon from '@mui/icons-material/ShieldRounded';
import { INDUSTRY_VERTICALS } from '@/data/verticalsData';

const PRIMARY_NAV = [
  { label: 'Platform', href: '/platform/' },
  { label: 'Health-Tech Agents', href: '/health-tech-agents/' },
  { label: 'Verticals', href: '/verticals/' },
  { label: 'Security & NIS2', href: '/security-compliance/' },
  { label: 'Pricing', href: '/pricing/' },
  { label: 'Investors', href: '/investors/' },
  { label: 'Docs', href: '/docs/' },
];

export function SiteChrome({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100dvh' }}>
      <a href="#page-heading" className="skip-link visually-hidden">
        Skip to main content
      </a>

      <AppBar
        component="header"
        position="sticky"
        elevation={0}
        sx={{
          bgcolor: '#0F172A',
          color: '#FFFFFF',
          borderBottom: '1px solid #1E293B',
        }}
      >
        <Container maxWidth="lg">
          <Toolbar disableGutters sx={{ minHeight: { xs: 64, md: 70 }, justifyContent: 'space-between', gap: 2 }}>
            <Box
              component={Link}
              href="/"
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 1.25,
                color: '#FFFFFF',
                textDecoration: 'none',
                fontWeight: 800,
                fontSize: '1.08rem',
                letterSpacing: '-0.02em',
              }}
            >
              <Box
                sx={{
                  width: 34,
                  height: 34,
                  borderRadius: '8px',
                  bgcolor: '#1B6B8D',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid #38BDF8',
                }}
              >
                <ShieldRoundedIcon sx={{ fontSize: 20, color: '#FFFFFF' }} aria-hidden="true" />
              </Box>
              <span>
                SlainteTech <Box component="span" sx={{ color: '#7DD3FC', fontWeight: 600 }}>AI Security Labs</Box>
              </span>
            </Box>

            {/* Desktop Primary Navigation */}
            <Box
              component="nav"
              aria-label="Primary"
              sx={{ display: { xs: 'none', lg: 'flex' }, alignItems: 'center', gap: 0.5 }}
            >
              {PRIMARY_NAV.map((item) => (
                <Button
                  key={item.href}
                  component={Link}
                  href={item.href}
                  sx={{
                    color: '#E2E8F0',
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    px: 1.4,
                    '&:hover': { bgcolor: 'rgba(56, 189, 248, 0.14)', color: '#FFFFFF' },
                  }}
                >
                  {item.label}
                </Button>
              ))}
              <Button
                component={Link}
                href="/contact/"
                variant="contained"
                color="primary"
                sx={{ ml: 1, border: '1px solid #38BDF8' }}
              >
                Book Pilot / Data Room
              </Button>
            </Box>

            {/* Mobile & Tablet Drawer Trigger */}
            <Box sx={{ display: { xs: 'flex', lg: 'none' } }}>
              <IconButton
                onClick={() => setMobileOpen(true)}
                aria-label="Open navigation menu"
                aria-expanded={mobileOpen}
                sx={{ color: '#FFFFFF', border: '1px solid #334155', borderRadius: 2, minWidth: 44, minHeight: 44 }}
              >
                <MenuRoundedIcon aria-hidden="true" />
              </IconButton>
            </Box>
          </Toolbar>
        </Container>
      </AppBar>

      {/* Responsive Tablet & Smartphone Navigation Drawer */}
      <Drawer
        anchor="right"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        PaperProps={{
          sx: { width: 'min(320px, 86dvw)', height: '100svh', bgcolor: '#0F172A', color: '#FFFFFF', p: 2 },
        }}
      >
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
          <Typography component="p" variant="subtitle1" fontWeight={800}>
            SlainteTech Navigation
          </Typography>
          <IconButton
            onClick={() => setMobileOpen(false)}
            aria-label="Close navigation menu"
            sx={{ color: '#FFFFFF', minWidth: 44, minHeight: 44 }}
          >
            <CloseRoundedIcon aria-hidden="true" />
          </IconButton>
        </Stack>
        <Divider sx={{ borderColor: '#1E293B', mb: 1 }} />
        <Box component="nav" aria-label="Mobile Primary">
          <List disablePadding>
            {PRIMARY_NAV.map((item) => (
              <ListItem key={item.href} disablePadding>
                <ListItemButton
                  component={Link}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  sx={{ borderRadius: 1.5, minHeight: 48 }}
                >
                  <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: 700, color: '#F8FAFC' }} />
                </ListItemButton>
              </ListItem>
            ))}
            <ListItem disablePadding sx={{ mt: 1.5 }}>
              <Button
                fullWidth
                variant="contained"
                color="primary"
                component={Link}
                href="/contact/"
                onClick={() => setMobileOpen(false)}
              >
                Book Pilot / Data Room
              </Button>
            </ListItem>
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1 }}>
        {children}
      </Box>

      <Box
        component="footer"
        sx={{
          bgcolor: '#0F172A',
          color: '#E2E8F0',
          borderTop: '1px solid #1E293B',
          pt: 7,
          pb: 5,
          mt: 8,
        }}
      >
        <Container maxWidth="lg">
          <Box component="nav" aria-label="Footer">
            <Grid container spacing={4}>
              <Grid size={{ xs: 12, md: 4 }}>
                <Typography component="p" variant="h6" fontWeight={800} sx={{ color: '#FFFFFF', mb: 1 }}>
                  SlainteTech AI Security Labs
                </Typography>
                <Typography variant="body2" sx={{ color: '#CBD5E1', mb: 2, maxWidth: 340 }}>
                  Autonomous clinical, compliance, and cybersecurity agents bound by deterministic Python FastMCP guardrails on HL7 FHIR R4. Responsive across desktop, hospital tablets, ambulance ePCR, and mobile home care.
                </Typography>
                <Typography variant="caption" sx={{ color: '#94A3B8', fontFamily: 'monospace', display: 'block' }}>
                  WCAG 2.2 AA Verified • NIS2 &amp; EU AI Act Ready • Zero Hallucinated Clinical Math
                </Typography>
              </Grid>

              <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                <Typography component="p" variant="subtitle2" fontWeight={800} sx={{ color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.05em', mb: 1.5 }}>
                  Industry Verticals (&ldquo;For...&rdquo;)
                </Typography>
                <Stack component="ul" role="list" spacing={1} sx={{ listStyle: 'none', p: 0, m: 0 }}>
                  {INDUSTRY_VERTICALS.map((v) => (
                    <li key={v.slug}>
                      <Box
                        component={Link}
                        href={`/verticals/${v.slug}/`}
                        className="touch-nav-link"
                        sx={{ color: '#CBD5E1', textDecoration: 'none', fontSize: '0.9rem', '&:hover': { color: '#7DD3FC', textDecoration: 'underline' } }}
                      >
                        {v.forLabel} ({v.brand})
                      </Box>
                    </li>
                  ))}
                </Stack>
              </Grid>

              <Grid size={{ xs: 12, sm: 6, md: 4 }}>
                <Typography component="p" variant="subtitle2" fontWeight={800} sx={{ color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.05em', mb: 1.5 }}>
                  Platform, Agents &amp; Company
                </Typography>
                <Stack component="ul" role="list" spacing={1} sx={{ listStyle: 'none', p: 0, m: 0 }}>
                  {[
                    { label: 'All 11 Health-Tech Agents', href: '/health-tech-agents/' },
                    { label: 'Platform & FastMCP Architecture', href: '/platform/' },
                    { label: 'Security, GDPR Art. 9 & NIS2', href: '/security-compliance/' },
                    { label: 'Commercial Pricing (Land & Expand)', href: '/pricing/' },
                    { label: 'Investor Thesis & Data Room', href: '/investors/' },
                    { label: 'Developer & SMART-on-FHIR v2 Docs', href: '/docs/' },
                    { label: 'About SlainteTech', href: '/about/' },
                    { label: 'Contact & Hospital Pilot Booking', href: '/contact/' },
                    { label: 'GEO AI Manifest (/llms.txt)', href: '/llms.txt' },
                  ].map((item) => (
                    <li key={item.href}>
                      <Box
                        component={Link}
                        href={item.href}
                        className="touch-nav-link"
                        sx={{ color: '#CBD5E1', textDecoration: 'none', fontSize: '0.9rem', '&:hover': { color: '#7DD3FC', textDecoration: 'underline' } }}
                      >
                        {item.label}
                      </Box>
                    </li>
                  ))}
                </Stack>
              </Grid>
            </Grid>
          </Box>
          <Divider sx={{ borderColor: '#1E293B', my: 4 }} />
          <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" spacing={1}>
            <Typography variant="caption" sx={{ color: '#94A3B8' }}>
              © 2026 SlainteTech AI Security Labs. Sovereign Healthcare Cybersecurity &amp; Clinical Interoperability.
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8' }}>
              HL7® and FHIR® are registered trademarks of Health Level Seven International.
            </Typography>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
}
