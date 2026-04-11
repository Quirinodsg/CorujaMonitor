-- Migração: Aplicar threshold padrão (95%) em todos os sensores disk/cpu/memory
-- que ainda têm o valor antigo de fábrica (80) ou NULL.
-- Sensores com threshold diferente de 80 e diferente de NULL são considerados
-- personalizados e NÃO são alterados.

-- Atualizar threshold_warning de 80 → 95 para disk, cpu, memory
UPDATE sensors
SET threshold_warning = 95
WHERE sensor_type IN ('disk', 'cpu', 'memory')
  AND (threshold_warning = 80 OR threshold_warning IS NULL);

-- Atualizar threshold_critical de 95 → 95 (já correto, mas garantir NULL → 95)
UPDATE sensors
SET threshold_critical = 95
WHERE sensor_type IN ('disk', 'cpu', 'memory')
  AND threshold_critical IS NULL;

-- Recalcular status das últimas métricas para disk/cpu/memory
-- Status = 'ok' se value < 95, 'warning' se 80 <= value < 95, 'critical' se >= 95
-- Como agora o threshold warning é 95, qualquer valor < 95 deve ser 'ok'
UPDATE metrics m
SET status = CASE
    WHEN m.value >= 95 THEN 'critical'
    WHEN m.value >= 95 THEN 'warning'
    ELSE 'ok'
END
WHERE m.sensor_id IN (
    SELECT id FROM sensors WHERE sensor_type IN ('disk', 'cpu', 'memory')
)
AND m.timestamp = (
    SELECT MAX(m2.timestamp) FROM metrics m2 WHERE m2.sensor_id = m.sensor_id
);

-- Mais simples: qualquer valor < 95 vira 'ok' para disk/cpu/memory
UPDATE metrics m
SET status = 'ok'
WHERE m.sensor_id IN (
    SELECT id FROM sensors WHERE sensor_type IN ('disk', 'cpu', 'memory')
)
AND m.value < 95
AND m.timestamp = (
    SELECT MAX(m2.timestamp) FROM metrics m2 WHERE m2.sensor_id = m.sensor_id
);

UPDATE metrics m
SET status = 'warning'
WHERE m.sensor_id IN (
    SELECT s.id FROM sensors s WHERE s.sensor_type IN ('disk', 'cpu', 'memory')
      AND s.threshold_warning IS NOT NULL
)
AND m.value >= (
    SELECT s.threshold_warning FROM sensors s WHERE s.id = m.sensor_id
)
AND m.value < (
    SELECT COALESCE(s.threshold_critical, 100) FROM sensors s WHERE s.id = m.sensor_id
)
AND m.timestamp = (
    SELECT MAX(m2.timestamp) FROM metrics m2 WHERE m2.sensor_id = m.sensor_id
);

UPDATE metrics m
SET status = 'critical'
WHERE m.sensor_id IN (
    SELECT s.id FROM sensors s WHERE s.sensor_type IN ('disk', 'cpu', 'memory')
      AND s.threshold_critical IS NOT NULL
)
AND m.value >= (
    SELECT s.threshold_critical FROM sensors s WHERE s.id = m.sensor_id
)
AND m.timestamp = (
    SELECT MAX(m2.timestamp) FROM metrics m2 WHERE m2.sensor_id = m.sensor_id
);
