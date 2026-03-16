import React, { useState } from 'react';
import './Discovery.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Discovery() {
  const [tab, setTab] = useState('network');
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');

  // Network scan state
  const [subnet, setSubnet] = useState('192.168.1.0/24');
  const [timeout, setTimeout_] = useState(1000);

  // SNMP discovery state
  const [snmpTarget, setSnmpTarget] = useState('');
  const [community, setCommunity] = useState('public');
  const [snmpVersion, setSnmpVersion] = useState('2c');

  // WMI discovery state
  const [wmiTarget, setWmiTarget] = useState('');
  const [wmiUser, setWmiUser] = useState('');
  const [wmiPass, setWmiPass] = useState('');
  const [wmiDomain, setWmiDomain] = useState('');

  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` };

  const runNetworkScan = async () => {
    setScanning(true);
    setError('');
    setResults([]);
    try {
      const res = await fetch(`${API}/discovery/network-scan`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ subnet, timeout_ms: timeout }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResults(data.hosts || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setScanning(false);
    }
  };

  const runSnmpDiscovery = async () => {
    setScanning(true);
    setError('');
    setResults([]);
    try {
      const res = await fetch(`${API}/discovery/snmp`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ target: snmpTarget, community, version: snmpVersion }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResults(data.sensors || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setScanning(false);
    }
  };

  const runWmiDiscovery = async () => {
    setScanning(true);
    setError('');
    setResults([]);
    try {
      const res = await fetch(`${API}/discovery/wmi`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ target: wmiTarget, username: wmiUser, password: wmiPass, domain: wmiDomain }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResults(data.sensors || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setScanning(false);
    }
  };

  const addToMonitoring = async (item) => {
    try {
      await fetch(`${API}/discovery/add-sensor`, {
        method: 'POST',
        headers,
        body: JSON.stringify(item),
      });
      setResults(prev => prev.map(r => r === item ? { ...r, added: true } : r));
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="discovery-page">
      <div className="discovery-header">
        <h1>🔍 Discovery</h1>
        <p>Descubra hosts e sensores automaticamente na sua rede</p>
      </div>

      <div className="discovery-tabs">
        {[
          { id: 'network', label: '🌐 Scan de Rede' },
          { id: 'snmp', label: '📡 SNMP Discovery' },
          { id: 'wmi', label: '🖥️ WMI Discovery' },
        ].map(t => (
          <button
            key={t.id}
            className={`disc-tab ${tab === t.id ? 'active' : ''}`}
            onClick={() => { setTab(t.id); setResults([]); setError(''); }}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="discovery-body">
        {/* Network Scan */}
        {tab === 'network' && (
          <div className="disc-form">
            <div className="disc-form-row">
              <label>Subnet (CIDR)</label>
              <input value={subnet} onChange={e => setSubnet(e.target.value)} placeholder="192.168.1.0/24" />
            </div>
            <div className="disc-form-row">
              <label>Timeout (ms)</label>
              <input type="number" value={timeout} onChange={e => setTimeout_(Number(e.target.value))} min={100} max={5000} />
            </div>
            <button className="disc-btn-scan" onClick={runNetworkScan} disabled={scanning}>
              {scanning ? '⏳ Escaneando...' : '▶ Iniciar Scan'}
            </button>
          </div>
        )}

        {/* SNMP Discovery */}
        {tab === 'snmp' && (
          <div className="disc-form">
            <div className="disc-form-row">
              <label>Host / IP</label>
              <input value={snmpTarget} onChange={e => setSnmpTarget(e.target.value)} placeholder="192.168.1.1" />
            </div>
            <div className="disc-form-row">
              <label>Community</label>
              <input value={community} onChange={e => setCommunity(e.target.value)} placeholder="public" />
            </div>
            <div className="disc-form-row">
              <label>Versão SNMP</label>
              <select value={snmpVersion} onChange={e => setSnmpVersion(e.target.value)}>
                <option value="1">v1</option>
                <option value="2c">v2c</option>
                <option value="3">v3</option>
              </select>
            </div>
            <button className="disc-btn-scan" onClick={runSnmpDiscovery} disabled={scanning || !snmpTarget}>
              {scanning ? '⏳ Descobrindo...' : '▶ Iniciar Discovery SNMP'}
            </button>
          </div>
        )}

        {/* WMI Discovery */}
        {tab === 'wmi' && (
          <div className="disc-form">
            <div className="disc-form-row">
              <label>Host / IP</label>
              <input value={wmiTarget} onChange={e => setWmiTarget(e.target.value)} placeholder="192.168.1.10" />
            </div>
            <div className="disc-form-row">
              <label>Usuário</label>
              <input value={wmiUser} onChange={e => setWmiUser(e.target.value)} placeholder="DOMAIN\usuario" />
            </div>
            <div className="disc-form-row">
              <label>Senha</label>
              <input type="password" value={wmiPass} onChange={e => setWmiPass(e.target.value)} placeholder="••••••••" />
            </div>
            <div className="disc-form-row">
              <label>Domínio (opcional)</label>
              <input value={wmiDomain} onChange={e => setWmiDomain(e.target.value)} placeholder="CORP" />
            </div>
            <button className="disc-btn-scan" onClick={runWmiDiscovery} disabled={scanning || !wmiTarget}>
              {scanning ? '⏳ Descobrindo...' : '▶ Iniciar Discovery WMI'}
            </button>
          </div>
        )}

        {error && <div className="disc-error">⚠️ {error}</div>}

        {scanning && (
          <div className="disc-scanning">
            <div className="disc-spinner" />
            <span>Executando discovery...</span>
          </div>
        )}

        {results.length > 0 && (
          <div className="disc-results">
            <div className="disc-results-header">
              <span>{results.length} resultado{results.length !== 1 ? 's' : ''} encontrado{results.length !== 1 ? 's' : ''}</span>
            </div>
            <table className="disc-table">
              <thead>
                <tr>
                  {tab === 'network' && <>
                    <th>IP</th><th>Hostname</th><th>Status</th><th>Latência</th><th>Portas Abertas</th><th>Ação</th>
                  </>}
                  {tab === 'snmp' && <>
                    <th>OID</th><th>Nome</th><th>Tipo</th><th>Valor</th><th>Ação</th>
                  </>}
                  {tab === 'wmi' && <>
                    <th>Sensor</th><th>Tipo</th><th>Valor</th><th>Unidade</th><th>Ação</th>
                  </>}
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => (
                  <tr key={i}>
                    {tab === 'network' && <>
                      <td><code>{r.ip}</code></td>
                      <td>{r.hostname || '—'}</td>
                      <td><span className={`disc-badge disc-badge-${r.status === 'up' ? 'ok' : 'down'}`}>{r.status}</span></td>
                      <td>{r.latency_ms != null ? `${r.latency_ms}ms` : '—'}</td>
                      <td>{(r.open_ports || []).join(', ') || '—'}</td>
                      <td>
                        <button className="disc-btn-add" disabled={r.added} onClick={() => addToMonitoring(r)}>
                          {r.added ? '✓ Adicionado' : '+ Monitorar'}
                        </button>
                      </td>
                    </>}
                    {tab === 'snmp' && <>
                      <td><code>{r.oid}</code></td>
                      <td>{r.name}</td>
                      <td>{r.type}</td>
                      <td>{r.value}</td>
                      <td>
                        <button className="disc-btn-add" disabled={r.added} onClick={() => addToMonitoring(r)}>
                          {r.added ? '✓ Adicionado' : '+ Monitorar'}
                        </button>
                      </td>
                    </>}
                    {tab === 'wmi' && <>
                      <td>{r.name}</td>
                      <td>{r.type}</td>
                      <td>{r.value}</td>
                      <td>{r.unit}</td>
                      <td>
                        <button className="disc-btn-add" disabled={r.added} onClick={() => addToMonitoring(r)}>
                          {r.added ? '✓ Adicionado' : '+ Monitorar'}
                        </button>
                      </td>
                    </>}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!scanning && results.length === 0 && !error && (
          <div className="disc-empty">
            <div className="disc-empty-icon">🔍</div>
            <p>Configure os parâmetros e inicie o discovery</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Discovery;
