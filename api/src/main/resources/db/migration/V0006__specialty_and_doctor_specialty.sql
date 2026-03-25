CREATE TABLE specialty (
    id              BIGSERIAL PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    name_ka         TEXT NOT NULL,
    name_en         TEXT NOT NULL,
    description_ka  TEXT,
    description_en  TEXT,
    parent_id       BIGINT REFERENCES specialty(id),
    sort_order      INT NOT NULL DEFAULT 1000,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX specialty_sort_order_name_en ON specialty (sort_order, name_en);

CREATE TABLE doctor_specialty (
    doctor_id     BIGINT NOT NULL REFERENCES doctor(id) ON DELETE CASCADE,
    specialty_id  BIGINT NOT NULL REFERENCES specialty(id),
    is_primary    BOOLEAN NOT NULL DEFAULT false,
    PRIMARY KEY (doctor_id, specialty_id)
);

CREATE UNIQUE INDEX doctor_specialty_one_primary
    ON doctor_specialty (doctor_id) WHERE is_primary = true;

CREATE INDEX doctor_specialty_specialty_id ON doctor_specialty (specialty_id);
