ALTER TABLE doctor ADD COLUMN merged_into_id BIGINT REFERENCES doctor(id);
ALTER TABLE doctor DROP CONSTRAINT doctor_status_check;
ALTER TABLE doctor ADD CONSTRAINT doctor_status_check
    CHECK (status IN ('ACTIVE','INACTIVE','MERGED'));
CREATE INDEX doctor_merged_into_id ON doctor (merged_into_id);

ALTER TABLE clinic ADD COLUMN merged_into_id BIGINT REFERENCES clinic(id);
CREATE INDEX clinic_merged_into_id ON clinic (merged_into_id);

ALTER TABLE doctor_clinic    ADD COLUMN via_merge BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE doctor_specialty ADD COLUMN via_merge BOOLEAN NOT NULL DEFAULT FALSE;
