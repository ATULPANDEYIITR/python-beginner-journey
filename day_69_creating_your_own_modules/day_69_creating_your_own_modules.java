import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

/*
 * Creating Your Own Modules
 *
 * Java 17 enterprise module architecture.
 *
 * Demonstrates:
 * - Interfaces and implementations
 * - Records and immutable metadata
 * - Encapsulation
 * - Dependency resolution
 * - Semantic version compatibility
 * - Capability-based permissions
 * - Lifecycle management
 * - Service-oriented architecture
 * - Asynchronous execution
 * - Enterprise validation and reporting
 *
 * Compile:
 * javac ModuleArchitecture.java
 *
 * Run:
 * java ModuleArchitecture
 *
 * This is a single-file application. A production JPMS deployment
 * would additionally use module-info.java and separate source modules.
 */

public class ModuleArchitecture {

    enum ModuleState {
        REGISTERED,
        INITIALIZED,
        ACTIVE,
        FAILED,
        DISABLED
    }

    enum Permission {
        READ_DATA,
        WRITE_DATA,
        CALCULATE,
        EXPORT_DATA
    }

    static class ModuleException extends RuntimeException {
        ModuleException(String message) {
            super(message);
        }

        ModuleException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    static class DependencyException extends ModuleException {
        DependencyException(String message) {
            super(message);
        }
    }

    static class AuthorizationException extends ModuleException {
        AuthorizationException(String message) {
            super(message);
        }
    }

    record Version(int major, int minor, int patch)
            implements Comparable<Version> {

        Version {
            if (major < 0 || minor < 0 || patch < 0) {
                throw new IllegalArgumentException(
                    "Version components cannot be negative."
                );
            }
        }

        @Override
        public int compareTo(Version other) {
            int comparison = Integer.compare(
                major, other.major
            );

            if (comparison != 0) return comparison;

            comparison = Integer.compare(
                minor, other.minor
            );

            if (comparison != 0) return comparison;

            return Integer.compare(patch, other.patch);
        }

        @Override
        public String toString() {
            return major + "." + minor + "." + patch;
        }
    }

    record Dependency(
        String moduleName,
        Version minimumVersion
    ) {
        Dependency {
            Objects.requireNonNull(moduleName);
            Objects.requireNonNull(minimumVersion);
        }
    }

    record ModuleMetadata(
        String name,
        Version version,
        String description,
        String owner,
        Set<Permission> permissions,
        List<Dependency> dependencies
    ) {
        ModuleMetadata {
            Objects.requireNonNull(name);
            Objects.requireNonNull(version);
            Objects.requireNonNull(description);
            Objects.requireNonNull(owner);

            if (!name.matches("[a-z][a-z0-9_]*")) {
                throw new IllegalArgumentException(
                    "Invalid module name."
                );
            }

            if (description.isBlank() || owner.isBlank()) {
                throw new IllegalArgumentException(
                    "Description and owner are required."
                );
            }

            permissions = Set.copyOf(permissions);
            dependencies = List.copyOf(dependencies);
        }
    }

    record ModuleConfiguration(
        int precision,
        String reportTitle
    ) {
        ModuleConfiguration {
            if (precision < 0 || precision > 12) {
                throw new IllegalArgumentException(
                    "Precision must be between 0 and 12."
                );
            }

            Objects.requireNonNull(reportTitle);
        }
    }

    record AnalyticsRequest(
        String operation,
        List<Double> values
    ) {
        AnalyticsRequest {
            Objects.requireNonNull(operation);
            values = List.copyOf(values);

            if (values.isEmpty()) {
                throw new IllegalArgumentException(
                    "Input values cannot be empty."
                );
            }

            if (values.stream().anyMatch(
                value -> value == null ||
                         !Double.isFinite(value)
            )) {
                throw new IllegalArgumentException(
                    "Input contains invalid numbers."
                );
            }
        }
    }

