# Requirements Document

## Introduction

The Hyper-V Observability Dashboard is a new module for the Coruja Monitor enterprise platform. It provides dedicated monitoring, visualization, and FinOps analysis for Microsoft Hyper-V virtualization hosts and their virtual machines. The module extends the existing WMI-based probe infrastructure to collect Hyper-V-specific metrics (via `Msvm_ComputerSystem`, `Msvm_SummaryInformation`, `Win32_ComputerSystem`), exposes REST and WebSocket APIs, and renders a real-time React dashboard with health scoring, resource gauges, top consumers, heatmaps, and AI-driven optimization recommendations. The UI follows the existing dark theme and pt-BR localization conventions.

## Glossary

- **HyperV_Collector**: The probe-side component that queries Hyper-V WMI classes (`Msvm_ComputerSystem`, `Msvm_SummaryInformation`, `Win32_ComputerSystem`) on target hosts and produces structured metric payloads.
- **HyperV_API**: The FastAPI router (`/api/v1/hyperv/...`) that serves Hyper-V overview, host, VM, and FinOps data to the frontend.
- **HyperV_WebSocket**: The WebSocket endpoint (`/api/v1/ws/hyperv`) that pushes real-time Hyper-V metric updates to connected clients.
- **HyperV_Dashboard**: The React component (`HyperVObservabilityDashboard`) that renders the Hyper-V monitoring UI.
- **Health_Score**: A numeric value from 0 to 100 representing the overall health of a Hyper-V host, computed from CPU, memory, storage utilization, VM state ratios, and alert counts.
- **FinOps_Engine**: The backend logic that analyzes historical Hyper-V metrics to detect overprovisioning, idle VMs, estimate per-VM costs, and compute host density.
- **Alert_Engine**: The existing Coruja alert engine (`alert_engine/engine.py`) that processes events and generates alerts.
- **AI_Agent**: The existing AI subsystem (`ai_agents/`) that provides root-cause analysis, anomaly detection, and optimization suggestions.
- **Sidebar**: The React navigation component that organizes menu items into categories.
- **Heatmap**: A visual grid showing resource utilization intensity across hosts and time periods.
- **Hotspot**: A host or VM that exceeds defined utilization thresholds, flagged for operator attention.
- **VM**: A Hyper-V virtual machine managed by a monitored host.
- **Host**: A physical Windows Server running the Hyper-V role.

## Requirements

### Requirement 1: Hyper-V WMI Data Collection

**User Story:** As a platform operator, I want the probe to collect Hyper-V metrics from target hosts via WMI, so that the system has the raw data needed for monitoring and analysis.

#### Acceptance Criteria

1. WHEN a collection cycle starts, THE HyperV_Collector SHALL query `Msvm_ComputerSystem` on each configured Hyper-V host to retrieve the list of virtual machines and their power states.
2. WHEN a collection cycle starts, THE HyperV_Collector SHALL query `Msvm_SummaryInformation` on each configured Hyper-V host to retrieve CPU usage, memory usage, and uptime for each VM.
3. WHEN a collection cycle starts, THE HyperV_Collector SHALL query `Win32_ComputerSystem` on each configured Hyper-V host to retrieve total physical memory and processor count of the host.
4. THE HyperV_Collector SHALL produce a structured metric payload containing host-level aggregates (total CPU%, total memory%, total storage%, VM count, running VM count) and per-VM details (name, state, CPU%, memory MB, disk bytes).
5. IF a WMI query fails or times out, THEN THE HyperV_Collector SHALL log the error with host IP and query class, mark the host status as "unreachable", and continue collecting from remaining hosts.
6. THE HyperV_Collector SHALL complete a full collection cycle for a single host within 10 seconds.
7. WHEN metrics are collected, THE HyperV_Collector SHALL send the payload to the API via the existing probe-to-API ingestion pipeline (Redis stream `metrics_stream`).

### Requirement 2: Hyper-V REST API Endpoints

**User Story:** As a frontend developer, I want REST endpoints that serve Hyper-V data, so that the dashboard can fetch overview, host, VM, and FinOps information.

