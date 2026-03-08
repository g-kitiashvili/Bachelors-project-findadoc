CREATE TABLE doctor (
    id          BIGSERIAL    PRIMARY KEY,
    slug        TEXT         NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);
