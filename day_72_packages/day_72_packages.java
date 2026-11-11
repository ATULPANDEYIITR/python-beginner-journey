import java.util.*;
import java.util.stream.Collectors;

/*
 * Enterprise Python Package Management and Governance.
 *
 * Java 17 implementation.
 * Models package repositories, dependency resolution,
 * security policies, installation transactions, and auditing.
 */

public class Main {

    enum PackageStatus {
        AVAILABLE,
        BLOCKED,
        DEPRECATED
    }

    enum InstallationStatus {
        PENDING,
        INSTALLED,
        FAILED
    }

    record Version(int major, int minor, int patch)
            implements Comparable<Version> {

        Version {
            if (major < 0 || minor < 0 || patch < 0) {
                throw new IllegalArgumentException(
                    "Negative version components are prohibited."
                );
            }
        }

        static Version parse(String value) {
            if (value == null ||
                !value.matches(
                    "(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)"
                )) {
                throw new IllegalArgumentException(
                    "Invalid semantic version: " + value
                );
            }

            String[] parts = value.split("\\.");

            return new Version(
                Integer.parseInt(parts[0]),
                Integer.parseInt(parts[1]),
                Integer.parseInt(parts[2])
            );
        }

        @Override
        public int compareTo(Version other) {
            int result = Integer.compare(major, other.major);

            if (result != 0) return result;

            result = Integer.compare(minor, other.minor);

            if (result != 0) return result;

            return Integer.compare(patch, other.patch);
        }

        @Override
        public String toString() {
            return major + "." + minor + "." + patch;
        }
    }


    record Dependency(String name, String constraint) {
        Dependency {
            name = normalizeName(name);

            if (constraint == null || constraint.isBlank()) {
                constraint = "*";
            }
        }
    }


    static final class PackageRecord {
        private final String name;
        private final Version version;
        private final String description;
        private final List<Dependency> dependencies;
        private final String license;
        private final String source;
        private final PackageStatus status;

        PackageRecord(
            String name,
            Version version,
            String description,
            List<Dependency> dependencies,
            String license,
            String source,
            PackageStatus status
        ) {
            this.name = normalizeName(name);
            this.version = Objects.requireNonNull(version);
            this.description = Objects.requireNonNull(description);
            this.dependencies = List.copyOf(dependencies);
            this.license = Objects.requireNonNull(license);
            this.source = Objects.requireNonNull(source);
            this.status = Objects.requireNonNull(status);

            if (description.isBlank()) {
                throw new IllegalArgumentException(
                    "Description is required."
                );
            }

            Set<String> names = new HashSet<>();

            for (Dependency dependency : dependencies) {
                if (dependency.name().equals(this.name)) {
                    throw new IllegalArgumentException(
                        "Self-dependency is prohibited."
                    );
                }

                if (!names.add(dependency.name())) {
                    throw new IllegalArgumentException(
                        "Duplicate dependency."
                    );
                }
            }
        }

        String name() {
            return name;
        }

        Version version() {
            return version;
        }

        List<Dependency> dependencies() {
            return dependencies;
        }

        String license() {
            return license;
        }

        String source() {
            return source;
        }

        PackageStatus status() {
            return status;
        }
    }


    static final class PackageException extends RuntimeException {
        PackageException(String message) {
            super(message);
        }
    }


    static String normalizeName(String name) {
        if (name == null ||
            !name.matches(
                "[A-Za-z0-9](?:[A-Za-z0-9._-]{0,198}[A-Za-z0-9])?"
            ) ||
            name.contains("..")) {
            throw new IllegalArgumentException(
                "Invalid package name: " + name
            );
        }

        return name.replaceAll("[-_.]+", "-").toLowerCase(
            Locale.ROOT
        );
    }


    static boolean satisfies(
        Version actual,
        String constraint
    ) {
        if (constraint.equals("*")) {
            return true;
        }

        String operator = null;

        for (String candidate :
             List.of("==", "!=", ">=", "<=", ">", "<")) {
            if (constraint.startsWith(candidate)) {
                operator = candidate;
                break;
            }
        }

        if (operator == null) {
            throw new IllegalArgumentException(
                "Unsupported constraint: " + constraint
            );
        }

        Version expected = Version.parse(
            constraint.substring(operator.length())
        );

        int comparison = actual.compareTo(expected);

        return switch (operator) {
            case "==" -> comparison == 0;
            case "!=" -> comparison != 0;
            case ">=" -> comparison >= 0;
            case "<=" -> comparison <= 0;
            case ">" -> comparison > 0;
            case "<" -> comparison < 0;
            default -> false;
        };
    }