    record ModuleResult(
        String executionId,
        String moduleName,
        String operation,
        double value,
        int inputCount
    ) {}

    record ExecutionAudit(
        String executionId,
        String moduleName,
        boolean successful,
        String detail
    ) {}

    interface EnterpriseModule {
        void initialize(ModuleConfiguration configuration);

        Object execute(Object request);

        void shutdown();
    }

    static final class AnalyticsModule
            implements EnterpriseModule {

        private int precision = 2;
        private boolean initialized;

        @Override
        public void initialize(
            ModuleConfiguration configuration
        ) {
            this.precision = configuration.precision();
            this.initialized = true;
        }

        @Override
        public Object execute(Object request) {
            if (!initialized) {
                throw new ModuleException(
                    "Analytics module is not initialized."
                );
            }

            if (!(request instanceof AnalyticsRequest analytics)) {
                throw new IllegalArgumentException(
                    "Invalid analytics request."
                );
            }

            List<Double> values = analytics.values();

            double result;

            switch (analytics.operation()) {
                case "sum":
                    result = values.stream()
                        .mapToDouble(Double::doubleValue)
                        .sum();
                    break;

                case "average":
                    result = values.stream()
                        .mapToDouble(Double::doubleValue)
                        .average()
                        .orElseThrow();
                    break;

                case "maximum":
                    result = values.stream()
                        .mapToDouble(Double::doubleValue)
                        .max()
                        .orElseThrow();
                    break;

                case "minimum":
                    result = values.stream()
                        .mapToDouble(Double::doubleValue)
                        .min()
                        .orElseThrow();
                    break;

                default:
                    throw new IllegalArgumentException(
                        "Unsupported analytics operation."
                    );
            }

            result = Math.round(
                result * Math.pow(10, precision)
            ) / Math.pow(10, precision);

            return new ModuleResult(
                UUID.randomUUID().toString(),
                "analytics",
                analytics.operation(),
                result,
                values.size()
            );
        }

        @Override
        public void shutdown() {
            initialized = false;
        }
    }

    static final class ReportingModule
            implements EnterpriseModule {

        private String title;
        private boolean initialized;

        @Override
        public void initialize(
            ModuleConfiguration configuration
        ) {
            title = configuration.reportTitle();
            initialized = true;
        }

        @Override
        public Object execute(Object request) {
            if (!initialized) {
                throw new ModuleException(
                    "Reporting module is not initialized."
                );
            }

            if (!(request instanceof List<?> records)) {
                throw new IllegalArgumentException(
                    "Reporting expects a list of records."
                );
            }

            return Map.of(
                "title", title,
                "recordCount", records.size(),
                "records", List.copyOf(records)
            );
        }

        @Override
        public void shutdown() {
            initialized = false;
            title = null;
        }
    }

    static final class ModuleRecord {
        private final ModuleMetadata metadata;
        private final EnterpriseModule implementation;

        private ModuleState state = ModuleState.REGISTERED;
        private final AtomicLong executions = new AtomicLong();
        private String lastError;

        ModuleRecord(
            ModuleMetadata metadata,
            EnterpriseModule implementation
        ) {
            this.metadata = metadata;
            this.implementation = implementation;
        }
    }

    static final class ModuleRegistry {

        private final Map<String, ModuleRecord> modules =
            new HashMap<>();

        private final Set<Permission> allowedPermissions =
            Collections.unmodifiableSet(
                Set.of(Permission.values())
            );

        private final List<ExecutionAudit> auditLog =
            Collections.synchronizedList(
                new ArrayList<>()
            );

