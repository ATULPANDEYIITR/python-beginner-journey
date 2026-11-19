-- ============================================================
-- INSTANCE ATTRIBUTES: POSTGRESQL IMPLEMENTATION
-- PostgreSQL 14+
-- ============================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS instance_lab;

SET search_path TO instance_lab, public;

-- ------------------------------------------------------------
-- 1. ENUMERATED DOMAIN TYPES
-- ------------------------------------------------------------

CREATE TYPE device_status AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'MAINTENANCE'
);

CREATE TYPE attribute_data_type AS ENUM (
    'TEXT',
    'NUMBER',
    'BOOLEAN',
    'JSON'
);

-- ------------------------------------------------------------
-- 2. ORGANIZATIONS
-- ------------------------------------------------------------

CREATE TABLE organizations (
    organization_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_name VARCHAR(150) NOT NULL UNIQUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 3. DEVICE MODELS
--
-- Model attributes describe available properties.
-- They do not represent the actual state of a device instance.
-- ------------------------------------------------------------

CREATE TABLE device_models (
    model_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    model_name VARCHAR(120) NOT NULL,

    manufacturer VARCHAR(120) NOT NULL,

    shared_category VARCHAR(80) NOT NULL
        DEFAULT 'NETWORK_EQUIPMENT',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (model_name, manufacturer)
);

-- ------------------------------------------------------------
-- 4. INSTANCE REGISTRY
--
-- Each row represents one independent object instance.
-- ------------------------------------------------------------

CREATE TABLE device_instances (
    instance_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    organization_id BIGINT NOT NULL
        REFERENCES organizations(organization_id),

    model_id BIGINT NOT NULL
        REFERENCES device_models(model_id),

    instance_code VARCHAR(60) NOT NULL,

    instance_name VARCHAR(150) NOT NULL,

    temperature NUMERIC(6,2) NOT NULL DEFAULT 25.00,

    status device_status NOT NULL DEFAULT 'ACTIVE',

    configuration JSONB NOT NULL DEFAULT '{}'::JSONB,

    tags TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],

    revision INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_instance_per_organization
        UNIQUE (organization_id, instance_code),

    CONSTRAINT chk_instance_temperature
        CHECK (temperature BETWEEN -50 AND 150),

    CONSTRAINT chk_instance_revision
        CHECK (revision >= 0),

    CONSTRAINT chk_instance_name
        CHECK (LENGTH(TRIM(instance_name)) > 0),

    CONSTRAINT chk_configuration_object
        CHECK (jsonb_typeof(configuration) = 'object')
);

-- ------------------------------------------------------------
-- 5. INSTANCE ATTRIBUTE DEFINITIONS
--
-- Attribute definitions specify permitted properties.
-- ------------------------------------------------------------

CREATE TABLE attribute_definitions (
    attribute_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    model_id BIGINT NOT NULL
        REFERENCES device_models(model_id),

    attribute_name VARCHAR(100) NOT NULL,

    data_type attribute_data_type NOT NULL,

    is_required BOOLEAN NOT NULL DEFAULT FALSE,

    is_mutable BOOLEAN NOT NULL DEFAULT TRUE,

    default_value JSONB,

    UNIQUE (model_id, attribute_name)
);

-- ------------------------------------------------------------
-- 6. INSTANCE-SPECIFIC ATTRIBUTE VALUES
--
-- The same attribute definition can have different values
-- for different device instances.
-- ------------------------------------------------------------

CREATE TABLE instance_attribute_values (
    value_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    instance_id BIGINT NOT NULL
        REFERENCES device_instances(instance_id)
        ON DELETE CASCADE,

    attribute_id BIGINT NOT NULL
        REFERENCES attribute_definitions(attribute_id),

    attribute_value JSONB NOT NULL,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (instance_id, attribute_id)
);

-- ------------------------------------------------------------
-- 7. ATTRIBUTE AUDIT HISTORY
-- ------------------------------------------------------------