    interface PackageRepository {
        void publish(PackageRecord packageRecord);

        PackageRecord find(String name, String constraint);
    }


    static final class InMemoryRepository
            implements PackageRepository {

        private final Map<String, List<PackageRecord>> packages =
            new HashMap<>();

        @Override
        public void publish(PackageRecord packageRecord) {
            List<PackageRecord> versions =
                packages.computeIfAbsent(
                    packageRecord.name(),
                    ignored -> new ArrayList<>()
                );

            boolean duplicate = versions.stream().anyMatch(
                existing ->
                    existing.version().equals(packageRecord.version())
            );

            if (duplicate) {
                throw new PackageException(
                    "Duplicate package version."
                );
            }

            versions.add(packageRecord);

            versions.sort(
                Comparator.comparing(
                    PackageRecord::version
                ).reversed()
            );
        }

        @Override
        public PackageRecord find(
            String name,
            String constraint
        ) {
            String key = normalizeName(name);

            return packages.getOrDefault(key, List.of())
                .stream()
                .filter(p -> p.status() == PackageStatus.AVAILABLE)
                .filter(p -> satisfies(p.version(), constraint))
                .findFirst()
                .orElseThrow(() -> new PackageException(
                    "No compatible version for " + key
                ));
        }
    }


    static final class DependencyResolver {
        private final PackageRepository repository;

        DependencyResolver(PackageRepository repository) {
            this.repository = repository;
        }

        List<PackageRecord> resolve(
            String name,
            String constraint
        ) {
            List<PackageRecord> ordered = new ArrayList<>();

            Set<String> visited = new HashSet<>();
            Set<String> active = new HashSet<>();

            visit(
                name,
                constraint,
                ordered,
                visited,
                active
            );

            return List.copyOf(ordered);
        }

        private void visit(
            String name,
            String constraint,
            List<PackageRecord> ordered,
            Set<String> visited,
            Set<String> active
        ) {
            String key = normalizeName(name);

            if (active.contains(key)) {
                throw new PackageException(
                    "Circular dependency: " + key
                );
            }

            PackageRecord packageRecord =
                repository.find(key, constraint);

            String identity =
                key + "@" + packageRecord.version();

            if (visited.contains(identity)) {
                return;
            }

            active.add(key);

            packageRecord.dependencies().stream()
                .sorted(Comparator.comparing(Dependency::name))
                .forEach(dependency -> visit(
                    dependency.name(),
                    dependency.constraint(),
                    ordered,
                    visited,
                    active
                ));

            active.remove(key);
            visited.add(identity);
            ordered.add(packageRecord);
        }
    }


    static final class ReviewPolicy {
        private final Set<String> blockedPackages;
        private final Set<String> allowedLicenses;
        private final Set<String> allowedSources;

        ReviewPolicy(
            Set<String> blockedPackages,
            Set<String> allowedLicenses,
            Set<String> allowedSources
        ) {
            this.blockedPackages = blockedPackages.stream()
                .map(Main::normalizeName)
                .collect(Collectors.toUnmodifiableSet());

            this.allowedLicenses = Set.copyOf(allowedLicenses);
            this.allowedSources = Set.copyOf(allowedSources);
        }

        List<String> evaluate(List<PackageRecord> packages) {
            List<String> issues = new ArrayList<>();

            for (PackageRecord packageRecord : packages) {
                if (blockedPackages.contains(packageRecord.name())) {
                    issues.add(
                        packageRecord.name() + ": blocked"
                    );
                }

                if (!allowedLicenses.contains(packageRecord.license())) {
                    issues.add(
                        packageRecord.name() + ": prohibited license"
                    );
                }

                if (!allowedSources.contains(packageRecord.source())) {
                    issues.add(
                        packageRecord.name() + ": untrusted source"
                    );
                }
            }

            return List.copyOf(issues);
        }
    }


    static final class InstallationService {
        private final Map<String, PackageRecord> installed =
            new TreeMap<>();

        private final ReviewPolicy policy;

        InstallationService(ReviewPolicy policy) {
            this.policy = policy;
        }

