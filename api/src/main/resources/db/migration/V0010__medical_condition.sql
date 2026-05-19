CREATE TABLE medical_condition (
    id              BIGSERIAL PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    name_ka         TEXT NOT NULL,
    name_en         TEXT NOT NULL,
    description_ka  TEXT,
    description_en  TEXT,
    sort_order      INT NOT NULL DEFAULT 1000,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX medical_condition_sort_order_name_en ON medical_condition (sort_order, name_en);

CREATE TABLE condition_specialty (
    condition_id  BIGINT NOT NULL REFERENCES medical_condition(id) ON DELETE CASCADE,
    specialty_id  BIGINT NOT NULL REFERENCES specialty(id) ON DELETE CASCADE,
    PRIMARY KEY (condition_id, specialty_id)
);
CREATE INDEX condition_specialty_specialty_id ON condition_specialty (specialty_id);
