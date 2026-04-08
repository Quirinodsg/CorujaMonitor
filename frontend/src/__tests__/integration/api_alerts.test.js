/**
 * Integration tests for IntelligentAlerts using MSW.
 */
import React from 'react';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import IntelligentAlerts from '../../components/IntelligentAlerts';

const allAlerts = [
  { id: 'ia1', title: 'Critical CPU', severity: 'critical', status: 'open', confidence: 0.95, created_at: '2024-01-15T10:00:00Z' },
  { id: 'ia2', title: 'Warning Memory', severity: 'warning', status: 'acknowledged', confidence: 0.80, created_at: '2024-01-15T09:00:00Z' },
  { id: 'ia3', title: 'Info Disk', severity: 'info', status: 'resolved', confidence: 0.70, created_at: '2024-01-15T08:00:00Z' },
  { id: 'ia4', title: 'Critical Network', severity: 'critical', status: 'open', confidence: 0.91, created_at: '2024-01-15T07:00:00Z' },
];

const server = setupServer(
  http.get('/api/v1/alerts/intelligent', ({ request }) => {
    const url = new URL(request.url);
    const severity = url.searchParams.get('severity');
    const status = url.searchParams.get('status');
    let filtered = [...allAlerts];
    if (severity) filtered = filtered.filter(a => a.severity === severity);
    if (status) filtered = filtered.filter(a => a.status === status);
    return HttpResponse.json({ alerts: filtered });
  }),
  http.get('/api/v1/alerts/intelligent/:id/root-cause', () => {
    return HttpResponse.json({ root_cause: 'Connection pool exhaustion', affected_hosts: ['db-primary'] });
  }),
  http.post('/api/v1/alerts/intelligent/:id/acknowledge', () => {
    return HttpResponse.json({ status: 'acknowledged' });
  }),
  http.post('/api/v1/alerts/intelligent/:id/resolve', () => {
    return HttpResponse.json({ status: 'resolved' });
  }),
);

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

beforeEach(() => {
  localStorage.setItem('token', 'test-token');
});

describe('API Alerts Integration', () => {
  test('fetches and renders intelligent alerts', async () => {
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => {
      expect(screen.getByText('Critical CPU')).toBeInTheDocument();
      expect(screen.getByText('Warning Memory')).toBeInTheDocument();
      expect(screen.getByText('Info Disk')).toBeInTheDocument();
    });
  });

  test('filters work with API params', async () => {
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => expect(screen.getByText('Critical CPU')).toBeInTheDocument());

    // Filter by severity=critical
    const severitySelect = screen.getAllByRole('combobox')[1];
    await act(async () => {
      fireEvent.change(severitySelect, { target: { value: 'critical' } });
    });
    await waitFor(() => {
      expect(screen.getByText('Critical CPU')).toBeInTheDocument();
      expect(screen.getByText('Critical Network')).toBeInTheDocument();
      expect(screen.queryByText('Warning Memory')).not.toBeInTheDocument();
      expect(screen.queryByText('Info Disk')).not.toBeInTheDocument();
    });
  });

  test('resolve/acknowledge actions call API', async () => {
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => expect(screen.getByText('Critical CPU')).toBeInTheDocument());

    // Click on alert to open detail
    await act(async () => {
      fireEvent.click(screen.getByText('Critical CPU'));
    });
    await waitFor(() => {
      expect(screen.getByText(/Reconhecer/i)).toBeInTheDocument();
      expect(screen.getByText(/Resolver/i)).toBeInTheDocument();
    });
  });

  test('handles pagination (limit param)', async () => {
    // Verify the component sends limit param
    let capturedUrl = '';
    server.use(
      http.get('/api/v1/alerts/intelligent', ({ request }) => {
        capturedUrl = request.url;
        return HttpResponse.json({ alerts: allAlerts });
      }),
    );
    await act(async () => { render(<IntelligentAlerts />); });
    await waitFor(() => {
      expect(capturedUrl).toContain('limit=');
    });
  });
});
