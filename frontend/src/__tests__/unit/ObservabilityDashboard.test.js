import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import ObservabilityDashboard from '../../components/ObservabilityDashboard';

// Mock the api service
jest.mock('../../services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
  },
}));

import api from '../../services/api';

const mockHealthData = {
  score: 87,
  status: 'healthy',
  breakdown: {
    sensors_ok: 95,
    sensors_warning: 8,
    sensors_critical: 2,
    sensors_unknown: 3,
    sensors_total: 108,
    open_incidents: 4,
  },
};

const mockImpactMap = {
  nodes: [
    { id: 'n1', name: 'Server-A', ip: '10.0.0.1', severity: 'critical', critical_sensors: 3, warning_sensors: 0 },
    { id: 'n2', name: 'Server-B', ip: '10.0.0.2', severity: 'warning', critical_sensors: 0, warning_sensors: 2 },
  ],
};

const mockAlerts = {
  alerts: [
    { id: 'a1', title: 'CPU Spike', severity: 'critical', root_cause: 'DB overload', confidence: 0.92, created_at: '2024-01-01T00:00:00Z' },
    { id: 'a2', title: 'Memory High', severity: 'warning', root_cause: null, confidence: 0.78, created_at: '2024-01-01T01:00:00Z' },
  ],
};

function setupApiSuccess() {
  api.get.mockImplementation((url) => {
    if (url.includes('health-score')) return Promise.resolve({ data: mockHealthData });
    if (url.includes('impact-map')) return Promise.resolve({ data: mockImpactMap });
    if (url.includes('alerts/intelligent')) return Promise.resolve({ data: mockAlerts });
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

describe('ObservabilityDashboard', () => {
  test('renders loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {})); // never resolves
    render(<ObservabilityDashboard />);
    expect(screen.getAllByText(/Carregando/i).length).toBeGreaterThan(0);
  });

  test('renders health score when data loaded', async () => {
    setupApiSuccess();
    await act(async () => {
      render(<ObservabilityDashboard />);
    });
    await waitFor(() => {
      expect(screen.getByText('87')).toBeInTheDocument();
    });
    expect(screen.getByText(/HEALTH SCORE/i)).toBeInTheDocument();
  });

  test('renders impact map nodes', async () => {
    setupApiSuccess();
    await act(async () => {
      render(<ObservabilityDashboard />);
    });
    await waitFor(() => {
      expect(screen.getByText('Server-A')).toBeInTheDocument();
      expect(screen.getByText('Server-B')).toBeInTheDocument();
    });
  });

  test('renders alerts table', async () => {
    setupApiSuccess();
    await act(async () => {
      render(<ObservabilityDashboard />);
    });
    await waitFor(() => {
      expect(screen.getByText('CPU Spike')).toBeInTheDocument();
      expect(screen.getByText('Memory High')).toBeInTheDocument();
    });
    // Root cause column
    expect(screen.getByText('DB overload')).toBeInTheDocument();
  });

  test('shows error state on fetch failure', async () => {
    api.get.mockRejectedValue(new Error('Network Error'));
    await act(async () => {
      render(<ObservabilityDashboard />);
    });
    await waitFor(() => {
      expect(screen.getByText(/Erro/i)).toBeInTheDocument();
    });
  });

  test('shows empty state when no alerts', async () => {
    api.get.mockImplementation((url) => {
      if (url.includes('health-score')) return Promise.resolve({ data: mockHealthData });
      if (url.includes('impact-map')) return Promise.resolve({ data: { nodes: [] } });
      if (url.includes('alerts/intelligent')) return Promise.resolve({ data: { alerts: [] } });
      return Promise.resolve({ data: {} });
    });
    await act(async () => {
      render(<ObservabilityDashboard />);
    });
    await waitFor(() => {
      expect(screen.getByText(/Nenhum alerta inteligente aberto/i)).toBeInTheDocument();
    });
  });

  test('displays WS status badge', async () => {
    setupApiSuccess();
    await act(async () => {
      render(<ObservabilityDashboard />);
    });
    // Initially connecting, then connected after WS mock auto-connects
    await waitFor(() => {
      const badge = screen.getByText(/Live|Conectando|Offline/i);
      expect(badge).toBeInTheDocument();
    });
  });
});
