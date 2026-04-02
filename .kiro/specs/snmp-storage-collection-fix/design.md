# SNMP Storage Collection Fix — Bugfix Design

## Overview

Storage sensors (Dell EqualLogic, NetApp, etc.) added via the Coruja Monitor frontend remain stuck in "Aguardando" status because `collect_snmp_v2c()` queries 17 Linux-specific UCD-SNMP-MIB OIDs against devices that don't support them, causing 255-375s of timeouts per collection cycle. Secondary issues in the frontend `typeMap`, `handleTemplateSelect`, and probe routing prevent storage sensors from being correctly typed and routed. The fix introduces category-aware OID selection in the probe, adds 'storage' to the frontend type mapping and probe routing, and ensures template selection inherits the parent category.

## Glossary

- **Bug_Condition (C)**: A sensor with category 'storage' (or sensor_type 'storage') is collected via SNMP, triggering queries against 17 unsupported Linux OIDs that time out
- **Property (P)**: Storage sensors SHALL be collected using only STANDARD_OIDS (MIB-II), completing within ~30s and transitioning out of "Aguardando"
- **Preservation**: All existing SNMP collection for Linux, Windows, standard, network devices, and all non-SNMP collectors (HTTP, ICMP, Engetron, Conflex, Printer) must remain unchanged
- **`collect_snmp_v2c()`**: Method in `probe/collectors/snmp_collector.py` that queries SNMP OIDs; defaults to STANDARD_OIDS + LINUX_SERVER_OIDS when `oids=None`
- **`_collect_snmp_standalone()`**: Method in `probe/probe_core.py` that calls `collect_snmp_v2c()` without passing category-aware OIDs
- **`_collect_standalone_sensors()`**: Router method in `probe/probe_core.py` that dispatches sensors to the correct collector based on sensor_type/name
- **`typeMap`**: Object in `SensorLibrary.js` that maps category names to sensor_type values; currently missing 'storage' → 'snmp'
- **`handleTemplateSelect()`**: Function in `SensorLibrary.js` that populates sensor form from a template; defaults category to 'snmp' instead of inheriting parent
- **STANDARD_OIDS**: 8 RFC 1213 MIB-II OIDs (sysDescr, sysUpTime, sysName, ifNumber, ifDescr, ifSpeed, ifInOctets, ifOutOctets)
- **LINUX_SERVER_OIDS**: 17 UCD-SNMP-MIB OIDs (1.3.6.1.4.1.2021.*) for CPU, memory, disk, load average — only supported by Linux net-snmp

## Bug Details

### Bug Condition

The bug manifests when a Storage sensor (category='storage') is collected via SNMP. The `_collect_snmp_standalone()` method calls `collect_snmp_v2c()` without passing an OID list, causing it to default to all 25 OIDs (8 standard + 17 Linux). Storage devices don't support UCD-SNMP-MIB, so each of the 17 Linux OIDs times out at ~15s (5s × 3 attempts), totaling 255-375s. Additionally, the frontend doesn't correctly map 'storage' to 'snmp' sensor_type, and the probe routing doesn't explicitly handle 'storage' in its SNMP check.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type SensorCollectionRequest {category, sensor_type, ip_address, oids_param}
  OUTPUT: boolean

  RETURN (input.category == 'storage' OR input.sensor_type == 'storage')
         AND input.ip_address IS NOT NULL
         AND input.oids_param IS NULL
         // When oids_param is None, collect_snmp_v2c defaults to STANDARD_OIDS + LINUX_SERVER_OIDS
         // Storage devices don't support LINUX_SERVER_OIDS → 17 timeouts × ~15s each
