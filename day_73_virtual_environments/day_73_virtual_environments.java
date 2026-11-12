import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Enterprise Virtual Environment Governance System.
 *
 * Java 17
 *
 * Features:
 * - Environment registration
 * - Runtime and isolation policies
 * - Dependency management
 * - Environment lifecycle
 * - Approval and validation
 * - Environment inventory
 * - Audit history
 * - Failure handling
 */

public class VirtualEnvironmentManager {

    enum RuntimeType {
        PYTHON,
        NODE,
        JAVA
    }

    enum IsolationLevel {
        STRICT,
        STANDARD,
        SHARED
    }

    enum EnvironmentStatus {
        CREATED,
        CONFIGURING,
        READY,
        FAILED,
        RETIRED
    }

    enum DependencyScope {
        PRODUCTION,
        DEVELOPMENT,
        TESTING
    }

    record Dependency(
        String name,
        String version,
        DependencyScope scope
    ) {

        Dependency {

            if (
                name == null ||
                !name.matches("[A-Za-z0-9_.-]+")
            ) {
                throw new IllegalArgumentException(
                    "Invalid dependency name."
                );
            }

            if (
                version == null ||
                !version.matches("[A-Za-z0-9.+_-]+")
            ) {
                throw new IllegalArgumentException(
                    "Invalid dependency version."
                );
            }

            Objects.requireNonNull(scope);
        }

        String key() {
            return name.toLowerCase();
        }
    }

    record EnvironmentConfiguration(
        String name,
        String project,
        RuntimeType runtime,
        String runtimeVersion,
        IsolationLevel isolation,
        int diskSpaceMB,
        boolean lockfilePresent,
        boolean systemPackagesEnabled
    ) {

        EnvironmentConfiguration {

            if (
                name == null ||
                !name.matches("[A-Za-z0-9_-]{1,50}")
            ) {
                throw new IllegalArgumentException(
                    "Invalid environment name."
                );
            }

            if (project == null || project.isBlank()) {
                throw new IllegalArgumentException(
                    "Project is required."
                );
            }

            Objects.requireNonNull(runtime);
            Objects.requireNonNull(isolation);

            if (
                runtimeVersion == null ||
                runtimeVersion.isBlank()
            ) {
                throw new IllegalArgumentException(
                    "Runtime version is required."
                );
            }

            if (diskSpaceMB < 0) {
                throw new IllegalArgumentException(
                    "Disk allocation cannot be negative."
                );
            }
        }
    }

    record PolicyViolation(String code, String message) {}

    record PolicyResult(
        boolean permitted,
        List<PolicyViolation> violations
    ) {

        PolicyResult {
            violations = List.copyOf(violations);
        }
    }

    record AuditEvent(
        Instant timestamp,
        String action,
        String details
    ) {}

    static class EnvironmentException extends RuntimeException {

        EnvironmentException(String message) {
            super(message);
        }
    }

    static class EnvironmentPolicy {

        private final Set<RuntimeType> permittedRuntimes;
        private final int minimumDiskSpaceMB;
        private final int maximumDependencies;
        private final boolean requireLockfile;
        private final boolean prohibitSystemPackages;
        private final boolean requireStrictIsolation;

        EnvironmentPolicy(
            Set<RuntimeType> permittedRuntimes,
            int minimumDiskSpaceMB,
            int maximumDependencies,
            boolean requireLockfile,
            boolean prohibitSystemPackages,
            boolean requireStrictIsolation
        ) {

            if (
                permittedRuntimes == null ||
                permittedRuntimes.isEmpty()
            ) {
                throw new IllegalArgumentException(
                    "At least one runtime must be permitted."
                );
            }

            if (
                minimumDiskSpaceMB < 0 ||
                maximumDependencies < 0
            ) {
                throw new IllegalArgumentException(
                    "Invalid policy limits."
                );
            }

            this.permittedRuntimes = Set.copyOf(
                permittedRuntimes
            );

            this.minimumDiskSpaceMB = minimumDiskSpaceMB;
            this.maximumDependencies = maximumDependencies;
            this.requireLockfile = requireLockfile;
            this.prohibitSystemPackages = prohibitSystemPackages;
            this.requireStrictIsolation = requireStrictIsolation;
        }

