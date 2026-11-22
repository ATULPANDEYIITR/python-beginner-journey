-- ============================================================
-- STATIC METHODS: POSTGRESQL IMPLEMENTATION
-- ============================================================
--
-- PostgreSQL does not implement object-oriented static methods
-- in the same way as Java, Python, C++, or JavaScript.
--
-- PostgreSQL schema-level functions provide the closest
-- functional equivalent for reusable operations that do not
-- depend on an individual database object.
--
-- This implementation demonstrates:
-- 1. Schema-level utility functions.
-- 2. IMMUTABLE, STABLE, and VOLATILE function classifications.
-- 3. Static business-rule validation.
-- 4. Static factory-like record creation.
-- 5. Transaction processing.
-- 6. Database constraints and triggers.
-- 7. Static authorization policies.
-- 8. Aggregation and reporting.
-- 9. Idempotency.
-- 10. Function security and execution privileges.
--
-- Compatible with PostgreSQL 14+.
--
-- Run using psql against a database where the executing role
-- has permission to create the schema and its objects.

BEGIN;

CREATE SCHEMA IF NOT EXISTS static_methods;

SET search_path TO static_methods, public;

-- ============================================================
-- 1. ENUMERATIONS
-- ============================================================

CREATE TYPE transaction_type AS ENUM (
    'CREDIT',
    'DEBIT'
);

CREATE TYPE transaction_status AS ENUM (
    'PENDING',
    'COMPLETED',
    'REJECTED'
);

CREATE TYPE application_role AS ENUM (
    'READER',
    'ANALYST',
    'ADMINISTRATOR'
);

CREATE TYPE operation_type AS ENUM (
    'READ',
    'ANALYZE',
    'WRITE',
    'DELETE'
);

-- ============================================================
-- 2. SCHEMA-LEVEL STATIC UTILITY FUNCTIONS
-- ============================================================

-- IMMUTABLE means identical arguments always produce
-- the same result without depending on database state.

CREATE OR REPLACE FUNCTION add_numbers(
    p_first NUMERIC,
    p_second NUMERIC
)
RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
STRICT
PARALLEL SAFE
AS $$
    SELECT p_first + p_second;
$$;

CREATE OR REPLACE FUNCTION subtract_numbers(
    p_first NUMERIC,
    p_second NUMERIC
)
RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
STRICT
PARALLEL SAFE
AS $$
    SELECT p_first - p_second;
$$;

CREATE OR REPLACE FUNCTION multiply_numbers(
    p_first NUMERIC,
    p_second NUMERIC
)
RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
STRICT
PARALLEL SAFE
AS $$
    SELECT p_first * p_second;
$$;

