CREATE TABLE clinic_brand (
    id          BIGSERIAL PRIMARY KEY,
    slug        TEXT NOT NULL UNIQUE,
    name_ka     TEXT NOT NULL,
    name_en     TEXT NOT NULL,
    sort_order  INT NOT NULL DEFAULT 1000,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE clinic ADD COLUMN brand_id BIGINT REFERENCES clinic_brand(id);
CREATE INDEX clinic_brand_id ON clinic (brand_id);
