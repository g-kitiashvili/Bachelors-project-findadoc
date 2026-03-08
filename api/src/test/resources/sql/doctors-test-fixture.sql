INSERT INTO doctor (slug, full_name_ka, full_name_en, status, is_accepting_new_patients, treats_children, treats_adults) VALUES
  ('a-test', 'ა ტესტი', 'A Test', 'ACTIVE',   true,  false, true),
  ('b-test', 'ბ ტესტი', 'B Test', 'ACTIVE',   true,  true,  true),
  ('c-test', 'გ ტესტი', 'C Test', 'ACTIVE',   false, false, true),
  ('d-test', 'დ ტესტი', 'D Test', 'ACTIVE',   true,  false, true),
  ('e-test', 'ე ტესტი', 'E Test', 'ACTIVE',   true,  true,  false),
  ('f-test', 'ვ ტესტი', 'F Test', 'ACTIVE',   true,  false, true),
  ('g-test', 'ზ ტესტი', 'G Test', 'ACTIVE',   true,  false, true),
  ('inactive-test', 'ი ნაქტივი', 'Inactive Test', 'INACTIVE', true, false, true);
