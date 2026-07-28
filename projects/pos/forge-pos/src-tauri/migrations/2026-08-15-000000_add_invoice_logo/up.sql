-- Add invoice_logo column to settings — a separate logo for invoices/receipts
-- distinct from the main logo (used for app branding).
ALTER TABLE settings ADD COLUMN invoice_logo TEXT;
