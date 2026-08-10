ALTER TABLE sales DROP COLUMN tax_profile_id;

ALTER TABLE products DROP COLUMN tax_profile_id;

DROP TABLE tax_profiles;
