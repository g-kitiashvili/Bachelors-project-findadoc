DELETE FROM doctor_specialty;
DELETE FROM specialty;
DELETE FROM doctor;

INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES
  ('surgery', 'ქირურგია', 'Surgery', 50);

INSERT INTO specialty (slug, name_ka, name_en, sort_order, parent_id)
SELECT 'maxillofacial-surgery', 'ყბა-სახის ქირურგია', 'Maxillofacial Surgery', 52, id
FROM specialty WHERE slug = 'surgery';

INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at) VALUES
  ('plain-surgeon', 'გია ქირურგი', 'Gia Surgeon', 'ACTIVE', true, false, true, 'https://example.test/s1', now()),
  ('jaw-surgeon',   'ნინო ყბა',     'Nino Jaw',     'ACTIVE', true, false, true, 'https://example.test/s2', now());

UPDATE doctor SET family_name_ka = split_part(full_name_ka, ' ', -1),
                  family_name_en = split_part(full_name_en, ' ', -1);

INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
SELECT d.id, s.id, true FROM doctor d, specialty s
WHERE (d.slug = 'plain-surgeon' AND s.slug = 'surgery')
   OR (d.slug = 'jaw-surgeon'   AND s.slug = 'maxillofacial-surgery');
