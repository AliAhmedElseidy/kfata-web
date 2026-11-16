\pset pager off
BEGIN READ ONLY;
SELECT current_setting('server_version') AS server_version,
       rolsuper, rolcreaterole, rolcreatedb, rolreplication, rolbypassrls
FROM pg_roles WHERE rolname = current_user;
SELECT count(*) FILTER (WHERE am.amname = 'gin') AS gin_indexes,
       count(*) FILTER (WHERE am.amname = 'brin') AS brin_indexes,
       count(*) FILTER (WHERE am.amname = 'gist' AND EXISTS (
          SELECT 1 FROM unnest(ix.indclass) AS c(id)
          JOIN pg_opclass oc ON oc.oid = c.id WHERE oc.opcname = 'gist_trgm_ops'
       )) AS trgm_gist_indexes,
       count(*) FILTER (WHERE am.amname = 'btree' AND EXISTS (
          SELECT 1 FROM pg_attribute a WHERE a.attrelid = idx.oid
          AND a.atttypid = 'bpchar'::regtype AND a.atttypmod = -1
       )) AS unconstrained_bpchar_btree_indexes,
       count(*) FILTER (WHERE NOT ix.indisvalid) AS invalid_indexes
FROM pg_index ix JOIN pg_class idx ON idx.oid = ix.indexrelid
JOIN pg_namespace n ON n.oid = idx.relnamespace JOIN pg_am am ON am.oid = idx.relam
WHERE n.nspname = 'public';
COMMIT;
