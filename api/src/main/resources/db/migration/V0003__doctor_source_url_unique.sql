-- Pipeline always sets last_source_url; tighten and use it as the idempotency key.
ALTER TABLE doctor
    ALTER COLUMN last_source_url SET NOT NULL,
    ALTER COLUMN last_updated_at SET NOT NULL;

ALTER TABLE doctor
    ADD CONSTRAINT doctor_last_source_url_unique UNIQUE (last_source_url);
