DELETE FROM doctor_clinic;
DELETE FROM doctor_specialty;
DELETE FROM doctor;
DELETE FROM clinic;
DELETE FROM specialty;

INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES
  ('cardiology','კარდიოლოგია','Cardiology',10);

INSERT INTO clinic (slug, name_ka, name_en, last_source_url, last_updated_at, status, merged_into_id) VALUES
  ('alpha-canonical','ალფა','Alpha Clinic','https://example.test/a1', now(), 'ACTIVE', NULL);
INSERT INTO clinic (slug, name_ka, name_en, last_source_url, last_updated_at, status, merged_into_id) VALUES
  ('alpha-merged','ალფა','Alpha Clinic','https://example.test/a2', now(), 'MERGED',
     (SELECT id FROM clinic WHERE slug='alpha-canonical'));

INSERT INTO doctor (slug, full_name_ka, full_name_en, last_source_url, last_updated_at, status, merged_into_id) VALUES
  ('canon-doc','კ დ','Canon Doc','https://example.test/c1', now(), 'ACTIVE', NULL);
INSERT INTO doctor (slug, full_name_ka, full_name_en, last_source_url, last_updated_at, status, merged_into_id) VALUES
  ('merged-doc','კ დ','Canon Doc','https://example.test/c2', now(), 'MERGED',
     (SELECT id FROM doctor WHERE slug='canon-doc'));

INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
SELECT d.id, s.id, true FROM doctor d, specialty s
WHERE d.slug='canon-doc' AND s.slug='cardiology';

-- canon-doc is linked to both canonical and merged clinic (merged clinic still has a stale doctor link)
INSERT INTO doctor_clinic (doctor_id, clinic_id)
SELECT d.id, c.id FROM doctor d, clinic c
WHERE d.slug='canon-doc' AND c.slug='alpha-canonical';

INSERT INTO doctor_clinic (doctor_id, clinic_id)
SELECT d.id, c.id FROM doctor d, clinic c
WHERE d.slug='canon-doc' AND c.slug='alpha-merged';