        PolicyResult evaluate(
            EnvironmentConfiguration configuration,
            int dependencyCount
        ) {

            List<PolicyViolation> violations = new ArrayList<>();

            if (!permittedRuntimes.contains(configuration.runtime())) {
                violations.add(new PolicyViolation(
                    "RUNTIME_NOT_ALLOWED",
                    "Runtime is not approved."
                ));
            }

            if (
                configuration.diskSpaceMB() <
                minimumDiskSpaceMB
            ) {
                violations.add(new PolicyViolation(
                    "DISK_LIMIT",
                    "Disk allocation is insufficient."
                ));
            }

            if (dependencyCount > maximumDependencies) {
                violations.add(new PolicyViolation(
                    "DEPENDENCY_LIMIT",
                    "Dependency limit exceeded."
                ));
            }

            if (
                requireLockfile &&
                !configuration.lockfilePresent()
            ) {
                violations.add(new PolicyViolation(
                    "LOCKFILE_REQUIRED",
                    "A dependency lockfile is required."
                ));
            }

            if (
                prohibitSystemPackages &&
                configuration.systemPackagesEnabled()
            ) {
                violations.add(new PolicyViolation(
                    "GLOBAL_PACKAGES",
                    "System package access is prohibited."
                ));
            }

            if (
                requireStrictIsolation &&
                configuration.isolation() != IsolationLevel.STRICT
            ) {
                violations.add(new PolicyViolation(
                    "ISOLATION_REQUIRED",
                    "Strict isolation is required."
                ));
            }

            return new PolicyResult(
                violations.isEmpty(),
                violations
            );
        }
    }

    static class Environment {

        private final UUID id;
        private final EnvironmentConfiguration configuration;

        private final Map<String, Dependency> dependencies =
            new HashMap<>();

        private final List<AuditEvent> auditEvents =
            new ArrayList<>();

        private EnvironmentStatus status =
            EnvironmentStatus.CREATED;

        private final Instant createdAt;

        Environment(EnvironmentConfiguration configuration) {

            this.id = UUID.randomUUID();
            this.configuration = configuration;
            this.createdAt = Instant.now();

            record("CREATE", "Environment registered.");
        }

        private void record(String action, String details) {

            auditEvents.add(
                new AuditEvent(
                    Instant.now(),
                    action,
                    details
                )
            );
        }

        void transition(EnvironmentStatus next) {

            Map<EnvironmentStatus, Set<EnvironmentStatus>> allowed =
                Map.of(
                    EnvironmentStatus.CREATED,
                    Set.of(
                        EnvironmentStatus.CONFIGURING,
                        EnvironmentStatus.RETIRED
                    ),
                    EnvironmentStatus.CONFIGURING,
                    Set.of(
                        EnvironmentStatus.READY,
                        EnvironmentStatus.FAILED,
                        EnvironmentStatus.RETIRED
                    ),
                    EnvironmentStatus.READY,
                    Set.of(
                        EnvironmentStatus.CONFIGURING,
                        EnvironmentStatus.FAILED,
                        EnvironmentStatus.RETIRED
                    ),
                    EnvironmentStatus.FAILED,
                    Set.of(
                        EnvironmentStatus.CONFIGURING,
                        EnvironmentStatus.RETIRED
                    ),
                    EnvironmentStatus.RETIRED,
                    Set.of()
                );

            if (!allowed.get(status).contains(next)) {
                throw new EnvironmentException(
                    "Invalid state transition: " +
                    status + " -> " + next
                );
            }

            EnvironmentStatus previous = status;
            status = next;

            record(
                "STATE_CHANGE",
                previous + " -> " + next
            );
        }

        void addDependency(Dependency dependency) {

            if (status == EnvironmentStatus.RETIRED) {
                throw new EnvironmentException(
                    "Retired environments cannot be modified."
                );
            }

            String key = dependency.key();

            if (dependencies.containsKey(key)) {
                throw new EnvironmentException(
                    "Dependency already exists: " + key
                );
            }

            dependencies.put(key, dependency);

            record(
                "DEPENDENCY_ADDED",
                dependency.name() + " " + dependency.version()
            );
        }

        void removeDependency(String name) {

            if (status == EnvironmentStatus.RETIRED) {
                throw new EnvironmentException(
                    "Retired environments cannot be modified."
                );
            }

            String key = name.toLowerCase();

            if (dependencies.remove(key) == null) {
                throw new EnvironmentException(
                    "Dependency does not exist: " + name
                );
            }

            record("DEPENDENCY_REMOVED", name);
        }

        UUID id() {
            return id;
        }

        String name() {
            return configuration.name();
        }

        String project() {
            return configuration.project();
        }

        EnvironmentStatus status() {
            return status;
        }

        EnvironmentConfiguration configuration() {
            return configuration;
        }

        Map<String, Dependency> dependencies() {
            return Collections.unmodifiableMap(dependencies);
        }

        List<AuditEvent> auditEvents() {
            return List.copyOf(auditEvents);
        }

        Instant createdAt() {
            return createdAt;
        }
    }

    static class EnvironmentRegistry {

        private final Map<String, Environment> environments =
            new HashMap<>();

        private final Map<String, Set<String>> projectIndex =
            new HashMap<>();

        private final EnvironmentPolicy policy;

        EnvironmentRegistry(EnvironmentPolicy policy) {
            this.policy = Objects.requireNonNull(policy);
        }

        synchronized Environment register(
            EnvironmentConfiguration configuration
        ) {

            if (environments.containsKey(configuration.name())) {
                throw new EnvironmentException(
                    "Environment name already registered."
                );
            }

            PolicyResult result = policy.evaluate(
                configuration,
                0
            );

            if (!result.permitted()) {
                throw new EnvironmentException(
                    formatViolations(result.violations())
                );
            }

            Environment environment = new Environment(
                configuration
            );

            environments.put(
                environment.name(),
                environment
            );

            projectIndex.computeIfAbsent(
                environment.project(),
                key -> new HashSet<>()
            ).add(environment.name());

            return environment;
        }

