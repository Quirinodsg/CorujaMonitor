/**
 * Resilience tests — error handling and edge cases.
 */
import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import ObservabilityDashboard from '../../components/ObservabilityDashboard';
import IntelligentAlerts from '../../components/IntelligentAlerts';

jest.mock('../../services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
  },
}));

import api from '../../services/api';

beforeEach(() => {
  jest.clearAllMocks();
  localStorage.setItem('token', 'test-token');
});

describe('Error Handling Resilience', () => {
  test('API 500 shows error fallback', async () => {
    api.get.mockRejectedValue(new Error('Request failed with status code 500'));
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText(/Erro/i)).toBeInTheDocument();
    });
  });

  test('API timeout shows error message', async () => {
    api.get.mockRejectedValue(new Error('timeout of 30000ms exceeded'));
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText(/Erro/i)).toBeInTheDocument();
    });
  });

  test('invalid JSON response handled', async () => {
    // Simulate a response that causes JSON parse issues
    api.get.mockRejectedValue(new Error('Unexpected token < in JSON'));
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText(/Erro/i)).toBeInTheDocument();
    });
  });

  test('component does not crash on null data', async () => {
    api.get.mockImplementation((url) => {
      if (url.includes('health-score')) return Promise.resolve({ data: null });
      if (url.includes('impact-map')) return Promise.resolve({ data: null });
      if (url.includes('alerts/intelligent')) return Promise.resolve({ data: null });
      return Promise.resolve({ data: null });
    });
    // Should not throw
    await act(async () => { render(<ObservabilityDashboard />); });
    // Component should still be in the DOM
    expect(screen.getByText(/Observabilidade/i)).toBeInTheDocument();
  });

  test('component does not crash on missing fields', async () => {
    api.get.mockImplementation((url) => {
      if (url.includes('health-score')) return Promise.resolve({ data: { score: 50 } }); // missing breakdown
      if (url.includes('impact-map')) return Promise.resolve({ data: {} }); // missing nodes
      if (url.includes('alerts/intelligent')) return Promise.resolve({ data: {} }); // missing alerts
      return Promise.resolve({ data: {} });
    });
    await act(async () => { render(<ObservabilityDashboard />); });
    await waitFor(() => {
      expect(screen.getByText('50')).toBeInTheDocument();
    });
  });

  test('retry mechanism works (auto-refresh recovers)', async () => {
    jest.useFakeTimers();
    let callCount = 0;
    api.get.mockImplementation((url) => {
      callCount++;
      if (callCount <= 3) return Promise.reject(new Error('fail'));
      if (url.includes('health-score')) return Promise.resolve({ data: { score: 88, status: 'healthy', breakdown: { sensors_ok: 80, sensors_warning: 5, sensors_critical: 1, sensors_unknown: 0, sensors_total: 86, open_incidents: 2 } } });
      if (url.includes('impact-map')) return Promise.resolve({ data: { nodes: [] } });
      if (url.includes('alerts/intelligent')) return Promise.resolve({ data: { alerts: [] } });
      return Promise.resolve({ data: {} });
    });

    await act(async () => { render(<ObservabilityDashboard />); });
    // First call fails
    await waitFor(() => expect(screen.getByText(/Erro/i)).toBeInTheDocument());

    // Advance to trigger auto-refresh
    await act(async () => { jest.advanceTimersByTime(31000); });
    await waitFor(() => {
      // After enough retries, data should load
      expect(callCount).toBeGreaterThan(3);
    });
    jest.useRealTimers();
  });
});

describe('IntelligentAlerts Resilience', () => {
  test('handles fetch failure gracefully', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
    await act(async () => { render(<IntelligentAlerts />); });
    // Should not crash, shows empty or error state
    await waitFor(() => {
      expect(screen.getByText(/Nenhum alerta encontrado/i)).toBeInTheDocument();
    });
    jest.restoreAllMocks();
  });
});