#### Acceptance Criteria

1. THE HyperV_API SHALL expose `GET /api/v1/hyperv/overview` returning total hosts, total VMs, running VMs, active alert count, and aggregate Health_Score.
2. THE HyperV_API SHALL expose `GET /api/v1/hyperv/hosts` returning a list of Hyper-V hosts with name, IP, status, CPU%, memory%, storage%, WMI latency in milliseconds, VM count, and Health_Score.
3. THE HyperV_API SHALL expose `GET /api/v1/hyperv/hosts/{host_id}/vms` returning the list of VMs on a specific host with name, state, CPU%, memory MB, disk bytes, and uptime.
4. THE HyperV_API SHALL expose `GET /api/v1/hyperv/vms` returning all VMs across all hosts with the same fields as criterion 3 plus the parent host name.
5. THE HyperV_API SHALL expose `GET /api/v1/hyperv/finops/recommendations` returning FinOps analysis results (overprovisioned VMs, idle VMs, cost estimates, density metrics).
6. WHEN a `period` query parameter is provided (values: `24h`, `7d`, `30d`), THE HyperV_API SHALL filter time-series data to the specified period.
7. WHEN a `host` query parameter is provided, THE HyperV_API SHALL filter results to the specified host.
8. WHEN a `status` query parameter is provided (values: `running`, `stopped`, `paused`, `saved`), THE HyperV_API SHALL filter VM results to the specified state.
9. IF a requested host_id does not exist, THEN THE HyperV_API SHALL return HTTP 404 with a JSON body containing an `error` field.
10. THE HyperV_API SHALL respond to all endpoints within 500 milliseconds under normal load (up to 50 concurrent requests).

### Requirement 3: Hyper-V WebSocket Real-Time Updates

**User Story:** As a NOC operator, I want real-time Hyper-V metric updates pushed to my dashboard, so that I can react to changes without manual refresh.

#### Acceptance Criteria

1. THE HyperV_WebSocket SHALL accept connections at `/api/v1/ws/hyperv`.
2. WHEN new Hyper-V metrics are ingested, THE HyperV_WebSocket SHALL broadcast an update message to all connected clients within 5 seconds of data arrival.
3. THE HyperV_WebSocket SHALL send messages in JSON format containing `type` ("overview_update", "host_update", "vm_update", "alert_update"), `timestamp`, and `data` fields.
4. WHEN a client sends a JSON message with `action: "subscribe"` and a `filters` object (containing optional `host_id` and `status` fields), THE HyperV_WebSocket SHALL deliver only messages matching the subscription filters to that client.
5. IF a WebSocket connection is idle for more than 60 seconds without a ping, THEN THE HyperV_WebSocket SHALL send a ping frame to verify connectivity.
6. IF a client disconnects, THEN THE HyperV_WebSocket SHALL remove the client from the broadcast list and release associated resources.

### Requirement 4: Hyper-V Dashboard UI

**User Story:** As a NOC operator, I want a dedicated Hyper-V dashboard with visual indicators, so that I can monitor the virtualization infrastructure at a glance.

#### Acceptance Criteria

1. THE HyperV_Dashboard SHALL display a header section with five summary cards: "Total Hosts", "Total VMs", "VMs Rodando", "Alertas Ativos", and "Health Score".
2. THE HyperV_Dashboard SHALL display three gauge charts showing aggregate CPU%, Memory%, and Storage% utilization.
3. THE HyperV_Dashboard SHALL display a host list table with columns: Nome, Status, CPU%, Memória%, Storage%, Latência WMI, VMs, and Health Score.
4. WHEN a user clicks a host row in the table, THE HyperV_Dashboard SHALL expand or navigate to show the list of VMs on that host.
5. THE HyperV_Dashboard SHALL display a "Top Consumers" section with two ranked lists: top 5 VMs by CPU usage and top 5 VMs by memory usage.
6. THE HyperV_Dashboard SHALL display a heatmap visualization showing resource utilization intensity across hosts over the selected time period.
7. THE HyperV_Dashboard SHALL apply the existing Coruja dark theme (`design-system.css`, `global-dark-override.css`) and use pt-BR labels for all UI text.
8. THE HyperV_Dashboard SHALL provide filter controls for time period (24h, 7d, 30d), host selection, and VM status.
9. WHEN filters are changed, THE HyperV_Dashboard SHALL update all displayed data within 2 seconds.
10. THE HyperV_Dashboard SHALL update displayed metrics in real time via the HyperV_WebSocket connection without requiring page refresh.

