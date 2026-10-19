import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class RecursionEnterpriseDemo {

    record Employee(String id, String name, String managerId) {}

    record Department(String id, String name) {}

    enum VisitState {
        UNSEEN,
        ACTIVE,
        COMPLETE
    }

    static final class OrganizationService {
        private final Map<String, Employee> employees = new HashMap<>();

        void addEmployee(Employee employee) {
            if (employees.containsKey(employee.id())) {
                throw new IllegalArgumentException(
                    "Duplicate employee ID: " + employee.id()
                );
            }

            if (employee.id().isBlank() || employee.name().isBlank()) {
                throw new IllegalArgumentException(
                    "Employee ID and name are required"
                );
            }

            employees.put(employee.id(), employee);
        }

        List<String> reportingChain(String employeeId) {
            if (!employees.containsKey(employeeId)) {
                throw new IllegalArgumentException(
                    "Unknown employee: " + employeeId
                );
            }

            List<String> chain = new ArrayList<>();
            Set<String> visited = new HashSet<>();
            buildReportingChain(employeeId, chain, visited);
            return chain;
        }

        private void buildReportingChain(
            String employeeId,
            List<String> chain,
            Set<String> visited
        ) {
            /*
             * The visited set turns an otherwise potentially infinite
             * recursive manager relationship into a validated workflow.
             */
            if (!visited.add(employeeId)) {
                throw new IllegalStateException(
                    "Circular management relationship detected at "
                    + employeeId
                );
            }

            Employee employee = employees.get(employeeId);
            chain.add(employee.name());

            if (employee.managerId() != null) {
                if (!employees.containsKey(employee.managerId())) {
                    throw new IllegalStateException(
                        "Manager does not exist: " + employee.managerId()
                    );
                }

                buildReportingChain(employee.managerId(), chain, visited);
            }
        }

        int organizationalDepth(String employeeId) {
            if (!employees.containsKey(employeeId)) {
                throw new IllegalArgumentException(
                    "Unknown employee: " + employeeId
                );
            }

            return organizationalDepth(
                employees.get(employeeId),
                new HashSet<>()
            );
        }

        private int organizationalDepth(
            Employee employee,
            Set<String> visited
        ) {
            if (!visited.add(employee.id())) {
                throw new IllegalStateException(
                    "Cycle detected while measuring organizational depth"
                );
            }

            if (employee.managerId() == null) {
                return 1;
            }

            Employee manager = employees.get(employee.managerId());

            if (manager == null) {
                throw new IllegalStateException(
                    "Manager does not exist: " + employee.managerId()
                );
            }

            return 1 + organizationalDepth(manager, visited);
        }
    }

    static final class ExpressionEvaluator {

        sealed interface Node
            permits NumberNode, OperationNode {}

        record NumberNode(int value) implements Node {}

        record OperationNode(
            char operator,
            Node left,
            Node right
        ) implements Node {}

        static int evaluate(Node node) {
            if (node instanceof NumberNode number) {
                return number.value();
            }

            OperationNode operation = (OperationNode) node;
            int left = evaluate(operation.left());
            int right = evaluate(operation.right());

            return switch (operation.operator()) {
                case '+' -> left + right;
                case '-' -> left - right;
                case '*' -> left * right;
                case '/' -> {
                    if (right == 0) {
                        throw new ArithmeticException(
                            "division by zero"
                        );
                    }
                    yield left / right;
                }
                default -> throw new IllegalArgumentException(
                    "Unsupported operator: " + operation.operator()
                );
            };
        }
    }

    static final class DependencyService {
        private final Map<String, List<String>> dependencies =
            new HashMap<>();

        void addModule(String module, List<String> requiredModules) {
            if (dependencies.containsKey(module)) {
                throw new IllegalArgumentException(
                    "Module already exists: " + module
                );
            }

            dependencies.put(
                module,
                List.copyOf(requiredModules)
            );
        }

        List<String> resolve(String root) {
            if (!dependencies.containsKey(root)) {
                throw new IllegalArgumentException(
                    "Unknown module: " + root
                );
            }

            Map<String, VisitState> states = new HashMap<>();
            List<String> result = new ArrayList<>();

            visit(root, states, result);

            Collections.reverse(result);
            return result;
        }

        private void visit(
            String module,
            Map<String, VisitState> states,
            List<String> result
        ) {
            VisitState state =
                states.getOrDefault(module, VisitState.UNSEEN);

            if (state == VisitState.COMPLETE) {
                return;
            }

            if (state == VisitState.ACTIVE) {
                throw new IllegalStateException(
                    "Circular dependency detected at " + module
                );
            }

            List<String> required = dependencies.get(module);

            if (required == null) {
                throw new IllegalStateException(
                    "Missing dependency definition: " + module
                );
            }

            states.put(module, VisitState.ACTIVE);

            for (String dependency : required) {
                visit(dependency, states, result);
            }

            states.put(module, VisitState.COMPLETE);
            result.add(module);
        }
    }

    static long factorial(int n) {
        if (n < 0) {
            throw new IllegalArgumentException(
                "factorial requires n >= 0"
            );
        }

        if (n <= 1) {
            return 1;
        }

        return n * factorial(n - 1);
    }

    static long fibonacci(int n, Map<Integer, Long> cache) {
        if (n < 0) {
            throw new IllegalArgumentException(
                "Fibonacci requires n >= 0"
            );
        }

        if (n <= 1) {
            return n;
        }

        Long cached = cache.get(n);

        if (cached != null) {
            return cached;
        }

        long value =
            fibonacci(n - 1, cache) +
            fibonacci(n - 2, cache);

        cache.put(n, value);
        return value;
    }

    static int recursiveBinarySearch(
        List<Integer> values,
        int target,
        int low,
        int high
    ) {
        if (low > high) {
            return -1;
        }

        int middle = low + (high - low) / 2;

        if (values.get(middle) == target) {
            return middle;
        }

        if (target < values.get(middle)) {
            return recursiveBinarySearch(
                values,
                target,
                low,
                middle - 1
            );
        }

        return recursiveBinarySearch(
            values,
            target,
            middle + 1,
            high
        );
    }

    static int recursiveSum(
        List<Integer> values,
        int index
    ) {
        if (index == values.size()) {
            return 0;
        }

        return values.get(index)
            + recursiveSum(values, index + 1);
    }

    public static void main(String[] args) {
        System.out.println("=== Enterprise organization recursion ===");

        OrganizationService organization =
            new OrganizationService();

        organization.addEmployee(
            new Employee("E001", "Chief Executive", null)
        );
        organization.addEmployee(
            new Employee("E002", "Engineering Director", "E001")
        );
        organization.addEmployee(
            new Employee("E003", "Platform Manager", "E002")
        );
        organization.addEmployee(
            new Employee("E004", "Backend Engineer", "E003")
        );

        System.out.println(
            "Reporting chain: "
            + organization.reportingChain("E004")
        );

        System.out.println(
            "Organizational depth: "
            + organization.organizationalDepth("E004")
        );

        System.out.println("\n=== Recursive expression tree ===");

        ExpressionEvaluator.Node expression =
            new ExpressionEvaluator.OperationNode(
                '*',
                new ExpressionEvaluator.OperationNode(
                    '+',
                    new ExpressionEvaluator.NumberNode(8),
                    new ExpressionEvaluator.NumberNode(4)
                ),
                new ExpressionEvaluator.OperationNode(
                    '-',
                    new ExpressionEvaluator.NumberNode(10),
                    new ExpressionEvaluator.NumberNode(3)
                )
            );

        System.out.println(
            "Expression result: "
            + ExpressionEvaluator.evaluate(expression)
        );

        System.out.println("\n=== Dependency resolution ===");

        DependencyService dependencyService =
            new DependencyService();

        dependencyService.addModule(
            "application",
            List.of("service", "database")
        );
        dependencyService.addModule(
            "service",
            List.of("validation", "logging")
        );
        dependencyService.addModule(
            "database",
            List.of("logging")
        );
        dependencyService.addModule(
            "validation",
            List.of("logging")
        );
        dependencyService.addModule(
            "logging",
            List.of()
        );

        System.out.println(
            "Build order: "
            + dependencyService.resolve("application")
        );

        System.out.println("\n=== Mathematical recursion ===");

        System.out.println("7! = " + factorial(7));

        Map<Integer, Long> fibonacciCache = new HashMap<>();
        fibonacciCache.put(0, 0L);
        fibonacciCache.put(1, 1L);

        System.out.println(
            "F(40) = "
            + fibonacci(40, fibonacciCache)
        );

        List<Integer> sorted =
            List.of(2, 4, 9, 13, 18, 27, 31);

        System.out.println(
            "Binary search index: "
            + recursiveBinarySearch(
                sorted,
                18,
                0,
                sorted.size() - 1
            )
        );

        System.out.println(
            "Recursive sum: "
            + recursiveSum(
                List.of(12, 7, 19, 4),
                0
            )
        );

        System.out.println("\n=== Failure-state validation ===");

        DependencyService cyclic =
            new DependencyService();

        cyclic.addModule("A", List.of("B"));
        cyclic.addModule("B", List.of("C"));
        cyclic.addModule("C", List.of("A"));

        try {
            cyclic.resolve("A");
        } catch (IllegalStateException error) {
            System.out.println(
                "Rejected cycle: " + error.getMessage()
            );
        }

        System.out.println("\n=== Implementation characteristics ===");
        System.out.println(
            "Recursive organization traversal mirrors hierarchical domain data."
        );
        System.out.println(
            "Dependency recursion uses explicit states to distinguish an active path from a completed path."
        );
        System.out.println(
            "Memoized Fibonacci stores results in a mutable cache while the recursive function controls the computation."
        );
        System.out.println(
            "Java stack depth remains a practical constraint, so externally controlled recursion should be bounded or converted to an explicit stack."
        );
    }
}
