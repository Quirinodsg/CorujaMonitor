-- TimescaleDB Setup - Coruja Monitor Enterprise
-- Executar como superuser no PostgreSQL com TimescaleDB instalado

-- 1. Habilitar extensão
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 2. Converter tabela de métricas em hypertable
-- (assumindo que a tabela sensor_metrics já existe)
SELECT create_hypertable(
    'sensor_metrics',
    'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 3. Compressão automática em chunks com mais de 7 dias
ALTER TABLE sensor_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'server_id, sensor_type'
);

SELECT add_compression_policy('sensor_metrics', INTERVAL '7 days', if_not_exists => TRUE);

-- 4. Retention policy: raw metrics → 30 dias
SELECT add_retention_policy('sensor_metrics', INTERVAL '30 days', if_not_exists => TRUE);

-- 5. Continuous aggregate: médias horárias (retenção 90 dias)
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS bucket,
    server_id,
    sensor_type,
    AVG(value)   AS avg_value,
    MAX(value)   AS max_value,
    MIN(value)   AS min_value,
    COUNT(*)     AS sample_count
FROM sensor_metrics
GROUP BY bucket, server_id, sensor_type
WITH NO DATA;

SELECT add_continuous_aggregate_policy(
    'sensor_metrics_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset   => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

SELECT add_retention_policy('sensor_metrics_hourly', INTERVAL '90 days', if_not_exists => TRUE);

-- 6. Continuous aggregate: médias diárias (retenção 1 ano = aggregated metrics)
CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_metrics_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', timestamp) AS bucket,
    server_id,
    sensor_type,
    AVG(value)   AS avg_value,
    MAX(value)   AS max_value,
    MIN(value)   AS min_value,
    COUNT(*)     AS sample_count
FROM sensor_metrics
GROUP BY bucket, server_id, sensor_type
WITH NO DATA;

SELECT add_continuous_aggregate_policy(
    'sensor_metrics_daily',
    start_offset => INTERVAL '3 days',
    end_offset   => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

SELECT add_retention_policy('sensor_metrics_daily', INTERVAL '365 days', if_not_exists => TRUE);
