-- PostgreSQL 15+
-- Property-oriented domain modeling, validation, computed values,
-- cached aggregates, audit history, and controlled state transitions.

BEGIN;

CREATE SCHEMA IF NOT EXISTS property_lab;

SET search_path TO property_lab, public;

-- 1. Property categories and data types
CREATE TYPE property_lab.property_type AS ENUM (
    'TEXT',
    'INTEGER',
    'DECIMAL',
    'BOOLEAN',
    'TIMESTAMP',
    'JSON'
);

CREATE TYPE property_lab.record_status AS ENUM (
    'ACTIVE',
    'SUSPENDED',
    'CLOSED'
);

-- 2. Employee records with constrained properties
CREATE TABLE employees (
    employee_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    employee_code VARCHAR(20) NOT NULL UNIQUE,
    employee_name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    salary NUMERIC(14, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT employee_code_valid
        CHECK (employee_code ~ '^[A-Z0-9]{4,20}$'),

    CONSTRAINT employee_name_valid
        CHECK (length(trim(employee_name)) BETWEEN 2 AND 100),

    CONSTRAINT employee_age_valid
        CHECK (age BETWEEN 18 AND 120),

    CONSTRAINT employee_salary_valid
        CHECK (salary >= 0)
);

CREATE INDEX idx_employees_active
    ON employees(employee_id)
    WHERE is_active = TRUE;

-- 3. Generic property metadata
CREATE TABLE property_definitions (
    property_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    property_name VARCHAR(100) NOT NULL UNIQUE,
    data_type property_lab.property_type NOT NULL,
    is_required BOOLEAN NOT NULL DEFAULT FALSE,
    is_read_only BOOLEAN NOT NULL DEFAULT FALSE,
    minimum_value NUMERIC,
    maximum_value NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT property_range_valid
        CHECK (
            minimum_value IS NULL
            OR maximum_value IS NULL
            OR minimum_value <= maximum_value
        )
);

CREATE TABLE employee_properties (
    employee_id BIGINT NOT NULL
        REFERENCES employees(employee_id) ON DELETE CASCADE,

    property_id BIGINT NOT NULL
        REFERENCES property_definitions(property_id),

    text_value TEXT,
    integer_value BIGINT,
    decimal_value NUMERIC(18, 4),
    boolean_value BOOLEAN,
    timestamp_value TIMESTAMPTZ,
    json_value JSONB,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (employee_id, property_id),

    CONSTRAINT one_property_value
        CHECK (
            num_nonnulls(
                text_value,
                integer_value,
                decimal_value,
                boolean_value,
                timestamp_value,
                json_value
            ) = 1
        )
);

CREATE INDEX idx_employee_properties_property
    ON employee_properties(property_id, employee_id);

-- 4. Property audit history
CREATE TABLE property_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_identifier TEXT NOT NULL,
    field_name TEXT NOT NULL,
    old_value JSONB,
    new_value JSONB,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT NOT NULL DEFAULT CURRENT_USER
);

CREATE INDEX idx_property_audit_record
    ON property_audit(table_name, record_identifier, changed_at DESC);

-- 5. Automatic timestamp maintenance
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := clock_timestamp();
    RETURN NEW;
END;
$$;

CREATE TRIGGER employees_timestamp_trigger
BEFORE UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();

-- 6. Audit salary changes
CREATE OR REPLACE FUNCTION audit_employee_salary()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.salary IS DISTINCT FROM NEW.salary THEN
        INSERT INTO property_audit (
            table_name,
            record_identifier,
            field_name,
            old_value,
            new_value
        )
        VALUES (
            'employees',
            NEW.employee_id::TEXT,
            'salary',
            jsonb_build_object('salary', OLD.salary),
            jsonb_build_object('salary', NEW.salary)
        );
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER employee_salary_audit_trigger
AFTER UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION audit_employee_salary();

-- 7. Property type compatibility validation
CREATE OR REPLACE FUNCTION validate_employee_property()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    definition RECORD;
    supplied_value_count INTEGER;
    numeric_value NUMERIC;
