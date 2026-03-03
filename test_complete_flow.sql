-- TESTE COMPLETO DO FLUXO DE INCIDENTES
-- 1. Verificar estado inicial
\echo '========================================='
\echo '1. ESTADO INICIAL'
\echo '========================================='
SELECT 
    s.id, 
    s.name, 
    m.value, 
    m.status, 
    m.timestamp,
    m.metadata->>'simulated' as is_simulated
FROM sensors s
LEFT JOIN LATERAL (
    SELECT * FROM metrics 
    WHERE sensor_id = s.id 
    ORDER BY timestamp DESC 
    LIMIT 1
) m ON true
WHERE s.id IN (199, 200)
ORDER BY s.id;

\echo ''
\echo 'Incidentes abertos:'
SELECT id, sensor_id, severity, status, title 
FROM incidents 
WHERE status = 'open';

\echo ''
\echo '========================================='
\echo '2. INSERINDO METRICA SIMULADA'
\echo '========================================='
-- Inserir métrica simulada para sensor 199 (CPU)
INSERT INTO metrics (sensor_id, value, unit, status, timestamp, metadata)
VALUES (199, 96.0, 'percent', 'critical', NOW(), '{"simulated": true, "test_mode": true}');

\echo 'Metrica simulada inserida!'

\echo ''
\echo '========================================='
\echo '3. CRIANDO INCIDENTE'
\echo '========================================='
-- Criar incidente
INSERT INTO incidents (sensor_id, severity, status, title, description, created_at, ai_analysis)
VALUES (
    199, 
    'critical', 
    'open', 
    '[TESTE] Falha simulada - CPU',
    'Falha simulada para teste de resolução',
    NOW(),
    '{"simulated": true, "test_mode": true}'
)
RETURNING id, title, status;

\echo ''
\echo '========================================='
\echo '4. VERIFICANDO ESTADO APOS SIMULACAO'
\echo '========================================='
SELECT 
    s.id, 
    s.name, 
    m.value, 
    m.status, 
    m.timestamp,
    m.metadata->>'simulated' as is_simulated
FROM sensors s
LEFT JOIN LATERAL (
    SELECT * FROM metrics 
    WHERE sensor_id = s.id 
    ORDER BY timestamp DESC 
    LIMIT 1
) m ON true
WHERE s.id = 199;

\echo ''
\echo 'Incidentes abertos:'
SELECT id, sensor_id, severity, status, title 
FROM incidents 
WHERE status = 'open';

\echo ''
\echo '========================================='
\echo 'PRESSIONE ENTER PARA RESOLVER INCIDENTE'
\echo '========================================='
\prompt 'Pressione ENTER para continuar...' dummy

\echo ''
\echo '========================================='
\echo '5. RESOLVENDO INCIDENTE (SIMULANDO API)'
\echo '========================================='
-- Simular o que a API faz ao resolver incidente
WITH incident_to_resolve AS (
    SELECT id, sensor_id 
    FROM incidents 
    WHERE status = 'open' 
    AND ai_analysis->>'simulated' = 'true'
    LIMIT 1
),
deleted_metrics AS (
    DELETE FROM metrics 
    WHERE sensor_id IN (SELECT sensor_id FROM incident_to_resolve)
    AND metadata->>'simulated' = 'true'
    RETURNING id
)
UPDATE incidents 
SET 
    status = 'resolved',
    resolved_at = NOW()
WHERE id IN (SELECT id FROM incident_to_resolve)
RETURNING id, title, status, resolved_at;

\echo ''
\echo 'Metricas simuladas deletadas:'
SELECT COUNT(*) as deleted_count
FROM metrics 
WHERE sensor_id = 199 
AND metadata->>'simulated' = 'true';

\echo ''
\echo '========================================='
\echo '6. ESTADO FINAL'
\echo '========================================='
SELECT 
    s.id, 
    s.name, 
    m.value, 
    m.status, 
    m.timestamp,
    m.metadata->>'simulated' as is_simulated
FROM sensors s
LEFT JOIN LATERAL (
    SELECT * FROM metrics 
    WHERE sensor_id = s.id 
    ORDER BY timestamp DESC 
    LIMIT 1
) m ON true
WHERE s.id = 199;

\echo ''
\echo 'Incidentes abertos:'
SELECT id, sensor_id, severity, status, title 
FROM incidents 
WHERE status = 'open';

\echo ''
\echo 'Incidentes resolvidos (ultimos 5):'
SELECT id, sensor_id, severity, status, title, resolved_at 
FROM incidents 
WHERE status = 'resolved'
ORDER BY resolved_at DESC
LIMIT 5;

\echo ''
\echo '========================================='
\echo 'TESTE CONCLUIDO!'
\echo '========================================='
