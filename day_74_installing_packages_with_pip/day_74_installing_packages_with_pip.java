import java.time.Instant;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/*
 * Installing Packages with pip
 *
 * Java 17 enterprise package-management model.
 *
 * Features:
 * - Immutable package definitions
 * - Dependency graph resolution
 * - Version constraints
 * - Security policy enforcement
 * - Installation approval workflow
 * - State transitions
 * - Audit history
 * - Asynchronous execution model
 *
 * The application simulates pip operations.
 * Actual installation is performed by Python's pip executable.
 */

public class PipEnterpriseManager {

    enum InstallationState {
        REQUESTED,
        VALIDATED,
        APPROVED,
        RESOLVING,
        INSTALLING,
        INSTALLED,
        REJECTED,
        FAILED
    }

    enum RiskLevel {
        LOW,
        MEDIUM,
        HIGH,
        CRITICAL
    }

    enum OperationType {
        INSTALL,
        UPGRADE,
        REMOVE
    }

    static class PackageException extends RuntimeException {
        PackageException(String message) {
            super(message);
        }
    }

    record Dependency(
        String packageName,
        String minimumVersion
    ) {
        Dependency {
            Objects.requireNonNull(packageName);
            Objects.requireNonNull(minimumVersion);

            Version.parse(minimumVersion);
        }
    }

    record PackageDefinition(
        String name,
        String version,
        String indexUrl,
        RiskLevel risk,
        List<Dependency> dependencies,
        String sha256
    ) {
        PackageDefinition {
            Objects.requireNonNull(name);
            Objects.requireNonNull(version);
            Objects.requireNonNull(indexUrl);
            Objects.requireNonNull(risk);

            if (!Pattern.matches(
                    "[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?",
                    name
            )) {
                throw new PackageException(
                    "Invalid package name: " + name
                );
            }

            Version.parse(version);

            if (!indexUrl.startsWith("https://")) {
                throw new PackageException(
                    "Package index must use HTTPS."
                );
            }

            dependencies = List.copyOf(dependencies);
        }

        String requirement() {
            return name + "==" + version;
        }
    }

    record AuditEvent(
        Instant timestamp,
        String packageName,
        InstallationState state,
        String details
    ) {}

    record InstallationRequest(
        String requestId,
        String requestedBy,
        OperationType operation,
        List<PackageDefinition> packages,
        Instant requestedAt
    ) {
        InstallationRequest {
            Objects.requireNonNull(requestId);
            Objects.requireNonNull(requestedBy);
            Objects.requireNonNull(operation);

            packages = List.copyOf(packages);

            if (packages.isEmpty()) {
                throw new PackageException(
                    "At least one package is required."
                );
            }
        }
    }

    static class Version {

        static List<Integer> parse(String value) {
            if (
                value == null ||
                !value.matches("\\d+(\\.\\d+)*")
            ) {
                throw new PackageException(
                    "Unsupported numeric version: " + value
                );
            }

            List<Integer> parts = new ArrayList<>();

            for (String token : value.split("\\.")) {
                parts.add(Integer.parseInt(token));
            }

            return parts;
        }

        static boolean atLeast(
            String actual,
            String required
        ) {
            List<Integer> a = new ArrayList<>(parse(actual));
            List<Integer> b = new ArrayList<>(parse(required));

            int size = Math.max(a.size(), b.size());

            while (a.size() < size) a.add(0);
            while (b.size() < size) b.add(0);

            for (int i = 0; i < size; i++) {
                int comparison = Integer.compare(
                    a.get(i),
                    b.get(i)
                );

                if (comparison != 0) {
                    return comparison > 0;
                }
            }

            return true;
        }
    }

    interface ApprovalPolicy {
        void evaluate(
            InstallationRequest request,
            PackageDefinition definition
        );
    }

    static class RepositoryPolicy implements ApprovalPolicy {

        private final Set<String> approvedIndexes;
        private final Set<String> deniedPackages;
        private final Set<String> authorizedUsers;
        private final RiskLevel maximumRisk;
        private final boolean requireHash;
        private final boolean permitUpgrade;

        RepositoryPolicy(
            Set<String> approvedIndexes,
            Set<String> deniedPackages,
            Set<String> authorizedUsers,
            RiskLevel maximumRisk,
            boolean requireHash,
            boolean permitUpgrade
        ) {
            this.approvedIndexes = Set.copyOf(approvedIndexes);
            this.deniedPackages = Set.copyOf(deniedPackages);
            this.authorizedUsers = Set.copyOf(authorizedUsers);
            this.maximumRisk = maximumRisk;
            this.requireHash = requireHash;
            this.permitUpgrade = permitUpgrade;
        }

