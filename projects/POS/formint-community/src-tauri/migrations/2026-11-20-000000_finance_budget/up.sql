-- Finance & Budget module.
--
-- finance_transactions: income (collection) / expense (payment) records.
--   category_id references the app's INVOICE_CATEGORIES ids (e.g. 'products',
--   'pay_supplier', 'employee_meal') so finance categories reuse the existing
--   finance-document taxonomy. direction mirrors INVOICE_CATEGORIES:
--   'collection' = income, 'payment' = expense.
CREATE TABLE IF NOT EXISTS finance_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                -- YYYY-MM-DD
    category_id TEXT NOT NULL,         -- INVOICE_CATEGORIES id
    direction TEXT NOT NULL DEFAULT 'collection'
        CHECK (direction IN ('collection', 'payment')),
    amount REAL NOT NULL DEFAULT 0,
    description TEXT,
    reference TEXT,                    -- invoice/PO number, receipt id, etc.
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_finance_transactions_date ON finance_transactions (date);
CREATE INDEX IF NOT EXISTS idx_finance_transactions_category ON finance_transactions (category_id);
CREATE INDEX IF NOT EXISTS idx_finance_transactions_direction ON finance_transactions (direction);

-- budgets: per-category spending limits for a period.
--   category_id uses the same INVOICE_CATEGORIES taxonomy; a budget with
--   category_id = NULL means a global budget for the period.
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id TEXT,                  -- INVOICE_CATEGORIES id or NULL (global)
    period_start TEXT NOT NULL,        -- YYYY-MM-DD
    period_end TEXT NOT NULL,          -- YYYY-MM-DD
    amount REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets (period_start, period_end);
