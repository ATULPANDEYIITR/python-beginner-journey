DROP SCHEMA IF EXISTS file_writing CASCADE;

CREATE SCHEMA file_writing;

SET search_path TO file_writing, public;

CREATE TYPE file_operation AS ENUM (
    'write',
    'append'
);

CREATE TYPE file_status AS ENUM (
    'active',
    'archived',
    'deleted'
);

CREATE TABLE stored_files (
    file_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    relative_path TEXT NOT NULL UNIQUE,
    status file_status NOT NULL DEFAULT 'active',
    encoding TEXT NOT NULL DEFAULT 'UTF-8',
    byte_size BIGINT NOT NULL DEFAULT 0,
    line_count BIGINT NOT NULL DEFAULT 0,
    version_no INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (relative_path <> ''),
    CHECK (relative_path !~ '(^|/)\.\.(/|$)'),
    CHECK (byte_size >= 0),
    CHECK (line_count >= 0),
    CHECK (version_no > 0)
);

CREATE TABLE file_operations (
    operation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_id BIGINT NOT NULL
        REFERENCES stored_files(file_id)
        ON DELETE CASCADE,
    operation file_operation NOT NULL,
    content TEXT NOT NULL,
    bytes_written BIGINT NOT NULL,
    lines_written BIGINT NOT NULL,
    operation_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (bytes_written >= 0),
    CHECK (lines_written >= 0)
);

CREATE TABLE file_snapshots (
    snapshot_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_id BIGINT NOT NULL
        REFERENCES stored_files(file_id)
        ON DELETE CASCADE,
    version_no INTEGER NOT NULL,
    content TEXT NOT NULL,
    byte_size BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (file_id, version_no),
    CHECK (byte_size >= 0)
);

CREATE INDEX idx_file_operations_file_time
    ON file_operations (file_id, operation_at DESC);

CREATE INDEX idx_stored_files_status
    ON stored_files (status);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_stored_files_updated_at
BEFORE UPDATE ON stored_files
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE FUNCTION validate_relative_path()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.relative_path ~ '(^|/)\.\.(/|$)' THEN
        RAISE EXCEPTION 'Path traversal is not permitted: %',
            NEW.relative_path;
    END IF;

    IF NEW.relative_path LIKE '/%'
       OR NEW.relative_path ~ '^[A-Za-z]:'
    THEN
        RAISE EXCEPTION 'Absolute paths are not permitted: %',
            NEW.relative_path;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_relative_path
BEFORE INSERT OR UPDATE ON stored_files
FOR EACH ROW
EXECUTE FUNCTION validate_relative_path();

