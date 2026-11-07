'use client';

import { createTheme } from '@mui/material/styles';

/**
 * SlainteTech Clinical & Security Design System Theme (MUI v6).
 * Derived directly from SlainteDash (--tropical-primary #2E86AB / darkened #1B6B8D for >=5.7:1 WCAG AA contrast on white,
 * --tropical-dark #1E293B / #0F172A, --tropical-success #15803D, --tropical-danger #B91C1C).
 */
export const slainteTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1B6B8D',       // 5.91:1 contrast against #FFFFFF (WCAG AA Pass)
      dark: '#134E68',       // 8.85:1 contrast against #FFFFFF (WCAG AAA Pass)
      light: '#E0F2FE',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#0F172A',       // 17.8:1 contrast against #FFFFFF
      dark: '#020617',
      light: '#1E293B',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#15803D',       // 5.13:1 contrast against #FFFFFF
      light: '#DCFCE7',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#B45309',       // 5.02:1 contrast against #FFFFFF
      light: '#FEF3C7',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#B91C1C',       // 6.47:1 contrast against #FFFFFF
      light: '#FEE2E2',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#F3F6F9',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#0F172A',    // 17.8:1 on white
      secondary: '#334155',  // 10.3:1 on white
    },
    divider: '#CBD5E1',
  },
  typography: {
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    h1: {
      fontSize: 'clamp(1.95rem, 1.35rem + 2.4vw, 2.85rem)',
      fontWeight: 800,
      letterSpacing: '-0.025em',
      lineHeight: 1.15,
    },
    h2: {
      fontSize: 'clamp(1.45rem, 1.15rem + 1.2vw, 2.05rem)',
      fontWeight: 800,
      letterSpacing: '-0.02em',
      lineHeight: 1.22,
    },
    h3: {
      fontSize: 'clamp(1.12rem, 1rem + 0.5vw, 1.32rem)',
      fontWeight: 700,
      letterSpacing: '-0.01em',
      lineHeight: 1.3,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.65,
    },
    body2: {
      fontSize: '0.925rem',
      lineHeight: 1.6,
    },
    button: {
      textTransform: 'none',
      fontWeight: 700,
      letterSpacing: '0.01em',
    },
  },
  shape: {
    borderRadius: 10,
  },
  components: {
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          minHeight: 44,
          paddingInline: '1.15rem',
          borderRadius: 8,
          transition: 'transform 160ms cubic-bezier(0.22, 1, 0.36, 1), background-color 160ms ease, box-shadow 160ms ease',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 12px rgba(15, 23, 42, 0.12)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
          '&:focus-visible': {
            outline: '3px solid #1B6B8D',
            outlineOffset: '3px',
          },
          '@media (prefers-reduced-motion: reduce)': {
            transition: 'none',
            '&:hover': {
              transform: 'none',
            },
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          border: '1px solid #CBD5E1',
          boxShadow: '0 1px 3px rgba(15, 23, 42, 0.04)',
          transition: 'transform 180ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 180ms ease, border-color 180ms ease',
          '@media (prefers-reduced-motion: reduce)': {
            transition: 'none',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 700,
          borderRadius: 6,
        },
      },
    },
  },
});
