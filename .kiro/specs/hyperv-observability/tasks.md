# Implementation Plan: Hyper-V Observability Dashboard

## Overview

Backend-first implementation: database migration → SQLAlchemy models → health/finops engines → REST API router → WebSocket → probe collector → React frontend → sidebar/layout integration → tests. Each task builds incrementally so there is no orphaned code.

## Tasks

- [x] 1. Database migration and SQLAlchemy models
  - [x] 1.1 Create database migration script `api/migrate_hyperv.py`
    - Create the four tables: `hyperv_hosts`, `hyperv_vms`, `hyperv_metrics`, `hyperv_finops_recommendations`
    - Include all columns, constraints, foreign keys, and defaults as specified in the design schema
    - Create indexes `idx_hyperv_metrics_host_ts` on (host_id, timestamp) and `idx_hyperv_metrics_vm_ts` on (vm_id, timestamp)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 1.2 Add SQLAlchemy models to `api/models.py`
    - Append `HyperVHost`, `HyperVVM`, `HyperVMetric`, and `HyperVFinOpsRecommendation` models
    - Include UUID primary keys, relationships (`HyperVHost.vms ↔ HyperVVM.host`), and index definitions
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 1.3 Create Pydantic response schemas `api/schemas/hyperv.py`
    - Define `HyperVOverview`, `HyperVHostResponse`, `HyperVVMResponse`, `FinOpsRecommendation`, `AISuggestion`, `HeatmapCell`, `HeatmapResponse` schemas
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 8.2, 9.2_

- [x] 2. Health Score engine
  - [x] 2.1 Implement `api/services/hyperv_health.py`
    - Create `compute_health_score(cpu_percent, memory_percent, storage_percent, vm_ratio, alert_count) -> float`
    - Implement weighted formula: CPU 0.30, Memory 0.25, Storage 0.20, VM ratio 0.15, Alerts 0.10
    - Apply critical penalty for CPU > 90% (cap CPU component at 10) and memory > 95% (cap memory component at 5)
    - Clamp final result to [0, 100]
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 2.2 Write property test for Health Score Range Invariant
    - **Property 1: Health Score Range Invariant**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 11.2**

- [x] 3. FinOps engine
  - [x] 3.1 Implement `api/services/hyperv_finops.py`
    - Create `HyperVFinOpsEngine` class with methods: `detect_overprovisioned`, `detect_idle`, `estimate_vm_cost`, `compute_density`, `generate_recommendations`
    - Overprovisioned: avg CPU < 20% for 7 consecutive days
    - Idle: avg CPU < 5% for 30 consecutive minutes
    - Cost: `vcpus × rate_vcpu + memory_gb × rate_mem + storage_gb × rate_storage`
    - Density: VMs/host, vCPU overcommit ratio, memory overcommit ratio
    - Recommendations with categories: overprovisioned, idle, right-size, rebalance
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ]* 3.2 Write property test for FinOps Overprovisioned Detection
    - **Property 9: FinOps Overprovisioned Detection**
    - **Validates: Requirements 7.1**

  - [ ]* 3.3 Write property test for FinOps Idle Detection
    - **Property 10: FinOps Idle Detection**
    - **Validates: Requirements 7.2**

  - [ ]* 3.4 Write property test for FinOps Cost Estimation
    - **Property 11: FinOps Cost Estimation**
    - **Validates: Requirements 7.3**

  - [ ]* 3.5 Write property test for FinOps Density Computation
    - **Property 12: FinOps Density Computation**
    - **Validates: Requirements 7.4**

  - [ ]* 3.6 Write property test for Recommendation Completeness
    - **Property 13: Recommendation Completeness**
    - **Validates: Requirements 7.5, 7.6**

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Hyper-V REST API router
  - [x] 5.1 Implement `api/routers/hyperv.py`
    - Create FastAPI router with prefix `/api/v1/hyperv`
    - Implement 7 endpoints: `GET /overview`, `GET /hosts`, `GET /hosts/{host_id}/vms`, `GET /vms`, `GET /finops/recommendations`, `GET /heatmap`, `GET /ai/suggestions`
    - Support query parameters: `period` (24h, 7d, 30d), `host`, `status` (running, stopped, paused, saved)
    - Return HTTP 404 with `{"error": "..."}` for non-existent host_id
    - Integrate `compute_health_score` for host health scores
    - Integrate `HyperVFinOpsEngine` for FinOps endpoint
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 6.1, 6.5, 7.5, 8.1, 8.2, 9.2_

  - [ ]* 5.2 Write property test for API Filter Correctness
    - **Property 4: API Filter Correctness**
    - **Validates: Requirements 2.6, 2.7, 2.8**

  - [ ]* 5.3 Write property test for Host-VM Ownership
    - **Property 5: Host-VM Ownership**
    - **Validates: Requirements 2.3**

  - [ ]* 5.4 Write property test for Top Consumers Sorting
    - **Property 8: Top Consumers Sorting**
    - **Validates: Requirements 4.5**

  - [ ]* 5.5 Write property test for Hotspot Detection
    - **Property 14: Hotspot Detection**
    - **Validates: Requirements 8.1**

- [x] 6. Hyper-V WebSocket
  - [x] 6.1 Implement `api/routers/hyperv_ws.py`
    - Create WebSocket endpoint at `/api/v1/ws/hyperv`
    - Implement connection manager with per-client subscription filters (`host_id`, `status`)
    - Broadcast messages with structure: `{"type": "...", "timestamp": "...", "data": {...}}`
    - Handle subscribe action: `{"action": "subscribe", "filters": {...}}`
    - Implement ping/pong for idle connections (60s timeout)
    - Clean up disconnected clients
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ]* 6.2 Write property test for WebSocket Message Structure
    - **Property 6: WebSocket Message Structure**
    - **Validates: Requirements 3.3**

  - [ ]* 6.3 Write property test for WebSocket Subscription Filtering
    - **Property 7: WebSocket Subscription Filtering**
    - **Validates: Requirements 3.4**