        void register(
            ModuleMetadata metadata,
            EnterpriseModule implementation
        ) {
            Objects.requireNonNull(metadata);
            Objects.requireNonNull(implementation);

            if (modules.containsKey(metadata.name())) {
                throw new ModuleException(
                    "Duplicate module registration: " +
                    metadata.name()
                );
            }

            if (!allowedPermissions.containsAll(
                metadata.permissions()
            )) {
                throw new AuthorizationException(
                    "Unauthorized module permissions."
                );
            }

            modules.put(
                metadata.name(),
                new ModuleRecord(metadata, implementation)
            );

            System.out.println(
                "Registered module: " + metadata.name()
            );
        }

        private ModuleRecord get(String name) {
            ModuleRecord record = modules.get(name);

            if (record == null) {
                throw new ModuleException(
                    "Unknown module: " + name
                );
            }

            return record;
        }

        private void visit(
            String name,
            Set<String> visited,
            Set<String> visiting,
            List<String> order
        ) {
            if (visiting.contains(name)) {
                throw new DependencyException(
                    "Circular dependency: " + name
                );
            }

            if (visited.contains(name)) {
                return;
            }

            ModuleRecord record = get(name);

            visiting.add(name);

            for (
                Dependency dependency :
                record.metadata.dependencies()
            ) {
                ModuleRecord required = get(
                    dependency.moduleName()
                );

                if (required.state == ModuleState.DISABLED) {
                    throw new DependencyException(
                        "Disabled dependency: " +
                        dependency.moduleName()
                    );
                }

                if (
                    required.metadata.version().compareTo(
                        dependency.minimumVersion()
                    ) < 0
                ) {
                    throw new DependencyException(
                        "Incompatible dependency version: " +
                        dependency.moduleName()
                    );
                }

                visit(
                    dependency.moduleName(),
                    visited,
                    visiting,
                    order
                );
            }

            visiting.remove(name);
            visited.add(name);
            order.add(name);
        }

        List<String> dependencyOrder(String name) {
            Set<String> visited = new HashSet<>();
            Set<String> visiting = new HashSet<>();
            List<String> order = new ArrayList<>();

            visit(name, visited, visiting, order);

            return order;
        }

        void activate(
            String name,
            ModuleConfiguration configuration
        ) {
            List<String> order = dependencyOrder(name);

            for (String current : order) {
                ModuleRecord record = get(current);

                if (record.state == ModuleState.ACTIVE) {
                    continue;
                }

                if (record.state == ModuleState.DISABLED) {
                    throw new ModuleException(
                        "Disabled modules cannot be activated."
                    );
                }

                try {
                    record.implementation.initialize(
                        configuration
                    );

                    record.state = ModuleState.ACTIVE;

                } catch (RuntimeException error) {
                    record.state = ModuleState.FAILED;
                    record.lastError = error.getMessage();

                    throw new ModuleException(
                        "Module activation failed: " + current,
                        error
                    );
                }
            }
        }

        CompletableFuture<Object> executeAsync(
            String name,
            Object request,
            Set<Permission> callerPermissions
        ) {
            ModuleRecord record = get(name);

            if (record.state != ModuleState.ACTIVE) {
                throw new ModuleException(
                    "Module is not active: " + name
                );
            }

            if (!callerPermissions.containsAll(
                record.metadata.permissions()
            )) {
                throw new AuthorizationException(
                    "Caller lacks required permissions."
                );
            }

            return CompletableFuture.supplyAsync(() -> {
                String executionId = UUID.randomUUID().toString();

                try {
                    Object result =
                        record.implementation.execute(request);

                    record.executions.incrementAndGet();

                    auditLog.add(
                        new ExecutionAudit(
                            executionId,
                            name,
                            true,
                            "Execution completed."
                        )
                    );

                    return result;

                } catch (RuntimeException error) {
                    record.lastError = error.getMessage();

                    auditLog.add(
                        new ExecutionAudit(
                            executionId,
                            name,
                            false,
                            error.getMessage()
                        )
                    );

                    throw new CompletionException(error);
                }
            });
        }

