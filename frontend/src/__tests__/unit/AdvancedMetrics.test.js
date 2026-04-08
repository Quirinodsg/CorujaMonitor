import React from 'react';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import AdvancedMetrics from '../../components/AdvancedMetrics';

let fetchMock;

const mockServers = [
  { id: 1, name: 'Server-1', hostname: 'srv-1.local' },
  { id: 2, name: 'Server-2', hostname: 'srv-2.local' },
];

const mockSensors = [
  { id: 100, name: 'CPU Sensor', sensor_type: 'cpu', server_id: 1 },
  { id: 101, name: 'Memory Sensor', sensor_type: 'memory', server_id: 1 },
];

const mockMetrics = Array.from({ length: 20 }, (_, i) => ({
  id: i, sensor_id: 100, value: 30 + Math.random() * 40, unit: '%', status: 'ok',
  timestamp: new Date(Date.now() - i * 60000).toISOString(),
}));

beforeEach(() => {
  localStorage.setItem('token', 'test-token');
  fetchMock = jest.fn().mockImplementation((url) => {
    if (url.includes('/servers')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockServers) });
    if (url.includes('/sensors')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockSensors) });
    if (url.includes('/metrics')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockMetrics) });
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });
  global.fetch = fetchMock;
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe('AdvancedMetrics', () => {
  test('renders server selector', async () => {
    await act(async () => { render(<AdvancedMetrics />); });
    await waitFor(() => {
      expect(screen.getByText('Selecione um servidor')).toBeInTheDocument();
      expect(screen.getByText('Server-1')).toBeInTheDocument();
      expect(screen.getByText('Server-2')).toBeInTheDocument();
    });
  });

  test('renders period buttons', async () => {
    await act(async () => { render(<AdvancedMetrics />); });
    expect(screen.getByText('1h')).toBeInTheDocument();
    expect(screen.getByText('6h')).toBeInTheDocument();
    expect(screen.getByText('24h')).toBeInTheDocument();
    expect(screen.getByText('7d')).toBeInTheDocument();
  });

  test('renders sparkline charts after server selection', async () => {
    await act(async () => { render(<AdvancedMetrics />); });
    await waitFor(() => expect(screen.getByText('Server-1')).toBeInTheDocument());

    const select = screen.getByRole('combobox');
    await act(async () => {
      fireEvent.change(select, { target: { value: '1' } });
    });
    await waitFor(() => {
      // Sparkline renders SVG polyline elements
      const svgs = document.querySelectorAll('svg polyline');
      expect(svgs.length).toBeGreaterThan(0);
    });
  });

  test('shows export CSV button', async () => {
    await act(async () => { render(<AdvancedMetrics />); });
    expect(screen.getByText(/Exportar CSV/i)).toBeInTheDocument();
  });

  test('handles no server selected', async () => {
    await act(async () => { render(<AdvancedMetrics />); });
    await waitFor(() => {
      expect(screen.getByText(/Selecione um servidor para visualizar/i)).toBeInTheDocument();
    });
  });

  test('handles loading state', async () => {
    fetchMock.mockImplementation((url) => {
      if (url.includes('/servers')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockServers) });
      // Sensors/metrics never resolve
      return new Promise(() => {});
    });
    await act(async () => { render(<AdvancedMetrics />); });
    await waitFor(() => expect(screen.getByText('Server-1')).toBeInTheDocument());

    const select = screen.getByRole('combobox');
    await act(async () => {
      fireEvent.change(select, { target: { value: '1' } });
    });
    await waitFor(() => {
      expect(screen.getByText(/Carregando métricas/i)).toBeInTheDocument();
    });
  });

  test('handles empty metrics', async () => {
    fetchMock.mockImplementation((url) => {
      if (url.includes('/servers')) return Promise.resolve({ ok: true, json: () => Promise.resolve(mockServers) });
      if (url.includes('/sensors')) return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    });
    await act(async () => { render(<AdvancedMetrics />); });
    await waitFor(() => expect(screen.getByText('Server-1')).toBeInTheDocument());

    const select = screen.getByRole('combobox');
    await act(async () => {
      fireEvent.change(select, { target: { value: '1' } });
    });
    await waitFor(() => {
      expect(screen.getByText(/Nenhuma métrica encontrada/i)).toBeInTheDocument();
    });
  });
});
