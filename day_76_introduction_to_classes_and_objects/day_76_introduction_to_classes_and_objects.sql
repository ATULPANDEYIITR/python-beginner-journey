-- ============================================================
-- INTRODUCTION TO CLASSES AND OBJECTS
-- PostgreSQL relational model: Object-oriented library system
--
-- Concepts represented:
-- Objects       -> Library members and books
-- Identity      -> Primary keys
-- Attributes    -> Relational columns
-- Relationships -> Foreign keys
-- Encapsulation -> Controlled database operations
-- State         -> Loan lifecycle
-- Constraints   -> Object and relationship validation
-- Composition   -> Loans referencing members and books
-- Polymorphism  -> Book categories and borrowing policies
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS object_learning;

SET search_path TO object_learning, public;

-- ------------------------------------------------------------
-- ENUMS: Controlled object and workflow states
-- ------------------------------------------------------------

CREATE TYPE member_status AS ENUM (
    'ACTIVE',
    'SUSPENDED',
    'CLOSED'
);

CREATE TYPE book_status AS ENUM (
    'AVAILABLE',
    'BORROWED',
    'RETIRED'
);

CREATE TYPE loan_status AS ENUM (
    'ACTIVE',
    'RETURNED',
    'OVERDUE',
    'CANCELLED'
);

-- ------------------------------------------------------------
-- MEMBERS: Objects with unique identity and attributes
-- ------------------------------------------------------------

CREATE TABLE members (
    member_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    membership_type VARCHAR(20) NOT NULL
        CHECK (membership_type IN ('STANDARD', 'PREMIUM')),
    status member_status NOT NULL DEFAULT 'ACTIVE',
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (LENGTH(TRIM(full_name)) > 0)
);

-- ------------------------------------------------------------
-- BOOKS: Independent entities with object attributes
-- ------------------------------------------------------------

CREATE TABLE books (
    book_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    isbn VARCHAR(17) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(150) NOT NULL,
    category VARCHAR(40) NOT NULL,
    status book_status NOT NULL DEFAULT 'AVAILABLE',
    replacement_cost NUMERIC(10, 2) NOT NULL
        CHECK (replacement_cost > 0),
    published_year INTEGER
        CHECK (
            published_year BETWEEN 1450 AND 2100
        ),

    CHECK (LENGTH(TRIM(title)) > 0),
    CHECK (LENGTH(TRIM(author)) > 0)
);

-- ------------------------------------------------------------
-- BORROWING POLICIES: Different behavior by member type
-- ------------------------------------------------------------

CREATE TABLE borrowing_policies (
    membership_type VARCHAR(20) PRIMARY KEY
        CHECK (membership_type IN ('STANDARD', 'PREMIUM')),

    maximum_books INTEGER NOT NULL
        CHECK (maximum_books > 0),

    borrowing_days INTEGER NOT NULL
        CHECK (borrowing_days > 0),

    daily_fine NUMERIC(8, 2) NOT NULL
        CHECK (daily_fine >= 0),

    maximum_fine NUMERIC(10, 2) NOT NULL
        CHECK (maximum_fine >= 0)
);

-- ------------------------------------------------------------
-- LOANS: Relationship between members and books
-- ------------------------------------------------------------

CREATE TABLE loans (
    loan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    member_id BIGINT NOT NULL
        REFERENCES members(member_id),

    book_id BIGINT NOT NULL
        REFERENCES books(book_id),

    borrowed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    due_at TIMESTAMPTZ NOT NULL,
    returned_at TIMESTAMPTZ,

    status loan_status NOT NULL DEFAULT 'ACTIVE',

    fine_amount NUMERIC(10, 2) NOT NULL DEFAULT 0
        CHECK (fine_amount >= 0),

    CHECK (due_at > borrowed_at),

    CHECK (
        returned_at IS NULL OR returned_at >= borrowed_at
    ),

    CHECK (
        (status IN ('ACTIVE', 'OVERDUE')
            AND returned_at IS NULL)
        OR
        (status = 'RETURNED'
            AND returned_at IS NOT NULL)
        OR
        status = 'CANCELLED'
    )
);

-- One physical copy cannot have two active loans.
CREATE UNIQUE INDEX uq_active_book_loan
ON loans(book_id)
WHERE status IN ('ACTIVE', 'OVERDUE');

-- Efficient member-level active-loan retrieval.
CREATE INDEX idx_member_active_loans
ON loans(member_id, due_at)
WHERE status IN ('ACTIVE', 'OVERDUE');

CREATE INDEX idx_books_category_status
ON books(category, status);

CREATE INDEX idx_loans_borrowed_at
ON loans(borrowed_at DESC);

-- ------------------------------------------------------------
-- INITIAL POLICY DATA
-- ------------------------------------------------------------

