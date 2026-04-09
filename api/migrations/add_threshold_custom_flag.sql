-- Migration: Adicionar campo threshold_custom para proteger thresholds personalizados
-- Sensores com threshold diferente dos valores de fábrica (80/95) são marcados como personalizados.

-- 1. Adicionar coluna (se não existir)
ALTER TABLE sensors ADD COLUMN IF NOT EXISTS threshold_custom BOOLEAN NOT NULL DEFAULT FALSE;

-- 2. Marcar como personalizados os sensores que já têm thresholds diferentes do padrão de fábrica
--    Padrão de fábrica: warning=80, critical=95 para cpu/memory/disk
--    Qualquer valor diferente desses (e não NULL) indica personalização manual.
UPDATE sensors
SET threshold_custom = TRUE
WHERE sensor_type IN ('cpu', 'memory', 'disk')
  AND (
      (threshold_warning IS NOT NULL AND threshold_warning != 80 AND threshold_warning != 95)
      OR
      (threshold_critical IS NOT NULL AND threshold_critical != 95 AND threshold_critical != 80)
  );

-- 3. Sensores de outros tipos com threshold configurado também são personalizados
UPDATE sensors
SET threshold_custom = TRUE
WHERE sensor_type NOT IN ('cpu', 'memory', 'disk', 'ping', 'uptime', 'system', 'service', 'network_in', 'network_out')
  AND (threshold_warning IS NOT NULL OR threshold_critical IS NOT NULL);
