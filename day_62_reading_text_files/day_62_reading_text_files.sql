DROP SCHEMA IF EXISTS text_file_learning CASCADE;
CREATE SCHEMA text_file_learning;

SET search_path TO text_file_learning;

CREATE TABLE text_documents (
    document_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_name TEXT NOT NULL,
    encoding_name TEXT NOT NULL DEFAULT 'UTF-8',
    content TEXT NOT NULL,
    byte_size INTEGER GENERATED ALWAYS AS (
        octet_length(content)
    ) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT text_documents_file_name_ck
        CHECK (length(trim(file_name)) > 0),
    CONSTRAINT text_documents_encoding_ck
        CHECK (length(trim(encoding_name)) > 0),
    CONSTRAINT text_documents_size_ck
        CHECK (octet_length(content) <= 5242880)
);

CREATE TABLE document_lines (
    line_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id BIGINT NOT NULL
        REFERENCES text_documents(document_id)
        ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    line_text TEXT NOT NULL,
    character_count INTEGER GENERATED ALWAYS AS (
        char_length(line_text)
    ) STORED,
    is_empty BOOLEAN GENERATED ALWAYS AS (
        length(trim(line_text)) = 0
    ) STORED,
    CONSTRAINT document_lines_number_ck
        CHECK (line_number > 0),
    CONSTRAINT document_lines_unique_number
        UNIQUE (document_id, line_number)
);

CREATE TABLE document_words (
    document_id BIGINT NOT NULL
        REFERENCES text_documents(document_id)
        ON DELETE CASCADE,
    normalized_word TEXT NOT NULL,
    occurrence_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (document_id, normalized_word),
    CONSTRAINT document_words_word_ck
        CHECK (length(normalized_word) > 0),
    CONSTRAINT document_words_count_ck
        CHECK (occurrence_count >= 0)
);

CREATE INDEX document_lines_document_line_idx
    ON document_lines(document_id, line_number);

CREATE INDEX document_words_frequency_idx
    ON document_words(document_id, occurrence_count DESC);

CREATE INDEX text_documents_file_name_idx
    ON text_documents(file_name);

CREATE OR REPLACE FUNCTION validate_text_document()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.content IS NULL THEN
        RAISE EXCEPTION 'Document content cannot be NULL';
    END IF;

    IF octet_length(NEW.content) > 5242880 THEN
        RAISE EXCEPTION
            'Text document exceeds the 5 MiB size limit';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER text_documents_validate_trg
BEFORE INSERT OR UPDATE ON text_documents
FOR EACH ROW
EXECUTE FUNCTION validate_text_document();

