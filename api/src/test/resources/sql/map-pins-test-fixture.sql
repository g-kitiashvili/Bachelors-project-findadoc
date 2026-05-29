DELETE FROM doctor_clinic;
DELETE FROM clinic;
DELETE FROM doctor;

INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at) VALUES
  ('doc-near', 'ახლო ექიმი', 'Near Doctor', 'ACTIVE', true, false, true, 'https://example.test/n', now()),
  ('doc-far',  'შორი ექიმი', 'Far Doctor',  'ACTIVE', true, false, true, 'https://example.test/f', now());

UPDATE doctor SET family_name_ka = split_part(full_name_ka, ' ', -1),
                  family_name_en = split_part(full_name_en, ' ', -1);

INSERT INTO clinic (slug, name_ka, name_en, last_source_url, last_updated_at, status, location) VALUES
  ('near-clinic', 'ახლო კლინიკა', 'Near Clinic', 'https://example.test/cn', now(), 'ACTIVE', ST_SetSRID(ST_MakePoint(44.800, 41.700), 4326)::geography),
  ('far-clinic',  'შორი კლინიკა', 'Far Clinic',  'https://example.test/cf', now(), 'ACTIVE', ST_SetSRID(ST_MakePoint(42.270, 42.250), 4326)::geography),
  ('no-loc-clinic', 'უადგილო', 'No Location Clinic', 'https://example.test/cnl', now(), 'ACTIVE', NULL);

INSERT INTO doctor_clinic (doctor_id, clinic_id)
SELECT d.id, c.id FROM doctor d, clinic c
WHERE (d.slug = 'doc-near' AND c.slug = 'near-clinic')
   OR (d.slug = 'doc-near' AND c.slug = 'far-clinic')  -- doc-near also practices at far-clinic
   OR (d.slug = 'doc-far'  AND c.slug = 'far-clinic');
