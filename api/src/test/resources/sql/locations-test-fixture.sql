DELETE FROM doctor_specialty;
DELETE FROM doctor;
DELETE FROM specialty;
DELETE FROM location;

INSERT INTO location (slug, name_ka, name_en, parent_id, sort_order) VALUES
  ('tbilisi', 'თბილისი', 'Tbilisi', NULL, 10),
  ('imereti', 'იმერეთი', 'Imereti', NULL, 20);

INSERT INTO location (slug, name_ka, name_en, parent_id, sort_order)
SELECT 'kutaisi', 'ქუთაისი', 'Kutaisi', id, 10 FROM location WHERE slug = 'imereti';

INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES
  ('cardiology', 'კარდიოლოგია', 'Cardiology', 10);

INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, location_id)
SELECT 'doc-tbilisi', 'თბ ექიმი', 'Tbilisi Doc', 'ACTIVE', true, false, true, 'https://example.test/loc-tb', now(), id
FROM location WHERE slug = 'tbilisi';

INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, location_id)
SELECT 'doc-kutaisi', 'ქუთ ექიმი', 'Kutaisi Doc', 'ACTIVE', true, false, true, 'https://example.test/loc-kt', now(), id
FROM location WHERE slug = 'kutaisi';

INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, location_id)
VALUES ('doc-nowhere', 'უ ადგილო', 'Nowhere Doc', 'ACTIVE', true, false, true, 'https://example.test/loc-nl', now(), NULL);

INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
SELECT d.id, s.id, true FROM doctor d, specialty s
WHERE d.slug = 'doc-kutaisi' AND s.slug = 'cardiology';
