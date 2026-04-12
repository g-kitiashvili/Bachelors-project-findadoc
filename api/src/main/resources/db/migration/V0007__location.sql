CREATE TABLE location (
    id          BIGSERIAL PRIMARY KEY,
    slug        TEXT NOT NULL UNIQUE,
    name_ka     TEXT NOT NULL,
    name_en     TEXT NOT NULL,
    parent_id   BIGINT REFERENCES location(id),
    sort_order  INT NOT NULL DEFAULT 1000,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX location_parent_id ON location (parent_id);
CREATE INDEX location_sort_order_name_en ON location (sort_order, name_en);

ALTER TABLE doctor ADD COLUMN location_id BIGINT REFERENCES location(id);
CREATE INDEX doctor_location_id ON doctor (location_id);