### Requirement 5: Sidebar Navigation Integration

**User Story:** As a user, I want to access the Hyper-V dashboard from the sidebar menu, so that I can navigate to it consistently with other modules.

#### Acceptance Criteria

1. THE Sidebar SHALL include a "Hyper-V" menu item within the "Observabilidade" category, using a server/VM icon and the label "Hyper-V".
2. WHEN a user clicks the "Hyper-V" menu item, THE Sidebar SHALL navigate to the HyperV_Dashboard page.
3. WHILE the user is on the HyperV_Dashboard page, THE Sidebar SHALL highlight the "Hyper-V" menu item as active.

### Requirement 6: Health Score Computation

**User Story:** As a platform operator, I want a health score per Hyper-V host, so that I can quickly identify hosts that need attention.

#### Acceptance Criteria

1. THE HyperV_API SHALL compute a Health_Score for each host as a numeric value between 0 and 100.
2. THE HyperV_API SHALL calculate Health_Score using weighted factors: CPU utilization (weight 0.30), memory utilization (weight 0.25), storage utilization (weight 0.20), ratio of running VMs to total VMs (weight 0.15), and active alert count penalty (weight 0.10).
3. WHEN CPU utilization exceeds 90%, THE HyperV_API SHALL apply a critical penalty reducing the CPU component to a maximum score of 10 out of 30.
4. WHEN memory utilization exceeds 95%, THE HyperV_API SHALL apply a critical penalty reducing the memory component to a maximum score of 5 out of 25.
5. THE HyperV_API SHALL recalculate Health_Score on every data refresh cycle.

### Requirement 7: FinOps On-Premise Analysis

**User Story:** As an infrastructure manager, I want FinOps recommendations for my Hyper-V environment, so that I can optimize resource usage and reduce waste.

#### Acceptance Criteria

1. THE FinOps_Engine SHALL detect overprovisioned VMs where average CPU utilization remains below 20% for 7 consecutive days.
2. THE FinOps_Engine SHALL detect idle VMs where average CPU utilization remains below 5% for 30 consecutive minutes.
3. THE FinOps_Engine SHALL estimate a monthly cost per VM based on allocated vCPUs, allocated memory GB, and allocated storage GB using configurable unit rates.
4. THE FinOps_Engine SHALL compute host density metrics: VMs per host, vCPU overcommit ratio, and memory overcommit ratio.
5. THE FinOps_Engine SHALL generate recommendations with categories: "overprovisioned", "idle", "right-size", and "rebalance".
6. WHEN a recommendation is generated, THE FinOps_Engine SHALL include the VM name, host name, current resource allocation, suggested action, and estimated monthly savings.

### Requirement 8: Hotspot Detection and Heatmap

**User Story:** As a NOC operator, I want to see resource hotspots visually, so that I can identify overloaded hosts before they cause incidents.

#### Acceptance Criteria

1. THE HyperV_API SHALL identify hotspot hosts where CPU exceeds 85% or memory exceeds 90% for more than 5 consecutive minutes.
2. THE HyperV_API SHALL expose heatmap data via `GET /api/v1/hyperv/heatmap` returning a time-series grid of utilization values per host, bucketed by the selected time period granularity.
3. THE HyperV_Dashboard SHALL render the heatmap using a color gradient from green (0-50% utilization) through yellow (50-75%) to red (75-100%).
4. WHEN a hotspot is detected, THE HyperV_API SHALL emit an event to the Alert_Engine with severity "warning" or "critical" based on the threshold exceeded.