INSERT INTO borrowing_policies (
    membership_type,
    maximum_books,
    borrowing_days,
    daily_fine,
    maximum_fine
)
VALUES
    ('STANDARD', 3, 14, 5.00, 200.00),
    ('PREMIUM', 8, 30, 2.00, 500.00);

-- ------------------------------------------------------------
-- DATA INTEGRITY TRIGGER
--
-- Prevents invalid book status changes and protects loan
-- lifecycle consistency.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_loan()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_member_status member_status;
    v_book_status book_status;
    v_membership_type VARCHAR(20);
    v_policy borrowing_policies%ROWTYPE;
    v_active_count INTEGER;
BEGIN
    SELECT status, membership_type
    INTO v_member_status, v_membership_type
    FROM members
    WHERE member_id = NEW.member_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Member does not exist.';
    END IF;

    SELECT status
    INTO v_book_status
    FROM books
    WHERE book_id = NEW.book_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Book does not exist.';
    END IF;

    IF NEW.status IN ('ACTIVE', 'OVERDUE') THEN

        IF v_member_status <> 'ACTIVE' THEN
            RAISE EXCEPTION 'Member is not eligible to borrow.';
        END IF;

        IF TG_OP = 'INSERT' THEN
            IF v_book_status <> 'AVAILABLE' THEN
                RAISE EXCEPTION 'Book is not available.';
            END IF;
        END IF;

        SELECT *
        INTO v_policy
        FROM borrowing_policies
        WHERE membership_type = v_membership_type;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Borrowing policy not configured.';
        END IF;

        SELECT COUNT(*)
        INTO v_active_count
        FROM loans
        WHERE member_id = NEW.member_id
          AND status IN ('ACTIVE', 'OVERDUE')
          AND (
              TG_OP <> 'UPDATE'
              OR loan_id <> OLD.loan_id
          );

        IF v_active_count >= v_policy.maximum_books THEN
            RAISE EXCEPTION
                'Member has reached the borrowing limit.';
        END IF;

        IF NEW.status = 'ACTIVE' THEN
            IF NEW.due_at <= NEW.borrowed_at THEN
                RAISE EXCEPTION 'Invalid loan due date.';
            END IF;
        END IF;

    END IF;

    IF TG_OP = 'UPDATE' THEN
        IF OLD.status IN ('RETURNED', 'CANCELLED')
           AND NEW.status <> OLD.status THEN
            RAISE EXCEPTION
                'Terminal loan states cannot be changed.';
        END IF;

        IF OLD.book_id <> NEW.book_id
           OR OLD.member_id <> NEW.member_id THEN
            RAISE EXCEPTION
                'Loan ownership cannot be changed.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_loan
BEFORE INSERT OR UPDATE ON loans
FOR EACH ROW
EXECUTE FUNCTION validate_loan();

-- ------------------------------------------------------------
-- BOOK STATE MANAGEMENT
-- Synchronizes book state with loan state.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION synchronize_book_status()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'ACTIVE' AND TG_OP = 'INSERT' THEN

        UPDATE books
        SET status = 'BORROWED'
        WHERE book_id = NEW.book_id;

    ELSIF NEW.status = 'RETURNED' THEN

        UPDATE books
        SET status = 'AVAILABLE'
        WHERE book_id = NEW.book_id;

    ELSIF NEW.status = 'CANCELLED' THEN

        UPDATE books
        SET status = 'AVAILABLE'
        WHERE book_id = NEW.book_id;

    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_synchronize_book
AFTER INSERT OR UPDATE OF status ON loans
FOR EACH ROW
EXECUTE FUNCTION synchronize_book_status();

