DELETE FROM doctor_clinic; DELETE FROM clinic; DELETE FROM clinic_brand;
INSERT INTO clinic_brand (slug, name_ka, name_en) VALUES ('acme', 'აკმე', 'Acme');
INSERT INTO clinic (slug, name_ka, name_en, last_source_url, brand_id, address, location) VALUES
  ('alpha-clinic', 'ალფა', 'Alpha Clinic', 'https://t.test/k/alpha',
     (SELECT id FROM clinic_brand WHERE slug='acme'), 'Rustaveli 1', NULL),
  ('beta-clinic',  'ბეტა', 'Beta Clinic',  'https://t.test/k/beta', NULL, NULL, NULL),
  ('alpha-saburtalo', 'ალფა საბურთალო', 'Alpha Saburtalo', 'https://t.test/k/alpha-sab',
     (SELECT id FROM clinic_brand WHERE slug='acme'), 'Vaja 5',
     ST_SetSRID(ST_MakePoint(44.77, 41.72), 4326)::geography);
INSERT INTO doctor_clinic (doctor_id, clinic_id)
SELECT d.id, c.id FROM doctor d, clinic c WHERE d.slug='doc-kutaisi' AND c.slug='alpha-clinic';
