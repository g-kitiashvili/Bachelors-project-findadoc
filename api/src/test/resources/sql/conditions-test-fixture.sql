DELETE FROM condition_specialty;
DELETE FROM medical_condition;
DELETE FROM doctor_specialty;
DELETE FROM specialty;
DELETE FROM doctor;

INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, specialty_ka, specialty_en) VALUES
  ('giorgi-tsintsadze',  'გიორგი ცინცაძე',  'Giorgi Tsintsadze',  'ACTIVE',   true,  false, true,  'https://example.test/g1', now(), 'კარდიოლოგი', 'Cardiologist'),
  ('mariam-beridze',     'მარიამ ბერიძე',    'Mariam Beridze',     'ACTIVE',   false, true,  true,  'https://example.test/m1', now(), 'კარდიოლოგი', 'Cardiologist'),
  ('davit-gelashvili',   'დავით გელაშვილი',  'Davit Gelashvili',   'ACTIVE',   true,  false, true,  'https://example.test/d1', now(), 'პედიატრი',   'Pediatrician'),
  ('inactive-test',      'ი ნაქტივი',        'Inactive Test',      'INACTIVE', true,  false, true,  'https://example.test/inactive', now(), NULL, NULL);

UPDATE doctor SET family_name_ka = split_part(full_name_ka, ' ', -1),
                  family_name_en = split_part(full_name_en, ' ', -1);

INSERT INTO specialty (slug, name_ka, name_en, description_ka, description_en, sort_order) VALUES
  ('cardiology', 'კარდიოლოგია', 'Cardiology', 'KA description', 'EN description', 10),
  ('pediatrics', 'პედიატრია',   'Pediatrics', 'KA description', 'EN description', 20);

INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
SELECT d.id, s.id, true
FROM doctor d, specialty s
WHERE (d.slug = 'giorgi-tsintsadze' AND s.slug = 'cardiology')
   OR (d.slug = 'mariam-beridze'    AND s.slug = 'cardiology')
   OR (d.slug = 'davit-gelashvili'  AND s.slug = 'pediatrics')
   OR (d.slug = 'inactive-test'     AND s.slug = 'cardiology');

INSERT INTO medical_condition (slug, name_ka, name_en, description_ka, description_en, sort_order) VALUES
  ('hypertension', 'არტერიული ჰიპერტენზია', 'Hypertension', 'KA description', 'EN description', 100),
  ('migraine',     'შაკიკი',                'Migraine',     NULL,             NULL,             200);

INSERT INTO condition_specialty (condition_id, specialty_id)
SELECT mc.id, s.id
FROM medical_condition mc, specialty s
WHERE mc.slug = 'hypertension' AND s.slug = 'cardiology';
