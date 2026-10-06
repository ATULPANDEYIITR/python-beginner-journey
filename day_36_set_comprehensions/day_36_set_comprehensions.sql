-- PostgreSQL-compatible demonstration of set-comprehension semantics.
--
-- SQL has no Python-style set-comprehension syntax. The relational
-- equivalents are DISTINCT projections, filtered SELECT statements,
-- joins, EXISTS predicates, array/JSON expansion, and aggregation.
-- The examples below use a realistic skills-and-permissions domain so
-- uniqueness, filtering, transformation, nested expansion, validation,
-- and set relationships are visible at the database layer.

DROP SCHEMA IF EXISTS set_comprehension_demo CASCADE;

CREATE SCHEMA set_comprehension_demo;

SET search_path TO set_comprehension_demo;

CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE skills (
    skill_id BIGSERIAL PRIMARY KEY,
    skill_name TEXT NOT NULL UNIQUE
);

CREATE TABLE user_skills (
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    skill_id BIGINT NOT NULL REFERENCES skills(skill_id) ON DELETE CASCADE,
    proficiency INTEGER NOT NULL CHECK (proficiency BETWEEN 1 AND 5),
    PRIMARY KEY (user_id, skill_id)
);

CREATE TABLE permissions (
    permission_id BIGSERIAL PRIMARY KEY,
    permission_name TEXT NOT NULL UNIQUE
);

CREATE TABLE role_permissions (
    role_name TEXT NOT NULL,
    permission_id BIGINT NOT NULL
        REFERENCES permissions(permission_id) ON DELETE CASCADE,
    PRIMARY KEY (role_name, permission_id)
);

INSERT INTO users (username, active)
VALUES
    ('anita', TRUE),
    ('rahul', TRUE),
    ('meera', FALSE),
    ('vikas', TRUE);

INSERT INTO skills (skill_name)
VALUES
    ('python'),
    ('sql'),
    ('git'),
    ('java'),
    ('javascript'),
    ('docker');

INSERT INTO user_skills (user_id, skill_id, proficiency)
SELECT u.user_id, s.skill_id, v.proficiency
FROM (
    VALUES
        ('anita', 'python', 5),
        ('anita', 'sql', 4),
        ('anita', 'git', 4),
        ('rahul', 'java', 5),
        ('rahul', 'sql', 5),
        ('rahul', 'git', 4),
        ('meera', 'python', 3),
        ('meera', 'javascript', 4),
        ('vikas', 'sql', 4),
        ('vikas', 'docker', 5)
) AS v(username, skill_name, proficiency)
JOIN users u ON u.username = v.username
JOIN skills s ON s.skill_name = v.skill_name;

INSERT INTO permissions (permission_name)
VALUES
    ('read'),
    ('write'),
    ('approve'),
    ('export'),
    ('comment');

INSERT INTO role_permissions (role_name, permission_id)
SELECT v.role_name, p.permission_id
FROM (
    VALUES
        ('finance', 'read'),
        ('finance', 'write'),
        ('finance', 'approve'),
        ('analytics', 'read'),
        ('analytics', 'export'),
        ('support', 'read'),
        ('support', 'comment'),
        ('guest', 'read')
) AS v(role_name, permission_name)
JOIN permissions p
    ON p.permission_name = v.permission_name;

CREATE INDEX idx_user_skills_skill_id
    ON user_skills(skill_id);

CREATE INDEX idx_users_active
    ON users(active)
    WHERE active = TRUE;

-- A direct relational equivalent of a set comprehension that maps
-- every active user to a unique skill.
SELECT DISTINCT s.skill_name
FROM users u
JOIN user_skills us ON us.user_id = u.user_id
JOIN skills s ON s.skill_id = us.skill_id
WHERE u.active
ORDER BY s.skill_name;

-- Filter first, then project unique values. This corresponds to a
-- comprehension such as:
-- {skill for skill in skills if skill satisfies a predicate}.
SELECT DISTINCT s.skill_name
FROM user_skills us
JOIN skills s ON s.skill_id = us.skill_id
WHERE us.proficiency >= 4
ORDER BY s.skill_name;

-- Nested relational expansion: active users combined with each of
-- their skills. DISTINCT removes duplicate output rows if the source
-- model were ever to produce them.
SELECT DISTINCT
    u.username,
    s.skill_name
FROM users u
JOIN user_skills us ON us.user_id = u.user_id
JOIN skills s ON s.skill_id = us.skill_id
WHERE u.active
ORDER BY u.username, s.skill_name;

