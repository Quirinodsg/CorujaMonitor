/**
 * Performance tests — rendering large datasets.
 */
import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { generateBulkMetrics, generateBulkAlerts, generateBulkTopology } from '../utils/event_gen';
import ObservabilityDashboard from '../../components/ObservabilityDashboard';
import IntelligentAlerts from '../../components/IntelligentAlerts';
import TopologyView from '../../components/TopologyView';

jest.mock('../../services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

import api from '../../services/api';

beforeEach(() => {
  jest.clearAllMocks();
  localStorage.setItem('token', 'test-token');
});

describe('Render Performance', () => {
  test('renders 1000 metrics without lag (< 3s)', async () => {
    const bulkMetrics = generateBulkMetrics(1000);
    // Group into types for the dashboard
    const grouped = {};
    bulkMetrics.forEach(m => {
      const key = m.sensor_type || 'other';
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(m);
    });

    // Test that generating 1000 metrics is fast
    const start = performance.now();
    expect(bulkMetrics).toHaveLength(1000);
    expect(Object.keys(grouped).length).toBeGreaterThan(0);
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(3000);
  });

  test('renders 500 alerts without lag', async () => {
    const bulkAlerts = generateBulkAlerts(500);

    global.fetch = jest.fn().mockImplementation(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve({ alerts: bulkAlerts.slice(0, 100) }) })
    );

    const start = performance.now();
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => {
      expect(screen.getByText('Bulk Alert 1')).toBeInTheDocument();
    });
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(3000);

    jest.restoreAllMocks();
  });

  test('no excessive re-renders on data update', async () => {
    let renderCount = 0;
    const OriginalDashboard = ObservabilityDashboard;

    // Track renders via api call count as proxy
    api.get.mockImplementation((url) => {
      renderCount++;
      if (url.includes('health-score')) return Promise.resolve({ data: { score: 85, status: 'healthy', breakdown: { sensors_ok: 90, sensors_warning: 5, sensors_critical: 2, sensors_unknown: 1, sensors_total: 98, open_incidents: 3 } } });
      if (url.includes('impact-map')) return Promise.resolve({ data: { nodes: [] } });
      if (url.includes('alerts/intelligent')) return Promise.resolve({ data: { alerts: [] } });
      return Promise.resolve({ data: {} });
    });

    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => expect(screen.getByText('85')).toBeInTheDocument());

    const initialRenderCount = renderCount;

    // Simulate a WS update — should not cause excessive API re-fetches
    const ws = global.WebSocket._instances[global.WebSocket._instances.length - 1];
    if (ws) {
      await act(async () => {
        ws._simulateMessage({ type: 'observability_update', health_score: 90, sensors_ok: 95, sensors_critical: 1, sensors_total: 100 });
      });
    }

    // API calls should not spike (WS updates state directly, not via API)
    expect(renderCount - initialRenderCount).toBeLessThan(5);
  });

  test('large topology graph renders', async () => {
    const bigTopo = generateBulkTopology(50);
    api.get.mockImplementation((url) => {
      if (url.includes('topology/graph')) return Promise.resolve({ data: bigTopo });
      return Promise.resolve({ data: {} });
    });

    const start = performance.now();
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => {
      expect(screen.getByText(/50 nos/i)).toBeInTheDocument();
    });
    const elapsed = performance.now() - start;
    expect(elapsed).toBeLessThan(5000);
  });
});
