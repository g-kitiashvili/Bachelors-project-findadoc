CREATE TABLE condition_synonym (
    condition_id  BIGINT NOT NULL REFERENCES medical_condition(id) ON DELETE CASCADE,
    term          TEXT   NOT NULL,
    lang          TEXT   NOT NULL,
    PRIMARY KEY (condition_id, lang, term)
);
CREATE INDEX condition_synonym_term_trgm ON condition_synonym USING gin (lower(term) gin_trgm_ops);

CREATE TABLE specialty_alias (
    specialty_id  BIGINT NOT NULL REFERENCES specialty(id) ON DELETE CASCADE,
    term          TEXT   NOT NULL,
    lang          TEXT   NOT NULL,
    PRIMARY KEY (specialty_id, lang, term)
);
CREATE INDEX specialty_alias_term_trgm ON specialty_alias USING gin (lower(term) gin_trgm_ops);