### Requirement 9: AI-Driven Optimization Suggestions

**User Story:** As an infrastructure manager, I want AI-generated suggestions for VM placement and workload balancing, so that I can optimize my Hyper-V cluster proactively.

#### Acceptance Criteria

1. THE AI_Agent SHALL analyze Hyper-V metrics and generate suggestions in the categories: "move VM to less loaded host", "shutdown idle VM", and "balance cluster workload".
2. THE HyperV_API SHALL expose `GET /api/v1/hyperv/ai/suggestions` returning the list of AI-generated suggestions with category, description, affected VMs, target host, and confidence score (0.0 to 1.0).
3. WHEN a suggestion has a confidence score above 0.8, THE HyperV_Dashboard SHALL display the suggestion with a "Recomendado" badge.
4. THE AI_Agent SHALL re-evaluate suggestions on every data refresh cycle using the latest metric window.

### Requirement 10: Database Schema for Hyper-V Data

**User Story:** As a backend developer, I want dedicated database tables for Hyper-V entities, so that host, VM, and metric data is persisted and queryable.

#### Acceptance Criteria

1. THE HyperV_API SHALL store Hyper-V host records in a `hyperv_hosts` table with columns: id (UUID), hostname, ip_address, total_cpus, total_memory_gb, total_storage_gb, status, health_score, last_seen (timestamp), and created_at (timestamp).
2. THE HyperV_API SHALL store VM records in a `hyperv_vms` table with columns: id (UUID), host_id (FK to hyperv_hosts), name, state, vcpus, memory_mb, disk_bytes, cpu_percent, memory_percent, uptime_seconds, and last_updated (timestamp).
3. THE HyperV_API SHALL store time-series metrics in a `hyperv_metrics` table with columns: id, host_id (FK), vm_id (FK, nullable for host-level metrics), metric_type, value, timestamp.
4. THE HyperV_API SHALL store FinOps recommendations in a `hyperv_finops_recommendations` table with columns: id (UUID), vm_id (FK), host_id (FK), category, description, suggested_action, estimated_savings, created_at, status (active/dismissed).
5. THE HyperV_API SHALL create appropriate indexes on `hyperv_metrics(host_id, timestamp)` and `hyperv_metrics(vm_id, timestamp)` for efficient time-range queries.

### Requirement 11: Automated Test Coverage

**User Story:** As a developer, I want automated tests for the Hyper-V module, so that regressions are caught early.

#### Acceptance Criteria

1. THE test suite SHALL include unit tests in `tests/test_hyperv_module.py` covering HyperV_API endpoint responses, Health_Score computation, and FinOps_Engine detection logic.
2. THE test suite SHALL include a property-based test verifying that Health_Score output is always between 0 and 100 for any valid combination of CPU (0-100), memory (0-100), storage (0-100), VM ratio (0.0-1.0), and alert count (0-N).
3. THE test suite SHALL include integration tests verifying WebSocket message delivery within 5 seconds of metric ingestion.
4. THE test suite SHALL include tests verifying that the HyperV_API returns HTTP 404 for non-existent host_id values.
5. THE test suite SHALL include tests verifying FinOps overprovisioning detection triggers when CPU average is below 20% for 7 days of sample data.
6. THE test suite SHALL include tests verifying FinOps idle VM detection triggers when CPU average is below 5% for 30 minutes of sample data.

### Requirement 12: Configured Host Monitoring

**User Story:** As a platform operator, I want the system to monitor the two production Hyper-V hosts, so that the dashboard shows real data from day one.

#### Acceptance Criteria

1. THE HyperV_Collector SHALL be pre-configured to monitor host SRVHVSPRD010 at IP address 192.168.31.110.
2. THE HyperV_Collector SHALL be pre-configured to monitor host SRVHVSPRD011 at IP address 192.168.31.111.
3. WHEN the probe starts, THE HyperV_Collector SHALL begin collecting metrics from both configured hosts within the first collection cycle.
4. THE HyperV_Collector SHALL support adding new hosts via the existing probe configuration mechanism without code changes.
