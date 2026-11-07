import java.lang.module.ModuleDescriptor;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.stream.Collectors;

/*
 * Introduction to Modules in Java 17
 *
 * Demonstrates:
 * - Packages and classes
 * - Interfaces
 * - Java module system (JPMS)
 * - Module metadata
 * - Records
 * - Encapsulation
 * - Dependency resolution
 * - Service interfaces
 * - Immutable collections
 * - Enterprise module lifecycle
 *
 * Compile:
 * javac --release 17 IntroductionToModules.java
 *
 * Run:
 * java IntroductionToModules
 */

public class IntroductionToModules {

    // =====================================================
    // 1. Core module
    // =====================================================

    static final class CoreModule {

        private CoreModule() {
        }

        static void validateName(String name) {
            if (name == null ||
                !name.matches("[a-zA-Z][a-zA-Z0-9._-]*")) {
                throw new IllegalArgumentException(
                    "Invalid module name"
                );
            }
        }

        static void validateVersion(String version) {
            if (version == null ||
                !version.matches("\\d+\\.\\d+\\.\\d+")) {
                throw new IllegalArgumentException(
                    "Version must follow major.minor.patch"
                );
            }
        }
    }

    // =====================================================
    // 2. Domain records
    // =====================================================

    enum ModuleStatus {
        REGISTERED,
        ACTIVE,
        DISABLED,
        FAILED
    }

    record ModuleDefinition(
        String name,
        String version,
        Set<String> dependencies,
        String owner
    ) {

        ModuleDefinition {
            CoreModule.validateName(name);
            CoreModule.validateVersion(version);

            if (owner == null || owner.isBlank()) {
                throw new IllegalArgumentException(
                    "Module owner is required"
                );
            }

            Objects.requireNonNull(dependencies);

            dependencies = Set.copyOf(dependencies);

            if (dependencies.contains(name)) {
                throw new IllegalArgumentException(
                    "Self-dependency is not allowed"
                );
            }
        }
    }

    record ModuleReport(
        String moduleName,
        long recordCount,
        double total,
        double average
    ) {
    }

    // =====================================================
    // 3. Service interface
    // =====================================================

    interface ModuleService<T, R> {
        R execute(T input);
    }

    // =====================================================
    // 4. Mathematics module
    // =====================================================

    static final class MathematicsModule {

        private MathematicsModule() {
        }

        static double add(double a, double b) {
            validate(a, b);
            return a + b;
        }

        static double multiply(double a, double b) {
            validate(a, b);
            return a * b;
        }

        static double divide(double a, double b) {
            validate(a, b);

            if (b == 0.0) {
                throw new ArithmeticException(
                    "Division by zero"
                );
            }

            return a / b;
        }

        private static void validate(double... values) {
            for (double value : values) {
                if (!Double.isFinite(value)) {
                    throw new IllegalArgumentException(
                        "Values must be finite"
                    );
                }
            }
        }
    }

    // =====================================================
    // 5. Analytics module
    // =====================================================

    static final class AnalyticsModule
        implements ModuleService<List<Double>, ModuleReport> {

        @Override
        public ModuleReport execute(List<Double> records) {

            Objects.requireNonNull(records);

            if (records.isEmpty()) {
                throw new IllegalArgumentException(
                    "Analytics requires records"
                );
            }

            if (records.size() > 100_000) {
                throw new IllegalArgumentException(
                    "Record limit exceeded"
                );
            }

            double total = 0.0;

            for (double value : records) {
                if (!Double.isFinite(value)) {
                    throw new IllegalArgumentException(
                        "Invalid numeric record"
                    );
                }

                total += value;
            }

            return new ModuleReport(
                "analytics",
                records.size(),
                total,
                total / records.size()
            );
        }
    }

    // =====================================================
    // 6. Enterprise module registry
    // =====================================================

    static final class ModuleRegistry {

        private final Map<String, ModuleDefinition> definitions =
            new HashMap<>();

        private final Map<String, ModuleStatus> statuses =
            new HashMap<>();

        public void register(ModuleDefinition definition) {

            Objects.requireNonNull(definition);

            if (definitions.containsKey(definition.name())) {
                throw new IllegalStateException(
                    "Module already exists: " + definition.name()
                );
            }

            definitions.put(definition.name(), definition);
            statuses.put(
                definition.name(),
                ModuleStatus.REGISTERED
            );
        }

        public List<String> resolveDependencies(String target) {

            if (!definitions.containsKey(target)) {
                throw new IllegalArgumentException(
                    "Unknown module: " + target
                );
            }

            Set<String> visiting = new HashSet<>();
            Set<String> visited = new HashSet<>();
            List<String> result = new ArrayList<>();

            resolve(
                target,
                visiting,
                visited,
                result
            );

            return List.copyOf(result);
        }

        private void resolve(
            String name,
            Set<String> visiting,
            Set<String> visited,
            List<String> result
        ) {

            if (visiting.contains(name)) {
                throw new IllegalStateException(
                    "Circular dependency detected: " + name
                );
            }

            if (visited.contains(name)) {
                return;
            }

            ModuleDefinition definition = definitions.get(name);

            if (definition == null) {
                throw new IllegalStateException(
                    "Missing dependency: " + name
                );
            }

            visiting.add(name);

            // Sorting makes dependency resolution deterministic.
            for (String dependency :
                 new TreeSet<>(definition.dependencies())) {

                resolve(
                    dependency,
                    visiting,
                    visited,
                    result
                );
            }

            visiting.remove(name);
            visited.add(name);
            result.add(name);
        }