END FUNCTION
```

### Examples

- **Dell EqualLogic (192.168.31.92)**: category='storage', sensor_type='snmp', `_collect_snmp_standalone()` calls `collect_snmp_v2c("192.168.31.92", "public", 161)` with `oids=None` → queries 17 Linux OIDs → 255s+ timeout → sensor stays "Aguardando". Expected: only query 8 STANDARD_OIDS → responds in <30s → status "ok"
- **Frontend category selection**: User selects 'storage' category → `typeMap` has no 'storage' key → `sensor_type` set to `'storage'` (raw string) instead of `'snmp'`. Expected: `typeMap['storage']` returns `'snmp'`
- **Template selection (Dell EqualLogic)**: User clicks Dell EqualLogic template while 'storage' is selected → `handleTemplateSelect` sets `category: template.category || 'snmp'` → template has no `category` field → defaults to 'snmp'. Expected: inherit 'storage' from parent dropdown
- **Probe routing**: Sensor with `sensor_type='storage'` arrives at `_collect_standalone_sensors()` → doesn't match `('snmp', 'snmp_ap', 'snmp_ups', 'snmp_switch')` → falls to generic fallback → still calls `_collect_snmp_standalone()` without category-aware OIDs. Expected: 'storage' included in SNMP routing check

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Linux servers (category='linux') must continue to receive STANDARD_OIDS + LINUX_SERVER_OIDS for full CPU/memory/disk/load metrics
- Windows servers (category='windows') must continue to receive the same OID set as today
- Standard SNMP devices (category='snmp', switches, APs) must continue to receive the full OID set
- Database servers (category='database') must continue to receive the full OID set
- HTTP, ICMP, Printer, Engetron, and Conflex collectors must continue routing and collecting through their dedicated paths
- `collect_snmp_v2c()` called with an explicit `oids` parameter (not None) must continue using the provided list without modification
- Unreachable devices must continue to report status 'critical' and fall back to ping check
- Frontend `typeMap` mappings for 'network'→'http', 'azure'→'azure', 'snmp'→'snmp', 'icmp'→'icmp' must remain unchanged
- `handleTemplateSelect()` must continue to use a template's own `category` field when it exists

**Scope:**
All inputs that do NOT involve category='storage' or sensor_type='storage' should be completely unaffected by this fix. This includes:
- All existing SNMP sensor types (snmp, snmp_ap, snmp_ups, snmp_switch)
- All non-SNMP collectors (HTTP, ICMP, Engetron, Conflex, Printer)
- All existing frontend category mappings
- All existing API endpoint behavior for non-storage sensors

## Hypothesized Root Cause

Based on the bug description and code analysis, the issues are:

1. **No Category-Aware OID Selection in `_collect_snmp_standalone()`**: The method in `probe/probe_core.py` (line ~830) calls `collector.collect_snmp_v2c(ip, community, port)` without passing `oids`. This causes `collect_snmp_v2c()` to default to `STANDARD_OIDS + LINUX_SERVER_OIDS` for ALL devices, including storage devices that only support MIB-II.

2. **Missing 'storage' in Frontend `typeMap`**: In `SensorLibrary.js` (line ~655), the `typeMap` is `{ network: 'http', azure: 'azure', snmp: 'snmp', icmp: 'icmp' }`. When user selects 'storage', the fallback `typeMap[cat] || cat` produces `'storage'` as sensor_type instead of `'snmp'`.

3. **Missing 'storage' in Probe Routing**: In `probe/probe_core.py` `_collect_standalone_sensors()`, the SNMP check is `sensor_type in ('snmp', 'snmp_ap', 'snmp_ups', 'snmp_switch')`. A sensor with `sensor_type='storage'` doesn't match, falling through to the generic fallback.

4. **`handleTemplateSelect()` Doesn't Inherit Parent Category**: In `SensorLibrary.js` (line ~306), `category: template.category || 'snmp'` defaults to 'snmp' when the template has no `category` field. Storage templates in `sensorTemplates.js` don't have a `category` field, so selecting "Dell EqualLogic" while browsing the 'storage' category resets category to 'snmp'.

5. **API Category Propagation**: The `/sensors/standalone/by-probe` endpoint in `api/routers/sensors.py` returns `category: cfg.get("category", s.sensor_type)`. If the sensor was created with `sensor_type='storage'` (from bug #2) and no explicit category in config, the API returns `category='storage'` which is correct but the probe doesn't handle it properly.

## Correctness Properties

Property 1: Bug Condition - Storage Sensors Collect with Standard OIDs Only

_For any_ SNMP collection request where the sensor has category='storage' (isBugCondition returns true), the fixed `_collect_snmp_standalone()` function SHALL pass only `STANDARD_OIDS` (8 MIB-II OIDs) to `collect_snmp_v2c()`, completing collection within a reasonable time (<30s) and producing a valid result with status 'ok' when the device responds to standard OIDs.

**Validates: Requirements 2.1, 2.2**

Property 2: Preservation - Non-Storage SNMP Collection Unchanged

_For any_ SNMP collection request where the sensor does NOT have category='storage' (isBugCondition returns false), the fixed code SHALL produce the same OID query behavior as the original code, preserving full STANDARD_OIDS + LINUX_SERVER_OIDS collection for Linux, Windows, standard, and database categories.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

Property 3: Bug Condition - Frontend Storage Category Maps to SNMP Type

_For any_ category selection in the frontend where the user selects 'storage', the fixed `typeMap` SHALL map 'storage' to 'snmp' so that `sensor_type` is correctly set to 'snmp'.

**Validates: Requirements 2.3**

Property 4: Preservation - Existing Frontend Category Mappings Unchanged

_For any_ category selection in the frontend where the user selects a category other than 'storage' (network, azure, snmp, icmp), the fixed `typeMap` SHALL produce the same sensor_type mapping as the original code.

**Validates: Requirements 3.7**

Property 5: Bug Condition - Probe Routes Storage to SNMP Collector

_For any_ sensor with sensor_type='storage' arriving at `_collect_standalone_sensors()`, the fixed routing SHALL explicitly match it to the SNMP collector path, not the generic fallback.

**Validates: Requirements 2.4**

Property 6: Bug Condition - Template Selection Inherits Parent Category

_For any_ template selection via `handleTemplateSelect()` where the template has no `category` field and the user has a parent category selected (e.g., 'storage'), the fixed function SHALL use the currently selected parent category instead of defaulting to 'snmp'.

**Validates: Requirements 2.5**

Property 7: Preservation - Non-SNMP Collectors Unchanged

_For any_ sensor that routes to HTTP, ICMP, Printer, Engetron, or Conflex collectors, the fixed code SHALL produce exactly the same routing and collection behavior as the original code.

**Validates: Requirements 3.6**

## Collector Review Findings

After reviewing all 29 files in `probe/collectors/`, the following patterns were identified:

**Dedicated collectors that already pass specific OIDs (working correctly):**
- `printer_collector.py` — passes `PRINTER_OIDS` to `collect_snmp_v2c()`, avoids Linux OID timeouts
- `conflex_collector.py` — passes Conflex enterprise OIDs to `collect_snmp_v2c()`, avoids Linux OID timeouts
- `engetron_collector.py` — uses HTTP scraping (not SNMP), no OID issue

**SNMP collectors that exist but are NOT wired into probe_core routing:**
- `snmp_ac_collector.py` — APC/Liebert AC collector (probe_core uses conflex_collector instead)
- `snmp_ap_collector.py` — Access Point collector (probe_core uses generic `_collect_snmp_standalone` instead)

**Missing collector:**
- No `storage_collector.py` exists. Storage devices fall through to `_collect_snmp_standalone()` which calls `collect_snmp_v2c()` with `oids=None`, triggering the 17 Linux OID timeouts.

**Design decision:** Create a dedicated `storage_collector.py` following the same pattern as `printer_collector.py` and `conflex_collector.py`. This is the cleanest approach because:
1. It follows the existing architecture pattern (each device type has its own collector)
2. It allows future expansion with Dell EqualLogic enterprise OIDs (1.3.6.1.4.1.12740.*)
3. It keeps `_collect_snmp_standalone()` unchanged for other device types (preservation)
4. The routing in `probe_core.py` adds a new `elif` for storage, same as printer/conflex

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**NEW File**: `probe/collectors/storage_collector.py` (deployed to Windows Sonda via RDP)

**Specific Changes**:
1. **Create dedicated Storage collector** following the `printer_collector.py` pattern:
   - Class `StorageCollector(ip, community, port)`
   - `collect()` method that calls `SNMPCollector.collect_snmp_v2c()` with only STANDARD_OIDS (MIB-II)
   - Returns structured metrics: status (ok/critical), sysName, sysUpTime, interface count, interface status
   - Future-ready: includes placeholder for Dell EqualLogic enterprise OIDs (1.3.6.1.4.1.12740.*)

---

**File**: `probe/probe_core.py` (deployed to Windows Sonda via RDP)

**Function**: `_collect_standalone_sensors()`

**Specific Changes**:
2. **Add storage routing BEFORE the generic SNMP check**: Add a new `elif` block that detects storage sensors by `category == 'storage'` and routes them to `_collect_storage()`, similar to how printer/conflex are routed. This must be placed BEFORE the generic SNMP check to ensure storage sensors don't fall through.

**New Function**: `_collect_storage()`

**Specific Changes**:
3. **Add `_collect_storage()` method** following the same pattern as `_collect_printer()` and `_collect_conflex()`:
   - Imports `StorageCollector` from `collectors.storage_collector`
   - Calls `collector.collect()` and processes the result
   - Appends metric to buffer with `sensor_type='storage'`, status, and metadata

---

**File**: `frontend/src/components/SensorLibrary.js` (deployed to Linux via git)

**Function**: Category dropdown `onChange` handler

**Specific Changes**:
4. **Add 'storage' to `typeMap`**: Change `typeMap` from `{ network: 'http', azure: 'azure', snmp: 'snmp', icmp: 'icmp' }` to `{ network: 'http', azure: 'azure', snmp: 'snmp', icmp: 'icmp', storage: 'snmp' }`.

**Function**: `handleTemplateSelect()`

**Specific Changes**:
5. **Inherit parent category**: Change `category: template.category || 'snmp'` to `category: template.category || newSensor.category || 'snmp'`. This way, if the template has no category, it inherits the currently selected category from the form state (e.g., 'storage'), and only falls back to 'snmp' if neither exists.

---

**File**: `api/routers/sensors.py` (deployed to Linux via git)

**Function**: `/sensors/standalone/by-probe` endpoint

**Specific Changes**:
6. **Ensure category propagation**: The current code `category: cfg.get("category", s.sensor_type)` already propagates category from config. Verify that when a storage sensor is created with the fixed frontend (sensor_type='snmp', category='storage'), the config stores category='storage' and the API returns it correctly. If the config doesn't store category, add it to the sensor creation flow.

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that simulate SNMP collection for storage sensors and verify which OIDs are queried. Run these tests on the UNFIXED code to observe failures and understand the root cause.

**Test Cases**:
1. **Storage OID Selection Test**: Call `_collect_snmp_standalone()` with a storage sensor and verify that `collect_snmp_v2c()` receives only STANDARD_OIDS (will fail on unfixed code — it receives None/all OIDs)
2. **Frontend typeMap Test**: Simulate selecting 'storage' category and verify sensor_type is 'snmp' (will fail on unfixed code — produces 'storage')
3. **Probe Routing Test**: Pass a sensor with sensor_type='storage' through routing logic and verify it matches SNMP path (will fail on unfixed code — falls to fallback)
4. **Template Category Inheritance Test**: Simulate selecting Dell EqualLogic template while 'storage' is selected and verify category stays 'storage' (will fail on unfixed code — resets to 'snmp')

**Expected Counterexamples**:
- `_collect_snmp_standalone()` calls `collect_snmp_v2c()` with `oids=None` for storage sensors, causing 17 Linux OID timeouts
- `typeMap['storage']` returns `undefined`, causing fallback to raw category string 'storage'
- Sensor with `sensor_type='storage'` doesn't match SNMP routing tuple, falls to generic fallback

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL sensor WHERE isBugCondition(sensor) DO
  oids_passed := capture_oids_arg(_collect_snmp_standalone_fixed(sensor))
  ASSERT oids_passed == list(STANDARD_OIDS.values())
  ASSERT collection_time < 30 seconds
  ASSERT result.status IN ('ok', 'critical')  // not stuck in 'Aguardando'
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL sensor WHERE NOT isBugCondition(sensor) DO
  ASSERT oids_passed_original(sensor) == oids_passed_fixed(sensor)
  ASSERT route_original(sensor) == route_fixed(sensor)
  ASSERT typeMap_original(sensor.category) == typeMap_fixed(sensor.category)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many sensor configurations automatically across the input domain (random categories, sensor_types, names, IPs)
- It catches edge cases that manual unit tests might miss (e.g., sensor with category='storage' but name containing 'engetron')
- It provides strong guarantees that behavior is unchanged for all non-storage inputs

**Test Plan**: Observe behavior on UNFIXED code first for non-storage sensors, then write property-based tests capturing that behavior.

**Test Cases**:
1. **Linux OID Preservation**: Verify that sensors with category='linux' still receive STANDARD_OIDS + LINUX_SERVER_OIDS after the fix
2. **Windows OID Preservation**: Verify that sensors with category='windows' still receive the full OID set
3. **SNMP Device Routing Preservation**: Verify that sensors with sensor_type='snmp' still route to the SNMP collector path
4. **Frontend typeMap Preservation**: Verify that 'network'→'http', 'azure'→'azure', 'snmp'→'snmp', 'icmp'→'icmp' mappings are unchanged
5. **Non-SNMP Collector Preservation**: Verify HTTP, ICMP, Engetron, Conflex sensors continue routing to their dedicated collectors

### Unit Tests

- Test `_collect_snmp_standalone()` with category='storage' passes only STANDARD_OIDS
- Test `_collect_snmp_standalone()` with category='linux' passes None (full OID set)
- Test `_collect_standalone_sensors()` routing with sensor_type='storage' matches SNMP path
- Test `typeMap` includes 'storage' → 'snmp' mapping
- Test `handleTemplateSelect()` inherits parent category when template has no category field
- Test `handleTemplateSelect()` uses template's own category when it exists (preservation)

### Property-Based Tests

- Generate random sensor configurations with category in ('storage', 'linux', 'windows', 'snmp', 'standard', 'database') and verify OID selection is correct for each
- Generate random sensor configurations with various sensor_types and verify routing matches expected collector
- Generate random category selections and verify typeMap produces correct sensor_type for all categories

### Integration Tests

- Test full flow: create storage sensor via frontend → verify API stores correct category/sensor_type → verify probe collects with STANDARD_OIDS only
- Test full flow: create Linux sensor → verify probe still collects with full OID set
- Test that storage sensor transitions from "Aguardando" to "ok" after fix is deployed
