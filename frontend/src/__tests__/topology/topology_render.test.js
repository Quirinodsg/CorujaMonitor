/**
 * Topology rendering tests.
 */
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
    { id: 'n1', name: 'Core-Router', type: 'router', status: 'ok', metadata: { ip: '10.0.0.1', device_type: 'router' } },
    { id: 'n2', name: 'Web-Server', type: 'server', status: 'ok', metadata: { ip: '10.0.0.2', device_type: 'server' } },
    { id: 'n3', name: 'DB-Primary', type: 'database', status: 'critical', metadata: { ip: '10.0.0.3', device_type: 'database' } },
    { id: 'n4', name: 'Firewall-Main', type: 'firewall', status: 'ok', metadata: { ip: '10.0.0.4', device_type: 'firewall' } },
  ],
  edges: [
    { source: 'n1', target: 'n2', type: 'infrastructure' },
    { source: 'n1', target: 'n3', type: 'dependency' },
    { source: 'n4', target: 'n1', type: 'infrastructure' },
  ],
};

function setupApi() {
  api.get.mockImplementation((url) => {
    if (url.includes('topology/graph')) return Promise.resolve({ data: mockGraph });
    if (url.includes('topology/impact/')) return Promise.resolve({
      data: { total_impact: 2, affected_hosts: ['Web-Server', 'DB-Primary'], depends_on: [], all_affected: ['n2', 'n3'], edge_count: 3 },
    });
    return Promise.resolve({ data: {} });
  });
}

beforeEach(() => {
  jest.clearAllMocks();
  localStorage.setItem('token', 'test-token');
});

describe('Topology Render', () => {
  test('renders nodes from API data', async () => {
    setupApi();
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => {
      expect(screen.getByLabelText(/No: Core-Router/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/No: Web-Server/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/No: DB-Primary/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/No: Firewall-Main/i)).toBeInTheDocument();
    });
  });

  test('renders edges between nodes', async () => {
    setupApi();
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => {
      const svg = screen.getByLabelText(/Grafo de topologia/i);
      // Edges are rendered as path elements with quadratic curves
      const edgePaths = svg.querySelectorAll('path[d^="M"]');
      expect(edgePaths.length).toBeGreaterThanOrEqual(3);
    });
  });

  test('different node types have different icons', async () => {
    setupApi();
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => {
      const svg = screen.getByLabelText(/Grafo de topologia/i);
      // Each node group has an inner SVG with a path for the icon
      const nodeGroups = svg.querySelectorAll('.topo-node');
      expect(nodeGroups.length).toBe(4);

      // Verify type labels are shown below nodes
      expect(screen.getByText('router')).toBeInTheDocument();
      expect(screen.getByText('server')).toBeInTheDocument();
      expect(screen.getByText('database')).toBeInTheDocument();
      expect(screen.getByText('firewall')).toBeInTheDocument();
    });
  });

  test('impact highlight shows affected nodes', async () => {
    setupApi();
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => expect(screen.getByLabelText(/No: Core-Router/i)).toBeInTheDocument());

    await act(async () => {
      fireEvent.click(screen.getByLabelText(/No: Core-Router/i));
    });
    await waitFor(() => {
      expect(screen.getByText(/Blast Radius/i)).toBeInTheDocument();
      expect(screen.getByText(/Nós Afetados/i)).toBeInTheDocument();
    });
  });

  test('empty topology shows message', async () => {
    api.get.mockImplementation((url) => {
      if (url.includes('topology/graph')) return Promise.resolve({ data: { nodes: [], edges: [] } });
      return Promise.resolve({ data: {} });
    });
    await act(async () => { render(<TopologyView />); });
    await waitFor(() => {
      expect(screen.getByText(/Topologia nao configurada/i)).toBeInTheDocument();
    });
  });
});
