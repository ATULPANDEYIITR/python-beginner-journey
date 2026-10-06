import java.util.*;
import java.util.stream.Collectors;

/**
 * SetComprehensionPatterns
 *
 * Java does not provide Python-style set-comprehension syntax.
 * Java's closest idiomatic mechanisms are Stream.filter(), Stream.map(),
 * and Collectors.toSet(), plus explicit loops when nested processing or
 * stateful validation is easier to express imperatively.
 *
 * The program models set-comprehension semantics through realistic
 * repository-independent data-processing and authorization scenarios.
 */
public class SetComprehensionPatterns {

    record Transaction(String account, int amount) {}

    record User(String username, Set<String> roles, boolean active) {
        User {
            roles = Set.copyOf(roles);
        }
    }

    static void heading(String title) {
        System.out.println("\n" + "=".repeat(72));
        System.out.println(title);
        System.out.println("=".repeat(72));
    }

    static void basicSetConstruction() {
        heading("Basic Set Construction");

        List<Integer> numbers = List.of(1, 2, 2, 3, 4, 4, 5);

        Set<Integer> squares = numbers.stream()
                .map(number -> number * number)
                .collect(Collectors.toSet());

        Set<Integer> evens = numbers.stream()
                .filter(number -> number % 2 == 0)
                .collect(Collectors.toSet());

        System.out.println("Squares: " + new TreeSet<>(squares));
        System.out.println("Even numbers: " + new TreeSet<>(evens));
    }

    static void filteringAndTransformation() {
        heading("Filtering and Transformation");

        List<Transaction> transactions = List.of(
                new Transaction("A100", 2500),
                new Transaction("A101", 750),
                new Transaction("A100", 1250),
                new Transaction("A102", 4000),
                new Transaction("A103", -50)
        );

        Set<String> highValueAccounts = transactions.stream()
                .filter(transaction -> transaction.amount() >= 2000)
                .map(Transaction::account)
                .collect(Collectors.toSet());

        Set<Integer> positiveAmounts = transactions.stream()
                .filter(transaction -> transaction.amount() > 0)
                .map(Transaction::amount)
                .collect(Collectors.toSet());

        System.out.println("High-value accounts: "
                + new TreeSet<>(highValueAccounts));
        System.out.println("Positive amounts: "
                + new TreeSet<>(positiveAmounts));
    }

    static void nestedIteration() {
        heading("Nested Iteration");

        Set<String> combinations = new TreeSet<>();

        for (String letter : List.of("A", "B")) {
            for (int number : List.of(1, 2, 3)) {
                combinations.add(letter + number);
            }
        }

        System.out.println("Cartesian combinations: " + combinations);

        Set<String> coordinates = new TreeSet<>();

        for (int x = 0; x < 3; x++) {
            for (int y = 0; y < 3; y++) {
                if (x != y) {
                    coordinates.add(x + "," + y);
                }
            }
        }

        System.out.println("Distinct coordinates: " + coordinates);
    }

    static void structuredRecords() {
        heading("Structured Records");

        List<User> users = List.of(
                new User(
                        "anita",
                        Set.of("reader", "analyst"),
                        true
                ),
                new User(
                        "rahul",
                        Set.of("admin", "reader"),
                        true
                ),
                new User(
                        "meera",
                        Set.of("reader"),
                        false
                ),
                new User(
                        "vikas",
                        Set.of("analyst", "auditor"),
                        true
                )
        );

        Set<String> activeUsers = users.stream()
                .filter(User::active)
                .map(User::username)
                .collect(Collectors.toSet());

        Set<String> analysts = users.stream()
                .filter(user ->
                        user.active() &&
                        user.roles().contains("analyst")
                )
                .map(User::username)
                .collect(Collectors.toSet());

        Set<String> activeRoles = users.stream()
                .filter(User::active)
                .flatMap(user -> user.roles().stream())
                .collect(Collectors.toSet());

        System.out.println("Active users: " + new TreeSet<>(activeUsers));
        System.out.println("Active analysts: " + new TreeSet<>(analysts));
        System.out.println("Active roles: " + new TreeSet<>(activeRoles));
    }

    static void setRelationships() {
        heading("Set Relationships");

        Set<String> requested = Set.of(
                "read", "write", "delete", "audit"
        );

        Set<String> granted = Set.of(
                "read", "write", "audit"
        );

        Set<String> missing = requested.stream()
                .filter(permission -> !granted.contains(permission))
                .collect(Collectors.toSet());

        Set<String> intersection = requested.stream()
                .filter(granted::contains)
                .collect(Collectors.toSet());

        System.out.println("Missing permissions: "
                + new TreeSet<>(missing));
        System.out.println("Intersection: "
                + new TreeSet<>(intersection));
    }

