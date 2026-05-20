DELETE FROM condition_synonym;
DELETE FROM condition_specialty;
DELETE FROM specialty_alias;
DELETE FROM doctor_specialty;
DELETE FROM doctor;
DELETE FROM medical_condition;
DELETE FROM specialty;

INSERT INTO specialty (slug, name_ka, name_en, sort_order) VALUES
  ('cardiology',  'კარდიოლოგია',  'Cardiology',  10),
  ('dermatology', 'დერმატოლოგია', 'Dermatology', 40);

INSERT INTO specialty_alias (specialty_id, term, lang)
SELECT id, 'heart', 'en' FROM specialty WHERE slug = 'cardiology'
UNION ALL SELECT id, 'გული', 'ka' FROM specialty WHERE slug = 'cardiology'
UNION ALL SELECT id, 'კანი', 'ka' FROM specialty WHERE slug = 'dermatology';

INSERT INTO medical_condition (slug, name_ka, name_en, sort_order) VALUES
  ('hypertension', 'არტერიული ჰიპერტენზია', 'Hypertension', 100);

INSERT INTO condition_specialty (condition_id, specialty_id)
SELECT mc.id, s.id FROM medical_condition mc, specialty s
WHERE mc.slug = 'hypertension' AND s.slug = 'cardiology';

INSERT INTO condition_synonym (condition_id, term, lang)
SELECT id, 'high blood pressure', 'en' FROM medical_condition WHERE slug = 'hypertension'
UNION ALL SELECT id, 'მაღალი წნევა', 'ka' FROM medical_condition WHERE slug = 'hypertension';

INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, specialty_ka, specialty_en) VALUES
  ('giorgi-tsintsadze', 'გიორგი ცინცაძე', 'Giorgi Tsintsadze', 'ACTIVE', true,  false, true, 'https://example.test/g1', now(), 'კარდიოლოგი', 'Cardiologist'),
  ('mariam-beridze',    'მარიამ ბერიძე',  'Mariam Beridze',    'ACTIVE', false, true,  true, 'https://example.test/m1', now(), 'კარდიოლოგი', 'Cardiologist');

INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
SELECT d.id, s.id, true FROM doctor d, specialty s
WHERE (d.slug = 'giorgi-tsintsadze' AND s.slug = 'cardiology')
   OR (d.slug = 'mariam-beridze'    AND s.slug = 'cardiology');
