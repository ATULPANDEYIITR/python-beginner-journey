-- ============================================================
-- ATTRIBUTES AND METHODS
-- PostgreSQL implementation of an object-oriented banking
-- domain using relational attributes and database routines.
--
-- Demonstrates:
-- 1. Database attributes through columns.
-- 2. Domain entities through relational tables.
-- 3. Instance-oriented operations through functions.
-- 4. Class-level configuration through reference tables.
-- 5. Validation through CHECK constraints.
-- 6. Encapsulation through controlled database routines.
-- 7. Inheritance-like specialization through account types.
-- 8. State transitions through triggers and functions.
-- 9. Composition through transaction history.
-- 10. Reporting through views and aggregate queries.
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS oop_demo;

SET search_path TO oop_demo, public;


-- ============================================================
-- 1. DOMAIN TYPES
-- ============================================================

CREATE TYPE account_status AS ENUM (
    'ACTIVE',
    'FROZEN',
    'CLOSED'
);

CREATE TYPE transaction_type AS ENUM (
    'DEPOSIT',
    'WITHDRAWAL',
    'TRANSFER_IN',
    'TRANSFER_OUT'
);


-- ============================================================
-- 2. CLASS-LEVEL CONFIGURATION
-- ============================================================

CREATE TABLE bank_configuration (
    configuration_id SMALLINT PRIMARY KEY
        CHECK (configuration_id = 1),

    bank_name VARCHAR(150) NOT NULL
        CHECK (length(trim(bank_name)) > 0),

    currency_code CHAR(3) NOT NULL DEFAULT 'INR',

    minimum_balance NUMERIC(15, 2) NOT NULL DEFAULT 0
        CHECK (minimum_balance >= 0),

    maximum_transaction NUMERIC(15, 2) NOT NULL DEFAULT 1000000
        CHECK (maximum_transaction > 0),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO bank_configuration (
    configuration_id,
    bank_name,
    currency_code,
    minimum_balance,
    maximum_transaction
)
VALUES (
    1,
    'National Digital Bank',
    'INR',
    0.00,
    1000000.00
);


-- ============================================================
-- 3. ACCOUNT TYPE REFERENCE DATA
-- ============================================================

CREATE TABLE account_types (
    account_type_id SMALLINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    type_code VARCHAR(30) NOT NULL UNIQUE,

    description VARCHAR(200) NOT NULL,

    default_interest_rate NUMERIC(5, 2) NOT NULL DEFAULT 0
        CHECK (
            default_interest_rate >= 0
            AND default_interest_rate <= 100
        ),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO account_types (
    type_code,
    description,
    default_interest_rate
)
VALUES
    ('STANDARD', 'Standard deposit account', 0.00),
    ('SAVINGS', 'Interest-bearing savings account', 5.00);


-- ============================================================
-- 4. ACCOUNT ENTITY
-- ============================================================

CREATE TABLE bank_accounts (
    account_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    account_number VARCHAR(30) NOT NULL UNIQUE,

    owner_name VARCHAR(150) NOT NULL
        CHECK (length(trim(owner_name)) > 0),

    account_type_id SMALLINT NOT NULL
        REFERENCES account_types(account_type_id),

    balance NUMERIC(15, 2) NOT NULL DEFAULT 0
        CHECK (balance >= 0),

    interest_rate NUMERIC(5, 2) NOT NULL DEFAULT 0
        CHECK (interest_rate BETWEEN 0 AND 100),

    status account_status NOT NULL DEFAULT 'ACTIVE',

    version BIGINT NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT account_number_format
        CHECK (account_number ~ '^[A-Z0-9-]{4,30}$')
);

CREATE INDEX idx_accounts_owner
    ON bank_accounts(owner_name);

CREATE INDEX idx_accounts_status
    ON bank_accounts(status);

CREATE INDEX idx_accounts_type
    ON bank_accounts(account_type_id);


-- ============================================================
-- 5. TRANSACTION HISTORY
-- ============================================================

CREATE TABLE account_transactions (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    transaction_reference UUID NOT NULL UNIQUE
        DEFAULT gen_random_uuid(),

    account_id BIGINT NOT NULL
        REFERENCES bank_accounts(account_id),

    transaction_type transaction_type NOT NULL,

    amount NUMERIC(15, 2) NOT NULL
        CHECK (amount > 0),

    balance_after NUMERIC(15, 2) NOT NULL
        CHECK (balance_after >= 0),

    related_account_id BIGINT
        REFERENCES bank_accounts(account_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT no_self_transaction
        CHECK (
            related_account_id IS NULL
            OR related_account_id <> account_id
        )
);

CREATE INDEX idx_transactions_account_time
    ON account_transactions(account_id, created_at DESC);

CREATE INDEX idx_transactions_type
    ON account_transactions(transaction_type);

CREATE INDEX idx_transactions_reference
    ON account_transactions(transaction_reference);


-- ============================================================
-- 6. ATTRIBUTE VALIDATION TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION validate_account_attributes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_default_rate NUMERIC(5, 2);
BEGIN
    NEW.account_number := upper(trim(NEW.account_number));
    NEW.owner_name := trim(NEW.owner_name);

    IF NEW.account_number = '' OR NEW.owner_name = '' THEN
        RAISE EXCEPTION
            'Account number and owner name are required.';
    END IF;

    SELECT default_interest_rate
    INTO v_default_rate
    FROM account_types
    WHERE account_type_id = NEW.account_type_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown account type.';
    END IF;

    IF TG_OP = 'INSERT' THEN
        IF NEW.interest_rate IS NULL THEN
            NEW.interest_rate := v_default_rate;
        END IF;

    ELSE
        NEW.updated_at := CURRENT_TIMESTAMP;
        NEW.version := OLD.version + 1;

        -- A closed account cannot be reactivated by direct update.
        IF OLD.status = 'CLOSED'
           AND NEW.status <> 'CLOSED' THEN
            RAISE EXCEPTION
                'Closed account cannot be reactivated.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_account_attributes
BEFORE INSERT OR UPDATE ON bank_accounts
FOR EACH ROW
EXECUTE FUNCTION validate_account_attributes();


-- ============================================================
-- 7. TRANSACTION AUDIT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION prevent_transaction_modification()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION
        'Transaction records are immutable.';
END;
$$;

CREATE TRIGGER trg_immutable_transactions
BEFORE UPDATE OR DELETE ON account_transactions
FOR EACH ROW
EXECUTE FUNCTION prevent_transaction_modification();


-- ============================================================
-- 8. INSTANCE-ORIENTED METHOD: DEPOSIT
-- ============================================================

CREATE OR REPLACE FUNCTION deposit_amount(
    p_account_number VARCHAR,
    p_amount NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_account bank_accounts%ROWTYPE;
    v_maximum NUMERIC(15, 2);
    v_new_balance NUMERIC(15, 2);
BEGIN
    IF p_amount IS NULL
       OR p_amount <= 0
       OR p_amount <> round(p_amount, 2) THEN
        RAISE EXCEPTION
            'Deposit must be positive and support two decimals.';
    END IF;

    SELECT maximum_transaction
    INTO v_maximum
    FROM bank_configuration
    WHERE configuration_id = 1;

    IF p_amount > v_maximum THEN
        RAISE EXCEPTION
            'Deposit exceeds transaction limit.';
    END IF;

    SELECT *
    INTO v_account
    FROM bank_accounts
    WHERE account_number = upper(trim(p_account_number))
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account not found.';
    END IF;

    IF v_account.status <> 'ACTIVE' THEN
        RAISE EXCEPTION
            'Account is not active.';
    END IF;

    v_new_balance := v_account.balance + p_amount;

    UPDATE bank_accounts
    SET balance = v_new_balance
    WHERE account_id = v_account.account_id;

    INSERT INTO account_transactions (
        account_id,
        transaction_type,
        amount,
        balance_after
    )
    VALUES (
        v_account.account_id,
        'DEPOSIT',
        p_amount,
        v_new_balance
    );

    RETURN v_new_balance;
END;
$$;


-- ============================================================
-- 9. INSTANCE-ORIENTED METHOD: WITHDRAWAL
-- ============================================================

CREATE OR REPLACE FUNCTION withdraw_amount(
    p_account_number VARCHAR,
    p_amount NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_account bank_accounts%ROWTYPE;
    v_minimum NUMERIC(15, 2);
    v_maximum NUMERIC(15, 2);
    v_new_balance NUMERIC(15, 2);
BEGIN
    IF p_amount IS NULL
       OR p_amount <= 0
       OR p_amount <> round(p_amount, 2) THEN
        RAISE EXCEPTION
            'Withdrawal must be positive and support two decimals.';
    END IF;

    SELECT minimum_balance, maximum_transaction
    INTO v_minimum, v_maximum
    FROM bank_configuration
    WHERE configuration_id = 1;

    IF p_amount > v_maximum THEN
        RAISE EXCEPTION
            'Withdrawal exceeds transaction limit.';
    END IF;

    SELECT *
    INTO v_account
    FROM bank_accounts
    WHERE account_number = upper(trim(p_account_number))
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account not found.';
    END IF;

    IF v_account.status <> 'ACTIVE' THEN
        RAISE EXCEPTION 'Account is not active.';
    END IF;

    v_new_balance := v_account.balance - p_amount;

    IF v_new_balance < v_minimum THEN
        RAISE EXCEPTION 'Insufficient funds.';
    END IF;

    UPDATE bank_accounts
    SET balance = v_new_balance
    WHERE account_id = v_account.account_id;

    INSERT INTO account_transactions (
        account_id,
        transaction_type,
        amount,
        balance_after
    )
    VALUES (
        v_account.account_id,
        'WITHDRAWAL',
        p_amount,
        v_new_balance
    );

    RETURN v_new_balance;
END;
$$;


-- ============================================================
-- 10. COMPOSED METHOD: ACCOUNT TRANSFER
-- ============================================================

CREATE OR REPLACE FUNCTION transfer_amount(
    p_source VARCHAR,
    p_destination VARCHAR,
    p_amount NUMERIC
)
RETURNS TABLE (
    source_balance NUMERIC,
    destination_balance NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_source bank_accounts%ROWTYPE;
    v_destination bank_accounts%ROWTYPE;
    v_minimum NUMERIC(15, 2);
    v_maximum NUMERIC(15, 2);
BEGIN
    IF upper(trim(p_source)) = upper(trim(p_destination)) THEN
        RAISE EXCEPTION 'Self-transfer is prohibited.';
    END IF;

    IF p_amount IS NULL
       OR p_amount <= 0
       OR p_amount <> round(p_amount, 2) THEN
        RAISE EXCEPTION 'Invalid transfer amount.';
    END IF;

    SELECT minimum_balance, maximum_transaction
    INTO v_minimum, v_maximum
    FROM bank_configuration
    WHERE configuration_id = 1;

    IF p_amount > v_maximum THEN
        RAISE EXCEPTION 'Transfer exceeds transaction limit.';
    END IF;

    -- Lock rows in ascending account ID order to reduce deadlocks.
    PERFORM account_id
    FROM bank_accounts
    WHERE account_number IN (
        upper(trim(p_source)),
        upper(trim(p_destination))
    )
    ORDER BY account_id
    FOR UPDATE;

    SELECT *
    INTO v_source
    FROM bank_accounts
    WHERE account_number = upper(trim(p_source));

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Source account not found.';
    END IF;

    SELECT *
    INTO v_destination
    FROM bank_accounts
    WHERE account_number = upper(trim(p_destination));

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Destination account not found.';
    END IF;

    IF v_source.status <> 'ACTIVE'
       OR v_destination.status <> 'ACTIVE' THEN
        RAISE EXCEPTION
            'Both accounts must be active.';
    END IF;

    IF v_source.balance - p_amount < v_minimum THEN
        RAISE EXCEPTION 'Insufficient source balance.';
    END IF;

    IF v_destination.balance + p_amount >
       9999999999999.99 THEN
        RAISE EXCEPTION 'Destination balance limit exceeded.';
    END IF;

    UPDATE bank_accounts
    SET balance = balance - p_amount
    WHERE account_id = v_source.account_id;

    UPDATE bank_accounts
    SET balance = balance + p_amount
    WHERE account_id = v_destination.account_id;

    INSERT INTO account_transactions (
        account_id,
        transaction_type,
        amount,
        balance_after,
        related_account_id
    )
    VALUES (
        v_source.account_id,
        'TRANSFER_OUT',
        p_amount,
        v_source.balance - p_amount,
        v_destination.account_id
    );

    INSERT INTO account_transactions (
        account_id,
        transaction_type,
        amount,
        balance_after,
        related_account_id
    )
    VALUES (
        v_destination.account_id,
        'TRANSFER_IN',
        p_amount,
        v_destination.balance + p_amount,
        v_source.account_id
    );

    RETURN QUERY
    SELECT
        source.balance,
        destination.balance
    FROM bank_accounts AS source
    JOIN bank_accounts AS destination
      ON destination.account_id = v_destination.account_id
    WHERE source.account_id = v_source.account_id;
END;
$$;


-- ============================================================
-- 11. STATE TRANSITION METHODS
-- ============================================================

CREATE OR REPLACE FUNCTION change_account_status(
    p_account_number VARCHAR,
    p_new_status account_status
)
RETURNS account_status
LANGUAGE plpgsql
AS $$
DECLARE
    v_account bank_accounts%ROWTYPE;
BEGIN
    SELECT *
    INTO v_account
    FROM bank_accounts
    WHERE account_number = upper(trim(p_account_number))
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account not found.';
    END IF;

    IF v_account.status = 'CLOSED' THEN
        RAISE EXCEPTION
            'Closed accounts cannot change status.';
    END IF;

    IF p_new_status = 'CLOSED'
       AND v_account.balance <> 0 THEN
        RAISE EXCEPTION
            'Account must have zero balance before closure.';
    END IF;

    UPDATE bank_accounts
    SET status = p_new_status
    WHERE account_id = v_account.account_id;

    RETURN p_new_status;
END;
$$;


-- ============================================================
-- 12. SPECIALIZED METHOD: SAVINGS INTEREST
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_interest(
    p_account_number VARCHAR
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_account bank_accounts%ROWTYPE;
    v_type VARCHAR(30);
BEGIN
    SELECT account.*, account_type.type_code
    INTO v_account, v_type
    FROM bank_accounts AS account
    JOIN account_types AS account_type
      ON account_type.account_type_id = account.account_type_id
    WHERE account.account_number = upper(trim(p_account_number));

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account not found.';
    END IF;

    IF v_type <> 'SAVINGS' THEN
        RAISE EXCEPTION
            'Interest calculation requires a savings account.';
    END IF;

    RETURN round(
        v_account.balance * v_account.interest_rate / 100,
        2
    );
END;
$$;


CREATE OR REPLACE FUNCTION apply_interest(
    p_account_number VARCHAR
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_interest NUMERIC(15, 2);
BEGIN
    v_interest := calculate_interest(p_account_number);

    IF v_interest > 0 THEN
        RETURN deposit_amount(
            p_account_number,
            v_interest
        );
    END IF;

    RETURN 0;
END;
$$;


-- ============================================================
-- 13. STORED PROCEDURE
-- ============================================================

CREATE OR REPLACE PROCEDURE create_account(
    p_account_number VARCHAR,
    p_owner_name VARCHAR,
    p_type_code VARCHAR,
    p_initial_balance NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_type_id SMALLINT;
    v_interest_rate NUMERIC(5, 2);
BEGIN
    IF p_initial_balance IS NULL
       OR p_initial_balance < 0
       OR p_initial_balance <> round(p_initial_balance, 2) THEN
        RAISE EXCEPTION 'Invalid initial balance.';
    END IF;

    SELECT account_type_id, default_interest_rate
    INTO v_type_id, v_interest_rate
    FROM account_types
    WHERE type_code = upper(trim(p_type_code));

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid account type.';
    END IF;

    INSERT INTO bank_accounts (
        account_number,
        owner_name,
        account_type_id,
        balance,
        interest_rate
    )
    VALUES (
        p_account_number,
        p_owner_name,
        v_type_id,
        p_initial_balance,
        v_interest_rate
    );
END;
$$;


-- ============================================================
-- 14. SAMPLE DOMAIN RECORDS
-- ============================================================

CALL create_account(
    'ACC1001',
    'Rahul Sharma',
    'STANDARD',
    50000.00
);

CALL create_account(
    'ACC1002',
    'Priya Verma',
    'SAVINGS',
    75000.00
);

CALL create_account(
    'ACC1003',
    'Amit Kumar',
    'STANDARD',
    10000.00
);

-- Invalid cases are demonstrated through executable blocks
-- that catch expected failures without aborting the script.

DO $$
BEGIN
    BEGIN
        PERFORM deposit_amount('ACC1001', -500.00);
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Expected validation failure: %', SQLERRM;
    END;

    BEGIN
        PERFORM withdraw_amount('ACC1001', 1000000.00);
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Expected insufficient funds failure: %', SQLERRM;
    END;

    BEGIN
        PERFORM transfer_amount(
            'ACC1001',
            'ACC1001',
            100.00
        );
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Expected self-transfer failure: %', SQLERRM;
    END;
END;
$$;


-- ============================================================
-- 15. VALID OPERATIONS
-- ============================================================

SELECT deposit_amount('ACC1001', 5000.00);

SELECT withdraw_amount('ACC1001', 2000.00);

SELECT *
FROM transfer_amount(
    'ACC1001',
    'ACC1002',
    3000.00
);

SELECT calculate_interest('ACC1002');

SELECT apply_interest('ACC1002');


-- ============================================================
-- 16. VIEWS
-- ============================================================

CREATE OR REPLACE VIEW account_details AS
SELECT
    account.account_id,
    account.account_number,
    account.owner_name,
    account_type.type_code,
    account.balance,
    account.interest_rate,
    account.status,
    account.created_at,
    account.updated_at
FROM bank_accounts AS account
JOIN account_types AS account_type
    ON account_type.account_type_id = account.account_type_id;


CREATE OR REPLACE VIEW account_transaction_summary AS
SELECT
    account.account_number,
    account.owner_name,
    count(transaction.transaction_id) AS transaction_count,
    coalesce(
        sum(transaction.amount)
            FILTER (
                WHERE transaction.transaction_type = 'DEPOSIT'
            ),
        0
    ) AS total_deposits,
    coalesce(
        sum(transaction.amount)
            FILTER (
                WHERE transaction.transaction_type = 'WITHDRAWAL'
            ),
        0
    ) AS total_withdrawals
FROM bank_accounts AS account
LEFT JOIN account_transactions AS transaction
    ON transaction.account_id = account.account_id
GROUP BY
    account.account_id,
    account.account_number,
    account.owner_name;


-- ============================================================
-- 17. RETRIEVAL AND REPORTING QUERIES
-- ============================================================

-- Retrieve all account attributes.
SELECT *
FROM account_details
ORDER BY account_number;

-- Retrieve active accounts.
SELECT *
FROM account_details
WHERE status = 'ACTIVE';

-- Retrieve transaction history.
SELECT
    account.account_number,
    transaction.transaction_type,
    transaction.amount,
    transaction.balance_after,
    transaction.created_at
FROM account_transactions AS transaction
JOIN bank_accounts AS account
    ON account.account_id = transaction.account_id
ORDER BY transaction.created_at DESC;

-- Aggregate account balances by account type.
SELECT
    type_code,
    count(*) AS account_count,
    sum(balance) AS total_balance,
    avg(balance) AS average_balance
FROM account_details
GROUP BY type_code;

-- Transaction reporting.
SELECT *
FROM account_transaction_summary
ORDER BY transaction_count DESC;

-- CTE: rank accounts by balance.
WITH ranked_accounts AS (
    SELECT
        account_number,
        owner_name,
        balance,
        dense_rank() OVER (
            ORDER BY balance DESC
        ) AS balance_rank
    FROM bank_accounts
)
SELECT *
FROM ranked_accounts
ORDER BY balance_rank, account_number;

-- Eligibility evaluation.
SELECT
    account_number,
    owner_name,
    balance,
    status,
    CASE
        WHEN status <> 'ACTIVE' THEN 'INELIGIBLE'
        WHEN balance < 1000 THEN 'LOW_BALANCE'
        ELSE 'ELIGIBLE'
    END AS eligibility
FROM bank_accounts;


-- ============================================================
-- 18. ATTRIBUTE AND METHOD METADATA
-- ============================================================

-- Inspect table attributes.
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'oop_demo'
ORDER BY table_name, ordinal_position;

-- Inspect database routines.
SELECT
    routine_name,
    routine_type,
    data_type
FROM information_schema.routines
WHERE routine_schema = 'oop_demo'
ORDER BY routine_name;

COMMIT;


-- ============================================================
-- 19. TRANSACTION FAILURE HANDLING EXAMPLE
-- ============================================================

-- This transaction is deliberately rolled back.
-- The account balance remains unchanged.

BEGIN;

SELECT deposit_amount('ACC1003', 1000.00);

ROLLBACK;


-- ============================================================
-- 20. FINAL VERIFICATION
-- ============================================================

SELECT
    account_number,
    owner_name,
    balance,
    status
FROM oop_demo.account_details
ORDER BY account_number;

SELECT
    account_number,
    transaction_count,
    total_deposits,
    total_withdrawals
FROM oop_demo.account_transaction_summary
ORDER BY account_number;
