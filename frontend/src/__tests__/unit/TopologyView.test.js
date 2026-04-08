import React from 'react';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import TopologyView from '../../components/TopologyView';

jest.mock('../../services/api', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

import api from '../../services/api';

const mockGraph = {
  nodes: [
    { id: 'n1', name: 'Core-Switch', type: 'switch', status: 'ok', metadata: { ip: '10.0.0.1', device_type: 'switch', hostname: 'core-sw' } },
    { id: 'n2', name: 'Web-Server', type: 'server', status: 'ok', metadata: { ip: '10.0.0.2', device_type: 'server', hostname: 'web-01' } },
    { id: 'n3', name: 'DB-Server', type: 'database', status: 'critical', metadata: { ip: '10.0.0.3', device_type: 'database', hostname: 'db-01' } },
  ],
  edges: [
    { source: 'n1', target: 'n2', type: 'infrastructure' },
    { source: 'n1', target: 'n3', type: 'dependency' },
  ],
};

const mockImpact = {
  total_impact: 2,
  affected_hosts: ['web-01', 'db-01'],
  depends_on: ['core-switch'],
  all_affected: ['n2', 'n3'],
  edge_count: 3,
};

function setupApiSuccess() {
  api.get.mockImplementation((url) => {
    if (url.includes('topology/graph')) return Promise.resolve({ data: mockGraph });
    if (url.includes('topology/impact/')) return Promise.resolve({ data: mockImpact });
    return Promise.resolve({ data: {} });
  });
}

beforeEach(() => {
  jest.clearAllMocks();
  localStorage.setItem('token', 'test-token');
});

describe('TopologyView', () => {
  test('renders SVG graph', async () => {
    setupApiSuccess();
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => {
      expect(screen.getByLabelText(/Grafo de topologia/i)).toBeInTheDocument();
    });
  });

  test('renders nodes with correct icons', async () => {
    setupApiSuccess();
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => {
      expect(screen.getByLabelText(/No: Core-Switch/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/No: Web-Server/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/No: DB-Server/i)).toBeInTheDocument();
    });
  });

  test('renders edges between nodes', async () => {
    setupApiSuccess();
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => {
      const svg = screen.getByLabelText(/Grafo de topologia/i);
      const paths = svg.querySelectorAll('path[d^="M"]');
      // At least 2 edge paths
      expect(paths.length).toBeGreaterThanOrEqual(2);
    });
  });

  test('shows impact panel on node click', async () => {
    setupApiSuccess();
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => expect(screen.getByLabelText(/No: Core-Switch/i)).toBeInTheDocument());

    await act(async () => {
      fireEvent.click(screen.getByLabelText(/No: Core-Switch/i));
    });
    await waitFor(() => {
      expect(screen.getByText(/Blast Radius/i)).toBeInTheDocument();
    });
  });

  test('handles empty topology', async () => {
    api.get.mockImplementation((url) => {
      if (url.includes('topology/graph')) return Promise.resolve({ data: { nodes: [], edges: [] } });
      return Promise.resolve({ data: {} });
    });
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => {
      expect(screen.getByText(/Topologia nao configurada/i)).toBeInTheDocument();
    });
  });

  test('handles loading state', () => {
    api.get.mockImplementation(() => new Promise(() => {}));
    render(<TopologyView />);
    expect(screen.getByText(/Carregando topologia/i)).toBeInTheDocument();
  });
});