CREATE OR REPLACE FUNCTION populate_document_lines(
    p_document_id BIGINT,
    p_content TEXT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    current_line TEXT;
    current_number INTEGER := 0;
BEGIN
    DELETE FROM document_lines
    WHERE document_id = p_document_id;

    FOREACH current_line IN ARRAY regexp_split_to_array(
        replace(p_content, E'\r\n', E'\n'),
        E'\n'
    )
    LOOP
        current_number := current_number + 1;

        INSERT INTO document_lines (
            document_id,
            line_number,
            line_text
        )
        VALUES (
            p_document_id,
            current_number,
            current_line
        );
    END LOOP;
END;
$$;

CREATE OR REPLACE FUNCTION rebuild_word_index(
    p_document_id BIGINT
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    line_record RECORD;
    token TEXT;
BEGIN
    DELETE FROM document_words
    WHERE document_id = p_document_id;

    FOR line_record IN
        SELECT line_text
        FROM document_lines
        WHERE document_id = p_document_id
        ORDER BY line_number
    LOOP
        FOR token IN
            SELECT lower(value)
            FROM regexp_matches(
                line_record.line_text,
                '[[:alnum:]_''-]+',
                'g'
            ) AS match(value)
        LOOP
            INSERT INTO document_words (
                document_id,
                normalized_word,
                occurrence_count
            )
            VALUES (
                p_document_id,
                token,
                1
            )
            ON CONFLICT (
                document_id,
                normalized_word
            )
            DO UPDATE SET
                occurrence_count =
                    document_words.occurrence_count + 1;
        END LOOP;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE ingest_document(
    p_file_name TEXT,
    p_content TEXT,
    p_encoding TEXT DEFAULT 'UTF-8'
)
LANGUAGE plpgsql
AS $$
DECLARE
    new_document_id BIGINT;
BEGIN
    IF p_file_name IS NULL
       OR length(trim(p_file_name)) = 0 THEN
        RAISE EXCEPTION 'File name is required';
    END IF;

    IF p_content IS NULL THEN
        RAISE EXCEPTION 'Content is required';
    END IF;

    INSERT INTO text_documents (
        file_name,
        encoding_name,
        content
    )
    VALUES (
        p_file_name,
        p_encoding,
        p_content
    )
    RETURNING document_id INTO new_document_id;

    PERFORM populate_document_lines(
        new_document_id,
        p_content
    );

    PERFORM rebuild_word_index(new_document_id);
END;
$$;

CALL ingest_document(
    'operations.txt',
    E'Reading text files requires explicit encoding.\n'
    || E'Streaming reads reduce memory usage.\n'
    || E'Validation prevents unsafe input.\n'
    || E'Streaming reads are useful for large files.'
);

CALL ingest_document(
    'empty-lines.txt',
    E'First line.\n\nThird line.\nFourth line.'
);

CALL ingest_document(
    'incident-notes.txt',
    E'Input validation is required.\n'
    || E'Input validation prevents malformed data.\n'
    || E'Large files should be processed incrementally.'
);

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM text_documents
        WHERE file_name = 'operations.txt'
    ) THEN
        RAISE EXCEPTION
            'Required demonstration document is missing';
    END IF;
END;
$$;

COMMIT;

CREATE OR REPLACE VIEW document_report AS
SELECT
    d.document_id,
    d.file_name,
    d.encoding_name,
    d.byte_size,
    count(l.line_id)::INTEGER AS line_count,
    count(l.line_id) FILTER (
        WHERE NOT l.is_empty
    )::INTEGER AS non_empty_line_count,
    COALESCE(
        sum(l.character_count),
        0
    )::BIGINT AS character_count,
    COALESCE(
        sum(w.occurrence_count),
        0
    )::BIGINT AS word_count,
    count(w.normalized_word)::INTEGER AS unique_word_count
FROM text_documents d
LEFT JOIN document_lines l
    ON l.document_id = d.document_id
LEFT JOIN document_words w
    ON w.document_id = d.document_id
GROUP BY
    d.document_id,
    d.file_name,
    d.encoding_name,
    d.byte_size;

-- Retrieve complete document metadata and content.
SELECT
    document_id,
    file_name,
    encoding_name,
    byte_size,
    content
FROM text_documents
ORDER BY document_id;

-- Retrieve a document in its original line order.
SELECT
    d.file_name,
    l.line_number,
    l.line_text
FROM text_documents d
JOIN document_lines l
    ON l.document_id = d.document_id
WHERE d.file_name = 'operations.txt'
ORDER BY l.line_number;

-- Case-insensitive line search.
SELECT
    d.file_name,
    l.line_number,
    l.line_text
FROM text_documents d
JOIN document_lines l
    ON l.document_id = d.document_id
WHERE lower(l.line_text) LIKE '%streaming%'
ORDER BY d.file_name, l.line_number;

-- Documents containing a requested word.
SELECT
    d.file_name,
    w.normalized_word,
    w.occurrence_count
FROM text_documents d
JOIN document_words w
    ON w.document_id = d.document_id
WHERE w.normalized_word = 'validation'
ORDER BY d.file_name;

-- File-level reporting.
SELECT *
FROM document_report
ORDER BY document_id;

-- Top words per document using a window function.
WITH ranked_words AS (
    SELECT
        d.file_name,
        w.normalized_word,
        w.occurrence_count,
        dense_rank() OVER (
            PARTITION BY w.document_id
            ORDER BY w.occurrence_count DESC
        ) AS word_rank
    FROM document_words w
    JOIN text_documents d
        ON d.document_id = w.document_id
)
SELECT
    file_name,
    normalized_word,
    occurrence_count
FROM ranked_words
WHERE word_rank <= 5
ORDER BY file_name, word_rank, normalized_word;

-- Identify files containing empty lines.
SELECT
    d.file_name,
    count(*) AS empty_line_count
FROM text_documents d
JOIN document_lines l
    ON l.document_id = d.document_id
WHERE l.is_empty
GROUP BY d.file_name
ORDER BY d.file_name;

-- Validation query for line-number continuity.
WITH numbered AS (
    SELECT
        document_id,
        line_number,
        row_number() OVER (
            PARTITION BY document_id
            ORDER BY line_number
        ) AS expected_number
    FROM document_lines
)
SELECT
    d.file_name,
    n.line_number,
    n.expected_number
FROM numbered n
JOIN text_documents d
    ON d.document_id = n.document_id
WHERE n.line_number <> n.expected_number
ORDER BY d.file_name, n.line_number;

-- Demonstrate an atomic read/report operation.
BEGIN;

SELECT
    d.document_id,
    d.file_name,
    count(l.line_id) AS lines
FROM text_documents d
LEFT JOIN document_lines l
    ON l.document_id = d.document_id
GROUP BY d.document_id, d.file_name
ORDER BY d.document_id;

COMMIT;
