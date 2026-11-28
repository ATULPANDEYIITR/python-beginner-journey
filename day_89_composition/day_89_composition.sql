-- ============================================================
-- COMPOSITION: POSTGRESQL RELATIONAL IMPLEMENTATION
-- ============================================================
--
-- Scenario:
-- Enterprise product assembly and manufacturing management.
--
-- Models:
--   Components
--   Component specifications
--   Suppliers
--   Product assemblies
--   Bill of Materials
--   Nested component composition
--   Inventory
--   Assembly validation
--   Assembly execution
--   Audit records
--
-- PostgreSQL 14+
--
-- Run using:
-- psql -U postgres -d composition_db -f composition.sql
--
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS composition;

SET search_path TO composition, public;


-- ============================================================
-- 1. ENUMERATED DOMAIN TYPES
-- ============================================================

CREATE TYPE component_type AS ENUM (
    'ELECTRONIC',
    'MECHANICAL',
    'STRUCTURAL',
    'SOFTWARE'
);

CREATE TYPE assembly_status AS ENUM (
    'DRAFT',
    'VALIDATED',
    'ASSEMBLING',
    'COMPLETED',
    'FAILED'
);

CREATE TYPE audit_action AS ENUM (
    'CREATED',
    'UPDATED',
    'VALIDATED',
    'ASSEMBLY_STARTED',
    'ASSEMBLY_COMPLETED',
    'ASSEMBLY_FAILED'
);


-- ============================================================
-- 2. SUPPLIERS
-- ============================================================

