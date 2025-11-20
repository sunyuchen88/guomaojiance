-- Migration: Add new fields for requirement 2.5.1 sample basic information
-- Date: 2025-11-20
-- Requirement: 详情页样品基本信息新增字段

-- Add commission_unit_address column (委托单位地址)
ALTER TABLE check_objects
ADD COLUMN IF NOT EXISTS commission_unit_address VARCHAR(500);

-- Add production_date column (生产日期，默认"/")
ALTER TABLE check_objects
ADD COLUMN IF NOT EXISTS production_date VARCHAR(50) DEFAULT '/';

-- Add sample_quantity column (样品数量)
ALTER TABLE check_objects
ADD COLUMN IF NOT EXISTS sample_quantity VARCHAR(50);

-- Add inspection_date column (检测日期)
ALTER TABLE check_objects
ADD COLUMN IF NOT EXISTS inspection_date VARCHAR(50);

-- Add comments for documentation
COMMENT ON COLUMN check_objects.commission_unit_address IS '委托单位地址 - 需求2.5.1';
COMMENT ON COLUMN check_objects.production_date IS '生产日期，默认"/" - 需求2.5.1';
COMMENT ON COLUMN check_objects.sample_quantity IS '样品数量 - 需求2.5.1';
COMMENT ON COLUMN check_objects.inspection_date IS '检测日期 - 需求2.5.1';