- [x] 7. Register routers in `api/main.py`
  - Import and register `hyperv.router` and `hyperv_ws.router` via `app.include_router()`
  - _Requirements: 2.1, 3.1_

- [ ] 8. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Hyper-V WMI Collector
  - [x] 9.1 Implement `probe/collectors/hyperv_wmi_collector.py`
    - Create `HyperVWMICollector` class using existing `WMIEngine`/`wmi_pool` infrastructure
    - Implement `collect_host(host_config)` with 10s timeout per host
    - Query `Msvm_ComputerSystem` for VM list and power states
    - Query `Msvm_SummaryInformation` for CPU, memory, uptime per VM
    - Query `Win32_ComputerSystem` for host physical resources
    - Implement `collect_all()` that continues on failure, marks failed hosts as "unreachable"
    - Send payload to Redis stream `metrics_stream`
    - Pre-configure hosts SRVHVSPRD010 (192.168.31.110) and SRVHVSPRD011 (192.168.31.111)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 12.1, 12.2, 12.3, 12.4_

  - [ ]* 9.2 Write property test for Collector Payload Completeness
    - **Property 2: Collector Payload Completeness**
    - **Validates: Requirements 1.4**

  - [ ]* 9.3 Write property test for Collector Error Resilience
    - **Property 3: Collector Error Resilience**
    - **Validates: Requirements 1.5**

- [ ] 10. Checkpoint - Ensure all backend and probe tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. HyperV Dashboard React component
  - [x] 11.1 Create `frontend/src/components/HyperVDashboard.js` and `HyperVDashboard.css`
    - Implement main `HyperVDashboard` component with state management
    - Header section: 5 summary cards (Total Hosts, Total VMs, VMs Rodando, Alertas Ativos, Health Score)
    - 3 gauge charts (CPU%, Memory%, Storage%)
    - Filter controls (period: 24h/7d/30d, host dropdown, VM status dropdown)
    - Host table with columns: Nome, Status, CPU%, Memória%, Storage%, Latência WMI, VMs, Health Score
    - Expandable host rows showing VM list on click
    - Top Consumers section: top 5 by CPU, top 5 by Memory
    - Heatmap visualization with color gradient (green 0-50%, yellow 50-75%, red 75-100%)
    - FinOps recommendations section
    - AI suggestions section with "Recomendado" badge for confidence > 0.8
    - WebSocket connection for real-time updates with auto-reconnect (exponential backoff)
    - All labels in pt-BR, using existing dark theme (`design-system.css`, `global-dark-override.css`)
    - Fetch data from all 7 REST endpoints
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 8.3, 9.3_

  - [ ]* 11.2 Write property test for Heatmap Color Mapping
    - **Property 15: Heatmap Color Mapping**
    - **Validates: Requirements 8.3**

  - [ ]* 11.3 Write property test for AI Suggestion Completeness
    - **Property 16: AI Suggestion Completeness**
    - **Validates: Requirements 9.1, 9.2**

  - [ ]* 11.4 Write property test for Recomendado Badge Threshold
    - **Property 17: Recomendado Badge Threshold**
    - **Validates: Requirements 9.3**

- [x] 12. Sidebar and MainLayout integration
  - [x] 12.1 Add Hyper-V menu item to `frontend/src/components/Sidebar.js`
    - Add `{ id: "hyperv", icon: "🖥️", label: "Hyper-V" }` to the "Observabilidade" category in the `CATS` array
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 12.2 Add Hyper-V case to `frontend/src/components/MainLayout.js`
    - Import `HyperVDashboard` and add `case 'hyperv': return <HyperVDashboard />;` to the page rendering switch
    - _Requirements: 5.2_

- [ ] 13. Unit tests
  - [ ] 13.1 Create `tests/test_hyperv_module.py`
    - Test `compute_health_score` with known inputs and expected outputs
    - Test critical penalties (CPU > 90%, memory > 95%)
    - Test FinOps overprovisioned detection with 7-day sample data
    - Test FinOps idle detection with 30-minute sample data
    - Test FinOps cost estimation with known rates
    - Test API endpoint response structure (mocked DB)
    - Test HTTP 404 for non-existent host_id
    - Test heatmap color mapping boundary values (0, 49, 50, 74, 75, 100)
    - Test WebSocket message structure validation
    - Test collector payload structure with mocked WMI data
    - Test hotspot detection with boundary time series
    - _Requirements: 11.1, 11.4, 11.5, 11.6_

- [ ] 14. Property-based tests file setup
  - [ ] 14.1 Create `tests/test_hyperv_pbt.py` with all 17 property tests
    - Each property test tagged with comment referencing design property number
    - Use `hypothesis` library with `@settings(max_examples=100)`
    - Properties 1–17 as individual test functions covering: Health Score Range, Collector Payload Completeness, Collector Error Resilience, API Filter Correctness, Host-VM Ownership, WebSocket Message Structure, WebSocket Subscription Filtering, Top Consumers Sorting, FinOps Overprovisioned, FinOps Idle, FinOps Cost Estimation, FinOps Density, Recommendation Completeness, Hotspot Detection, Heatmap Color Mapping, AI Suggestion Completeness, Recomendado Badge Threshold
    - _Requirements: 11.2_

- [ ] 15. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Backend-first approach ensures APIs are ready before frontend consumes them