CREATE OR REPLACE FUNCTION apply_file_operation(
    p_relative_path TEXT,
    p_operation file_operation,
    p_content TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_file_id BIGINT;
    v_old_content TEXT;
    v_new_content TEXT;
    v_bytes BIGINT;
    v_lines BIGINT;
    v_version INTEGER;
BEGIN
    IF p_relative_path IS NULL OR btrim(p_relative_path) = '' THEN
        RAISE EXCEPTION 'File path cannot be empty';
    END IF;

    IF p_content IS NULL THEN
        RAISE EXCEPTION 'File content cannot be NULL';
    END IF;

    IF p_relative_path ~ '(^|/)\.\.(/|$)' THEN
        RAISE EXCEPTION 'Path traversal is not permitted';
    END IF;

    SELECT file_id, version_no
    INTO v_file_id, v_version
    FROM stored_files
    WHERE relative_path = p_relative_path
    FOR UPDATE;

    IF p_operation = 'write' THEN
        v_new_content := p_content;

        IF v_file_id IS NULL THEN
            INSERT INTO stored_files (
                relative_path,
                byte_size,
                line_count
            )
            VALUES (
                p_relative_path,
                octet_length(v_new_content),
                CASE
                    WHEN v_new_content = '' THEN 0
                    ELSE array_length(
                        string_to_array(v_new_content, E'\n'),
                        1
                    )
                END
            )
            RETURNING file_id, version_no
            INTO v_file_id, v_version;
        ELSE
            v_version := v_version + 1;

            UPDATE stored_files
            SET byte_size = octet_length(v_new_content),
                line_count = CASE
                    WHEN v_new_content = '' THEN 0
                    ELSE array_length(
                        string_to_array(v_new_content, E'\n'),
                        1
                    )
                END,
                version_no = v_version,
                status = 'active'
            WHERE file_id = v_file_id;
        END IF;

    ELSIF p_operation = 'append' THEN
        IF v_file_id IS NULL THEN
            v_new_content := p_content;

            INSERT INTO stored_files (
                relative_path,
                byte_size,
                line_count
            )
            VALUES (
                p_relative_path,
                octet_length(v_new_content),
                CASE
                    WHEN v_new_content = '' THEN 0
                    ELSE array_length(
                        string_to_array(v_new_content, E'\n'),
                        1
                    )
                END
            )
            RETURNING file_id, version_no
            INTO v_file_id, v_version;
        ELSE
            SELECT COALESCE(content, '')
            INTO v_old_content
            FROM file_snapshots
            WHERE file_id = v_file_id
            ORDER BY version_no DESC
            LIMIT 1;

            v_old_content := COALESCE(v_old_content, '');
            v_new_content := v_old_content || p_content;
            v_version := v_version + 1;

            UPDATE stored_files
            SET byte_size = octet_length(v_new_content),
                line_count = CASE
                    WHEN v_new_content = '' THEN 0
                    ELSE array_length(
                        string_to_array(v_new_content, E'\n'),
                        1
                    )
                END,
                version_no = v_version,
                status = 'active'
            WHERE file_id = v_file_id;
        END IF;
    ELSE
        RAISE EXCEPTION 'Unsupported file operation';
    END IF;

    v_bytes := octet_length(p_content);

    v_lines := CASE
        WHEN p_content = '' THEN 0
        ELSE array_length(string_to_array(p_content, E'\n'), 1)
    END;

    INSERT INTO file_operations (
        file_id,
        operation,
        content,
        bytes_written,
        lines_written
    )
    VALUES (
        v_file_id,
        p_operation,
        p_content,
        v_bytes,
        v_lines
    );

    INSERT INTO file_snapshots (
        file_id,
        version_no,
        content,
        byte_size
    )
    VALUES (
        v_file_id,
        v_version,
        v_new_content,
        octet_length(v_new_content)
    )
    ON CONFLICT (file_id, version_no)
    DO UPDATE SET
        content = EXCLUDED.content,
        byte_size = EXCLUDED.byte_size;

    RETURN v_file_id;
END;
$$;

BEGIN;

SELECT apply_file_operation(
    'logs/application.log',
    'write',
    'Application started'
);

SELECT apply_file_operation(
    'logs/application.log',
    'append',
    E'\nConfiguration loaded'
);

SELECT apply_file_operation(
    'logs/application.log',
    'append',
    E'\nDatabase connection established'
);

SELECT apply_file_operation(
    'logs/application.log',
    'append',
    E'\nWorker process started'
);

SELECT apply_file_operation(
    'logs/application.log',
    'append',
    E'\nApplication ready\n'
);

SELECT apply_file_operation(
    'reports/daily.txt',
    'write',
    'Daily report initialized'
);

SELECT apply_file_operation(
    'reports/daily.txt',
    'append',
    E'\nRecords processed: 250'
);

COMMIT;

-- Current file state.
SELECT
    file_id,
    relative_path,
    status,
    encoding,
    byte_size,
    line_count,
    version_no,
    updated_at
FROM stored_files
ORDER BY relative_path;

-- Complete operation history.
SELECT
    f.relative_path,
    o.operation,
    o.bytes_written,
    o.lines_written,
    o.operation_at
FROM file_operations AS o
JOIN stored_files AS f
    ON f.file_id = o.file_id
ORDER BY o.operation_at, o.operation_id;

-- Current content for every file.
SELECT DISTINCT ON (f.file_id)
    f.relative_path,
    s.version_no,
    s.content
FROM stored_files AS f
JOIN file_snapshots AS s
    ON s.file_id = f.file_id
ORDER BY f.file_id, s.version_no DESC;

-- Version history.
SELECT
    f.relative_path,
    s.version_no,
    s.byte_size,
    s.created_at
FROM file_snapshots AS s
JOIN stored_files AS f
    ON f.file_id = s.file_id
ORDER BY f.relative_path, s.version_no;

-- Aggregate operation statistics.
SELECT
    f.relative_path,
    COUNT(*) AS operation_count,
    SUM(o.bytes_written) AS total_bytes_written,
    SUM(o.lines_written) AS total_lines_written,
    COUNT(*) FILTER (WHERE o.operation = 'write') AS write_count,
    COUNT(*) FILTER (WHERE o.operation = 'append') AS append_count
FROM file_operations AS o
JOIN stored_files AS f
    ON f.file_id = o.file_id
GROUP BY f.file_id, f.relative_path
ORDER BY f.relative_path;

-- Find append-heavy files.
SELECT
    f.relative_path,
    COUNT(*) FILTER (WHERE o.operation = 'append') AS append_operations
FROM stored_files AS f
JOIN file_operations AS o
    ON o.file_id = f.file_id
GROUP BY f.file_id, f.relative_path
HAVING COUNT(*) FILTER (WHERE o.operation = 'append') > 1
ORDER BY append_operations DESC;

-- Validation query for files with consistent snapshot metadata.
SELECT
    f.relative_path,
    f.byte_size = s.byte_size AS size_consistent,
    f.version_no = s.version_no AS version_consistent
FROM stored_files AS f
JOIN LATERAL (
    SELECT version_no, byte_size
    FROM file_snapshots
    WHERE file_id = f.file_id
    ORDER BY version_no DESC
    LIMIT 1
) AS s ON TRUE
ORDER BY f.relative_path;

-- Demonstrate transactional rollback for a failed operation.
BEGIN;

SELECT apply_file_operation(
    'logs/temporary.txt',
    'write',
    'This transaction will be rolled back'
);

ROLLBACK;

-- The rolled-back file must not exist.
SELECT *
FROM stored_files
WHERE relative_path = 'logs/temporary.txt';
