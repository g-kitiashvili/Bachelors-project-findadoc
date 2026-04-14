ALTER TABLE doctor ADD COLUMN family_name_ka TEXT;
ALTER TABLE doctor ADD COLUMN family_name_en TEXT;

CREATE INDEX doctor_family_name_en ON doctor (family_name_en);
