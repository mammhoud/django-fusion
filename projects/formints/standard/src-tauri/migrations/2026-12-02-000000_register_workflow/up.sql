ALTER TABLE settings ADD COLUMN printer_port TEXT;
ALTER TABLE settings ADD COLUMN printer_enabled BOOLEAN NOT NULL DEFAULT 0;

CREATE TABLE shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opened_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    opening_cash REAL NOT NULL DEFAULT 0.0 CHECK (opening_cash >= 0),
    closing_cash REAL CHECK (closing_cash IS NULL OR closing_cash >= 0),
    expected_cash REAL,
    cash_difference REAL,
    shift_status TEXT NOT NULL DEFAULT 'open' CHECK (shift_status IN ('open', 'closed')),
    shift_notes TEXT
);

CREATE UNIQUE INDEX idx_one_open_shift ON shifts(shift_status) WHERE shift_status = 'open';
CREATE INDEX idx_shifts_opened_at ON shifts(opened_at DESC);

CREATE TRIGGER employee_schedule_no_overlap_insert
BEFORE INSERT ON employee_schedules
WHEN NEW.status NOT IN ('completed', 'cancelled', 'no_show')
 AND EXISTS (
    SELECT 1 FROM employee_schedules existing
    WHERE existing.employee_id = NEW.employee_id
      AND existing.status NOT IN ('completed', 'cancelled', 'no_show')
      AND existing.shift_start < NEW.shift_end
      AND existing.shift_end > NEW.shift_start
)
BEGIN
    SELECT RAISE(ABORT, 'This employee already has an overlapping shift.');
END;

CREATE TRIGGER employee_schedule_no_overlap_update
BEFORE UPDATE OF employee_id, shift_start, shift_end, status ON employee_schedules
WHEN NEW.status NOT IN ('completed', 'cancelled', 'no_show')
 AND EXISTS (
    SELECT 1 FROM employee_schedules existing
    WHERE existing.id <> NEW.id
      AND existing.employee_id = NEW.employee_id
      AND existing.status NOT IN ('completed', 'cancelled', 'no_show')
      AND existing.shift_start < NEW.shift_end
      AND existing.shift_end > NEW.shift_start
)
BEGIN
    SELECT RAISE(ABORT, 'This employee already has an overlapping shift.');
END;
