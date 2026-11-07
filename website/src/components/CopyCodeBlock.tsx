'use client';

import React, { useState } from 'react';
import { Box, Button, Stack, Typography } from '@mui/material';
import ContentCopyRoundedIcon from '@mui/icons-material/ContentCopyRounded';
import DoneRoundedIcon from '@mui/icons-material/DoneRounded';

export function CopyCodeBlock({
  caption,
  code,
}: {
  caption: string;
  code: string;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <Box
      component="figure"
      sx={{
        m: 0,
        borderRadius: 2.5,
        overflow: 'hidden',
        border: '1px solid #334155',
        bgcolor: '#0F172A',
      }}
    >
      <Stack
        component="figcaption"
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        sx={{
          px: 2,
          py: 1,
          bgcolor: '#1E293B',
          borderBottom: '1px solid #334155',
        }}
      >
        <Typography variant="caption" sx={{ color: '#E2E8F0', fontFamily: 'monospace', fontWeight: 700 }}>
          {caption}
        </Typography>
        <Button
          size="small"
          onClick={handleCopy}
          startIcon={
            copied ? (
              <DoneRoundedIcon aria-hidden="true" sx={{ fontSize: 16 }} />
            ) : (
              <ContentCopyRoundedIcon aria-hidden="true" sx={{ fontSize: 16 }} />
            )
          }
          sx={{
            minHeight: 36,
            px: 1.5,
            color: '#FFFFFF',
            bgcolor: copied ? '#15803D' : '#334155',
            '&:hover': { bgcolor: copied ? '#15803D' : '#475569' },
          }}
        >
          {copied ? 'Copied' : 'Copy'}
        </Button>
      </Stack>
      <Box
        component="pre"
        tabIndex={0}
        sx={{
          m: 0,
          p: 2.5,
          overflowX: 'auto',
          color: '#F8FAFC',
          fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
          fontSize: '0.85rem',
          lineHeight: 1.6,
        }}
      >
        <code>{code}</code>
      </Box>
    </Box>
  );
}
