-- ============================================================
-- READING AND WRITING CSV FILES
-- PostgreSQL 14+
--
-- Demonstrates:
-- 1. CSV import staging
-- 2. Schema validation
-- 3. Data type conversion
-- 4. Data quality checks
-- 5. Duplicate detection
-- 6. Transactional processing
-- 7. Error isolation
-- 8. CSV export using COPY
-- 9. Aggregation and reporting
-- 10. Database constraints and auditing
--
-- Execute using psql.
-- Server-side COPY requires server filesystem permissions.
-- Use \copy in psql for client-side file access.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS csv_lab;

SET search_path TO csv_lab, public;

-- ============================================================
-- 1. Import batch management
-- ============================================================

CREATE TABLE IF NOT EXISTS import_batch (
    batch_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    file_name TEXT NOT NULL,

    source_system TEXT NOT NULL,

    imported_by TEXT NOT NULL,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    batch_status TEXT NOT NULL DEFAULT 'PROCESSING',

    total_rows INTEGER NOT NULL DEFAULT 0,

    accepted_rows INTEGER NOT NULL DEFAULT 0,

    rejected_rows INTEGER NOT NULL DEFAULT 0,

    duplicate_rows INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT valid_batch_status
        CHECK (
            batch_status IN (
                'PROCESSING',
                'COMPLETED',
                'FAILED'
            )
        ),

    CONSTRAINT nonnegative_batch_counts
        CHECK (
            total_rows >= 0
            AND accepted_rows >= 0
            AND rejected_rows >= 0
            AND duplicate_rows >= 0
        )
);

-- ============================================================
-- 2. Raw CSV staging table
--
-- Text columns preserve source values before conversion.
-- ============================================================

CREATE TABLE IF NOT EXISTS invoice_staging (
    staging_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    batch_id BIGINT NOT NULL REFERENCES import_batch(batch_id),

    source_line_number INTEGER NOT NULL,

    invoice_id_text TEXT,

    customer_id_text TEXT,

    customer_name_text TEXT,

    amount_text TEXT,

    currency_text TEXT,

    status_text TEXT,

    CONSTRAINT unique_source_line
        UNIQUE (batch_id, source_line_number)
);

CREATE INDEX IF NOT EXISTS idx_staging_batch
    ON invoice_staging(batch_id);

-- ============================================================
-- 3. Validated invoice table
-- ============================================================

CREATE TABLE IF NOT EXISTS invoice (
    invoice_id BIGINT PRIMARY KEY,

    customer_id BIGINT NOT NULL,

    customer_name TEXT NOT NULL,

    amount NUMERIC(14, 2) NOT NULL,

    currency CHAR(3) NOT NULL,

    invoice_status TEXT NOT NULL,

    source_batch_id BIGINT NOT NULL
        REFERENCES import_batch(batch_id),

    imported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_invoice_id
        CHECK (invoice_id > 0),

    CONSTRAINT positive_customer_id
        CHECK (customer_id > 0),

    CONSTRAINT valid_amount
        CHECK (amount >= 0),

    CONSTRAINT valid_currency
        CHECK (currency ~ '^[A-Z]{3}$'),

    CONSTRAINT valid_invoice_status
        CHECK (
            invoice_status IN (
                'DRAFT',
                'APPROVED',
                'PAID',
                'REJECTED'
            )
        ),

    CONSTRAINT nonempty_customer_name
        CHECK (length(trim(customer_name)) > 0)
);

CREATE INDEX IF NOT EXISTS idx_invoice_customer
    ON invoice(customer_id);

CREATE INDEX IF NOT EXISTS idx_invoice_status
    ON invoice(invoice_status);

CREATE INDEX IF NOT EXISTS idx_invoice_import_time
    ON invoice(imported_at DESC);

-- ============================================================
-- 4. Import error table
-- ============================================================

