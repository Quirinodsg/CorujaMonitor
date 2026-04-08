/**
 * Bulk test data generators for Coruja Monitor v3.0 frontend tests.
 */

export function generateHealthScore(overrides = {}) {
  return {
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
    ...overrides,
  };
}

export function generateImpactMap(count = 5) {
  return Array.from({ length: count }, (_, i) => ({
    id: `node-${i + 1}`,
    name: `Server-${String.fromCharCode(65 + i)}`,
    ip: `192.168.1.${10 + i}`,
    severity: i === 0 ? 'critical' : i < 3 ? 'warning' : 'ok',
    critical_sensors: i === 0 ? 3 : 0,
    warning_sensors: i < 3 ? 2 : 0,
  }));
}

export function generateAlerts(count = 10, overrides = {}) {
  const severities = ['critical', 'warning', 'info'];
  const statuses = ['open', 'acknowledged', 'resolved'];
  return Array.from({ length: count }, (_, i) => ({
    id: `alert-${i + 1}`,
    title: `Alert ${i + 1}: ${i % 3 === 0 ? 'CPU spike' : i % 3 === 1 ? 'Memory pressure' : 'Disk full'}`,
    severity: severities[i % 3],
    status: statuses[i % 3],
    confidence: 0.7 + Math.random() * 0.3,
    root_cause: i % 2 === 0 ? 'Database connection pool exhaustion' : null,
    created_at: new Date(Date.now() - i * 3600000).toISOString(),
    resolved_at: statuses[i % 3] === 'resolved' ? new Date().toISOString() : null,
    ...overrides,
  }));
}

export function generateTopologyGraph(nodeCount = 8) {
  const types = ['server', 'switch', 'router', 'firewall', 'database', 'ap'];
  const statuses = ['ok', 'warning', 'critical', 'unknown'];
  const nodes = Array.from({ length: nodeCount }, (_, i) => ({
    id: `topo-node-${i + 1}`,
    name: `Device-${String.fromCharCode(65 + i)}`,
    type: types[i % types.length],
    status: i < nodeCount - 2 ? 'ok' : statuses[i % statuses.length],
    metadata: {
      ip: `10.0.0.${i + 1}`,
      device_type: types[i % types.length],
      hostname: `device-${String.fromCharCode(97 + i)}`,
    },
  }));
  const edges = [];
  for (let i = 1; i < nodeCount; i++) {
    edges.push({
      source: nodes[0].id,
      target: nodes[i].id,
      type: i % 2 === 0 ? 'dependency' : 'infrastructure',
    });
  }
  return { nodes, edges };
}

export function generateServers(count = 5) {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `Server-${i + 1}`,
    hostname: `srv-${i + 1}.local`,
    ip_address: `192.168.10.${i + 1}`,
    status: i < count - 1 ? 'ok' : 'warning',
    device_type: 'server',
  }));
}

export function generateSensors(count = 8, serverId = null) {
  const types = ['cpu', 'memory', 'disk', 'network', 'ping', 'http', 'snmp', 'process'];
  return Array.from({ length: count }, (_, i) => ({
    id: 100 + i,
    name: `Sensor ${types[i % types.length]} #${i + 1}`,
    sensor_type: types[i % types.length],
    server_id: serverId || 1,
    status: 'ok',
    category: i % 2 === 0 ? 'system' : 'network',
  }));
}

export function generateMetrics(count = 50) {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    sensor_id: 100 + (i % 8),
    value: 20 + Math.random() * 60,
    unit: '%',
    status: 'ok',
    timestamp: new Date(Date.now() - i * 60000).toISOString(),
  }));
}

export function generatePipelineStatus() {
  return {
    total_runs: 156,
    total_intelligent_alerts: 42,
    total_remediation_actions: 18,
    circuit_breaker: 'closed',
    last_run: new Date().toISOString(),
  };
}

// Bulk generators for performance tests
export function generateBulkMetrics(count = 1000) {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    sensor_id: 100 + (i % 20),
    sensor_type: ['cpu', 'memory', 'disk', 'network'][i % 4],
    sensor_name: `Sensor-${i % 20}`,
    value: Math.random() * 100,
    unit: '%',
    status: i % 50 === 0 ? 'critical' : i % 10 === 0 ? 'warning' : 'ok',
    timestamp: new Date(Date.now() - i * 30000).toISOString(),
  }));
}

export function generateBulkAlerts(count = 500) {
  const severities = ['critical', 'warning', 'info'];
  return Array.from({ length: count }, (_, i) => ({
    id: `bulk-alert-${i + 1}`,
    title: `Bulk Alert ${i + 1}`,
    severity: severities[i % 3],
    status: i % 4 === 0 ? 'resolved' : i % 3 === 0 ? 'acknowledged' : 'open',
    confidence: 0.5 + Math.random() * 0.5,
    root_cause: i % 3 === 0 ? `Root cause for alert ${i + 1}` : null,
    created_at: new Date(Date.now() - i * 60000).toISOString(),
  }));
}

export function generateBulkTopology(nodeCount = 50) {
  const nodes = Array.from({ length: nodeCount }, (_, i) => ({
    id: `bulk-node-${i}`,
    name: `Node-${i}`,
    type: ['server', 'switch', 'router'][i % 3],
    status: i % 10 === 0 ? 'critical' : 'ok',
    metadata: { ip: `10.0.${Math.floor(i / 256)}.${i % 256}`, device_type: 'server' },
  }));
  const edges = [];
  for (let i = 1; i < nodeCount; i++) {
    edges.push({ source: nodes[Math.floor(i / 3)].id, target: nodes[i].id, type: 'dependency' });
  }
  return { nodes, edges };
}

export function generateAnomalyEvents(count = 100) {
  return Array.from({ length: count }, (_, i) => ({
    id: `anomaly-${i}`,
    type: 'anomaly',
    severity: i % 5 === 0 ? 'critical' : 'warning',
    metric: ['cpu', 'memory', 'disk', 'latency'][i % 4],
    value: 80 + Math.random() * 20,
    threshold: 80,
    host: `host-${i % 10}`,
    timestamp: new Date(Date.now() - i * 30000).toISOString(),
  }));
}
