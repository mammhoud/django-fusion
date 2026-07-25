-- Migration: Add border_color column to products table
--
-- The `border_color` column was added to the CREATE TABLE in the
-- create_all migration, but `CREATE TABLE IF NOT EXISTS` won't add
-- new columns to tables that already existed from an older migration.
--
-- This migration handles the case where the database was created
-- before `border_color` was added to the schema.
--
-- SQLite 3.35.0+ supports ADD COLUMN IF NOT EXISTS.
-- The Tauri-bundled SQLite is 3.42+, so this is safe.

ALTER TABLE products ADD COLUMN IF NOT EXISTS border_color TEXT;
