# Bugfix Requirements Document

## Introduction

SNMP Storage sensors (e.g., Dell EqualLogic at 192.168.31.92) added to the Coruja monitoring system remain stuck in "Aguardando" (waiting) status and never collect data. The root cause is a chain of issues across the backend probe, frontend UI, and API layer. The primary issue is that `collect_snmp_v2c()` queries 17 Linux-specific UCD-SNMP-MIB OIDs (1.3.6.1.4.1.2021.*) for ALL devices, including storage devices that don't support them. Each unsupported OID times out at 5s × 3 attempts = ~15s, totaling 255-375+ seconds of waiting for 17 OIDs. Secondary issues include the frontend `typeMap` not mapping 'storage' to 'snmp', the probe routing not explicitly handling 'storage' sensor_type, `handleTemplateSelect` not inheriting the parent category, and the API not propagating category correctly when the template defaults it.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN `_collect_snmp_standalone()` in `probe/probe_core.py` is called for any sensor (including Storage devices) THEN the system calls `collector.collect_snmp_v2c(ip, community, port)` without passing any OIDs, causing `collect_snmp_v2c()` to default to querying ALL 25 OIDs (8 STANDARD_OIDS + 17 LINUX_SERVER_OIDS) regardless of device category

1.2 WHEN `collect_snmp_v2c()` in `probe/collectors/snmp_collector.py` is called with `oids=None` for a Storage device that does not support UCD-SNMP-MIB (1.3.6.1.4.1.2021.*) THEN the system attempts to query all 17 Linux-specific OIDs, each timing out after ~15 seconds (5s timeout × 2 retries + original request), causing the total collection to take 255-375+ seconds

1.3 WHEN the SNMP collection takes too long due to Linux OID timeouts on a Storage device THEN the result either returns with an empty or near-empty `data` dict, or the collection cycle is skipped entirely, causing the sensor to remain in "Aguardando" status indefinitely

1.4 WHEN a user selects the 'storage' category in the frontend category dropdown in `SensorLibrary.js` without selecting a template THEN the `typeMap` (`{ network: 'http', azure: 'azure', snmp: 'snmp', icmp: 'icmp' }`) does not contain a 'storage' key, so `sensor_type` is set to `'storage'` (the raw category name) via the fallback `typeMap[cat] || cat`

1.5 WHEN a sensor has `sensor_type='storage'` (from issue 1.4) THEN the probe routing in `_collect_standalone_sensors()` does not match it against the SNMP check (`sensor_type in ('snmp', 'snmp_ap', 'snmp_ups', 'snmp_switch')`), causing it to fall through to the generic fallback which also calls `_collect_snmp_standalone()` without category-aware OID selection

1.6 WHEN `handleTemplateSelect()` in `SensorLibrary.js` is called for a storage template (e.g., Dell EqualLogic) THEN the system sets `category: template.category || 'snmp'`, but storage templates do not have a `category` field, so the category defaults to 'snmp' instead of inheriting the currently selected parent category 'storage'

### Expected Behavior (Correct)

2.1 WHEN `_collect_snmp_standalone()` is called for a sensor with category 'storage' THEN the system SHALL pass only `STANDARD_OIDS` (MIB-II) to `collect_snmp_v2c()`, avoiding the 17 Linux-specific OID queries and completing collection within a reasonable time (under 30 seconds)

2.2 WHEN `collect_snmp_v2c()` receives a category-appropriate OID list for a Storage device THEN the system SHALL only query the provided OIDs, and when standard MIB-II OIDs return valid data (sysDescr, sysUpTime, sysName, interface data) the sensor SHALL be reported as "ok" and transition out of "Aguardando" status

2.3 WHEN a user selects the 'storage' category in the frontend category dropdown THEN the `typeMap` SHALL map 'storage' to 'snmp' so that `sensor_type` is correctly set to 'snmp'

2.4 WHEN the probe routing evaluates a sensor with `sensor_type='storage'` THEN the system SHALL explicitly route it to the SNMP collector by including 'storage' in the SNMP sensor_type routing list

2.5 WHEN `handleTemplateSelect()` is called while the user has 'storage' selected as the parent category THEN the system SHALL use the currently selected category from the parent dropdown (or the template's own category if present), not default to 'snmp'

2.6 WHEN `_collect_snmp_standalone()` is called for sensors with categories other than 'storage' (e.g., 'linux', 'snmp', 'windows', 'standard', 'database') THEN the system SHALL continue to pass the full OID set (STANDARD_OIDS + LINUX_SERVER_OIDS) as it does today

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a Linux server is monitored via SNMP THEN the system SHALL CONTINUE TO query both `STANDARD_OIDS` and `LINUX_SERVER_OIDS` to collect CPU, memory, disk, and load average metrics

3.2 WHEN a Windows server is monitored via SNMP THEN the system SHALL CONTINUE TO query the same OID set it currently uses (standard + Linux OIDs as fallback)

3.3 WHEN an SNMP device (switch, AP, UPS) with sensor_type 'snmp' is monitored and responds to standard OIDs THEN the system SHALL CONTINUE TO collect and report data normally with status "ok"

3.4 WHEN `collect_snmp_v2c()` is called with an explicit `oids` parameter (not None) THEN the system SHALL CONTINUE TO use the provided OID list without modification

3.5 WHEN a device is completely unreachable via SNMP (all OIDs fail) THEN the system SHALL CONTINUE TO report status "critical" and fall back to ping check as it does today

3.6 WHEN HTTP, ICMP, Printer, Engetron, or Conflex sensors are collected THEN the system SHALL CONTINUE TO route and collect them through their existing dedicated collectors without any change

3.7 WHEN a user selects categories 'network', 'azure', 'snmp', or 'icmp' in the frontend dropdown THEN the `typeMap` SHALL CONTINUE TO map them to 'http', 'azure', 'snmp', and 'icmp' respectively

3.8 WHEN `handleTemplateSelect()` is called for a template that has an explicit `category` field THEN the system SHALL CONTINUE TO use the template's own category value