-- Set difference: skills used by active users but not by inactive users.
WITH active_skills AS (
    SELECT DISTINCT s.skill_name
    FROM users u
    JOIN user_skills us ON us.user_id = u.user_id
    JOIN skills s ON s.skill_id = us.skill_id
    WHERE u.active
),
inactive_skills AS (
    SELECT DISTINCT s.skill_name
    FROM users u
    JOIN user_skills us ON us.user_id = u.user_id
    JOIN skills s ON s.skill_id = us.skill_id
    WHERE NOT u.active
)
SELECT skill_name
FROM active_skills
EXCEPT
SELECT skill_name
FROM inactive_skills
ORDER BY skill_name;

-- Set intersection: skills used by both active and inactive users.
WITH active_skills AS (
    SELECT DISTINCT s.skill_name
    FROM users u
    JOIN user_skills us ON us.user_id = u.user_id
    JOIN skills s ON s.skill_id = us.skill_id
    WHERE u.active
),
inactive_skills AS (
    SELECT DISTINCT s.skill_name
    FROM users u
    JOIN user_skills us ON us.user_id = u.user_id
    JOIN skills s ON s.skill_id = us.skill_id
    WHERE NOT u.active
)
SELECT skill_name
FROM active_skills
INTERSECT
SELECT skill_name
FROM inactive_skills
ORDER BY skill_name;

-- A transformed set: normalize skill names before deduplication.
SELECT DISTINCT lower(trim(skill_name)) AS normalized_skill
FROM skills
ORDER BY normalized_skill;

-- Count how many distinct users possess each skill. The HAVING clause
-- acts as the filter after grouping.
SELECT
    s.skill_name,
    COUNT(DISTINCT us.user_id) AS user_count
FROM skills s
JOIN user_skills us ON us.skill_id = s.skill_id
GROUP BY s.skill_name
HAVING COUNT(DISTINCT us.user_id) >= 2
ORDER BY s.skill_name;

-- Skills that occur for exactly one user illustrate a more advanced
-- filtered-set query.
SELECT s.skill_name
FROM skills s
JOIN user_skills us ON us.skill_id = s.skill_id
GROUP BY s.skill_name
HAVING COUNT(DISTINCT us.user_id) = 1
ORDER BY s.skill_name;

-- Build a PostgreSQL array from a distinct set. ARRAY_AGG preserves the
-- relational result while providing a collection representation.
SELECT ARRAY_AGG(skill_name ORDER BY skill_name) AS unique_skills
FROM (
    SELECT DISTINCT s.skill_name
    FROM user_skills us
    JOIN skills s ON s.skill_id = us.skill_id
) unique_values;

-- Permission-policy set construction.
-- Roles containing both read and approve are eligible for approval.
SELECT role_name
FROM role_permissions rp
JOIN permissions p ON p.permission_id = rp.permission_id
WHERE p.permission_name IN ('read', 'approve')
GROUP BY role_name
HAVING COUNT(DISTINCT p.permission_name) = 2
ORDER BY role_name;

-- Demonstrate a policy failure through database constraints.
DO $$
BEGIN
    BEGIN
        INSERT INTO user_skills (user_id, skill_id, proficiency)
        VALUES (1, 1, 9);
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE
                'Expected validation failure: proficiency must be 1 through 5.';
    END;
END
$$;

-- Demonstrate uniqueness enforcement.
DO $$
BEGIN
    BEGIN
        INSERT INTO users (username, active)
        VALUES ('anita', TRUE);
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE
                'Expected validation failure: username already exists.';
    END;
END
$$;

-- Transactional construction of a new skill assignment.
BEGIN;

INSERT INTO skills (skill_name)
VALUES ('postgresql')
ON CONFLICT (skill_name) DO NOTHING;

INSERT INTO user_skills (user_id, skill_id, proficiency)
SELECT
    u.user_id,
    s.skill_id,
    5
FROM users u
CROSS JOIN skills s
WHERE u.username = 'anita'
  AND s.skill_name = 'postgresql'
ON CONFLICT (user_id, skill_id) DO UPDATE
SET proficiency = EXCLUDED.proficiency;

COMMIT;

-- Final unique skill set for the selected user.
SELECT DISTINCT s.skill_name
FROM users u
JOIN user_skills us ON us.user_id = u.user_id
JOIN skills s ON s.skill_id = us.skill_id
WHERE u.username = 'anita'
ORDER BY s.skill_name;