        @Override
        public void evaluate(
            InstallationRequest request,
            PackageDefinition definition
        ) {
            if (!authorizedUsers.contains(request.requestedBy())) {
                throw new PackageException(
                    "Requester is not authorized."
                );
            }

            if (deniedPackages.contains(definition.name())) {
                throw new PackageException(
                    "Package is explicitly denied: " +
                    definition.name()
                );
            }

            if (!approvedIndexes.contains(definition.indexUrl())) {
                throw new PackageException(
                    "Unapproved package index."
                );
            }

            if (
                definition.risk().ordinal() >
                maximumRisk.ordinal()
            ) {
                throw new PackageException(
                    "Package exceeds permitted risk level."
                );
            }

            if (
                requireHash &&
                (
                    definition.sha256() == null ||
                    !definition.sha256().matches("[a-fA-F0-9]{64}")
                )
            ) {
                throw new PackageException(
                    "Verified SHA-256 hash required."
                );
            }

            if (
                request.operation() == OperationType.UPGRADE &&
                !permitUpgrade
            ) {
                throw new PackageException(
                    "Upgrade operation is prohibited."
                );
            }
        }
    }

    static class PackageRepository {

        private final Map<String, PackageDefinition> catalog =
            new LinkedHashMap<>();

        void register(PackageDefinition definition) {
            PackageDefinition existing =
                catalog.putIfAbsent(
                    definition.name(),
                    definition
                );

            if (existing != null) {
                if (!existing.equals(definition)) {
                    throw new PackageException(
                        "Duplicate or conflicting definition: " +
                        definition.name()
                    );
                }
            }
        }

        PackageDefinition get(String name) {
            PackageDefinition definition = catalog.get(name);

            if (definition == null) {
                throw new PackageException(
                    "Package not found: " + name
                );
            }

            return definition;
        }

        boolean contains(String name) {
            return catalog.containsKey(name);
        }
    }

    static class DependencyResolver {

        private final PackageRepository repository;

        private final Map<String, Integer> color =
            new HashMap<>();

        private final List<PackageDefinition> resolved =
            new ArrayList<>();

        DependencyResolver(PackageRepository repository) {
            this.repository = repository;
        }

        List<PackageDefinition> resolve(String root) {
            color.clear();
            resolved.clear();

            visit(root);

            return Collections.unmodifiableList(
                new ArrayList<>(resolved)
            );
        }

        private void visit(String name) {
            int state = color.getOrDefault(name, 0);

            if (state == 1) {
                throw new PackageException(
                    "Circular dependency detected: " + name
                );
            }

            if (state == 2) {
                return;
            }

            color.put(name, 1);

            PackageDefinition definition =
                repository.get(name);

            for (Dependency dependency : definition.dependencies()) {
                PackageDefinition required =
                    repository.get(dependency.packageName());

                if (!Version.atLeast(
                        required.version(),
                        dependency.minimumVersion()
                )) {
                    throw new PackageException(
                        "Unsatisfied dependency: " +
                        dependency.packageName()
                    );
                }

                visit(dependency.packageName());
            }

            color.put(name, 2);
            resolved.add(definition);
        }
    }

    static class InstallationService {

        private final PackageRepository repository;
        private final ApprovalPolicy policy;

        private final List<AuditEvent> audit =
            Collections.synchronizedList(new ArrayList<>());

        private final Map<String, InstallationState> states =
            new HashMap<>();

        InstallationService(
            PackageRepository repository,
            ApprovalPolicy policy
        ) {
            this.repository = repository;
            this.policy = policy;
        }

        private void transition(
            String packageName,
            InstallationState next,
            String message
        ) {
            states.put(packageName, next);

            audit.add(
                new AuditEvent(
                    Instant.now(),
                    packageName,
                    next,
                    message
                )
            );
        }

