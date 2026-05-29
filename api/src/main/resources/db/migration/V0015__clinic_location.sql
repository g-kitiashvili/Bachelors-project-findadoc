CREATE EXTENSION IF NOT EXISTS postgis;

ALTER TABLE clinic ADD COLUMN location geography(Point, 4326);

CREATE INDEX clinic_location_gist ON clinic USING gist (location);
