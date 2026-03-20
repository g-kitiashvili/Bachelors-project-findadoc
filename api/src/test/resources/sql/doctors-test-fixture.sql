DELETE FROM doctor;

INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults, last_source_url, last_updated_at, specialty_ka, specialty_en) VALUES
  ('a-test', 'ა ტესტი', 'A Test', 'ACTIVE',   true,  false, true, 'https://example.test/a', now(), 'კარდიოლოგი', 'Cardiologist'),
  ('b-test', 'ბ ტესტი', 'B Test', 'ACTIVE',   true,  true,  true, 'https://example.test/b', now(), 'ნეიროლოგი', 'Neurologist'),
  ('c-test', 'გ ტესტი', 'C Test', 'ACTIVE',   false, false, true, 'https://example.test/c', now(), NULL, NULL),
  ('d-test', 'დ ტესტი', 'D Test', 'ACTIVE',   true,  false, true, 'https://example.test/d', now(), 'პედიატრი', NULL),
  ('e-test', 'ე ტესტი', 'E Test', 'ACTIVE',   true,  true,  false, 'https://example.test/e', now(), 'ენდოკრინოლოგი', 'Endocrinologist'),
  ('f-test', 'ვ ტესტი', 'F Test', 'ACTIVE',   true,  false, true, 'https://example.test/f', now(), NULL, NULL),
  ('g-test', 'ზ ტესტი', 'G Test', 'ACTIVE',   true,  false, true, 'https://example.test/g', now(), NULL, NULL),
  ('inactive-test', 'ი ნაქტივი', 'Inactive Test', 'INACTIVE', true, false, true, 'https://example.test/inactive', now(), NULL, NULL);
