DROP SCHEMA IF EXISTS recursion_lab CASCADE;
CREATE SCHEMA recursion_lab;
SET search_path TO recursion_lab;

-- PostgreSQL recursive queries are useful when the stored data is hierarchical.
-- The schema below represents a dependency-management system where modules
-- can depend on other modules and recursive queries can discover transitive
-- dependencies.

CREATE TABLE repositories (
    repository_id BIGSERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE modules (
    module_id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(repository_id)
        ON DELETE CASCADE,
    module_name TEXT NOT NULL,
    version TEXT NOT NULL,
    UNIQUE (repository_id, module_name, version)
);

CREATE TABLE module_dependencies (
    module_id BIGINT NOT NULL
        REFERENCES modules(module_id)
        ON DELETE CASCADE,
    dependency_id BIGINT NOT NULL
        REFERENCES modules(module_id)
        ON DELETE RESTRICT,
    PRIMARY KEY (module_id, dependency_id),
    CHECK (module_id <> dependency_id)
);

CREATE INDEX idx_module_dependencies_dependency
    ON module_dependencies(dependency_id);

INSERT INTO repositories (repository_name)
VALUES
    ('payment-platform'),
    ('analytics-platform');

INSERT INTO modules (repository_id, module_name, version)
SELECT r.repository_id, data.module_name, data.version
FROM repositories r
JOIN (
    VALUES
        ('payment-platform', 'application', '3.2'),
        ('payment-platform', 'api', '3.2'),
        ('payment-platform', 'validation', '2.4'),
        ('payment-platform', 'database', '5.1'),
        ('payment-platform', 'logging', '4.0'),
        ('payment-platform', 'metrics', '2.1'),
        ('analytics-platform', 'pipeline', '1.8'),
        ('analytics-platform', 'storage', '1.3'),
        ('analytics-platform', 'logging', '4.0')
) AS data(repository_name, module_name, version)
ON r.repository_name = data.repository_name;

INSERT INTO module_dependencies (module_id, dependency_id)
SELECT parent.module_id, child.module_id
FROM modules parent
JOIN modules child
  ON child.repository_id = parent.repository_id
WHERE
    (parent.module_name = 'application' AND child.module_name IN ('api', 'database'))
 OR (parent.module_name = 'api' AND child.module_name IN ('validation', 'logging'))
 OR (parent.module_name = 'database' AND child.module_name IN ('logging', 'metrics'))
 OR (parent.module_name = 'validation' AND child.module_name = 'logging')
 OR (parent.module_name = 'pipeline' AND child.module_name IN ('storage', 'logging'))
 AND parent.repository_id = child.repository_id;

-- Recursive CTE: start at one module, then repeatedly follow its
-- dependencies until no new dependency remains.
WITH RECURSIVE dependency_tree AS (
    SELECT
        m.module_id,
        m.module_name,
        m.repository_id,
        0 AS depth,
        ARRAY[m.module_id] AS path
    FROM modules m
    WHERE m.repository_id = (
        SELECT repository_id
        FROM repositories
        WHERE repository_name = 'payment-platform'
    )
    AND m.module_name = 'application'

    UNION ALL

    SELECT
        dependency.module_id,
        dependency.module_name,
        dependency.repository_id,
        tree.depth + 1,
        tree.path || dependency.module_id
    FROM dependency_tree tree
    JOIN module_dependencies md
      ON md.module_id = tree.module_id
    JOIN modules dependency
      ON dependency.module_id = md.dependency_id
    WHERE NOT dependency.module_id = ANY(tree.path)
)
SELECT
    module_name,
    depth
FROM dependency_tree
ORDER BY depth, module_name;

-- Recursive aggregation computes the maximum dependency depth.
WITH RECURSIVE dependency_tree AS (
    SELECT
        m.module_id,
        m.module_name,
        0 AS depth,
        ARRAY[m.module_id] AS path
    FROM modules m
    JOIN repositories r
      ON r.repository_id = m.repository_id
    WHERE r.repository_name = 'payment-platform'
      AND m.module_name = 'application'

    UNION ALL

    SELECT
        dependency.module_id,
        dependency.module_name,
        tree.depth + 1,
        tree.path || dependency.module_id
    FROM dependency_tree tree
    JOIN module_dependencies md
      ON md.module_id = tree.module_id
    JOIN modules dependency
      ON dependency.module_id = md.dependency_id
    WHERE NOT dependency.module_id = ANY(tree.path)
)
SELECT MAX(depth) AS maximum_dependency_depth
FROM dependency_tree;

-- PostgreSQL recursive queries can also build a readable dependency path.
WITH RECURSIVE dependency_paths AS (
    SELECT
        m.module_id,
        m.module_name,
        ARRAY[m.module_name] AS dependency_path,
        ARRAY[m.module_id] AS id_path
    FROM modules m
    JOIN repositories r
      ON r.repository_id = m.repository_id
    WHERE r.repository_name = 'payment-platform'
      AND m.module_name = 'application'

    UNION ALL

    SELECT
        dependency.module_id,
        dependency.module_name,
        paths.dependency_path || dependency.module_name,
        paths.id_path || dependency.module_id
    FROM dependency_paths paths
    JOIN module_dependencies md
      ON md.module_id = paths.module_id
    JOIN modules dependency
      ON dependency.module_id = md.dependency_id
    WHERE NOT dependency.module_id = ANY(paths.id_path)
)
SELECT
    array_to_string(dependency_path, ' -> ') AS dependency_path
FROM dependency_paths
ORDER BY cardinality(dependency_path) DESC;

-- The following transaction demonstrates database-level integrity.
-- A self-dependency is rejected by the CHECK constraint before the
-- transaction can successfully commit.

BEGIN;

INSERT INTO module_dependencies (module_id, dependency_id)
SELECT module_id, module_id
FROM modules
WHERE module_name = 'logging'
  AND repository_id = (
      SELECT repository_id
      FROM repositories
      WHERE repository_name = 'payment-platform'
  );

ROLLBACK;

-- A recursive query can inspect whether the graph contains a cycle.
-- The sample graph is acyclic, so the query returns no rows.
WITH RECURSIVE graph_walk AS (
    SELECT
        md.module_id AS start_module,
        md.dependency_id AS current_module,
        ARRAY[md.module_id, md.dependency_id] AS path,
        false AS cycle
    FROM module_dependencies md

    UNION ALL

    SELECT
        walk.start_module,
        md.dependency_id,
        walk.path || md.dependency_id,
        md.dependency_id = ANY(walk.path)
    FROM graph_walk walk
    JOIN module_dependencies md
      ON md.module_id = walk.current_module
    WHERE NOT walk.cycle
)
SELECT
    start_module,
    current_module,
    path
FROM graph_walk
WHERE cycle;

-- Recursive SQL is powerful for trees and graphs, but production systems
-- must prevent pathological depth and cycles. The path array above provides
-- explicit cycle detection rather than relying on an assumed acyclic graph.