        public void activate(String name) {

            List<String> order = resolveDependencies(name);

            for (String module : order) {

                ModuleStatus current = statuses.get(module);

                if (current == ModuleStatus.FAILED ||
                    current == ModuleStatus.DISABLED) {
                    throw new IllegalStateException(
                        "Cannot activate module: " + module
                    );
                }

                statuses.put(module, ModuleStatus.ACTIVE);
            }
        }

        public void disable(String name) {

            if (!definitions.containsKey(name)) {
                throw new IllegalArgumentException(
                    "Unknown module"
                );
            }

            // Prevent disabling a dependency of an active module.
            for (ModuleDefinition definition : definitions.values()) {

                if (statuses.get(definition.name()) ==
                        ModuleStatus.ACTIVE &&
                    definition.dependencies().contains(name)) {

                    throw new IllegalStateException(
                        "Active module depends on: " + name
                    );
                }
            }

            statuses.put(name, ModuleStatus.DISABLED);
        }

        public Map<String, ModuleStatus> getStatuses() {
            return Collections.unmodifiableMap(
                new HashMap<>(statuses)
            );
        }

        public List<ModuleDefinition> listModules() {
            return definitions.values()
                .stream()
                .sorted((a, b) -> a.name().compareTo(b.name()))
                .collect(Collectors.toUnmodifiableList());
        }
    }

    // =====================================================
    // 7. Java Platform Module System inspection
    // =====================================================

    static void inspectJavaModuleSystem() {

        System.out.println("\n1. JAVA PLATFORM MODULE SYSTEM");

        Module currentModule =
            IntroductionToModules.class.getModule();

        System.out.println(
            "Application module name: " +
            currentModule.getName()
        );

        System.out.println(
            "Named module: " +
            currentModule.isNamed()
        );

        Module javaBase =
            Object.class.getModule();

        System.out.println(
            "Java base module: " +
            javaBase.getName()
        );

        System.out.println(
            "Java base is named: " +
            javaBase.isNamed()
        );

        ModuleDescriptor descriptor =
            javaBase.getDescriptor();

        System.out.println(
            "Java base descriptor: " +
            descriptor.name()
        );

        System.out.println(
            "Java base requires: " +
            descriptor.requires().size()
        );
    }

    // =====================================================
    // 8. Application execution
    // =====================================================

    public static void main(String[] args) {

        try {

            inspectJavaModuleSystem();

            System.out.println("\n2. MATHEMATICS MODULE");

            System.out.println(
                "Addition: " +
                MathematicsModule.add(20, 10)
            );

            System.out.println(
                "Multiplication: " +
                MathematicsModule.multiply(5, 6)
            );

            System.out.println(
                "Division: " +
                MathematicsModule.divide(100, 4)
            );


            System.out.println("\n3. ANALYTICS MODULE");

            AnalyticsModule analytics = new AnalyticsModule();

            List<Double> sales = List.of(
                1200.0, 1500.0, 1800.0, 2000.0
            );

            ModuleReport report = analytics.execute(sales);

            System.out.println("Module: " + report.moduleName());
            System.out.println("Records: " + report.recordCount());
            System.out.println("Total: " + report.total());
            System.out.println("Average: " + report.average());


            System.out.println("\n4. ENTERPRISE MODULE REGISTRY");

            ModuleRegistry registry = new ModuleRegistry();

            registry.register(new ModuleDefinition(
                "core", "1.0.0", Set.of(), "Platform Team"
            ));

            registry.register(new ModuleDefinition(
                "database", "2.0.0",
                Set.of("core"), "Data Team"
            ));

            registry.register(new ModuleDefinition(
                "analytics", "1.2.0",
                Set.of("core", "database"), "Analytics Team"
            ));

            registry.register(new ModuleDefinition(
                "dashboard", "1.0.0",
                Set.of("analytics"), "Application Team"
            ));

            System.out.println(
                "Load order: " +
                registry.resolveDependencies("dashboard")
            );

            registry.activate("dashboard");

            System.out.println("Module states:");

            registry.getStatuses().forEach(
                (name, status) ->
                    System.out.println(name + " = " + status)
            );


            System.out.println("\n5. MODULE DEFINITIONS");

            registry.listModules().forEach(
                definition -> System.out.println(
                    definition.name() +
                    " v" + definition.version() +
                    " | Owner: " + definition.owner()
                )
            );


            System.out.println("\n6. FAILURE HANDLING");

            try {
                MathematicsModule.divide(10, 0);
            } catch (ArithmeticException error) {
                System.out.println(error.getMessage());
            }

            try {
                registry.resolveDependencies("missing");
            } catch (IllegalArgumentException error) {
                System.out.println(error.getMessage());
            }

            try {
                registry.disable("core");
            } catch (IllegalStateException error) {
                System.out.println(error.getMessage());
            }


            System.out.println("\n7. VALIDATION");

            if (MathematicsModule.add(2, 3) != 5) {
                throw new IllegalStateException(
                    "Addition test failed"
                );
            }

            if (report.recordCount() != 4) {
                throw new IllegalStateException(
                    "Analytics test failed"
                );
            }

            System.out.println("All tests passed.");

        } catch (Exception error) {

            System.err.println(
                "Application failure: " + error.getMessage()
            );

            System.exit(1);
        }
    }
}
