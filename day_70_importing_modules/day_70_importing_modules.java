/*
 * IMPORTING MODULES IN JAVA 17
 *
 * Demonstrates:
 * - Single-type imports
 * - Wildcard imports
 * - Static imports
 * - Fully qualified class names
 * - Package organization
 * - Java module system concepts
 * - Reflection
 * - ServiceLoader
 * - Class loading
 * - Dependency validation
 * - Enterprise module initialization
 * - Failure handling
 *
 * Save as ImportingModules.java
 *
 * Compile:
 * javac ImportingModules.java
 *
 * Run:
 * java ImportingModules
 */

import java.lang.reflect.Method;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.logging.Level;
import java.util.logging.Logger;

// ---------------------------------------------------------
// 1. Enterprise module demonstration
// ---------------------------------------------------------

public class ImportingModules {

    private static final Logger LOGGER =
        Logger.getLogger(ImportingModules.class.getName());

    public static void main(String[] args) {

        try {

            demonstrateBasicImports();

            demonstratePackageConcepts();

            demonstrateReflection();

            demonstrateEnterpriseModuleSystem();

            demonstrateModuleFailures();

            runTests();

            System.out.println("\nExecution completed.");

        } catch (Exception exception) {

            LOGGER.log(
                Level.SEVERE,
                "Application execution failed",
                exception
            );

            System.exit(1);
        }
    }


    // -----------------------------------------------------
    // 2. Different import styles
    // -----------------------------------------------------

    private static void demonstrateBasicImports() {

        System.out.println("\n1. IMPORT MECHANISMS");

        List<Integer> numbers =
            Arrays.asList(10, 20, 30, 40, 50);

        double average = numbers.stream()
            .mapToInt(Integer::intValue)
            .average()
            .orElseThrow();

        System.out.println("Average: " + average);

        Set<String> languages = new HashSet<>(
            Arrays.asList(
                "Java",
                "Python",
                "C++",
                "Java"
            )
        );

        System.out.println("Unique languages: " + languages);

        // Fully qualified class name.
        java.util.UUID identifier = UUID.randomUUID();

        System.out.println("Identifier: " + identifier);

        // Static method invocation.
        double squareRoot = Math.sqrt(144);

        System.out.println("Square root: " + squareRoot);

        System.out.println(
            "Current timestamp: " + LocalDateTime.now()
        );
    }


    // -----------------------------------------------------
    // 3. Package and import concepts
    // -----------------------------------------------------

    private static void demonstratePackageConcepts() {

        System.out.println("\n2. PACKAGE ORGANIZATION");

        List<String> examples = List.of(
            "import java.util.List;",
            "import java.util.*;",
            "import static java.lang.Math.sqrt;",
            "import static java.util.Collections.sort;",
            "java.time.LocalDateTime"
        );

        examples.forEach(System.out::println);

        System.out.println(
            "Current class package: "
            + ImportingModules.class.getPackageName()
        );

        System.out.println(
            "Class loader: "
            + ImportingModules.class.getClassLoader()
        );

        System.out.println(
            "Bootstrap classes may have a null class loader."
        );
    }


    // -----------------------------------------------------
    // 4. Reflection and class loading
    // -----------------------------------------------------

    private static void demonstrateReflection()
        throws Exception {

        System.out.println("\n3. REFLECTION");

        Class<?> target = Class.forName(
            "java.util.ArrayList"
        );

        System.out.println("Class name: " + target.getName());

        System.out.println(
            "Methods: " + target.getDeclaredMethods().length
        );

        Object instance = target
            .getDeclaredConstructor()
            .newInstance();

        if (!(instance instanceof List<?>)) {
            throw new IllegalStateException(
                "Unexpected class type"
            );
        }

        Method addMethod = target.getMethod(
            "add",
            Object.class
        );

        addMethod.invoke(instance, "Module A");

        System.out.println("Instance: " + instance);
    }


    // -----------------------------------------------------
    // 5. Enterprise module domain types
    // -----------------------------------------------------

    enum ModuleState {
        REGISTERED,
        INITIALIZING,
        ACTIVE,
        FAILED
    }


