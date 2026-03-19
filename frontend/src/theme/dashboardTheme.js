/**
 * Coruja Monitor — Dashboard Theme Tokens
 * Single source of truth for all design decisions.
 * Extracted from Dashboard.css + design-system.css
 */

export const colors = {
  // Backgrounds
  bgBase:     '#0B0F14',
  bgSurface:  '#111827',
  bgElevated: '#1a2235',
  bgOverlay:  '#1e2a3a',

  // Borders
  borderSubtle:  'rgba(255,255,255,0.06)',
  borderDefault: 'rgba(255,255,255,0.10)',
  borderStrong:  'rgba(255,255,255,0.18)',

  // Brand
  primary:       '#6366F1',
  primaryHover:  '#4f52d9',
  primaryGlow:   'rgba(99,102,241,0.25)',
  primarySubtle: 'rgba(99,102,241,0.12)',

  // Status
  success:        '#22C55E',
  successSubtle:  'rgba(34,197,94,0.12)',
  warning:        '#F59E0B',
  warningSubtle:  'rgba(245,158,11,0.12)',
  critical:       '#EF4444',
  criticalSubtle: 'rgba(239,68,68,0.12)',
  info:           '#60A5FA',
  infoSubtle:     'rgba(96,165,250,0.12)',

  // Text
  textPrimary:   '#E5E7EB',
  textSecondary: '#9CA3AF',
  textMuted:     '#6B7280',
  textDisabled:  '#374151',
};

export const radius = {
  sm:   '6px',
  md:   '10px',
  lg:   '14px',
  xl:   '18px',
  full: '9999px',
};

export const spacing = {
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
};

export const shadows = {
  sm:   '0 1px 3px rgba(0,0,0,0.4)',
  md:   '0 4px 16px rgba(0,0,0,0.5)',
  lg:   '0 8px 32px rgba(0,0,0,0.6)',
  glow: '0 0 20px rgba(99,102,241,0.25)',
};

export const typography = {
  fontSans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  fontMono: "'JetBrains Mono', 'Fira Code', monospace",
  xs:   '11px',
  sm:   '13px',
  base: '14px',
  md:   '15px',
  lg:   '18px',
  xl:   '22px',
};

// Card style — matches .dash-kpi-card / .dash-section
export const cardStyle = {
  background:   colors.bgSurface,
  border:       `1px solid ${colors.borderSubtle}`,
  borderRadius: radius.lg,
  padding:      spacing[6],
};

// Status badge map
export const statusColors = {
  ok:       { bg: colors.successSubtle,  text: colors.success  },
  online:   { bg: colors.successSubtle,  text: colors.success  },
  warning:  { bg: colors.warningSubtle,  text: colors.warning  },
  critical: { bg: colors.criticalSubtle, text: colors.critical },
  error:    { bg: colors.criticalSubtle, text: colors.critical },
  unknown:  { bg: 'rgba(107,114,128,0.15)', text: colors.textMuted },
  offline:  { bg: 'rgba(107,114,128,0.15)', text: colors.textMuted },
};

export default { colors, radius, spacing, shadows, typography, cardStyle, statusColors };