    static boolean isPrime(int number) {
        if (number < 2) {
            return false;
        }

        if (number == 2) {
            return true;
        }

        if (number % 2 == 0) {
            return false;
        }

        for (int divisor = 3;
             divisor <= Math.sqrt(number);
             divisor += 2) {
            if (number % divisor == 0) {
                return false;
            }
        }

        return true;
    }

    static void algorithmicConstruction() {
        heading("Algorithmic Set Construction");

        Set<Integer> primes = java.util.stream.IntStream
                .rangeClosed(2, 100)
                .filter(SetComprehensionPatterns::isPrime)
                .boxed()
                .collect(Collectors.toSet());

        System.out.println("Primes: " + new TreeSet<>(primes));
    }

    static void validation() {
        heading("Validation and Edge Cases");

        List<Object> values = List.of(
                10,
                "20",
                30,
                true,
                10
        );

        Set<Integer> validIntegers = values.stream()
                .filter(Integer.class::isInstance)
                .map(Integer.class::cast)
                .collect(Collectors.toSet());

        Set<String> normalizedStrings = values.stream()
                .filter(String.class::isInstance)
                .map(String.class::cast)
                .map(String::toLowerCase)
                .collect(Collectors.toSet());

        System.out.println("Valid integers: "
                + new TreeSet<>(validIntegers));
        System.out.println("Normalized strings: "
                + new TreeSet<>(normalizedStrings));

        try {
            Objects.requireNonNull(
                    null,
                    "A required value cannot be null."
            );
        } catch (NullPointerException exception) {
            System.out.println(
                    "Expected validation failure: "
                            + exception.getMessage()
            );
        }
    }

    static void permissionPolicy() {
        heading("Permission Policy Model");

        Map<String, Set<String>> accounts = Map.of(
                "finance", Set.of("read", "write", "approve"),
                "analytics", Set.of("read", "export"),
                "support", Set.of("read", "comment"),
                "guest", Set.of("read")
        );

        Set<String> approvalEligibleRoles = accounts.entrySet()
                .stream()
                .filter(entry ->
                        entry.getValue().contains("read") &&
                        entry.getValue().contains("approve")
                )
                .map(Map.Entry::getKey)
                .collect(Collectors.toSet());

        Set<String> elevatedPermissions = accounts.values()
                .stream()
                .flatMap(Set::stream)
                .filter(permission ->
                        Set.of("write", "approve", "export")
                                .contains(permission)
                )
                .collect(Collectors.toSet());

        System.out.println(
                "Approval-eligible roles: "
                        + new TreeSet<>(approvalEligibleRoles)
        );

        System.out.println(
                "Elevated permissions: "
                        + new TreeSet<>(elevatedPermissions)
        );
    }

    static void immutableResult() {
        heading("Immutable Set Result");

        Set<String> mutable = new HashSet<>(
                List.of("read", "write", "read")
        );

        Set<String> immutable = Set.copyOf(mutable);

        System.out.println("Immutable unique values: "
                + new TreeSet<>(immutable));

        try {
            immutable.add("delete");
        } catch (UnsupportedOperationException exception) {
            System.out.println(
                    "Expected immutable-set failure: "
                            + exception.getClass().getSimpleName()
            );
        }
    }

    static void performanceModel() {
        heading("Performance Characteristics");

        long start = System.nanoTime();

        Set<Integer> values = java.util.stream.IntStream
                .range(0, 100_000)
                .filter(number -> number % 3 == 0)
                .map(number -> number * 2)
                .boxed()
                .collect(Collectors.toSet());

        long elapsed = System.nanoTime() - start;

        System.out.println("Unique transformed values: "
                + values.size());
        System.out.printf(
                Locale.ROOT,
                "Stream-to-set time: %.3f ms%n",
                elapsed / 1_000_000.0
        );

        // HashSet normally provides average O(1) membership checks.
        // TreeSet provides ordered storage with O(log n) operations.
        System.out.println(
                "Contains 60000: " + values.contains(60000)
        );
    }

    public static void main(String[] args) {
        basicSetConstruction();
        filteringAndTransformation();
        nestedIteration();
        structuredRecords();
        setRelationships();
        algorithmicConstruction();
        validation();
        permissionPolicy();
        immutableResult();
        performanceModel();
    }
}