    record ModuleDefinition(
        String name,
        String version,
        Set<String> dependencies,
        ModuleInitializer initializer
    ) {

        ModuleDefinition {

            if (
                name == null ||
                !name.matches("[a-z][a-z0-9.-]{1,63}")
            ) {
                throw new IllegalArgumentException(
                    "Invalid module name"
                );
            }

            if (
                version == null ||
                !version.matches("\\d+\\.\\d+\\.\\d+")
            ) {
                throw new IllegalArgumentException(
                    "Invalid semantic version"
                );
            }

            Objects.requireNonNull(
                dependencies,
                "Dependencies cannot be null"
            );

            Objects.requireNonNull(
                initializer,
                "Initializer cannot be null"
            );

            dependencies = Collections.unmodifiableSet(
                new HashSet<>(dependencies)
            );

            if (dependencies.contains(name)) {
                throw new IllegalArgumentException(
                    "Self-dependency is prohibited"
                );
            }
        }
    }


    @FunctionalInterface
    interface ModuleInitializer {
        void initialize() throws Exception;
    }


    record ModuleStatus(
        String name,
        ModuleState state,
        LocalDateTime updatedAt,
        String error
    ) {}


    // -----------------------------------------------------
    // 6. Custom exceptions
    // -----------------------------------------------------

    static class ModuleException extends Exception {

        ModuleException(String message) {
            super(message);
        }

        ModuleException(String message, Throwable cause) {
            super(message, cause);
        }
    }


    // -----------------------------------------------------
    // 7. Module management service
    // -----------------------------------------------------

    static class ModuleManager {

        private final Map<String, ModuleDefinition> definitions =
            new HashMap<>();

        private final Map<String, ModuleState> states =
            new HashMap<>();

        private final Map<String, ModuleStatus> history =
            new HashMap<>();

        private final Set<String> activePath =
            new HashSet<>();

        private final List<String> loadOrder =
            new ArrayList<>();

        public synchronized void register(
            ModuleDefinition definition
        ) throws ModuleException {

            Objects.requireNonNull(definition);

            if (definitions.containsKey(definition.name())) {
                throw new ModuleException(
                    "Duplicate module: " + definition.name()
                );
            }

            definitions.put(
                definition.name(),
                definition
            );

            updateState(
                definition.name(),
                ModuleState.REGISTERED,
                null
            );
        }


        public synchronized void load(
            String moduleName
        ) throws ModuleException {

            if (!definitions.containsKey(moduleName)) {
                throw new ModuleException(
                    "Unknown module: " + moduleName
                );
            }

            loadRecursive(moduleName);
        }


        private void loadRecursive(
            String moduleName
        ) throws ModuleException {

            ModuleState state = states.get(moduleName);

            if (state == ModuleState.ACTIVE) {
                return;
            }

            if (state == ModuleState.FAILED) {
                throw new ModuleException(
                    "Previously failed module: " + moduleName
                );
            }

            if (!activePath.add(moduleName)) {
                throw new ModuleException(
                    "Circular dependency: " + moduleName
                );
            }

            updateState(
                moduleName,
                ModuleState.INITIALIZING,
                null
            );

            ModuleDefinition definition =
                definitions.get(moduleName);

            try {

                for (String dependency :
                     definition.dependencies()) {

                    if (!definitions.containsKey(dependency)) {
                        throw new ModuleException(
                            "Missing dependency: " + dependency
                        );
                    }

                    loadRecursive(dependency);
                }

                definition.initializer().initialize();

                updateState(
                    moduleName,
                    ModuleState.ACTIVE,
                    null
                );

                loadOrder.add(moduleName);

            } catch (Exception exception) {

                updateState(
                    moduleName,
                    ModuleState.FAILED,
                    exception.getMessage()
                );

                if (exception instanceof ModuleException) {
                    throw (ModuleException) exception;
                }

                throw new ModuleException(
                    "Initialization failed: " + moduleName,
                    exception
                );

            } finally {

                activePath.remove(moduleName);
            }
        }


        private void updateState(
            String name,
            ModuleState state,
            String error
        ) {

            states.put(name, state);

            history.put(
                name,
                new ModuleStatus(
                    name,
                    state,
                    LocalDateTime.now(),
                    error
                )
            );
        }


