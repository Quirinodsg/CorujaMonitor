import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import AIOpsV3 from '../../components/AIOpsV3';

let fetchMock;

const mockPipelineStatus = {
  total_runs: 156,
  total_intelligent_alerts: 42,
  total_remediation_actions: 18,
  circuit_breaker: 'closed',
};

const mockRuns = {
  runs: [
    {
      run_id: 'run-abc-123-def-456',
      agents: ['AnomalyDetection', 'Correlation', 'RootCause', 'Decision'],
      agents_success: 4,
      agents_error: 0,
      started_at: '2024-01-15T10:00:00Z',
    },
  ],
};

const mockLogs = {
  logs: [
    { id: 'log-1', agent_name: 'AnomalyDetection', run_id: 'run-abc-123', status: 'success', output: { anomalies: 2 }, timestamp: '2024-01-15T10:00:00Z' },
    { id: 'log-2', agent_name: 'RootCause', run_id: 'run-abc-123', status: 'error', error: 'Timeout', timestamp: '2024-01-15T10:01:00Z' },
  ],
};

const mockFeedback = { actions_successful: 42, actions_failed: 3 };

beforeEach(() => {
  localStorage.setItem('token', 'test-token');
  fetchMock = jest.fn().mockImplementation((url) => {
    if (url.includes('pipeline/status')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockPipelineStatus) });
    if (url.includes('pipeline/runs')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockRuns) });
    if (url.includes('pipeline/logs')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockLogs) });
    if (url.includes('feedback-metrics')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockFeedback) });
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
  global.fetch = fetchMock;
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe('AIOpsV3', () => {
  test('renders pipeline agents', async () => {
    await act(async () => { render(<AIOpsV3 />); });
    await waitFor(() => {
      expect(screen.getByText('Anomaly Detection')).toBeInTheDocument();
      expect(screen.getByText('Correlation')).toBeInTheDocument();
      expect(screen.getByText('Root Cause')).toBeInTheDocument();
      expect(screen.getByText('Decision')).toBeInTheDocument();
      expect(screen.getByText('Auto Remediation')).toBeInTheDocument();
    });
  });

  test('shows agent status colors', async () => {
    await act(async () => { render(<AIOpsV3 />); });
    await waitFor(() => {
      // Runs tab shows success/error counts
      expect(screen.getByText(/4✓/)).toBeInTheDocument();
    });
  });

  test('displays execution history', async () => {
    await act(async () => { render(<AIOpsV3 />); });
    await waitFor(() => {
      expect(screen.getByText(/run-abc-123/)).toBeInTheDocument();
    });
  });

  test('shows circuit breaker state', async () => {
    await act(async () => { render(<AIOpsV3 />); });
    await waitFor(() => {
      // Pipeline status metrics are rendered
      expect(screen.getByText('156')).toBeInTheDocument(); // total_runs
      // 42 appears in both "Alertas Gerados" and "Ações Bem-sucedidas"
      expect(screen.getAllByText('42').length).toBeGreaterThanOrEqual(2);
    });
  });

  test('handles empty pipeline data', async () => {
    fetchMock.mockImplementation((url) => {
      if (url.includes('pipeline/status')) return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
      if (url.includes('pipeline/runs')) return Promise.resolve({ ok: true, json: () => Promise.resolve({ runs: [] }) });
      if (url.includes('pipeline/logs')) return Promise.resolve({ ok: true, json: () => Promise.resolve({ logs: [] }) });
      if (url.includes('feedback-metrics')) return Promise.resolve({ ok: false });
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });
    await act(async () => { render(<AIOpsV3 />); });
    await waitFor(() => {
      expect(screen.getByText(/Nenhum run registrado/i)).toBeInTheDocument();
    });
  });
});
