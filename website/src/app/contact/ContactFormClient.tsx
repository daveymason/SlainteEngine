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
import EmailRoundedIcon from '@mui/icons-material/EmailRounded';
import ContentCopyRoundedIcon from '@mui/icons-material/ContentCopyRounded';
import { INDUSTRY_VERTICALS } from '@/data/verticalsData';

const TRACK_CONFIG = {
  pilot: {
    email: 'hello@slainte-tech.com',
    label: '30-Day Clinical Vertical or SMART-on-FHIR Sidecar Pilot',
  },
  ciso: {
    email: 'hello@slainte-tech.com',
    label: 'CISO / DPO Security, BOLA & NIS2 Compliance Review',
  },
  investor: {
    email: 'hello@slainte-tech.com',
    label: 'Institutional Investor Data Room & Live Demo',
  },
} as const;

type TrackKey = keyof typeof TRACK_CONFIG;

export function ContactFormClient() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [organization, setOrganization] = useState('');
  const [vertical, setVertical] = useState('emergency-departments');
  const [inquiryType, setInquiryType] = useState<TrackKey>('pilot');
  const [notes, setNotes] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [deliveryMode, setDeliveryMode] = useState<'endpoint' | 'mailto'>('mailto');
  const [mailtoUrl, setMailtoUrl] = useState('');
  const [summaryText, setSummaryText] = useState('');
  const [copied, setCopied] = useState(false);

  const selectedTrack = TRACK_CONFIG[inquiryType];

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitting(true);

    const selectedVertical = INDUSTRY_VERTICALS.find((v) => v.slug === vertical);
    const verticalLabel = selectedVertical ? `${selectedVertical.forLabel} (${selectedVertical.brand})` : vertical;
    const subject = `[SlainteTech Briefing] ${selectedTrack.label} — ${organization.trim() || 'Inquiry'}`;
    const bodyLines = [
      `Track: ${selectedTrack.label}`,
      `Primary Vertical: ${verticalLabel}`,
      `Name & Role: ${name.trim()}`,
      `Work Email: ${email.trim()}`,
      `Organization: ${organization.trim()}`,
      `Deployment Context: ${notes.trim() || 'Not specified'}`,
    ];
    const body = bodyLines.join('\n');
    const composedMailto = `mailto:${selectedTrack.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

    setSummaryText(`To: ${selectedTrack.email}\nSubject: ${subject}\n\n${body}`);
    setMailtoUrl(composedMailto);

    const endpoint = process.env.NEXT_PUBLIC_CONTACT_ENDPOINT;
    if (endpoint) {
      try {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
          body: JSON.stringify({
            name: name.trim(),
            email: email.trim(),
            organization: organization.trim(),
            inquiryType,
            inquiryLabel: selectedTrack.label,
            vertical,
            verticalLabel,
            notes: notes.trim(),
            recipient: selectedTrack.email,
          }),
        });
        if (res.ok) {
          setDeliveryMode('endpoint');
          setSubmitted(true);
          setSubmitting(false);
          return;
        }
      } catch {
        // Fall through cleanly to mailto launch if static webhook is unreachable
      }
    }

    setDeliveryMode('mailto');
    setSubmitted(true);
    setSubmitting(false);
    window.location.href = composedMailto;
  };

  const handleCopySummary = async () => {
    try {
      await navigator.clipboard.writeText(summaryText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      setCopied(false);
    }
  };

  return (
    <Paper elevation={0} sx={{ p: { xs: 3, md: 4 }, bgcolor: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: 3 }}>
      <Typography component="h2" variant="h2" sx={{ color: '#0F172A', mb: 1 }}>
        Book a Pilot, CISO Review, or Investor Walkthrough
      </Typography>
      <Typography variant="body2" sx={{ color: '#334155', mb: 3 }}>
        Select your clinical vertical or diligence track below to schedule a live 30-minute walkthrough of the 8-vertical platform and 16 autonomous agents.
      </Typography>

      {submitted ? (
        <Stack spacing={2}>
          <Alert severity="success" sx={{ fontWeight: 600 }}>
            {deliveryMode === 'endpoint' ? (
              <>
                Thank you — your briefing request has been submitted to{' '}
                <a href={`mailto:${selectedTrack.email}`} style={{ color: 'inherit', fontWeight: 800 }}>
                  {selectedTrack.email}
                </a>
                .
              </>
            ) : (
              <>
                Thank you — your briefing request is ready to send to{' '}
                <a href={mailtoUrl} style={{ color: 'inherit', fontWeight: 800 }}>
                  {selectedTrack.email}
                </a>
                . If your email app did not open automatically, click the button or copy the summary below.
              </>
            )}
          </Alert>

          <Box
            component="pre"
            sx={{
              m: 0,
              p: 2,
              borderRadius: 2,
              bgcolor: '#F8FAFC',
              border: '1px solid #CBD5E1',
              color: '#0F172A',
              fontFamily: 'monospace',
              fontSize: '0.82rem',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {summaryText}
          </Box>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
            <Button
              component="a"
              href={mailtoUrl}
              variant="contained"
              color="primary"
              startIcon={<EmailRoundedIcon aria-hidden="true" />}
            >
              Open in Email Client ({selectedTrack.email})
            </Button>
            <Button
              type="button"
              variant="outlined"
              color="primary"
              startIcon={<ContentCopyRoundedIcon aria-hidden="true" />}
              onClick={handleCopySummary}
            >
              {copied ? 'Copied Summary' : 'Copy Request Summary'}
            </Button>
            <Button
              type="button"
              variant="text"
              onClick={() => setSubmitted(false)}
            >
              Edit Request
            </Button>
          </Stack>
        </Stack>
      ) : (
        <Box component="form" onSubmit={handleSubmit}>
          <Stack spacing={2.5}>
            <TextField
              required
              id="contact-name"
              name="name"
              label="Full Name & Clinical / Executive Role"
              autoComplete="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
            />
            <TextField
              required
              id="contact-email"
              name="email"
              type="email"
              label="Work or Institutional Email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              fullWidth
            />
            <TextField
              required
              id="contact-org"
              name="organization"
              label="Hospital, Clinic, Ambulance Service, or Fund"
              autoComplete="organization"
              value={organization}
              onChange={(e) => setOrganization(e.target.value)}
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel id="inquiry-track-label">Briefing Track</InputLabel>
              <Select
                labelId="inquiry-track-label"
                id="inquiry-track"
                value={inquiryType}
                label="Briefing Track"
                onChange={(e) => setInquiryType(e.target.value as TrackKey)}
              >
                <MenuItem value="pilot">{TRACK_CONFIG.pilot.label}</MenuItem>
                <MenuItem value="ciso">{TRACK_CONFIG.ciso.label}</MenuItem>
                <MenuItem value="investor">{TRACK_CONFIG.investor.label}</MenuItem>
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
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              fullWidth
            />

            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              disabled={submitting}
              endIcon={<SendRoundedIcon aria-hidden="true" />}
            >
              {submitting ? 'Sending Briefing Request...' : 'Request Live Briefing'}
            </Button>
          </Stack>
        </Box>
      )}
    </Paper>
  );
}
