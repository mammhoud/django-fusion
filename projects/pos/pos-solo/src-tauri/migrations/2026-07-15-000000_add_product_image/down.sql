-- SQLite does not support dropping columns directly.
-- To revert, you would need to recreate the table without the column.
-- For safety, this down migration is a no-op.
SELECT 1;
