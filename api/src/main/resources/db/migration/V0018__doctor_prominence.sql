-- Precomputed, explainable ranking score (0-100) written by the pipeline `prominence`
-- pass. Drives the default browse order and breaks ties in relevance search.
ALTER TABLE doctor ADD COLUMN prominence REAL NOT NULL DEFAULT 0;

CREATE INDEX doctor_prominence ON doctor (status, prominence DESC);