        synchronized Environment get(String name) {

            Environment environment = environments.get(name);

            if (environment == null) {
                throw new EnvironmentException(
                    "Environment not found: " + name
                );
            }

            return environment;
        }

        synchronized PolicyResult evaluate(String name) {

            Environment environment = get(name);

            return policy.evaluate(
                environment.configuration(),
                environment.dependencies().size()
            );
        }

        synchronized void validateReadyForDeployment(String name) {

            Environment environment = get(name);

            PolicyResult result = evaluate(name);

            if (environment.status() != EnvironmentStatus.READY) {
                throw new EnvironmentException(
                    "Environment is not READY."
                );
            }

            if (!result.permitted()) {
                throw new EnvironmentException(
                    formatViolations(result.violations())
                );
            }
        }

        synchronized List<Environment> listByProject(String project) {

            return projectIndex
                .getOrDefault(project, Set.of())
                .stream()
                .map(environments::get)
                .filter(Objects::nonNull)
                .sorted(
                    (a, b) -> a.name().compareTo(b.name())
                )
                .collect(Collectors.toList());
        }

        synchronized void retire(String name) {
            get(name).transition(EnvironmentStatus.RETIRED);
        }

        private String formatViolations(
            List<PolicyViolation> violations
        ) {

            return violations.stream()
                .map(v -> v.code() + ": " + v.message())
                .collect(Collectors.joining("; "));
        }
    }

    static void printReport(
        EnvironmentRegistry registry,
        Environment environment
    ) {

        System.out.println("\nENVIRONMENT REPORT");
        System.out.println("------------------------------");

        System.out.println("ID: " + environment.id());
        System.out.println("Name: " + environment.name());
        System.out.println("Project: " + environment.project());
        System.out.println(
            "Runtime: " +
            environment.configuration().runtime()
        );
        System.out.println(
            "Runtime version: " +
            environment.configuration().runtimeVersion()
        );
        System.out.println("State: " + environment.status());
        System.out.println(
            "Isolation: " +
            environment.configuration().isolation()
        );

        System.out.println("\nDEPENDENCIES");

        environment.dependencies().values()
            .stream()
            .sorted(
                (a, b) -> a.name().compareTo(b.name())
            )
            .forEach(System.out::println);

        System.out.println("\nPOLICY EVALUATION");

        PolicyResult result = registry.evaluate(environment.name());

        System.out.println("Permitted: " + result.permitted());

        result.violations().forEach(System.out::println);

        System.out.println("\nAUDIT HISTORY");

        environment.auditEvents().forEach(
            event -> System.out.println(
                event.timestamp() + " | " +
                event.action() + " | " +
                event.details()
            )
        );
    }

    public static void main(String[] args) {

        try {

            EnvironmentPolicy policy = new EnvironmentPolicy(
                Set.of(
                    RuntimeType.PYTHON,
                    RuntimeType.NODE,
                    RuntimeType.JAVA
                ),
                100,
                20,
                true,
                true,
                true
            );

            EnvironmentRegistry registry =
                new EnvironmentRegistry(policy);

            EnvironmentConfiguration configuration =
                new EnvironmentConfiguration(
                    "analytics-dev",
                    "analytics-platform",
                    RuntimeType.PYTHON,
                    "3.13",
                    IsolationLevel.STRICT,
                    2048,
                    true,
                    false
                );

            Environment environment =
                registry.register(configuration);

            environment.addDependency(
                new Dependency(
                    "numpy",
                    "2.3.0",
                    DependencyScope.PRODUCTION
                )
            );

            environment.addDependency(
                new Dependency(
                    "pandas",
                    "2.3.0",
                    DependencyScope.PRODUCTION
                )
            );

            environment.addDependency(
                new Dependency(
                    "pytest",
                    "8.4.0",
                    DependencyScope.TESTING
                )
            );

            environment.transition(
                EnvironmentStatus.CONFIGURING
            );

            environment.transition(
                EnvironmentStatus.READY
            );

            registry.validateReadyForDeployment(
                environment.name()
            );

            printReport(registry, environment);

            System.out.println("\nPROJECT INVENTORY");

            registry.listByProject("analytics-platform")
                .forEach(
                    item -> System.out.println(
                        item.name() + " | " + item.status()
                    )
                );

            System.out.println("\nRETIRING ENVIRONMENT");

            registry.retire(environment.name());

            System.out.println(
                "Final state: " + environment.status()
            );

            System.out.println("\nTESTING INVALID TRANSITION");

            try {
                environment.transition(
                    EnvironmentStatus.READY
                );
            } catch (EnvironmentException exception) {
                System.out.println(
                    "Expected rejection: " + exception.getMessage()
                );
            }

        } catch (Exception exception) {

            System.err.println(
                "APPLICATION ERROR: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