        synchronized void install(
            List<PackageRecord> packages
        ) {
            if (packages.isEmpty()) {
                throw new PackageException(
                    "No packages supplied."
                );
            }

            List<String> violations = policy.evaluate(packages);

            if (!violations.isEmpty()) {
                throw new PackageException(
                    "Policy rejected installation: " +
                    String.join("; ", violations)
                );
            }

            // Copy-on-write provides atomic state replacement.
            Map<String, PackageRecord> candidate =
                new TreeMap<>(installed);

            for (PackageRecord packageRecord : packages) {
                PackageRecord existing =
                    candidate.get(packageRecord.name());

                if (existing != null &&
                    !existing.version().equals(packageRecord.version())) {
                    throw new PackageException(
                        "Version conflict: " + packageRecord.name()
                    );
                }

                candidate.put(packageRecord.name(), packageRecord);
            }

            installed.clear();
            installed.putAll(candidate);
        }

        synchronized void uninstall(String name) {
            String key = normalizeName(name);

            if (!installed.containsKey(key)) {
                throw new PackageException(
                    "Package is not installed."
                );
            }

            List<String> dependents = installed.values()
                .stream()
                .filter(p -> p.dependencies().stream()
                    .anyMatch(d -> d.name().equals(key)))
                .map(PackageRecord::name)
                .toList();

            if (!dependents.isEmpty()) {
                throw new PackageException(
                    "Package is required by " + dependents
                );
            }

            installed.remove(key);
        }

        synchronized List<PackageRecord> list() {
            return List.copyOf(installed.values());
        }
    }


    static PackageRecord createPackage(
        String name,
        String version,
        String description,
        List<Dependency> dependencies
    ) {
        return new PackageRecord(
            name,
            Version.parse(version),
            description,
            dependencies,
            "MIT",
            "pypi",
            PackageStatus.AVAILABLE
        );
    }


    public static void main(String[] args) {
        try {
            InMemoryRepository repository =
                new InMemoryRepository();

            repository.publish(createPackage(
                "numpy",
                "2.1.0",
                "Numerical computing.",
                List.of()
            ));

            repository.publish(createPackage(
                "pandas",
                "2.2.0",
                "Data analysis.",
                List.of(
                    new Dependency("numpy", ">=2.0.0")
                )
            ));

            repository.publish(createPackage(
                "requests",
                "2.32.0",
                "HTTP client.",
                List.of()
            ));

            repository.publish(createPackage(
                "analytics-toolkit",
                "1.0.0",
                "Analytics application.",
                List.of(
                    new Dependency("pandas", ">=2.2.0"),
                    new Dependency("requests", ">=2.30.0")
                )
            ));

            System.out.println(
                "\n1. Dependency resolution"
            );

            DependencyResolver resolver =
                new DependencyResolver(repository);

            List<PackageRecord> packages =
                resolver.resolve("analytics-toolkit", "*");

            packages.forEach(p ->
                System.out.println(
                    p.name() + "==" + p.version()
                )
            );

            System.out.println(
                "\n2. Enterprise package policy"
            );

            ReviewPolicy policy = new ReviewPolicy(
                Set.of("malicious-library"),
                Set.of("MIT", "Apache-2.0", "BSD-3-Clause", "ISC"),
                Set.of("pypi")
            );

            List<String> issues = policy.evaluate(packages);

            if (!issues.isEmpty()) {
                throw new PackageException(
                    String.join("; ", issues)
                );
            }

            System.out.println("Policy approved.");

            System.out.println(
                "\n3. Transactional package installation"
            );

            InstallationService service =
                new InstallationService(policy);

            service.install(packages);

            service.list().forEach(p ->
                System.out.println(
                    p.name() + "==" + p.version()
                )
            );

            System.out.println(
                "\n4. Version policy validation"
            );

            if (!satisfies(
                Version.parse("2.1.0"),
                ">=2.0.0"
            )) {
                throw new PackageException(
                    "Version validation failed."
                );
            }

            System.out.println("Version validation passed.");

            System.out.println(
                "\n5. Dependency protection"
            );

            try {
                service.uninstall("numpy");
            } catch (PackageException error) {
                System.out.println(
                    "Expected failure: " + error.getMessage()
                );
            }

            System.out.println(
                "\n6. Final installed packages"
            );

            service.list().forEach(p ->
                System.out.println(
                    p.name() + "==" + p.version()
                )
            );

        } catch (RuntimeException error) {
            System.err.println(
                "Package management failure: " +
                error.getMessage()
            );

            System.exit(1);
        }
    }
}