        void disable(String name) {
            ModuleRecord record = get(name);

            boolean activeDependents = modules.values()
                .stream()
                .filter(candidate ->
                    candidate.state == ModuleState.ACTIVE
                )
                .anyMatch(candidate ->
                    candidate.metadata.dependencies()
                        .stream()
                        .anyMatch(dependency ->
                            dependency.moduleName().equals(name)
                        )
                );

            if (activeDependents) {
                throw new DependencyException(
                    "Cannot disable module with active dependents."
                );
            }

            if (record.state == ModuleState.ACTIVE) {
                record.implementation.shutdown();
            }

            record.state = ModuleState.DISABLED;
        }

        void printInventory() {
            System.out.println("\nMODULE INVENTORY");

            modules.forEach((name, record) -> {
                System.out.printf(
                    "%-15s %-10s %-15s executions=%d%n",
                    name,
                    record.metadata.version(),
                    record.state,
                    record.executions.get()
                );

                if (record.lastError != null) {
                    System.out.println(
                        "Last error: " + record.lastError
                    );
                }
            });
        }

        List<ExecutionAudit> auditRecords() {
            synchronized (auditLog) {
                return List.copyOf(auditLog);
            }
        }
    }

    private static void runTests(ModuleRegistry registry) {
        Object response = registry.executeAsync(
            "analytics",
            new AnalyticsRequest(
                "average",
                List.of(10.0, 20.0, 30.0)
            ),
            Set.of(Permission.CALCULATE)
        ).join();

        ModuleResult result = (ModuleResult) response;

        if (result.value() != 20.0) {
            throw new AssertionError(
                "Average calculation failed."
            );
        }

        try {
            registry.executeAsync(
                "analytics",
                new AnalyticsRequest(
                    "average",
                    List.of(1.0, 2.0)
                ),
                Set.of()
            );

            throw new AssertionError(
                "Unauthorized execution was accepted."
            );

        } catch (AuthorizationException expected) {
            System.out.println(
                "Permission validation passed."
            );
        }

        System.out.println("All tests passed.");
    }

    public static void main(String[] args) {
        ModuleRegistry registry = new ModuleRegistry();

        ModuleMetadata analyticsMetadata =
            new ModuleMetadata(
                "analytics",
                new Version(2, 1, 0),
                "Numerical analytics service",
                "Engineering",
                Set.of(Permission.CALCULATE),
                List.of()
            );

        ModuleMetadata reportingMetadata =
            new ModuleMetadata(
                "reporting",
                new Version(1, 0, 0),
                "Enterprise reporting service",
                "Engineering",
                Set.of(
                    Permission.READ_DATA,
                    Permission.EXPORT_DATA
                ),
                List.of(
                    new Dependency(
                        "analytics",
                        new Version(2, 0, 0)
                    )
                )
            );

        registry.register(
            analyticsMetadata,
            new AnalyticsModule()
        );

        registry.register(
            reportingMetadata,
            new ReportingModule()
        );

        ModuleConfiguration configuration =
            new ModuleConfiguration(
                3,
                "Enterprise Analytics"
            );

        registry.activate(
            "reporting",
            configuration
        );

        ModuleResult result = (ModuleResult)
            registry.executeAsync(
                "analytics",
                new AnalyticsRequest(
                    "average",
                    List.of(100.0, 150.0, 200.0, 250.0)
                ),
                Set.of(Permission.CALCULATE)
            ).join();

        System.out.println("\nANALYTICS RESULT");
        System.out.println(result);

        Object report = registry.executeAsync(
            "reporting",
            List.of(result),
            Set.of(
                Permission.READ_DATA,
                Permission.EXPORT_DATA
            )
        ).join();

        System.out.println("\nREPORT");
        System.out.println(report);

        runTests(registry);

        registry.printInventory();

        System.out.println("\nAUDIT LOG");
        registry.auditRecords().forEach(
            System.out::println
        );

        registry.disable("reporting");
        registry.disable("analytics");
    }
}