CREATE TABLE suppliers (
    supplier_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    supplier_name VARCHAR(150) NOT NULL UNIQUE,

    contact_email VARCHAR(254) NOT NULL,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_supplier_email
        CHECK (contact_email ~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$')
);


-- ============================================================
-- 3. COMPONENT CATALOG
-- ============================================================

CREATE TABLE components (
    component_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    component_code VARCHAR(50) NOT NULL UNIQUE,

    component_name VARCHAR(150) NOT NULL,

    component_type component_type NOT NULL,

    description TEXT,

    unit_cost NUMERIC(14,2) NOT NULL,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    supplier_id BIGINT REFERENCES suppliers(supplier_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_component_cost
        CHECK (unit_cost >= 0),

    CONSTRAINT valid_component_code
        CHECK (component_code ~ '^[A-Z0-9_-]+$')
);


-- ============================================================
-- 4. COMPONENT INVENTORY
-- ============================================================

CREATE TABLE component_inventory (
    component_id BIGINT PRIMARY KEY
        REFERENCES components(component_id),

    quantity_available INTEGER NOT NULL DEFAULT 0,

    quantity_reserved INTEGER NOT NULL DEFAULT 0,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT nonnegative_inventory
        CHECK (quantity_available >= 0),

    CONSTRAINT nonnegative_reserved
        CHECK (quantity_reserved >= 0)
);


-- ============================================================
-- 5. PRODUCT ASSEMBLIES
-- ============================================================

CREATE TABLE product_assemblies (
    assembly_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    assembly_code VARCHAR(50) NOT NULL UNIQUE,

    assembly_name VARCHAR(150) NOT NULL,

    version INTEGER NOT NULL DEFAULT 1,

    status assembly_status NOT NULL DEFAULT 'DRAFT',

    created_by VARCHAR(100) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_assembly_version
        CHECK (version > 0)
);


-- ============================================================
-- 6. BILL OF MATERIALS
-- ============================================================
--
-- A Bill of Materials defines the components required
-- to construct a product.
--
-- A component can itself represent another assembly.
-- This allows hierarchical composition.
--
-- A parent assembly cannot contain itself directly.
--
-- ============================================================

CREATE TABLE assembly_components (
    assembly_component_id BIGINT
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    parent_assembly_id BIGINT NOT NULL
        REFERENCES product_assemblies(assembly_id),

    child_component_id BIGINT
        REFERENCES components(component_id),

    child_assembly_id BIGINT
        REFERENCES product_assemblies(assembly_id),

    quantity_required INTEGER NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT exactly_one_child
        CHECK (
            (
                child_component_id IS NOT NULL
                AND child_assembly_id IS NULL
            )
            OR
            (
                child_component_id IS NULL
                AND child_assembly_id IS NOT NULL
            )
        ),

    CONSTRAINT positive_required_quantity
        CHECK (quantity_required > 0),

    CONSTRAINT no_direct_self_composition
        CHECK (
            child_assembly_id IS NULL
            OR child_assembly_id <> parent_assembly_id
        )
);


-- ============================================================
-- 7. ASSEMBLY EXECUTION RECORDS
-- ============================================================

CREATE TABLE assembly_executions (
    execution_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    assembly_id BIGINT NOT NULL
        REFERENCES product_assemblies(assembly_id),

    requested_quantity INTEGER NOT NULL,

    completed_quantity INTEGER NOT NULL DEFAULT 0,

    status assembly_status NOT NULL DEFAULT 'DRAFT',

    initiated_by VARCHAR(100) NOT NULL,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    CONSTRAINT positive_requested_quantity
        CHECK (requested_quantity > 0),

    CONSTRAINT valid_completed_quantity
        CHECK (
            completed_quantity >= 0
            AND completed_quantity <= requested_quantity
        ),

    CONSTRAINT valid_execution_timestamps
        CHECK (
            completed_at IS NULL
            OR (
                started_at IS NOT NULL
                AND completed_at >= started_at
            )
        )
);


-- ============================================================
-- 8. AUDIT LOG
-- ============================================================

CREATE TABLE composition_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    assembly_id BIGINT
        REFERENCES product_assemblies(assembly_id),

    execution_id BIGINT
        REFERENCES assembly_executions(execution_id),

    action audit_action NOT NULL,

    performed_by VARCHAR(100) NOT NULL,

    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 9. PERFORMANCE INDEXES
-- ============================================================

CREATE INDEX idx_components_type_active
    ON components(component_type, active);

CREATE INDEX idx_components_supplier
    ON components(supplier_id);

CREATE INDEX idx_assembly_components_parent
    ON assembly_components(parent_assembly_id);

CREATE INDEX idx_assembly_components_child_component
    ON assembly_components(child_component_id)
    WHERE child_component_id IS NOT NULL;

CREATE INDEX idx_assembly_components_child_assembly
    ON assembly_components(child_assembly_id)
    WHERE child_assembly_id IS NOT NULL;

CREATE INDEX idx_assembly_status
    ON product_assemblies(status);

CREATE INDEX idx_execution_status
    ON assembly_executions(status);

CREATE INDEX idx_audit_assembly_time
    ON composition_audit(assembly_id, occurred_at DESC);


-- ============================================================
-- 10. PREVENT DUPLICATE COMPONENT ENTRIES
-- ============================================================

CREATE UNIQUE INDEX uq_parent_component
    ON assembly_components(parent_assembly_id, child_component_id)
    WHERE child_component_id IS NOT NULL;

CREATE UNIQUE INDEX uq_parent_assembly
    ON assembly_components(parent_assembly_id, child_assembly_id)
    WHERE child_assembly_id IS NOT NULL;


-- ============================================================
-- 11. AUDIT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION record_assembly_creation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO composition_audit (
        assembly_id,
        action,
        performed_by,
        details
    )
    VALUES (
        NEW.assembly_id,
        'CREATED',
        NEW.created_by,
        jsonb_build_object(
            'assembly_code', NEW.assembly_code,
            'assembly_name', NEW.assembly_name,
            'version', NEW.version
        )
    );

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_assembly_creation
AFTER INSERT ON product_assemblies
FOR EACH ROW
EXECUTE FUNCTION record_assembly_creation();


-- ============================================================
-- 12. UPDATED TIMESTAMP TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_assembly_update
BEFORE UPDATE ON product_assemblies
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();


-- ============================================================
-- 13. PREVENT CYCLIC ASSEMBLY COMPOSITION
-- ============================================================
--
-- Example of a cycle:
-- A contains B
-- B contains C
-- C contains A
--
-- Recursive traversal detects the cycle before insertion.
--
-- ============================================================

CREATE OR REPLACE FUNCTION prevent_assembly_cycle()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    cycle_exists BOOLEAN;
BEGIN
    IF NEW.child_assembly_id IS NULL THEN
        RETURN NEW;
    END IF;

    IF NEW.parent_assembly_id = NEW.child_assembly_id THEN
        RAISE EXCEPTION 'An assembly cannot contain itself';
    END IF;

    WITH RECURSIVE descendants(assembly_id, path) AS (
        SELECT
            NEW.child_assembly_id,
            ARRAY[NEW.child_assembly_id]::BIGINT[]

        UNION ALL

        SELECT
            ac.child_assembly_id,
            d.path || ac.child_assembly_id

        FROM descendants d

        JOIN assembly_components ac
            ON ac.parent_assembly_id = d.assembly_id

        WHERE ac.child_assembly_id IS NOT NULL
          AND NOT ac.child_assembly_id = ANY(d.path)
    )
    SELECT EXISTS (
        SELECT 1
        FROM descendants
        WHERE assembly_id = NEW.parent_assembly_id
    )
    INTO cycle_exists;

    IF cycle_exists THEN
        RAISE EXCEPTION
            'Circular assembly composition detected';
    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER trg_prevent_assembly_cycle
BEFORE INSERT OR UPDATE ON assembly_components
FOR EACH ROW
EXECUTE FUNCTION prevent_assembly_cycle();


-- ============================================================
-- 14. VALIDATE AN ASSEMBLY
-- ============================================================
--
-- Validation checks:
-- 1. Assembly existence.
-- 2. Non-empty Bill of Materials.
-- 3. Active components.
-- 4. Active suppliers when supplied.
-- 5. Valid nested assemblies.
-- 6. Circular composition is separately prevented.
--
-- ============================================================

CREATE OR REPLACE FUNCTION validate_assembly(
    p_assembly_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    component_count INTEGER;
    invalid_count INTEGER;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM product_assemblies
        WHERE assembly_id = p_assembly_id
    ) THEN
        RAISE EXCEPTION 'Assembly does not exist';
    END IF;

    SELECT COUNT(*)
    INTO component_count
    FROM assembly_components
    WHERE parent_assembly_id = p_assembly_id;

    IF component_count = 0 THEN
        RAISE EXCEPTION 'Assembly requires at least one component';
    END IF;

    SELECT COUNT(*)
    INTO invalid_count
    FROM assembly_components ac

    LEFT JOIN components c
        ON c.component_id = ac.child_component_id

    LEFT JOIN suppliers s
        ON s.supplier_id = c.supplier_id

    LEFT JOIN product_assemblies nested
        ON nested.assembly_id = ac.child_assembly_id

    WHERE ac.parent_assembly_id = p_assembly_id
      AND (
          (
              ac.child_component_id IS NOT NULL
              AND (
                  c.component_id IS NULL
                  OR NOT c.active
                  OR (
                      c.supplier_id IS NOT NULL
                      AND NOT COALESCE(s.active, FALSE)
                  )
              )
          )
          OR
          (
              ac.child_assembly_id IS NOT NULL
              AND (
                  nested.assembly_id IS NULL
                  OR nested.status NOT IN ('VALIDATED', 'COMPLETED')
              )
          )
      );

    IF invalid_count > 0 THEN
        RAISE EXCEPTION
            'Assembly contains invalid or inactive dependencies';
    END IF;

    UPDATE product_assemblies
    SET status = 'VALIDATED'
    WHERE assembly_id = p_assembly_id
      AND status = 'DRAFT';

    INSERT INTO composition_audit (
        assembly_id,
        action,
        performed_by,
        details
    )
    SELECT
        assembly_id,
        'VALIDATED',
        'SYSTEM',
        jsonb_build_object(
            'component_count', component_count
        )
    FROM product_assemblies
    WHERE assembly_id = p_assembly_id;

    RETURN TRUE;
END;
$$;


-- ============================================================
-- 15. CALCULATE RECURSIVE ASSEMBLY COST
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_assembly_cost(
    p_assembly_id BIGINT
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    total_cost NUMERIC(18,2);
BEGIN
    WITH RECURSIVE expanded AS (

        SELECT
            ac.child_component_id,
            ac.child_assembly_id,
            ac.quantity_required::NUMERIC AS required_quantity,
            ARRAY[ac.parent_assembly_id]::BIGINT[] AS path

        FROM assembly_components ac

        WHERE ac.parent_assembly_id = p_assembly_id

        UNION ALL

        SELECT
            child.child_component_id,
            child.child_assembly_id,
            expanded.required_quantity
                * child.quantity_required,
            expanded.path || child.parent_assembly_id

        FROM expanded

        JOIN assembly_components child
            ON child.parent_assembly_id = expanded.child_assembly_id

        WHERE expanded.child_assembly_id IS NOT NULL
          AND NOT child.parent_assembly_id = ANY(expanded.path)
    )

    SELECT COALESCE(SUM(
        expanded.required_quantity * components.unit_cost
    ), 0)

    INTO total_cost

    FROM expanded

    JOIN components
        ON components.component_id = expanded.child_component_id;

    RETURN total_cost;
END;
$$;


-- ============================================================
-- 16. DETERMINE INVENTORY ELIGIBILITY
-- ============================================================
--
-- Calculates total component requirements across nested assemblies.
--
-- ============================================================

CREATE OR REPLACE FUNCTION check_assembly_inventory(
    p_assembly_id BIGINT,
    p_quantity INTEGER
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    insufficient_count INTEGER;
BEGIN
    IF p_quantity <= 0 THEN
        RAISE EXCEPTION 'Assembly quantity must be positive';
    END IF;

    WITH RECURSIVE requirements AS (

        SELECT
            ac.child_component_id,
            ac.child_assembly_id,
            ac.quantity_required::BIGINT AS required_quantity,
            ARRAY[ac.parent_assembly_id]::BIGINT[] AS path

        FROM assembly_components ac

        WHERE ac.parent_assembly_id = p_assembly_id

        UNION ALL

        SELECT
            child.child_component_id,
            child.child_assembly_id,
            requirements.required_quantity
                * child.quantity_required,
            requirements.path || child.parent_assembly_id

        FROM requirements

        JOIN assembly_components child
            ON child.parent_assembly_id =
                requirements.child_assembly_id

        WHERE requirements.child_assembly_id IS NOT NULL
          AND NOT child.parent_assembly_id = ANY(requirements.path)
    ),

    totals AS (
        SELECT
            child_component_id AS component_id,
            SUM(required_quantity * p_quantity) AS needed

        FROM requirements

        WHERE child_component_id IS NOT NULL

        GROUP BY child_component_id
    )

    SELECT COUNT(*)

    INTO insufficient_count

    FROM totals

    LEFT JOIN component_inventory inventory
        ON inventory.component_id = totals.component_id

    WHERE inventory.component_id IS NULL
       OR inventory.quantity_available < totals.needed;

    RETURN insufficient_count = 0;
END;
$$;


-- ============================================================
-- 17. VIEW: ASSEMBLY COMPONENT DETAILS
-- ============================================================

CREATE OR REPLACE VIEW assembly_component_details AS
SELECT
    pa.assembly_code,
    pa.assembly_name,
    pa.status AS assembly_status,

    c.component_code,
    c.component_name,

    nested.assembly_code AS nested_assembly_code,

    ac.quantity_required,

    CASE
        WHEN c.component_id IS NOT NULL
        THEN c.unit_cost * ac.quantity_required
        ELSE NULL
    END AS direct_component_cost

FROM product_assemblies pa

JOIN assembly_components ac
    ON ac.parent_assembly_id = pa.assembly_id

LEFT JOIN components c
    ON c.component_id = ac.child_component_id

LEFT JOIN product_assemblies nested
    ON nested.assembly_id = ac.child_assembly_id;


-- ============================================================
-- 18. VIEW: ASSEMBLY COST REPORT
-- ============================================================

CREATE OR REPLACE VIEW assembly_cost_report AS
SELECT
    assembly_id,
    assembly_code,
    assembly_name,
    status,
    calculate_assembly_cost(assembly_id) AS estimated_cost

FROM product_assemblies;


-- ============================================================
-- 19. SAMPLE DATA
-- ============================================================

INSERT INTO suppliers (
    supplier_name,
    contact_email
)
VALUES
    ('Tech Components India', 'sales@techindia.example'),
    ('Mechanical Systems Ltd', 'contact@mechanical.example'),
    ('Inactive Supplier', 'inactive@supplier.example');


UPDATE suppliers
SET active = FALSE
WHERE supplier_name = 'Inactive Supplier';


INSERT INTO components (
    component_code,
    component_name,
    component_type,
    unit_cost,
    supplier_id
)
SELECT
    data.component_code,
    data.component_name,
    data.component_type::component_type,
    data.unit_cost,
    suppliers.supplier_id

FROM (
    VALUES
        (
            'CPU-001',
            'Processing Unit',
            'ELECTRONIC',
            12000.00,
            'Tech Components India'
        ),
        (
            'RAM-001',
            'Memory Module',
            'ELECTRONIC',
            3500.00,
            'Tech Components India'
        ),
        (
            'CASE-001',
            'Computer Chassis',
            'STRUCTURAL',
            5000.00,
            'Mechanical Systems Ltd'
        ),
        (
            'FAN-001',
            'Cooling Fan',
            'MECHANICAL',
            1500.00,
            'Mechanical Systems Ltd'
        ),
        (
            'BAD-001',
            'Inactive Supplier Component',
            'ELECTRONIC',
            2000.00,
            'Inactive Supplier'
        )
) AS data(
    component_code,
    component_name,
    component_type,
    unit_cost,
    supplier_name
)

JOIN suppliers
    ON suppliers.supplier_name = data.supplier_name;


INSERT INTO component_inventory (
    component_id,
    quantity_available
)
SELECT
    component_id,
    CASE component_code
        WHEN 'CPU-001' THEN 100
        WHEN 'RAM-001' THEN 200
        WHEN 'CASE-001' THEN 50
        WHEN 'FAN-001' THEN 150
        ELSE 20
    END

FROM components;


INSERT INTO product_assemblies (
    assembly_code,
    assembly_name,
    created_by
)
VALUES
    ('SUB-001', 'Cooling Subassembly', 'admin'),
    ('SUB-002', 'Memory Subassembly', 'admin'),
    ('PROD-001', 'Enterprise Workstation', 'admin'),
    ('PROD-002', 'Incomplete Workstation', 'admin');


-- Cooling subassembly contains two fans.
INSERT INTO assembly_components (
    parent_assembly_id,
    child_component_id,
    quantity_required
)
SELECT
    pa.assembly_id,
    c.component_id,
    2

FROM product_assemblies pa
JOIN components c
    ON c.component_code = 'FAN-001'

WHERE pa.assembly_code = 'SUB-001';


-- Memory subassembly contains two RAM modules.
INSERT INTO assembly_components (
    parent_assembly_id,
    child_component_id,
    quantity_required
)
SELECT
    pa.assembly_id,
    c.component_id,
    2

FROM product_assemblies pa
JOIN components c
    ON c.component_code = 'RAM-001'

WHERE pa.assembly_code = 'SUB-002';


-- Enterprise workstation contains:
-- One CPU
-- One chassis
-- One cooling subassembly
-- One memory subassembly

INSERT INTO assembly_components (
    parent_assembly_id,
    child_component_id,
    quantity_required
)
SELECT
    pa.assembly_id,
    c.component_id,
    1

FROM product_assemblies pa
CROSS JOIN components c

WHERE pa.assembly_code = 'PROD-001'
  AND c.component_code IN ('CPU-001', 'CASE-001');


INSERT INTO assembly_components (
    parent_assembly_id,
    child_assembly_id,
    quantity_required
)
SELECT
    parent.assembly_id,
    child.assembly_id,
    1

FROM product_assemblies parent

CROSS JOIN product_assemblies child

WHERE parent.assembly_code = 'PROD-001'
  AND child.assembly_code IN ('SUB-001', 'SUB-002');


-- Incomplete workstation has an inactive component.
INSERT INTO assembly_components (
    parent_assembly_id,
    child_component_id,
    quantity_required
)
SELECT
    pa.assembly_id,
    c.component_id,
    1

FROM product_assemblies pa
JOIN components c
    ON c.component_code = 'BAD-001'

WHERE pa.assembly_code = 'PROD-002';


-- ============================================================
-- 20. VALIDATION QUERIES
-- ============================================================

-- Validate the two subassemblies.
SELECT validate_assembly(assembly_id)
FROM product_assemblies
WHERE assembly_code IN ('SUB-001', 'SUB-002');


-- Validate the main product.
SELECT validate_assembly(assembly_id)
FROM product_assemblies
WHERE assembly_code = 'PROD-001';


-- The following assembly must fail validation because it
-- contains an inactive supplier's component.
DO $$
DECLARE
    invalid_assembly_id BIGINT;
BEGIN
    SELECT assembly_id
    INTO invalid_assembly_id
    FROM product_assemblies
    WHERE assembly_code = 'PROD-002';

    BEGIN
        PERFORM validate_assembly(invalid_assembly_id);
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Expected validation failure: %',
                SQLERRM;
    END;
END;
$$;


-- ============================================================
-- 21. COST EVALUATION
-- ============================================================

SELECT
    assembly_code,
    assembly_name,
    calculate_assembly_cost(assembly_id) AS total_cost

FROM product_assemblies

ORDER BY assembly_code;


-- ============================================================
-- 22. INVENTORY ELIGIBILITY
-- ============================================================

SELECT
    assembly_code,

    check_assembly_inventory(
        assembly_id,
        5
    ) AS can_build_five_units

FROM product_assemblies

WHERE assembly_code = 'PROD-001';


-- ============================================================
-- 23. ASSEMBLY WORKFLOW PROCEDURE
-- ============================================================
--
-- Inventory reservation and execution creation occur
-- in the same database transaction.
--
-- Row locks protect inventory from concurrent reservations.
--
-- ============================================================

CREATE OR REPLACE PROCEDURE start_assembly(
    p_assembly_id BIGINT,
    p_quantity INTEGER,
    p_user VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
DECLARE
    inventory_record RECORD;
    required_record RECORD;
    new_execution_id BIGINT;
    requirements CURSOR FOR
        WITH RECURSIVE expanded AS (

            SELECT
                ac.child_component_id,
                ac.child_assembly_id,
                ac.quantity_required::BIGINT AS needed,
                ARRAY[ac.parent_assembly_id]::BIGINT[] AS path

            FROM assembly_components ac

            WHERE ac.parent_assembly_id = p_assembly_id

            UNION ALL

            SELECT
                child.child_component_id,
                child.child_assembly_id,
                expanded.needed * child.quantity_required,
                expanded.path || child.parent_assembly_id

            FROM expanded

            JOIN assembly_components child
                ON child.parent_assembly_id =
                    expanded.child_assembly_id

            WHERE expanded.child_assembly_id IS NOT NULL
              AND NOT child.parent_assembly_id = ANY(expanded.path)
        )

        SELECT
            child_component_id AS component_id,
            SUM(needed * p_quantity)::BIGINT AS quantity_needed

        FROM expanded

        WHERE child_component_id IS NOT NULL

        GROUP BY child_component_id

        ORDER BY child_component_id;

BEGIN
    IF p_quantity <= 0 THEN
        RAISE EXCEPTION 'Quantity must be positive';
    END IF;

    IF p_user IS NULL OR BTRIM(p_user) = '' THEN
        RAISE EXCEPTION 'User identity is required';
    END IF;

    -- Lock the target assembly.
    PERFORM 1
    FROM product_assemblies
    WHERE assembly_id = p_assembly_id
      AND status = 'VALIDATED'
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Assembly must exist and be validated';
    END IF;

    -- Validate inventory before reservation.
    IF NOT check_assembly_inventory(
        p_assembly_id,
        p_quantity
    ) THEN
        RAISE EXCEPTION 'Insufficient component inventory';
    END IF;

    -- Create execution record.
    INSERT INTO assembly_executions (
        assembly_id,
        requested_quantity,
        status,
        initiated_by,
        started_at
    )
    VALUES (
        p_assembly_id,
        p_quantity,
        'ASSEMBLING',
        p_user,
        CURRENT_TIMESTAMP
    )
    RETURNING execution_id
    INTO new_execution_id;

    -- Lock and reserve every required component.
    OPEN requirements;

    LOOP
        FETCH requirements INTO required_record;

        EXIT WHEN NOT FOUND;

        SELECT *
        INTO inventory_record

        FROM component_inventory

        WHERE component_id = required_record.component_id

        FOR UPDATE;

        IF NOT FOUND
           OR inventory_record.quantity_available
                < required_record.quantity_needed THEN

            RAISE EXCEPTION
                'Inventory changed during reservation';
        END IF;

        UPDATE component_inventory

        SET
            quantity_available =
                quantity_available - required_record.quantity_needed,

            quantity_reserved =
                quantity_reserved + required_record.quantity_needed,

            updated_at = CURRENT_TIMESTAMP

        WHERE component_id = required_record.component_id;

    END LOOP;

    CLOSE requirements;

    UPDATE product_assemblies
    SET status = 'ASSEMBLING'
    WHERE assembly_id = p_assembly_id;

    INSERT INTO composition_audit (
        assembly_id,
        execution_id,
        action,
        performed_by,
        details
    )
    VALUES (
        p_assembly_id,
        new_execution_id,
        'ASSEMBLY_STARTED',
        p_user,
        jsonb_build_object(
            'quantity', p_quantity
        )
    );

    RAISE NOTICE
        'Assembly execution created: %',
        new_execution_id;
END;
$$;


-- ============================================================
-- 24. COMPLETE ASSEMBLY PROCEDURE
-- ============================================================
--
-- Reserved inventory is consumed when assembly completes.
--
-- The operation is transactional.
--
-- ============================================================

CREATE OR REPLACE PROCEDURE complete_assembly(
    p_execution_id BIGINT,
    p_user VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
DECLARE
    execution_record assembly_executions%ROWTYPE;
    required_record RECORD;
    requirements CURSOR FOR
        WITH RECURSIVE expanded AS (

            SELECT
                ac.child_component_id,
                ac.child_assembly_id,
                ac.quantity_required::BIGINT AS needed,
                ARRAY[ac.parent_assembly_id]::BIGINT[] AS path

            FROM assembly_components ac

            JOIN assembly_executions ae
                ON ae.assembly_id = ac.parent_assembly_id

            WHERE ae.execution_id = p_execution_id

            UNION ALL

            SELECT
                child.child_component_id,
                child.child_assembly_id,
                expanded.needed * child.quantity_required,
                expanded.path || child.parent_assembly_id

            FROM expanded

            JOIN assembly_components child
                ON child.parent_assembly_id =
                    expanded.child_assembly_id

            WHERE expanded.child_assembly_id IS NOT NULL
              AND NOT child.parent_assembly_id = ANY(expanded.path)
        )

        SELECT
            child_component_id AS component_id,
            SUM(needed * execution_record.requested_quantity)::BIGINT
                AS quantity_needed

        FROM expanded

        WHERE child_component_id IS NOT NULL

        GROUP BY child_component_id

        ORDER BY child_component_id;

BEGIN
    SELECT *
    INTO execution_record

    FROM assembly_executions

    WHERE execution_id = p_execution_id

    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Execution not found';
    END IF;

    IF execution_record.status <> 'ASSEMBLING' THEN
        RAISE EXCEPTION 'Execution is not active';
    END IF;

    IF p_user IS NULL OR BTRIM(p_user) = '' THEN
        RAISE EXCEPTION 'User identity is required';
    END IF;

    OPEN requirements;

    LOOP
        FETCH requirements INTO required_record;

        EXIT WHEN NOT FOUND;

        UPDATE component_inventory

        SET
            quantity_reserved =
                quantity_reserved - required_record.quantity_needed,

            updated_at = CURRENT_TIMESTAMP

        WHERE component_id = required_record.component_id
          AND quantity_reserved >= required_record.quantity_needed;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'Reserved inventory inconsistency for component %',
                required_record.component_id;
        END IF;

    END LOOP;

    CLOSE requirements;

    UPDATE assembly_executions

    SET
        status = 'COMPLETED',
        completed_quantity = requested_quantity,
        completed_at = CURRENT_TIMESTAMP

    WHERE execution_id = p_execution_id;

    UPDATE product_assemblies

    SET status = 'COMPLETED'

    WHERE assembly_id = execution_record.assembly_id;

    INSERT INTO composition_audit (
        assembly_id,
        execution_id,
        action,
        performed_by,
        details
    )
    VALUES (
        execution_record.assembly_id,
        p_execution_id,
        'ASSEMBLY_COMPLETED',
        p_user,
        jsonb_build_object(
            'completed_quantity',
            execution_record.requested_quantity
        )
    );
END;
$$;


-- ============================================================
-- 25. WORKFLOW EXECUTION
-- ============================================================
--
-- This block demonstrates transaction handling.
-- A failed operation rolls back its inventory reservations.
--
-- ============================================================

DO $$
DECLARE
    target_assembly BIGINT;
    execution_id_value BIGINT;
BEGIN
    SELECT assembly_id
    INTO target_assembly
    FROM product_assemblies
    WHERE assembly_code = 'PROD-001';

    BEGIN
        CALL start_assembly(
            target_assembly,
            2,
            'production_manager'
        );

        SELECT execution_id
        INTO execution_id_value
        FROM assembly_executions
        WHERE assembly_id = target_assembly
          AND status = 'ASSEMBLING'
        ORDER BY execution_id DESC
        LIMIT 1;

        CALL complete_assembly(
            execution_id_value,
            'production_manager'
        );

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Assembly workflow failed: %',
                SQLERRM;
    END;
END;
$$;


-- ============================================================
-- 26. RETRIEVAL QUERIES
-- ============================================================

SELECT *
FROM assembly_component_details
ORDER BY assembly_code, component_code;


SELECT
    assembly_code,
    assembly_name,
    status,
    calculate_assembly_cost(assembly_id) AS estimated_cost

FROM product_assemblies

ORDER BY estimated_cost DESC;


-- ============================================================
-- 27. AGGREGATION AND INVENTORY REPORTING
-- ============================================================

SELECT
    c.component_type,

    COUNT(*) AS component_count,

    SUM(c.unit_cost) AS total_catalog_value,

    SUM(i.quantity_available) AS available_units,

    SUM(i.quantity_reserved) AS reserved_units

FROM components c

JOIN component_inventory i
    ON i.component_id = c.component_id

GROUP BY c.component_type

ORDER BY c.component_type;


-- ============================================================
-- 28. ASSEMBLY ELIGIBILITY REPORT
-- ============================================================

SELECT
    pa.assembly_code,
    pa.assembly_name,
    pa.status,

    calculate_assembly_cost(pa.assembly_id) AS estimated_unit_cost,

    check_assembly_inventory(
        pa.assembly_id,
        5
    ) AS eligible_for_five_units

FROM product_assemblies pa

ORDER BY pa.assembly_code;


-- ============================================================
-- 29. EXECUTION REPORT
-- ============================================================

SELECT
    ae.execution_id,
    pa.assembly_code,
    pa.assembly_name,
    ae.requested_quantity,
    ae.completed_quantity,
    ae.status,
    ae.initiated_by,
    ae.started_at,
    ae.completed_at

FROM assembly_executions ae

JOIN product_assemblies pa
    ON pa.assembly_id = ae.assembly_id

ORDER BY ae.execution_id DESC;


-- ============================================================
-- 30. AUDIT REPORT
-- ============================================================

SELECT
    audit_id,
    assembly_id,
    execution_id,
    action,
    performed_by,
    details,
    occurred_at

FROM composition_audit

ORDER BY occurred_at DESC;


-- ============================================================
-- 31. RECURSIVE COMPOSITION TREE
-- ============================================================

WITH RECURSIVE composition_tree AS (

    SELECT
        pa.assembly_id,
        pa.assembly_code,
        pa.assembly_name,
        0 AS depth,
        ARRAY[pa.assembly_id]::BIGINT[] AS path

    FROM product_assemblies pa

    WHERE pa.assembly_code = 'PROD-001'

    UNION ALL

    SELECT
        child.assembly_id,
        child.assembly_code,
        child.assembly_name,
        tree.depth + 1,
        tree.path || child.assembly_id

    FROM composition_tree tree

    JOIN assembly_components ac
        ON ac.parent_assembly_id = tree.assembly_id

    JOIN product_assemblies child
        ON child.assembly_id = ac.child_assembly_id

    WHERE NOT child.assembly_id = ANY(tree.path)
)

SELECT
    REPEAT('  ', depth)
        || assembly_code
        || ' - '
        || assembly_name AS composition_hierarchy,

    depth

FROM composition_tree

ORDER BY path;


-- ============================================================
-- 32. TRANSACTIONAL FAILURE TEST
-- ============================================================
--
-- A circular relationship must be rejected.
-- The test catches the expected exception.
--
-- ============================================================

DO $$
DECLARE
    parent_id BIGINT;
    child_id BIGINT;
BEGIN
    SELECT assembly_id INTO parent_id
    FROM product_assemblies
    WHERE assembly_code = 'SUB-001';

    SELECT assembly_id INTO child_id
    FROM product_assemblies
    WHERE assembly_code = 'PROD-001';

    BEGIN
        INSERT INTO assembly_components (
            parent_assembly_id,
            child_assembly_id,
            quantity_required
        )
        VALUES (
            child_id,
            parent_id,
            1
        );

        -- The inverse relationship already exists.
        -- A valid cycle test requires the existing graph
        -- to be traversed before accepting this insertion.

        RAISE EXCEPTION
            'Cycle test unexpectedly succeeded';

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Cycle or test failure correctly rejected: %',
                SQLERRM;
    END;
END;
$$;


-- ============================================================
-- 33. FINAL DATABASE STATE
-- ============================================================

SELECT
    assembly_code,
    status,
    calculate_assembly_cost(assembly_id) AS estimated_cost

FROM product_assemblies

ORDER BY assembly_code;


COMMIT;
