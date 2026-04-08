import React from 'react';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import IntelligentAlerts from '../../components/IntelligentAlerts';

// Mock fetch globally for this component (uses native fetch, not axios)
const mockAlerts = [
  { id: 'a1', title: 'CPU Spike on DB', severity: 'critical', status: 'open', confidence: 0.95, root_cause: 'Connection pool exhaustion', created_at: '2024-01-15T10:00:00Z' },
  { id: 'a2', title: 'Memory Pressure', severity: 'warning', status: 'acknowledged', confidence: 0.82, root_cause: null, created_at: '2024-01-15T09:00:00Z' },
  { id: 'a3', title: 'Disk Usage Info', severity: 'info', status: 'resolved', confidence: 0.71, root_cause: 'Log rotation needed', created_at: '2024-01-15T08:00:00Z', resolved_at: '2024-01-15T08:30:00Z' },
];

let fetchMock;

beforeEach(() => {
  localStorage.setItem('token', 'test-token');
  fetchMock = jest.fn().mockImplementation((url) => {
    if (url.includes('/alerts/intelligent') && !url.includes('/root-cause') && !url.includes('/acknowledge') && !url.includes('/resolve')) {
      const urlObj = new URL(url, 'http://localhost');
      const severity = urlObj.searchParams.get('severity');
      const status = urlObj.searchParams.get('status');
      let filtered = [...mockAlerts];
      if (severity) filtered = filtered.filter(a => a.severity === severity);
      if (status) filtered = filtered.filter(a => a.status === status);
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ alerts: filtered }) });
    }
    if (url.includes('/root-cause')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ root_cause: 'DB overload', affected_hosts: ['db-1'] }) });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
  global.fetch = fetchMock;
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe('IntelligentAlerts', () => {
  test('renders alert list', async () => {
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => {
      expect(screen.getByText('CPU Spike on DB')).toBeInTheDocument();
      expect(screen.getByText('Memory Pressure')).toBeInTheDocument();
    });
  });

  test('filters by severity', async () => {
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => expect(screen.getByText('CPU Spike on DB')).toBeInTheDocument());

    const severitySelect = screen.getAllByRole('combobox')[1]; // second select
    await act(async () => {
      fireEvent.change(severitySelect, { target: { value: 'critical' } });
    });
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('severity=critical'),
        expect.anything()
      );
    });
  });

  test('filters by status', async () => {
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => expect(screen.getByText('CPU Spike on DB')).toBeInTheDocument());

    const statusSelect = screen.getAllByRole('combobox')[0]; // first select
    await act(async () => {
      fireEvent.change(statusSelect, { target: { value: 'open' } });
    });
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining('status=open'),
        expect.anything()
      );
    });
  });

  test('shows root cause column', async () => {
    await act(async () => { render(<IntelligentAlerts />); });
    // Click on an alert to see root cause in detail
    await waitFor(() => expect(screen.getByText('CPU Spike on DB')).toBeInTheDocument());
    await act(async () => {
      fireEvent.click(screen.getByText('CPU Spike on DB'));
    });
    await waitFor(() => {
      expect(screen.getByText(/Causa Raiz/i)).toBeInTheDocument();
    });
  });

  test('shows confidence percentage', async () => {
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => {
      expect(screen.getByText(/95% conf/i)).toBeInTheDocument();
      expect(screen.getByText(/82% conf/i)).toBeInTheDocument();
    });
  });

  test('handles empty alerts', async () => {
    fetchMock.mockImplementation(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve({ alerts: [] }) })
    );
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => {
      expect(screen.getByText(/Nenhum alerta encontrado/i)).toBeInTheDocument();
    });
  });

  test('handles loading state', () => {
    fetchMock.mockImplementation(() => new Promise(() => {}));
    render(<IntelligentAlerts />);
    expect(screen.getByText(/Carregando alertas/i)).toBeInTheDocument();
  });
});
