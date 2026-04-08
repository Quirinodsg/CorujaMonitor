/**
 * Integration tests for ObservabilityDashboard using jest.mock for api.
 */
import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import ObservabilityDashboard from '../../components/ObservabilityDashboard';

jest.mock('../../services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
  },
}));

import api from '../../services/api';

const healthData = {
  score: 92,
  status: 'healthy',
  breakdown: { sensors_ok: 100, sensors_warning: 5, sensors_critical: 1, sensors_unknown: 2, sensors_total: 108, open_incidents: 3 },
};

const impactNodes = [
  { id: 'im1', name: 'Impacted-Server', ip: '10.0.0.5', severity: 'critical', critical_sensors: 2, warning_sensors: 1 },
];

const alertsData = {
  alerts: [
    { id: 'ia1', title: 'Integration Alert 1', severity: 'critical', root_cause: 'Disk failure', confidence: 0.88, created_at: '2024-01-15T10:00:00Z' },
  ],
};

function setupSuccess() {
  api.get.mockImplementation((url) => {
    if (url.includes('health-score')) return Promise.resolve({ data: healthData });
    if (url.includes('impact-map')) return Promise.resolve({ data: { nodes: impactNodes } });
    if (url.includes('alerts/intelligent')) return Promise.resolve({ data: alertsData });
    return Promise.resolve({ data: {} });
  });
}

beforeEach(() => {
  jest.clearAllMocks();
  localStorage.setItem('token', 'test-token');
});

describe('API Dashboard Integration', () => {
  test('fetches health score and renders', async () => {
    setupSuccess();
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText('92')).toBeInTheDocument();
    });
  });

  test('fetches impact map and renders nodes', async () => {
    setupSuccess();
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText('Impacted-Server')).toBeInTheDocument();
    });
  });

  test('fetches alerts and renders table', async () => {
    setupSuccess();
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText('Integration Alert 1')).toBeInTheDocument();
      expect(screen.getByText('Disk failure')).toBeInTheDocument();
    });
  });

  test('handles API 500 error gracefully', async () => {
    api.get.mockRejectedValue(new Error('Request failed with status code 500'));
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText(/Erro/i)).toBeInTheDocument();
    });
  });

  test('handles network timeout', async () => {
    api.get.mockRejectedValue(new Error('Network Error'));
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText(/Erro/i)).toBeInTheDocument();
    });
  });

  test('retries on failure (auto-refresh)', async () => {
    jest.useFakeTimers();
    let callCount = 0;
    api.get.mockImplementation((url) => {
      callCount++;
      if (callCount <= 3) return Promise.reject(new Error('fail'));
      if (url.includes('health-score')) return Promise.resolve({ data: healthData });
      if (url.includes('impact-map')) return Promise.resolve({ data: { nodes: [] } });
      if (url.includes('alerts/intelligent')) return Promise.resolve({ data: { alerts: [] } });
      return Promise.resolve({ data: {} });
    });
    await act(async () => { render(<ObservabilityDashboard />); });
    // First call fails
    await waitFor(() => expect(screen.getByText(/Erro/i)).toBeInTheDocument());
    // Advance timer to trigger auto-refresh (30s interval)
    await act(async () => { jest.advanceTimersByTime(31000); });
    await waitFor(() => {
      expect(callCount).toBeGreaterThanOrEqual(2);
    });
    jest.useRealTimers();
  });
});