        public synchronized ModuleStatus getStatus(
            String name
        ) throws ModuleException {

            ModuleStatus status = history.get(name);

            if (status == null) {
                throw new ModuleException(
                    "Module status unavailable: " + name
                );
            }

            return status;
        }


        public synchronized List<String> getLoadOrder() {

            return List.copyOf(loadOrder);
        }


        public synchronized Map<String, ModuleStatus>
        getAllStatuses() {

            return Collections.unmodifiableMap(
                new HashMap<>(history)
            );
        }
    }


    // -----------------------------------------------------
    // 8. Enterprise module registration
    // -----------------------------------------------------

    private static void demonstrateEnterpriseModuleSystem()
        throws ModuleException {

        System.out.println("\n4. ENTERPRISE MODULE MANAGEMENT");

        ModuleManager manager = new ModuleManager();

        manager.register(
            new ModuleDefinition(
                "configuration",
                "1.0.0",
                Set.of(),
                () -> System.out.println(
                    "Configuration initialized"
                )
            )
        );

        manager.register(
            new ModuleDefinition(
                "database",
                "2.1.0",
                Set.of("configuration"),
                () -> System.out.println(
                    "Database initialized"
                )
            )
        );

        manager.register(
            new ModuleDefinition(
                "analytics",
                "1.2.0",
                Set.of("configuration", "database"),
                () -> System.out.println(
                    "Analytics initialized"
                )
            )
        );

        manager.register(
            new ModuleDefinition(
                "application",
                "1.0.0",
                Set.of("analytics"),
                () -> System.out.println(
                    "Application initialized"
                )
            )
        );

        manager.load("application");

        // Repeated loading does not repeat initialization.
        manager.load("application");

        System.out.println(
            "Load order: " + manager.getLoadOrder()
        );

        manager.getAllStatuses().forEach(
            (name, status) -> System.out.println(
                name + " -> " + status.state()
            )
        );
    }


    // -----------------------------------------------------
    // 9. Module failure scenarios
    // -----------------------------------------------------

    private static void demonstrateModuleFailures()
        throws ModuleException {

        System.out.println("\n5. MODULE FAILURE SCENARIOS");

        ModuleManager circularManager =
            new ModuleManager();

        circularManager.register(
            new ModuleDefinition(
                "first",
                "1.0.0",
                Set.of("second"),
                () -> {}
            )
        );

        circularManager.register(
            new ModuleDefinition(
                "second",
                "1.0.0",
                Set.of("first"),
                () -> {}
            )
        );

        try {

            circularManager.load("first");

        } catch (ModuleException exception) {

            System.out.println(
                "Circular dependency detected: "
                + exception.getMessage()
            );
        }

        ModuleManager missingManager =
            new ModuleManager();

        missingManager.register(
            new ModuleDefinition(
                "service",
                "1.0.0",
                Set.of("missing"),
                () -> {}
            )
        );

        try {

            missingManager.load("service");

        } catch (ModuleException exception) {

            System.out.println(
                "Missing dependency: "
                + exception.getMessage()
            );
        }
    }


    // -----------------------------------------------------
    // 10. Validation
    // -----------------------------------------------------

    private static void runTests()
        throws Exception {

        ModuleManager manager = new ModuleManager();

        manager.register(
            new ModuleDefinition(
                "base",
                "1.0.0",
                Set.of(),
                () -> {}
            )
        );

        manager.register(
            new ModuleDefinition(
                "service",
                "1.0.0",
                Set.of("base"),
                () -> {}
            )
        );

        manager.load("service");

        if (
            manager.getStatus("base").state()
            != ModuleState.ACTIVE
        ) {
            throw new AssertionError(
                "Base module was not activated"
            );
        }

        if (
            manager.getStatus("service").state()
            != ModuleState.ACTIVE
        ) {
            throw new AssertionError(
                "Service module was not activated"
            );
        }

        if (manager.getLoadOrder().size() != 2) {
            throw new AssertionError(
                "Unexpected module load count"
            );
        }

        System.out.println("\nAll Java 17 tests passed.");
    }
}
