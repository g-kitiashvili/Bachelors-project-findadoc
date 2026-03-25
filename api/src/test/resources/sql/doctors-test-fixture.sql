DELETE FROM doctor_specialty;
DELETE FROM specialty;
DELETE FROM doctor;

INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, specialty_ka, specialty_en) VALUES
  ('giorgi-tsintsadze',  'გიორგი ცინცაძე',  'Giorgi Tsintsadze',  'ACTIVE',   true,  false, true,  'https://example.test/g1', now(), 'კარდიოლოგი',      'Cardiologist'),
  ('mariam-beridze',     'მარიამ ბერიძე',    'Mariam Beridze',     'ACTIVE',   true,  true,  true,  'https://example.test/m1', now(), 'ნეიროლოგი',       'Neurologist'),
  ('nika-kapanadze',     'ნიკა კაპანაძე',    'Nika Kapanadze',     'ACTIVE',   false, false, true,  'https://example.test/n1', now(), NULL,              NULL),
  ('davit-gelashvili',   'დავით გელაშვილი',  'Davit Gelashvili',   'ACTIVE',   true,  false, true,  'https://example.test/d1', now(), 'პედიატრი',        NULL),
  ('ana-eradze',         'ანა ერაძე',        'Ana Eradze',         'ACTIVE',   true,  true,  false, 'https://example.test/a1', now(), 'ენდოკრინოლოგი',   'Endocrinologist'),
  ('luka-javakhishvili', 'ლუკა ჯავახიშვილი', 'Luka Javakhishvili', 'ACTIVE',   true,  false, true,  'https://example.test/l1', now(), 'გასტროენტეროლოგი','Gastroenterologist'),
  ('tamar-maisuradze',   'თამარ მაისურაძე',  'Tamar Maisuradze',   'ACTIVE',   true,  false, true,  'https://example.test/t1', now(), NULL,              NULL),
  ('inactive-test',      'ი ნაქტივი',        'Inactive Test',      'INACTIVE', true,  false, true,  'https://example.test/inactive', now(), NULL, NULL);

INSERT INTO specialty (slug, name_ka, name_en, description_ka, description_en, sort_order) VALUES
  ('cardiology',  'კარდიოლოგია',  'Cardiology',  'KA description', 'EN description', 10),
  ('neurology',   'ნევროლოგია',   'Neurology',   'KA description', 'EN description', 70),
  ('pediatrics',  'პედიატრია',    'Pediatrics',  'KA description', 'EN description', 20),
  ('dermatology', 'დერმატოლოგია', 'Dermatology', NULL,             NULL,             40),
  ('surgery',     'ქირურგია',     'Surgery',     NULL,             NULL,             50),
  ('immunology',  'იმუნოლოგია',   'Immunology',  NULL,             NULL,             90);

INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
SELECT d.id, s.id, true
FROM doctor d, specialty s
WHERE (d.slug = 'giorgi-tsintsadze'  AND s.slug = 'cardiology')
   OR (d.slug = 'mariam-beridze'     AND s.slug = 'cardiology')
   OR (d.slug = 'nika-kapanadze'     AND s.slug = 'neurology')
   OR (d.slug = 'davit-gelashvili'   AND s.slug = 'pediatrics')
   OR (d.slug = 'luka-javakhishvili' AND s.slug = 'dermatology')
   OR (d.slug = 'tamar-maisuradze'   AND s.slug = 'surgery');

INSERT INTO doctor_specialty (doctor_id, specialty_id, is_primary)
SELECT d.id, s.id, false
FROM doctor d, specialty s
WHERE d.slug = 'luka-javakhishvili' AND s.slug = 'neurology';
