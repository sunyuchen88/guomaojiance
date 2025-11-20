-- Migration: Add check_method, unit, detection_limit fields to check_object_items
-- Date: 2025-11-20
-- Requirement: T2.2 - Support 5 core fields for check result input

-- Add check_method column (检测方法)
ALTER TABLE check_object_items
ADD COLUMN IF NOT EXISTS check_method VARCHAR(200);

-- Add unit column (单位)
ALTER TABLE check_object_items
ADD COLUMN IF NOT EXISTS unit VARCHAR(50);

-- Add detection_limit column (检出限)
ALTER TABLE check_object_items
ADD COLUMN IF NOT EXISTS detection_limit VARCHAR(100);

-- Add comments for documentation
COMMENT ON COLUMN check_object_items.check_method IS '检测方法';
COMMENT ON COLUMN check_object_items.unit IS '单位';
COMMENT ON COLUMN check_object_items.detection_limit IS '检出限';