CREATE TABLE IF NOT EXISTS import_error (
    error_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    batch_id BIGINT NOT NULL REFERENCES import_batch(batch_id),

    source_line_number INTEGER NOT NULL,

    error_code TEXT NOT NULL,

    error_message TEXT NOT NULL,

    original_record JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_import_error_batch
    ON import_error(batch_id, source_line_number);

-- ============================================================
-- 5. Import audit table
-- ============================================================

CREATE TABLE IF NOT EXISTS import_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    batch_id BIGINT NOT NULL REFERENCES import_batch(batch_id),

    event_type TEXT NOT NULL,

    event_details JSONB NOT NULL DEFAULT '{}'::JSONB,

    event_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. Import sample batch
-- ============================================================

INSERT INTO import_batch (
    file_name,
    source_system,
    imported_by
)
VALUES (
    'invoices_2026.csv',
    'FINANCE_ERP',
    'data_import_service'
)
RETURNING batch_id
\gset

-- ============================================================
-- 7. Stage imported CSV records
--
-- In psql, the following is a server-independent alternative:
--
-- \copy csv_lab.invoice_staging (
--   batch_id, source_line_number, invoice_id_text,
--   customer_id_text, customer_name_text,
--   amount_text, currency_text, status_text
-- ) FROM 'invoices.csv' WITH (FORMAT CSV, HEADER TRUE);
--
-- The sample below inserts equivalent staged records.
-- ============================================================

INSERT INTO invoice_staging (
    batch_id,
    source_line_number,
    invoice_id_text,
    customer_id_text,
    customer_name_text,
    amount_text,
    currency_text,
    status_text
)
VALUES
    (
        :batch_id, 2, '5001', '101',
        'Alice Johnson', '15000.00', 'INR', 'PAID'
    ),
    (
        :batch_id, 3, '5002', '102',
        'Bob Smith', '22000.00', 'INR', 'APPROVED'
    ),
    (
        :batch_id, 4, '5003', '101',
        'Alice Johnson', '8500.00', 'INR', 'PAID'
    ),
    (
        :batch_id, 5, '5004', '103',
        'Charlie Brown, Jr.', '12500.00', 'INR', 'PAID'
    ),
    (
        :batch_id, 6, '5005', '102',
        'Bob Smith', '1000000.00', 'INR', 'APPROVED'
    ),
    (
        :batch_id, 7, '5006', '104',
        'Diana Miller', '-500.00', 'INR', 'PAID'
    ),
    (
        :batch_id, 8, '5001', '101',
        'Duplicate Invoice', '5000.00', 'INR', 'PAID'
    ),
    (
        :batch_id, 9, 'INVALID', '105',
        'Invalid ID', '1000.00', 'INR', 'PAID'
    ),
    (
        :batch_id, 10, '5007', '106',
        'Missing Amount', '', 'INR', 'PAID'
    );

-- ============================================================
-- 8. Validation function
--
-- Validation is performed before conversion to typed columns.
-- ============================================================

CREATE OR REPLACE FUNCTION validate_invoice_record(
    p_invoice_id TEXT,
    p_customer_id TEXT,
    p_customer_name TEXT,
    p_amount TEXT,
    p_currency TEXT,
    p_status TEXT
)
RETURNS TABLE (
    valid BOOLEAN,
    error_code TEXT,
    error_message TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    IF p_invoice_id IS NULL
       OR p_invoice_id !~ '^[1-9][0-9]*$' THEN

        RETURN QUERY SELECT
            FALSE,
            'INVALID_INVOICE_ID',
            'Invoice ID must be a positive integer';

        RETURN;
    END IF;

    IF p_customer_id IS NULL
       OR p_customer_id !~ '^[1-9][0-9]*$' THEN

        RETURN QUERY SELECT
            FALSE,
            'INVALID_CUSTOMER_ID',
            'Customer ID must be a positive integer';

        RETURN;
    END IF;

    IF p_customer_name IS NULL
       OR length(trim(p_customer_name)) = 0 THEN

        RETURN QUERY SELECT
            FALSE,
            'MISSING_CUSTOMER_NAME',
            'Customer name is required';

        RETURN;
    END IF;

    IF p_amount IS NULL
       OR p_amount !~ '^[0-9]+(\.[0-9]{1,2})?$' THEN

        RETURN QUERY SELECT
            FALSE,
            'INVALID_AMOUNT',
            'Amount must be a non-negative decimal with at most two decimal places';

        RETURN;
    END IF;

    IF p_currency IS NULL
       OR p_currency !~ '^[A-Z]{3}$' THEN

        RETURN QUERY SELECT
            FALSE,
            'INVALID_CURRENCY',
            'Currency must contain three uppercase letters';

        RETURN;
    END IF;

    IF p_status NOT IN (
        'DRAFT',
        'APPROVED',
        'PAID',
        'REJECTED'
    ) THEN

        RETURN QUERY SELECT
            FALSE,
            'INVALID_STATUS',
            'Unsupported invoice status';

        RETURN;
    END IF;

    RETURN QUERY SELECT
        TRUE,
        NULL::TEXT,
        NULL::TEXT;

END;
$$;

-- ============================================================
-- 9. Staging validation view
-- ============================================================

CREATE OR REPLACE VIEW invoice_validation AS
SELECT
    s.staging_id,
    s.batch_id,
    s.source_line_number,
    s.invoice_id_text,
    s.customer_id_text,
    s.customer_name_text,
    s.amount_text,
    s.currency_text,
    s.status_text,
    v.valid,
    v.error_code,
    v.error_message
FROM invoice_staging s
CROSS JOIN LATERAL validate_invoice_record(
    s.invoice_id_text,
    s.customer_id_text,
    s.customer_name_text,
    s.amount_text,
    s.currency_text,
    s.status_text
) v;

-- ============================================================
-- 10. Process one import batch
--
-- The function:
-- - validates every row
-- - rejects malformed records
-- - detects duplicate invoice IDs
-- - applies a maximum amount policy
-- - inserts accepted records
-- - updates batch statistics
-- ============================================================

CREATE OR REPLACE FUNCTION process_invoice_batch(
    p_batch_id BIGINT,
    p_maximum_amount NUMERIC DEFAULT 500000.00
)
RETURNS TABLE (
    total_rows BIGINT,
    accepted_rows BIGINT,
    rejected_rows BIGINT,
    duplicate_rows BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    r RECORD;

    v_total BIGINT := 0;
    v_accepted BIGINT := 0;
    v_rejected BIGINT := 0;
    v_duplicates BIGINT := 0;

    v_invoice_id BIGINT;
    v_customer_id BIGINT;
    v_amount NUMERIC(14, 2);

    v_error_code TEXT;
    v_error_message TEXT;

BEGIN

    PERFORM 1
    FROM import_batch
    WHERE batch_id = p_batch_id
      AND batch_status = 'PROCESSING'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Batch % does not exist or is not processing',
            p_batch_id;
    END IF;

    IF p_maximum_amount < 0 THEN
        RAISE EXCEPTION 'Maximum amount cannot be negative';
    END IF;

    FOR r IN
        SELECT *
        FROM invoice_staging
        WHERE batch_id = p_batch_id
        ORDER BY source_line_number
    LOOP

        v_total := v_total + 1;

        v_error_code := NULL;
        v_error_message := NULL;

        SELECT
            error_code,
            error_message
        INTO
            v_error_code,
            v_error_message
        FROM validate_invoice_record(
            r.invoice_id_text,
            r.customer_id_text,
            r.customer_name_text,
            r.amount_text,
            r.currency_text,
            r.status_text
        )
        WHERE NOT valid;

        IF v_error_code IS NOT NULL THEN

            INSERT INTO import_error (
                batch_id,
                source_line_number,
                error_code,
                error_message,
                original_record
            )
            VALUES (
                p_batch_id,
                r.source_line_number,
                v_error_code,
                v_error_message,
                to_jsonb(r)
            );

            v_rejected := v_rejected + 1;

            CONTINUE;
        END IF;

        v_invoice_id := r.invoice_id_text::BIGINT;
        v_customer_id := r.customer_id_text::BIGINT;
        v_amount := r.amount_text::NUMERIC(14, 2);

        IF v_amount > p_maximum_amount THEN

            INSERT INTO import_error (
                batch_id,
                source_line_number,
                error_code,
                error_message,
                original_record
            )
            VALUES (
                p_batch_id,
                r.source_line_number,
                'AMOUNT_POLICY_VIOLATION',
                'Invoice exceeds permitted import amount',
                to_jsonb(r)
            );

            v_rejected := v_rejected + 1;

            CONTINUE;
        END IF;

        IF EXISTS (
            SELECT 1
            FROM invoice
            WHERE invoice_id = v_invoice_id
        ) OR EXISTS (
            SELECT 1
            FROM invoice_staging previous
            WHERE previous.batch_id = p_batch_id
              AND previous.source_line_number < r.source_line_number
              AND previous.invoice_id_text = r.invoice_id_text
              AND previous.invoice_id_text ~ '^[1-9][0-9]*$'
        ) THEN

            INSERT INTO import_error (
                batch_id,
                source_line_number,
                error_code,
                error_message,
                original_record
            )
            VALUES (
                p_batch_id,
                r.source_line_number,
                'DUPLICATE_INVOICE',
                'Invoice ID already exists in the database or batch',
                to_jsonb(r)
            );

            v_duplicates := v_duplicates + 1;

            CONTINUE;
        END IF;

        INSERT INTO invoice (
            invoice_id,
            customer_id,
            customer_name,
            amount,
            currency,
            invoice_status,
            source_batch_id
        )
        VALUES (
            v_invoice_id,
            v_customer_id,
            r.customer_name_text,
            v_amount,
            r.currency_text,
            r.status_text,
            p_batch_id
        );

        v_accepted := v_accepted + 1;

    END LOOP;

    UPDATE import_batch
    SET
        total_rows = v_total,
        accepted_rows = v_accepted,
        rejected_rows = v_rejected,
        duplicate_rows = v_duplicates,
        batch_status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP
    WHERE batch_id = p_batch_id;

    INSERT INTO import_audit (
        batch_id,
        event_type,
        event_details
    )
    VALUES (
        p_batch_id,
        'IMPORT_COMPLETED',
        jsonb_build_object(
            'total', v_total,
            'accepted', v_accepted,
            'rejected', v_rejected,
            'duplicates', v_duplicates
        )
    );

    RETURN QUERY SELECT
        v_total,
        v_accepted,
        v_rejected,
        v_duplicates;

END;
$$;

-- ============================================================
-- 11. Execute the import
-- ============================================================

SELECT *
FROM process_invoice_batch(
    :batch_id,
    500000.00
);

-- ============================================================
-- 12. Retrieval
-- ============================================================

SELECT
    invoice_id,
    customer_id,
    customer_name,
    amount,
    currency,
    invoice_status,
    imported_at
FROM invoice
ORDER BY invoice_id;

-- ============================================================
-- 13. Rejected record analysis
-- ============================================================

SELECT
    source_line_number,
    error_code,
    error_message,
    original_record
FROM import_error
WHERE batch_id = :batch_id
ORDER BY source_line_number;

-- ============================================================
-- 14. Aggregation
-- ============================================================

SELECT
    currency,
    invoice_status,
    COUNT(*) AS invoice_count,
    SUM(amount) AS total_amount,
    AVG(amount)::NUMERIC(14, 2) AS average_amount
FROM invoice
GROUP BY currency, invoice_status
ORDER BY currency, invoice_status;

-- ============================================================
-- 15. Customer reporting
-- ============================================================

CREATE OR REPLACE VIEW paid_customer_report AS
SELECT
    customer_id,
    customer_name,
    COUNT(*) AS paid_invoice_count,
    SUM(amount)::NUMERIC(14, 2) AS total_paid,
    AVG(amount)::NUMERIC(14, 2) AS average_paid
FROM invoice
WHERE invoice_status = 'PAID'
GROUP BY customer_id, customer_name;

SELECT *
FROM paid_customer_report
ORDER BY total_paid DESC;

-- ============================================================
-- 16. Common table expression for eligibility
--
-- An invoice is eligible for payment processing when:
-- - it is approved
-- - its amount is positive
-- - it belongs to an accepted import batch
-- ============================================================

WITH eligible_invoices AS (
    SELECT
        i.invoice_id,
        i.customer_id,
        i.customer_name,
        i.amount,
        i.currency
    FROM invoice i
    INNER JOIN import_batch b
        ON b.batch_id = i.source_batch_id
    WHERE i.invoice_status = 'APPROVED'
      AND i.amount > 0
      AND b.batch_status = 'COMPLETED'
)
SELECT
    invoice_id,
    customer_id,
    customer_name,
    amount,
    currency,
    TRUE AS eligible_for_payment
FROM eligible_invoices
ORDER BY invoice_id;

-- ============================================================
-- 17. Batch performance and quality report
-- ============================================================

SELECT
    batch_id,
    file_name,
    source_system,
    batch_status,
    total_rows,
    accepted_rows,
    rejected_rows,
    duplicate_rows,
    ROUND(
        100.0 * accepted_rows /
        NULLIF(total_rows, 0),
        2
    ) AS acceptance_percentage,
    started_at,
    completed_at
FROM import_batch
WHERE batch_id = :batch_id;

-- ============================================================
-- 18. Audit retrieval
-- ============================================================

SELECT
    audit_id,
    event_type,
    event_details,
    event_time
FROM import_audit
WHERE batch_id = :batch_id
ORDER BY event_time;

-- ============================================================
-- 19. CSV export
--
-- Run from psql.
-- \copy writes to the client machine.
--
-- \copy (
--   SELECT
--       invoice_id,
--       customer_id,
--       customer_name,
--       amount,
--       currency,
--       invoice_status
--   FROM csv_lab.invoice
--   ORDER BY invoice_id
-- ) TO 'approved_invoices.csv'
-- WITH (FORMAT CSV, HEADER TRUE, ENCODING 'UTF8');
--
-- CSV output should be treated as untrusted when opened in
-- spreadsheet software. Database COPY does not provide
-- spreadsheet formula-injection protection.
-- ============================================================

-- ============================================================
-- 20. Transaction completion
-- ============================================================

COMMIT;