CREATE OR REPLACE FUNCTION divide_numbers(
    p_first NUMERIC,
    p_second NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
PARALLEL SAFE
AS $$
BEGIN
    IF p_first IS NULL OR p_second IS NULL THEN
        RETURN NULL;
    END IF;

    IF p_second = 0 THEN
        RAISE EXCEPTION 'Division by zero is not permitted.'
            USING ERRCODE = '22012';
    END IF;

    RETURN p_first / p_second;
END;
$$;

CREATE OR REPLACE FUNCTION calculate_percentage(
    p_part NUMERIC,
    p_total NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
PARALLEL SAFE
AS $$
BEGIN
    IF p_part IS NULL OR p_total IS NULL THEN
        RAISE EXCEPTION 'Percentage arguments cannot be NULL.';
    END IF;

    IF p_total = 0 THEN
        RAISE EXCEPTION 'Total cannot be zero.';
    END IF;

    RETURN ROUND((p_part / p_total) * 100, 2);
END;
$$;

-- ============================================================
-- 3. STATIC VALIDATION FUNCTIONS
-- ============================================================

CREATE OR REPLACE FUNCTION validate_positive_amount(
    p_amount NUMERIC
)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT COALESCE(
        p_amount > 0
        AND p_amount < 'Infinity'::NUMERIC,
        FALSE
    );
$$;

CREATE OR REPLACE FUNCTION validate_employee_id(
    p_employee_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT COALESCE(p_employee_id > 0, FALSE);
$$;

CREATE OR REPLACE FUNCTION validate_email(
    p_email TEXT
)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT COALESCE(
        p_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
        FALSE
    );
$$;

CREATE OR REPLACE FUNCTION validate_port(
    p_port INTEGER
)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT COALESCE(p_port BETWEEN 1 AND 65535, FALSE);
$$;

-- ============================================================
-- 4. STATIC FACTORY-LIKE FUNCTION
-- ============================================================

CREATE TABLE employees (
    employee_id BIGINT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT employee_id_positive
        CHECK (employee_id > 0),

    CONSTRAINT employee_name_nonempty
        CHECK (LENGTH(TRIM(full_name)) > 0),

    CONSTRAINT employee_email_valid
        CHECK (validate_email(email))
);

CREATE OR REPLACE FUNCTION create_employee(
    p_employee_id BIGINT,
    p_full_name TEXT,
    p_email TEXT,
    p_department TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
VOLATILE
AS $$
DECLARE
    v_employee_id BIGINT;
BEGIN
    IF NOT validate_employee_id(p_employee_id) THEN
        RAISE EXCEPTION 'Invalid employee ID.';
    END IF;

    IF p_full_name IS NULL OR LENGTH(TRIM(p_full_name)) = 0 THEN
        RAISE EXCEPTION 'Employee name is required.';
    END IF;

    IF NOT validate_email(p_email) THEN
        RAISE EXCEPTION 'Invalid email address.';
    END IF;

    IF p_department IS NULL OR LENGTH(TRIM(p_department)) = 0 THEN
        RAISE EXCEPTION 'Department is required.';
    END IF;

    INSERT INTO employees (
        employee_id,
        full_name,
        email,
        department
    )
    VALUES (
        p_employee_id,
        TRIM(p_full_name),
        LOWER(TRIM(p_email)),
        TRIM(p_department)
    )
    RETURNING employee_id INTO v_employee_id;

    RETURN v_employee_id;
END;
$$;

-- ============================================================
-- 5. ACCOUNTS AND TRANSACTIONS
-- ============================================================

CREATE TABLE accounts (
    account_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_employee_id BIGINT NOT NULL
        REFERENCES employees(employee_id),

    balance NUMERIC(18, 2) NOT NULL DEFAULT 0,

    account_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT nonnegative_account_balance
        CHECK (balance >= 0)
);

CREATE INDEX idx_accounts_employee
    ON accounts(owner_employee_id);

CREATE TABLE transactions (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    external_reference VARCHAR(100) NOT NULL UNIQUE,

    account_id BIGINT NOT NULL
        REFERENCES accounts(account_id),

    transaction_type transaction_type NOT NULL,

    amount NUMERIC(18, 2) NOT NULL,

    status transaction_status NOT NULL DEFAULT 'PENDING',

    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    completed_at TIMESTAMPTZ,

    CONSTRAINT positive_transaction_amount
        CHECK (validate_positive_amount(amount))
);

CREATE INDEX idx_transactions_account_date
    ON transactions(account_id, created_at DESC);

CREATE INDEX idx_transactions_status
    ON transactions(status, created_at);

-- ============================================================
-- 6. STATIC TRANSACTION VALIDATION
-- ============================================================

CREATE OR REPLACE FUNCTION validate_transaction(
    p_type transaction_type,
    p_amount NUMERIC
)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT COALESCE(
        p_type IS NOT NULL
        AND validate_positive_amount(p_amount),
        FALSE
    );
$$;

-- ============================================================
-- 7. DATABASE INTEGRITY TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION enforce_transaction_integrity()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF OLD.status <> 'PENDING' THEN
            RAISE EXCEPTION
                'Completed or rejected transactions cannot be modified.';
        END IF;

        IF NEW.account_id <> OLD.account_id
           OR NEW.transaction_type <> OLD.transaction_type
           OR NEW.amount <> OLD.amount
           OR NEW.external_reference <> OLD.external_reference THEN

            RAISE EXCEPTION
                'Transaction identity and financial fields are immutable.';
        END IF;
    END IF;

    IF NEW.status = 'COMPLETED' THEN
        NEW.completed_at := COALESCE(
            NEW.completed_at,
            NOW()
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_transaction_integrity
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION enforce_transaction_integrity();

-- ============================================================
-- 8. STATIC AUTHORIZATION POLICY TABLES
-- ============================================================

CREATE TABLE role_permissions (
    role application_role NOT NULL,
    operation operation_type NOT NULL,

    PRIMARY KEY (role, operation)
);

INSERT INTO role_permissions(role, operation)
VALUES
    ('READER', 'READ'),
    ('ANALYST', 'READ'),
    ('ANALYST', 'ANALYZE'),
    ('ADMINISTRATOR', 'READ'),
    ('ADMINISTRATOR', 'ANALYZE'),
    ('ADMINISTRATOR', 'WRITE'),
    ('ADMINISTRATOR', 'DELETE');

CREATE OR REPLACE FUNCTION evaluate_permission(
    p_role application_role,
    p_operation operation_type
)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
PARALLEL SAFE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM role_permissions
        WHERE role = p_role
          AND operation = p_operation
    );
$$;

-- STABLE is appropriate because this function reads table
-- state but does not modify it. It must not be IMMUTABLE.

-- ============================================================
-- 9. STATIC PRICING FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_discounted_price(
    p_price NUMERIC,
    p_discount_rate NUMERIC,
    p_tax_rate NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
PARALLEL SAFE
AS $$
DECLARE
    v_discounted NUMERIC;
BEGIN
    IF p_price IS NULL
       OR p_discount_rate IS NULL
       OR p_tax_rate IS NULL THEN

        RAISE EXCEPTION 'Pricing arguments cannot be NULL.';
    END IF;

    IF p_price < 0
       OR p_discount_rate < 0
       OR p_discount_rate > 1
       OR p_tax_rate < 0 THEN

        RAISE EXCEPTION 'Invalid pricing parameters.';
    END IF;

    v_discounted := p_price * (1 - p_discount_rate);

    RETURN ROUND(v_discounted * (1 + p_tax_rate), 2);
END;
$$;

-- ============================================================
-- 10. STATIC TRANSACTION PROCESSING FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION process_transaction(
    p_external_reference VARCHAR(100),
    p_account_id BIGINT,
    p_type transaction_type,
    p_amount NUMERIC,
    p_description TEXT DEFAULT NULL
)
RETURNS TABLE (
    result_transaction_id BIGINT,
    result_status transaction_status,
    result_balance NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_balance NUMERIC(18, 2);
    v_new_balance NUMERIC(18, 2);
    v_transaction_id BIGINT;
    v_existing transactions%ROWTYPE;
BEGIN
    IF p_external_reference IS NULL
       OR LENGTH(TRIM(p_external_reference)) = 0 THEN

        RAISE EXCEPTION 'External reference is required.';
    END IF;

    IF NOT validate_transaction(p_type, p_amount) THEN
        RAISE EXCEPTION 'Invalid transaction parameters.';
    END IF;

    -- Serialize concurrent updates to the same account.
    SELECT balance
    INTO v_balance
    FROM accounts
    WHERE account_id = p_account_id
      AND account_active = TRUE
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active account not found.';
    END IF;

    -- Idempotency: repeated external references cannot
    -- produce a second financial transaction.
    SELECT *
    INTO v_existing
    FROM transactions
    WHERE external_reference = p_external_reference;

    IF FOUND THEN
        IF v_existing.account_id <> p_account_id
           OR v_existing.transaction_type <> p_type
           OR v_existing.amount <> p_amount THEN

            RAISE EXCEPTION
                'External reference reused with different parameters.';
        END IF;

        RETURN QUERY
        SELECT
            v_existing.transaction_id,
            v_existing.status,
            v_balance;

        RETURN;
    END IF;

    IF p_type = 'CREDIT' THEN
        v_new_balance := v_balance + p_amount;
    ELSE
        IF p_amount > v_balance THEN
            RAISE EXCEPTION 'Insufficient account balance.';
        END IF;

        v_new_balance := v_balance - p_amount;
    END IF;

    INSERT INTO transactions (
        external_reference,
        account_id,
        transaction_type,
        amount,
        status,
        description
    )
    VALUES (
        p_external_reference,
        p_account_id,
        p_type,
        p_amount,
        'PENDING',
        p_description
    )
    RETURNING transaction_id INTO v_transaction_id;

    UPDATE accounts
    SET balance = v_new_balance
    WHERE account_id = p_account_id;

    UPDATE transactions
    SET status = 'COMPLETED'
    WHERE transaction_id = v_transaction_id;

    RETURN QUERY
    SELECT
        v_transaction_id,
        'COMPLETED'::transaction_status,
        v_new_balance;
END;
$$;

-- ============================================================
-- 11. STATIC AGGREGATION FUNCTIONS
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_account_statistics(
    p_account_id BIGINT
)
RETURNS TABLE (
    transaction_count BIGINT,
    total_credits NUMERIC,
    total_debits NUMERIC,
    average_transaction NUMERIC
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        COUNT(*),
        COALESCE(
            SUM(amount) FILTER (
                WHERE transaction_type = 'CREDIT'
            ),
            0
        ),
        COALESCE(
            SUM(amount) FILTER (
                WHERE transaction_type = 'DEBIT'
            ),
            0
        ),
        COALESCE(AVG(amount), 0)
    FROM transactions
    WHERE account_id = p_account_id
      AND status = 'COMPLETED';
$$;

-- ============================================================
-- 12. STATIC REPORTING VIEW
-- ============================================================

CREATE VIEW account_transaction_report AS
SELECT
    a.account_id,
    e.full_name AS account_owner,
    a.balance AS current_balance,
    COUNT(t.transaction_id) FILTER (
        WHERE t.status = 'COMPLETED'
    ) AS completed_transactions,

    COALESCE(
        SUM(t.amount) FILTER (
            WHERE t.status = 'COMPLETED'
              AND t.transaction_type = 'CREDIT'
        ),
        0
    ) AS total_credits,

    COALESCE(
        SUM(t.amount) FILTER (
            WHERE t.status = 'COMPLETED'
              AND t.transaction_type = 'DEBIT'
        ),
        0
    ) AS total_debits

FROM accounts a

JOIN employees e
    ON e.employee_id = a.owner_employee_id

LEFT JOIN transactions t
    ON t.account_id = a.account_id

GROUP BY
    a.account_id,
    e.full_name,
    a.balance;

-- ============================================================
-- 13. SAMPLE DATA
-- ============================================================

INSERT INTO employees (
    employee_id,
    full_name,
    email,
    department
)
VALUES
    (101, 'Aarav Sharma', 'aarav@example.com', 'Research'),
    (102, 'Meera Singh', 'meera@example.com', 'Finance'),
    (103, 'Kabir Verma', 'kabir@example.com', 'Technology');

INSERT INTO accounts (
    owner_employee_id,
    balance
)
VALUES
    (101, 100000),
    (102, 75000),
    (103, 50000);

-- ============================================================
-- 14. VALID TRANSACTION PROCESSING
-- ============================================================

SELECT *
FROM process_transaction(
    'TX-1001',
    1,
    'CREDIT',
    25000,
    'Quarterly funding'
);

SELECT *
FROM process_transaction(
    'TX-1002',
    1,
    'DEBIT',
    10000,
    'Infrastructure expenditure'
);

SELECT *
FROM process_transaction(
    'TX-2001',
    2,
    'DEBIT',
    5000,
    'Operational expenditure'
);

-- ============================================================
-- 15. ELIGIBILITY AND POLICY EVALUATION
-- ============================================================

SELECT
    role,
    operation,
    evaluate_permission(role, operation) AS permitted
FROM role_permissions
ORDER BY role, operation;

SELECT
    evaluate_permission(
        'READER',
        'DELETE'
    ) AS reader_delete_permission;

SELECT
    validate_positive_amount(500) AS valid_amount,
    validate_positive_amount(-50) AS invalid_amount,
    validate_email('user@example.com') AS valid_email,
    validate_port(8080) AS valid_port;

-- ============================================================
-- 16. RETRIEVAL AND AGGREGATION
-- ============================================================

SELECT *
FROM account_transaction_report
ORDER BY account_id;

SELECT *
FROM calculate_account_statistics(1);

SELECT
    account_id,
    transaction_type,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount
FROM transactions
WHERE status = 'COMPLETED'
GROUP BY account_id, transaction_type
ORDER BY account_id, transaction_type;

-- ============================================================
-- 17. FUNCTION EVALUATION
-- ============================================================

SELECT
    add_numbers(10, 20) AS addition,
    subtract_numbers(50, 15) AS subtraction,
    multiply_numbers(12, 5) AS multiplication,
    divide_numbers(100, 4) AS division,
    calculate_percentage(25, 100) AS percentage;

SELECT calculate_discounted_price(
    10000,
    0.10,
    0.18
) AS final_price;

-- ============================================================
-- 18. TRANSACTION ROLLBACK DEMONSTRATION
-- ============================================================

-- This transaction intentionally fails and is rolled back.
-- Run it inside a savepoint so the complete installation script
-- remains executable.

SAVEPOINT failed_transaction_test;

DO $$
BEGIN
    PERFORM *
    FROM process_transaction(
        'TX-INVALID-001',
        1,
        'DEBIT',
        999999999,
        'Intentional insufficient-funds test'
    );
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Expected failure handled: %', SQLERRM;
END;
$$;

ROLLBACK TO SAVEPOINT failed_transaction_test;

RELEASE SAVEPOINT failed_transaction_test;

-- ============================================================
-- 19. IDEMPOTENCY VERIFICATION
-- ============================================================

-- Repeating the same reference with identical parameters
-- returns the existing transaction instead of charging twice.

SELECT *
FROM process_transaction(
    'TX-1001',
    1,
    'CREDIT',
    25000,
    'Repeated funding request'
);

-- ============================================================
-- 20. FINAL DATABASE REPORT
-- ============================================================

SELECT
    e.employee_id,
    e.full_name,
    COUNT(DISTINCT a.account_id) AS account_count,
    COUNT(t.transaction_id) FILTER (
        WHERE t.status = 'COMPLETED'
    ) AS completed_transaction_count

FROM employees e

LEFT JOIN accounts a
    ON a.owner_employee_id = e.employee_id

LEFT JOIN transactions t
    ON t.account_id = a.account_id

GROUP BY e.employee_id, e.full_name

ORDER BY e.employee_id;

-- ============================================================
-- 21. SECURITY AND EXECUTION CONSIDERATIONS
-- ============================================================

-- Production deployments should:
-- 1. Use a dedicated database role.
-- 2. Avoid granting PUBLIC unrestricted function execution.
-- 3. Grant only required schema and function permissions.
-- 4. Restrict direct modification of financial balances.
-- 5. Keep application credentials outside SQL scripts.
-- 6. Audit administrative access and sensitive operations.
-- 7. Review SECURITY DEFINER functions before introducing them.
-- 8. Use explicit schema qualification in security-sensitive code.
--
-- Example privilege configuration for an existing application role:
--
-- REVOKE ALL ON SCHEMA static_methods FROM PUBLIC;
-- REVOKE ALL ON ALL TABLES IN SCHEMA static_methods FROM PUBLIC;
-- GRANT USAGE ON SCHEMA static_methods TO application_user;
-- GRANT EXECUTE ON FUNCTION
--     static_methods.add_numbers(NUMERIC, NUMERIC)
-- TO application_user;
--
-- Additional table and function privileges should be granted
-- according to the application's actual access requirements.

COMMIT;
