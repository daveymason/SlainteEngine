'use client';

import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import SendRoundedIcon from '@mui/icons-material/SendRounded';
import { INDUSTRY_VERTICALS } from '@/data/verticalsData';

export function ContactFormClient() {
  const [submitted, setSubmitted] = useState(false);
  const [vertical, setVertical] = useState('emergency-departments');
  const [inquiryType, setInquiryType] = useState('pilot');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <Paper elevation={0} sx={{ p: { xs: 3, md: 4 }, bgcolor: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: 3 }}>
      <Typography component="h2" variant="h2" sx={{ color: '#0F172A', mb: 1 }}>
        Book a Pilot, CISO Review, or Investor Walkthrough
      </Typography>
      <Typography variant="body2" sx={{ color: '#334155', mb: 3 }}>
        Select your clinical vertical or diligence track below to schedule a live 30-minute walkthrough of the 8-vertical platform and 11 autonomous agents.
      </Typography>

      {submitted ? (
        <Alert severity="success" sx={{ fontWeight: 600 }}>
          Thank you — your briefing request has been prepared. For immediate engineering &amp; investor access, email{' '}
          <a href="mailto:pilots@slaintetech.ie" style={{ color: 'inherit', fontWeight: 800 }}>
            pilots@slaintetech.ie
          </a>
          .
        </Alert>
      ) : (
        <Box component="form" onSubmit={handleSubmit}>
          <Stack spacing={2.5}>
            <TextField
              required
              id="contact-name"
              name="name"
              label="Full Name & Clinical / Executive Role"
              autoComplete="name"
              fullWidth
            />
            <TextField
              required
              id="contact-email"
              name="email"
              type="email"
              label="Work or Institutional Email"
              autoComplete="email"
              fullWidth
            />
            <TextField
              required
              id="contact-org"
              name="organization"
              label="Hospital, Clinic, Ambulance Service, or Fund"
              autoComplete="organization"
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel id="inquiry-track-label">Briefing Track</InputLabel>
              <Select
                labelId="inquiry-track-label"
                id="inquiry-track"
                value={inquiryType}
                label="Briefing Track"
                onChange={(e) => setInquiryType(e.target.value)}
              >
                <MenuItem value="pilot">30-Day Clinical Vertical or SMART-on-FHIR Sidecar Pilot</MenuItem>
                <MenuItem value="ciso">CISO / DPO Security, BOLA &amp; NIS2 Compliance Review</MenuItem>
                <MenuItem value="investor">Institutional Investor Data Room &amp; Live Demo</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="primary-vertical-label">Primary Vertical of Interest</InputLabel>
              <Select
                labelId="primary-vertical-label"
                id="primary-vertical"
                value={vertical}
                label="Primary Vertical of Interest"
                onChange={(e) => setVertical(e.target.value)}
              >
                {INDUSTRY_VERTICALS.map((v) => (
                  <MenuItem key={v.slug} value={v.slug}>
                    {v.forLabel} ({v.brand})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              id="contact-notes"
              name="notes"
              label="Deployment Context (e.g., Epic/Cerner Sidecar, Standalone Clinic, Mobile Nursing, Air-Gapped)"
              multiline
              minRows={3}
              fullWidth
            />

            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              endIcon={<SendRoundedIcon aria-hidden="true" />}
            >
              Request Live Briefing
            </Button>
          </Stack>
        </Box>
      )}
    </Paper>
  );
}
