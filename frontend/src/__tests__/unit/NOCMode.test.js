import React from 'react';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import NOCMode from '../../components/NOCMode';

jest.mock('../../services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

import api from '../../services/api';

const mockGlobal = {
  servers_ok: 45,
  servers_warning: 3,
  servers_critical: 1,
  availability: '99.8',
  companies: [
    { id: 1, name: 'Empresa A', status: 'ok', ok: 20, warning: 1, critical: 0, availability: '99.9' },
  ],
};

const mockIncidents = [
  { id: 1, severity: 'critical', server_name: 'srv-db-01', description: 'CPU acima de 95%', created_at: new Date().toISOString(), duration: '15min' },
  { id: 2, severity: 'warning', server_name: 'srv-web-02', description: 'Memória alta', created_at: new Date().toISOString(), duration: '5min' },
];

function setupApiSuccess() {
  api.get.mockImplementation((url) => {
    if (url.includes('global-status')) return Promise.resolve({ data: mockGlobal });
    if (url.includes('heatmap')) return Promise.resolve({ data: [] });
    if (url.includes('active-incidents')) return Promise.resolve({ data: mockIncidents });
    if (url.includes('kpis')) return Promise.resolve({ data: { mttr: '12', mtbf: '800', sla: '99.97', incidents_24h: '8' } });
    if (url.includes('standalone')) return Promise.resolve({ data: [] });
    if (url.includes('servers')) return Promise.resolve({ data: [] });
    return Promise.resolve({ data: {} });
  });
}

beforeEach(() => {
  jest.useFakeTimers();
  jest.clearAllMocks();
  localStorage.setItem('token', 'test-token');
});

afterEach(() => {
  jest.useRealTimers();
});

describe('NOCMode', () => {
  test('renders fullscreen layout', async () => {
    setupApiSuccess();
    await act(async () => {
      render(<NOCMode onExit={jest.fn()} />);
    });
    expect(screen.getByText(/CORUJA MONITOR - NOC/i)).toBeInTheDocument();
  });

  test('calls onExit callback', async () => {
    setupApiSuccess();
    const onExit = jest.fn();
    await act(async () => {
      render(<NOCMode onExit={onExit} />);
    });
    const exitBtn = screen.getByText(/Sair/i);
    fireEvent.click(exitBtn);
    expect(onExit).toHaveBeenCalledTimes(1);
  });

  test('displays critical alerts prominently', async () => {
    setupApiSuccess();
    await act(async () => {
      render(<NOCMode onExit={jest.fn()} />);
    });
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument(); // servers_critical
    });
    expect(screen.getByText(/CRÍTICOS/i)).toBeInTheDocument();
  });

  test('shows server status grid', async () => {
    setupApiSuccess();
    await act(async () => {
      render(<NOCMode onExit={jest.fn()} />);
    });
    await waitFor(() => {
      expect(screen.getByText('45')).toBeInTheDocument(); // servers_ok
      expect(screen.getByText('3')).toBeInTheDocument();  // servers_warning
    });
  });

  test('auto-refreshes data', async () => {
    setupApiSuccess();
    await act(async () => {
      render(<NOCMode onExit={jest.fn()} />);
    });
    const initialCallCount = api.get.mock.calls.length;
    await act(async () => {
      jest.advanceTimersByTime(3500); // NOC refreshes every 3s
    });
    expect(api.get.mock.calls.length).toBeGreaterThan(initialCallCount);
  });
});
