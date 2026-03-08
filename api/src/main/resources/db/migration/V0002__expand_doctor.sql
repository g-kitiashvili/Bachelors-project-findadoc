ALTER TABLE doctor
    ADD COLUMN full_name_ka              TEXT                                  NOT NULL,
    ADD COLUMN full_name_en              TEXT                                  NOT NULL,
    ADD COLUMN gender                    TEXT         CHECK (gender IN ('male','female','other')),
    ADD COLUMN photo_url                 TEXT,
    ADD COLUMN is_accepting_new_patients BOOLEAN      NOT NULL DEFAULT TRUE,
    ADD COLUMN treats_children           BOOLEAN      NOT NULL DEFAULT FALSE,
    ADD COLUMN treats_adults             BOOLEAN      NOT NULL DEFAULT TRUE,
    ADD COLUMN bio_ka                    TEXT,
    ADD COLUMN bio_en                    TEXT,
    ADD COLUMN last_source_url           TEXT,
    ADD COLUMN last_updated_at           TIMESTAMPTZ,
    ADD COLUMN status                    TEXT         NOT NULL DEFAULT 'ACTIVE'
                                                      CHECK (status IN ('ACTIVE','INACTIVE'));