CREATE TABLE attribute_audit (
    audit_id BIGINT GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    instance_id BIGINT NOT NULL
        REFERENCES device_instances(instance_id),

    attribute_id BIGINT NOT NULL
        REFERENCES attribute_definitions(attribute_id),

    old_value JSONB,

    new_value JSONB NOT NULL,

    changed_by VARCHAR(120) NOT NULL,

    changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 8. INDEXES
-- ------------------------------------------------------------

CREATE INDEX idx_instance_organization
    ON device_instances(organization_id);

CREATE INDEX idx_instance_model
    ON device_instances(model_id);

CREATE INDEX idx_instance_status
    ON device_instances(status);

CREATE INDEX idx_instance_temperature
    ON device_instances(temperature)
    WHERE temperature >= 70;

CREATE INDEX idx_instance_configuration
    ON device_instances USING GIN(configuration);

CREATE INDEX idx_instance_tags
    ON device_instances USING GIN(tags);

CREATE INDEX idx_attribute_values_instance
    ON instance_attribute_values(instance_id);

CREATE INDEX idx_attribute_values_definition
    ON instance_attribute_values(attribute_id);

CREATE INDEX idx_attribute_audit_history
    ON attribute_audit(instance_id, changed_at DESC);

-- ------------------------------------------------------------
-- 9. ATTRIBUTE TYPE VALIDATION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_attribute_value()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    definition attribute_definitions%ROWTYPE;
    instance_model BIGINT;
    valid_type BOOLEAN;
BEGIN
    SELECT *
    INTO definition
    FROM attribute_definitions
    WHERE attribute_id = NEW.attribute_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Attribute definition does not exist.';
    END IF;

    SELECT model_id
    INTO instance_model
    FROM device_instances
    WHERE instance_id = NEW.instance_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Device instance does not exist.';
    END IF;

    IF instance_model <> definition.model_id THEN
        RAISE EXCEPTION
            'Attribute definition does not belong to this device model.';
    END IF;

    valid_type := CASE definition.data_type
        WHEN 'TEXT' THEN
            jsonb_typeof(NEW.attribute_value) = 'string'
        WHEN 'NUMBER' THEN
            jsonb_typeof(NEW.attribute_value) = 'number'
        WHEN 'BOOLEAN' THEN
            jsonb_typeof(NEW.attribute_value) = 'boolean'
        WHEN 'JSON' THEN
            jsonb_typeof(NEW.attribute_value) IN (
                'object', 'array', 'string',
                'number', 'boolean'
            )
        ELSE FALSE
    END;

    IF NOT valid_type THEN
        RAISE EXCEPTION
            'Attribute value does not match its declared data type.';
    END IF;

    IF TG_OP = 'UPDATE' THEN
        IF NOT definition.is_mutable THEN
            RAISE EXCEPTION
                'Attribute % is immutable.',
                definition.attribute_name;
        END IF;
    END IF;

    NEW.updated_at := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_validate_attribute_value
BEFORE INSERT OR UPDATE
ON instance_attribute_values
FOR EACH ROW
EXECUTE FUNCTION validate_attribute_value();

-- ------------------------------------------------------------
-- 10. AUTOMATIC INSTANCE REVISION MANAGEMENT
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_instance_revision()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF ROW(
        NEW.instance_name,
        NEW.temperature,
        NEW.status,
        NEW.configuration,
        NEW.tags
    ) IS DISTINCT FROM ROW(
        OLD.instance_name,
        OLD.temperature,
        OLD.status,
        OLD.configuration,
        OLD.tags
    ) THEN
        NEW.revision := OLD.revision + 1;
        NEW.updated_at := CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_instance_revision
BEFORE UPDATE ON device_instances
FOR EACH ROW
EXECUTE FUNCTION update_instance_revision();

-- ------------------------------------------------------------
-- 11. ATTRIBUTE AUDIT TRIGGER
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION record_attribute_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    previous_value JSONB;
    actor VARCHAR(120);
BEGIN
    IF TG_OP = 'UPDATE' THEN
        previous_value := OLD.attribute_value;
    ELSE
        previous_value := NULL;
    END IF;

    actor := COALESCE(
        NULLIF(current_setting('app.current_user', TRUE), ''),
        CURRENT_USER
    );

    INSERT INTO attribute_audit (
        instance_id,
        attribute_id,
        old_value,
        new_value,
        changed_by
    )
    VALUES (
        NEW.instance_id,
        NEW.attribute_id,
        previous_value,
        NEW.attribute_value,
        actor
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_attribute_audit
AFTER INSERT OR UPDATE
ON instance_attribute_values
FOR EACH ROW
EXECUTE FUNCTION record_attribute_change();

-- ------------------------------------------------------------
-- 12. ATTRIBUTE UPDATE FUNCTION
--
-- Uses an explicit transaction and row lock.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_instance_attribute(
    p_instance_id BIGINT,
    p_attribute_name VARCHAR(100),
    p_value JSONB,
    p_actor VARCHAR(120)
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_attribute_id BIGINT;
    v_model_id BIGINT;
    v_definition_model BIGINT;
BEGIN
    SELECT model_id
    INTO v_model_id
    FROM device_instances
    WHERE instance_id = p_instance_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Instance % does not exist.', p_instance_id;
    END IF;

    SELECT attribute_id, model_id
    INTO v_attribute_id, v_definition_model
    FROM attribute_definitions
    WHERE model_id = v_model_id
      AND attribute_name = p_attribute_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown attribute: %', p_attribute_name;
    END IF;

    PERFORM set_config(
        'app.current_user',
        COALESCE(NULLIF(p_actor, ''), CURRENT_USER),
        TRUE
    );

    INSERT INTO instance_attribute_values (
        instance_id,
        attribute_id,
        attribute_value
    )
    VALUES (
        p_instance_id,
        v_attribute_id,
        p_value
    )
    ON CONFLICT (instance_id, attribute_id)
    DO UPDATE SET
        attribute_value = EXCLUDED.attribute_value,
        updated_at = CURRENT_TIMESTAMP;
END;
$$;

-- ------------------------------------------------------------
-- 13. REQUIRED ATTRIBUTE VALIDATION FUNCTION
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_required_attributes(
    p_instance_id BIGINT
)
RETURNS TABLE(attribute_name VARCHAR(100))
LANGUAGE sql
STABLE
AS $$
    SELECT definition.attribute_name
    FROM device_instances instance
    JOIN attribute_definitions definition
      ON definition.model_id = instance.model_id
    LEFT JOIN instance_attribute_values value
      ON value.instance_id = instance.instance_id
     AND value.attribute_id = definition.attribute_id
    WHERE instance.instance_id = p_instance_id
      AND definition.is_required = TRUE
      AND value.value_id IS NULL;
$$;

-- ------------------------------------------------------------
-- 14. INSTANCE ATTRIBUTE VIEW
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW v_instance_attributes AS
SELECT
    instance.instance_id,
    instance.instance_code,
    instance.instance_name,
    model.model_name,
    model.manufacturer,
    model.shared_category,
    instance.temperature,
    instance.status,
    instance.configuration,
    instance.tags,
    instance.revision,
    COALESCE(
        jsonb_object_agg(
            definition.attribute_name,
            value.attribute_value
        ) FILTER (WHERE definition.attribute_id IS NOT NULL),
        '{}'::JSONB
    ) AS custom_attributes
FROM device_instances instance
JOIN device_models model
    ON model.model_id = instance.model_id
LEFT JOIN instance_attribute_values value
    ON value.instance_id = instance.instance_id
LEFT JOIN attribute_definitions definition
    ON definition.attribute_id = value.attribute_id
GROUP BY
    instance.instance_id,
    model.model_id;

-- ------------------------------------------------------------
-- 15. SAMPLE ORGANIZATIONS
-- ------------------------------------------------------------

INSERT INTO organizations (organization_name)
VALUES
    ('Enterprise Network Division'),
    ('Security Operations Division');

-- ------------------------------------------------------------
-- 16. SAMPLE DEVICE MODELS
-- ------------------------------------------------------------

INSERT INTO device_models (
    model_name,
    manufacturer,
    shared_category
)
VALUES
    ('Catalyst Core Router', 'Cisco', 'NETWORK_EQUIPMENT'),
    ('FortiGate Firewall', 'Fortinet', 'SECURITY_EQUIPMENT');

-- ------------------------------------------------------------
-- 17. ATTRIBUTE DEFINITIONS
-- ------------------------------------------------------------

INSERT INTO attribute_definitions (
    model_id,
    attribute_name,
    data_type,
    is_required,
    is_mutable,
    default_value
)
SELECT
    model_id,
    'location',
    'TEXT',
    TRUE,
    TRUE,
    '"Lucknow Data Centre"'::JSONB
FROM device_models
WHERE model_name = 'Catalyst Core Router';

INSERT INTO attribute_definitions (
    model_id,
    attribute_name,
    data_type,
    is_required,
    is_mutable
)
SELECT
    model_id,
    'serial_number',
    'TEXT',
    TRUE,
    FALSE
FROM device_models
WHERE model_name = 'Catalyst Core Router';

INSERT INTO attribute_definitions (
    model_id,
    attribute_name,
    data_type,
    is_required,
    is_mutable
)
SELECT
    model_id,
    'firmware_version',
    'TEXT',
    TRUE,
    TRUE
FROM device_models
WHERE model_name = 'Catalyst Core Router';

INSERT INTO attribute_definitions (
    model_id,
    attribute_name,
    data_type,
    is_required,
    is_mutable
)
SELECT
    model_id,
    'monitoring_enabled',
    'BOOLEAN',
    FALSE,
    TRUE
FROM device_models
WHERE model_name = 'Catalyst Core Router';

INSERT INTO attribute_definitions (
    model_id,
    attribute_name,
    data_type,
    is_required,
    is_mutable
)
SELECT
    model_id,
    'security_zone',
    'TEXT',
    TRUE,
    TRUE
FROM device_models
WHERE model_name = 'FortiGate Firewall';

-- ------------------------------------------------------------
-- 18. SAMPLE DEVICE INSTANCES
-- ------------------------------------------------------------

INSERT INTO device_instances (
    organization_id,
    model_id,
    instance_code,
    instance_name,
    temperature,
    status,
    configuration,
    tags
)
SELECT
    organization.organization_id,
    model.model_id,
    'DEV-001',
    'Core Router',
    42.50,
    'ACTIVE',
    '{"ip": "192.168.1.1", "ports": 24}'::JSONB,
    ARRAY['network', 'critical']
FROM organizations organization
CROSS JOIN device_models model
WHERE organization.organization_name =
      'Enterprise Network Division'
  AND model.model_name = 'Catalyst Core Router';

INSERT INTO device_instances (
    organization_id,
    model_id,
    instance_code,
    instance_name,
    temperature,
    status,
    configuration,
    tags
)
SELECT
    organization.organization_id,
    model.model_id,
    'DEV-002',
    'Backup Router',
    38.00,
    'MAINTENANCE',
    '{"ip": "192.168.1.2", "ports": 48}'::JSONB,
    ARRAY['network', 'backup']
FROM organizations organization
CROSS JOIN device_models model
WHERE organization.organization_name =
      'Enterprise Network Division'
  AND model.model_name = 'Catalyst Core Router';

INSERT INTO device_instances (
    organization_id,
    model_id,
    instance_code,
    instance_name,
    temperature,
    status,
    configuration,
    tags
)
SELECT
    organization.organization_id,
    model.model_id,
    'DEV-003',
    'Enterprise Firewall',
    82.00,
    'ACTIVE',
    '{"ip": "192.168.1.3", "ports": 8}'::JSONB,
    ARRAY['security', 'critical']
FROM organizations organization
CROSS JOIN device_models model
WHERE organization.organization_name =
      'Security Operations Division'
  AND model.model_name = 'FortiGate Firewall';

-- ------------------------------------------------------------
-- 19. POPULATE INSTANCE-SPECIFIC ATTRIBUTES
-- ------------------------------------------------------------

SELECT update_instance_attribute(
    instance.instance_id,
    'location',
    to_jsonb('Lucknow Data Centre'::TEXT),
    'network_admin'
)
FROM device_instances instance
WHERE instance.instance_code = 'DEV-001';

SELECT update_instance_attribute(
    instance.instance_id,
    'serial_number',
    to_jsonb('CS-ROUTER-1001'::TEXT),
    'network_admin'
)
FROM device_instances instance
WHERE instance.instance_code = 'DEV-001';

SELECT update_instance_attribute(
    instance.instance_id,
    'firmware_version',
    to_jsonb('17.09.04'::TEXT),
    'network_admin'
)
FROM device_instances instance
WHERE instance.instance_code = 'DEV-001';

SELECT update_instance_attribute(
    instance.instance_id,
    'monitoring_enabled',
    'true'::JSONB,
    'network_admin'
)
FROM device_instances instance
WHERE instance.instance_code = 'DEV-001';

SELECT update_instance_attribute(
    instance.instance_id,
    'location',
    to_jsonb('Backup Data Centre'::TEXT),
    'network_admin'
)
FROM device_instances instance
WHERE instance.instance_code = 'DEV-002';

SELECT update_instance_attribute(
    instance.instance_id,
    'serial_number',
    to_jsonb('CS-ROUTER-1002'::TEXT),
    'network_admin'
)
FROM device_instances instance
WHERE instance.instance_code = 'DEV-002';

SELECT update_instance_attribute(
    instance.instance_id,
    'firmware_version',
    to_jsonb('17.09.03'::TEXT),
    'network_admin'
)
FROM device_instances instance
WHERE instance.instance_code = 'DEV-002';

SELECT update_instance_attribute(
    instance.instance_id,
    'security_zone',
    to_jsonb('DMZ'::TEXT),
    'security_admin'
)
FROM device_instances instance
WHERE instance.instance_code = 'DEV-003';

-- ------------------------------------------------------------
-- 20. INSTANCE ATTRIBUTE RETRIEVAL
-- ------------------------------------------------------------

SELECT *
FROM v_instance_attributes
ORDER BY instance_id;

-- ------------------------------------------------------------
-- 21. DIRECT ATTRIBUTE RETRIEVAL
-- ------------------------------------------------------------

SELECT
    instance.instance_code,
    definition.attribute_name,
    value.attribute_value,
    value.updated_at
FROM instance_attribute_values value
JOIN device_instances instance
    ON instance.instance_id = value.instance_id
JOIN attribute_definitions definition
    ON definition.attribute_id = value.attribute_id
ORDER BY instance.instance_code, definition.attribute_name;

-- ------------------------------------------------------------
-- 22. SHARED MODEL ATTRIBUTES VS INSTANCE ATTRIBUTES
-- ------------------------------------------------------------

SELECT
    instance.instance_code,
    model.shared_category,
    model.manufacturer,
    instance.instance_name,
    instance.temperature,
    instance.configuration
FROM device_instances instance
JOIN device_models model
    ON model.model_id = instance.model_id
ORDER BY instance.instance_code;

-- ------------------------------------------------------------
-- 23. INSTANCE ATTRIBUTE INDEPENDENCE
-- ------------------------------------------------------------

SELECT
    instance.instance_code,
    value.attribute_value AS location
FROM device_instances instance
JOIN instance_attribute_values value
    ON value.instance_id = instance.instance_id
JOIN attribute_definitions definition
    ON definition.attribute_id = value.attribute_id
WHERE definition.attribute_name = 'location'
ORDER BY instance.instance_code;

-- ------------------------------------------------------------
-- 24. REQUIRED ATTRIBUTE VALIDATION
-- ------------------------------------------------------------

SELECT
    instance.instance_code,
    missing.attribute_name
FROM device_instances instance
CROSS JOIN LATERAL validate_required_attributes(
    instance.instance_id
) AS missing
ORDER BY instance.instance_code;

-- ------------------------------------------------------------
-- 25. TEMPERATURE MONITORING
-- ------------------------------------------------------------

SELECT
    instance_code,
    instance_name,
    temperature,
    status
FROM device_instances
WHERE temperature >= 70
ORDER BY temperature DESC;

-- ------------------------------------------------------------
-- 26. STATUS AGGREGATION
-- ------------------------------------------------------------

SELECT
    status,
    COUNT(*) AS instance_count,
    ROUND(AVG(temperature), 2) AS average_temperature,
    MAX(temperature) AS maximum_temperature
FROM device_instances
GROUP BY status
ORDER BY status;

-- ------------------------------------------------------------
-- 27. CUSTOM ATTRIBUTE REPORT
-- ------------------------------------------------------------

SELECT
    instance.instance_code,
    definition.attribute_name,
    value.attribute_value
FROM device_instances instance
JOIN instance_attribute_values value
    ON value.instance_id = instance.instance_id
JOIN attribute_definitions definition
    ON definition.attribute_id = value.attribute_id
WHERE definition.attribute_name IN (
    'firmware_version',
    'location',
    'security_zone'
)
ORDER BY instance.instance_code;

-- ------------------------------------------------------------
-- 28. JSONB ATTRIBUTE SEARCH
-- ------------------------------------------------------------

SELECT
    instance_code,
    configuration ->> 'ip' AS ip_address,
    (configuration ->> 'ports')::INTEGER AS port_count
FROM device_instances
WHERE configuration @> '{"ports": 24}'::JSONB;

-- ------------------------------------------------------------
-- 29. UPDATE INSTANCE STATE
-- ------------------------------------------------------------

UPDATE device_instances
SET
    temperature = 36.50,
    configuration = jsonb_set(
        configuration,
        '{ports}',
        '48'::JSONB
    )
WHERE instance_code = 'DEV-001';

-- ------------------------------------------------------------
-- 30. VERIFY AUTOMATIC REVISION
-- ------------------------------------------------------------

SELECT
    instance_code,
    temperature,
    configuration,
    revision,
    updated_at
FROM device_instances
WHERE instance_code = 'DEV-001';

-- ------------------------------------------------------------
-- 31. ATTRIBUTE UPDATE AUDIT
-- ------------------------------------------------------------

SELECT
    instance.instance_code,
    definition.attribute_name,
    audit.old_value,
    audit.new_value,
    audit.changed_by,
    audit.changed_at
FROM attribute_audit audit
JOIN device_instances instance
    ON instance.instance_id = audit.instance_id
JOIN attribute_definitions definition
    ON definition.attribute_id = audit.attribute_id
ORDER BY audit.changed_at DESC;

-- ------------------------------------------------------------
-- 32. VALID ATTRIBUTE UPDATE
-- ------------------------------------------------------------

BEGIN;

SELECT update_instance_attribute(
    instance_id,
    'firmware_version',
    to_jsonb('17.09.05'::TEXT),
    'network_admin'
)
FROM device_instances
WHERE instance_code = 'DEV-001';

COMMIT;

-- ------------------------------------------------------------
-- 33. INVALID ATTRIBUTE TYPE
--
-- Run separately to observe the expected trigger exception.
-- ------------------------------------------------------------

-- SELECT update_instance_attribute(
--     (SELECT instance_id FROM device_instances
--      WHERE instance_code = 'DEV-001'),
--     'firmware_version',
--     '12345'::JSONB,
--     'network_admin'
-- );

-- ------------------------------------------------------------
-- 34. IMMUTABLE ATTRIBUTE PROTECTION
--
-- Run separately to observe the expected trigger exception.
-- ------------------------------------------------------------

-- SELECT update_instance_attribute(
--     (SELECT instance_id FROM device_instances
--      WHERE instance_code = 'DEV-001'),
--     'serial_number',
--     '"CHANGED-SERIAL"'::JSONB,
--     'network_admin'
-- );

-- ------------------------------------------------------------
-- 35. INSTANCE ATTRIBUTE AUDIT REPORT
-- ------------------------------------------------------------

SELECT
    instance.instance_code,
    COUNT(audit.audit_id) AS attribute_changes,
    MAX(audit.changed_at) AS last_attribute_change
FROM device_instances instance
LEFT JOIN attribute_audit audit
    ON audit.instance_id = instance.instance_id
GROUP BY instance.instance_id, instance.instance_code
ORDER BY attribute_changes DESC;

-- ------------------------------------------------------------
-- 36. DATA INTEGRITY CHECK
-- ------------------------------------------------------------

SELECT
    instance.instance_code,
    instance.temperature,
    instance.revision,
    CASE
        WHEN instance.temperature >= 70 THEN 'OVERHEATING'
        WHEN instance.status = 'MAINTENANCE' THEN 'UNDER_MAINTENANCE'
        ELSE 'NORMAL'
    END AS operational_condition
FROM device_instances instance
ORDER BY instance.instance_code;

COMMIT;
