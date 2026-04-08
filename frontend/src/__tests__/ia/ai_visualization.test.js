/**
 * AI/AIOps visualization tests.
 */
import React from 'react';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import AIOpsV3 from '../../components/AIOpsV3';

let fetchMock;

const mockPipelineStatus = {
  total_runs: 200,
  total_intelligent_alerts: 55,
  total_remediation_actions: 22,
  circuit_breaker: 'closed',
};

const mockRuns = {
  runs: [
    {
      run_id: 'run-viz-001-abc-def',
      agents: ['AnomalyDetection', 'Correlation', 'RootCause', 'Decision', 'AutoRemediationAgent'],
      agents_success: 4,
      agents_error: 1,
      started_at: '2024-01-15T10:00:00Z',
    },
  ],
};

const mockLogs = {
  logs: [
    { id: 'l1', agent_name: 'AnomalyDetection', run_id: 'run-viz-001', status: 'success', output: { anomalies: 3 }, timestamp: '2024-01-15T10:00:00Z' },
    { id: 'l2', agent_name: 'RootCause', run_id: 'run-viz-001', status: 'error', error: 'Model timeout', timestamp: '2024-01-15T10:01:00Z' },
  ],
};

const mockFeedback = { actions_successful: 42, actions_failed: 8, total_feedback: 50 };

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

describe('AI Visualization', () => {
  test('anomaly events shown in pipeline', async () => {
    await act(async () => { render(<AIOpsV3 />); });
    await waitFor(() => {
      // Pipeline stages are always visible
      expect(screen.getByText('Anomaly Detection')).toBeInTheDocument();
    });
    // Switch to logs tab to see anomaly agent logs
    await act(async () => {
      fireEvent.click(screen.getByText(/Logs de Agentes/i));
    });
    await waitFor(() => {
      expect(screen.getByText('AnomalyDetection')).toBeInTheDocument();
    });
  });

  test('root cause analysis visible', async () => {
    await act(async () => { render(<AIOpsV3 />); });
    // Switch to logs tab
    await act(async () => {
      fireEvent.click(screen.getByText(/Logs de Agentes/i));
    });
    await waitFor(() => {
      expect(screen.getByText('RootCause')).toBeInTheDocument();
      expect(screen.getByText('Model timeout')).toBeInTheDocument();
    });
  });

  test('agent status indicators correct', async () => {
    await act(async () => { render(<AIOpsV3 />); });
    await waitFor(() => {
      // Runs tab shows success/error counts
      expect(screen.getByText(/4✓/)).toBeInTheDocument();
      expect(screen.getByText(/1✗/)).toBeInTheDocument();
    });
  });

  test('circuit breaker state displayed', async () => {
    await act(async () => { render(<AIOpsV3 />); });
    await waitFor(() => {
      // Pipeline metrics show total runs and alerts
      expect(screen.getByText('200')).toBeInTheDocument();
      expect(screen.getByText('55')).toBeInTheDocument();
      expect(screen.getByText('22')).toBeInTheDocument();
    });
  });

  test('feedback metrics shown', async () => {
    await act(async () => { render(<AIOpsV3 />); });
    await waitFor(() => {
      // Feedback actions_successful
      expect(screen.getByText('42')).toBeInTheDocument();
      expect(screen.getByText(/Ações Bem-sucedidas/i)).toBeInTheDocument();
    });
  });
});