BEGIN
    SELECT *
    INTO definition
    FROM property_definitions
    WHERE property_id = NEW.property_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Property definition does not exist.';
    END IF;

    supplied_value_count := num_nonnulls(
        NEW.text_value,
        NEW.integer_value,
        NEW.decimal_value,
        NEW.boolean_value,
        NEW.timestamp_value,
        NEW.json_value
    );

    IF supplied_value_count <> 1 THEN
        RAISE EXCEPTION 'Exactly one property value is required.';
    END IF;

    IF definition.is_read_only THEN
        IF TG_OP = 'UPDATE' THEN
            IF ROW(
                NEW.text_value,
                NEW.integer_value,
                NEW.decimal_value,
                NEW.boolean_value,
                NEW.timestamp_value,
                NEW.json_value
            ) IS DISTINCT FROM ROW(
                OLD.text_value,
                OLD.integer_value,
                OLD.decimal_value,
                OLD.boolean_value,
                OLD.timestamp_value,
                OLD.json_value
            ) THEN
                RAISE EXCEPTION 'Property % is read-only.',
                    definition.property_name;
            END IF;
        ELSE
            RAISE EXCEPTION 'Property % is read-only.',
                definition.property_name;
        END IF;
    END IF;

    IF definition.data_type = 'TEXT'
       AND NEW.text_value IS NULL THEN
        RAISE EXCEPTION 'Text property requires text_value.';
    ELSIF definition.data_type = 'INTEGER'
       AND NEW.integer_value IS NULL THEN
        RAISE EXCEPTION 'Integer property requires integer_value.';
    ELSIF definition.data_type = 'DECIMAL'
       AND NEW.decimal_value IS NULL THEN
        RAISE EXCEPTION 'Decimal property requires decimal_value.';
    ELSIF definition.data_type = 'BOOLEAN'
       AND NEW.boolean_value IS NULL THEN
        RAISE EXCEPTION 'Boolean property requires boolean_value.';
    ELSIF definition.data_type = 'TIMESTAMP'
       AND NEW.timestamp_value IS NULL THEN
        RAISE EXCEPTION 'Timestamp property requires timestamp_value.';
    ELSIF definition.data_type = 'JSON'
       AND NEW.json_value IS NULL THEN
        RAISE EXCEPTION 'JSON property requires json_value.';
    END IF;

    numeric_value := CASE
        WHEN definition.data_type = 'INTEGER'
            THEN NEW.integer_value::NUMERIC
        WHEN definition.data_type = 'DECIMAL'
            THEN NEW.decimal_value
        ELSE NULL
    END;

    IF numeric_value IS NOT NULL THEN
        IF definition.minimum_value IS NOT NULL
           AND numeric_value < definition.minimum_value THEN
            RAISE EXCEPTION 'Value is below the minimum.';
        END IF;

        IF definition.maximum_value IS NOT NULL
           AND numeric_value > definition.maximum_value THEN
            RAISE EXCEPTION 'Value exceeds the maximum.';
        END IF;
    END IF;

    NEW.updated_at := clock_timestamp();

    RETURN NEW;
END;
$$;

CREATE TRIGGER employee_property_validation_trigger
BEFORE INSERT OR UPDATE ON employee_properties
FOR EACH ROW
EXECUTE FUNCTION validate_employee_property();

-- 8. Inventory with a stored computed property
CREATE TABLE inventory (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL UNIQUE,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(14, 2) NOT NULL,

    inventory_value NUMERIC(20, 2)
        GENERATED ALWAYS AS (quantity * unit_price) STORED,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT inventory_quantity_valid CHECK (quantity >= 0),
    CONSTRAINT inventory_price_valid CHECK (unit_price >= 0)
);

CREATE INDEX idx_inventory_value
    ON inventory(inventory_value DESC);

-- 9. Controlled state transitions
CREATE TABLE customer_accounts (
    account_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_number VARCHAR(20) NOT NULL UNIQUE,
    customer_name VARCHAR(100) NOT NULL,
    balance NUMERIC(16, 2) NOT NULL DEFAULT 0,
    status property_lab.record_status NOT NULL DEFAULT 'ACTIVE',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT account_balance_valid CHECK (balance >= 0),
    CONSTRAINT account_number_valid
        CHECK (account_number ~ '^[A-Z0-9]{6,20}$')
);

CREATE OR REPLACE FUNCTION enforce_account_state()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.status = 'CLOSED' AND NEW.status <> 'CLOSED' THEN
        RAISE EXCEPTION 'Closed accounts cannot be reactivated.';
    END IF;

    NEW.updated_at := clock_timestamp();
    RETURN NEW;
END;
$$;

CREATE TRIGGER account_state_trigger
BEFORE UPDATE ON customer_accounts
FOR EACH ROW
EXECUTE FUNCTION enforce_account_state();

