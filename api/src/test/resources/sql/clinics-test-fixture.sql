DELETE FROM doctor_clinic; DELETE FROM clinic;
INSERT INTO clinic (slug, name_ka, name_en, last_source_url) VALUES
  ('alpha-clinic', 'ალფა', 'Alpha Clinic', 'https://t.test/k/alpha'),
  ('beta-clinic',  'ბეტა', 'Beta Clinic',  'https://t.test/k/beta');
INSERT INTO doctor_clinic (doctor_id, clinic_id)
SELECT d.id, c.id FROM doctor d, clinic c WHERE d.slug='doc-kutaisi' AND c.slug='alpha-clinic';
