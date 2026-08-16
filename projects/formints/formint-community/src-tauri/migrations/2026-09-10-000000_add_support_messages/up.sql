-- Support messages / contact tickets table.
-- Persists every message sent from the chat widget (Tawk-style pre-chat form)
-- with its workflow state so the Support Chat page can list history.
CREATE TABLE IF NOT EXISTS support_messages (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    subject TEXT,
    category TEXT,
    priority TEXT NOT NULL DEFAULT 'normal',
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_support_messages_status ON support_messages (status);
CREATE INDEX IF NOT EXISTS idx_support_messages_created_at ON support_messages (created_at);
