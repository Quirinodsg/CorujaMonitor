/**
 * MSW handlers for all API endpoints used by frontend components.
 * Uses MSW v2 syntax.
 */
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import {
  generateHealthScore,
  generateImpactMap,
  generateAlerts,
  generateTopologyGraph,
  generateServers,
  generateSensors,
  generateMetrics,
  generatePipelineStatus,
} from './event_gen';

// Default successful handlers
export const handlers = [
  // Observability
  http.get('/api/v1/observability/health-score', () => {
    return HttpResponse.json(generateHealthScore());
  }),

  http.get('/api/v1/observability/impact-map', () => {
    return HttpResponse.json({ nodes: generateImpactMap(5) });
  }),

  // Alerts
  http.get('/api/v1/alerts/intelligent', ({ request }) => {
    const url = new URL(request.url);
    const severity = url.searchParams.get('severity');
    const status = url.searchParams.get('status');
    let alerts = generateAlerts(10);
    if (severity) alerts = alerts.filter(a => a.severity === severity);
    if (status) alerts = alerts.filter(a => a.status === status);
    return HttpResponse.json({ alerts });
  }),

  http.get('/api/v1/alerts/intelligent/:id/root-cause', ({ params }) => {
    return HttpResponse.json({
      root_cause: 'High CPU usage on database server causing cascading failures',
      affected_hosts: ['db-primary', 'app-server-1', 'app-server-2'],
      confidence: 0.92,
    });
  }),

  http.post('/api/v1/alerts/intelligent/:id/acknowledge', () => {
    return HttpResponse.json({ status: 'acknowledged' });
  }),

  http.post('/api/v1/alerts/intelligent/:id/resolve', () => {
    return HttpResponse.json({ status: 'resolved' });
  }),

  http.delete('/api/v1/alerts/intelligent/:id', () => {
    return HttpResponse.json({ deleted: true });
  }),

  // Topology
  http.get('/api/v1/topology/graph', () => {
    return HttpResponse.json(generateTopologyGraph(8));
  }),

  http.get('/api/v1/topology/impact/:id', ({ params }) => {
    return HttpResponse.json({
      total_impact: 3,
      affected_hosts: ['host-a', 'host-b', 'host-c'],
      depends_on: ['core-switch'],
      all_affected: ['host-a', 'host-b', 'host-c'],
      edge_count: 5,
    });
  }),

  http.post('/api/v1/topology/sync-from-servers', () => {
    return HttpResponse.json({ message: 'Sync concluido', created: 5, updated: 2 });
  }),

  // Servers & Sensors
  http.get('/api/v1/servers', () => {
    return HttpResponse.json(generateServers(5));
  }),

  http.get('/api/v1/sensors', ({ request }) => {
    const url = new URL(request.url);
    const serverId = url.searchParams.get('server_id');
    return HttpResponse.json(generateSensors(8, serverId));
  }),

  // Metrics
  http.get('/api/v1/metrics', ({ request }) => {
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '50');
    return HttpResponse.json(generateMetrics(Math.min(limit, 200)));
  }),

  // AIOps Pipeline
  http.get('/api/v1/aiops-pipeline/status', () => {
    return HttpResponse.json(generatePipelineStatus());
  }),

  http.get('/api/v1/aiops-pipeline/runs', () => {
    return HttpResponse.json({
      runs: [
        {
          run_id: 'run-abc-123-def-456',
          agents: ['AnomalyDetection', 'Correlation', 'RootCause', 'Decision'],
          agents_success: 4,
          agents_error: 0,
          started_at: new Date().toISOString(),
        },
      ],
    });
  }),

  http.get('/api/v1/aiops-pipeline/logs', () => {
    return HttpResponse.json({
      logs: [
        {
          id: 'log-1',
          agent_name: 'AnomalyDetection',
          run_id: 'run-abc-123',
          status: 'success',
          output: { anomalies: 2 },
          timestamp: new Date().toISOString(),
        },
      ],
    });
  }),

  http.get('/api/v1/aiops-v3/feedback-metrics', () => {
    return HttpResponse.json({
      actions_successful: 42,
      actions_failed: 3,
      total_feedback: 45,
    });
  }),

  http.post('/api/v1/aiops-pipeline/run', () => {
    return HttpResponse.json({ run_id: 'new-run-id', status: 'started' });
  }),

  http.post('/api/v1/aiops-pipeline/simulate', () => {
    return HttpResponse.json({
      run_id: 'sim-run-id-12345678',
      events_processed: 1,
      agents_run: 5,
      agents_success: 5,
      should_alert: true,
      results: [
        { agent: 'AnomalyDetection', success: true },
        { agent: 'Correlation', success: true },
        { agent: 'RootCause', success: true },
        { agent: 'Decision', success: true },
        { agent: 'AutoRemediationAgent', success: true },
      ],
    });
  }),

  // NOC endpoints
  http.get('/api/v1/noc/global-status', () => {
    return HttpResponse.json({
      servers_ok: 45,
      servers_warning: 3,
      servers_critical: 1,
      availability: '99.8',
      companies: [
        { id: 1, name: 'Empresa A', status: 'ok', ok: 20, warning: 1, critical: 0, availability: '99.9' },
        { id: 2, name: 'Empresa B', status: 'warning', ok: 15, warning: 2, critical: 1, availability: '98.5' },
      ],
    });
  }),

  http.get('/api/v1/noc/heatmap', () => {
    return HttpResponse.json([
      { id: 1, hostname: 'srv-web-01', status: 'ok', availability: '99.9' },
      { id: 2, hostname: 'srv-db-01', status: 'warning', availability: '93.2' },
      { id: 3, hostname: 'srv-app-01', status: 'critical', availability: '85.1' },
    ]);
  }),

  http.get('/api/v1/noc/active-incidents', () => {
    return HttpResponse.json([
      {
        id: 1,
        severity: 'critical',
        server_name: 'srv-db-01',
        description: 'CPU acima de 95%',
        created_at: new Date().toISOString(),
        duration: '15min',
      },
    ]);
  }),

  http.get('/api/v1/noc/kpis', () => {
    return HttpResponse.json({ mttr: '12', mtbf: '800', sla: '99.97', incidents_24h: '8' });
  }),

  // Standalone sensors & batch metrics for NOC datacenter
  http.get('/api/v1/sensors/standalone', () => {
    return HttpResponse.json([]);
  }),

  http.get('/api/v1/metrics/latest/batch', () => {
    return HttpResponse.json({});
  }),

  http.get('/api/v1/dashboard/network-assets-status', () => {
    return HttpResponse.json({});
  }),
];

// Create MSW server
export const server = setupServer(...handlers);

// Error handler factories
export function createErrorHandler(path, statusCode = 500) {
  return http.get(path, () => {
    return HttpResponse.json({ error: 'Internal Server Error' }, { status: statusCode });
  });
}

export function createTimeoutHandler(path) {
  return http.get(path, async () => {
    await new Promise(resolve => setTimeout(resolve, 60000));
    return HttpResponse.json({});
  });
}

export function createNetworkErrorHandler(path) {
  return http.get(path, () => {
    return HttpResponse.error();
  });
}

export { http, HttpResponse };