-- ------------------------------------------------------------
-- OBJECT CREATION AND BUSINESS OPERATION
-- A controlled function acts as the borrowing interface.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION borrow_book(
    p_member_id BIGINT,
    p_book_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_membership_type VARCHAR(20);
    v_policy borrowing_policies%ROWTYPE;
    v_loan_id BIGINT;
    v_now TIMESTAMPTZ := NOW();
BEGIN
    SELECT membership_type
    INTO v_membership_type
    FROM members
    WHERE member_id = p_member_id
      AND status = 'ACTIVE'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active member not found.';
    END IF;

    SELECT *
    INTO v_policy
    FROM borrowing_policies
    WHERE membership_type = v_membership_type;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Member policy does not exist.';
    END IF;

    INSERT INTO loans (
        member_id,
        book_id,
        borrowed_at,
        due_at,
        status
    )
    VALUES (
        p_member_id,
        p_book_id,
        v_now,
        v_now + make_interval(days => v_policy.borrowing_days),
        'ACTIVE'
    )
    RETURNING loan_id INTO v_loan_id;

    RETURN v_loan_id;
END;
$$;

-- ------------------------------------------------------------
-- RETURN OPERATION WITH FINE CALCULATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION return_book(
    p_loan_id BIGINT
)
RETURNS NUMERIC(10, 2)
LANGUAGE plpgsql
AS $$
DECLARE
    v_loan loans%ROWTYPE;
    v_membership_type VARCHAR(20);
    v_policy borrowing_policies%ROWTYPE;
    v_days_overdue INTEGER;
    v_fine NUMERIC(10, 2);
BEGIN
    SELECT *
    INTO v_loan
    FROM loans
    WHERE loan_id = p_loan_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Loan does not exist.';
    END IF;

    IF v_loan.status NOT IN ('ACTIVE', 'OVERDUE') THEN
        RAISE EXCEPTION 'Loan cannot be returned in its current state.';
    END IF;

    SELECT membership_type
    INTO v_membership_type
    FROM members
    WHERE member_id = v_loan.member_id;

    SELECT *
    INTO v_policy
    FROM borrowing_policies
    WHERE membership_type = v_membership_type;

    v_days_overdue := GREATEST(
        0,
        CEIL(
            EXTRACT(
                EPOCH FROM (NOW() - v_loan.due_at)
            ) / 86400.0
        )::INTEGER
    );

    v_fine := LEAST(
        v_days_overdue * v_policy.daily_fine,
        v_policy.maximum_fine
    );

    UPDATE loans
    SET status = 'RETURNED',
        returned_at = NOW(),
        fine_amount = v_fine
    WHERE loan_id = p_loan_id;

    RETURN v_fine;
END;
$$;

-- ------------------------------------------------------------
-- VIEW: Combined object and relationship information
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW active_loan_details AS
SELECT
    l.loan_id,
    m.member_id,
    m.full_name,
    m.membership_type,
    b.book_id,
    b.title,
    b.author,
    l.borrowed_at,
    l.due_at,
    l.status,
    l.fine_amount
FROM loans l
JOIN members m ON m.member_id = l.member_id
JOIN books b ON b.book_id = l.book_id
WHERE l.status IN ('ACTIVE', 'OVERDUE');

-- ------------------------------------------------------------
-- VIEW: Member-level object summary
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW member_object_summary AS
SELECT
    m.member_id,
    m.full_name,
    m.membership_type,
    m.status,
    COUNT(l.loan_id) FILTER (
        WHERE l.status IN ('ACTIVE', 'OVERDUE')
    ) AS active_loans,
    COALESCE(SUM(l.fine_amount), 0) AS total_fines
FROM members m
LEFT JOIN loans l ON l.member_id = m.member_id
GROUP BY
    m.member_id,
    m.full_name,
    m.membership_type,
    m.status;

-- ------------------------------------------------------------
-- SAMPLE OBJECT INSTANCES
-- ------------------------------------------------------------

INSERT INTO members (
    full_name,
    email,
    membership_type
)
VALUES
    ('Aarav Sharma', 'aarav@example.com', 'STANDARD'),
    ('Meera Singh', 'meera@example.com', 'PREMIUM'),
    ('Kabir Verma', 'kabir@example.com', 'STANDARD'),
    ('Ananya Gupta', 'ananya@example.com', 'PREMIUM');

INSERT INTO books (
    isbn,
    title,
    author,
    category,
    replacement_cost,
    published_year
)
VALUES
    (
        '9780132350884',
        'Clean Code',
        'Robert C. Martin',
        'PROGRAMMING',
        650.00,
        2008
    ),
    (
        '9780134685991',
        'Effective Java',
        'Joshua Bloch',
        'PROGRAMMING',
        750.00,
        2018
    ),
    (
        '9781492056355',
        'Designing Data-Intensive Applications',
        'Martin Kleppmann',
        'DATABASES',
        900.00,
        2017
    ),
    (
        '9780262033848',
        'Introduction to Algorithms',
        'Thomas H. Cormen',
        'ALGORITHMS',
        1100.00,
        2009
    ),
    (
        '9780134494166',
        'Object-Oriented Design',
        'Grady Booch',
        'SOFTWARE_ENGINEERING',
        850.00,
        2016
    );

-- ------------------------------------------------------------
-- VALID TRANSACTION: Borrow a book
-- ------------------------------------------------------------

DO $$
DECLARE
    v_loan_id BIGINT;
BEGIN
    v_loan_id := borrow_book(1, 1);

    RAISE NOTICE 'Created loan: %', v_loan_id;
END;
$$;

-- ------------------------------------------------------------
-- INVALID TRANSACTION EXAMPLE
-- Duplicate active borrowing of the same physical book fails.
-- The exception is caught so the complete script continues.
-- ------------------------------------------------------------

DO $$
BEGIN
    BEGIN
        PERFORM borrow_book(2, 1);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Expected borrowing failure: %', SQLERRM;
    END;
END;
$$;

-- ------------------------------------------------------------
-- ADDITIONAL VALID BORROWING
-- ------------------------------------------------------------

DO $$
DECLARE
    v_loan_id BIGINT;
BEGIN
    v_loan_id := borrow_book(2, 2);

    RAISE NOTICE 'Premium member loan: %', v_loan_id;
END;
$$;

-- ------------------------------------------------------------
-- RETRIEVAL
-- ------------------------------------------------------------

SELECT
    member_id,
    full_name,
    email,
    membership_type,
    status
FROM members
ORDER BY member_id;

SELECT
    book_id,
    title,
    author,
    category,
    status
FROM books
ORDER BY title;

SELECT *
FROM active_loan_details
ORDER BY due_at;

-- ------------------------------------------------------------
-- VALIDATION: Members who have reached their limit
-- ------------------------------------------------------------

SELECT
    m.member_id,
    m.full_name,
    COUNT(l.loan_id) AS active_loans,
    p.maximum_books
FROM members m
JOIN borrowing_policies p
    ON p.membership_type = m.membership_type
LEFT JOIN loans l
    ON l.member_id = m.member_id
    AND l.status IN ('ACTIVE', 'OVERDUE')
GROUP BY
    m.member_id,
    m.full_name,
    p.maximum_books
HAVING COUNT(l.loan_id) >= p.maximum_books;

-- ------------------------------------------------------------
-- AGGREGATION: Category-level inventory report
-- ------------------------------------------------------------

SELECT
    category,
    COUNT(*) AS total_books,
    COUNT(*) FILTER (
        WHERE status = 'AVAILABLE'
    ) AS available_books,
    COUNT(*) FILTER (
        WHERE status = 'BORROWED'
    ) AS borrowed_books
FROM books
GROUP BY category
ORDER BY category;

-- ------------------------------------------------------------
-- CTE: Borrowing activity by member
-- ------------------------------------------------------------

WITH borrowing_activity AS (
    SELECT
        member_id,
        COUNT(*) AS total_loans,
        COUNT(*) FILTER (
            WHERE status = 'RETURNED'
        ) AS returned_loans,
        COUNT(*) FILTER (
            WHERE status IN ('ACTIVE', 'OVERDUE')
        ) AS outstanding_loans
    FROM loans
    GROUP BY member_id
)
SELECT
    m.full_name,
    COALESCE(a.total_loans, 0) AS total_loans,
    COALESCE(a.returned_loans, 0) AS returned_loans,
    COALESCE(a.outstanding_loans, 0) AS outstanding_loans
FROM members m
LEFT JOIN borrowing_activity a
    ON a.member_id = m.member_id
ORDER BY m.full_name;

-- ------------------------------------------------------------
-- EVALUATION: Overdue loan detection
-- ------------------------------------------------------------

SELECT
    loan_id,
    member_id,
    book_id,
    due_at,
    CEIL(
        EXTRACT(EPOCH FROM (NOW() - due_at)) / 86400.0
    ) AS overdue_days
FROM loans
WHERE status = 'ACTIVE'
  AND due_at < NOW();

-- ------------------------------------------------------------
-- TRANSACTION: Return a book
-- ------------------------------------------------------------

DO $$
DECLARE
    v_loan_id BIGINT;
    v_fine NUMERIC(10, 2);
BEGIN
    SELECT loan_id
    INTO v_loan_id
    FROM loans
    WHERE member_id = 1
      AND status = 'ACTIVE'
    ORDER BY loan_id
    LIMIT 1;

    IF v_loan_id IS NOT NULL THEN
        v_fine := return_book(v_loan_id);

        RAISE NOTICE
            'Loan % returned. Fine: %',
            v_loan_id,
            v_fine;
    END IF;
END;
$$;

-- ------------------------------------------------------------
-- REPORTING: Member-level object summary
-- ------------------------------------------------------------

SELECT *
FROM member_object_summary
ORDER BY member_id;

-- ------------------------------------------------------------
-- REPORTING: Total inventory value and utilization
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS inventory_size,
    SUM(replacement_cost) AS inventory_value,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status = 'BORROWED'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS utilization_percentage
FROM books
WHERE status <> 'RETIRED';

-- ------------------------------------------------------------
-- WORKFLOW: Explicitly retire an available book
-- ------------------------------------------------------------

UPDATE books
SET status = 'RETIRED'
WHERE book_id = 5
  AND status = 'AVAILABLE';

-- ------------------------------------------------------------
-- FINAL DATABASE STATE
-- ------------------------------------------------------------

SELECT
    l.loan_id,
    m.full_name,
    b.title,
    l.status,
    l.fine_amount,
    l.borrowed_at,
    l.due_at,
    l.returned_at
FROM loans l
JOIN members m ON m.member_id = l.member_id
JOIN books b ON b.book_id = l.book_id
ORDER BY l.loan_id;

COMMIT;
