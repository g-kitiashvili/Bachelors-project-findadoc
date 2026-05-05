CREATE TABLE clinic (
    id              BIGSERIAL PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    name_ka         TEXT NOT NULL,
    name_en         TEXT NOT NULL,
    address         TEXT,
    phone           TEXT,
    website         TEXT,
    last_source_url TEXT NOT NULL UNIQUE,
    last_updated_at TIMESTAMPTZ,
    status          TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX clinic_name_en ON clinic (name_en);
CREATE INDEX clinic_name_ka_trgm ON clinic USING gin (name_ka gin_trgm_ops);
CREATE INDEX clinic_name_en_trgm ON clinic USING gin (lower(name_en) gin_trgm_ops);

CREATE TABLE doctor_clinic (
    doctor_id  BIGINT NOT NULL REFERENCES doctor(id) ON DELETE CASCADE,
    clinic_id  BIGINT NOT NULL REFERENCES clinic(id) ON DELETE CASCADE,
    PRIMARY KEY (doctor_id, clinic_id)
);
CREATE INDEX doctor_clinic_clinic_id ON doctor_clinic (clinic_id);
