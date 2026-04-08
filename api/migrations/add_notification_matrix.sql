-- Migration: Add notification_matrix column to tenants table
-- Feature: Matriz de Notificação Inteligente
-- Stores per-tenant sensor_type → channels mapping as JSON

ALTER TABLE tenants ADD COLUMN IF NOT EXISTS notification_matrix JSON;
