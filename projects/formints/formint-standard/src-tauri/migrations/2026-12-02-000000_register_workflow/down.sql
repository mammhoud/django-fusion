DROP TRIGGER IF EXISTS employee_schedule_no_overlap_update;
DROP TRIGGER IF EXISTS employee_schedule_no_overlap_insert;
DROP INDEX IF EXISTS idx_shifts_opened_at;
DROP INDEX IF EXISTS idx_one_open_shift;
DROP TABLE IF EXISTS shifts;
ALTER TABLE settings DROP COLUMN printer_port;
ALTER TABLE settings DROP COLUMN printer_enabled;
