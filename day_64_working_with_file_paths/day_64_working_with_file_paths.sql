DROP SCHEMA IF EXISTS file_path_demo CASCADE;

CREATE SCHEMA file_path_demo;

SET search_path TO file_path_demo;

CREATE TYPE node_type AS ENUM ('file', 'directory');

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    root_path TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (length(trim(name)) > 0),
    CHECK (length(root_path) > 0)
);

CREATE TABLE filesystem_nodes (
    node_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    parent_id BIGINT
        REFERENCES filesystem_nodes(node_id)
        ON DELETE CASCADE,
    node_name TEXT NOT NULL,
    node_type node_type NOT NULL,
    relative_path TEXT NOT NULL,
    size_bytes BIGINT,
    checksum TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (repository_id, relative_path),
    CHECK (length(trim(node_name)) > 0),
    CHECK (position(E'\0' in node_name) = 0),
    CHECK (position(E'\0' in relative_path) = 0),
    CHECK (size_bytes IS NULL OR size_bytes >= 0),
    CHECK (
        (node_type = 'file' AND size_bytes IS NOT NULL)
        OR
        (node_type = 'directory' AND size_bytes IS NULL)
    )
);

CREATE INDEX idx_nodes_repository_parent
    ON filesystem_nodes(repository_id, parent_id);

CREATE INDEX idx_nodes_repository_type
    ON filesystem_nodes(repository_id, node_type);

CREATE INDEX idx_nodes_relative_path
    ON filesystem_nodes(repository_id, relative_path);

CREATE TABLE path_access_policies (
    policy_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    allowed_prefix TEXT NOT NULL,
    allow_read BOOLEAN NOT NULL DEFAULT TRUE,
    allow_write BOOLEAN NOT NULL DEFAULT FALSE,
    allow_delete BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (repository_id, allowed_prefix),
    CHECK (length(allowed_prefix) > 0)
);

CREATE TABLE path_operations (
    operation_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    operation_type TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        operation_type IN (
            'read',
            'write',
            'copy',
            'move',
            'delete',
            'list'
        )
    ),
    CHECK (
        status IN ('accepted', 'completed', 'rejected', 'failed')
    ),
    CHECK (length(relative_path) > 0)
);

