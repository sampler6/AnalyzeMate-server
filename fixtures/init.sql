CREATE DATABASE analyzemate;
\connect analyzemate;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
SELECT set_similarity(0.5);