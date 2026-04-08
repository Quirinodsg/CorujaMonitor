/**
 * WebSocket realtime tests for ObservabilityDashboard.
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

const mockHealth = {
  score: 85,
  status: 'healthy',
  breakdown: { sensors_ok: 90, sensors_warning: 5, sensors_critical: 2, sensors_unknown: 1, sensors_total: 98, open_incidents: 3 },
};

function setupApi() {
  api.get.mockImplementation((url) => {
    if (url.includes('health-score')) return Promise.resolve({ data: mockHealth });
    if (url.includes('impact-map')) return Promise.resolve({ data: { nodes: [] } });
    if (url.includes('alerts/intelligent')) return Promise.resolve({ data: { alerts: [] } });
    return Promise.resolve({ data: {} });
  });
}

function getLatestWS() {
  return global.WebSocket._instances[global.WebSocket._instances.length - 1];
}

beforeEach(() => {
  jest.useFakeTimers();
  jest.clearAllMocks();
  global.WebSocket._instances = [];
  localStorage.setItem('token', 'test-token');
  setupApi();
});

afterEach(() => {
  jest.useRealTimers();
});

describe('WebSocket Realtime', () => {
  test('connects to WS on mount', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });
    // WS connection is delayed by 100ms in the component
    await act(async () => { jest.advanceTimersByTime(200); });
    expect(global.WebSocket._instances.length).toBeGreaterThanOrEqual(1);
    const ws = getLatestWS();
    expect(ws.url).toContain('/api/v1/ws/observability');
  });

  test('updates health score from WS message', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => expect(screen.getByText('85')).toBeInTheDocument());

    await act(async () => { jest.advanceTimersByTime(200); });
    const ws = getLatestWS();

    await act(async () => {
      ws._simulateMessage({
        type: 'observability_update',
        health_score: 95,
        sensors_ok: 100,
        sensors_critical: 0,
        sensors_total: 100,
      });
    });

    await waitFor(() => {
      expect(screen.getByText('95')).toBeInTheDocument();
    });
  });

  test('handles WS disconnect', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });
    await act(async () => { jest.advanceTimersByTime(200); });
    const ws = getLatestWS();

    await act(async () => {
      ws._simulateDisconnect();
    });

    await waitFor(() => {
      const badge = screen.getByText(/Offline/i);
      expect(badge).toBeInTheDocument();
    });
  });

  test('reconnects after disconnect (5s delay)', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });
    await act(async () => { jest.advanceTimersByTime(200); });

    const initialCount = global.WebSocket._instances.length;
    const ws = getLatestWS();

    await act(async () => {
      ws._simulateDisconnect();
    });

    // Advance 5s for reconnect
    await act(async () => { jest.advanceTimersByTime(5100); });

    expect(global.WebSocket._instances.length).toBeGreaterThan(initialCount);
  });

  test('handles burst of 100 messages without freeze', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });
    await act(async () => { jest.advanceTimersByTime(200); });
    const ws = getLatestWS();

    const start = performance.now();
    await act(async () => {
      for (let i = 0; i < 100; i++) {
        ws._simulateMessage({
          type: 'observability_update',
          health_score: 50 + (i % 50),
          sensors_ok: 90 + i,
          sensors_critical: i % 3,
          sensors_total: 100 + i,
        });
      }
    });
    const elapsed = performance.now() - start;

    // Should process 100 messages in under 3 seconds
    expect(elapsed).toBeLessThan(3000);
    // Last message should be reflected
    await waitFor(() => {
      expect(screen.getByText('99')).toBeInTheDocument(); // 50 + (99 % 50) = 99
    });
  });

  test('no duplicate updates from same message', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });
    await act(async () => { jest.advanceTimersByTime(200); });
    const ws = getLatestWS();

    const msg = {
      type: 'observability_update',
      health_score: 77,
      sensors_ok: 80,
      sensors_critical: 1,
      sensors_total: 90,
    };

    await act(async () => {
      ws._simulateMessage(msg);
      ws._simulateMessage(msg);
      ws._simulateMessage(msg);
    });

    await waitFor(() => {
      // Should show 77 exactly once in the health gauge
      const elements = screen.getAllByText('77');
      expect(elements.length).toBe(1);
    });
  });

  test('shows correct WS status badge (connected/disconnected/error)', async () => {
    await act(async () => { render(<ObservabilityDashboard />); });

    // Initially connecting
    expect(screen.getByText(/Conectando/i)).toBeInTheDocument();

    // After WS connects
    await act(async () => { jest.advanceTimersByTime(200); });
    await waitFor(() => {
      expect(screen.getByText(/Live/i)).toBeInTheDocument();
    });

    // After disconnect
    const ws = getLatestWS();
    await act(async () => { ws._simulateDisconnect(); });
    await waitFor(() => {
      expect(screen.getByText(/Offline/i)).toBeInTheDocument();
    });
  });
});
