/**
 * Integration tests for ObservabilityDashboard using MSW.
 */
import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import ObservabilityDashboard from '../../components/ObservabilityDashboard';

// We need to mock the api module to use our MSW base URL
jest.mock('../../services/api', () => {
  const axios = require('axios');
  const instance = axios.create({ baseURL: '' });
  return { __esModule: true, default: instance };
});

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

const server = setupServer(
  http.get('/api/v1/observability/health-score', () => HttpResponse.json(healthData)),
  http.get('/api/v1/observability/impact-map', () => HttpResponse.json({ nodes: impactNodes })),
  http.get('/api/v1/alerts/intelligent', () => HttpResponse.json(alertsData)),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

beforeEach(() => {
  localStorage.setItem('token', 'test-token');
});

describe('API Dashboard Integration', () => {
  test('fetches health score and renders', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText('92')).toBeInTheDocument();
    });
  });

  test('fetches impact map and renders nodes', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText('Impacted-Server')).toBeInTheDocument();
    });
  });

  test('fetches alerts and renders table', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText('Integration Alert 1')).toBeInTheDocument();
      expect(screen.getByText('Disk failure')).toBeInTheDocument();
    });
  });

  test('handles API 500 error gracefully', async () => {
    server.use(
      http.get('/api/v1/observability/health-score', () => HttpResponse.json({ error: 'Internal Server Error' }, { status: 500 })),
      http.get('/api/v1/observability/impact-map', () => HttpResponse.json({ error: 'fail' }, { status: 500 })),
      http.get('/api/v1/alerts/intelligent', () => HttpResponse.json({ error: 'fail' }, { status: 500 })),
    );
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText(/Erro/i)).toBeInTheDocument();
    });
  });

  test('handles network timeout', async () => {
    server.use(
      http.get('/api/v1/observability/health-score', () => HttpResponse.error()),
      http.get('/api/v1/observability/impact-map', () => HttpResponse.error()),
      http.get('/api/v1/alerts/intelligent', () => HttpResponse.error()),
    );
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText(/Erro/i)).toBeInTheDocument();
    });
  });

  test('retries on failure (auto-refresh)', async () => {
    jest.useFakeTimers();
    let callCount = 0;
    server.use(
      http.get('/api/v1/observability/health-score', () => {
        callCount++;
        if (callCount <= 1) return HttpResponse.error();
        return HttpResponse.json(healthData);
      }),
      http.get('/api/v1/observability/impact-map', () => HttpResponse.json({ nodes: [] })),
      http.get('/api/v1/alerts/intelligent', () => HttpResponse.json({ alerts: [] })),
    );
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