        CompletableFuture<List<PackageDefinition>> process(
            InstallationRequest request
        ) {
            return CompletableFuture.supplyAsync(() -> {
                try {
                    List<PackageDefinition> plan =
                        new ArrayList<>();

                    for (PackageDefinition definition : request.packages()) {
                        transition(
                            definition.name(),
                            InstallationState.REQUESTED,
                            "Installation requested."
                        );

                        policy.evaluate(request, definition);

                        transition(
                            definition.name(),
                            InstallationState.APPROVED,
                            "Enterprise policy approved package."
                        );

                        plan.addAll(
                            new DependencyResolver(repository)
                                .resolve(definition.name())
                        );
                    }

                    // Deduplicate while retaining dependency order.
                    Map<String, PackageDefinition> unique =
                        plan.stream().collect(
                            Collectors.toMap(
                                PackageDefinition::name,
                                definition -> definition,
                                (first, second) -> {
                                    if (!first.equals(second)) {
                                        throw new PackageException(
                                            "Conflicting package versions."
                                        );
                                    }
                                    return first;
                                },
                                LinkedHashMap::new
                            )
                        );

                    for (PackageDefinition definition : unique.values()) {
                        transition(
                            definition.name(),
                            InstallationState.RESOLVING,
                            "Dependencies resolved."
                        );

                        transition(
                            definition.name(),
                            InstallationState.INSTALLING,
                            "Installation stage entered."
                        );

                        // This is a simulated completion state.
                        transition(
                            definition.name(),
                            InstallationState.INSTALLED,
                            "Installation workflow simulated."
                        );
                    }

                    return List.copyOf(unique.values());

                } catch (RuntimeException exception) {
                    request.packages().forEach(definition ->
                        transition(
                            definition.name(),
                            InstallationState.REJECTED,
                            exception.getMessage()
                        )
                    );

                    throw exception;
                }
            });
        }

        void printAudit() {
            System.out.println("\nENTERPRISE INSTALLATION AUDIT");

            synchronized (audit) {
                audit.stream()
                    .sorted(Comparator.comparing(AuditEvent::timestamp))
                    .forEach(event ->
                        System.out.printf(
                            "%s | %-20s | %-12s | %s%n",
                            event.timestamp(),
                            event.packageName(),
                            event.state(),
                            event.details()
                        )
                    );
            }
        }

        Map<String, InstallationState> states() {
            return Map.copyOf(states);
        }
    }

    static PackageDefinition packageDefinition(
        String name,
        String version,
        List<Dependency> dependencies
    ) {
        return new PackageDefinition(
            name,
            version,
            "https://pypi.org/simple",
            RiskLevel.LOW,
            dependencies,
            null
        );
    }

    public static void main(String[] args) {
        try {
            System.out.println(
                "=== ENTERPRISE PIP PACKAGE MANAGEMENT ==="
            );

            PackageRepository repository =
                new PackageRepository();

            repository.register(
                packageDefinition(
                    "urllib3",
                    "2.2.3",
                    List.of()
                )
            );

            repository.register(
                packageDefinition(
                    "certifi",
                    "2024.8.30",
                    List.of()
                )
            );

            repository.register(
                packageDefinition(
                    "idna",
                    "3.10",
                    List.of()
                )
            );

            repository.register(
                packageDefinition(
                    "charset-normalizer",
                    "3.4.0",
                    List.of()
                )
            );

            repository.register(
                packageDefinition(
                    "requests",
                    "2.32.3",
                    List.of(
                        new Dependency("urllib3", "1.21.1"),
                        new Dependency("certifi", "2017.4.17"),
                        new Dependency("idna", "2.5"),
                        new Dependency("charset-normalizer", "2.0.0")
                    )
                )
            );

            RepositoryPolicy policy =
                new RepositoryPolicy(
                    Set.of("https://pypi.org/simple"),
                    Set.of("malicious-package"),
                    Set.of("build-engineer", "release-manager"),
                    RiskLevel.HIGH,
                    false,
                    false
                );

            InstallationService service =
                new InstallationService(
                    repository,
                    policy
                );

            InstallationRequest request =
                new InstallationRequest(
                    "REQ-1001",
                    "build-engineer",
                    OperationType.INSTALL,
                    List.of(repository.get("requests")),
                    Instant.now()
                );

            List<PackageDefinition> installed =
                service.process(request).join();

            System.out.println("\nResolved packages:");

            installed.forEach(definition ->
                System.out.println(
                    definition.requirement()
                )
            );

            System.out.println("\nInstallation states:");

            service.states().forEach(
                (name, state) ->
                    System.out.println(name + ": " + state)
            );

            service.printAudit();

            System.out.println(
                "\nDependency workflow completed successfully."
            );

            System.out.println(
                "Execution is simulated; no packages were installed."
            );

        } catch (CompletionException exception) {
            System.err.println(
                "Installation workflow failed: " +
                exception.getCause().getMessage()
            );

            System.exit(1);

        } catch (RuntimeException exception) {
            System.err.println(
                "Application error: " + exception.getMessage()
            );

            System.exit(1);
        }
    }
}
