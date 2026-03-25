CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX doctor_full_name_ka_trgm ON doctor USING gin (full_name_ka gin_trgm_ops);
CREATE INDEX doctor_full_name_en_trgm ON doctor USING gin (full_name_en gin_trgm_ops);
CREATE INDEX doctor_specialty_ka_trgm ON doctor USING gin (specialty_ka gin_trgm_ops);
CREATE INDEX doctor_specialty_en_trgm ON doctor USING gin (specialty_en gin_trgm_ops);
