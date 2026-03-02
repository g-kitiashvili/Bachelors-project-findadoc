CREATE TABLE doctor (
    id          BIGSERIAL PRIMARY KEY,
    slug        TEXT NOT NULL UNIQUE,
    full_name   TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO doctor (slug, full_name) VALUES
    ('test-doctor', 'Test Doctor');
