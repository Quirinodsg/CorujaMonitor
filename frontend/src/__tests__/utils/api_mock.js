/**
 * API mock helpers for Coruja Monitor v3.0 frontend tests.
 * Uses jest.mock('../../services/api') pattern instead of MSW.
 */
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

/**
 * Setup api.get mock with default successful responses for ObservabilityDashboard.
 * @param {object} api - The mocked api module default export
 * @param {object} overrides - Optional overrides for specific endpoints
 */
export function setupDashboardMocks(api, overrides = {}) {
  const healthData = overrides.health || generateHealthScore();
  const impactData = overrides.impact || { nodes: generateImpactMap(5) };
  const alertsData = overrides.alerts || { alerts: generateAlerts(10) };

  api.get.mockImplementation((url) => {
    if (url.includes('health-score')) return Promise.resolve({ data: healthData });
    if (url.includes('impact-map')) return Promise.resolve({ data: impactData });
    if (url.includes('alerts/intelligent')) return Promise.resolve({ data: alertsData });
    return Promise.resolve({ data: {} });
  });
}

/**
 * Setup global.fetch mock with default successful responses for IntelligentAlerts.
 * @param {object} overrides - Optional overrides
 * @returns {jest.Mock} The fetch mock
 */
export function setupAlertsFetchMock(overrides = {}) {
  const allAlerts = overrides.alerts || generateAlerts(10);

  const fetchMock = jest.fn().mockImplementation((url) => {
    if (url.includes('/alerts/intelligent') && !url.includes('/root-cause') && !url.includes('/acknowledge') && !url.includes('/resolve')) {
      const urlObj = new URL(url, 'http://localhost');
      const severity = urlObj.searchParams.get('severity');
      const status = urlObj.searchParams.get('status');
      let filtered = [...allAlerts];
      if (severity) filtered = filtered.filter(a => a.severity === severity);
      if (status) filtered = filtered.filter(a => a.status === status);
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ alerts: filtered }) });
    }
    if (url.includes('/root-cause')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          root_cause: overrides.rootCause || 'High CPU usage on database server causing cascading failures',
          affected_hosts: overrides.affectedHosts || ['db-primary', 'app-server-1'],
          confidence: 0.92,
        }),
      });
    }
    if (url.includes('/acknowledge')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ status: 'acknowledged' }) });
    }
    if (url.includes('/resolve')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ status: 'resolved' }) });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });

  global.fetch = fetchMock;
  return fetchMock;
}

/**
 * Setup api.get mock to return errors for all endpoints.
 * @param {object} api - The mocked api module default export
 * @param {number} statusCode - HTTP status code
 */
export function setupErrorMocks(api, statusCode = 500) {
  api.get.mockRejectedValue(new Error(`Request failed with status code ${statusCode}`));
}

/**
 * Setup api.get mock for NOC endpoints.
 * @param {object} api - The mocked api module default export
 * @param {object} overrides - Optional overrides
 */
export function setupNOCMocks(api, overrides = {}) {
  const globalData = overrides.global || {
    servers_ok: 45, servers_warning: 3, servers_critical: 1,
    availability: '99.8',
    companies: [
      { id: 1, name: 'Empresa A', status: 'ok', ok: 20, warning: 1, critical: 0, availability: '99.9' },
      { id: 2, name: 'Empresa B', status: 'warning', ok: 15, warning: 2, critical: 1, availability: '98.5' },
    ],
  };

  api.get.mockImplementation((url) => {
    if (url.includes('global-status')) return Promise.resolve({ data: globalData });
    if (url.includes('heatmap')) return Promise.resolve({ data: overrides.heatmap || [] });
    if (url.includes('active-incidents')) return Promise.resolve({ data: overrides.incidents || [] });
    if (url.includes('kpis')) return Promise.resolve({ data: overrides.kpis || { mttr: '12', mtbf: '800', sla: '99.97', incidents_24h: '8' } });
    if (url.includes('standalone')) return Promise.resolve({ data: [] });
    if (url.includes('servers')) return Promise.resolve({ data: [] });
    return Promise.resolve({ data: {} });
  });
}

/**
 * Setup global.fetch mock for AIOps pipeline endpoints.
 * @param {object} overrides - Optional overrides
 * @returns {jest.Mock} The fetch mock
 */
export function setupAIOpsFetchMock(overrides = {}) {
  const pipelineStatus = overrides.status || generatePipelineStatus();
  const runs = overrides.runs || {
    runs: [{
      run_id: 'run-abc-123-def-456',
      agents: ['AnomalyDetection', 'Correlation', 'RootCause', 'Decision'],
      agents_success: 4, agents_error: 0,
      started_at: new Date().toISOString(),
    }],
  };
  const logs = overrides.logs || {
    logs: [{
      id: 'log-1', agent_name: 'AnomalyDetection', run_id: 'run-abc-123',
      status: 'success', output: { anomalies: 2 }, timestamp: new Date().toISOString(),
    }],
  };
  const feedback = overrides.feedback || { actions_successful: 42, actions_failed: 3 };

  const fetchMock = jest.fn().mockImplementation((url) => {
    if (url.includes('pipeline/status')) return Promise.resolve({ ok: true, json: () => Promise.resolve(pipelineStatus) });
    if (url.includes('pipeline/runs')) return Promise.resolve({ ok: true, json: () => Promise.resolve(runs) });
    if (url.includes('pipeline/logs')) return Promise.resolve({ ok: true, json: () => Promise.resolve(logs) });
    if (url.includes('feedback-metrics')) return Promise.resolve({ ok: true, json: () => Promise.resolve(feedback) });
    if (url.includes('pipeline/run')) return Promise.resolve({ ok: true, json: () => Promise.resolve({ run_id: 'new-run', status: 'started' }) });
    if (url.includes('pipeline/simulate')) return Promise.resolve({ ok: true, json: () => Promise.resolve({ run_id: 'sim-run', events_processed: 1, agents_run: 5, agents_success: 5, should_alert: true, results: [] }) });
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
  });

  global.fetch = fetchMock;
  return fetchMock;
}

// Dummy test so Jest doesn't fail when collecting this file
test('utility module loads', () => { expect(true).toBe(true); });
