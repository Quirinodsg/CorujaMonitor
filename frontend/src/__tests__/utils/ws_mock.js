/**
 * WebSocket mock utilities for testing realtime features.
 */

export class MockWS {
  constructor() {
    this.instances = [];
    this._original = global.WebSocket;
  }

  /** Get the latest WS instance created */
  get latest() {
    return this.instances[this.instances.length - 1] || null;
  }

  /** Get all WS instances */
  get all() {
    return this.instances;
  }

  /** Install mock — call in beforeEach */
  install() {
    const self = this;
    this.instances = [];
    global.WebSocket = class extends global.WebSocket {
      constructor(url) {
        super(url);
        self.instances.push(this);
      }
    };
    // Copy static constants
    global.WebSocket.CONNECTING = 0;
    global.WebSocket.OPEN = 1;
    global.WebSocket.CLOSING = 2;
    global.WebSocket.CLOSED = 3;
    return this;
  }

  /** Restore original — call in afterEach */
  restore() {
    global.WebSocket = this._original;
    this.instances = [];
  }

  /** Send a message to the latest WS instance */
  sendMessage(data) {
    const ws = this.latest;
    if (ws) ws._simulateMessage(data);
  }

  /** Send multiple messages in burst */
  sendBurst(messages) {
    const ws = this.latest;
    if (!ws) return;
    messages.forEach(msg => ws._simulateMessage(msg));
  }

  /** Simulate disconnect on latest instance */
  disconnect() {
    const ws = this.latest;
    if (ws) ws._simulateDisconnect();
  }

  /** Simulate error on latest instance */
  triggerError() {
    const ws = this.latest;
    if (ws) ws._simulateError();
  }

  /** Simulate reconnect: disconnect then wait for new instance */
  async reconnect(delayMs = 100) {
    this.disconnect();
    return new Promise(resolve => setTimeout(() => resolve(this.latest), delayMs));
  }
}

/**
 * Create a burst of observability_update messages
 */
export function createObservabilityBurst(count = 100) {
  return Array.from({ length: count }, (_, i) => ({
    type: 'observability_update',
    health_score: 50 + Math.floor(Math.random() * 50),
    sensors_ok: 100 + i,
    sensors_critical: Math.floor(Math.random() * 5),
    sensors_total: 120 + i,
  }));
}

export default MockWS;


// Dummy test so Jest doesn't fail when collecting this file
test('utility module loads', () => { expect(true).toBe(true); });
