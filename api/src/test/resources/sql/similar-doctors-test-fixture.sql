DELETE FROM doctor_clinic; DELETE FROM doctor_specialty; DELETE FROM doctor; DELETE FROM clinic; DELETE FROM specialty; DELETE FROM location;

INSERT INTO location (slug, name_ka, name_en, parent_id, sort_order) VALUES
  ('tbilisi', 'თბილისი', 'Tbilisi', NULL, 10),
  ('imereti', 'იმერეთი', 'Imereti', NULL, 20);
INSERT INTO location (slug, name_ka, name_en, parent_id, sort_order)
SELECT 'kutaisi', 'ქუთაისი', 'Kutaisi', id, 10 FROM location WHERE slug = 'imereti';

INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES
  ('cardiology', 'კარდიოლოგია', 'Cardiology', 10),
  ('dermatology', 'დერმატოლოგია', 'Dermatology', 20);

INSERT INTO doctor (slug, full_name_ka, full_name_en, family_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, location_id)
SELECT 'sim-target', 'სამიზნე ექიმი', 'Target Doc', 'Target', 'ACTIVE', true, false, true, 'https://t/sim-target', now(), id FROM location WHERE slug = 'tbilisi';
INSERT INTO doctor (slug, full_name_ka, full_name_en, family_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, location_id)
SELECT 'sim-samecity', 'იმავე ქალაქის ექიმი', 'Samecity Doc', 'Samecity', 'ACTIVE', true, false, true, 'https://t/sim-samecity', now(), id FROM location WHERE slug = 'tbilisi';
INSERT INTO doctor (slug, full_name_ka, full_name_en, family_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, location_id)
SELECT 'sim-othercity', 'სხვა ქალაქის ექიმი', 'Othercity Doc', 'Othercity', 'ACTIVE', true, false, true, 'https://t/sim-othercity', now(), id FROM location WHERE slug = 'kutaisi';
INSERT INTO doctor (slug, full_name_ka, full_name_en, family_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, location_id)
SELECT 'sim-derm', 'დერმატოლოგი', 'Derm Doc', 'Derm', 'ACTIVE', true, false, true, 'https://t/sim-derm', now(), id FROM location WHERE slug = 'tbilisi';
INSERT INTO doctor (slug, full_name_ka, full_name_en, family_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, location_id)
SELECT 'sim-merged', 'შერწყმული ექიმი', 'Merged Doc', 'Merged', 'MERGED', true, false, true, 'https://t/sim-merged', now(), id FROM location WHERE slug = 'tbilisi';

-- cardiology: target + same-city peer + other-city peer + a merged one (must be excluded)
INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
SELECT d.id, s.id, true FROM doctor d, specialty s
WHERE s.slug = 'cardiology' AND d.slug IN ('sim-target', 'sim-samecity', 'sim-othercity', 'sim-merged');
-- dermatology only: shares no specialty with the target (must be excluded)
INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
SELECT d.id, s.id, true FROM doctor d, specialty s
WHERE s.slug = 'dermatology' AND d.slug = 'sim-derm';
