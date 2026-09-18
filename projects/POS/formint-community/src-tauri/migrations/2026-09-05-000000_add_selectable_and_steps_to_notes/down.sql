-- Remove selectable + steps columns from receipt_templates
ALTER TABLE receipt_templates DROP COLUMN selectable;
ALTER TABLE receipt_templates DROP COLUMN steps;