-- 10. Property access function
CREATE OR REPLACE FUNCTION get_employee_property(
    p_employee_id BIGINT,
    p_property_name TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT CASE pd.data_type
        WHEN 'TEXT' THEN to_jsonb(ep.text_value)
        WHEN 'INTEGER' THEN to_jsonb(ep.integer_value)
        WHEN 'DECIMAL' THEN to_jsonb(ep.decimal_value)
        WHEN 'BOOLEAN' THEN to_jsonb(ep.boolean_value)
        WHEN 'TIMESTAMP' THEN to_jsonb(ep.timestamp_value)
        WHEN 'JSON' THEN ep.json_value
    END
    INTO result
    FROM employee_properties ep
    JOIN property_definitions pd
      ON pd.property_id = ep.property_id
    WHERE ep.employee_id = p_employee_id
      AND pd.property_name = p_property_name;

    RETURN result;
END;
$$;

-- 11. Insert realistic property definitions
INSERT INTO property_definitions (
    property_name,
    data_type,
    is_required,
    is_read_only,
    minimum_value,
    maximum_value
)
VALUES
    ('department', 'TEXT', TRUE, FALSE, NULL, NULL),
    ('performance_score', 'DECIMAL', FALSE, FALSE, 0, 100),
    ('employee_number', 'INTEGER', TRUE, TRUE, 1, 999999),
    ('remote_enabled', 'BOOLEAN', FALSE, FALSE, NULL, NULL),
    ('joining_date', 'TIMESTAMP', TRUE, FALSE, NULL, NULL),
    ('preferences', 'JSON', FALSE, FALSE, NULL, NULL);

-- 12. Sample employee records
INSERT INTO employees (
    employee_code,
    employee_name,
    age,
    salary
)
VALUES
    ('EMP1001', 'Asha Sharma', 30, 75000.00),
    ('EMP1002', 'Rahul Verma', 35, 95000.00),
    ('EMP1003', 'Neha Singh', 28, 65000.00);

-- 13. Sample property values
INSERT INTO employee_properties (
    employee_id,
    property_id,
    text_value
)
SELECT e.employee_id, p.property_id,
       CASE e.employee_code
           WHEN 'EMP1001' THEN 'Engineering'
           WHEN 'EMP1002' THEN 'Security'
           ELSE 'Research'
       END
FROM employees e
CROSS JOIN property_definitions p
WHERE p.property_name = 'department';

INSERT INTO employee_properties (
    employee_id,
    property_id,
    decimal_value
)
SELECT e.employee_id, p.property_id,
       CASE e.employee_code
           WHEN 'EMP1001' THEN 92.5
           WHEN 'EMP1002' THEN 85.0
           ELSE 96.0
       END
FROM employees e
CROSS JOIN property_definitions p
WHERE p.property_name = 'performance_score';

INSERT INTO employee_properties (
    employee_id,
    property_id,
    integer_value
)
SELECT e.employee_id, p.property_id,
       CASE e.employee_code
           WHEN 'EMP1001' THEN 1001
           WHEN 'EMP1002' THEN 1002
           ELSE 1003
       END
FROM employees e
CROSS JOIN property_definitions p
WHERE p.property_name = 'employee_number';

INSERT INTO employee_properties (
    employee_id,
    property_id,
    boolean_value
)
SELECT e.employee_id, p.property_id, TRUE
FROM employees e
CROSS JOIN property_definitions p
WHERE p.property_name = 'remote_enabled';

INSERT INTO employee_properties (
    employee_id,
    property_id,
    timestamp_value
)
SELECT e.employee_id, p.property_id,
       TIMESTAMPTZ '2024-01-15 09:00:00+05:30'
FROM employees e
CROSS JOIN property_definitions p
WHERE p.property_name = 'joining_date';

INSERT INTO employee_properties (
    employee_id,
    property_id,
    json_value
)
SELECT e.employee_id, p.property_id,
       '{"theme":"dark","notifications":true}'::JSONB
FROM employees e
CROSS JOIN property_definitions p
WHERE p.property_name = 'preferences';

-- 14. Inventory records
INSERT INTO inventory (
    product_name,
    quantity,
    unit_price
)
VALUES
    ('Laptop', 10, 65000.00),
    ('Keyboard', 30, 1500.00),
    ('Mouse', 50, 750.00);

-- 15. Customer account records
INSERT INTO customer_accounts (
    account_number,
    customer_name,
    balance
)
VALUES
    ('BANK10001', 'Asha Sharma', 50000.00),
    ('BANK10002', 'Rahul Verma', 75000.00);

-- 16. Computed employee reporting view
CREATE OR REPLACE VIEW employee_property_report AS
SELECT
    e.employee_id,
    e.employee_code,
    e.employee_name,
    e.salary,
    e.is_active,
    department.text_value AS department,
    performance.decimal_value AS performance_score,
    employee_number.integer_value AS employee_number,
    remote_enabled.boolean_value AS remote_enabled,
    joining_date.timestamp_value AS joining_date
FROM employees e
LEFT JOIN property_definitions dp
    ON dp.property_name = 'department'
LEFT JOIN employee_properties department
    ON department.employee_id = e.employee_id
    AND department.property_id = dp.property_id
LEFT JOIN property_definitions pp
    ON pp.property_name = 'performance_score'
LEFT JOIN employee_properties performance
    ON performance.employee_id = e.employee_id
    AND performance.property_id = pp.property_id
LEFT JOIN property_definitions ep
    ON ep.property_name = 'employee_number'
LEFT JOIN employee_properties employee_number
    ON employee_number.employee_id = e.employee_id
    AND employee_number.property_id = ep.property_id
LEFT JOIN property_definitions rp
    ON rp.property_name = 'remote_enabled'
LEFT JOIN employee_properties remote_enabled
    ON remote_enabled.employee_id = e.employee_id
    AND remote_enabled.property_id = rp.property_id
LEFT JOIN property_definitions jp
    ON jp.property_name = 'joining_date'
LEFT JOIN employee_properties joining_date
    ON joining_date.employee_id = e.employee_id
    AND joining_date.property_id = jp.property_id;

-- 17. Property aggregation
CREATE OR REPLACE VIEW department_performance AS
SELECT
    department.text_value AS department,
    COUNT(*) AS employee_count,
    ROUND(AVG(performance.decimal_value), 2) AS average_score,
    MAX(performance.decimal_value) AS highest_score
FROM employees e
JOIN property_definitions dp
    ON dp.property_name = 'department'
JOIN employee_properties department
    ON department.property_id = dp.property_id
    AND department.employee_id = e.employee_id
JOIN property_definitions pp
    ON pp.property_name = 'performance_score'
JOIN employee_properties performance
    ON performance.property_id = pp.property_id
    AND performance.employee_id = e.employee_id
GROUP BY department.text_value;

-- 18. Update property and audit salary in one transaction
SAVEPOINT before_salary_update;

UPDATE employees
SET salary = salary * 1.05
WHERE employee_code = 'EMP1001';

-- 19. Reporting queries
SELECT *
FROM employee_property_report
ORDER BY employee_id;

SELECT *
FROM department_performance
ORDER BY average_score DESC;

SELECT
    product_name,
    quantity,
    unit_price,
    inventory_value
FROM inventory
ORDER BY inventory_value DESC;

SELECT
    account_number,
    customer_name,
    balance,
    status
FROM customer_accounts;

-- 20. Retrieve a dynamic property
SELECT get_employee_property(
    (SELECT employee_id FROM employees WHERE employee_code = 'EMP1001'),
    'department'
) AS department_property;

-- 21. Property eligibility determination
SELECT
    employee_name,
    department,
    performance_score,
    CASE
        WHEN performance_score >= 90 THEN 'ELIGIBLE'
        WHEN performance_score >= 75 THEN 'REVIEW_REQUIRED'
        ELSE 'NOT_ELIGIBLE'
    END AS performance_eligibility
FROM employee_property_report
WHERE is_active = TRUE;

-- 22. Audit report
SELECT
    table_name,
    record_identifier,
    field_name,
    old_value,
    new_value,
    changed_at,
    changed_by
FROM property_audit
ORDER BY changed_at DESC;

-- 23. Invalid account state transition example.
-- The following statement is intentionally executed inside a subtransaction.
DO $$
BEGIN
    BEGIN
        UPDATE customer_accounts
        SET status = 'CLOSED'
        WHERE account_number = 'BANK10001';

        UPDATE customer_accounts
        SET status = 'ACTIVE'
        WHERE account_number = 'BANK10001';

    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Invalid state transition rejected: %', SQLERRM;
    END;
END;
$$;

-- 24. Demonstrate constraint failure without aborting the main transaction.
DO $$
BEGIN
    BEGIN
        INSERT INTO employees (
            employee_code,
            employee_name,
            age,
            salary
        )
        VALUES ('INVALID', 'Invalid Employee', 15, -100);
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'Invalid employee data rejected.';
    END;
END;
$$;

RELEASE SAVEPOINT before_salary_update;

COMMIT;