CREATE OR REPLACE FUNCTION validate_relative_path(
    input_path TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    part TEXT;
BEGIN
    IF input_path IS NULL OR length(trim(input_path)) = 0 THEN
        RETURN FALSE;
    END IF;

    IF position(E'\0' in input_path) > 0 THEN
        RETURN FALSE;
    END IF;

    IF left(input_path, 1) = '/' THEN
        RETURN FALSE;
    END IF;

    IF input_path ~ '^[A-Za-z]:[\\/]' THEN
        RETURN FALSE;
    END IF;

    FOREACH part IN ARRAY string_to_array(
        replace(input_path, '\', '/'),
        '/'
    )
    LOOP
        IF part = '..' THEN
            RETURN FALSE;
        END IF;
    END LOOP;

    RETURN TRUE;
END;
$$;

ALTER TABLE filesystem_nodes
ADD CONSTRAINT valid_relative_path
CHECK (validate_relative_path(relative_path));

ALTER TABLE path_access_policies
ADD CONSTRAINT valid_policy_prefix
CHECK (validate_relative_path(allowed_prefix));

CREATE OR REPLACE FUNCTION update_node_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_nodes_updated
BEFORE UPDATE ON filesystem_nodes
FOR EACH ROW
EXECUTE FUNCTION update_node_timestamp();

CREATE OR REPLACE FUNCTION prevent_invalid_parent()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    parent_type node_type;
    parent_repository BIGINT;
BEGIN
    IF NEW.parent_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT node_type, repository_id
    INTO parent_type, parent_repository
    FROM filesystem_nodes
    WHERE node_id = NEW.parent_id;

    IF parent_type IS DISTINCT FROM 'directory' THEN
        RAISE EXCEPTION
            'Parent node % must be a directory',
            NEW.parent_id;
    END IF;

    IF parent_repository <> NEW.repository_id THEN
        RAISE EXCEPTION
            'Parent and child must belong to the same repository';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_parent
BEFORE INSERT OR UPDATE ON filesystem_nodes
FOR EACH ROW
EXECUTE FUNCTION prevent_invalid_parent();

CREATE OR REPLACE FUNCTION path_extension(input_path TEXT)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT CASE
        WHEN position('.' IN reverse(split_part(input_path, '/', -1))) > 1
        THEN lower(
            substring(
                split_part(input_path, '/', -1)
                FROM position(
                    '.' IN reverse(split_part(input_path, '/', -1))
                )
            )
        )
        ELSE '[no extension]'
    END;
$$;

INSERT INTO repositories (name, root_path)
VALUES
    ('operations', '/srv/app/operations'),
    ('archive', '/srv/app/archive');

INSERT INTO filesystem_nodes (
    repository_id,
    parent_id,
    node_name,
    node_type,
    relative_path,
    size_bytes,
    checksum
)
SELECT
    repository_id,
    NULL,
    'reports',
    'directory',
    'reports',
    NULL,
    NULL
FROM repositories
WHERE name = 'operations';

INSERT INTO filesystem_nodes (
    repository_id,
    parent_id,
    node_name,
    node_type,
    relative_path,
    size_bytes,
    checksum
)
SELECT
    repository_id,
    node_id,
    '2026',
    'directory',
    'reports/2026',
    NULL,
    NULL
FROM repositories r
JOIN filesystem_nodes n
    ON n.repository_id = r.repository_id
WHERE r.name = 'operations'
  AND n.relative_path = 'reports';

INSERT INTO filesystem_nodes (
    repository_id,
    parent_id,
    node_name,
    node_type,
    relative_path,
    size_bytes,
    checksum
)
SELECT
    repository_id,
    node_id,
    'report.csv',
    'file',
    'reports/2026/report.csv',
    2450,
    'sha256:abc123'
FROM repositories r
JOIN filesystem_nodes n
    ON n.repository_id = r.repository_id
WHERE r.name = 'operations'
  AND n.relative_path = 'reports/2026';

INSERT INTO filesystem_nodes (
    repository_id,
    parent_id,
    node_name,
    node_type,
    relative_path,
    size_bytes,
    checksum
)
SELECT
    repository_id,
    node_id,
    'report.txt',
    'file',
    'reports/2026/report.txt',
    918,
    'sha256:def456'
FROM repositories r
JOIN filesystem_nodes n
    ON n.repository_id = r.repository_id
WHERE r.name = 'operations'
  AND n.relative_path = 'reports/2026';

INSERT INTO path_access_policies (
    repository_id,
    allowed_prefix,
    allow_read,
    allow_write,
    allow_delete
)
SELECT
    repository_id,
    'reports',
    TRUE,
    TRUE,
    FALSE
FROM repositories
WHERE name = 'operations';

INSERT INTO path_access_policies (
    repository_id,
    allowed_prefix,
    allow_read,
    allow_write,
    allow_delete
)
SELECT
    repository_id,
    'reports/2026',
    TRUE,
    FALSE,
    FALSE
FROM repositories
WHERE name = 'operations';

INSERT INTO path_operations (
    repository_id,
    operation_type,
    relative_path,
    status
)
SELECT
    repository_id,
    'read',
    'reports/2026/report.csv',
    'completed'
FROM repositories
WHERE name = 'operations';

INSERT INTO path_operations (
    repository_id,
    operation_type,
    relative_path,
    status,
    error_message
)
SELECT
    repository_id,
    'read',
    '../outside.txt',
    'rejected',
    'Path traversal is not permitted'
FROM repositories
WHERE name = 'operations';

INSERT INTO path_operations (
    repository_id,
    operation_type,
    relative_path,
    status
)
SELECT
    repository_id,
    'write',
    'reports/2026/report.txt',
    'completed'
FROM repositories
WHERE name = 'operations';

-- Retrieve every file in a repository.
SELECT
    r.name AS repository,
    n.relative_path,
    n.size_bytes,
    n.checksum
FROM repositories r
JOIN filesystem_nodes n
    ON n.repository_id = r.repository_id
WHERE r.name = 'operations'
  AND n.node_type = 'file'
ORDER BY n.relative_path;

-- Extension-based reporting.
SELECT
    path_extension(relative_path) AS extension,
    COUNT(*) AS file_count,
    SUM(size_bytes) AS total_bytes
FROM filesystem_nodes
WHERE node_type = 'file'
GROUP BY path_extension(relative_path)
ORDER BY extension;

-- Validate paths before accepting an operation.
WITH candidate_paths(path) AS (
    VALUES
        ('reports/2026/report.csv'),
        ('reports/../outside.txt'),
        ('/etc/passwd'),
        ('reports/new.txt')
)
SELECT
    path,
    validate_relative_path(path) AS valid
FROM candidate_paths;

-- Evaluate whether an operation is covered by an access policy.
SELECT
    o.operation_id,
    o.relative_path,
    o.operation_type,
    o.status,
    EXISTS (
        SELECT 1
        FROM path_access_policies p
        WHERE p.repository_id = o.repository_id
          AND (
              o.relative_path = p.allowed_prefix
              OR o.relative_path LIKE p.allowed_prefix || '/%'
          )
          AND CASE o.operation_type
              WHEN 'read' THEN p.allow_read
              WHEN 'list' THEN p.allow_read
              WHEN 'write' THEN p.allow_write
              WHEN 'copy' THEN p.allow_write
              WHEN 'move' THEN p.allow_write
              WHEN 'delete' THEN p.allow_delete
              ELSE FALSE
          END
    ) AS policy_allows_operation
FROM path_operations o
ORDER BY o.operation_id;

-- Report successful and rejected operations.
SELECT
    status,
    COUNT(*) AS operation_count
FROM path_operations
GROUP BY status
ORDER BY status;

-- Transactional workflow: record an accepted write.
BEGIN;

INSERT INTO path_operations (
    repository_id,
    operation_type,
    relative_path,
    status
)
SELECT
    repository_id,
    'write',
    'reports/2026/new-report.csv',
    'accepted'
FROM repositories
WHERE name = 'operations';

UPDATE path_operations
SET status = 'completed'
WHERE operation_id = (
    SELECT MAX(operation_id)
    FROM path_operations
    WHERE operation_type = 'write'
      AND relative_path = 'reports/2026/new-report.csv'
);

COMMIT;

-- The following query gives a compact operational view.
SELECT
    r.name AS repository,
    COUNT(*) FILTER (WHERE n.node_type = 'directory') AS directories,
    COUNT(*) FILTER (WHERE n.node_type = 'file') AS files,
    COALESCE(SUM(n.size_bytes) FILTER (
        WHERE n.node_type = 'file'
    ), 0) AS total_file_bytes
FROM repositories r
LEFT JOIN filesystem_nodes n
    ON n.repository_id = r.repository_id
GROUP BY r.repository_id, r.name
ORDER BY r.name;
